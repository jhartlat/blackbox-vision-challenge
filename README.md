# Blackbox Vision Challenge

A phone-friendly Python quiz that teaches **how data moves**, not just how to make a web page.

**Status:** source code and a Render deployment recipe. This repository does not claim a live deployment. `https://quiz-app.onrender.com` in the original brief is an illustrative address, not an address reserved or deployed by this project. Render assigns the actual URL after deployment.

## Start here

Requires Python 3.12. Use a terminal inside this folder:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
flask --app app run
```

Windows PowerShell activation and environment variable:

```powershell
.venv\Scripts\Activate.ps1
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
flask --app app run
```

Open `http://127.0.0.1:5000`. Keep the key stable while running the app; a new key resets browser sessions. Never commit a real key. `.env.example` is illustrative; this app does not automatically load `.env` files.

For a phone on the **same trusted Wi-Fi**, run `flask --app app run --host=0.0.0.0`, then open `http://YOUR-COMPUTER-LAN-IP:5000` on the phone. Your firewall must permit it. Do not expose the Flask development server to the internet or enable its debugger for this test.

Run checks:

```bash
python -m pytest -q
```

## The small product

- All 20 supplied Python cards, shuffled once per quiz.
- Four shuffled answers: one correct and three sampled from other cards.
- Question number, current score, a question, and large answer buttons.
- Correct/Incorrect feedback, then the next question after about one second.
- Final score and percentage only. No leaderboard, accounts, analytics, or saved history.
- Refresh resumes the current question (or completed result). Clear this site's cookies or use a private browser session to begin again. There is intentionally no extra restart button on the final screen.

## Follow the data

```text
cards.txt -> load_cards() -> cards -> build_question() -> question_data
 -> Flask -> JSON -> HTML -> User Click -> selected_answer
 -> Flask -> check_answer() -> score
```

1. [Purpose, scope, and incremental build](docs/01-purpose.md)
2. [Data lifecycle: every shape, owner, and consumer](docs/02-data-lifecycle.md)
3. [Processing categories and function contracts](docs/03-processing.md)
4. [Requests, responses, and session state](docs/04-communication.md)
5. [Presentation and phone interaction](docs/05-presentation.md)
6. [Deploy to Render and verify](docs/06-deployment.md)

[Architecture diagram](docs/diagrams/data-flow.md) · [Request sequence](docs/diagrams/request-sequence.md)

## Change the questions

Edit `cards.txt`, then restart the server. Use exactly `Question|Answer` on each content line. Blank lines and lines beginning with `#` (after whitespace) are ignored. Inline comments are not supported. Whitespace around fields is trimmed. Each answer must be unique ignoring case. At least four cards are required. An empty field, extra delimiter, missing delimiter, or duplicate answer causes a clear startup error with a line number where applicable.

This is a small-deck teaching app, not an exam platform. It uses Flask's signed, **readable** session cookie for temporary progress. No database or score file exists. Cookie size, simultaneous tabs, and replay limitations are explained in [communication](docs/04-communication.md). Do not use it for grades or sensitive information.

## Repository map

```text
app.py                       Python functions and Flask communication
cards.txt                    Teacher-owned question source
requirements*.txt            Runtime and test dependencies
templates/index.html         Semantic page skeleton
static/style.css             Mobile presentation
static/script.js             Send selections and render responses
docs/01-purpose.md ...       Learning path organized by data lifecycle
docs/diagrams/               GitHub-rendered Mermaid + text descriptions
tests/                       File validation and full quiz-flow checks
render.yaml                  Optional deployment blueprint
.github/workflows/tests.yml  Automated tests on GitHub
```

No license is selected. Public visibility alone does not grant an open-source license; the owner can choose one later.
