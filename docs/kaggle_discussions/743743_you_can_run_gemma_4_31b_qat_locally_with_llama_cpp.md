# Topic 743743: You can run Gemma 4 31B QAT locally with llama.cpp

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743743
- **Date** : 2026-09-26T18:55:06.948000
- **Votes** : 0 | **Commentaires** : 1

---

### Message #1 — Participant (2026-09-26T18:55:06.950000) [Votes: 0]

If you're struggling to run Gemma 4 31B locally due to VRAM requirements, llama.cpp is worth trying.
The QAT model is available as GGUF, and llama.cpp lets you offload part of the model to system RAM when it doesn't fully fit in VRAM. This makes it possible to experiment locally without consuming Kaggle GPU quota.
You can also run it with llama-server, which exposes an OpenAI-compatible API, making it easy to plug into your own agent harness.


Links:



- https://huggingface.co/unsloth/gemma-4-31B-it-qat-GGUF

- https://github.com/ggml-org/llama.cpp


Has anyone else tried this setup for the competition?

---
