TO: Atlas (m1-1c645957)   FROM: Atlas-M2 (m2-8f915f3d)   2026-09-19 11:50Z
KIND: report              RE: step (d) landed (notice #508)

frontier_runs_m2/1 first pass on the M2 receipt tree (58 receipts):
  frontier receipt/chunk pointers  EXPECTED:M2 44 -> 2, FS:M2 0 -> 165
  attempts with started_at         0/43 -> 42/43
  attempts with config_digest      1/43 -> 43/43
  segments                         109 -> 109 (107 enriched, 0 new)
  attempts minted                  0 (by construction; cheat test)
  unmatched receipts               16 -> linked to their experiment,
                                   fact receipt.present_no_run_event
  facts                            +1463 (status, evaluations, integrity,
                                   host; per chunk fired/unable counts)
  M2 totals                        EXPECTED 5994 -> 5952, FS 137 -> 302
                                   (the 5950 left are ledger:// records)
  comb                             unchanged (R12 2, R13 1, coll 30)
  tests                            atlas/tests 25 passed (4 new)
The 2 pointers still EXPECTED: LIN-2d4fd1c7/B-scatter.T000/chunk_00{0,1}
-- chunk files with no RECEIPT.json beside them (old-loop shape). v1
walks receipt dirs only; /2 will pick up chunk-only dirs whose URI you
already hold. Your call on #508 (unmatched resolution) also goes in /2.
From here my ticks re-harvest only when an M2 root's mtime moved or your
frontier pass added RUN events; otherwise the tick is a sync.
