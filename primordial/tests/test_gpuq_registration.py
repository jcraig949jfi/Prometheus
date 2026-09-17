"""F-R7-1 contract for the GPU arbiter: nv.gpuq serve registers lane 'gpu' with tag == its consumer name, refreshes the
registration while serving, and unregisters on exit (also when a job raises)."""
from __future__ import annotations

import sys
import types

import pytest

from primordial.nv import gpuq


class _R:
    def __init__(self, msgs=()):
        self.msgs = list(msgs)
        self.acked = []

    def xgroup_create(self, *a, **k):
        return True

    def xreadgroup(self, group, consumer, streams, count=1, block=0):
        self.consumer = consumer
        return [(gpuq.QUEUE, [self.msgs.pop(0)])] if self.msgs else []

    def xack(self, q, g, mid):
        self.acked.append(mid)


@pytest.fixture
def fake_residue(monkeypatch):
    calls = []
    mod = types.ModuleType("primordial.ops.residue")
    mod.GPU_LANE = "gpu"
    mod.register = lambda r, lane, repo, round_id=None, pid=None, tag=None: calls.append(("register", lane, tag)) or "k1"
    mod.refresh = lambda r, key: calls.append(("refresh", key))
    mod.unregister = lambda r, key: calls.append(("unregister", key))
    monkeypatch.setitem(sys.modules, "primordial.ops.residue", mod)
    import primordial.ops as ops
    monkeypatch.setattr(ops, "residue", mod, raising=False)
    return calls


def test_arbiter_registers_refreshes_and_unregisters(fake_residue, monkeypatch):
    monkeypatch.setenv("PM_TAG", "m1-testtag")
    r = _R()
    arb = gpuq.Arbiter(r, lane="E")
    assert arb.serve(max_jobs=None, block_ms=1, idle_exit_s=0.0) == []
    kinds = [c[0] for c in fake_residue]
    assert fake_residue[0] == ("register", "gpu", "m1-testtag") and r.consumer == "m1-testtag"
    assert "refresh" in kinds and kinds[-1] == "unregister"


def test_arbiter_unregisters_when_a_job_raises(fake_residue, monkeypatch):
    monkeypatch.setenv("PM_TAG", "m1-testtag")
    r = _R([("1-0", {"job_id": "j"})])
    arb = gpuq.Arbiter(r, lane="E")
    monkeypatch.setattr(arb, "run_job", lambda job: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        arb.serve(max_jobs=1, block_ms=1)
    assert [c[0] for c in fake_residue][-1] == "unregister"
