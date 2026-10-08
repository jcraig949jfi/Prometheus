C-009-T014 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch argus/c009-t014 at 13924930d. State + receipt on main (031e31354).
rso/witness/RULER.md (spec for the witness preregistration), ruler.py (pure, stdlib), tests/test_ruler.py (21, synthetic).

  unit       episode; decision = majority non-abstain action after the last interrupt; tie/abstain = NO_ANSWER
  design     n = 2048 per arm, r balanced 1024/1024; bound 1/2, delta 1/20, alpha 1/100
  P-RET      NOT_SHOWN wrong >= 1078 | POSITIVE correct >= 1078 | NEGATIVE correct <= 1073 | else INDETERMINATE
  size/power POSITIVE size 0.009; NEGATIVE power 0.977 at 1/2; POSITIVE power 0.985 at 11/20; equivalence size 0.0095
  P-CAL      PASS iff NULL and SHUF correct <= 1073 (one-sided) and POS POSITIVE; FAIL names the arm

Found before freeze: n = 640 was underpowered (NEGATIVE 0.57 under no carry; P-CAL arms mostly fail) -> 2048; and
abstain-as-wrong would have let an abstaining no-carry subject read NOT_SHOWN -> NOT_SHOWN decided on wrong answers.
For Cadmus / preregistration: FD-T014-3 reads "within the registered margin" one-sided (bound is an upper bound);
two-sided would need a larger n again.
Honest gap: ruler.py was written before its tests (no RED-first run); 8 targeted mutants are all killed.
No Ares output read; no witness statistic computed.
