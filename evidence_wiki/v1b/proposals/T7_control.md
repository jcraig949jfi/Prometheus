# PROPOSAL T7 (control)

Task: extend the Prometheus BSD verification program to elliptic curves of rank >= 2,
on the local LMFDB mirror (lmfdb Postgres on M1: `ec_curvedata` 3.8M rows,
`lfunc_lfunctions` 24M rows, `bsd_joined` materialized view, 2,481,157 rows).
Author: T7 control arm. Date: 2026-09-02.

## Hypothesis

**H1 (primary).** For rank >= 2 elliptic curves over Q in the mirror's covered range
(conductor <= ~400K), the *unrounded* BSD quotient

    Q(E) = ( L^(r)(E,1) / r! ) * |Tor(E)|^2 / ( Omega(E) * Reg(E) * Tam(E) )

computed entirely from BSD-independent ingredients — `leading_term` (analytic, from the
L-function side), `regulator` and `torsion` (algebraic, from descent/Mordell-Weil), and
Omega (real period) and Tam (Tamagawa product) **computed by us from `ainvs`** — is,
within a precision tolerance frozen at calibration time, (a) a positive integer, and
(b) a perfect square (Cassels: if Sha(E) is finite its order is a square).

**H0 (null).** Q(E) is not constrained to near-integer / near-square values beyond what
a pairing-broken null produces; i.e., the apparent structure is conditioning, precision
artifact, or circular data provenance.

**Sha circularity — named up front, and how this design escapes it.** The mirror's
`sha` column at rank >= 2 is *defined* as round(Q(E)) computed by LMFDB **assuming the
full BSD formula** (documented in `thesauros/bsd_joined_view.md` line 40 and
`thesauros/unified_data_plan.md` known-issue #2; Mnemosyne circularity catch,
2026-04-15). It is not ground truth at rank >= 2, and the prior repo-wide "Sha is a
perfect square: 100.0000%" result (`harmonia/docs/millennium_prize_tests.md`, Test 2)
is at rank >= 2 a test of LMFDB's *rounding step*, not of BSD — the stored integer was
produced by assuming BSD and rounding, so its squareness partially inherits the
assumption. This proposal therefore:
1. **Never uses the `sha` column as ground truth at rank >= 2.** It appears in rank >= 2
   analysis only as a descriptive cross-check, explicitly labeled non-evidential
   (agreement is expected by construction: LMFDB ran the same formula).
2. **Moves the evidential weight to the unrounded quotient.** What LMFDB's pipeline
   cannot guarantee by construction is that Q(E) computed from independent ingredients
   lands *near* an integer at all, and near a *square* integer. That closeness is a
   genuine, falsifiable prediction of BSD (integrality of the conjectural #Sha), and it
   is measured here against an explicit precision budget and a pairing-permutation null.
3. **Calibrates only where Sha is independent.** Rank 0/1 (BSD proven — Kolyvagin,
   Gross-Zagier; `sha` there is independent ground truth per `bsd_joined_view.md` rank
   table) is used to validate our Omega/Tamagawa instrument and to freeze tolerances,
   BEFORE any rank >= 2 number is examined.

What this experiment can and cannot claim: a pass is *large-scale numerical consistency
of the rank >= 2 BSD formula on the mirror's stored data* — a characterization of the
data plus a survived falsification attempt, never a proof; a resolved violation would
be a major data-or-conjecture anomaly (adjudication protocol below). Scope discipline
follows `aporia/catalog_attacks/ATTACK_CAT-MATH-0348_2026-08-21.md`.

## Design

**BSD ingredients and their provenance (per curve E, minimal model from `ainvs`):**
- `leading_term` = L^(r)(E,1)/r! — from `lfunc_lfunctions` via `bsd_joined`; analytic
  side, computed by LMFDB from the L-function independently of BSD. Pulled from the
  base table's TEXT column (not the view's DOUBLE cast) to keep every stored digit.
- `rank` r, `regulator`, `torsion` — algebraic side (`ec_curvedata`), from descent and
  explicit Mordell-Weil generators; independent of BSD. Caveats logged as assumptions:
  (i) some rank >= 2 upper bounds in LMFDB may be conditional (GRH/analytic input);
  (ii) an unsaturated generator set inflates the regulator by an integer index squared.
  Both are adjudication items for individual violators, not silent trust.
- Omega(E) — NOT in the mirror (`bsd_joined_view.md` "Missing Data"). Computed by us:
  fundamental real period of the minimal model via AGM (mpmath, 30 working digits),
  times 2 when disc > 0 (`signD` column gives the component count). New operation in
  `prometheus_math`, forged under the math-tdd discipline with authority tests against
  the rank 0/1 calibration stratum.
- Tam(E) = prod_p c_p — NOT in the mirror. Computed by us: Tate's algorithm on the
  minimal model at each prime in `bad_primes` (exact integer arithmetic; no factoring
  needed — `bad_primes` is stored). Same math-tdd forging.
- Convention check (Phase 0): the exact stored normalization of `leading_term`
  (L^(r)/r! vs L^(r); arithmetic vs analytic normalization) is *determined empirically
  on rank <= 1*, where the full formula is proven and `sha` is independent: the
  convention is whichever makes round(Q) == sha on the calibration stratum. Frozen
  after Phase 0, before any rank >= 2 fetch.

**Strata (enumerated by preflight census BEFORE sampling — inventory first, no
prefix/window sampling):**
- Rank 2: ~275,644 curve rows in `bsd_joined`; class count from preflight
  `SELECT count(DISTINCT ec_iso) ... WHERE rank = 2`. Analysis sample: full census if
  the preflight cost probe (100 classes) extrapolates to <= 72h; otherwise a
  preregistered stratified sample of 20,000 isogeny classes, allocated proportionally
  across conductor decade bands, selected deterministically (ORDER BY ec_iso within
  band, evenly spaced offsets — no TABLESAMPLE; synchronized-scan nondeterminism is a
  known mirror hazard, 0348 doctrine).
- Rank 3: exhaustive — all classes among the 6,728 curve rows.
- Rank 4: exactly 1 curve in the view — computed and *reported descriptively only*
  (n=1 supports no inference). Rank 5: absent from the view (all above the 400K
  conductor lfunc-coverage cutoff); explicitly out of scope.
- Calibration stratum (Phase 0): 2,000 classes, 1,000 each rank 0 and rank 1,
  stratified by conductor decade, deterministic selection as above.
- Substrata reported throughout: conductor decade band, CM vs non-CM, semistable vs
  not, torsion trivial vs not, class_size 1 vs > 1.

**Row hygiene (mirror-specific, inherited from prior audits):** all fetches
`DISTINCT ON` the relevant label (degree-1 lfunc rows are provably not label-unique —
0348 P73 instrument finding; the same guard is applied and *checked* here for
`bsd_joined`); the isogeny-class join means curves in one class share one
`leading_term`, so per-curve rows within a class are never treated as independent.

**Procedure:**
1. **Preflight census** (recorded before any statistic): class and curve counts per
   rank stratum; NULL rates of `leading_term`, `regulator`, `torsion` per stratum;
   stored-precision census of `leading_term` and `regulator` (significant digits in the
   TEXT fields); conductor histograms; per-class compute-cost probe. Any stratum whose
   usable-row count collapses (e.g. NULL regulator) is reported as VACUOUS, not
   silently dropped.
2. **Phase 0 — instrument calibration (rank 0/1 only).** Compute Q on the calibration
   stratum. Gates: F0 below. Output: (a) validated Omega/Tam code, (b) frozen
   leading-term convention, (c) frozen integrality tolerance tol(E) — set from the
   *observed* |Q − sha| error distribution (e.g. 99.9th percentile times a safety
   factor of 5, floored at 0.01 absolute and Q·1e-6 relative), so the gate line is
   chosen from measured error, before Phase 1, never after seeing rank >= 2 results.
   The measurement-error requirement is explicit: if the attainable tolerance exceeds
   0.5 (stored digits cannot separate adjacent integers), the rank >= 2 test is
   declared TEST_INFEASIBLE and stops — a gate must be reachable and must exceed
   measurement error.
3. **Phase 1 — rank >= 2 measurement.** Per class: compute Q for every curve in the
   class (each curve has its own Omega, Reg, Tor, Tam; `leading_term` is shared). A
   class PASSES integrality iff every curve's Q is within tol of a positive integer;
   PASSES squareness iff every rounded Q is a perfect square. Full per-curve arrays
   (Q, tol, ingredients) committed with the verdict in the same commit — rows ship
   with verdicts.
4. **Statistics.** Per stratum: pass rates with Wilson 95% CIs on the *class* count;
   distribution of d(E) = |Q − nint(Q)|; KS distance between observed d and the
   permutation-null d; per-conductor-band consistency (P78-style strata check).
5. **Violator adjudication protocol (asymmetric null discipline).** A failed curve is
   a claim about the instrument until resolved: each violator gets a dossier —
   recompute Omega/Tam at 60 digits; re-parse stored fields; check the known coverage/
   duplication defects; test the "regulator off by an integer square factor"
   saturation hypothesis (is Q·k^2 integral for small k?); check rank-provenance
   conditionality. Only unresolved violators count against F1/F2/F6. Both counts
   (raw and adjudicated) are reported.

## Controls

- **C1 — pairing-permutation null (breaks the object-level relation, preserves
  marginals).** Within each (rank, conductor-decade) cell, permute `leading_term`
  across isogeny classes (1,000 seeded permutations, seed 20260902) and recompute the
  integrality/squareness pass rates. This is the chance floor: it preserves both
  marginal distributions and the selection relation's strata while destroying only the
  curve↔L-value pairing. (A control drawn from the treatment's selection relation is
  the treatment — hence permutation within cells, not a resampled cohort.)
- **C2 — negative-control (mis-specified formula) sensitivity.** On the Phase 0
  calibration stratum, rerun the pipeline with (a) Tam omitted, (b) |Tor|^1 instead of
  |Tor|^2, (c) Omega without the disc>0 component factor. Each must collapse the pass
  rate (threshold in F4); otherwise the statistic cannot detect a wrong formula and a
  rank >= 2 "pass" would be vacuous.
- **C3 — precision control.** Recompute Omega/Tam for a 500-class subsample at 60
  digits; require max |ΔQ| below tol/10. Guards against the computed ingredients, the
  one part of the pipeline we introduce, dominating the error budget.
- **C4 — trivial-integrality control.** Because Sha = 1 dominates (prior mirror
  measurement: at rank >= 2 the stored analytic Sha is ~always 1), Q ≈ 1 and "near an
  integer" could be cheap if Q were loosely distributed around 1. C1 quantifies
  exactly this: the null pass rate at the same tol is the price of that objection.
  Additionally the d(E) distribution is reported on log scale — a genuine integrality
  signal concentrates at d ~ measurement error (<= 1e-4-ish), not merely d < tol.
- **C5 — coverage/selection confound, direction stated.** `bsd_joined` coverage falls
  from 93% (<1K) to 0% (>400K); high-conductor mirror rows are biased toward prime
  conductor and trivial torsion, and an adjudicated audit
  (`cartography/docs/audit_F044_rank4_lmfdb_selection_results.md`) showed the LMFDB
  rank >= 2 population at conductor >= 1e8 is a selection-frame artifact (essentially
  100% single-bad-prime semistable, consistent with rank-record-construction
  sourcing) — one reason the high-rank strata here are reported per band and never
  extrapolated to "elliptic curves in general". Missing L-values cannot fabricate integrality (no
  `leading_term`, no Q — those classes are excluded, not imputed), but all claims are
  scoped to the covered strata and reported per band; the confound's push direction
  relative to each gate is stated in the verdict.
- **C6 — circular-column quarantine.** The `sha` column at rank >= 2 appears nowhere
  in any gate. The descriptive round(Q)-vs-sha agreement table is emitted in a
  separate, labeled NON-EVIDENTIAL section of the results file.

## Preregistered falsifiers (each with an explicit numeric threshold)

- **F0 (instrument, Phase 0 gate).** On the 2,000-class rank 0/1 calibration stratum:
  round(Q) == independent `sha` AND |Q − round(Q)| <= 0.01 for >= 99.5% of classes.
  Below 99.5% ⇒ **INSTRUMENT_FAIL**: the Omega/Tam pipeline or convention is wrong;
  Phase 1 does not run. (Falsifies the instrument, not BSD.)
- **F1 (integrality at rank 2).** Adjudicated class-level integrality pass rate
  >= 0.99 ⇒ consistent. Pass rate < 0.95 (Wilson 95% CI upper bound < 0.99) after the
  violator-adjudication protocol ⇒ **H1a falsified on the mirror**:
  RANK2_QUOTIENT_NOT_INTEGRAL, escalated as a data-anomaly/conjecture-anomaly finding
  with the full violator dossiers. Rates in [0.95, 0.99) ⇒ MARGINAL, no consistency
  claim.
- **F2 (squareness at rank 2).** Among integrality-passing classes, perfect-square
  rate >= 0.99; < 0.95 ⇒ **H1b falsified** (CASSELS_SQUARE_FAIL), same escalation.
- **F3 (discrimination / gate reachability).** The C1 permutation-null mean pass rate
  at the frozen tol must be <= 0.10, and the observed rate must exceed the null 97.5th
  percentile. If the null mean pass rate > 0.5 × observed pass rate ⇒ **TEST_VACUOUS**
  — the statistic cannot distinguish BSD structure from chance at this precision, and
  no consistency claim is made regardless of F1/F2.
- **F4 (sensitivity).** Every C2 mis-specified formula must drop the Phase 0 pass rate
  by >= 30 percentage points. Any variant dropping < 30pp ⇒ **TEST_INSENSITIVE** for
  the corresponding ingredient; that ingredient's contribution is excluded from claims.
- **F5 (strata consistency).** No conductor decade band with >= 500 classes may show
  an adjudicated violation rate > 3% while the pooled rate passes F1; otherwise the
  verdict is BAND_INCONSISTENT and the pooled pass is not claimed (P78 discipline).
- **F6 (rank 3, exhaustive).** Adjudicated integrality pass rate >= 0.99 over all
  rank-3 classes; each violator individually dossiered. < 0.95 ⇒ falsified as in F1.
- **F7 (precision stability).** C3 max |ΔQ| between 30- and 60-digit recomputation
  <= tol/10 on all 500 probe classes; any breach ⇒ the affected stratum's verdict is
  withheld pending a full high-precision rerun (budget permitting) or reported
  PRECISION_LIMITED.

## Stopping rule

Fixed-sequence, no optional stopping, thresholds frozen at commit of this file:
1. **Preflight census** runs first; if the rank-2 usable class count < 5,000 or the
   rank-3 usable class count < 500 (NULL ingredients), the affected stratum is
   declared VACUOUS and the design halts for re-scoping — no threshold surfing.
2. **Phase 0 gate:** INSTRUMENT_FAIL (F0) or TEST_INFEASIBLE (attainable tolerance
   > 0.5) ⇒ hard stop; report; no rank >= 2 data is fetched or examined.
3. **Phase 1** runs to the preregistered sample sizes (full census or 20,000-class
   sample per the preflight cost probe; exhaustive rank 3) and then stops. No
   early peeking; no sample extension after results are seen.
4. **Budget cap:** 72h wall clock for Phase 1 compute. If exceeded, fall back to the
   preregistered reduced sample (2,000 rank-2 classes, same deterministic selection),
   disclosed as reduced-power.
5. Adjudication of violators is bounded: 60-digit recompute plus the four listed
   checks per dossier, once; no iterative "retry until it passes".

## Unit of inference

The **isogeny class** (`ec_iso`), not the curve row. All curves in a class share one
L-function and one `leading_term` (isogeny-level join, `bsd_joined_view.md`), so
per-curve rows are correlated by construction; n for every SE, CI, and threshold above
is the class count (SE on the wrong unit inflated precision 57x in a prior audit —
not repeated here). Within a class, per-curve Q values are combined by the
all-curves-pass rule, which is also a free bonus test (BSD must hold for every curve
in the class simultaneously, a stronger joint constraint). Verdicts are per
(rank-stratum × conductor band), pooled only when F5 passes.

## Prior work bearing on this design (cite repo paths if any; 'none found' is acceptable)

- `thesauros/bsd_joined_view.md` — the view's schema, coverage cliff at conductor
  400K, rank×count table, the explicit **Sha-circularity warning at rank >= 2**, and
  the "Missing Data" note that Omega and Tamagawa are absent (this design computes
  them). The example "BSD Phase 2 Calibration" query stub is the unexecuted seed this
  proposal turns into an experiment.
- `thesauros/unified_data_plan.md`, `thesauros/data_dictionary.md` — all-TEXT column
  hazard (casts), `ainvs` availability, high-conductor selection bias (prime
  conductor / trivial torsion), isogeny-level join caveat, index inventory.
- `harmonia/docs/millennium_prize_tests.md` — prior BSD program results this design
  **supersedes in part**: Test 1 (rank == analytic_rank, 100% over 3.82M curves) is
  already adjudicated and is deliberately NOT re-proposed as primary; Test 2 ("Sha is
  a perfect square", 100% over 3.06M) consumed the stored `sha` column, which at
  rank >= 2 is the rounded BSD-assuming quotient — this proposal replaces it there
  with the unrounded independent-ingredient quotient. Also documents that stored
  analytic Sha ~= 1 for essentially all rank >= 2 rows (motivates control C4).
- `charon/scripts/bsd_phase2_unblock.py` (2026-04-15) — the direct predecessor: a
  stratified BSD-ratio==1 test (100/100/50/20 classes per rank 0-3) that pulled
  real_period, tamagawa_product, and `sha_an` from the REMOTE devmirror `ec_mwbsd`
  table. **Superseded here on two counts:** (a) it placed `sha_an` in the denominator
  at rank >= 2, where sha_an is defined by assuming the very ratio being tested — the
  ratio==1 outcome is tautological there; this design removes Sha from the formula and
  tests integrality/squareness of the residual quotient instead; (b) it depended on a
  live remote mirror for Omega/Tam, which this design computes locally from `ainvs`.
  Its docstring's convention claim ("leading_term is already L^(r)(1)/r!") is treated
  as a hypothesis and verified empirically in Phase 0, not inherited.
- `harmonia/scripts/test_bsd.py` — the script of record behind
  `harmonia/docs/millennium_prize_tests.md` (tests 1-6, including refined-formula
  verification "on curves with known Sha"); its rank <= 1 machinery is the template
  for the Phase 0 calibration stratum, while its rank >= 2 use of stored Sha is what
  the primary endpoint here replaces.
- `cartography/docs/audit_F044_rank4_lmfdb_selection_results.md` (+ companion
  frame-based-resample audit) — RETRACTED F044 as a Pattern-4 selection-frame
  artifact: all LMFDB rank 4-5 curves (and rank 2-3 at conductor >= 1e8) are
  single-bad-prime semistable by construction of the source lists. Directly motivates
  control C5's scoping and the decision to treat rank 4 as descriptive-only.
- `harmonia/bsd_sha_paradox.py` — precedent for inverting the BSD formula against
  mirror columns and for catching a conditioning tautology (BSD_TAUTOLOGY_NO_PARADOX
  branch); its inversion A = L·Tor²/Sha is the rank-0 special case of Q.
- `aporia/catalog_attacks/ATTACK_CAT-MATH-0348_2026-08-21.md` (+ attack_0348_*.py) —
  mirror fetch doctrine reused wholesale: deterministic ORDER BY fetches (no
  TABLESAMPLE), `DISTINCT ON` label dedup (duplicate-row instrument finding),
  stratum-level cardinality checks, pre-stated readings, disjoint-slice replication,
  conductor-band strata consistency, commit-before-run.
- `prometheus_math/bsd_rank_env.py`, `prometheus_math/bsd_rich_env.py` — existing BSD
  rank-prediction environments (different question: learnability of rank, not formula
  verification); shows the corpus loader plumbing this pipeline can reuse.
- `aporia/docs/deep_research_batch6/report_116_bsd_tamagawa_calibration.md`,
  `aporia/docs/deep_research_batch7/report_126_sha_analytic_order.md` — background
  research reports on Tamagawa calibration and analytic Sha (Tier-2 anchors only;
  no numeric claim above depends on them).
- `harmonia/docs/millennium_prize_tests.md` Test 5 / `scripts/tick2_seed.py`,
  `scripts/tick4_responses.py`, `scripts/tick10_seed.py` — adjacent bsd_joined
  consumers (Goldfeld deviation, Szpiro stratification, symmetry-type splits);
  no overlap with the primary question here.
