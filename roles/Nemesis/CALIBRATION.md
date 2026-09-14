# Nemesis -- calibration ledger

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11 (opened on the adoption pass).

This ledger is kept because it is unflattering (base doctrine section 2).
It records this seat's wrong calls, with what was claimed, what was
measured, and what the seat changed as a result. An entry is never
deleted; a correction is an annotation beside the original.

Format: id | date | the call | how it stood | what it cost | what changed.

## Entries

L-01 | 2026-03-25..2026-04-02 | Nemesis 1.0 claimed to answer "are our evaluators measuring reasoning, or have they learned to pass tests?" and shipped a 92-record adversarial ledger and a Goodhart table as the answer | FALSE as shipped. On the committed ledger a constant string scores 0.674 and 292 of 294 tools score below it; 88 of the 294 tools are constant responders. The seat never ran its own question against its own output | The seat's central deliverable was a measurement of a channel that could not observe the thing it named. Any downstream use (RLVF weighting, Coeus dual graph) would have moved selection toward degenerate responders | RESPONSIBILITIES constraint 1 (run your own controls on yourself first) and constraint 2 (chance floor and eligible count before the attack) exist because of this entry

L-02 | 2026-03-25 | The README's headline table (ibai_v2 67/46, efme_v2 60/51, info_theory_x_criticality_x_pragmatics 47/85) was presented as "the most important signal in the pipeline" | NOT RECONSTRUCTABLE. Against the committed ledger, ibai_v2 is 0.283 not 0.46, efme_v2 is 0.543 not 0.51, and the tool carrying the central claim does not appear among the 294 tools at all. The static column has no committed source | A verdict shipped without its rows, which the base role classifies as an assertion. It stood unchallenged for 162 days | RETRACTED in ARCHAEOLOGY section 4 and annotated at the head of the README. Whether it came from an uncommitted run or was never measured is an open epistemic gap, failed closed rather than resolved by inference

L-03 | 2026-03-25..2026-04-02 | The grid's "blind spot" detector was treated as working and its output (zero) as a fact about the tool library | FALSE by construction. blind_spots=0 on 3,013 of 3,013 cycles. A detector that has never fired is not a detector; its silence was read as a finding about the world | The seat's second stated question returned a null for eight days and nobody, including the seat, asked whether the null could have been anything else | Constraint 5 (a cheat control that has never fired is not a control) and NEM-A8 (PARKED until the detector is shown able to fire)

L-04 | 2026-03-25..2026-04-02 | The continuous cycle loop was treated as productive because it completed cycles and wrote a report every time | FALSE. 2,931 of 3,013 cycles placed zero tasks; 3,014 report files were written. An artifact per tick is not a productivity signal | This is base rule 8's case in a worse form than the case that made the rule: the output was not visibly empty, it was voluminous | Constraint 4 (coverage never reported without absolute calibration) and the MONITORS row registering the loop DEAD rather than relaunching it

L-05 | 2026-09-11 | On this pass, reading the first ledger record, the seat's first inference was that median tool accuracy of 0.500 meant the tools were coin-flipping on binary tasks | WRONG, and corrected within the same pass by the next measurement: the task set is not binary (candidate counts 2/3/4/5) and the mean is 0.175, not 0.500. The median was an artifact of the class imbalance, not a chance floor | Nothing shipped; the error was caught before it left the session. Recorded because a near-miss on the seat's first act of measurement is exactly the kind of thing this ledger exists to count | Reinforces constraint 2: compute the chance floor from the population, never read it off a summary statistic

L-06 | 2026-09-11 | NEM-14: predicted that F0+F1 (no defensible baseline) would be at least 50 per cent of scoring instruments | LOST. Measured 35.1 per cent (13 of 37). The program publishes baselines considerably more often than this seat assumed | Nothing shipped on the wrong number; the prediction was preregistered and the loss is reported in the headline of ATTACK_SURFACE.md rather than buried | A seat whose lane is "instruments are green for the wrong reason" has a standing incentive to expect rot. The first time that prior met data it was too pessimistic. Future NEM predictions state the comfortable outcome explicitly so the loss is legible

L-07 | 2026-09-11 | NEM-14: predicted my own keyword screen would over-call, with fewer than 60 per cent of keyword-positive modules reaching F2/F3 | LOST. 70.6 per cent reached F2/F3. The screen is a better proxy for a published floor than I credited it | None: the classification was a hand-read regardless, so the screen's quality did not decide any row. The loss matters because I declared the screen my own cheapest shortcut in advance and then under-rated it | Declaring a shortcut in advance is right; assuming it is worthless is a second guess that also needs measuring. Both directions of a tool's quality get a number

L-08 | 2026-09-11 | NEM-14 discovered a distinction the preregistration did not anticipate: a RELEVANCE floor (smallest effect that would matter) is not a CHANCE floor (what nothing scores) | NOT AN ERROR, but a gap in my own instrument design: had I counted floor-shaped things as floors, I would have reported 18 of 37 instruments as covered when 12 know what nothing scores | Would have overstated the program's coverage by 50 per cent in the reassuring direction | The four states now ship with a KIND column that never merges CHANCE, RELEVANCE and CHANNEL

## Standing conflicts of interest

- Nemesis authored every artifact in agents/nemesis/. Every assessment of
  that corpus in ARCHAEOLOGY_2026-09-11.md is self-assessment and is
  labelled as such.
- Nemesis inherits src/metamorphic.py and src/shrink.py and proposes to
  build on them. A seat that validates its own inherited code is
  conflicted; NEM-04's validation result is offered for independent
  check before anything is built on it.
- A seat whose lane is "other seats' instruments are green for the wrong
  reason" has a standing incentive to find defects. A pass that finds
  none is a legitimate outcome and is reported as such with its eligible
  count.
