import os
import pathlib
import sys

sys.dont_write_bytecode = True
os.environ["RSO_COUNTERFEIT"] = r"F:\Prometheus-worktrees\dionysus-base-role\docs\phase3\review\FABLE-5.1\counterfeit"
SCR = pathlib.Path(r"C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify3")
HARNESS = SCR / "mirror" / "root" / "docs" / "phase3" / "hardening" / "FABLE-5.1" / "harness"
sys.path.insert(0, str(HARNESS))
from rso_harness import audits, claims, ladder, meta, registration, retain1, rulers, search, stats, torture  # noqa: E402
from rso_harness.verdict import ALL, BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result, combine  # noqa: E402
from rso_harness.stats import khash  # noqa: E402

CF = meta.COUNTERFEIT
