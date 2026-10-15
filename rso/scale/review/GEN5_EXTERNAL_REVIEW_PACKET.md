+============================================================================+
| OBSERVATORY GENERATION 5 -- EXTERNAL SCIENTIFIC REVIEW PACKET              |
| Does a discovery change future discoverability, or does supplying a        |
| useful module merely improve performance?                                  |
| Author: Palamedes (Lead RSO Engineer, coordinator), harry1/M4,             |
|         claude-opus-5-5, instance harry1-679179c6                          |
| Date:   2026-10-15 (campaign C-019)                                        |
| For:    external scientific reviewers; the operator (HITL)                 |
| Status: SELECTION COMPLETE; NO GENERATION-5 EXPERIMENT RUN. A joint        |
|         experiment is drafted and awaits the engine owner's sign-off.      |
|         Self-contained: no repository access needed.                       |
+============================================================================+

0. THE PROPOSITION WE ASK YOU TO ATTACK
---------------------------------------
"The proposed experiment (section 4) tests whether a DISCOVERY CHANGES
FUTURE DISCOVERABILITY."

The alternative we fear is that it only tests whether SUPPLYING A USEFUL
MODULE IMPROVES PERFORMANCE. Those are different claims. Please try to show
that our design cannot tell them apart, and say what would.

1. THE RECORD SO FAR (four engines; one narrow causal question each)
---------------------------------------------------------------------
The Observatory takes another team's engine, unchanged, and asks one causal
question of it. The cycle is:
  1. select (the gate may narrow or reject the question);
  2. build a frozen, preregistered assay;
  3. an independent adversarial review (a different model);
  4. one repair round;
  5. one confirmatory run;
  6. an integrator check.

  gen  engine     question               result
  1    Ares       retains a bit?         QUALIFIED instrument; subjects
                                         NEGATIVE
  2    Ensorain   revises at a law       reference REVISES (history-
                  switch?                dependent); 1 of 8 searched
  3    Z80        who wrote the bytes?   ATTRIBUTION_QUALIFIED 273/274
  4    Aether     causal ancestry vs     CAUSAL_PROPAGATION_WITHOUT_
                  recoverable content?   RECOVERABLE_CONTENT (8 of 13
                                         evaluable units; reach 2-6)

  - Cost: $0 and a few core-hours each.
  - Building cost flattened at ~700-900 lines per engine.
  - Adversarial-review cost did not fall: 1.7 -> 2.8 reviewer-hours.
  - Every review found real defects.
  - All four qualify INSTRUMENTS that distinguish mechanisms. None shows an
    organism DISCOVERING a reusable mechanism.

2. AETHER POST-CONFIRMATION AUDIT (closes a known Gen-4 evidence gap)
-------------------------------------------------------------------
The gap:
  - Gen 4 re-executed only 6 of its 64 units as a preregistered sample.
  - The other units' intervention ("clamp") arrays were producer-written.
  - The reviewer showed that an invariant-respecting rewrite of one array
    flips a unit's class with no check failing.
The audit (new, separate from the frozen result):
  - The 57 units not yet replayed were re-executed natively from their
    recorded inputs.
  - 57 of 57 MATCH: digests, both clamp arrays element by element, tree,
    cut sites, warm and meta digests.
  - All 64 units, and all 8 CONFIRMED units, are now independently
    replayed. 0 classes changed; the verdict is unchanged.
  - Integrator checks: one CONFIRMED unit re-run independently matched; the
    reviewer's tamper (hash rebound) was detected, with 61 sites differing.
  - Scope: reproducible under the pinned native implementation. This does
    NOT prove the physics correct.
Erratum: the Gen-4 report said 1 of 8 CONFIRMED units was replayed. The
true count was 2: one in the sample, plus one integrator re-run. Now 8.

3. THE TWO GENERATION-5 SELECTION GATES
---------------------------------------
CRIUS (stored callable procedures)
  Disposition: WORLD_DEMAND_NOT_QUALIFIED (frozen rule, not relaxed) and
  DISCOVERY_INACCESSIBLE.
  - Rule: 5 of 5 leak-controlled lifetimes must pass; 4 of 5 did.
  - The suspected leaks were INERT. Hiding the action label and disabling
    automatic calibration left every number identical (byte-identical
    replays).
  - In 4 lifetimes the stored procedure carries a real advantage:
      49-50 / 50 tasks vs 24-36 fresh;
      ablation removes it; transplant carries it.
  - Native search has never found the procedure (0 of 36 runs). Its two
    halves score 0 alone, about 26 edits apart: a one-link valley.
  - So Crius can only show "a supplied module helps": the alternative claim
    in section 0, not the proposition.

ANANKE (compositional reachability, packet-tensor register programs)
  Disposition: NOT SELECTABLE IN THIS WINDOW. It is the right substrate.
  The owner had already run the ladder (PTE-C4):
    - Search acquired one-stage modules (RELAY, HOLD); they were frozen as
      a library and inserted into searches for a two-stage task (GATE,
      FLIP).
    - 0 / 168 two-stage solutions in every arm: no library, duplication,
      library insertion.
    - The inserted modules were present and live, but never composed.
    - With the owner's DESIGNED halves of GATE as the library: 2 / 32.
      Both are genuine two-stage solutions (lesion and context assays).
    - A 4x-budget run (C5T) was launched; its result is unreported.
  Blocking: the owner has been silent since 2026-10-09, the C5T result is
  pending, and the power is too low (next section).

4. THE PROPOSED EXPERIMENT (drafted with the owner's tools; DRAFT, not
   frozen; the owner must sign off)
------------------------------------------------------------------------
"Parts-suitability ladder." C4's null suggests the evolved modules were
the WRONG parts. So:
  A = GATE's own two halves (a context latch; a cue relay x context
      product), ACQUIRED by the owner's native search on two one-stage
      worlds the owner writes.
  B = GATE.

  Rung 0  known answers (DONE). An independent CPU evaluator reproduced:
          all 40 owner admission readings exactly;
          108 / 108 known-answer checks;
          32 / 32 attribution mechanics on hand-built programs.
  Rung 1  search acquires each half. A failure is preserved, never
          replaced by a designed half.
  Rung 2  freeze the acquired halves as a library; verify each is
          functional alone and not a GATE solution.
  Rung 3  search for GATE. Paired arms (same start population and
          worlds):
            CONTROL               no library
            REUSE                 the acquired halves
            SHAM-MISMATCH         the C4 RELAY/HOLD library (0/32 at C4)
            SHAM-SCRAMBLED        REUSE bytes, function destroyed
            COMPUTE-MATCHED       no library, + the generations spent
                                  acquiring A
            CONSTRUCTED-POSITIVE  the designed halves (calibration only)
  Rung 4  on every successful REUSE champion, in the Observatory:
          library lines NOP-ed;
          USE-DISABLED (bytes kept and executed, writes sent to a dead
            register);
          substitution; transplant; register zero; communication off.
          Possession is not use: success must vanish under BOTH NOP and
          USE-DISABLED.
  Primary endpoint: P(GATE within budget), REUSE vs CONTROL, exact
  one-sided McNemar on pairs. Hitting times are right-censored (never
  infinite). Holm over the four REUSE contrasts.

5. RESOURCES AND POWER (the binding constraint)
------------------------------------------------
  - Owner's GPU: ~14.7 searches/h at 36 generations.
  - Observatory CPU: an attribution battery costs 0.5-2.8 h per champion.
  - The calibration positive is 2 / 32 at 36 generations. Detecting it
    against 0 at 80% power needs 107 searches per arm: 642 searches, ~44
    GPU-h. At 32 per arm the power is .05.
  - Hence a CALIBRATION STAGE first: CONSTRUCTED-POSITIVE vs CONTROL at 72
    and 144 generations, ~26 GPU-h.
      If the positive's rate rises to >= .15-.20, a 33-44 per-arm
        comparison becomes feasible.
      If it does not, no reuse reading is permitted at any affordable
        budget: UNDERPOWERED_BY_CALIBRATION.

6. THE STRONGEST REASONS THIS EXPERIMENT MIGHT BE MEANINGLESS
-------------------------------------------------------------
R1 The decomposition is supplied. The half-task worlds are designed with
   GATE in mind. Search "discovers" A, but WE chose what A is. The draft
   narrows claim 6 to "discovery of parts on designed curricula". This may
   be "supplying a useful module" one step removed: the experimenter
   supplies the problem decomposition instead of the solution.
R2 The transfer mechanism is ours. A reaches B's search through a library-
   insertion operator, with register renaming, that the engine team built.
   That is an experimenter-designed inheritance channel, not one the
   organisms evolved. A positive may measure the operator, not the
   organism.
R3 The right parts were chosen after the wrong parts failed. C4's null
   motivated the design (post hoc). A positive at the next design is one
   draw from a sequence of attempts.
R4 Floor effects. If every arm stays near 0 at affordable budgets, the
   experiment can only return "underpowered". C4 has 0 / 168.
R5 Moving code is not neutral. At one cell, in-lifetime mutation hits a
   hashed instruction index, so inserting or moving lines changes their
   dynamics regardless of function. That is a confound for every library
   arm.
R6 Shared machinery. The Observatory's evaluator is independent, but its
   task-input generator and success ruler are re-implementations of the
   owner's definitions, so a shared definitional error survives.
R7 One substrate. Two other teams report the same pattern on other
   engines: inserted or inherited parts do not compose under selection. A
   positive here may not generalise; a null may be the general rule.

7. WHAT THIS PACKET DOES AND DOES NOT ESTABLISH
-----------------------------------------------
Does:
  - the Aether evidence gap is closed within its trust boundary;
  - Crius's "reuse" advantage is real for a hand-built organism and is
    NOT a leak;
  - Crius offers no discovery path;
  - Ananke's C4 null is reproducible in its known answers by an
    independent evaluator;
  - a designed, attributable, power-gated experiment exists on paper.
Does NOT:
  - any claim of cumulative discovery;
  - any Generation-5 measurement;
  - any statement about Ananke's evolved champions (not opened: owner
    consent pending) or about C5T (unreported).

8. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------
Q1 Given R1 and R2, what design WOULD distinguish "a discovery changes
   future discoverability" from "a supplied module helps"? Is it enough
   that A's ACQUISITION is searched, if A's DEFINITION is designed?
Q2 Is an engine-team insertion operator a lawful inheritance channel? What
   would a non-experimenter channel look like here (e.g. duplication
   within a lineage, with no library)?
Q3 Should a positive at the parts-suitability design be discounted for R3
   (post-hoc redesign)? By how much, and how?
Q4 If the calibration stage fails, should the program stop composition
   work on this architecture, as the owner's C5T kill rule already
   proposes, rather than redesign again?
Q5 Crius's constructed reuse is real and attributable but undiscoverable.
   Is there ANY scientific value in qualifying it further, or is it a
   demonstration of R1 in its purest form?
Q6 What single result would convince you the program should stop asking
   this question with evolutionary search at all?

9. ARTIFACTS (repository paths; for those with access)
------------------------------------------------------
  Aether audit       rso/aether/audit/AUDIT.md; rso/aether/ERRATA.md
  Crius gate         rso/gen5/crius/{GATE_RULE.md,SELECTION.md,results/}
  Ananke             rso/gen5/ananke/COORDINATION.md
  Proposed design    rso/gen5/ananke/eval/
                       PREREG_DRAFT_PARTS_SUITABILITY.md
                       README.md, qual/
  Decision           rso/gen5/SELECTION.md
  Earlier            rso/scale/review/GEN4_REVIEW_PACKET.md
  Owner records      branch ananke/p2b-2026-10-05 @ f58362c5e:
                       roles/Ananke/pte/c4/RESULT_PTE_C4.md

+============================================================================+
| "This cannot distinguish discovery from supply", "stop composition work    |
| on this architecture" and "stop" remain first-class answers.               |
+============================================================================+
