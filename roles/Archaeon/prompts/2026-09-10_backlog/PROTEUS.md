PROTEUS -- NEXT WORK (operator 2026-09-10, via Archaeon; schema in
roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md; authority in
roles/Archaeon/prompts/2026-09-10_delegation/00_COMMON.md)

OPEN FROM TODAY, IN ORDER
1. H1 BETA TASK UNIVERSE: 3-bit tasks cannot test relevance (8 witnesses,
   K=4, pool = complement of the seeded prefix). Characterise the 4-input
   universe (65,536 functions) for the Boolean library: the size-bounded
   solvable fraction at max_expr_size 5/6/7 (enumerated, not sampled where
   feasible), the witness pool reachable under constant vs per-task
   ordering with K=4 and K=8, and the exhaustive-verification cost (16
   cases). Commit the table; Harmonia sizes beta from it.
2. PER-TASK ORDERING: you shipped seeded_permutation_v1; Vivarium is asked
   to expose an ordering_seed_policy. Provide the fixture that proves a
   per-task ordering reaches all 2^n inputs over a task set and that the
   first-witness rule is unchanged (ordering changes WHICH case is first,
   never what a mismatch is).
3. Z3 PARITY WITH TECHNE: your truth-table oracle is the reference; supply
   the 256-function parity fixture and the counterexample-validation hook
   Techne needs for item 2 of his prompt.
4. TEMPORAL-PROGRAM INTERFACE (H0/H2 1.1): design the finite-input-sequence
   counterexample for the Boolean library (a witness is a sequence, the
   evaluator is stateful across it) with reset, budget and independent-
   oracle fixtures, as a proposal with the exact finite correctness scope
   stated. Not wired; the kind is Vivarium's.
5. PLAYER FOUNDRY V0.5 (your own lane): the V0.4 discovery did not
   replicate and the mutation kernel carried an authored probability
   current; test DETAILED BALANCE on the kernel, not marginal drift, and
   commit the result either way.

THEN THE BACKLOG: roles/Proteus/BACKLOG_H0H5.md, at least 20 items.
Seed it with: B1 library milestones (beta/1.0/1.1 from the design table);
the compile/evaluate parity fixtures per grammar version; a grammar v1
with NOT as a primitive (a new grammar_version, never a change to v0);
the boolean3 substrate's frozen USE_A registry and what a new population
interface needs; the Player Foundry's own ladder; the PR-ID organism_ref
convention applied to Boolean programs.

REPORT: SHA on main and path per item; exact commands.
