"""Run the new suites from scratch_apply/ (the tree produced by `patch -p1 < promotion.diff`), recording wall and
process CPU seconds (all threads of this process; the core-isolation child is timed separately by its test).
usage: python dev/applied_run.py [pytest args]   (default: both new suites)"""
import os
import pathlib
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parents[1]
S = HERE / "scratch_apply"
sys.path.insert(0, str(S))
os.chdir(S)
import prometheus  # noqa: E402

assert pathlib.Path(prometheus.__file__).resolve().parent == S / "prometheus", prometheus.__file__
import pytest  # noqa: E402

args = sys.argv[1:] or ["prometheus/explib/tests", "prometheus/ananke/audit/tests"]
t0, c0 = time.time(), time.process_time()
rc = pytest.main(["-q", "-p", "no:cacheprovider", "--import-mode=importlib", "--durations=8", *args])
print(f"RC={int(rc)} wall_s={time.time() - t0:.1f} cpu_s={time.process_time() - c0:.1f}")
sys.exit(int(rc))
