# Phase 3.K — Permutation null on the PAIR-AWARE robustness claim (ITER-83)

**Date:** 2026-06-03 (Charon adversarial audit, four days after the Phase 3 stress audit)
**Author:** Charon
**Verdict:** **STATISTICALLY UNDERDETERMINED** (pair-aware claim) **+ FALSIFIED** (triplet claim). The architecture's single strongest real-data validation — the Phase 3.E "ROBUST PASS, lift filter is load-bearing" claim (2 deltas vs the pair-aware counter) — does **not** survive a permutation null against its own discriminating baseline (p = 0.105, 7-seed mean 0.102). The triplet claim (ITER-84, §6.5) fails harder: observed below null. After this audit, **no Erebos Layer-2 real-data signal claim survives a permutation null.**
**Harness:** `charon/agents/erebos/sprint1/phase3/pair_aware_permutation_null.py` (+ inline triplet null, §6.5)

---

## §1 — The gap this audit closes

The Phase 3 stress audit (ITER-63/64/66, `PHASE3_STRESS_AUDIT_VERDICT_2026-05-30.md`) ran three independent stress tests on the cross-cell primitive:

- **ITER-63** permutation null
- **ITER-66** scale stress
- **ITER-64** parent-child isolation

All three compared the substrate against `per_plugin_majority` — the **unconditional** counter (the 3-delta number).

But the architecture's strongest real-data validation is a **different** number. Per `PHASE3_EFG_VERDICT_2026-05-30.md` §1 and §6:

> **Phase 3.E (pair-aware counter baseline, ITER-59): ROBUST PASS — 2 deltas vs pair-counter (lift filter is load-bearing).**
> "ITER-59 demonstrated it's robust against the strongest counter baseline."
> "the substrate now has 4 architectural passes on real data (cross-cell, pair-robustness, triplets, BSD infrastructure)."

Per `feedback_counter_baseline_discriminator`, the discriminating question is whether Layer 2 beats **counters**, not whether it beats a *weak* counter. The pair-aware counter IS that discriminating baseline. So the permutation null that actually matters is the one on the **substrate-vs-pair-aware** delta count.

**That number — the load-bearing one — was never null-tested.** Every stress test in the audit targeted the weaker (per-plugin) comparison. This audit runs the missing test.

## §2 — Protocol

`pair_aware_permutation_null.py` mirrors `permutation_null.py` exactly (same `SEED=1789`, `N_PERMUTATIONS=200`, `MIN_COOCCURRENCE=3`, `MIN_LIFT=1.5`, same `_shuffle_signatures`, same `_load_real_rows(include_enriched=True)`). The **only** difference is the baseline: it counts substrate-vs-pair-aware deltas instead of substrate-vs-per-plugin deltas.

Each trial shuffles the `input_signature` column (preserving plugin×kp marginals, breaking per-signature linkage), then recomputes **both** the substrate recommendations and the pair-aware counter recommendations on the shuffled data and counts deltas. This is the correct null for "do the two methods diverge more on real data than on noise" — the substrate-vs-pair delta is a comparison of two methods (lift-max vs count-max), so under the null both methods must see broken linkage.

## §3 — Results

```
observed deltas vs PAIR-AWARE counter     = 2
observed deltas vs per-plugin counter     = 3   (cross-check vs ITER-63)

null mean (200 trials)                    = 0.48
null std                                  = 0.82
null max                                  = 4
null p95                                  = 2      <-- observed == p95
n_null >= observed                        = 21 / 200
empirical p-value                         = 0.1050
z-score                                   = 1.85
VERDICT                                   = STATISTICALLY_UNDERDETERMINED
```

### Seed robustness (per `feedback_replicate_seeds`)

300 trials × 7 permutation seeds:

```
seed    p_value   null_mean
1789    0.0900    0.450
1       0.1100    0.493
7       0.1000    0.423
42      0.1067    0.463
101     0.0933    0.470
2026    0.0967    0.453
31337   0.1167    0.517
-------------------------------
mean p  0.1019    all seeds >= 0.05
```

The result is stable: p ∈ [0.090, 0.117]. Not a seed artifact.

## §4 — What this means

The 2 substrate-vs-pair-aware deltas are the cases where the lift filter makes the substrate diverge from a pair-aware counter that, for those cells, fell back to the global majority kp (`stygian_hecate_meta_test_not_yet_implemented`). The Phase 3.E claim is that this divergence reflects real cross-cell structure the lift filter captures.

The permutation null says: **under shuffled signatures (no real cross-cell structure), lift-max and count-max already disagree on ~0.5 cells on average, and reach 2 disagreements in ~10% of trials.** The observed 2 sits exactly at the null's 95th percentile. The lift filter's divergence from the pair-aware counter is **not distinguishable from chance lift-vs-count disagreement** at conventional significance.

In plain terms: lift-max and count-max are simply *different functions*. They disagree on noise. The observed 2-delta disagreement on real data is within the range that disagreement produces on noise.

### Cross-check: the per-plugin claim has also decayed

Re-running the original `permutation_null.py` on the current ledger (699 rows, grown from the 674 in the original verdict via daemon ticks):

```
observed = 3, null mean = 0.69, null p95 = 3, p-value = 0.0750
VERDICT (harness's own logic) = STATISTICALLY_UNDERDETERMINED
```

The original verdict reported p=0.055 ("BORDERLINE"). On the current larger ledger it is **p=0.075** — it has crossed from borderline to failing the harness's own pre-committed p<0.05 threshold. This is consistent with the ITER-66 scale-stress finding (the signal grows slower than the noise): as the ledger grows, the per-plugin signal weakens.

## §5 — Honest residual (per `residual_signal`)

This is **not** a zero-signal result. Observed (2) sits at the null p95, not deep inside the bulk. ~10% of permutations fail to reach it. The structural observation behind Phase 3.E remains true: a per-plugin counter genuinely *cannot* express conditional recommendations, and lift-normalization genuinely *is* a different operation from raw co-occurrence counting. What collapses is the **statistical** claim that the 2-delta divergence on real data is above chance — not the structural claim that the operations differ.

The residual: the signal is real-but-borderline-underdetermined, the same class the stress audit assigned to the per-plugin number. The honest state is "underdetermined," not "falsified."

## §6 — Doctrinal reframe required

`PHASE3_EFG_VERDICT` §6 claims "4 architectural passes on real data (cross-cell, pair-robustness, triplets, BSD infrastructure)." This audit forces a downgrade of one of those four:

- **cross-cell (3 deltas vs per-plugin):** permutation null p=0.075 on current ledger → STATISTICALLY UNDERDETERMINED (was "borderline p=0.055").
- **pair-robustness (2 deltas vs pair-aware):** permutation null p=0.105 → STATISTICALLY UNDERDETERMINED (this audit). **Was never tested before; the strongest claim rested on a raw count of 2 with no null.**
- **triplets (1 triplet, lift 9.0):** permutation null run as ITER-84 (see §6.5). **FAILS hardest of the three — observed is BELOW the null.** Shuffled signatures produce ~14 triplet motifs on average vs the observed 1; p(n≥observed)=1.00 across all seeds; ~90% of shuffles produce a triplet with lift ≥ the observed 8.54. The real ledger has *less* triplet structure than chance.
- **BSD infrastructure:** an infrastructure pass, not a signal claim; unaffected.

## §6.5 — ITER-84: triplet permutation null (run inline, same audit)

The triplet smoke (`triplet_smoke.py`) PASS criterion is `n_triplet_motifs >= 1` above `min_cooccurrence=2, min_lift=1.5`. Same shuffle-null, 300 trials × 5 seeds:

```
observed n_triplet_motifs = 1, top_lift = 8.54

seed    p(n>=obs)   null_mean_n   p(top_lift>=obs)
1789    1.0000      14.35         0.8900
1       1.0000      13.46         0.9000
7       1.0000      14.46         0.9233
42      1.0000      15.36         0.9067
101     1.0000      13.98         0.8867
```

**The observed count (1) is below the null mean (~14).** Under shuffled signatures the data produces *more* triplet motifs than the real ledger, and ~90% of shuffles produce one with lift ≥ 8.54. This is lift inflation from low expected counts — the exact failure mode `permutation_null.py`'s own docstring named (lines 14-16): "If null permutations produce comparable numbers of deltas, the primitive's 'signal' was lift inflation from low expected counts, not real cross-cell structure."

Why the observed is *below* null: in real data the relevant cells co-occur in a few concentrated batch signatures, so distinct triplet combinations are limited. Shuffling spreads cells across many signatures, manufacturing many low-expected-count triplets whose lift inflates. The PASS criterion (≥1 motif) is therefore non-discriminating: noise satisfies it ~14× over. The single real triplet is not evidence of above-chance higher-order structure.

**Verdict: the triplet "PASS" (Phase 3.F / ITER-60) is FALSIFIED, not merely underdetermined.** It is the cleanest of the three failures.

The honest net after this audit:

> On the current real ledger, Erebos Layer 2's value claim — that it produces decision-relevant signal counters cannot — is **statistically underdetermined against the discriminating (pair-aware) baseline**, and **underdetermined against even the unconditional baseline** after ledger growth. The structural distinction (joint vs marginal, lift-normalized vs raw) is real; the claim that it produces *above-chance* decision deltas on real data is not currently supported.

This puts **Possibility C** from the stress audit (the doctrine's main claim may be wrong) ahead of **Possibility A/B**. With all three signal-claim passes now non-significant under permutation nulls — two underdetermined, one falsified — there is currently **no real-data signal claim for Erebos Layer 2 that survives a permutation null.** The residual (§5) and the untested lateral-data hypothesis (ITER-65) leave a path to recovery, but the affirmative evidence for the doctrine's main claim is, as of this audit, absent.

## §7 — What proceeds

Per `feedback_take_a_stand`:

1. **Triplet permutation null (ITER-84): DONE (see §6.5).** Result: FALSIFIED — observed below null. All three signal-claim passes (cross-cell, pair-robustness, triplet) are now non-significant. The architecture is squarely in Possibility-C-credible territory.
2. **Re-run `PHASE3_EFG_VERDICT` and `STATE_AND_NEXT_STEPS` framing.** Both still carry "4 architectural passes / robust against the strongest counter baseline" language that this audit contradicts. Update for honesty per `feedback_instrument_vs_architectural_pass`. The honest count is now: **0 signal-claim passes survive a null; 1 infrastructure pass (BSD) stands.**
3. **Build the null INTO every counter-baseline harness going forward.** The structural lesson: a "PASS vs baseline X" claim is not substrate-grade until it carries a permutation null vs baseline X. Phase 3.E shipped a raw count without one; Phase 3.F shipped a `≥1 motif` criterion that noise satisfies ~14× over; the stress audit added a null but only for the weaker baseline. All three are the same class of error — measuring against the convenient comparison, not testing the load-bearing one against chance. **Candidate discipline primitive:** a smoke harness that asserts `>=1 delta/motif vs baseline` must, by construction, also emit the permutation-null p-value for that same statistic, or refuse to render a PASS verdict.
4. **The signal-grows-slower-than-noise pattern (ITER-66) is now confirmed three ways** (per-plugin p 0.055→0.075 as the ledger grew; pair-aware p=0.105; triplet observed-below-null). This is the strongest single diagnostic. Lateral/organic data (ITER-65) is the only path that could reverse it; if more data keeps weakening the signal, the stand should flip to **Possibility C — pause and reopen the doctrine.**

## §8 — Doctrinal posture

Per `feedback_failure_metabolization_doctrine`: *optimization consumes failure; Prometheus metabolizes failure.* This audit is the doctrine eating its own strongest claim. The substrate built a careful robustness test (Phase 3.E) and then never pointed the null at it — exactly the "careful instrument not yet pointed at anything" failure mode Q7 of `STATE_AND_NEXT_STEPS` named. The metabolization is: the load-bearing number now has a null, and the null downgrades it.

Per `feedback_counter_baseline_discriminator`: the cargo-cult detector fired correctly again. ITER-59's "ROBUST PASS against the strongest baseline" was the right *kind* of test — but the verdict reported a raw count where it needed a null. Beating a baseline by 2 raw deltas is not the same as beating it significantly.

Per `feedback_architectural_claim_narrows_under_adversarial`: the architectural claim has narrowed once more. After the stress audit it was "narrow hierarchical-prediction capability with real-but-borderline signal." After this audit it is "a structural distinction (joint vs marginal) whose real-data decision advantage is statistically underdetermined against discriminating baselines." The claim keeps narrowing under each successive adversarial pass — itself a signal worth heeding.

Per `feedback_calibration`: stay calibrated. This is a downgrade of one claim, with a documented residual, not a wholesale falsification. The triplet null (ITER-84) and the lateral-data test (ITER-65) are the two remaining moves that could move the architecture back toward Possibility A — or push it into Possibility C.

---

**End Phase 3.K verdict. ITER-83 + ITER-84 close. The architecture's strongest real-data validation is downgraded to STATISTICALLY UNDERDETERMINED; the triplet claim is FALSIFIED. After this audit, no Erebos Layer-2 real-data signal claim survives a permutation null. Next: re-frame PHASE3_EFG + STATE_AND_NEXT_STEPS (item 2); then ITER-65 (lateral/organic data) as the one remaining path to recovery before Possibility C (pause + reopen doctrine) becomes the stand.**
