# C9 -- outcome, and a post-run defect addendum

The frozen, audited record is `REPORT_C9.md`, `ADJUDICATION_C9.json` and `AUDIT_C9.json`
(21 of 21 checks PASS). It is **not edited**. This addendum records what mining the
record found afterwards. Where the two differ, this addendum says why, and the frozen
record keeps its verdicts as they were computed.

Run: protocol `5819bc6d...`, launch commit `df336f912`, 07:06:42 -> 13:51:28 (6.75 wall-h,
6 workers). 1,200 of 1,200 runs, 380 of 380 bundles complete, 0 errors. The freeze still
verifies after drain. Bundle archive: `bundles_C9.tar.gz`, sha256
`e1786a0467150c2407d4cb25d2e61e45d34e7d55bf772edc0e1550acd130bd08`.

| hypothesis | frozen verdict | classification after mining |
|---|---|---|
| H1 cue gating | NO_DETECTED_EFFECT (M = 0.0, I = 0.0) | **INVALID -- C9-D16** |
| H2 propagation | REPLICATION_EVENTS_WITHOUT_PROPAGATION (both authorship readings) | **WEAK_SIGNAL** |
| H3 reservoir (R3) | NOT_DEMONSTRATED (certificates A/B/C = 1/1/0 of 64) | **CLEAN_NULL** |

## H1 -- C9-D16: the intervention never reached the measurement

All four arms are identical to the last reported decimal: mean final held-out
competence 0.325 in every arm, crossed_ever 0.20 and crossed_at_final 0.05 in every arm.
Exact identity is not what a null looks like. `world.Runner` stores `output_gate` and
`cue_cost` (`world.py` lines 123-124), but **no task spec the world builds receives
them**. `tasks.spec_from_cell` and every `TaskSpec(...)` reconstruction in `world.py`
leave both at their defaults. The VM gate (`z8 out_gate_reads`) and the task-side
handling (`tasks.py` lines 159-161) exist and were tested. The plumbing from world to
task was never tested. H1 therefore compared one experiment with itself four times. **It
is not evidence of "no effect".** Repair and rerun: child `C9-H1R`.

## H2 -- a specimen-specific weak signal

- 15 of 16 specimens: arm B never reaches causal depth 2.
- `7ae3f9c1437c8000-s54765-tL-a0` (WELL_MIXED / Z8_64, RECOMBINATION axis): B reaches depth
  >= 5 in **4/16** seeds, >= 3 in 5/16, >= 2 in 7/16. The random-bytes control C is
  **0/16** at every depth, and in-situ arm A is 0/16. That is below the frozen bar
  (B >= 8), so the verdict is DOES_NOT_SUPPORT, and it stays so.
- `c2a87e5970ad345d-s80949-tL-a0`: B reaches depth >= 3 in 1/16.

The record contains one genome that propagates through P-11-causal copying when
implanted, never from random bytes of the same length, and never in situ. Child:
`X-H2-7AE3`.

## H3 -- a clean null, and what the material ruler saw

Cell `4931614d912c52b2`: no crossings at all in any arm (0/32/arm). Cell `a62116831aa6d956`:
crossings are common (crossed_ever A 24, B 29, C 25 of 32), and the easy niche does not
raise them (A <= B). Only one crossing per arm, in A and in B, is by a genome that is
majority easy-niche MATERIAL. The legacy id certificate would have counted 10/10/0.
Crossings here are made of hard-niche material, and the easy niche is no reservoir in
this cell.
