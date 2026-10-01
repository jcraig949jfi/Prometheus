"""Conformance: explib and its core tests run with every engine made unimportable.

A child interpreter installs an import blocker for torch and for every prometheus subpackage except
prometheus.explib (prometheus.ananke, prometheus.toolbox, prometheus.cosmos, ...), then runs the other core test
modules. Any engine import anywhere in explib, or in a core test, fails the child run. (W2-F
checks/core_isolation.py, promoted; the blocker now admits the prometheus package root, which explib needs as
its parent package.)"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

CHILD = r'''
import importlib.abc, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        top = name.split(".")
        if top[0] == "torch" or (top[0] == "prometheus" and len(top) > 1 and top[1] != "explib"):
            raise ImportError("BLOCKED import of %s (explib core must be engine-free)" % name)
        return None
sys.meta_path.insert(0, Block())
import prometheus.explib
for m in ("outcomes", "trace", "lockstep", "reach", "authority", "controls", "metamorphic", "attainable",
          "provenance", "stats", "toys"):
    __import__("prometheus.explib." + m)
import pytest
sys.exit(pytest.main(["-q", "-p", "no:cacheprovider", "--import-mode=importlib", *sys.argv[1:]]))
'''


def test_core_runs_with_engines_blocked():
    tests = [str(p) for p in sorted(HERE.glob("test_*.py")) if p.name != "test_core_isolation.py"]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="-1", PYTHONDONTWRITEBYTECODE="1")
    # the child must resolve prometheus.explib exactly as this process does (a staging overlay extends
    # prometheus.__path__; hand the same search path down)
    import prometheus
    env["PROMETHEUS_EXTRA_PATHS"] = os.pathsep.join(list(prometheus.__path__))
    boot = ("import os, sys\n"
            "paths = [p for p in os.environ.get('PROMETHEUS_EXTRA_PATHS', '').split(os.pathsep) if p]\n"
            "sys.path[:0] = [os.path.dirname(p) for p in paths]\n"
            "import prometheus\n"
            "for p in paths:\n"
            "    p not in prometheus.__path__ and prometheus.__path__.append(p)\n")
    r = subprocess.run([sys.executable, "-c", boot + CHILD, *tests], env=env, capture_output=True, text=True,
                       timeout=600)
    assert r.returncode == 0, r.stdout[-4000:] + r.stderr[-4000:]
