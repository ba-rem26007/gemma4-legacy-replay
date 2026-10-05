# Topic 744070: Can the scoring server load Gemma 4 LoRA adapters?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744070
- **Date** : 2026-09-28T14:36:22.378000
- **Votes** : 1 | **Commentaires** : 2

---

### Message #1 — Participant (2026-09-28T14:48:48.127000) [Votes: 1]

We're using a patched version of vLLM 0.19, updated in the wheelhouse recently. You might try re-downloading or updating your wheelhouse dataset if you haven't recently. The getting started notebook appears to show it working.

---

### Message #2 — Participant (2026-09-28T14:36:22.377000) [Votes: 1]

The rules explicitly permit PEFT LoRA adapters on `gemma-4-31b-it-qat-w4a16-ct`, but the published wheelhouse contains vLLM 0.19.1. Starting that required model with the sample's `adapter: main_lora` produces `ValueError: Gemma4ForConditionalGeneration does not support LoRA yet` before inference. vLLM's tagged 0.19.1 implementation does not implement `SupportsLoRA` for this class. Does the private scoring service use a different vLLM build or another adapter-serving path? Could you confirm a minimal adapter-bearing sample can be scored, or publish a compatible wheelhouse? This determines whether LoRA training is usable for this track.

---
