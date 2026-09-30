# RB-6 -- EDITABLE IMPROVER (V5) AND THE IMP@K TRANSPLANT PROTOCOL (T03, T20)

Literature + design, with a small simulation. Autonomous. Estimated 1 day. Read RB-00
first, then PRIOR_ART_A_RSI_AGENTS.md sections 0-2 (the L0/L1/L2 vocabulary; STOP;
Promptbreeder; Hyperagents/DGM-H; HGM) and PRIOR_ART_B 1.19 (meta-GP / autoconstructive
evolution: weak record).

WHY
  Every Aphrodite experiment fixes the improver (derive -> certify -> LGG -> select). By
  the field's vocabulary that makes it an L1 (process-improvement) system. It CANNOT show
  improvement of the improver (V5), which is what "recursive self-improvement" names.
  Hyperagents (2026) is the closest protocol: evolve a meta-agent, freeze it, transplant
  it to an unseen domain with a fixed initial task agent, and measure imp@k. That is
  Aphrodite's S4 causal transplant, one level up.

DELIVERABLE 1 -- IMPROVER PARAMETER INVENTORY
  List every free parameter of a17.donor and its sub-steps that could be data rather than
  code, for example:
    - the LGG hole count;
    - the class-pairing rule;
    - the equivalence/certification battery;
    - the candidate-library construction (SCHEMA_k vs SCHEMA_ALL);
    - the selection statistic (paired mean vs CMP-like 2-generation);
    - the library walk order;
    - the escrow split between library and fallback;
    - the composition move (RB-3).
  For each, say whether a donor's own products could plausibly set it, e.g. "use the hole
  count that produced the last selected schema".

DELIVERABLE 2 -- LEVER CHECK (small simulation)
  On the K5 supplies, run 3-4 hand-set improver variants (2-hole LGG; CMP selection;
  composition ON) with a fixed initial library. Measure the spread of V1/V3/V4 outcomes
  across variants. Zero spread means the improver has no meaningful levers in this DSL,
  and V5 is untestable here. That is a stop signal worth reporting.

DELIVERABLE 3 -- IMP@K DESIGN SKETCH
  If the spread is non-zero:
    - improver variants evolve on supply A;
    - the best is frozen and transplanted to supply B with the PRISTINE library;
    - imp@k is compared against the fixed improver, with a sham (random-variant) control.
  Write it as an AMENDMENT draft for Aphrodite, with the smuggling risks listed.

OUTPUT
  science/frontier/rb6/ (EDITABLE_IMPROVER_DESIGN.md, sim scripts, JSON).
