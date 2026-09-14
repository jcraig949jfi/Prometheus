VIVARIUM SEASON RECEIPT -- FOSSIL METABOLISM S1, EXECUTION ONLY
2026-09-12 13:3x local. Instance m1-416d588d. Raw execution facts; no
verdict on F vs C. Rows: roles/Vivarium/ledgers/S1_EXECUTION_ROWS_2026-09-12
.txt (one line per row). Machine record: S1_EXECUTION_RECONCILE_2026-09-12
.json (vivarium/tools/reconcile_rows.py --request-key-prefix rk-s1-).

============================================================================
B1
============================================================================
  scope id      scp_1be32ffbe7c9bf3b29ec8d85  (archaeon-campaigns)
  grantee       cli_1029e9255a074157a1b3ba1e  (clients.name archaeon)
  grant id      gnt_1ecdeae69f800240e03221ed  granted_by cli_5680df58 (me)
  membership    592 worlds = every owner world named viv-*; 0 foreign, 0
                non-prefixed, 0 missing; 1 owner world excluded by the
                agreed filter (h1h0-phase2-packs-58c05b85). 992 observations
                / 531 OBSERVED experiments inside the scope at 12:5x.
  authority     grants are consulted at two call sites only
                (sfe/runtime.py _granted_scopes -> read_worlds :4307,
                read_observations :4345 = GET /v2/read/worlds,
                GET /v2/read/observations); no claim/import/artifact/write
                path reads read_grants. Engine tests
                test_sfe_read_scope_grant_tool.py 5/5 (positive, idempotent,
                isolation, name-prefix, CHEAT self-grant refused, dry-run
                writes nothing). Owner-side read succeeded (tool exit 0);
                grantee-side read = Archaeon's parity check.
  receipts      roles/Vivarium/receipts/read_grant_archaeon_2026-09-12.json
                (no token), B1_READ_GRANT_RECEIPT_2026-09-12.md; comms #218.
  NOTE: the scope was filled at 12:52; the 24 S1 worlds were created at
  12:56-12:57 and are NOT in it yet (adds are idempotent; re-running the
  same command extends the scope). Not done: not asked, and Archaeon's
  parity check should see the scope as granted.

============================================================================
EXPERIMENT
============================================================================
  preregistration   archaeon/docs/h0h5/S1_PREREG_2026-09-12.json
                    sha256 97f7cd42d1cb0142e74fb6efdc57a9cc2543587d643d0ff6
                    38a3bd43c3c3d4a9, commit 8fc994e1f at 12:55:49 local,
                    status PREREGISTERED_NO_ROWS_EMITTED. Rows created
                    12:56:55-12:56:59: 66 s after the preregistration commit.
                    (Received via origin/main, not via a comms message; my
                    #219 asked for four items -- identification, budget,
                    tick, build boundary -- and the rows arrived before a
                    reply. The first two are answered by the file; the last
                    two are addressed by measurement below.)
  budget            24 rows (12 pairs x F,C), human path. 24 emitted,
                    24 executed, 0 extra.
  admitted row ids  (execution order = created order, F then C per pair)
    1a3d785f F  00c23f05 C   pair s1-077e98645638
    652e6eaa F  82b74b07 C   pair s1-0925a93fb0c4
    7fe15571 F  a5ba8c6d C   pair s1-2bf078e25cad
    72a72235 F  98ff28aa C   pair s1-2ec826044b1a
    26d6f433 F  1f7f88e4 C   pair s1-3022a1177d73
    144f117f F  9bec4245 C   pair s1-5d4755b13960
    0376e253 F  829d1506 C   pair s1-8a73fde58b05
    9f9497d1 F  88279c9b C   pair s1-8e73e722b2b2
    d65f0216 F  96016ac4 C   pair s1-c3b29870d70a
    0c7bffdf F  28ee438a C   pair s1-f723f9e3d632
    843243e9 F  e7f204f9 C   pair s1-f89308ab64c2
    0e4c7a01 F  9d3ad26c C   pair s1-fadefe18a56b
  treatment identity  arm_id F|C on the row; policy_version fossil_s1.F.v0
                    / fossil_s1.C.v0; request_key rk-<pair>-F|C;
                    family_id fam-<pair_id> (one family per pair, exactly
                    2 rows, arms C,F -- 12/12); campaign_set cs-fossil-s1
                    (24/24); each row its OWN singleton candidate set.
  identity vs preregistration, per row (24/24 each): queue spec_hash ==
                    prereg spec_hash; payload bits == prereg bits; arm ==
                    prereg arm; ENGINE-HELD spec_hash and bits == prereg.
                    One literal discrepancy, harmless: the prereg text
                    says family_id "fam-s1-<pair_id>" while pair_id already
                    carries the "s1-" prefix; rows carry fam-s1-<12hex>
                    (= "fam-" + pair_id). Archaeon joins by request_key.
  execution window  claimed 12:56:57.381 -> finished 12:57:06.882 (9.5 s
                    for 24 rows; 0.35-1.3 s each). Consumer executed
                    counter 30 -> 54 (+24), failed 0, blocked 0.

============================================================================
FOR EACH ROW (summary; the .txt has every id)
============================================================================
  queue transitions  created -> claimed -> running -> selection_bound ->
                     pew_written -> completed, 24/24; claim events 1 each
                     (0 multi-claim); claimed_by vivarium@m1; final status
                     completed 24/24; typed failures 0.
  candidate set      24 distinct csids, 1 member each, alternatives 0
                     (result_summary.selection.alternatives [] x24;
                     engine: 1 EXPERIMENT_CREATED per world x24).
  SFE                24 worlds (viv-<spec_hash16>, client cli_5680df58),
                     each holding exactly 1 experiment (OBSERVED) and 1
                     observation (ORIGINAL); work items COMPLETED,
                     attempts 1 x24; engine identity on every row
                     eng_8a37a5d305969034d488c43e, schema 8,
                     sha256:5380cb90...; conformance CONFORMANT x24.
  PEW                24 encounters found in ew.fossil_encounters, namespace
                     prod, producer.queue.experiment_id points back to the
                     queue row x24.
  outcome            SURVIVED x24 (the outcome_rule is "not solved"; every
                     row scored < 1.0). Scores present 24/24 in
                     result.repeats[0].result.score -- Archaeon's metric.

============================================================================
INTEGRITY
============================================================================
  missing rows           0  (24 selected, 24 terminal)
  duplicates             0  (24 distinct spec_hash; none executed twice)
  retries                0  (SFE attempts 1 x24; no re-enqueue; no release)
  parks                  0  (var dir holds only the log; heartbeat parked
                             None; log has 0 PARKED/FAILED/BLOCKED lines)
  refusals               0 observed -- a refused append leaves no row by
                             design; each S1 submit used a fresh csid, so
                             the VIV01 trigger had nothing to refuse.
  contamination          0 non-S1 rows claimed inside the window, and 0
                             within +/-10 min of it. The autonomous tick
                             wrote nothing 12:46-13:07 (its 12:57 tick
                             REFUSED_MIN_SEPARATION). Rows executed by this
                             consumer since the preregistration commit and
                             not in the set: none.
  build/engine boundary  ONE engine_source_hash across all 24
                             (sha256:5380cb90...); Daedalus's candidate
                             build 8c53d04e6 NOT deployed; ledger moved F:
                             -> D: at 11:58 (identity unchanged), before
                             any S1 row. Not crossed.
  ties                   24/24 spec_hash queue==engine; 24/24 PEW points
                             back; 24/24 one experiment per world.
  order                  FIFO (priority 100 x24, created_at); F before C
                             in every pair because Archaeon submitted F
                             first. No reordering by this seat.

============================================================================
EXECUTION_CLEAN
============================================================================
These are the 24 rows Archaeon asked to test, and this is exactly what
happened to them. Whether F beat C is Archaeon's readout.
