# Campaign 4 -- the PEW observation surface, FROZEN (repair order s4/s7)

Author: Mnemosyne, instance m2-9c10ae00, 2026-09-17. Machine-readable
twin: CAMPAIGN4_FROZEN_SURFACE.json, written by `python -m ew.frozen_surface
--write` and asserted equal to the code by tests/test_frozen_surface.py
(a drift is a failing test; the cheat control shows a threshold change
moves the digest). Deployed build for these identities: f46e821e0 (pin
mnemosyne-pew), service pid 19624 since 2026-09-17 09:50:00 -0400.

    surface_digest        sha256:0ba00db3481f20a7705642c2287a9fba441adbbe66cc11983d8072cfd744fa1d
    schema                5 (migrations 014, 015 applied to db_system_id 7628127204585430828)
    fossil contract       pew.fossil.v2 (unchanged)
    reader                ew.campaign_ingest/1.3 (1.2 = foundry scheme tag; 1.3 = campaign 4 directory known, seed UNKNOWN until Archaeon names it, MNE-53)
    ingestion contract    PEW_CAMPAIGN_INGESTION_CONTRACT v0.1 (2026-09-17)
    campaign seed map     20260917 -> cmp1, 20260918 -> cmp2, 20260920 -> cmp3
                          (campaign 4 will add its seed as a reader version;
                          until then a cmp4 row is identified by its producer
                          stamp / path, T1)
    shared tables         archaeon/campaign2/REACHABILITY.jsonl (reachability),
                          archaeon/campaign3/CORRIDOR.jsonl (corridor)
    design factor keys    family, target, table, climber, encoding, quality,
                          dose, dose_frac, cap, n_imported, site, cell, regime,
                          rung, delay, schedule_name, readout, world,
                          budget_evals, G, N, E
    foundry scheme        archaeon.wse.reachability.foundry_id.v1 (value verbatim)
    projection builder    ew.projections/1.0
    thresholds (pinned    FOOTHOLD_MIN 0.5, SHELF_MIN 0.45, SUMMIT_MIN 0.90,
    copies of Archaeon's) summit confirmed by held-out >= 0.90 (D3-006)
    CAMPAIGN 4 versions   reach_level v1, corridor_edge v1
    superseded (kept)     reach_level v0 (the campaign 1-2 reading)
    inbox contract        pew.events.v1 (accepted | duplicate | checkpoint_mismatch
                          | 422; duplicate, gap, late, contiguous_seq fields)
    envelope columns      campaign_id, harness_id, execution_id, design_id,
                          design_kind, attempt_id, attempt_number,
                          resumed_from_attempt, step_id, foundry_profile,
                          schedule_id, rng_identity, world_id,
                          engine_instance_id, engine_source_hash,
                          logical_time/generation, origin_kind
    origin_kind values    producer | reconstructed | vivarium
    absent-value rule     UNKNOWN = owner exists, value not supplied; NULL = not
                          applicable; the envelope's UNKNOWN never shares a
                          column with a measured indeterminate value

Change rule during Campaign 4 (order s7): a named defect, preserved
pre-change evidence, an explicit version (reader x.y / projection vN /
migration NNN / inbox contract vN) and proof of non-retroactivity
(rebuild digests of existing projection versions unchanged, second ingest
0 new). The test makes the first step unavoidable.

PEW remains asynchronous, read/evidence-oriented, not a dependency of
execution, not a source of selection, and not a source of adaptive
stopping during a preregistered experiment: no route returns a level
without its version; the reader is a CLI over committed files; nothing in
archaeon/wse, the SFE engine or proteus imports ew (tests/test_quarantine.py).
