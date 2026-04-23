# Algebraic Lineage Drafts — 6 NO_LINEAGE_METADATA F-IDs

**Drafted:** 2026-04-20 (harmonia/tmp, gitignored — not for commit)
**Scope:** F011, F013, F014, F022, F044, F045 — the six specimens flagged by
`harmonia/sweeps/retrospective.py` as carrying no algebraic_lineage metadata
and therefore falling to the manual Pattern 30 gate on every downstream task.
**Goal:** shrink that manual gate to zero by giving gen_06's automatic filter
a `CouplingCheck` factory it can register in `LINEAGE_REGISTRY`.

---

## Schema chosen

Each block below mirrors the existing registry entries in
`harmonia/sweeps/retrospective.py` (`bsd_f043_check`, `f015_szpiro_check`,
`_f041a_check`). That pattern is already the de facto schema, so adopting it
means gen_06's `LINEAGE_REGISTRY.update(...)` call is a one-line change per
F-ID. The block captures:

1. **`core_variables`** — the free symbols the specimen actually tests.
   These are what the sympy atom-overlap check compares.
2. **`X_expr` / `Y_expr`** — the two quantities whose correlation / regression
   is the claimed finding, in sympy form where possible. For specimens whose
   finding isn't a correlation at all (F014 density claim, F022 ρ=0 under
   P001, F044 categorical disc=conductor count, F045 per-prime F-test) we
   still declare symbolic forms so the atom-check can say "no shared atoms,
   CLEAN."
3. **`known_identities`** — sympy `Eq(lhs, rhs)` facts that constrain the
   atoms. These are what fires the Level 3 REARRANGEMENT branch.
4. **`transform`** — `"log"` if both sides are on log-scale (the F043 case);
   `"linear"` otherwise. Pattern 30 doesn't use this semantically today but
   the F043 anchor declares it, so we keep the field for future-proofing.
5. **`baseline_severity`** — the level we're claiming at the caller-declared
   severity_hint layer. This is what `sweep()` returns if the auto-check
   can't see an obvious shared atom but the analyst knows the lineage.
6. **`cross_references`** — other F-IDs or symbols sharing algebraic
   structure. gen_06 can follow these edges when deciding whether a
   downstream claim on F_X inherits a Level 1+ coupling from F_Y.
7. **`rationale`** — prose for the Pattern 30 log entry.

The block is written as a `CouplingCheck` factory function, matching the
existing registry convention.

---

## Findings flagged for Pattern 30 promotion / retraction review

- **F013** — REVIEW_RECOMMENDED at Level 1 (WEAK_ALGEBRAIC). F013's cells
  currently hold +2 at P023, P028, P041, P051, P104. Its P028 split is
  "downstream of F011 excised ensemble" by the feature's own description;
  F013 tests a rank-stratified zero-spacing slope, and Katz-Sarnak parity
  splits rank via BSD parity (rank even ↔ SO_even). Because the
  stratification variable (rank) and the resolving axis (SO_even/SO_odd)
  are linked by the BSD parity identity `(-1)^rank = root_number`, a
  correlation of spacing-slope against rank, read through P028, has a
  partial algebraic expectation in the direction of the split.
  Recommendation: annotate at Level 1, not block; the magnitude and
  sign-flip shape (SO_even slope +0.01284 vs SO_odd −0.00216) are not
  forced by the identity. Same pattern as F015's existing Level 1
  annotation.
- **F044** — REVIEW_RECOMMENDED at Level 0 with a Pattern 4 caveat, not
  Pattern 30. The claim `2085/2086 rank-4 EC have disc=conductor` involves
  two arithmetic invariants, but `disc = conductor` IS the definition of
  "no additive reduction" — i.e., this is a definitional tautology if
  read as "curves with semistable reduction have disc=conductor." That is
  Level 4 IDENTITY by the letter of Pattern 30, but the specimen isn't
  claiming a correlation — it's claiming that rank ≥ 4 EC *happen to land*
  in the no-additive-reduction corridor. The right gate is Pattern 4
  (sampling-frame), not Pattern 30. Recommend Level 0 on Pattern 30 with
  an explicit note pointing to Pattern 4 as the active concern.
- **F045** — REVIEW_RECOMMENDED for potential collapse into F041a. F045's
  description already names "correlation with F041a nbp ladder" as a
  kill-confirm task. If isogeny-class-size and num_bad_primes are
  correlated (and they are via P100↔P039 partial tautology declared in
  the projection graph), F045's 5/21 significant primes may be algebraically
  downstream of F041a's nbp ladder. Recommend Level 1 WEAK_ALGEBRAIC with
  cross-reference to F041a; promote to Level 2 SHARED_VARIABLE if the
  nbp-correlation audit confirms.

## F-IDs where lineage could not be determined confidently

- **F022** — LOW_CONFIDENCE. F022 is tier=killed (NF backbone via feature
  distribution, z=0 under P001 permutation null). Its single +2 cell sits
  at P010 (Galois-label object-keyed scorer), which is cross-listed
  to the same data as F010. F010 is also tier=killed (block-shuffle
  z=-0.86). The F022 +2 at P010 encodes "same object at a different
  projection" per the feature_graph edge `F022 → F010 same_object_different_projection`.
  The algebra of a ρ=0 null-result has no meaningful X_expr/Y_expr —
  there is no correlation to break. I've drafted a "vacuous" block
  (CLEAN at Level 0 with a provenance note) but flagged it as
  low-confidence; if Pattern 30 is meant to cover killed specimens at
  all, this may need a separate `killed_specimen_lineage` subclass
  rather than a `CouplingCheck`.

---

## F011 — GUE first-gap variance deficit (rank-0 residual 22.90%)

**Tensor description anchor:** EPS011@v2. Rank-0 residual eps_0 = 22.90% ±
0.78 (1/log(N) ansatz), z=29σ from 0. Independent-unfolding audit survived
(real data 22.90% vs all 50 null permutations at −50% floor; 72.9pp gap).
Cells at P020, P021, P023, P025, P026, P028, P036, P050, P051, P104.

**What is being tested against what:**
- X: post-unfolding first-gap variance of L-function central-zero spacings,
  restricted to rank-0 EC.
- Y: GUE asymptotic first-gap variance (Gaudin distribution).
- Statistic: fractional deficit `(Var_GUE - Var_observed) / Var_GUE`, fitted
  as `eps(N) = eps_0 + C / log(N)^alpha`.

**Algebraic relationships:**
- The N(T) unfolding transform `P051` divides spacings by local density
  `rho(T) = log(N * T^2 / (4 pi^2))`. This is a deterministic transform,
  not a correlation — it rescales one quantity by a known function of
  conductor, introducing at most a Level 0-1 dependence on log(N).
- The three ansatze (power-law / 1/log(N) / 1/log(N)²) are FIT FORMS, not
  algebraic identities connecting X and Y. eps_0 is a fit intercept, not
  a closed-form algebraic quantity.
- Duenez-HKMS (2011) excised ensemble gives a closed-form prediction for
  the LAYER 1 calibration component; F011 description separates this from
  the LAYER 2 rank-0 residual. LAYER 1 is Level 4 IDENTITY by virtue of
  being a known theorem; LAYER 2 is Level 0 by definition (the residual
  is what remains after calibration is subtracted).

**Baseline Pattern 30 severity:** **0 CLEAN**.
- Rationale: no definitional coupling between "first-gap variance of zeros
  restricted to rank-0" and "GUE theoretical prediction." The unfolding
  step is a transform, not an identity coupling. The rank-0 restriction is
  a stratification (Pattern 20 / Pattern 21 territory), not a Pattern 30
  concern.
- Caveat: the P028 Katz-Sarnak resolution of F011 (z=7.63 spread) IS
  algebraically coupled to rank parity via BSD (see F013 entry). When
  gen_06 evaluates a downstream claim that *combines* F011 P028 data
  with a rank-parity-dependent statistic, promote to Level 1.

**Cross-references:**
- F013 — parallel_density_regime (same N(T) unfolding preprocessing).
- F042 — sub_finding_of (CM sub-family within F011 rank-0 residual).
- F043 — F043 mechanistically_explains the T4 sub-family of F011; F043
  was retracted as Level 3 REARRANGEMENT, so any F011 claim that
  *inherits F043's mechanism language* (period-vs-Sha buffering) carries
  the F043 Level 3 coupling. gen_06 should follow this edge.
- F015 — pattern_20 co-anchor; not algebraically coupled.

**Draft `CouplingCheck` factory:**

```python
def f011_gue_deficit_check() -> CouplingCheck:
    """F011 GUE first-gap variance deficit vs GUE asymptote.
    Level 0 CLEAN: no definitional coupling between observed and theoretical
    variance. Stratification and unfolding are transforms, not identities."""
    import sympy
    var_obs, var_gue, N, T = sympy.symbols(
        "var_obs var_gue N T", positive=True)
    eps = (var_gue - var_obs) / var_gue
    return CouplingCheck(
        X_expr=var_obs,
        Y_expr=var_gue,
        known_identities=[],  # no identity connects observed to theoretical
        transform="linear",
        severity_hint="clean",
    )
```

**Note for gen_06:** the F011 rank-0 residual is NOT the correlation itself;
it is `eps_0` from a fit. Pattern 30 as currently implemented doesn't model
fit intercepts. Flag if a downstream F-ID cites `eps_0 = 22.90%` as if it
were a correlation coefficient — that's a category error, not an algebraic
coupling.

---

## F013 — Zero spacing rigidity vs rank (Katz-Sarnak split)

**Tensor description anchor:** Stratified by Katz-Sarnak P028: SO_even
slope=+0.01284, SO_odd slope=−0.00216, slope-diff z=13.68. Block-shuffle
verified at z_block=15.31. Cells at P023, P028, P041, P051, P104.

**What is being tested against what:**
- X: EC rank (integer 0..5).
- Y: slope of `var(zero_spacing)` vs rank, unfolded under P051.
- Stratifier: P028 Katz-Sarnak symmetry type ∈ {SO_even, SO_odd}.

**Algebraic relationships:**
- **BSD parity identity**: `(-1)^rank = root_number` (F003 calibration
  anchor). Root number determines Katz-Sarnak class for EC L-functions:
  SO_even iff rank even, SO_odd iff rank odd.
- Therefore: stratifier P028 is an algebraic function of the independent
  variable X (rank) via BSD parity. A regression of slope against rank
  *within* a Katz-Sarnak stratum is definitionally restricted to same-parity
  ranks (SO_even = {0, 2, 4}; SO_odd = {1, 3, 5}).
- This is NOT a Level 3 rearrangement (Y is not written in terms of X via
  the identity); it IS a Level 1 WEAK_ALGEBRAIC because the stratification
  axis and the regression axis are algebraically linked.

**Baseline Pattern 30 severity:** **1 WEAK_ALGEBRAIC**.
- The direction of the slope sign-flip (SO_even positive, SO_odd negative)
  is partially algebraically expected: conditioning on parity restricts
  rank to every-other-integer, which changes the fit geometry.
- The MAGNITUDES (+0.01284 vs −0.00216) and the SIGN-FLIP itself are
  NOT forced by BSD parity — parity alone doesn't predict the sign of
  the per-parity slope.
- Same pattern as F015 (Level 1 via `log(N)` denominator) and F041a
  (Level 1 via CFKRS arithmetic factor).

**Cross-references:**
- F011 — downstream_of (F013's P028 split is mechanistically driven by
  F011 excised-ensemble central-zero-forcing).
- F003 — constrains (BSD parity is the identity connecting rank to
  Katz-Sarnak class).
- F015 — sibling Level 1 annotation (log-denominator coupling); F013
  inherits the same "direction partially expected, shape not forced"
  reporting discipline.

**Draft `CouplingCheck` factory:**

```python
def f013_rank_spacing_check() -> CouplingCheck:
    """F013 zero-spacing slope vs rank, stratified by P028 Katz-Sarnak.
    Level 1 WEAK_ALGEBRAIC: stratifier (symmetry type) is an algebraic
    function of the regressor (rank) via BSD parity (-1)^rank = root_number.
    Direction-of-slope partially forced; magnitude and sign-flip are not."""
    import sympy
    rank, slope, root_number = sympy.symbols(
        "rank slope root_number", integer=False)
    return CouplingCheck(
        X_expr=rank,
        Y_expr=slope,
        known_identities=[
            # BSD parity — connects rank to Katz-Sarnak stratum via P028
            sympy.Eq(root_number, (-1)**rank),
        ],
        transform="linear",
        severity_hint="weak_algebraic",
    )
```

**Note for gen_06:** If a downstream F-ID claims a within-stratum slope AND
conditions on rank parity independently, the double-conditioning is a
Level 2 SHARED_VARIABLE. The current F013 entry as described does not
do this, but it is a near-miss — any reformulation toward
"slope-vs-rank within SO_even" needs re-auditing.

---

## F014 — Lehmer Mahler measure spectrum (Salem density in (1.176, 1.228))

**Tensor description anchor:** Lehmer bound touched at degrees 10 and 20.
Observed gap 3.41%; 3 polynomials strictly in (1.17628, 1.228), minimum a
Salem polynomial at 1.216392. Bound-touched only at num_ram=1,2; jumps at
num_ram≥3. Cells at P053, P040 (deferred), P023, P021.

**What is being tested against what:**
- X: polynomial class (number field minimal polynomial, Salem polynomial).
- Y: Mahler measure `M(P) = |leading| * prod_{|root_i| > 1} |root_i|`
  under P053.
- Stratified by: degree (P023), num_ram = num_bad_primes (P021).

**Algebraic relationships:**
- Lehmer's polynomial has Mahler measure 1.17628081... (Lehmer 1933). This
  is a specific algebraic number, not an identity.
- Mahler measure is a function of the polynomial's roots:
  `M(P) = |a_d| * prod_{i=1}^{d} max(1, |alpha_i|)`. This is a DEFINITIONAL
  formula, not a coupling between two distinct quantities.
- Salem numbers: algebraic integers α > 1 whose minimal polynomial has
  all other roots on or inside the unit circle, with at least one on.
  Salem polynomial MM is `M(P) = |alpha|` (the single root outside the
  unit circle). No coupling identity here either — it's a definitional
  specialization of the Mahler formula.
- Trinomial floor (Charon eb6d31df): `M(x^n − x − 1) → 1.381` as n→∞.
  This is an asymptotic formula for a SPECIFIC polynomial sequence, not
  a coupling between Mahler measure and any other quantity.

**Baseline Pattern 30 severity:** **0 CLEAN**.
- F014 doesn't run a correlation at all. It reports a density claim
  (3.41% gap, 3 polynomials in-region) and a structural claim (the
  floor widens with degree). No X-vs-Y correlation exists, so there is
  no definitional coupling to catch.
- The per-num_ram monotone (bound touched at num_ram=1,2 only) IS a
  claimed structural relationship between Mahler measure and bad-prime
  count. Since num_ram is derived from the polynomial's discriminant and
  Mahler measure is derived from the polynomial's roots, both are
  functions of the same polynomial — but they are not algebraically
  coupled in the Pattern 30 sense (no rearrangement identity connects
  them).

**Cross-references:**
- F011 — sibling (F014 P021 num_ram monotone "echoes F011 P021 monotone");
  not algebraically coupled.
- F027 — contradicts_at_P053 (Alexander Mahler bridge killed at z=0; same
  P053 projection, different polynomial source).
- F028 — killed tautology (Szpiro × Faltings encodes log|Disc|). Both
  sides of F028 share `log|Disc|`. F014 does NOT share atoms with F028
  (F014 operates on polynomial roots, not discriminants directly), but
  gen_06 should note that `Disc(P)` and `M(P)` are both polynomial
  invariants and guard against Level 2 if a downstream claim correlates
  them.

**Draft `CouplingCheck` factory:**

```python
def f014_lehmer_mahler_check() -> CouplingCheck:
    """F014 Lehmer spectrum: Salem density in (1.176, 1.228).
    Level 0 CLEAN: the finding is a density claim, not a correlation.
    No X-vs-Y coupling to check. Flag downstream claims that correlate
    M(P) with Disc(P) — those could be Level 2 via polynomial-invariant
    shared atoms."""
    import sympy
    M_poly, alpha, deg, num_ram = sympy.symbols(
        "M_poly alpha deg num_ram", positive=True)
    return CouplingCheck(
        X_expr=M_poly,
        Y_expr=alpha,  # Mahler measure of Salem poly IS its largest root
        known_identities=[
            # Salem polynomial MM identity (definitional, informative to gen_06)
            sympy.Eq(M_poly, alpha),
        ],
        transform="linear",
        severity_hint="clean",
    )
```

**Note for gen_06:** The identity `M(Salem) = largest root` is Level 4
IDENTITY for the Salem case specifically, but F014 uses it as a
*definition* (Salem polynomials are those where this holds), not as a
test. The severity_hint="clean" override is the right call; the identity
is declared so downstream F-IDs that correlate M(P) against root-location
statistics get correctly flagged.

---

## F022 — NF backbone via feature distribution (KILLED)

**Tensor description anchor:** tier=killed. z=0.00 under permutation null
when coupling = cosine of feature vectors (P001). Same data as F010 (also
killed). Single active cell: P010 at +2 (same data, object-keyed scorer).

**What is being tested against what:**
- X: feature vectors on NF objects (distributional side).
- Y: feature vectors on Artin-rep objects (distributional side).
- Statistic under P001: cosine similarity of normalized feature vectors,
  z-scored against permutation null.
- Statistic under P010: Galois-label object-keyed match count.

**Algebraic relationships:**
- P001 cosine coupling is a function of the feature vectors; no identity
  connects NF features to Artin features in the F022 framing. Langlands
  functoriality relates the L-functions of these objects, but that
  relationship is not expressible as a sympy identity on the scalar
  features P001 consumes.
- P010 object-keyed match is a categorical identity check (does Galois
  label X appear in both datasets?), not a correlation.

**Baseline Pattern 30 severity:** **0 CLEAN (vacuous)**.
- F022 is a ρ=0 kill. There is no correlation to break. The P010 +2 is a
  categorical count, not a correlation coefficient.
- The block is declared for completeness so gen_06's LINEAGE_REGISTRY
  has F022 → CLEAN rather than NO_LINEAGE_METADATA. This shrinks the
  manual-gate surface without changing any verdict.

**Cross-references:**
- F010 — same_object_different_projection. F010 is also CLEAN (a killed
  specimen with no correlation to audit). If F010 is separately registered,
  gen_06 should inherit F022's CLEAN verdict through this edge.

**Draft `CouplingCheck` factory:**

```python
def f022_nf_backbone_dist_check() -> CouplingCheck:
    """F022 NF backbone via P001 feature-distribution cosine — killed at z=0.
    Level 0 CLEAN (vacuous): ρ=0 kill has no correlation to audit. Block
    declared so gen_06 doesn't fall through to NO_LINEAGE_METADATA."""
    import sympy
    nf_features, artin_features = sympy.symbols(
        "nf_features artin_features")
    return CouplingCheck(
        X_expr=nf_features,
        Y_expr=artin_features,
        known_identities=[],  # Langlands not expressible as scalar identity
        transform="linear",
        severity_hint="clean",
    )
```

**Note for gen_06:** LOW_CONFIDENCE. F022 is structurally different from
the other five — it's a killed specimen whose "finding" is the absence of
signal. Pattern 30 is designed for correlation-based findings; applying it
to a ρ=0 kill is vacuous. If the project eventually distinguishes
`killed_specimen_lineage` from `correlation_lineage`, move this entry. For
now, CLEAN is the conservative call.

---

## F044 — Rank-4 disc=conductor corridor (additive reduction forbidden?)

**Tensor description anchor:** 2085/2086 rank-4 EC in LMFDB have
disc=conductor (no additive bad reduction — only multiplicative). Cells at
P020, P023, P026.

**What is being tested against what:**
- X: EC rank (= 4 by restriction).
- Y: boolean `disc == conductor` (equivalent to "reduction type at every
  bad prime is multiplicative", i.e., P026 semistable half).
- Statistic: counting proportion (2085/2086).

**Algebraic relationships:**
- **Definitional identity**: `disc(E) == conductor(E)` iff E has
  semistable reduction at every bad prime. This is a theorem (Ogg's
  formula: `v_p(disc) = v_p(conductor) + m_p` where m_p is the number of
  components in the Neron model special fiber; m_p = 0 iff multiplicative,
  m_p ≥ 1 iff additive).
- Therefore "disc = conductor" is definitionally "semistable at all primes",
  and the specimen's Y axis is algebraically equal to the P026 stratifier
  restricted to "additive half is empty."
- This is NOT a Pattern 30 concern in the standard sense — the specimen
  does not claim a correlation between rank and a separately-measured
  quantity; it observes that a specific population (rank-4 EC) lies almost
  entirely in the semistable corridor. Pattern 4 (sampling frame) is the
  active concern.

**Baseline Pattern 30 severity:** **0 CLEAN with Pattern 4 flag**.
- The Pattern-30-pedantic reading would be Level 4 IDENTITY (Y is
  definitionally semistable), but "Y = semistable" is a property of
  each object, not a function of rank. The observation "rank-4 curves
  concentrate in the semistable corridor" is a categorical count over
  two independent-per-object attributes — no identity connects them.
- The REAL risk is Pattern 4: LMFDB's rank-4 population is not a random
  sample (Stein/Elkies/Dujella record constructions may be biased toward
  searchable-conductor families). F044 description already names this.

**Cross-references:**
- F003 — constrains (BSD parity anchor; F044 constrains the high-rank
  slice of F003).
- F033 — overlaps_objects (same 2086 rank-4 population).
- P026 — Y axis is algebraically equivalent to the P026 semistable
  stratifier. gen_06 should note: a downstream F-ID that tests rank-4
  prevalence under P026 stratification is double-counting.

**Draft `CouplingCheck` factory:**

```python
def f044_rank4_disc_cond_check() -> CouplingCheck:
    """F044 rank-4 disc=conductor corridor. Level 0 CLEAN on Pattern 30;
    the active risk is Pattern 4 (sampling frame), not algebraic coupling.
    Flag: 'disc == conductor' is definitionally equivalent to P026
    semistable — double-stratification on (Y, P026) is a tautology."""
    import sympy
    disc, conductor, rank, is_semistable = sympy.symbols(
        "disc conductor rank is_semistable", positive=True)
    return CouplingCheck(
        X_expr=rank,
        Y_expr=sympy.Eq(disc, conductor),  # boolean
        known_identities=[
            # Ogg's formula: disc=conductor ⟺ semistable everywhere
            sympy.Eq(sympy.Eq(disc, conductor), is_semistable),
        ],
        transform="linear",
        severity_hint="clean",  # not an algebraic coupling; Pattern 4 gate
    )
```

**Note for gen_06:** Recommend gen_06 attach a Pattern 4 side-flag on F044
promotions rather than a Pattern 30 verdict. F044 is a frame-resample
specimen per the session memory; Pattern 30 is the wrong gate.

---

## F045 — Isogeny-class murmuration (5/21 primes significant)

**Tensor description anchor:** Murmuration-style stratification by isogeny
class size shows 5 of 21 tested primes significant (vs ~1 expected under
chance). Headline p=79 F=6.6. 5-10x weaker than classical rank-based
murmurations. Single cell: P023 at +1.

**What is being tested against what:**
- X: isogeny class size (stratifier via P100, values in {1,2,3,4,6,8}).
- Y: per-prime-p EC attribute (a_p normalized, murmuration-style).
- Statistic: F-test per prime, 5/21 significant.

**Algebraic relationships:**
- **P100 ↔ P039 partial tautology**: isogeny class size ≥ 2 ⇔
  nonmax_primes ≠ [] (declared in the P100 projection description). F041a
  operates on nonmax_primes structure via num_bad_primes (P021).
- **P021 ↔ P100 coupling**: isogeny class size is correlated with
  bad-prime structure (curves with many bad primes tend to have larger
  isogeny classes via torsion constraints). Mazur-bounded values for
  class_size imply a discrete relationship, not a smooth one, but the
  correlation is there.
- F041a's nbp ladder is a rank-2+ slope that's monotone in num_bad_primes.
  If F045's 5/21 significant primes correlate with F041a's nbp ladder,
  F045 may be a partial projection of F041a through the P100↔P021
  coupling.

**Baseline Pattern 30 severity:** **1 WEAK_ALGEBRAIC** (provisional).
- The isogeny-class-size axis is partially algebraic-derived from
  bad-prime structure via the P100↔P021 coupling. If F045's 5 significant
  primes cluster with F041a's nbp ladder, the severity promotes to Level 2
  SHARED_VARIABLE (the stratifier and the test axis both encode bad-prime
  information).
- The specimen's own kill/confirm task names this: "compute per-prime
  uncorrected p-values + correlation with F041a nbp ladder to test
  whether isogeny-class-size and num_bad_primes are independent axes. If
  correlated, F045 may collapse into F041a."

**Cross-references:**
- F041a — adjacent_to. F045 potentially inherits F041a's Level 1
  WEAK_ALGEBRAIC severity via P100↔P021↔nbp coupling. Promote F045 to
  Level 2 if the audit confirms.
- F003 — rank-based murmurations are BSD-parity-conditioned; F045's
  isogeny axis is orthogonal to parity.

**Draft `CouplingCheck` factory:**

```python
def f045_isogeny_murmuration_check() -> CouplingCheck:
    """F045 isogeny-class-size murmuration, 5/21 primes significant.
    Level 1 WEAK_ALGEBRAIC (provisional): P100 class-size ↔ P039 nonmax
    ↔ P021 num_bad_primes partial tautology. If F045 5-prime set correlates
    with F041a's nbp ladder, promote to Level 2 SHARED_VARIABLE."""
    import sympy
    class_size, a_p, num_bad_primes, nonmax_primes = sympy.symbols(
        "class_size a_p num_bad_primes nonmax_primes", positive=True)
    return CouplingCheck(
        X_expr=class_size,
        Y_expr=a_p,
        known_identities=[
            # P100 ↔ P039 partial tautology
            sympy.Eq(class_size >= 2, nonmax_primes > 0),
            # Implicit P021 coupling — correlation, not identity; declared
            # as hint to gen_06 rather than rigorous Eq
        ],
        transform="linear",
        severity_hint="weak_algebraic",
    )
```

**Note for gen_06:** If gen_06 supports a "promote on downstream evidence"
path, wire F045 to re-evaluate its Pattern 30 level when F041a↔F045
correlation data lands. The F045 description explicitly names this as a
kill/confirm path; gen_06 should trigger the re-eval automatically rather
than waiting for manual review.

---

## Summary table

| F-ID | Baseline level | Status | Review flag |
|---|---|---|---|
| F011 | 0 CLEAN | confident | Flag downstream if rank-parity combined with P028 data |
| F013 | 1 WEAK_ALGEBRAIC | confident | **Promotion review** (like F015) |
| F014 | 0 CLEAN | confident | Flag downstream M(P) ↔ Disc(P) correlations |
| F022 | 0 CLEAN (vacuous) | **LOW_CONFIDENCE** | Killed-specimen lineage category needed? |
| F044 | 0 CLEAN + Pattern 4 | confident | **Redirect to Pattern 4** gate |
| F045 | 1 WEAK_ALGEBRAIC (provisional) | confident | **Promotion review** pending F041a audit |

**Epistemic debt reduction if these are accepted:** 6/6 NO_LINEAGE_METADATA
entries retire. Manual Pattern 30 gate on downstream tasks from these
F-IDs closes. Pattern 30 auto-check graduates to 9 registered F-IDs
(F011, F013, F014, F015, F022, F041a, F043, F044, F045).

---

*End of draft. Not for commit — `harmonia/tmp/` is gitignored per repo
convention.*
