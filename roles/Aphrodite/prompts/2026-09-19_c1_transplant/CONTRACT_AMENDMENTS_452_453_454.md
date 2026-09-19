# Aphrodite: amendments to the Campaign 1 contract requests #452 (Archaeon), #453 (Harmonia), #454 (Vivarium)

2026-09-19. Authority: operator relay of 2026-09-19 (RELAY_verbatim.md in
this directory, item 6: "Give Harmonia a hostile adjudication contract
and Vivarium a hostile execution contract before launch"). Campaign 1 is
now preregistered around MECHANISM TRANSPLANTATION:
roles/Aphrodite/science/campaign1/PREREG_C1_TRANSPLANT_2026-09-19.md
(design frozen before any data; execution NOT authorised). Scope is
unchanged: contracts and CPU fixtures only, no production run.

## To Harmonia (#453): make the adjudication contract HOSTILE

Each item below must be a CHEAT FIXTURE the contract demonstrably
catches (a fixture that is not caught is a failed contract, not a
passed test):
1. MEMORY LEAKAGE -- a recipient that receives the donor's state (memory,
   cache, archive, logs) through any path other than the declared
   artifact.
2. EVALUATOR EXPLOITATION -- an improver that reads or infers the
   evaluator's code, tasks or answers, or scores from a side channel.
3. INCREASED BUDGET -- an improver that obtains more tokens or compute than
   its escrow (unmetered call, second model object, raised limits,
   retries outside the policy).
4. TASK MEMORISATION -- performance that depends on having seen the
   specific instances (detected by the fresh-instance and sealed-family
   layers).
5. LINEAGE-ID SHORTCUT -- behaviour keyed to a lineage identifier, seed or
   host label rather than to the task.
Adjudication path: verdicts only from the preregistered analysis code on
committed rows; the contract names who runs it and who countersigns.

## To Vivarium (#454): make the execution contract HOSTILE

1. RESETS PROVEN: a recipient's reset must be shown to destroy forbidden
   state -- a fixture plants a marker in memory, cache, temp files,
   process state and environment, and the reset receipt proves every
   marker is gone before the recipient runs.
2. TRANSPLANT-BOUNDARY RECEIPTS: for every transplant cell, a receipt
   listing exactly what crossed into the recipient (file paths and
   hashes of the declared artifact) and attesting nothing else did.
3. CELLS the preregistration needs: SCRATCH, TRANSPLANT, MEMORY-ONLY, SHAM
   (from the donor's rejected-mutation archive, so rejected diffs must be
   retained), POSITIVE, EQ-COMPUTE, AS-RUN, module swaps; and, for the
   exploratory endpoints, cross-lineage insertion into another lineage's
   evolved agent.

## To Archaeon (#452): one addition to the sealed task-generator contract

A declared REGIME-SHIFT variant for every task family: a change of rules
(e.g. output convention or operator semantics) that retaining the
pre-shift policy cannot solve, applied from generation 5, specified and
hashed before execution. Pre- and post-shift instances must both be
available in the sealed layers (the primary endpoint is measured on
fresh post-shift tasks).
