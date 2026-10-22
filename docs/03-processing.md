# 03 · Processing: responsibilities and contracts

Functions have jobs, not just names. A function can coordinate more than one category, but its contract should make those boundaries explicit.

**Data lens:** Python owns parsed/validated cards and decisions. Helpers consume values and return new values; route functions consume requests and return responses. JavaScript owns page construction. File I/O, session mutation, HTTP, DOM changes, and random sampling are the explicit effects.

## Categories

| Category | Examples | Purpose |
|---|---|---|
| File input | `open()`, `readlines()`, `read_lines()` | Read data |
| Parsing | `strip()`, `split()`, `parse_lines()` | Transform text |
| Validation | `validate_cards()`, `current_quiz()` | Evaluate correctness |
| Transformation | `build_question()`, `build_choices()`, `display_data()` | Change shape |
| Communication | `jsonify()`, `request.get_json()`, routes, `api()` | Move data |
| Evaluation | `check_answer()` | Make a decision |
| Scoring | `update_score()`, `calculate_percentage()` | Track progress |
| Presentation | `render_template()`, `render()`, `showError()` | Make information perceivable |
| Composition/state | `create_app()`, `new_quiz()` | Connect responsibilities and initialize progress |

## Python function contracts

| Function / category | Purpose | Inputs and shape | Output and shape | Side effects |
|---|---|---|---|---|
| `read_lines(filepath)` / file input | Load source text | Path or path string | `list[str]` | Opens and reads file; may raise an I/O/encoding error |
| `parse_lines(lines)` / parsing | Ignore comments/blanks, trim and split | `list[str]` | `list[tuple[int, list[str]]]` | None |
| `validate_cards(parsed)` / validation | Check format and collection rules | Numbered split values | `None` or raised `ValueError` | Raises clear errors; no input mutation |
| `load_cards(filepath)` / input coordinator | Read, parse, validate, create tuples | Path | `list[tuple[str, str]]` | Reads file; propagates validation errors |
| `build_question(card)` / transformation | Name a card's fields | `(question, answer)` | `dict` with question/answer strings | None |
| `build_choices(cards, correct_index)` / transformation | Sample distractors and shuffle | Card list, integer index | Four distinct integer indexes | Uses random generator; does not mutate cards |
| `check_answer(selected, correct)` / evaluation | Compare strings exactly | Two strings | `bool` | None |
| `update_score(score, correct)` / scoring | Add one or zero | Integer, Boolean | Integer | None |
| `calculate_percentage(score, total)` / scoring | Calculate final percentage | Integers; total is validated >= 4 | `float`, one decimal | None |
| `create_app(config=None)` / composition | Configure app, load deck, register routes | Optional configuration dictionary | Flask application | Reads environment/file; fails startup on invalid content or missing key |
| `new_quiz()` / transformation/state | Shuffle each card index once | Captured card list and deck fingerprint | Quiz state dictionary | Random shuffle, random token; no persistent write |
| `display_data(quiz)` / transformation | Remove answer field; expose display/progress | Quiz state dictionary | Question or final-result dictionary | None |
| `current_quiz()` / validation | Check presence and deck compatibility | Flask session, captured deck fingerprint | Quiz dictionary or `None` | Reads session |
| `index()` / communication/presentation | Serve page shell | GET request | HTML response | Template rendering |
| `start()` / communication/state | Start fresh quiz | POST request | JSON question response | Replaces session quiz |
| `question()` / communication | Read current display | GET request/session | JSON payload or 409 error | Reads session; never advances |
| `answer()` / communication/evaluation/scoring | Validate, check, score, advance | JSON selected string/token, session | Feedback JSON or 400/409 error | Reassigns session, creates token/choices |
| `prevent_cache(response)` / communication | Avoid stale personalized API responses | Flask response | Same response with header | Adds `Cache-Control: no-store` for API paths |

The nested functions capture `cards`; this keeps the validated deck application-local without creating a global mutable quiz for all visitors. `create_app()` is an application factory: a small setup function that also lets tests pass temporary files/configuration.

## Browser function contracts

| Function / category | Purpose | Inputs | Output | Side effects |
|---|---|---|---|---|
| `api(path, body)` / communication | Fetch and decode JSON | Path string, optional object | Promise for a JavaScript object, or error | Sends HTTP request |
| `showError(error)` / presentation | Explain interruption and offer reload | Error object | No return value | Updates live feedback and recovery button |
| `render(data)` / presentation/transformation | Turn payload into text/buttons | Question or result object | No return value | Rebuilds DOM, resets busy flag, focuses heading |
| `submit(selected, token, button)` / communication | Send one click and show feedback | String, string, DOM button | Promise with no result | Disables choices, POSTs, schedules next GET after ~1 second |
| `initialize()` / communication | Resume or start | No explicit input | Promise with no result | GET current state, POST start if absent, render |
| Choice click callback / communication | Forward one selected choice | Browser click event via closure | No return value | Calls `submit()` |
| Choice creation callback / presentation | Create one button | Choice string | No return value | Creates/appends button and listener |
| Disable-button callback / presentation | Lock choices while request runs | DOM button | No return value | Sets `disabled` |
| Timeout callback / communication | Fetch next question after feedback | Timer event | Promise with no result | GET and render or show error |
| Retry click callback / presentation/navigation | Recover by fetching current server state | Click event | No return value | Reloads page; does not blindly resend answer |

## Keep these distinctions clear

- Parsing asks **what pieces are here?** Validation asks **are those pieces allowed?**
- A transformation returns a new representation. An evaluation returns a decision.
- Communication does not make the answer correct; it moves the selection to the evaluator.
- Scoring takes a Boolean, not a DOM element or HTTP request.
- Case-insensitive uniqueness prevents ambiguous answer choices. Actual scoring uses exact strings because valid clicks submit one of the existing offered strings.

## Exercise

Call `build_question(("len()", "Returns length"))` without Flask. Then call `check_answer("Returns length", "Returns length")`. If those functions required a phone, a session, or HTML to work, they would have too many responsibilities.
