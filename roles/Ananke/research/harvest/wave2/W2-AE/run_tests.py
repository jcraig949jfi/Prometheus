"""W2-AE staging harness: run tests with the promotion package OVERLAID on the repository's prometheus package.

The package tree pkg/prometheus/... adds new subpackages only (prometheus.explib, prometheus.ananke.audit). To run
it before it is applied, this harness appends pkg/prometheus to prometheus.__path__ and
pkg/prometheus/ananke to prometheus.ananke.__path__ (nothing in the repository is written), then runs pytest.

usage (from anywhere, CPU only):
  python run_tests.py core            # prometheus.explib tests (includes the engine-blocked child run)
  python run_tests.py audit           # prometheus.ananke.audit tests
  python run_tests.py existing        # the repository's prometheus/ananke/tests with the overlay active
  python run_tests.py toolbox         # the repository's prometheus/toolbox/tests with the overlay active
  python run_tests.py <pytest args>   # anything else is passed to pytest verbatim
"""
from __future__ import annotations

import os
import pathlib
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE / "pkg"
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO))

import prometheus  # noqa: E402
import prometheus.ananke  # noqa: E402

prometheus.__path__.append(str(PKG / "prometheus"))
prometheus.ananke.__path__.append(str(PKG / "prometheus" / "ananke"))
assert pathlib.Path(prometheus.__file__).resolve().parent == REPO / "prometheus"

import pytest  # noqa: E402

ALIASES = {
    "core": [str(PKG / "prometheus/explib/tests")],
    "audit": [str(PKG / "prometheus/ananke/audit/tests")],
    "existing": [str(REPO / "prometheus/ananke/tests")],
    "toolbox": [str(REPO / "prometheus/toolbox/tests")],
}
args = sys.argv[1:] or ["core"]
expanded = []
for a in args:
    expanded += ALIASES.get(a, [a])
sys.exit(pytest.main(["-p", "no:cacheprovider", "--import-mode=importlib", "-q", *expanded]))
