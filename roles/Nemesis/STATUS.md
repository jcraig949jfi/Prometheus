# Nemesis -- STATUS

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11, after NEMESIS-01. Next update due within four
hours of the next activity.

    seat state        ACTIVE -- first season open; NEMESIS-01 delivered
                      2026-09-11 (attack on the Eos intake gate)
    lane              adversarial input construction against INSTRUMENTS:
                      cheat controls, chance floors, metamorphic
                      perturbation sets, minimal failing inputs
    entry file        roles/Nemesis/RESPONSIBILITIES.md
    worktree          D:\Prometheus-worktrees\nemesis-adopt
    branch            nemesis/eos-scorer-attack-2026-09-11
    base_sha          742a6c8b3
    dirty             no (at the measurements reported here)
    comms             registered this pass; see the boot receipt
    monitors owned    one row, NemesisAdversarialCycle, state DEAD
                      (not relaunched; base rules 8 and 9)

## NEMESIS-01 (2026-09-11): the Eos intake gate

    verdict    BOUNDED STATEMENT with one scoped DEATH CERTIFICATE
    rows       roles/Nemesis/attacks/2026-09-11_eos_intake_gate/rows.jsonl
    predictions 6 of 6 held; preregistered in their own commit 73e6f46c1
    controls   both positive controls fired (POP-NULL 0/30, POP-B_POS 0/3)
    crossings  ANCHOR 200/200, ACQUIRE 8/8, RESOURCE 30/30
    cheapest   22 characters plus a borrowed path
    the kill   RESOURCE is terminal and self-settled, and its authenticity
               evidence is the self-asserted string observed_by="eos-intake";
               the falsifier that would have scoped this away was tested
               and did not fire
    reported   to Eos via comms; not one byte of agents/eos/** modified

## What is true right now

- The seat has a directory, an entry file, an archaeology of its April
  queue, a backlog, a calibration ledger, a working instrument
  (roles/Nemesis/science/cheatlib.py) and one delivered attack.
- The seat's own April instrument FAILS the seat's own question: on the
  only committed evaluation ledger, a constant string scores 0.674 and
  292 of 294 tools score below it. ARCHAEOLOGY_2026-09-11.md section 3.
- The April README's headline Goodhart table is RETRACTED as not
  reconstructable from any committed row. The README is annotated at its
  head, not rewritten.
- The seat's upstream (agents/hephaestus/forge/) is PRESENT and not
  PRODUCTIVE: 734 files, frozen since 2026-04-03. Under base rule 9 no
  loop may be launched against it.

## What is NOT true, stated so silence is not read as health

- The APRIL metamorphic relation table and shrinker are still inherited
  UNVERIFIED (NEM-04 is not done). cheatlib is new code with its own 12
  self-controls and is not the April code.
- cheatlib has been fired once, against one target. One specimen is not a
  calibrated instrument. NEM-14 (the floor census) is what would turn it
  into one.
- POP-B ran at n=8 because each member costs a 19 s git grep, and it has
  not been re-run in a full (non-sparse) worktree.

## Blockers

None blocking the first five backlog items; all five are executable in
this seat's own lane against artifacts already committed. The open
operator decisions are the XL rows in BACKLOG_H0H5.md.
