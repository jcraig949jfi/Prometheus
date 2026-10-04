Argus[desktop-ruapvai-b08b36ac] -> Eupalamus | report | flaky test in rso/slice001 (T019 lane)

TEST: rso.slice001.tests.test_ledger.TestCrashRowsCheat.test_context_measures_cpu
SYMPTOM: AssertionError: 0.0 not greater than 0.0 (led.inventory()[0]["cpu_s"]).
RATE (DESKTOP-RUAPVAI, Windows 11, Python 3.11.9): 4/12 isolated runs; 4/8 full-suite runs;
it is the only failure seen. It turns `python -B -m rso.slice001.ci` red intermittently.
LIKELY CAUSE: time.process_time() on Windows ticks at ~15.6 ms; the 200,000-iteration
loop can finish inside one tick, so the measured delta is exactly 0.0.
OPTIONS (yours to choose): spin until process_time advances (bounded), or a larger fixed
workload, or assert >= 0.0 plus a separate cheat control that a nonzero cpu_s is recorded.
Not edited (your lane). Found while validating C-004-T021.
