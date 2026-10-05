# Topic 743056: Gemma4 allowed variant

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743056
- **Date** : 2026-09-24T19:01:33.990000
- **Votes** : 0 | **Commentaires** : 5

---

### Message #1 — Participant (2026-09-24T20:27:21.040000) [Votes: 0]

It says in www.kaggle.com/competitions/gemma-4-developer-agent/overview/model-selection-budget-and-harness-rules :



  At present, we only support the gemma-4-31b-it-qat-w4a16-ct Gemma 4 model variant. You must choose this model for every agent and subagent.



The idea is not that you upload your own model/checkpoint. You must upload a LoRA that is applied to this model.

---

### Message #2 — Participant (2026-09-25T11:37:02.453000) [Votes: 0]

Harness file says, any one of the below variants can be used. We can't use 2 different variants.


"All agents in a submission must declare at most ONE unique base model (len(models) == 1). Declaring two different base models (e.g., gemma-4-31b-it in the root agent and gemma-4-9b-it in a sub-agent) raises ParticipantVisibleError."


gemma-4-31b-it-qat-w4a16-ct (Starter Kit default)
gemma-4-31b-it, gemma-4-31b
gemma-4-27b-it, gemma-4-27b
gemma-4-26b-a4b-it, gemma-4-26b-a4b, diffusiongemma-26b-a4b-it
gemma-4-12b-it, gemma-4-12b
gemma-4-9b-it, gemma-4-9b
gemma-4-e4b-it, gemma-4-e4b
gemma-4-e2b-it, gemma-4-e2b

---

### Message #3 — Participant (2026-09-25T11:39:41.150000) [Votes: 0]

I'm also not sure now. Is the overview section correct or the Harness md file? @elanlearns

---

### Message #4 — Participant (2026-09-25T13:37:58.260000) [Votes: 3]

It's only the one model listed in the Overview. We're working on supporting others.

---

### Message #5 — Participant (2026-09-24T19:01:33.990000) [Votes: 0]

Hello! Are all Gemma 4 variants allowed in this competition, including E2B and E4B, or must participants use a specific version?
I have a laptop with an RTX 4050 and 16 GB of RAM. Does the competition provide any free GPU/TPU resources or training credits?
Are quantized models and LoRA/QLoRA fine-tuning allowed?
Thank you!

---
