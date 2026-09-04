# PROPOSAL V2-T07 (arm)

## Hypothesis
The locally-mirrored derived quantities for elliptic curves (regulator `Reg`, real period `Ω`, Tamagawa product `∏c_p`, analytic Sha `sha_an`, and the L-function leading special value) satisfy the strong BSD identity

    L*(E,1) = (Ω · Reg(E) · ∏c_p · Sha_an) / |E(Q)_tors|^2

to within the mirror's stated numerical precision, **only** on the subset of curves where `sha_an` is independently corroborated (e.g. rank 0/1, descent-verified). A naive whole-table audit of this identity will report a near-universal "pass," but that pass is largely **tautological** on the rank ≥ 2 stratum, because `sha_an` is itself back-solved from this same identity there (per wiki claim [REF]). The audit therefore has real discriminative power only on the non-circular stratum, and must report the two strata separately.

## Motivating evidence
- Existing full-table result: analytic vs algebraic rank agree with zero mismatches across 3,824,372 curves and analytic Sha is always a perfect square ([REF], [REF]) — establishes the mirror is large, already load-bearing, and superficially "clean."
- [REF] ([retrieval system], OBSERVED, QUALIFIES [REF]): "F005 cannot be used to verify BSD at rank ≥ 2 because Sha values on that stratum are themselves computed assuming BSD." This is the direct precedent for the circularity this design targets.
- [REF] (Harmonia): F043's BSD-Sha anticorrelation was RETRACTED as a tautological algebraic-identity rearrangement — a documented instance of exactly the failure mode this audit must not repeat.
- Repo: `prometheus_math/bsd_rich_features.py` confirms the mirror stores per-curve `regulator`, `real_period`, `sha_an`, `tamagawa_product`, and a leading L-value/log_L1 field — i.e., all ingredients of the identity already exist as first-class fields, so the audit is a direct recomputation, not a new derivation.

## Prospective predictions
1. On rank-0/1 curves with independently-verified Sha, the identity holds (log-relative error < 1e-4) for >99.9% of rows.
2. On rank ≥2 curves, the identity holds ~100% of the time by construction, regardless of whether other stored fields (regulator, Tamagawa product) are perturbed — i.e., it fails to independently constrain anything there.
3. Injecting a random multiplicative perturbation (factor drawn log-uniform in [0.5, 2]) into `regulator` or `tamagawa_product` will be detected (flagged as identity failure) on rank 0/1 at >95% but on rank ≥2 at a rate not distinguishable from the mirror's baseline float-noise floor.
4. Re-deriving "every distinct sha_an is a perfect square" independently on this run will replicate [REF]; failure to replicate blocks the rest of the design (pipeline bug, not a new finding).

## Experiment
1. **Smoke test.** Hand-verify the identity on 3 famous, published curves spanning rank 0/1/3 (e.g. 11a1, 37a1, 5077a1) before any batch run, to validate the audit script's own arithmetic.
2. **Replication check.** Re-derive the "sha_an always a perfect square" statistic ([REF]) on the current mirror snapshot. Must replicate before proceeding (see Stopping rule).
3. **Stratify by analytic rank** r ∈ {0, 1, ≥2}. For every row compute `L_pred = (Ω·Reg·∏c_p·sha_an)/|Tors|^2` and compare to the stored special-value field via log-space relative error, never absolute difference (magnitudes range over many orders — see Confound defenses).
4. **Identify the non-circular subset**: curves whose `sha_an` provenance metadata (if present in the mirror) indicates independent computation (descent / 2-descent bound + visibility) rather than back-solved-from-BSD. This subset, not the full table, is the only stratum whose pass rate counts as "verification" rather than "consistency."
5. **Perturbation/injection test**: on a held-out sample per stratum (50k rows × 3 strata), multiply `regulator` or `tamagawa_product` by a random non-1 factor, recompute the identity check, and measure detection rate per stratum. This is the design's core discriminator between "audit has teeth" and "audit is definitionally satisfied."
6. **Scale-up**: only after 1-5 pass on a stratified sample with stable estimates, run the full ~3.8M-row mirror.

## Controls
- **Positive control**: hand-verified famous curves (step 1) — validates the arithmetic itself, independent of scale.
- **Negative control (perturbation)**: as in step 5 — corrupted inputs must be caught on rank 0/1; the (expected) failure to catch them on rank ≥2 is itself the key measured output, not noise to be explained away.
- **Null model**: within each rank stratum, shuffle `regulator` values across curves (breaking true curve↔quantity correspondence while preserving the marginal distribution), then **recompute** `sha_an` from the shuffled inputs via the identity (not compare against the stale stored value) and re-check squareness/self-consistency. This tests whether the "identity holds" and "sha_an is square" results are structural (an algebraic tautology, expected to survive shuffling on rank ≥2) versus genuinely curve-specific (expected to break under shuffling on rank 0/1).

## Confound defenses
- **Circularity** ([REF]): hard split by rank; rank ≥2 results are reported only as "internal table consistency," never as "BSD verification."
- **Algebraic tautology** (F043 precedent, [REF]): before interpreting any pass/fail rate, write a short derivation memo showing the check is not a rearrangement of an identity used to *define* one of the compared fields (this is exactly what killed F043).
- **Scale/magnitude mismatch** (theseus corpus precedent, [REF], where an abs-diff test between a single-digit invariant and a four-digit conductor was structurally vacuous): use log-space ratio/relative-error tests exclusively; never absolute-difference thresholds across heterogeneous-magnitude fields.
- **Precision/rounding artifacts**: pull per-row precision/error-bound metadata if the mirror carries it; if absent, any "failure" below the table's documented significant-digit count is logged UNRESOLVED, not FAIL.
- **Selection bias in the "independent Sha" subset**: if that subset is small or skewed to tiny conductors, report the power limitation explicitly and do not extrapolate its pass rate to the full table.

## Preregistered falsifiers (numeric thresholds)
- F1: REJECT "stored quantities satisfy BSD" if log-relative error > 1e-4 on more than 0.1% of rank-0/1 rows in the independently-verified-Sha subset.
- F2: REJECT the circularity hypothesis (i.e., treat rank ≥2 as partially non-circular) if perturbation-injection detection rate on rank ≥2 is NOT ≤5% (a genuine positive/surprise result if triggered).
- F3: kill/redesign the audit as underpowered if perturbation-injection detection rate on rank 0/1 is NOT ≥95%.
- F4: HALT before scaling if independent re-derivation of "every distinct sha_an is a perfect square" ([REF]) produces any counterexample beyond float rounding at 1e-6 — indicates a pipeline bug or that the prior claim does not hold on this snapshot.

## Stopping rule
Run smoke test + F4 replication first; halt on failure. Then run on a stratified sample (50k rows/stratum) with CI half-width < 10% of the point estimate required before scaling to the full ~3.8M-row mirror. Halt entirely and report NOT_ESTABLISHED (rather than substitute a proxy) if the mirror lacks any metadata distinguishing independently-verified from back-solved `sha_an` — that gap is a blocking precondition, not something to route around silently.

## Expected failure modes
- Mirror lacks Sha-provenance metadata → design collapses to the already-known rank-based split only, with no finer non-circular subset (still useful, strictly less informative than planned).
- Float/stored-precision noise dominates at high conductor, producing false failures without log-relative-error framing.
- Some rank ≥2 curves may have independently-computed Sha via other methods (Kolyvagin systems, visibility) for small-conductor special cases, producing a mixed (not clean binary) circularity signal — the design must report this as a gradient, not force a single verdict.
- The "independent Sha" subset may be too small for the CI-width stopping criterion to ever clear, stalling the design at the sampling stage.

## Compute estimate
Per-row identity evaluation is O(1) floating-point arithmetic. Full mirror pass (~3.8M rows) is single-core, single-machine, well under 1 hour, dominated by table I/O rather than compute. Perturbation sub-experiment (150k rows total) is under 10 minutes. No GPU, no training. Total wall-clock budget including smoke test and staged sampling: under 2 hours.

## Prior evidence that materially changed this design (or 'none found')
- [REF] forced the rank-stratified design and the requirement for a non-circular ("independently-verified Sha") subset, instead of a single flat whole-table pass/fail statistic.
- [REF] (F043 retraction) added the explicit pre-analysis "is this a rearranged identity" derivation-memo defense as a mandatory step before interpreting results.
- [REF] forced log-relative-error/ratio metrics instead of absolute-difference thresholds, given the heterogeneous magnitudes of regulator/period/special-value fields.
- [REF] and [REF] were used as the smoke-test replication target (F4) and as prior evidence the mirror/scale is already usable for this class of audit.
- [REF] (Szpiro-vs-conductor, PARTIAL — some slope algebraically expected) reinforced the general posture of separating algebraically-forced patterns from genuinely informative ones before issuing a verdict.

## Unresolved uncertainty
- Whether the mirror actually carries per-curve provenance distinguishing independently-computed Sha from back-solved Sha (not checked in this spec pass; schema must be inspected at execution time).
- Whether any rank ≥2 curves have independently-computed Sha, which would make the circularity partial rather than total.
- Whether per-row precision/error-bound metadata exists in the mirror.
- Whether the mirror's "special value" field is the raw L-function leading coefficient or an already-normalized ratio — needs a schema check before step 3 of Experiment.

