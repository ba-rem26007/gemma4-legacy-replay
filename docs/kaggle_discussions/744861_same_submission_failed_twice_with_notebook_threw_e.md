# Topic 744861: Same submission failed twice with "Notebook Threw Exception" within minutes (Sep 30 and Oct 1), no adapters

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744861
- **Date** : 2026-10-01T08:10:21.082000
- **Votes** : 2 | **Commentaires** : 2

---

### Message #1 — Participant (2026-10-01T08:10:21.083000) [Votes: 2]

Hi @ryanholbrook,


Our submission failed twice with "Notebook Threw Exception", both times within a few minutes, well before vLLM could have finished loading. The API reports both as COMPLETE with no score:



- 2026-09-30 20:41 UTC (ID: ): failed about 3 minutes in.

- 2026-10-01 07:42 UTC (ID: ): the exact same zip from the same notebook version, failed about 1 minute in.


Both come from notebook darovalos/g4-agent-submit, version 2.


What we checked on our side:



- The notebook only decodes an embedded submission.zip, verifies its sha256 and writes /kaggle/working/submission.zip. It runs without accelerator or internet. Its code and kernel metadata are identical to version 1, which scored normally on Sep 28.

- The bundle differs from that scored one only in prompt text and YAML comments. It ships no adapters, and eval_config.yaml sets only the four supported keys.

- The same zip compiles with adk-submission and ran 40 public tasks end to end with swegemma's Evaluator in a 4x L4 notebook on Sep 30.


The first failure matches the timing of the scorer changes you mentioned that day (wheelhouse v25, LoRA parameters sized per submission, the reasoning_content fix). Since our bundle has no adapters, could the LoRA sizing produce an invalid vLLM config when there are none? Only a guess.


Could you check the logs and, if the cause is on the scoring side, rerun them? Is a CPU-only submission notebook like ours still supported? And is the change that scores unfinished tasks as 0 at the 12 h limit already live?


Thanks!

---

### Message #2 — Participant (2026-10-01T12:44:51.030000) [Votes: 0]

Same here, is there any way to find out what is behine "Notebook Threw Exception"?

---
