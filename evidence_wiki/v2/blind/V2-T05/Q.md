# PROPOSAL V2-T05 (arm)

## Hypothesis
A failure signature sigma discovered as a strong within-family kill/doom predictor (concrete instance in this repo: OBSTRUCTION_SHAPE, `{n_steps=5, neg_x=4, pos_x=1, has_diag_neg=True}` on OEIS A149*, 54x lift = 5/5 matched-group unanimous-kill vs 1/54 non-match) generalizes to neighboring/sibling families in the same generative program well enough to serve as a program-wide early-abort trigger ONLY IF the cross-family test controls for (a) base-rate drift between families, (b) discovery-family-specific index/provenance artifacts, and (c) feature degeneracy under structural regime shift. Absent those controls, an apparent cross-family lift is not distinguishable from a within-corpus generalization artifact — and the OEIS case already shows the naive version of this test fails.

## Motivating evidence
- `sigma_kernel/a149_obstruction.py` — the original 54x-lift discovery on the A149* cluster (5 sequences).
- `aporia/scouting/04_obstruction_shape_oeis_a150_a151.md` — a pre-registered scout brief that anticipated exactly this generalization risk (selection bias, regime-degenerate features, A-number/hash-locality bias) before the cross-family test was run.
- [retrieval system] claim `[REF]` — the cross-family test was actually run and REFUTED: after corpus-extension raised battery coverage (A148 38->91, A150 0->142, A151 3->52), A148 has 0 strict matches in 91 covered sequences, A150 has 0 in 142, and A151 has 0 strict matches (1 unanimous-kill in 34 non-matches). The signature survives only as A149*-family-specific; cross-family promotion remains blocked.

## Prospective predictions
If a candidate signature is genuinely program-wide-valid:
- P1: lift on held-out same-generative-block families falls inside a pre-registered retention band of the discovery-family lift (does not collapse to ~1x).
- P2: predictive power does not depend on features that go structurally degenerate outside the discovery family's geometry (survives a regime-crossing ablation).
- P3: a base-rate-matched permutation null shows the signature's lift exceeds the null by a margin larger than any base-rate-driven artifact.

If it is a within-corpus artifact instead: lift collapses toward the global base rate on extension — precisely what was already observed for OBSTRUCTION_SHAPE (0/91, 0/142 strict matches after coverage was raised).

## Experiment
Three-phase protocol, adapted directly from the scout brief's Phase 0-2 and tightened with explicit statistics and a fourth provenance-control phase:

- **Phase 0 (stratify & power).** Enumerate the full generative block the discovery family belongs to; stratify by structurally distinct regimes (e.g., 3D-octant vs 2D-quadrant lattice walks); compute current kill-battery coverage per regime; compute minimum N per regime for target power before scoring anything.
- **Phase 1 (within-block held-out replication).** Run the SAME frozen kill battery (never re-tuned on extension data) on newly-covered same-regime family members not used at discovery. Score against the pre-registered retention band.
- **Phase 2 (regime-crossing stress test).** Project the signature's feature vector onto a structurally different regime within the same program (drop/replace features that go degenerate, e.g., 3D-only diagonal/z-axis flags in a 2D regime). Three mutually exclusive, pre-registered outcomes: fires with similar lift (genuine geometric signal); fires only in the discovery regime (regime-specific artifact); fails to fire in either (original result was selection bias).
- **Phase 3 (provenance/hash-locality control).** Test on families with matched surface schema but a genuinely different generative provenance (different author/submission batch, not merely an adjacent family ID), to rule out index-neighborhood memorization being mistaken for structural generalization.

## Controls
- Base-rate-matched null: resample non-match rows to the GLOBAL kill base rate observed after coverage extension, not the (possibly unrepresentative) discovery-family base rate.
- Frozen predicate: signature and threshold frozen before Phase 1 begins — no re-fitting on extension data. This is what makes "0 strict matches in 91/142" a legitimate falsification rather than a moving target.
- Regime-degenerate feature ablation: explicit stratified test zeroing out features that are structurally undefined outside the discovery regime, to separate genuine geometric signal from a discovery-regime artifact.
- Provenance/hash-locality control: same-schema families from a different author/submission batch, to separate a structural predicate from index-neighborhood memorization.

## Confound defenses
- Battery-coverage selection bias: the original 54x figure was fit on a battery-scored slice (100/1,534 rows, overwhelmingly A148/A149) — require near-complete battery coverage on every held-out family before scoring lift, never a small biased slice.
- Step-count / feature-count confound: if the signature partially encodes a scalar (e.g., step-count) that varies systematically by regime, stratify explicitly on that scalar before scoring.
- A-number/index-locality confound: adjacent family IDs from the same submission batch are NOT independent cross-family evidence (confirmed in the scout brief: A148-A151 are one contiguous 2008 Kauers submission block) — any extension within that block is a within-corpus generalization test, not a cross-domain one; only Phase 3's different-batch family counts toward a genuine cross-family claim.
- Small-N false lift: any lift computed on a matched-group of <30 instances (the original A149* match-group was n=5) is reported as provisional only, never as the promotion-grade number.

## Preregistered falsifiers (numeric thresholds)
- F1: held-out same-regime lift outside [0.75x, 1.25x] of the discovery-family lift => retained only as regime-specific, not promoted (band taken verbatim from the scout brief's own preregistered success criterion).
- F2: strict-match count in held-out extension = 0 at N>=90 covered instances => signature FALSIFIED for that family (matches the already-observed A148: 0/91, A150: 0/142 result) — do not promote program-wide.
- F3: regime-crossing test — if the degenerate-feature-ablated predicate's lift in the new regime is statistically indistinguishable from the global base rate (two-proportion z-test, alpha=0.05) => predicate is discovery-regime-specific; blocks early-abort deployment outside that regime.
- F4: program-wide promotion requires retention (per F1) in >=2 independent regimes AND a pass on >=1 different-provenance family (Phase 3); failing this bar caps status at "family-specific," matching the claim_ceiling already recorded for OBSTRUCTION_SHAPE.
- F5: program-wide deployment additionally requires false-abort rate (killing a run the frozen ground-truth battery would NOT have killed) < 5% on held-out non-match instances — an early-abort trigger with a high false-positive rate risks operator disengagement (feedback_program_dies_of_frustration_not_silence.md), which is a worse failure mode than no trigger at all.

## Stopping rule
Stop and report FALSIFIED-CROSS-FAMILY the moment F2 or F3 triggers on the first fully-covered held-out family — no further families need be tested once the strict-match count is 0 at N>=90 (this is exactly what already happened for A148/A150; the kill is the highest-value output, per feedback_assume_wrong.md). Otherwise proceed through all four phases; only report PASSED-REGIME-SPECIFIC or PASSED-PROGRAM-WIDE after the complete falsifier set (F1-F5) has been evaluated — never promote off Phase 1 alone.

## Expected failure modes
- Selection-bias artifact: lift computed on a small, non-representative battery-scored slice (the documented root-cause candidate for the original 54x figure).
- Discovery-regime feature degeneracy silently inflating in-regime lift while being undefined out-of-regime.
- A-number/index-locality memorization mistaken for structural generalization.
- Re-fitting the predicate on extension data (leakage) making a real falsification look like a pass.
- Under-powered held-out family (N too small) producing a spurious pass or spurious kill.

## Compute estimate
The kill battery (F1_permutation_null, F6_base_rate, F9_simpler_explanation, F11_cross_validation) is CPU-only with no LLM calls; the historical corpus (1,534 rows) was scored at script-level, sub-day cost on a single machine. Full protocol (Phases 0-3) requires scoring on the order of 1,000-1,500 additional held-out rows (the ~833 unscored A150*/A151* rows plus a comparable different-provenance control set) at the same per-row cost. Estimate: single-machine, sub-day compute budget, no new infrastructure, no GPU.

## Prior evidence that materially changed this design (or 'none found')
`[REF]` (REFUTED: OBSTRUCTION_SHAPE falsified cross-family, survives only as A149*-specific) and its source `aporia/scouting/04_obstruction_shape_oeis_a150_a151.md` materially changed this design in three concrete ways: (1) supplied the exact numeric retention band F1 uses ([0.75x, 1.25x] = +/-25%), taken verbatim from the brief's own preregistered success criterion; (2) surfaced the A-number/hash-locality confound, now Confound Defense #3 and Phase 3 of the Experiment; (3) surfaced regime-degenerate features (3D-only diagonal/z-axis flags going structurally undefined in a 2D regime) as the specific mechanism by which a discovery-regime artifact masquerades as universal signal, now F3 and the regime-crossing phase. Without this evidence the design would have proposed the naive test that was already tried and already failed to establish independence — treating adjacent family IDs as independent cross-family evidence when they are the same submission batch.

## Unresolved uncertainty
- Whether the F5 false-abort threshold (<5%) is the right operating point for this program's actual cost-of-false-kill vs cost-of-wasted-compute tradeoff; no prior calibration study for that ratio was found in the consulted evidence.
- Whether a genuinely different-provenance, same-schema family exists at adequate N for Phase 3 — the scout brief flags the 79-orbit Bousquet-Melou quadrant census as the candidate set but explicitly notes it "needs a real lookup pass" and is not yet confirmed available.
- Whether the already-recorded REFUTED status for OBSTRUCTION_SHAPE itself should be read as terminal, or whether this tightened protocol could still recover a narrower, real regime-specific trigger (Phase 2's middle outcome) if applied to a fresh candidate signature; this SPEC does not resolve that, it only ensures the next attempt does not repeat the same falsified inference path.

