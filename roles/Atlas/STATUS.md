# Atlas status

Currency: 2026-09-19 (charter + addendum adopted; first populated pass).

seat state: ACTIVE.
what it asserts: PRESENT (Atlas[m1-1c645957]), ACTIVE, PRODUCTIVE (schema
  atlas on M1 populated by 8 harvesters + the comb rules), VALID for the
  controls in atlas/tests (16 passed); classifications are Atlas's and
  labelled as such.
workspace: worktree atlas-base-role, branch atlas/charter-2026-09-19,
  base 74b09076d (origin/main when the charter arrived).
store: prometheus_fire (M1), schema atlas, migrations 001-004.
index (2026-09-19 pass): 11 engines registered (4 with experiments:
  sfe, archaeon.frontier, npe, vivarium), 48 campaigns, ~1,897
  experiments, ~1,592 attempts, 3,225 segments, ~12k source pointers,
  ~18k facts, ~1.3k edges, 217 defects, 189 open signals. Exact counts:
  roles/Atlas/reports/REPORT_2026-09-19.txt.
coverage: M1 only. M2-local evidence (frontier runs/, the M2 SFE ledger,
  M2 logs) is recorded as EXPECTED:M2, not as absent.
monitors owned or fed: none. No loop is scheduled; harvests run on
  command (ATLAS-21 registers one before any launch).
sibling seat: Atlas-M2 (m2-8f915f3d, M2), its own seat, assisting with
  the M2-resident part of the index on the operator's instructions
  (roles/Atlas/SIBLINGS.md).
blockers: none; the M2 layer arrives with the M2 instance.
ruled 2026-09-19: F:/SerendipityD is ignored for now (operator).
next executable action: ATLAS-05 (wse/ssf git adapter), ATLAS-06 (cmp1
  verdicts), ATLAS-18 (eligibility counts beside each rule).
