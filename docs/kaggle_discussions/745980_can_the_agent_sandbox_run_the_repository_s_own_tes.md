# Topic 745980: Can the agent sandbox run the repository's own tests?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745980
- **Date** : 2026-10-05T15:56:50.322000
- **Votes** : -2 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-05T15:56:50.323000) [Votes: -2]

Hi @ryanholbrook,

we’d like to clarify whether the environment where the agent works is expected to be able to run the repository’s own tests.
You mentioned in #742882 that the private grading sandbox uses a different dependency set from the public one, and that the hidden tasks validate 100% with gold patches. So we understand that the final validation environment can run a correct solution.


What we’re less clear about is the environment where the agent actually investigates and develops that solution.


In the public data, all FastAPI tasks currently get Starlette 1.6.0. But the FastAPI snapshots themselves require Starlette below 1.0; 38 of the 67 tasks specify <0.51.0.


With Starlette 1.6.0, even creating FastAPI() fails with:


Router.init() got an unexpected keyword argument 'on_startup'


That means the agent can’t run the project’s tests to evaluate its own changes, regardless of whether its patch is correct. When we keep Starlette below 1.0, the reference fixes work again; we’ve checked this on eight FastAPI tasks in Docker.


Pls, could you clarify two things?



- In the actual scorer, does the agent’s working sandbox use dependencies compatible with the task repository, like the final validation environment does?

- Could the public wheels/ selection be adjusted to respect the dependency constraints of each repository snapshot, so results on the public FastAPI tasks are representative?


Thanks!
Mugur B.

---
