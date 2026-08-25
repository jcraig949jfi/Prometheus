# PREREGISTRATION — IQ-PORT-1

**Integration qualification, NOT a numbered scientific cycle. Zero novelty claim is an
output requirement, not a risk.**

Written 2026-08-25 **before any port code exists**. Governing doctrine:
`aporia/docs/DOCTRINE_counterfeit_battery_and_ladder_2026-08-25.md`.
Ladder position: step 1 of 7. Nothing downstream may run until this emits a terminal state.

---

## 0. Frozen evaluator (evaluation-counterfeit falsifier, §2)

Committed before the run. Any change to these bytes invalidates every number below.

    COMBINED sha256 = 10fa10db9989eb3a79c2039d18b748a83e93f751578ec6d0a0e12717eb0fa5ae

    apollo/src/blackboard.py                   8c907dd287a15122
    apollo/src/blackboard_evolve.py            7ef2904b0cf3ccf2
    apollo/src/blackboard_ops.py               93e7fc488bf82c17
    apollo/src/blackboard_ops_v2.py            ad1c6bd7d8c555bd
    apollo/src/blackboard_ops_r2.py            6e2a3219f80aa73a
    apollo/src/blackboard_ops_compare.py       ee6cff066cad4533
    apollo/data/clean_canary_v01.json          0bc32a590ce2a4ad
    apollo/scripts/composition_gauntlet.py     6fd34a1e26a95be6
    apollo/scripts/inference_canary.py         0dd5b23171cd7ab7
    apollo/scripts/cross_tier_canary.py        ca86c07a9650be8f
    agents/hephaestus/src/forge_primitives.py  2f35c3f5c784952a

**The baseline registry is not edited.** Port ops live in a new, separate module and the
extended pool `C ∪ {p}` is assembled in the measurement harness. `C` is `be.REGISTRY`
verbatim. This is what makes ΔE and IQ-NULL measurable at all.

## 1. Inventory, executed first (`aporia/iq/inventory_battery.py`, run 2026-08-25)

Battery = 120 tasks. canary 50 · synth 30 · inference 20 · cross_tier 20.
Known 0.833 organism re-executed here: **100/120 = 0.8333**, replicating Apollo's figure.

    canary:numeric_comparison       10/10   solved
    canary:numeric_stated_premise   10/10   solved
    canary:transitivity             10/10   solved
    canary:all_but_n                 0/5     ALL ABSTAIN
    canary:temporal_ordering         0/5     ALL ABSTAIN
    canary:vacuous_truth             0/5     ALL ABSTAIN
    canary:consistency_check         0/5     ALL ABSTAIN
    synth:nth_ranked                15/15 · synth:two_stage_count 15/15
    inference:inference_chain       20/20 · cross_tier:cross_tier_rank 20/20

The 5 `all_but_n` prompts are instances of one template — *"There were T items. N were
removed. How many remain?"* — with (T,N) ∈ {(15,1),(49,1),(5,2),(10,5),(13,11)}.
Candidates are number-prefixed strings; the correct candidate's numeric prefix is T−N.

**Recorded now because it constrains SYNTH-1 later, not this step:** `vacuous_truth` has
only **two** distinct prompt strings across its 5 tasks and the correct answer begins
"Yes" in **5/5**; `consistency_check` has **two** prompt strings and answers Yes/Yes/Yes/No/No.
A degenerate "pick the candidate starting with Yes" op would score 5/5 on vacuous_truth.
SYNTH-1 therefore **cannot** be measured on these 5 canary tasks alone.

## 2. The intervention, and its class — fixed mechanically, before the result

Class: **`PORT_EXISTING_CAPABILITY`** (ΔE_port namespace). Provenance: `all_but_n` exists at
`agents/hephaestus/src/forge_primitives.py:359`, is declared in
`apollo/src/primitive_types.py:65` as `({"items":"int","exception":"int"}, "int")`, and is
listed in the `arithmetic` family of both `apollo/src/genome.py:23` and the archived
`apollo/archive/v1/src/genome.py:23`. It is absent from `be.REGISTRY` (27 ops, checked).

Three components will be added to the harness pool:

    parse_all_but_n   NEW CODE. transformer. reads problem_text, writes quantities.
    op_all_but_n      THE PORT. transformer. reads quantities, writes counts.
                      Body must DELEGATE to fp.all_but_n; it may not recompute T-N.
    (tail)            NO NEW SCORER. Reuses the existing op_aggregate_quantities and
                      score_by_aggregate__g from C.

`quantities` is a slot **no operator in C writes** (noted in `blackboard_evolve.py:100`).
`entity_counter` reads it; nothing produces it. The port makes a dead slot live.

## 3. Predicted readings — stated before execution

    P1  footprint of the two new ops = exactly the 5 canary:all_but_n tasks, 0 others
    P2  exhibited pipeline accuracy   0.8333 -> 0.8750   (105/120)
    P3  canary subset                 0.6000 -> 0.7000   (35/50)
    P4  ΔE_port(all_but_n)            = +0.041667 = 5/120, exactly
    P5  single_primitive_baseline     unchanged at 0.0000
    P6  knockout of op_all_but_n      -> back to 0.8333 (Δ = −0.041667)
    P7  knockout of parse_all_but_n   -> back to 0.8333 (Δ = −0.041667)
    P8  all four mutants              -> ΔE = 0.000000, every one
    P9  delegation probe              -> monkeypatching fp.all_but_n to a constant
                                        CHANGES the op's output on all 5 tasks

## 4. Mandatory falsifiers for this class (doctrine §2), each with the input that fails it

**retrieval counterfeit** — is the capability already somewhere accessible? *That is the
claim, not a threat.* Falsifier inverted: the port is void if `all_but_n` turns out to be
reachable inside `C` already. **Fails if** any pipeline over `C` alone solves ≥1 all_but_n
task. Measured directly: all 5 abstain under the ceiling organism, and
`_single_primitive_baseline = 0`.

**parse counterfeit** — is this a representation change wearing a reasoning badge?
Two state injections on the **unmodified ceiling pipeline over `C`**:

    INJ-A  inject quantities = {"total": T, "removed": N}   (the parser's output)
    INJ-B  inject counts     = {"remaining": {"count": T-N}} (the port's output)

**Preregistered branch, verified to partition over INJ-A × INJ-B:**

    B1  INJ-A = 5/5                    -> PARSE_ADAPTER. The port is void; the arithmetic
                                          was already reachable given the parse. STOP.
    B2  INJ-A in [1,4]                 -> PARTIAL. Reclassify and STOP.
    B3  INJ-A = 0 and INJ-B = 5/5      -> PORT_EXISTING_CAPABILITY with a declared parser
                                          dependency. Proceed to IQ-NULL.
    B4  INJ-A = 0 and INJ-B in [0,4]   -> NEW_ROUTING_REQUIRED. The tail is not reusable;
                                          the intervention is larger than a port. STOP.

    Coverage assert (executed, not asserted in prose): INJ-A ∈ {0..5} and INJ-B ∈ {0..5};
    the four branches map every one of the 36 cells to exactly one terminal state.

I expect **B3**. B3 is the *deflationary* reading and I am stating it in advance: it means
ΔE_port here is carried by a NEW PARSER plus a one-line subtraction that already existed.
The port framing survives only because the arithmetic kernel is invoked verbatim.

**answer counterfeit** — mutation battery on the ported kernel. All must give ΔE = 0:

    M1 plus         T + N
    M2 off_by_one   T - N + 1
    M3 swapped      N - T
    M4 identity     T

**composition counterfeit** — leave-one-out knockout across every op of the exhibited
pipeline; report the full vector, not only the two new ops.

**search counterfeit** — n/a for a bound; no evolutionary search is run. Declared.

**budget counterfeit** — the evaluator is deterministic and exhaustive over 120 tasks; the
budget cannot vary. Declared, not measured.

**distribution counterfeit** — **NOT DISCHARGED HERE.** No G-heldout, no X-heldout. It is
TRANSFER-1's job. Any all_but_n number from this step is a 5-task reading and must be
quoted that way.

## 5. Adapter-vs-rewrite test — executed, not inspected

The resume file requires: *if the wrapper is a rewrite rather than an adapter, stop and
reclassify.* Mechanical discriminator, run as code:

> Monkeypatch `fp.all_but_n` to return a constant. Re-run the exhibited pipeline.
> **ADAPTER** iff accuracy collapses to the baseline on the 5 tasks.
> **REWRITE** iff accuracy is unchanged — the op computed the answer itself.

A REWRITE verdict reclassifies the intervention to a mint and **stops the pass** with a
PARK, per the ladder.

## 6. How ΔE is obtained, and the bound's honest limits

A full re-enumeration is out of budget: the O1 run was 1,737,000 evaluations over 15
transformers; the extended pool has 17, and subsets containing both new ops alone number
22,819 before orderings and tails. **This step does not re-enumerate.** Instead:

    ΔE_lower  exhibited: acc(ceiling body + parse_all_but_n + op_all_but_n + same tail)
              minus 0.8333. A witness; certain.
    ΔE_upper  footprint bound: outside the footprint F the new ops leave state identical,
              so any g over C ∪ {p} agrees with g-minus-new-ops there, giving
              acc(g) ≤ E(C) + |F|/120.

**Named weakness of the upper bound:** it requires g-minus-new-ops to be a valid ordering
over `C`. Deleting an op can orphan a downstream read. It is checked mechanically for the
exhibited pipeline only. **ΔE_upper is therefore strength=SUPPORTED, never CERTAIN**, and
the pass reports it that way or not at all.

## 7. Terminal states — exactly one is emitted

    ADVANCE   P1-P9 all hold, branch B3, ADAPTER verdict. IQ-PORT-1 passes; pipeline frozen;
              IQ-NULL is next. Novelty claim recorded as ZERO.
    REDESIGN  a prediction fails in a way attributable to the harness, not the substrate.
    PARK      REWRITE verdict, or branch B1/B2/B4. Reclassify; GATE_ELI5 filed.
    KILL      the port cannot be expressed in the substrate at all.

## 8. Cost-to-falsify ledger — opened BEFORE outcomes are known (doctrine §5)

Per the standing guard, hypotheses are logged with predicted probe cost **now**, and scored
after. Recorded in `aporia/iq/COST_TO_FALSIFY.jsonl`, one row per hypothesis, written at
prediction time.
