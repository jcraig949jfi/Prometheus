# T-X-4  What is the cheapest reusable demonstration that an intervention reached its pathway?

Status: RESEARCH / instrumentation question. NOT a fleet law. Nothing
here is imposed on other seats. Evidence gathered read-only by W-D
(../workers/W-D/REPORT.md).

QUESTION
Before a null (or a positive) from an intervention is interpreted, what
is the cheapest check that the intervention actually intersected the
candidate causal pathway? Does one check generalize across engines?

EVIDENCE (8 verified cases, 5 seats)
- REACH (switch never set / condition never met): Nestor C9-D16,
  Archaeon SFE-01 tabu (0 hits; produced a false POSITIVE), SFE-05 ladder.
- INFECT (set but never read): PTE frozen routing under dest_mode "all";
  BEE G1T (energy law makes the score irrelevant).
- PROPAGATE (outside the readout window): PTE C1 packet-ablation window.
- WRONG TARGET (confound): Nestor FORCED_READ.
- FORCED OUTCOME (could not have been otherwise): Aether full-ring
  starvation.
Existing guards that missed D16 checked the mechanism in isolation or
the declaration, not the measurement path.

CURRENT BEST ANSWER (W-D)
No single check. Three checks, plus one free alarm, cover all 8 cases:
  C1 a must-flip plant run THROUGH THE ARM'S OWN CODE, plus a reach
     counter (events touched) beside the verdict;
  C2 an arm-diff: the arms' actual inputs and targets differ only in the
     declared factor;
  C3 a could-fail counter-plant: a case where the hypothesis is false and
     the intervention must NOT produce the effect, plus a count of the
     units eligible to show it;
  alarm: ARM_IDENTICAL under common random numbers (an arm equal to its
     control on all pairs = the intervention never took).

OPEN QUESTIONS (bounded)
Q1 Cost model: can C1-C3 be expressed as one generic harness shape per
   engine (a plant, a counter, a diff)? Survey each engine's arm-building
   code path (read-only) and say where each check would attach.
Q2 False positives: 3a shows an inert arm can create a spurious effect
   when the RNG streams diverge. How often do seats run without common
   random numbers? (Read-only census.)
Q3 Could-fail controls are the rarest (only Aether needed one). Is there
   a cheap generic construction ("invert the law", "a sham with the
   channel inert")?
Q4 Does the RIPR framing (mutation testing) map cleanly, or does
   "forced outcome" need its own category?
PTE-side work (Ananke owns): T-D1 reach counters on lens verdicts;
T-D2 a plant library per intervention; T-D3 an ARM_IDENTICAL flag.

HOW TO SHARE
Offer the case table and checks to the seats concerned as information
(comms, to the named seats), only after an operator nod if it would read
as a rule. The value is in the worked cases, not in a mandate.

STOP. 3 h for Q1-Q4, read-only.
