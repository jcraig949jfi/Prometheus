"""The template registry: the menu random science draws from."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from archaeon.producer import templates as T


def _admitted(tmp_path, tid="t.v0", kind="evaluate_bitstring", **over):
    t = {"template_id": tid, "registry_version": T.REGISTRY_VERSION,
         "kind": kind,
         "param_space": {"world": {"seed_root": {"int_range": [1, 9]}},
                         "payload": {"length": {"choices": [16, 24]},
                                     "bits": {"uniform_bits": "length"}}},
         "origin": {"source": "RNG", "proposed_by": "test"},
         "status": "ADMITTED", "admitted_by": "test",
         "admitted_at": "2026-09-06T00:00:00+00:00"}
    t.update(over)
    t["admitted_content_hash"] = T._content_hash(t)
    p = tmp_path / "{}.json".format(tid)
    p.write_text(json.dumps(t), encoding="utf-8")
    return p


# --------------------------------------------------------------------------
def test_the_shipped_baseline_loads_and_is_frozen():
    menu = T.admitted()
    ids = {t["template_id"] for t in menu}
    assert "bitstring.uniform.v0" in ids
    t = next(t for t in menu if t["template_id"] == "bitstring.uniform.v0")
    assert t.get("frozen") is True
    assert t["admitted_content_hash"] == t["_content_hash"]


def test_baseline_reproduces_the_old_random_generator_space():
    """bitstring.uniform.v0 must be random.v0 ported verbatim: same lengths,
    same seed_root range, same bits rule. It is the frozen baseline."""
    from archaeon.producer import randomgen as R
    from archaeon.producer import contract as C
    t = next(t for t in T.admitted() if t["template_id"] == "bitstring.uniform.v0")
    assert t["param_space"]["payload"]["length"]["choices"] == list(C.ALLOWED_LENGTHS)
    assert t["param_space"]["world"]["seed_root"]["int_range"] == list(R.SEED_ROOT_RANGE)


def test_draw_is_deterministic_and_inside_the_space(tmp_path):
    _admitted(tmp_path)
    a = T.draw("l", "2026-09-06", directory=tmp_path)
    b = T.draw("l", "2026-09-06", directory=tmp_path)
    assert a["seed"] == b["seed"] and a["params"] == b["params"]
    p = a["params"]
    assert p["length"] in (16, 24) and len(p["bits"]) == p["length"]
    assert 1 <= p["seed_root"] <= 9
    assert a["template_id"] == "t.v0" and a["menu_size"] == 1


def test_draw_varies_with_nonce(tmp_path):
    _admitted(tmp_path)
    a = T.draw("l", "2026-09-06", nonce="0", directory=tmp_path)
    b = T.draw("l", "2026-09-06", nonce="1", directory=tmp_path)
    assert a["seed"] != b["seed"]


# --------------------------------------------------------------------------
# Admission is a human act; the inbox is never drawn from
# --------------------------------------------------------------------------
def test_proposed_templates_are_never_drawn(tmp_path):
    _admitted(tmp_path, tid="live.v0")
    _admitted(tmp_path, tid="pending.v0", status="PROPOSED")
    menu = T.admitted(tmp_path)
    assert {t["template_id"] for t in menu} == {"live.v0"}


def test_propose_writes_only_proposed_and_strips_admission(tmp_path):
    inbox = tmp_path / "inbox"
    p = T.propose({"template_id": "x.v0", "kind": "evaluate_bitstring",
                   "param_space": {"payload": {"bits": {"uniform_bits": "length"},
                                               "length": {"choices": [16]}}},
                   "origin": {"source": "LLM", "proposed_by": "test"},
                   "status": "ADMITTED", "admitted_by": "sneaky"},
                  directory=inbox)
    t = json.loads(p.read_text())
    assert t["status"] == "PROPOSED"
    assert "admitted_by" not in t
    # and the inbox directory is not the menu
    assert T.admitted(tmp_path) == []


def test_an_admitted_template_that_changed_is_refused(tmp_path):
    p = _admitted(tmp_path)
    t = json.loads(p.read_text())
    t["param_space"]["payload"]["length"]["choices"] = [16, 24, 32, 64]  # edited
    p.write_text(json.dumps(t))
    with pytest.raises(T.TemplateError, match="changed after admission"):
        T.load(p)


def test_admitted_needs_an_admitter(tmp_path):
    p = _admitted(tmp_path)
    t = json.loads(p.read_text())
    t.pop("admitted_by")
    p.write_text(json.dumps(t))
    with pytest.raises(T.TemplateError, match="admitted_by"):
        T.load(p)


# --------------------------------------------------------------------------
# A template Vivarium cannot run is an expansion request
# --------------------------------------------------------------------------
def test_unimplemented_kind_is_an_expansion_request_not_a_menu_item(tmp_path):
    _admitted(tmp_path, tid="future.v0", kind="archaeon.probe.v0",
              param_space={"payload": {}})
    assert T.admitted(tmp_path) == []
    t = T.load(tmp_path / "future.v0.json")
    c = T.check(t)
    assert not c["runnable"] and c["lane"] == "vivarium"


def test_param_mismatch_with_kind_is_archaeons_problem(tmp_path):
    _admitted(tmp_path, tid="bad.v0",
              param_space={"payload": {"bits": {"uniform_bits": "length"}}})
    c = T.check(T.load(tmp_path / "bad.v0.json"))
    assert not c["runnable"] and c["lane"] == "archaeon"


def test_menu_growth_metric(tmp_path):
    _admitted(tmp_path, tid="a.v0")
    _admitted(tmp_path, tid="b.v0", origin={"source": "LITERATURE",
                                            "proposed_by": "t"})
    (tmp_path / "inbox").mkdir()
    (tmp_path / "inbox" / "c.json").write_text("{}")
    g = T.menu_growth(tmp_path)
    assert g["admitted"] == 2 and g["proposed_in_inbox"] == 1
    assert g["admitted_by_origin"] == {"RNG": 1, "LITERATURE": 1}


def test_the_shipped_baseline_is_actually_drawable():
    """Loading is not drawing. The baseline was loaded in tests and never drawn,
    and the first draw against it raised KeyError because sort_keys=True put
    `bits` before `length`. A template on the menu must survive a real draw."""
    d = T.draw("prod", "2026-09-06", nonce="0")
    assert d["template_id"] == "bitstring.uniform.v0"
    p = d["params"]
    assert len(p["bits"]) == p["length"]
    assert p["length"] in (16, 24, 32)


def test_draw_is_independent_of_declared_key_order(tmp_path):
    """Same seed, same params, whichever order the file lists keys in."""
    t = {"template_id": "o.v0", "registry_version": T.REGISTRY_VERSION,
         "kind": "evaluate_bitstring",
         "param_space": {"world": {"seed_root": {"int_range": [1, 9]}},
                         "payload": {"bits": {"uniform_bits": "length"},
                                     "length": {"choices": [16, 24]}}},
         "origin": {"source": "RNG", "proposed_by": "t"},
         "status": "ADMITTED", "admitted_by": "t",
         "admitted_at": "2026-09-06T00:00:00+00:00"}
    t["admitted_content_hash"] = T._content_hash(t)
    (tmp_path / "o.v0.json").write_text(json.dumps(t, sort_keys=True))
    a = T.draw("l", "2026-09-06", directory=tmp_path)["params"]
    (tmp_path / "o.v0.json").write_text(json.dumps(t, sort_keys=False))
    b = T.draw("l", "2026-09-06", directory=tmp_path)["params"]
    assert a == b
