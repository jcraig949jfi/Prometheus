# REPORT

## 1. WHAT I SET OUT TO TEST
The program claims that what it inherits (operator libraries, failure taxonomies, operators already adapted from earlier engines) is what makes it capable. The sharpest test is to remove all of it and see whether a generic typed enumerator, working from nothing, does as well on the same frontier with the same budget. That whole-stack ablation was recommended but never run.

I ran the smallest honest version I could build within budget:
- **Substrate:** the Apollo blackboard organism. It is the one place in the repository with a mechanically defined frontier: the 20 tasks the known 0.8333 organism abstains on, 5 in each of all_but_n, temporal_ordering, vacuous_truth and consistency_check.
- **Arms:** one built on the inherited Hephaestus library, one that enumerates generic expressions.
- **Endpoints:** the gain over the 0.8333 ceiling, evaluations until the first gain, a mutation battery, and transfer to an independently authored battery.

## 2. WHAT I DID
**Inputs.** I exported code and data with `git archive` from the repository at 6ff2b2f8a (origin/main) into `src/`:
- `apollo/src`
- `apollo/scripts` (o1_enumerate.py for the battery and the known organism)
- `apollo/data/clean_canary_v01.json`
- `agents/hephaestus/src` (forge_primitives.py)
- `apollo/src/hephaestus_ops.py`
- `roles/Charon/apollo_e9/charon_battery_E9.json`. This battery is committed and was already scored once, so it is not sealed; I used it as the independent-authorship heldout.

**Harness.**
- I wrote PREREG.md before any run.
- `ablate.py` is the harness and `extra.py` computes the order statistics.
- **Shared insertion point:** the known body, plus `parse_numbers`, then the candidate, then the known five-guard tail. Adding `parse_numbers` on its own leaves the score at 0.8333.
- **Shared adapter:** a candidate fires only if all the slots it reads are non-empty and no existing route has claimed the task. Its output is routed by type: numbers go to `extreme_number`, booleans to `comparison`, lists of strings to `ordered`. In each case an existing guarded scorer consumes the slot.

**Arm I (inherit): 55 candidates, which set the matched budget.**
- All 25 forge primitives, with every argument binding compatible with the slot types, including permutations of the parsed numbers.
- 11 primitives could not be bound, because no slot carries their input types.
- Plus the 6 already-adapted transformers in hephaestus_ops.
- Two orders:
  - **I-rank:** candidates ranked by how well the failing-category names match each primitive's name and docstring. This stands in for "the failure corpus as proposer".
  - **I-rand:** the mean over 2000 random orders.

**Arm G (generic): a bottom-up typed enumerator with no inherited content.**
- Leaves: n0..n2, len(slot), and optionally the constants 0, 1, 2, True, False.
- Operations: + - * max min, < == &gt;, not.
- Enumerated up to AST size 5: 81,420 raw expressions (28,133 without constants).
- After removing expressions that behave identically on the battery, 239 remain (161 without constants).
- Run at the matched budget of 55 evaluations, and over its whole space.

**Run.** `env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE python3 ablate.py` took 32 s of wall time and 17 s of user CPU, with 68 MB peak memory.

## 3. RESULT
**Baseline:** 100/120. On Charon's 24 tasks in the four frontier categories, the organism gets 0 correct and abstains on all 24.

**Best gain at the matched budget of 55 evaluations:**

| Arm | Best gain | Operator | Mutation battery | Charon all_but_n (6 tasks) |
|---|---|---|---|---|
| I-rank and I-rand | +5/120 | all_but_n(n0,n1), on all_but_n only | swap, off-by-one, negate and identity all 0 | 3 correct, 2 wrong, 1 abstain |
| G without constants | +5/120 | -(n0,n1), the same function | same as arm I | same as arm I |
| G with constants | +8/120 | constant `True` (5 vacuous_truth, 3 consistency_check) | fails: the negated mutant also gains +2 | 7 correct, 5 wrong on vacuous_truth and consistency_check; this only reflects "yes" being the more common answer |

**Evaluations until the first operator that fully solves all_but_n:**

| Arm | Fixed order | Random order (mean) | Chance of finding it within 55 |
|---|---|---|---|
| I-rank | 1 | – | – |
| I-rand | – | 19.0 | 100% |
| G without constants | 10 | 79.9 | 34% |
| G with constants | 15 | 121.6 | 22% |

I-rank's head start is retrieval: the top-ranked primitive is named after the failing category, and both come from the same Hephaestus test taxonomy.

**Other findings.**
- Only one inherited mechanism gains anything: `all_but_n(total, n) = total - n`, a single subtraction. The other positive inherited candidate, fencepost_count, gains one task by coincidence.
- The already-adapted hephaestus_ops never help:
  - parse_rules gains 6 frontier tasks but misfires on 14 and breaks 15 solved ones, a net of -9 in both scorer placements.
  - ordering_resolve breaks 8 solved tasks.
  - The rest do nothing.
- Nothing in either arm touches temporal_ordering, or touches vacuous_truth or consistency_check without guessing. On those tasks the organism parses nothing into any slot.
- The inherited primitives that look relevant (temporal_order, check_transitivity, solve_constraints) cannot be bound, because no parser produces their input types.
- Several generic expressions (n1, the constant 2, n0 - 1) get isolated tasks right by coincidence. Five tasks per category do not pin down the semantics.

**Conclusion.** At matched budget, the inherited machinery does not beat the generic enumerator on this frontier. Both reach the same ceiling with the same function and pass the mutation battery and the independent battery identically. Inheritance only buys faster retrieval through name matching, which is a port or retrieval effect, not synthesis. The only thing that "beats" inheritance is a constant-True counterfeit, and the mutation battery correctly rejects it.

## 4. DID IT RESOLVE THE QUESTION
Partly. On the one substrate with a mechanically defined frontier, the result is a clean null for inheritance: it gives no reachability advantage, only a search-order advantage from retrieval by name.

It is a narrow instance, not the whole-stack ablation:
- The frontier is 20 tasks.
- Three of the four categories are blocked by the parser gap, so the effective test is one category of 5 tasks.
- No learned proposer or LLM minting was used, because the budget is CPU-only on committed inputs.
- The failure corpus was used only to rank candidates.

The question is also partly badly posed:
- The outcome depends heavily on the generic grammar (constants or not, AST depth) and on the shared adapter.
- The frontier and the inherited library share authorship, which biases the comparison toward inheritance, and inheritance still does not win.

## 5. CONSEQUENCES
- **Clean null on this substrate.** The one inherited operator that moves the ceiling is a subtraction that a size-3 generic enumeration finds in 10 evaluations. This fits the earlier result that brute-force enumeration reproduced the evolved organism.
- **False premise for operator ablation here.** The frontier is parsing, not operators: three categories never populate any slot. Operator-proposal ablations are uninformative until the parsers are keyed on meaning rather than surface templates. The earlier independent-battery failure already pointed at this.
- **The home all_but_n tasks are plain subtraction, not "all but" semantics.** Charon's versions show it: both arms fail the tasks that ask for the complement and the task with the numbers in the other order.
- **Harness defect:**
  - The "constant" mutant built from one frontier answer necessarily solves that task (+1/120 in both arms). The rule that all mutants must fail to move the gain needs a tolerance, or the constant should come from a task the operator did not gain.
  - Latent risk: score_by_extreme_number matches by string prefix ("1" matches "13 ..."), which could credit wrong numeric answers.
- **Generic enumerators should run without constants, or with the mutation battery enforced.** Otherwise a constant answer prior shows up as the best operator.
- **Who should know:**
  - Aporia (owner of this experiment ladder): the ablation step now has a first data point, and it is null.
  - Aphrodite: keep the transplant claim separate from any inheritance claim.
  - Crius and Archaeon: the operator library is not the bottleneck on this substrate.
  - Apollo: parsers need to be keyed on meaning, not text templates.

## 6. COST
- About 1.3 hours of my time.
- Under 3 CPU-minutes in total, one process at a time, peak memory under 100 MB.
- Not done:
  - No live or learned proposer, which would need an LLM.
  - No ablation of evolution or of the forge ontology beyond this substrate.
  - No second substrate.
  - No generic enumeration over problem_text, meaning a generic parser grammar. This is the part that would actually test the parser-gap frontier, and it is the natural next step.

## ADDENDUM (sent by the same worker after a late background search; appended verbatim by the orchestrator)

**Addendum to section 5 (CONSEQUENCES):**
- **This reproduces work already on record.** Lexis (`roles/Lexis/notes/STEP1_CEILING_CLOSED_2026-08-25.md` @ origin/main) had already shown that 0.8333 is the exact ceiling of the operators already in the blackboard. It found that all 20 frontier tasks lie outside anything those operators can reach, and that the only composition scoring higher wins by unconditional guessing. My constant-`True` counterfeit (+8/120) is the same effect found independently. The one real gain either arm finds, the subtraction, needs a new operator, and a size-3 generic enumeration finds it as easily as the inherited library does.
- **Aporia's objection to this experiment applies here.** Aporia (`roles/Aporia/resume_aporia.md` @ origin/main, around line 273) warned that a "generic" enumerator still inherits the blackboard type system, the guard grammar, the task families and the scoring harness. Aporia asked for that boundary to be fixed in advance. My PREREG.md did fix it before any run. Both arms share the type system, the guards, the adapter, the battery and `parse_numbers`. Only the operator-proposal layer was removed, meaning the library, the ranking by failure category and the already-adapted operators. So the null holds for the operator layer only. It is not a verdict on the whole stack.

**Addendum to section 4:** "Partly" stands. What I ran is Aporia's preregistered-boundary version, limited to the operator layer.

The five-line summary is unchanged, except that line 1 should add: "this matches Lexis's earlier proof that the 0.8333 ceiling is closed."
