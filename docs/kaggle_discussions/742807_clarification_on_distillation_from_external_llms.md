# Topic 742807: Clarification on distillation from external LLMs

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/742807
- **Date** : 2026-09-23T15:38:32.632000
- **Votes** : 44 | **Commentaires** : 11

---

### Message #1 — Participant (2026-09-29T14:58:14.727000) [Votes: 3]

Hello and thank you for your question and your patience. As long as you are using those models in accordance with their model license terms, and the output you're using to submit to that competition doesn't 'conflict with the license requirement of the rules of this competition, you may use them.

---

### Message #2 — Participant (2026-09-29T15:10:11.167000) [Votes: -1]

So models like Claude and GPT are off the table, but Muse and Chinese aren’t?

---

### Message #3 — Participant (2026-09-23T15:38:32.633000) [Votes: 44]

Hi organizers,


My understanding is that using external LLM APIs to generate synthetic training data has generally been allowed in recent Kaggle competitions. Given Section 2.6, I would expect this to be permitted here as well, subject to the competition’s external data and model requirements.


Could you clarify whether participants may use proprietary models, such as OpenAI Astra or Claude Opus 5.5, to generate code patches and agent trajectories for training Gemma specifically for this competition?


Regarding provider restrictions on developing competing models, my current understanding is that training a model solely for this competition may be permissible, while deploying or using the resulting model outside the competition could raise separate concerns. I recognize that participants remain responsible for complying with their providers’ terms.


With that distinction in mind, could you clarify:



- Does the competition allow this form of distillation from proprietary API models? Are there any restrictions on which teacher models may be used?

- Are there different requirements for proprietary API teachers versus open-weight teachers?

- How would a model intended solely for competition use fit with the winner licensing and release requirements under Sections 2.5 and 2.8? In particular, would winners need to release the trained weights or adapters for unrestricted use outside the competition?


Examples of acceptable teacher models would be very helpful.


Thank you!

---

### Message #4 — Participant (2026-09-24T10:46:39.967000) [Votes: 5]

Hi @cnumber,


We are confering and will have an answer for you soon.

---

### Message #5 — Participant (2026-09-27T12:02:33.733000) [Votes: 3]

any updates? :)

---

### Message #6 — Participant (2026-09-29T08:14:11.043000) [Votes: 0]

Hi @cnumber,


  We are confering and will have an answer for you soon.



Any updates? If not, I’ll just start with GLM 5.3

---

### Message #7 — Participant (2026-09-25T14:51:19.727000) [Votes: 1]

I'm looking at using distillation methods for open source models as well. I'm not against open sourcing my training data results from the distillation process as I have a tool that does this for Gemma 4 already developed. I'm curious what they decide on here!


Edit: Here is my KD tool which I'll be updating for this competition Ghostwriter

---

### Message #8 — Participant (2026-09-27T17:36:57.870000) [Votes: 0]

hey this looks cool, thanks

---

### Message #9 — Participant (2026-09-25T11:53:09.197000) [Votes: -8]

what a state this world is in when a response like this warms my heart ❣️

---

### Message #10 — Participant (2026-09-25T17:13:40.430000) [Votes: 0]

I worry a bit about getting my accounts banned or routed to inferior models for distillation.

---

### Message #11 — Participant (2026-09-25T17:21:39.050000) [Votes: 1]

I wouldn't do this with closed source models but given that Gemma 31B is a smaller model you can get some good gains from open source KD. It is very much against their ToS doing any type of distillation.

---
