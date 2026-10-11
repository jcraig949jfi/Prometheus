# THESEUS-34 verdict (prereg roles/Theseus/prereg/2026-10-08_aligned_binding/, ddc22ff73)

Run: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_2a_2026-10-08 --g0-readers
--cond-ops --aligned-binding --workers 4; scan composition_v3 --ref v0_2a_2026-10-08 (wall
1756 s, CPU 6275 s). (run_v0.py gained a default-off --master-seed flag while this run was in
progress; later pools re-imported it; behaviour unchanged.)

MANIPULATION CHECK: viable ecology genomes holding both parts with writer and reader on the
same memory channel: 15/31 (34) vs 4/30 (30e); one-sided Fisher p .0032. PASSES.
GATE: planted pair 40/40; neg_bg 0/40; neg_recall 0/40. PASSES.
Genomes with >= 1 in-context composition: D 2/120, G 1/120, P 1/120, R 5/120; E, S, B, C
0/120; A 0/36. D > one-shot (1/360) p .16; D > R p .94; R > D p .22.
VERDICT: INDETERMINATE. Every found pair is remember + inject/modulate.

Reading across 30c-34 (descriptive): with the parts available (30e) and aligned (34),
writer/reader compositions appear at low rates in EVERY arm, roughly at the rate the parts
happen to co-occur; recursion does not enrich them. Nothing in the ecology selects for a
composition (no task, no reward) -- Hestia's REWARD bottleneck. The task controls already
show a writer + inject pair solves cue recall (memcomp J 1.0, 31a/31b), so the next test is
a TASK-SELECTED ecology on this substrate (THESEUS-31c).

Predictions: A1 manipulation passes RIGHT; A2 D share higher than 30e (2/120 vs 1/120) RIGHT;
A3 H-ASSEMBLE supported WRONG.
