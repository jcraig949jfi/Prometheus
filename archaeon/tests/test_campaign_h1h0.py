"""H1/H0 plan (Track A items 7-8): split, licensed metadata, frozen
retrieval, two-phase plan, validation against the kind."""
from __future__ import annotations

import json

import pytest

from archaeon.producer import campaign_h1h0 as H


def test_task_split_is_seeded_disjoint_and_excludes_constants():
    s1, s2 = H.task_split(), H.task_split()
    assert [t["tt"] for t in s1["source"]] == [t["tt"] for t in s2["source"]]
    src = {t["tt"] for t in s1["source"]}; tgt = {t["tt"] for t in s1["target"]}
    assert len(src) == H.N_SOURCE and len(tgt) == H.N_TARGET and not src & tgt
    assert "00000000" not in src | tgt and "11111111" not in src | tgt
    assert H.task_split(seed=1)["source"][0]["tt"] != s1["source"][0]["tt"]


def test_licensed_metadata_on_known_functions():
    maj3 = H.truth_table(lambda a, b, c: 1 if a + b + c >= 2 else 0)
    xor3 = H.truth_table(lambda a, b, c: a ^ b ^ c)
    and01 = H.truth_table(lambda a, b, c: a & b)
    m = H.licensed_metadata(maj3)
    assert m["symmetric"] and m["self_dual"] and m["monotone"] and m["popcount"] == 4
    x = H.licensed_metadata(xor3)
    assert x["symmetric"] and x["self_dual"] and not x["monotone"]
    a = H.licensed_metadata(and01)
    assert not a["symmetric"] and not a["self_dual"] and a["monotone"] and a["popcount_bucket"] == "low"


def _fake_source_results(split):
    out = []
    for i, t in enumerate(split["source"]):
        wit = [{"candidate_size": 1 + (j % 3), "inputs": [(i + j) & 1, (i >> 1) & 1, j & 1],
                "expected": 1, "observed": 0, "reason": "mismatch"} for j in range(3)]
        sol = json.dumps(["and", ["input", 0], ["input", 1]]) if i % 2 == 0 else json.dumps(["or", ["and", ["input", 0], ["input", 1]], ["input", 2]])
        out.append({"task_id": t["task_id"], "tt": t["tt"], "licensed_metadata": t["licensed_metadata"],
                    "result": {"witnesses": wit, "solution": sol}})
    return out


def test_packs_are_distinct_seeded_and_report_shortfall():
    split = H.task_split()
    pool = H.failure_pool(_fake_source_results(split))
    t = split["target"][0]
    p1 = H.build_pack(pool, "random_compatible", t)
    p2 = H.build_pack(pool, "random_compatible", t)
    assert p1["object"]["items"] == p2["object"]["items"] and p1["k_actual"] == H.K_PACK and p1["shortfall"] == 0
    assert len({tuple(x) for x in p1["object"]["items"]}) == p1["k_actual"]
    # a poor pool: shortfall is reported, never topped up
    small = [pool[0], dict(pool[0])]
    p3 = H.build_pack(small, "random_compatible", t)
    assert p3["k_actual"] == 1 and p3["shortfall"] == H.K_PACK - 1 and p3["shortfall_rule"] == "report_and_proceed"
    with pytest.raises(ValueError):
        H.build_pack(pool, "by_target_labels", t)


def test_signature_policy_ranks_by_licensed_metadata_and_is_marked_unlicensed():
    split = H.task_split()
    pool = H.failure_pool(_fake_source_results(split))
    t = split["target"][0]
    p = H.build_pack(pool, "signature_v0", t)
    assert p["retrieval_rationale"]["licence_status"].startswith("PROPOSED")
    # the first chosen input comes from a source task of maximal agreement
    best = max(H._signature_agreement(t["licensed_metadata"], q["source_metadata"]) for q in pool)
    assert p["retrieval_rationale"]["top_agreement"] == best
    # never from the target's own table
    assert all(q["source_tt"] != t["tt"] for q in pool)


def test_extractor_is_deterministic_and_labelled_derived():
    split = H.task_split()
    lib = H.extract_library(_fake_source_results(split))
    assert lib["provenance"] == "derived" and not lib["instrument_control"]
    assert lib["n_kept"] >= 1 and lib["object"]["components"][0]["expr"] == ["and", ["input", 0], ["input", 1]]
    inst = H.library_object(H.INSTRUMENT_LIBRARY, provenance="instrument_control")
    assert inst["instrument_control"]


def test_phase2_cells_differ_only_in_the_two_slots_and_relevant_arm_is_withheld():
    split = H.task_split()
    p2 = H.plan_phase2(_fake_source_results(split), split)
    rows = p2["rows"]
    by = {(r["task_id"], r["arm_id"]): r for r in rows}
    t0 = split["target"][0]["task_id"]
    cells = {c: by[(t0, c)]["spec"]["work"]["payload"] for c in H.H0_CELLS}
    for c in H.H0_CELLS:
        others = {k: v for k, v in cells[c].items() if k not in ("source_pack", "component_library")}
        assert others == {k: v for k, v in cells["S00"].items() if k not in ("source_pack", "component_library")}
    assert cells["S00"]["source_pack"] is None and cells["S00"]["component_library"] is None
    assert cells["S11"]["source_pack"] is not None and cells["S11"]["component_library"] is not None
    assert cells["S10"]["source_pack"] == cells["S11"]["source_pack"]
    if not H.RELEVANCE_LICENSED:
        assert not any(r["arm_id"] == "relevant_pack" for r in rows)
        assert len(p2["withheld"]) == H.N_TARGET
    assert len({r["request_key"] for r in rows}) == len(rows)
    assert p2["library_provenance"] == "instrument_control"
    assert all(r["library"]["instrument_control"] for r in rows if r["library"])


def test_phase1_and_phase2_validate_against_the_kind_when_registered():
    c1 = H.check(H.plan_phase1())
    if not c1["kind_registered"]:
        assert c1["blockers"][0]["lane"] == "vivarium"
        return
    assert c1["ok_to_issue"] is True, c1["invalid"][:3]
    split = H.task_split()
    p2 = H.plan_phase2(_fake_source_results(split), split)
    c2 = H.check(p2["rows"])
    assert c2["ok_to_issue"] is True, c2["invalid"][:3]
    assert all(v["slot"] for v in p2["artifacts"].values())


def test_failure_pool_accepts_the_live_case_shape_and_the_bare_vector():
    split = H.task_split()
    t = split["source"][0]
    live = {"task_id": t["task_id"], "tt": t["tt"], "licensed_metadata": t["licensed_metadata"],
            "result": {"witnesses": [{"inputs": [[1, 1, 1]], "expected": [[1]], "observed": [[0]], "candidate_size": 4},
                                     {"inputs": [0, 1, 0], "candidate_size": 2},
                                     {"inputs": None, "reason": "no_witness_and_not_full_coverage"}]}}
    pool = H.failure_pool([live])
    assert [p["inputs"] for p in pool] == [[1, 1, 1], [0, 1, 0]]


def test_plan_reports_the_order_only_scope_and_the_rescope_condition():
    split = H.task_split()
    p2 = H.plan_phase2(_fake_source_results(split), split)
    assert p2["h1_contrast"].startswith("transport_only") and "pool_distinct" in p2
    assert p2["relevance_testable_here"] == (p2["pool_distinct"] >= 2 * H.K_PACK)
    assert H.RELEVANCE_LICENSED is False
