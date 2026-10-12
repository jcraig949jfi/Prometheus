# D1 -- archive-arm ladder on the p1_slice reach world: PREREGISTRATION v1.0.1

Version: v1.0.1 = v1.0.0 (frozen at 307afe4b1, sha256 879efd39) + wording-only amendment A1 (s9). Where A1 restates
a line of s4, s5 or s7, A1 governs; every number in s2-s6 is unchanged.

C-013-T010, Argus[harry1-6417c3ea] (claude-opus-5-5, Q2), 2026-10-10. Frozen by FREEZE_D1.md BEFORE any confirmatory
lineage has been executed. The run is C-013-T012, after Pallas's Q3 challenge (C-013-T011); Pallas receives no outcome
before its challenge set is committed (ruling s4). Authority: Operator Ruling 2026-10-10 s2-s3; directive s5.

DERIVATIVE OF NYX'S DESIGN. The ladder, the cell descriptor C-BEH, the matched genotype-hash baseline and the decision
table are Nyx's (nyx/atlas/experiments/reach_archive/DESIGN_G1_ARCHIVE_ARMS.md, sha256 4600c6a9...; reference
implementation archive_arms.py, sha256 df41a40e...; commit 3318a2098, Nyx[gandalf-d1f90ae1], 2026-10-03), used read
only and cited. The harness is independent and lives in rso/reach/. The world is the FABLE-5.1 prototype
(docs/phase3/design/FABLE-5.1/prototype/p1_slice/, read only, five files pinned by sha256 in rso/reach/_proto.py).

## 0. Exposure (everything the designer had seen when this was frozen)

- RECEIPT_reach.json (prototype, seed 777, 24 lineages, B = 200,000): neutral chain 1/24 at d = 1, 3, 8 and 0/24 at d = 2;
  strict 9/24, 1/24, 0/24, 0/24 at d = 1, 2, 3, 8; margin 24/24 at d = 1, 0/24 beyond; 0 of 2,000,000 random programs
  reach 0.9. This is why d = 1, 3, 8 are used (the operator's "1/24 baseline") and why the chain arms are RE-MEASURED on
  fresh seeds here rather than borrowed.
- Instrument measurements made before the freeze (none is an outcome of any arm): the descriptor qualification
  (DESCRIPTOR_QUALIFICATION.json: every shortest-path intermediate scores 32 or 20 of 126; C-BEH R1 separation 0.006,
  R1c 1.0, R2 1.0; the full action trace separates no better than C-BEH); the timing (TIMING_py.json, TIMING_nb.json,
  NUMBA_DECISION.md); the outcome-blind cell-count calibration (CALIBRATION_B.json: the hit test disabled, so no hit could
  be observed).
- Development lineages. Tests and timing ran every arm on lineages < 0 at toy budgets; no hit/no-hit outcome of any
  development lineage was printed or inspected (tests assert implementation equalities only). EARLIER in development,
  before the frozen-set guard existed, tests executed lineages 1000-1005 of seed 20261010 at budgets <= 26,000 (equality
  assertions only, outcomes not inspected). That seed and range are BURNED: the frozen set below uses a different seed
  and range, and arms.run_reach_lineage refuses lineages >= 0 outside a confirmatory call.

## 1. Question and claim form

Q: On the p1_slice reach world, at a frozen budget, does each of four search ingredients -- (i) neutral acceptance,
(ii) retention of genomes in a behaviour-cell archive, (iii) rarely-visited (count-weighted) parent selection,
(iv) admission of strictly worse genomes into empty cells -- change the rate at which lineages produce a CERTIFIED
builder from a knock-out start; and does the behaviour-cell structure matter beyond a matched structure-free archive?

Claims are relative and rendered only with: arm pair, d set {1, 3, 8}, B = 200,000 proposals, lineages completed per
cell, certification rule, and the Holm-adjusted p. Form: "On p1_slice T5 at B = 200,000 and n = N per distance, arm A
produced certified builders in a/3N lineages vs b/3N for arm B (stratified exact test, Holm-adjusted p = ...)". No claim
about substrates in general, other engines, Go-Explore, or "deserts are crossable".

## 2. World, target, operator, fitness (all unchanged from the prototype)

Target builder_min (organisms.py:96-111). Start: reach.knock_out(target, 8, d, seed=20261001, lineage index) -- d
distinct rows set to NOP (reach.py:78-91); d = 8 is the empty program. Operator: one row replaced, its four fields drawn
from a counter hash (reach.py:105-111; arms._mutate_into). Search fitness: correct BUILD probes on training lives 0..15
(126 probes), wm_mini.probe_fitness semantics. A HIT = an evaluated genome scoring 126/126 on training.

## 3. Arms (one factor between ladder neighbours) and the declared contrast family

| arm | archive / cells | parent | child admitted iff |
|---|---|---|---|
| chain_strict | none | current parent | f(child) > f(parent) |
| chain_neutral | none | current parent | f(child) >= f(parent) |
| X1 | C-BEH cells | elite of a best-scoring cell (ties: ascending cell key, index = floor(u * #ties)) | f(child) >= f(parent) |
| X2 | C-BEH cells | weight 1/sqrt(1 + times chosen), cells in insertion order | f(child) >= f(parent) |
| X3 | C-BEH cells | as X2 | as X2, OR the child's cell is empty |
| X3G | genotype hash mod B_d | as X2 | as X3 |

In every archive arm an admitted child replaces its cell's elite iff f(child) >= f(elite) or the cell is empty
(Nyx archive_arms.py:42-49). C-BEH = the per-type (novel, repeat, probe, other) correct-count vector on the training
block (Nyx DESIGN s3). Parent-selection uniforms come from a separate hash purpose (arms.P_SEL).

Family of five contrasts (each two-sided):

| id | contrast | isolates |
|---|---|---|
| C1 | chain_neutral vs chain_strict | NEUTRAL ACCEPTANCE |
| C2 | X1 vs chain_neutral | RETENTION of genomes (Nyx: "detachment" only in the population-genetic sense) |
| C3 | X2 vs X1 | RARELY-VISITED (count) SELECTION |
| C4 | X3 vs X2 | ADMISSION OF WORSE genomes into NEW behaviour cells (not plateau crossing: >= already admits neutral new cells, Nyx DESIGN s2) |
| C5 | X3 vs X3G | BEHAVIOUR-CELL STRUCTURE vs a structure-free archive of matched size |

## 4. Design (frozen numbers)

- Distances d in {1, 3, 8}; budget B = 200,000 proposals per lineage; N_MAX = 24 lineages per (arm, d).
- Seeds: search seed 20261011 (arms.SEED); lineage j (0..23) starts from knock-out index 5000 + j (arms.LINEAGE0), the
  SAME start for every arm (balanced; shared starts make the unpaired test conservative); mutation stream
  (5000 + j) * 16 + arm_id, purpose 7,000,003 + d; selection uniforms purpose 11,000,003 + d.
- X3G bucket counts (outcome-blind calibration, CALIBRATION_B.json; rule: median final X3 cell count of four
  development lineages at the full budget with the hit test disabled): B_1 = 12,226, B_3 = 12,762, B_8 = 12,388.
- Execution: rso.reach.run_d1 with the numba port (arms_nb.py; exact differential vs the reference). Rounds j = 0..23,
  each round = lineage j of all 18 (arm, d) cells, at most 2 worker processes, NUMBA_NUM_THREADS = 1.
- CPU CAP (outcome-independent stopping): after each completed round, if the summed worker process CPU time (search +
  certification) is >= 3.2 core-hours the run stops; only completed rounds are analysed. Development + calibration used
  ~0.6 core-hours, so the demonstration stays within the 4 core-hour authorization. Worst case at the measured 0.11-0.16
  ms per proposal is 2.6-3.8 core-hours, so a run on a slow or throttled host may stop between rounds 20 and 24.
- MINIMUM: fewer than 12 completed rounds -> no contrast is read (status UNDERPOWERED); every count is still reported.
- Resume: --resume continues at the first missing round; rounds are atomic and deterministic (tests/test_runner.py).

## 5. Certification and controls

- A lineage is a SUCCESS iff its hit is CERTIFIED by certify.py: (1) >= 90% of BUILD probes correct on selection lives
  2000..2063; (2) rulers.class_exclusion PASS (alpha 1e-6) on sealed lives SEALED_BASE+130,000 .. +130,063; (3) the
  independent pure-Python oracle reproduces the sealed counts and the training probe score exactly. Training-perfect
  hits that fail (1) or (2) are failures, reported separately. Training fitness is never read by certify().
- An oracle disagreement (VOID) stops the run: status VOID_INSTRUMENT; nothing is analysed.
- CONTROLS (CONTROLS.json, never pooled): every arm started AT the target (d = 0) must report a seeded hit at
  evaluation 0 that certifies and is NOT counted as a discovery; holder, constant, lookup and the empty program must
  not certify. Any control failure: status VOID_CONTROLS, nothing is analysed.

## 6. Analysis (rso/reach/analyze.py, tests/test_analysis.py)

PRIMARY. For each contrast: the exact conditional test of equal success odds, stratified by d (convolution of the
per-distance hypergeometrics; two-sided by the probability-ordering rule; equals two-sided Fisher for one stratum),
on certified-success counts over the completed rounds. Holm over the five contrasts at family-wise alpha = 0.05. A
contrast SEPARATES iff its Holm-adjusted p <= 0.05; its direction is the sign of the pooled difference. Otherwise:
"NOT SEPARATED at this budget and n", with both arms' counts and upper bounds.

POWER (stats.power; Monte-Carlo, per-distance baseline 1/24, Holm worst-case level 0.01). N = 24: uniform +0.15 -> 0.56,
+0.20 -> 0.82, +0.25 -> 0.94, +0.30 -> 0.99; +0.46 at one distance only -> 0.62. N = 20: 0.45 / 0.71 / 0.88 / 0.96; one
distance 0.50. N = 12: 0.15 / 0.33 / 0.53 / 0.70; one distance 0.22. Empirical size under the null at N = 24: 0.002.
So this design detects a large ingredient effect (about +0.2 per lineage or more); smaller effects will mostly read
NOT SEPARATED, and that reading says nothing stronger than its upper bounds.

SECONDARY (descriptive only; no test, no claim): per (arm, d) certified count with 95% upper bound; rate by budget
checkpoints 2,000 / 20,000 / 200,000; hit times; training-perfect-but-uncertified count; median realised cells and
distinct genomes (cells / distinct = over-splitting, Nyx A4.1); stepping stones -- lineages that EVALUATED a
shortest-path intermediate, lineages that RETAINED one at the end, the most rows restored (lower bounds: exact row
equality); new cells admitted.

## 7. Interpretation rules (frozen; adapted from Nyx DESIGN s5 with the pre-freeze descriptor finding)

| reading | permitted conclusion |
|---|---|
| C1 separates | neutral acceptance changes certified-reach rate on this target at this budget (direction stated) |
| C2 separates, X1 > chain | retaining genomes helps here; "detachment" may be used in the population-genetic sense only |
| C3 separates | count-weighted selection changes the rate beyond retention |
| C4 separates, X3 > X2 | admitting WORSE genomes into new cells helps: the route crosses downhill steps in behaviour space |
| C5 separates, X3 > X3G | the behaviour-cell structure matters beyond archive size; NOT that the descriptor kept stepping stones (s0: shortest-path intermediates are behaviourally invisible; the stepping-stone counts are reported, not inferred) |
| C5 separates, X3G > X3 | a structure-free archive of matched size does better: the descriptor is not what helps |
| C4 or C5 X3 > ... and the stepping-stone counts show no retained intermediate | the gain came from off-path routes or parent diversity, not from preserving shortest-path stones |
| nothing separates | "no ingredient detectably changed the rate at B = 200,000 and n = N"; each arm's upper bound reported; NOT "archives do not help" and NOT "the target is unreachable" |
| any certified hit in any arm | the target is reachable from that start by that search at that budget (a discovery, with its hit time and genome) -- even where contrasts do not separate |

Forbidden in any result: "Go-Explore", "state restoration", "return to state", "impossible", "unreachable", any pooling
of seeded controls with discoveries, any claim beyond p1_slice T5.

## 8. What D1 cannot show

Environment-state restoration (the program is the state). Representation or credit sensitivity (M7, M8; M8 is the next
cheapest informative measurement given s0). Population maintenance around incomplete mechanisms (no population arm).
Effects smaller than the s6 power table. Anything about other engines.

## 9. Amendments

Any change to s2-s7 after FREEZE_D1 and before the run is a versioned amendment committed BEFORE the first confirmatory
lineage, with its reason; the runner refuses to start if any frozen file's hash differs from FROZEN_D1.json. A change
after any confirmatory lineage has run makes the run exploratory and is reported as such.

### Amendment A1 (v1.0.0 -> v1.0.1), wording only -- C-013-T013, Argus[harry1-91546d7d], 2026-10-10

Committed BEFORE the first confirmatory lineage (none has run: no rso/reach/runs/ exists at this commit; seed 20261011
lineages 0..23 untouched). Reason: Pallas's Q3 challenge of the v1.0.0 freeze (C-013-T011,
rso/reach/challenge/D1/REPORT.md, s3 and s4) found the registered test, stopping rule and certification code sound and
nothing blocking, but three s7 rows, one s5 description and one s4 phrase that the frozen ledger cannot support as
written. Authority: operator ruling 2026-10-10 s4 (one bounded repair round); packet C-013-T013. Unchanged, and not
reopened: the arms, seeds, budgets, B_d, the test, alpha, Holm over five, the power table, the CPU cap and its numbers,
the 12-round minimum, the certification rule (90% on lives 2000..2063, sealed PASS, oracle agreement), the controls.
No code that the run executes changes in this amendment; the behavioural tests it adds are listed at the end.

A1.1 (s4, CPU cap; REPORT.md:111-117, F4). For "outcome-independent stopping" read "OUTCOME-SYMMETRIC stopping". The
stop time depends on outcomes (a hit ends a lineage early and only hits are certified, so the CPU spent per round
moves with the round's outcomes; S1 saw N vary 20-22 under the cap). What the test's validity needs is that the
per-round cost is the same symmetric function of all 18 arms' outcomes, so the cap cannot favour an arm; S1 measured
the size under the cap at 0.002-0.027 (<= alpha everywhere).

A1.2 (s5, certification; REPORT.md:121-146, P1 / E2 / E1). (a) The selection lives 2000..2063 (certify.SELECT0,
N_SELECT) are a band of their own: they lie in none of the prototype rulers' declared bands (TRAIN 0..999, SELECT
1000..1999, SEALED >= SEALED_BASE) and are disjoint from training (0..15), from reach.py's confirm block (1000..1063)
and from every sealed block. (b) The sealed class-exclusion ruler is the REPORTING block (the numbers a result quotes
come from lives the search never saw, exposure hygiene), NOT a second discriminator: on every program tried (the
target, 24 synonyms, the impostors, builder(4..8), 24 random programs) the selection gate alone decided, and every
program failing selection had sealed INDETERMINATE or PASS, never FAIL. "Certified" therefore means: at least 90% of
BUILD probes correct on the 64 selection lives AND oracle agreement (with sealed PASS, which has not been observed to
bind). The boundary is a 7-of-8 mechanism: builder(7) scores 449/500 = 89.8% on the selection lives and is
NOT_CERTIFIED by one probe (pinned by tests/test_repair_v101.py). (c) The selection block is not oracle-rechecked
(only the training and sealed blocks are); recorded, not changed.

A1.3 (s6/s7, direction; REPORT.md:84-94, B1 / P4). Every s7 verdict row is a statement POOLED OVER d = {1, 3, 8}:
"X3 > X2" means the pooled certified count of X3 exceeds X2's and the stratified test separates. The result must
print the per-(arm, d) counts (RESULT.json `cells`) beside each separating contrast; where any stratum's direction
opposes the pooled sign, the row's mechanism gloss does not apply at that d and the result says so for that d
(the post-hoc probe posthoc_p4.json shows a separation with two of three strata opposed is possible). s6 unchanged.

A1.4 (s7, rows restated). The table in s7 is read with these rows replacing the v1.0.0 wording; rows not listed are
unchanged (C1, C3, "nothing separates").

| reading | permitted conclusion (v1.0.1) |
|---|---|
| C2 separates, X1 > chain | keeping cell elites with best-cell parent choice raises the pooled certified-reach rate here; NOT that the near-target start is retained (an equal-score same-cell child replaces the elite, arms.py:228-229; REPORT.md:187-190) |
| C4 separates, X3 > X2 | admitting, and preferentially selecting (a new cell enters with chosen = 0, the maximum weight, arms.py:207, 230-231), worse-but-new genomes changes the pooled rate, with an archive several times larger than X2's (B3: X2 at the end held 10-15% of X3's cells). A RATE statement only: D1 records no route (no parent chain, no cells passed through; run_d1.py:64-74, REPORT.md:180-183), so "the route crosses downhill steps" is withdrawn |
| C5 separates, X3 > X3G | the behaviour-cell structure matters beyond FINAL archive size. The X3G control is matched at the END of the budget only: it fills 87-99% of its buckets by b/8 .. b/4 and admits its children almost unfiltered, so its parent pool is larger for most of the run (REPORT.md:166-178); a difference in either direction may be a parent-pool-size or admission-rate effect. NOT that the descriptor kept stepping stones |
| C5 separates, X3G > X3 | a structure-free archive matched in FINAL size does better: the descriptor is not what helps at this budget; the same end-of-budget caveat applies |
| C4 or C5 X3 > ... with the stepping-stone counts | WITHDRAWN as an inferential row. The stone instrument counts a genome on a shortest path only by exact equality of all four fields of every row (arms._path_restored, arms.py:105-130); an exact restoration costs about 1.2 M proposals on average, six times the lineage budget, and development lineages evaluated zero stones under both the exact and a functional predicate (REPORT.md:149-164, B2a / B2b / P3). The counts are reported (s6 secondary) with the sentence "stone counts cannot support or refute path preservation at this budget and operator"; no conclusion about off-path routes or parent diversity is drawn from them. A functional-equivalence stone count may be added later only as a labelled secondary, never as a claim |
| any certified hit in any arm | a CERTIFIED builder (s5 / A1.2: >= 90% on the 64 selection lives, oracle-agreeing) is reachable from that start by that search at that budget -- not necessarily builder_min or a synonym of it (REPORT.md:185-186, F1) |

A1.5 Behavioural pins added with this amendment (rso/reach/tests/test_repair_v101.py; RED evidence
rso/reach/repair_v101/red_rows.jsonl). Each fails on its mutant applied verbatim and passes on the frozen code:
E1 selection reads the selection lives (certify.py:52); E3 Holm, not the raw p, decides SEPARATES (analyze.py:93); E4
--resume counts the CPU already in the ledger (run_d1.py:141); M80 the 90% threshold (certify.py:54) with builder(7)
at 449/500 as the boundary witness. Until v1.0.0 these lines were held only by the hash manifest.
