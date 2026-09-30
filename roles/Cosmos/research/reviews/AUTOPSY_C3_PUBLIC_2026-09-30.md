# C3 failure autopsy (public record)

Date: 2026-09-30. Author: Cosmos[m2-44f84976] (claude-opus-5-5, M2 SPECTREX5).
Authority: operator C3 disposition 2026-09-30 (roles/Cosmos/prompts/2026-09-30_operator_c3_disposition/).
C3 is CLOSED / KILLED BEFORE HOLDOUT. D2 is SEALED / UNREAD / UNSPENT. This autopsy read no D or D2 material.

This file names no coordinate, law, threshold, world or failure region. The full technical autopsy is
WITHHELD on the local M2 branch `cosmos/c3-autopsy-2026-09-30`. Its hashes (s4) make it checkable if the
operator ever triggers publication. Companion record: research/reviews/COORD_AUDIT_C3_2026-09-29.md.

## 1. The failure in one paragraph
C3 asked whether one cross-substrate quantity decides when a system USES information from its past,
across three unrelated mechanisms. The target was the certificate class NONE / PASSIVE / FUNCTIONAL, set
by P1 (the history is decodable from the state) and P2 (swapping the history changes behaviour). The
candidate law's coordinate was built from the SAME paired common-random-number construction that the P2
certificate uses to swap histories. Its value is, by construction, the size of the P2 intervention as the
readout sees it, so the law restated the phenomenon's definition with a noise threshold on top. The
other candidate coordinates mostly identified which substrate family a world came from. Neither kind was
evidence of a law.

## 2. OBSERVED / INFERRED / CONCLUDED
OBSERVED (executed; visible worlds only; 40 per family, 3 families)
- A zero-parameter rule is the P1/P2 preconditions written in the coordinate construction: no fitted
  value, no threshold. It reproduces 104/120 certificate classes (40/40, 34/40, 30/40 by family) and
  12/12 substitution worlds. Its 16 misses fall in two classes: 7 worlds where the certificate itself
  returned no class, and 9 where the construction registers a perturbation that carries no usable
  information.
- Candidate law vs the zero rule on the fitted binary target, 113 determinate worlds: 6 worlds only the
  law got right and 1 only the rule got right (exact McNemar p = .125). All 6 law wins are
  noise-floor cases.
- Out of sample (the adversary's 90 fresh certified worlds): on the confident stratum (n 44) the law and
  the zero rule are right on exactly the same 42 worlds. On all determinate rows (n 81) the zero rule is
  right more often (64 vs 60). The band stratum (n 37) was chosen near the law's own boundary, so it is
  selected against the law.
- Certificate coupling: the law's coordinate rank-correlates .875 with the P2 effect size. Every world
  where the coordinate is exactly zero has a P2 effect <= 1/3000 (31/31).
- Family leakage: the candidate coordinate set identifies the substrate family at .77 leave-one-out
  accuracy (.87 with the stored diagnostics) against chance .33. One family is identified perfectly by a
  bitwise identity between two coordinates (40/40).
- The rule that won the search was preregistered, before any data, as the expected result (credence .5).
  All 12 of the search's top candidates contain the same coordinate.
- The preregistered baselines did NOT include the zero-parameter definition rung. The seat's baseline
  ladder added that rung on 2026-09-29, five days after the search ran.
INFERRED
- The coupling is mechanical, not empirical. Both independent audit replicas traced it to shared code
  paths, the same paired-noise construction and swap time, and every observation above agrees with that
  reading.
- Family identity enters through export choices, not physics: how much state the readout sees, which
  families have a zero-noise lattice point, the state dimension, and the encoding of discrete variables.
  The distance-based construction is also not invariant to a change of basis. Its only invariant repair
  is a decoding-based measure, and that measure is the certificate.
- The law's threshold behaves as a noise floor that mostly one family sets.
CONCLUDED
- The C3 candidate invariant showed no explanatory structure beyond its measurement and certificate
  construction. The coordinate audit was right to reject it, and stopping before D2 was the right
  outcome.
- This is the second instance of one failure mode. C0's surviving laws re-derived C0's planted
  certificate economics (RESULTS R-0001/2; T-I1 v3). C3 re-derived C3's certificate intervention.
- Scientifically, C3's result is the falsification.

## 3. General lessons for world-graph campaigns (binding on C4 and later; the C4 prereg must cite them)
L1 Explain != define. A candidate coordinate may not be computed with any machinery the label uses: paired
   noise, swaps, ablations, effect statistics or probe outputs. Check this in CODE (shared call paths),
   not only in prose.
L2 Preregister the definition rung. Before any search, write the zero-parameter rule that follows from
   the certificate's semantics and make "materially beats it under family-held-out evaluation" the first
   gate. A search that cannot beat it returns NO LAW.
L3 Measure family leakage as a number. Report how well the representation predicts family, next to how
   well it predicts the phenomenon. Leave-one-family-out is the primary evaluation, not pooled fit.
L4 Record the rule, not only its score. A verification must store the rule's definition and the code
   hash with its counts. C3's VERIFY record stored counts only; the autopsy had to re-derive the rule and
   re-execute it (it reproduced exactly).
L5 Distance is not information. Perturbation magnitude (sensitivity) is not causally usable history.
   Noisy chaotic dynamics amplify any perturbation. A coordinate that cannot tell sensitivity from
   information will fail where they diverge, and that is where a physical law has to earn its keep.
L6 Watch for a preregistered expectation that is also the construction's output. If the coordinate was
   designed so that the hoped-for law is its natural reading, a successful search is expected either way
   and is not evidence.
L7 Export choices are free parameters. What a substrate exposes (readout size, encoding, noise lattice) sets
   the coordinates' values. Preregister an export rule, or use statistics that are invariant to it.

## 4. Evidence hashes (sha256 over LF-normalised bytes unless noted)
| object | hash | where |
|---|---|---|
| withheld Session 1 head | git e73e5eb26aa3edbc786a1941817bce738b4f58ec | local branch cosmos/c3-s1-2026-09-24 |
| withheld autopsy commit | git c9f8aff1777ceec49951bd5ee09ab734caea6370 | local branch cosmos/c3-autopsy-2026-09-30 |
| AUTOPSY_C3_WITHHELD.md | adc2e8883de11c2ff9d93cfeb88bea79acc3b0afed8955f1bd4edb27152febcc | same |
| autopsy_c3.py | 12f6733e921a05eb9083c6b7066122b1e5c02ab9bc94253cee85e9ad60ce4ba5 | same |
| AUTOPSY_DATA.json (re-run byte-identical) | 298ef81696537e474d1427724eb78d9ed197d1a94ae81a1e5859407a870be646 | same |
| visible-world map store | 28ccb48d81ea10da3c44bfefd79e7b0719637cc06a0cf030230c93c159591ec0 | withheld branch |
| law-search store | d1d2a5b042d3b70fe1888d704e86ea310b9ab53702d62b744e056fcb7c885eb1 | withheld branch |
| adversary store | e7c783fd728b7a24649e6ab41e7ec5e82c9b03cbf4358b77e2c460b9bafaa41d | withheld branch |
| audit bundle manifest / VERIFY.json | 187eebbd...b5be7d5a9 / c294f24788ccfe047a82c273d9691cdc7b8fe6658e9e55e8f63561032f2d6fc5 | M2 cosmos_runs |
| audit replicas 1 / 2 | e2d43755...f27e88c / 6349aa10...8e4d241e | M2 cosmos_runs |

## 5. What this does not show
It does not show that no substrate-independent law of historical accessibility exists. It shows that
none can be found with coordinates built from the certificate's own machinery. It does not change the
certificate's standing (v3 gate PASS, with its recorded power limit). It carries no information about
D2.
