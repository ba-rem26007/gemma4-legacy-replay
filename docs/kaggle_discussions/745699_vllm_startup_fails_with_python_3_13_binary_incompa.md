# Topic 745699: vLLM Startup Fails with Python 3.13 Binary Incompatibility

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745699
- **Date** : 2026-10-03T19:03:06.431000
- **Votes** : 4 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-03T19:03:06.430000) [Votes: 4]

I’m getting a ServerStartupError when starting the vLLM server in the Gemma 4 Developer Agent competition environment.


Link: https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent/notebook


The error is:


ImportError: …/vllm/_C.abi3.so: undefined symbol: _ZN3c1013MessageLoggerC1EPKciib


My environment is using Python 3.13.15 and vLLM 0.19.1 from the competition wheelhouse.


It looks like there may be a compatibility issue between the vLLM wheel, PyTorch, and Python 3.13.


Could someone please confirm whether the competition is expected to run on Python 3.12 or lower, and if so, how we can use that Python version in Kaggle?

---
