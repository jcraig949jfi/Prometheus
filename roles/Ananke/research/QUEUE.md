# Ananke experiment queue (mature experiments waiting for a resource)

Queued Threads are ready to run as written. Researchers do not wait:
while an item waits, other work continues.

Q1 T-CT-1 carrier census over all C1 SIGNAL cells (threads/
   T-CT-1_carrier_census.md). Needs: a GPU lease, ~1 h, <= 2 GB VRAM.
   Queued 2026-09-27: the GPU is leased by worker W-B (SETRULE census)
   under the host lease file. Runs when that lease is released. PLAN.md
   is written first, per the thread.
   -> DEQUEUED 2026-09-27: W-B released the GPU lease; dispatched to worker
      W-F (workers/W-F/), which takes the lease itself.

Q2 T-WC-2 / X4: does an emission cost select presence codes? 4 remaining
   full-spec GA searches (HOLD at M2 physics; arms A0/A1, seeds 1-2 plus
   the GPU re-run of seed 0). Exact commands and the fixed decision rule
   are in workers/W-C/QUEUE.md. Needs: a GPU lease, ~40 min. Queued
   2026-09-27: GPU leased by W-F (carrier census). Runs when released.
