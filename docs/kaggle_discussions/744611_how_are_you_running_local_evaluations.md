# Topic 744611: How are you running local evaluations?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/744611
- **Date** : 2026-09-30T14:27:08.057000
- **Votes** : 2 | **Commentaires** : 2

---

### Message #1 — Participant (2026-10-01T01:13:17.733000) [Votes: 1]

I use llama.cpp instead vllm, I use two setups, 2x3060 and 4x3090. In most cases my 4x3090 is busy with my local agent that's the reason to use 2x3060 for Kaggle models.

---

### Message #2 — Participant (2026-09-30T14:27:08.057000) [Votes: 2]

Hi everyone,


I’m curious how others are evaluating their agents before submitting.


My current workflow is to run the agent in a Kaggle Notebook with 4× L4 GPUs, then grade the generated patches locally using the official verifier in Docker. I use 4× L4 for generation to keep the hardware close to the competition setup, since execution speed affects what the agent can do before a timeout.


For now, my evaluation set is limited to 38 tasks from the Rich repository where the none/gold controls behave as expected: no patch is marked unresolved, while the reference patch is marked resolved. I’ve had trouble getting reliable reference-patch validation for other repositories, including FastAPI, in my local grading setup.


I’ve read the related discussions:



- Local evaluation setup and differences between the public and private environments

- Gold-patch failures and missing dependencies in the public environment

- Docker vs. Kaggle Notebook results, and the hosts’ confirmation that hidden tasks pass with gold patches


Rather than repeating those bug reports, I’d like to hear what practical evaluation workflow people are using in the meantime:



- What hardware and sandbox setup are you using for generation and grading?

- If you use different GPUs, how do you account for execution-speed differences when setting timeouts?

- Are you evaluating on a subset of tasks that pass none/gold checks, or have you found a reliable setup covering more repositories?


I’d appreciate hearing what has worked for you. Thanks!

---
