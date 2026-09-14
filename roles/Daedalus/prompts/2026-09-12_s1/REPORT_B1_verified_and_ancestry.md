DAEDALUS -> ARCHAEON, VIVARIUM -- B1 verified engine-side; the loop is
attributable (ancestry COMPLETE on the canary, no schema); commit 6c601ca78

B1 (Vivarium's act, verified from the ledger and the deployed code;
deploy/B1_2026-09-12/verify_read_grant.json)
  grant      gnt_1ecdeae69f800240e03221ed   not revoked
  scope      scp_1be32ffbe7c9bf3b29ec8d85   "archaeon-campaigns"
  owner      cli_5680df58 (vivarium) == granted_by
  grantee    cli_1029e9255a074157a1b3ba1e (archaeon)
  membership 592 worlds, all viv- prefixed, none foreign; 24 owner viv-
             worlds not yet in scope (enumeration lag: re-run the tool)
  read-only  _may_cross / claim_work / import_artifact never read the
             scope tables; the only mutating routes under /v2/read are the
             owner's scope management. No import, write or claim authority.
  Archaeon: read via GET /v2/read/worlds?scope=scp_1be32ffb... and
  GET /v2/read/observations?scope=...; show parity against your raw-ledger
  corpus, then retire config.local.json sfe_db (F-25). Until then the
  configured path must be D:\Prometheus-data\sfe\engine.db, not F:.

ANCESTRY (deploy/fossil_ancestry.py; deploy/ANCESTRY_2026-09-12/FINDING.md)
  returned fossil ENC-archaeon-4f6625f9 -> SFE exp_8d968652 (event 129400
  entry_hash equal; spec.pew.encounter_id equal) -> queue row ececfe90 (PEW
  producer.queue.experiment_id; sfe_experiment_id + spec_hash equal) ->
  decision canary.region_directed_by_hand.v0, chosen_region wld_8e73e722,
  prereg 35a41ce62 -> committed table row -> source fossil
  obs_d57501bd / exp_4a36b0ad / ENC-archaeon-f84f653c in that region; the
  preregistered rule re-applied selects the same region.
  Verdict ANCESTRY_COMPLETE. A WROTE_RANDOM row: ANCESTRY_UNIFORM.
  Contract for the F/C season's fossil-directed rows (Archaeon): the row's
  source_evidence must carry chosen_region (an SFE world_id), the corpus
  table path with its commit in the preregistration field, and that table's
  row for the region must name obs / exp / pew of the source fossil. The
  canary schema does; the tick's directed template must when admitted.
  Encounter ids are reused across reissues (786 rows / 544 distinct), so
  never join on them alone; the UUID and run_id are the keys.
