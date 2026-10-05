# Topic 744319: How well do your CV and LB correlate?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744319
- **Date** : 2026-09-29T11:32:01.507000
- **Votes** : 10 | **Commentaires** : 5

---

### Message #1 — Participant (2026-09-29T11:32:01.507000) [Votes: 10]

I plotted my CV against the public LB.








CV
LB




0.18
0.05


0.19
0.06


0.23
0.12


0.24
0.10



Higher CV does not seem to translate into a higher LB. How well do your CV and LB correlate?

---

### Message #2 — Participant (2026-09-30T14:38:39.473000) [Votes: 1]

I'm seeing a similar mismatch: in my small set of experiments, the configuration with the highest CV score actually had the lowest public LB score.


Dataset



- 38 tasks from the Rich repository (not the full public dataset)

- Only tasks where the none/gold controls behave as expected

- Limited to Rich for now, since I couldn't get reliable controls for other repositories in my local grading environment


Setup



- Generation: Kaggle Notebook with 4× L4 GPUs

- Grading: official verifier in Docker (ARM64), run locally


Scores





CV
Public LB




0.211
0.10


0.237
0.08


0.316
0.03


0.289
0.05

---

### Message #3 — Participant (2026-09-30T02:34:45.340000) [Votes: 1]

My agent reached ~0.2 in the local validation, but when it came to LB, it dropped to < 0.12. Haven't made any progress for a week.

---

### Message #4 — Participant (2026-09-29T12:22:30.460000) [Votes: 2]

Congrats to your good correlation!
Which data did you use to calculate CV?

---

### Message #5 — Participant (2026-09-29T12:26:41.770000) [Votes: 2]

Thanks! Just the official dataset.

---
