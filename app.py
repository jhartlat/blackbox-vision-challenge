"""A small, readable quiz: file -> cards -> payload -> click -> score."""
import hashlib
import os
import random
import secrets
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session


def read_lines(filepath):
    """File input: read a UTF-8 file into a list of strings."""
    with open(filepath, encoding="utf-8") as file:
        return file.readlines()


def parse_lines(lines):
    """Parsing: ignore blank/comment lines; retain source numbers for errors."""
    parsed = []
    for number, line in enumerate(lines, start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        parsed.append((number, [part.strip() for part in text.split("|")]))
    return parsed


def validate_cards(parsed):
    """Validation: evaluate split values, raising ValueError on bad input."""
    seen_answers = set()
    for number, values in parsed:
        if len(values) != 2:
            raise ValueError(f"Line {number}: expected exactly one | separator.")
        question, answer = values
        if not question or not answer:
            raise ValueError(f"Line {number}: question and answer must not be empty.")
        normalized = answer.casefold()
        if normalized in seen_answers:
            raise ValueError(f"Line {number}: answers must be unique (case-insensitive).")
        seen_answers.add(normalized)
    if len(parsed) < 4:
        raise ValueError("Quiz needs at least 4 cards for 3 distinct distractors.")


def load_cards(filepath):
    """File-input coordinator: read, parse, validate, then make card tuples."""
    parsed = parse_lines(read_lines(filepath))
    validate_cards(parsed)
    return [(values[0], values[1]) for _, values in parsed]


def build_question(card):
    """Transformation: a two-value card becomes a named internal question."""
    return {"question": card[0], "answer": card[1]}


def build_choices(cards, correct_index):
    """Transformation: choose three other answers and shuffle four choices."""
    other_indexes = [i for i in range(len(cards)) if i != correct_index]
    indexes = random.sample(other_indexes, 3) + [correct_index]
    random.shuffle(indexes)
    return indexes


def check_answer(selected, correct):
    """Evaluation: return a Boolean, never trust a browser-supplied score."""
    return selected == correct


def update_score(score, correct):
    """Scoring: return a new score without changing the input."""
    return score + (1 if correct else 0)


def calculate_percentage(score, total):
    """Scoring: return a percentage rounded to one decimal place."""
    return round(score / total * 100, 1)


def create_app(config=None):
    """Composition: configure Flask and validate the deck before serving."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        CARDS_FILE=Path(__file__).with_name("cards.txt"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("RENDER") == "true",
        MAX_CONTENT_LENGTH=4096,
    )
    if config:
        app.config.update(config)
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Set SECRET_KEY before starting (see README.md).")
    cards = load_cards(app.config["CARDS_FILE"])
    # Detect a changed deck after a deployment rather than score against new cards.
    deck_version = hashlib.sha256(repr(cards).encode()).hexdigest()[:16]

    def new_quiz():
        """Transformation/state: shuffle card indexes once for this quiz."""
        order = list(range(len(cards)))
        random.shuffle(order)
        return {"order": order, "position": 0, "score": 0,
                "choices": build_choices(cards, order[0]),
                "token": secrets.token_urlsafe(12), "deck": deck_version}

    def display_data(quiz):
        """Transformation: project internal state into a public payload."""
        if quiz["position"] == len(cards):
            return {"complete": True, "score": quiz["score"], "total": len(cards),
                    "percentage": calculate_percentage(quiz["score"], len(cards))}
        question_data = build_question(cards[quiz["order"][quiz["position"]]])
        return {"complete": False, "question": question_data["question"],
                "choices": [cards[i][1] for i in quiz["choices"]],
                "number": quiz["position"] + 1, "total": len(cards),
                "score": quiz["score"], "token": quiz["token"]}

    def current_quiz():
        """Validation: reject a missing session or a session from an old deck."""
        quiz = session.get("quiz")
        if not quiz or quiz.get("deck") != deck_version:
            return None
        return quiz

    @app.get("/")
    def index():
        """Presentation/communication: send the HTML shell."""
        return render_template("index.html")

    @app.post("/api/start")
    def start():
        """Communication: create a quiz and return its first display payload."""
        session["quiz"] = new_quiz()
        return jsonify(display_data(session["quiz"]))

    @app.get("/api/question")
    def question():
        """Communication: read the current question without advancing."""
        quiz = current_quiz()
        if quiz is None:
            return jsonify(error="Start a new quiz to continue."), 409
        return jsonify(display_data(quiz))

    @app.post("/api/answer")
    def answer():
        """Communication: validate input, evaluate, update state, send feedback."""
        quiz = current_quiz()
        if quiz is None:
            return jsonify(error="Start a new quiz to continue."), 409
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get("selected"), str):
            return jsonify(error="Send JSON with a selected answer string."), 400
        if quiz["position"] >= len(cards) or data.get("token") != quiz["token"]:
            return jsonify(error="This question has already changed. Reload to continue."), 409
        selected = data["selected"]
        if selected not in [cards[i][1] for i in quiz["choices"]]:
            return jsonify(error="Choose one of the four displayed answers."), 400
        question_data = build_question(cards[quiz["order"][quiz["position"]]])
        correct = check_answer(selected, question_data["answer"])
        quiz["score"] = update_score(quiz["score"], correct)
        quiz["position"] += 1
        quiz["token"] = secrets.token_urlsafe(12)
        if quiz["position"] < len(cards):
            quiz["choices"] = build_choices(cards, quiz["order"][quiz["position"]])
        # Reassign: Flask notices this change and signs an updated cookie.
        session["quiz"] = quiz
        return jsonify(correct=correct, score=quiz["score"])

    @app.after_request
    def prevent_cache(response):
        """Communication: do not cache per-browser quiz responses."""
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    return app


app = create_app()
