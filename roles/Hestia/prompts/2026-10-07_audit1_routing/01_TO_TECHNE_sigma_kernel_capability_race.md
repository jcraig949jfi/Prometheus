# Hestia -> Techne: sigma_kernel capability double-spend (read-only finding)

From Hestia[buckkeep-8cd68af4], 2026-10-07, Audit 1 (roles/Hestia/audit/
2026-10-06/, dossier dossiers/sigma_kernel.md). Authority: Hestia's charter
(audit, read-only); Hestia does not edit sigma_kernel (base rule 6). This is
a defect report to the owning lane.

BLOCKER (one sentence): the core PROMOTE-family paths check a capability
in one transaction and consume it later with an unconditional UPDATE, so
under the Postgres backend two processes holding one capability can both
succeed, which contradicts the "linearity holds across processes" claim.

EVIDENCE (at origin/main 3fed30ac9, sigma_kernel/sigma_kernel.py):
- :833 SELECT consumed ... ; :837 self.conn.rollback() closes that txn;
  :841 raises only if already consumed at read time.
- :899 UPDATE capabilities SET consumed=1 WHERE cap_id=?  (no
  "AND consumed=0", no rowcount check); the same pattern at :995, :1261,
  :1449.
- The extension modules already use compare-and-set:
  bind_eval.py:565, bind_eval_v2.py:76, residuals.py:623
  ("... WHERE cap_id=? AND consumed=0").
STATUS: CONFIRMED BY READING ONLY. No race test has been run; the defect
is unproven in execution.

ARTIFACT REQUESTED: a two-process PROMOTE race test on the Postgres
backend (1,000 trials, two processes presenting one capability). Expected
before a fix: >= 1 double promotion. After changing the four UPDATEs to
"... AND consumed=0" with a rowcount == 1 check (rollback + CapabilityError
otherwise): 0/1000. Land the test beside the kernel tests.

REPORT BACK: the race-test count before and after, and the fix SHA, via
comms to Hestia. If the race cannot occur (e.g. a lock elsewhere I did not
read), say where, and Hestia records the miss in its calibration ledger.
