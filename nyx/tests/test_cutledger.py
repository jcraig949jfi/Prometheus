"""The cut ledger falsifies itself: a defective ledger withholds metrics; verbosity without
revision is called FAILURE; a kind change is counted as material revision."""
from nyx.chop import cutledger


def _base():
    return {
        "specimen": "t",
        "cuts": ["CUT-1", "CUT-2"],
        "candidates": [
            {"id": "c1", "name": "a", "introduced_in": "CUT-1", "origin": "INHERITED",
             "source_boundary": "file X", "dispositions": {"CUT-1": "ORGAN", "CUT-2": "ORGAN"},
             "lineage": [], "unknown_fields": {"CUT-1": ["state"], "CUT-2": []},
             "record_bytes": {"CUT-1": 1000, "CUT-2": 1300}, "independent_test": "none",
             "independent_test_ref": "none", "ancestor_free_contract": "unknown", "consumer_returns": []},
            {"id": "c2", "name": "b", "introduced_in": "CUT-1", "origin": "DISCOVERED",
             "source_boundary": "none", "dispositions": {"CUT-1": "ORGAN", "CUT-2": "ORGAN"},
             "lineage": [], "unknown_fields": {"CUT-1": [], "CUT-2": []},
             "record_bytes": {"CUT-1": 1000, "CUT-2": 1300}, "independent_test": "none",
             "independent_test_ref": "none", "ancestor_free_contract": "unknown", "consumer_returns": []},
        ],
        "deliveries": [], "cheat_controls": [],
    }


def test_verbose_without_revision_is_failure():
    m = cutledger.metrics(_base())
    t = m["transitions"]["CUT-1 -> CUT-2"]
    assert t["materially_revised"] == 0
    assert t["VERBOSITY_FAILURE"] is True
    assert m["per_cut"]["CUT-1"]["inherited_boundary_rate_of_introduced"].startswith("1/2")
    assert m["final"]["unknown_became_known"] == 1


def test_kind_change_is_material_and_not_verbosity():
    l = _base()
    l["candidates"][0]["dispositions"]["CUT-2"] = "POLICY"
    l["candidates"][0]["lineage"] = [{"cut": "CUT-2", "relation": "DEMOTED", "from": ["c1"]}]
    t = cutledger.metrics(l)["transitions"]["CUT-1 -> CUT-2"]
    assert t["materially_revised"] == 1
    assert t["VERBOSITY_FAILURE"] is False
    assert t["survived_same_kind"].startswith("1/2")


def test_boundary_categories_cross_origin_with_support():
    l = _base()
    l["candidates"][0]["boundary_support"] = "FALSIFIED"; l["candidates"][0]["boundary_support_ref"] = "receipt.json"
    l["candidates"][1]["boundary_support"] = "SUPPORTED"; l["candidates"][1]["boundary_support_ref"] = "receipt.json"
    l["knife_application"] = {"K1": {"status": "FIRED", "evidence": "rate fell"}, "K7": {"status": "NOT_APPLICABLE", "evidence": ""}}
    assert cutledger.check(l) == []
    b = cutledger.metrics(l)["per_cut"]["CUT-2"]["boundary_categories_over_live"]
    assert b == {"inherited": 1, "independently_supported": 1, "inherited_and_supported": 0,
                 "inherited_and_falsified": 1, "not_inherited_and_supported": 1,
                 "not_inherited_and_falsified": 0, "untested": 0}


def test_support_and_knife_status_need_evidence():
    l = _base()
    l["candidates"][0]["boundary_support"] = "SUPPORTED"  # no ref
    l["knife_application"] = {"K3": {"status": "FIRED", "evidence": ""}, "K9": {"status": "MAYBE"}}
    d = cutledger.check(l)
    assert any("boundary_support SUPPORTED without a ref" in x for x in d)
    assert any("K3" in x and "without evidence" in x for x in d)
    assert any("K9" in x for x in d)


def test_recurrence_needs_ancestry_and_delivery_states_are_typed():
    l = _base()
    l["candidates"][0]["dispositions"]["CUT-2"] = "RECURRENCE"  # no recurrence_of
    l["deliveries"] = [{"seat": "Vivarium", "msg": 1, "posted": "2026-09-11T20:53Z", "cut": "CUT-1",
                        "first_substantive_return": "2026-09-11T21:23Z", "state": "REJECTED_BLOCKED"},  # no state_ref
                       {"seat": "Archaeon", "msg": 2, "posted": "2026-09-11T20:53Z", "cut": "CUT-1",
                        "first_substantive_return": None, "state": "METABOLIZED"}]  # not a state
    d = cutledger.check(l)
    assert any("RECURRENCE without recurrence_of" in x for x in d)
    assert any("msg 1" in x and "state_ref" in x for x in d)
    assert any("msg 2" in x and "not in" in x for x in d)
    l["candidates"][0]["recurrence_of"] = "organ.lean_simp.x.cut1"
    l["deliveries"][0]["state_ref"] = "msg 182"
    l["deliveries"][1]["state"] = "DELIVERED"
    assert cutledger.check(l) == []
    # a consumer that ran the organ and failed at the value-geometry boundary (ruling 2026-09-12)
    l["deliveries"].append({"seat": "Archaeon", "msg": 3, "posted": "2026-09-11T23:06Z", "cut": "CUT-2",
                            "first_substantive_return": "2026-09-12T03:42Z", "state": "INTERFACE_INSUFFICIENT",
                            "state_ref": "msg 200", "state_history": ["DELIVERED", "ATTEMPTED", "INTERFACE_INSUFFICIENT"]})
    assert cutledger.check(l) == []
    l["deliveries"][2]["state_history"].append("METABOLIZED")
    assert any("state_history" in x for x in cutledger.check(l))
    l["deliveries"][2]["state_history"].pop()
    by = cutledger.metrics(l)["consumers"]["deliveries_by_metabolic_state (ruling 2026-09-12; never collapsed to one bit)"]
    assert by["REJECTED_BLOCKED"] == 1 and by["DELIVERED"] == 1 and by["CONSUMED"] == 0


def test_defects_withhold_metrics():
    l = _base()
    l["candidates"][0]["independent_test"] = "run"  # no ref
    l["candidates"][1]["origin"] = "GUESSED"
    d = cutledger.check(l)
    assert any("assertion" in x for x in d)
    assert any("origin" in x for x in d)
