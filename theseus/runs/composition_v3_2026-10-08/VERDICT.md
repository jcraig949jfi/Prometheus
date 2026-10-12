# THESEUS-30c verdict (prereg roles/Theseus/prereg/2026-10-08_composition_v3/, a2e1a5ac1)

Run: python -m theseus.synth.composition_v3 --tag composition_v3_2026-10-08 --workers 2
(wall 4778 s, CPU 6749 s). Detector v3: in-context pairwise epistasis, bitwise traces at IC
seeds 0, 1 (two rules each with zero effect added to the rest of the genome, nonzero together).

GATE: planted 40/40 genomes with a composition and the planted pair found in 40/40;
neg_bg 0/40; neg_recall 0/40 (writer/recall pair found 0/40). GATE PASSES.

Arms (identical v0_1 sample of 23b/30b): genomes with >= 1 in-context composition:
D 0/120, E 0/120, S 0/120, G 0/120, B 0/120, C 0/120, P 0/120, R 0/120, A 0/51.
Verdict by the frozen rule: WALL-IN-CONTEXT-AT-v0_1. H-COMP not supported (all zero).

Scope (stated so it is not over-read): the v0_1 genomes are built from the v0 op set, whose
only memory reader ("recall") acts alone; the conditional readers ("inject", "modulate")
did not exist when v0_1 ran. This verdict therefore applies Hestia's KILL clause (#1897
s4.19) to the v0 OP SET: no v0_1 program, deep, shallow, one-shot, LLM-written or random,
contains a two-part mechanism whose parts are each inert in context. Whether the substrate
WITH conditional readers hosts composition, and whether recursion assembles one, is
THESEUS-30d. The control harness (30a/30b/30c detectors and gates) is kept.

Predictions: W1 gate passes RIGHT; W2 some arm has >= 1 composition WRONG; W3 H-COMP not
supported RIGHT.
