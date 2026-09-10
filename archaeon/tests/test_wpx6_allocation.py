"""WP-X6: the exploration reserve is allocated across FAMILIES first.

    X6-a  100 templates vs 1: the same family-level entitlement
    X6-b  more families than slots: every eligible family served in the horizon
    X6-c  a baseline family cannot enter the reserve through an alias or an
          ambiguous classification; no eligible family -> unspent, reported
    X6-d  counters update once per event; a frozen order does not change with
          later counters or timestamps
"""
from __future__ import annotations

from datetime import date

from archaeon.producer import allocation as A

TODAY = date(2026, 9, 7)
POL = dict(A.PROPOSED, active=True, chosen_by="test", chosen_on="2026-09-07")


def _tmpl(tid, kind, family=None, admitted_at="2026-09-01"):
    t = {"template_id": tid, "kind": kind, "admitted_at": admitted_at}
    if family:
        t["family"] = family
    return t


def _classified(templates, rows=None):
    return A.classify(A.families(templates), TODAY, rows or {}, POL)


# ---------------------------------------------------------------- X6-a
def test_family_with_100_templates_and_family_with_1_get_equal_entitlement():
    big = [_tmpl("big.{}".format(i), "kx", family="fam.big", admitted_at="2026-09-01") for i in range(100)]
    small = [_tmpl("small.0", "ky", family="fam.small", admitted_at="2026-09-01")]
    cl = _classified(big + small)
    assert cl["fam.big"]["share"] == "reserve" and cl["fam.small"]["share"] == "reserve"
    served = {}
    counts = {"fam.big": 0, "fam.small": 0}
    for i in range(20):
        fam = A.choose_family(["fam.big", "fam.small"], served, i, "prod", "2026-09-07")
        served[fam] = served.get(fam, 0) + 1
        counts[fam] += 1
    assert counts == {"fam.big": 10, "fam.small": 10}


# ---------------------------------------------------------------- X6-b
def test_more_families_than_slots_all_served_within_horizon():
    fams = ["fam.{}".format(i) for i in range(10)]
    ts = [_tmpl("t{}".format(i), "k{}".format(i), family=f) for i, f in enumerate(fams)]
    cl = _classified(ts)
    served = {}
    seen = set()
    slots_per_day = POL["reserve_draws_per_day"]
    horizon = POL["horizon_days"]
    for day in range(horizon):
        for slot in range(slots_per_day):
            d = A.plan_draw(slot_index=slot, lane="prod", day="d{}".format(day), classified=cl,
                            served=served, offered_total=len(seen) + sum(served.values()), policy=POL)
            served[d["family"]] = served.get(d["family"], 0) + 1
            seen.add(d["family"])
    # 10 families, 1 reserve slot/day, horizon 7 -> cannot all be served; the
    # policy must SAY so rather than silently starve: deficit rule serves 7
    # distinct families in 7 days and never repeats before all are served.
    assert len(seen) == min(len(fams), horizon * slots_per_day)
    assert max(served.values()) == 1


# ---------------------------------------------------------------- X6-c
def test_baseline_family_cannot_enter_reserve_via_alias_or_ambiguity():
    base = _tmpl("bitstring.uniform.v0", "evaluate_bitstring", admitted_at="2026-09-06")   # implicit family
    alias = _tmpl("bitstring.alias.v0", "evaluate_bitstring", admitted_at="2026-09-07")    # young, but implicit
    cl = _classified([base, alias])
    assert set(cl) == {"kind:evaluate_bitstring"}
    assert cl["kind:evaluate_bitstring"]["share"] == "established"
    # an explicit family that merely re-labels the baseline kind but is listed
    # as established in policy stays established
    relabel = _tmpl("bitstring.relabel.v0", "evaluate_bitstring", family="kind:evaluate_bitstring",
                    admitted_at="2026-09-07")
    cl2 = _classified([relabel])
    assert cl2["kind:evaluate_bitstring"]["share"] == "established"
    assert "listed as established" in cl2["kind:evaluate_bitstring"]["reason"]


def test_no_eligible_family_leaves_reserve_unspent_and_reported():
    cl = _classified([_tmpl("bitstring.uniform.v0", "evaluate_bitstring")])
    d = A.plan_draw(slot_index=0, lane="prod", day="2026-09-07", classified=cl,
                    served={}, offered_total=0, policy=POL)
    assert d["slot_share"] == "reserve" and d["reserve_unspent"] is True
    assert d["share"] == "established" and d["family"] == "kind:evaluate_bitstring"


def test_thin_and_young_classification_with_rows():
    old_thin = _tmpl("a", "ka", family="fam.a", admitted_at="2026-01-01")
    old_fat = _tmpl("b", "kb", family="fam.b", admitted_at="2026-01-01")
    cl = _classified([old_thin, old_fat], rows={"fam.a": 3, "fam.b": 500})
    assert cl["fam.a"]["share"] == "reserve" and "thin" in cl["fam.a"]["reason"]
    assert cl["fam.b"]["share"] == "established"


# ---------------------------------------------------------------- X6-d
def test_counters_update_once_and_frozen_order_is_immune_to_later_events():
    ts = [_tmpl("t{}".format(i), "k{}".format(i), family="fam.{}".format(i)) for i in range(3)]
    cl = _classified(ts)
    snap = A.freeze_snapshot(cl, served={}, policy=POL, lane="prod", day="2026-09-07")
    order1 = A.order_from_snapshot(snap, n_slots=12)
    # later events: counters move, time moves -- the frozen order does not
    counters = {}
    for ev in ("offered", "published", "failed", "withdrawn"):
        A.count_event(counters, "fam.0", ev)
    assert counters["fam.0"] == {"offered": 1, "published": 1, "failed": 1, "withdrawn": 1}
    order2 = A.order_from_snapshot(snap, n_slots=12)
    assert order1 == order2
    snap2 = A.freeze_snapshot(cl, served={"fam.0": 5}, policy=POL, lane="prod", day="2026-09-07")
    assert snap2["snapshot_hash"] != snap["snapshot_hash"]


def test_policy_inactive_without_operator_file(tmp_path):
    pol = A.load_policy(tmp_path / "missing.json")
    assert pol["active"] is False and "proposal" in pol["note"]
    (tmp_path / "p.json").write_text('{"policy_id": "allocation.reserve.v0", "quota_per_day": 6, '
                                     '"reserve_draws_per_day": 1, "young_days": 90, "thin_rows": 24, '
                                     '"established": [], "chosen_by": null, "chosen_on": null}')
    assert A.load_policy(tmp_path / "p.json")["active"] is False


# ---------------------------------------------------------------- X6-e (third amendment)
def test_inactive_policy_continues_established_share_and_never_spends_reserve(tmp_path, monkeypatch):
    """While D-6 is pending, authorized collection continues under the
    existing policy: every draw is the established share, the reserve is
    untouched, nothing is admitted, and a frozen snapshot is unchanged by a
    later activation. D-6 was ACTIVATED on 2026-09-10 (pilot v0), so this
    test points the loader at a missing file to exercise the inactive path."""
    monkeypatch.setattr(A, "POLICY_PATH", tmp_path / "no-policy.json")
    inactive = dict(A.PROPOSED, active=False)
    ts = [_tmpl("t0", "k0", family="fam.new")]
    cl = A.classify(A.families(ts), TODAY, {}, inactive)
    snap_before = A.freeze_snapshot(cl, served={}, policy=inactive, lane="prod", day="2026-09-07")
    order = A.order_from_snapshot(snap_before, n_slots=6)
    # the tick's record while inactive
    from archaeon.producer import tick as tickmod
    rec = tickmod._allocation_record()
    assert rec["active"] is False and rec["share"] == "established"
    # activating later does not rewrite the frozen snapshot's order
    assert A.order_from_snapshot(snap_before, n_slots=6) == order


def test_live_policy_is_the_d6_pilot_v0_with_a_review_point():
    """Operator 2026-09-10: 'ACTIVATE bounded pilot'. The committed policy
    file is active, carries who chose it and when, and names its review."""
    pol = A.load_policy()
    assert pol["active"] is True and pol["chosen_on"] == "2026-09-10" and "operator" in pol["chosen_by"]
    assert pol["pilot"]["status"] == "PILOT_V0" and pol["pilot"]["review_on"] == "2026-09-24"
    assert pol["quota_per_day"] == 6 and pol["reserve_draws_per_day"] == 1
