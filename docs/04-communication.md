# 04 · Communication: phone ↔ Flask

**Data lens:** the server owns the answer key and scoring logic. The browser owns a pending selection and rendered DOM. JSON moves display data outward and selected text inward. A signed cookie transports temporary quiz progress between requests; it is not a database or account.

## Three small endpoints

| Request | Input | Successful response | State change |
|---|---|---|---|
| `GET /` | None | HTML shell | None |
| `POST /api/start` | Empty JSON object from UI | First question payload | New shuffled quiz replaces old one |
| `GET /api/question` | Session cookie | Current question or final result | None |
| `POST /api/answer` | `{"selected":"…","token":"…"}` | `{"correct":true,"score":3}` | Score, position, token, next choices |

There are no external APIs. These are simply routes inside the same Flask app. `fetch()` sends same-origin cookies automatically. `jsonify()` serializes dictionaries; `request.get_json(silent=True)` parses submitted JSON or returns `None` for malformed/non-JSON input.

## One complete exchange

1. Page loads and asks for current question.
2. If no compatible quiz exists, server returns 409; the page POSTs start.
3. Server shuffles all card indexes once and returns question 1 with four choices.
4. User taps a choice. JavaScript immediately disables all buttons and sends selected text plus the current token.
5. Server checks session/deck, body type, token, and membership in offered choices. It looks up the answer itself; a submitted `score` or `correct` field is ignored.
6. Server evaluates, increments score if appropriate, advances one position, prepares next choices, and signs a new session cookie.
7. UI says Correct or Incorrect. About 1 second later it GETs the next display payload.
8. After the last answer, that GET returns the final score and percentage.

[Sequence diagram](diagrams/request-sequence.md)

## Temporary state without persistent storage

```python
{
    "order": [2, 0, 3, 1],
    "position": 1,
    "score": 1,
    "choices": [2, 0, 1, 3],
    "token": "random-current-question-token",
    "deck": "fingerprint-of-validated-cards"
}
```

This four-card example is a **Flask session**, not an authenticated user. The cookie is non-permanent (no application-set expiration date), but browsers may restore session cookies after closing. Refresh retains progress. Cookies are per browser profile, not per tab. There is no database, server-memory session registry, score file, analytics, or application history.

The server's `SECRET_KEY` signs the cookie. A visitor can read its contents, but cannot ordinarily edit it and produce a valid signature without the key. Signing is **not encryption**. The question payload omits the answer field, but the source deck is public and cookie indexes are readable. This is not an anti-cheating system.

### Honest limitations, rather than extra architecture

- **Small decks:** signed cookies have browser size limits (roughly 4 KB). The supplied 20-card deck is comfortably small. The order list grows with larger decks; thousands of cards are outside this teaching design. Do not silently assume arbitrary file sizes will work.
- **Sequential duplicate clicks:** the UI busy flag disables repeat clicks. A repeated old token with the latest cookie gets 409 and cannot advance again.
- **Concurrent/replayed requests:** two requests carrying the same old signed cookie can both be evaluated. A visitor can replay an earlier valid cookie; multiple tabs can overwrite progress. There is no exactly-once server registry. Do not use this design for assessed exams or valuable scores. Adding such guarantees would require a different scoped state architecture.
- **Deck changes:** validated-card fingerprint mismatch returns 409 and the UI begins a new quiz. Restart the service after editing the file. Do not change the deck midway through a graded session, which this project does not support anyway.
- **Secret changes:** old cookies become invalid and a new quiz starts. All Gunicorn workers must share the same environment key. No hardcoded fallback key is included.

## Errors and recovery

- Invalid content file: startup fails, with a line-specific error where applicable. Do not silently skip malformed content.
- Missing `SECRET_KEY`: startup fails with setup guidance.
- Missing/old session: 409, start a fresh quiz.
- Malformed JSON, wrong selected type, or non-offered choice: 400; score/position unchanged.
- Old token or already-complete quiz: 409; score/position unchanged.
- Oversized request body: Flask rejects it (413); UI offers reload if it cannot decode an error body.
- Network failure: show a recovery button. **Do not automatically retry POST /api/answer** because it may already have reached the server. Reload asks for current state. If the response cookie never arrived, the old question may remain; that is another small-session limitation, not a promise of transaction recovery.

API responses use `Cache-Control: no-store`. Cookies are HttpOnly and SameSite=Lax; on Render they are Secure. No cross-origin CORS access is enabled. These defaults help a small app, but this repository is not a comprehensive web-security course.

Official reference: [Flask sessions](https://flask.palletsprojects.com/en/stable/quickstart/#sessions).
