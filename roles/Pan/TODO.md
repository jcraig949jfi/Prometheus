# Pan TODO

Currency: 2026-10-15T08:47Z (UTC). Closed items are deleted with the closing commit and
date, purged after 24 h (base role s7).

- [ ] M2 BUSY with operator experiments (from ~09:30Z): heavy GPU/CPU work only through driver v3's idle +
      lease gates; refresh / intake with PAN_EMBED_DEVICE=cpu
- [ ] SAGACITY FOUNDATION (operator 2026-10-11, prompts/2026-10-11_sagacity_foundation): all deliverables DONE
      -- P1 PAN-40/41/42 (c22bf02f4); P2 PAN-43 (packet REVIEW_PACKET_2026-10-11_PAN43.txt); P3 PAN-44 (MCP
      stdio read-only, 15/15 + SDK conformance); PAN-45 handoff + checkpoint packet DELIVERED 2026-10-12T10:42Z;
      PAN-46 DESIGNED (docs/sagacity/PAN46_CACHE_AND_FABRIC_DESIGN.md: no cache until its precommitted trigger
      fires). Loop extended to 2026-10-16T10:40Z.
- [ ] PAN-26 evidence wiki: still BLOCKED -- PEW port 8377 refused on M2 (127.0.0.1) and timed out on M1
      (192.168.1.202), last re-check 2026-10-15T13:47:20Z; re-check daily
- [ ] Status report 25 by ~2026-10-15T14:47Z (report 24 written 08:47Z); next fleet re-probe + republish ~20:47Z
- [ ] ubu002 off the LAN since 08:24Z (last ok 2026-10-12T22:29Z); FYI posted #2241 (Achilles + operator, 09:30:01Z):
      re-check each tick; post again only when it comes back
- [ ] PAN-37: 3 reviewers scored + packet (2026-10-11); dispatch to seats ONLY if the operator answers Q-011
- [ ] Daily intake + digest (next ~2026-10-15T14:30Z; 2026-10-14 done 15:06Z; when >150 items wait for vectors, prefer the GPU under a gpu0 lease)
- [ ] Machines/Pantheon tabs (+ per-engine CPU sample in the local probe, for Achilles #2090): re-probe + rebuild fleet datasets each loop tick (fleet probe; mk_datamap --only fleet;
      upload + dataset url update); Q-012 decides whether ubu004-006 get measured
- [ ] Refresh the index each loop tick; answer seat feedback on pan search
- [ ] Atlas copy each loop tick: python -m pan atlas snapshot (skips unless Atlas harvested)
- [ ] Act on operator answers (QUESTIONS.md Q-002..Q-018) when they arrive
- [ ] Closing report at the extended end 2026-10-16T10:40Z: reports/CLOSING_REPORT, WORK_STATE HOLD, stop the loop

Closed 2026-10-09: charter, inventory, catalog, commits, chunks, vectors,
Iceberg (8+ tables), consolidation (rows + docs), comms index, frontier intake
+ vectors + digest + snapshots, reference graph, pivot, dictionary, skill,
MONITORS row, pgvector packet, retrieval verdicts (stopped), duplication,
model smoke tests, code benchmark (PAN-33), data map dashboard, feed intake
(PAN-35: 35 feeds, controls 4/4), GitHub watch (PAN-36: 29 owners, 4/4).
Closed 2026-10-11: PAN-34 (report + packet).
Closed 2026-10-14: PAN-52 Machines-tab labels for hosts skipped by ruling (datasets v12, 20:48:51Z).
Closed 2026-10-12: stale "review packet for PAN-27 + PAN-28" line (REVIEW_PACKET_2026-10-10_PAN27_28.txt s5.1 already records
the too-easy recall gate); stale "PAN-46 design note next" (designed 2026-10-11).
Closed 2026-10-10: PAN-38 fleet tabs; PAN-27 atlas copy (7/7); PAN-28 pgvector (5/5); Atlas's two
M1 defects (tables_cli schema-qualified; pivot neighbours off M2 via pgvector).
