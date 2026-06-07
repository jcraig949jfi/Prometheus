# Greedy LoRA follow-up — progress log (2026-06-07)

Directive (James): run all four greedy-followup tasks **sequentially**:
1. Ablate greedy sources (which of the 6 sources carry weight)
2. Score CounterMath OOD properly (real accuracy number)
3. Charon adapter expansion + re-eval (does more varied failure data grow the reasoning share)
4. Un-stall Theseus handoff to ship kills

Doc-as-you-go: this file is updated as each step lands; nothing load-bearing stays in chat.

## Environment (verified 2026-06-07)
- Interpreter: `C:/Users/jcrai/AppData/Local/Programs/Python/Python311/python.exe` — torch 2.11.0.dev+cu128, CUDA available. (default `python` = 3.12, NO torch.)
- Model: local Qwen2.5-Math-1.5B-Instruct snapshot under `E:/hf_cache/hub` (rig auto-resolves).
- Rig: `ergon/learner/greedy/{build_corpus,train_greedy,eval_greedy,sources,serializers}.py`.

## Baselines carried in (from GREEDY_LORA_RESULT_2026-06-03.md)
- Base Qwen2.5-Math-1.5B: gold acc 0.228 (parse-fail 0.653; 0.000 on False).
- Greedy LoRA v1 (real labels): 0.907. Shuffled control: 0.681. Content effect +0.226.
- Entity-disjoint: E-hidden 0.744, E-shown 0.841. Reasoning share ~0.10 (E-shown − E-hidden).
- v1 corpus: 18,464 train, 59.6% failure. Sources: theseus 13200, hephaestus 4346, charon_md:stygian 583, erebos 233, pollux 86, harmonia 16. Gold eval: theseus 800 / pollux 200 / hephaestus 200 (600T/600F).

## CounterMath blocker (task 2)
- Cached copy `E:/hf_cache/.../countermath_eval.jsonl` (1,216 rows) has NO gold label — fields: statement, chinese_statement, field, txt(=filename). Need labeled CounterMATH or LLM-judge. Resolve before task 2.

---

## Task 1 — source ablation
Design: leave-one-source-out on TRAIN only; eval on fixed `gold_eval_v1.jsonl` (1200, 600T/600F). Config matches headline: rank 16, 1 epoch. Conditions: full + minus-{theseus,hephaestus,erebos,pollux,charon_md,harmonia}.

Launched: `ergon/learner/greedy/run_ablation.sh` (background, detached) — 7 conditions train+eval, logs to `runs/ablation/ablation_run.log`. Full condition confirmed healthy (LoRA trainable% 0.28). Added `--skip-base` to eval_greedy (additive) so base is measured once.

### Task 1 RESULT — source ablation (acc on fixed 1200-item gold)
Reproduction check: full = base 0.2283 / trained 0.9083 (matches headline 0.228/0.907 exactly). Rig sound.

```
condition         acc      d_vs_full   T      F      | thes   poll   heph
base             0.2283               0.457  0.000  |  (parse_fail 0.65, always-True bias)
full             0.9083   +0.000     0.905  0.912  | 0.863   1.0    1.0
minus_charon_md  0.9133   +0.005     0.927  0.900  | 0.870   1.0    1.0
minus_erebos     0.9050   -0.003     0.900  0.910  | 0.858   1.0    1.0
minus_harmonia   0.9033   -0.005     0.908  0.898  | 0.855   1.0    1.0
minus_hephaestus 0.7883   -0.120     0.903  0.673  | 0.860   1.0    0.29
minus_pollux     0.8092   -0.099     0.912  0.707  | 0.865   0.395  1.0
minus_theseus    0.5000   -0.408     0.000  1.000  | 0.250   1.0    1.0
```

**Findings (calibrated, somewhat deflating — a useful kill):**
1. **The gold task decomposes into 3 independent per-source slices with ~zero cross-source transfer.** Each gold-labeled source teaches only ITS OWN slice: drop theseus → theseus slice 0.86→0.25 (overall collapses to all-False, −0.41); drop hephaestus → heph slice 1.0→0.29; drop pollux → pollux slice 1.0→0.395. Other slices are untouched each time. Hephaestus+pollux+charon training cannot teach knot×EC judgement, and vice-versa.
2. **The pure failure-reasoning sources contribute ZERO to the gold metric.** Removing erebos (composed-falsification), charon_md (prose), or harmonia (retractions) moves accuracy by ≤0.005 (within noise). Caveat: these have NO gold-eval slice of their own, so the ablation measures only their *transfer* to the gold slices — which is nil. It does not measure their value on a "predict the failure mode" task (no held-out eval exists for that).
3. **The gains look like per-template class-learning, not reasoning.** pollux gold claims are all-False templated ("correlation survives normalization" → False by construction); 86 train rows → 1.0 on its 200-item slice; remove them and the model reverts toward its True-prior (0.395). Same shape for hephaestus. This matches the entity-disjoint decomposition where genuine reasoning (~0.10) was the smallest component.

**Implication:** the greedy corpus's measured gold gain is the sum of three narrow template-classifiers; the richest "what-doesn't-work" data adds nothing *to this metric*. To grow the reasoning share, both the data (cross-domain claims, multi-step, balanced-within-template) and the eval (a transfer test, not per-source slices) must change. Task 2's computable-gold OOD set is exactly that transfer test.

Artifacts: `runs/ablation/abl_eval_*.json`, `runs/ablation/ablation_summary.json`, `aggregate_ablation.py`.

(status: task 1 DONE; OOD eval running)

## Task 3 RESULT — diverse-gold transfer test (reframed)
Original "Charon adapter expansion" was reframed after two findings made it low-yield:
- **Stygian's structured kill_ledger is ~95% infrastructure exhaust** (366/373 UNVERIFIED, 344 skipped; kill_patterns `hecate_meta_test_not_yet_implemented` ×242, `no_loader_registered` ×101). Only ~29 real verdicts, all open-problem conjectures (Lehmer/BSD) with no computable gold. Wiring it is the "logged ≠ navigable" trap. The rich Charon content the rig already gets via prose adds nothing to the gold metric (ablation).
- So the high-value version: **does adding balanced, computable-gold judgement data from a NEW meta-domain (number theory) correct the False-prior and transfer to HELD-OUT sub-domains?** Train = substrate v1 + 3,200 balanced rows across 4 NT domains (primality/divisibility/coprime/modular); held-out = 3 disjoint NT domains (perfect_square/summation/inequality); 1 epoch, rank 16.

```
                       held-out acc   T      F      perfect_sq  summation  inequality
full (no OOD train)    0.5317        0.287  0.777   0.600       0.510      0.485
transfer (+4 NT dom)   0.5583        0.357  0.760   0.695       0.510      0.470
delta                  +0.0266       +0.070 -0.017  +0.095      0.000      -0.015
substrate gold: 0.9083 -> 0.9025 (no regression)
```

**Verdict — transfer is essentially absent, even within number theory.** +0.027 overall on n=600 (~1.3σ, NOT significant). The entire lift is perfect_square (+0.095, ~2.7σ); summation and inequality are flat. The decisive read: **transfer appears only where the surface pattern is shared (perfect_square) and is absent exactly where genuine computation is required** (summation needs n(n+1)/2; inequality needs comparing 2^k). The False-prior barely moved (T 0.29→0.36, still ≪0.5). So the greedy LoRA is a bag of per-template surface classifiers; balanced same-meta-domain gold does not induce reasoning at this scale (rank-16, 1 epoch, 1.5B). This is the sharpest statement of the kill.

Artifacts: `runs/transfer/{eval_heldout_baseline,eval_heldout_transfer,eval_gold_transfer}.json`, `corpus/{ood_train,ood_heldout,train_transfer}.jsonl`, `run_transfer.sh`.

## Task 4 RESULT — un-stall Theseus handoff
State found: pipeline stalled since **2026-05-19** (last consumed bundle; daemon last fire May 25; Penelope ingesting 0). The audit's rec #1 (open gate to kills) was ALREADY implemented post-audit (Fire #33: REJECTED in verdict_filter; 20% falsify floor). What actually remained:
1. **Root cause of the stall found + fixed:** `export_for_ergon`'s scoring loop walked the **entire 346 GB / 265-batch corpus** to pick 500 records, while only the episode index was bounded by `max_recent_files`. A full walk per 30-min cycle is infeasible → that's why it stalled. Fixed `_iter_corpus_records` to honor `max_recent_files` (newest-N batches), threaded it through `export_for_ergon`'s scoring loop, and added a `--max-recent-files` CLI arg (default 5) so a direct call can't accidentally walk 346 GB. Tests unaffected (call `export_for_ergon` directly): **7/7 handoff tests pass.**
2. **Falsify floor raised 0.20 → 0.40** (proportional to corpus's ~40% kill rate; failures first-class per audit rec #5 + doctrine). Scoped caveat in-comment: the ablation kill is about the gold-judgement metric, NOT the Learner's routing objective (no eval yet) — failure-first representation stays correct for the Learner's actual purpose.
3. **Re-ran the handoff** (bounded, newest-5 batches) — and the re-emit surfaced the pipeline is **doubly blocked**, not just stalled:
   - **First re-emit:** 141,435 candidates → 500 emitted, but **all degenerate** (relation=None, catalog `?_x_?`, all generator d2 = `kill_neighborhood` kills). The `training_anchor` mapper renders **only `invariant_equality` knot×EC** records; every other kind → placeholder `Does relation `?` hold…` garbage. **This is the real reason the main Learner corpus is a knot×EC confirmation monoculture** — the mapper silently mangles all other kinds, and kills are disproportionately other kinds.
   - **Added a mappability gate** (skip non-`invariant_equality` / no-relation records → never ship garbage) and quarantined the d2 bundle (`ergon_outbox/quarantine_20260607/`).
   - **Second re-emit:** 0 candidates — because recent `invariant_equality` records score **w mean 0.199, max 0.330 (0% ≥ 0.5 threshold)**, while the unmappable d2 kills sit exactly at 0.5. So the only mappable kind is below threshold and what clears threshold isn't mappable.

**Final disposition (safe state, strictly better than found):** mechanism un-stalled (bounded walk — daemon runnable, won't hang on 346 GB); floor at 0.40; gate ensures **nothing-or-clean, never garbage**; inbox empty. The handoff cannot ship useful failure data until **Theseus-side** fixes land: (a) extend the mapper to all claim_kinds — port `ergon/learner/greedy/serializers.py` (already renders kills correctly), and (b) recalibrate `training_weight`/threshold so `invariant_equality` kills clear the bar (they score ~0.2 now). Given the ablation kill (more of this data won't grow reasoning), ship-nothing-until-fixed is the correct conservative state.

Files: `theseus/handoff/ergon_handoff.py` (+46/−6; 4 edits, all commented as Ergon 2026-06-07). Tests 7/7. Logs: `handoff_reemit*_20260607.log`.

## Task 3 prep — Charon pantheon survey (filesystem)
Structured `kill_ledger.jsonl` present for: erebos (233), pollux (286), **stygian (373)**. Rig ingests pollux+erebos as STRUCTURED but stygian only as low-trust prose (charon_md:stygian, 583 rows, trust 0.4). Expansion opportunities:
1. Add **stygian structured kill_ledger adapter** (373 rows, promote to tier-1 trust).
2. erebos has `kill_ledger_enriched.jsonl` + `kill_ledger_scale_stress.jsonl` — unused.
3. charon_md only yielded from stygian; lethe/acheron/hecate/moros/nephele artifacts gave no parseable verdicts.

## Task 2 — CounterMath blocker RESOLVED (by substitution)
**CounterMATH ground truth is withheld by design.** THUKElab/COUNTERMATH README (fetched via raw.githubusercontent — api.github.com is unreachable from this host; HF + raw.* are): *"The ground truth is not publicly available for ensuring high-quality evaluation. You can submit your results"* to the leaderboard. `data/countermath_ver1.1.jsonl` carries no judgement; `Sheaa/CounterMATH` HF repo 404s even with token; only the label-stripped `Sheaa/countermath_eval` is public. So a real, authoritative CounterMath accuracy number is impossible offline — only a circular LLM-judge or a leaderboard submission could approximate it. Not fabricating one.

**Stand taken:** deliver the *intent* (a real OOD accuracy number for the trained model's judgement behavior) via a **computable-gold OOD set** — `ergon/learner/greedy/ood_judgement.py`. 494 rows, balanced 247T/247F, 0 independent-recheck mismatches, 7 number-theory domains (primality, divisibility, coprimality, perfect-square, modular, inequality, summation) all DISJOINT from training (knot×EC / Mahler / forge). Gold computed deterministically — non-circular, reproducible, offline. Rows are eval_greedy-schema-compatible → scored with the existing harness. The CounterMath distribution-shift probe (unscored direction) is retained as free signal.

### Task 2 RESULT — OOD judgement (computable-gold, 494 balanced) + CounterMath direction
```
                acc     T      F      parse_fail
OOD base       0.000   0.000  0.000  1.000   (base emits NO verdict in 8 tokens on these — pure format failure)
OOD trained    0.5506  0.198  0.903  0.000   (always answers; heavy False-lean)
by-domain (trained): coprime 0.625, perfect_square 0.60, inequality 0.57, divisibility 0.54, modular 0.54, primality 0.50, summation 0.50
```
CounterMath direction (no gold; distribution only): base {unparsed 50, true 56, false 14} → trained {false 103, true 17, unparsed 0}.

**Verdict — OOD reasoning transfer is weak, and it's a prior, not reasoning.**
- **Format transfers fully** (parse_fail 1.0 → 0.0). The biggest, most robust effect — consistent everywhere.
- **Judgement barely transfers**: 0.5506 vs 0.50 chance on a balanced set (n=494, SE≈0.022 → ~2.3σ over chance). The T/F asymmetry (0.20/0.90) shows this is mostly a **False/kill prior** the failure-data instilled, not discrimination. A pure-False model scores 0.50 here; the extra +0.05 is faint signal concentrated in coprimality/perfect-square; primality & summation show **zero** (0.50).
- **The False-lean explains the CounterMath shift** (86% False): directionally "correct" only because CounterMath is counterexample-heavy. The balanced OOD set proves the lean is **indiscriminate** — it tanks True-claim accuracy to 0.20. So the earlier "plausibly good, unverified" CounterMath direction is now explained: it's a prior, not OOD reasoning.

This corroborates the ablation decisively: **no cross-domain transfer.** The in-domain reasoning (~0.10, entity-disjoint) does not generalize to unseen number-theory relations. Real OOD number for the record: **~0.55 (barely above chance), prior-driven.**

Artifacts: `runs/eval_ood.json`, `runs/eval_ood.log`, `corpus/ood_gold.jsonl`, `ood_judgement.py`.
