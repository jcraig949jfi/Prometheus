# BEL-RD-72 REVIEW RECORD

## R1 -- adversarial review of the K design (background agent, 2026-10-10 10:26Z -> ~12:55Z; read-only; scripts in session scratch reviewK/)

Mandate: break the K reachability desert and the K endpoints (shortcuts, leakage, environmental completion, attribution,
plan / analysis). Heavy searches on a C port of the VM validated against tasks.verify_exact on 40,000 tapes (2,231
competent) and a Python port on 60,000.

| item | verdict | evidence |
|---|---|---|
| 1 shortcuts | SOUND | 2-step: 0 competent of ~3.0e9 per fixture (all ordered pairs of SUB/INS/DEL/MOVE<=16); 3-SUB at 7..20 0/6.0e9; 3-mixed reduced alphabet 0/2.0e9; DEL 0/64; short programs 0/8.4M; only other compact transform (x^0xD5)+0x83, same length; min distance 4 SUB (X), 5 (Y) |
| 2 reward leakage | SOUND (minor) | random 0/300,000 competent (~0.5% LO-correct); every single mutant non-competent; 16-input panel vs 256 -> add full check |
| 3 environmental completion | SOUND | truncated writers k = 8..24 over random targets 0/1.0M; real execution: one route (Y copy-length 5 -> 12 writing over X_al), competent but not a replicator; robust to one background mutation 18,094/20,000 |
| 4 two-source attribution | BROKEN | 5/14 critical positions identical in X and Y; 9/9 single-source machines labelled two-source in a real XY_AL world |
| 5 plan / analysis | CONCERN | extinction -> trivial nulls; ON vs OFF confounds selection with parent survival; dose 32 vs 16+16; SH/NS gradient absent in physics; seeds unpaired (harmless) |

Disposition: all six ranked fixes adopted (prereg s3 amendment A1; plan_k2 / analyze_k2), K-P4 control RANDOM_REWARD
(YOKED would need a dependency on each ON run; RANDOM_REWARD gives the same total bonus with no individual link). No K
run had been made. Load note: the review ran at nice 5 for ~2 h beside D1 / A3; no data effect (runs are deterministic).
