"""WP-0e: the kind-generic builder.

    0e-a  bitstring and fixed-scale walk templates build and validate through
          their real kind contracts; a third, different payload (a fixture
          kind registered only for the test) exercises the generic path
    0e-b  missing kind, destroyed value, unsupported sampler, wrong scalar
          type, vector-valued outcome field -> specific failures, before queueing
    0e-c  incoherent bit/length rejected; unrelated axes independently drawable
    0e-d  fixed-seed draws replay; nothing defaulted; legacy sealed spec keeps
          its hash
"""
from __future__ import annotations

import json

import pytest

from archaeon.producer import kindspec as K
from archaeon.producer import specbuild, templates as T
from archaeon.producer.specbuild import SpecInvalid


def _t(tid, kind, space, **extra):
    t = {"template_id": tid, "kind": kind, "param_space": space,
         "origin": {"source": "LLM", "field": "t", "reference": "-", "proposed_by": "t"},
         "status": "PROPOSED", "registry_version": T.REGISTRY_VERSION}
    t.update(extra)
    return t


def _load(tmp_path, t):
    p = tmp_path / "{}.json".format(t["template_id"])
    p.write_text(json.dumps(t, indent=2, sort_keys=True), encoding="utf-8")
    return T.load(p)


WALK_RULE = {"field": "displacement", "op": ">=", "value": 10.0,
             "if_true": "FALSIFIED", "if_false": "SURVIVED",
             "if_indeterminate": "INCONCLUSIVE"}
WALK_REPEAT = {"count": 4, "order": "sequential", "seed_derivation": "sha256_index",
               "state": "persist", "budget": {"max_seconds": 60, "max_observations": 8}}


# ---------------------------------------------------------------- 0e-a
def test_bitstring_legacy_path_builds_and_keeps_hash(tmp_path):
    t = _load(tmp_path, _t("bs.v0", "evaluate_bitstring",
                           {"seed_root": {"constant": 7}, "length": {"constant": 16},
                            "bits": {"uniform_bits": "length"}}))
    params = T.draw_params(t, seed=3)
    spec = K.build_validated(t, params)
    legacy = specbuild.build_validated(params)
    assert specbuild.spec_hash(spec) == specbuild.spec_hash(legacy)


def test_fixed_scale_walk_template_builds_v3(tmp_path):
    t = _load(tmp_path, _t("walk.v1", "random_walk_v0",
                           {"seed_root": {"constant": 1}, "steps": {"choices": [100, 400]},
                            "step_scale": {"constant": 1}},
                           outcome_rule=WALK_RULE, repeat=WALK_REPEAT))
    c = T.check(t)
    assert (c["runnable"], c["drawable"], c["buildable"]) == (True, True, True), c
    spec = K.build_validated(t, T.draw_params(t, seed=0))
    assert spec["spec_version"] == 3 and spec["repeat"]["state"] == "persist"
    assert spec["work"]["payload"]["step_scale"] == 1


def test_shipped_falsification_walk_v1_is_buildable_and_v0_is_not():
    v1 = T.load(T.INBOX_DIR / "falsification_walk.v1.json")
    c1 = T.check(v1)
    assert (c1["runnable"], c1["drawable"], c1["buildable"]) == (True, True, True), c1
    v0 = T.load(T.INBOX_DIR / "falsification_walk.v0.json")
    c0 = T.check(v0)
    assert c0["runnable"] and not c0["drawable"]      # nulls stay null
    assert "destroyed" in c0["reason"]


def test_third_kind_fixture_exercises_generic_path(monkeypatch, tmp_path):
    """A kind that is NOT bitstring or walk, registered only for this test,
    with its own result fields: the builder must not special-case."""
    from viv import kinds as vk
    fake = vk.Kind(kind="nk_fixture_v0", params=frozenset({"bits", "length", "k"}),
                   implemented=True, owner="test", stateful=False)
    real = K._kind
    monkeypatch.setattr(K, "_kind", lambda name: fake if name == "nk_fixture_v0" else real(name))
    monkeypatch.setitem(K.RESULT_FIELDS, "nk_fixture_v0",
                        {"score": float, "contribution": list, "solved": bool})
    monkeypatch.setitem(K.PARAM_TYPES, "nk_fixture_v0", {"bits": (str,), "length": (int,), "k": (int,)})
    t = _t("nk.v0", "nk_fixture_v0",
           {"world": {"seed_root": {"constant": 2}},
            "payload": {"length": {"constant": 8}, "k": {"choices": [0, 2]},
                        "bits": {"uniform_bits": "length"}}},
           outcome_rule={"field": "solved", "op": "==", "value": False,
                         "if_true": "SURVIVED", "if_false": "FALSIFIED",
                         "if_indeterminate": "INCONCLUSIVE"})
    t["param_space"], _ = T.normalize_param_space(t["param_space"])
    params = T.draw_params(t, seed=1)
    spec = K.build_from_template(t, params)          # unvalidated: kind unknown to viv validator
    assert spec["work"]["kind"] == "nk_fixture_v0" and set(spec["work"]["payload"]) == {"bits", "length", "k"}
    # vector-valued outcome field is refused
    bad = dict(t, outcome_rule=dict(t["outcome_rule"], field="contribution"))
    with pytest.raises(SpecInvalid, match="vector-valued"):
        K.build_from_template(bad, params)


# ---------------------------------------------------------------- 0e-b
def test_specific_failures_before_queueing(tmp_path):
    base = {"seed_root": 1, "steps": 100, "step_scale": 1}
    walk = _t("w", "random_walk_v0", {}, outcome_rule=WALK_RULE, repeat=WALK_REPEAT)
    with pytest.raises(SpecInvalid, match="not registered"):
        K.build_from_template(dict(walk, kind="no_such_kind"), base)
    with pytest.raises(SpecInvalid, match="null"):
        K.build_from_template(walk, dict(base, steps=None))
    with pytest.raises(SpecInvalid, match="must be int"):
        K.build_from_template(walk, dict(base, steps="100"))
    with pytest.raises(SpecInvalid, match="must be int"):
        K.build_from_template(walk, dict(base, steps=True))
    with pytest.raises(SpecInvalid, match="does not accept"):
        K.build_from_template(walk, dict(base, extra=1))
    with pytest.raises(SpecInvalid, match="nothing is defaulted"):
        K.build_from_template(walk, {"seed_root": 1, "steps": 100})
    with pytest.raises(SpecInvalid, match="not a declared result field"):
        K.build_from_template(dict(walk, outcome_rule=dict(WALK_RULE, field="nope")), base)
    with pytest.raises(SpecInvalid, match="declares no outcome_rule"):
        K.build_from_template(dict(walk, outcome_rule=None), base)
    with pytest.raises(SpecInvalid, match="stateful"):
        K.build_from_template(dict(walk, repeat=None), base)
    with pytest.raises(SpecInvalid, match="quietly not happening"):
        bs = _t("b", "evaluate_bitstring", {}, outcome_rule={"field": "solved", "op": "==",
                "value": False, "if_true": "SURVIVED", "if_false": "FALSIFIED",
                "if_indeterminate": "INCONCLUSIVE"}, repeat=WALK_REPEAT)
        K.build_from_template(bs, {"seed_root": 1, "bits": "0101", "length": 4})


def test_unsupported_sampler_fails_at_draw(tmp_path):
    t = _load(tmp_path, _t("s", "random_walk_v0",
                           {"seed_root": {"constant": 1}, "steps": {"gaussian": [1, 2]},
                            "step_scale": {"constant": 1}},
                           outcome_rule=WALK_RULE, repeat=WALK_REPEAT))
    c = T.check(t)
    assert c["runnable"] and not c["drawable"]
    assert "unknown parameter space form" in c["reason"]


# ---------------------------------------------------------------- 0e-c
def test_incoherent_bits_length_rejected_and_other_axes_independent(tmp_path):
    bs = _t("b", "evaluate_bitstring", {})
    with pytest.raises(SpecInvalid, match="bits is 4 characters but length is 8"):
        K.build_from_template(bs, {"seed_root": 1, "bits": "0101", "length": 8})
    t = _load(tmp_path, _t("w", "random_walk_v0",
                           {"seed_root": {"int_range": [1, 1000]}, "steps": {"choices": [100, 400, 1600]},
                            "step_scale": {"constant": 1}},
                           outcome_rule=WALK_RULE, repeat=WALK_REPEAT))
    draws = [T.draw_params(t, seed=s) for s in range(40)]
    assert len({d["seed_root"] for d in draws}) > 5 and len({d["steps"] for d in draws}) == 3
    assert {d["step_scale"] for d in draws} == {1}


# ---------------------------------------------------------------- 0e-d
def test_fixed_seed_replay_and_no_defaults(tmp_path):
    t = _load(tmp_path, _t("w", "random_walk_v0",
                           {"seed_root": {"int_range": [1, 1000]}, "steps": {"choices": [100, 400]},
                            "step_scale": {"constant": 1}},
                           outcome_rule=WALK_RULE, repeat=WALK_REPEAT))
    a = K.build_validated(t, T.draw_params(t, seed=11))
    b = K.build_validated(t, T.draw_params(t, seed=11))
    assert specbuild.spec_hash(a) == specbuild.spec_hash(b)
    assert set(a["work"]["payload"]) == {"steps", "step_scale"}


def test_local_result_fields_match_executor_source():
    """The declared copy must agree with what the executors actually return."""
    from archaeon.producer.contract import ensure_viv_importable
    ensure_viv_importable()
    import inspect
    from viv import executors as ex
    src = inspect.getsource(ex)
    # evaluate_bitstring delegates to the ENGINE's reference executor, so its
    # result keys live in sfe/executors.py
    from pathlib import Path
    eng = (Path(ex.__file__).resolve().parents[2] / "SerendipityFoundry" /
           "SerendipityFoundryEngine" / "sfe" / "executors.py").read_text(encoding="utf-8")
    for kind, fields in K.RESULT_FIELDS.items():
        for f in fields:
            assert '"{}"'.format(f) in src or '"{}"'.format(f) in eng, (kind, f)
