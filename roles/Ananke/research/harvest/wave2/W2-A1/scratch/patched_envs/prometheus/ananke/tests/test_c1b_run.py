"""C1b driver: fail-closed guard, eligibility suffixes, and the battery_row
code path exercised on HAND PLANTS only (CPU; no specimen genome)."""
from __future__ import annotations

import pytest

from prometheus.ananke import assays, c1b, c1b_run, envs, plants


def test_guard_refuses_without_a_release():
    with pytest.raises(SystemExit) as e:
        c1b_run.guard(None)
    assert "HOLD stands" in str(e.value)


@pytest.mark.parametrize("msg_id", ["605", "631", "684"])
def test_real_non_release_messages_are_refused(msg_id):
    """#696 NEGATIVE CONTROLS from REAL comms ids. #605 and #631 mention both
    HOLD and release in their subjects and passed the v1 substring guard."""
    commit, when = c1b_run.freeze_commit()
    m = c1b_run.fetch_message(msg_id)
    assert c1b_run.check_release(m, commit, when), msg_id
    with pytest.raises(SystemExit):
        c1b_run.guard(msg_id)


def _release(commit, when, **kw):
    import datetime
    m = {"id": 0, "sender": "Aporia", "kind": "ruling", "recipients": ["Ananke", "Cyclops"],
         "subject": "C1B HOLD RELEASE: reviews answered; C1b may run",
         "created_at": (when + datetime.timedelta(hours=1)).isoformat(),
         "body": f"Releasing the HOLD for C1b at freeze {commit[:9]}."}
    m.update(kw)
    return m


def test_synthetic_well_formed_release_passes():
    """#696 POSITIVE CONTROL: the guard can say yes."""
    commit, when = c1b_run.freeze_commit()
    assert c1b_run.check_release(_release(commit, when), commit, when) == []


@pytest.mark.parametrize("field,value", [
    ("sender", "Cyclops"), ("kind", "prompt"), ("recipients", ["Cyclops"]),
    ("subject", "Re: C1B HOLD RELEASE: not at the start"),
    ("subject", "c1b hold release: wrong case"),
    ("body", "Releasing the HOLD, no sha here."), ("body", "freeze 000000000 is wrong"),
])
def test_each_release_check_can_fail_on_its_own(field, value):
    commit, when = c1b_run.freeze_commit()
    assert c1b_run.check_release(_release(commit, when, **{field: value}), commit, when)


def test_release_before_the_freeze_is_refused():
    import datetime
    commit, when = c1b_run.freeze_commit()
    m = _release(commit, when, created_at=(when - datetime.timedelta(minutes=1)).isoformat())
    assert any("before the freeze" in x for x in c1b_run.check_release(m, commit, when))


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
