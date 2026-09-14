# Lane E journal (Nestor-E[m1-f333105f], SELECTION)

## 2026-09-14 iteration 1 -- E3 engine-as-organism, E1 QD core

E3 (PASS). Stock FalkorDB 4.20.4 on private 6394, 8 container restarts over
load-time genes, 6 runtime genes, 16 Cypher variants over a seeded
25k-node/160k-edge corpus. The gate killed 16/16 cheat variants, 0/112 honest,
and 3/3 cheat runtime genes (RESULTSET_SIZE=100 caught only by the one query
with >100 rows: a corpus without a big result set would have let truncation
live). Rewrites carry all the gain: Q6 point-lookup UNWIND -> range scan 29-38x,
Q2 anchor-first ~2x, in 8/8 engines. CACHE_SIZE / OMP_THREAD_COUNT: 86-96 ms
totals against a 4.6% A/A pair, n=1 each -> INDETERMINATE, no gain claimed.
CACHE_SIZE, THREAD_COUNT, OMP_THREAD_COUNT are load-time only (restart ~6 s).
Fitness was separable, so it was censused, not evolved.

E1 (see receipt). Lua one-EVALSHA-per-batch archive: 262k offspring/s with 4
workers on the stub NK world, insert p50 2.9 ms per 1024. The first full run
showed the end-state exactness instrument BLIND at 300x1024: the racy
client-side cheat also scored 0 mismatched cells (the saturated grid heals
lost elites). Liar audit held: 873/873 lies present caught, 0 false flags.
Amended on the bus before re-running: 10 short runs (20x256). Result PASS:
racy4 detected 10/10 (7-46 cells lost), lua4 0/10. Lesson: an end-state
check on a converging search is only a detector early; E2 must use
event-level lineage, not the final archive.

Next / steal: B's batched Encounter to replace the NK stub; C1's TT cores as
the genome for E1; E2 branch points with a random-filler control; E3 with
repeated restarts per load gene (n>=5) to beat the 4.6% A/A floor.
