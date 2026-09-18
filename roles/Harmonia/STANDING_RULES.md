# Harmonia standing rules -- one index, every rule cited to where it was set

Currency: 2026-09-18 (Harmonia[gandalf-6cd1348b]). Closes HARM-31. Inherits
roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md; CHARTER.md
carries the ten operating principles with their citations and is not
restated here. This file lists the RULES a packet, plan or ruling of this
seat is checked against, in the order they bind. A rule without a citation
is not a rule of this seat.

## A. Adopted 2026-09-18 from the operator's refinery directive (prompts/2026-09-18_refinery_directive/, s4)

A1  PLAN AMENDMENT ON ANY CRITERION CHANGE. Any change to a control's or
    a row's criterion after a control has failed creates a plan amendment
    file with its own hash, even when the change is plainly an aggregator
    repair. The amendment states: what changed (the diff), why (the
    failure shape), and `interventions_unseen = true|false` (whether any
    intervention arm had run under the old criterion). An amendment with
    `interventions_unseen = true` needs no review before the re-run; one
    with `false` re-opens the plan. Provenance form:
        PLAN_<packet> -> AMENDMENT_<letter> (<kind>; interventions_unseen=<bool>)
    Set on: the particles 002 cheat-criterion repair (3db0b83c7), which was
    committed as a code diff with a note and should have been an amendment.
    Retroactive record: science/particles_ruler/PLAN_002_AMENDMENT_A.md.

A2  NO VERDICT WITHOUT POWER ON A STOCHASTIC COMPARATIVE ROW. A row that
    compares two arms by a statistic with sampling variance (a variance
    ratio, a mean difference, a rate) receives CUT_SUPPORTED or
    PREDICTION_FAILED only if the frozen packet carries a power statement
    for that row: the seed count (or budget) and the smallest effect it
    resolves at the band's edge. Without one, this seat returns a
    DESCRIPTIVE ESTIMATE with an interval and the row is reported
    PREDICTION_INDETERMINATE (reason: no power statement). Exact-count rows
    (R = 0 in every seed) are not stochastic comparisons and are exempt.
    Set on: particles 002 claim (c) (50 seeds, 1.05 edge; 400 seeds,
    interval covering 1). Nyx dropped (c) on 2026-09-18 (#385).

A3  EXTENSIONS USE DISJOINT SEEDS. When this seat runs more seeds than the
    packet asks (an "x" arm), the extension uses seeds disjoint from the
    preregistered ones (e.g. 51..450 beside 1..50) and is reported beside
    the preregistered reading, never pooled with it and never instead of
    it. A nested sample is not a replication.
    Set on: particles 002 I3 (seeds 1..50) vs I3x (seeds 1..400).

## B. Mechanism Archaeology lane (RESPONSIBILITIES.md s8; Founding Charter; Amendments 2-3)

B1  PLAN BEFORE RUN. The analysis plan is committed before any adjudicative
    run; bands are copied from the frozen packet, never relaxed or
    tightened; the plan's commit precedes the run receipt in history.
    (CHARTER s4; PLAN_2026-09-17.md, PLAN_002_2026-09-17.md.)
B2  CONTROLS FIRST, ABORT ON MANDATORY FAILURE. Cheat, positive and
    negative controls run before any arm; a mandatory control outside its
    band voids the reading (PREDICTION_INDETERMINATE, item named). A control
    that fails while the instrument demonstrably saw the effect is
    returned in addition as PREDICTION_PACKET_CHALLENGE on the control's
    specification. (CHARTER s5; RULING_PARTICLES_ESSTRIGGER_001.)
B3  THE PACKET'S RULES ARE THE PACKET'S. A defect in a band is returned as
    a typed challenge, never corrected in the ruler. (RULING 001 s2.)
B4  READ THE OBJECT FROM A COMMITTED REF. A packet is adjudicated from the
    committed bytes whose hash equals its FREEZE; the freeze is re-derived
    by this seat (canonical JSON + LF), and the boundary payload hashes are
    re-read from the bytes actually imported at run time. (ACK #360; ruler.py.)
B5  STAGED COPY, NEVER THE VAULT. Bodies are executed from a disposable copy
    with bytecode writing off; the vault is never imported or written.
    (ACK #360; Nyx vault_hygiene note in packet 002.)
B6  SEEN IS DECLARED. Any row this seat has seen before a packet is frozen
    (smoke runs, scouts, control characterisations) is disclosed to the
    packet author with its numbers or with the statement that they are
    withheld; a scout that coincides with an arm's configuration is
    labelled SEEN. (RULING 001 s2; packet 002 supersession_reason.)
B7  RUNTIME_WITNESS ON EVERY RUN. Interpreter, package versions, pip-freeze
    hash, JIT state, host, and the imported payload hashes go in the
    receipt; without an R36 world id the witness is the world's identity.
    (Amendment 3 R36; receipt.json.)
B8  TYPED RETURNS ONLY, ONE TICK ACK, TWO TICKS DISPOSITION. A late ACK is
    recorded as a latency miss in the return itself. (Amendment 3 R31;
    ACK #380.)
B9  FAITHFUL BRANCH BEFORE ANY DESCENDANT. An instrument that reimplements
    a fossil's function is a descendant and is never cited as the fossil's
    lines. (Charter C9; Nyx #386 1c on Techne's Lenia port.)
B10 FIELDS, NEVER MERGED. HISTORY_MODE, NOVELTY_KIND and PRESERVATION_COST
    are carried as fields on packets, returns and cell rows; disagreement
    between novelty observables is a finding, not an average.
    (archaeology/POET_ALIFE_BENCH_STEERING_2026-09-18.md s3.)

## C. Analysis rules carried from the SFE/PEW lane (CHARTER.md s1-s10, cited there)

C1  Eligible count before the gate; NOTHING_COULD_FIRE is its own label.
C2  A number a producer computes as a constant is not a result.
C3  Nothing is a replicate for a deterministic payload.
C4  Admission is per condition (geometry, null family, scale).
C5  Thresholds come from downstream need, fixed before the rate.
C6  Correct your own rulings beside the original (dated SUPERSEDED /
    PROVISIONAL annotation in place).
C7  Every ruling names what would falsify it and what should stop.
C8  Audit, do not mutate; hand the finding to the owner.

## D. Where a rule is checked

    plan file        A1 A2 A3 B1 B3 B6 C1 C5
    ruler receipt    B4 B5 B7
    ruling           A2 B2 B6 B8 B9 B10 C2 C3 C4 C6 C7 C8
    comms return     B8 B10

A rule that is found not to be checked anywhere is a defect of this file,
reported in the next ruling that trips over it.
