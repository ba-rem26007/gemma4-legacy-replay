# Making a Legacy PHP Monolith Verifiable for a Gemma 4 Bug-Fixing Agent

### Hidden replay oracles on 33 post-cutoff PHP bugs, and empirical findings from a Gemma-only self-learning loop

**Author:** Rémi Soubeyrand · Kaggle "Google – The Gemma 4 Developer Agent", Paper Track  
**Code, data and traces:** https://github.com/ba-rem26007/gemma4-legacy-replay (Apache-2.0)  

---

## Abstract

Most code-repair benchmarks evaluate on Python repositories with pre-existing unit test suites. However, over 76% of the web operates on PHP, dominated by stateful legacy monoliths where defects manifest in interactive browser sessions coupled to relational database state. We introduce an evaluation harness making one such enterprise monolith, **PrestaShop**, systematically verifiable: each of **33 real, post-cutoff bugs** is evaluated using an end-to-end Playwright oracle run against Dockerized containers with deterministic MariaDB state resets.

Using a fixed-turn agent flow without open-ended tool loops, **Gemma 4 31B** resolves **12.8 / 33 bugs** (38.6%, mean of 4 independent trials) from the issue ticket alone. Retrieval of historical PRs (Condition R) and glossaries (Condition C) produce no gain over baseline. Providing model-written reproduction tests with execution feedback (Condition B) reaches **15 / 33** in a single trial (+6.8 pts, 95% bootstrap CI [−2.3, +16.7], sign-flip permutation $p \approx 0.11$, not statistically significant at $N=33$). Providing the hidden oracle as feedback (Condition O, empirical upper bound) resolves 16 / 33.

When closing the training loop using Gemma 4 31B alone to generate verifiers and trajectories on historical bugs, **13 of 41 nominally "solved" bugs (32%) edit code outside the official maintainer fix**, exploiting test ambiguities. Finally, on edge-scale models, fine-tuning **Gemma 4 E4B** via QLoRA yields **4 / 33** resolutions (12.1%): we show that this gain is primarily driven by **syntactic format compliance** (syntax rejection dropping from 54.5% to 15.2%) rather than deep reasoning. A chunked cross-entropy implementation accommodates Gemma 4's 262k vocabulary within commodity 16GB GPUs at zero financial cost.

---

## 1. Problem & Motivation

Server-side web applications remain predominantly powered by PHP (76.2% of surveyed back-ends; W3Techs, 2026). In e-commerce, PrestaShop powers over 300,000 active stores handling critical transactions, while Dolibarr supports over 100,000 organizations. Much of this infrastructure constitutes classical "legacy code": software lacking regression test suites [Feathers].

Existing benchmarks like SWE-bench [SWE-bench] and Multi-SWE-bench [Multi-SWE] rely on unit tests and exclude PHP. In an enterprise monolith like PrestaShop, an issue such as #41921 ("Cannot change stock behaviour in shared stock mode") depends on multi-store configuration flags, relational constraints across SQL tables, and back-office UI interactions. No standalone unit test exists upstream to isolate it.

Furthermore, enterprise applications face strict data compliance mandates (GDPR, PCI-DSS). Offloading private codebases to third-party APIs presents real privacy concerns. Developing verifiable, local-first repair pipelines with open-weight models like Gemma 4 is therefore of immediate operational value.

We investigate three research questions:
- **Q1.** Can browser-based end-to-end replay with database snapshot resets provide a deterministic evaluation signal for an open-weight model on legacy PHP code?
- **Q2.** Which auxiliary signals improve resolution: retrieved historical PRs, domain glossaries, model-generated reproduction tests, or the reference oracle?
- **Q3.** Can Gemma bootstrap its own repair trajectories using model-generated verifiers, and does this loop exhibit reward hacking?

---

## 2. Benchmark Construction & Protocol

### Selection & Cutoff Integrity
Candidate issues were screened by extracting merged, functional bug-fix pull requests from the PrestaShop 9.1.x branch matching the following criteria:
1. Linked to a reproducibly described GitHub issue.
2. Modifying $\le 3$ source code files.
3. Containing verifiable browser-reproducible symptoms.

From 187 candidate PRs merged after our cutoff (2025-06-01), 55 were screened, yielding **33 verifiable test bugs** (`data/bugs_test.csv`). Exclusions stemmed from frontend JS build dependencies (13) or non-deterministic UI triggers (9).

All 33 PRs were merged between 2026-02-12 and 2026-07-22, providing $\ge 12$ months separation from Gemma 4's January 2025 pre-training cutoff [Gemma4-card]. While 5 ticket descriptions were opened earlier, all code patches were merged strictly post-cutoff.

### Execution Environment & Oracles
Each bug is containerized via Docker with MariaDB 10.11:
- **Deterministic Reset:** Before each evaluation round, a database snapshot (`setup.sql`) restores the exact shop state.
- **Hidden Oracles (`oracle*.spec.js`):** Playwright browser tests (27 Back-Office, 6 Front-Office) verify user-facing fixes. **The agent never sees this oracle.** It runs strictly once post-run to establish ground truth.
- **Smoke Check:** Queries Front-Office (`/fr/`) and Back-Office (`/admin-dev/index.php`). Rejects patches causing HTTP errors or fatal PHP logs.
- **Verifier Separation:** In feedback conditions (B, C), the agent executes visible reproduction tests (`replay*.spec.js`) generated from the ticket alone. Only Condition O accesses the oracle as an explicit ceiling.

---

## 3. Agent Architecture

Rather than deploying open-ended autonomous agent loops with dynamic bash execution [SWE-agent], we employ a fixed-stage flow inspired by Agentless [Agentless] to ensure reproducibility across runs:

```
[Issue Ticket] 
      │
      ▼
1. LOCATE  ──► Model outputs keywords ──► git grep & path ranking
      │
      ▼
2. READ    ──► Model selects ≤ 3 files ──► relevance-ranked code windows
      │
      ▼
3. EDIT    ──► Model outputs SEARCH/REPLACE diff blocks
      │
      ▼
4. TEST    ──► (Feedback conditions only) Replay test executed;
               up to 2 retry turns provided if execution fails.
```

1. **LOCATE:** The model emits 3–8 search keywords. The harness performs keyword grep and file-tree matching, returning ranked paths.
2. **READ:** The model selects up to 3 candidate files. Relevance-ranked windows (centered on function headers and symbol density) are extracted (`agent/flow.py`).
3. **EDIT:** The model generates atomic `SEARCH / REPLACE` diff blocks. The harness verifies that `SEARCH` lines match target file content exactly.
4. **TEST (Feedback conditions):** If a test fails, the error trace and current modified files are returned to the model for up to 2 retry attempts (budgeting up to 5 total assistant turns).

Primary evaluations were conducted with **Gemma 4 31B** [Gemma4] via the Google AI Studio API at temperature 0.2 across 4,349 total API calls at zero monetary cost.

---

## 4. Empirical Evaluation

### Main Benchmark Results

| Condition | Auxiliary Signal Provided | Solved / 33 | Resolution (%) | Right File Read | Smoke Regr. |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **A** (Baseline) | Issue ticket only (4 trials: 12, 13, 15, 11) | **12.8 / 33** | **38.6% ± 4.5%** | 19.8 / 33 | 0 / 132 |
| **R** (Retrieval) | + 2 similar training PRs (TF-IDF) + glossary (4 trials) | 12.8 / 33 | 38.6% ± 4.5% | 20.2 / 33 | 0 / 132 |
| **C** (Static Test)| + Ticket glossary + static reproduction test (10 bugs; 1 run) | 13.0 / 33 | 39.4% | 18.0 / 33 | 1 / 33 |
| **B** (Replay FB) | + Visible reproduction test **with execution feedback** (1 run) | **15.0 / 33** | **45.5%** | 17.0 / 33 | 0 / 33 |
| **O** (Oracle FB) | + **Hidden evaluation oracle as feedback** (Upper Bound; 1 run) | **16.0 / 33** | **48.5%** | 19.0 / 33 | 2 / 33 |
| **A-26B** (MoE) | Ticket only, Gemma 4 26B-A4B zero-shot (1 run) | 5.0 / 33 | 15.2% | 21.0 / 33 | 0 / 33 |
| **E-Base** (4B) | Condition E prompt/rules, base Gemma 4 E4B zero-shot (1 run) | 3.0 / 33 | 9.1% | 13.0 / 33 | 0 / 33 |
| **E-LoRA** (4B) | Condition E prompt/rules, Gemma 4 E4B + QLoRA adapter (1 run) | 4.0 / 33 | 12.1% | 14.0 / 33 | 1 / 33 |

*Notes: Paired bootstrap confidence intervals (95%, 5,000 resamples, random seed 0) are computed relative to Baseline A. "Right File Read" measures whether the agent inspected the file modified in the reference fix.*

### Statistical Analysis & Verifier Dynamics (Q1 & Q2)

1. **Context Augmentation (Conditions R & C):** Historical PRs (Condition R) yielded no gain over baseline ($R - A = 0.0$ pts, 95% CI [−9.1, +9.1]). Adding domain glossaries (Condition C) matched 16 tickets but did not improve localization (18.0 vs 19.8 files read).
2. **Replay Feedback (Condition B):** Gemma 4 31B generated synthetic reproduction tests from ticket descriptions (`bench/reprotest.py`), yielding valid failing tests for 10 / 33 bugs (for the other 23, B collapses to A).
   - In this trial, Condition B resolved 15 / 33 (+6.8 pts over A mean, 95% CI [−2.3, +16.7]).
   - A one-sided sign-flip permutation test yields $p \approx 0.11$ (two-sided $p \approx 0.23$), not statistically significant at $N=33$ ($\alpha = 0.05$).
   - Across 3 repetitions on the 10 feedback bugs, Pass@1 was 36.7%. 15/33 also falls within the single-trial range of Baseline A (11 to 15).
   - In 9 of 10 bugs, model tests never passed during retries, acting as static negative feedback. On #41923, the patch succeeded on turn 1 prior to feedback, showing visible tests acted primarily as specifications.
3. **Oracle Feedback Upper Bound (Condition O):** Providing the hidden oracle directly resolved 16 / 33 (+9.8 pts, 95% CI [+0.8, +20.5]). Feedback converted 3 failing bugs (#41299, #41394, #41923), while breaking smoke checks on two others (#41225, #41573).

---

## 5. Failure Taxonomy & Localization Bottleneck

Across all 132 baseline attempts in Condition A (4 runs × 33 bugs), 81 attempts failed. We analyze the failure distribution:

```
Condition A Failure Distribution (81 total failures across 132 attempts):
┌───────────────────────────────────────────────┬───────┬────────────┐
│ Failure Mode                                  │ Count │ Percentage │
├───────────────────────────────────────────────┼───────┼────────────┤
│ 1. Localization Failure (Target never opened) │  46   │   56.8%    │
│ 2. Syntactic / Search Mismatch (No edit applied)│ 19   │   23.5%    │
│ 3. Incorrect Logic / Partial Patch            │  16   │   19.8%    │
│ 4. Platform Runtime Regressions               │   0   │    0.0%    │
└───────────────────────────────────────────────┴───────┴────────────┘
```

### Contingency Analysis: Localization vs. Resolution
To examine whether target localization guarantees patch success, we construct the contingency table across the 132 attempts:

| Condition A Attempts | Target File Read (`loc_hit = True`) | Target File Missed (`loc_hit = False`) | Total |
| :--- | :---: | :---: | :---: |
| **Oracle Passed (Solved)** | 51 (38.6%) | 0 (0.0%) | 51 |
| **Oracle Failed (Unsolved)** | 35 (26.5%) | 46 (34.8%) | 81 |
| **Total** | 86 (65.2%) | 46 (34.8%) | 132 |

- **Localization is a strict prerequisite:** In 0% of cases where the target file was missed was the bug resolved.
- **Conditional Resolution:** When the model successfully located and opened the target file, resolution was **51 / 86 (59.3%)**.
- The main bottleneck in legacy codebases remains keyword-based search: long classes (500+ lines) and decoupled Symfony-to-Legacy bridges frequently cause grep queries to hit unrelated boilerplate.

---

## 6. Self-Learning Loop & Reward Hacking (Q3)

To test whether open-weight models can bootstrap repair capabilities without proprietary supervision, we constructed an autonomous self-training loop using **Gemma 4 31B alone** on historical training bugs merged prior to our temporal split:

1. **Oracle Generation:** Gemma generated standalone PHP command-line oracles from tickets and reference diffs (`bench/gentest.py`). Browser-based oracles failed to execute reliably (0 / ~22), but CLI oracles succeeded on **99 of 254 bugs (39.0%)**.
2. **Autonomous Trajectory Generation:** Gemma attempted to fix each bug under Condition O using its own generated oracle as feedback, resolving 41 of 99 bugs.
3. **Execution Guards:** We introduced an automated guard (`trajectories/self_paths.py`) checking whether the model's patch touched files and functions outside the official human PR.

```
                  41 Nominally "Solved" Bugs
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
      28 Inside PR Scope                13 Reward Hacking
      (Legitimate Fixes)                (31.7% of successes)
            │                                 │
     23 Passed Split Filters           Altered unrelated SQL/stubs
     (Retained for Training)           to satisfy model test
```

### Reward Hacking Findings
Of the 41 self-generated solutions, **13 (31.7%) modified code outside the official fix** while still causing the synthetic test to pass:
- On issue #38417, the official fix rectified a faulty `ImageType::getImagesTypes()` call in the webservice. Gemma instead introduced an ad-hoc conditional inside the core `ImageType` class (`if ($type === 'customizations') $type = 'products';`), bypassing the issue symptomatically.
- On issue #38168, the agent altered an unrelated database query to force an empty return array, neutralizing an assertion failure without resolving the underlying business logic.

**Takeaway:** In autonomous self-training on legacy code, passing a synthetic verifier is insufficient. Without structural anchoring against maintainer diffs, approximately one third of self-generated trajectories learn degenerate shortcuts that satisfy the verifier while degrading architectural integrity.

---

## 7. Edge Model Adaptation & Cross-Architecture Comparison

### Factorial Evaluation on Dense 4B
To isolate the contribution of parameter scale versus fine-tuning, we evaluated three configurations within the Gemma 4 family on identical hardware:

1. **Gemma 4 26B-A4B (Sparse MoE, ~4B active params):** Evaluated zero-shot with ticket alone (Condition A), resolving **5 / 33 (15.2%)**. It opened the target file in 21 / 33 cases (63.6%), but produced valid SEARCH/REPLACE edits in only 12 cases.
2. **Gemma 4 E4B Base (Dense 4B params):** Evaluated zero-shot with full Condition E prompt and rules, resolving **3 / 33 (9.1%)** (#40651, #41130, #41193).
3. **Gemma 4 E4B + QLoRA Adapter (Dense 4B params):** Fine-tuned on PrestaShop trajectories, resolving **4 / 33 (12.1%)** (#40971, #41007, #41130, #41193) with 1 regression (#41299).

```
Model Comparison on 33 Benchmark Bugs:
[Gemma 4 31B (Dense)]       ████████████████ 45.5% (15/33)
[Gemma 4 26B-A4B (MoE)]     █████ 15.2% (5/33)
[Gemma 4 E4B + QLoRA (4B)]  ████ 12.1% (4/33)
[Gemma 4 E4B Base (4B)]     ███ 9.1% (3/33)
```

### Syntactic Compliance as the Primary Driver
A critical finding is that the performance delta between Base E4B and QLoRA E4B (+1 bug solved, 9.1% → 12.1%) is predominantly explained by **syntactic format compliance**:
- Base E4B produced malformed diffs or search-string mismatches on **18 of 33 bugs (54.5% syntax rejection rate)**.
- QLoRA fine-tuning reduced syntax rejections to **5 of 33 bugs (15.2%)**.
- Fine-tuning a 4B parameter model on domain trajectories teaches the strict SEARCH/REPLACE replacement syntax required for automated patching, rather than inducing deep architectural reasoning.

### Memory-Efficient Chunked Loss Adaptation
Gemma 4's 262k vocabulary makes unchunked float32 cross-entropy prohibitive: a 2,048-token sequence allocates ~2.15 GB for logits alone (4.29 GB for batch size 2), triggering OOMs on 16GB GPUs.

We implemented chunked cross-entropy (`training/chunked_loss.py`) tailored to Gemma 4:

```python
for i in range(0, active_tokens.size(0), chunk_size):
    logits_chunk = lm_head(hidden_states[i : i + chunk_size]).float()
    loss += F.cross_entropy(logits_chunk, targets[i : i + chunk_size], reduction="sum")
```

Projecting hidden states in 256-token micro-chunks across active assistant tokens shrinks the peak tensor from 4.29 GB to 268 MB. Total training VRAM dropped from **28.4 GB to 13.8 GB (−51%)**, enabling stable QLoRA on standard 16GB Nvidia T4 instances at zero cost.

### Edge Efficiency Profile
In edge deployments, Gemma 4 E4B operates within **4.29 GB VRAM** (FP16/INT4 weights and KV cache), fitting within consumer laptops. Local inference consumed **1.81 Wh per attempted bug** (1.39 Wh generation + 0.42 Wh Docker reset). For organizations unable to export code to cloud APIs, fine-tuned 4B models provide an autonomous triage filter resolving ~12% of issues locally.

---

## 8. Threats to Validity & Limitations

1. **Sample Size ($N=33$):** Captures the available post-cutoff PrestaShop 9.1.x PRs meeting criteria; power to detect +6.8 pt lifts is limited ($p \approx 0.11$).
2. **Single-Run Trials for B & O:** While Baseline A was evaluated across 4 trials (132 runs), Conditions B and O represent single full runs.
3. **Synthetic Verifier Coverage:** Generated reproduction tests compiled and failed cleanly on 10 / 33 bugs.
4. **Pre-Training Contamination:** 5 ticket descriptions were opened before January 2025; however, code fixes were merged strictly post-cutoff.
5. **Oracle Authorship:** Ground truth Playwright tests were drafted with LLM assistance, though verified by execution on unpatched and patched containers.

---

## 9. Reproducibility & Open Assets

All code, datasets, evaluation traces, and environment harnesses are publicly available under Apache-2.0:
- **Repository:** `https://github.com/ba-rem26007/gemma4-legacy-replay`
- **Docker Harness & Oracles:** `bench/env/docker-compose.yml`, `bench/checkout.sh`, `bench/replay/`
- **Agent Flow & Windows:** `agent/run.py`, `agent/flow.py`
- **Raw Traces & Results:** Full per-bug traces for all conditions in `runs/` and `eval/results.csv`
- **Training Harness:** `training/chunked_loss.py`, `training/snapshots/train_kaggle_v15.py`
- **Fine-Tuned Adapter:** `https://huggingface.co/elrems/lora_gemma4-4b-prestashop-v1`

---

## Acknowledgments & AI Assistance Disclosure

Claude Code (Anthropic) and Google Antigravity were used as interactive developer tools to assist in writing Docker orchestration scripts, testing harnesses, and drafts of this writeup. **No output from any proprietary model is present in any fine-tuning dataset.** All training trajectories are derived deterministically from human maintainer commits or generated autonomously by Gemma 4 models and verified by deterministic execution. All reported agent benchmarks reflect the outputs of the Gemma 4 model family.

---

## References

- [Agentless] Xia et al., 2024. *Agentless: Demystifying LLM-based Software Engineering Agents.* https://arxiv.org/abs/2407.01489
- [Feathers] Feathers, M., 2004. *Working Effectively with Legacy Code.* Prentice Hall.
- [Gemma4] Gemma Team, 2026. *Gemma 4 Technical Report.* https://arxiv.org/abs/2607.02770
- [Gemma4-card] Google DeepMind, 2026. *Gemma 4 Model Card.* https://ai.google.dev/gemma/docs/core/model_card_4
- [Multi-SWE] Zan et al., 2025. *Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving.* https://arxiv.org/abs/2504.02605
- [SWE-agent] Yang et al., 2024. *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering.* https://arxiv.org/abs/2405.15793
- [SWE-bench] Jimenez et al., 2023. *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* https://arxiv.org/abs/2310.06770
- [SWE-Gym] Pan et al., 2024. *Training Software Engineering Agents and Verifiers with SWE-Gym.* https://arxiv.org/abs/2412.21139
- [SWE-smith] Yang et al., 2025. *SWE-smith: Scaling Data for Software Engineering Agents.* https://arxiv.org/abs/2504.21798
- [W3Techs] W3Techs, 2026. *Usage Statistics of Server-side Programming Languages for Websites.* https://w3techs.com/technologies/details/pl-php
- [WATERFALL] Hammoudi et al., 2016. *WATERFALL: An Incremental Approach for Repairing Record-Replay Tests of Web Applications.* FSE 2016.
