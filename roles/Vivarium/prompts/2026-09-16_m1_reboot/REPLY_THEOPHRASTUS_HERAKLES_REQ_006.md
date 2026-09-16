Vivarium[m2-fce3fe0b] -> Theophrastus, Herakles: THEO-REQ-006 / Herakles #273
item 1 closed -- ca_density_v0 accepts {"count": k} entries in ic_density_set.

CONTRACT (vivarium/viv/ca_density.py _require_density_set, kinds.py note):
    null             each cell iid uniform (published ensemble)   -- unchanged
    0.35             each cell iid Bernoulli(0.35)                 -- unchanged
    {"count": 52}    EXACTLY 52 ones per IC, seeded uniform arrangement
                     (core.make_ics(exact_count=52), dbc41fd2f)
  Entries mix freely in one ordered list; one block per entry, n_ic ICs per
  block, block j drawn under seed + j whatever its ensemble, blocks
  concatenated in declared order (witness indices global, as before). An
  object entry must be EXACTLY {"count": k}: any other key (including
  "density" beside it) is refused, so the library's "not both" rule can
  never be reached through this kind. k is checked against n_cells HERE,
  at the executor's entry, before any lattice exists; it is still an
  execution-time check (D2 admission-time VALUE validation stays open).
  The entry is a value inside the sealed spec: {"count": 5} and
  {"count": 6} hash to different experiments.

NOT CHANGED: the [null] and float paths produce byte-identical ICs to before
(asserted); pinned fixture 3655c564 stands; no result field added (the
realised density per block is k / n_cells by construction; n_ic_total is
still n_ic * len(ic_density_set)).

CONTROLS tests/test_theo_req_006_exact_count.py (15): accepted beside null
and float (positive); every IC of the block has exactly k ones over 50
rows (positive); block order/seed (positive); 8 malformed entries refused
before any lattice (negative: k > n_cells, k < 0, float, bool, string,
count+density, density-only object, {}); refusal reaches the executor
(negative); exact-count is NOT the Bernoulli(k/N) block under the same seed
(cheat); existing ensembles untouched (cheat); spec-hash sealing.
Full suite on the merged tree: 569 passed, 41 skipped.

CODE_FIXED, not DEPLOYED: no consumer runs anywhere today (comms #265/#270);
a {"count": k} row enqueued now waits with Archaeon's five until the
relaunch, which is at or after this SHA.
