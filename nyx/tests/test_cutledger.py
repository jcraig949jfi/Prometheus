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


def test_defects_withhold_metrics():
    l = _base()
    l["candidates"][0]["independent_test"] = "run"  # no ref
    l["candidates"][1]["origin"] = "GUESSED"
    d = cutledger.check(l)
    assert any("assertion" in x for x in d)
    assert any("origin" in x for x in d)
