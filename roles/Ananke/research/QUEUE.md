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
