# Pan TODO

Currency: 2026-10-10T09:35Z (UTC). Closed items are deleted with the closing commit and
date, purged after 24 h (base role s7).

- [ ] PAN-34: finish the model runs within budget (gpt-oss@4096 needs ~1.5-2 GPU-h: tomorrow),
      then report + review packet
- [ ] M2 BUSY with operator experiments (from ~09:30Z): heavy GPU/CPU work only through driver v3's idle +
      lease gates; refresh / intake with PAN_EMBED_DEVICE=cpu
- [ ] Status report 5 by ~2026-10-10T10:03Z
- [ ] PAN-37: first calibrated reviewer = a local model on the 60-item set (GPU, after PAN-34 runs); portal view
      of the review queue; dispatch to seats ONLY if the operator answers Q-011
- [ ] Daily intake + digest (next ~2026-10-10T14:30Z)
- [ ] Refresh the index each loop tick; answer seat feedback on pan search
- [ ] Act on operator answers (QUESTIONS.md Q-001..Q-010) when they arrive
- [ ] Closing report at the window end (2026-10-12T10:40Z)

Closed 2026-10-09: charter, inventory, catalog, commits, chunks, vectors,
Iceberg (8+ tables), consolidation (rows + docs), comms index, frontier intake
+ vectors + digest + snapshots, reference graph, pivot, dictionary, skill,
MONITORS row, pgvector packet, retrieval verdicts (stopped), duplication,
model smoke tests, code benchmark (PAN-33), data map dashboard, feed intake
(PAN-35: 35 feeds, controls 4/4), GitHub watch (PAN-36: 29 owners, 4/4).
