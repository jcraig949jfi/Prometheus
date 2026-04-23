---
catalog_name: Knot–Number-Field silence as lens mismatch (Alexander vs A-polynomial)
problem_id: knot-nf-lens-mismatch
version: 1
version_timestamp: 2026-04-21T05:40:00Z
status: alpha
cnd_frame_status: y_identity_dispute
teeth_test_verdict: FAIL_via_Y_IDENTITY_DISPUTE
teeth_test_sub_flavor: lens_swap_remediable (Lens 2 identifies correct Y; remediation = run that lens)
teeth_test_resolved: 2026-04-23
teeth_test_resolver: Harmonia_M2_sessionC
teeth_test_cross_resolver: Harmonia_M2_sessionA
teeth_test_third_reader: Harmonia_M2_sessionB
shadows_on_wall_tier: coordinate_invariant
teeth_test_doc: agora:harmonia_sync 1776907566863-0 (sessionC FORWARD_PATH_APPLICATION + Y_IDENTITY_DISPUTE first-anchor filing) + 1776907933474-0 (sessionA cross-resolve ENDORSE + sub_flavor lens_swap_remediable) + 1776909320024-0 (sessionB third-reader ENDORSE)
teeth_test_note: First concrete anchor for proposed v1.1 enum extension FAIL_via_Y_IDENTITY_DISPUTE. Lens 2 (A-polynomial Mahler) actively denies Lens 1 (Alexander Mahler) Y-legitimacy: 'wrong polynomial.' 26 Chinburg verifications confirm Lens 2's Y bridges to NF; Lens 1's Y demonstrably does not. Distinct from CND_FRAME (lenses don't deny each other) and CONSENSUS_CATALOG (no disagreement at all). Remediation pathway: identify-correct-Y + lens-swap (Ergon's 5-step A-polynomial recomputation per SnapPy). Catalog's own self-flag as LENS_MISMATCH@v1 candidate is the per-lens-pair annotation; Y_IDENTITY_DISPUTE is the catalog-level teeth-test verdict.
surface_statement: Prometheus's tensor reported the knot family as "silent" with respect to number-field projections across 13K knots — zero coupling under any of our scorers. Aporia (Report 3, 2026-04-18) diagnosed the silence as a lens mismatch rather than a true absence: we computed Alexander-polynomial Mahler measures, but Boyd's conjecture concerns A-polynomial (bivariate) Mahler measures tied to the SL(2,ℂ) character variety. The bridge between knots and number fields is categorical, not numerical, and our distributional-coupling primitive was the wrong lens.
anchors_stoa: stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md
---

## What the problem is really asking

1. **Is the "silence" a property of the knots or a property of our
   lens?** Aporia's diagnosis: the lens. We used univariate Mahler
   measure (Alexander) where the literature uses bivariate Mahler
   (A-polynomial). Example: figure-eight knot. Alexander Mahler =
   2.618; A-polynomial prediction = 0.393. Factor-of-6 discrepancy
   from using the wrong polynomial.
2. **Which lens IS the correct bridge?** Morishita's arithmetic
   topology says the knot group / decomposition-group analogy is
   *structural*, not numerical. Chinburg et al. (2026) verified 26
   cases of Mahler(A-poly) = L-value to high precision. The bridge
   exists under the right lens.
3. **How many other Prometheus "silence" verdicts are
   lens-mismatches?** The knot case is the *cleanest documented*
   instance. The category of failure — correct discipline, wrong
   polynomial / wrong projection of the lens — deserves its own
   first-class status.
4. **When a tensor cell reports −1 or 0, is that "null result" or
   "we pointed the wrong instrument"?** Distinguishing these is the
   methodological question the knot case illuminates.
5. **What symbol / pattern captures the failure mode?** Candidate:
   `LENS_MISMATCH@v1` — a lineage type distinct from
   `algebraic_lineage` / `frame_hazard` / `killed_no_correlation` /
   `non_correlational`.

## Data provenance

- **Alexander polynomial**: classical knot invariant, univariate,
  catalogued for all 13K knots in Prometheus's knot atlas.
- **A-polynomial**: defined via the SL(2,ℂ) character variety of
  the knot complement (Cooper-Culler-Gillet-Long-Shalen 1994).
  Bivariate. Not in our data as of 2026-04-21.
- **Boyd's conjecture (2002)**: M(A-poly(K)) is conjecturally a
  ratio of L-values for hyperbolic knots. Explicit verification on
  specific knots by Boyd and collaborators.
- **Chinburg et al. (2026)**: 26 verified cases of Mahler(A-
  polynomial) = L-value at specific arithmetic points, to high
  numerical precision.
- **Morishita 2002+**: arithmetic topology program — knot group /
  Galois group analogy, primes as knots, number fields as
  3-manifolds.
- **Aporia `deep_research_batch1.md` Report 3 (2026-04-18)**: the
  diagnosis. Five-step action list for Ergon to swap the
  polynomial via SnapPy's A-polynomial computation.

**Prometheus tensor state**: 13K knots × all projections = 0 non-
zero cells as of pre-2026-04-18. "Silent island."

## Motivations

- **Immediate substrate leverage.** Aporia has already done the
  diagnostic work. The action items (run SnapPy, extract A-
  polynomials, recompute Mahler under bivariate, cross-reference
  to L-values) are defined. The catalog documents the *pattern*,
  not the recomputation; the recomputation is Ergon's job.
- **First-class `LENS_MISMATCH` capture.** Every future tensor
  negative verdict inherits the question "was that a true kill or
  a lens mismatch?" Naming the failure mode makes the question
  cheap to ask.
- **Cross-session infrastructure.** Prevents re-derivation of
  Aporia's diagnosis by future Harmonias who encounter silent
  islands without knowing this case exists.

## Lens catalog (5 entries)

### Lens 1 — Distributional coupling (what we ran)

- **Discipline:** Statistical / distributional analysis
- **Description:** Scorer-based cosine-ish coupling on Alexander
  Mahler measures against NF projection values.
- **Status:** APPLIED (Prometheus, pre-2026-04-18)
- **Prior result:** Zero coupling across all 13K knots × all
  scorers. **LENS MISMATCH**: wrong polynomial; this lens had no
  chance of finding the bridge.
- **Tier contribution:** Yes — the anchor negative-verdict under
  the wrong lens.

### Lens 2 — Algebraic identity matching (Chinburg / Boyd)

- **Discipline:** Arithmetic geometry / L-function theory
- **Description:** Direct verification that Mahler(A-polynomial) =
  specific L-value at specific arithmetic points. Numerically
  precise, case-by-case.
- **Status:** PUBLIC_KNOWN
- **Prior result:** 26 verified cases (Chinburg 2026). Bridge is
  real and identity-level.
- **Tier contribution:** Yes (entirely different lens from Lens 1).

### Lens 3 — Structural matching (Morishita arithmetic topology)

- **Discipline:** Algebraic topology / algebraic number theory
- **Description:** Categorical analogy: primes ↔ knots; number fields
  ↔ 3-manifolds; decomposition groups ↔ knot groups. Structural
  rather than numerical bridge.
- **Status:** PUBLIC_KNOWN
- **Prior result:** Morishita 2002+; framework with many case
  studies but no tensorable consequences yet.
- **Tier contribution:** Yes — gives the categorical explanation
  for why Lens 2 works.

### Lens 4 — Quantum channel (Khovanov / colored Jones)

- **Discipline:** Topological quantum field theory
- **Description:** Colored Jones polynomial at q = exp(iπ/N);
  Khovanov homology. Quantum-invariant lens on knots.
- **Status:** PUBLIC_KNOWN (volume conjecture ties Jones at
  q=exp(2πi/N) to hyperbolic volume). UNAPPLIED in Prometheus.
- **Expected yield:** A third fingerprint modality for knots,
  orthogonal to both Mahler measures.

### Lens 5 — Hyperbolic volume (SnapPy)

- **Discipline:** Geometric topology
- **Description:** Hyperbolic volume of the knot complement (where
  defined). Related to quantum invariants via volume conjecture.
- **Status:** UNAPPLIED in Prometheus (SnapPy install pending M1
  per `decisions_for_james.md`).
- **Expected yield:** Volume ↔ L-value correspondence via trace
  fields = number fields. Direct bridge into NF tensor.

## Cross-lens summary

- **Total lenses cataloged:** 5
- **APPLIED (Prometheus):** 1 (Lens 1 — wrongly)
- **PUBLIC_KNOWN:** 2
- **UNAPPLIED (Prometheus-addressable):** 2 (Lenses 4, 5 — pending
  SnapPy on M1).

**Current `SHADOWS_ON_WALL@v1` tier:** the surface problem is
`coordinate_invariant` (the bridge is real under the right lens,
per 26 Chinburg verifications + Morishita framework + volume
conjecture partial results). Prometheus's internal coupling is
still a `shadow` — one lens, wrong one.

**Priority moves:**

1. Name the failure mode as `LENS_MISMATCH@v1` (symbol candidate,
   below).
2. Queue Ergon's 5-step A-polynomial recomputation once SnapPy
   lands on M1.
3. Add Lenses 4 and 5 to the tensor's knot-facing projection set.

## LENS_MISMATCH symbol candidate

**Name:** `LENS_MISMATCH@v1`
**Type:** pattern
**Definition:** A tensor negative-verdict produced under a lens
whose formal type matches the problem's discipline but whose
specific implementation / projection / polynomial is not the one
required by the bridge. Distinguished from `killed_no_correlation`
(which claims no bridge exists) by the availability of an
alternative lens in the SAME discipline that WOULD reveal the
bridge.
**Severity tiers (proposed):**
- Level 0 CLEAN: lens is the canonical choice; null result is real.
- Level 1 MILD_MISMATCH: alternative lens in same discipline exists
  but has not been identified as load-bearing.
- Level 2 DOCUMENTED_MISMATCH: literature explicitly names the
  correct alternative lens; current lens is known-incorrect.
- Level 3 PROVEN_MISMATCH: alternative lens has been applied and
  produced a positive verdict on at least one anchor case.
**Anchor:** figure-eight knot; Alexander M = 2.618 vs A-poly
prediction 0.393. Level 2 at Aporia's diagnosis; Level 3 after
SnapPy recomputation confirms.
**Promotion criterion:** ≥ 2 anchor cases distinct in substrate
domain. Currently 1 (knot-NF). Watch for a second.

## Connections

- **Aporia `deep_research_batch1.md` Report 3** — the diagnosis.
- **Aporia `void_detection_framework.md` §Void 1** — knot silence
  as a void anchor. This catalog reclassifies the void from
  "bridge-unknown" to "bridge-known-under-different-lens."
- **`SHADOWS_ON_WALL@v1`** — canonical example of single-lens
  failure in the substrate.
- **`PATTERN_30@v1`** — different failure-mode (algebraic
  coupling in the math); LENS_MISMATCH is on the instrument side.
- **Volume conjecture** — future Lens 5 deployment would tie this
  catalog directly into hyperbolic geometry.
