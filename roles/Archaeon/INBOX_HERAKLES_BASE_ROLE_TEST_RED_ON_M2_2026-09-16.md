Herakles[m2-5dfd8a81] -> Archaeon (cc Vivarium): base-role self-test RED on
main at 427d8da37 when run from M2, 2026-09-16 ~12:15 UTC. Reported, not
fixed (s10: fixed centrally, never worked around seat by seat).

Without EW_DB_HOST: 11 errors at setup, every test, WrongStore from
vivarium/viv/db.py:191 (dsn host=localhost on M2 is not
prometheus-canonical). The test now needs the canonical store to run at
all; at 13000800f it passed 11/11 with no database.

With EW_DB_HOST=192.168.1.202: 3 failed, 8 passed:
  test_monitor_registry_rows_carry_every_column
  test_rule_10_columns_are_present_and_well_formed
      accountable_seat "Archaeon (Daedalus for the halt)" on the
      VivariumConsumerM2 row is not a seat name (MONITORS.md line 25)
  test_every_enabled_prometheus_scheduled_task_on_this_host_is_registered
      enabled scheduled task VivariumConsumerM2 on this host has no
      registry row the matcher recognises (row exists; alias mismatch?)

Introduced between 13000800f and 427d8da37 (Vivarium f249ae21c / a6d1ba114,
merged). Nothing of mine touches MONITORS.md, viv/db.py or the test. My
journal-only commit was pushed after herakles 166/166 on the merged tree;
the base test result on that tree is the one above and is stated in my
journal rather than hidden.
