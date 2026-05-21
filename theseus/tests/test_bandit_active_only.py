"""Bandit must only ever pick generators whose status is ACTIVE.

Regression test for the 2026-05-20 OOM-then-stub-cascade failure.
On 2026-05-20T05:42-07:13 the YieldProportionalBandit started picking
all-stub generator sets after a 28M-record b3 batch crashed with
MemoryError. Each subsequent batch had requested=[5 stubs] and
active=[] for zero records emitted. The proximate cause was passing
`list(REGISTRY.keys())` to bandit.select, which exposed the 15 stub
generators as candidates. Fix wires the daemon to pass `list_active()`
instead. This test pins the contract.
"""
from __future__ import annotations

from theseus.bandit.epsilon_greedy import EpsilonGreedyBandit
from theseus.bandit.yield_proportional import YieldProportionalBandit
from theseus.generators.base import GeneratorStatus
from theseus.registry import REGISTRY, list_active


def _is_active(gid: str) -> bool:
    cls = REGISTRY[gid]
    return getattr(cls, "status", None) == GeneratorStatus.ACTIVE


def test_registry_list_active_filters_stubs():
    actives = list_active()
    assert len(actives) > 0
    for gid in actives:
        assert _is_active(gid), f"{gid} appears in list_active() but is not ACTIVE"
    # And every stub should be excluded.
    for gid, cls in REGISTRY.items():
        status = getattr(cls, "status", None)
        if status != GeneratorStatus.ACTIVE:
            assert gid not in actives, (
                f"{gid} status={status} leaked into list_active()"
            )


def test_yield_proportional_bandit_only_picks_actives_when_constrained():
    """Pinning the contract: callers must constrain `available` to actives.

    The fix lives at the call site (daemon.py passes list_active()), so
    this test exercises the bandit through that same constraint."""
    b = YieldProportionalBandit(seed=0)
    actives = list_active()
    chosen = b.select(available=actives, history={}, n=5)
    assert len(chosen) == 5
    for gid in chosen:
        assert _is_active(gid), f"bandit returned non-active generator: {gid}"


def test_epsilon_greedy_bandit_only_picks_actives_when_constrained():
    b = EpsilonGreedyBandit(epsilon=0.5, seed=0)
    actives = list_active()
    chosen = b.select(available=actives, history={}, n=5)
    assert len(chosen) == 5
    for gid in chosen:
        assert _is_active(gid), f"bandit returned non-active generator: {gid}"


def test_bandit_repeatedly_never_picks_stub_under_constraint():
    """Run 100 rounds with the actives-only constraint; never a stub."""
    b = YieldProportionalBandit(seed=42)
    actives = list_active()
    for _ in range(100):
        chosen = b.select(available=actives, history={}, n=5)
        for gid in chosen:
            assert _is_active(gid)
