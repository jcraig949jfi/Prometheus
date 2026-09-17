# Preregistration: CRUCIBLE-C and CRUCIBLE-B (frozen 2026-09-13, before any result)

Governing definitions: `alien_circuitry/nursery/CRUCIBLES.md` at commit 86a429e. This file adds only the operational
details those definitions left open. Nothing here is changed after results.

## CRUCIBLE-C (NUR-004 / NUR-001 second ecology)

**Source rows (provenance).** Diomedes h1 counterexample-hunting states, rebuilt by the frozen builder
`roles/Diomedes/cycle002_run.py::build` (imported, not copied) from the identity-proved harvest cache
(`roles/Diomedes/harvest_cache.py::load_verified`), exactly as `cycle003_run.py` does. Seeds
[20260824..20260828] (5, frozen in cycle 001). A state = (current object, invariant pair key = (inv_a, inv_b),
relation, up to K = 100 candidate objects); label per candidate = 1 iff testing it BREAKS the relation (exact,
`cycle001_run.relation_holds`, oracle validated 1.0000 in cycle 001). Features = cycle 002's 22 relational
coordinates over companions (`FEATS`), no carry features (matches cycle 003's T2/T3 arms). States with all-0 or
all-1 labels are excluded by the builder. Pairs with < 200 states are excluded (cycle 003 `MIN_PAIR_STATES`).

**What cycle 003 already established (OBSERVED, not re-litigated).** Within-pair held-state AUC 0.6600 vs
across-pair 0.5444, complete seed separation; break-rate control does not rise; in-sample = held (no overfit).
The pooling-artefact question at the AUC level is therefore answered YES on these rows. CRUCIBLE-C's open
clauses are the two the committed definition makes decisive:

1. **Decision-time observability.** The class key (inv_a, inv_b) and the relation are attributes of the state the
   agent is in when it chooses a candidate; they are in every row before any label is known. OBSERVABLE by
   construction. Recorded, not tested. Relation type is likewise observable; per the committed definition it may be
   used as a class only if observable -> it is, but to avoid multiple testing the PRIMARY class is the pair key alone
   (the committed candidate); pair x relation is reported as SECONDARY only.
2. **Consequential decision.** Does the class-conditional ranking change the search a counterexample hunter
   performs? Operationalised as the exact cost to first break: rank the K candidates by predicted break
   probability, test in that order, count candidates tested until the first label-1 candidate. This is the
   inference-count analogue of HC_D.

**Frozen comparison (per seed, held states within each qualifying pair, 60/40 split by state as in cycle 003):**

- POOLED: one logistic regression (sklearn, default C, same as cycle 003 `fit_eval`) on ALL training states of all
  qualifying pairs; scored on the held states of every pair. Same model family and capacity as CANONICAL.
- CANONICAL: one logistic per pair on that pair's training states; scored on that pair's held states.
- MATCHED-N POOLED (sample-size control): pooled logistic trained on a random subsample of the pooled training
  states of the same size as the median per-pair training set.
- RANDOM-CLASS (committed negative control): states assigned to pseudo-classes of the same sizes as the real pairs
  by a seeded shuffle; one logistic per pseudo-class.
- ORACLE: rank by the true label (cost = 1 at every state). RANDOM: seeded random order. B1: rank by break-rate only.

**Primary metric.** Mean cost-to-first-break on held states, and headroom captured
HC = 1 - (C_method - C_oracle) / (C_pooled - C_oracle) with C_oracle = 1. Secondary: held AUC (to tie to cycle 003).

**Null.** Permutation null on the primary metric: 200 permutations of the state->pair assignment within each seed
(this is the RANDOM-CLASS control repeated), giving the distribution of the CANONICAL-minus-POOLED cost difference
under "classes carry no structure". Report the observed difference and its rank in the null.

**Thresholds (fixed now).** KILL if the CANONICAL cost reduction over POOLED is inside the 95th percentile of the
random-class null, OR if MATCHED-N POOLED matches CANONICAL within one bootstrap SE (then it is sample size, not
structure). PASS if the reduction is outside the null AND exceeds the matched-N control by more than one SE AND HC
>= 0.10 (at least a tenth of the pooled-to-oracle gap). WEAK if outside the null but HC < 0.10. Verdict vocabulary:
C-PASS / C-WEAK / C-KILL / C-INSTRUMENT-FAILURE.

**Multiple testing.** One class definition (pair key). The pair x relation secondary is reported, never used for
the verdict.

## CRUCIBLE-B (NUR-002)

**World.** Frozen T_7 corpus and D chart (`alien_circuitry/ac01d/corpus.py`, hashes in FREEZE.json). Universe,
D, targets, reachability unchanged. Evaluation = the frozen harness (`ac01d/evaluate.py` Context, 300 problems per
held set, budget 40,000, kernel-aware pruning, engine verification).

**Macro mining (frozen).** Mechanism = repeated EXACT generator subsequences on oracle shortest paths. From FIT
problems only (train states x train targets, pair role fit; 2,000 sampled problems with D >= 5, seed 20260912),
compute one oracle shortest path each (D descent, ties by lowest successor out-degree then action index, as in
`metrics.Searcher.oracle`); count all contiguous subsequences of length 2, 3 and 4; take the top k = 6 by count
with the constraint that no selected macro is a prefix/suffix of another selected one. Macro = the composed map;
applying it costs its length in transitions (charged), counts as one action for ordering, and is legal iff every
intermediate step is legal (always, in T_7). Macros never mined from held problems.

**Random-macro control (frozen).** k = 6 random generator sequences drawn with the same length multiset as the mined
set, seed 20260913, excluding the mined set; 3 independent draws reported (mean and each).

**Policies.** Kernel-aware DFS and GBFS (as in v1 baselines) with the action set = 3 generators + macros, ordering by
the frozen KA key (rank distance then action order; macros ordered after generators at equal key). No learned
distance predictor: the test isolates the move set.

**Accounting.** Transitions examined counts every generator application inside a macro; states expanded counts
macro endpoints only; both reported. Path length counts generator steps (a macro of length 3 adds 3). Excess path
vs D. Failures reported separately; any failure disqualifies HC_D on that set.

**Primary metric.** HC_D on transitions vs KA-DFS (C_K) with the oracle (C_O) from the frozen references; on
HELD_STATES, HELD_TARGETS, HELD_BOTH; bootstrap 95% CI over 300 problems.

**Thresholds (fixed now).** KILL if mined macros do not beat the mean of the random-macro draws by more than the
bootstrap CI half-width on HELD_TARGETS and HELD_BOTH, or if mined macros have HC_D <= 0 there. PASS if mined
macros beat random by more than the CI and reach HC_D >= 0.20 on HELD_TARGETS and HELD_BOTH. WEAK if they beat
random but HC_D < 0.20. If random macros beat mined macros, that is recorded as the result (connectivity effect,
NUR-002 killed in T_7).

**Not done.** No macro is tuned after a held result; k, lengths, seeds are fixed above; no distance model is added.
