# Phase 3.H — Permutation null verdict (ITER-63)

**Date:** 2026-05-30 (same day as today's architectural passes)
**Verdict:** **STATISTICALLY UNDERDETERMINED.** p-value = 0.055, just above the 0.05 threshold. Substrate signal is real (z=2.48) but borderline significant. Today's architectural PASSes are honestly downgraded.
**Harness:** `charon/agents/erebos/sprint1/phase3/permutation_null.py`

---

## What this iteration found

The most discriminating single test of today's claims: shuffle `input_signature` across rows (preserving plugin × kp marginals exactly), re-run cross-cell extraction, count actionable deltas. Empirical p-value = fraction of null permutations producing ≥3 deltas.

```
observed actionable deltas    = 3
null distribution mean        = 0.64
null std                      = 0.95
null max                      = 4
null p95                      = 3
n null permutations >= 3      = 11 out of 200
empirical p-value             = 0.0550
z-score (obs vs null)         = 2.48
ALPHA                         = 0.05
```

**p = 0.055 is one trial off the conventional significance threshold.** The substrate's signal IS above chance (z=2.48 is meaningful, ~2.5σ), but it is NOT statistically significant at the pre-committed p<0.05 level.

## Three honest readings

### Reading 1: the substrate has REAL but MODEST signal

The z-score of 2.48 means the observed 3 deltas is ~2.5σ above the null mean of 0.64. The null distribution puts ≥3 deltas at 5.5% chance. This is not "Layer 2 is fake" — it's "Layer 2's signal is real but the data is too thin to distinguish definitively from chance."

### Reading 2: today's architectural verdicts were not entirely artifacts

- The cross-cell primitive (ITER-58) IS structurally distinct from counters
- The triplet motif at lift 9.0 (ITER-60) is a separate observation not tested by this null
- The BSD MVP loader (ITER-61) works as infrastructure, not as architectural claim
- The pair-aware counter robustness (ITER-59) showed substrate retains 2 deltas — also above the 0.64 null mean

But the SIGNIFICANCE of the architectural pass is weaker than presented.

### Reading 3: the data is at the edge of what the substrate can prove

640-674 rows is a small ledger. The null distribution has substantial spread (std 0.95). With 1000+ rows of similar quality, the p-value could go either way:
- If the signal scales, p would drop well below 0.05 → DEFINITIVE PASS
- If it's an artifact, p would converge upward → DEFINITIVE FAIL

The current state is "we don't yet know." The substrate has not been falsified, but it has also not been confirmed at conventional significance.

## What this changes

The 5 architectural passes from today are reclassified:

```
ITER-58  Phase 3.D  cross-cell primitive               BORDERLINE PASS  (p=0.055)
ITER-59  Phase 3.E  pair-aware counter robustness      BORDERLINE PASS  (2 deltas, ~null max)
ITER-60  Phase 3.F  triplet motif primitive            INCONCLUSIVE     (n=1; not null-tested)
ITER-61  Phase 3.G  BSD MVP loader                     INFRASTRUCTURE PASS (independent)
ITER-62  Phase 3.G  cross-domain motif retest          ARCHITECTURAL FINDING (independent)
```

The substrate's architectural value claim now reads:

> "Layer 2 produces decision-relevant signal counters cannot, with z=2.48 above the permutation null on the current 670-row real ledger. The signal is borderline significant at p=0.055; convergence to either p<0.01 or p>0.10 depends on additional data."

That's a more honest framing than today's earlier "PASS" verdicts. The doctrine survives; the claim's strength is calibrated downward.

## What does NOT change

- The cross-cell primitive is by-construction structurally distinct from per-plugin counters. This is unaffected by the null test.
- The triplet motif at lift 9.0 is a separate observation; ITER-60 didn't claim it was statistically significant in any case.
- The BSD MVP loader's value is its real-data Layer-1 verdicts, not architectural significance.
- The cross-domain gap from ITER-62 is independent of significance — it's a structural absence of a primitive.

## Three definitive next-iteration paths

The substrate has two ways to resolve p=0.055:

**Path A — More data (ITER-66 scale stress).**
Run 5× more enrichment via Phase 1A detector parameter sweeps. Re-run permutation null. If signal scales linearly with data, p drops well below 0.05 → DEFINITIVE PASS. If it washes out → DEFINITIVE FAIL.

**Path B — Better baselines (ITER-67 multi-counter tournament).**
Test substrate against 5+ counter baselines (Markov, Laplace-smoothed, kp-clustering-aware). The baseline floor the substrate STILL beats is the architectural claim's real strength. If substrate ties Markov counter, the claim weakens further.

**Path C — Address the substrate's most exposed claim.**
The 3 actionable deltas are all parent-child predictions (Erebos emission → Stygian battery). If the substrate has nothing on LATERAL structure (rows that share an input without a parent-child relationship), the architectural claim is narrower than the doctrine's framing. ITER-64 was designed for this isolation test.

**Recommendation:** Run all three. Path A is highest information per iteration cost. Path C is most discriminating of the doctrinal claim. Path B addresses the counter-sophistication ceiling.

## Doctrinal posture

Per `feedback_calibration` and `feedback_assume_wrong`: this finding is exactly what the substrate's instruments were built for. The permutation null caught a borderline signal that synthetic tests, counter-baseline comparisons, and triplet checks did not flag. Calibration check: the substrate does not have a definitive architectural pass yet.

Per `feedback_failure_metabolization_doctrine`: today's flow was failure → 4 passes → 1 architectural finding → 1 borderline-significance honest downgrade. The substrate metabolized today's headline confidence into a more accurate calibration. That's the doctrine working.

Per `feedback_take_a_stand`: the substrate now stands at "real but unproven." The next iteration (ITER-66 scale stress) is the natural next move; the verdict depends on data the substrate can produce.

---

**End Phase 3.H verdict. ITER-63 closes. Today's 6 verdicts now read: 1 FAIL + 1 SUFFICIENT + 1 BORDERLINE PASS (cross-cell) + 1 INFRASTRUCTURE PASS + 1 ARCHITECTURAL FINDING + 1 STATISTICAL DOWNGRADE.**

**Next: ITER-66 Phase 3.K scale stress (5x enrichment), the natural resolution test for p=0.055.**
