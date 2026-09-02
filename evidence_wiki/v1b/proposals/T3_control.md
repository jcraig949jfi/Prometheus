# PROPOSAL T3 (control)

Object-level coupling between elliptic-curve features and L-function features in the Prometheus data spine.
Author: Prometheus research designer (spec only; no execution in this pass).
Date: 2026-09-02. Status: PREREGISTERED SPECIFICATION — frozen before first data contact.

Data spine: LMFDB mirror in Postgres on M1 (`lmfdb` DB; `ec_curvedata` 3,824,372 rows; `lfunc_lfunctions`
24,351,376 rows; schema in `thesauros/postgres_lmfdb.md`; the EC↔L join exists as the materialized view
`bsd_joined`, 2,481,157 curve rows, built by `thesauros/create_bsd_joined.py`). The Harmonia cross-domain
feature tensor (`harmonia/memory/landscape_tensor.npz`, built by `harmonia/memory/build_landscape_tensor.py`)
is the destination for the verdict cell and supplies the existing distributional-coupling baseline this
design goes beyond.

## Hypothesis

H1 (object-level coupling): For an elliptic-curve isogeny class C over Q and its L-function L_C, the
*pairing itself* carries information — algebraic EC features of C predict analytic features of L_C better
than they predict the analytic features of a different L-function drawn from the same construction stratum
(same conductor band, same rank, same degree-2/motivic-weight-1 family). Formally: within strata defined by
(log-conductor ventile × rank class), the within-stratum association between the EC feature vector X(C) and
the L feature vector Y(L_C) exceeds its distribution under random re-pairing of X and Y within stratum.

H0 (construction-only coupling): All observable EC↔L association is induced by feature construction —
shared covariates (conductor is the dominant scale on both sides; rank enters both sides via the order of
vanishing), definitional/algebraic identities (BSD rearrangements, parity), and selection into the joined
universe. Under H0, within-stratum re-pairing leaves every association statistic unchanged.

Sharpening, forced by prior retractions (see Prior work): "beyond what feature construction alone induces"
means beyond (a) Pattern-30 algebraic identities between the two feature sets, (b) dependence mediated by
the stratifiers, and (c) join/selection artifacts. Theorem-predicted but genuinely pairing-specific effects
(e.g. explicit-formula dependence of low zeros on the curve's own a_p; Katz-Sarnak rank repulsion) COUNT as
object-level coupling under H1; they are attributed to known mathematics in the disposition, which is kept
in a separate ledger from the preregistered verdict.

## Design

### Population
- Universe: `bsd_joined` (isogeny-class-level join `lf.origin = 'EllipticCurve/Q/' || conductor || '/' || iso_letter`),
  restricted to conductor ≤ 400,000 (the L-function coverage boundary: 0% coverage above; 66–93% below —
  `thesauros/bsd_joined_view.md`). All claims are scoped to this joined universe, stated as such, because
  join coverage is conductor-correlated and cannot be treated as random.
- Deduplication: collapse to ONE row per isogeny class (the L-function is a class invariant; multiple EC
  rows join to one lfunc row). EC representative = the curve with LMFDB curve number 1 in the class.
  Prior lesson: failing to dedupe by class multiplied a twist census 373× (`aporia/docs/CYCLE_142F_NATIVE_VERBS_2026-08-23.md`).
- Pass 0 (inventory, before any statistic): enumerate the full eligible population — exact class count,
  per-stratum counts, per-feature NULL rates, coverage by conductor band. No analysis on a prefix or sample;
  the population is a census of eligible classes (expected order 1.0–1.5M classes; the exact number is a
  pass-0 measurement, not an assumption).
- Row-eligibility: z1, z2, z3 non-NULL; conductor, rank, and all X features non-NULL. Classes failing this
  are counted and reported by stratum (truncation direction must be discussed in the verdict: missing-zero
  rows are conductor-skewed and their exclusion direction relative to each gate is stated).

### Features
EC-side X(C) (7 features, class unit; all from `ec_curvedata` via `bsd_joined`):
- x1 torsion order (representative curve)
- x2 log2(class_size)
- x3 log2(class_deg)
- x4 num_bad_primes
- x5 semistable (0/1)
- x6 CM indicator (cm ≠ 0)
- x7 faltings_height (used only via within-stratum ranks; conductor dependence is absorbed by the stratifier —
  Pattern-30 note: h_F is linear in log|Δ|, which co-moves with log N; residual variation within a conductor
  ventile is what is being tested)

L-side Y(L_C) (3 features, from `lfunc_lfunctions` via `bsd_joined`):
- y1 unfolded first zero  ẑ1 = z1 · log(analytic_conductor) / (2π)   (fallback: log(conductor) if
  analytic_conductor NULL; the choice is made once, at pass 0, by NULL rate, and reported)
- y2 unfolded gap ẑ2 − ẑ1
- y3 unfolded gap ẑ3 − ẑ2
Mean-spacing unfolding is applied BEFORE any statistic (scale-vs-shape doctrine); a raw-z1 run is kept as a
diagnostic only, to display the size and direction of the conductor artifact the unfolding removes.

Excluded from the confirmatory family, by Pattern-30 algebraic screen (each exclusion documented by writing
the statistic in atomic observables {L, Ω, Reg, ∏c_p, Sha, Tor, log N, log|Δ|}):
- rank / analytic_rank vs any order-of-vanishing or zero feature — rank is in the STRATIFIER; the rank↔z1
  channel is the positive control, not a discovery claim.
- leading_term vs anything algebraic — leading_term = Ω·Reg·∏c_p·|Sha|/Tor² (BSD, proven at rank ≤ 1), so
  torsion, bad primes, and regulator all appear in it definitionally (F043/H40/H83 failure mode). Exploratory
  annex only, clearly labeled non-confirmatory.
- root_number / sign_arg — parity-coupled to rank (a theorem), and constant within rank strata.
- sha at rank ≥ 2 — LMFDB computes it assuming BSD (circularity warning in `thesauros/bsd_joined_view.md`); excluded everywhere.

### Strata
S = (log-conductor ventile: 20 equal-count bins over eligible classes) × (rank class: 0, 1, ≥2) → ≤ 60 strata.
Preregistered merge rule: any stratum with n < 200 is merged into its conductor-adjacent neighbor of the same
rank class before analysis; final strata frozen at pass 0 and published with the verdict.

### Statistics
Primary (multivariate, one number): T_global = Σ_s (n_s/N) · dCor_s(X, Y), the class-count-weighted mean
within-stratum distance correlation between the 7-dim X and 3-dim Y (features rank-transformed within
stratum first).
Secondary (confirmatory family, m = 21): Spearman ρ_jk between each (x_j, y_k) pair, computed within stratum
and combined across strata by inverse-variance weighting into one z per pair; Holm correction over the 21 pairs.

### Null model
Within-stratum permutation of the pairing: hold every X row and every Y row fixed, permute the C ↔ L_C
assignment uniformly WITHIN each stratum, recompute T_global and all 21 pair statistics. This is the
NULL_BSWCD member of the Harmonia null family (preserves the stratifier's marginals; tests within-stratum
pairing) and it perturbs exactly the axis the statistic varies on — the pairing — while breaking the
selection relation nothing else can break. B = 2,000 permutations; z = (T_obs − mean(T_null)) / sd(T_null);
empirical p alongside. NULL_PLAIN (unstratified permutation) is also run; per Pattern 21, PLAIN-fires-but-
BSWCD-doesn't is recorded as between-stratum drift and is NOT object-level coupling.
Seeds: {11, 13, 17, 19, 23} — the full pipeline (including permutations) runs under 5 seeds; all 5 verdict
statistics are reported, none averaged away.

### Reporting
Verdict, per-stratum ledgers (n_s, dCor_s, all pair ρ's, null means/SDs), the Pattern-30 screen table, and
the raw per-class extract hash ship in the SAME commit as the verdict (a verdict without rows is an
assertion). Effect sizes and CIs are reported beside every z. The preregistered verdict ledger and the
program-disposition ledger (theorem attribution, follow-ups) are separate files.

## Controls

C1 — Signature-exists positive control (run FIRST, before any negative control is interpreted): with
conductor-only strata (rank NOT in the stratifier), the rank ↔ ẑ1 association must fire strongly (rank ≥ 1
forces zeros at the center; Katz-Sarnak repulsion of ẑ1 is established in this very corpus — F011 line).
If the instrument cannot see this known object-level signal, every other reading is VACUOUS by
preregistration; no verdict on H1 is issued.

C2 — Instrument calibration / gate reachability (before data contact): inject a synthetic within-stratum
coupling of Spearman ρ = 0.02 between one x and one y on the real marginals (permute, then re-sort a 2%
sub-block); the pipeline must recover it with power ≥ 0.9 at the Holm-adjusted per-pair α = 0.05/21. This
proves the effect floor and the significance gate are simultaneously reachable on this N and B (a gate that
cannot fire on any input reads as a fake null).

C3 — Matched-impostor negative control (independent implementation check on the null): assign each class the
L-function of a different class from the same stratum via a fixed derangement; the full statistic suite on
this impostor pairing must be null. Because the impostor is one draw from the permutation null, a firing
here means a code/join defect (e.g. leakage of the true pairing through an unstratified covariate), not
structure.

C4 — Pattern-30 algebraic screen (per feature pair, before analysis): each of the 21 confirmatory pairs is
written in atomic observables; any pair where one side appears as a term or factor of the other is excluded
(the "control-for variable chosen by algebraic decomposition, not visible regressors" rule from
`harmonia/memory/algebraic_coupling_audit.md`). The screen table is published with the spec, frozen.

C5 — Unfolding control: the confirmatory suite runs on unfolded zeros only; the raw-z1 diagnostic run
quantifies how much association the conductor scale alone would have manufactured, with its direction
relative to each gate stated.

C6 — Multiplicity and unit: Holm over m = 21 pairs; all SEs and permutation resampling at the isogeny-class
unit (never curve rows — n inflation across class members is the known 57×-class error mode).

C7 — Selection scoping: coverage by conductor band is reported; no claim extends past the joined,
conductor ≤ 400K universe.

## Preregistered falsifiers (each with an explicit numeric threshold)

FAL-1 (vacuity): If the C1 positive control yields z < 5 for rank ↔ ẑ1 under conductor-only strata, the
instrument is declared VACUOUS. Terminal verdict "VACUOUS — no reading on H1", preregistered here as the
required outcome of that branch. (Expected value under a working instrument: z ≫ 10.)

FAL-2 (unreachable gate): If C2 synthetic power < 0.9 for planted ρ = 0.02 at α = 0.05/21 with B = 2,000,
the design is declared unable to fire; redesign required before any data contact. Any null obtained with an
unreachable gate is void.

FAL-3 (leaky null): If the C3 impostor pairing gives |z| ≥ 3 on T_global or on any confirmatory pair, the
pipeline is declared defective; any positive H1 reading from the same code is void until the leak is found
and the pass counter restarts.

FAL-4 (primary falsifier of H1): H1 is FALSIFIED for this feature set and population if BOTH
  (a) T_global z < 3 against the within-stratum permutation null, AND
  (b) no (x_j, y_k) pair survives Holm at family α = 0.05 with within-stratum |ρ| ≥ 0.02.
Verdict: "NO OBJECT-LEVEL COUPLING BEYOND CONSTRUCTION at effect floor 0.02 / dCor floor 0.005" —
explicitly scoped to the 7×3 feature menu, not to the objects (the 141-E/142-F lesson: nulls can be
vocabulary artifacts; the scope sentence is mandatory).

FAL-5 (effect floor): A pair with Holm-passing z ≥ 3 but within-stratum |ρ| < 0.02, or T_global z ≥ 3 with
weighted dCor < 0.005, is verdicted "SUB-FLOOR RESIDUE", not coupling. (At N ~ 10^6 classes, |ρ| ≈ 0.003
already gives z ≈ 3; significance without the floor is not a finding.)

FAL-6 (discordance): If NULL_PLAIN gives z ≥ 3 while NULL_BSWCD gives z < 3 on the same statistic, the
signal is classified BETWEEN-STRATUM DRIFT (construction-induced); H1 is NOT supported by that statistic.

FAL-7 (seed instability): If across the 5 seeds any verdict-bearing z flips sign, or max|z|/min|z| > 10,
the result is NOT PROMOTABLE regardless of magnitude; verdict "UNSTABLE — no reading".

Confirmation criterion (for symmetry, also preregistered): H1 is SUPPORTED only if T_global z ≥ 3 with
weighted dCor ≥ 0.005 under NULL_BSWCD, stable across all 5 seeds, with FAL-1/2/3 all passed; per-pair
claims additionally need Holm-passing z ≥ 3 with |ρ| ≥ 0.02.

## Stopping rule

- Pass 0 (inventory) → C2 calibration → C1 positive control → C3 impostor → single confirmatory pass on the
  frozen population, features, strata, thresholds. No feature, stratum, unfolding, or threshold change after
  first contact with real pairing data.
- B = 2,000 permutations per statistic per seed. One preregistered escalation only: if an empirical p lies
  within 2 Monte-Carlo SEs of its decision threshold, B for that statistic rises to 10,000, once. No other
  reason to rerun.
- A discovered pipeline bug voids the pass and restarts the counter; maximum 3 passes total, then the
  terminal verdict is whatever the last valid pass produced (including VACUOUS/UNSTABLE). Kill/verdict
  outcomes are never grounds for another pass by themselves.
- No optional stopping on N: the population is the full eligible census, fixed at pass 0.
- The verdict commit contains: verdict, all ledgers and null draws' summary stats, the frozen spec hash, and
  the extract manifest — same commit, tracked.

## Unit of inference

The isogeny class over Q (equivalently: one degree-2 L-function). The L-function is an invariant of the
class, and `bsd_joined` maps many curve rows to one lfunc row, so the exchangeable unit under H0's
re-pairing null is the class. All n's, SEs, permutations, and power computations use class counts
(pass-0-measured; order 10^6 in the joined, conductor ≤ 400K universe), never the 2.48M curve rows and never
the 3.8M-row curve table. Strata are computation blocks, not inference units; per-stratum statistics are
combined by class-count weights. Scope of any conclusion: joined universe only.

## Prior work bearing on this design (cite repo paths if any; 'none found' is acceptable)

- `harmonia/memory/algebraic_coupling_audit.md` — Pattern 30 and the three COUPLED retractions (F043 rank-0
  log Sha vs log A = BSD rearrangement; H40 Szpiro vs Faltings via shared log|Δ|; H83 class-number × regulator
  = Dirichlet CNF). This audit is the reason "beyond feature construction" is operationalized as the C4
  algebraic screen plus within-stratum re-pairing, and the reason leading_term/root_number/sha are excluded.
- `thesauros/bsd_joined_view.md`, `thesauros/create_bsd_joined.py`, `thesauros/postgres_lmfdb.md` — the
  EC↔L join (class-level origin key), coverage cliff at conductor 400K, rank-stratified row counts, the
  Sha-at-rank≥2 circularity warning, and available columns (z1/z2/z3, leading_term, root_number present;
  Omega and Tamagawa absent).
- `harmonia/memory/null_family_catalog.md` and `harmonia/wsw_F011*.py`, `harmonia/F041a_conductor_control.py`,
  `harmonia/F011_independent_unfolding_check.py` — the null family (NULL_PLAIN vs NULL_BSWCD discordance =
  Pattern 21), conductor as the dominant EC–L confound, and the established rank ↔ first-zero signal (F011
  line) reused here as the C1 positive control rather than re-claimed as a finding.
- `aporia/docs/identity_join_strategy_spec.md` — the identity-vs-distributional coupling distinction: the
  Harmonia tensor's distributional scorer is deaf to pairing; this proposal is precisely a pairing-level
  (identity-keyed) test, the calibration philosophy (run on known bridges first) is inherited as C1.
- `aporia/docs/CYCLE_142F_NATIVE_VERBS_2026-08-23.md` and `aporia/docs/CYCLE_140D_LMFDB_OPERATORS_2026-08-23.md` —
  isogeny-class deduplication (a 373× count inflation caught only at dedup) and the vocabulary-scoping lesson
  used in FAL-4's mandatory scope sentence.
- `harmonia/memory/build_landscape_tensor.py`, `harmonia/memory/landscape_tensor.npz` — the cross-domain
  feature tensor this verdict feeds (one cell, with its invariance vector across the null family).
