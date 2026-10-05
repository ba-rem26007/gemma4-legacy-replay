# Topic 745059: include_thoughts currently disables reasoning instead of only hiding it [adk_submission 0.2.12]

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745059
- **Date** : 2026-10-02T00:48:44.099000
- **Votes** : 3 | **Commentaires** : 2

---

### Message #1 — Participant (2026-10-02T00:48:44.100000) [Votes: 3]

Hi organizers,


Thanks for fixing reasoning persistence and `thinking_budget` forwarding. I found a remaining semantic mismatch in `adk_submission 0.2.12`.


Google’s `ThinkingConfig` defines:



- `thinking_budget`: controls the reasoning-token budget.

- `include_thoughts`: controls whether generated thoughts are included in the response.


vLLM separately uses `enable_thinking` to control whether Gemma 4 generates reasoning at all.


However, the current bridge maps:



```
include_thoughts: false
        ↓
enable_thinking: false
        ↓
no reasoning generated

```

Therefore, this configuration does not provide private reasoning:



```
thinking_config:
  thinking_budget: 4096
  include_thoughts: false

```

Because thinking is disabled, the positive budget is effectively unused. Competitors can currently choose between:



- No reasoning.

- Reasoning generated, returned, and retained during tool-call continuations.


There is no mode that generates reasoning for the current inference while omitting it from subsequent request context.



## Why this matters

Gemma’s prompt-formatting documentation recommends preserving thoughts within a function-calling turn, so stripping them is not necessarily better. However, long coding-agent tool chains can accumulate reasoning and approach the 32K context limit. Separate controls would let competitors evaluate that tradeoff.


Could the harness expose separate controls for:



- Whether reasoning is generated.

- Whether reasoning is returned by the inference server.

- Whether returned reasoning is retained in subsequent ADK requests.


At minimum, could `include_thoughts: false` avoid setting `enable_thinking: false`, so that the configuration above means “generate reasoning, but do not return it”?



## Potential implementation

A minimal fix appears possible in the `adk-submission` package, primarily in:


`adk_submission/resolvers/generation.py`



In `apply_thinking_config_to_model()`, derive vLLM’s `enable_thinking` only from `thinking_budget` or `thinking_level`. Do not use `include_thoughts` to disable generation:



- `thinking_budget > 0` → `enable_thinking: true`

- `thinking_budget <= 0` or `thinking_level: none` → `enable_thinking: false`

In `install_litellm_reasoning_patch()`, handle `include_thoughts` independently on the response path:



- `include_thoughts: true` → preserve reasoning parts.

- `include_thoughts: false` → remove `Part(thought=True)` before the response enters ADK session history.

- Always preserve visible text, function calls, usage metadata, errors, and final-response metadata.


This would support all three configurations:



```
# 1. No reasoning
thinking_config:
  thinking_budget: 0
  include_thoughts: false

# 2. Reasoning generated and retained
thinking_config:
  thinking_budget: 4096
  include_thoughts: true

# 3. Reasoning generated but not retained
thinking_config:
  thinking_budget: 4096
  include_thoughts: false

```

Thanks!

---

### Message #2 — Participant (2026-10-03T09:08:31.697000) [Votes: 0]

Thanks for reporting this, I also found this issue this afternoon when I was reviewing "metric/gemma-4-developer-agent-wheelhouss/adk_submission-0.2.12-py3-none-any.whl/adk_submission/resolvers/generation.py", hope your suggestion can be supported promptly.

---
