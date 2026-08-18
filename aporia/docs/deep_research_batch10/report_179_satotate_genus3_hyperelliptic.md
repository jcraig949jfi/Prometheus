# Report 179 — Sato-Tate Refinement for Genus-3 Hyperelliptic Jacobians

**Aporia ID:** 179
**Domain:** Arithmetic geometry / L-functions
**Status:** Open (partial classification, ~2016–2024)
**Substrate posture:** Calibration-anchor hunt in a thin structural region
**Author:** Charon (deep research brief)
**Date:** 2026-04-28

---

## 1. Problem Statement

For an abelian variety A of dimension g over a number field, the Sato-Tate group ST(A) is the conjectural compact Lie subgroup of USp(2g) governing the limiting distribution of normalized Frobenius conjugacy classes. For elliptic curves over Q, Clozel-Harris-Shepherd-Barron-Taylor (2008) proved Sato-Tate, exhausting the three SU(2)-classes (generic, CM, CM-by-Q). Fité-Kedlaya-Rotger-Sutherland (2012) gave the complete refined classification for g = 2: exactly 52 admissible Sato-Tate groups USp(4)-conjugate, 34 occurring over Q.

For **genus 3 hyperelliptic Jacobians** the analogous refined classification is **not finalized**. Lower bounds on the number of admissible USp(6)-conjugate groups exist (Fité-Kedlaya-Sutherland and successors, 2016–2024), but completeness — every group on the list is realized by some genus-3 hyperelliptic Jac/Q, and no others occur — is open. The substrate question: can empirical Frobenius-moment signatures, computed across LMFDB's genus-3 corpus, identify cluster structure consistent with the partial list and surface anchors in under-populated USp(6) cells?

## 2. Literature

- Clozel, Harris, Shepherd-Barron, Taylor (2008) — Sato-Tate proven for non-CM elliptic curves over totally real fields via potential automorphy.
- Fité, Kedlaya, Rotger, Sutherland, *Sato-Tate distributions and Galois endomorphism modules in genus 2* (Compositio 2012) — complete g=2 classification, 52 groups, of which 34 over Q.
- Fité, Kedlaya, Sutherland, *Sato-Tate groups of some weight 3 motives* (2014) — moment-method machinery later reused for higher g.
- Fité, Sutherland, *Sato-Tate distributions of twists of y² = x⁵ − x and y² = x⁶ + 1* (2014) — explicit non-generic g=2 anchor families; methodology lifts to g=3 hyperelliptic with extra automorphisms.
- Fité, Lorenzo García, Sutherland (2018) — Sato-Tate groups of split Jacobians and twists in higher dimension; partial g=3 enumeration.
- Lombardo (2019, 2021) — explicit open-image / endomorphism algebra computations relevant to bounding ST(A) for g ≥ 3.
- Costa, Mascot, Sijsling, Voight — endomorphism rings of genus-3 Jacobians via numerical / certified methods (the engine that closes calibration).
- Sutherland's `smalljac` / LMFDB Sato-Tate data — moment statistics tabulated for many g=2 curves; partial coverage in g=3.

## 3. LMFDB / Corpus Data

- `g3c_curves`: LMFDB genus-3 curves table — both hyperelliptic and non-hyperelliptic (plane quartics). Order ~10⁵; smaller-conductor coverage is dense, large conductor sparse.
- `g3hyp_curves`: hyperelliptic-only slice (Mestre/Shaska invariants keyed). The relevant base rate for this brief.
- Trace data: `lfunc_lpolys` / `lfunc_lhash` keyed L-polynomials L_p(T) of degree ≤ 6 for primes p of good reduction up to a per-curve cutoff (typically p ≤ 2¹³–2¹⁵).
- Endomorphism / Sato-Tate annotations exist for elliptic and many g=2 cases; for g=3 the `st_group` column is **mostly NULL** — exactly the structural region the substrate should be illuminating (cf. *feedback_calibration_anchors_in_depth*).
- Anchor curves: y² = x⁷ + 1 (Aut ⊇ C₇ × C₂, CM-rich), y² = x⁸ + 1 (D₄ symmetry), y² = x⁷ − x (extra involutions), Klein quartic (non-hyperelliptic, useful negative control).

## 4. Test Design

1. **Pull L-polys.** For every curve in `g3hyp_curves` with ≥ 500 good primes tabulated, extract {a_p^(1), a_p^(2), a_p^(3)} from L_p(T) coefficients (power sums → elementary via Newton).
2. **Build signatures.** Compute the first ~30 normalized Frobenius moments M_{i,k} = mean over good p ≤ X of (a_p^(i))^k / p^{(ik)/2} for i ∈ {1,2,3}, k ≤ 10. Stratify X **per curve** to fix the prime window (avoid PATTERN_PRIME_GRAVITATIONAL_OVERFIT by detrending each moment against the prime-counting baseline before clustering).
3. **Conductor-stratified clustering.** Bucket curves by log-conductor decile (PATTERN_CONDUCTOR_CONFOUND: do **not** pool across conductors). Within each bucket, run UMAP + HDBSCAN on the 30-d signature.
4. **Calibrate against anchors.** For each known-ST anchor (y² = x⁷+1, x⁸+1, x⁷−x, generic Lombardo example), compute its signature and check it lands inside its theoretically-predicted cluster centroid (USp(6), U(3), SU(2)×SU(2)×SU(2)/twist, etc.).
5. **Permutation null.** Repeat clustering on (curve_id ↔ signature) shuffles within each conductor bucket; require empirical silhouette / ARI to exceed the 99th-percentile null. Report effect size, not just p-value.

## 5. Falsification

- **Calibration pass:** ≥ 4/5 anchor curves land in their expected cluster (centroid distance below 95th percentile of within-cluster distances). Signature is then provisionally validated.
- **Calibration fail:** < 3/5 anchors hit. Conclusion: the 30-moment signature is too coarse for USp(6) refinement — refine (add joint moments, twist-distinguishing invariants) **before** any structural claim. Either outcome is publishable as a methodological calibration result; null is not failure (cf. *feedback_assume_wrong*).
- **PATTERN_BASE_RATE_NEGLECT:** report cluster sizes as fractions of the 'curves with ≥ 500 good primes' base, not of LMFDB total.
- **PATTERN_CONDUCTOR_CONFOUND:** any cluster crossing > 2 conductor deciles is flagged and re-tested within-decile.
- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT:** detrend each M_{i,k} against the all-curves prime-window mean for that (i,k,X) before clustering.

## 6. Budget

- Charon, ~8 hours single session.
- Hour 0–1: pull `g3hyp_curves` + `lfunc_lpolys` slice from local LMFDB Postgres mirror (cf. *reference_lmfdb_postgres*); cache as parquet.
- Hour 1–3: signature computation (vectorised numpy over Newton's identities).
- Hour 3–5: conductor stratification + clustering + permutation null (≥ 200 shuffles).
- Hour 5–7: anchor calibration + cluster-population reporting.
- Hour 7–8: writeup, deposit signatures into the unified tensor as a new node-set keyed by curve LMFDB label (cf. *feedback_tensor_first*); discipline tag is a docstring on the node, not a coordinate (cf. *feedback_domains_are_docstrings*).

## 7. Expected Outcome

Best case: signature separates ≥ 3 ST-classes within at least one conductor decile, with anchors landing correctly. This produces calibration anchors per Sato-Tate group in a previously sparsely-annotated structural region of g=3 curve space — exactly the kind of high-dimensional under-explored substrate territory the doctrine flags as priority. Output is **not** a claimed completion of the FKRS-style classification; it is a calibrated empirical map that downstream specialist work (endomorphism certification a la Costa-Mascot-Sijsling-Voight) can validate cluster-by-cluster.

Worst case: signature is too coarse, anchors smear. This refines the moment-set requirements (likely add Frobenius **joint** moments across small prime pairs and twist-class indicators) and is itself a substrate-level finding about what dimension of statistic genus-3 ST-refinement actually demands. Either way, the run produces durable artifacts in the tensor and tightens the open-question framing.

Word count ≈ 760
