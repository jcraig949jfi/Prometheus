# Koios -- Phase 3 intake dossier (with shared surfaces alien_circuitry/, sigma_kernel/, prometheus_math/)

Seat: Koios
Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main)
Date: 2026-10-01

Summary. Koios ("the Axis") was a short-lived April 2026 "tensor custodian"
seat whose charter is to admit invariant "coordinates" into a Mathematical
Phenotype Atlas (MPA) tensor through five gates and three "IDN"
normalizations [INTENT] (roles/Koios/RESPONSIBILITIES.md). What was BUILT and
RUN [IMPL]: four standalone numpy/scipy scripts (koios/scripts/), run once
each between 2026-04-12 and 2026-04-18, that (1) computed the moment ratio
M4/M2^2 of normalized coefficient sequences for elliptic curves, modular
forms and Maass forms and declared it ADMITTED 5/5, (2) rejected log(aut)/log(size)
4/5, (3) rejected a mod-p determinant fingerprint 4/5, and (4) ran an SVD of
a 31 x 37 Harmonia "invariance tensor" (a matrix, 90.6% empty) and declared
"Geometry 1 FALSIFIED" (effective rank 12-16, not <= 5) [RESULT-UNVERIFIED]
(koios/results/*.json; cartography/docs/tensor_rank_analysis.md; commits
e3b627bab, 66a0e5bc9, d4472562a, 5f2298789). Reading the admission script
shows two of the five gates cannot fail as coded (Gate 3 is hard-coded True;
Gate 5 is computed on per-domain OLS residuals whose domain means are zero by
construction) [IMPL] (koios/scripts/mpa_area1_moment_ratio.py:376, 173-183,
415-472). The seat never ran again; its only later trace is a 2026-09-01
Mnemosyne TODO (open) and a base-role header line. Koios has no organism, no
world and no learner. Because no seat of this crawl built alien_circuitry/,
sigma_kernel/ or prometheus_math/, and Koios is the representation/tensor
seat, those three shared surfaces are described in labelled appendices at the
end of this dossier.

## 1. Identity, charter and pivots

- koios/: 6 commits, 2026-04-12..2026-04-23 [IMPL] (git log -- koios). First:
  e3b627bab "Koios workspace + Area 1: M4/M2^2 ADMITTED to MPA tensor (5/5
  gates)". Last own: 5f2298789 2026-04-18 "Koios rank-analyst: SVD of
  invariance tensor -- Geometry 1 FALSIFIED".
- roles/Koios/: 3 commits: 2052e5d7c 2026-04-16 "Gather remaining M2
  artifacts" (role docs came from M2), 60721f003 2026-09-01 (Mnemosyne TODO),
  249bb0f98 2026-09-11 (base-role inheritance header) [IMPL].
- No base-role adoption pass, no STATUS, no journal, no ARCHAEOLOGY file
  exist for Koios [IMPL by absence]. Achilles census lists engine `koios`
  with primary seat Koios [CLAIM] (roles/Achilles/census/registry/engines.json).
- Relationships named in the charter: Ergon tensor builder, Cartography
  dissection pipeline, shadow archive, Harmonia (invariance tensor source:
  harmonia/memory/build_landscape_tensor.py) [IMPL] (rank_analysis.py:30-35).
- Infrastructure lines in RESPONSIBILITIES.md include a Redis password in
  plain text; not reproduced here.

## 2. Engine/system inventory

No engine in the loop sense. Four analysis scripts and one registry:
- koios/scripts/mpa_area1_moment_ratio.py (22.8 KB): reads
  charon/data/charon.duckdb (EC, MF) and cartography JSON (Maass); computes
  M4/M2^2 per object; IDN; five gates; writes results/mpa_area1_results.json
  [IMPL]. Open TODO: repoint off the frozen DuckDB (roles/Koios/todo_20260901.md)
  [IMPL].
- koios/scripts/mpa_area2_aut_ratio.py, mpa_area3_modp_fingerprint.py
  (same template; lattices, groups, genus-2; knots, lattices, NF) [IMPL].
- koios/scripts/rank_analysis.py (17.6 KB): three SVD variants (naive,
  singular value thresholding, observed-only agreement) on the Harmonia
  landscape tensor; writes cartography/docs/tensor_rank_analysis.{md,json}
  and plots [IMPL].
- koios/data/mpa_tensor_schema.json: registry with 1 admitted, 2 rejected,
  0 pending coordinates [IMPL].
- roles/Koios/TENSOR_INVENTORY.md (2026-04-15): catalogue of 11 tensor
  artifacts owned by other seats (Ergon tensor 58,111 x 28; shadow tensor;
  dissection tensor NOT BUILT; detrended tensor; v2 domain tensors; tensor
  bridges 2.7M links) [CLAIM] -- a locator, not Koios code.
- Deps: numpy, scipy.stats, duckdb, matplotlib [IMPL]. Scale: EC 31,073,
  MF 17,314, Maass 14,995 objects (Area 1); groups 533,287 (Area 2)
  [RESULT-UNVERIFIED] (results JSON).

## 3. Code architecture and dataflow

DB/JSON -> per-object scalar invariant -> three IDN transforms (size
residual by linregress on log1p(size); entropy ratio; rank quantile within
20 size bins) -> five gates -> JSON verdict [IMPL]. Doc-vs-code
disagreements:
- Charter Gate 3 "Not reducible to marginals (survives size/density
  controls)"; code: `gate3_pass = True  # Will set based on info retention`
  (mpa_area1_moment_ratio.py:376) -- never set [IMPL].
- Charter Gate 5 "Domain-agnostic"; code: eta^2 of domain label over the
  concatenated per-domain size residuals (lines 415-472). Each domain's
  residuals come from its own OLS fit with intercept, so each domain mean is
  zero and ss_between is zero up to float error; recorded eta^2 = 7.8e-34
  [IMPL] (results/mpa_area1_results.json). The Area 2 commit admits Gate 5
  "passed ... but vacuously -- IDN removed all signal" (d4472562a) [CLAIM].
  Gate 5 cannot fail on a size-residualised scalar [CODE-INFERRED].
- Gate 1 "Null-calibrated (survives permutation baseline)"; code: KS test of
  5,000 EC values against 10,000 draws of M4/M2^2 from n=25 Beta(1.5,1.5)
  (semicircle) samples, pass if p < 0.05 (lines 284-292) [IMPL]. The
  semicircle is the Sato-Tate law itself, so this tests deviation from the
  expected law at very large n, not signal versus random [CODE-INFERRED].
- Sanity checks recorded beside the ADMITTED verdict: EC SU(2) mean 2.16 vs
  expected 2.0; EC CM mean 3.51 vs expected 1.5 [IMPL]
  (mpa_area1_results.json sanity_checks); listed as "known limitations",
  not as a failed check [IMPL] (mpa_tensor_schema.json).

## 4. Claimed computational primitive vs actual mechanism

- Label: "MPA tensor" of validated invariant coordinates; "tensor
  stewardship"; "Geometry 1" low-rank invariance tensor.
- Smallest actual mechanism: a scalar per object (ratio of 4th to squared 2nd
  moment of ~25 normalized coefficients) plus threshold tests; an SVD of a
  31 x 37 matrix with 108 observed cells [IMPL/RESULT-UNVERIFIED]
  (tensor_rank_analysis.md:27,149). No tensor of order > 2 is constructed;
  the analysis notes "The invariance object is a 2-index matrix ... the SVD
  IS the MPS decomposition" [CLAIM] (tensor_rank_analysis.md:143).
- What it could express: a per-object feature vector (one admitted column).
- Phenomenon targeted: domain-agnostic structural invariants; low-rank
  latent geometry of "what survives".
- Could it perform it: M4/M2^2 is a known Sato-Tate class indicator (SU(2)
  2.0, CM 1.5 in the limit) [CODE-INFERRED from the script's own expected
  values]; the ADMIT is a rediscovery of a known statistic with bias at n=25.
- Ruler vs shortcut: two gates cannot fail; Gate 1 passes on any deviation at
  n=5000. The ruler cannot tell an informative coordinate from any scalar
  that is size-residualised [CODE-INFERRED]. The rank analysis itself warns
  that 108 observations are below the ~600 needed for rank ~12 and that an
  imputation variant collapsed to rank 1 as an artifact [CLAIM]
  (tensor_rank_analysis.md:55,149).

## 5. Representation/state architecture

JSON registry {admitted, rejected, pending} with gate results per
coordinate [IMPL]. No persistent tensor was written by Koios.

## 6. Organism/player architecture

None found.

## 7. World/environment architecture

None; inputs are static LMFDB-derived tables (via charon DuckDB) and
cartography JSON [IMPL].

## 8. Search/training/adaptation mechanism

None ("one invariant family at a time", by hand) [INTENT].

## 9. Measurement/ruler stack

Five gates and three IDN normalizations as above; rank analysis: effective
rank at 95% variance, three methods [IMPL]. Blind spots: hard-coded and
vacuous gates; no multiple-comparison control; no positive control (a known
domain-specific feature that Gate 5 must reject was not run; Area 3 serves
as a "calibration death" only for Gate 5's MI variant) [CODE-INFERRED].

## 10. Baselines and controls

Area 2 permutation of aut within size groups (the gate that killed it)
[RESULT-UNVERIFIED]; Area 3 designed as an expected rejection ("Calibration
area", mpa_area3_results.json note) [IMPL]. No controls for Area 1's Gates 3
and 5.

## 11. Historical experiment campaigns

C-K1 MPA Area 1, M4/M2^2. 2026-04-12, e3b627bab. Datasets EC 31K, MF 17K,
Maass 15K. Reported ADMITTED 5/5. Later: no recorded challenge in tree; this
crawl finds Gates 3 and 5 non-falsifiable as coded [CORRECTION, this crawl].
Label: REPORTED POSITIVE (instrument defective).

C-K2 MPA Area 2, aut ratio. 2026-04-13, d4472562a. Reported REJECTED 4/5
(Gate 1 permutation). Label: REPORTED NEGATIVE/NULL.

C-K3 MPA Area 3, mod-p fingerprint. 2026-04-12, 66a0e5bc9. Reported REJECTED
4/5 (Gate 5, MI 0.20 driven by mod 2), "as designed". Label: REPORTED
NEGATIVE/NULL.

C-K4 Rank analysis of Harmonia invariance tensor. 2026-04-18, 5f2298789.
Reported Geometry 1 FALSIFIED; "3-dimensional core captures 48-74%".
Self-caveat: 90.6% cells untested, estimates +/- 3-4. Label: INCONCLUSIVE
(the falsification rests on a matrix too sparse for the claimed rank, per
its own text).

## 12. Reported results and later corrections

No later correction recorded by any seat for Koios results [UNKNOWN; not
found in roles/ grep for Koios beyond Achilles census]. This crawl's reading
(Gate 3/5 vacuity; Gate 1 semantics; CM sanity check failing by 2.0) is a
[CORRECTION] candidate, not a seat-recorded one.

## 13. False-positive archaeology

The ADMITTED verdict for M4/M2^2 with two unfalsifiable gates and a failed
CM sanity check recorded as a "limitation".

## 14. Likely false-negative regimes

Gate 1 permutation design for Area 2 compares within size bins; a coordinate
that carries information only across sizes would be rejected
[CODE-INFERRED]. Rank analysis: sparse matrix may over- or under-state rank.

## 15. Phase 3 audit (Koios scripts)

a. Representation richness: hierarchy NO; compositional NO; variable
   binding NO; memory NO; recurrence NO; counterfactual state NO; latent
   variables PARTIAL (SVD components); temporal abstraction NO; spatial
   abstraction NO; reusable substructure NO; dynamic routing NO;
   self-reference NO.
b. Reasoning opportunity: none (descriptive statistics).
c. Shortcut surface: size-residualisation guarantees Gate 5; Gate 3 constant.
d. Ruler resolving power: low for admission; moderate for rejection by
   permutation (Area 2).
e. Scale: ~63K objects (Area 1), 533K groups (Area 2), 31 x 37 matrix with
   108 observed cells (rank analysis); single runs.

## 16. Research reports and substantial documents

- roles/Koios/RESPONSIBILITIES.md -- charter, five gates, IDN.
- roles/Koios/TENSOR_INVENTORY.md -- inventory of 11 tensor artifacts (other
  seats').
- cartography/docs/tensor_rank_analysis.md -- Geometry 1 test.
- koios/data/mpa_tensor_schema.json -- admission registry.

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

roles/Koios/todo_20260901.md (OPEN: repoint Area 1 off charon.duckdb);
koios/scripts/DUCKDB_NOTICE.md. No journal, backlog or adoption pass.

## 18. Dependencies on other engines and seats

Charon (DuckDB EC/MF), Cartography (JSON datasets), Harmonia
(build_landscape_tensor), Mnemosyne (data steward TODO), Ergon (tensor
inventory) [IMPL/CLAIM]. No use of prometheus_math or sigma_kernel; no
descendant of the MPA in either package (grep for MPA, invariance tensor,
M4/M2 found none) [RESULT of sub-search, CODE-INFERRED].

## 19. Scaling limitations

One scalar at a time by hand; gates per-script, not a library.

## 20. Lens potential for Phase 3 (descriptive)

Substrate: tables of number-theoretic objects. Phenomenon family: invariant
admission / representation geometry. Reusable: the IDN idea and the
permutation-within-size control (Area 2); the rank analysis's own sparse-data
caveat. Toy-grade: Gates 3 and 5 as coded. Unknowns: what the MPA would be
with working gates.

## 21. Open questions / coverage gaps (Koios part)

Read: RESPONSIBILITIES, todo, TENSOR_INVENTORY (sections 1-11 head), schema,
three results JSONs, Area 1 script gate code, rank_analysis.py head,
tensor_rank_analysis.md key lines, commit messages. Not read: Area 2 and 3
scripts, rest of rank_analysis.py, the plots, Harmonia
build_landscape_tensor.py.

---

## Appendix S1. Shared surface: alien_circuitry/ (AC-01, AC-01D, Nursery)

Attribution: 40 commits 2026-09-12..2026-09-14, author James Craig with Claude
co-author (two Claude sessions), subject prefixes AC-01 / AC-01D-v1 /
AC-01D-v2 / Nursery, no seat name; no roles/ directory [IMPL] (git log --
alien_circuitry). Achilles census: primary_seat null, Artemis as auditor
[CLAIM] (engines.json alien_circuitry). Receipts call the author "this seat"
/ "AC-01 seat" [CLAIM]. Not built by any of this crawl's five seats.
CRUCIBLE-C imports frozen code from roles/Diomedes (crucible_c.py:12-16)
[IMPL, per sub-reader].

Question (README): when an inference frontier is combinatorially large, is
its decision-relevant consequence structure much smaller, and can that
structure replace search while keeping verified correctness [INTENT].

Inventory [IMPL]: universe/ (directed rewriting over words in {x,X,y,Y},
length <= 10, 1,398,101 states; presentations ABELIAN, BRAID_B3, one-way
variant; exhaustive reverse-BFS distance chart D), universe/monoid.py (full
transformation monoid T_7, 823,543 maps, 3 generators, D by reverse BFS per
rank-2 target), gate/ and gate2/ (lookahead and navigation), ac01d/ (frozen
corpus with hashed state/target/pair masks, 13 of 63 targets held out;
families C1 low-rank SVD, C2 CP-ALS and TT/Tucker (torch), C3/C4 exact
quotient, C5 DigitNet MLP (torch/cuda), C6 genetic-programming expressions;
forensic and interpret modules; v2 canonical orbit table), nursery/
(NURSERY.jsonl 10 entries, crucibles B and C), tests (32 functions; 28
reported passing, not run here). Deps numpy, scipy, sklearn, torch. Scale:
11,138,190 reachable pairs; storage reference (lzma sparse D) 1,060,696 B;
FIT 4.29M rows; 300 navigation problems per held set with D >= 5.

Campaigns (labels per shared scheme; numbers RESULT-UNVERIFIED unless
marked):
- Datalog universe (898338725, DATALOG_FAILURE.md): 32,768 states, no
  reachability-changing transitions; INSTRUMENT FAILURE.
- Phase A/B ABELIAN / BRAID_B3 at L=10 (9abb1efdf): 88% (braid) and 100%
  (abelian) of traps are target artifacts; residual traps shallow;
  INSTRUMENT FAILURE.
- U-A3 lookahead gate (fb6f4c9cf): depth-4 lookahead proves all 12,191
  traps; D equals a count formula; NO-GO TOO SHALLOW; REPORTED NEGATIVE/NULL.
- Universe C design search (f7ba88312): T_7 chosen; INCONCLUSIVE (design).
- Survivor gate (prereg 9997a3367, result 014aa4f75): K3 fires (U-C1
  residual R1 = 0 on 51.7M pairs), K2 fires by letter; NO-GO RESIDUAL TOO
  SMALL; REPORTED NEGATIVE/NULL.
- AC-01D-v1 (freeze 95f22c88f .. receipt 495846246): metric HC_D =
  1 - (C_M - C_O)/(C_K - C_O) in transitions (C_K kernel-aware DFS, C_O
  oracle). C1 killed (HC_D -2.3), C3/C4 killed (no row redundancy), CP r16
  1,708 B HC_D 0.55-0.61, TT r16 0.36-0.54 (GPU non-reproducible:
  [CORRECTION] 495846246), C5 227 KB HC_D 0.91, C6 1,428 B 0.54-0.59; label
  permutation collapses C5. Value-relabelling symmetry finding withdrawn
  [CORRECTION] (188306fe3). Mid-range HC_D denominators shown to roughly
  double under a tie-break change [CORRECTION] (93cdb3392). LATER OVERTURNED
  (interpretation).
- AC-01D-v2 orbit table (188306fe3, BUG run fa4ecf253 [CORRECTION], final
  9072a959f): D is an exact function of the (f,t) contingency-table orbit
  under domain relabelling; 25,382 orbits, 34.8 KB table, HC_D 0.997-0.999;
  "STRONG POSITIVE"; REPORTED POSITIVE.
- Nursery harvest (86a429efe): CP vs C6 error correlation 0.82;
  REPORTED NEGATIVE/NULL.
- CRUCIBLE-C (prereg d3b9533b7, result 8157e9e70): pair-quotient of Diomedes
  counterexample-hunt states cuts cost-to-first-break 2.69 -> 2.22, 5/5
  seeds p = 0.005; REPORTED POSITIVE (modest).
- CRUCIBLE-B (9b0a96314 INSTRUMENT FAILURE: preregistered random-macro
  control infeasible, runner hung 11 h; addendum 8851f05c3; result
  93cdb3392): mined T_7 macros worst of 84 under DFS; harness
  duplicate-successor/tie-break defect found [CORRECTION]; REPORTED NEGATIVE.

Claimed primitive vs actual mechanism: label "alien circuitry" / compressed
consequence structure. Smallest mechanism: an exhaustive reverse-BFS distance
table over a finite monoid word graph, approximated by factorizations or an
MLP and used to order successors in a DFS; the v2 winner is a hash lookup
from a canonicalized (sorted) column arrangement to average D, i.e. the
double-coset quotient of the S_7 domain action [IMPL] (v2/canonical.py:35-37;
orbit_navigation.py:115-130, per sub-reader). Harness facts that bound what
the ruler sees [IMPL] (per sub-reader): the true kernel invariant is handed to
every searcher for pruning (evaluate.py:56 `dead()` reads kmask), and
representation calls cost zero transitions in HC_D (evaluate.py:89). FIT
already covers 25,363 of 25,382 orbits, so "held-out targets/states" are
in-distribution after quotienting [CODE-INFERRED]. The README doctrine
"Rediscovery of known mathematics ... is instrument success, not alien
circuitry" [INTENT] places v2 as instrument success, while NURSERY.md files it
as specimen NUR-001 [CLAIM]. Artemis harvest calls v2 "the cleanest case of a
discovered representation turning search into lookup"
(roles/Artemis/backlog/harvest/D4_sfe_era.md:417-421) [CLAIM]; this crawl
records disagreement: the quotient was derived by the analyst from exact
symmetry, splits are not orbit-disjoint, and kernel pruning is free
[CORRECTION, this crawl].

Representation richness (T_7 graph and families): hierarchy NO; compositional
PARTIAL (monoid composition; C6 syntactic trees); variable binding NO; memory
NO; recurrence NO; counterfactual state YES on the oracle side (exhaustive D)
only; latent variables PARTIAL (kernel, orbit; C5 internal rank code,
probe R^2 0.997 RESULT-UNVERIFIED); temporal abstraction NO (macros killed);
spatial NO; reusable substructure NO; dynamic routing NO; self-reference NO.
Reasoning opportunity: shortest-path navigation in a fully enumerable graph;
nothing requires more than a distance oracle. Shortcut surface: free kernel
invariant, non-orbit-disjoint holdout, D >= 5 filter, free representation
compute, tie-break-sensitive denominator. Toy scale: n = 7, rank-2 targets,
~25K orbits; scaling to rank 3 or n = 8 "prohibited by the brief"
(CRUCIBLES.md:106) [CLAIM]. Coverage: sub-reader did not read
TENSION_INVENTORY.md, most of NURSERY.md, PREREGISTRATION_DRAFT.md, the
interpret/forensic bodies, most result JSONs; nothing re-run.

## Appendix S2. Shared surface: sigma_kernel/

Attribution: 41 commits 2026-04-29..2026-05-09, author James Craig; messages
name Techne 19, Substrate-Tester 14, Aporia 9, Charon 7, Ergon 7 (Mnemosyne
Postgres fill-in 7a053e6b6); Achilles census owner Techne from
roles/Techne/RESPONSIBILITIES.md:21 [CLAIM]; design spec by documentation at
harmonia/memory/architecture/sigma_kernel.md [CLAIM]. Not any of the five
seats; none of the five imports it [CODE-INFERRED, grep].
What it is [IMPL] (sigma_kernel.py:39-128, 509-1485, per sub-reader): a
provenance/promotion ledger: frozen Symbol(name, version, def_hash,
provenance, tier), Claim(hypothesis, evidence, kill_path), linear
Capability with persisted spent_caps, nine opcodes (RESOLVE, CLAIM,
FALSIFY, GATE, PROMOTE, ERRATA, TRACE, REWRITE, EQUIV), SQLite default and
Postgres backend. FALSIFY calls omega_oracle.py, a self-described stub that
parses "mean OP value" and compares with evidence["true_mean"] supplied by
the claimant (omega_oracle.py:39-70) [IMPL]. REWRITE/EQUIV only record links
("actual transformation logic ... is the caller's responsibility") [IMPL].
OBSTRUCTION_SHAPE: A149 5/5 vs 1/54 "54x lift" on n = 5 [RESULT-UNVERIFIED];
cross-family transfer INCONCLUSIVE (A148 0/201 strict matches) [CORRECTION]
(a148_validation_results.json, a150_a151_validation_results.json); the
promotion path rewrites a stored hypothesis with a direct SQL UPDATE and
feeds the claimant's own rate to the oracle (a149_obstruction.py:336-361)
[IMPL, per sub-reader]. Harmonia's 06-22 audit already recorded "PROMOTE
never re-runs the kill battery" [CORRECTION] (Atlas digest
harmonia_rulers_and_satellites.md, failures table). Tier A++ TensorNetwork,
B, C MomentPolytope, D, E are pytest stubs that skip because the modules do
not exist [IMPL]. "Substrate-Tester fire" scores are mutation-kill ratios on
~10 mutants per module (e.g. 0.300 -> 1.000, 6eeb1c823) -- test-suite
sensitivity, not science [IMPL]. Only real coordinate chart: Lehmer degree-14
palindromic (coordinate_charts/lehmer.py:121-213) [IMPL]. Smallest mechanism:
an append-only content-addressed claim ledger; no substrate, no memory
mechanism beyond the ledger.

## Appendix S3. Shared surface: prometheus_math/ (theme-relevant parts)

Attribution: 219 commits from 2026-04-25 (skeleton c56436efa); Techne the
main builder (85 messages name Techne; 59 subject lines), Aporia tickets and
ratifications, 59 automated "arsenal: capability matrix updated" commits by
prometheus-bot to 2026-09-30 [IMPL] (git log). Achilles owner Techne [CLAIM].
Structure [IMPL]: registry.py backend probe list (sympy, sage, cypari,
flint, snappy, gudhi, z3, pysat, scip ...), facade __init__.py, ARSENAL.md
generator, @arsenal_op metadata decorator (arsenal_meta.py), tests/ 143
files, databases/ 39, research/ 22, recipes/ 16, substrate_generation/ 14.
Theme-relevant parts:
- symbolic_tensor_decomp.py (607 lines, 2026-04-25): tensorly wrappers for
  CP/Tucker/TT and rank estimates [IMPL].
- tensor_train.py (149 lines, 2026-08-21, Techne loop cycle 002): TT bond
  ranks via quimb with a fiber-shuffle null -- the smallest real
  tensor-representation mechanism in the package [IMPL].
- research/tensor.py (1,402 lines): Harmonia 4-axis (domain, object, phoneme,
  invariant) tensor with MMD/identity-join scorers; fetch functions
  "placeholders" by its own docstring [IMPL/INTENT].
- Discovery environments: sigma_env.py (13-arm bandit over arsenal ops; 9 of
  13 arms "jackpots" per its docstring), discovery_env v1-v3 (reciprocal
  polynomial construction, +100 reward for 1.001 < M < 1.18), obstruction_env,
  BSD/genus-2/knot/mock-theta/modular-form/OEIS envs [IMPL]. Reported:
  0 PROMOTEs across 9 ablation cells / ~270K episodes; REINFORCE BSD rank
  +1.37x over random but "recovers the rank prior" [RESULT-UNVERIFIED]
  (DISCOVERY_PIPELINE_VALIDATION.md s6); v2/v3 found nothing [CORRECTION]
  (DISCOVERY_V2_RESULTS.md, DISCOVERY_V3_RESULTS.md). The reward band
  contains Lehmer's number 1.17628, so its rediscovery would register as a
  hit [CODE-INFERRED].
- kill_vector.py (1,762 lines), evidence_field.py, conjecture_engine.py:
  bodies not read [UNKNOWN].
Use by the five seats: Talos reads prometheus_math/ as TEXT for its corpus
(agents/talos/daemon.py:162-163, stream weight 0.20) and its September
measurements found prometheus_math tests the only family that is mostly
executable and semantically real [RESULT-UNVERIFIED]
(roles/Talos/ledgers/SEMANTIC_SAMPLE_2026-09-11.md); Arachne, Icarus, Nous,
Koios: no reference found [CODE-INFERRED, grep]. Talos corpus README cites
prometheus_math/lehmer/in_band.py, which is not in the tracked tree [IMPL].
Coverage: not read -- most tests, most *_RESULTS.md, substrate_generation,
databases internals, the bodies listed above.
