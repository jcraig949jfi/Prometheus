# RB-10 -- IMPROVER-EVOLUTION PROGRAM (P2), STAGE 1: DO THE UNTESTED LEVERS MOVE ANYTHING?
# (separate program; NOT part of the compounding assays)

Medium, autonomous, forensic. Read RB-00 first. Then read
science/compounding/rb6/IMPROVER_EVOLUTION_PROGRAM.md, IMPROVER_PARAMETER_INVENTORY.md
and RB6_LEVER_CHECK_RESULT.md.

WHY
  RB-6's lever check found the tested improver levers nearly inert on K5 supplies:
  1-hole vs 2-hole LGG, lookahead selection and median selection moved held-out value by
  <= 4%. The inventory predicts the large levers are the UNTESTED ones:
    (a) ENTRY SHAPE (how a derived schema becomes a library entry: init/final coupling,
        instantiation depth);
    (b) ESCROW SPLIT between library walk and fallback;
    (c) COMPOSITION (now shown to matter; see AMENDMENTS 18/19).
  If (a) and (b) are also inert, P2 should stop in this DSL, per RB-6's own stop rule.
TASKS
  1. Implement (a) and (b) as improver DATA (never code forks). Run the RB-6 lever-check
     protocol on the K5 supplies AND on the A19 constructed supply (engine/A19_C2/).
     Report the spread of held-out value and of the ladder stages.
  2. Nonzero spread on (a) or (b): draft the P2 stage-2 preregistration (improver
     variants proposed from donor traces vs random proposal vs fixed; freeze and
     transplant to an unseen supply; imp@k with a variance-matched sham).
     Zero spread: write the stop note.
GUARDRAIL: never mix P2 runs into compounding dispositions. Use labels "RB10-...".
DELIVERABLES: science/compounding/rb10/ (scripts, JSON, STAGE1.md).
