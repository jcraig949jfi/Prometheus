# PROPOSAL T5 (control)

Designer: control arm, 2026-09-02. Target: coupling search between `topology.knots`
invariants and spectral/arithmetic data in the Prometheus spine (Postgres, prometheus_sci).

## Hypothesis

**H1 (primary, conductor-level arithmetic coupling).** The composition of the knot
population sharing a given determinant value q carries information about the low-lying
spectral statistics of Dirichlet L-functions of conductor q, beyond what the magnitude
and prime structure of q already determine.

Operationally: for each distinct odd q that occurs as a knot determinant, define

- X1(q) = fraction of knots with det = q that are alternating, read off the Jones span
  law: alternating iff span(V_K) = c+1 exactly (Kauffman–Murasugi–Thistlethwaite;
  observed as a database law in ATTACK_MATH-0332), where span = (index of last nonzero
  Jones coefficient − index of first nonzero) and c = crossing_number.
- X2(q) = mean log Mahler measure of the Jones polynomial over knots with det = q
  (log M(V) = Σ max(0, log|r_i|) over roots r_i of the coefficient vector, + log|lead|).
- Y(q) = mean unfolded first-zero height over rows of `zeros.dirichlet_zeros` with
  conductor = q: z̃1 = z1 · log(q+2)/(2π) (density unfolding; shape, not scale — the
  raw z1 trend with q is pure magnitude and is removed before any coupling claim).

H1 predicts a nonzero partial association between X_i(q) and Y(q) after removing the
magnitude/arithmetic trend of q. **Default expectation is the null**: the only channel
connecting a knot to conductor q is the integer q itself, so any residual association
is either a discovery or an unmodeled confound. This proposal is written so the null
is a clean, publishable NO_COUPLING verdict, not a failure.

**H2 (secondary, spectral-universality replication).** Unfolded spacing statistics of
Jones-root angles on/near the unit circle are indistinguishable from a degree- and
coefficient-range-matched random-polynomial ensemble (i.e., prior GUE-adjacent claims
are generic-polynomial artifacts, not knot structure). This replicates, with frozen
thresholds, the kill battery in `cartography/shared/scripts/knot_root_gue_verify.py`.

## Design

**Data snapshot (frozen before execution; row extracts committed with the verdict).**

- Knots: `topology.knots`, restricted to rows with `array_length(jones_coeffs,1) > 0`.
  Known data reality (trap #8): all 12,965 rows are NOT NULL but the 9,988
  crossing-13 rows hold EMPTY arrays; effective population is **2,977 knots,
  crossings 3–12** — filter on array_length, never on IS NOT NULL. `signature` is
  0/12,965 populated and is EXCLUDED from the design; `determinant` is populated
  exactly on the 2,977; `crossing_number` was repaired from the name prefix
  (thesauros/proposals.md) — spot-check 20 names against the prefix before use.
- Determinant inventory (measured on the source JSON, 2026-09-02): 167 distinct
  values, all odd, range 1–377, 155 values with multiplicity ≥ 2.
- Spectral: `zeros.dirichlet_zeros` (184,830 rows; conductor, degree, zeros_vector).
  Use degree-1 rows only. Preflight: enumerate conductor coverage on 1–377 FIRST
  (full inventory, no prefix/window sampling); N_q = number of distinct knot
  determinants with ≥ 1 covered L-function.
- Consistency calibration (free, non-gating): |Δ_K(−1)| recomputed from
  alexander_coeffs must equal `determinant` wherever both exist; mismatch rate > 1%
  aborts to a data-audit, not a science verdict.

**Primary statistic.** Spearman partial correlation ρ_p(X_i, Y | Z) across the N_q
distinct conductor values, with covariate set Z = { log q, ω(q) (number of distinct
prime factors), 1_prime(q) }, computed by rank-regressing X and Y on Z and correlating
residuals. Two pre-named tests: (X1, Y) and (X2, Y); Holm correction over exactly
these two, family size 2. No other invariant–statistic pair may be promoted to
confirmatory; anything else run is labeled exploratory in the ledger.

**Null model (primary).** 10,000 permutations, seed 42, permuting the X̄ vector over
conductor values *within magnitude deciles of q* (block permutation). This perturbs
the axis the statistic lives on (the q-indexed pairing) while preserving each
variable's marginal distribution and its magnitude trend. A full unrestricted
permutation is also reported (weaker; magnitude leakage expected) but is not the gate.

**Power/SE preflight (before reading any verdict).** With N_q ≤ 167,
SE(ρ) ≈ 1/√(N_q − 3) ≈ 0.078 at N_q = 167. The effect threshold (0.20 below) is
≥ 2.5 × SE at N_q = 167 and ≥ 2 × SE down to N_q = 120; below N_q = 120 the gate is
declared unreachable and the run reads VACUOUS (gate must exceed measurement error;
gate must be shown reachable — compute the attainable |ρ| range given tied ranks and
within-decile block sizes before unblinding Y).

**Positive control (instrument calibration, run first).** The pipeline must detect the
KNOWN coupling before the residual test is read: raw (un-unfolded) z1 vs log q must
show |Spearman ρ| ≥ 0.5 across the same N_q conductors. If it does not, the
instrument is broken; stop, no science verdict (signature-existence-first).

**Secondary arm (H2).** Unfolded angle-spacing distribution of Jones roots within
0.05 of the unit circle, pooled over the 2,977 knots, vs (a) CUE spacing, (b) 500
random integer polynomials matched per-knot on degree and max-|coefficient|
(construction as in knot_root_gue_verify.py), 200 ensemble redraws for the null band.
Statistics: spacing variance and two-sample KS distance.

**Unit-of-inference discipline.** All primary p-values and SEs use n = N_q
(conductor-level), never n = 2,977 knots: knots sharing a determinant see the same
arithmetic partner, so knot-level n would inflate precision by the mean multiplicity
(~18x) — the SE-on-the-wrong-unit trap.

## Controls

1. **Magnitude/scale control:** density unfolding of z1 before any comparison
   (mean-spacing normalization first); log q in the covariate set; block permutation
   within magnitude deciles. Guards the known magnitude-compatibility tautology.
2. **Prime-atmosphere control:** ω(q) and 1_prime(q) in Z. Additionally report the
   correlation with and without these covariates; if |ρ_p| drops by more than 50%
   when they are added, classify any surviving signal as PRIME_ATMOSPHERE_ARTIFACT
   pending a dedicated follow-up (96%+ of prior cross-dataset structure was primes).
3. **Empty-array control (trap #8):** eligibility by array_length > 0; report the
   count 2,977 and the crossing range 3–12 in the verdict header.
4. **Negative control:** replace X with a structureless per-knot feature (parity of
   md5(name)), aggregate identically to X̄(q), run the identical pipeline. It must
   NOT pass the gate; if it does, the pipeline is broken and no verdict issues.
5. **Positive control:** raw z1 vs log q, threshold above.
6. **Selection-relation control:** the knot table is a complete tabulation for 3–12
   crossings (no selection), but `zeros.dirichlet_zeros` conductor coverage may be
   selective. Report coverage as a function of q on 1–377; if covered q differ from
   uncovered q in magnitude distribution (KS p < 0.01), reweight or restrict to the
   covered range and disclose — the null must be drawn exchangeably with the data.
7. **Multiplicity control:** recompute the primary test restricted to the 155 q with
   multiplicity ≥ 2 (where X̄(q) is a genuine population summary, not a single knot);
   sign and significance must agree with the full-N_q result or the verdict is
   downgraded to UNSTABLE.
8. **Ledger control:** raw per-q rows (q, X1, X2, Y, covariates, multiplicity) ship
   in the same commit as the verdict; permutation seed and count stamped.

## Preregistered falsifiers (each with an explicit numeric threshold)

- **F1 (coverage/reachability):** N_q < 120, or attainable |ρ_p| range excludes 0.20
  → verdict VACUOUS_COVERAGE (pre-committed vacuous reading; not a null result).
- **F2 (effect size):** max over the two Holm-corrected tests of |ρ_p| < 0.20
  → NO_COUPLING at the resolvable effect size; report the 95% CI beside the verdict.
- **F3 (permutation null):** block-permutation p ≥ 0.001 (one-sided in the observed
  direction, 10,000 permutations, seed 42) → NO_COUPLING.
- **F4 (replication):** split conductors into odd/even rank halves by q; if the two
  halves disagree in sign, or either half has permutation p ≥ 0.05, → NO_COUPLING
  (a full-sample pass with a failed split is reported as UNSTABLE, never as a pass).
- **F5 (prime atmosphere):** |ρ_p| with prime covariates < 0.5 × |ρ_p| without them
  → PRIME_ATMOSPHERE_ARTIFACT, not coupling.
- **F6 (negative control):** hash-feature control achieves p < 0.01 under the same
  pipeline → PIPELINE_INVALID, no science verdict.
- **F7 (positive control):** raw z1 vs log q gives |ρ| < 0.5 → INSTRUMENT_FAIL,
  no science verdict.
- **F8 (H2, knot-specific spectra):** claim knot-specific spectral structure only if
  the knot spacing variance lies outside the central 99.9% band of the 200 matched
  random-polynomial ensemble draws AND |var_knot − var_null_mean| > 0.02 AND
  KS D(knot, null) > 0.05 with ensemble p < 0.001. Otherwise verdict
  GENERIC_POLYNOMIAL (the expected outcome given the prior kill battery).
- **F9 (data integrity):** |Δ_K(−1)| vs determinant mismatch rate > 1% → DATA_AUDIT,
  run aborts before any coupling readout.

A positive coupling claim requires jointly: F1–F7 all passed in the non-falsifying
direction, i.e., |ρ_p| ≥ 0.20, p < 0.001, both split halves same-sign with p < 0.05,
prime-covariate attenuation < 50%, both controls behaving. Anything less is one of
the named verdicts above — the verdict ledger and the program-disposition ledger are
kept separate.

## Stopping rule

Single fixed-N pass on the frozen snapshot. Exactly 10,000 permutations (seed 42) and
200 ensemble redraws (seed 43); no data-dependent extension, no threshold movement
after unblinding (the X-2 failure mode: two passes spent moving a verdict across a
line closer than its own SE). Order of operations: preflight coverage inventory →
F9 integrity gate → F1 reachability gate → F7 positive control → F6 negative control
→ primary tests → F4 split → H2 arm. The run STOPS at the first failed gate in that
order and issues that gate's verdict; later stages are then not executed and not
reported as evidence in either direction. One verdict per arm, committed with rows;
any post-hoc exploration goes to a separate exploratory ledger and cannot amend the
preregistered verdict.

## Unit of inference

The distinct determinant/conductor value q (conductor-level): n = N_q ≤ 167, not
n = 2,977 knots. Knots sharing det = q are exchangeable copies with respect to the
arithmetic partner, so the knot level would inflate precision ~18-fold. For H2 the
unit is the pooled spacing distribution vs ensemble draw (n = 200 draws for the null
band); per-spacing counts are never used as n. All SEs, CIs, and permutation
p-values are computed at these units.

## Prior work bearing on this design (cite repo paths if any; 'none found' is acceptable)

- `aporia/catalog_attacks/ATTACK_MATH-0332_2026-08-19.md` — trap #8 (NOT-NULL empty
  Jones arrays; effective coverage 2,977 knots, crossings 3–12) and the KMT span law
  (span = c+1 iff alternating) surfacing as a database law. Both are load-bearing
  here: the eligibility filter and the X1 alternating read-off come from this file.
- `thesauros/proposals.md` — crossing_number repaired from name prefix; determinant
  populated 2,977/12,965; signature 0/12,965 (source gap → signature excluded).
- `thesauros/data_dictionary.md` — schemas for `topology.knots`,
  `zeros.dirichlet_zeros`, `zeros.object_zeros`, `lfunc_lfunctions`.
- `cartography/shared/scripts/knot_root_gue_verify.py` — prior GUE-at-var-0.180
  claim and its kill battery (matched random-coefficient null, shuffled-coefficient
  null, CUE comparison). H2 is a preregistered, thresholded replication of exactly
  this battery; its matched-null construction is reused verbatim.
- `cartography/shared/scripts/v2/knot_primes_starvation.py` (+ `_results.json`) —
  prior knot-vs-primes contact: p-adic starvation profiles of Alexander/Jones
  coefficients; motivates the prime-atmosphere covariates.
- `cartography/shared/scripts/v2/c37_knot_det_m4m2_results.json` — determinant moment
  ratio M4/M2² = 2.156, CI excluding SU(2)=2.0, labeled NOVEL_UNIVERSALITY_CLASS;
  a determinant-distribution fact this design conditions on rather than re-tests.
- `cartography/shared/scripts/m1_c41_knot_unit_circle.py` (+ v2 results) — Jones/
  Alexander unit-circle profiles; jones–alex profile correlation 0.716, crossing
  η² = 0.14 (invariants are far from independent — why only TWO confirmatory X's).
- `cartography/shared/scripts/v2/jones_alexander_independence.py` — Jones and
  Alexander recurrence structures independent (Fisher p = 0.98).
- `cartography/shared/scripts/v2/m20_knots_moment_space_results.json` — knots mapped
  into Sato-Tate moment space by cosine similarity: 78% pile into D_{3,2}; a
  cautionary example of similarity-without-null, the exact trap this design's
  permutation gates exist to avoid.
- `cartography/shared/scripts/v2/knot_bridge_expansion.py` (+ results) — determinant
  vs OEIS overlap scan; high-overlap hits with no null model; same caution.
- `evidence_wiki/docs/PREREGISTRATION_V1.md` — lists T5 and its known trap
  (correlation-without-null); this design's gates F2–F6 answer it.
