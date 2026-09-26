"""C1b driver: fail-closed guard, eligibility suffixes, and the battery_row
code path exercised on HAND PLANTS only (CPU; no specimen genome)."""
from __future__ import annotations

import pytest

from prometheus.ananke import assays, c1b, c1b_run, envs, plants


def test_guard_refuses_without_a_release():
    with pytest.raises(SystemExit) as e:
        c1b_run.guard(None)
    assert "HOLD stands" in str(e.value)


def test_guard_refuses_a_message_that_is_not_a_release():
    with pytest.raises(SystemExit) as e:
        c1b_run.guard("684")          # Aporia's A3 ack: not a HOLD release
    assert "not a HOLD release" in str(e.value) or "cannot verify" in str(e.value)


def test_plan_covers_every_stage():
    p = c1b_run.plan()
    assert len(p["S1"]) == 3 and len(p["S2"]) == 12 and len(p["S3"]) == 12


def test_m2_suffixes():
    dl = dict(A=True, Z=True, B=True, C=True, I=False, K_S=False, K_Kp=False, K_w=False, K_En=False)
    assert c1b_run.label_m2(dl, []) == "DELAY_LINE_SPECIMEN"
    assert c1b_run.label_m2(dl, ["Z"]) == "DELAY_LINE_SPECIMEN_UNRESOLVED"
    fn = dict(dl, Z=False)
    assert c1b_run.label_m2(fn, ["Z"]) == "FLUSH_NONSPECIFIC"      # needs Z FALSE: unaffected
    mixed = dict(dl, B=False, K_w=True)
    assert c1b_run.label_m2(mixed, ["Z"]).endswith("_UNRESOLVED")


def test_m3_suffixes():
    t = dict(T=True, X=False, R=False, M=False)
    assert c1b_run.label_m3(t, ["T_c1_window"], True) == "TRANSPORT_ONLY_UNRESOLVED"
    r = dict(T=False, X=False, R=True, M=True)
    assert c1b_run.label_m3(r, ["T_c1_window"], True) == "SELF_MODIFYING_ONLY"
    none = dict(T=False, X=False, R=False, M=False)
    assert c1b_run.label_m3(none, ["not_R"], True) == "NOT_SUPPORTED_UNRESOLVED"


def test_battery_row_on_hand_plants():
    seeds = assays.world_seeds(c1b.DEV_NS + 2, 16)
    ph = plants.c1b_echo_physics()
    env = c1b.fixture_envs()["hold"]
    row = c1b_run.battery_row("M2", "echo_plant", ph, env, plants.echo_hold(ph)[None], seeds,
                              {}, "cpu")
    assert row["label"] == "DELAY_LINE_SPECIMEN", (row["label"], row["booleans"])
    assert not row["carryover"]["CARRYOVER"]
    ph = plants.c1b_rule_physics().replace(dest_mode="all")
    row = c1b_run.battery_row("M3", "rule_plant", ph, env, plants.rule_switch_hold(ph), seeds,
                              {}, "cpu")
    assert "RULE_SWITCH" in row["label"] or "SELF_MODIFYING" in row["label"], row["label"]
    assert row["booleans"]["_routing"] == "INERT_BY_PHYSICS" and "wording" in row
