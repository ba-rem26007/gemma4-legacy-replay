# Topic 745855: The first task in the list (fastapi_15661) seems unsolvable from the prompt alone: hidden tests import names that appear nowhere in the task

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745855
- **Date** : 2026-10-04T22:19:52.084000
- **Votes** : 7 | **Commentaires** : 2

---

### Message #1 — Participant (2026-10-04T22:19:52.083000) [Votes: 7]

Hi all,


I'd like to check whether others are seeing the same thing, or whether I'm missing something.


The task: fastapi_15661, the first task in the list, so it's the first one every agent tries. The whole problem statement is the title "👷 Automate release preparation", followed by the empty PR template. The only extra hint is a link in the AI disclaimer to a PR in a different repo, which can't be opened because the sandbox is offline.


What the hidden tests require: The test_patch imports a specific module path, a specific set of function and class names, specific CLI subcommands and options, specific environment variable names, and exact error message strings. I'm not going to list them here, but none of them appear in the task text or anywhere in the repo.


What my agent did: It explored the repo, found an existing related script, and wrote a reasonable new script that worked when run. The result:


resolved=False, exit_code=2, patch_chars=3246, tool_calls=27


My understanding is that exit code 2 is pytest stopping at collection, because the module the tests import doesn't exist under that name. I haven't confirmed this inside the harness, so please correct me if that's wrong.


Why this bothers me: Nothing in the prompt or the repo tells the agent what the file, the classes, or the env var prefix must be called. I don't think any prompt or model can get this right except by luck. A correct, working solution with different names scores the same as an empty patch.


Questions:


Have you seen other tasks where the names the tests need appear nowhere in the task text?


Is the benchmark meant to reward guessing names, or is this a gap in the task?


Has anyone found a good way to handle these cases?


Side note: the 5-minute limit was also tight. About 295 s went to 27 tool calls, mostly model generation time.


Thanks!

---

### Message #2 — Participant (2026-10-05T02:02:35.083000) [Votes: 2]

You're reading it right: exit code 2 is pytest stopping at collection on the missing module.


It is not only this task. I checked all 129 public tasks for the same pattern: the tests import a module or name that (a) exists nowhere in the repo at the base commit, (b) is introduced by the reference patch, and (c) is never mentioned in the problem statement.


6 of 129 tasks match:



- fastapi_15661: module scripts.prepare_release and six names in it

- fastapi_15030: module fastapi.sse (EventSourceResponse, ServerSentEvent)

- rich_3930: module rich._unicode_data, plus private names such as _parse_version

- fastapi_14609: PydanticV1NotSupportedError

- fastapi_15785: RouteContext

- fastapi_15745: three private names (e.g. _IncludedRouter)


If I also count identifiers the tests use without importing them (new methods, constants), it is 16 of 129. That count is looser.


In my runs Gemma solved none of the hidden import tasks I can verify locally (0 of 4), against 41 of the other 109. So for local validation I now leave these out: they only add zeros. In a scored run the practical answer is to not spend the time budget on them.


Some names are guessable from convention (fastapi.sse), others are not (a private helper name). The check is static, so treat the list as a lower bound.

---
