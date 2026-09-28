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
    assert v and all(x.split()[0] in ("A2", "A9", "A16") for x in v)


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


def _perfect(origins=None):
    keys = [k for k, c in F.ADVERSARIAL.items() if origins is None or c["origin"] in origins]
    return [n for n, fn in K.DEFINITIONS.items() if n != "D6_HEREDITARY"
            and all(fn(F.ADVERSARIAL[k]["record"]) == F.ADVERSARIAL[k]["intended"]["reproduction"] for k in keys)]


def test_the_winner_depends_on_the_case_set():
    """Review 1 (R1-3): the earlier claim 'only D7 matches' came from two author-added cases. Record the dependence instead of a
    winner: on the directive's own cases four definitions tie; each added case set changes who survives."""
    assert _perfect({"directive"}) == ["D5_CAPACITY", "D5T_CAPABLE_MATERIAL", "D7_MACHINERY_IBD", "D7_STRICT"]
    assert _perfect({"directive", "archaeon"}) == ["D5T_CAPABLE_MATERIAL", "D7_MACHINERY_IBD"]
    assert _perfect({"directive", "review1"}) == ["D5_CAPACITY", "D5T_CAPABLE_MATERIAL"]
    assert _perfect() == ["D5T_CAPABLE_MATERIAL"]


@pytest.mark.parametrize("name,breaker", [
    ("D1_RESEMBLANCE", "homopolymer_painter"), ("D1_RESEMBLANCE", "ibs_without_ibd"), ("D2_MATERIAL", "cargo_without_capacity"),
    ("D2_MATERIAL", "harness_copy"), ("D3_BYTE_IDENTITY", "changed_encoding_conserved_function"),
    ("D3F_FOUNDER_MATERIAL", "machinery_without_founder_bytes"), ("D4_ORGANISM_MATERIAL", "cargo_without_capacity"),
    ("D5_CAPACITY", "trace_material_constructed_copier"), ("D7_STRICT", "machinery_synonymous_mutation"),
    ("D7_MACHINERY_IBD", "von_neumann_constructor_description"), ("D4_ORGANISM_MATERIAL", "universal_copier_junk")])
def test_named_breakers(name, breaker):
    assert not _score(K.DEFINITIONS[name])[breaker]


def test_d5t_threshold_is_bounded_not_pinned():
    ok = [t / 100 for t in range(1, 101) if all(K.D5T_CAPABLE_MATERIAL(c["record"], t / 100) == c["intended"]["reproduction"]
                                                for c in F.ADVERSARIAL.values())]
    assert min(ok) == 0.04 and max(ok) == 0.5                             # (1/32, 0.5]: the gap between two authored points


def test_review1_counterexamples_now_rejected():
    import copy
    r = copy.deepcopy(F.TH014_LEAK["SELF_CONSTRUCTED"]); r["carrier"]["template"] = "P"; r["production"]["ancestor"] = "P"
    assert sum(x.startswith("A1") for x in S.check(r)) == 2                                                     # CX-1a
    r = copy.deepcopy(F.TH014_LEAK["SELF_CONSTRUCTED"]); r["state"]["apparent_fidelity"] = 1.0
    assert S.check(r) == []                                                                                     # CX-1b
    h = copy.deepcopy(F.TH014_LEAK["HARNESS_COPY"]); h["aggregation"] = [{"label": "replicator", "rule": "x", "convention": True}]
    assert any(x.startswith("A14") for x in S.check(h))                                                         # CX-2c
    r = copy.deepcopy(F.TH014_LEAK["SELF_CONSTRUCTED"]); r["material"]["resolution"] = "counts"
    r["material"]["segments"] = [S.seg(0, 32, entity="P"), S.seg(0, 32, entity="Q")]
    assert any(x.startswith("A4") for x in S.check(r))                                                          # CX-5c
    t = copy.deepcopy(F.ADVERSARIAL["trace_material_constructed_copier"]["record"])
    t["capability"][0]["machinery_loci"] = [0]
    assert any(x.startswith("A17") for x in S.check(t))                                                         # CX-3c
    assert not K.D7_MACHINERY_IBD(F.ADVERSARIAL["universal_copier_junk"]["record"])                             # CX-3a


def test_source_diversity_separates_painting_from_copying():
    paint = F.ADVERSARIAL["self_painting_homopolymer"]["record"]; copy = F.ADVERSARIAL["exact_copier_no_heritable_variation"]["record"]
    assert S.source_diversity(paint) == 1 / 32 and S.source_diversity(copy) == 1.0
    assert S.donors(paint) == S.donors(copy) == {"P": 1.0}               # identical by every donor-share measure


def test_heredity_separate_from_reproduction():
    c = F.ADVERSARIAL["exact_copier_no_heritable_variation"]["record"]
    assert K.D5T_CAPABLE_MATERIAL(c) and not K.D6_HEREDITARY(c)
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
RELEVANT_RULE = {"descends_from": "A8", "lineage_member": "A8", "parent_id": "A11", "recombinant": "A15", "mixed_parent": "A15",
                 "causal_reproduction": "A14", "reproduction": "A14"}


@pytest.mark.parametrize("k", sorted(R.CASES))
def test_regression_case(k):
    c = R.CASES[k]; r = c["record"]
    assert S.check(r) == [], k
    assert K.production_class(r) == c["expect"]["class"], k
    if "reproduction" in c["expect"]: assert K.D7_MACHINERY_IBD(r) == c["expect"]["reproduction"], k
    if "donors" in c["expect"]: assert len(S.donors(r)) == c["expect"]["donors"], k
    if "capability" in c["expect"]: assert S.reproduces(r) == c["expect"]["capability"], k
    for lab in c.get("old_labels", []):   # the historical mistake must be rejected BY THE RULE THAT NAMES IT (Review 1 R1-4)
        r2 = json.loads(json.dumps(r)); r2["aggregation"] = r2["aggregation"] + [lab]
        fired = {x.split()[0] for x in S.check(r2)}
        want = RELEVANT_RULE.get(lab["label"], {"A9", "A8"})              # self labels: wrong channel (A9) or no donor (A8)
        assert fired & set(want if isinstance(want, set) else {want}), (k, lab, fired)


# ---------------------------------------------------------------- saturated-ruler guard
def test_saturated_guard():
    out = GD.compare({"a": 1.0, "b": 1.0}, max_score=1.0, distinct=True)
    assert out["verdict"] == GD.UNINFORMATIVE
    out = GD.compare({"a": 1.0, "b": 1.0}, max_score=1.0, distinct=True, secondary={"a": 0.3, "b": 0.9})
    assert out["verdict"] == "SEPARATED_BY_SECONDARY"
    assert GD.compare({"a": 1.0, "b": 0.7}, max_score=1.0, distinct=True)["verdict"] == "SEPARATED"
    assert GD.compare({"a": 1.0, "b": 1.0}, max_score=1.0, distinct=False)["verdict"] == "SAME_ENTITY"
