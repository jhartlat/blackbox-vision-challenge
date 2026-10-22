# One-question communication sequence

```mermaid
sequenceDiagram
    actor Learner
    participant Browser
    participant Flask
    participant Cards as Validated cards
    Browser->>Flask: GET /api/question + cookie
    Flask->>Cards: Read current card and choice indexes
    Flask-->>Browser: JSON question, choices, progress, token
    Learner->>Browser: Tap an answer
    Browser->>Browser: Disable buttons
    Browser->>Flask: POST /api/answer {selected, token}
    Flask->>Cards: Look up correct answer
    Flask->>Flask: Evaluate, score, advance
    Flask-->>Browser: JSON correctness + updated signed cookie
    Browser->>Learner: Correct / Incorrect
    Browser->>Browser: Wait about one second
    Browser->>Flask: GET /api/question
    Flask-->>Browser: Next question or final score
```

On the first visit, a missing quiz returns 409, so the browser first POSTs `/api/start`. A refresh only GETs current state. An uncertain failed POST is never automatically resent. No database participates in this sequence.
