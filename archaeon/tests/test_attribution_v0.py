"""Attribution v0: schema validator, TH-014 known-answer fixture, adversarial reproduction boundary, structures, regression suite,
saturated-ruler guard."""
import json

import pytest

from archaeon.attribution import schema as S, classify as K, fixtures as F, regression as R, guards as GD


# ---------------------------------------------------------------- TH-014: same bytes, different history, different attribution
def test_th014_children_identical_but_classes_distinct():
    assert len(set(F.TH014_CHILD_BYTES.values())) == 1
    classes = {k: K.production_class(r) for k, r in F.TH014_LEAK.items()}
    assert classes == {k: k for k in F.TH014_LEAK}                     # each fixture's known answer is its key
    assert len(set(classes.values())) == 6


@pytest.mark.parametrize("k", sorted(F.TH014_LEAK))
def test_th014_fixtures_valid(k):
    assert S.check(F.TH014_LEAK[k]) == []


@pytest.mark.parametrize("k", sorted(F.th014_leaky_variants()))
def test_th014_leaky_variants_rejected(k):
    v = S.check(F.th014_leaky_variants()[k])
    assert v and all(x.split()[0] in ("A2", "A9") for x in v)


def test_th014_self_label_only_on_self_construction():
    ok = []
    for k, r in F.TH014_LEAK.items():
        r2 = json.loads(json.dumps(r)); r2["aggregation"] = [{"label": "SELF_COPY", "rule": "native_flag", "convention": False}]
        if not S.check(r2): ok.append(k)
    assert ok == ["SELF_CONSTRUCTED"]


# ---------------------------------------------------------------- reproduction boundary
def test_adversarial_records_valid():
    for k, c in F.ADVERSARIAL.items(): assert S.check(c["record"]) == [], k


def _score(fn):
    return {k: fn(c["record"]) == c["intended"]["reproduction"] for k, c in F.ADVERSARIAL.items()}


def test_only_machinery_ibd_matches_every_intended_verdict():
    perfect = [n for n, fn in K.DEFINITIONS.items() if n != "D6_HEREDITARY" and all(_score(fn).values())]
    assert perfect == ["D7_MACHINERY_IBD"]


@pytest.mark.parametrize("name,breaker", [
    ("D1_RESEMBLANCE", "homopolymer_painter"), ("D1_RESEMBLANCE", "ibs_without_ibd"), ("D2_MATERIAL", "cargo_without_capacity"),
    ("D2_MATERIAL", "harness_copy"), ("D3_BYTE_IDENTITY", "changed_encoding_conserved_function"),
    ("D3F_FOUNDER_MATERIAL", "machinery_without_founder_bytes"), ("D4_ORGANISM_MATERIAL", "cargo_without_capacity"),
    ("D5_CAPACITY", "trace_material_constructed_copier"), ("D7_STRICT", "machinery_synonymous_mutation")])
def test_named_breakers(name, breaker):
    assert not _score(K.DEFINITIONS[name])[breaker]


def test_threshold_is_bounded_not_pinned():
    ok = [t / 100 for t in range(1, 101) if all(K.D7_MACHINERY_IBD(c["record"], t / 100) == c["intended"]["reproduction"]
                                                for c in F.ADVERSARIAL.values())]
    assert min(ok) == 0.01 and max(ok) == 0.8


def test_source_diversity_separates_painting_from_copying():
    paint = F.ADVERSARIAL["self_painting_homopolymer"]["record"]; copy = F.ADVERSARIAL["exact_copier_no_heritable_variation"]["record"]
    assert S.source_diversity(paint) == 1 / 32 and S.source_diversity(copy) == 1.0
    assert S.donors(paint) == S.donors(copy) == {"P": 1.0}               # identical by every donor-share measure


def test_heredity_separate_from_reproduction():
    c = F.ADVERSARIAL["exact_copier_no_heritable_variation"]["record"]
    assert K.D7_MACHINERY_IBD(c) and not K.D6_HEREDITARY(c)
    for k, cc in F.ADVERSARIAL.items():
        assert K.D6_HEREDITARY(cc["record"]) == cc["intended"]["hereditary"], k


def test_qualifiers():
    for k, c in F.ADVERSARIAL.items():
        if "qualifier" in c["intended"]: assert K.qualifier(c["record"]) == c["intended"]["qualifier"], k


# ---------------------------------------------------------------- directive item 2 structures
def test_structures_representable_without_parent_field():
    for k, r in F.STRUCTURE.items():
        assert S.check(r) == [], k
        assert not any("parent" in key for key in r)


def test_no_singular_parent_where_mixed():
    for k in ("two_material_parents", "one_producer_two_donors", "recombination", "ibs_without_ibd", "ibd_with_changed_state"):
        assert S.singular_parent(F.STRUCTURE[k]) is None, k


def test_parent_id_convention_enforced():
    r = json.loads(json.dumps(F.STRUCTURE["two_material_parents"]))
    r["aggregation"] = [{"label": "parent_id", "value": "A", "rule": "SINGULAR_MATERIAL_PARENT", "convention": True}]
    assert any(x.startswith("A11") for x in S.check(r))
    h = json.loads(json.dumps(F.STRUCTURE["harness_copy"]))
    h["aggregation"] = [{"label": "parent_id", "value": "P", "rule": "SINGULAR_MATERIAL_PARENT", "convention": True}]
    assert S.check(h) == []                                            # a singular MATERIAL parent is fine; production says harness


def test_parent_field_rejected():
    r = json.loads(json.dumps(F.TH014_LEAK["SELF_CONSTRUCTED"])); r["parent_id"] = "P"
    assert any(x.startswith("A1") for x in S.check(r))
    r = json.loads(json.dumps(F.TH014_LEAK["SELF_CONSTRUCTED"])); r["material"]["parent"] = "P"
    assert any(x.startswith("A1") for x in S.check(r))


def test_validator_rules():
    base = F.TH014_LEAK["SELF_CONSTRUCTED"]
    def mut(fn):
        r = json.loads(json.dumps(base)); fn(r); return S.check(r)
    assert any(x.startswith("A4") for x in mut(lambda r: r["material"]["segments"].pop()))
    assert any(x.startswith("A5") for x in mut(lambda r: r["material"]["segments"][0].update(via="location")))
    assert any(x.startswith("A3") for x in mut(lambda r: r["carrier"].update(exec_what={"via": "pc"})))
    assert any(x.startswith("A6") for x in mut(lambda r: r["dependence"].append({"target": "material", "outcome": "x", "result": "ceases", "contrast": "c"})))
    assert any(x.startswith("A7") for x in mut(lambda r: r["capability"].append({"capability": "exact_self_copy", "result": True, "method": "label"})))
    assert any(x.startswith("A8") for x in mut(lambda r: (r["material"].update(segments=[S.seg(0, 32, "new_input")]),
                                                          r["aggregation"].append({"label": "descends_from", "rule": "x", "convention": False}))))
    assert any(x.startswith("A12") for x in mut(lambda r: r["contrast"].update(baseline="")))


# ---------------------------------------------------------------- historical regression suite
@pytest.mark.parametrize("k", sorted(R.CASES))
def test_regression_case(k):
    c = R.CASES[k]; r = c["record"]
    assert S.check(r) == [], k
    assert K.production_class(r) == c["expect"]["class"], k
    if "reproduction" in c["expect"]: assert K.D7_MACHINERY_IBD(r) == c["expect"]["reproduction"], k
    if "donors" in c["expect"]: assert len(S.donors(r)) == c["expect"]["donors"], k
    for lab in c.get("old_labels", []):                                   # the historical mistake must be rejected by the validator
        r2 = json.loads(json.dumps(r)); r2["aggregation"] = r2["aggregation"] + [lab]
        assert S.check(r2), (k, lab)


# ---------------------------------------------------------------- saturated-ruler guard
def test_saturated_guard():
    out = GD.compare({"a": 1.0, "b": 1.0}, max_score=1.0, distinct=True)
    assert out["verdict"] == GD.UNINFORMATIVE
    out = GD.compare({"a": 1.0, "b": 1.0}, max_score=1.0, distinct=True, secondary={"a": 0.3, "b": 0.9})
    assert out["verdict"] == "SEPARATED_BY_SECONDARY"
    assert GD.compare({"a": 1.0, "b": 0.7}, max_score=1.0, distinct=True)["verdict"] == "SEPARATED"
    assert GD.compare({"a": 1.0, "b": 1.0}, max_score=1.0, distinct=False)["verdict"] == "SAME_ENTITY"
