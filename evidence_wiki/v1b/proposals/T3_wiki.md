# PROPOSAL T3 (wiki)

## Hypothesis

H1 (tested): After conditioning on the shared analytic backbone — log conductor, order of
vanishing, and root number — elliptic-curve arithmetic features (torsion order, isogeny-class
degree and size, log Tamagawa product, log regulator, analytic Sha, semistability, bad-prime
count) carry residual predictive information about fine L-function zero features (unfolded
low-zero heights, low-zero gap shape) of the SAME object, i.e. the signal dies when object
identity is destroyed by within-stratum permutation but marginals and conditioning are preserved.

H0 (default, favored by prior evidence C-8f20c74fa0cf, C-1f1a743fce1b, C-9334502f16d1): all
apparent EC–L coupling in the spine is (a) induced by feature construction / shared primitives
(conductor, discriminant, rank), or (b) distributional geometry that survives object permutation
— i.e. not object-level.

Scope: this is an object-level pairing question on the LMFDB mirror, not a theorem about
elliptic curves. It also fills the open Evidence Wiki gap H-bac36ae694a2 (mechanism =
projection_equivalence on substrate_class = lmfdb_arithmetic).

## Design

Population and join (enumerate BEFORE sampling — inventory is a preregistered deliverable):
- Postgres `lmfdb` on M1 (localhost:5432). Join at the ISOGENY-CLASS level:
  `lfunc_lfunctions l ON l.origin = 'EllipticCurve/Q/' || REPLACE(e.lmfdb_iso,'.','/')`
  from `ec_curvedata e`. NEVER join via `object_id` / xref registry: C-948eae5cb70c documents
  1,984,167 / 2,009,089 EC rows with NULL object_id from the 2026-04-16 load; `lmfdb_label` /
  `lmfdb_iso` are intact on every row and are the identity keys.
- Eligibility: `l.positive_zeros IS NOT NULL` with >= 10 stored positive zeros; representative
  curve = the class's optimal curve (`lmfdb_label = lmfdb_iso || '1'`), preregistered.
- Step 0 inventory query (runs first, committed before any statistic): count of joined classes
  broken down by conductor decade x order_of_vanishing x root_number, plus zeros-per-row
  distribution. No prefix/alphabetical sampling; if compute-bound, stratified sample of
  N = 200,000 classes proportional to the (conductor-decade x rank) inventory, seeded.
- Step 0b preflight data audit (pilot, 100 known rank>=2 classes): determine whether
  `positive_zeros` includes central zeros (gamma = 0) for vanishing-order > 0. Y-features are
  defined on the first zero with gamma > 1e-6 accordingly. Verdict blocked until this is recorded.

Variables (one row per isogeny class):
- Conditioning set Z: log(conductor), order_of_vanishing, root_number. (Degree = 2 and
  self_dual = true are constants on this population.)
- EC-side X (8 features, frozen): torsion order; class_deg; class_size; log(Tamagawa product);
  log(regulator) (rank > 0 rows only, else imputed 0 + indicator); sha_an; semistable (0/1);
  number of bad primes. Algebraic-forcing pre-screen (see Controls) may strike pairs, never add.
- L-side Y (4 statistics, frozen): y1 = unfolded first noncentral zero gamma_1*log(N)/(2*pi);
  y2 = mean of first 9 unfolded gaps; y3 = variance of first 9 unfolded gaps;
  y4 = normalized second moment of the first 10 unfolded zeros.
- Explicitly EXCLUDED from X: rank, and any feature definitionally shared with the L-row
  (order_of_vanishing, root/sign, conductor itself). Rank vs order_of_vanishing is a known
  deterministic identity in this mirror (C-954b8ae3b448: 3,824,372/3,824,372 agreement) — it is
  the positive control, not a discovery target.

Statistics (both estimators, both preregistered):
- S1 predictive skill: out-of-fold Delta-R^2 = R^2(Z + X) - R^2(Z) for each Y, gradient-boosted
  trees with frozen hyperparameters (depth 4, 300 trees, lr 0.05), 5 seeds (replicate-seeds
  doctrine), cross-validation BLOCKED on conductor decade (train/test never share a decade band)
  so conductor structure cannot leak across folds.
- S2 residual dependence: distance correlation dCor(X_res, Y_res) after residualizing both sides
  on Z within (rank x root_number) strata using quantile-binned log-conductor (20 bins).
- Primary endpoint: the 4 omnibus tests (all-X joint Delta-R^2, one per Y), Holm-corrected at
  alpha = 0.01. The 8x4 per-feature grid is secondary/descriptive only.
- Analysis script written, hashed (sha256), and committed BEFORE the first true pairing is read;
  permutation and negative-control arms run from the same script.

Harmonia tensor comparison arm (secondary, characterization only): repeat S2 with the Harmonia
cross-domain tensor's EC and L feature columns in place of raw DB features. Per C-8f20c74fa0cf
the tensor measures feature geometry; this arm's expected outcome is signal that dies under the
object permutation, and it can only ever extend that claim, never establish coupling.

## Controls

1. Object-permutation null (the decisive null, modeled on the kill in C-1f1a743fce1b): within
   cells of (log-conductor multiplicative bin width 1.10 x order_of_vanishing x root_number),
   permute the EC-row-to-L-row pairing. This preserves both marginals and the full conditioning
   structure and destroys ONLY object identity — it perturbs exactly the axis the coupling
   statistic varies on (null-axis doctrine). B = 1000 permutations for dCor, B = 200 for
   Delta-R^2 (compute-bound), identical stratification in every arm.
2. Conditioning control (forced by C-9334502f16d1 and C-d151768c6740, both killed by
   conductor/rank conditioning): Z is regressed out / blocked in every estimator; any candidate
   signal is additionally re-tested with Z-residualization tightened one notch (40 conductor
   bins) — a signal that shrinks by > 50 percent under tightening is booked as residual
   conductor structure, not coupling.
3. Feature-construction negative control (the "beyond what feature construction alone induces"
   arm): synthesize Y' by drawing, for each class, a Y value from the empirical Z-conditional
   distribution (same cell, different object). (X, Y') has by construction all
   construction-induced and conditioning-induced structure and zero object-level content. The
   observed statistic must exceed the 99th percentile of the Y' distribution (50 replicates).
4. Algebraic-forcing pre-screen (forced by C-96779c5836df Szpiro x Faltings tautology and
   C-450a0c8756cf BSD-Sha retraction): before any data are read, each of the 32 (X, Y) pairs
   gets a one-paragraph derivation audit; any pair where both sides are known functions of a
   shared primitive (log|Disc|, conductor, rank) is struck from the discovery set and listed as
   FORCED in the report. Struck pairs cannot re-enter.
5. Positive control / instrument-vacuity gate (verify-signature-exists doctrine): run the full
   pipeline with rank removed from Z, X = {rank}, Y = order_of_vanishing. The known
   deterministic coupling (C-954b8ae3b448) must be recovered: permutation z > 10 and
   Delta-R^2 > 0.9. If not, the instrument is blind and the pre-committed VACUOUS reading is
   issued — no null claim.
6. SE-before-gate check: SE of Delta-R^2 estimated from control arms (over blocks) before the
   true statistic is unblinded; the 0.01 gate must sit > 2*SE from zero or N escalates (once)
   before any verdict.

## Preregistered falsifiers (each with an explicit numeric threshold)

- FALSIFIER-1 (kills H1): omnibus Delta-R^2 < 0.01 for all 4 Y endpoints (Holm alpha = 0.01
  family), OR permutation z < 4 for the corresponding dCor, OR observed statistic <= 99th
  percentile of the feature-construction negative control — any one of the three, for every
  endpoint, and H1 is dead. A coupling claim requires ALL THREE simultaneously on at least one
  Holm-surviving endpoint: Delta-R^2 >= 0.01 with block-bootstrap 95 percent CI excluding 0,
  permutation z >= 4, and > 99th percentile of negative control.
- FALSIFIER-2 (kills the null VERDICT, not H1): positive control fails (permutation z <= 10 or
  Delta-R^2 <= 0.9 on rank/order_of_vanishing) => verdict VACUOUS_INSTRUMENT; neither H0 nor H1
  may be claimed.
- FALSIFIER-3 (kills a candidate signal as conductor residue): any endpoint passing FALSIFIER-1
  thresholds but losing > 50 percent of its Delta-R^2 under the tightened 40-bin conditioning is
  reclassified RESIDUAL_CONDITIONING; it does not count toward H1.
- FALSIFIER-4 (kills the tensor arm as coupling): tensor-arm dCor permutation z >= 4 while
  raw-arm z < 2 on the same endpoint => verdict FEATURE_GEOMETRY_CONFIRMED (extends
  C-8f20c74fa0cf); tensor-arm results can never satisfy FALSIFIER-1 on their own.
- FALSIFIER-5 (gate reachability, pre-verdict): before unblinding, compute the attainable range
  of Delta-R^2 given Var(Y|Z) on control arms; if the 0.01 gate exceeds the attainable maximum,
  the design is declared INELIGIBLE and re-scoped — a null read against an unreachable gate is
  forbidden.
- Seed stability: the primary verdict must hold in >= 4 of 5 seeds; 3/5 or worse => NO_VERDICT.

## Stopping rule

Fixed-N, single-pass design. One preregistered N (full join population if <= 200,000 eligible
classes, else the stratified 200,000). No data-dependent stopping, no adding endpoints, features,
or permutations after the true pairing is first read. Exactly one permitted escalation: if the
SE-before-gate check (control arms only, before unblinding) shows 0.01 < 2*SE(Delta-R^2), N
doubles once; if the gate is still inside 2*SE, the experiment stops with verdict UNDERPOWERED.
Hard resource caps: statement_timeout 300s per query, 12 wall-clock hours total on M1; if the
Step 0 inventory returns < 50,000 eligible joined classes, stop, publish the inventory, and
re-scope — do not proceed on a population 25x smaller than assumed (wrong-population doctrine).

## Unit of inference

The ISOGENY CLASS (one L-function per class; curves within a class share it — inference at curve
level would replicate each L-row class_size times and inflate n). All SEs and CIs are computed on
the correct exchangeable unit: permutation exchanges classes within (conductor-bin x rank x
root_number) cells; Delta-R^2 uncertainty uses block bootstrap over conductor-decade blocks
(n = number of blocks, not number of rows — SE-on-the-wrong-unit doctrine). Claims generalize to
"isogeny classes in the LMFDB mirror over the observed conductor range," nothing broader.

## Prior work bearing on this design

- C-8f20c74fa0cf (SUPPORTED, Aporia/X-9747d5cd5ab0): "The tensor measures feature geometry, not
  object-level coupling, confirmed across all three scorers." Ceiling: direct-DB-query tests
  survive. The direct antecedent of this experiment.
- C-1f1a743fce1b (REFUTED claim = NF backbone kill, E-0e68ead742f0): permutation null z = 0.0
  showed bond structure is distributional, not object-level. Template for the decisive null here.
- C-9334502f16d1 (REFUTED, Harmonia): L-zero moment hierarchy did not stratify EC families
  beyond conductor and rank; ceiling: zero ORDERING survives as a shape invariant.
- C-d151768c6740 (REFUTED, Harmonia): OQ1 spectral-tail rank-spacing correlation killed by
  conductor conditioning.
- C-96779c5836df (REFUTED, Mnemosyne): Szpiro x Faltings rho = 0.97 was algebraically forced
  (both sides encode log|Disc|). C-450a0c8756cf (RETRACTED, Harmonia): BSD-Sha anticorrelation
  was an identity rearrangement. Together they force the algebraic-forcing pre-screen.
- C-954b8ae3b448 (ESTABLISHED, Aporia): BSD rank agreement 3,824,372/3,824,372 — supplies the
  positive control and mandates excluding rank from the discovery set.
- C-948eae5cb70c (OBSERVED, Ergon): object_zeros NULL defect — object_id unusable as join key;
  lmfdb_label/lmfdb_iso intact.
- C-a3744a88ea5e (OBSERVED, Aporia, cycle 141-E): 7 generic operators, 0 relations over 295M
  EC-trace triples — generic verbs find nothing on this substrate; features here are native
  invariants, not generic sequence operators.
- C-1938a4759fd8 (REFUTED, Ergon): correct-feature re-encoding did not rescue knot coupling —
  cautions against a "better features will find it" rescue loop; hence single-pass design.
- Gap H-bac36ae694a2: projection_equivalence x lmfdb_arithmetic is an empty evidence cell this
  experiment populates either way.
- Join pattern grounded in F:\Prometheus\harmonia\scripts\spectral_tail_isogeny.py (origin =
  'EllipticCurve/Q/' || REPLACE(lmfdb_iso,'.','/')); DB access pattern in
  F:\Prometheus\aporia\catalog_attacks\attack_0348_grh.py.

## Evidence Wiki consultation log (queries run + object ids retrieved)

Client: ew.client.EvidenceWiki(machine='M1', agent='V1B-T3-wiki'), canonical_revision 521
(embedding index behind 0; cp derived view behind 118).

1. search_evidence("tensor coupling elliptic curve L-function cross-domain") -> C-9334502f16d1
   (REFUTED), C-8f20c74fa0cf (SUPPORTED), C-a3744a88ea5e (OBSERVED), C-96779c5836df (REFUTED),
   C-954b8ae3b448 (ESTABLISHED), C-1f1a743fce1b (REFUTED), C-948eae5cb70c (OBSERVED),
   C-1938a4759fd8 (REFUTED), C-450a0c8756cf (RETRACTED), C-e0b3b4966385 (RETRACTED).
2. search_evidence("feature geometry backbone Harmonia tensor claim") -> C-8f20c74fa0cf,
   C-1f1a743fce1b, C-e0b3b4966385, C-d151768c6740, C-1938a4759fd8 (top 5).
3. get_claim("C-8f20c74fa0cf") -> version 1, SUPPORTED, experiment X-9747d5cd5ab0, packet
   SP-2256eb272cce, evidence E-69e563924f3e (gate: "convergent verdict across 3 independent
   scorer classes"; quote: "Tensor measures FEATURE GEOMETRY, not object-level coupling (all 3
   scorers confirmed)"); ceiling: "Batch 01 open-problem tests survive (direct DB queries, not
   tensor)". Relations: R-1b3075bf1ab4 GENERALIZES C-1f1a743fce1b; R-95c887826827
   SAME_MECHANISM from C-f8f06a6e21ca (projection-equivalence reading).
4. get_counterevidence("C-8f20c74fa0cf") -> counter_relations: [] (none); negative_evidence:
   E-69e563924f3e only. No standing counterevidence to the feature-geometry claim.
5. related_findings("C-8f20c74fa0cf") -> graph: C-1f1a743fce1b, C-f8f06a6e21ca (1 hop);
   C-5dfca4937762, C-a2cba4576ecd, C-b287aa6823b0 (2 hops); semantic: C-e0b3b4966385,
   C-b5c1a85cca8b, C-94fc12c3e6af, C-1938a4759fd8, others; edge R-fe557200af2e ("failed rescue
   leaves the NF backbone kill standing").
6. Negative-evidence query: search_evidence("coupling signal killed permutation null negative
   elliptic curve L-function zeros") -> kills/negatives: C-9334502f16d1, C-1f1a743fce1b
   (E-0e68ead742f0, metric "z=0.0 under permutation null"), C-96779c5836df, C-d151768c6740,
   C-1938a4759fd8, C-450a0c8756cf; plus C-948eae5cb70c (defect), C-d0f2742bd8ed (PARTIAL,
   retained), C-a36c7e9fe323, C-954b8ae3b448.
7. contradictions() -> one open pair: R-e68c9331eca2, C-3a1c49fa5a78 vs C-3d12c440f087
   (D-5 vs D-8 on executable-history reuse; APPARENT_UNDER_DIFFERING_CONDITIONS). Not in this
   design's domain; no bearing.
8. find_gaps() -> H-a86125892a3e, H-41f9f15ce208, H-bac36ae694a2 (projection_equivalence x
   lmfdb_arithmetic — RELEVANT, this design fills it), H-c9832bd95134, H-7c607f34d50e,
   H-9b0a7922015e (candidate relation, foundry domain, not relevant).
9. Follow-up get_claim on C-1f1a743fce1b, C-9334502f16d1, C-948eae5cb70c, C-d151768c6740 for
   gates, metrics, and ceilings (E-0e68ead742f0, E-e2c3d903daeb, E-f7c8e4db8f66, E-cdb670a5d454).

## Evidence that changed this design (specific ids + the concrete design decision each changed)

- C-8f20c74fa0cf + its ceiling ("direct DB queries survive"): demoted the Harmonia tensor from
  instrument to secondary characterization arm; the primary test runs on raw DB features, and
  FALSIFIER-4 forbids a tensor-only result from ever counting as coupling.
- C-1f1a743fce1b / E-0e68ead742f0 (permutation null z = 0.0 killed the NF backbone): made the
  within-stratum object-pairing permutation the DECISIVE null and defined "object-level" itself
  as survival-of-permutation; set the null on the pairing axis rather than a row/label shuffle.
- C-9334502f16d1 + C-d151768c6740 (both killed by conductor/rank conditioning): put log
  conductor, order_of_vanishing, and root_number into the conditioning set Z from the start,
  added the tightened-conditioning re-test, and added FALSIFIER-3 (>50 percent shrinkage =>
  RESIDUAL_CONDITIONING). Also, the C-9334502f16d1 ceiling ("ordering of zero values survives as
  a shape invariant") steered Y toward unfolded gap-shape statistics rather than raw moments.
- C-96779c5836df + C-450a0c8756cf (tautology/identity kills): created the algebraic-forcing
  pre-screen (Control 4) that audits all 32 (X, Y) pairs for shared primitives before data are
  read, with struck pairs unable to re-enter.
- C-954b8ae3b448 (100.000000 percent rank agreement): moved rank/order_of_vanishing OUT of the
  discovery set and IN as the positive control with numeric vacuity gates (z > 10,
  Delta-R^2 > 0.9) — FALSIFIER-2's instrument check.
- C-948eae5cb70c (object_zeros NULL defect, lmfdb_label intact): fixed the join to
  lmfdb_iso -> lfunc_lfunctions.origin string construction and banned object_id/xref as a key;
  added the Step 0 full-join inventory before any sampling.
- C-1938a4759fd8 (feature re-encoding failed to rescue knot coupling): motivated the single-pass,
  no-rescue-loop stopping rule — a null here is booked, not iterated on with new features.
- H-bac36ae694a2 (empty cell projection_equivalence x lmfdb_arithmetic): confirmed the experiment
  is non-duplicative and set the write-back target: the verdict is submitted against this gap.
