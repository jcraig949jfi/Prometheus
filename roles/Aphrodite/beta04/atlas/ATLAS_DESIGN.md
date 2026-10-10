# REACHABILITY-DESERT ATLAS (Beta-04, Experiment 2): design, API, calibration

Author: the ATLAS lead (Aphrodite Beta-04, C-015). Branch `aphrodite/b04-atlas`. Code in
`roles/Aphrodite/beta04/atlas/`, built on the TFS-1 substrate (`tfs1/`, imported, not modified).

- **Contract.** Tasks are consumed ONLY as contract task JSON (EXPERIMENT_PLAN s1). `beta04/foundry/` was not read.
- **Status.** BUILT; tests **14 PASS / 0 FAIL** (`ATLAS_TEST_RESULTS.json`); end-to-end calibration on four PLANTED
  toys plus an atlas-pipeline pass on 6 FOUNDRY pilot task JSONs (`ATLAS_CALIBRATION_RESULT.json`, per-part files in
  `calibration/`). This is an **instrument build and
  calibration, not discovery**. `REACHABILITY_ATLAS_COMPLETE` needs FOUNDRY-admitted R2/R3 tasks, the coordinator's
  freeze of s7, and A/B interpreter conformance (TFS-1 L8).
- **Forbidden words honoured.** "Go-Explore" is not used. Restoring a program is a **genotype copy**; the only
  **state restore** is the search-process snapshot used in the restoration test (never in a production arm).

---

## 1. Files

| File | Role |
|---|---|
| `common.py` | Task loading; the information boundary (`LearnerView` = dev + target-free probes; `Certifier` = test + witness + tribunal); credit channels; existence; `final_evaluation` (archive-free) |
| `sample.py` | Uniform sampling from a TFS-1 size class without materialisation; batched static keyed-walk ranks (`ranks_of`) |
| `route.py` | Pruning lattice of a witness under the mutator's own operators; canonical and credit routes; path enumeration; EXACT mutator step probabilities; semantics-preserving synonyms |
| `measure.py` | The atlas measurements per task (s3) and the candidate limit classifier (s5) |
| `descriptors.py` | Descriptors D-BEH / D-CERT / D-RES, controls C-FIT / GENO / TRACE, RAND:K; the outcome-free qualification test (s4) |
| `arms.py` | The unified burst driver; one-factor arms A/B1/B2/B3 and random controls C3/C2; archive entries; snapshots; outcome-blind K calibration (s6) |
| `toys.py` | Planted calibration tasks (labelled) |
| `calibration.py` | End-to-end calibration runner (parts `atlas`, `qual`, `arms`, `scale`, `scale2`, `ladder`; `--summary`) |
| `pilot.py` | The atlas + qualification + D1 ladder on FOUNDRY pilot task JSON (dev-only to search) |
| `costs.py` | Cost per task per arm at 1x -> `calibration/COSTS.json` |
| `tests/run_tests.py` | Instrument tests -> `ATLAS_TEST_RESULTS.json` |

Commands (from `roles/Aphrodite/beta04/`, `OMP_NUM_THREADS=1`, one process each):
`python -m atlas.tests.run_tests` (about 1 CPU-min); `python -m atlas.calibration --toy GRADED --part atlas|qual|arms|scale`;
`python -m atlas.calibration --summary`.

## 2. API

```python
from atlas import common as K, measure as M, descriptors as D, arms as A
task = K.load_task("family.json")                        # contract JSON (witness optional)
rec  = M.atlas(task, lib=None, seeds=(0,1,2,3), enum_budget=..., enum_max_size=8, density_max_n=7, robust_n=1000)
lab  = M.classify(rec, budget=B, scale=16, arm_results=None)          # candidate labels (s5)
q    = D.qualify(task, task["witness"], lib)                           # outcome-free descriptor test (s4)
k    = A.calibrate_random_k(task, lib, "B3-CELLADMIT", "D-BEH", B, seeds=(1000,1001,1002))   # outcome-blind
r    = A.run_arm(task, lib, "B3-CELLADMIT", seed, B, descriptor="D-BEH", burst=10, stop_on_hit=True,
                 watch=None, credit="exact")                           # one arm run, final evaluation attached
fe   = K.final_evaluation(r["program"], task, lib)                     # program ALONE, fresh tribunal
```
`run_arm` result: `hit`, `hit_charge`, `program`, `first_false_hits`, `decision_log_sha256`, `first_visit_route`,
`mechanisms` (qualified skeletons with first charge, qualified genotypes, dev-correctness patterns seen), `archive`
(entries, live entries, realised cells, replacements), the **four-row cognitive ledger** (`organism`,
`developmental`, `search`, `certifier`), `archive_assisted_discovery` and `autonomous_competence`.
`A.Search(...)` exposes `step()`, `snapshot()`, `restore_state()`, `lineage(entry_id)`, `entries`.

## 3. Definitions (atlas measurements)

**Information boundary.** Searches and archives see a `LearnerView`: family id, output type, dev examples (inputs and
outputs) and 8 **target-free probe inputs** derived only from dev-input statistics (length and value range, keyed RNG).
Test outputs, the witness and the tribunal live only in the `Certifier`, which is consulted for a dev-consistent
candidate and whose answer only decides whether a run stops (tested, s8).

| Quantity | Definition |
|---|---|
| QUALIFIED | correct on ALL test examples AND equal to the witness, value-or-FAIL, on every tribunal input (empty, length 1, extremes, length 16, 24 random lists over a widened range). No witness -> test only |
| existence | the witness parses, type-checks at the output type, and is correct on dev and test |
| hitting cost (enumeration) | charges of the keyed TFS-1 walk to the first QUALIFIED program, per CRN seed (slot = family_id); the first dev-consistent-but-spurious hits are listed with their charges; static witness rank via `ranks_of` (classes > 7M members reported as a bracket) |
| credit channels | **exact** = # dev examples exactly right (the search's credit); **partial** = mean per-example positional match (List) / exact (Int, Bool); **magnitude** (diagnostic only) = mean 1/(1+log2(1+\|err\|)) |
| viable intermediate | exact dev credit in [1, \|dev\|-1] (dev-consistent on a non-empty proper subset). Density per size class (exhaustive up to 100k members, else 5,000 uniform samples), plus all-FAIL share, dev-consistent count and qualified-among-dev-consistent |
| pruning lattice | every program reachable from the witness by PRUNE moves, each the exact inverse of one forward mutation (reverse-replace: a value subterm of size 2..max_fill becomes a same-type leaf; reverse-insert: op(..a_i..) -> a_i when the other arguments have size <= max_fill-1). Every lattice edge is a single forward mutation (tested). These are route intermediates **under the arm's own operator** (Nyx M2), not witness prefixes |
| routes | `canonical` (greedy max-shrink, structure-only tie-break) and `best_for_<channel>` (exhaustive over all lattice paths: smallest crossing estimate in that channel) |
| step probability | EXACT probability that one mutation attempt on the parent yields the child (sum over operator x site x random choices); `p_eff = p_single / (1 - p_none)` with `p_none` sampled (1,000 attempts). Tested against empirical frequencies (60k draws per step, \|z\| < 2.6) |
| feedback gradient | per route step: exact / partial / magnitude credit. An **unrewarded segment** = consecutive steps with no strict credit increase, closed by the first rewarded step. `widest_unrewarded_segment` (steps); `crossing_cost_estimate` = max over segments of 1/prod(p_eff) -- a directed-walk ESTIMATE, not a hitting time, and lattice-relative (search can and does use routes outside the lattice) |
| mutation robustness | 1,000 single mutations of the witness and of each canonical-route program: share that stay QUALIFIED, keep / raise exact credit, are all-FAIL, keep the identical dev behaviour |
| revisitability | genotype restore exactness (re-evaluating the stored genotype reproduces the stored outputs); re-encounter cost under enumeration = static rank of every route program; re-encounter probability from its route predecessor = p_eff; per-arm first-visit charge of every route program (`watch`, reporting only) |

## 4. Descriptor qualification (outcome-free; must pass BEFORE a descriptor may guide an archive)

Candidates: **D-BEH** (coarse behavioural fingerprint on the probes: FAIL / sign + log2 bucket / list length + sum
bucket), **D-CERT** (partial-mechanism certificate: per-dev-example credit level 0..3), **D-RES** (residual signature
per dev example: `= F T < > =p =n !`). Must-fail controls **C-FIT** (score bin) and **GENO** (genotype); reference
**TRACE** (exact dev + probe outputs).

**Procedure = the committed C-013 D1 procedure** (`rso/reach/descriptor.py` + PREREGISTRATION s0), PORTED to TFS-1
(their world is not imported; their 0.006 is specific to p1_slice and is not a comparator). Rulers (fixed in
`descriptors.py` before any measurement):
- **R1 separation** = share of (intermediate, equal-exact-score other) pairs put in DIFFERENT cells; PASS >= 0.90.
- **R1c** = R1 on pairs whose TRACE differs (behaviourally distinguishable pairs); reported.
- **R2 invariance** = share of (intermediate, semantics-preserving synonym) pairs in the SAME cell; PASS >= 0.90.
- **QUALIFIED iff R1 PASS and R2 PASS** (the D1 rule), `controls_ok` (C-FIT fails R1 AND GENO fails R2, else VOID),
  and >= 20 pairs each (else INSUFFICIENT).
- Beta-04 addition, reported only: **G** = distinct cells / distinct genotypes over the pool (Nyx A4 over-splitting
  guard), `OVERSPLIT_WARNING` if > 0.50. Not part of the verdict.

Intermediates = the witness's pruning lattice minus W (the TFS-1 analogue of D1's shortest-edit-path intermediates
under the arms' own operator). Others (as D1) = uniform random programs of every size class up to min(8, size(W)+1)
(1,500 per size) + OFF-PATH one- and two-step mutants of the target and of every intermediate (60 per node) + 6,000
short random-walk programs from the generic starts, lattice excluded; 20 equal-score others per intermediate (D1
`per`). Breakdowns by intermediate score and by prune depth (D1's "rows missing").
A descriptor that fails makes any archive arm it guides **INSTRUMENT_UNVALIDATED** on that task.

## 5. Candidate limit classification (`measure.classify`; thresholds are candidates, not frozen)

Two separate verdicts at budget B and scale s = 16:
- **enumeration** (credit-free): crossing point per seed = observed first QUALIFIED hit, else witness rank.
  REACHED (all <= B) / RARITY_LIMIT (all <= sB) / RARITY_LIMIT_BEYOND_16x / UNRESOLVED.
- **local search** (credit-guided mutation), a PREDICTION from the lattice routes: REACHED_PREDICTED
  (exact-channel crossing <= B) / RARITY_LIMIT (<= sB) / CREDIT_LIMIT (exact > sB but a correctness-credit
  alternative channel, `partial`, crosses <= sB) / REACHABILITY_DESERT (no correctness channel crosses; a note is
  added when the magnitude heuristic would). Empirical ordinary-arm hits are attached beside the prediction.
- If a best route does not start at one of the search's generic starts, the prediction omits the approach cost and
  the label is suffixed `_UNANCHORED`. Every route label carries `status = PREDICTION (not calibrated)`: s8.4 shows
  it mislabels the planted DESERT. **The empirical reading (`classify_empirical`, s6) is the instrument.**
- MEASUREMENT_FAILURE: the witness does not verify. REPRESENTATION_LIMIT: the witness is larger than the mutator's
  max_size (not producible by any operator here). No label ever says "impossible" or "unreachable".

## 6. Exploration arms (matched compute; CRN; one factor per contrast)

All arms share one driver. A run is a sequence of **bursts**: a burst starts with a RESTORE (genotype copy), then
L = 10 mutation steps as a neutral chain (move iff not all-FAIL and credit >= current). Every arm: same task view,
same mutator (max_fill 3, max_size 16), same CRN stream start (`rng_for(seed, family_id)`), same start set
(Int: `0`, `(len xs)`, `(sum xs)`; List: `xs`; Bool: `(lt 0 (len xs))`), starts charged once, exactly **1 charge per
evaluated child** (all dev examples evaluated), budget in charges. Restores = ceil((charges - starts)/L) exactly
(A-CHAIN: 1). Tested.

| Arm | Admission | Restore selection | One factor vs |
|---|---|---|---|
| A-ENUM | -- | -- (keyed enumeration) | ordinary search |
| A-FRESH | none | a START program | baseline (restart hill-climbing) |
| A-CHAIN | none | never restores | A-FRESH: no restarts |
| B1-RETAIN | child with credit >= its chain parent (genome retention) | uniform over entries | A-FRESH: RETENTION |
| B2-DESCSEL | as B1 | cell with weight 1/sqrt(1+times chosen), then uniform in cell | B1: SELECTION |
| B3-CELLADMIT | new cell -> admit even if worse; occupied -> replace iff strictly better | uniform over entries (= cells) | B1: ADMISSION |
| C3-RAND | as B3 with RAND:K genotype hash | as B3 | B3: descriptor vs random cells, matched cell count + restore frequency |
| C2-RAND | as B2 with RAND:K | as B2 | B2: same, for selection |

**C-013 D1 ladder** (coordinator addendum; `rso/reach/arms.py` + PREREGISTRATION s3, mapped onto TFS-1; **derived from
Nyx's design (3318a2098) via C-013 D1 (Palamedes)**). One child per parent selection; archive arms keep one elite per
cell, replaced iff f >= f(elite) or the cell is empty:

| Arm | Parent | Child admitted iff | Contrast |
|---|---|---|---|
| D1-chain_strict | current | f(child) > f(parent) | |
| D1-chain_neutral | current | f(child) >= f(parent) (== A-CHAIN) | C1 vs strict: NEUTRAL ACCEPTANCE |
| D1-X1 | elite of a best-scoring cell (ties: cell insertion order -- TFS-1 cell keys are not mutually orderable) | f >= f(parent) | C2 vs chain_neutral: RETENTION |
| D1-X2 | cell weight 1/sqrt(1 + times chosen) | f >= f(parent) | C3 vs X1: COUNT SELECTION |
| D1-X3 | as X2 | f >= f(parent) OR empty cell | C4 vs X2: WORSE INTO NEW CELLS |
| D1-X3G | as X3, RAND:K genotype hash, K matched outcome-blind to X3 | as X3 | C5 X3 vs X3G: CELL STRUCTURE |

Both ladders run side by side: the B-arms keep the operator's "matched restore frequency" design (bursts of L = 10);
the D1 ladder keeps C-013 comparability (L = 1). Paired CRN censored costs, exact sign-flip (one-sided reported).

**Credit-blind control.** `credit="none"` makes a chain accept every non-all-FAIL child: A-CHAIN vs A-CHAIN[none] at
matched compute is the empirical FEEDBACK test (does the search's credit carry it?). `measure.classify_empirical`
turns the chain trio (exact / none / partial) into flags FEEDBACK_USED, ALT_CREDIT_HELPS, DRIFT_CROSSES and a reading
(RARITY_LIMIT-type / CREDIT_LIMIT / REACHABILITY_DESERT / UNRESOLVED_ALL_CENSORED).

**K calibration (outcome-blind):** run the reference descriptor arm with `stop_on_hit=False` and no certifier on
calibration seeds 1000-1002, read only realised cell counts, set K, verify the random arm's realised cells within 5%
(adjust once by the ratio). Restore frequency is matched by construction (same L).

**Archive entries** record: genotype (text + term), cell, exact/partial credit, channel key, acquisition charge,
anchor parent id (full trajectory via `lineage()`), burst index and step, RNG state (sha256 of `getstate()`; full state
with `store_rng=True`), and descendant outcomes (children, admitted children, best child credit, dev-consistent and
qualified descendants, times restored).

**Final evaluation separation.** `archive_assisted_discovery` = the arm found a QUALIFIED program with its archive.
`autonomous_competence` = `final_evaluation(program, task)`: the program alone (the function has no archive or search
argument; tested) on test + a FRESH tribunal (salt FINAL != search salt). The archive is OFF at final evaluation by
construction.

**Scaling hooks.** Any arm at budget m x B (m in 1, 4, 16) with `stop_on_hit=False` records the first qualified charge,
distinct qualified **skeletons** (multiset of base primitives of the expanded program), NEW certified mechanisms
(qualified skeletons whose primitive set is not a superset of an earlier one; `calibration.novel_mechanisms`), distinct
qualified genotypes, distinct dev-correctness patterns, and the new-certified-mechanism rate per 1k charges.

**Credit channel option.** `credit="partial"` (or `"magnitude"`) switches the chain/elite comparisons to that channel
(hits are still dev-exact + QUALIFIED); used to confirm a CREDIT_LIMIT diagnosis empirically.

## 7. Tests (`ATLAS_TEST_RESULTS.json`) -- 14 PASS / 0 FAIL, about 1.5 CPU-min

| Test | Result |
|---|---|
| sampler_uniform_over_class | 3 classes (Int n=4: 658; List n=5: 904; Int n=3 with a 1-entry library: 128), 40 draws/member: support == class, coverage 1.0, chi-square z = 1.32 / -0.36 / 0.81 |
| ranks_of_equals_rank_of | 72 (term, seed) pairs on two tasks incl. a library: batched rank == `Enumerator.rank_of` |
| route_edges_are_legal_mutations_and_step_prob_exact | 41 lattice edges, 0 not a single forward mutation; route steps p_eff vs 60k empirical draws: z = -0.73, -0.65, 2.55 |
| synonyms_are_semantically_identical | 338 synonyms, identical outputs on dev + probes + tribunal |
| determinism_in_process_and_fresh_process | identical decision-log sha256 in process and in a fresh process; another seed differs |
| matched_compute_accounting_exact | 13 arms (incl. the 6 D1-ladder arms) at 2,500 charges: charges == budget, log length == budget - starts, restores == ceil((B - starts)/L) (chains 1; D1 archive arms L = 1), both unit ledgers re-summed independently from the logged genotypes == recorded |
| archive_target_blindness_perturbation | 7 (task, arm) pairs incl. B1, B2, B3, C3, D1-X1, D1-X3 and a library task: test outputs perturbed + witness replaced -> identical decision log AND archive; the perturbation did change the certifier's answers (e.g. 54 vs 0 qualified skeletons) |
| genotype_and_state_restoration | 783 entries: stored genotype re-evaluates to the stored credit and cell, RNG-state hash matches; snapshot at charge 1,700 restored into a NEW Search reproduces the uninterrupted run exactly; genotype-only restore (fresh RNG) diverges |
| random_control_matching | calibration K = 645 (target 605.7 cells; realised 598, within 5%); evaluation seeds B3 vs C3 cells (558, 586), (636, 603), (644, 612) (within 15%); restores equal |
| final_evaluation_is_archive_free | signature (program, task, lib, witness, salt); witness passes, a wrong program fails; FINAL tribunal differs from the search tribunal |
| descriptor_qualification_controls_behave | C-FIT R1 = 0.0 and GENO R2 = 0.0 on two toys (controls_ok) |
| crosscheck_tfs1_toy_hitting_cost | TOY-D2 seed 0 enumeration hitting cost **78,783** == the SUBSTRATE lead's value |
| planted_label_calibration | route PREDICTION labels: GRADED -> RARITY_LIMIT, DESERT -> REACHABILITY_DESERT, CREDIT -> CREDIT_LIMIT (B = 5,000). NB: this checks the predictor reproduces the planted design; s8 shows the prediction is NOT calibrated against the arms |
| empirical_flags_and_blind_control | known-answer flags for synthetic cost vectors (incl. all-censored -> UNRESOLVED); credit-blind chain accounting |

## 8. Calibration (PLANTED toys; instrument calibration, NOT discovery)

Base budget B = 5,000 charges (1x); 4x = 20,000; 16x = 80,000. Arms: CRN seeds 0-7; scaling: seeds 0-3; random-control
K calibration: seeds 1000-1002 (outcome-blind). Descriptor guiding B2/B3/X1-X3: D-BEH. Toys (`toys.py`):
- TOY-D2 = the SUBSTRATE lead's depth-2 toy with P1 promoted (Int);
- GRADED / DESERT = witness `(map (lam x (pow (mul x x) 2)) xs)` with stratified vs |v| >= 2 dev lists;
- CREDIT = `(map (lam x (mod (mul x x) 3)) xs)` with dev built so only per-position (partial) credit exists on the route.

### 8.1 Atlas measurements

| | TOY-D2 | GRADED | DESERT | CREDIT |
|---|---|---|---|---|
| existence | yes (size 6, expanded 16) | yes (7) | yes (7) | yes (7) |
| enumeration hitting cost, seeds 0-7 | 78,783 75,319 26,234 50,779 41,556 50,261 11,573 89,449 (== SUBSTRATE lead) | 13,740 14,003 25,588 47,343 19,818 24,228 17,761 10,865 | 16,601 15,611 16,215 10,496 14,819 9,261 27,516 26,965 | 42,646 29,253 45,297 25,973 17,958 11,480 13,268 27,048 |
| dev-consistent-but-spurious hits | 0 | 0 | 0 | 0 |
| enumeration label at B | RARITY_LIMIT_BEYOND_16x (89,449 > 80k) | RARITY_LIMIT | RARITY_LIMIT | RARITY_LIMIT |
| viable-intermediate share, size 6 / 7 | 0.089 / 0.089 | 0.200 / 0.185 | 0.0005 / 0.0007 | 0.0010 / 0.0011 |
| pruning lattice (nodes / paths) | 16 / 140 | 13 / 30 | 13 / 30 | 13 / 30 |
| canonical route, exact credit | 0, 0, 0, 1 | 0.3, 0.3, 0.6, 1 | 0, 0, 0, 1 | 0, 0, 0, 1 (partial 0, 0, 0.63, 1) |
| route step p_eff | 0.013, 0.0098, 0.00039 | 0.020, 0.0020, 0.00044 | 0.019, 0.0019, 0.00045 | 0.019, 0.0012, 0.0010 |
| crossing estimate exact / partial / magnitude | 7.8e3 / 7.8e3 / 226 | 2.5e4 / 2.5e4 / 2.5e4 | 4.0e7 / 4.0e7 / 953 | 3.9e7 / 1.8e3 / 953 |
| route PREDICTION (local search) | RARITY_LIMIT | RARITY_LIMIT | REACHABILITY_DESERT (+ magnitude note) | CREDIT_LIMIT |
| witness robustness: stay qualified / keep credit | 0.101 / 0.102 | 0.088 / 0.088 | 0.099 / 0.099 | 0.097 / 0.100 |

TOY-D2's best exact route uses an accidental stepping stone `(sum (map (lam x 2) xs))`: 1/8 dev right, because the
dev list [0] maps to 2. The lattice finds such credit when it lies on a pruning path.

### 8.2 Descriptor qualification (C-013 D1 procedure ported; 20 others per intermediate)

R1 separation / R2 invariance, then the verdict:

| Descriptor | TOY-D2 | GRADED | DESERT | CREDIT |
|---|---|---|---|---|
| D-BEH (probe fingerprint) | 0.910 / 1.0 QUALIFIED | **0.775** / 1.0 FAIL | 0.967 / 1.0 QUALIFIED | 0.967 / 1.0 QUALIFIED |
| D-CERT (dev correctness certificate) | **0.000** / 1.0 FAIL | 0.500 / 1.0 FAIL | **0.008** / 1.0 FAIL | 0.650 / 1.0 FAIL |
| D-RES (dev residual signature) | 0.383 / 1.0 FAIL | 0.638 / 1.0 FAIL | 0.646 / 1.0 FAIL | 0.871 / 1.0 FAIL |
| TRACE (reference) R1 | 0.920 | 0.775 | 0.967 | 0.971 |
| controls (C-FIT R1 = 0, GENO R2 = 0) | ok | ok | ok | ok |
| pairs R1 / R2; pool | 300 / 86; 8,540 | 240 / 68; 7,790 | 240 / 68; 7,793 | 240 / 68; 7,728 |

- **The D1 finding reproduces for dev-feedback descriptors.** D-CERT separates route intermediates from equal-score
  programs at **0.000 (TOY-D2) and 0.008 (DESERT)**: every flat-credit intermediate shares the all-zero certificate
  with equal-score junk. A certificate built from the search's own feedback cannot see a desert's stepping stones.
- **D-BEH passes where it does because target-free probes see behaviour the dev score does not.** Its R1 equals
  TRACE's (the finest behaviour descriptor) on every toy, so it is as good as behaviour can be and no better.
- **On GRADED, D-BEH FAILS** because some equal-score others are behaviourally IDENTICAL to intermediates
  (R1c = 1.0).
- G (cells per genotype) is 0.12-0.20, so D-BEH is not a genotype hash in disguise.
- **Status of D-BEH-guided arms:** VALIDATED on TOY-D2, DESERT and CREDIT; **INSTRUMENT_UNVALIDATED on GRADED**.

### 8.3 Exploration arms at 1x (B = 5,000; hits of 8; every hit also passes AUTONOMOUS final evaluation)

| Arm | TOY-D2 | GRADED | DESERT | CREDIT |
|---|---|---|---|---|
| A-FRESH (restarts, L = 10) | 0 | 0 | 0 | 0 |
| A-CHAIN (= D1-chain_neutral) | 0 | **8** (median 1,767) | **4** | 0 |
| A-CHAIN[none] (credit-blind) | 0 | 0 | 0 | 0 |
| A-CHAIN[partial] | 0 | 8 | 4 | **3** |
| B1-RETAIN | 0 | 2 | 0 | 0 |
| B2-DESCSEL (D-BEH) | 0 | 3 | 0 | 0 |
| B3-CELLADMIT (D-BEH) | 0 | 1 | 0 | 0 |
| C3-RAND (K matched to B3) | 0 | 1 | 0 | 0 |
| C2-RAND (K matched to B2) | 0 | 2 | 1 | 0 |
| D1-chain_strict | 0 | 0 | 0 | 0 |
| D1-X1 / X2 / X3 / X3G | 0 / 1 / 0 / 0 | 4 / 2 / 1 / 0 | 5 / 0 / 0 / 2 | 2 / 0 / 0 / 0 |
| random K (C3, C2, X3G) | 866, 800, 1835 | 1028, 229, 1935 | 844, 850, 1893 | 1020, 1050, 1971 |

Key paired contrasts (exact sign-flip, one-sided, n = 8):
- **FEEDBACK (A-CHAIN vs credit-blind):** GRADED 8-0, p = 0.0039; DESERT 4-0, p = 0.0625; TOY-D2 and CREDIT all
  censored.
- **Neutral vs strict (D1 C1):** GRADED 8-0, p = 0.0039; DESERT 4-0, p = 0.0625.
- **Retention:** B1 vs A-FRESH on GRADED 2-0 (p = 0.25). D1 C2 (X1 vs chain_neutral) on GRADED: 2 better, 6 worse.
- **Descriptor vs random cells (B3 vs C3; D1 C5 = X3 vs X3G):** no separation anywhere (at most 1-1 or 0-2).
- **Partial vs exact credit:** CREDIT 3-0 (p = 0.125); GRADED and DESERT tied overall.
- **Empirical readings** (`classify_empirical`, alpha 0.05):
  - GRADED: RARITY_LIMIT-type (feedback used);
  - DESERT and CREDIT: "REACHABILITY_DESERT" at alpha 0.05, but **underpowered** (4-0 and 3-0 can reach at best
    p = 1/16 and 1/8);
  - TOY-D2: UNRESOLVED_ALL_CENSORED.

### 8.4 What the calibration shows (and where the instrument failed)

1. **The route PREDICTOR is NOT calibrated and must not be used alone.**
   - It said DESERT is a desert (crossing estimate 4.0e7). The exact-credit chain crossed it in 4/8 seeds at about
     600-1,900 charges, while the credit-blind chain crossed 0/8.
   - Diagnosis (seed-0 trajectory): the chain climbed on OFF-LATTICE accidental partial credit (programs scoring 1-2
     of 10 dev lists), which the witness lattice cannot see. The hits were other spellings (`(pow x (add 1 3))`,
     `zipw` forms). The planted toy is flat only on its own route, not in the landscape.
   - In the other direction, on the pilots the predictor said RARITY / REACHED for routes whose start is not a search
     start (now flagged `_UNANCHORED`), and nothing was hit.
   - **Use the empirical trio (exact / credit-blind / partial chains) plus 1x/4x/16x scaling as the instrument. Keep
     the route numbers as descriptive geometry.**
2. **The credit-blind control does separate desert from rarity empirically.**
   - GRADED: feedback 8-0 (p = 0.004).
   - DESERT: feedback 4-0 (p = 0.06).
   - CREDIT: feedback 0-0, but partial credit 3-0.
   - TOY-D2 needs more than 1x.
   - Eight seeds are not enough for the weaker cases. The production run needs >= 24 (D1 power: 0/24 vs 6/24 gives
     p = 0.022).
3. **At 1x, no archive arm beat the neutral chain on any toy, and no descriptor archive beat its matched random
   archive.** Restarts (A-FRESH, L = 10) are strictly worse than one chain on these landscapes. Scaling (8.5) shows the
   archive arms catch up only at 16x. This is calibration on toys: it shows the arms are wired and comparable, not
   that archives fail to help on FOUNDRY tasks.
4. **Archive-assisted discovery == autonomous competence on every hit.** The found program alone passes test plus a
   fresh tribunal, so no hit depended on the archive at evaluation. This is expected for genotype archives: the
   archive helps the search and is never part of the evaluated organism.

### 8.5 Scaling (stop_on_hit = False)

Each cell gives success out of 4 seeds at 1x / 4x / 16x, then the mean number of NEW certified mechanisms per run at
the same three budgets:

| Arm | TOY-D2 | GRADED | DESERT | CREDIT |
|---|---|---|---|---|
| A-FRESH | 0/1/3; 0/0.5/1.25 | 0/1/2; 0/0.25/0.5 | 0/0/1; 0/0/0.25 | 0/0/0 |
| A-CHAIN | 0/1/1; 0/1.75/1.75 | 4/4/4; 3.5/7.75/7.75 | 3/4/4; 2.0/4.5/4.5 | 0/2/3; 0/5.75/10.0 |
| B1-RETAIN | 0/0/0 | 0/3/4; 0/1.25/5.25 | 0/0/1; 0/0/0.5 | 0/0/0 |
| B3-CELLADMIT | 0/0/1; 0/0/0.25 | 0/0/4; 0/0/2.75 | 0/1/3; 0/0.5/2.25 | 0/0/1; 0/0/0.5 |
| C3-RAND | 0/0/0 | 1/3/4; 0.5/6.5/13.0 | 0/3/4; 0/2.25/12.0 | 0/2/4; 0/2.0/18.0 |

- **Definition.** A "new certified mechanism" is a QUALIFIED program whose primitive SET is not a superset of an
  earlier qualified one. Raw distinct skeletons are also stored.
- **Caveat: the count is inflated by drift.** It still counts neutral re-spellings that swap primitives (e.g. `gcd x x`
  for `x`), so the chain's and the random archive's mechanism counts are a crude proxy (open decision O9).
- **Depth.** Mechanism DEPTH is 1 throughout, because these arms do no promotion. Per the directive, these toys can
  show only reachability changes, never composition.

### 8.6 FOUNDRY pilot tasks (atlas pipeline only; foundry v1 is NOT_QUALIFIED per 7cd8fc3f4)

Selection: the first R2 and first R3 admitted task of W1, W2 and W3 (origin/main 3491cfd49). Search saw dev only;
4 seeds; B = 5,000.

| Task | size | enumeration (80k, complete through size 6) | lattice nodes | route prediction | D-BEH R1 | arm hits (8 arms x 4 seeds) |
|---|---|---|---|---|---|---|
| W1-F023-R2 | 10 | censored; witness rank in [6.1e7, 6.2e8] | 12 | RARITY_LIMIT_UNANCHORED | 0.900 QUALIFIED | 0 |
| W1-F037-R3 | 16 | censored | 258 | RARITY_LIMIT_UNANCHORED | 0.832 FAIL | 0 |
| W2-F019-R2 | 12 | censored; **2 spurious dev-consistent hits per seed** | 42 | REACHED_PREDICTED_UNANCHORED | 0.817 FAIL | 0 |
| W2-F028-R3 | 18 | censored | 1,276 (200k paths, truncated) | REPRESENTATION_LIMIT (witness > mutator max_size 16) | 0.944 QUALIFIED | 0 |
| W3-F021-R2 | 12 | censored | 89 | REACHABILITY_DESERT_UNANCHORED | 0.734 FAIL | 0 |
| W3-F032-R3 | 14 | censored | 195 | CREDIT_LIMIT | 0.709 FAIL | 0 |

- All 6 witnesses verify (existence).
- D-CERT and D-RES fail on all 6.
- Every empirical reading is UNRESOLVED_ALL_CENSORED at 1x. These tasks need the 4x/16x escalation, which was not run
  (compute cap).

## 9. Costs (M4/HARRY1, Python 3.12, 1 thread; `calibration/COSTS.json`)

CPU seconds for one arm run at 1x (5,000 charges, full budget):

| Arm | TOY-D2 | GRADED | DESERT | CREDIT |
|---|---|---|---|---|
| A-FRESH | 0.47 | 0.59 | 0.67 | 0.62 |
| A-CHAIN | 0.98 | 2.60 | 1.42 | 0.95 |
| B1-RETAIN | 1.59 | 1.07 | 1.39 | 1.45 |
| B2-DESCSEL (+40k probe runs) | 2.09 | 1.52 | 1.66 | 1.96 |
| B3-CELLADMIT (+40k probe runs) | 1.42 | 1.71 | 1.41 | 1.55 |
| C3-RAND | 1.16 | 0.99 | 0.89 | 1.20 |
| C2-RAND | 1.34 | 1.73 | 1.69 | 1.86 |

Per-task part costs (CPU seconds):

| Part | Cost |
|---|---|
| Atlas measurements | 15-18 (toys) |
| Descriptor qualification | 4-5 (toys) |
| Arms part (9 arms x 8 seeds + K calibration) | 118-157 |
| D1 ladder (8 arms x 8 seeds + K calibration) | 232-326 |
| Scaling (5 arms x 4 seeds x 1/4/16x) | 770-950 |
| One pilot task (atlas + qualification + ladder) | 130-200 |

- Throughput is 2-10k charges per CPU-s.
- Descriptor arms make 8 probe runs per charge. These are NOT search charges (O4).
- This lead's total is about 2.5 core-h, at <= 2 workers. One ~10 s smoke run overlapped two workers, so there was
  briefly a 3-process moment.

## 10. Frozen-parameter candidates (NOT frozen; coordinator decision)

| Parameter | Candidate |
|---|---|
| Budget | B = 5,000 charges at 1x; 4x and 16x |
| Burst length L | 10 for the B-arms; 1 for the D1 ladder |
| Mutator | max_fill 3; max_size 16 (**must be >= the largest witness: W2-F028-R3 is 18**) |
| Starts | per output type, as in s6 |
| Descriptor | D-BEH with 8 probes |
| Qualification thresholds | R1 / R2 >= 0.90 (D1); G warning at 0.50 |
| Random-control K | calibrated on seeds 1000-1002, matched within 5% |
| Tribunal | 9 edge inputs + 24 random inputs + the task's own tribunal |
| Seeds | >= 24 per cell for confirmation; 8 for screening |
| Escalation | 1x -> 4x -> 16x only when the certified-mechanism rate rises (Hestia) |

## 11. Risks

- **The route predictor is lattice-relative** (one witness, pruning moves under max_fill 3). It ignores off-route
  credit and equivalent spellings, and it mislabelled the planted DESERT. Mitigation: the empirical trio plus scaling.
- **Power.** n = 8 detects only all-or-nothing contrasts (minimum p = 1/2^nonzero). Use >= 24 seeds per cell.
- **Descriptor ceiling.** D-BEH's R1 equals TRACE's on every toy and pilot: a behaviour descriptor cannot do better
  than behaviour. Where intermediates are behaviourally identical to equal-score others (GRADED), no behaviour
  descriptor can pass R1.
- **Mechanism counting** inflates with neutral drift (8.5).
- **Enumeration horizon.** Size 7-8 at most within a 15-CPU-min run. Every pilot witness (sizes 10-18) is beyond it, so
  enumeration hitting costs on FOUNDRY tasks will be censored, with only rank brackets.
- **Lattice size** grows fast with witness size: 1,276 nodes and > 200k paths at size 18. Path enumeration truncates
  at 200k (flagged).
- **Interpreter conformance** (TFS-1 L8) is still unverified against interpreter A.

## 12. Open decisions

| # | Decision | Choice here |
|---|---|---|
| O1 | Hit definition | first QUALIFIED (test + generated tribunal + task tribunal); spurious dev-consistent hits listed |
| O2 | Search credit channel | exact dev count; `partial` / `magnitude` / `none` available |
| O3 | Tribunal FAIL agreement | required (a candidate must FAIL where the witness FAILs) |
| O4 | Are descriptor probe runs search charges? | no (reported as probe_runs and units in the search ledger) |
| O5 | Route = pruning lattice under the arm's operator; not proven shortest; predictor demoted to descriptive | as built |
| O6 | Label rules and thresholds (crossing <= 16B; alpha 0.05 for empirical flags) | candidates |
| O7 | Primary arm family: B-arms (matched restore frequency, L = 10) or the D1 ladder (L = 1) | both run |
| O8 | D-BEH fails on GRADED because of behavioural duplicates: should R1c (TRACE-differs pairs) be the ruler? | D1 rule (R1) kept |
| O9 | Mechanism identity for the scaling readout | primitive-set antichain (crude); a semantic normaliser is needed |
| O10 | magnitude: credit channel or diagnostic | diagnostic |
| O11 | Mutator max_size vs FOUNDRY witness sizes | 16 (too small for W2-F028-R3) |
| O12 | Run D-BEH-guided arms where D-BEH failed qualification? | run, labelled INSTRUMENT_UNVALIDATED |
