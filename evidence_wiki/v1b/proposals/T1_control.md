# PROPOSAL T1 (control)

Powered adjudication of selection vs churn in D-5 retention: MUT_REDUNDANT (I1) vs RANDOM eviction (I3), with an MRU replication anchor (I0), on fresh seeds.

This is the control-shaped proposal in the Gen-2 slate: it is the experiment the Gen-1B packet itself names as the single most valuable cheap next step (ergon/gen1b/REVIEW_PACKET_GEN1B_2026-09-01.txt, section 15). It introduces no new policy, no new consumer, no new task battery. Its job is to settle the one contrast Gen-1 left dangling, and to serve as the baseline against which more exploratory Gen-2 proposals are judged.

## Hypothesis

H1 (primary): In the frozen D-5 executable-program ecology, the principled retention policy I1 (evict only residents that are redundant BOTH behaviourally — identical behaviour fingerprint to another resident — AND mutationally — offspring-sketch Jaccard >= 0.50; MRU fallback otherwise) produces higher future capability than arbitrary eviction I3 (uniform-random evictee), where capability is per-lineage CFR: the fraction of the 42 non-control D-5 tasks (families F1–F4) solved exactly within a 30,000-evaluation budget per task.

Point prediction carried forward from Gen-1: delta(I1 − I3) = +1.51 pp (observed at n = 30, p = 0.0228, Holm 0.0912 — suggestive, not established; ergon/gen1b/gen1_primary_results.json).

H2 (secondary, replication): the Gen-1 headline delta(I1 − I0) = +2.78 pp (Holm 0.0040) reproduces on a disjoint seed batch. This arm exists so that a null on H1 is interpretable: without it, "selection does not beat random" is confounded with "the whole Gen-1 effect was fragile to the seed batch."

Estimand (unchanged from Gen-1 prereg, ergon/gen1b/PREREG_GEN1_2026-09-01.txt section 1): the causal effect of the eviction policy INCLUDING its induced search trajectory. NOT the effect of library composition holding candidate generation fixed — exact stream freezing is architecturally impossible under the frozen D-5 consumer (Gen-1A ruling). Any positive result is a claim about policy + trajectory, and must be stated that way.

## Design

Substrate, all frozen and identical across arms (byte-identical imports, no edits):
- Search core: m1.m1_rx, imported unmodified (as in ergon/gen1b/gen1_run.py).
- Admission: frozen m1.admissions (solver + up to 4 behaviour-distinct).
- Mutation operators: frozen physics.mutate.
- Library cap: 64 in every arm.
- Task corpus: the 42 non-control D-5 tasks (F1–F4), identical order in every arm; every task uses the shared 64-point input domain (0..63), verified in Gen-1B Phase 1.
- Budget: 30,000 organism-evaluations per task, every arm.
- agent_d5_blind/ imported read-only, untouched.

Arms (eviction is the ONLY treatment; definitions verbatim from PREREG_GEN1_2026-09-01.txt section 3):
- I0 D5_BASELINE_MRU — evict the oldest resident. Replication anchor.
- I1 MUT_REDUNDANT — evict a resident redundant both behaviourally (exact fingerprint match with another resident) and mutationally (offspring-sketch Jaccard >= 0.50; sketch = 32 matched mutations, seed 4242, computed once at admission and cached); older of a qualifying pair first; MRU fallback when no pair qualifies. I1 policy compute (~1,332 extra sketch mutations + fingerprint evaluations per lineage) is charged and reported, per the no-free-intelligence rule.
- I3 RANDOM — evict a uniformly random resident. The arbitrary-memory comparator.

I2 (EFFECTIVE_USAGE) is dropped: I2 − I3 measured +0.16 pp, p = 0.78 at n = 30; re-running it buys nothing this generation.

Sample size and pairing:
- n = 64 paired lineages per arm (192 arm-lineages total). Lineage L uses nav_seed base 300000 + 1000·L, L = 0..63, in EVERY arm — arms are paired on starting stream. This seed range is disjoint from Gen-1's (200000 + 1000·L, L = 0..29; max 229000), so no lineage is reused from the run that generated the hypothesis.
- Power basis: Gen-1 empirical paired-delta SD for I1 − I3 is 0.0322 (SE 0.005875 at n = 30, gen1_primary_results.json). Planning SD is inflated to 0.036 (the ~80% upper confidence bound on an SD estimated with 29 df). At n = 64, two-sided alpha = 0.05:
  - MDE at 80% power: 2.80 × 0.036 / 8 = 1.26 pp.
  - Power at the Gen-1 point estimate +1.51 pp: ~92%.
  - Power at +1.0 pp: ~60% (disclosed: a true effect near 1 pp can still be missed).
- The MDE (1.26 pp) exceeds the design SE (0.45 pp) by ~2.8×, satisfying the gate-exceeds-measurement-error rule; the 90% CI is reported beside every verdict.

Endpoint and analysis (fixed here; not altered after outcomes are seen):
- Primary endpoint: per-lineage CFR over the 42 tasks.
- Primary contrast (family of ONE, alpha = 0.05 two-sided, no correction needed): I1 − I3. Two-sided paired sign-flip permutation on the 64 lineage-level deltas, 20,000 permutations, seed 424243 (fresh; Gen-1 used 424242). 90% percentile-bootstrap CI resampling lineages. Sign counts (positive / negative / tied) reported alongside.
- Secondary family (Holm within family of two, never promoted to primary): I1 − I0, I3 − I0. Same test machinery.
- Rows ship with the verdict: per-lineage CFR vectors for all three arms and all per-lineage deltas are committed in the SAME commit as the results summary (machine-readable JSON), per the verdict-without-rows rule.
- The analysis script is committed BEFORE any results file is opened; the prereg, runner, and this proposal are committed with recorded git blob hashes before the first experimental organism-evaluation, then pushed and verified with `git merge-base --is-ancestor`.

Instrumentation addition (closes Gen-1B declared gap #1, section 14):
- The runner is extended to log, per lineage, a per-candidate stream digest (hash of each candidate genotype in generation order, buffered and written per task), sufficient to compute (a) first-divergence index between paired arms and (b) candidate-set overlap per task. Descriptive only; never an endpoint.
- Preflight bit-identity gate: before the freeze, the instrumented runner replays Gen-1 lineages L = 0 and L = 1 under I0 and I1 (seeds 200000, 201000) and must reproduce the stored Gen-1 per-task solved/unsolved vectors exactly (84/84 task outcomes per arm-lineage). If it does not, the logging is removed and the run proceeds on the frozen uninstrumented gen1_run.py, with the gap re-declared. Replay outputs are discarded and are not part of the analysis set.

Cost: 3 arms × 64 lineages × 42 tasks × 30,000 = 241,920,000 organism-evaluations; ~78 minutes wall at the measured Gen-1 rate (48.6 min / 120 arm-lineages); local CPU; $0; ~8 MB results + ~2–4 GB candidate-digest logs (compressed, prunable after the divergence summary is computed and committed).

Verdict vocabulary (pre-committed):
- SELECTIVE_BEATS_ARBITRARY (established, bounded to this substrate/battery/budget) — F1 and F2 both pass.
- SELECTION_NOT_SEPARATED — primary p >= 0.05 with CI upper bound >= 1.26 pp.
- SELECTION_BOUNDED_NULL — primary p >= 0.05 and 90% CI upper bound < 1.26 pp: churn explains Gen-1; the honest program summary remains "MRU is the worst rule tried."
- REPLICATION_FAILURE flag — appended to any of the above if F4 fires; all primary readings are then interpreted under seed-batch fragility.

## Controls

1. Arbitrary-memory comparator IS the treatment's control: I3 performs the same number of evictions under the same cap with the same frozen admission stream, differing only in WHICH resident dies. It breaks the selection relation while preserving churn rate, library size, and memory turnover (control-must-break-the-selection-relation doctrine).
2. Replication anchor: I0 on the same fresh seeds controls for seed-batch effects and re-tests the only Holm-surviving Gen-1 claim out-of-sample.
3. Pairing as blocking: identical nav_seed base per lineage across arms removes between-stream variance from every contrast (between-lineage variance share measured at 1.85% in ergon/gen1a/power_analysis_2026-09-01.json).
4. Treatment-purity gates, checked mechanically after the run (any failure voids the run, see falsifier F5): every arm-lineage terminates with exactly 64 artifacts; admission mechanics are the same frozen call in every arm; credit/effective-use bookkeeping consults only trailing-window information; pairing is a function of lineage index only.
5. No mid-run analysis, no adaptive seed selection, no per-arm code paths outside the eviction function: eviction policy is the single dispatch point, as in gen1_run.py.
6. Preflight replay control (above) guards against the instrumentation itself becoming a hidden treatment.
7. Multiplicity control: primary family of one; secondary family Holm-corrected; secondary and descriptive measures (divergence indices, mechanism autopsy quantities) are never promoted if the primary is null (frozen per Gen-1 prereg section 6 discipline).

## Preregistered falsifiers (each with an explicit numeric threshold)

- F1 (primary significance): If the two-sided paired sign-flip permutation p for I1 − I3 at n = 64 is >= 0.05, the hypothesis "principled selection beats arbitrary eviction" is NOT established. No secondary or descriptive measure may rescue it.
- F2 (magnitude gate): A positive claim additionally requires the 90% bootstrap CI lower bound for I1 − I3 to be > 0.0 pp and the point estimate to be >= +1.26 pp (the design MDE). p < 0.05 with mean < +1.26 pp is reported as DETECTED_BELOW_DESIGN_MDE, not as the established effect.
- F3 (bounded null): If p >= 0.05 AND the 90% CI upper bound for I1 − I3 is < +1.26 pp, declare SELECTION_BOUNDED_NULL — the selection component of the Gen-1 result is bounded below the smallest effect this design was built to see, and churn is the standing explanation.
- F4 (replication of the anchor): If the secondary contrast I1 − I0 has Holm-corrected p >= 0.05 at n = 64 (a test with > 99% power at the Gen-1 point estimate of +2.78 pp, and ~94% power even at the Gen-1 CI floor of +1.59 pp), the Gen-1 headline is flagged REPLICATION_FAILURE and every other reading in this experiment carries that flag. This falsifies out-of-sample durability of the only established Gen-1 claim.
- F5 (integrity, run-voiding): the run is declared UNINTERPRETABLE — not null — if ANY of: (a) any of the 192 arm-lineages terminates with a library size != 64; (b) mean distinct-artifacts-admitted differs between any two arms by > 5% (Gen-1 observed range 165.1–166.6, i.e. < 1%); (c) the preflight replay reproduces fewer than 84/84 task outcomes per replayed arm-lineage and the instrumented runner is nevertheless used; (d) any per-task evaluation counter exceeds 30,000.
- F6 (sign-structure sanity, disclosed not gating): if I1 − I3 reaches p < 0.05 while strictly fewer than 55% of non-tied lineage deltas are positive, the result is reported with an OUTLIER_DRIVEN disclosure and the trimmed (10%) mean delta is reported beside the primary.

## Stopping rule

Fixed-length run: 64 lineages × 3 arms, executed to completion, in lineage order. No interim analysis, no optional stopping, no extension or reduction of n after any outcome is seen, no re-randomisation of seeds. If execution halts early (crash, power, operator), the completed paired lineages are analysed exactly as prespecified with their count disclosed, and the run is labelled UNDERPOWERED_PARTIAL (with the achieved-n MDE recomputed and reported) rather than reinterpreted; it is not topped up, because a top-up conditional on an interim look is optional stopping by another name. The only aborts are the F5 integrity gates, which void rather than stop the analysis. One engineering shakedown (2 lineages, 3,000 evaluations, separate _smoke directory, outputs discarded) is permitted before the freeze and disclosed here.

## Unit of inference

The LINEAGE (n = 64 per arm), paired across arms by nav_seed base — the Gen-1A ruling, carried forward unchanged. Every test statistic is computed on lineage-level CFR deltas; no task-level statistic is used for inference anywhere (task-level variance share is 31% and tasks are shared across arms within a lineage, so task-level n would inflate precision — the SE-on-the-wrong-unit failure). Per-task solve indicators are recorded and committed as rows, but only ever aggregated to lineage CFR before testing.

## Prior work bearing on this design (cite repo paths if any; 'none found' is acceptable)

- ergon/gen1b/REVIEW_PACKET_GEN1B_2026-09-01.txt — the Gen-1 result this design adjudicates: I1 − I0 = +2.78 pp (Holm 0.0040, established); I1 − I3 = +1.51 pp (Holm 0.0912, NOT established); section 15 explicitly recommends this powered rerun as the first Gen-2 experiment; section 14 declares the candidate-stream instrumentation gap this design closes.
- ergon/gen1b/PREREG_GEN1_2026-09-01.txt — frozen arm definitions, effective-use definition, estimand narrowing, uninterpretability conditions; reused verbatim where applicable.
- ergon/gen1b/gen1_primary_results.json — per-lineage rows; source of the empirical paired-delta SD (0.0322) used for power planning.
- ergon/gen1b/gen1_run.py — the frozen runner this design extends (blob 577125847aabf6a3087d06935e39701cffc751be at Gen-1 freeze).
- ergon/gen1a/power_analysis_2026-09-01.json + ergon/gen1a/REVIEW_PACKET_GEN1A_2026-09-01.txt — variance decomposition (lineage share 1.85%, task share 31%), the lineage-as-unit ruling, and the MDE methodology this design inherits.
- ergon/gen1b/phase1_mutational_redundancy.json / .py — why I1's definition requires mutational (not merely behavioural) redundancy: only 23% of behavioural duplicate pairs reach sketch-Jaccard 0.50.
- ergon/gen1b/phase7_halflife.json — hazard structure (threshold-then-plateau, no decay); grounds for NOT introducing a dormancy-based arm in the control proposal.
- ergon/gen1/REVIEW_PACKET_GEN1_PRECONDITION_A_2026-09-01.txt and ergon/gen1/ERGON_GEN1_PERSISTENCE_SPEC.txt — persistence instrument and freeze audit for the D-5 line.
- ergon/gen0/REVIEW_PACKET_GEN0_2026-08-31.txt — seat charter and consumer-fit constraints (memory-metabolism seat; admission = executable + exact-execution).
- agent_d5_blind/ (MANIFEST.md, VERDICT.md, developmental_history/final_libraries/) — the frozen substrate, imported read-only; also the site of the corrected Gen-0/1A scope error about persisted libraries, which motivates this design's explicit enumeration of what is logged and committed.
- Doctrine directly load-bearing here: replicate-seeds (fresh disjoint seed batch), gate-must-exceed-measurement-error (MDE 2.8× design SE, CI beside verdict), verdict-without-rows (rows in the verdict commit), control-must-break-the-selection-relation (I3 as churn-preserving control), committed-SHA-can-be-orphaned (push then verify ancestry), preflight (replay bit-identity gate).
