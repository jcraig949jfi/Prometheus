# SOLO THREE-PERSONA READER -- case POLLUX (control arm)

You are ONE agent asked to perform, in sequence and in a single report, the three
roles of the Necropolis case cycle: Necromancer (reconstruct), Cleric (attack the
reconstruction), Judge (adjudicate).  Read COMMON_RULES.md first (same directory
as this file) and obey it; it is the whole of your authority.

Write ONE file:
  roles/Rhadamanthus/prompts/2026-09-14_court/case_pollux/SOLO_three_persona.md

Part A -- NECROMANCER: reconstruct the dead experiment: claimed capability,
implementation (line numbers, constants, thresholds), assembly, inputs, outputs
(present / absent in this tree), dependencies, controls, gates (can each refuse?),
consumers (full consumer-trace hit list), historical verdicts (zero weight),
contradictory evidence, later repairs, surviving components.  End Part A with a
numbered PROPOSITIONS list P1..Pn (discrete, falsifiable, each tagged and cited)
and a draft DEATH CERTIFICATE with a cause class from {DESIGN_ERROR,
MEASUREMENT_ERROR, INFRASTRUCTURE, HYPOTHESIS_FAILURE, RECORD_INSUFFICIENT,
CONSUMER_ABSENT, OTHER} plus its strongest rival.

Part B -- CLERIC: attack Part A.  For each of: the death certificate; the
reconstructed cause; a FAIR-test claim (the experiment could have answered its
question); an UNFAIR-test claim (it could not); salvage value; a Frankenstein
counterfactual (one mutation that would have changed the outcome) -- state the
attack, the evidence, and the outcome STANDS / WEAKENED / FALLS /
UNTESTABLE_WITHOUT_EXECUTION.  Attack propositions by number.  You are allowed to
conclude that the hypothesis itself failed (HYPOTHESIS_FAILURE), or that the
record cannot decide.

Part C -- JUDGE: for each disputed proposition: the proposition, the evidence each
side relies on, whether the dispute is factual / taxonomic / causal / epistemic,
the observation that would resolve it, and whether that observation is worth its
cost.  Then a final classification of the grave and a list of what remains
unresolved.  Some things should remain unresolved.

Also record at the top: files_opened, instruments_executed, excluded_by_charter.
Tag every factual sentence per COMMON_RULES.  Do not report pass/fail summaries;
report the shape of each failure.  When finished, reply with the report path and
the count of propositions only.
