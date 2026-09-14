"""The retired donor adapters (TECHNE-51, 2026-09-12) still pass their battery, and the
registry gate keeps them retired.

The adapters for DisCoPy and cvc5 were retired for having no consumer, not for being
broken; a retired module that rots is a history nobody can reconstruct. So the
load-bearing checks of the Gen-0 battery run here against the verbatim modules under
techne/lib/donors/retired/, and three gate checks make sure retirement is a state the
registry enforces rather than a comment.
"""
from __future__ import annotations

import pytest

from techne.lib import donors as D
from techne.lib.donors.contract import RETIRED
from techne.tests import test_donor_adapters as battery

# Explicit import is the only way a retired adapter reaches the registry.
from techne.lib.donors.retired import cvc5_adapter, discopy_adapter  # noqa: F401

RETIRED_NAMES = sorted(RETIRED)


def _retired(name):
    try:
        return D.get(name, include_retired=True)
    except Exception as e:                                            # noqa: BLE001
        pytest.skip("retired adapter %s unavailable here: %r" % (name, e))


# -- the gate -----------------------------------------------------------------------------
def test_retired_names_are_both_registered_and_refused():
    for name in RETIRED_NAMES:
        assert name in D.registry, name
        with pytest.raises(KeyError, match="RETIRED"):
            D.get(name)


def test_available_excludes_retired_unless_asked():
    assert not set(RETIRED_NAMES) & set(D.available())
    assert set(RETIRED_NAMES) <= set(D.available(include_retired=True)) or any(
        _is_missing(n) for n in RETIRED_NAMES)


def _is_missing(name):
    try:
        D.get(name, include_retired=True).identity()
        return False
    except Exception:                                                 # noqa: BLE001
        return True


def test_live_battery_does_not_cover_retired_names():
    assert not set(RETIRED_NAMES) & set(battery.ADAPTERS)


# -- the preserved battery ------------------------------------------------------------------
@pytest.mark.parametrize("name", RETIRED_NAMES)
@pytest.mark.parametrize("check", [
    battery.test_t1_identity_reports_expected_upstream_and_version,
    battery.test_t2_effective_config_is_inspectable,
    battery.test_t3_same_input_config_seed_gives_identical_output,
    battery.test_t5_artifact_carries_donor_identity_and_config,
    battery.test_t7_unknown_config_key_raises,
    battery.test_t7b_unknown_capability_raises,
    battery.test_t8_selection_relation_is_explicitly_declared,
    battery.test_t9_no_prometheus_score_field_on_the_artifact,
    battery.test_t10_donor_failure_is_typed_not_an_empty_success,
], ids=lambda f: f.__name__.split("_")[1])
def test_retired_adapter_still_passes(name, check):
    # cvc5: T9 then T10 in one process is the pair that segfaulted at teardown before the
    # adapter's ordering discipline; running the battery here keeps that regression live.
    check(_retired(name))


@pytest.mark.parametrize("name", RETIRED_NAMES)
def test_t6_replay_of_a_retired_adapter_needs_the_archaeology_flag(name):
    """T6 for a retired adapter: the replay record still round-trips and reruns, but ONLY
    through include_retired=True. Replaying through the public route is refused -- that is
    the gate working on a ledger row, which is where a resurrection would otherwise happen."""
    import json
    adapter = _retired(name)
    cap, payload, cfg, seed = battery._fixture(name)
    first = adapter.propose(cap, payload, cfg, seed=seed)
    rec = json.loads(json.dumps(first.replay_seed()))
    assert rec["donor"] == name and rec["capability"] == cap
    with pytest.raises(KeyError, match="RETIRED"):
        D.get(rec["donor"])
    again = D.get(rec["donor"], include_retired=True).propose(rec["capability"], payload,
                                                             rec["config"], seed=rec["seed"])
    if {c.name: c.deterministic for c in adapter.capabilities()}.get(cap):
        assert again.output_digest == first.output_digest
