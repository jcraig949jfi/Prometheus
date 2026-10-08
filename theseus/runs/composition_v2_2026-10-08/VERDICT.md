# THESEUS-30b verdict (prereg roles/Theseus/prereg/2026-10-08_composition_v2/, 833be3586)

Run: python -m theseus.synth.composition_v2 --tag composition_v2_2026-10-08 --workers 2
(wall 945 s, CPU 1331 s). Detector v2: a part is inert iff its state trajectory is bitwise
identical to EMPTY's at IC seeds 0 and 1; composition iff the whole is not inert and some
split gives both contiguous parts inert.

GATE (30a control genomes): planted 40/40 flagged; neg_active 0/40; neg_recall 0/40;
neg_inert 0/40 (all 40 inert as a whole). GATE PASSES.

Arms (identical sample to 23b): compositions D 0/120, E 0/120, S 0/120, G 0/120,
B 0/120, C 0/120, P 0/120, R 0/120, A 0/51. Verdict by the frozen rule: WALL-AT-v0_1.
H-COMP not supported (all zero).

Descriptive: most genomes contain inert single rules (D 106/120, R 100/120; median 1-2
inert rules), but no genome splits into two contiguous inert blocks. Limitation that
defines the successor: v2 asks whether the WHOLE genome is a two-part composition, which
a 10-14-rule genome full of active rules almost never can be even if a two-part
mechanism is embedded in it. THESEUS-30c: in-context pairwise epistasis (rules i, j each
with exactly zero effect added to the rest of the genome, nonzero together), with an
embedded-planted positive control.

Predictions: V1 gate passes RIGHT; V2 all arms < 2% RIGHT; V3 not supported RIGHT.
