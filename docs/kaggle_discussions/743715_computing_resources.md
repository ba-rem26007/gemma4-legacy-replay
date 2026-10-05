# Topic 743715: computing resources

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743715
- **Date** : 2026-09-26T14:58:44.801000
- **Votes** : 0 | **Commentaires** : 11

---

### Message #1 — Participant (2026-09-26T18:06:02.933000) [Votes: 0]

Is there a supported way to use the competition's four L4 GPUs in a private research notebook with no competition data source mounted, or with an official sanitized development-only resource instead?


We want to use only the permitted Gemma model, approved wheelhouse and development tasks while keeping reference fixes, verification tests and held-out tasks inaccessible during generation. Standard sanitized-only notebooks currently offer T4 x2, while attaching the competition source enables L4 x4. Does Kaggle provide an entitlement-only competition association, an approved private template, or a sanitized resource that grants L4 x4 access? Please also clarify the applicable free quota and notebook storage limits.


This is an access/configuration question; no solution code, model output, private data or credentials will be included.

---

### Message #2 — Participant (2026-09-26T18:22:42.227000) [Votes: 0]

Competition source has to be attached. Notebook can be private, but it needs to be attached. Of course, don’t abuse it for something outside this competition, since Kaggle staff can eject you by their discretion.

---

### Message #3 — Participant (2026-09-26T16:02:39.997000) [Votes: 0]

You probably can’t post train locally. You may be able to run the model for inference and A/B, but probably need cloud for SFT and RL.

---

### Message #4 — Participant (2026-09-26T16:15:57.633000) [Votes: 0]

Thank you John. That leaves me out. Unfortunately I don't have resources for online computing. 
The people likely to win this competition do! 
Thanks again John.

---

### Message #5 — Participant (2026-09-26T18:21:04.643000) [Votes: 0]

Yeah MLX would probably be slow for inference anyways. Of course, CUDA is always preferred, with tensor cores, but you could post train on the Kaggle GPUs, and run the customized harness with your own laptop to improve it, but in my experience even with my 128gb m4 MacBook, it’ll probably overheat and shut off (which would stop your iterations), so I have my own 64gb rig of Nvidia GPUs. I also was using oMLX, which is essentially one of the most optimized inference stacks for Metal.

---

### Message #6 — Participant (2026-09-26T18:30:24.383000) [Votes: 0]

Modal offers $30 of free credits a month. I typically have run SFT/RL on their systems costing about $5-8 per a run. Caveat being it is cost beneficial once you have all the setup kinks figured out. Ping me on here I'll share my open source work on Modal and using Gemma and Qwen based models on Modal which should save you a few days of pain if you want! I'm working on my setup for this competition on Modal right now and if it's not to much of a giveaway I can open source those scripts for this competition as well. 


Having your SFT/RL regime and data organized and ready to go will save you compute cost and resources.

---

### Message #7 — Participant (2026-09-26T18:59:14.340000) [Votes: 0]

Lowkey could I get your setup? I still need resources for post training.

---

### Message #8 — Participant (2026-09-26T19:02:26.037000) [Votes: 0]

LLM Tuning Gemma Tuning


This should be enough to get past the hard part with Modal. For the sake of the competition I won't dive into my data mix and overall setup but this should make getting into Modal and going with Gemma pretty much out the box easier. I've built MLX/Metal inference engines around the Gemma models (Hyperion Project) so seeing this competition was a fun one to get into for me haha

---

### Message #9 — Participant (2026-09-26T19:06:18.003000) [Votes: 0]

Thanks John. Will wait for another competition!

---

### Message #10 — Participant (2026-09-26T19:07:05.667000) [Votes: 0]

Thank you so much for your offer Justin. I'll defo hit u up in another competition.

---

### Message #11 — Participant (2026-09-26T14:58:44.800000) [Votes: 0]

i have a macbook m1 pro. is that enough for this competition? so my only free resources are kaggle gpu and people are getting timed out. do i need to us cloud computing? ree
thank you in advance

---
