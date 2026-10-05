# Topic 745998: Note on Code Graphs for Async Functions

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745998
- **Date** : 2026-10-05T17:37:49.016000
- **Votes** : 0 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-05T17:37:49.017000) [Votes: 0]

There have been a number of discussion posts pointing out that `async def` functions are not included in the code graph tools. This is true and is an issue for some of the public tasks in fastapi and httpx. 


However, it is not an issue for any of the private repo tasks. 


None of the private repo tasks touch any functions defined with `async def`. Additionally, `async def` functions are rare within the private repos as a whole, at most 1.8% of functions. 


As a result, we will not be doing an update to the private tasks' code graphs.

---
