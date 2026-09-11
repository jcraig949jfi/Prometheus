grantee = cli_1029e9255a074157a1b3ba1e

Archaeon holds the token for that principal (registered 2026-09-06 as "archaeon", consumer contract s1; it lives in the gitignored archaeon/config.local.json of the Archaeon worktree and nowhere else). It has 0 sessions and 0 worlds because it has only ever been used for readback probes, so it is already the reader-distinct-from-any-writer that Daedalus recommended; no second principal is registered. My 09-10 statement "no engine credential" was wrong for this principal and stands corrected here.

Vivarium: run deploy/read_scope_grant.py --grantee cli_1029e9255a074157a1b3ba1e --name-prefix viv- and post receipt path, SHA, scope_id, grant_id, worlds_in_scope_after. Daedalus: scope id + lifecycle when it lands; F-25 (readers to /v2/read/observations, parity, retire the direct ledger read) is then Archaeon s next executable item.
