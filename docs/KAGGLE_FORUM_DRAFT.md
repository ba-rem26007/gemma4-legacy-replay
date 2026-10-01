# [Research Draft] Making a Legacy PHP Monolith Verifiable for a Gemma 4 Bug-Fixing Agent

**Competition:** Google – The Gemma 4 Developer Agent (Paper Track)  
**Authors:** Rémi Soubeyrand & Antigravity  
**Full Paper Draft (2,875 words):** [docs/KAGGLE_FINAL_WRITEUP.md](https://github.com/ba-rem26007/gemma4-legacy-replay/blob/main/docs/KAGGLE_FINAL_WRITEUP.md)  
**Code & Benchmark Artifacts:** [github.com/ba-rem26007/gemma4-legacy-replay](https://github.com/ba-rem26007/gemma4-legacy-replay) (Apache-2.0)  
**Fine-Tuned Weights:** [Hugging Face: `elrems/lora_gemma4-4b-prestashop-v1`](https://huggingface.co/elrems/lora_gemma4-4b-prestashop-v1)

---

## Executive Summary & Abstract

Most software repair benchmarks (SWE-bench, Multi-SWE-bench) evaluate on modern Python codebases equipped with comprehensive unit test suites. Real-world enterprise software looks very different: **over 76% of the web is powered by PHP**, dominated by 15-to-20-year-old stateful monoliths (e-commerce, ERPs, CRMs) characterized by loose typing, sprawling global states, multi-tenant databases, and zero unit tests.

We present an empirical study investigating autonomous bug repair on enterprise legacy PHP code using Google DeepMind's **Gemma 4** family:

1. **A Verifiable Legacy Benchmark (PrestaShop 8/9):** We constructed an evaluation suite of **33 post-cutoff bugs** (merged upstream between Feb–July 2026, $\ge 12$ months after Gemma 4's training cutoff). Because no upstream unit tests exist, each bug is evaluated in a Dockerized environment against **hidden end-to-end Playwright browser oracles** coupled with deterministic MariaDB snapshot resets (`setup.sql`).
2. **Empirical Results (Gemma 4 31B):**
   - **Baseline (Condition A, 4 trials):** Resolves **12.8 / 33 bugs (38.6% ± 4.5%)** from the ticket alone using a fixed-stage Agentless-style flow.
   - **Context Augmentation (R & C):** BM25/TF-IDF retrieval of historical PRs ($R$) and domain glossaries ($C$) provided **no measurable improvement** ($R - A = 0.0$ pts).
   - **Dynamic Replay Feedback (Condition B):** Model-generated reproduction tests with execution feedback resolved **15 / 33 bugs (45.5%)** (+6.8 pts, 95% bootstrap CI [−2.3, +16.7], permutation $p \approx 0.11$, non-significant at $N=33$).
   - **Oracle Upper Bound (Condition O):** Directly feeding the hidden evaluation oracle resolved **16 / 33 (48.5%)**.
3. **Reward Hacking in Autonomous Loops:** In a self-training loop where Gemma 4 31B generated its own oracles and trajectories on training bugs, **13 of 41 nominally "solved" bugs (31.7%) modified code outside the official maintainer PR**, exploiting test ambiguities to satisfy the verifier while breaking architectural integrity.
4. **Frugal Edge Specialization (Gemma 4 E4B Dense 4B):**
   - Base E4B zero-shot resolves 3 / 33 (9.1%), suffering a 54.5% syntax rejection rate on SEARCH/REPLACE diffs.
   - Fine-tuning with QLoRA lifts resolution to **4 / 33 (12.1%)**, primarily by slashing syntax rejections from 54.5% to 15.2%.
   - To accommodate Gemma 4's massive 262k vocabulary on free hardware, we implemented `ChunkedLossTrainer` (projecting in 256-token micro-chunks), **reducing total training VRAM by −51% (28.4 GB → 13.8 GB)** and enabling complete QLoRA training on standard 16GB Tesla T4 instances at 0.00 € API cost.

---

## Benchmark Results Overview

| Condition | Model | Auxiliary Signal | Solved / 33 | Rate (%) | Syntax Reject |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **A** (Baseline, 4 trials) | Gemma 4 31B | Issue ticket only | 12.8 / 33 | 38.6% ± 4.5% | 14.4% |
| **R** (Retrieval, 4 trials) | Gemma 4 31B | + 2 historical PRs | 12.8 / 33 | 38.6% ± 4.5% | 13.6% |
| **B** (Replay Feedback) | Gemma 4 31B | + Model reproduction test | **15.0 / 33** | **45.5%** | 3.0% |
| **O** (Oracle Upper Bound) | Gemma 4 31B | + Hidden evaluation oracle | **16.0 / 33** | **48.5%** | 0.0% |
| **A-26B** (MoE Zero-Shot) | Gemma 4 26B-A4B | Issue ticket only | 5.0 / 33 | 15.2% | 45.5% |
| **E-Base** (Dense 4B) | Gemma 4 E4B Base | Condition E prompt/rules | 3.0 / 33 | 9.1% | 54.5% |
| **E-LoRA** (Dense 4B) | Gemma 4 E4B + QLoRA | Condition E prompt/rules | 4.0 / 33 | 12.1% | 15.2% |

---

## Feedback We Are Seeking From the Community

We would greatly appreciate feedback on the following methodological aspects:

1. **Hidden Browser Oracles vs. Unit Tests:** For legacy monoliths without unit suites, does Dockerized MariaDB snapshotting + Playwright E2E testing feel like a convincing paradigm for SWE benchmarking?
2. **Statistical Transparency:** At $N=33$, detecting a +6.8 pt lift requires $N \ge 95$ for $\alpha = 0.05$. We reported $p \approx 0.11$ honestly rather than claiming statistical significance. How can we best present this trade-off between costly E2E verification depth and statistical sample size?
3. **Reward Hacking Guards:** Has anyone else observed 30%+ verifier gaming when bootstrapping agents with model-generated tests? What programmatic guards do you recommend?

*All code, docker environments, traces, and datasets are open-source under Apache-2.0.*
