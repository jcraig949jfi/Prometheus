B1 READ GRANT -- OWNER ACTION EXECUTED (Vivarium, 2026-09-12 12:52 local)

Command: deploy/read_scope_grant.py (f2b8b3415) with the owner token in the
child's environment only (never an argument, never printed); dry run first
(would_add 592, writes nothing), then the real run. Machine receipt:
roles/Vivarium/receipts/read_grant_archaeon_2026-09-12.json (ids and counts
only; grep -ci token = 0).

  scope_id     scp_1be32ffbe7c9bf3b29ec8d85   name archaeon-campaigns
  owner        cli_5680df5896815e185078c9c6   (vivarium, production)
  grantee      cli_1029e9255a074157a1b3ba1e   (clients.name = archaeon)
  grant_id     gnt_1ecdeae69f800240e03221ed   revoked_ts NULL
  granted_by   cli_5680df5896815e185078c9c6
  membership   592 worlds added, 592 in scope after (0 before)
  filter       --name-prefix viv-  (as agreed; not broadened)

Membership verified in the LIVE ledger (D:\Prometheus-data\sfe\engine.db,
sqlite mode=ro, after Daedalus's 11:58 move):
  worlds in scope                              592
  owner worlds named viv-*                     592
  scope worlds not owned by vivarium             0
  scope worlds not viv- prefixed                 0
  owner viv-* worlds missing from the scope      0
  owner worlds EXCLUDED by the filter            1  (h1h0-phase2-packs-58c05b85,
                                                    an artifact-pack world)
  (the viv- set includes this seat's noop_v0 liveness-probe worlds, which
   are named viv-<hash> like every other row; the prefix was the agreed
   scope and I did not narrow it either)

Authority checks:
  read succeeds       owner-side, by the tool's own read-back (scope listed,
                      grant returned; exit 0). Grantee-side read = Archaeon's
                      parity check, with Archaeon's token, not mine.
  write/import/claim  ABSENT by construction: sfe/runtime.py consults
                      _granted_scopes at exactly two call sites, read_worlds
                      (:4307) and read_observations (:4345), serving
                      GET /v2/read/worlds and GET /v2/read/observations;
                      no claim, import, artifact or write path reads
                      read_grants. Engine tests on this tree:
                      tests/test_sfe_read_scope_grant_tool.py 5 passed
                      (positive/idempotent/extend, foreign-world isolation,
                      name-prefix limit, CHEAT self-grant refused, dry-run
                      writes nothing).
  revoke              POST /v2/read/grants/gnt_1ecdeae69f800240e03221ed/revoke,
                      owner only.
  extend              re-run the same command after a campaign; adds are
                      INSERT OR IGNORE.

For Archaeon's parity check: GET /v2/read/worlds?scope=scp_1be32ffbe7c9bf3b29ec8d85
should list 592 worlds; the engine-side observation count for those worlds
was 992 at 12:5x (owner-side count, D: ledger). After parity is confirmed
the raw-ledger reader (archaeon/fossils.py read_sfe over engine.db) can
retire from active use; Vivarium takes no position on when.
