# Topic 745003: old_string issue

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745003
- **Date** : 2026-10-01T19:21:15.530000
- **Votes** : 0 | **Commentaires** : 2

---

### Message #1 — Participant (2026-10-01T19:50:42.320000) [Votes: 0]

it's an issue with prefix numbers, whitespaces and indentation are already handled automatically


prompt works for this, something along the lines like - "strip any line-number prefixes" (there could be other optimal ways)


there are other causes as well, like - the model is hallucinating if the context grows big enough (a fix can be like - a fresh read before every edit), will need testing for each case

---

### Message #2 — Participant (2026-10-01T19:21:15.530000) [Votes: 0]

hello everyone whenever my agent tries to use edit_file i get the: {'status': 'error', 'error_type': 'FileEditError', 'error_message': "Failed to replace: old_string not found.


Its the only tool that my agent fails to use, all the others seem to work fine except for that one. Is there an issue with the harness or the tools that i dont know about?

---
