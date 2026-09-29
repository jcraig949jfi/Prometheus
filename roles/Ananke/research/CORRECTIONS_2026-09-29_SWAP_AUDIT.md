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
