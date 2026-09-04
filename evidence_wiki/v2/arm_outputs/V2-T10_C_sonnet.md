# PROPOSAL V2-T10 (arm C)

## Hypothesis

Ranking candidate cross-domain "bridges" between object catalogs (knots, number fields, elliptic
curves, L-function/zeta zero statistics) by feature-vector similarity can surface candidate
correspondences whose cross-catalog hit rate exceeds a correctly-specified, availability-preserving
null by a preregistered margin — but ONLY when the feature vectors are built from native,
theory-motivated invariants; a generic, catalog-agnostic feature-vector similarity metric (moments,
magnitudes, generic numeric summaries) will not clear that bar and will instead reproduce the
already-demonstrated "feature geometry, not object-level coupling" artifact.

This is a two-part, falsification-first hypothesis: H1 (generic vectors fail) and H2 (native-invariant
vectors may succeed, gated by calibration anchors). The design exists to determine which half is true,
not to presume the idea works.

## Motivating evidence

`F:\Prometheus\whitepapers\cross_domain_discovery_instrument.md` (v5.3, 2026-04-09) already mapped this
territory once: a 3-layer model of cross-catalog structure — Layer 1 (scalar correlation) is "a dead
end," 96%+ explained by shared prime factorization and empty after detrending; Layer 2 (structural:
congruences, spectra, recurrences) is "the instrument's sweet spot"; Layer 3 (transformational bridges
— the layer a "cross-domain bridge" actually lives in) is explicitly "largely beyond the instrument's
current reach," with its one Layer-3 probe (M24-EC Hecke matches) later killed by Sturm-bound
verification (Section 16, "Kill #15"). A feature-vector-similarity ranking is a Layer-1/Layer-2
instrument by construction; it has no known mechanism for detecting Layer-3 transformations.

The pack (`v2/packs/V2-T10_pack.json`, canonical_revision 838) adds three later, more specific results
that bear directly on this exact idea: the coupling tensor over NF/EC/knots/modular-forms data measured
feature geometry, not object-level coupling, on all three scorers (C-8f20c74fa0cf), confirmed
independently by a permutation null on the NF backbone landing at z=0.0 (C-1f1a743fce1b); a concrete
attempt to fix a similarity/coupling approach for knots by re-encoding with the mathematically correct
features (Mahler measure, root-of-unity evaluations) still found no signal (C-1938a4759fd8); and a
concrete, large-scale cross-domain bridge candidate (small-Salem number fields as hyperbolic knot trace
fields via the McMullen K3 construction) was cleanly killed at 245,280 evaluations, 0 hits at 10^-40
tolerance (C-534275646eeb). Separately, a generic-vs-native operator comparison on elliptic curves found
that seven generic operators produced zero relations over 294,909,843 reachable triples while one
native verb (quadratic twist) found 4,476 (C-a3744a88ea5e, C-96a0e90f4eeb) — direct evidence that
"generic" vocabularies fail on these object classes where native ones do not, which is exactly the
generic/native split this design tests for feature-vector similarity.

## Prospective predictions

1. The generic-feature arm (Experiment, Stage 1) will find 0 or near-0 candidate correspondences across
   all six catalog pairs, at a scale comparable to the 294,909,843-triple generic-operator null.
2. The native-invariant arm will only be executable for catalog pairs where a theory-motivated
   transformation is already known to exist (e.g. EC-EC via twist); for pairs with no known candidate
   transformation (most knot<->zero-statistics and knot<->NF pairs beyond McMullen K3), the native arm
   is expected to be UNTESTABLE, not merely negative.
3. Any apparent positive signal in either arm will substantially shrink (>=50% of its materiality) under
   the marginal-shuffle "feature geometry" control, reproducing C-8f20c74fa0cf/C-1f1a743fce1b.
4. The naive (within-set) shuffled-label null, if anyone is tempted to reuse it, will again land
   meaningfully above chance (repeating C-750f2b6fc3ac's 0.5903 vs 0.5029); this design preregisters the
   corrected across-set stratified conditional null specifically to prevent that recurrence.

## Experiment

**Catalogs and identity keys.** Elliptic curves: `xref.object_registry` joined via `lmfdb_label` only
— never the raw `object_id` sequence, and only rows with `object_id > 134475` (the reversible repair
watermark) if `object_id` is used at all for bookkeeping. Knots: hyperbolic knot census, keyed by shape
field roots (12,963 available per C-534275646eeb's run). Number fields: NF catalog keyed by
discriminant/Galois-group/defining polynomial, including the 5-polynomial Salem-field set already
characterized. Zeros: zeta/L-function zero-spacing statistics (e.g. Katz-Sarnak family, per the
whitepaper's Layer-2 calibration set of 35,416 Maass forms across 120 level/symmetry pairs, reused here
as a fourth catalog rather than rebuilt).

**Two parallel feature-vector arms, per catalog pair (6 pairs: knots-NF, knots-EC, knots-zeros, NF-EC,
NF-zeros, EC-zeros):**
- Generic arm: catalog-agnostic numeric summaries (moments of trace/coefficient sequences, magnitude of
  discriminant/conductor, degree, spacing statistics) — the same feature class already shown to produce
  feature-geometry artifacts.
- Native arm: only where a preregistered, theory-motivated transformation candidate exists (documented
  before any run, e.g. McMullen K3 for knots<->Salem-NF, quadratic twist for EC-EC as an in-catalog
  calibration case). Pairs with no such candidate are marked UNTESTABLE and excluded from Stage 1, not
  silently scored.

**Stage 0 — instrument calibration (must pass before Stage 1 runs at all).**
Recover two known anchors through the exact same similarity-ranking pipeline: (a) the quadratic-twist
positive anchor (expect >=4,252 of 4,476 relations, i.e. >=95%, collapsing to 12/12 class-level
distinct triples under isogeny-class dedup — C-96a0e90f4eeb); (b) the McMullen K3 negative anchor
(expect exactly 0 hits at 10^-40 tolerance over the same 5 Salem polynomials x 12,963 knot roots —
C-534275646eeb). Any deviation (missed positive anchor, or a nonzero hit on the negative anchor) means
the pipeline is miscalibrated; do not proceed to Stage 1.

**Stage 1 — candidate bridge ranking.** For each testable (pair, arm) cell, rank candidate object pairs
by feature-vector similarity, take the top-k candidates (k preregistered per pair before the run,
matched to the pair's object-count scale), and score the empirical hit rate (correspondence confirmed
by an independent, non-similarity-based check — e.g. exact trace-sequence match, exact algebraic
relation — never by the similarity score itself) against the null defined in Controls below.

## Controls

1. **Corrected null (replaces the vacuous naive null).** Across-set stratified conditional permutation:
   permute candidate labels *across* sets within matched (parent-catalog, relation-type, hit-count)
   strata, preserving availability and hold-count structure — the exact fix C-750f2b6fc3ac's cycle
   specified after its within-set shuffle leaked (0.5903 vs chance 0.5029, >20 SE).
2. **Feature-geometry / marginal-shuffle control.** Recompute the ranking after replacing each object's
   feature vector with a random draw from its own catalog's marginal distribution (preserves per-catalog
   marginals, destroys cross-catalog joint structure). This directly operationalizes C-8f20c74fa0cf and
   C-1f1a743fce1b as an executable control rather than a citation.
3. **Generic-vs-native vocabulary split.** Run both arms separately per pair; do not average or combine
   their scores (no naive score combination across heterogeneous feature populations).
4. **Known-anchor recovery gate.** Stage 0 above; VOID the entire run for a pair if it fails.
5. **Class-level deduplication.** Any "novel" hit must be deduplicated by isogeny-class/equivalence-class
   before being counted, per C-96a0e90f4eeb's 3,896 -> 12 collapse.
6. **Catalog identity/integrity control.** EC joins via `lmfdb_label`, watermark check per
   C-948eae5cb70c; refuse any row where `object_id` is NULL or below 134475 without explicit repair
   verification.
7. **Prime/conductor stratification.** Any conductor- or discriminant-indexed feature is stratified by
   bad-prime count / conductor decade before comparison, per the abc/Szpiro selection-effect rescue
   (C-4d867be1dc68), guarding against the Layer-1 "96% is prime factorization" confound.
8. **No SVD/low-rank shortcut.** The ranking/coupling scores are never passed through SVT-style
   low-rank factorization; C-e0b3b4966385 showed this is invalid for sparse ordinal MNAR data of this
   shape and inflates apparent structure from row/column density marginals alone (~52% of any
   rank-flavored signal).

## Confound defenses

- **Prime atmosphere:** every discriminant/conductor-linked feature is detrended for shared prime
  factorization before any cross-catalog comparison (whitepaper Layer-1: 96%+ of naive scalar
  correlation is this).
- **Feature geometry vs. object coupling:** control 2 above is mandatory, not optional, on every cell
  that reports a positive D.
- **Availability confound:** the stratified null in control 1 exists specifically because a
  state-conditioned ranking can trivially reflect which features/relations are jointly available rather
  than genuine correspondence (C-750f2b6fc3ac).
- **Isogeny/equivalence-class inflation:** control 5.
- **Vocabulary confound:** a null generic-arm result must not be read as "no bridge exists" — it may
  only mean the vocabulary is wrong (C-a3744a88ea5e / C-96a0e90f4eeb); this is why the native arm is
  scored and reported separately rather than folded into a single verdict.
- **Instrument-tautology confound:** Stage 0's negative anchor (McMullen K3, expected exactly 0) guards
  against a pipeline that finds "hits" everywhere regardless of ground truth.

## Preregistered falsifiers (numeric thresholds)

- **F1 — null-calibration gate.** If the corrected across-set stratified conditional null's hit rate
  deviates from theoretical/empirical chance by more than 2 x SE, the cell is VACUOUS regardless of any
  observed D; no accuracy figure from that cell is reportable (tightened from the 146-J episode, where
  the naive null was allowed to drift >20 x SE before being caught).
- **F2 — materiality bar.** D (observed top-k hit rate minus corrected-null hit rate) must exceed
  5 x SE(D) to be considered nontrivial. This is necessary, not sufficient (F1 must also pass).
- **F3 — feature-geometry kill.** If the marginal-shuffle control (Controls #2) recovers >=50% of the
  observed D, the cell is declared a feature-geometry artifact, not object-level coupling.
- **F4 — generic-vocabulary falsifier.** If the generic arm finds 0 candidate hits across a full pass
  (order 10^8 evaluated pairs, matching the 294,909,843-triple precedent) while the native arm (where
  testable) finds >0, the original "generic feature-vector similarity" formulation is falsified for
  that pair; only a native-invariant reformulation may proceed.
- **F5 — anchor-recovery falsifier.** Positive anchor recovered at <95% (< 4,252/4,476, or dedup
  collapse other than exactly 12/12), OR negative anchor returns any nonzero hit at 10^-40 tolerance:
  VOID the run for that pipeline configuration.
- **F6 — dedup-collapse falsifier.** If >=90% of raw "novel" hits collapse to already-LMFDB-recorded or
  same-class duplicates under Control 5, report zero novel discoveries for that cell.
- **F7 — multiple-comparisons control.** 6 catalog pairs x 2 arms = up to 12 family-wise tests; apply
  Holm-Bonferroni at alpha=0.05 across all cells that reach Stage 1 scoring.

## Stopping rule

Stage 0 (calibration) is attempted at most twice per pipeline configuration; two failures -> terminal
ABANDON for that configuration, no Stage 1 run. Within Stage 1, any cell that trips F1 (null
miscalibration) stops immediately for that cell — no D is read, no accuracy figure is reported — and is
routed to a null-redesign track capped at 2 iterations total across the whole program (matching how
much redesign budget 146-J already consumed); a third null failure on the same cell is terminal ABANDON
for that catalog pair, not a third redesign attempt. No new feature definitions, catalog pairs, or arms
may be added once Stage 1 scoring has begun on any cell (no post-hoc metric shopping). The program stops
entirely, with a written VACUOUS/REDESIGN verdict, the moment two of the eight controls fail on any
cell — mirroring the exact "2 of 4 controls failed -> terminal REDESIGN" bar C-750f2b6fc3ac already
used for a structurally identical ranking-validation problem.

## Expected failure modes

1. Feature geometry reproduces itself again (3/3 direct prior attempts in this territory failed this
   way): highest-probability outcome per motivating evidence.
2. Null misspecification recurs in a new form specific to a 4-catalog design that the 2-catalog 146-J
   fix has not been exercised against.
3. Generic vocabulary finds nothing at all six pairs, and no theory-motivated native transformation is
   known for most pairs beyond McMullen K3 (already killed) and EC-twist (already known, not novel) —
   leaving the program with no testable native arm for most of the catalog space.
4. EC catalog joins silently pick up NULL-`object_id` rows, biasing the sample toward the 24,922 curves
   already in the registry pre-rekey.
5. Prime-conductor selection effects reappear in a feature nobody flagged as discriminant/conductor-like
   (e.g. a derived moment that is itself prime-correlated).
6. Someone reintroduces SVD/low-rank scoring as a "cleaner" ranking shortcut, silently resurrecting the
   retracted MNAR-violating method.
7. A positive result is entirely a dedup/isogeny-class-multiplicity artifact, caught only if Control 5
   is actually run rather than assumed clean.

## Compute estimate

CPU-bound, DB-query-dominated; no GPU required for the core pipeline. Up to 12 (pair, arm) cells x
(Stage 0 + Stage 1) ~= 24 similarity-ranking runs, each at a scale comparable to prior single-session
cycles already executed on this infrastructure (141-E: 294,909,843 triples; 142-F: 900 curves x 40-prime
window; 146-J: 1,408,539 extension attempts) — order 10^6-10^8 pair evaluations per cell, minutes to a
few hours each on existing DB infra. Total wall-clock: roughly 1-3 days across a single machine for the
full 12-cell program, assuming Stage 0 passes on the first attempt. Minor LLM/agent time for
native-transformation candidate identification and dedup-class labeling per pair; no training runs, no
new corpus ingestion.

## Prior evidence that materially changed this design (or 'none found')

`F:\Prometheus\whitepapers\cross_domain_discovery_instrument.md` (Layer 1/2/3 model) reframed the
hypothesis from "will feature-vector similarity find bridges" to "feature-vector similarity is a
Layer-1/2 instrument with no known mechanism for Layer-3 transformations" — this is why the hypothesis
is stated as a generic-vs-native split rather than a single monolithic claim.
`F:\Prometheus\aporia\docs\CYCLE_146J_OPERATOR_RANKING_2026-08-24.md` supplied the exact corrected-null
mechanics (across-set stratified conditional permutation, replacing a within-set shuffle that leaked
>20 SE above chance) used verbatim in Controls #1 and Falsifier F1.
`F:\Prometheus\aporia\docs\CYCLE_142F_NATIVE_VERBS_2026-08-23.md` supplied the generic-vs-native
methodology (7 generic operators vs 1 native verb) and the exact dedup-collapse mechanics (3,896 -> 12)
used in Controls #3/#5 and Falsifiers F4/F6.

## Pack items that changed this design (ids -> concrete decision; 'pack did not affect design' is valid)

- C-8f20c74fa0cf -> mandated an executable marginal-shuffle "feature geometry" control (Controls #2),
  not merely a citation of the risk.
- C-1938a4759fd8 -> the design does not treat "use the mathematically correct features" as sufficient;
  it requires a native-vs-generic split with the generic arm expected to fail regardless.
- C-534275646eeb -> repurposed as the Stage 0 negative calibration anchor (must reproduce exactly 0 hits
  at 10^-40) rather than a hypothesis to re-test.
- C-1f1a743fce1b -> reinforced Controls #2 as mandatory (distributional-vs-object-level distinction).
- C-e0b3b4966385 -> added the explicit SVD/low-rank ban (Controls #8).
- C-96a0e90f4eeb / C-a3744a88ea5e -> produced the two-arm generic-vs-native design itself; set F4's
  0-hits generic threshold and F6's dedup-collapse threshold and the Stage 0 positive-anchor numbers
  (4,476 / 95% / 12-of-12).
- C-750f2b6fc3ac -> replaced the naive shuffled-label null with the corrected across-set stratified
  conditional permutation (Controls #1) and set the "2 of N controls fail -> terminal" stopping bar.
- C-948eae5cb70c -> added the EC catalog identity/integrity control (`lmfdb_label`, watermark 134475).
- C-4d867be1dc68 -> added the prime/conductor stratification confound defense.

## Operation log (numbered; ops used / 15, documents opened / 12)

1. Read `v2/packs/V2-T10_pack.json` (free, not counted against budget).
2. Grep (files_with_matches): `cross-domain bridge|feature-vector similarity|feature vector similarity`
   over `F:\Prometheus`.
3. Grep (files_with_matches): `McMullen K3|Salem` over `F:\Prometheus`.
4. Read `F:\Prometheus\whitepapers\cross_domain_discovery_instrument.md` (document 1/12).
5. Read `F:\Prometheus\aporia\docs\CYCLE_146J_OPERATOR_RANKING_2026-08-24.md` (document 2/12).
6. Read `F:\Prometheus\aporia\docs\CYCLE_142F_NATIVE_VERBS_2026-08-23.md` (document 3/12).

Ops used: 5 / 15 (excluding the free pack read). Documents opened: 3 / 12. Early stop: the two greps
plus three targeted reads gave concordant, mutually reinforcing evidence (a genesis whitepaper stating
the Layer-1/2/3 ceiling, plus the two most recent, most methodologically detailed cycles in the pack)
sufficient to fully specify the validation without further search.
