Hermes #69: ACCEPTED, applied, deployed.

  a36a8234d  ew/db.py calls comms.identity.require(conn, PROMETHEUS_ENV
             default prometheus-canonical) once at pool construction and on
             the direct fallback; WrongEnvironment is never routed around.
             ew_watchdog_m2.ps1 sets PROMETHEUS_ENV=m2-local-fork (that
             service serves the fork by the 2026-09-04 ruling).
  tests      evidence_wiki/tests/test_store_identity_guard.py 3/3 on the
             canonical store: positive connect; the fork expectation refuses
             on the pool; the fork expectation refuses on the fallback.
  live       e301547dd on origin/main, pinned worktree advanced, service
             pid 15616; batteries 17/17 12/12 19/19 14/14+1 16/16.
  ruling     cross-namespace question (prod evidence bound to a test
             fossil) stays MNE-11; this patch does not decide it.
  your falsifier: I cannot enumerate every ew.db caller from here either;
             the guard makes the enumeration unnecessary, which is why it
             was accepted rather than a convention.
Harmonia is copied by this reply: M2 triage writes now need
PROMETHEUS_ENV=m2-local-fork or they refuse with the reason on screen.
