# Erebos v3 DR Synthesis — Batch 5 (G24 Symmetry/Twist + G25 Degeneracy/Trivial-Case)

**Batch:** 5 of 5 (final)
**Source DRs:** `21_g24_symmetry_twist_v2_design_audit.md`, `22_g25_degeneracy_trivial_case_v2_design_audit.md`
**Agent:** deep-research-pro-preview-12-2025 (both)
**Synthesis date:** 2026-05-27
**Synthesizer scope:** Key Points + Sections 1-3 + Section 5 of each report (per task brief)

---

## Orientation

This is the smallest batch in the Erebos v3 synthesis run, covering the two
plugins whose v1 reputations were "100% pass rates that mean nothing." Both
DRs converge on the same diagnosis: the v1 plugins were *measuring the wrong
thing*, and a v1 "pass" is statistically indistinguishable from "the
instrument is asleep." The remediation prescribed in both DRs is structurally
identical even though the underlying mathematics is different — and that
convergence is itself the most important finding of this batch.

Where prior batches surfaced ~6-10 cross-cutting themes, this batch is
deliberately tighter (2 plugins → 2-4 themes, 1-3 contrarians). The signal
density per theme is higher.

---

## A. CROSS-CUTTING THEMES (both DRs)

### A1. "Tautological pass" is the dominant v1 pathology — and it is invisible to row-count gates

Both DRs frame their respective v1 plugins as **tautology generators that
have been mislabelled as validators**.

- **G24 v1** audits the Mossinghoff catalog with the same two symmetries
  (reciprocal + sign-flip) that Mossinghoff/Boyd's original 1990s search
  algorithms used to *prune* the catalog. The DR's contrarian Section 7
  argues this is structurally tautological: every entry is in the catalog
  *because* it already survived these filters on PARI/C clusters 25+ years
  ago. A 200/200 pass rate is therefore mathematically inevitable, not
  evidentially weighty.
- **G25 v1** approves any subset where `len(catalog_subset) > 0`. The
  Iter-12 case study (§5) shows G11 v1 running on an n=8501 subset drawn
  entirely from a single Salem-cluster, "discovering" that 100% of entries
  had the Salem-class property — i.e. asking "do all apples in this bag of
  apples have apple-like qualities?" G25 v1 cleared the run because n > 0.

The shared pathology: **v1 gates check a presence/availability property
(row exists, symmetry generates output) instead of an evidential property
(this check could have produced a meaningful negative)**. Both DRs name the
fix `kill_tautological_pass` or equivalent. This is the same anti-pattern
seen in batches 1-4 around "calibration mode vs discovery mode" — surfacing
here in its purest form.

### A2. Degeneracy / invariance are *relational*, not intrinsic — gates must consult the hypothesis

Both DRs argue the v2 architecture cannot be a monolithic pre-filter sitting
in front of the data; it must be a **per-query consultant** that ingests the
downstream plugin's hypothesis profile.

- **G25 §6** ("Degeneracy is a Property of the Inquiry") makes this explicit:
  a 5,000-row all-Salem subset is *degenerate* for a chi-square Salem-vs-non-Salem
  test but *rich* for a trace-distribution test. The same data, two verdicts.
  The proposed sidecar:
  `G25.evaluate_suitability(Raw_Data, Plugin.Hypothesis_Matrix) → verdict`
  rather than `Filtered = G25(Raw); Result = Plugin(Filtered)`.
- **G24 §3** independently arrives at the same shape: Mahler-preserving
  symmetries do *not* preserve every metadata field. Sign-flip preserves
  M(P) but *breaks* `salem_class`; cyclotomic extraction preserves M(P) but
  *breaks* `degree_minimum`. The audit verdict must therefore be
  parameterised by (symmetry, metadata-field) pairs — exactly the same
  relational shape as G25's (data, hypothesis) pairs.

Both DRs prescribe a **registration protocol** where downstream plugins
publish their evidential requirements (variance thresholds, preserved-field
sets, test-types) and the v2 gate evaluates fitness against that registered
profile. The shared schema element is a structured `Alert` object with
`target_plugins`, `degeneracy_type`/`symmetry_break_type`, and
`kill_pattern`, mutated onto the `parent_row` so downstream plugins must
explicitly consult before firing.

### A3. Information-theoretic / precision-aware thresholds replace static numeric tolerances

A subtler but equally clean convergence: both DRs replace a single
hardcoded threshold (G24's `1e-6` Mahler tolerance, G25's
`len(subset) > 0`) with **dynamically-calculated, context-sensitive
quantities derived from the actual computation**.

- **G24 §4** ties tolerance to PARI/GP's reported error bound, the
  polynomial's degree-dependent condition number, and the catalog's
  native precision (~14 decimal digits for Mossinghoff,
  arbitrary-precision via Arb for modern recomputation):
  `τ_audit = max(ε_catalog, Error_PARI × C_d)`
- **G25 §2** replaces "n > 0" with Shannon entropy of the binned feature
  distribution, Effective Sample Size `N_ess = 1 / Σw_i²`, and EVT-based
  tail-collapse tests (GPD shape parameter ξ on the upper/lower 5%).

Both DRs explicitly note that the old static thresholds *waste* available
information — G24 squanders 8 of 14 significant digits, G25 ignores the
entropy structure of the 8500 rows it cleared. The shared principle: **let
the gate's threshold be a function of the same precision/structure that
the underlying mathematical machinery already computed**, rather than a
human-picked constant.

### A4. v2 plugins must be capable of producing falsifications, not just passes

This emerges as a unifying methodological frame across §6 of G24 ("Instrument
Validation vs. Discovery") and §3/§5 of G25 (DegeneracyAlert + Iter-12 case
study). Both DRs argue the *measure of a good v2 gate* is whether it can,
on real catalog data, produce a non-trivial negative — either a
`kill_pattern` that halts a downstream plugin (G25) or an empirical
violation of a conjectured symmetry that constitutes "substrate-grade
evidence" (G24 §6, exhaustively clearing Lehmer's danger zone for
candidate proofs).

A v2 plugin that never kills anything has the same epistemic value as v1.
This dovetails with the Prometheus posture
`feedback_failure_signal_vector_field.md`: failures are directional
pointers, not pass/fail. Both gates must emit *typed* kill-patterns
(not just booleans) so the failure signal carries enough structure to
route subsequent work.

---

## B. PRIOR ART CONVERGENCE (cited / load-bearing in both DRs)

The two DRs draw from very different bodies of literature (G24 is pure
analytic number theory + computational algebra; G25 is statistical ML +
logic + PDE identifiability). True cross-citation is therefore sparse,
but two anchors recur structurally:

### B1. Lehmer's Conjecture / Salem numbers / Mossinghoff catalog
Both DRs use Lehmer/Salem as their primary running example.
- G24: foundational subject — Lehmer's polynomial L(x) = x^10 + x^9 - x^7 -
  ... + 1, M(L) ≈ 1.17628; Mossinghoff catalog cited as `[cite: 12, 13]`.
- G25 §5 (case study): Salem numbers as the example for the Iter-12
  tautology; the smallest Salem number λ_0 ≈ 1.1762808; the Mossinghoff
  catalog cited as `[cite: 13]`.

Both reports lean on the same `[cite: 13]` Mossinghoff-derived corpus and
on the same Lehmer-conjecture conceptual scaffolding. This is the single
most strongly shared empirical substrate of the batch.

### B2. PARI/GP + Arb + arbitrary-precision arithmetic as the *computational* substrate
G24 explicitly cites PARI/GP's `polroots`, `\p 38` precision settings, and
Arb interval arithmetic (`[cite: 14, 15, 16]`). G25 does not cite PARI
directly, but its EVT-based threshold module and ESS adjustment assume an
equivalent arbitrary-precision numerical backbone — both reports
implicitly treat the underlying CAS layer as the source-of-truth for
"how much precision is actually available," and both architect v2 to
*ask* that layer rather than guess.

### B3. (Soft convergence — methodological, not citational)
- G24 §3's field-by-field symmetry matrix and G25 §1.3's "structural
  non-identifiability" taxonomy both descend from the same lineage of
  *parameter identifiability in inverse problems* (G25 cites `[cite: 6, 7]`
  from nih.gov on PDE identifiability). G24 doesn't cite this lineage
  but reinvents its shape: "indistinguishable under the lens of the
  specific mathematical inquiry" (G25 §1.3) is the same insight as
  "M(P)-invariant but degree_minimum-breaking" (G24 §3.1).
- Both DRs draw on the broader 2024-2026 wave of formal-verification +
  computational-mathematics literature (Lean 4's Mathlib `logMahlerMeasure_mul_eq_add_logMahlerMeasure`
  in G24; LogicAgent semiotic-square + Existential Import Check in G25).

No author appears in both citation lists by name. The convergence is at
the level of methodological frame, not specific papers.

---

## C. NEW SUBSTRATE-CAPABILITIES THE DRs DEMAND

The two DRs together demand five new substrate-level capabilities. These
are stated as concrete subsystems that *do not yet exist* in
Erebos v1/v2 and are prerequisites for the v3 specifications in the DRs.

### C1. A `Hypothesis_Matrix` / `DataRequirementProfile` registration bus
Both v2 specs require downstream plugins to *declare* what they need from
their input before they run. G25 §3.1 names this the "data requirement
profile" (registered fields, variance thresholds, test type); G24 §3
implies an equivalent (preserved-metadata-field set, expected-break-set
per symmetry). Substrate needs:
- A typed schema for these profiles (per-plugin, per-test-variant).
- A pub/sub mechanism on the `parent_row` so v2 gates can intercept
  before execute() is called.
- A registry that maps `(plugin, test_type) → required_profile` so
  profiles are discoverable and auditable.

This is the single largest substrate-architecture change demanded by the
batch.

### C2. A precision-introspection API on the computational backend
G24 §4 requires the audit layer to *ask* PARI/GP for the per-evaluation
error bound (e.g., `Error_PARI` from `polroots` conditioning) and combine
it with the polynomial's degree-dependent conditioning constant to derive
the audit tolerance. Substrate needs:
- A wrapper around the PARI/Arb call sites that returns
  `(value, error_bound, precision_used)` rather than bare floats.
- A `CoordinateChart`-style metadata object so downstream code knows
  *what* precision regime the value lives in (this aligns with
  `feedback_substrate_v2_lockins.md` lock-in #2: no metric across
  heterogeneous spaces without a registered chart).
- Symmetric support for G25's information-theoretic measures: Shannon
  entropy, ESS, GPD-tail-fit must all carry their own confidence bands.

### C3. Typed kill-patterns with payload, not boolean flags
Both DRs propose specific named kill-patterns:
- G24: `kill_field_salem_negation_violation`,
  `kill_field_degree_minimum_mismatch`, `kill_smyth_reciprocity_collapse`,
  `kill_precision_limit_reached`, `kill_galois_closure_failure`,
  `kill_measure_deviation_exceeds_dynamic_tau`.
- G25: `kill_tautological_pass`, `kill_degenerate_input_artifact`,
  `kill_chi_sq_degeneracy`, `kill_perm_degeneracy`,
  `kill_false_invariance_detected`.

Substrate needs a `KillPattern` type with: name, triggering plugin, target
parent_row, metrics that triggered it, resolution_advice. The
`DegeneracyAlert` JSON schema in G25 §3.2 is a usable template.

### C4. Cross-plugin alert routing (DAG with pre-flight interception)
G25 §3 spells out a 4-stage protocol: register → evaluate → emit → consult.
G24 implies a quieter version of the same mechanism in §5.1 (the auditor
mutates `kill_pattern` strings into the audit log; downstream consumers
of the catalog must check). The substrate-level requirement is a single
event bus + decorator pattern that wraps every plugin's `execute()` and
forces consultation. This should be implemented *once*, used by both
gates (and retrofitted onto G11, G17, G02, G04).

### C5. Discovery-mode harness alongside validation-mode harness
G24 §6 ("Instrument Validation vs. Discovery") explicitly proposes
re-pointing the same architectural machinery at *unproven* conjectures:
multivariate exact polynomial substitutions (Boyd-Brunault L-value
identities), spherical Mahler measure (Sean Paul 2026), Fuglede-Kadison
determinants on graph polynomials. Substrate needs:
- A toggle / mode where v2 gates run against *non-catalog* inputs (e.g.,
  systematically-generated symmetry-twists, multivariate substitutions).
- Logging of "exhaustively cleared the danger zone" as a first-class
  substrate-grade evidence type (G24 explicitly names degrees ≤ 180,
  M < 1.3 as the canonical Lehmer danger zone).
- This dovetails with G25's note that the same gate that detects
  degeneracy in calibration data should detect *interesting* degeneracy
  in discovery data — non-identifiability that points at a real
  mathematical structure.

---

## D. PLUGIN-SPECIFIC HOTSPOTS (code-level change demanded, one per plugin)

### D1. G24 Symmetry/Twist — Hotspot: replace the static `tolerance=1e-6` symmetry comparator with a `(symmetry, field) → preservation_expectation` matrix + dynamic τ

The single most concrete code-level change demanded by G24's DR is in §3.1
and §4.1. Current G24 v1/v2 loaders do something equivalent to:

```python
if abs(M(twisted_poly) - catalog_M) < 1e-6:
    pass_count += 1
```

The DR demands this be replaced by:

```python
# §3 matrix: per-symmetry, per-metadata-field expected behavior
SYMMETRY_FIELD_MATRIX = {
    ("x→-x", "salem_class"):       "breaks",
    ("x→-x", "degree_minimum"):    "invariant",
    ("x→1/x", "salem_class"):      "invariant",
    ("cyclotomic_extract", "degree_minimum"): "breaks",
    # ...
}

# §4 dynamic tolerance
tau = max(1e-14, error_pari * conditioning_multiplier(degree))

# audit asserts BOTH the expected M-preservation AND the expected field-behavior
for (sym, field), expected in SYMMETRY_FIELD_MATRIX.items():
    twisted = apply(sym, poly)
    if expected == "invariant" and abs(M(twisted) - catalog_M) > tau:
        raise KillPattern("kill_symmetry_breaking_dynamic_tau", ...)
    if expected == "breaks" and abs(M(twisted) - catalog_M) <= tau:
        raise KillPattern("kill_false_invariance_detected", ...)
    # plus metadata-field check per matrix row
```

The DR's `G24v3SymmetryAuditor` class skeleton in §5.1 is the canonical
target. Additionally, the suite must be *extended* beyond reciprocal +
sign-flip to include cyclotomic-factor extraction, Galois conjugation /
orbit closure, anti-reciprocal, plus *expected-to-break* shifts (x→x+a)
and scalings (x→cx) — the latter to verify the instrument is actually
recomputing rather than returning a cached pass.

### D2. G25 Degeneracy / Trivial-Case — Hotspot: replace `len(subset) > 0` with `(N_ess, H(X), tail-shape ξ)` triple, parameterized by downstream test-type

The single most concrete code-level change demanded by G25's DR is in §2
and §4. Current G25 v1 does essentially:

```python
def validate(parent_row):
    return len(parent_row.data) > 0
```

The DR demands:

```python
def evaluate_suitability(parent_row, hypothesis_matrix):
    feature = hypothesis_matrix.target_feature
    test_type = hypothesis_matrix.test_type

    # entropy-based ESS
    H = shannon_entropy(parent_row.data[feature])
    N_ess = 1 / sum(w**2 for w in normalized_weights(parent_row.data, feature))

    # tail-collapse
    xi = fit_gpd(parent_row.data[feature].tail_quantile(0.05)).shape_param

    # per-test-type thresholds (§4.1 component C)
    if test_type == 'chi_square' and N_ess < max(30, 0.05 * len(parent_row.data)):
        return DegeneracyAlert(kind='chi_sq_degeneracy', N_ess=N_ess, H=H, ...)
    if test_type == 'permutation_null' and N_ess < 2:
        return DegeneracyAlert(kind='perm_degeneracy', ...)
    if xi < EXPECTED_TAIL_LOWER_BOUND[test_type]:
        return DegeneracyAlert(kind='tail_collapse', ...)
    return Valid()
```

The Iter-12 walkthrough in §5.4 is the canonical regression test: a
n=8501 subset all in one Salem cluster must yield H(cluster_id) = 0,
N_ess = 1, and `kill_tautological_pass` emitted to G11 *before* G11 runs.

Note: the per-test-type table in §4.1 component C is the critical
substrate piece — without it, G25 v2 would simply trade one false-rejection
problem (over-strict) for another (over-permissive). Chi-square's strict
balance requirement and permutation-null's tolerance for imbalance are
*intrinsically different*; v2 must encode both.

---

## E. CONTRARIAN ALTERNATIVES

### E1. The Tautology-IS-The-Point Steelman (G24 §7)

The DR steelmans, then partially endorses, the position that **auditing
the Mossinghoff catalog with the same symmetries Mossinghoff used to
generate it is mathematically vacuous, and we should be honest about
this.** The argument: Boyd's limit-point algorithms and Mossinghoff's
genetic-algorithm searches *inherently* used cyclotomic-factor pruning
and reciprocal-symmetry reduction. Every entry in the catalog is there
*because* it survived those filters in 1998-2010. G24 v2's 200/200 pass
rate teaches us nothing mathematical — it merely verifies that
Mossinghoff's bare-metal C code didn't suffer a cosmic-ray bit-flip and
that the JSON serialization round-trip didn't corrupt anything. The
contrarian conclusion: **stop calling G24 a mathematical instrument and
admit it is a CI/CD checksum**, then either deprecate it or repurpose
the architecture for genuine discovery (per §6).

The DR's rebuttal (also in §7) is itself worth taking seriously: a
"tautology" applied across two independent system implementations
(1998 PARI/GP vs 2026 SageMath+Arb) is the definition of a rigorous
cross-software checksum, and is *especially* valuable because metadata
fields like `salem_class` and `degree_minimum` *were not* in the
original generation pipeline and *can* fail.

**Prometheus reading:** lean toward the steelman. The fair posture is to
explicitly mode-split G24 into (a) calibration-mode (checksum, no
evidential weight) and (b) discovery-mode (per §6 — substitutions into
multivariate Mahler measures, spherical measure, Fuglede-Kadison
determinants on graphs), and only count (b) toward Prometheus's
mathematical claims. Aligns with
`feedback_substrate_passive_consumer_warning.md` — every G24 doc must
trace to a behavior delta, and "passes the checksum" is not one.

### E2. Reject the Consultant Architecture, Embrace Universal Conservatism (anti-G25 §6)

A contrarian to G25's "degeneracy is relational" thesis: the *price* of
the consultant architecture is a combinatorial explosion of
`(plugin, test_type, hypothesis_matrix)` triples that must all be
specified, registered, and version-controlled. Each new downstream plugin
forces a new G25 profile; each schema change cascades. An alternative
position: **adopt a single, conservative global gate (e.g., demand
N_ess ≥ 30 and H(X) ≥ 1 bit for *every* test, regardless of type) and
accept that some valid permutation-null tests will be rejected.** This
trades scientific reach for architectural simplicity and removes the
attack surface where a buggy or missing hypothesis_matrix silently
re-introduces tautological passes.

The G25 DR rejects this implicitly by repeatedly invoking the
chi-square-vs-permutation-null asymmetry. But for Prometheus specifically
— given the
`feedback_substrate_tester_multi_instance.md` posture that
substrate-discipline matters more than per-plugin yield — the
conservative-global-gate option deserves explicit consideration as the
v3 default, with per-plugin overrides only when a plugin can produce a
documented justification. This inverts the DR's preferred default
(consultant first, fall back to global) into (global first, opt out to
consultant).

### E3. Symmetry-Closure vs Symmetry-Audit (deep-cut for G24)

A third contrarian, implicit in G24 §2.2 (Galois conjugation) but not
fully articulated: instead of *auditing* the catalog by applying
symmetries and checking invariance, **canonicalize the catalog under the
full symmetry group first**, storing only one representative per orbit
under (reciprocal × sign-flip × cyclotomic-extraction × anti-reciprocal ×
Galois). Then symmetry-audit becomes a no-op — every twist returns the
representative, and the only failure mode is a representative-selection
bug. The DR doesn't propose this because the Mossinghoff catalog is
not under our control, but for Prometheus's *internal* catalogs (Charon
zeros, Megethos basis, etc.) the canonicalization-first approach
collapses an entire class of false-positive findings into a single
data-engineering decision made once. This pairs naturally with
`prometheus_math/databases/canonicalization_fuzz_failures.json` already
present in the repo (per git status) — the same machinery, applied at
catalog-write time rather than audit-read time.

---

## Closing observations (batch-5 specific)

1. **Batch 5 is the cleanest convergence of the five batches.** With only
   two plugins, both authored by the same DR agent, the architectural
   prescription emerges crisp: relational gates, typed kill-patterns,
   pre-flight interception, precision-introspection. Where prior batches
   had to triangulate across 5-7 reports, here the signal is dense.

2. **G24 and G25 are structurally dual.** G24 catches when an *operation*
   that should preserve a property fails to (or fails to fail to). G25
   catches when a *dataset* that should support an inquiry doesn't (or
   appears to but doesn't really). Both are "expected-vs-actual"
   verifiers parameterized over (object, hypothesis). The v3 substrate
   should consider unifying them under a single `RelationalGate`
   abstraction, with G24/G25 as instantiations.

3. **The "tautological pass" failure mode is now the dominant Erebos
   anti-pattern across all 5 batches.** Batch 1 saw it as
   "calibration-as-discovery" confusion; batch 3 as "instrument noise
   masquerading as signal"; batch 5 surfaces it in its purest form —
   gates that *cannot* return negative. Erebos v3's substrate-level
   commitment should be: **every gate must have a non-empty preimage of
   inputs on which it returns FALSE on real catalog data**, and that
   preimage must be exercised in CI. (This is a concrete substrate
   commitment and a candidate for `aporia/doctrine/critical_memories.md`.)

4. **Discovery-mode toggle is the cross-batch lever.** G24 §6's
   redirection of validator architecture onto unproven conjectures is the
   highest-leverage capability in batch 5. Combined with G25's
   `DegeneracyAlert` machinery (which can detect *interesting*
   degeneracies — geometric collapses that point at real mathematical
   structure), v3 has the bones of an active mathematical-instrument
   loop, not just a passive checksum. This is the most direct line from
   Erebos v3 to Prometheus's stated north star
   (`project_falsification_routing_learner.md`,
   `feedback_substrate_passive_consumer_warning.md`).
