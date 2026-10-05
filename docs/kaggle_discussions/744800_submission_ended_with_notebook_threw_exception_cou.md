# Topic 744800: Submission ended with "Notebook Threw Exception": could you check what raised?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744800
- **Date** : 2026-10-01T01:25:17.093000
- **Votes** : 3 | **Commentaires** : 5

---

### Message #1 — Participant (2026-10-01T01:25:17.093000) [Votes: 3]

Hi @ryanholbrook, my submission from notebook notebook35c2b989ac (version DMV4, submitted on 1 Oct) ended with "Notebook Threw Exception" and no score. Its commit run succeeded (91 s), and in that run validate_directory, validate_single_declared_model and compile_submission (wheelhouse v25) all passed. The same notebook design scored on 28, 29 and 30 Sep; this version only changed prompt text.


Could you check what raised in this run, and whether it was on the scorer side (for example during today's patches)? If so, a rerun would be much appreciated. Thanks!!

---

### Message #2 — Participant (2026-10-01T01:56:50.953000) [Votes: 1]

Same here: submission 56729291 (2026-10-01 00:07 UTC) ended with "Your notebook hit an unhandled error while rerunning your code". No adapters. It's a self-contained notebook (bundle embedded, no input datasets) that writes /kaggle/working/submission.zip. The notebook run completes normally, and the zip is valid (agent.yaml at the root; it passes validate_directory and compile_submission with wheelhouse v25). The failure came about 4–7 min after submitting, likely before vLLM had finished starting. The same bundle is running fine through the official Evaluator on Kaggle 4×L4. Could you check what raised, and rerun it or restore the allowance if it was on the scorer side? Thanks!

---

### Message #3 — Participant (2026-10-05T10:12:25.607000) [Votes: 0]

+1 same here

---

### Message #4 — Participant (2026-10-05T06:27:55.333000) [Votes: 0]

+1 Same here for submitting the submission.zip

---

### Message #5 — Participant (2026-10-01T01:55:45.103000) [Votes: 0]



---
