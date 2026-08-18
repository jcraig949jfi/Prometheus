# Deep Research Report #196: Bianchi L-function Zero Spectrum at h(K) > 1

**Target Agent:** Harmonia
**Date:** 2026-04-28
**Front:** Batch 10 Tier 1 — L-function regions beyond GL(2)/Q
**Doctrine:** feedback_tensor_first; feedback_domains_are_docstrings; PATTERN_PRIME_GRAVITATIONAL_OVERFIT; PATTERN_CONDUCTOR_CONFOUND; PATTERN_BASE_RATE_NEGLECT

## 1. Problem Statement

Bianchi modular forms are GL(2) automorphic forms over imaginary quadratic K = Q(√-d), the cohomological-weight analog of classical modular forms attached to PSL(2, O_K) acting on hyperbolic 3-space. Each cuspidal Bianchi newform f has an L-function L(f, s) with completed functional equation and (conjecturally) Riemann hypothesis. The empirical question for this report: does the F011-class bulk rigidity finding for EC L-functions over Q (gap-k spacing deficit of +46-51% vs GUE at k=24, consistent with Katz-Sarnak universality) extend into the structural region of Bianchi forms over imaginary quadratic K with class number h(K) > 1, or is the universality region GL(2)/Q-bounded?

The h(K) > 1 stratum matters because it is where O_K stops being a PID and the level-structure of Bianchi forms picks up class-group torsion that has no analog over Q. Distinct from Batch 6 #104 (Bianchi base-change to GL(2)/Q(√d), which addresses transfer of forms to a quadratic extension): here we treat Bianchi L-functions as primary objects in their own structural region and ask whether operator behavior — specifically the bulk-zero repulsion shape — survives the change of region.

## 2. Literature

- **Cremona (1981, 1984, ongoing)** — original Bianchi tables for d = 1, 2, 3, 7, 11; Hecke eigenvalues by hand-iterated algorithms then expanded across imaginary quadratic Euclidean fields and beyond.
- **Sengun (2011), Sengun-Williams** — class-number-conscious Bianchi computations into h(K) ≥ 2 territory; cohomology of Bianchi groups and torsion.
- **Cohen-Lenstra (1984)** — heuristics for h(K) distribution over imaginary quadratic K; relevant for choosing the stratification denominators.
- **Voight et al.** — algorithmic frameworks underlying recent expansion of Bianchi tables.
- **F011 (Charon, 2026)** — canonical Katz-Sarnak finding being tested for region transfer: bulk gap-k deficit at k=24 for EC L-functions over Q.

## 3. LMFDB / Corpus Data

- `nf_fields` filtered by `degree = 2 AND signature = '[0,1]'` returns ~2000 imaginary quadratic K (and exposes `class_number`, `disc_abs`).
- LMFDB Bianchi coverage is partial — `bmf_forms` and `bmf_dims` exist but populated mostly for small |disc| and small h(K). Expected gap above h(K) ≈ 5.
- Data hunt is part of the test design: query LMFDB Bianchi tables, then supplement from Cremona's published tables and Voight-affiliated datasets to fill h(K) ≥ 6 strata. Mnemosyne ingest may be required if local Postgres doesn't already mirror the supplemental sources.
- L-function zero data: where present, `lfunc_lfunctions` carries low-lying zeros; otherwise compute via Dokchitser/`lcalc` from Hecke eigenvalues.

## 4. Test Design

**Step 1.** Pull ~50 imaginary quadratic K with h(K) ≥ 2 having at least one Bianchi newform with Hecke eigenvalues at the first 50 prime ideals of O_K (by norm).

**Step 2.** For each form, compute the first ~30 nontrivial L-function zeros above the real axis (or pull pre-computed zeros where LMFDB has them).

**Step 3.** Stratify by class-number bin: h(K) = 2, h(K) ∈ [3, 5], h(K) ∈ [6, 10], h(K) ≥ 11. Per PATTERN_CONDUCTOR_CONFOUND, do not pool across bins.

**Step 4.** Compute gap-k spacing distribution for k ∈ {1, 4, 8, 24} per stratum; compare to GUE matched on local mean spacing per form (scale-vs-shape discipline — normalize before comparing).

**Step 5.** Prime-detrending audit (PATTERN_PRIME_GRAVITATIONAL_OVERFIT): regress out the leading prime-counting contribution to zero density at the relevant height; record pre-detrend and post-detrend deficit magnitudes side-by-side; the headline number is the post-detrend value.

**Step 6.** Base-rate denominators (PATTERN_BASE_RATE_NEGLECT): report total Bianchi forms screened, forms surviving Hecke-eigenvalue completeness gate, forms surviving zero-computation gate, and per-stratum N. Reported effects are conditional on these denominators.

## 5. Falsification

- **F011-class reproduction:** post-detrend gap-24 deficit lands in [+40%, +55%] across strata with overlapping CIs → operator behavior crosses cleanly into Bianchi region; treat as universality calibration anchor.
- **Universality killed:** post-detrend deficit < +15% or sign-flips in any stratum → the F011 shape is a property of the GL(2)/Q region, not of GL(2)-automorphic L-functions generally.
- **h(K)-conditional structure:** monotone deficit-vs-h(K) trend (e.g., deficit erodes as h(K) grows) survives bootstrap and prime-detrend → h(K) is itself an operator-relevant coordinate, becomes a calibration anchor for class-group-conditional L-function behavior.
- **Null sanity:** permutation null over (form, zero) pairing must wipe the deficit; if not, test is uninformative.

## 6. Budget

Harmonia ~8 hours. Data hunt and cleaning ~3h (likely Mnemosyne ingest if LMFDB Bianchi h(K) ≥ 6 coverage is thin). Zero-spacing computation ~2h. Stratified gap-k comparison and prime-detrend audit ~1h. Writeup ~2h. Possible Techne dependency on TOOL_TT_SPLICE (REQ-027 just shipped) for cross-region comparison if signal warrants splicing the Bianchi spectrum against the F011 EC spectrum on shared coordinates.

## 7. Expected Outcome

A quantitative empirical map of Bianchi L-function bulk zero spacings stratified by h(K), with prime-atmosphere detrended and base rates reported. Either outcome is a calibration anchor: a survival result extends the region where F011-class operator behavior is measured and tightens the universality claim; a kill result sharpens the boundary of that region and makes h(K) (or imaginary-quadratic structure more broadly) a candidate operator-relevant coordinate. Either way this densifies labeled-anchor coverage in a previously-thin structural region per `feedback_calibration_anchors_in_depth`, and gives Harmonia a quantitative handle on whether the GL(2) operator behaves the same outside Q.

**Word count: 798**
