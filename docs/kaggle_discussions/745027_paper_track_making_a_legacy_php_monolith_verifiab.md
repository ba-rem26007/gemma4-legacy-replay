# Topic 745027: [Paper Track] Making a Legacy PHP Monolith Verifiable for a Gemma 4 Bug-Fixing Agent

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745027
- **Date** : 2026-10-01T20:35:22.851000
- **Votes** : 1 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-01T20:35:22.853000) [Votes: 1]

## Feedback We Are Seeking From the Community

We would greatly appreciate feedback on the following methodological aspects:



- Hidden Browser Oracles vs. Unit Tests: For legacy monoliths without unit suites, does Dockerized MariaDB snapshotting + Playwright E2E testing feel like a convincing paradigm for SWE benchmarking?

- Statistical Transparency: At $N=33$, detecting a +6.8 pt lift requires $N \ge 95$ for $\alpha = 0.05$. We reported $p \approx 0.11$ honestly rather than claiming statistical significance. How can we best present this trade-off between costly E2E verification depth and statistical sample size?

- Reward Hacking Guards: Has anyone else observed 30%+ verifier gaming when bootstrapping agents with model-generated tests? What programmatic guards do you recommend?


All code, docker environments, traces, and datasets are open-source under Apache-2.0.

---
