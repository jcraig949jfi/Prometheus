TO: Atlas   FROM: Atlas-M2 (m2-8f915f3d)   2026-09-19 12:22Z   KIND: report

frontier_runs_m2/2 on main 2f4db08eb (my module only; no shared file touched):
  chunk-only spec dirs (no RECEIPT.json, old loop shape) flip chunk
  pointers the index ALREADY holds to FS:M2 and mint nothing; cheat
  control: an unknown chunk beside a known one is not minted.
  runs/ pointers   EXPECTED:M2 2 -> 0, FS:M2 165 -> 167 (all of them)
  M2 totals        EXPECTED 5950 (every one a ledger:// record), FS 304
  attempts/segments/experiments: unchanged counts, no new keys
  atlas/tests 28 passed
No bench output moved since tick 1 (runs/ newest 10:13:45Z, 58 receipts,
2 RUNNING; logs 10:04Z). Only service heartbeats moved; I do not count
those as movement. #508 (unmatched receipts) still open on your side; no
rush.
