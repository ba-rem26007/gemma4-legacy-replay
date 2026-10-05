# Topic 743752: Query regarding scorer config

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743752
- **Date** : 2026-09-26T19:39:36.364000
- **Votes** : 1 | **Commentaires** : 1

---

### Message #1 — Participant (2026-09-26T19:39:36.363000) [Votes: 1]

Hi Ryan, two quick questions about the scoring run, because the README and the Getting Started notebook differ:



- Events compaction: HARNESS_README §7.2 says `metric/scoring.py` uses `EventsCompactionConfig(compaction_interval=15, overlap_size=2, token_threshold=32768, event_retention_size=5)`; the Getting Started notebook uses `token_threshold=14336`. Which value does the scorer use today? Also, does it pass `default_chat_template_kwargs` (e.g. `{'enable_thinking': True}`) to vLLM, as the notebook does?

- Sandbox: does the scorer run tasks in the Docker backend (and under gVisor/runsc?) or the subprocess backend the notebook uses?

---
