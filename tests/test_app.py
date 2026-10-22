from pathlib import Path

import pytest

from app import (build_choices, build_question, calculate_percentage, check_answer,
                 create_app, load_cards, parse_lines, read_lines, update_score)


@pytest.fixture
def deck(tmp_path):
    path = tmp_path / "cards.txt"
    path.write_text("Q1|Alpha\nQ2|Beta\nQ3|Gamma\nQ4|Delta\n", encoding="utf-8")
    return path


@pytest.fixture
def app(deck):
    return create_app({"TESTING": True, "SECRET_KEY": "test-only-key", "CARDS_FILE": deck,
                       "SESSION_COOKIE_SECURE": False})


@pytest.fixture
def client(app):
    return app.test_client()


def test_file_read_parse_and_load(deck):
    assert read_lines(deck)[0] == "Q1|Alpha\n"
    assert parse_lines([" # comment\n", "\n", "  Q | A  \n"]) == [(3, ["Q", "A"])]
    assert load_cards(deck) == [("Q1", "Alpha"), ("Q2", "Beta"), ("Q3", "Gamma"), ("Q4", "Delta")]


@pytest.mark.parametrize("text, message", [
    ("Q1|A\nQ2|B\nQ3|C", "at least 4"),
    ("missing separator\nQ2|B\nQ3|C\nQ4|D", "Line 1"),
    ("Q1|A|extra\nQ2|B\nQ3|C\nQ4|D", "exactly one"),
    ("|A\nQ2|B\nQ3|C\nQ4|D", "must not be empty"),
    ("Q1|  \nQ2|B\nQ3|C\nQ4|D", "must not be empty"),
    ("Q1|Immutable Sequence\nQ2|immutable sequence\nQ3|C\nQ4|D", "unique"),
    ("Q1|Straße\nQ2|STRASSE\nQ3|C\nQ4|D", "unique"),
    ("# only comments\n\n", "at least 4"),
])
def test_invalid_deck_fails_startup(tmp_path, text, message):
    path = tmp_path / "bad.txt"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        create_app({"SECRET_KEY": "test-key", "CARDS_FILE": path})


def test_blank_comments_and_windows_lines(tmp_path):
    path = tmp_path / "cards.txt"
    path.write_bytes(b" # Heading\r\nQ1|A\r\n\r\nQ2|B\r\nQ3|C\r\nQ4|D\r\n")
    assert len(load_cards(path)) == 4


def test_duplicate_questions_allowed(deck):
    deck.write_text("Q|A\nQ|B\nQ|C\nQ|D")
    assert len(load_cards(deck)) == 4


def test_missing_secret_fails(deck):
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"SECRET_KEY": None, "CARDS_FILE": deck})


def test_pure_helpers(deck):
    cards = load_cards(deck)
    original = cards.copy()
    assert build_question(cards[0]) == {"question": "Q1", "answer": "Alpha"}
    for _ in range(30):
        indexes = build_choices(cards, 0)
        assert len(indexes) == len(set(indexes)) == 4
        assert 0 in indexes
    assert cards == original
    assert check_answer("Alpha", "Alpha") is True
    assert check_answer("Beta", "Alpha") is False
    assert update_score(2, True) == 3
    assert update_score(2, False) == 2
    assert calculate_percentage(16, 20) == 80.0
    assert calculate_percentage(1, 6) == 16.7


def test_complete_quiz_no_repeats_and_correct_score(client, deck):
    answers = dict(load_cards(deck))
    data = client.post("/api/start", json={}).get_json()
    seen = []
    for number in range(1, 5):
        assert data["number"] == number
        assert data["total"] == 4
        assert "answer" not in data
        assert len(set(data["choices"])) == 4
        assert answers[data["question"]] in data["choices"]
        seen.append(data["question"])
        selected = answers[data["question"]]
        if number == 2:
            selected = next(x for x in data["choices"] if x != selected)
        result = client.post("/api/answer", json={"selected": selected, "token": data["token"], "score": 999}).get_json()
        assert result["correct"] is (number != 2)
        data = client.get("/api/question").get_json()
    assert len(set(seen)) == 4
    assert data == {"complete": True, "score": 3, "total": 4, "percentage": 75.0}
    assert client.post("/api/answer", json={"selected": "Alpha", "token": "old"}).status_code == 409


def test_refresh_stable_and_sequential_duplicate_rejected(client, deck):
    data = client.post("/api/start").get_json()
    assert client.get("/api/question").get_json() == data
    body = {"selected": dict(load_cards(deck))[data["question"]], "token": data["token"]}
    assert client.post("/api/answer", json=body).status_code == 200
    assert client.post("/api/answer", json=body).status_code == 409
    current = client.get("/api/question").get_json()
    assert current["number"] == 2 and current["score"] == 1


@pytest.mark.parametrize("body", [{}, [], {"selected": 123}, {"selected": None}])
def test_bad_body_does_not_advance(client, body):
    initial = client.post("/api/start").get_json()
    assert client.post("/api/answer", json=body).status_code == 400
    assert client.get("/api/question").get_json() == initial


def test_missing_session_and_bad_requests(client):
    assert client.get("/api/question").status_code == 409
    assert client.post("/api/answer", json={"selected": "Alpha"}).status_code == 409
    data = client.post("/api/start").get_json()
    assert client.post("/api/answer", data="not-json", content_type="application/json").status_code == 400
    assert client.post("/api/answer", json={"selected": "not offered", "token": data["token"]}).status_code == 400
    assert client.post("/api/answer", json={"selected": data["choices"][0], "token": "old"}).status_code == 409
    assert client.get("/api/question").get_json() == data


def test_clients_have_independent_progress(app):
    first, second = app.test_client(), app.test_client()
    q1 = first.post("/api/start").get_json()
    q2 = second.post("/api/start").get_json()
    first.post("/api/answer", json={"selected": q1["choices"][0], "token": q1["token"]})
    assert second.get("/api/question").get_json() == q2
    assert first.get("/api/question").get_json()["number"] == 2


def test_deck_fingerprint_and_new_quiz(client):
    client.post("/api/start")
    with client.session_transaction() as session:
        state = session["quiz"]
        state["deck"] = "old-deck"
        session["quiz"] = state
    assert client.get("/api/question").status_code == 409
    assert client.post("/api/start").get_json()["number"] == 1


def test_html_assets_cookie_and_cache(client):
    assert b"Blackbox Vision Challenge" in client.get("/").data
    assert client.get("/static/script.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200
    response = client.post("/api/start")
    cookie = response.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie
    assert "Expires=" not in cookie
    assert response.headers["Cache-Control"] == "no-store"


def test_shipped_deck_twenty_and_cookie_size():
    path = Path(__file__).resolve().parents[1] / "cards.txt"
    assert len(load_cards(path)) == 20
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key"})
    assert len(app.test_client().post("/api/start").headers["Set-Cookie"]) < 4093
