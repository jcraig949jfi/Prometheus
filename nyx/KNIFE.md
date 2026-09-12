# The knife: Chop Shop decomposition procedure, amended from observed failure

Currency: 2026-09-11 (first amendment, after the Lean/mathlib simp proving
specimen). This file is PROCEDURE. It does not amend the charter
(roles/Nyx/prompts/2026-09-11_charter/CHARTER_verbatim.md); where they
disagree the charter wins. Every rule below names the failure that caused
it; a rule without ancestry is not admitted. Rules are added by date and
never rewritten; a rule found wrong is annotated, not deleted.

## Rules (2026-09-11, ancestry: lean_simp CUTS.md and the assessment)

K1  SKELETON-BLIND FIRST PASS. Do not draw candidate boundaries from a
    grep of def / structure / file names. Read bodies in data-flow order
    (what flows in, out, and is read or written) and draw the boundary
    from the flow; only then check whether it coincides with a name and
    stamp INHERITED if it does. If the skeleton was read first, every
    boundary that coincides with it is INHERITED, no exceptions.
      Ancestry: CUT-1 inherited-boundary rate 20/23 = 0.87 (O1); the same
      habit was journaled after DreamCoder and did not go away by being
      known.

K2  THE LEGAL WORD. A charter-IV field whose honest value is unmeasured
    BEGINS with "unknown -- " followed by what would make it known. Prose
    that hedges ("claimed, not measured") without the prefix is a defect.
    The ledger counts prefixes; the schema HOLLOW check still needs the
    bare word.
      Ancestry: CUT-1 wrote 0 literal unknowns across 120 fields while
      hedging in all of them (O2), which made the preregistered
      "unknown -> measurable" metric unattainable for the whole trial.

K3  RUN THE SPECIMEN'S OWN SWITCHES BEFORE THE PAPER ATTACK. If the
    specimen exposes configuration that disables a candidate (a flag, an
    erase syntax, a mode), running it is the first attack, not the third
    cut. A paper attack on an unrun specimen produces revisions; a run
    produces falsifications.
      Ancestry: CUT-2 changed 7 kinds by argument and falsified nothing;
      CUT-3 (one 9-second compile) changed 1 kind by experiment, falsified
      a control, and found the only two PERTURBED boundaries of the trial.

K4  NEGATIVE CONTROLS FIRST. Write and run the control that must FAIL
    before the one that must pass. Passing positives taught nothing here;
    the one negative that did not fire changed the cut.
      Ancestry: c23 negative control (decide off, folders erased) did not
      fire; five positive controls passed and moved no disposition.

K5  NAME THE FOREIGN CALLEE. For every ORGAN, before delivery, name the
    mechanism OUTSIDE the preregistered boundary that could reproduce its
    fitness value, and say how the control would tell them apart. A
    boundary is a hypothesis; the callees are where it leaks.
      Ancestry: c30 -- closed Nat arithmetic is decided by the unifier
      (ExprDefEq, excluded by PREREG s1), reached through a reflexive rule;
      c23's headline fitness belonged to it.

K6  THE NULL CONFIGURATION IS NOT NULL UNTIL SHOWN. Before using a
    specimen's "minimal" or "only" mode as a control baseline, enumerate
    what it secretly includes, by erasing candidates until the baseline
    stops working.
      Ancestry: c29 -- `simp only` always loads eq_self and iff_self
      (Elab/Tactic/Simp.lean 410); the c07 positive control passed because
      of a rule that was never named in it.

K7  CONSUMER-FIRST CUTOFF ON PRESSURES. Do not write pressure N+1 for a
    seat that has not returned on pressure 1. Hold the candidate in the
    ledger as a note with its ancestry; write the record when a return
    arrives or the operator relays.
      Ancestry: six Nyx pressures queued unseen at Vivarium (#44, #52,
      #175 x4); mutual_normalisation (c13) and memo validity (c14) held
      rather than posted.

K8  ORIGIN IS STAMPED AT DRAWING, NOT AT WRITE-UP. The INHERITED /
    DISCOVERED / PERTURBED stamp goes into the ledger the moment the
    boundary is drawn, with the source boundary it coincides with. A
    stamp added later is a memory of a stamp.
      Ancestry: PREREG s2 step 2 required it and it was the only reason
      the 0.87 could be computed rather than estimated.

## Rules considered and NOT admitted (no observed failure yet)

- "distrust papers as boundaries": no paper was read in this trial.
- "force state extrusion" as a separate rule: c14 (memo validity) was
  found by following state across files, which K1 already requires.
- "demand independent intervention" beyond K3: no organ has yet been
  run outside its ancestor; the failure that would justify the rule has
  not been observed because the test has not been attempted.

## How the knife is applied per specimen

    ACQUIRE/CITE  pins to Techne receipts or, failing those, to bytes on
                  disk with the gap reported (lean_simp PROVENANCE.md)
    PREREG        boundary, reading order, predictions, stopping rule,
                  metric mapping -- BEFORE reading bodies (K1, K8)
    CUT-1         flow-first; ledger stamps; records with K2 prefixes
    SWITCHES      run every specimen-exposed ablation and every negative
                  control that needs no patch (K3, K4, K6); receipt
    DELIVER       organs + failures + foreign callees (K5) to Archaeon;
                  pressures to Vivarium under K7
    CUT-2         paper attack (the twelve questions) on what survived
                  the switches
    CUT-3         on a consumer return or a patched-build ablation
    ASSESS        cutledger; the preregistered composite; predictions
                  scored; this file amended only from a new failure

## Rules added 2026-09-11 evening (ancestry: Vivarium return #182 on #44/#52/#175)

K9  ROUTE TO THE SUBSTRATE OWNER. A pressure names, in its world
    requirements, a substrate (a term language, a stream format, a task
    generator). Before delivery, name the SEAT that owns that substrate; if
    none does, mark the pressure UNHOSTABLE_TODAY in the record and say so
    in the delivery. Deliver to (Vivarium + owner) in ONE message. A
    pressure sent to Vivarium alone always waits on a third seat -- that is
    the seat boundary, knowable in advance, not a backlog.
      Ancestry: #182 -- six Nyx pressures reached Vivarium; zero buildable by
      Vivarium alone; all four lean_simp pressures blocked on requirement 1
      (a rewriting substrate nobody on Prometheus owns).

K10 AN INVARIANCE CHEAT CONTROL IS ONE-SIDED; WRITE THE READ-OUT. A
    control of the form "two copies under a symmetry must agree" proves the
    defect when they DISAGREE and proves only equivariance when they agree.
    The record must state what agreement does NOT show and name the second
    check that credits the capability.
      Ancestry: #182 on orientation_is_a_choice; the program already held
      this doctrine (feedback: invariance null is asymmetric, 2026-08-25) and
      Nyx did not apply it. Not new knowledge; a new place it must be applied.

REVISION BOUNDARY: N1 (hypothesis shrinker) had not begun when #182 was
processed. N1 begins under K1-K10. No part of N1 was done under K1-K8 only.
