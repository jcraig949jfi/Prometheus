# Pre-registration — h2 information-recovery law experiment

**Author:** Harmonia_M2_C
**Date:** 2026-06-10 (registered BEFORE the analysis harness was run)
**Governs:** `D:\Prometheus\harmonia\experiments\h2_backfill_and_validate.py`,
`D:\Prometheus\harmonia\experiments\h2_info_recovery_law.py`
**Proposal:** `D:\Prometheus\harmonia\proposals\2026-06-09\E_h2_opaque_kill_backfill.md`

---

## 0. Ground-truth facts established before registration (Round 0)

- **Corpus absence:** `theseus/corpus/` is empty on this host; daemon paused since
  2026-05-29 (BATCH_LOG: "Fire #234 … LOOP PAUSED"). The 87K historical h2 kills are
  not locally available. Production-emission scan over the live corpus is therefore
  N/A on this host and reported as such; emission behavior is instead verified by
  driving the production generator class directly.
- **Backfill feasibility by schema archaeology:** the pre-refactor h2
  (`git show 487b611f~1`) emitted the *identical* `claim_payload`
  (`knot_invariant`, `ec_invariant`, `method_verdicts`, `method_counts`,
  `method_r2s`, …) and full per-method `step_trace`. The structured label is a
  deterministic function of the retained payload → backfill is a pure local rewrite
  wherever the corpus bytes exist. The information was withheld by the *label*, never
  destroyed in the *record*.
- **Witness space:** 6 knot invariants × 4 EC invariants = 24 (ki, ei) pairs.
  `nf_class_number` present in only 8/52 knots (degenerate x-support for those pairs).
- **Thresholds:** REJECTED iff R² < 0.3 (a4); E[R²] under independent sampling
  ≈ d/(n−1) ≤ 0.053 for all three h2 method variants.

## 1. The structural theorem (stated before measurement)

h2 evaluates independently-resampled catalog draws. **Conditional on the pair
(ki, ei), the three method verdicts and any future evaluation are independent.**
Therefore, for any label component T derived from the evaluation path
(method_tag, agreement_class):

    I(T ; Y_fresh | pair) = 0   — exactly, by construction,

where Y_fresh is the outcome of any fresh evaluation of the same pair. Path-derived
label components can carry information about fresh outcomes only *through* the pair
(data-processing inequality: I(T; Y) ≤ I(pair; Y)).

**Scope condition:** this holds only when evaluations are independent given the
claim coordinates. Generators whose evaluation consumes accumulated corpus state
(e.g., kill-neighborhood generators) may violate the premise; the cross-generator
audit probes this boundary.

The MC experiment does not test the theorem (it is analytic); it measures the
empirical quantities the theorem cannot fix:

## 2. Pre-registered quantities and binding decision rules

All MC at R = 2000 draws per (pair × method) for ground truth; emission simulation
via the production `H2TriangulationProtocolGenerator.next()` with injected parents
(N ≥ 20,000 kills); seeds fixed at 20260610, 20260611, 20260612 (3 replicates;
do not redraw).

**Q1 — Concentration of the structured scheme (cosmetic check).**
Under both pair mixes (uniform over 24; a4-INCONCLUSIVE-weighted):
- top-1 share and Shannon entropy of: full label; tag component; agreement
  component; pair component.
- **COSMETIC on the tag axis** ⟺ top-1 tag share ≥ 0.90 (echoes the old 100%
  concentration). **Differentiated** ⟺ top-1 tag share ≤ 0.75. Else AMBIGUOUS.

**Q2 — Information decomposition (the heart).** With Y_fresh = verdict triple of a
fresh (M1, M2, M3) evaluation of the same pair (independent seeds):
- I(pair; Y_fresh), I(tag; Y_fresh), I(tag; Y_fresh | pair), each with a
  permutation-null 95% bound (200 shuffles).
- **Coordinates carry signal** ⟺ I(pair; Y_fresh) exceeds the permutation-null
  95th percentile AND ≥ 0.05 bits.
- **Tag is conditionally empty** (theorem confirmed empirically) ⟺
  I(tag; Y_fresh | pair) within permutation-null 95% bound.
- **Volume-vs-information verdict:** if I(pair; Y_fresh) < 0.05 bits, h2's kills
  are irreducibly low-information *regardless of labeling* → "44% of volume,
  ~0% of information" is CONFIRMED quantitatively.

**Q3 — Tag stability (echo vs noise).** Per pair: H(tag | pair) and
P(tag₁ = tag₂ | pair) for two independent emissions.
- **Echo** (tag ≈ deterministic coordinate relabel) ⟺ median per-pair
  P(match) ≥ 0.9. **Noise** ⟺ median ≤ the global-marginal collision rate + 0.05.
  Else mixed.

**Q4 — Frozen gate.** `baseline_costume.costume_check` with claim =
{record → tag}, key_fn = pair, label_fn = tag, on the emission-simulated kills.
Pre-registered read: COSTUME_OF:marginal_majority or COSTUME_OF:volume_weighted
⇒ the tag refinement is a costume per the frozen gate; DISTINCT ⇒ gate and
information analysis disagree → investigate before any claim.

**Q5 — Backfill validation.** The backfill function (payload → structured label)
must reproduce the production-emitted `kill_pattern` byte-for-byte on ≥ 5,000
freshly emitted kills (production code as oracle). Anything < 100% match =
backfill NOT proven; report the mismatch shapes.

**Law formulation rule.** The law is asserted only if: theorem-consistent
empirics (Q2), cross-generator audit produces ≥ 3 generators whose label schemes
sort cleanly under the coordinate/path decomposition, and no counterexample
(path-derived component with conditional info above null on an
independence-holding generator). A counterexample kills the law's core, and the
violation mechanism becomes the finding (failure-signature doctrine: report the
shape either way).

**Stopping rule (iterate-or-kill):** redesign rounds end when two consecutive
rounds add no separable information (all new components fail their Q2-analog),
or when the analytic + empirical picture is decisive. The honest terminal states
are: (a) a better witness encoding that earns signal, (b) proof that h2 kills
are irreducibly lossy at the single-record level with all recoverable
information already carried by the coordinates, or (c) ambiguity with the
failure shapes reported.

## 3. What is NOT claimed in advance

- No claim that the historical corpus rows are recoverable on other hosts (their
  existence elsewhere is unverified here).
- No claim about Learner-side utility beyond information content (utility depends
  on the Learner's loss, which is out of scope).
- The dcl/"instrument echo" interpretation of I(pair; Y) — that it reflects
  catalog-marginal/instrument interaction rather than mathematical structure — is
  an interpretation; the measured bits are the result.
