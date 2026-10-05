# Topic 743383: Rules: Only LORA allowed?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743383
- **Date** : 2026-09-25T20:22:57.264000
- **Votes** : 1 | **Commentaires** : 6

---

### Message #1 — Participant (2026-09-25T20:33:42.767000) [Votes: 2]

Our evaluation system in this competition is only able to accept LoRA adapters.

---

### Message #2 — Participant (2026-09-25T20:38:06.733000) [Votes: 0]

So If I pre-train and post-train a 120B coder variant of gemma 4 you would not allow it into the competition?

---

### Message #3 — Participant (2026-09-26T00:16:50.423000) [Votes: 1]

I'm a competitor but here are the Gemma Docs on tuning. Using Lora with swappable heads is likely the best path.

---

### Message #4 — Participant (2026-09-26T04:22:24.427000) [Votes: 0]

I have my own methods ive been working on for about a year now. I can provide weights.

---

### Message #5 — Participant (2026-09-26T11:46:00.320000) [Votes: 1]

It's not against the rules per se, it's just that our system isn't configured to run it. For one, we don't have the GPUs. The system is configured to accept LoRA adapters, so if you tried to submit it, the script would just throw an error. We chose to accept LoRA adapters to allow some amount of finetuning while also keeping submission file sizes moderate and for being more accessible under the hardware people are likely to have access to.

---

### Message #6 — Participant (2026-09-25T20:22:57.263000) [Votes: 2]

Hello! I was curious whether the rules allow only LoRA adapters, or whether we can use other methods as long as the base model is the correct one?


thanks

---
