"""The catalogue falsifies itself: a name-restating mechanism is rejected; a query naming a bit is refused;
two bits with the same behavioural signature are reported as a recurrence; a behavioural query finds a
planted bit without its name; a nonsense query ranks nothing highly."""
import pytest

from nyx.catalog import schema, search


def _bit(i, **over):
    b = {"schema": schema.SCHEMA, "id": f"bit.test.{i}", "name": f"Widget{i}", "lineage": ["search"],
         "mechanism": "given a keyed archive and a candidate record, keep the candidate only if it is better under a total order on fitness",
         "scale": "PRIMITIVE", "sources": [{"ref": "test", "grade": "T3"}], "grade": "T3",
         "verb": "SELECT", "in_geometry": "MAP", "out_geometry": "MAP", "order_req": "TOTAL", "metric_req": "EQUALITY",
         "state_req": "GLOBAL", "control": "CALLBACK", "guarantee": "MONOTONE", "strategy": "GREEDY", "cost": "CONSTANT",
         "requires": ["a key per candidate"], "fails_when": ["ties under the order"], "instances": [], "related": []}
    b.update(over)
    return b


def test_validator_rejects_name_restated_and_empty_failure():
    b = _bit(1, mechanism="Widget1 does what Widget1 does and that is what it does here")
    codes = {c for c, _ in schema.validate(b)}
    assert "NAME_IN_MECHANISM" in codes
    b2 = _bit(2, fails_when=[])
    assert "NO_FAILURE" in {c for c, _ in schema.validate(b2)}
    assert schema.validate(_bit(3)) == []


def test_recurrence_is_by_signature_not_name():
    a = _bit(1, name="Alpha", lineage=["quality diversity"])
    b = _bit(2, name="Omega", lineage=["reinforcement learning"])
    c = _bit(3, name="Alpha", verb="ORDER")  # same name, different behaviour: NOT a recurrence
    rec = schema.recurrences([a, b, c])
    assert list(rec.values()) == [["bit.test.1", "bit.test.2"]]


def test_query_is_name_blind_and_finds_by_behaviour():
    bits = [_bit(1), _bit(2, verb="ORDER", in_geometry="SEQUENCE", out_geometry="SEQUENCE", guarantee="TERMINATES"),
            _bit(3, verb="COMPRESS", in_geometry="PROGRAM", out_geometry="PROGRAM", order_req="NONE", guarantee="APPROXIMATE")]
    with pytest.raises(ValueError):
        search.match({"name": "Widget1"}, bits)
    ranked = search.match({"verb": "SELECT", "in_geometry": "MAP", "order_req": "TOTAL"}, bits)
    assert ranked[0][1]["id"] == "bit.test.1" and ranked[0][0] == 1.0
    # partial credit: a SEQUENCE bit queried as STRING scores 0.5 on that axis, not 0
    ranked2 = search.match({"verb": "ORDER", "in_geometry": "STRING"}, bits)
    assert ranked2[0][1]["id"] == "bit.test.2" and abs(ranked2[0][0] - 0.75) < 1e-9
    # nonsense point: nothing scores above 0.5
    ranked3 = search.match({"verb": "SYNCHRONIZE", "in_geometry": "PROOF", "guarantee": "OPTIMAL"}, bits)
    assert ranked3[0][0] <= 0.5
