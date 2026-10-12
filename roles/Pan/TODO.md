# Pan TODO

Currency: 2026-10-12T14:18Z (UTC). Closed items are deleted with the closing commit and
date, purged after 24 h (base role s7).

- [ ] M2 BUSY with operator experiments (from ~09:30Z): heavy GPU/CPU work only through driver v3's idle +
      lease gates; refresh / intake with PAN_EMBED_DEVICE=cpu
- [ ] SAGACITY FOUNDATION (operator 2026-10-11, prompts/2026-10-11_sagacity_foundation): deliverables due
      2026-10-12T10:40Z -- P1 PAN-40/41/42 DONE (c22bf02f4: map, proposals 15/15, access 12/12); P2 PAN-43 DONE
      (calibration PROMOTED; prereg A1-A4; smoke plumbing only; packet REVIEW_PACKET_2026-10-11_PAN43.txt); P3 PAN-44 DONE (MCP stdio read-only, 15/15 + SDK conformance); PAN-45 handoff WRITTEN, checkpoint packet
      at 2026-10-12T10:40Z; PAN-46 design note next;
      continuity handoff + checkpoint packet. Loop extended to 2026-10-16T10:40Z. PAN-46 Redis/A2A: design first.
- [ ] Status report 14 by ~2026-10-12T20:18Z (report 13 written 14:18Z)
- [ ] PAN-37: 3 reviewers scored + packet (2026-10-11); dispatch to seats ONLY if the operator answers Q-011
- [ ] Daily intake + digest (next ~2026-10-12T14:30Z; 2026-10-11 done 14:43Z)
- [ ] Machines/Pantheon tabs (+ per-engine CPU sample in the local probe, for Achilles #2090): re-probe + rebuild fleet datasets each loop tick (fleet probe; mk_datamap --only fleet;
      upload + dataset url update); Q-012 decides whether ubu004-006 get measured
- [ ] Refresh the index each loop tick; answer seat feedback on pan search
- [ ] Atlas copy each loop tick: python -m pan atlas snapshot (skips unless Atlas harvested)
- [ ] Review packet for PAN-27 + PAN-28 (pgvector: the packet's recall gate was too easy -- record it)
- [ ] Act on operator answers (QUESTIONS.md Q-002..Q-012) when they arrive
- [ ] Closing report at the extended end 2026-10-16T10:40Z (checkpoint packet DELIVERED 2026-10-12T10:42Z)
      (DRAFT written 2026-10-11 ~12:35Z in the session scratchpad as CHECKPOINT_DRAFT.txt; at 10:40Z refresh its
      numbers/replies, fill <END>/<final>, publish as reports/CHECKPOINT_PACKET_2026-10-12_SAGACITY.txt)

Closed 2026-10-09: charter, inventory, catalog, commits, chunks, vectors,
Iceberg (8+ tables), consolidation (rows + docs), comms index, frontier intake
+ vectors + digest + snapshots, reference graph, pivot, dictionary, skill,
MONITORS row, pgvector packet, retrieval verdicts (stopped), duplication,
model smoke tests, code benchmark (PAN-33), data map dashboard, feed intake
(PAN-35: 35 feeds, controls 4/4), GitHub watch (PAN-36: 29 owners, 4/4).
Closed 2026-10-11: PAN-34 (report + packet).
Closed 2026-10-10: PAN-38 fleet tabs; PAN-27 atlas copy (7/7); PAN-28 pgvector (5/5); Atlas's two
M1 defects (tables_cli schema-qualified; pivot neighbours off M2 via pgvector).
