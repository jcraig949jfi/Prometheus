HARM-13 -- exchangeability class table per detector (EX EX-1.0.0)

IDENTITY (printed first)
  ledger      C:\Prometheus-data\sfe\engine.db
  instance    eng_906356f7fb1da180131f9290   schema 9
  chart       sfe.candidate_score.v0   lookback 2000   rows 0   corpus_hash corpus:e3b0c4429
  tenancy     {"admitted_client_names": ["vivarium"], "admitted_client_ids": 1, "excluded_attested_by_client_name": {"daedalus-livebar-1788565703": 1, "daedalus-livebar-1788571150": 1, "harmonia-arena": 2, "harmonia-arena-r2": 5, "harmonia-bisect": 1, "harmonia-diag-fossil": 1, "harmonia-integration": 1, "harmoni
  2026-09-10  NOT REACHABLE from M2 (M1 ledger eng_8a37a5d3 is an archive on SKULLPORT)

  det  eligible  mirror  EXCH  SUSP  VIOL  INDET  blocked_reason
  ---  --------  ------  ----  ----  ----  -----  --------------
  D1          0       0     0     0     0      0  chart 'sfe.candidate_score.v0' does not model player identity, so this
  D2          0       0     0     0     0      0  chart 'sfe.candidate_score.v0' does not model player identity, so this
  D4          0       0     0     0     0      0  chart 'sfe.candidate_score.v0' does not model player identity, so this
  D5          0       0     0     0     0      0  no configuration cell has d5_min_repeats=3 observations inside a famil
  D6          0       0     0     0     0      0  every coordinate axis is degenerate (zero span) in this corpus, so no 

eligible = the detector's own detect() count; mirror = grains this module produced (pairs: one record per side).
Every grain's row_ids and record are in the JSON beside this file; rows carry committed_seq for reproduction.
