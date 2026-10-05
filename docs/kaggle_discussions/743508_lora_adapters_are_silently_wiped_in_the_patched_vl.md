# Topic 743508: LoRA adapters are silently wiped in the patched vLLM 0.19.1 (Gemma4 decoder layers registered twice)

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743508
- **Date** : 2026-09-26T06:03:03.949000
- **Votes** : 4 | **Commentaires** : 6

---

### Message #1 — Participant (2026-09-26T06:03:03.950000) [Votes: 4]

Tested with the patched vllm 0.19.1 from `metric/gemma-4-developer-agent-wheelhouse` (uploaded 2026-09-25). This is the build whose `gemma4.py` / `gemma4_mm.py` add `SupportsLoRA` to `Gemma4ForConditionalGeneration`. With it, `--enable-lora --lora-modules name=path` starts fine and the adapter is reported as loaded. But the adapter has no effect on the outputs.


Cause


Gemma4Model registers every decoder layer twice:



- once as `language_model.model.layers.N`;

- once through the YOCO alias `language_model.model.self_decoder.decoder_layers.N`. `Gemma4SelfDecoderLayers` keeps a slice of the same `ModuleList` as a submodule, and it is built even when `kv_sharing_fast_prefill` is off.


`LoRAModelManager.activate_adapter` iterates over both names:



- Under `layers.N` it finds the adapter weights and calls `set_lora`.

- Under the alias name the adapter has no weights, so it calls `module.reset_lora(index)` on the same layer object. This wipes the weights it has just set.


Repro



- Take any adapter for `gemma-4-31b-it-qat-w4a16-ct` and set every `lora_B` to large random values (std 1.0).

- Serve it with the patched vLLM and `--enable-lora`.

- Compare the top logprobs for the base model name and the adapter name on the same prompt at temperature 0. They are identical.

- With `VLLM_LOGGING_LEVEL=DEBUG`, the log shows 240 lines of `Successfully loaded LoRA weights for module language_model.model.layers.N...`, followed by 240 lines of `No LoRA weights found for module language_model.model.self_decoder.decoder_layers.N..., skipping.`

- Inspecting the LoRA layers afterwards shows that every `lora_b_stacked` slot is zero.


Possible fixes



- Store `decoder_layers` in `Gemma4SelfDecoderLayers` / `Gemma4CrossDecoderLayers` without registering them as submodules. The patch already does this for `embed_tokens` and the other shared modules via `self.__dict__[...]`.

- Or skip `reset_lora` for a module object that already received weights under another name.


This affects any submission that ships an adapter, because it would score exactly like the base model. It is separate from the earlier "does not support LoRA yet" startup error discussed in https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743213.

---

### Message #2 — Participant (2026-09-29T10:55:16.617000) [Votes: 0]

Following up with a reproduction on the current Wheelhouse, in case it helps.


Setup: Kaggle notebook, GPU L4 x4, Internet off · Wheelhouse dataset version [N] (vLLM 0.19.1) · gemma-4-31b-it-qat-w4a16-ct v2 · adapter = the `sample_submission/adapters/[main_lora]` adapter with its `lora_B` weights replaced by N(0, 1) noise, so any working LoRA path should visibly change the output.


1. Through `adk_submission.VllmServer` (`enable_lora=True, max_loras=8, max_lora_rank=128`, adapter passed via `discover_adapters` → `adapter_manifest`): `/v1/models` lists only the base model, no LoRA entry. With `VLLM_ALLOW_RUNTIME_LORA_UPDATING=True` set before startup, `POST /v1/load_lora_adapter` returns 404.


2. Directly in vLLM, bypassing the server:



```
llm = LLM(model=MODEL_PATH, tensor_parallel_size=4, max_model_len=4096,
          enable_lora=True, max_loras=1, max_lora_rank=128)
sp = SamplingParams(temperature=0, max_tokens=40, logprobs=3)
base = llm.chat(PROMPT, sp)
lora = llm.chat(PROMPT, sp, lora_request=LoRARequest("loud_lora", 1, ADAPTER_PATH))

```

Base and LoRA outputs are identical: same text ("2, 3, 5, 7, 11, 13, 17, 19, 23, 29") and same logprobs. vLLM does handle the request (it logs its LoRA-tokenizer warning), so the adapter seems to load but have no effect.


Caveat: I only randomised `lora_B`. If the sample adapter's `lora_A` is all zeros, that alone would explain it. I'll re-run with both A and B randomised and post the result.


Two questions:



- Is the zeroing fix meant to be in the current Wheelhouse, or only on the scorer?

- Should the harness server list the adapter in `/v1/models` when it's in `adapter_manifest`?


Thanks!

---

### Message #3 — Participant (2026-09-30T14:34:38.550000) [Votes: 0]

- The zeroing fix landed in v23 of the wheelhouse dataset (now on v25). You might check that your notebook has the most recent version.

- Yes, it should. `discover_adapters` expects the submission root, so make sure you're passing that and not the adapter directory.

---

### Message #4 — Participant (2026-09-26T11:19:21.103000) [Votes: 0]

Thanks for the report. I will address.

---

### Message #5 — Participant (2026-09-30T12:53:50.507000) [Votes: 0]

Is there an update on this @ryanholbrook? Appreciate all the help but I think this is a serious bug for anyone attempting to use adapters.

---

### Message #6 — Participant (2026-09-30T14:34:58.417000) [Votes: 0]

It should be fixed in the most recent wheelhouse version, but please let me know if it seems otherwise.

---
