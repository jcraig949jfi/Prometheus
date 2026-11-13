# 06 -- Falsification plan

How to tell genuine recursive improvement from optimisation that looks like it. Everything here is a design. No
arm has been run. Thresholds are proposals to be frozen, with a supply screen, before the first confirmatory run.

## 1. The claim under test, in testable parts

| Part | Statement | Level |
|---|---|---|
| C1 | A lifetime of experience leaves durable state that lowers the engine's cost on unseen task families | L1 |
| C2 | Part of that gain is carried by search-and-learning machinery (laws, schemas), not only by vocabulary (library entries), and it exceeds what the same compute buys without learning | L2 |
| C3 | Machinery built in one lifetime is causally used by the improver in the next lifetime to build further machinery that helps | L3 |
| C4 | The gains in C2 and C3 hold on families from an independently written generator and after an environment change | L4 |

Each part has its own controls. A higher part is never inferred from a lower one.

## 2. Custody and independence

| Rule | Mechanism |
|---|---|
| The evaluator is a separate package, run in a separate process, at a commit pinned before any treatment run | `mathesis_eval/`; its code hash is written into every result row |
| The engine never receives test examples, tribunal examples, family names, rungs or verdicts | Redacted arm view, as `roles/Aphrodite/beta04/tfs1/e3/worlds.py` provides. An access log is checked after every lifetime |
| Only a file crosses from engine to evaluator, and its hash is checked on both sides | `tfs1.membrane` export, receipt and verification |
| The engine cannot change evaluation rules, budgets, records or the kernel | The kernel hash is part of the artifact; a mismatch voids the run. The evaluator owns the work meter used for scoring and re-measures; it does not trust the engine's own counts |
| The set of runs is fixed before any outcome | A sealed manifest of (arm, world seed, generation), built with `rso.completeness.manifest.build` and checked with `verify`. A missing or duplicated shard blocks the verdict |
| Exact reproducibility | Every arm is run twice, on two hosts. Artifact hashes and row hashes must be identical. Search order is keyed by hash, not by a generator state (`tfs1.enum.order_key`) |
| No model judges anything | Every label in s7 is a function of counts and one exact test |

## 3. Task families and what is held out

Held-out means held-out **families**, generated from different worlds, never new seeds of a family the engine
practised on.

| Set | Source | Seen by | Purpose |
|---|---|---|---|
| F_practice[g] | Foundry worlds, fresh for each generation g | Engine, dev examples only | Experience |
| F_val | Foundry worlds disjoint from all practice worlds | Engine's acceptance test | The engine's own decisions about itself |
| F_near | Foundry worlds disjoint from both, sealed | Evaluator only | Primary endpoint for C1-C3 |
| F_far | A generator written independently of the foundry, over the same 29 primitives, with a different family grammar | Evaluator only | C4 |
| F_ext | Externally sourced tasks expressible in the contract language (for example integer-sequence and list-function tasks) | Evaluator only | C4, and a check against structure planted by the foundry |
| F_shift | F_near with the input distribution changed (list length, value range) | Evaluator only | C4, environment change |

**Common opportunity set.** Every arm is scored on the same sealed families at the same per-task work budget, and
no family is dropped because some arm already "has" it. This is the repair for the headroom artifact that
explained 80-93% of Aphrodite's R8 deficit (finding F8).

## 4. World admission: can the experiment detect what it is looking for?

No treatment run is interpreted until these pass. They answer the S, W and R axes of
`docs/phase3/PHASE3_CHALLENGES.md` Challenge 1.

| Gate | Test | Pass rule |
|---|---|---|
| W1 world demand | Foundry null ladder on every admitted family (constant, lookup, reactive, history, fixed library, small search) | Every null fails on test; the known positive passes |
| W2 layered structure exists | A **reference artifact** built by hand: the world's true level-1 mechanisms as entries, plus hand-written laws about them | The reference artifact solves at least a preregistered number of rung-3 and rung-4 families that the frozen baseline does not, at the evaluation budget. If it cannot, no learned artifact could, and a null would be about the world |
| W3 second level exists | The same with a hand-built depth-2 reference artifact | It beats the depth-1 reference artifact. Without this, generation 2 has nothing to find and C3 is untestable in this world |
| R1 the ruler can fire | Evaluate the reference artifact through the full pipeline | Labelled as a gain by the frozen rule |
| R2 the ruler can refuse | Evaluate a random library and an inert theory through the full pipeline | Labelled as no gain |
| R3 controls can fail | Run `rso.qualify.falsifiable.audit` on every claim-critical control: `cannot_emit`, `constant_passes`, `oracle_fails`, `reads_answer`, `trusts_derived`, `near_miss_rejected` | No control is impossible by construction; none reads the answer |
| R4 the pipeline resists known counterfeits | Run `rso.adversary` attacks (`drop`, `duplicate`, `rewrite_derived`, `constant_detector`, `scrub_answer`) against the evaluator and the reducer | No SURVIVED verdict. Recorded limitations are listed in the result |
| PW power | A supply screen on worlds not used in the confirmatory run | The number of world seeds gives at least 80% power for the preregistered effect, by simulation from the screen's variance |

W2 and W3 use hand-built artifacts **only as instruments**. They are never offered to the engine. Finding F2 is a
warning here: a supplied component proves the world can pay, and proves nothing about discovery.

## 5. Arms

"Work" is the unified cost of file 04 s3. Every arm's total work is recorded, including failed modifications,
acceptance replays, mining and verification.

| Arm | What it is | The alternative explanation it stands for |
|---|---|---|
| BASE | Generation-0 engine, frozen: plain TFS-1 enumeration, no designer pruning rules | The original fixed baseline |
| BASE+ | BASE with per-task observational-equivalence pruning | "A known search trick with no learning does as well" |
| TREAT | Full engine, G generations of self-modification with inheritance | -- |
| MATCHED | BASE+ given, per sealed task, the evaluation budget plus the lineage's entire lifetime work amortised over the sealed task count | "It was the extra compute" |
| MATCHED-LIFE | One lifetime from generation 0 with budget G x B_gen, self-modification on, no generation boundary | "Generations add nothing over one long lifetime" |
| SHAM-INERT | Every accepted law replaced by a verified law that never fires within the search horizon; every entry by a random body of the same type and size (the existing `RANDOM-LIBRARY` arm); every schema by a random template of the same shape | "Any artifact of this size and shape helps" |
| SHAM-SCRAMBLED | Laws with operators permuted within type | Brackets the other side: a wrong theory should hurt. If it does not, the theory is not being used |
| NO-INHERIT | Every generation starts from the empty artifact; same lifetimes, same work | "Each lifetime re-derives everything; inheritance is idle" |
| PARAM-ONLY | Only production weights adapt; no entries, laws or schemas | "It is parameter tuning" |
| ABLATE-x | The final TREAT artifact with one class removed: laws, schemas, entries, inverse use, normalise-before-compress. Also each item alone, for attribution | "The learned mechanism is not what carries the gain" |
| CLAMP | Generation-1 lifetime in which T_1 and S_1 are available to SEARCH but withheld from PROMOTE and MINE | "Generation 2's new machinery did not need generation 1's machinery" |
| SHUFFLED | Practice families presented in a scrambled order (the existing `SHUFFLED-HISTORY` arm) | "It is exposure, not accumulation" |
| REFERENCE | The hand-built artifact of gate W2 | The ceiling; never a treatment |

The brief's eight required elements map as follows: fixed baseline = BASE; treatment = TREAT; compute-matched =
MATCHED and MATCHED-LIFE; random or sham = SHAM-INERT and SHAM-SCRAMBLED; inheritance disabled = NO-INHERIT;
ablation of the learned improvement mechanism = ABLATE-x and CLAMP; unseen families = F_near, F_far, F_ext;
second-generation test = s6.

## 6. The second-generation test

```
                 lifetime 1                lifetime 2                      scored on F_near
   empty  ---------------------> A_1 ---------------------> A_2(REC)   ---> reach_REC
                                  |
                                  +-- CLAMP lifetime 2 ----> A_2(CLAMP) ---> reach_CLAMP
                                  |
                                  +-- no lifetime 2 ------->  A_1       ---> reach_1
   empty  -- NO-INHERIT, two separate lifetimes ----------->  best of two -> reach_NOINH
   empty  -- MATCHED-LIFE, one lifetime of 2 x B_gen ------>  A_long    ---> reach_LONG
   BASE+ with the lineage's whole work amortised --------------------------> reach_MATCHED
```

`reach` is the number of sealed families solved within the per-task evaluation budget.

Second-generation recursive improvement is supported only if **all** of these hold:

| # | Condition | What it rules out |
|---|---|---|
| G1 | `reach_REC > reach_1` | Generation 2 added nothing |
| G2 | `reach_REC > reach_CLAMP` | The second increment did not need the first generation's machinery in the improver |
| G3 | `reach_REC > reach_NOINH` and `reach_REC > reach_LONG` | Inheritance and the generational structure are idle |
| G4 | `reach_REC > reach_MATCHED` | Compute explains it |
| G5 | At least one L3 event exists (file 05 s5: a helpful law about a learned entry, found by a self-made schema, that the clamped miner does not find at the same budget) | The gain came through a path other than the claimed one |
| G6 | Removing second-order items (schema-found laws about entries; depth-2 entries) from A_2(REC) removes at least a preregistered share of `reach_REC - reach_CLAMP` | The second-order items are present but idle |
| G7 | G1-G4 replicate on a second, independent batch of world seeds | A lucky batch |

G2 is the heart of it. REC and CLAMP have the same first generation, the same search machinery in lifetime 2, the
same practice tasks and the same budget. They differ only in whether the improver may use what the previous
improver made. This is ASTRA's nested criterion (clamp the process that constructs the update process) made
concrete.

## 7. Outcome classification

Two axes. The engineering axis is yes or no. The science axis takes **exactly one** of five labels, decided by
the ordered procedure below, so the labels partition the outcome space. (IQ-NULL's terminal table did not, as
`PHASE3_CHALLENGES.md` records.)

**Engineering axis.**

`ENGINEERING_SUCCESS` iff: every run in the sealed manifest completed; replay is bit-identical on two hosts; the
kernel hash is constant; the access log shows no evaluator-side read; the adversary kit reports no SURVIVED.
It can be YES while the science label is negative.

**Science axis -- ordered procedure.**

```
1. If any admission gate of s4 fails, or SHAM-INERT is labelled a gain, or SHAM-SCRAMBLED is not worse than TREAT,
   or the manifest does not verify, or power gate PW was not met:
        INVALID_OR_INCONCLUSIVE          (record which gate; a null here is about the apparatus)

2. Else if C1 fails:                      RECURSION_NOT_DEMONSTRATED   (reason NO_LEARNING)

3. Else if C2 fails:                      LEARNING_DEMONSTRATED

4. Else if any of G1-G7 fails,
   or generation 2 was not run:           SELF_MODIFICATION_DEMONSTRATED

5. Else:                                  BOUNDED_RECURSIVE_IMPROVEMENT_SUPPORTED
                                          with qualifier TRANSFER = YES | NO | UNTESTED from C4
                                          and DEPTH = the number of generations for which G1-G6 held
```

Alongside the label, every result carries one separate field, `recursion_test`, with the value `UNTESTED`,
`SUPPORTED`, or `NOT_DEMONSTRATED:<reason>`. So a run can be labelled `SELF_MODIFICATION_DEMONSTRATED` with
`recursion_test = NOT_DEMONSTRATED:SATURATED`: second-order improvement was validly tested and did not appear.
The field keeps "we did not look" apart from "we looked and it was not there".

**The tests behind each step.** Units are foundry worlds (independent world seeds), paired across arms. The test
is the exact sign-flip test on paired differences (`tfs1.membrane.flip_test`), one-sided, with Holm correction
inside each family of comparisons. Proposed thresholds, to be frozen after the supply screen:

| Claim | Passes iff |
|---|---|
| C1 | TREAT (generation 1) beats BASE+ on F_near at equal per-task evaluation work, p < 0.05, at least 20 world pairs; and ABLATE-all returns it to BASE+ within the equivalence margin; and SHUFFLED does not beat BASE+ by as much |
| C2 | (a) removing laws and schemas while keeping entries loses at least 25% of TREAT minus BASE+, p < 0.05; (b) TREAT beats MATCHED; (c) TREAT beats PARAM-ONLY; (d) at least one accepted law or schema has origin SELF and non-zero use on F_near |
| C3 | G1-G7 |
| C4 | C2's conditions (a)-(c) hold on F_far and on F_ext, and C2(b) holds on F_shift |

Reasons recorded in `recursion_test = NOT_DEMONSTRATED:<reason>`:

| Reason | Meaning |
|---|---|
| SATURATED | G1 fails: the gain ratio between generations is at or below one |
| IMPROVER_IDLE | G2 fails: REC does not beat CLAMP |
| INHERITANCE_SUBSTITUTES | G3 fails: a fresh start or one long lifetime does as well |
| COMPUTE_EXPLAINED | G4 fails |
| PATH_NOT_USED | G5 or G6 fails: the gain is real but did not pass through schemas |
| NOT_REPLICATED | G7 fails |

## 8. The essential causal questions, each with its test

| Question from the brief | Answered by |
|---|---|
| Did the system change its own improvement machinery? | Diff of T and S between artifacts; provenance tags (SELF, not DESIGNER or PARENT); kernel hash unchanged |
| Did that change produce a measurable benefit? | TREAT against BASE+ on F_near; ABLATE-laws-and-schemas |
| Was the benefit caused by the change? | ABLATE-x per class and per item; SHAM-INERT; SHAM-SCRAMBLED |
| Could the parent have achieved the same under matched compute? | MATCHED and MATCHED-LIFE |
| Did the descendant use its inherited improvement to discover a further useful mechanism? | CLAMP against REC (G2); the L3 event (G5); second-order ablation (G6) |
| Did the result transfer beyond the selection environment? | F_far, F_ext, F_shift |
| Was the discovery endogenous, or designer-supplied? | Provenance tags; generation 0 runs with no designer pruning rules; the REFERENCE artifact is never shown to the engine; the list of designer-supplied operators in file 04 s7 is published with the result |

## 9. What is measured in every run

| Quantity | Why |
|---|---|
| Work (execution units + match units), per phase | The primary cost |
| Search charges | Comparability with every Aphrodite result |
| Wall time, peak memory, per phase | Honest engineering cost; catches work the meter misses |
| Energy, where the host exposes a counter (Linux RAPL) | The brief asks for it where relevant; optional |
| Modifications proposed, accepted, rejected, retracted, with the work each cost | Failed modifications are part of the price |
| Use count of every accepted entry, law and schema, on practice and on F_near | The single-use-library check (file 02 s3) |
| Blamed misses: tasks solved only with the theory off | Soundness of the learned theory |
| Break-even task count: sealed tasks needed before lifetime work is repaid | The economics, reported even when the science fails |
| Provenance tag counts in each artifact | Endogenous versus supplied |

## 10. Measurement artifacts this plan is built to catch

| Artifact | Seen before in | Guard |
|---|---|---|
| Unequal headroom: an arm looks worse because it has less left to learn | Aphrodite R8 (F8) | Common opportunity set; score increments and end states separately |
| An uncharged ledger hides the cost of the mechanism | Beta-04 pruning costs | One meter; evaluator re-measures |
| Budget-relative "capability" that is really a walk-order cliff | ARC3 s1(d) | Report the full reach-versus-budget curve at several budgets, not one point |
| A control that cannot fail | C-013, C-016, C-017 (F14) | Gate R3 |
| Selection on the held-out set | Ares, per the Hestia audit | The engine selects on F_val only; champions are never chosen on F_near |
| Warm-start cache mistaken for learning | D-5: shuffled history kept all the gain | SHUFFLED; NO-INHERIT; artifacts carry no solutions |
| Memorised programs promoted as "abstractions" | Aphrodite's original selector, 11/22 seeds | `closed_args=True`; `RANDOM-LIBRARY`; lookup null in the ladder |
| Planted structure merely recovered | A23: the donor mostly recovered the planted motif | F_far and F_ext; report literal-recovery rate against the foundry's mechanism list |
| A dev-consistent program that is wrong on test | TFS-1 `false_hits` | Solved means correct on sealed test and tribunal, verified by the evaluator |
| Timestamps or counts written from expectation | Several ledger corrections in the record | Rows carry clock times and hashes written by the runner |

## 11. Stop conditions

Frozen before the first run. A stop is a result, not a failure to be worked around.

| Condition | Action |
|---|---|
| Gate W2 fails after one permitted repair round | Stop. The world cannot pay. Report as a world finding |
| Gate W3 fails | Run C1 and C2 only. Declare C3 UNTESTABLE in this world. Do not run generation 2 |
| Prediction PRED-1 of file 05 fails (the miner does not rediscover the foundry's hand-written rules) | Stop and repair the miner. No treatment claims |
| C1 fails at M0 scale with gates passed | Stop the line. The mechanism does not pay for itself even at first order |
| TREAT does not beat BASE+ on total work, although it beats BASE | Stop: the learned theory is a slower way to do per-task pruning |
| Blamed-miss rate above a preregistered ceiling | Halt runs; the theory is unsound; repair verification |
| Gain ratio at or below one for two consecutive generations | Stop adding generations. Label SATURATED. Record the depth reached |
| Any arm's result changes on replay | Halt everything until determinism is restored |
| A threshold or arm definition needs changing after data | Only through a dated amendment, with the old result kept and labelled |

## 12. What this plan cannot establish

- It cannot show open-ended improvement. It tests a fixed number of generations in a finite world.
- It cannot show that the engine discovered its learning procedures. They are supplied, and the plan says so.
- A positive on foundry worlds alone is a positive under constructed recurrence, which is the scope Aphrodite
  attached to A23. Only F_far and F_ext can widen it.
- Thresholds such as "25% of the gap" are judgement calls. They should be argued over before the freeze, not
  after.
