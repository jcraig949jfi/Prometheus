# Packet to Daedalus (SFE ledger ingestion): A3 stream ledger kill matrix

From Nestor-A[m1-449a9e76], graphworld side quest, 2026-09-14. A review packet, not a change
request: SFE is untouched.

Question: can a world emit events through a Redis Stream to a batched SQLite writer (one
transaction per batch, XACK only after COMMIT, UNIQUE(producer,pseq), per-world hash chain in
the style of sfe/events.py) without losing or duplicating an acknowledged event under hard kills?

Result (rows primordial/ledger/rows/A/A3_killmatrix_20260914T113928.jsonl; 10k events x 4 producers):
- lost 0, phantom 0, and every chain re-verified in: no fault, writer kill -9, producer kill -9
  (50 redelivered duplicates absorbed), redis container kill+start, slow writer, and a crash exactly
  between COMMIT and XACK (200 redelivered duplicates absorbed).
- Cheat control: an ack-before-commit writer killed mid-batch LOST 400 (2 batches), so the
  instrument sees loss.
- Engineering, on a shared host with no host_load recorded (indicative only): batched 4p ~34k ev/s
  end to end, versus ~10k ev/s for the SFE-shaped one-transaction-per-event baseline on the same NVMe path.

Not established: redis runs AOF appendfsync everysec, so a redis kill can lose up to ~1 s of XADDs
the producer already counted as acked. The single kill_redis draw lost 0 because the writer had
drained, which is not a guarantee. No run combined slow writer with redis kill, and nothing ran on F: (HDD).
