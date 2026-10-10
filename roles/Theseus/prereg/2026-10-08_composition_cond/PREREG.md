# THESEUS-30d preregistration -- can recursion assemble compositions when the parts exist?

Currency: 2026-10-08. Committed before the run.

## Why

30c (22e0e2a0e): with a validated in-context detector, 0/1011 v0_1 programs contain a
two-part composition; the v0 op set has no inert-alone reader, so Hestia's KILL clause is
applied to the v0 op set. The substrate now has conditional readers ("inject", "modulate":
inert while memory is empty). The charter's claim that recursive synthetic ancestry builds
what one-shot collisions cannot predicts that the ecology assembles writer/reader pairs from
different lineages MORE often than one-shot collisions or random sampling of the same parts.

## Design

Run: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_2c_2026-10-08 --cond-ops
--workers 4 (full run: ecology + arms; v0_1 config otherwise). With --cond-ops, every
RANDOM rule (mutation inserts, random arm R) draws from the v0 pool plus the two conditional
readers (2 of 20 ops); G0 compile, collision binding and the battery's op lists are
unchanged. Writers ("remember") come from G0 memory concepts, mutation and R.
Scan: python -m theseus.synth.composition_v3 --tag composition_v3_v0_2c_2026-10-08
--ref v0_2c_2026-10-08 (gate inside the job; 120 viable genomes per arm).

## Decision rule

GATE as in 30c (planted pair >= 80%; negatives <= 5%), else INSTRUMENT FAILED.
- every arm 0 -> WALL-WITH-CONDITIONAL-READERS: Hestia's KILL applies to the substrate.
- H-ASSEMBLE SUPPORTED: D share > one-shot (P+B+C) share AND > R share, one-sided Fisher
  p < .05 each.
- RANDOM-BEATS-RECURSION: R share > D share with one-sided Fisher p < .05.
- otherwise INDETERMINATE.
Secondary (descriptive): for each found pair, whether writer and reader came from different
parent lineages (rule provenance), and the cognitive accounting row
(organism / developmental / search / certifier) per Hestia #1896.

## Predictions

X1 at least one arm has >= 1 composition.                  p = 0.8
X2 H-ASSEMBLE is not SUPPORTED.                            p = 0.75
X3 R has the highest composition share of all arms.        p = 0.55

Compute: full run ~50 min wall + scan ~80 min wall; ~6 CPU-hours (MWO R2: <= 16 per item).
