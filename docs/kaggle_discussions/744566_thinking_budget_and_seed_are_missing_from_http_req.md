# Topic 744566: thinking_budget and seed are missing from HTTP requests in my wheelhouse test

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744566
- **Date** : 2026-09-30T10:12:12.580000
- **Votes** : 1 | **Commentaires** : 4

---

### Message #1 — Participant (2026-09-30T10:12:12.580000) [Votes: 1]

Hi organizers,


I found a possible problem with thinking_budget and seed. I tested the packages from the official wheelhouse v25 in a Kaggle CPU notebook.


I used a short message, the same in every test. The request went through the installed adk_submission thinking-config bridge, Google ADK and LiteLLM. A small local HTTP server recorded the final request and returned a fixed reply. I did not load Gemma or run the full scoring process.


Packages: adk-submission 0.2.11, google-adk 1.36.1, google-genai 2.11.0, litellm 1.82.4 and openai 2.32.0.


Results:



- thinking_budget=4096 and thinking_budget=1024 produced the same HTTP body. Neither request included a numeric thinking budget.

- seed=1234 and seed=4321 also produced the same HTTP body. The seed field was missing.

- As a check, changing max_output_tokens from 8192 to 4096 changed max_completion_tokens in the request.

- Changing include_thoughts from true to false changed chat_template_kwargs.enable_thinking correctly.


All seven test cases completed successfully. This test checks what the client sends. It does not prove that the hidden scorer uses exactly the same path. It also does not test whether vLLM applies a budget after receiving it.


In the code I checked, the bridge handles include_thoughts and thinking_level, but not thinking_budget. The ADK conversion also does not pass seed. The upstream vLLM 0.19.1 API has fields named seed and thinking_token_budget.


This seems separate from the loss of thoughts between tool calls discussed here: https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744354


Could you please clarify:



- Does the scoring environment pass these two parameters to vLLM?

- If not, could the harness pass seed and map thinking_budget to thinking_token_budget? Could you also check that the server can apply the limit correctly for Gemma?

- Will the planned reasoning patch cover this issue too, or does it need a separate fix?


Thank you for your help!

---

### Message #2 — Participant (2026-09-30T15:52:50.227000) [Votes: 0]

Hi @veronikayaitskikh,


Thanks for the heads up. I will patch.

---

### Message #3 — Participant (2026-09-30T19:10:59.720000) [Votes: 0]

How we can reproduce that patch in our systems?

---

### Message #4 — Participant (2026-09-30T19:59:18.313000) [Votes: 0]

The most recent wheelhouse dataset should have the patches.

---
