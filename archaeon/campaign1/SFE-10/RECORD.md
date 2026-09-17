# SFE-10 -- PRODUCER-CONSUMER SPECIALIZATION (record; directive IV shape)

## A. STARTUP

- experiment ID: SFE-10
- question: under a MATCHED total resource envelope with EXPLICIT
  communication and storage costs, does a system of producers (searching
  source cells and publishing artifacts) plus a consumer (importing them
  and searching the target) improve later solving over a monolithic
  search of the same total budget?
- starting commit: the SFE-09 close commit; harness sfe10.py.
- services: engine v2 (two producer worlds FULLY_SHARED and one consumer
  world EXPLICIT_IMPORT_ONLY under one topology group; producer elites
  published as info_kind success artifacts; imported and fetched by the
  consumer, which runs with the fetched bytes; experiment + observation
  per arm x seed).
- envelope: N=200, G_total=60 generations, E=16 on target W2_K2 (4-bit).
  mono spends all 60 on the target. pc_p: producers on W0 and W1_d1 spend
  round(60 x p / 2) generations each (p in {0.2, 0.4}: 6+6 and 12+12);
  the consumer pays communication ceil(bytes/4096) generations and
  storage 0.5 generation per artifact held, and spends the remainder on
  the target seeded from the fetched elites (top-4 per producer).
  pc_p_noex: the same producer spend, consumer with random generation 0
  and the remainder (no exchange costs): the artifact effect vs budget
  loss.
- seeds 1,2,3; common random numbers for the consumer arms.
- controls: mono; noex; costs declared before running and recorded per
  arm in the receipt (bytes, artifacts, generations charged).
- assay capability: W2_K2 is reachable from random generation 0 in some
  seeds (SFE-01 00: 1/3 at G=60) and from register seeds (SFE-07/08); if
  mono and every pc arm stay at the floor the row is INCONCLUSIVE.
- time: 12 producer runs (short) + 15 consumer runs; ~3 min on 12 procs.
