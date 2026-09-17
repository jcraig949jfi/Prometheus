# Campaign 3 ingestion receipt (and campaigns 1-2) -- 2026-09-17

Author: Mnemosyne, instance m2-9c10ae00. Source commit for every row:
e98d2ee8c9e134b8c92187f65ec92e92eb8cfccf (origin/main at ingestion; the
campaign files are unchanged since cb9135104, Campaign 3 CLOSED). Reader
ew.campaign_ingest/1.1; contract v0.1. Machine-readable receipts:
derived/release/ingest_c{1,2,3}_run{1,2}.json (task worktree) and the
ew.ingestion_checkpoints rows (278 streams, producer 'archaeon').

## Campaign 3 (ING-20260917T065356-e98d2ee8; then repeats)

    run 1 (reader 1.0)   seen 20,288  new 20,288  conflicts 0   18.4 s
    run 2                seen 20,288  new 0       conflicts 0   17.9 s
    run 3 (reader 1.1)   seen 20,288  new 0       envelopes refreshed 20,288
    run 4                seen 20,288  new 0       refreshed 0
    rows by kind         reachability 1,265 (the SHARED table: all
                         campaigns + wse-survey-v01 + ssf-c1..c3, each row
                         stamped by its seed/producer), corridor 155,
                         ledger 41, attempt 29, design 32, receipt 45,
                         engine_record 1,212, artifact_ref 45, run 762,
                         generation 16,700, import 2
    identical copies     14,682 dropped before writing (the of-record
                         rows.json is a copy of attempts/aNN/rows.json)
    UNKNOWN identities   foundry_profile 45 (receipts), design_id 3,
                         engine_instance_id 21, rng_identity 199
    reconstructed        0
    T1 applied           every C3 receipt of record says campaign="cmp2";
                         ingested as cmp3 from campaign_seed 20260920 with
                         the disagreement noted on the row
    definition ids       reachability@09558e0c..., corridor@a8954c14...,
                         evolve@41be8126..., telemetry@80e90677... (git
                         blob shas at the source commit)

What Campaign 3 can now represent, checked by the release check and the
s18 queries (integration/campaign_release_results.json,
campaign3_queries_results.json):

    10 attempted slots         45 receipt rows (10 of record + attempts),
                               29 attempt rows, 32 design rows
    dispositions               the producer's disposition_candidate is in
                               each receipt's measured, as written; the
                               recorded disposition (RECORD.md prose) is
                               NOT ingested -- it is an adjudication
    engine identity            eng_906356f7fb1da180131f9290 on every
                               C2/C3 receipt; 1,212 engine records
                               (exp_id/obs_id) with attempt ids
    attempts / resumes         resumed_from on 9 attempts; replayed steps
                               29 (C3-SFE-09/a04) and 6 (C3-SFE-10/a04)
    reachability evidence      486 cmp3 rows; 321 censored before a
                               confirmed summit; horizons G 60..300
    zero-summit observations   pooled W2_K2 4-bit N200G60E16: 272 rows,
                               0 SUMMIT, 0 confirmed summits (all
                               campaigns); cmp3 at G300: censored 24/24
                               in C3-SFE-01
    corridor evidence          155 rows -> 25 corridor_edge v1 rows
    generation/run evidence    762 runs, 16,700 generation rows (rung, p,
                               best, mean, hold per generation)
    delay-general              C3-SFE-03/a05: 12 runs, 11 general on
                               trained delays; per seed general_gen and
                               rung_at_general on the row
    trained vs held-out        heldout_by_rung, general_heldout, per-ask
                               held-out on the rows
    unseen delays              C3-SFE-04: 7 runs at W1_d8, 7 at W1_d16
    retention schedule         C3-SFE-05 rows carry p and the schedule
                               series (generation rows)
    import dose / control      C3-SFE-10: 238 runs; quality mature 112 /
                               control 112 / none 14; intended dose ==
                               realized dose (n_imported) in every arm;
                               cap 0 / 0.05 / 0.25; import_share_final
    lineage/origin share       origin_shares / import_series in the
                               verbatim rows; per-generation for C2 traces
    basin strata               C3-SFE-06: table skelA/skelB x climber
                               first_improvement/population, 142 runs
    CA lesion evidence         C3-SFE-09 rows: site, min_lesion, margin,
                               permuted-reset controls, verbatim
    instrument failures        ledger rows 41 (7 BUG, 12 RECOVERY, ...)

## Campaign 2 (ING-20260917T065851-e98d2ee8)

    seen 6,506  new 5,086  repeat 0 new  (the shared tables were already
    in); receipts 38, attempts 26, designs 20, engine records 971,
    artifact refs 243, imports 13, runs 632, generations 3,094, ledger 49
    UNKNOWN: world_id 556 (rows.json rows carry none), foundry_profile 38,
    engine_instance_id 12, rng_identity 135, design_id 3, attempt_id 1
    notes: PHASE-A rows.json is not a list of run rows (skipped, said so)

## Campaign 1 (ING-20260917T065941-e98d2ee8)

    seen 2,682  new 1,262  repeat 0 new; receipts 14 (10 of record + 4
    attempt-1 files), engine records 7 (engine_records dict, older
    shape), artifact refs 91 (bare id strings), imports 5, runs 153,
    generations 960, ledger 32
    reconstructed: 1,230 rows -- attempt identity from the file pair
    (RECEIPT_attempt1.json present -> of record is a02), origin_kind says so
    UNKNOWN: design_id 14/14 receipts (no sealed prereg existed),
    engine_instance_id 102, foundry_profile 14, rng_identity 153, world_id 7
    Campaign 1 is the incomplete-identity acceptance test the order asked
    for: nothing was invented, everything absent is UNKNOWN or marked
    reconstructed.

## Store after ingestion

    campaign_observations 26,636 rows (cmp1 1,352; cmp2 5,629; cmp3 19,436;
    wse-survey-v01 126; ssf-c1 36; ssf-c2 39; ssf-c3 18), 53 MB; 278
    checkpoints; 0 conflicts; write_log carries one campaign.ingest row
    per run with the sha256 over the run's observation ids.
