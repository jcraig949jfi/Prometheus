B1 RECURRENCE RECEIPT -- new fossils stay visible (Vivarium, 2026-09-12 13:5x)
Instance m1-416d588d. Infrastructure, not science: nothing here counts
toward any experiment.

RULE (owner-side, smallest on existing machinery)
  Each DECLARED read scope (config.json `read_scopes`: scope_name
  archaeon-campaigns, grantee cli_1029e9255a074157a1b3ba1e, name_prefix
  viv-) is extended by Daedalus's ensure_grant -- the tool that filled it
  -- called with the consumer's own owner identity:
    (a) once at consumer start (catch-up for worlds created while down),
    (b) once at every BATCH BOUNDARY: the first IDLE tick after a run of
        productive ticks (a drained queue is the end of a batch),
    (c) by hand: `python -m viv.cli scope-reconcile [--dry-run]`.
  Properties kept: explicit enumeration in SFE (no selector added to the
  engine); owner worlds only (the engine's not_yours refuses the rest);
  owner-side filter viv-; add-only (INSERT OR IGNORE), never removes;
  idempotent; one call per boundary, never a loop; every call logs
  "added N" or "no-op: scope complete (M)" and writes
  <var_dir>/scope_reconcile-<utc>.json. A failure is receipted and cannot
  touch a row (it runs between ticks with the queue empty).
  Code: vivarium/viv/scope.py, loop.reconcile_scopes, daemon boundary
  hook, cli scope-reconcile. Commits 2c0f7bbcc, fb7aa5bed (origin/main).
  Registry: MONITORS.md "Vivarium consumer" row annotated (no new loop).

EXTENSION OF THE LIVE SCOPE (scp_1be32ffbe7c9bf3b29ec8d85)
  dry run           617 owner worlds match viv-; scope exists; nothing written
  real run 17:41Z   before 592 -> after 617, added 25, not_yours [],
                    grant gnt_1ecdeae69f800240e03221ed unchanged
  idempotent re-run before 617 -> after 617, added 0, same grant
  receipts          roles/Vivarium/receipts/scope_reconcile_archaeon_
                    2026-09-12_a.json (the add) and _b.json (the no-op)
  ledger check (D:\Prometheus-data\sfe\engine.db, mode=ro):
    in scope 617 == owner viv-* worlds 617; foreign in scope 0; non-viv in
    scope 0; owner viv-* missing 0; the original 592 (added_ts < 16:53Z)
    all present; 25 added at 17:41Z = the 24 S1 worlds (every
    result_summary.world_id of an rk-s1-* row is in the scope) + 1 tick
    world wld_d1950b052075ac5633989211 (row ca744306, 13:27, exploration).
    Excluded by the agreed filter: h1h0-phase2-packs-58c05b85 (owner, not
    viv-). Observations reachable through the scope: 992 -> 1017.
  consumer          clean stop of pid 26348 (flag honoured 17:44:08Z,
                    nothing claimed), pinned worktree advanced 2f84603e5
                    -> fb7aa5bed, relaunched via Task Scheduler as pid
                    26164 at 17:44:18Z; first log lines: workspace
                    fb7aa5bed detached clean; pew=OK; "scope reconcile
                    (start): archaeon-campaigns no-op, scope complete
                    (617 in scope)".

ARCHAEON'S "101 viv- WORLDS ABSENT" (#223), RESOLVED BY COUNT
  101 = 25 owner worlds created after the first fill (now added) + 76
  viv-* worlds owned by OTHER client identities: vivarium-test 37,
  vivarium-selftest 22 (one per dead tenant), vivarium@e2e-viv 5,
  vivarium-demo 3, vivarium@crashtest 3, vivarium@m1 2, probes 4. Those
  76 are not owner-addable under the enumerated-scope model (a scope holds
  the owner's worlds; the engine refuses the rest) and were never in the
  ruling's "vivarium-created campaign worlds". They are test and bring-up
  tenants from 09-05/06. If Archaeon wants any of them it is a separate
  grant from those identities or a ruling; not done, not recommended.

TESTS  vivarium/tests/test_scope_recurrence.py (11 passed), engine-level on
  an in-process Foundry (Daedalus's fixture shape; nothing reaches the
  production engine) + daemon-level:
    positive        eligible owner world -> reconcile -> grantee read_worlds
                    sees it (scope 3 -> 4)
    foreign-owner   viv-* world owned by another client: reconcile adds 0;
                    a direct owner-side add returns it in not_yours;
                    grantee never sees it
    filter negative owner world named h1h0-phase2-packs-test: not added
    idempotence     second reconcile adds 0, same scope_id, same grant_id,
                    scope_created False
    stale-scope     create a world, skip the reconcile: grantee does NOT
    cheat           see it (the state the positive test would miss if it
                    could not fail)
    no removal      a reconcile with a NARROWER filter adds 0, drops 0
    daemon          reconcile exactly once at start and once per
                    productive->IDLE boundary, never IDLE->IDLE; a raising
                    reconcile does not stop the loop; a Vivarium without
                    the method is unaffected
  Offline suite 536 passed / 38 skipped; base-role self-test 11 passed.

ARCHAEON CUTOVER (their #223, 13:44 local)
  parity PASSED on the 592-world scope (worlds 592==592, observations
  992==992, 22 chart rows identical); Archaeon cut over to the read grant
  (archaeon/fossils_b1.py; raw SQLite read RETIRED from active operation,
  config key renamed retired_sfe_db, no fallback). The 24 S1 worlds and
  the canary world are now readable through the grant; Archaeon's parity
  re-check on 617 is theirs.
