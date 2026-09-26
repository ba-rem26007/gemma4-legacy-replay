# Writeup Kaggle — brouillon (phase 9)

> Brouillon en anglais, 3 000 mots max. Les chiffres entre ⟦ ⟧ sont **provisoires** : réévaluation complète en cours après la correction de l'évaluateur (26 sept.). Ne rien publier avant `docs/RESULTATS.md` définitif.

---

## Title
**Making Legacy Verifiable: Replay Tests for a Gemma 4 Bug-Fixing Agent on PrestaShop**

## Subtitle
A reproducible benchmark of real, post-cutoff PHP bugs with hidden end-to-end browser oracles, and what actually helps a small open model fix them.

## Abstract
Agentic code-repair benchmarks are dominated by Python projects with rich unit test suites. Most production code is not like that. We build a benchmark on **PrestaShop**, a large legacy PHP e-commerce platform (1.6 → 9.1): 33 real bugs fixed upstream **after** Gemma 4's knowledge cutoff, each with a hidden **end-to-end oracle** (Playwright test run against a live shop, fails before the official fix, passes after), plus a leak-proof training pool of ≈ 4,800 older bug fixes and 569 verified reconstructed repair paths. We then measure, with a fixed-flow Gemma 4 31B agent, what an environment can add: retrieved similar fixes, tests written from the ticket, a business glossary, and — as an upper bound — the oracle itself as feedback. ⟦Baseline: 39 % solved; retrieved fixes: no effect; oracle as feedback: +3 bugs (39 % → 48 %)⟧. The dominant failure is **localisation** (⟦35 %⟧ of attempts never open the file that was fixed), not patch logic. All tools, data and traces are released; no proprietary model output is used as training data.

## 1. Introduction
- Legacy code is where developers need help most and where verification is weakest (no tests, UI-driven behaviour, database state).
- Question Q1: can **replay tests** (recorded front-office / back-office interactions) turn a legacy bug into a verifiable task for an open model?
- Question Q2: which kind of help matters — examples, tests, vocabulary, or a perfect verifier?
- Question Q3: can we build a leak-proof self-training loop without distilling a proprietary model?
- Contributions: (1) benchmark + environment, (2) controlled conditions A/B/C/R/O with repeated trials and paired CIs, (3) failure taxonomy, (4) negative results reported as is, (5) data factory for fine-tuning.

## 2. Benchmark and environment
- Bug selection: merged bug-fix PRs with a linked issue, security fixes excluded, temporal split on the model cutoff (provisional 2025-06-01; see `data/ETANCHEITE.md`).
- Environment: official Docker images, nearest release, **incremental upgrade** within 9.1.x (database kept, as in real shops), DB snapshot reset before each bug, parallel instances.
- Oracles: one Playwright spec per bug, hidden from the agent; verdict = oracle passes **and** smoke anti-regression (FO home + BO login) passes.
- Validity: 37 replayable → 33 oracles fail on pre-fix and pass on post-fix code; 4 excluded.
- Evaluator audit: a leak between evaluations (agent-edited files outside the official diff not restored) was found and fixed; all verdicts re-evaluated on fresh instances. ⟦à confirmer⟧

## 3. Agent
- Fixed flow (lesson from SWE-Gym / Agentless): LOCATE (keywords) → READ (≤ 3 files, windows) → EDIT (SEARCH/REPLACE) → TEST (≤ 2 corrections), ≤ 2 backtracks.
- Same message format for evaluation and training traces.
- Gemma 4 31B via Google AI Studio, temperature 0.2, reasoning stripped from context; cost ⟦0 €⟧.

## 4. Conditions
| Code | Agent sees | Purpose |
|---|---|---|
| A | ticket | baseline |
| R | ticket + 2 similar fixes from TRAIN (TF-IDF) | fine-tuning simulated by context |
| B | ticket + replay tests written from the ticket | realistic verifier |
| C | ticket + business glossary (term → code symbol) | localisation help |
| O | ticket + **oracle** feedback (deliberate leak) | upper bound of any verifier |
| D | fine-tuned model | planned |

## 4b. Self-improvement loop (Gemma only, no distillation)
The only condition with a significant gain is O: execution feedback from a faithful verifier. We turn that into training data without any proprietary model:
1. **Gemma writes verifiers for TRAIN bugs** (`bench/gentest.py`): from the ticket and the official fix, it writes a Playwright oracle, kept only if it **fails on the pre-fix code and passes on the fix** (up to 3 attempts with the error fed back). Verifiers are never training data.
2. **Gemma fixes TRAIN bugs with that verifier as feedback** (condition O on TRAIN, `ORACLE_PREFIX=g`).
3. **Successful runs become condensed paths** (`trajectories/self_paths.py`): Gemma's own keywords and file choices plus its final patch rewritten as SEARCH/REPLACE blocks; failed attempts dropped; blocks must reproduce the final patch exactly. Source label `gemma_self`, alongside ⟦569⟧ paths reconstructed from official fixes.
4. **QLoRA** on these paths → condition D on TEST (same fixed flow, same message format).
Leak-proofing: TRAIN bugs are merged before the cutoff, bugs touching a TEST function are excluded, and the exporter refuses TEST bugs.
⟦Pilot: n oracles validated / 10; paths collected; D results⟧

## 5. Results
⟦Tableau définitif depuis `docs/RESULTATS.md` : 4 essais A/R, pass@4, IC bootstrap apparié⟧
- R vs A: ⟦−0.8 pt, 95 % CI −10.6/+8.3⟧ → no measurable effect.
- B: tests written from the ticket reproduce 10/33 bugs, only 1 faithfully; on those 10, ⟦B 3.5 vs A 4.5⟧.
- O: first attempt ⟦13/33⟧ (≈ A ⟦12.8⟧), ⟦16/33⟧ after oracle feedback (+3 bugs) → a perfect verifier adds ⟦+9.8 pts, paired 95 % CI +0.8/+20.5⟧; it is the ceiling of any replay chain on this flow.
- Model size: 26B-A4B ⟦15 %⟧ vs 31B ⟦39 %⟧ at similar localisation.
- C (automatic glossary, 1 trial): ⟦13/33⟧ vs A ⟦12.8⟧; on the 16 tickets where it fires, right file ⟦6⟧ vs A ⟦7.75⟧ → an automatically mined glossary does not help localisation (negative result).

## 6. Why (failure analysis)
- Taxonomy (`docs/ECHECS.md`): ⟦35 %⟧ wrong file, ⟦14 %⟧ no usable edit, ⟦12 %⟧ wrong fix, 0 regressions.
- Consequence: a golden-master chain that only guards against regressions cannot raise the score here; what helps is (a) finding the right file and (b) a **faithful reproduction** test.
- Proposal validated by O: the expert records the reproduction once (Playwright codegen, 2–5 min/bug, `docs/ENREGISTREMENT.md`).

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
