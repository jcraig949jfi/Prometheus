# REACHABILITY-DESERT ATLAS (Beta-04, Experiment 2): design, API, calibration

Author: the ATLAS lead (Aphrodite Beta-04, C-015). Branch `aphrodite/b04-atlas`. Code in
`roles/Aphrodite/beta04/atlas/`, built on the TFS-1 substrate (`tfs1/`, imported, not modified).

- **Contract.** Tasks are consumed ONLY as contract task JSON (EXPERIMENT_PLAN s1). `beta04/foundry/` was not read.
- **Status.** BUILT; tests **13 PASS / 0 FAIL** (`ATLAS_TEST_RESULTS.json`); end-to-end calibration on four PLANTED
  toys (`ATLAS_CALIBRATION_RESULT.json`, per-part files in `calibration/`). This is an **instrument build and
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
| `calibration.py` | End-to-end calibration runner (parts `atlas`, `qual`, `arms`, `scale`; `--summary`) |
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

Pre-stated rulers (fixed in `descriptors.py` before any measurement; D1 convention so numbers are comparable to
C-013 D1's ~0.006):
- **R1 separation** = share of (intermediate, equal-exact-score other) pairs put in DIFFERENT cells; PASS >= 0.90.
- **R1c** = R1 on pairs whose TRACE differs (behaviourally distinguishable pairs); reported.
- **R2 invariance** = share of (intermediate, semantics-preserving synonym) pairs in the SAME cell; PASS >= 0.90.
- **G granularity** = distinct cells / distinct genotypes over the pool (over-splitting guard, Nyx A4); PASS <= 0.50.
- >= 20 pairs for R1 and for R2, else INSUFFICIENT; `controls_ok` = C-FIT fails R1 AND GENO fails R2, else VOID.

Intermediates = the witness's pruning lattice minus W. Others = uniform samples of every size class up to
min(8, size(W)+1) (1,500 per size) + 6,000 short random-walk programs from the generic starts, lattice excluded.
A descriptor that fails makes any archive arm it guides **INSTRUMENT_UNVALIDATED** on that task.

## 5. Candidate limit classification (`measure.classify`; thresholds are candidates, not frozen)

Two separate verdicts at budget B and scale s = 16:
- **enumeration** (credit-free): crossing point per seed = observed first QUALIFIED hit, else witness rank.
  REACHED (all <= B) / RARITY_LIMIT (all <= sB) / RARITY_LIMIT_BEYOND_16x / UNRESOLVED.
- **local search** (credit-guided mutation), a PREDICTION from the lattice routes: REACHED_PREDICTED
  (exact-channel crossing <= B) / RARITY_LIMIT (<= sB) / CREDIT_LIMIT (exact > sB but a correctness-credit
  alternative channel, `partial`, crosses <= sB) / REACHABILITY_DESERT (no correctness channel crosses; a note is
  added when the magnitude heuristic would). Empirical ordinary-arm hits are attached beside the prediction.
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
distinct qualified **skeletons** (multiset of base primitives of the expanded program = "certified mechanism"),
distinct qualified genotypes, distinct dev-correctness patterns, and the new-certified-mechanism rate per 1k charges.

**Credit channel option.** `credit="partial"` (or `"magnitude"`) switches the chain/elite comparisons to that channel
(hits are still dev-exact + QUALIFIED); used to confirm a CREDIT_LIMIT diagnosis empirically.

## 7. Tests (`ATLAS_TEST_RESULTS.json`) -- 13 PASS / 0 FAIL, about 1 CPU-min

| Test | Result |
|---|---|
| sampler_uniform_over_class | 3 classes (Int n=4: 658; List n=5: 904; Int n=3 with a 1-entry library: 128), 40 draws/member: support == class, coverage 1.0, chi-square z = 1.32 / -0.36 / 0.81 |
| ranks_of_equals_rank_of | 72 (term, seed) pairs on two tasks incl. a library: batched rank == `Enumerator.rank_of` |
| route_edges_are_legal_mutations_and_step_prob_exact | 41 lattice edges, 0 not a single forward mutation; route steps p_eff vs 60k empirical draws: z = -0.73, -0.65, 2.55 |
| synonyms_are_semantically_identical | 338 synonyms, identical outputs on dev + probes + tribunal |
| determinism_in_process_and_fresh_process | identical decision-log sha256 in process and in a fresh process; another seed differs |
| matched_compute_accounting_exact | 7 arms at 2,500 charges: charges == budget, log length == budget - starts, restores == ceil((B - starts)/10) (A-CHAIN 1), both unit ledgers re-summed independently from the logged genotypes == recorded |
| archive_target_blindness_perturbation | 5 (task, arm) pairs incl. B1, B2, B3, C3 and a library task: test outputs perturbed + witness replaced -> identical decision log AND archive; the perturbation did change the certifier's answers (e.g. 54 vs 0 qualified skeletons) |
| genotype_and_state_restoration | 783 entries: stored genotype re-evaluates to the stored credit and cell, RNG-state hash matches; snapshot at charge 1,700 restored into a NEW Search reproduces the uninterrupted run exactly; genotype-only restore (fresh RNG) diverges |
| random_control_matching | calibration K = 645 (target 605.7 cells; realised 598, within 5%); evaluation seeds B3 vs C3 cells (558, 586), (636, 603), (644, 612) (within 15%); restores equal |
| final_evaluation_is_archive_free | signature (program, task, lib, witness, salt); witness passes, a wrong program fails; FINAL tribunal differs from the search tribunal |
| descriptor_qualification_controls_behave | C-FIT R1 = 0.0 and GENO R2 = 0.0 on two toys (controls_ok) |
| crosscheck_tfs1_toy_hitting_cost | TOY-D2 seed 0 enumeration hitting cost **78,783** == the SUBSTRATE lead's value |
| planted_label_calibration | GRADED -> RARITY_LIMIT, DESERT -> REACHABILITY_DESERT, CREDIT -> CREDIT_LIMIT (local search, B = 5,000) |

CALIBRATION_SECTION_PLACEHOLDER
