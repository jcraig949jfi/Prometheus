# Selection ancestry on the 2026-09-12 canary: ANCESTRY_COMPLETE, no schema change

Daedalus, 2026-09-12. Specimen: the operator-ordered canary, Vivarium row
`ececfe90-3e20-4dfe-b271-6a9d45d9abb2` (request_key rk-canary-2026-09-12-1),
returned fossil `ENC-archaeon-4f6625f91b2e304b`. Tool: `deploy/fossil_ancestry.py`.
Run record: `canary_ececfe90.json` (COMPLETE), `uniform_cs-c1fb2785.json`
(UNIFORM, a WROTE_RANDOM tick row as the control). Tests:
`tests/test_sfe_fossil_ancestry.py` (8: positive, uniform, five cheat
controls, identity-never-by-name-or-timestamp).

## The deterministic join, edge by edge (every key is a durable identifier)

    returned fossil   ew.fossil_encounters[ENC-archaeon-4f6625f91b2e304b]
        run_id                exp_8d968652a8a6b0c9885ec716:wrk_0741fa4c800b927bb1322dd0
        sfe_event_seq/hash    129400 / sha256:6100e020...   == SFE events[129400].entry_hash
        sfe_world_id          wld_13b3caf41573e37f015bf9ff
        producer.queue.experiment_id   ececfe90-3e20-4dfe-b271-6a9d45d9abb2
        resources_used.obs_id          obs_52ac5c2564a0deaf0d3ed303
    SFE               experiments[exp_8d968652]: world wld_13b3caf4, spec_hash
                      sha256:3caf3b11..., spec.pew.encounter_id == the fossil id;
                      observations[obs_52ac5c25] on that experiment, ENGINE_WORK_RESULT
    Vivarium row      viv.research_experiment_queue[ececfe90]: sfe_experiment_id ==
                      exp_8d968652; spec_hash == the SFE experiment's; candidate_set
                      cs-40a8239f45904b56; family fam-canary-2026-09-12; arm resample_best
    decision          the row's source_evidence: schema archaeon.canary.v0, mode human,
                      policy canary.region_directed_by_hand.v0, selection_rule "highest
                      metric; tie -> earliest created_ts", corpus_hash
                      corpus:9ff9b911920024b5f16349bb (1029 rows), chosen_region
                      wld_8e73e722b2b2d883d917b5c0, preregistration
                      archaeon/docs/h0h5/CANARY_PREREG_2026-09-12.json (commit 35a41ce62),
                      corpus table archaeon/docs/h0h5/_directable_landscapes_2026-09-12.json
    corpus table      git blob 4990c86b at 35a41ce62, 24 rows; the row with
                      region == chosen_region names the SOURCE FOSSIL:
                      obs_d57501bd03d010e1c7c12797 / exp_4a36b0ad58fbc0e1de90a6d5 /
                      ENC-archaeon-f84f653c25247083, metric 0.75. Re-applying the
                      preregistered rule to the 24 rows selects the same region.
    source fossil     ew.fossil_encounters[ENC-archaeon-f84f653c]: sfe_world_id ==
                      chosen_region; SFE observations[obs_d57501bd] sits in that world on
                      exp_4a36b0ad.
    preregistration   CANARY_PREREG_2026-09-12.json at 35a41ce62 (committed 15:56:20Z,
                      the row created 15:56:46Z) carries spec_hash sha256:3caf3b11..., the
                      SAME hash the engine sealed at commit -- the executed experiment is
                      the preregistered one, by hash, not by name.

So the statement "this returned fossil exists because this selection policy
consumed this earlier fossil evidence and chose this experiment" is
mechanically answerable today, from existing records, by one read-only join.

## What is NOT identity-bearing and is never consulted

World names (viv-<hash>), timestamps, and the seed_root value (the descendant
world shares seed_root 926994 with the source region -- a value coincidence
by design of the resample template, not a link). The SFE ledger alone holds NO
edge from the descendant world to the source region: `worlds.parent_world_id`
is null on both and `lineage_edges` is world-scoped. The edge lives in the
Vivarium row's source_evidence and in the committed preregistration, both
durable, and PEW's producer block carries the row id. That is sufficient and
it is not a gap; it is where the decision was made, so it is where the
decision is recorded.

## Residuals stated, not hidden

- The 1029-row corpus is identified by hash and not content-committed; the
  24-row subset the rule consumed IS committed with the source fossil ids.
  Recomputing the corpus hash needs Archaeon's chart + window over the
  append-only ledger; not attempted here (their lane).
- Encounter ids are NOT unique across queue rows (786 rows, 544 distinct:
  reissues reuse the spec's id). The join therefore keys on PEW's
  producer.queue.experiment_id (UUID) and run_id (exp:wrk), never on the
  encounter id alone; the encounter id is checked for equality on the SFE
  spec as a consistency assertion.
- The 592-world scope, Idempotency-Keys, and A6 are orthogonal to this
  join; none is required for it.

## Requirement on the F/C season's rows (a contract, not a schema)

The tool resolves COMPLETE only when a fossil-directed row's source_evidence
carries: chosen_region (an SFE world_id), the corpus table path AND its
commit (via the preregistration field "... (commit <sha>)"), and the table's
row for that region names obs / exp / pew of the source fossil. A tick row
that declares corpus rows 0 with a uniform policy resolves UNIFORM (no
ancestor by design). Anything else is a named GAP. Archaeon's canary schema
already satisfies this; the tick's fossil-directed template must carry the
same fields when it is admitted.
