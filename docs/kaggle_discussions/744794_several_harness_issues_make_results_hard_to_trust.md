# Topic 744794: Several harness issues make results hard to trust: request for fixes and a status update

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744794
- **Date** : 2026-10-01T00:38:13.461000
- **Votes** : 3 | **Commentaires** : 3

---

### Message #1 — Participant (2026-10-01T14:51:52.190000) [Votes: 1]

- I'll look into the compaction issue.

- The KV-cache drop with LoRA should be addressed. Now vLLM will set its LoRA params dynamically based on what you actually submit. Submitting fewer adapters with lower rank (or no adapters) leaves more memory for KV-cache.

- KV-cache, double-encoded tool output, thoughts dropped, and thinking_budget / seed not sent are all fixed in the latest wheelhouse.

- Hard to estimate as it depends on the tool and how the model responds. You could experiment in a notebook on the training set to try to get estimates.

---

### Message #2 — Participant (2026-10-02T12:38:05.897000) [Votes: 0]

Hi Ryan, 
Is there a way to higher the compaction threshold ? like reduce max output. For now it's 14k on starter submission, I guess same setup on eval. 
Thank you

---

### Message #3 — Participant (2026-10-01T00:38:13.463000) [Votes: 3]

Several harness issues make results hard to trust: request for fixes and a status update


While testing locally with the official wheels, we ran into several problems that come from the scoring environment, not from the agent:



- Compaction loses tool results. The ADK summary keeps only text parts, and Gemma-4 rarely writes text next to its tool calls. So after compaction the model loses its context, and it often repeats its last call until it times out.

- LoRA on 4×L4. Enabling LoRA reduces the KV cache a lot, and long requests hang (#744331). This makes any adapter risky to submit.

- Double-encoded tool output (#744272). This makes many edit_file calls fail with "old_string not found".

- Thoughts dropped between tool calls (#744354), and thinking_budget / seed not sent (#744566).

- No way to measure speed. We cannot measure the scorer's real speed, so choosing max_time_minutes is a guess. A wrong guess either cuts solvable tasks or risks the 12-hour limit.


What we are asking for:



- Include tool calls and short tool results in the compaction summary, or keep the last few tool results as they are.

- Fix the KV-cache drop with LoRA, or tell us it will stay as it is.

- Confirm which of the fixes above are live in the scorer now, and whether earlier submissions will be re-scored.

- Share the approximate time per model call on 4×L4, so we can set time limits safely.


Thanks for the work on the competition.

---
