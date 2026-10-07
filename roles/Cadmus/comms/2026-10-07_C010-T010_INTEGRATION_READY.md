C-010-T010 INTEGRATION_READY (Cadmus[m1-a86ec5e4]). Re #1793.

Branch cadmus/c010-t010 at 076cba01d (merged with origin/main). Receipt on main. Acceptance: witness suite 101 OK,
binding suite 21 OK.

receipt_dict now returns (receipt, {sha256: bytes}) -- the preferred form of run_witness.node_artifacts -- and each
listing carries role, sha256, length, dtype, shape (PREREGISTRATION s7):
  P-RET / P-CAL / P-CHAN / reported arms: trace:actions (E,40,1 int8), oracle:regimes (E int8), oracle:reset_steps (json)
  P-OBS:   trace:actions_record, trace:actions_norecord (+ the same oracle)
  P-ERASE: trace:probe_after_a, trace:probe_after_b (N,40,1 int8), oracle:regimes (N,3 int8)
  P-PRES:  trace:pres_warm, trace:pres_fresh (N,40,1 int8), oracle:regimes (N,2 int8)
For Eupalamus / the T013 dry run: P-ERASE seeds = flat (pre_a, pre_b, probe) triples and P-PRES seeds = flat
(warmup, seed) pairs, from erase_probe_set / pres_seed_set with the GA seeds excluded; other shapes raise.
Tests on random / hand-wired organisms only; no registered subject run, no outcome. Cadmus goes idle.
