# Making a Legacy PHP Monolith Verifiable for a Gemma 4 Bug-Fixing Agent

### Hidden replay oracles on 33 post-cutoff PHP bugs, and how often a Gemma-only self-learning loop games its own tests

**Author:** Rémi Soubeyrand · Kaggle "Google – The Gemma 4 Developer Agent", Paper Track
**Code, data and traces:** https://github.com/ba-rem26007/gemma4-legacy-replay (Apache-2.0)

---

## Abstract

Code-repair benchmarks mostly use Python projects that ship unit tests. Much of the web runs on PHP [W3Techs], often legacy code where a bug only shows in a browser session against a database. We make one such monolith, PrestaShop, **verifiable**: each of 33 real bugs, fixed upstream after our 2025-06-01 split, gets a hidden Playwright oracle run against a Dockerized shop with a reset database, failing before and passing after the official fix. A fixed-flow Gemma 4 31B agent solves 12.8/33 from the ticket alone (38.6%, mean of 4 trials). Similar fixes (R) and a glossary (C) add nothing measurable. Gemma-written reproduction tests with execution feedback (B) reach 15/33 in a single run (+6.8 pts, 95% CI [−2.3, +16.7], p ≈ 0.11, not significant). The hidden oracle as feedback, an approximate ceiling in this flow (single run), reaches 16/33. We then close the loop with Gemma alone: it writes oracles for older TRAIN bugs, then fixes them. Of 41 "solved" bugs, **13 (32%) edit code outside the official fix** and are rejected by guards: without such a reference, the loop can reward gaming its own tests. We also report a modest QLoRA run of Gemma 4 E4B on two free T4 GPUs.

## 1. Problem

PHP runs on 69.8% of websites whose server-side language is known (W3Techs, 30 September 2026). Much of that code is "legacy" in Feathers' sense: code without tests [Feathers]. SWE-bench-style evaluation assumes the repository's own tests can judge a patch [SWE-bench]. Multi-SWE-bench adds seven languages but no PHP [Multi-SWE]. In PrestaShop, a typical bug (#41921, "Not able to change stock behaviour in shared stock") depends on multistore configuration, database rows and a back-office form. No unit test exists that would fail on it.

We ask three questions:
- **Q1.** Can end-to-end replay (browser + database) turn such bugs into verifiable tasks for an open model?
- **Q2.** Which help matters: examples, vocabulary, tests written from the ticket, or the hidden oracle itself?
- **Q3.** Can Gemma bootstrap its own training data from its own verifiers, without any proprietary model?

**Contributions:** (1) a replay benchmark of 33 post-cutoff PHP bugs with hidden browser+database oracles; (2) a measured comparison of verifier types for Gemma 4; (3) a Gemma-only self-learning loop where guards against the official fix reject 13 of 41 "solved" bugs.

## 2. Benchmark

**Selection.** `bench/select.py` keeps merged functional bug-fix PRs with a linked issue that touch at most 3 files. Of the 187 catalogued bugs merged after our 2025-06-01 split, 55 candidates from the 9.1.x branch were screened by hand (`data/bugs_test.csv`). **33** got a valid oracle. The other 22 were excluded, mostly because they need a JavaScript build (13) or have no reproducible UI path (5). The 33 fixes were merged between 2026-02-12 and 2026-07-22. Gemma 4's declared training cutoff is January 2025 [Gemma4-card], so the split leaves 5 months of margin. Five TEST issues (#20448, #29009, #29663, #35690, #36058) were **opened** before the cutoff (numbered before PR #37679, merged in 2024), so their ticket text may have been seen in pre-training. Only their fixes are later.

**Environment.** `bench/checkout.sh <pr> pre|post|patch.diff` starts the nearest official `prestashop/prestashop` image with MySQL 8.0, applies a database snapshot and puts the touched files in the requested state.

**Oracles.** Each bug has a Playwright spec (27 back office, 6 front office) plus a `setup.sql`, in the record-and-replay tradition of web testing [WATERFALL, WebTesting]. The agent never sees it. A bug counts as solved only if the oracle passes **and** a smoke test (front-office home page and back-office login) passes on a freshly reset database.

**Evaluator audit.** Files edited outside the official diff were not restored between bugs; after fixing this we re-ran the verdicts on fresh instances without calling the model again (`bench/reeval.py`). 322 of the 462 verdicts in `eval/results.csv` come from that re-evaluation.

## 3. Agent

Following Agentless [Agentless] rather than an open-ended agent [SWE-agent], the flow is fixed and short (`agent/run.py`, `agent/flow.py`):

1. **LOCATE.** The model returns keywords, which we grep in the repository.
2. **READ.** The model picks at most 3 files and sees keyword-centred windows of them.
3. **EDIT.** The model writes SEARCH/REPLACE blocks. It may backtrack twice to search or read again.
4. **TEST.** Feedback conditions only: up to 2 corrections, each showing the test output and the current edited files.

The main model is Gemma 4 31B [Gemma4] through the Google AI Studio API at temperature 0.2. The whole campaign used **3,910 API calls and cost 0 €** (`runs/_budget.json`).

## 4. Results

| Cond. | What the agent sees (Gemma 4 31B unless noted) | Solved /33 | Right file | Regr. |
|---|---|---|---|---|
| A | Ticket only; 4 trials (12/13/15/11) | **12.8 (38.6%)** | 19.8 | 0 |
| R | + 2 similar TRAIN fixes (TF-IDF) + glossary (8 tickets); 4 trials | 12.8 (38.6%) | 20.2 | 0 |
| C | + auto glossary; static repro test (10 bugs) | 13 (39.4%) | 18 | 1 |
| B | + Gemma-written repro test **with feedback** (10 bugs); 1 run | **15 (45.5%)** | 17 | 0 |
| O | + **hidden oracle as feedback** (approx. ceiling); 1 run | **16 (48.5%)** | 19 | 2 |
| A-26B | Ticket only, Gemma 4 26B A4B | 5 (15.2%) | 21 | 0 |
| E | Gemma 4 E4B + our LoRA + rules, glossary, B-style feedback | 4 (12.1%) | 14 | 1 |

Right file: attempts reading the officially fixed file (mean for A, R). Regr.: smoke-test regressions. A-26B is `A-4B` in `eval/results.csv` (from `bench/results.py`). A solves 17/33 at least once over 4 trials. CIs: paired per bug against A, 95% bootstrap, 5,000 resamples, `random.seed(0)`, as in `bench/results.py`.

**What does not help (Q2).** R − A = 0.0 pts, CI [−9.1, +9.1]: two similar historical fixes (plus the glossary on 8 tickets) change nothing. C's glossary matched 16 tickets without improving localisation (18 vs 19.8 right files); an index of back-office pages (11/33) did not help either.

**Approximate ceiling (O).** Feeding back the hidden oracle is a deliberate leak approximating the most a verifier could give in this flow. The first attempt solves 13/33, like A; feedback lifts it to 16/33 (#41299, #41394, #41923): +9.8 pts, CI [+0.8, +20.5], the only interval entirely above zero, barely. Two O attempts broke the smoke test (#41225, #41573).

**Realistic verifier (B).** `bench/reprotest.py` asks Gemma for a Playwright reproduction test **from the ticket alone**, kept only if it fails on the current code. This worked for 10 of 33 bugs (on the other 23, B's prompt equals A's). Only 1 of those tests passes with the official fix; on the other 9, no candidate patch ever passed it, including the 5 the hidden oracle accepts: the feedback was a constant "fail". B solves 15/33: +6.8 pts over A's mean, CI [−2.3, +16.7], one-sided sign-flip permutation p ≈ 0.11 (two-sided 0.23), **not significant**. It is a single run: 15 equals A's best trial (A ranges 11–15), is below A's 17/33 over 4 trials, and B reads the right file less often (17 vs 19.8). The split:
- On the 10 bugs with feedback, B solves 6 against 4.5 for A.
- On the 23 bugs without feedback, B solves 9 against 8.25 for A, likely sampling noise.
- Two earlier exploratory B runs on the same 10 bugs used an older flow version and solved 4 and 3.

The clearest case is PR #41923 ([link](https://github.com/PrestaShop/PrestaShop/pull/41923), issue #41921): 0/8 across A and R, solved in all 3 B runs (main plus two exploratory) and in C. In the main B run the final patch is identical to Gemma's first edit, written before any test output; the two failing rounds only caused a revert and a restore. The gain comes from seeing the reproduction test, not from execution feedback.

**Smaller models.** Gemma 4 26B A4B with the ticket alone solves 5/33 (−23.5 pts, CI [−38.6, −9.1]). It reads the right file at least as often as the 31B model (21 vs 19.8) but applies a patch in only 12/33 cases.

**Answer to Q1.** Replay makes the bugs *measurable* (every verdict reproducible and paired) but only partly *fixable*: the hidden oracle gains about 3 bugs, and a ticket-derived verifier gained less in our single run (+2.2 over A's mean), without statistical support at n = 33.

## 5. Self-learning loop and reward hacking (Q3)

O suggested verifiers as a training signal. We built the loop **with Gemma 4 31B only**, on TRAIN bugs merged before the split (10 of the 99 with a valid oracle share functions fixed after it and are excluded from training data):

1. **Gemma writes the oracle** (`bench/gentest.py`) from the ticket and official fix, kept only if it fails before and passes after the fix. Of 276 bugs, browser oracles: **0 of ~22** (Gemma could not drive the back office reliably); PHP command-line oracles: **99 of ~254** (**39%**). Totals come from `bench/gentest.jsonl`, the mode split from generation logs.
2. **Gemma fixes the bug** in condition O, with its own oracle as feedback. It "solves" **41 of 99**.
3. **Guards** (`trajectories/self_paths.py`) accept a path only if it was re-verified and each edited file and function is also touched by the official fix. **23 are accepted after the function-level split filter. 13 of 41 (32%) edit code outside the official fix** (7 other files, 6 other functions) and are rejected; 3 more, inside it, are dropped because the edited file never appeared in the agent's search.

On #38417 the official fix changes one faulty call to `ImageType::getImagesTypes()` in the webservice. Gemma instead rewrote an unrelated SQL join and added a special case inside `ImageType` (`if ($type === 'customizations') $type = 'products';`), which is enough to satisfy its oracle. On #38168 it edited the right file but a different method, making a query return nothing. We call these **reward hacking**: the model satisfied a model-written test without fixing the bug where the maintainers did.

This is our central finding for RL or self-training on legacy code: **when the oracle is model-written, "tests pass" is not a sufficient reward.** Up to one in three "successes" (13/41) edit code the maintainers did not touch; the two we inspected (#38417, #38168) are symptomatic patches. The guard is conservative (it would also reject a valid fix placed elsewhere), so 13/41 is an upper bound on gaming, not a measured rate. The loop stays usable only because TRAIN bugs have an official fix to compare against. Of the 25 accepted paths, 7 are identical to the official fix and 17 reach ≥ 0.4 similarity (`trajectories/self.jsonl`, `docs/BOUCLE.md`).

## 6. Frugal fine-tuning (modest result)

**Data.** The 585 prepared examples are 569 paths reconstructed deterministically from official TRAIN fixes (`trajectories/reconstruct.py`) plus 16 Gemma paths from the loop, which is how many existed at training time. No proprietary model output is included (unlike [SWE-Gym]), and bugs are real (unlike [SWE-smith]). TRAIN excludes any bug that shares a PR, an issue or a modified function with a TEST bug (`data/ETANCHEITE.md`: 820 TRAIN, 58 excluded). Only **89** examples fit in 2,048 tokens, and only those were trained on.

**Training.** We trained QLoRA on Gemma 4 E4B: 4-bit, r = 16, α = 32, 3 epochs, 18 steps, lr 5e-5, on 2× T4 on Kaggle. It ran for 7,209 s with a mean training loss of 1.192 (`training/snapshots/train_kaggle_v15.py`, `docs/FINETUNING_KAGGLE.md`).

**Chunked loss.** Gemma 4's vocabulary has 262,144 entries. Upcasting the full float32 logits takes 2.15 GB per 2,048-token sequence, 4.29 GB for a micro-batch of 2 (1 per device × 2 T4); `docs/FINETUNING_KAGGLE.md` reports an out-of-memory error. `training/chunked_loss.py` projects only assistant positions, 256 tokens at a time:

```python
for i in range(0, active_h.size(0), chunk_size):
    logits_chunk = head(active_h[i:i+chunk_size]).float()
    total_loss += F.cross_entropy(logits_chunk, active_l[i:i+chunk_size], reduction="sum")
```

The peak logits tensor drops to about 268 MB, 94% less than 4.29 GB (87.5% per sequence) **for that tensor**. Total VRAM was not measured.

**Result.** The complete system E (E4B + LoRA + business rules + glossary + replay feedback on 10 bugs + 2 retries) solves **4/33** (#40971, #41007, #41130, #41193), with one smoke regression (#41299). The nearest reference is Gemma 4 26B A4B with the ticket only (5/33). **This compares two systems, not the LoRA alone**: the models, prompts and feedback all differ, and we have no run of the base E4B model. E applies more patches (18 vs 12) but finds the right file less often (42.4% vs 63.6%). With 89 short examples, the adapter did not give a small model the 31B model's localisation.

## 7. Failure taxonomy

Of the 132 A attempts, 81 fail (`eval/results.csv`, `docs/ECHECS.md`):
- **56.8%** (46) never read the fixed file: localisation is the main bottleneck (34.8% of all attempts).
- **23.5%** (19) read it but produced no applicable edit, because of an inexact SEARCH copy or read-loops.
- **19.8%** (16) applied a wrong fix.

A made no regressions. Over the 8 A+R attempts per bug, 15 bugs are never solved and 3 are always solved. The difficulty is bimodal. The glossary, page index and fine-tuning all failed to add the architecture knowledge localisation needs.

## 8. Limitations

- **Small n.** 33 bugs, one project. B and O are single runs. B's p ≈ 0.11 is not significant, its feedback reaches only 10 bugs, and on 9 of them the test never passed.
- **Weak E.** E is a system-versus-system comparison trained on 89 examples. An isolated LoRA ablation on E4B (`bench/matrix_e4b.py`) is prepared but not run.
- **Pre-training exposure.** Five TEST issue texts pre-date the model cutoff.
- **TEST oracles** were written with Claude's help (see disclosure). Validated by execution and hidden from the agent, they are not independent of our tooling.
- **Evaluation setup.** The 31B model is evaluated through an API, not the local quantized build. Energy was not measured.
- **Loop data hygiene.** #32563 and #31571 touch functions also fixed after the split (TEST bug #41412; post-split #39788). Neither was in the trained snapshot; the exporter now filters them.
- **Perspective.** A Dolibarr ERP port was started; with no trained weights or validated benchmark, we claim nothing about it.

## 9. Reproducibility

- **Benchmark:** `bench/select.py`, `data/bugs_test.csv`, `data/ETANCHEITE.md`, `bench/env/docker-compose.yml`, `bench/checkout.sh`, `bench/replay/run.sh`, `bench/eval.py`, `bench/reeval.py`.
- **Agent:** `agent/run.py`, `agent/flow.py`.
- **Verdicts:** `bench/reprotest.py`, `eval/results.csv`, with traces and patches under `runs/`.
- **Tables:** `bench/results.py` generates `docs/RESULTATS.md` and `eval/results.csv`; all CIs are recomputable from that CSV.
- **Loop:** `bench/gentest.py`, `trajectories/self_paths.py`, `bench/loop_stats.py`, `docs/BOUCLE.md`.
- **Training:** `trajectories/reconstruct.py`, `trajectories/train.jsonl`, `training/chunked_loss.py`, `training/snapshots/train_kaggle_v15.py`.

Internal docs under `docs/` are in French; the numbers come from the CSV/JSONL files and scripts.

Example: `bench/checkout.sh 41923 pre && bench/replay/run.sh 41923` must fail, and `bench/checkout.sh 41923 post && bench/replay/run.sh 41923` must pass.

## AI assistance disclosure

Claude Code (Anthropic) helped build the tooling: scripts, Docker harness, evaluator, and drafts of this text, which the author checked against the repository. The 33 TEST oracles were written with Claude's help, validated by execution, and hidden from the evaluated agent. **No output of a proprietary model is in any training data.** Training examples are reconstructed deterministically from official fixes or produced by Gemma 4 and validated by execution. All reported agent behaviour is Gemma 4's.

## Related works and citations

- [SWE-bench] Jimenez et al., 2023. *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* https://arxiv.org/abs/2310.06770. Python only; judged by the repository's tests, including tests added with the reference fix.
- [Multi-SWE] Zan et al., 2025. *Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving.* https://arxiv.org/abs/2504.02605. Seven languages, no PHP.
- [SWE-agent] Yang et al., 2024. *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering.* https://arxiv.org/abs/2405.15793
- [Agentless] Xia et al., 2024. *Agentless: Demystifying LLM-based Software Engineering Agents.* https://arxiv.org/abs/2407.01489. Closest to our fixed flow.
- [SWE-Gym] Pan et al., 2024. *Training Software Engineering Agents and Verifiers with SWE-Gym.* https://arxiv.org/abs/2412.21139. Trajectories from proprietary models.
- [SWE-smith] Yang et al., 2025. *SWE-smith: Scaling Data for Software Engineering Agents.* https://arxiv.org/abs/2504.21798. Synthetic Python bugs.
- [Feathers] Feathers, 2004. *Working Effectively with Legacy Code.* Prentice Hall, ISBN 0-13-117705-2. https://openlibrary.org/isbn/0131177052
- [WATERFALL] Hammoudi, Rothermel & Stocco, 2016. *WATERFALL: An Incremental Approach for Repairing Record-Replay Tests of Web Applications.* FSE 2016. https://doi.org/10.1145/2950290.2950294
- [WebTesting] Li et al., 2024. *A Survey on Web Application Testing: Over a Decade of Evolution.* https://arxiv.org/abs/2412.10476
- [Gemma4] Gemma Team, 2026. *Gemma 4 Technical Report.* https://arxiv.org/abs/2607.02770
- [Gemma4-card] Gemma 4 model card (training cutoff January 2025). https://ai.google.dev/gemma/docs/core/model_card_4
- [W3Techs] Usage statistics of PHP for websites (69.8%, accessed 30 September 2026). https://w3techs.com/technologies/details/pl-php
- PrestaShop source and the fixes used as ground truth: https://github.com/PrestaShop/PrestaShop
