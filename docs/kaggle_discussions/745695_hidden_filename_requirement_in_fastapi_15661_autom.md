# Topic 745695: Hidden filename requirement in `fastapi_15661` (“Automate release preparation”)

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745695
- **Date** : 2026-10-03T18:43:03.286000
- **Votes** : 0 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-03T18:43:03.287000) [Votes: 0]

Hello @ryanholbrook 


I’m investigating the `fastapi_15661` task at base commit `1990ecb` (https://github.com/fastapi/fastapi/tree/1990ecb446d4db044e8f2be26758aa42b2c62fa8). The visible request is “Automate release preparation” and refers to Asyncer PR #608 (https://github.com/fastapi/asyncer/pull/608), but the agent environment is offline.


The base commit contains a release-date script, release notes, and publishing workflows. It does not contain `scripts/prepare_release.py` or `tests/test_prepare_release.py`. After my agent submitted a workflow-based patch, verification failed during test collection:



```
from scripts.prepare_release import (...)
ModuleNotFoundError: No module named 'scripts.prepare_release'

```

The original FastAPI PR #15661 (https://github.com/fastapi/fastapi/pull/15661) did add `scripts/prepare_release.py`, but that exact module name is not specified in the visible request or present in the base repository. An agent could guess it from the title; it cannot establish that the hidden tests require it from local evidence.


Is this task intended to require reproducing the referenced PR’s file-level interface? If so, could the task include the required module or command name, or make the relevant reference available offline? That would let agents work toward the behavior the tests actually check without revealing the tests themselves.

---
