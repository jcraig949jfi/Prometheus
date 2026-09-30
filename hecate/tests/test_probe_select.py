from hecate.probe_select import choose, eligible, parse_cost
from hecate.tests.test_schema import _valid


def test_parse_cost():
    assert parse_cost("3 CPU core-minutes") == 3
    assert parse_cost("2-5 core-minutes") == 5          # a range counts as its top
    assert parse_cost("about 30 seconds") == 0.5
    assert parse_cost("1 hour") == 60
    assert parse_cost(7) == 7
    assert parse_cost("~2 core-minutes (about 30 s wall on 8 cores)") == 2
    assert parse_cost("0.5 CPU core-minutes for 5 seeds x 3 arms") == 0.5
    assert parse_cost("cheap") is None


def _world(i, cost, **kw):
    w = {"id": i, "triplicateId": "HT-0000000000", "passId": "P0",
         "hypothesis": "h", "mechanism": "m", "intervention": "i",
         "control": "c", "positive_control": "p", "observable": "o",
         "success_criterion": "mean X exceeds null twin by at least 0.2 over 5 seeds",
         "failure_criterion": "f", "alternative_explanation": "a",
         "null_twin": "n", "cost_estimate": cost,
         "stupid_explanations": ["a", "b", "c"]}
    w.update(kw)
    return w


def test_lowest_cost_eligible_wins_and_ties_break_by_id():
    p = _valid()
    p["experiments"] = [_world("W2", "3 core-minutes"), _world("W1", "3 core-minutes"),
                        _world("W3", "1 core-minute", success_criterion="it works")]
    w, rej = choose(p)
    assert w["id"] == "W1"                 # W3 is cheaper but E4-ineligible
    assert "W3" in rej


def test_each_eligibility_rule_fires():
    p = _valid()
    assert eligible(p, _world("W", "11 core-minutes"))[0]
    assert eligible(p, _world("W", "1", null_twin=""))[0]
    assert eligible(p, _world("W", "1", stupid_explanations=["a"]))[0]
    assert eligible(p, _world("W", "1", success_criterion="better than null"))[0]
    assert not eligible(p, _world("W", "1"))[0]
