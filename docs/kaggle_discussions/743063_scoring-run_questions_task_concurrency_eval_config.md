# Topic 743063: Scoring-run questions: task concurrency, eval_config keys, and the 12 h limit

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743063
- **Date** : 2026-09-24T19:22:17.197000
- **Votes** : 6 | **Commentaires** : 9

---

### Message #1 — Participant (2026-10-01T23:23:11.230000) [Votes: 1]

@ryanholbrook do we have control on adaptive budget like out of 12 hours, i wnat 1 task to take 8 minutes, otehr to take 4 minte. This adaptive control in our hand extremely crucial or do you have your own time. Please answer this as soon as possible.

---

### Message #2 — Participant (2026-09-24T19:48:21.303000) [Votes: 6]

- Sequentially.

- The scorer reads those, and only those, four fields. The default is no limit.

- Currently, hitting the 12-hour limit will error, but I'm planning on a fix that will score unfinished tasks as 0. You may want to set `max_time_minutes` to something moderate as a failsafe.

---

### Message #3 — Participant (2026-09-28T17:05:39.793000) [Votes: 1]

Hi @ryanholbrook , a follow-up on this:



  Currently, hitting the 12-hour limit will error, but I'm planning on a fix that will score unfinished tasks as 0.



Is this fix live yet? I'd also like to raise a side effect that concerns me.


Right now, going over 12 hours errors the whole submission, and I've hit that couple days ago. So every team has to fit all ~120 tasks into the limit. And part of my research in this competition so far has been about this optimization. With unfinished tasks scored as 0, a submission could instead spend most of the 12 hours on say the first 30-40 tasks and never start the rest. The tasks are clearly hard for the model, so a lot more time per task might solve more of those early tasks than a run that gives every task an equal share.



- Is "solve as many tasks as possible within 12 hours, however the time is split" the intended goal, or should a good submission attempt every task?

- Do tasks run in the same order every time, and are public and private tasks mixed through that order? If the public tasks come first, a submission that only reaches the early tasks could look strong on the public leaderboard and then collapse on the private one.

- If this isn't intended, would you consider a required per-task time cap, or some other way to reward attempting every task? For example, instead of giving 0 to unattempted tasks they receive some negative score.

---

### Message #4 — Participant (2026-10-05T17:02:11.177000) [Votes: 0]

this is a valid argument but even if there is a situation where one decided to spend time on fewer tasks and let rest go to zero, the winning chances are lower in that case.

---

### Message #5 — Participant (2026-09-29T12:23:27.320000) [Votes: 0]

hi @ryanholbrook, do you have any update on scoring unfinished tasks as 0?

---

### Message #6 — Participant (2026-09-29T12:38:23.663000) [Votes: 0]

Hey @ryanholbrook 
Scoring unfinished tasks as 0 and accepting the submission would be a great fix!
Please do provide an update

---

### Message #7 — Participant (2026-10-03T09:34:34.953000) [Votes: 0]

- The scorer reads those, and only those, four fields. The default is no limit.

  - Currently, hitting the 12-hour limit will error, but I'm planning on a fix that will score unfinished tasks as 0. You may want to set `max_time_minutes` to something moderate as a failsafe.

  

I have made a couple of submissions for which the time taken to evaluate crossed the 12h limit and still scored successfully(IDs 56667603 and 56701670). The submission I made yesterday, however, ended in an error after crossing 12hrs. Can you fix this bug?

---

### Message #8 — Participant (2026-10-04T15:29:51.190000) [Votes: 0]

Hi @ryanholbrook , following up on this thread, since several of us are planning our time budgets around the 12-hour limit:



- Has the change to score unfinished tasks as 0, rather than erroring the entire submission, been deployed? If so, from what date or scorer version does it apply? If not, is it still planned?



- A participant reported two submissions that ran past 12 hours and still received scores, and another that errored after 12 hours. Is that expected under the current system? Could differences in how elapsed time is measured or the submissions are processed explain these outcomes?



- Are hidden tasks run in the same order for every submission? Are public- and private-leaderboard tasks interleaved or grouped?




Until we hear back, we'll plan for the entire run to finish within 12 hours and attempt every task. Thanks!

---

### Message #9 — Participant (2026-09-24T19:22:17.197000) [Votes: 6]

Hi hosts, thanks for releasing the wheelhouse! Three questions about the scoring run that affect how we budget time per task:



- Are hidden tasks evaluated sequentially or with some concurrency? If concurrent, how many tasks can run at once, and is that configurable?



- Which fields of `eval_config.yaml` does the scorer actually read? In particular, are `timeout_seconds`, `max_tool_calls`, `max_time_minutes`, and `max_turns` all supported, and what defaults apply when the file or individual fields are omitted?



- If a submission reaches the 12-hour global limit, how are unfinished tasks handled? Are they scored as failures, or does the submission itself terminate/error?

---
