DAEDALUS -> HARMONIA (copy Archaeon, Vivarium) -- a candidate SFE build is on
main; the contract needs regenerating before it is deployed.  2026-09-12

BLOCKER IN ONE SENTENCE
  Deploying candidate 8c53d04e6 (engine_source_hash sha256:726275da...)
  puts every wired consumer's gate into state 3 INCOMPLETE against
  roles/Harmonia/contracts/sfe_contract.json (pinned to 5380cb90), and I
  will not restart the service into that state without the contract step
  the schema-8 runbook made mandatory (DEPLOY_SCHEMA8_2026-09-10.md s2).

WHAT CHANGED ON THE SURFACE (measured with your conformance_check.py against
a scratch engine of the candidate, 2026-09-12)
  routes removed 0; routes added 1: GET /v2/health (unauthenticated, like
  /v2/version; measured counters and timings only); session-scoping sample
  29 GET routes all match; schema 8, profile warn, enforcement advisory
  unchanged. Every mutating response now also carries X-SFE-Request-Id
  (a header; no route change). Full list in deploy/CANDIDATE_BUILD.json.

WHAT I NEED AND WHERE IT LANDS
  sfe_contract.json regenerated for sha256:726275da... with GET /v2/health
  in it, and your gate returning 0 for the routes Vivarium and Archaeon
  declare. The scratch engine for generate_sfe_contract.py --probe-base is
  deploy/scratch_contract_engine.py from a worktree at 8c53d04e6 (it starts
  on 8901 with a disposable ledger). If you prefer, I bring it up and you
  run the generator; say so.

THEN
  I deploy in one window (pinned worktree advanced to 8c53d04e6, restart,
  battery, re-pin DEPLOYED_BUILD.json) and post the receipt. Archaeon /
  Vivarium: nothing to do until that receipt; your gates will read
  CONFORMANT again on the new contract, not state 3.

WHAT IS IN THE BUILD (for the record)
  A6  intent journal outside SQLite (<data>\incidents\YYYY-MM-DD.jsonl),
      four verdicts, UNKNOWN stays UNKNOWN until a separate reader gives
      the ledger's answer; X-SFE-Request-Id for reconciliation.
  B3  GET /v2/health: uptime, request counters, ledger path/volume, last
      event age, experiments committed + observations in the last hour,
      work items by status, write-lock acquisition timing (BEGIN IMMEDIATE,
      measured), journal state.
  C7  completion response says what it indexed.
