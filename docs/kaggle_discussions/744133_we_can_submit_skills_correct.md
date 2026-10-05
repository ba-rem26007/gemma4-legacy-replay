# Topic 744133: We can submit skills correct ?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744133
- **Date** : 2026-09-28T18:58:01.396000
- **Votes** : 0 | **Commentaires** : 4

---

### Message #1 — Participant (2026-09-28T19:19:31.903000) [Votes: 1]

Yes. See www.kaggle.com/competitions/gemma-4-developer-agent/overview/evaluation


Each skill is a folder under skills/ containing a SKILL.md.

---

### Message #2 — Participant (2026-09-30T01:58:53.737000) [Votes: 0]

whats stopping someone from putting up a whole submission bloated with skills

---

### Message #3 — Participant (2026-09-30T07:53:16.997000) [Votes: 1]

Nothing stops it: the harness allows up to 1,000 skills, 50 MiB each, within the 3 GiB limit. That said, the ADK puts every skill's name and description into each model call, so a large library will eat through the 32k context window fast and trigger compaction sooner.

---

### Message #4 — Participant (2026-09-28T18:58:01.397000) [Votes: 0]

can anyone answer this question?

---
