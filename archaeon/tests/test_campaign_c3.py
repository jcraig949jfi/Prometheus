"""C3 batch plan (Track B). Structure is testable before the wrapper lands;
validation against the kind is reported, not assumed."""
from __future__ import annotations

from archaeon.producer import campaign_c3 as C3


def test_centre_only_rules_read_only_the_centre_bit():
    # decode: bit k from the LEFT of the 32-hex string is neighbourhood k
    def out(rule_hex, k):
        n = int(rule_hex, 16)
        return (n >> (127 - k)) & 1
    for name, rh in C3.CENTRE_RULES.items():
        f0, f1 = int(name[-2]), int(name[-1])
        for k in range(128):
            assert out(rh, k) == (f1 if (k >> 3) & 1 else f0), (name, k)
    assert C3.CONSTANT_RULES["all_zero"] == "0" * 32 and C3.CONSTANT_RULES["all_one"] == "f" * 32


def test_plan_shape_pairing_and_arms():
    rows = C3.plan()
    arms = {}
    for r in rows:
        arms[r["arm_id"]] = arms.get(r["arm_id"], 0) + 1
    if C3.INCLUDE_NULL_ARM:
        assert arms == {"C3-hist": 6, "C3-base": 6, "C3-null": 18, "C3-acq": 120}
        assert len(rows) == 150
    else:
        assert arms == {"C3-hist": 6, "C3-base": 6, "C3-acq": 120}
        assert len(rows) == 132
    assert len({r["request_key"] for r in rows}) == len(rows)
    # one seed_root -> the same four IC samples for every rule (paired by construction)
    assert {r["spec"]["world"]["seed_root"] for r in rows} == {C3.SEED_ROOT}
    assert all(r["spec"]["repeat"]["count"] == 4 and r["spec"]["repeat"]["state"] == "reset" for r in rows)
    # transform has no executor default: every payload names it, and it equals the row's provenance
    assert all(r["spec"]["work"]["payload"]["transform"] == r["transform"] for r in rows)
    assert all(r["spec"]["work"]["payload"]["transform"] == "none" for r in rows if r["arm_id"] != "C3-null")
    assert all(r["spec"]["outcome_rule"]["aggregate"] == "all" for r in rows)
    if C3.INCLUDE_NULL_ARM:
        nulls = {(r["label"].split(":")[0], r["transform"]) for r in rows if r["arm_id"] == "C3-null"}
        assert nulls == {(g, t) for g in C3.HISTORICAL for t in C3.TRANSFORMS}
    # the six genomes come from Herakles's library, not a transcription here
    from herakles.evca import genomes as G
    for r in rows:
        if r["arm_id"] == "C3-hist":
            assert r["rule_hex"] == G.rule_hex(r["label"]) and len(r["rule_hex"]) == 32


def test_random_rules_are_seeded_and_distinct():
    rs = [C3.random_rule(i) for i in range(C3.N_RANDOM)]
    assert len(set(rs)) == C3.N_RANDOM and all(len(x) == 32 for x in rs)
    assert C3.random_rule(3) == C3.random_rule(3)


def test_check_reports_kind_registration_honestly():
    c = C3.check()
    assert c["rows"] == len(C3.plan()) and c["observations_planned"] == 4 * c["rows"]
    assert c["null_arm_included"] is C3.INCLUDE_NULL_ARM
    assert "IC sample" in c["independent_unit_for_accuracy"]
    if not c["kind_registered"]:
        assert c["blockers"] and c["blockers"][0]["lane"] == "vivarium"
        assert "ok_to_issue" not in c
    else:
        assert c["ok_to_issue"] is True, (c["invalid"][:3], c["executor_preflight"]["refused"])
        assert set(c["executor_preflight"]["ran"]) == set(c["arms"])       # every arm executed offline once


def test_ic_density_set_is_the_wrappers_list_form():
    # C3-1 failed on every row because this was a bare null (2026-09-10)
    assert C3.IC_DENSITIES == [None]
    assert all(r["spec"]["work"]["payload"]["ic_density_set"] == [None] for r in C3.plan())
