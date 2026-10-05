# Topic 745775: Missing FastAPI test dependencies in the evaluation sandbox

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745775
- **Date** : 2026-10-04T10:32:37.239000
- **Votes** : 3 | **Commentaires** : 3

---

### Message #1 — Participant (2026-10-04T10:32:37.240000) [Votes: 3]

## Summary

During local evaluation of the supplied tasks, some FastAPI tests failed during collection because `inline-snapshot` and `dirty-equals` were unavailable in the test container.


These packages are imported by existing tests in the supplied repository snapshots. We want to confirm the official environment requirements before installing a local workaround.


This report describes a local reproduction. It does not establish that the official Kaggle evaluation environment has the same issue.



## Reproduction environment


- Model: `gemma-4-31b-it-qat-w4a16-ct`.

- Evaluation: local evaluation harness with Docker sandbox.

- Sandbox image: `swebench-sandbox:latest`, built from the project's `docker/Dockerfile.sandbox`.

- Container Python: 3.13.

- Tasks and repository snapshots: supplied competition data.


The Dockerfile does not explicitly install either package. Other repository dependencies are installed through the evaluation setup; the question is whether that setup should also provision these test dependencies.



## Example 1: fastapi_14978

Test collection includes `tests/test_tutorial/test_body/test_tutorial001.py` and fails with:



```
from inline_snapshot import snapshot
ModuleNotFoundError: No module named 'inline_snapshot'

```

The supplied `snapshots/fastapi_14978.tgz` contains a `pyproject.toml` that declares:



```
"dirty-equals >=0.9.0",
"inline-snapshot >=0.21.1",

```

The test's import is present in the repository snapshot; it was not introduced by the agent patch.


This task also reports separate implementation errors, such as an unsupported `strict_content_type` argument. Those errors should not be attributed to missing dependencies. Installing the packages alone would not establish that the task is solved.



## Example 2: fastapi_14356

Test collection fails in `tests/test_tutorial/test_header_param_models/test_tutorial003.py`:



```
from dirty_equals import IsDict
ModuleNotFoundError: No module named 'dirty_equals'

```

This import is also present in the supplied repository snapshot.



## Observed impact

The evaluator cannot complete the selected tests when collection fails on these imports. Missing packages can therefore obscure whether an implementation patch is correct.


A test exit code of 2 is not sufficient to identify a dependency problem: other tasks also fail collection because of incomplete implementations. The examples above are identified by their explicit ModuleNotFoundError messages.



## Questions for the organizers


- Does the official Kaggle evaluation environment already include these dependencies?

- Should the harness automatically install each repository's test dependencies? If so, which setup step should we check locally?

- Is there a supported dependency manifest or wheel bundle for reproducing the official environment?

- If these packages are also missing in official evaluation, could the environment or setup instructions be updated?



## Workaround status

We have not installed these packages as a workaround for these evaluation runs. We want local evaluation to match the official environment before changing the sandbox.



## Local evidence

These paths are local evidence references, not public download links. Relevant excerpts can be attached to the Kaggle report.



- `results/summary.json`: per-task test output for this experiment.

- `results/logs/tests/`: saved test output files.

- Project `snapshots/fastapi_14978.tgz`: dependency declarations and existing test import.

- Project `snapshots/fastapi_14356.tgz`: existing test import.

- Project `docker/Dockerfile.sandbox`: base sandbox installation.


No credentials or API authentication data are included in this report.

---

### Message #2 — Participant (2026-10-05T17:59:10.723000) [Votes: 0]

Confirming this from a local host trial. Initial exploration, not exhaustive.


Run:
four fastapi tasks died in Phase 2 collection with `ModuleNotFoundError: No module named 'inline_snapshot'` (fastapi_14246, fastapi_14262, fastapi_14266, fastapi_14978).
The public `wheels/` set (124 wheels) is missing several test-only deps. I resolved the full test-dependency closure for fastapi/requests/rich into a supplemental wheel directory and verified in a sandbox-like py3.13 venv (install --no-deps, then `pytest --collect-only`):


fastapi : 2648 tests collected, 0 errors
  requests:  633 tests collected, 0 errors; a real `httpbin` fixture test passes
  rich    :  788 tests collected, 1 error (`pkg_resources`, setuptools 82+ removed it;
            that file is outside the required test nodes)
Missing distributions that had to be added: inline-snapshot, asttokens, executing, typing-extensions, dirty-equals, sqlmodel (+SQLAlchemy, greenlet), flask (+werkzeug, blinker), anyio/trio (+outcome, sortedcontainers), PyJWT, pyyaml, pwdlib (+argon2-cffi, cffi), python-multipart, itsdangerous, ujson, orjson, email-validator (+dnspython), uvicorn[standard] (+uvloop, httptools, watchfiles, websockets, python-dotenv),
fastapi-cli, pydantic-settings, pydantic-extra-types, pytest-httpbin (+httpbin), trustme, PySocks, attrs.
Caveat: initial exploration on a subset of tasks, not an exhaustive audit of all 129.

---

### Message #3 — Participant (2026-10-04T14:04:30.363000) [Votes: 0]

Update: 35 tasks were affected by missing test dependencies

---
