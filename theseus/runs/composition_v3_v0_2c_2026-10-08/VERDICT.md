# THESEUS-30d verdict (prereg roles/Theseus/prereg/2026-10-08_composition_cond/, 83fb032c3)

Run: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_2c_2026-10-08 --cond-ops
--workers 4 (full run), then composition_v3 --ref v0_2c_2026-10-08 (wall 3059 s, CPU 7412 s).

GATE: planted pair 40/40; neg_bg 0/40; neg_recall 0/40. PASSES.
Genomes with >= 1 in-context composition: R 19/120; D, E, S, G, B, C, P 0/120; A 0/51.
Every found pair is writer + conditional reader: remember with inject (10) or modulate (9).
D > one-shot p 1.0; D > R p 1.0; R > D one-sided Fisher p 8.8e-7.
VERDICT: RANDOM-BEATS-RECURSION.

Confound (found before this scan was read, recorded in 30e's prereg ba8fea644): conditional
readers enter the ecology only through rare mutation inserts -- 4/1182 v0_2c ecology
mechanisms contain any reader -- while the random arm draws them at 2/20 per rule. The
verdict is mostly an AVAILABILITY result: recursion did not assemble parts it almost never
had. 30e places writers and readers in different G0 lineages to test assembly itself.
What this run does establish: compositions of inert-alone parts OCCUR NATURALLY in this
substrate when the parts are present (16% of random programs at a 2/20 part rate), and the
v3 detector finds them outside its planted gate.
Descriptive (not the 30d question): the run's own pipeline H1 at n = 51 is FAIL.

Predictions: X1 some arm > 0 RIGHT; X2 H-ASSEMBLE not supported RIGHT; X3 R highest RIGHT.
