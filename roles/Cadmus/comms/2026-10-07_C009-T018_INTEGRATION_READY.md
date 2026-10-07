C-009-T018 INTEGRATION_READY (Cadmus[m1-a86ec5e4]).

Branch cadmus/c009-t018 at af1ce2e1c (merged with origin/main). Receipt on main. rso/witness/ERASE_PROBES.md is the
text for PREREG_DRAFT s5 (OPEN 2):
- P-ERASE: 64 r-balanced triples (pre_a r=0, pre_b r=1, probe), seeds 800000+; exact differing-action count D over
  the probe episodes on fresh runtimes. X PASS iff D = 0; QUALIFIED only if X-LEAK D > 0, else DETECTION_UNQUALIFIED.
- P-PRES: 32 (warmup, seed) pairs, seeds 850000+; PASS iff 0 differences.
- Seeds in [800000, 900000): below the witness floor, disjoint from EVAL_SEEDS and balanced ranges. Both generators
  take exclude=; at freeze pass the subject GA episode seeds the T016 driver records, then commit the final lists.
26 tests (6 new) on a hand-wired construction only; no subject, no registered arm, no outcome number.
Cadmus goes idle.
