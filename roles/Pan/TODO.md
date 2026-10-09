# Pan TODO

Currency: 2026-10-09T11:50Z (UTC). Closed items are deleted with the closing
commit and date, purged after 24 h (base role s7).

- [ ] PAN-31 v2 retrieval: doc-level vectors (stronger model) + duplicate-aware
      prior; freeze a NEW held-out set first (the v1 held-out set is spent)
- [ ] PAN-16 consolidation recipe: committed .jsonl/.json result rows ->
      Parquet + Iceberg, source line counts as the oracle
- [ ] PAN-17 incremental refresh loop (bounded, productivity signal; MONITORS row)
- [ ] PAN-18 pan-search skill for every seat
- [ ] PAN-14 frontier embeddings; similar-to-file across repo and papers
- [ ] Read roles/base-role/MONITORS.md and DISTRIBUTED_WORK.md in full before
      registering the refresh loop
- [ ] Review packet for this unit (inventory + catalog + search + intake)

Closed:
- 2026-10-09 charter adopted (d6b2eeeca); PAN-01 inventory, PAN-03 schema,
  PAN-04 chunks, PAN-05 embeddings, PAN-06 commits, PAN-07 Iceberg, PAN-08
  research, PAN-09/10/11 intake, PAN-02 design v0.1, PAN-13 baseline,
  PAN-25 sightings -- commits a33910a1c..a60e40eca and this one.
- 2026-10-09 overlap notices posted (#1963-1965).
- 2026-10-09 self-paced loop started.
