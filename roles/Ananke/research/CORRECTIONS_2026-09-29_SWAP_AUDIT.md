# Carrier-swap CHANCE audit: corrections register (2026-09-29)

Source: E-ANANKE-W-O (workers/W-O/REPORT.md, sha256 4d11edc1ca762cdc).
733 recorded CHANCE swap verdicts (W-F census, W-I trajectories, spikes
s_ct) re-run at 512 worlds, SINGLE-trial swaps, same absolute rule
(lens.swap_verdict). Principal recount from workers/W-O/out/rerun_table.csv:
615 stay CHANCE, 90 -> FLIP, 28 -> NO-EFFECT; readable (recorded normal
lo99 >= .60): 439 / 39 / 17. Inventory frozen by sha256 73eecd8a77a0c4e5
before any re-run (verified).

The raw records are NOT edited (they are other workers' outputs with
provenance). Read them through these registers:
- W-F census_table.csv class / class_late: workers/W-O/out/corrections_WF.csv
  (13 cells; e.g. 0187372b, 11f3ac85, 83d9d7b5 ELSEWHERE -> SITE; 2dccdaa5,
  8c37f32e, c16d5231 JOINT -> SITE; 8743da7f JOINT -> CHANNEL), plus 12
  UNREADABLE cells that get a class if readability is judged at 512 worlds.
- W-I table_<cell>.csv reader letters: workers/W-O/out/corrections_WI.csv
  (11 letters on 369f5a5b, 4781b0a1, 613162a3, c16d5231, cd5b6fd6, 8c37f32e;
  W-I motif strings built from them should be re-derived).
- W-E classes (from s_ct): no change.
Not audited: W-B deepdive*, W-C x1b_x5/x4, W-H cf, W-J e2/e3/e6, spikes
s_joint_4781 / s_m2.

## Qualification from W-P (T-INS-8, 2026-09-29)
For 4781b0a1 o14/o15 the corrected letters C / S describe the dominant
pattern, but ~1/3 of pair-trials there (.64-.70 within one clock phase) are
a clean JOINT carrier {Acc_sum, payload-1 in flight}. For 369f5a5b o2 the
proposed J -> S is NOT supported (W-P: fS .45, fN .33, higher-order). Treat
single letters on these cells as summaries only; see workers/W-P/REPORT.md.

## Qualification from W-Q (T-SWAP-REL2, 2026-09-29)
Of W-O's 42 "complete transfers at normal ~.57-.62", 24 are complete
(z <= -.95) and 16 are partial (z -.57 to -.77); they are 20 dependent
specimen x source x offset groups, not 42 independent findings. Under the
per-verdict relative rule, 95 of the 615 absolute-CHANCE verdicts become
FLIP_REL (53 of them only under the non-strict rule). Per-verdict table:
workers/W-Q/out/rel2_table.csv.
