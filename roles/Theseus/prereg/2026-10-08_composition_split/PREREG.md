# THESEUS-30e preregistration -- assembly test with the parts placed in different G0 lineages

Currency: 2026-10-08. Committed before the run (30d's verdict is not yet scored).

## Why

30d's design has an availability confound found before its scan finished: only 4/1182
ecology mechanisms in v0_2c contain any conditional reader (readers enter only via rare
mutation inserts), while the random arm draws them at 2/20 per rule. 30e makes the parts
available to every search arm from the start, so the comparison is about ASSEMBLY.

## Design

G0 variant compile_g0(readers=True): memory concepts carry a writer ("remember", no
"recall"); delayed/routed concepts carry inert-alone readers ("inject"/"modulate") instead
of "delay"/"gate"; a concept that fires both keeps exactly one part by name-hash parity.
Result: 30 writer-only, 16 reader-only, 0 both (no composition exists in G0 by construction).
Default compile is unchanged (byte-identical to the committed v0_1 corpus).
Run: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_2r_2026-10-08 --g0-readers
--cond-ops --workers 4 (full run). Scan: composition_v3 --ref v0_2r_2026-10-08 (gate inside).

## Decision rule

GATE as 30c. Then per arm the share of genomes with >= 1 in-context composition; G0 arm
must be 0 (check of construction). H-ASSEMBLE SUPPORTED: D share > one-shot (P+B+C) share
AND > R share, one-sided Fisher p < .05 each. ONE-SHOT-SUFFICES: one-shot share >= D share.
RANDOM-BEATS-RECURSION: R > D, one-sided Fisher p < .05. Every arm 0 -> WALL-WITH-PARTS-
AVAILABLE (Hestia's KILL applies to the substrate). Otherwise INDETERMINATE.
Accounting rows (organism / developmental / search / certifier) filled for found pairs.

## Predictions

Y1 at least one one-shot arm contains a composition.         p = 0.7
Y2 H-ASSEMBLE is SUPPORTED.                                  p = 0.3
Y3 D share > pooled one-shot share (point estimate).         p = 0.45

Compute: full run ~60 min wall + scan ~80 min wall; ~6 CPU-hours.
