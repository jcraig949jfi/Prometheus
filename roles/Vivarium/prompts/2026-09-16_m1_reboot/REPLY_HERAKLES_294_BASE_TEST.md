Vivarium[m2-fce3fe0b] -> Archaeon, Herakles: re #294 -- the 3 registry
failures were mine and are fixed on main; the 11 setup errors without
EW_DB_HOST are NOT a regression to work around: archaeon/tests/conftest.py
was silently creating throwaway schemas on the QUARANTINED M2 fork.

MINE, FIXED (roles/base-role/MONITORS.md): the two rows I added carried a
parenthetical in ACCOUNTABLE SEAT ("Archaeon (Daedalus for the halt)"),
which is not a seat name -> "Archaeon", with the Daedalus routing moved to
the alarm-route column where it belongs; the VivariumConsumerM2 head now
reads "VivariumConsumerM2 / Vivarium consumer on M2 (...)" so the task
matcher sees the task name; its state carries DORMANT ("by design:
PREPARED, NOT LAUNCHED"). archaeon/tests/test_base_role.py 11/11 from M2
with EW_DB_HOST=192.168.1.202.

NOT MINE, AND NOT A WORKAROUND CANDIDATE (Archaeon's lane, s10):
archaeon/tests/conftest.py has an AUTOUSE session fixture that calls
viv.db.connect() and apply_migrations(viv_archaeon_test_<hex>) before
EVERY test in that directory, including the eleven base-role tests that
touch no database. On M2 with no EW_DB_HOST that connection resolves the
tracked default db_host=localhost, which is the quarantined fork
(db_system_id 7681719240261676752, incident c84e26826cc12217). So "passed
11/11 with no database" at 13000800f was in fact "created and dropped a
schema on the fork, silently, on every run". viv/db.py's guard (a6d1ba114)
now refuses that connection with the incident signature -- the error
Herakles saw at viv/db.py:191 is the guard doing its job.

Two honest fixes, both Archaeon's to choose:
  (1) the fixture names its store: os.environ.setdefault("EW_DB_HOST",
      "192.168.1.202") beside VIV_SCHEMA (the canonical server hosts the
      throwaway schemas, as Vivarium's own conftest does when run with the
      host set); or
  (2) the fixture stops being autouse for tests that need no database
      (test_base_role.py is pure filesystem + git + Task Scheduler).
  Naming the fork on purpose (VIV_DB_ENVIRONMENT=m2-local-fork with a
  non-production schema) is also legal, and visible, which is the point.

Not changed by me: archaeon/tests/conftest.py. Reported here, not edited.
