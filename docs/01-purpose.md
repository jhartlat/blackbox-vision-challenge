# 01 · Purpose: make a small system understandable

## The problem, decomposed

A learner wants to practice Python concepts on a phone. Instead of starting with Flask, divide the problem into six questions:

1. Where do the questions come from? A UTF-8 text file.
2. Is that input usable? Validate each line and the whole collection.
3. Which question and choices should appear? Shuffle cards and sample distractors.
4. How does the phone receive them? An HTTP request and JSON response.
5. How does a choice become a decision? Send selected text back to Python.
6. How does a decision become a result? Add one for a correct answer; calculate a percentage.

**Data lens:** the author owns raw text; Python owns validated cards and quiz decisions; the browser owns the visible page and the user's pending selection. Text becomes tuples, a dictionary, JSON, DOM text, then a decision. Each layer consumes the output of the previous layer.

## Settled decisions and why they matter

| Decision | Reason and consequence |
|---|---|
| One `Question|Answer` per line | Readable without a spreadsheet or database; `|` cannot occur in either field. |
| Ignore blanks and full-line comments | Authors can organize the file without creating cards. |
| Trim surrounding whitespace | Accidental formatting should not become part of an answer. |
| At least four cards | One correct answer requires three other distinct answers. |
| Answers unique using `casefold()` | Case-only differences cannot masquerade as distinct choices. |
| Fail startup on malformed input | Fix bad source data before any learner sees an incomplete quiz. |
| Use all cards, shuffled once | One simple quiz length; each card is visited exactly once. |
| Three distractors from this file | No external service and no invented distractors. |
| Shuffle four choices | Correct answer has no fixed button position. |
| Python scores; JavaScript displays | The browser's submitted score is never authoritative. |
| Approximately one-second feedback | Small interaction loop without a manual Next button. |
| Final score and percentage only | No leaderboard, results history, analytics, or extra results workflow. |
| Signed session cookie | Temporary per-browser state without adding a database or shared memory service. |
| Flat `app.py`, small pure helpers | Show responsibility boundaries without introducing architecture frameworks. |
| Flask + Gunicorn on Render | Local development and a documented production-server path. |

Questions need not be unique under the supplied rules: each **card** appears once. If an author repeats question text with different answers, the text can appear twice; the author should avoid ambiguous prompts. Answer uniqueness is mandatory.

## Deliberately excluded

Databases, authentication, accounts, OAuth, payments, complex APIs, durable storage, custom quiz lengths, tracking, and saved scores. A cookie holding temporary progress is not an account or a persistent score database. It is still client-side state, with honest limits documented in chapter 04.

## Build incrementally: six checkpoints

These are exercises and a reconstruction path, not a claim of historical Git commits.

1. **Read:** implement `read_lines()` and print the list of strings. Check that newline characters survive.
2. **Parse and validate:** ignore comments/blanks, split, trim, and reject invalid lines. Run validation tests before any web code.
3. **Build one question:** take a tuple, name its fields, sample three other answers, shuffle four choices. Verify the original cards are unchanged.
4. **Play in Python:** shuffle indexes, evaluate one selected string, advance position, update score. State on paper should match state in code.
5. **Connect Flask:** expose start/question/answer operations. Inspect JSON in the browser's Network panel. Notice the answer key is not a response field.
6. **Present and deploy:** render buttons with `textContent`, prevent double clicks, add feedback and error recovery, test a whole quiz, then deploy.

At each checkpoint ask: What data exists? Who owns it? What shape is it? Who transforms it? Who consumes it? Do not add the next layer until the current data contract is clear.

## Completion criteria

All file validation tests pass. A complete quiz visits each card once, offers four distinct choices, scores correct/wrong answers accurately, and ends with a percentage. Phone controls work with touch and keyboard. Reload and connection errors are understandable. Invalid content prevents startup. Deployment instructions do not claim a URL is live before it is deployed.
