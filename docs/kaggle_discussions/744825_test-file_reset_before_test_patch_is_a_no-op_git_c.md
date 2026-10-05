# Topic 744825: Test-file reset before test_patch is a no-op (git checkout aborts on missing pathspecs)

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744825
- **Date** : 2026-10-01T04:44:53.597000
- **Votes** : 2 | **Commentaires** : 2

---

### Message #1 — Participant (2026-10-01T18:06:11.787000) [Votes: 2]

Addressing now.

---

### Message #2 — Participant (2026-10-01T04:44:53.597000) [Votes: 2]

Hello @ryanholbrook 


Summary
`verify_task` should reset agent-modified test/config files before applying `test_patch` (HARNESS_README, "Anti-Tampering Test & Config Reset"). In practice nothing gets reset.
Cause
swegemma 0.2.7 (wheelhouse v28), `harness/verification.py` ~L389-412:

```
git checkout HEAD -- <files_to_reset> 2>/dev/null || true

```


- `files_to_reset` always includes `sitecustomize.py`, `usercustomize.py` and `_swegemma_stubs.py`. These live in site-packages, not in `/workspace` HEAD.

- `git checkout` aborts the whole command if any pathspec doesn't match, and the error is swallowed.

- `git clean -f` still runs, so only added files are removed. Edits to existing test files survive.


Effect
If the agent edits an existing test file, `test_patch` fails to apply. The task is then scored as failed even when the source fix is correct:

```
Failed to apply test_patch: ... Reversed (or previously applied) patch detected

```

Seen locally on public tasks, e.g. fastapi_14077 and fastapi_14492. Re-verifying the same patches with the test-file hunks stripped makes them resolve. The Docker path runs the same code.


Repro



```
git init -q r && cd r && echo a > t.py && git add t.py && git commit -qm init
echo b > t.py
git checkout HEAD -- t.py sitecustomize.py; echo $?   # error: pathspec 'sitecustomize.py' did not match ...; 1
cat t.py                                              # b (not restored)

```

Suggested fix
Check out only the paths that exist in HEAD:

```
cd /workspace && git ls-tree -r -z --name-only HEAD -- <files_to_reset> | xargs -0 -r git checkout HEAD --

```

Thanks!

---
