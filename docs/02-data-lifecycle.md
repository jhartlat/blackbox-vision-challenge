# 02 · Data lifecycle: follow one value

The central idea is movement and transformation, not a directory tour. The examples use two cards to keep the page readable; a runnable file still needs **at least four**.

[Primary diagram](diagrams/data-flow.md)

## 1. Raw data → text

```text
print()|Displays output
len()|Returns length
```

The author owns this text in `cards.txt`. It is a string sequence on disk. No function has changed it. `read_lines()` consumes it.

## 2. File input → list of strings

```python
["print()|Displays output\n", "len()|Returns length\n"]
```

`read_lines()` uses `open()` and `readlines()`. Python now owns this in-memory list. Newlines are still present. `parse_lines()` consumes it. Reading is a side effect; it does not validate meaning.

## 3. Parsed data → split values

Conceptually:

```python
[["print()", "Displays output"], ["len()", "Returns length"]]
```

The actual program also retains line numbers for actionable errors:

```python
[(1, ["print()", "Displays output"]), (2, ["len()", "Returns length"])]
```

`parse_lines()` strips surrounding whitespace, ignores empty/full-comment lines, and splits on `|`. Python owns these `(line_number, values)` pairs. `validate_cards()` consumes them. Parsing is transformation, not proof of validity.

## 4. Validation → valid or error

```text
Valid -> continue
Error -> raise ValueError and stop startup
```

`validate_cards()` evaluates field count, empty fields, case-insensitive answer uniqueness, and minimum card count. It returns `None` on success or raises `ValueError` on failure. It does **not** transform the input into a different collection. `load_cards()` consumes the success/error outcome.

## 5. Quiz data → card tuples

```python
[("print()", "Displays output"), ("len()", "Returns length")]
```

After validation, `load_cards()` removes diagnostic line numbers and converts the two values into a tuple. The Flask application owns the read-only `cards` list for its lifetime. `new_quiz()`, `build_question()`, and `build_choices()` consume it. Neither scoring nor rendering edits the source cards.

## 6. Question data → named internal fields

```python
{"question": "len()", "answer": "Returns length"}
```

`build_question(card)` transforms a positional tuple into a dictionary with named fields. Python owns this short-lived internal dictionary. `display_data()` consumes the question field; the answer route consumes the answer field for evaluation. The entire dictionary is **not** sent to the browser.

## 7. Display data → public payload

```python
{
    "complete": False,
    "question": "len()",
    "choices": ["Returns length", "Displays output", "Defines function", "Creates loop"],
    "number": 3, "total": 20, "score": 2,
    "token": "opaque-current-question-token"
}
```

`build_choices()` samples three **other card indexes**, adds the correct index, and shuffles the four indexes. `display_data()` looks up their answer strings and adds progress metadata. Python owns the dictionary until `jsonify()` consumes it. There is no `answer` key or correct-choice marker. The example choices illustrate the shape, not the exact supplied deck's wording.

## 8. JSON response → network data

```json
{"complete":false,"question":"len()","choices":["Returns length","Displays output","Defines function","Creates loop"],"number":3,"total":20,"score":2,"token":"opaque-current-question-token"}
```

Flask's `jsonify()` serializes the Python dictionary as JSON. The server sends an HTTP response. The browser's `response.json()` consumes the bytes and produces a JavaScript object. Python `False` becomes JSON `false`; the network does not transmit a Python object itself.

## 9. Rendered HTML → interface

```html
<h1>len()</h1>
<button>Returns length</button>
```

`render()` consumes the JavaScript object, creates DOM elements, and assigns `textContent`. The browser owns the DOM; the learner consumes it visually or through assistive technology. CSS changes appearance, never scoring. No file content is inserted as raw HTML.

## 10. User response → user input

```json
{"selected":"Returns length","token":"opaque-current-question-token"}
```

The learner owns the choice. `submit()` wraps its string with the current-question token; `JSON.stringify()` serializes it. Flask's `request.get_json()` reads the request into a Python dictionary. The server checks type, offered-choice membership, and question token. The extra token distinguishes a stale click from an answer to the current question.

## 11. Result → decision, then progress

```python
True
```

`check_answer()` compares the selected string with the server's answer. `update_score(2, True)` produces `3`. Python advances the session position, prepares the next choices, and returns feedback:

```json
{"correct":true,"score":3}
```

The browser displays Correct, waits about one second, and requests the next question. At completion Python returns:

```json
{"complete":true,"score":16,"total":20,"percentage":80.0}
```

The final page consumes only the score, total, and percentage, headed Quiz Complete. No score is written to disk.

## The parallel state path

A browser-session cookie carries an ordered list of card indexes, current position, score, current choice indexes, token, and deck fingerprint. Flask signs it after each update. The browser transports it automatically on same-origin requests. The signature guards against ordinary tampering, **not reading or replay**. See chapter 04 before treating this design as an exam system.
