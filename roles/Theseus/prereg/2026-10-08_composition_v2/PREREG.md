# THESEUS-30b preregistration -- composition detector v2 (trace inertness) on the v0_1 arms

Currency: 2026-10-08. Committed before any run of theseus/synth/composition_v2.py.

## Why

30a showed the 23b detector is blind (planted 0/40). An exploratory post-hoc check on
the same 30a control genomes found a trace-based inertness test flags planted 40/40 and
negatives 0/40. That check is development, not evidence; this preregistration fixes the
v2 detector and re-runs its validity gate inside the same job before reading any arm.

## Detector v2

Part P inert iff its state trajectory equals EMPTY's bitwise at IC seeds 0 and 1.
COMPOSITION iff the whole is not inert and some split gives both parts inert.

## Design

Gate: the 160 THESEUS-30a control genomes. Arms: the identical sample used in 23b
(composition.load_arms, seed 20261008, 120 per arm; A 51) from committed v0_1 rows.
Descriptive per genome: inert rules, inert prefixes/suffixes.

## Decision rule

1. GATE: planted >= 80% flagged AND each negative class <= 5%. If the gate fails, the
   arm results are not read as evidence (reported as INSTRUMENT FAILED).
2. If the gate passes:
   - every arm 0 compositions -> WALL-AT-v0_1 (no two-part composition of inert-alone
     parts exists in any v0_1 arm sample; with a validated detector this is evidence)
   - H-COMP as in 23b: D rate > one-shot (P+B+C) rate and > R rate, one-sided Fisher
     p < 0.05 each -> SUPPORTED; D rate <= both -> NOT SUPPORTED; else INDETERMINATE.

## Predictions

V1 gate passes.                                                   p = 0.9
V2 every v0_1 arm has a composition rate < 2%.                    p = 0.75
V3 H-COMP is not SUPPORTED.                                       p = 0.85

Compute: trace runs only (no fingerprints): ~1200 genomes x ~4n runs x 17 ms / 4 CPUs,
about 15-30 min.
