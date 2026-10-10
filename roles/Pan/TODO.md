# Pan TODO

Currency: 2026-10-10T14:38Z (UTC). Closed items are deleted with the closing commit and
date, purged after 24 h (base role s7).

- [ ] PAN-34: finish the model runs within budget (gpt-oss@4096 needs ~1.5-2 GPU-h: tomorrow),
      then report + review packet
- [ ] M2 BUSY with operator experiments (from ~09:30Z): heavy GPU/CPU work only through driver v3's idle +
      lease gates; refresh / intake with PAN_EMBED_DEVICE=cpu
- [ ] Status report 6 by ~2026-10-10T16:00Z
- [ ] PAN-39: calibration set v2 without textual tells (tell gate; CPU kill checks under spectrex5:cpu12)
- [ ] PAN-37: first calibrated reviewer on set v2 (GPU, after PAN-34 runs), reported against the floors;
      dispatch to seats ONLY if the operator answers Q-011
- [ ] Daily intake + digest (next ~2026-10-11T14:30Z)
- [ ] Machines/Pantheon tabs: re-probe + rebuild fleet datasets each loop tick (fleet probe; mk_datamap --only fleet;
      upload + dataset url update); Q-012 decides whether ubu004-006 get measured
- [ ] Refresh the index each loop tick; answer seat feedback on pan search
- [ ] Atlas copy each loop tick: python -m pan atlas snapshot (skips unless Atlas harvested)
- [ ] Review packet for PAN-27 + PAN-28 (pgvector: the packet's recall gate was too easy -- record it)
- [ ] Act on operator answers (QUESTIONS.md Q-002..Q-012) when they arrive
- [ ] Closing report at the window end (2026-10-12T10:40Z)

Closed 2026-10-09: charter, inventory, catalog, commits, chunks, vectors,
Iceberg (8+ tables), consolidation (rows + docs), comms index, frontier intake
+ vectors + digest + snapshots, reference graph, pivot, dictionary, skill,
MONITORS row, pgvector packet, retrieval verdicts (stopped), duplication,
model smoke tests, code benchmark (PAN-33), data map dashboard, feed intake
(PAN-35: 35 feeds, controls 4/4), GitHub watch (PAN-36: 29 owners, 4/4).
Closed 2026-10-10: PAN-38 fleet tabs; PAN-27 atlas copy (7/7); PAN-28 pgvector (5/5); Atlas's two
M1 defects (tables_cli schema-qualified; pivot neighbours off M2 via pgvector).
