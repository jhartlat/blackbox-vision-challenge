# 05 · Presentation: make the data usable on a phone

**Data lens:** Flask sends a display dictionary as JSON. JavaScript owns a parsed object, transforms it into DOM elements, and the browser renders them. CSS consumes elements and changes layout. The learner consumes the interface and supplies one selected string. Neither CSS nor DOM text owns the answer key.

## Responsibilities

- `templates/index.html`: semantic main area, heading, progress, choice container, live feedback, and hidden recovery control.
- `static/style.css`: responsive widths, readable contrast, large tap targets, focus outlines, wrapping, and reduced-motion preference.
- `static/script.js`: fetch JSON, assign text, create four buttons, send a selection, show feedback, and fetch the next question.
- `app.py`: choose content, validate answers, score, and decide completion.

JavaScript is necessary only for this small request/display loop and its one-second delay. There are no frontend frameworks, build tools, routing libraries, client-side answer keys, or storage APIs.

## Question view

```text
Question 3 of 20                  Score: 2

What does len() return?

[ The number of items             ]
[ Key-value pairs                 ]
[ An ordered mutable collection   ]
[ A function definition           ]

Correct
```

Choices use native buttons, not clickable paragraphs. Controls are at least 56 CSS pixels high. A maximum reading width keeps desktop views comfortable, while a viewport meta tag and fluid layout support narrow screens. Long questions/answers wrap instead of overflowing.

## Click and focus

The first click locks all choices immediately. The selected button remains visibly marked. Text says **Correct** or **Incorrect**, so color is never the only feedback. A polite status region announces the message. After approximately one second (browser timers are not exact), the next payload is rendered and focus moves to the question heading. The final heading also receives focus.

A one-second automatic advance is a deliberate MVP rule, not ideal for every reading speed or assistive-technology user. A configurable or manual advance would be a future accessibility scope change, not a hidden extra feature here. The app honors reduced-motion preferences for decorative transitions, but keeps the required quiz timing.

## Completion

```text
Quiz Complete
16 / 20
80%
```

Only result information appears in the results panel. Progress controls and answer buttons are removed. No leaderboard, history, analytics, or restart button is added. The page's brand header remains.

## Error states

The page starts with a loading heading. If communication fails, it displays a clear message and a Reload quiz button. Reload requests state rather than resending an uncertain answer. If JavaScript is disabled, a `noscript` message explains why this interaction cannot run.

Content uses `textContent`, not `innerHTML`, so a card containing `<script>` is shown as text. Keep question writing clear and concise; code must never be evaluated from a card.

## Manual acceptance checklist

- At 320 px and 390 px widths, no horizontal scrolling; choices remain large and readable.
- Tab reaches each enabled answer; Enter/Space selects it.
- Two rapid clicks do not skip a question in the ordinary browser flow.
- One correct and one wrong answer produce the expected score and message.
- Reload shows the current question, with the same choices and order.
- Simulate offline mode; see an error and recovery control, not silent scoring.
- Finish all cards; see only score/percentage in the final panel.
- A second browser profile has independent progress; a second tab intentionally shares it.

Automated Python tests cover the protocol. A browser check must exercise the JavaScript too; API tests alone cannot prove the timer, layout, or focus behavior.
