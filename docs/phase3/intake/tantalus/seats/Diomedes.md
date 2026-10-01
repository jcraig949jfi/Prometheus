# Diomedes -- seat dossier

Crawler: Tantalus (worker)
Tree SHA: 21a47402a (origin/main)
Date: 2026-10-01

## Summary

Diomedes is a short-lived (2026-08-24 to 2026-08-26 active; parked 2026-09-02) audit seat whose
self-chosen mandate was "coordinate adequacy": before trusting a measurement, establish whether the
coordinate system it was taken in could have expressed the answer at all. It built no organism and
no world. Its entire engine is a set of small, read-only Python analysis scripts in roles/Diomedes/
that mine one slice of the Theseus failure corpus (generator h1, "kill_neighborhood" counterexample
hunts over knot x elliptic-curve invariant relations) and rank candidate replacement objects with
per-state AUC, logistic regression and (once) gradient boosting. Over five preregistered cycles and
two external review rounds it produced: (1) a type fact -- a state-only representation scores
exactly 0.5000 when asked to rank candidate actions [IMPL]; (2) an instrument finding -- the corpus
records verdicts on vertices, its only "trajectory" field has essentially zero action entropy, and
the kernel's edge opcode was never written [RESULT-UNVERIFIED, from Ergon's corpus scan plus own
sample]; (3) a "relational coordinates" result (cheap arithmetic features of (state, candidate)
reach AUC 0.66-0.74 locally but do not transfer across invariant pairs or relation types)
[RESULT-UNVERIFIED]; and (4) a decisive later correction: a proxy that reconstructs the withheld
invariant from companion invariants and re-applies the benchmark arithmetic reproduces performance
equal to ~41-45% of the local above-chance span, so the "navigational" reading was never separated
from a "sensor for the oracle's hidden variable" reading [CORRECTION]. The thread was closed KILL
(as a program disposition; the preregistered verdict is UNRESOLVED). The seat's most reusable
outputs are methodological: a conditional-headroom / gate-reachability / cluster-bootstrap /
identifiability census module (coordinate_census.py, later found to have a power-of-two bootstrap
defect by Nyx), a frozen preflight for a "representational multiplicity" branch, and a Lean
successor handoff. Alternative coordinate systems were computed only as hand-written arithmetic
feature families and six frozen "transport" maps, four of which were structurally degenerate on the
population.

## 1. Identity, charter and pivots

- Canonical name Diomedes; Claude Code (Opus 5) seat; machine never assigned (ROLE.md S8) [CLAIM].
- v1 (2026-08-24, commit 47323d457, roles/Diomedes/ROLE.md as first committed): "the mechanism
  seat -- model-side falsification of credited reasoning capability", premised on reviving
  Aporia's unrun activation-probing / steering protocol (aporia/docs/reasoning_steering_protocol
  v0.2/v0.3) [INTENT]. Pivoted the same day.
- v2 (8d7a59b62, 2026-08-24): "coordinate adequacy, not white-box mechanism"; two lanes: Lane N
  (navigational coordinates: does the failure record preserve directions needed to navigate
  search?) and Lane M (mechanism coordinates: does task-side behaviour preserve "mechanism"?;
  parked, never attached) [INTENT].
- Bounded autonomous research loop granted by HITL (LOOP_CHARTER.md, 248a36b86) [CLAIM].
- v3 (59e4e4e0e, 2026-08-25): Lane N CLOSED (KILL); seat raises its own retirement (ROLE.md S10).
- 2026-08-26: preflight for Aporia's representational-multiplicity branch (eca6af616 FINAL), Lean
  handoff (cedaad445), coordinate_census.py (67e750d31).
- 2026-09-02: PARKED by James ("We're parking this seat"), not retired (ff5b6c7ac). The parking
  session pivoted to Proteus (BOOTSTRAP.md banner).
- 2026-09-11: base-role adoption (f08c81c66): STATUS, BACKLOG_H0H5.md (22 rows, DIOM-01..22),
  CALIBRATION.md (16 wrong/overstated rows, 4 right rows), planted controls added to the census
  self-test.
- Relationships: consumes Ergon's corpus scan (ergon/probe/ledgers/corpus_scan/full_scan.json)
  and Theseus's corpus (theseus/corpus, ~346 GB, untracked); positions itself upstream of Charon
  (claim), Elenchus (work), Harmonia (instrument). Reviewed by external HITL reviewers; Charon
  issued a parallel correction ("181.4M parent-linked rows are NOT 181.4M decisions", dc838d59e).
  Downstream consumers: Nyx specimen nyx/specimens/diomedes_k0_census/ (chopped the census module,
  found defect F1), alien_circuitry nursery CRUCIBLE-C (8157e9e70, 2026-09-13) which re-used the
  frozen Diomedes h1 population (digest 1b4abb1a) [IMPL from git].

## 2. Engine/system inventory

There is no engine in the substrate/organism sense. Inventory of code (all roles/Diomedes/):

| Name | Paths | Purpose | Execution model / scale |
|---|---|---|---|
| Recon census | recon_census.py -> recon_census.json | stratified sample of theseus/corpus batch-*.jsonl.gz (10 files, <=40k lines each, 360,003 records, 24 cells); edge/vertex census, step_trace entropy | one-shot, read-only [IMPL] |
| h1 harvester + oracle + AUC | cycle001_run.py (harvest(), relation_holds(), auc()) | builds value table (catalog, invariant, object)->value from payloads; extracts h1 parent states with hunter_success, relation in {equal_mod_2, abs_diff_le_3}; pools up to K=100 candidates; exact break label | 12 files x <=150k lines; ~38k parent states, 1,052 objects, 12 value keys [IMPL + RESULT] |
| Harvest cache | harvest_cache.py, harvest_cache_proof.json | cached harvest refused unless digest 1b4abb1a... reproduced | identity proof [IMPL] |
| Preflights | cycle001_preflight.py, cycle005_preflight.py, cycle005_armB_preflight.py, cycle005_q1_headroom_census.py | oracle validation vs corpus holds labels; class balance; conditional headroom census | arithmetic [IMPL] |
| Feature families + scorers | cycle002_run.py (18 relational features over 3 companion invariants + 4 carryovers; logistic), cycle003_run.py (split discriminator, per-pair coefficient cosine), cycle004_run.py (2x2 pair x relation) | candidate ranking | sklearn LogisticRegression, 5 seeds [IMPL] |
| Operator enumeration | cycle005_operator_recovery.py, cycle005_operator_tables.json, cycle005_armA_run.py | recovers 6 integer operators of the b2 generator from data (three-source differential test), enumerates f(g(v))==g(f(v)) over v in -50..50 | exhaustive, 3,276 of 3,636 cells [IMPL] |
| Transport arm | cycle005_armB_run.py (32 KB), cycle005_armB_handcheck.py | frozen T0-T5 coordinate maps, two-sided; 552 ordered cell pairs x 5 seeds; first version OOM at 16.5 GB, rewritten to numpy | heaviest script [IMPL] |
| Review audits | review_response_run.py, review_round2_run.py | proxy reconstruction (ridge, then gradient boosting cross-fitted by object), leave-one-cell-out pooling, cluster bootstrap | [IMPL] |
| K0 instrument | coordinate_census.py (auc, conditional_headroom, gate_reachable, gate_exceeds_error, cluster_bootstrap with own LCG, identifiability_ceiling, car(), _planted_controls, _selftest) | the seat's reusable "standing offer": five arithmetic preflight checks plus enforced verdict enum {ADEQUATE, INADEQUATE, VACUOUS} | self-test only; zero external importers as of 09-11 [IMPL + CLAIM] |

Dependencies: numpy, scikit-learn; read-only access to theseus/corpus (env override
PROMETHEUS_CORPUS added 2026-09-13 by the nursery commit). No LLM, no network, no GPU [IMPL].

## 3. Code architecture and dataflow

theseus/corpus batch files -> harvest() (cycle001_run.py lines ~60-110): every record's
claim_payload contributes (catalog_x, invariant_x, object_x, value_x) to a value table and object
statistics (seen, broke, cells, relations); h1 records with hunter_success and a named varied side
become parent states (rel, side, inv_a, inv_b, obj_a, obj_b, val_a, val_b) [IMPL].
Per seed: for each parent, candidate pool = all objects with a known value for the varied side's
invariant (sampled to K=100 if more); label = relation broken when the candidate replaces the varied
object (exact arithmetic, relation_holds) [IMPL]. Features never read the candidate's tested
invariant (enforced by construction of feats()), but DO read companion invariants of the same
object (cycle002) [IMPL]. Split by invariant pair (T3), within pair (T2), in-sample (T0), or by
(pair, relation) cell (cycle004/005) [IMPL]. Score: tie-averaged rank AUC per state, mean over
states; SE = sd/sqrt(n_states) (later recognised as the wrong unit) [IMPL + CORRECTION].
Code vs docs: the prose says "navigation"; the code ranks one-step substitutions against a
one-step predicate. There is no multi-step search, no successor state, no horizon anywhere in the
code [IMPL]. Cycle 001 "Z_parent" arm is literally auc(lab, [1.0]*len(lab)) -- the exact 0.5000
"type result" is constructed, which the docs acknowledge [IMPL].

## 4. Claimed computational primitive vs actual mechanism

| Engine | Label given | Smallest actual mechanism | Could express | Phenomenon ruler targeted | Could organism do it? | Ruler vs cheap shortcut? |
|---|---|---|---|---|---|---|
| Lane N decomposition (cycles 001-004) | "navigational information", "state-conditional action information I(A*; Z_a | Z_x)" | per-state AUC of a logistic score over <=22 arithmetic features of (parent value, candidate companion values, target value) | which single substitution breaks a parity / bounded-difference relation | whether recorded failure coordinates tell you which move to try next | No organism; a ranker. One-step only | Not at first. Review round 1-2 showed a proxy that predicts the withheld invariant from companions then applies the relation reproduces ~41% (ridge) / ~45% (GBM) of the local above-chance span; per relation ~68% for abs_diff_le_3, ~21% for equal_mod_2 [CORRECTION] |
| Alternative coordinate systems / "relational coordinates" (cycle 002) | "relational coordinates phi(x,a)" | differences, abs differences, parity matches, threshold indicators, quantile-rank deltas over 3 companion invariants | local arithmetic relations between candidate and target on a cheap axis | whether cheap relational coords recover the conditional signal | n/a | Functional-dependency guard (single feature AUC >= 0.90 => CATALOG-DEPENDENCY) did not fire; but the guard is single-feature and could not see a multi-feature reconstruction of the withheld invariant -- exactly what A1 later measured [CODE-INFERRED + CORRECTION] |
| Coordinate transport (cycle 005 Arm B) | "mathematically natural chart change" | T0 identity, T1 score negation, T2 divide difference features by threshold, T3 replace mod 2 by mod m, T4 per-invariant quantile rank, T5 = T2 o T4 | rescaling between invariants of different units | chart mismatch vs intrinsic locality | n/a | Population has one threshold (3) and one modulus (2): T3 is identically identity, T2 acts only across relations, T1 is closed form, declared before measurement (AMENDMENT_2026-08-25b) [IMPL + CLAIM]. Effectively one live transport (T4) |
| Operator commutation landscape (Arm A) | "oracle not transparently encoded in features" | exhaustive enumeration of f(g(v))==g(f(v)) for 6 recovered scalar operators (abs, log2_floor, mod_3, sq_mod_100, ...) | operator-pair commutation | whether the decomposition survives a different oracle form | n/a | Landscape has 0.0265 conditional headroom; untestable by landscape [RESULT-UNVERIFIED] |
| Representational-multiplicity "Diagnose" preflight | "disagreement between two representations localizes a hidden assumption" | design only (PREFLIGHT_representational_multiplicity_2026-08-26.md); no code | -- | -- | never built | design anticipates generator-as-hidden-variable (F2), symbolic differ ceiling (G2, H2), matched-pair movement statistic (F3), pairing-permutation null (F4) [INTENT] |
| K0 census | "coordinate adequacy check" | arithmetic: oracle minus best state-independent ranking; gate inside [lo,hi]; gate vs 2x err; cluster bootstrap; sum_s P(s)/|A(s)| | disqualify populations | instrument-level vacuity | n/a | Self-test with planted controls passes [CLAIM]; Nyx F1: bootstrap degenerate (zero width) when cluster count is a power of two due to LCG low bits; F3 headroom None mislabels VACUOUS as INADEQUATE (nyx/specimens/diomedes_k0_census/FAILURES.md) [CORRECTION] |

## 5. Representation/state architecture

State x = (parent object, tested invariant, relation, the fixed-side value); action a = a candidate
replacement object; Z(x) = recorded corpus fields (kill_pattern, claim_kind, verdict,
convergence_status, method, invariant pair, relation) -- constant across candidates, hence exactly
0.5 [IMPL]. Z(a) = candidate object statistics (break rate, frequency, n_cells, n_rels). Z(x,a) =
the 18 relational features [IMPL]. Proposed but never built: EDGE(x_before, a, x_after,
observations, provenance, context) with two interface-enforced invariants (no generator writes the
epistemic outcome namespace; observations not collapsed to a success bit) -- handed to Techne as a
spec, routing unresolved (AMENDMENT_2026-08-25 S8) [INTENT].

## 6. Organism/player architecture

None found. The "players" are rankers (logistic regression, ridge, gradient boosting). The
navigating process whose records are mined is Theseus's h1 hunter (hunt_budget = 10, varied side
a or b), which is another seat's generator and was not inspected here.

## 7. World/environment architecture (toy scale)

- h1 population: two relation types only (equal_mod_2, abs_diff_le_3) after oracle validation
  excluded divides (0.9915 agreement) and equal (0.9998) [RESULT-UNVERIFIED]. Knot pools hold 52
  objects (exhaustive), EC pools ~1,000 (k=100 sampled). 24 invariant pairs, 12 mixed pairs, 24
  (pair, relation) cells. ~38k states per seed. One-step decision; label is a deterministic
  function of one hidden scalar (the candidate's tested invariant value) and the fixed-side value
  [IMPL]. This is a narrow, nearly memorizable toy: the decision structure is "is |u - t| <= 3" or
  "is u - t even" on a single withheld integer.
- b2 commutation landscape: 6 operators x 6 x 101 values = 3,636 cells; fully enumerable [IMPL].
- Q1 census of other corpus populations: b3 headroom 0.0012, b4 0.0011, c4 and b1 single-class,
  b5 k=2 with 1.4% negatives, c5 same arithmetic oracle family, g5 absent [RESULT-UNVERIFIED].

## 8. Search/training/adaptation mechanism

No search by the seat. Model fitting: logistic regression (max_iter 2000, standardized), ridge,
gradient boosting cross-fitted by object identity (round 2) [IMPL]. Collapse modes recorded:
global model averages near-orthogonal per-pair coefficients (mean cosine 0.0652), so the pooled
model scores below its own best single feature [RESULT-UNVERIFIED]; within-pair models fit across
relation types are anti-predictive on the other relation (B = 0.4885 below chance) [RESULT-UNVERIFIED].

## 9. Measurement/ruler stack

- Primary metric: per-state tie-averaged AUC, chance exactly 0.5 [IMPL].
- Controls on every cycle: ORACLE positive control (1.0000), SHUFFLE cheat control (labels
  permuted within state; 0.4993-0.5005), RANDOM; B1 object-break-rate control for memorization;
  functional-dependency guard (single feature AUC >= 0.90); population digest assertion;
  builder differential (60,640,200 feature values hashed per seed); AUC implementation
  differential; monotone-invariance check; 20 hand-checkable rows at float64 [IMPL/CLAIM].
- Decomposition ladder: chance 0.5000 / recorded coords 0.5560 / best state-independent ranking
  (computed from evaluation-set labels, a diagnostic ceiling, not a baseline) 0.6254 / Z(x,a)
  per pair 0.6600 / per cell 0.7101 (0.7392 on Arm B's row set) / oracle 1.0000 [RESULT-UNVERIFIED].
- Gates: mean - 3 SE vs ceiling; later recognised SE unit error (seed-level SE over re-splits of
  the same 24 cells; cell-clustered CI 52x wider) [CORRECTION].
- Blind spots, as the seat itself later named them: (a) the oracle is a deterministic function of
  a withheld scalar that admissible features partially sense; (b) one threshold and one modulus
  make transport families degenerate; (c) 24 clusters cannot power a Spearman gate; (d) no
  multi-step, horizon or decision-sufficiency test exists anywhere; (e) "state-independent
  ceiling" uses evaluation labels so it is not a deployable baseline [CORRECTION].

## 10. Baselines and controls

Baselines B1 candidate global break-rate (0.5626, the strongest cheap baseline; ties Z_full at
0.5633), B2 frequency (0.4943), B3 catalog adjacency (0.4797, below chance), n_rels, n_cells. Proxy
reconstruction A1 / A1b / A1-NL (reconstruct withheld invariant then apply relation): best 0.5979
(ridge), 0.6075 (GBM; nonlinearity +0.0096). LOCO pooling A2: 0.5646, cluster-bootstrap CI
[0.5097, 0.6200]. Transport recovery A3 cell-clustered CI [-0.0357, 0.2252] [RESULT-UNVERIFIED].
Missing: no successor-state or multi-step baseline; no learned-embedding baseline (deliberately
excluded); no CORAL/optimal-transport T_unsup class (deliberately excluded, deferred to successor).

## 11. Historical experiment campaigns

| Id | Date | Question | Arms / scale | Reported result | Later reinterpretation | Paths / commits | Label |
|---|---|---|---|---|---|---|---|
| RECON | 08-24 | does Prometheus store vertices or edges? | 360,003-record sample + Ergon full scan | step_trace 332,883/332,886 identical steps; sigma.symbols 0 rows; 36.9% of sample are named edges; ~48.4M parent-linked records | Charon: parent-linked rows are an upper bound on decisions, not decisions (dc838d59e); Diomedes renamed "transition corpus" | RECON_2026-08-24_navigational_information.md, recon_census.py; 47323d457 | REPORTED NEGATIVE/NULL (instrument finding) |
| C001 h1 counterfactual hunt | 08-24 | does recorded Z tell which move to make? | ORACLE, SHUFFLE, RANDOM, B1-B3, Z_parent, Z_full; 37,985 states, 5 seeds, held-out invariant pair | REDESIGN-COORDINATES; Z_full 0.5633 = B1 0.5626; Z_parent 0.5000 exactly | "75% of the signal is conditional" retracted as span ratio, not information; H2 narrowed to "this landscape" | CYCLE_001_*; ce8928043, 359ed29bd | MIXED |
| C002 relational coordinates | 08-24 | do cheap relational coords phi(x,a) reach the 0.3746 conditional signal? | PHI_REL (18 feats), PHI_ALL (22), per-feature AUCs | PHI_REL 0.5444 < 0.6254; KILL of global transfer | cycle 003 relocated to transfer failure | CYCLE_002_*; 3041b131f, 2780e5b53 | REPORTED NEGATIVE/NULL |
| C003 split discriminator | 08-24 | coordinates or transfer? | T3_ACROSS, T2_WITHIN, T0, B1_T2; 22 pairs, median 1,002 train states | T2 0.6600 > 0.6254; cosine 0.0652; REDESIGN | later: within-pair lift partly proxy reconstruction | CYCLE_003_*; 1fbc21337, 2d4388668 | LATER OVERTURNED (in interpretation) |
| C004 relation-type confound | 08-24 | pair or relation type? | 2x2 A/B/C/D, 12 mixed pairs, median 754 | A 0.7101, B 0.4885 (below chance), C 0.5349, D 0.4898; BOTH-AXES-MATTER | prereg anchor clause defective (declared) | CYCLE_004_*; 1698d9652, 96d3a9631 | MIXED |
| C005 Arm A | 08-25 | does decomposition survive a non-arithmetic oracle? | b2 commutation, exhaustive | headroom 0.0265; PARK; Q1 unresolved | Q1 census: no population in corpus can answer | CYCLE_005_ARMA_RESULT.md; 7ec9a2836, c4e098043 | INSTRUMENT FAILURE (landscape vacuous) |
| C005 Arm B transport | 08-25 | chart mismatch or locality? | T0-T5 x 552 ordered cell pairs x 5 seeds | best T5 recovery 6.03%; gate shown reachable (94.5% under T4) | "127 SE" withdrawn; CI includes zero; 4 of 6 transports degenerate | CYCLE_005_RESULT_armB_transport.md; e1d7b9ab3, 6213ec529 | INCONCLUSIVE |
| Review round 1 (A1/A2/A3) | 08-25 | is the local signal proxy reconstruction? | proxy, LOCO, cluster bootstrap | A1 PARTIAL 0.5979 (~41% span); A2 0.5646; KILL | round 2: branch selection was post hoc; preregistered verdict UNRESOLVED | REVIEW_RESPONSE_*; b9f0517cd | LATER OVERTURNED (verdict logic) |
| Review round 2 (A1-NL, A1-NL-CORR, A2-BOOT) | 08-25 | nonlinear proxy; does proxy quality track learnability? | GBM cross-fitted by object | 0.6075 PARTIAL; per relation 0.6636 / 0.5515; Spearman gate underpowered (declined); LOCO CI straddles gate | -- | REVIEW_ROUND2_*; ed859c7e4, 24cb8c105 | MIXED |
| Downstream: Nursery CRUCIBLE-C (not this seat) | 09-13 | does quotienting by invariant pair cut cost-to-first-break? | pooled vs canonical-pair vs matched-N, random-class null | C-PASS: 2.69 -> 2.22 (oracle 1.00, random 3.16) | -- | alien_circuitry/nursery/crucibles/RESULTS_C_B.md; 8157e9e70 | REPORTED POSITIVE (other seat) |

## 12. Reported results and later corrections (timelines)

1. "75% of the information is conditional" (SYNTHESIS_001, d9a59e240) -> challenge: AUC spans are
   not information -> correction b3763aa6d -> current: "roughly three quarters of the observed
   improvement from chance to the oracle is unavailable to the best state-independent ranking";
   ranking accuracies only.
2. "Cheap relational coordinates beat the state-independent ceiling" (C003, 0.6600) -> HITL
   review Interpretation 2 ("task construction") -> A1 proxy reproduces ~41% of span (ridge),
   ~45% (GBM) -> round-2 C1: not a decomposition either -> current: "candidate-conditioned
   predictability of a constructed label", not navigational information (REVIEW_ROUND2_CORRECTIONS
   S4) [CORRECTION].
3. "Navigation knowledge is local" (finding 3) -> AMENDMENT 08-25 demoted to PROVISIONAL -> Arm B
   6.03% recovery, then CI [-0.036, 0.225] -> current: PROVISIONAL, untested for joint-distribution
   alignment.
4. "127 SE below the gate" -> A3 cluster bootstrap 52x wider -> withdrawn.
5. "No shared structure" (LOCO) -> A2-BOOT CI straddles gate -> withdrawn; "naive supervised
   pooling adds little under this representation and model family".
6. Thread disposition PARK -> KILL (corpus-as-vehicle) -> round 2: KILL is a program disposition
   justified by the Q1 census; preregistered verdict UNRESOLVED.
7. coordinate_census.py "self-test PASSED" -> Nyx 2026-09-12: cluster_bootstrap zero width for
   power-of-two cluster counts; self-test uses 24 clusters and cannot see it [CORRECTION].
8. Recon corpus-wide counts rely on ergon/probe/ledgers/corpus_scan/full_scan.json; a sibling file
   full_scan.ATK-014-DEFECTIVE-ESTIMATOR.json exists in the same directory, i.e. at least one
   earlier scan estimator was flagged defective [UNKNOWN which numbers Diomedes used; not verified
   by this crawl].

## 13. False-positive archaeology

- The central false-positive class this seat both committed and then exposed: a benchmark whose
  oracle is a deterministic function of a hidden scalar, plus "admissible" features correlated
  with that scalar, manufactures apparent state-action "navigation" with no trajectory semantics
  (REVIEW_ROUND2_CORRECTIONS S6). Strongest for abs_diff_le_3 (coarse numeric band); weakest for
  parity.
- Constructed exactness: the 0.5000 for Z_parent is by construction (constant score); it is a
  type fact, not evidence about the corpus.
- Ceiling computed on evaluation labels (ORACLE_MARGINAL) was at first used as if a baseline.
- Wrong-population statistics (T1 ceiling from cell B quoted for all 552 pairs; aggregate of 288
  objective-changing with 264 coordinate-changing transfers).
- Gates below their own measurement error (LOCO margin 0.0054; Spearman bands 0.3 apart with SE
  0.21).

## 14. Likely false-negative regimes

- "Transport fails" was tested with one substantive map (T4 marginal quantile rank). Joint
  distribution alignment (CORAL, optimal transport on unlabeled target features), invariant-family
  or equivariant representations, factorised relation x invariant models were never run.
- Two relation types, one threshold, one modulus: any law that would transport across thresholds
  or moduli cannot be seen on this population.
- "Locality" and "no pooling" were measured with linear/GBM tabular models on 18 hand features.
- No multi-step or horizon-dependent quantity was ever measured; decision-sufficiency is named
  and untested, so a null on navigation here says nothing about multi-step mathematical search.
- The h1 hunter's own policy (hunt_budget 10) was not modelled; only post hoc candidate pools.

## 15. Phase 3 audit (per engine)

### 15.1 Lane N ranker (cycles 001-005)
a. Representation richness: hierarchy NO; compositional structure NO (fixed feature vector);
   variable binding NO; memory NO; recurrence NO; counterfactual state PARTIAL (the candidate pool
   is a set of counterfactual substitutions, evaluated by the oracle, not represented by the
   ranker); latent variables NO (the withheld invariant is a latent the proxy re-estimates);
   temporal abstraction NO; spatial abstraction NO; reusable substructure NO; dynamic routing NO
   (cell identity used only to choose which model); self-reference NO.
b. Reasoning opportunity: no. The task is a one-step threshold/parity predicate on one withheld
   integer; local pattern matching and estimation of a hidden scalar from correlated companions
   suffice.
c. Shortcut surface: reconstruct the withheld invariant from companion invariants of the same
   object; per-object base rate (B1); per-cell base rate and scale; candidate pool composition.
d. Ruler resolving power: can separate "has a candidate-indexed axis" from "does not" exactly; can
   NOT separate navigation from oracle-variable sensing (shown by A1); 24 clusters limit any
   cross-cell statistic.
e. Scale: ~38k states/seed, k <= 100 candidates, 18-22 features, 24 cells, 5 seeds, 2 relations,
   12 value keys, 1,052 objects; compute ceiling a laptop (one OOM at 16.5 GB fixed by layout).

### 15.2 Arm A operator-commutation enumeration
a. All NO except compositional structure PARTIAL (f o g vs g o f over 6 scalar operators).
b. No: commutation is ~97% determined by operator identity.
c. Operator-pair identity alone reaches 0.9735.
d. Exact (enumeration), but landscape headroom 0.0265 makes it vacuous for the question.
e. 3,636 cells (3,276 enumerated).

### 15.3 coordinate_census.py (K0 instrument)
a. Not a representation; n/a.
b. n/a.
c. Its own cheat path: power-of-two cluster counts give zero bootstrap width, so gate-vs-error
   passes any gate (Nyx F1) [CORRECTION].
d. Arithmetic disqualifier only ("headroom can kill an experiment; it cannot authorise one").
e. Tiny.

### 15.4 Representational-multiplicity Diagnose design (preflight only)
a. Design-level: two representations of one task, closed assumption vocabulary Q, crossed
   q x mechanism factor; nothing implemented.
b. Unknown; never built.
c. Generator idiosyncrasy encoding q; q base rate; surface features; a mechanical differ.
d. Designed with matched-pair movement (structural zero for surface predictors) and a
   pairing-permutation null; never run.
e. n/a.

## 16. Research reports and substantial documents

- RECON_2026-08-24_navigational_information.md -- vertices vs edges; prior art (LON, successor
  representations, empowerment, ATP); minimal decisive experiment.
- CYCLE_001..005 PREREG/RESULT files -- the five cycles.
- SYNTHESIS_001_cycles_001_004.md (+ amendment) -- overreached "75%" synthesis.
- AMENDMENT_2026-08-25_arity_and_transport.md -- "wrong causal arity"; EDGE primitive spec; two
  axis epistemic ladder.
- AMENDMENT_2026-08-25b_armB_specification.md -- degeneracy of T2/T3 declared before measurement.
- HITL_REVIEW_2026-08-25_cycle005_terminal.md -- self-contained external review packet with four
  competing interpretations.
- REVIEW_RESPONSE_PREREG/RESULT, REVIEW_ROUND2_PREREG/RESULT/CORRECTIONS -- the two audit rounds.
- TERMINAL_SYNTHESIS_2026-08-25.md -- charter S14 synthesis (read only by reference here).
- PREFLIGHT_representational_multiplicity_2026-08-26.md -- A-H5 preflight artifacts for Aporia.
- HANDOFF_lean_successor_2026-08-26.md -- Q*_H bounded verified reachability oracle; eight minimum
  artifacts.
- LOOP_CHARTER.md -- bounded autonomous loop rules incl. S20 non-LLM controls.
- PROVENANCE_NOTE_2026-08-25_commit_collision.md -- commits swept into other seats' commits.

## 17. Journals/TODOs/backlogs/pivots/abandoned branches

journal/2026-09-11.md (base-role pass); STATUS.md, STATUS_2026-08-25.md,
STATUS_2026-09-01_rebootstrap.md; BACKLOG_H0H5.md (DIOM-01 done; DIOM-02..15 proposed K0 audits of
other seats' verdicts, e.g. Techne Crucible 3 "every coordinate system scores BELOW random" at
n=54, Harmonia B E6, Harmonia A Gen3C; DIOM-16/17/18 operator XL decisions); CALIBRATION.md;
KICKOFF_PROMPT.md; PENDING_COMMIT_MESSAGE_2026-08-25.txt. Abandoned: v1 mechanism seat (activation
steering), Lane M (never attached), Recommendation C EDGE primitive (unrouted), Lean successor
(unrouted), residual decomposition experiments (filed, not scheduled).

## 18. Dependencies on other engines and seats

Theseus corpus and h1/b-series/c-series generators (data); Ergon corpus scan (corpus-wide shares);
sigma_kernel REWRITE opcode and migration 006 (inspected for row counts); Aporia (H-R1 Hodge
null, failure_signal_protocol, representational-multiplicity branch owner); Techne (EDGE spec
owner); Charon (parallel correction); Nyx and alien_circuitry nursery (consumers).

## 19. Scaling limitations

The population is fixed by the corpus: two validated relations, one threshold, one modulus, 24
clusters. Any cross-cell inference is cluster-limited; scaling seeds does not help. The harness
holds full feature tensors in memory (16.5 GB first attempt; nursery reruns peaked 8.6 GB).

## 20. Lens potential for Phase 3 (descriptive)

- Substrate: logged one-step substitution searches over catalog invariants (knots, elliptic
  curves).
- Organisms: none; rankers over candidate sets.
- Worlds: h1 counterexample-hunt neighbourhoods; b2 operator algebra.
- Pressures: none (offline).
- Phenomenon family: state-conditional action ranking; coordinate transport between local
  charts; representational vacuity.
- Current resolving mechanism: per-state AUC with exact oracle, positive/cheat controls, proxy
  reconstruction baseline, cluster bootstrap, headroom census.
- Likely resolution ceiling: one-step, two relations; cannot exceed "candidate-conditioned
  predictability of a constructed label".
- Noise sources: corpus sampling (12 of 165 files), cell clustering, candidate pool sampling.
- Architectural limit: no successor states, no horizon, oracle is a function of one withheld
  scalar.
- Reusable parts: the decomposition ladder idea (chance / state-independent ceiling / Z(x) /
  Z(x,a) / Z(x,a,x') / oracle); exact-zero Z(x) wiring check; proxy-reconstruction baseline
  cross-fitted by object identity; headroom census; matched-pair movement statistic and
  pairing-permutation null (design); Q*_H reachable-graph sampling design with four declared
  state measures.
- Toy-grade parts: the h1 population itself; the frozen transport family.
- Unknowns: whether the Lean successor would have non-trivial decision-bearing headroom; whether
  joint-distribution transport recovers the gap.

## 21. Open questions / coverage gaps

Read in full: ROLE, BOOTSTRAP, STATUS (all three), KICKOFF, RECON, all cycle preregs/results except
TERMINAL_SYNTHESIS and SYNTHESIS_001 (read by reference only), both amendments, HITL review,
review response result, round-2 corrections, round-2 result (first ~120 lines), PREFLIGHT, HANDOFF,
CALIBRATION, BACKLOG (rows), cycle001_run.py (main), cycle002_run.py (head),
coordinate_census.py (header and function list). Not read: LOOP_CHARTER.md body, the result JSON
files row by row, cycle003/004/armB runner bodies, review_*_run.py bodies, harvest_cache.py,
journal/2026-09-11.md, PROVENANCE_NOTE, REVIEW_*_PREREG bodies. Not verified: any number by
re-execution (no runs were made; theseus/corpus is untracked and was not opened). Not checked:
which corpus_scan estimator the recon used versus the ATK-014-defective file; the Theseus h1
generator code; Evidence Wiki entries. No Atlas seat-level record of Diomedes was found beyond the
DIOM-NN id regex in atlas/classify.py.
