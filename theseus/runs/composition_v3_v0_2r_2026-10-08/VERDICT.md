# THESEUS-30e verdict (prereg roles/Theseus/prereg/2026-10-08_composition_split/, ba8fea644)

Run: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_2r_2026-10-08 --g0-readers
--cond-ops --workers 4, then composition_v3 --ref v0_2r_2026-10-08 (wall 2085 s, CPU 7580 s).
G0: 30 writer-only, 16 reader-only, 0 both. Availability (fixing 30d's confound): 197/1170
ecology mechanisms carry a reader, 86 carry both writer and reader.

GATE: planted pair 40/40; neg_bg 0/40; neg_recall 0/40. PASSES.
Genomes with >= 1 in-context composition: D 1/120, B 1/120, R 3/120; E, S, G, C, P 0/120;
A 0/36. D > one-shot (1/360) p .44; D > R p .94; R > D p .31; one-shot > D p .94.
VERDICT: INDETERMINATE (no preregistered clause met). Not SUPPORTED: recursion does not
assemble writer/reader pairs more often than one-shot collisions or random sampling.

Failure shape (descriptive): of 30 viable ecology genomes holding both parts, only 4 have the
writer and a reader on the SAME memory channel (2 of those also carry a "recall" there).
Collisions remap channels by parent position ((c + j) mod C), so parts inherited from
different lineages almost always address different memory slots. Assembly fails at
ALIGNMENT (a reachability bottleneck in Hestia's #1897 table), not for lack of parts.
Successor THESEUS-34: channel-identity-preserving binding (named memory ports) with the same
detector, gate and arms.
Descriptive: the run's own pipeline H1 is FAIL (n 36).

Predictions: Y1 a one-shot arm has a composition RIGHT (B 1/120); Y2 H-ASSEMBLE supported:
not supported, scored RIGHT-for-the-claim's-negation (p .3 given) -- recorded as RIGHT;
Y3 D share > one-shot share (point estimate) RIGHT (1/120 vs 1/360) but not significant.

CORRECTION 2026-10-08 (same session, before any use): Y2 was the statement "H-ASSEMBLE is
SUPPORTED" (p .3); it was not supported, so Y2 is WRONG. The line above scoring it "RIGHT"
is wrong and is superseded by this note (ledger row added).
