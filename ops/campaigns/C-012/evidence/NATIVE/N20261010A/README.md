# C-012-T007 -- the first deterministic native-world epochs through the PostgreSQL path (run N20261010A)

OP-NF2: "Once PostgreSQL-backed synthetic epochs are qualified, put the first deterministic native-world epoch through
the new path." Qualified by T004 (operating point ADEQUATE, correctness gate PASS). Window 2026-10-10 ~11:23Z-11:25Z
(comms #2041), canonical Fabric queue, production Moonshot schema `moonshot` (created by this run), namespace
"native". Approved code 3f6c23ee4 (main), staged on both nodes before the window.

What ran: three wforge worlds (design v0.3 s8: the primary substrate), each 4 epochs x 8 ticks, under runtime
moonshot.native.wforge v1 (one Encounter per chain; the checkpoint holds the Encounter's ENTIRE state) and the fixed
frugal affordable-seeded policy, which never takes an unaffordable action -- wforge's F09 path is never exercised;
no organism; no survival search. The worlds were chosen so every part of the native state crosses nodes:

| Chain | World | Exercises | Epoch hosts | Outcome |
|---|---|---|---|---|
| NW1-E0 | Wbeea140cff34638d (genome seed 1, horizon 128) | stochastic stream (1/8), observation corruption (1/8), observation delay 2 | ubu002, ubu001, ubu002, ubu001 | 4 PUBLISHED, 4 VALIDATED, = reference |
| NW5-E0 | W20d3ef324b27eedd (seed 5, horizon 256) | action delay 4 (pending writes cross epoch boundaries), corruption (1/16), observation delay 2 | ubu001, ubu002, ubu001, ubu002 | 4 PUBLISHED, 4 VALIDATED, = reference |
| NW8-E0 | W125c2d03b50da697 (seed 8, horizon 128) | two slots, action delay 1 | ubu002, ubu001, ubu002, ubu002 | 4 PUBLISHED, 4 VALIDATED, = reference |

- Every epoch restored the checkpoint the previous epoch's node wrote, mostly on the OTHER node (Linux -> Linux),
  and every epoch was replayed on M2 (Windows) from the lineage input: 12/12 VALIDATED.
- "= reference": each published lineage equals an in-process replay of the same world with no Fabric, no database
  and no node -- checkpoint conformance holds through the real path, across nodes and operating systems.
- The wforge implementation hash in every spec (37cb6fff8cd6...) matched on M2 and both nodes (a different one is
  refused).
- No git remote in the window: FETCH_HEAD mtimes unchanged (ubu001 1791631388, ubu002 1791631389; staging fetch
  11:23Z). Audit: 12 attempts by the moonshot workers, 0 foreign claims, 0 Fabric events by other actors.
- Receipts (canonical, also stored content-addressed in moonshot.objects): RECEIPT_NW1-E0.json (4cec29e73ee2...),
  RECEIPT_NW5-E0.json (2098b99e9a64...), RECEIPT_NW8-E0.json (e866d36dba0c...).
- Lake (Pan's Iceberg, namespace moonshot, production tables -- Pan #2031: "Production tables without the prefix are
  fine when the first native-world epoch lands"): lake/MATERIALIZE_1.json ran inside the 60 s settle window and took
  only what was eligible (1 epoch, 8 trace lines, 1 attempt; oracle OK); lake/MATERIALIZE_2.json appended exactly
  the rest from each table's watermark (11 epochs, 88 trace lines, 11 attempts, 12 validations; oracle OK on all
  six). moonshot.catalog_v now lists the 12 live native epochs for Pan's collector.

Files: RUN.json (chains, per-step Fabric task/attempt/host/timing, classifications, validations, receipts, reference
comparison, preflight before/after, audit), RECEIPT_*.json, lake/MATERIALIZE_*.json; ../run_native.py the driver.

Not established: anything about organisms or survival (fixed policy, plumbing); behaviour of epochs longer than 8
ticks or of large checkpoints (these are under 1 KB; contract item N1 covers large ones); F09 itself (avoided by
construction, still open with its owner).
