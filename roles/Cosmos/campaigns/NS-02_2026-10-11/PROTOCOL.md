# NS-02 PROTOCOL (learning test; directive NS-01 s12; frozen in stages, each before its data)

Stage 1 (this commit, before its run): de-saturated signature (ns01/signature2.py: NS-01 signature + corruption
dose-response q .1/.3/.5 and dual-cue first/second) and engine requalification (ns01/engine2_test.py). Equivalence =
base distance <= .05 AND stress distance <= .10. QUALIFIED iff FR <= .10 on the 80 disguised witnesses, FA <= 1/7 on
the NS-01 look-alike pairs, and >= 4/6 NS-01-collapsed proposal pairs ((A02,A03), (A02,B07), (A06,C05), (B07,C05),
(A03,C03), (A01,B04)) separate by stress distance > .10. If it fails, NS-02 generation proceeds only with that defect
recorded and the stage-3 comparison restricted to base-signature labels.
Stage 2 (before generation): archive v2 frozen (NS-01 tier M + M-RELATIONAL with witness W-REL + NS-01 reproducibly
distinct behaviours A07 B01 B05 B08 C06 C07 D04 as witnesses + NS-01 KNOWN_EQUIVALENCE proposals' stress profiles).
Stage 3: 4 arms x 8, fresh tool-less conversations, same contract; B's prompt adds the F15 description; C's signal
from the stage-1 equivalence (rejects a perfect memory only if its stress profile matches a witness); D seed changed.
Primary learning measures: per arm, fraction of proposals that are relational (rf - full >= .20 with linear and
one-hot also failing) and fraction equivalent under archive v2, NS-02 vs NS-01; A is the run-to-run control.
