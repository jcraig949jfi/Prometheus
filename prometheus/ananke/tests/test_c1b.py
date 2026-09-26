"""PTE-C1b labels and known-answer fixtures (PREREG_PTE_C1b s3-s5). CPU,
hand plants only."""
from __future__ import annotations

import pytest

from prometheus.ananke import c1b


def test_label_tables_are_total_and_single_valued():
    t = c1b.label_tables()
    assert len(t["m2"]) == 2 ** 9 and len(t["m3"]) == 2 ** 4
    for key, lab in t["m2"].items():
        assert lab.split(":")[0] in c1b.M2_LABELS, (key, lab)
    for key, lab in t["m3"].items():
        assert lab in c1b.M3_LABELS, (key, lab)


def test_every_non_failure_label_is_reachable():
    t = c1b.label_tables()
    m2 = {v.split(":")[0] for v in t["m2"].values()}
    m3 = set(t["m3"].values())
    assert m2 == set(c1b.M2_LABELS) - {"INSTRUMENT_FAILURE"}, set(c1b.M2_LABELS) - m2
    assert m3 == set(c1b.M3_LABELS) - {"INSTRUMENT_FAILURE"}, set(c1b.M3_LABELS) - m3


def test_fixture_failure_overrides_everything():
    b2 = dict.fromkeys(c1b.M2_KEYS, True)
    b3 = dict.fromkeys(c1b.M3_KEYS, True)
    assert c1b.m2_label(b2, fixtures_ok=False) == "INSTRUMENT_FAILURE"
    assert c1b.m3_label(b3, fixtures_ok=False) == "INSTRUMENT_FAILURE"


def test_flush_without_sham_is_never_a_delay_line():
    """Review #643.2: A and not Z goes to FLUSH_NONSPECIFIC whatever else holds."""
    for key, lab in c1b.label_tables()["m2"].items():
        b = dict(zip(c1b.M2_KEYS, (c == "1" for c in key)))
        if b["A"] and not b["Z"]:
            assert lab == "FLUSH_NONSPECIFIC", key


@pytest.fixture(scope="module")
def fixtures():
    return c1b.run_fixtures(device="cpu", M=32)


@pytest.mark.parametrize("name", ["F_latch", "F_echo", "F_sham_positive", "F_DA", "F_rule", "F_route"])
def test_known_answer_fixture(fixtures, name):
    assert fixtures[name]["pass"], fixtures[name]["checks"]


def test_carryover_census_runs_and_is_quiet_on_the_echo_plant():
    from prometheus.ananke import assays, plants
    ph = plants.c1b_echo_physics()
    env = c1b.fixture_envs()["hold"]
    r = c1b.evaluate(ph, plants.echo_hold(ph)[None], env, assays.world_seeds(c1b.DEV_NS, 16))
    co = c1b.carryover(r, env)
    assert co["mean_inflight_at_onset"] == 0.0 and not co["CARRYOVER"]
