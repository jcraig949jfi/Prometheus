# PTE-C1b corrections (2026-09-27; labels unchanged, readings corrected)

Source: roles/Ananke/research/SPIKES_2026-09-27_LOG.md and
C1B_REVIEW_AND_MECHANISMS.md.

K1 REVIEW_PACKET s4 and s10: "in-flight signed-sum predictor 0.44 -- NOT
   the code" and "M2's code is unknown". WRONG as a reading. The census
   read only payload component 0; M2 has P = 2 and carries the code in
   component 1. The sign of the component-1 in-flight sum decodes the cue
   at 1.00 out of sample, and swapping only component 1 between mirror
   partners flips the answer. The same code appears in 3/3 fresh SIGNAL
   champions (one uses component 0).
K2 "M2 not a pure delay line (routing weights -0.06)": the w reset hurt by
   disruption. Swapping w carries nothing (4/4). In substance M2 is a pure
   in-flight carrier: a tuned two-stage echo, at chance beyond the
   trained gap.
K3 "M3's SETRULE role is inferred as configuration": now shown. Rule state
   is identical between mirror partners at every tick; all sites converge
   to rule 0 in trial 0; freezing SETRULE after that changes nothing.
The frozen labels (IN_FLIGHT_PLUS_JOINT_UNRESOLVED;
TRANSPORT+RULE_SWITCH_UNRESOLVED) are what the preregistered rules compute
and are not edited.
