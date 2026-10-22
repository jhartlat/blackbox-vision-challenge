# Primary data-flow diagram

```mermaid
flowchart TD
    A["cards.txt · text"] --> B["load_cards() · read, parse, validate"]
    B --> C["cards · list of tuples"]
    C --> D["build_question()"]
    D --> E["question_data · internal dictionary"]
    C --> F["build_choices() · four indexes"]
    E --> G["Flask / display_data() · remove answer field"]
    F --> G
    G --> H["JSON · network payload"]
    H --> I["HTML / DOM · interface"]
    I --> J["User Click"]
    J --> K["selected_answer · string + token"]
    K --> L["Flask · validate request"]
    L --> M["check_answer() · Boolean"]
    M --> N["update_score() · score"]
```

Text equivalent: `cards.txt → load_cards() → cards → build_question() → question_data → Flask → JSON → HTML → User Click → selected_answer → Flask → check_answer() → score`.

The author owns raw text. Python owns validated cards and evaluates answers. The browser owns the DOM and pending click. Each arrow is a handoff, not necessarily a network call: only Flask↔browser crosses HTTP. The answer field stays out of the public display payload.
