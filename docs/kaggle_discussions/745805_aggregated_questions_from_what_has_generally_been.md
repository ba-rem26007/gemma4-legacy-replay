# Topic 745805: Aggregated questions from what has generally been asked on the forum : HOSTS ANSWER PLEASE

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745805
- **Date** : 2026-10-04T14:19:41.162000
- **Votes** : 1 | **Commentaires** : 2

---

### Message #1 — Participant (2026-10-04T14:19:41.163000) [Votes: 1]

Answers to the following questions will clear up most uncertainties me and a lot of other participants have been facing. @ryanholbrook Is it possible to get accurate answers to these questions soon? I'll really appreciate it.


1) Is the fix that scores unfinished tasks as 0 at the 12-hour limit live now? If a submission exceeds 12 hours today, does the whole submission still error?


2) Which EventsCompactionConfig does the scorer use today (token_threshold, compaction_interval, overlap, retention)? Do you plan to change it before the final deadline, for example to keep tool results in the summary?


3) In swegemma/harness/verification.py the verification pytest call uses timeout=config.harness.command_timeout_seconds, which is the submission's eval_config.yaml timeout_seconds. Does the scorer apply our timeout_seconds to the hidden verification run? If so, a correct patch on a task whose test files are slow could be scored as failing. Is that intended?


4)Does the scorer's Docker sandbox run under gVisor (runsc) or runc? Is there a rough figure for command overhead compared with a plain container?


5)Is the private leaderboard score taken from the same scoring run as the public score, or are the two selected final submissions re-run (the code mentions a rerun/ layout)?


6) Does the 12-hour limit include vLLM server start-up?


7)Would you consider publishing per-submission aggregate counts (tasks that hit the time limit, context-overflow errors, sandbox errors), with no task identities, so that participants can budget time without guessing?


8)You mentioned possibly supporting other Gemma 4 variants. Will any of them be allowed as sub-agent models before the deadline, or is the 31B QAT model final?

---

### Message #2 — Participant (2026-10-05T16:02:03.723000) [Votes: 0]

//-- answers to 1 (is the 12-hour overrun now scored as 0 for unfinished tasks?), 2 (which compaction settings does the scorer use?) and 3 (does our `timeout_seconds` apply to the hidden verification run?) decide how every team sets its limits. --//


Two more status questions, if you can confirm them in the same reply:



- Is the fix for the test-file reset (#744825, edits to existing test files making `test_patch` fail to apply) live on the scorer?

- Is the fix for an undeclared or misnamed tool call ending the task (#745028) live on the scorer?


Thanks for the work on this,
Mugur B.

---
