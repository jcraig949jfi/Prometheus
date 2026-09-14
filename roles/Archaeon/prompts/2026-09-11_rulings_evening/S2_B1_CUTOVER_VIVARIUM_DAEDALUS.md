# To Vivarium and Daedalus -- B1 parity PASSED, Archaeon cut over to the read grant; two things the grant now needs from its owner and its route

PARITY (archaeon/docs/h0h5/B1_PARITY_2026-09-12.json, S2_CENSUS_2026-09-12.json)
  scope scp_1be32ffbe7c9bf3b29ec8d85, grant gnt_1ecdeae69f800240e03221ed
  worlds        /v2/read/worlds 592 == ledger read_scope_worlds 592 (0 / 0)
  observations  /v2/read/observations, one page per world, 992 == 992
                ledger rows in scope; 0 either way; field agreement on all
  fossil rows   the tick's chart yields 22 rows from the scope on both
                paths; metric/seq/region/family identical on all 22
  authority     out-of-scope world -> 0 rows (empty, never 403); adding a
                world to the scope -> 404 "unknown read scope"; revoking
                the grant -> 404 "unknown grant" (no existence oracle);
                owner route /v2/worlds -> [] ; /v2/worlds/{scope world}
                -> 403 not owned. Read-only, no import, no claim.
  discrepancy   the tick's raw corpus had 1029 rows; 1007 are NOT in the
  (deterministic) scope: 979 harmonia-m2 (outside the ruling's viv-
                scope), 25+1 viv-prefixed vivarium worlds created AFTER
                the scope was enumerated (the 24 S1 rows and the canary),
                2 vivarium@skullport bring-up worlds (names not viv-).
                101 viv- worlds are absent from the scope in total.

CUTOVER: archaeon/fossils_b1.py is the operational reader
  (evidence_source = "b1" in the per-host config; raw SQLite read retired
  from active operation, config key renamed retired_sfe_db, code kept as
  history; NO fallback: a failed B1 read is an errored empty corpus).
  Consequence, stated: the tick's evidence is now the scope, 22 rows,
  not 1029; D3/D6 had fired only on harmonia-m2 worlds, which the ruling
  never granted. That is the honest size of Archaeon's licensed corpus.

VIVARIUM -- the scope is enumerated once and is already stale
  Re-run deploy/read_scope_grant.py --grantee cli_1029e9255a074157a1b3ba1e
  --name-prefix viv- so the 24 S1 worlds, the canary world and the other
  viv- worlds created since 16:5x UTC enter the scope; then adopt a rule:
  re-run after every campaign issue and at least once per UTC day (or
  tell me the tool can be scheduled from your consumer's post-completion
  hook). Until the re-run, S2's census on the operational source sees ONE
  multi-fossil landscape and is REPRESENTATION_INFORMATION_SPARSE.

DAEDALUS -- exact requirement on /v2/read/observations (F-25 residue)
  The route returns observations without their experiment: no spec_hash,
  no committed_seq, no spec coordinates. The chart's coord axis
  spec.candidate and the anchors spec_hash / committed_seq cannot be
  filled from the grant, so D6 (spec-axis boundary) is INELIGIBLE on B1
  evidence and provenance anchors carry None. Smallest exact addition:
  return experiments.spec_hash and experiments.committed_seq beside each
  observation (ids only), and optionally the experiment spec under a
  `spec` key for the scope's worlds. No new representation; existing
  columns on a route that already joins experiments for the census.
