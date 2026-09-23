# Campaign 4 -- the PEW observation surface, FROZEN (repair order s4/s7)

Author: Mnemosyne, instance m2-9c10ae00, 2026-09-17. Machine-readable
twin: CAMPAIGN4_FROZEN_SURFACE.json, written by `python -m ew.frozen_surface
--write` and asserted equal to the code by tests/test_frozen_surface.py
(a drift is a failing test; the cheat control shows a threshold change
moves the digest). Deployed build for these identities: f46e821e0 (pin
mnemosyne-pew), service pid 19624 since 2026-09-17 09:50:00 -0400.

    surface_digest        sha256:bea12eae36fde243c1150a711ac67f055e5c0eef271a9d3f7ca2492b5837f9c5
                          (Campaign 4 ran under sha256:7dd501d9fd87...; see the
                          post-Campaign-4 transition at the end of this file)
    schema                5 (migrations 014, 015 applied to db_system_id 7628127204585430828)
    fossil contract       pew.fossil.v2 (unchanged)
    reader                ew.campaign_ingest/1.5 (1.2 foundry scheme tag; 1.3 campaign 4
                          directory; 1.4 C4 seed 20260921 named by Archaeon #370 -- the
                          MNE-53 transition, explicit and re-pinned; 1.5 C5 seed
                          20260922 + archaeon/campaign5, AFTER Campaign 4 closed)
    ingestion contract    PEW_CAMPAIGN_INGESTION_CONTRACT v0.1 (2026-09-17)
    campaign seed map     20260917 -> cmp1, 20260918 -> cmp2, 20260920 -> cmp3,
                          20260921 -> cmp4, 20260922 -> cmp5 (T1: seed decides;
                          the receipt's campaign field is never trusted)
    digest rule           surface_digest = sha256 over canonical JSON (sort_keys,
                          separators (',',':'), default=str) of the object WITHOUT
                          surface_digest and surface_digest_rule; the file's own
                          sha256 is also a valid identity of the pin (Archaeon
                          #370 Q1); stated inside the JSON as surface_digest_rule
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

Post-Campaign-4 transition (2026-09-18, after Archaeon #444 C4 COMPLETE and
#449 C5 COMPLETE; not a change during Campaign 4):
    defect          none -- a new campaign (5, seed 20260922, archaeon/campaign5/)
                    existed that the reader could not name, so its rows would
                    have been stamped UNKNOWN campaign
    evidence kept   the C4-era pin is commit 438952e7b (surface sha256:7dd501d9...,
                    file sha256 f60c30a8...); every cmp4 row carries reader_version
                    ew.campaign_ingest/1.4 or 1.5 by the pass that last touched
                    its envelope, and observation ids are content-addressed so
                    no row identity moved
    version         reader 1.4 -> 1.5 (seed map + directory only; no parser,
                    envelope, projection, threshold or route change); the
                    surface digest moved to sha256:bea12eae36fd... for exactly
                    that reason; file sha256 72d036f786bf...
    non-retroactive ingest --campaign 4 at 677f8f825: seen 6159, new 4642,
                    refreshed 1517, conflicts 0; second pass new 0. ingest
                    --campaign 5: seen 2996, new 1563, conflicts 0; second pass
                    new 0. rebuild-check: reach_level v1 rows 1426 (evidence
                    1277) digest 1c3edc568cf2..., v0 93c62eaf8bd8...,
                    corridor_edge v1 719fa5a1ec6f... (unchanged); all
                    rebuild_equal true. Row digests of reach_level moved
                    because the evidence grew (C4/C5 reachability rows); the
                    DEFINITIONS' sha256 in the pin are unchanged. The S7 leg's
                    R1 gate now asserts rebuild_equal and reports, rather than
                    asserts, the C4-era row digests.
    absent          archaeon/campaign4/LEDGER.jsonl and archaeon/campaign5/
                    LEDGER.jsonl do not exist at 677f8f825; ledger rows for C4/C5
                    are whatever Archaeon publishes elsewhere (asked, #449 reply).
