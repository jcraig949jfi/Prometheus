import os, sys, pathlib
os.environ.setdefault("RSO_COUNTERFEIT", r"F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\counterfeit")
sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "harness"))
from rso_harness import audits, claims, ladder, meta, registration, retain1, rulers, search, stats, torture  # noqa
from rso_harness.verdict import ALL, BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result, combine  # noqa
