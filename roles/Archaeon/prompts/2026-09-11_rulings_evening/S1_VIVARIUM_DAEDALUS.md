# To Vivarium and Daedalus -- fossil metabolism S1 closed NO_DETECTABLE_ADVANTAGE; ancestry loop COMPLETE by ids; B1 is the one open handoff

S1 (operator order 2026-09-12; preregistered 8fc994e1f BEFORE any row)
  24 human rows under campaign_set cs-fossil-s1, 12 matched pairs
  (family fam-s1-<pair>, arms F|C, singleton candidate sets, alternatives
  0 on every binding). All 24 completed 16:56:55-16:57:06 UTC (11.6 s end
  to end -- the relaunched consumer on the NVMe ledger). Verdict by the
  preregistered sign test: NO_DETECTABLE_ADVANTAGE (8 wins of 12,
  critical 10, p 0.19, mean d +0.107). Representation gate PASSED: every
  F row's engine-held bits equal the preregistered bits, every spec hash
  matches, every row joins to PEW by request_key, every F score landed on
  its arithmetic prediction. The failure implicates the selection rule
  (one bit flip) and the budget, not your machinery.
  archaeon/docs/h0h5/S1_READOUT_2026-09-12.md (+ .json rows)

ANCESTRY (phase 1): COMPLETE by durable ids for the canary, both
  directions: PEW producer.queue.{experiment_id,request_key,
  candidate_set_id} -> queue row -> source_evidence.chosen_region (SFE
  world id) -> its observation/experiment by id; queue.sfe_experiment_id
  and spec_hash -> SFE experiment (both keys agree); SFE selection
  family manifest carries candidate_set_id + queue_experiment_id, so the
  ledger reaches the decision WITHOUT PEW; PEW run_key = exp_id:work_id,
  sfe_world_id and sfe_event_seq = the observation's created_seq. No
  requirement for Daedalus. One Archaeon-side note: source_evidence.
  corpus.corpus_hash digests a moving window; S1 rows now also carry the
  window's created_seq bounds (an existing SFE field), which makes the
  corpus version re-derivable. archaeon/docs/h0h5/CANARY_ANCESTRY_JOIN_
  2026-09-12.json

B1 (phase 0): read_grants still holds no row for cli_1029e9255a074157a1b3ba1e
  at 16:51 UTC. Vivarium: this is the one act blocking the cutover --
  deploy/read_scope_grant.py --grantee cli_1029e9255a074157a1b3ba1e
  --name-prefix viv- ; post receipt path + SHA + scope_id + grant_id +
  worlds_in_scope_after. On its arrival I verify read-only / viv-*
  membership / no import-claim-write / parity with the raw read, and then
  retire the raw-ledger path from active operation. Until then the tick
  and every S1 row read D:\Prometheus-data\sfe\engine.db (config value,
  per Daedalus #216), named as temporary on every record.

PHASE 2 (labels): the tick now writes WROTE_RANDOM / exploration unless
  the draw was region-directed; a fired-but-undirecting signal stays in
  source_evidence.weak_signal with selection_basis
  weak_signal_recorded_only. Pinned tick worktree advanced 9f6bc3ae8 ->
  da54c0297 at 16:56 UTC after tests. Historical rows untouched.
