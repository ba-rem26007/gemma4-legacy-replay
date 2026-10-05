# Topic 745977: Context overflow can discard an already-correct patch

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745977
- **Date** : 2026-10-05T15:51:46.969000
- **Votes** : -2 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-05T15:51:46.970000) [Votes: -2]

Hi @ryanholbrook - we ran into a context-window failure that seems to discard work the agent has already completed.


On Kaggle (L4 x4, swegemma 0.2.7, adk-submission 0.2.12, vLLM 0.19.1), while running public task requests_7309, the agent had already made the correct edit. After 20 tool calls, however, the next model request failed with:
'This model's maximum context length is 32768 tokens. However, you requested 8192 output
tokens and your prompt contains at least 24577 input tokens, for a total of at least 32769 tokens.'
The harness then reported ContextWindowExceededError, followed by Error during sandbox execution, and the task finished with exit=-1 and an empty patch.


We were using the compaction settings from the Getting Started notebook (token_threshold: 14336), but the prompt still reached 24,577 tokens.


The practical problem is that with max_output_tokens: 8192, anything above 24,576 input tokens cannot be sent to the model — and if that happens, an otherwise valid working-tree change is lost.


Could the scorer handle this by either:



- compacting and retrying (or reducing the available output-token budget to what still fits), or

- collecting the current working-tree patch when a model error terminates the session, in the same spirit as the timeout fallback?


Also, does the scorer use the same compaction settings as the Getting Started notebook?


This seems related to the failure mode discussed in #745028, where an exception can terminate the task before the working-tree fallback gets a chance to run.


Thanks!
Mugur B.

---
