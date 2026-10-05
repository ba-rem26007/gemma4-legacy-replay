# Topic 743308: VRAM to run Gemma locally

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743308
- **Date** : 2026-09-25T16:08:26.145000
- **Votes** : 1 | **Commentaires** : 3

---

### Message #1 — Participant (2026-09-25T16:08:26.147000) [Votes: 1]

Hello!


What's the minimal amount of memory needed to run inference on a single GPU? Has anyone managed to run it successfully with full context length on 24GB?

---

### Message #2 — Participant (2026-09-26T18:24:37.830000) [Votes: 0]

Depends. Sometimes you can do some RAM offloading. But for 24g, post training is off the table.

---

### Message #3 — Participant (2026-09-25T18:19:35.120000) [Votes: 0]

I'm only figuring things out myself right now, but my 1 day tests are:


On Mac: 26-29 for one agent task at the full 32k context. Local but Kaggle style (4 tasks in parallel) - 70-76 GB.

---
