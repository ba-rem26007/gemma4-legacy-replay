# Topic 744259: Reference patches fail for most FastAPI tasks in the public sandbox: are hidden tasks filtered?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744259
- **Date** : 2026-09-29T05:51:35.093000
- **Votes** : 2 | **Commentaires** : 2

---

### Message #1 — Participant (2026-09-29T14:06:43.420000) [Votes: 1]

The tasks in the test set have been more rigorously filtered. I can confirm that a submission with "gold patches" validates at 100%. We will work on improving the training set.

---

### Message #2 — Participant (2026-09-29T05:51:35.093000) [Votes: 2]

Hi @elanlearns 
In the public sandbox (Dockerfile.sandbox plus the public wheel cache, with typing_inspection, h11, blinker and greenlet added), the reference patch passes only 18 of our 40 TRAIN tasks (3 of 23 FastAPI). swegemma injects the newest cached wheels (e.g. Starlette 1.6.0), so older FastAPI commits fail collection, and inline_snapshot, dirty_equals and attrs are missing from the cache. We reproduced this on two hosts. Also, one public task (rich_3468) passes with an empty patch. Are hidden tasks filtered to those whose reference patch passes, and whose empty patch fails, in the scoring environment?

---
