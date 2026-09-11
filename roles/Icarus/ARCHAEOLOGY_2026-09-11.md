# Icarus archaeology of the May-June 2026 queue (2026-09-11)

Currency: 2026-09-11. Booting an old seat is an archaeological event, not
an instruction to resume its last queue (base role, seat states; D-25).
Every item the seat held when it last ran (cycle 20, 2026-06-15,
596edeb0d) is classified here against the current north star
(roles/base-role/NORTH_STAR.md), the current ecology (SFE, H0-H5,
roles/Archaeon/H0H5_STATUS.md) and the current instrumentation doctrine
(base s2). NOTHING HERE IS EXECUTED. Only STILL_LIVE would become
executable work; NEEDS_REPREMISE must be re-stated first; the rest are
recorded. Nothing is marked dead: residue stays navigable and is named
below, with where it physically is.

Sources, all read at 56125e9e4 unless noted: agents/icarus/README.md;
agents/icarus/state/{tier_target,tier_currently_passing,
last_failure_direction,tier_calibration,debt_ledger,kill_clusters}.json;
agents/icarus/state/training_stream.jsonl (8 rows);
agents/icarus/cycles/_last_run_020.log; agents/icarus/wisdom/
kill_clusters.md; pivot/icarus_design_v01_2026-05-25.md,
icarus_design_v02_2026-05-25.md, icarus_v3_design_pressure_2026-05-28.md,
icarus_frontier_verdict_synthesis_2026-05-29.md;
whitepapers/icarus_synthetic_reasoning_v01_2026-05-27.md;
roles/Harmonia/RESUME_20260615_icarus_ladder.md;
roles/Harmonia/POSITION_20260812_north_star_reset.md (lines 82-88, 184-196);
aporia/doctrine/reasoning_ladder.md (rule 3, section 342-344);
git log -- agents/icarus (24 commits, 2026-05-25 to 2026-08-12).

## A. What Icarus was, in one paragraph

A self-improving loop (agents/icarus/daemon.py) that each cycle cloned the
last STABLE snapshot of a hand-written reasoner (cycles/cycle_N/code/
reasoner.py), asked an LLM-backed Improve() (Claude API, then from
2026-06-09 the Claude Code subscription CLI, ICARUS_LLM_BACKEND=loop) for
a rewrite that would pass the next rung of the Prometheus Reasoning
Ladder (R0-R12), ran TDD plus an 8-probe adversarial battery plus a
co-evolving Falsifier on a different model, froze the cycle, and marked
it STABLE or PARKED. A lens panel (skeptic, historian, integrator,
contract lens) turned each failure into a typed object (failure_class,
failure_subclass, nearby_survivor, regression_test_to_write,
representation_change_hint, improvement_kind). A debt ledger, a
kill-cluster miner and a tier-calibration matrix sat beside it. 22 cycles
ran, all on the operator's M2 machine (D:), between 2026-05-25 and
2026-06-15. Stable pointer: cycle 018. Passing: R5 (cleared cycle 18,
2026-06-10). Target when it stopped: R6 (conjecture counterexample
search). Cycle 20 PARKED with class tdd_failed, load-bearing lens
historian. Nothing has run since.

## B. The frame every row below is read in

The north star (operator, 2026-09-11) says: "We supply primitives,
environments, falsification instruments, provenance, and pressures --
not a predetermined reasoning architecture or ladder", and, for a seat's
daily choices, "do not build the reasoner. A seat that finds itself
designing the answer has left its lane." Icarus's mission was, word for
word, to climb a predetermined ladder by having an LLM redesign a
reasoner. The MISSION is therefore in direct tension with the north
star. The MACHINERY is not: typed failure residue that emits a direction,
kill clusters with nearby survivors, a falsifier on an independent model,
a calibration matrix that reports "too_weak_all_pass" and "vacuous" for
its own rungs, and a debt ledger are falsification instruments,
provenance and pressure -- the things the north star says a seat supplies.
And two doctrine lines the program still carries came out of Icarus:
"a plateau is an interface bug until an interface audit clears it"
(aporia/doctrine/reasoning_ladder.md rule 3, from Icarus R2 and R5) and
"a session that produced no typed object produced nothing" (Harmonia
08-12, citing the Icarus training_stream schema as the model). The
ladder itself was ratified as a measurement ruler, not a target; "Icarus
cleared R5" stands there as a measured claim on the canonical ruler.

## C. Queue items, classified

Format: item | class | why | what would have to be true to change it

1. Climb R6 (conjecture counterexample search, probe.kind=conjecture;
   state/tier_target.json set 2026-06-10 by the daemon after R5) |
   SUPERSEDED | the ladder is no longer the target; the reasoner is not
   ours to design; the only consumer of "R6 cleared" was the next rung |
   the operator re-premises Icarus (D below) as a lineage inside the
   ecology rather than a seat that designs reasoners, in which case R6
   is at most a task in a world, never the seat's objective.
2. Continue the daemon loop (--loop --interval 90) | SUPERSEDED as a
   standing loop; PARKED as machinery | base rule 8: a loop with no
   consumer of its output is activity, not progress; the training_stream
   has no reader in the current ecology (verified: no consumer names it
   in H0H5_STATUS.md, MONITORS.md or any 2026-09 prompt) | a consumer
   for typed failure objects names itself.
3. Q20 kill criterion (v3 design pressure, NEEDS-JAMES): "200 R5 cycles,
   0 capability promotions -> post-mortem, retire Icarus, keep the
   residue"; the operator owns the budget number and the
   retire/continue call | NEEDS_REPREMISE | it was never decided, and
   its premise (R5 as the wall) was overtaken: R5 cleared at cycle 18
   and the loop stopped at cycle 20 for lack of an operator, not for
   lack of promotions. The decision it asked for is still the live one,
   re-stated in D | the operator rules on D.
4. Seeded-primitive diagnostic vs "build our own reasoner from
   substrate" (verdict synthesis 05-29, TENSION TO RESOLVE WITH JAMES) |
   SUPERSEDED | the north star resolves it in the other direction:
   primitives are exactly what we supply; reasoners are grown, not
   built; the diagnostic's question (does the concept exist in the
   generator at all) is a question about an LLM's library, not about
   the ecology | none.
5. Q9 blind holdout tests, Q10 tier discrimination calibration, Q12
   decorative-code ablation (v3 pressure, "highest leverage OPEN") |
   PARKED | Q9/Q12 shipped in part on 2026-05-28 (cc507ffcd:
   holdout/, ablation.py, tier_calibration.py); the calibration matrix
   read "tier_R0/R1 too_weak_all_pass, tier_R2 vacuous, holdout_R1
   unreached_all_fail" on 2026-05-28 -- an eligibility count for the
   ladder itself, and it was not re-run after R5 cleared | a re-premise
   that keeps the ladder as a calibration ruler needs this matrix
   re-run first (a gate closer to the observed value than its own SE is
   not a gate; a rung every version passes is not a rung).
6. Q1 typed operator DAG (the representation rebuild) | SUPERSEDED |
   it is a reasoner architecture; the north star says grow, not
   hand-design | none.
7. Three open debts in state/debt_ledger.json (cycle-20 readout:
   open_debts=3) | PARKED | debts against a reasoner that will not be
   rewritten by this seat; the ledger stays as residue | item 1 changes.
8. Cosmetic lens debt (skeptic/integrator misread the empty diff field
   as "no changes applied"; Harmonia 06-15) | PARKED | harmless by the
   record (failure_class is mechanical ground truth); no reason to
   touch dormant code | the loop runs again.
9. Model Zoo binding test and legality replication (Harmonia RESUME
   06-15, threads 2 and 3) | TRANSFERRED (never Icarus's) | those were
   Harmonia's threads listed beside Icarus in a shared resume file |
   n/a.
10. 22 cycle directories cycles/cycle_001..020 (gitignored by
    agents/icarus/.gitignore; "kept locally for forensic value") |
    STILL_LIVE as a residue-preservation task, NOT as a science task |
    the forensic record of every parked cycle exists only on M2 (D:);
    on this machine (M1) only cycle_000 exists. The north star says
    residue stays navigable; a record on one disk that no seat can read
    from the repository is logged, not navigable | the operator or the
    M2 session copies cycles/ to a tracked or shared location
    (ICARUS-01 in the backlog; an operator action, since the files are
    on a machine this session cannot reach).
11. training_stream.jsonl (8 typed objects from 22 cycles; cycles 0-12
    emitted nothing, Harmonia 08-12) and wisdom/kill_clusters.md (3
    clusters, 6 failures) | STILL_LIVE as residue registration | these
    are the program's first typed failure objects and they are cited
    as the model for the register; they are in git, but no evidence
    store indexes them | register them in the Evidence Wiki as failure
    records with provenance (ICARUS-02), so a later search can reach
    them; no interpretation attached.
12. The whitepaper whitepapers/icarus_synthetic_reasoning_v01 (05-27)
    | RETIRED as a form | doctrine HARD-1: no papers, no publication
    framing; the file stays in history, annotated by pointer here, not
    edited (not this seat's lane to edit whitepapers/) | none.

## D. The decision this classification leaves for the operator

ICARUS-XL-1 (NEW): what is Icarus in Prometheus 2.0? The record supports
three options; the seat's stand is stated per base doctrine (take a
stand, assume you are wrong until proven).

  (a) RETIRE the seat with the residue made navigable (items 10, 11
      first). The machinery is absorbable by any seat that wants it.
  (b) PROBE BEFORE RESURRECTION (the Diomedes pattern, D-25): one
      bounded, preregistered measurement that would change a decision,
      then automatic return to PARKED unless it does. The candidate
      probe: do the kill clusters' recommended regression tests, when
      applied to the frozen cycle snapshots, catch the parked cycles
      they were mined from AND the later cycle-20 failure they were not
      (a positive control and an out-of-sample test of the residue's
      predictive value)? That is a measurement of whether "failure emits
      direction" was ever true for this loop, which is the one claim of
      Icarus's that the north star still cares about. It needs the M2
      cycle directories (item 10) before it can run.
  (c) RE-PREMISE as a lineage, not a seat: the self-modifying loop
      becomes a candidate organism under Vivarium's execution service,
      with the Falsifier and TDD as its deterministic selection
      predicates and the typed residue as its heredity record. This is
      the only reading under which the loop itself is consistent with
      the north star (mechanisms co-evolving under selection pressure),
      and it is also the most expensive: it needs an SFE kind, a world,
      and a decision that LLM-driven mutation is admissible in the
      ecology, none of which this seat can decide.

Stand: (b), then (a) unless (b) changes a decision. Reason: the loop
produced 8 typed objects in 22 cycles and three of its walls were
measured to be interface defects of the loop, not capability limits of
the reasoner; whether its residue has any predictive value is unmeasured
and cheap to measure once the cycle directories are reachable; (c) is a
design proposal that should compete with the H0-H5 organisms on the same
terms, not inherit a seat. The seat is BLOCKED on this decision and does
no autonomous work until it is made (base role, seat states).
