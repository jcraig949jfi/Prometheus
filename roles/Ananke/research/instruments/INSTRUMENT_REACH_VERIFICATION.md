# PTE instrument: reach verification (REACHED / UNREACHED / NOT_VERIFIED)

Status: PTE instrument, tested (test_lens_instruments.py,
test_reach_verification_three_verdicts). Built from W-K's fixture study
(workers/W-K/REPORT.md, T-K1). NOT a fleet rule. Code: lens.verify_reach,
lens.applied_ticks, lens.plant_fired.

CAUSAL QUESTION
Before a NULL from an intervention is read: did the intervention reach a
pathway that COULD carry the effect? W-K found no universal check. The
best single one (J .70, 0 false alarms) is a must-flip plant run through
the arm's OWN intervention code. An applied count separates "never
took" from "took but was unused".

VERDICTS
  UNREACHED     the intervention never changed the specimen's state
                (lockstep digest vs normal, every tick)
  REACHED       it changed state AND a plant that uses the pathway was
                decisively affected by the SAME intervention (A3.1 rule, or a
                FLIP)
  NOT_VERIFIED  it changed state but no plant fired (or none exists at this
                physics). The null is then indistinguishable from an
                inert/unreachable intervention: report it as NOT_VERIFIED, not
                as a mechanism null.
KNOWN ANSWERS (passing): echo + mid-gap flush -> REACHED; C1 drop window on
delay == delta relay -> UNREACHED; freeze_routing under dest_mode "all"
-> NOT_VERIFIED.

LIMITS (from W-K)
- For EFFECTS (not nulls) the relevant checks are different: a could-fail
  counter-plant (a forced-outcome fixture) and an arm-diff / sham
  identity (wrong target, probe side effects). Not packaged here (T-K1
  remainder).
- The applied count uses final-state digests per tick. A probe that
  mutates state is counted as applied (correctly), but it cannot tell a
  side effect from the intended change: use a sham arm.
- The plant must work at the specimen's physics (A2.2). Where none can,
  the verdict is NOT_VERIFIED by construction. That is the honest outcome.
- The frozen C1b code still treats NOT_APPLICABLE as intact (W-K T-K2).
  Use verify_reach in any NEW preregistration.
