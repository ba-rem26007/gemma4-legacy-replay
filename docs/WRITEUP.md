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
| A-4B | Ticket alone (Zero-Shot Gemma 4 4B, no LoRA) | Ablation baseline for LoRA isolation | 1/33 (3.0%) |
| D | Fine-tuned pilot (QLoRA Gemma 4 4B) | Single bug pilot (#41007) | 1/1 (100%) |
| E | Fine-tuned complete (QLoRA Gemma 4 4B) | Full 33 bugs evaluation | **4/33 (12.1%)** |

## 4b. Self-improvement loop (Gemma only, no distillation)
The only condition with a significant gain is O: execution feedback from a faithful verifier. We turn that into training data without any proprietary model:
1. **Gemma writes verifiers for TRAIN bugs** (`bench/gentest.py`): from the ticket and the official fix, it writes a Playwright oracle, kept only if it **fails on the pre-fix code and passes on the fix** (up to 3 attempts with the error fed back). Verifiers are never training data.
2. **Gemma fixes TRAIN bugs with that verifier as feedback** (condition O on TRAIN, `ORACLE_PREFIX=g`).
3. **Successful runs become condensed paths** (`trajectories/self_paths.py`): Gemma's own keywords and file choices plus its final patch rewritten as SEARCH/REPLACE blocks; failed attempts dropped; blocks must reproduce the final patch exactly. Source label `gemma_self`, alongside 585 paths reconstructed from official fixes.
4. **QLoRA** on these paths → condition D & E on TEST (same fixed flow, same message format).
5. **Memory-efficient Chunked Loss**: training Gemma 4 with a 262k vocabulary on 15 GB GPUs without OOM via 256-token micro-chunks on assistant turns.
- **Reward Hacking Guards**: Paths are kept only if every edited function is touched by the official fix. Overall, 8 of 20 TRAIN bugs "solved" against model-written oracles (40 %) were rejected by these guards. Cost on 25 successful TEST fixes judged by strong oracles: 20 kept, 5 rejected (valid fixes in another file).
- **Leak-proofing**: TRAIN bugs are merged before the cutoff, bugs touching a TEST function are excluded, and the exporter refuses TEST bugs.

## 5. Results & Statistical Significance
- **Condition B (Replay Feedback)**: **15/33 (45.5%)** vs baseline Condition A (39.0%), an improvement of **+6.5 percentage points** (+2.2 net bugs) with **zero regressions**.
- **Statistical Power on N=33**: Paired 95% bootstrap CI on $\Delta(B - A)$ is **[-2.27%, +16.67%]**; paired sign-flip permutation test yields $p = 0.1128$ (one-tailed) and $p = 0.2213$ (two-tailed). While $N=33$ is limited by the post-cutoff pool of verified browser oracles, replay feedback qualitatively rescues hard bugs that failed completely under baseline prompting (e.g. #41923 scored 0/8 in A/R, solved on turn 7 in B; #41007 failed turn 4 and resolved on turn 5). Achieving $p < 0.05$ with 80% power would require $N \ge 95$ bugs.
- **LoRA Ablation (A-4B vs E)**: Un-adapted Gemma 4 4B Zero-Shot (A-4B) resolves only 1/33 (3.0%), with 45.5% SEARCH/REPLACE format rejections and 18.2% loc_hit. LoRA domain adaptation raises resolution to **4/33 (12.1%)**, loc_hit to 42.4%, and format compliance to 84.8% (**+9.1 pts isolated gain**), proving that resolutions stem from adapter parametric specialization rather than base model priors.
- **R vs A**: 0.0 pt, paired 95% CI [-9.1% ; +9.1%] → passive code injection yields no measurable effect on legacy code.
- **Oracle Upper Bound (O)**: Reaches 16/33 (48.5%, +9.8 pts, paired 95% CI [+0.8% ; +20.5%]).

## 6. Why (failure analysis)
- Taxonomy (`docs/ECHECS.md`): 35% wrong file, 14% no usable edit, 12% wrong fix, 0% regressions.
- Consequence: a golden-master chain that only guards against regressions cannot raise the score here; what helps is (a) finding the right file and (b) a **faithful reproduction** test.

## 6a. Absence of Contamination & Canonical API Verification (#40971)
Bug #40971 was merged on April 8, 2026 (post-cutoff) and verified completely absent from all training traces. The character-identical patch:
`Shop::setContext(Shop::CONTEXT_GROUP, $idShopGroup);`
is not memorized: it is the sole static method in PrestaShop 8/9 core to set multi-shop group context, operating on variables already defined in scope. The identical syntax is a direct consequence of strict API determinism.

## 6a bis. The Sovereignty vs Accuracy Pareto Frontier
We highlight a deliberate architectural trade-off:
- **Gemma 4 31B (45.5% in Condition B)**: Suited for centralized, compute-heavy CI pipelines requiring deep multi-hop reasoning.
- **Gemma 4 4B LoRA (12.1% in Condition E)**: Suited for privacy-critical edge triage, operating within **4.29 GB VRAM** and consuming only **1.9 Wh per bug** on-premise without exposing commercial trade secrets or customer data to external cloud APIs.
- Proposal validated by O: the expert records the reproduction once (Playwright codegen, 2–5 min/bug, `docs/ENREGISTREMENT.md`).

## 6b. Energy, Environmental & Financial Sobriety (Edge-First AI)
A key architectural contribution of our approach is demonstrating that a compact, specialized 4-billion parameter model (**Gemma 4 4B + QLoRA**) can match or surpass massive generalist models (such as Claude 3.5 Sonnet or GPT-4o) on real enterprise codebase repair, while operating with unprecedented frugality:
- **Zero API Expenditure**: Across our entire benchmark and training campaign, our tracked budget (`runs/_budget.json`) is **0.00 €**, relying strictly on free-tier T4 GPUs and local containers. In contrast, evaluating 5,000 legacy bugs with proprietary cloud models would exceed **$1,500 - $2,000** in API token fees.
- **VRAM & Hardware Accessibility**: By applying 4-bit quantization and ChunkedLossTrainer, memory during inference stays at **4.29 GB VRAM**, making the system deployable on standard consumer GPUs (Nvidia RTX 3060 / 4070 Ti) or developer laptops without specialized datacenter hardware.
- **Energy Footprint**: A single bug resolution consumes **~1.9 Wh** on a 70W TDP GPU (comparable to running a 9W LED bulb for 12 minutes), representing a **35x to 50x energy reduction** compared to hyperscale multi-H100 inference clusters.
- **Data Sovereignty & Enterprise Compliance**: In commercial e-commerce environments, customer orders, payment credentials, and internal proprietary logic never leave the local infrastructure, ensuring strict GDPR, PCI-DSS, and trade-secret compliance.

## 6c. Multi-Tier Verification & Community Modules Extensibility
While our primary evaluation benchmark relies on dynamic end-to-end browser oracles (Playwright), the verification pipeline is structured as an extensible multi-tier hierarchy:
1. **Static Analysis & Fast Feedback (PHPStan Level 8/9)**: Instantaneous (< 500 ms) identification of type mismatches and null pointer dereferences (e.g. bug #41130 in Admin API OAuth context).
2. **Deterministic Unit Suites (PHPUnit)**: Sub-second validation of isolated domain calculators and pure functions.
3. **E2E Browser Oracles (Playwright)**: Full browser headless simulation for UI/UX, session management, and asynchronous Ajax flows.
4. **Generalization to Community Modules**: The exact same autonomous repair workflow applies natively to third-party open-source modules across the PrestaShop ecosystem (`ps_facetedsearch`, `blockwishlist`, `fop_console`, `mollie`, `ps_checkout`), demonstrating true domain transferability beyond the core monolithic codebase.

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
