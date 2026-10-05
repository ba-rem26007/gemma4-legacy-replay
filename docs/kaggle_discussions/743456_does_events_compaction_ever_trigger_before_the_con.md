# Topic 743456: Does events compaction ever trigger before the context limit?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743456
- **Date** : 2026-09-26T04:45:36.125000
- **Votes** : 1 | **Commentaires** : 1

---

### Message #1 — Participant (2026-09-26T04:45:36.127000) [Votes: 1]

Hi team, quick question on HARNESS_README §7.2 — EventsCompactionConfig sets token_threshold = 32,768, which matches max_model_len. Since every request already has to fit prompt + max_output_tokens inside that same 32,768-token window, is there a code path where compaction fires before a session hits ContextWindowExceededError? Or is the threshold measured against something narrower (e.g. just the events history, not the full request)? Trying to understand whether long agent sessions are expected to self-compact or just need to stay well under the limit on their own. Thanks!

---
