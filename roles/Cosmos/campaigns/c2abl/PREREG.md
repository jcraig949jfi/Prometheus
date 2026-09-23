# c2abl -- ablation: C2 without cost lines -- PREREGISTRATION (2026-09-23 ~15:37Z, before running)

Question: C2 produced a law surviving the location gate with offsets <= .015 log2, using cost lines on
top of random data AND location-aware selection. eta2 showed cost lines alone are not earned. Which
component did the work?
Design: config c2abl = c2 with costlines = 0; SAME seed (20260929), so the pools, oracle, random main
dataset (80/family), attacks' seeds and gates are identical to C2 except that no cost-line rows exist.
No sealed universe is used (none remains).
Readout: does a law survive (confident + location gate, 3 rounds)? its per-family location offsets;
its ceiling form; LOLO scores of the candidates.
Prediction (conf 0.55): WITHOUT cost lines, location-aware selection still yields a surviving law
(i.e. selection, not the lines, did the work).
