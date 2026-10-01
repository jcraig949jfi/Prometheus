"""Regression test for patches/causal_label_competence.SEMANTIC.diff: FAILS on current campaign.causal_label
(a dead / inverted adjudication run reads as NOT_SUPPORTED), PASSES on the scratch-patched copy."""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from pte_mut import env as _env  # noqa: E402,F401


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    m.__package__ = "prometheus.ananke"
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def _adj(normal, mem, zc=0.5, pa=0.5, perm=0.5):
    st = lambda a: {"status": "RAN", "acc": a}
    return {"result": {"controls": {"normal": {"acc": normal}, "memory_ablation": st(mem), "zero_comm": st(zc),
                                    "packet_ablation": st(pa), "env_permutation": {"acc": perm}}}}


CASES = [(_adj(0.0, 0.0), "HOLD"),      # invert_sign on echo (observed in the mutation score)
         (_adj(0.523, 0.5), "HOLD"),    # alter_timing on echo (observed: normal .523)
         (_adj(0.52, 0.5, 0.5, 0.5), "RELAY")]


def _check(mod):
    for adj, fam in CASES:
        assert mod.causal_label(adj, fam) == "INVALID_NORMAL", (adj, fam, mod.causal_label(adj, fam))
    # unchanged where the specimen is competent
    assert mod.causal_label(_adj(1.0, 0.5), "HOLD") == "CAUSAL_SUPPORT"
    assert mod.causal_label(_adj(1.0, 1.0), "HOLD") == "NOT_SUPPORTED"


@pytest.mark.xfail(strict=True, reason="current code has no competence precondition (the finding)")
def test_current_code_fails():
    from prometheus.ananke import campaign
    _check(campaign)


def test_patched_copy_passes():
    _check(_load(HERE.parent / "scratch/campaign_patched.py", "prometheus.ananke.campaign_patched"))
