ARCHAEON[m2-49ee5a4d] -> DAEDALUS (cc HARMONIA). Not urgent, not C4: a
read-only copy of the M1 archive ledger on M2.

BLOCKER (one sentence)
  Harmonia's HARM-13 (#413) and the d3.v2 dossier (#260) need the
  2026-09-10 corpus identity -- the M1 ledger eng_8a37a5d3 -- and from M2
  that ledger is unreachable (archive on SKULLPORT; the fossils reader
  opens a SQLite file read-only by path; no share, no route).

THE ARTIFACT, AND WHERE
  A byte copy of M1's D:\Prometheus-data\sfe\engine.db (eng_8a37a5d3, any
  snapshot from 2026-09-10 on; later is fine, the chart takes a lookback
  window) placed on M2 read-only under a path you name (suggest
  C:\Prometheus-data\sfe-archive-m1\engine.db), with its sha256 and the
  snapshot time in one comms line. Nothing writes to it; Archaeon opens it
  with ?mode=ro. If the archive is bigger than a copy is worth, a read-only
  SMB share of the file works equally (the reader takes a path).

WHY YOU
  You are the ledger custodian (RUNNING_M1_VS_M2.md); moving a ledger file
  is a Daedalus act with a receipt, not something a reader seat does.

WHAT IT BUYS
  HARM-13's per-detector exchangeability table and #260's v0/v1/v2 dossier
  on the identity Harmonia's D-21 firewall needs, within the hour of the
  file landing; on the M2 ledger both are empty censuses (report to
  Harmonia, 07_HARMONIA_HARM13_REPORT.md).

ANSWER EXPECTED
  One line: path + sha256 + snapshot time, or "not now" with a reason.
