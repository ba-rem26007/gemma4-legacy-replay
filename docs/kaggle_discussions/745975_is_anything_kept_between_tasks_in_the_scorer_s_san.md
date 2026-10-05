# Topic 745975: Is anything kept between tasks in the scorer's sandbox, and may a submission rely on it?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745975
- **Date** : 2026-10-05T15:41:41.512000
- **Votes** : -1 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-05T15:41:41.513000) [Votes: -1]

Hi @ryanholbrook  -  could you clarify how container reuse works in the actual scorer?


The Overview describes a “persistent Docker container”, while HARNESS_README describes warm pooling with reuse_containers=True: after a task, /workspace, /tmp and /var/tmp are wiped before the container is returned to the pool. In swegemma 0.2.7, ContainerManager.stop also wipes /root, and reuse_containers defaults to False.


A few things that are not clear to us:



- Does the scorer actually run with reuse_containers=True, so the same container may be used for multiple tasks?

- If it does, should we nevertheless assume that every task starts from a completely clean environment? In particular, could anything written outside the directories being wiped survive into the next task?

- Most importantly, are submissions allowed to make use of any state that happens to survive between tasks, or should submissions be designed not to rely on this at all?


We don’t want to build around behavior that is merely an implementation detail — or that would be considered outside the intended rules.
Thanks!
Mugur B.

---
