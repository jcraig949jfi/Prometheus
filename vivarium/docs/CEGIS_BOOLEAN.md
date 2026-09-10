# `cegis_boolean_v1` — the search inside the kind

*Vivarium, 2026-09-10. Track A items 5–6. Vivarium owns the kind contract;
Proteus owns the Boolean semantics (`proteus/eval/boolean.py`, `library.py`).*

## Where the adaptive part lives

Inside the kind, and nowhere else. Every input that governs an adaptive choice
is a hashed payload parameter: the candidate policy and its seed, the case
ordering, the caps, the trace bound, the termination rule, and the two artifact
slots. The generic runner sees a kind name and a result and never learns that a
search happened — `viv/executors.py` calls the loop with a payload, a seed and
frozen artifact data, and there is no route back out.

## The sixteen sealed parameters

    target_truth_table   8 chars of 0/1, Proteus's declared order (input 0 MSB)
    grammar_version      pinned; a mismatch is a new experiment, not a new run
    candidate_policy     seeded_enumeration_v1
    candidate_seed       fixes the order; the same in every arm
    max_expr_size        the declared search space
    max_candidates       the allowance
    oracle_call_cap      target labels
    vm_op_cap            the cap the comparison lives on
    trace_bound          witnesses recorded
    vm_ticks             per-case tick budget
    case_ordering        proteus_declared
    termination          first_solution | exhaust_candidates
    seed_probe_count     the probe ALLOWANCE, equal in every arm
    shortfall_rule       report_and_proceed
    source_pack          artifact slot, or null
    component_library    artifact slot, or null

## Four rules that are not negotiable

**`solved` requires full coverage.** All eight assignments expected and all
eight passed. `cases_with_expectation == 8` is asserted.

**No witness is never solved.** Passing the constraint subset means nothing was
found, not that nothing exists. Only the exhaustive check ends the loop
successfully.

**Budget exhaustion has three statuses** — `BUDGET_VM_OPS`,
`BUDGET_ORACLE_CALLS`, `BUDGET_CANDIDATES` — kept apart from
`EXHAUSTED_CANDIDATES`, which means the declared space actually ran out.

**Labels come from the target.** The pack format carries inputs and has nowhere
to put a label, so a wrong source label cannot corrupt a result — it can only
waste a probe.

## The empty input is a declared input

`source_pack: null` and `component_library: null` are values in a hashed
payload, not omitted keys. H0's four cells are four payloads differing in
exactly those two positions, run by one solver runtime — which is what makes
them four cells of one experiment. `Kind.optional_artifact_slots` declares
*which* slots may be null, so "may be empty" is itself a contract rather than a
convention; `artifact_probe_v1`'s slot may not be, because that kind without
its artifact is a broken request and not a control.

## What the caps actually buy, and what they do not

The enumeration order is fixed by the sealed seed, so the first satisfying
candidate is the same expression in every arm. What differs is how far down
that order an arm gets before `vm_op_cap` bites.

**The obvious story about seeding is wrong, and this was measured.** A seeded
constraint that *fires* kills a candidate in one or two VM cases instead of a
full eight-case verification; one that does *not* fire is pure added cost, paid
by every candidate that reaches it. So more constraints are not better
constraints. Seeding four fresh probes cut oracle calls on every target tried,
cut VM ops on the two that solve quickly, and **raised** VM ops by ~47% on the
one that scans its whole space. Both directions are reachable, which is exactly
why H1 is a question.

**The component library also cuts both ways.** Running the four H0 cells at
`vm_op_cap=30000` over six tasks, the hand-built instrument library *solved*
MAJ3 (unreachable at size 5 without it: its solution is nine nodes, and three
frozen subterms make it five) and *lost* XOR3 (its extra leaves enlarge every
size class and push XOR3's solution further down the same enumeration). Both
cells scored 5 of 6 and the aggregate contrast was zero while both were moving.
A solve-rate difference that nets to zero is not evidence of no effect.

## Running the arms

`tools/h1_h0_alpha_demo.py` executes the three H1 arms and four H0 cells end to
end on a development build and reports assigned / attempted / solved /
exhausted / budget / invalid / infrastructure-failure per arm, plus the
per-task matrix. It is a demonstration that the machinery runs, **not** the
alpha: Archaeon issues the task set, the arm assignment, the frozen retrieval
policy and the packs; Harmonia analyses. In particular the tool implements **no
relevance policy** — its two pack arms are `pack_a` and `pack_b` and neither is
claimed to be relevant, because relevance must be ranked by a structural
signature visible equally to all arms and never by the target's own labels.

`G = S11 - S00` and `I = S11 - S10 - S01 + S00` are Harmonia's analyses under
Harmonia's rules. Nothing in this kind computes a contrast, and `outcome_rule`
must not be used to smuggle one in.
