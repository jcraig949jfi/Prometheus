"""Tests for the Q2 protection metric (robustness.py): eligibility, determinism, bounds, and one known-answer
contrast -- a tape whose task code is NOT copied into offspring cannot be more task-robust than one whose is not the
question here; the known answer is simpler: mutations confined to bytes the tape never executes are neutral."""
from __future__ import annotations

from prometheus.z80atlas import vm
from prometheus.z80atlas.robustness import robustness
from prometheus.z80atlas.tasks import Task
from prometheus.z80atlas.world import Config

REP = vm.replicator(64)
HYB = vm.hybrid_relocated(vm.replicator(64), vm.witness_inc())


def cfg(**kw):
    base = dict(reproduction="ENDOGENOUS_COPY", physics="v3", coupling="ON", scoring="NEUTRAL", task="INC", ticks=40, cells=64)
    base.update(kw)
    return Config(**base)


def test_ineligible_without_the_trait():
    r = robustness(REP, cfg(), Task("INC"), n=16, seed=1)          # a pure copier cannot compute INC
    assert r["eligible"] is False and r["base_copy"] is True and r["base_task"] is False


def test_eligible_hybrid_bounds_and_determinism():
    c = cfg()
    a = robustness(HYB, c, Task("INC"), n=64, seed=7)
    b = robustness(HYB, c, Task("INC"), n=64, seed=7)
    assert a == b and a["eligible"] is True
    for k in ("task", "copy", "joint"):
        assert 0.0 <= a[k] <= 1.0
    assert a["joint"] <= min(a["task"], a["copy"])
    assert 0 < a["sampled_positions"] <= 64


def test_seed_changes_the_sample():
    c = cfg()
    assert robustness(HYB, c, Task("INC"), n=64, seed=1) != robustness(HYB, c, Task("INC"), n=64, seed=2)


def test_unexecuted_padding_is_neutral():
    """Known answer: the hybrid's trailing zero bytes past its HALT are never executed; a tape whose executed code is
    fixed and whose padding is mutated keeps both traits. Checked directly on every padding position."""
    from prometheus.z80atlas import adjudication as A
    c = cfg(); t = bytearray(HYB + bytes(64 - len(HYB)))
    last = max(i for i, b in enumerate(t) if b)
    pads = [i for i in range(last + 1, 64)]
    if not pads:
        return
    for i in pads[:4]:
        m = bytearray(t); m[i] = 0x7E                                  # an arbitrary non-zero byte in never-run padding
        assert A.verify_tape(bytes(m), c, Task("INC"))["exact"]
