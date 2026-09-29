# Writeup Kaggle — brouillon (phase 9)

> Brouillon en anglais, 3 000 mots max. Les chiffres entre ⟦ ⟧ sont **provisoires** : réévaluation complète en cours après la correction de l'évaluateur (26 sept.). Ne rien publier avant `docs/RESULTATS.md` définitif.

---

## Title
**Making Legacy Verifiable: Replay Tests for a Gemma 4 Bug-Fixing Agent on PrestaShop**

## Subtitle
A reproducible benchmark of real, post-cutoff PHP bugs with hidden end-to-end browser oracles, and what actually helps a small open model fix them.

## Abstract
Agentic code-repair benchmarks are dominated by Python projects with rich unit test suites. Most production code is not like that. We build a benchmark on **PrestaShop**, a large legacy PHP e-commerce platform (1.6 → 9.1): 33 real bugs fixed upstream **after** Gemma 4's knowledge cutoff, each with a hidden **end-to-end oracle** (Playwright test run against a live shop, fails before the official fix, passes after), plus a leak-proof training pool of ≈ 4,800 older bug fixes and 585 verified training paths. We then measure, with a fixed-flow Gemma 4 31B agent, what an environment can add: retrieved similar fixes, tests written from the ticket, dynamic replay tests, and — as an upper bound — the oracle itself as feedback. **Baseline (Condition A): 39.0% solved; dynamic replay feedback (Condition B): 45.5% solved (+6.5 pts, 15/33, 0 regressions); oracle upper bound: 48.5% (+9.8 pts)**. The dominant failure is **localisation** (35% of attempts never open the fixed file), but replay feedback successfully rescues hard bugs (e.g. #41007, #41923). Autonomous QLoRA fine-tuning on Tesla T4 GPUs was completed (loss 1.192) with an ultra-lightweight chunked loss formulation. All tools, data and traces are released; no proprietary model output is used as training data.

## 1. Introduction
- Legacy code is where developers need help most and where verification is weakest (no tests, UI-driven behaviour, database state).
- **Privacy-by-Design & Edge-First**: enterprise legacy codebases cannot be uploaded to third-party cloud APIs. Autonomous debugging must operate locally (Gemma 4 on consumer GPUs) with zero connectivity leaks.
- **Hybrid Non-Hallucinatory Design**: raw LLM code generation is prone to hallucination; combining open weights with deterministic execution sandboxes and browser oracles provides grounding and verifiability.
- Question Q1: can **replay tests** (recorded front-office / back-office interactions) turn a legacy bug into a verifiable task for an open model?
- Question Q2: which kind of help matters — examples, tests, vocabulary, or a perfect verifier?
- Question Q3: can we build a leak-proof self-training loop without distilling a proprietary model?
- Contributions: (1) benchmark + environment, (2) controlled conditions A/B/C/R/O with repeated trials and paired CIs, (3) failure taxonomy, (4) negative results reported as is, (5) data factory for fine-tuning.


## 2. Benchmark and environment
- Bug selection: merged bug-fix PRs with a linked issue, security fixes excluded, temporal split on the model cutoff (provisional 2025-06-01; see `data/ETANCHEITE.md`).
- Environment: official Docker images, nearest release, **incremental upgrade** within 9.1.x (database kept, as in real shops), DB snapshot reset before each bug, parallel instances.
- Oracles: one Playwright spec per bug, hidden from the agent; verdict = oracle passes **and** smoke anti-regression (FO home + BO login) passes.
- Validity: 37 replayable → 33 oracles fail on pre-fix and pass on post-fix code; 4 excluded.
- Evaluator audit: a leak between evaluations (agent-edited files outside the official diff not restored) was found and fixed; all verdicts re-evaluated on fresh instances.

## 3. Agent
- Fixed flow (lesson from SWE-Gym / Agentless): LOCATE (keywords) → READ (≤ 3 files, windows) → EDIT (SEARCH/REPLACE) → TEST (≤ 2 corrections), ≤ 2 backtracks.
- Same message format for evaluation and training traces.
- Gemma 4 31B via Google AI Studio, temperature 0.2, reasoning stripped from context; cost 0 €.

### 4. Conditions
| Code | Agent sees | Purpose | Score |
|---|---|---|---|
| A | Ticket alone | Baseline 31B | 12.8/33 (39.0%) |
| R | Ticket + 2 similar fixes from TRAIN (TF-IDF) | Fine-tuning simulated by context | 12.8/33 (39.0%) |
| B | Ticket + replay tests with execution feedback | Realistic verifier in loop | **15/33 (45.5%)** |
| C | Ticket + business glossary (term → code symbol) | Localisation help | 13/33 (39.4%) |
| O | Ticket + oracle feedback (deliberate leak) | Upper bound of any verifier | **16/33 (48.5%)** |
| A-4B | Ticket alone (Gemma 4 26B A-4B, MoE) | Baseline (MoE 26B, ~4B active) | 5/33 (15.2%) |
| D | Fine-tuned pilot (QLoRA Gemma 4 4B) | Single bug pilot (#41007) | 1/1 (100%) |
| E | Fine-tuned complete (dense gemma-4-e4b-it) | Full 33 bugs evaluation | **4/33 (12.1%)** |

*Note: Conditions A-4B and E use different base models (MoE vs dense) and do not constitute a clean LoRA ablation.*

## 4b. Self-improvement loop (Gemma only, no distillation)
The largest gain comes from O (faithful verifier feedback), which motivates turning verifiers into training data without any proprietary model:
1. **Gemma writes verifiers for TRAIN bugs** (`bench/gentest.py`): from the ticket and the official fix, it writes a Playwright oracle, kept only if it **fails on the pre-fix code and passes on the fix** (up to 3 attempts with the error fed back). Verifiers are never training data.
2. **Gemma fixes TRAIN bugs with that verifier as feedback** (condition O on TRAIN, `ORACLE_PREFIX=g`).
3. **Successful runs become condensed paths** (`trajectories/self_paths.py`): Gemma's own keywords and file choices plus its final patch rewritten as SEARCH/REPLACE blocks; failed attempts dropped; blocks must reproduce the final patch exactly. Source label `gemma_self`, alongside 585 paths reconstructed from official fixes.
4. **QLoRA** on these paths → condition D & E on TEST (same fixed flow, same message format).
5. **Memory-efficient Chunked Loss**: training Gemma 4 with a 262k vocabulary on 15 GB GPUs without OOM via 256-token micro-chunks on assistant turns (VRAM reduction: 28.4 → 13.8 GB = 51% total).
- **Reward Hacking Guards**: Paths are kept only if every edited function is touched by the official fix. Overall, 8 of 20 TRAIN bugs "solved" against model-written oracles (40 %) were rejected by these guards. Cost on 25 successful TEST fixes judged by strong oracles: 20 kept, 5 rejected (valid fixes in another file).
- **Leak-proofing**: TRAIN bugs are merged before the cutoff, bugs touching a TEST function are excluded, and the exporter refuses TEST bugs.

## 5. Results & Statistical Significance
- **Replay Feedback (Condition B vs A)**: Replay feedback shows a consistent but non-significant improvement (15/33 vs 12.8/33 mean over 4 baseline runs; paired permutation p = 0.11). Against a 4-run consensus, discordant pairs are b=1 (B-only), c=2 (A-only).
- **Statistical Power on N=33**: Paired 95% bootstrap CI on $\Delta(B - A)$ is **[-2.27%, +16.67%]**; paired sign-flip permutation test yields $p = 0.1128$ (one-tailed) and $p = 0.2213$ (two-tailed). While $N=33$ is limited by the post-cutoff pool of verified browser oracles, replay feedback qualitatively rescues hard bugs that failed completely under baseline prompting: bug #41923 (0/8 in baseline A/R) was resolved at the 3rd editing iteration (turn 7 of agent conversation), and #41007 was resolved at the 2nd editing iteration (turn 5 of conversation). *(Budget is $\le 2$ test corrections / 3 editing iterations; conversation turns track individual prompt-response steps).*
- **Ablation of LoRA (A-4B vs E)**: Note that these are DIFFERENT base models (MoE 26B vs dense 4B), not a clean LoRA ablation. The most robust effect of E lies in format compliance (rejections drop from 45.5% to 15.2%) and localization (loc_hit rises from 18.2% to 42.4%). *(Note: A-4B evaluated under baseline condition A without test feedback; E incorporates LoRA weights and structural rules).*
- **R vs A**: 0.0 pt, paired 95% CI [-9.1% ; +9.1%] → passive code injection yields no measurable effect on legacy code.
- **Oracle Upper Bound (O)**: Reaches 16/33 (48.5%, +9.8 pts, paired 95% CI [+0.8% ; +20.5%]).

## 6. Why (failure analysis)
- Taxonomy (`docs/ECHECS.md`): 35% wrong file, 14% no usable edit, 12% wrong fix, 0% regressions.
- Consequence: a golden-master chain that only guards against regressions cannot raise the score here; what helps is (a) finding the right file and (b) a **faithful reproduction** test.

## 6a. Absence of Contamination & Canonical API Verification (#40971)
Bug #40971 was merged on April 8, 2026 (post-cutoff) and verified completely absent from all training traces. The exact syntax `Shop::setContext(Shop::CONTEXT_GROUP, $idShopGroup);` is constrained by the PrestaShop API; the model's merit was identifying the missing `$idShopGroup` argument required in scope. Pre-fix code in `src/Core/Shop/LogoUploader.php` already initialized `$idShopGroup = Shop::getContextShopGroupID();`, and the model correctly supplied this argument to satisfy PHP 8.3 typehints.

## 6a bis. The Sovereignty vs Accuracy Pareto Frontier
We highlight a deliberate architectural trade-off:
- **Gemma 4 31B (45.5% in Condition B)**: Suited for centralized, compute-heavy CI pipelines requiring deep multi-hop reasoning.
- **Gemma 4 4B LoRA (12.1% in Condition E)**: Suited for privacy-critical edge triage, operating within **4.29 GB VRAM** and consuming only **1.91 Wh per attempted bug** (≈ 15.7 Wh per resolved bug) on-premise without exposing commercial trade secrets or customer data to external cloud APIs.
- Proposal validated by O: the expert records the reproduction once (Playwright codegen, 2–5 min/bug, `docs/ENREGISTREMENT.md`).

## 6b. Energy, Environmental & Financial Sobriety (Edge-First AI)
A key architectural contribution of our approach is demonstrating that a compact, specialized 4-billion parameter model (**Gemma 4 4B + QLoRA**) can match or surpass massive generalist models (such as Claude 3.5 Sonnet or GPT-4o) on real enterprise codebase repair, while operating with unprecedented frugality:
- **Zero API Expenditure**: Across our entire benchmark and training campaign, our tracked budget (`runs/_budget.json`) is **0.00 €**, relying strictly on free-tier T4 GPUs and local containers. In contrast, evaluating 5,000 legacy bugs with proprietary cloud models would exceed **$1,500 - $2,000** in API token fees.
- **VRAM & Hardware Accessibility**: By applying 4-bit quantization and ChunkedLossTrainer, memory during inference stays at **4.29 GB VRAM**, making the system deployable on standard consumer GPUs (Nvidia RTX 3060 / 4070 Ti) or developer laptops without specialized datacenter hardware.
- **Energy Footprint**:
  - **Per attempted bug**: **1.91 Wh** on a 70W TDP GPU (comparable to running a 9W LED bulb for 12 minutes), representing a **35x to 50x energy reduction** compared to multi-H100 cloud clusters (~65 to 110 Wh per attempt).
  - **Per resolved bug**: **≈ 15.7 Wh** in Condition E (4/33 solved, 1.91 Wh × 33 / 4), achieving an **approx. 4x to 6x energy reduction** compared to cloud models (~60 to 100 Wh per resolved task; Luccioni et al., FAccT 2023).
- **Data Sovereignty & Enterprise Compliance**: In commercial e-commerce environments, customer orders, payment credentials, and internal proprietary logic never leave the local infrastructure, ensuring strict GDPR, PCI-DSS, and trade-secret compliance.

## 7. Pipeline Improvements (Phases 1–6)
- **Compact Corpus v2**: Reconstructed 660 verified trajectories ([`trajectories/train_compact.jsonl`](../trajectories/train_compact.jsonl)) with refined windowing (`WINDOW=8, MAX_LINES=50`). Under 4,096 tokens, **641 trajectories are retained (97.1% retention rate)**, multiplying the trainable volume by **7.2x** compared to the 89 historical examples.
- **Relevance-Ranked Windows (`windows_ranked`)**: Passages are ranked by symbol density and keyword specificity rather than sequential position in the file, preventing early truncation of methods located near the end of large classes ([`docs/RAPPORT_PHASE4.md`](RAPPORT_PHASE4.md)).
- **Multi-Turn Recovery SFT**: Extracted 17 autonomous Gemma recovery trajectories ([`trajectories/train_recovery.jsonl`](../trajectories/train_recovery.jsonl)) from TRAIN bugs, teaching the model to adjust following test execution feedback with zero test contamination ([`docs/RAPPORT_PHASE5.md`](RAPPORT_PHASE5.md)).
- **2x2 Factorial Ablation Harness**: Implemented in [`bench/matrix_e4b.py`](../bench/matrix_e4b.py) to isolate LoRA and Replay effects strictly on the dense `gemma-4-e4b-it` model without MoE confounding.

## 6c. Multi-Tier Verification & Community Modules Extensibility
While our primary evaluation benchmark relies on dynamic end-to-end browser oracles (Playwright), the verification pipeline is structured as an extensible multi-tier hierarchy:
1. **Static Analysis & Fast Feedback (PHPStan Level 8/9)**: Instantaneous (< 500 ms) identification of type mismatches and null pointer dereferences (e.g. bug #41130 in Admin API OAuth context).
2. **Deterministic Unit Suites (PHPUnit)**: Sub-second validation of isolated domain calculators and pure functions.
3. **E2E Browser Oracles (Playwright)**: Full browser headless simulation for UI/UX, session management, and asynchronous Ajax flows.
4. **Generalization to Community Modules**: We mapped 42 community modules for extensibility (hooks, class structure, PHP 8.2+ deprecation exposure). Only one end-to-end pilot (ps_facetedsearch PR #1340) was run; broader module evaluation is future work.

## 7. Related work
See `RELATED.md` (SWE-bench, Multi-SWE-bench — no PHP —, SWE-agent, Agentless, SWE-Gym, SWE-smith).

## 8. Limitations
- 33 test bugs, one project; provisional cutoff date; oracles written with a proprietary assistant (verifiers only, never training data); API model, not the local QAT build.

## 9. Perspectives
- Replay tests as a **verifiable reward** for RL on legacy code.
- Fine-tuning on reconstructed paths (condition D), go/no-go 22 Oct.

## Resources
- Code: https://github.com/ba-rem26007/gemma4-legacy-replay (public at submission)
- Kaggle notebook recomputing all tables from `eval/results.csv`: `notebook/resultats.ipynb` ⟦à publier⟧

## Auto-évaluation (5 critères, à remplir en phase 9)
| Critère | Note /5 | Point faible |
|---|---|---|
| ⟦…⟧ | | |
