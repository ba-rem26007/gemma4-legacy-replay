# Topic 743663: How much of the submission runtime is excluded as patch validation?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743663
- **Date** : 2026-09-26T10:43:31.500000
- **Votes** : 2 | **Commentaires** : 3

---

### Message #1 — Participant (2026-09-26T11:24:41.307000) [Votes: 1]

IIRC, patch validation takes around two hours if a patch is submitted for every task. If no patch is submitted for a task, then validation is skipped and that task just scores 0. A "no patch" submission only takes about ten minutes.

---

### Message #2 — Participant (2026-09-26T11:29:27.233000) [Votes: 0]

Thanks, that’s very helpful!

---

### Message #3 — Participant (2026-09-26T10:43:31.500000) [Votes: 2]

I understand that the runtime shown for a Kaggle submission is the total wall-clock time, while the 12-hour agent limit includes sandbox setup but excludes patch validation.

Is there any estimate of how much time patch validation typically takes across the full test set? I’m trying to understand roughly how much of the total submission runtime does not count toward the 12-hour limit, so I can estimate what total wall-clock runtime is still safe.

---
