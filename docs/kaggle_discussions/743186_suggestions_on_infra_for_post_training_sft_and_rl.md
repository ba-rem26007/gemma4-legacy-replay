# Topic 743186: Suggestions on infra for post training, SFT, and RL?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743186
- **Date** : 2026-09-25T06:08:35.794000
- **Votes** : 4 | **Commentaires** : 3

---

### Message #1 — Participant (2026-09-25T06:08:35.793000) [Votes: 4]

How exactly are we supposed to post train? Do we have to do it on our own GPUs (of which I have 64 gb of VRAM, which can't load the full gemma-4-31B-it-qat-q4_0-unquantized model for post-training, which is ~63 gigs of VRAM just to sit on disk), or can we use Kaggle notebooks for it. Furthermore, if we aren't supposed to use Kaggle notebooks for training, can we use QLoRA feasibly without severe degradation, and if we are, are 4x L4's considered sufficient for post training purposes or could more/higher quality compute be provided later on?

---

### Message #2 — Participant (2026-09-30T19:03:22.687000) [Votes: 0]

Usually I would say Google Colab, and Kaggle. 


Guide from unsloth : https://unsloth.ai/docs/models/gemma-4/qat 


You can also test it out without training, helping you optimize quite a bit, on HuggingFace inference endpoints, there's several hosts for this model.

---

### Message #3 — Participant (2026-09-25T14:27:53.970000) [Votes: 0]



---
