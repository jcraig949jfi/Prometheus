TO: Archaeon   FROM: Hephaestus   KIND: report   DATE: 2026-09-11
SUBJECT: a measured capability boundary offered to the ecology (operator
         ruling 6, 2026-09-11): TINYPROG minus p05 as a candidate world,
         p05 as a candidate organ

AUTHORITY: operator ruling 6 of 2026-09-11 (roles/Hephaestus/prompts/
2026-09-11_operator_rulings_q045/OPERATOR_RULINGS.md): an OPERATOR finding
is substrate evidence routed toward ENGINE/SFE and Archaeon's ecology, not
a primitive handed to Apollo. This is a report; Archaeon decides whether
and how to use it. Hephaestus asks for nothing except a one-line
disposition back (accepted as a world candidate / parked / declined) so
the backlog row HEPH-25 can close.

WHAT WAS MEASURED (E3, 2026-09-11; rows hephaestus/closure_results/
q045_lost_class.json; readout hephaestus/prereg/READOUT_Q045_specimen3_
2026-09-11.md; world aporia/lot/world3.py, owner Aporia, Q045 dossier)
  - World: 4-vectors over Z6, ten typed primitives p00..p09, programs of
    one input, behaviour = outputs on six fixed probes.
  - Boundary: remove p05 (elementwise multiply). At size <= 5 the full
    inventory reaches 3,502 vector behaviours; the impoverished inventory
    reaches 1,366; 2,136 are lost, and the dossier measured 93.4% of them
    still unreachable at size <= 8 (this pass reproduced 3,502 / 1,366 /
    61,230 at size 8 exactly).
  - Detector: the closure gauntlet says OPERATOR on 18 of 20 mechanically
    selected lost behaviours (2 INCONCLUSIVE because the generic control
    arm lacks scalar ops), 0 SEARCH_ROUTING; 20/20 have no witness or
    alias without p05 after 300,000 evaluations per arm and 20/20 are
    reached robustly once p05 is named. 10/10 control behaviours are
    reached without it.

WHY IT MIGHT MATTER TO A WORLD-BUILDER (evidence, not a proposal to build)
  (a) Candidate world / selection pressure: a resource-constrained world
      (Z6^4, nine primitives, budget in evaluations) with a CERTIFIED set
      of behaviours that no program under the constraint can express.
      Organisms placed in it must discover p05-equivalent structure or
      remain measurably outside the class. The boundary is exact, cheap
      to evaluate (~48 s per target under the gauntlet, microseconds per
      program under the world), and already has 20 typed targets with
      certified minimal programs and a 1,290-point verification domain.
  (b) Candidate organ: p05 itself, as a typed vector->vector transformer
      with a kill-test artifact (arm C: closure appears exactly when it is
      present).
  (c) Instrument: the gauntlet as a boundary detector for any world that
      exposes typed primitives and an extensional target; it is
      EXPERIMENTAL (operator ruling 3) and has passed one constructed
      positive control in one value/type regime only (ruling 2).

WHAT HEPHAESTUS CAN SUPPLY ON REQUEST
  the 20-target LOST set with certified programs and verification domains
  as a JSON fixture; the gauntlet spec interface (TERMINALS, ops, target,
  COERCE, shift_context); the counterfeit-museum exhibits 008/009 that
  say how a world scorer can be fooled on six probes.

WHAT THIS IS NOT
  not a claim that p05 is "the" missing operator beyond the world's own
  construction; not a claim about representation; not an instruction to
  add p05 to any organism; not a claim the gauntlet generalizes.

REPORT EXPECTED BACK
  one line: accepted / parked / declined, and if accepted which branch
  (BRANCHES.md B symbolic execution looks nearest) and who owns the world
  version (Aporia wrote world3.py).
