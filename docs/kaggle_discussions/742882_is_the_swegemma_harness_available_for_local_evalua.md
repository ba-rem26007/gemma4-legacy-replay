# Topic 742882: Is the swegemma harness available for local evaluation?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/742882
- **Date** : 2026-09-23T21:47:08.957000
- **Votes** : 13 | **Commentaires** : 13

---

### Message #1 — Participant (2026-09-24T10:45:26.967000) [Votes: 10]

Hi @shimondanziger,


Here is a wheelhouse with the packages: Gemma 4 Developer Agent Wheelhouse.


I'll post a notebook later today illustrating how to run everything on Kaggle.

---

### Message #2 — Participant (2026-09-25T14:24:09.787000) [Votes: 0]



---

### Message #3 — Participant (2026-09-23T21:47:08.957000) [Votes: 13]

HARNESS_README.md section 9 shows a local CLI command:
swegemma eval --tasks … --submission-dir starter_kit/sample_submission --sandbox docker
But the dataset has no swegemma, adk-submission, or adk-eval-core package, and no starter_kit folder. It only has docker/, sandbox/setup.py, and wheels/.

- Will these packages be released (pip, GitHub, or a Kaggle dataset)?

If not, what is the recommended way to test a submission locally before submitting?
Thanks!

---

### Message #4 — Participant (2026-09-25T09:59:46.470000) [Votes: 0]

Hi @ryanholbrook, thanks for the wheelhouse! Is the "how to run everything on Kaggle" notebook still coming? Specifically:


Test dependencies: the public wheelhouse lacks some packages the task tests import (e.g. typing-inspection, inline-snapshot, dirty-equals, pytest-httpbin), so gold patches for many FastAPI and Requests tasks can't pass locally. Will the sandbox wheels from the scoring data be published, or should we supply these ourselves?
Sandbox mode: Docker isn't available in Kaggle notebooks. Is --sandbox subprocess the intended way to run swegemma eval there?
Server settings: which vLLM flags does the scorer use (tool/reasoning parser, --default-chat-template-kwargs, kv-cache dtype)?
Thanks!

---

### Message #5 — Participant (2026-09-25T18:42:00.897000) [Votes: 0]

I’m equally waiting. Let me know when you have it

---

### Message #6 — Participant (2026-09-25T18:42:51.693000) [Votes: 1]

It's here: https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent

---

### Message #7 — Participant (2026-09-25T20:39:39.697000) [Votes: 0]

@ryanholbrook 
We're validating the public tasks with `swegemma==0.2.7` using the official Docker verification path and the public competition `wheels/`.
We've hit two environment issues and wanted to confirm whether the private scorer differs:



- FastAPI tasks cannot import because the public wheel set includes Pydantic 2 but not `typing-inspection`. Several tasks also require packages such as `pytest-httpbin`, `inline-snapshot`, or `dirty-equals`, which aren't present in the public wheels.



- `_ensure_container_site_packages` can inject the repository's own released package (for example `requests` or `httpx`) into site-packages. In our checks, that package can shadow `/workspace`; for some Requests tasks the released wheel already contains the fix, so the test passes before applying the gold patch.




Does the private scoring wheel set contain the missing test dependencies? And in scoring, is the task repository's own released package also injected into site-packages, or is `/workspace` expected to take precedence?


We're asking because the task data and gold patches themselves validate cleanly, but these environment differences prevent the public verifier from providing a reliable gold-patch positive control.

---

### Message #8 — Participant (2026-09-26T11:49:05.143000) [Votes: 0]

Hi @irfanparaniya,


Thanks for the report. I will look into it (likely on Monday). For now, I can verify at least that the evaluation metric correctly validates a gold-patch submission at 100%.

---

### Message #9 — Participant (2026-09-26T21:00:50.320000) [Votes: 2]

@ryanholbrook — follow-up with a completed Kaggle reproduction of the public evaluation environment problems.


Thank you for confirming that the evaluation metric validates a gold-patch submission at 100%. We are trying to reproduce reliable reference-patch validation with the released tooling before using it to compare agents.


We ran a private Kaggle CPU notebook, using the unchanged installation cell from your current Getting Started notebook, with the competition data and official wheelhouse attached. The notebook used the released `verify_task` and subprocess sandbox, with no agent, model calls, inference, or competition submission. We ran fresh unpatched/reference controls for six public development tasks without changing patches, verification tests, pytest flags, or scoring expectations.


All 12 controls completed. Only 2 of the 6 reference controls passed:





Public task
Reference result




`fastapi_14786`
Pass: 9 tests


`rich_3043`
Pass: 96 tests


`fastapi_14356`
Collection fails: missing `dirty_equals`


`fastapi_15745`
Collection fails: missing `inline_snapshot`


`requests_7309`
6 failures; the failing traceback executes `/usr/local/lib/python3.12/dist-packages/requests/utils.py`, rather than the patched workspace source


`httpx_3672`
Collection fails because imported `httpx` has no `Stream`; the import probe resolves installed HTTPX rather than workspace source



The returned snapshot hashes for all six tasks, task-data hash, all 124 task-wheel hashes, and the verification/setup source hashes match our local copies. The notebook environment has Python 3.12.13, pytest 8.4.2, Pydantic 2.12.3, Starlette 0.52.1, Requests 2.32.4 and HTTPX 0.28.1. This was the public CPU/subprocess path; we are not claiming the private scorer or the GPU notebook has the same failures.


These failures prevent trustworthy comparisons in the public development environment: a correct reference patch can fail because a package is missing or because the verifier executes an installed distribution instead of the patched repository.


Could you clarify:



- Which supported environment/setup reproduces the successful reference-patch validation you reported? Could its sandbox image digest and complete dependency lock or wheel manifest be provided?

- Should the released setup ensure workspace source (including `src/` layouts) takes precedence over installed repository packages, and supply the missing test dependencies?

- Does private scoring use a different sandbox backend or dependency setup from the released notebook flow?


We can provide the diagnostic script, package/import inventories and hashes. No reference patch text, test bodies, credentials or raw verification logs need to be posted.

---

### Message #10 — Participant (2026-09-27T11:12:58.517000) [Votes: 0]

This may be a problem with the subprocess sandbox. I don't recall seeing these failures using the Docker sandbox. The private Docker sandbox uses the same base image but installs a different set of dependencies because the test issues come from a different set of repos.


I'll look into getting a more reliable setup going in the notebook environment.

---

### Message #11 — Participant (2026-09-28T19:16:11.890000) [Votes: 0]

@ryanholbrook - Did you get a chance to look at this?

---

### Message #12 — Participant (2026-10-03T11:42:13) [Votes: 0]



---

### Message #13 — Participant (2026-09-26T20:59:55.013000) [Votes: 0]



---
