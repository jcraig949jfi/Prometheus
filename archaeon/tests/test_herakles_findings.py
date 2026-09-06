"""Herakles's expansion-design pass (2026-09-06) found three defects in
Archaeon's lane and one analytic fact about the substrate. Each is pinned
here so it cannot silently return.

    flat param_space   69 inbox templates were written flat against the
                       roadmap example; the loader nested; zero were runnable
    F-2                check() validated NAMES, not drawability
    C-6 / F-3          nothing checked coherence BETWEEN axes before publish
    C-0                no way to pin a value (fixed-seed pattern)
    F-6                on a hashed target var(score) = 1/(4L) for ANY bits, so
                       a length sweep manufactures a variance ratio D3 reads
"""
from __future__ import annotations

import json

import pytest

from archaeon import config as cfg
from archaeon.producer import templates as T


def _write(tmp_path, name, body):
    p = tmp_path / "{}.json".format(name)
    p.write_text(json.dumps(body, indent=2, sort_keys=True), encoding="utf-8")
    return p


def _tmpl(tid, kind, space, **extra):
    t = {"template_id": tid, "kind": kind, "param_space": space,
         "origin": {"source": "LLM", "field": "test", "reference": "-",
                    "proposed_by": "test"},
         "status": "PROPOSED", "registry_version": T.REGISTRY_VERSION}
    t.update(extra)
    return t


# --------------------------------------------------------------------------
# flat vs nested
# --------------------------------------------------------------------------
def test_flat_param_space_is_normalised_by_name_not_inferred(tmp_path):
    flat = _tmpl("flat.v0", "evaluate_bitstring",
                 {"seed_root": {"int_range": [1, 9]},
                  "length": {"choices": [16]},
                  "bits": {"uniform_bits": "length"}})
    t = T.load(_write(tmp_path, "flat.v0", flat))
    assert t["_param_space_form"] == "flat"
    assert set(t["param_space"]["world"]) == {"seed_root"}
    assert set(t["param_space"]["payload"]) == {"bits", "length"}
    c = T.check(t)
    assert (c["runnable"], c["drawable"], c["buildable"]) == (True, True, True)


def test_flat_and_nested_of_same_content_share_one_hash(tmp_path):
    flat = _tmpl("h.v0", "evaluate_bitstring",
                 {"seed_root": {"constant": 5}, "length": {"constant": 16},
                  "bits": {"uniform_bits": "length"}})
    nested = _tmpl("h.v0", "evaluate_bitstring",
                   {"world": {"seed_root": {"constant": 5}},
                    "payload": {"length": {"constant": 16},
                                "bits": {"uniform_bits": "length"}}})
    a = T.load(_write(tmp_path, "a", flat))
    b = T.load(_write(tmp_path, "b", nested))
    assert a["_content_hash"] == b["_content_hash"]


def test_nested_with_unknown_section_is_refused(tmp_path):
    bad = _tmpl("bad.v0", "evaluate_bitstring",
                {"payload": {}, "world": {}, "extra": {}})
    with pytest.raises(T.TemplateError, match="unknown sections"):
        T.load(_write(tmp_path, "bad", bad))


# --------------------------------------------------------------------------
# F-2: names are not drawability; C-6: drawable is not buildable
# --------------------------------------------------------------------------
def test_destroyed_range_fails_check_with_a_typed_reason_not_a_typeerror(tmp_path):
    t = T.load(_write(tmp_path, "d", _tmpl(
        "destroyed.v0", "random_walk_v0",
        {"steps": {"int_range": None}, "step_scale": {"int_range": None}})))
    c = T.check(t)
    assert c["runnable"] and not c["drawable"] and not c["buildable"]
    assert "destroyed" in c["reason"] and c["lane"] == "archaeon"
    with pytest.raises(T.TemplateError):
        T.draw_params(t, seed=0)


def test_empty_choices_is_not_drawable(tmp_path):
    t = T.load(_write(tmp_path, "e", _tmpl(
        "empty.v0", "random_walk_v0",
        {"steps": {"choices": []}, "step_scale": {"constant": 1}})))
    assert not T.check(t)["drawable"]


def test_template_without_seed_root_draws_but_does_not_build(tmp_path):
    """The one fully parameterised inbox template has no world section. A
    spec needs seed_root and Vivarium permits no defaults, so it is
    drawable and NOT buildable -- and admitted() must exclude it."""
    body = _tmpl("noworld.v0", "evaluate_bitstring",
                 {"length": {"constant": 16}, "bits": {"uniform_bits": "length"}})
    h = T.load(_write(tmp_path, "n", body))["_content_hash"]   # as PROPOSED
    body.update(status="ADMITTED", admitted_by="test", admitted_content_hash=h)
    _write(tmp_path, "n", body)
    t = T.load(tmp_path / "n.json")
    c = T.check(t)
    assert c["drawable"] and not c["buildable"]
    assert "seed_root" in c["reason"]
    assert T.admitted(tmp_path) == []


def test_random_walk_template_is_not_buildable_until_e18(tmp_path):
    t = T.load(_write(tmp_path, "w", _tmpl(
        "walk.v0", "random_walk_v0",
        {"seed_root": {"constant": 1}, "steps": {"constant": 100},
         "step_scale": {"constant": 1}})))
    c = T.check(t)
    assert c["runnable"] and c["drawable"] and not c["buildable"]
    assert "E18" in c["reason"]


def test_incoherent_axes_cannot_reach_a_spec(tmp_path):
    """F-3: bits and length drawn independently. The builder refuses the
    mismatch, and check() reports it before admission."""
    t = T.load(_write(tmp_path, "i", _tmpl(
        "incoherent.v0", "evaluate_bitstring",
        {"seed_root": {"constant": 1}, "length": {"constant": 32},
         "bits": {"choices": ["0101010101010101"]}})))
    c = T.check(t)
    assert c["drawable"] and not c["buildable"]
    assert "bits is 16" in c["reason"]


# --------------------------------------------------------------------------
# C-0: the fixed-seed pattern
# --------------------------------------------------------------------------
def test_constant_form_pins_the_world_across_draws(tmp_path):
    t = T.load(_write(tmp_path, "c", _tmpl(
        "fixed.v0", "evaluate_bitstring",
        {"seed_root": {"constant": 424242}, "length": {"constant": 24},
         "bits": {"uniform_bits": "length"}})))
    draws = [T.draw_params(t, seed=s) for s in range(6)]
    assert {d["seed_root"] for d in draws} == {424242}
    assert {d["length"] for d in draws} == {24}
    assert len({d["bits"] for d in draws}) > 1, "queries vary, target does not"
    assert T.check(t)["buildable"]


def test_shipped_calibration_templates_load_and_check():
    """E3 (exchangeability null) and C-0 (fixed target) are PROPOSED in the
    inbox; both must be fully checkable so admission is a one-line act."""
    for name in ("bitstring.exchangeability_null.v0", "bitstring.fixed_target.v0"):
        t = T.load(T.INBOX_DIR / "{}.json".format(name))
        assert t["status"] == "PROPOSED"
        c = T.check(t)
        assert (c["runnable"], c["drawable"], c["buildable"]) == (True, True, True), c


# --------------------------------------------------------------------------
# F-6: the analytic null of the bitstring substrate
# --------------------------------------------------------------------------
def analytic_score_variance(length: int) -> float:
    """score = matches/L with matches ~ Binomial(L, 1/2) on a hashed target,
    for ANY candidate bits. var = L*(1/4)/L^2 = 1/(4L)."""
    return 1.0 / (4.0 * length)


def test_d3_is_not_fooled_by_length_within_allowed_lengths():
    from archaeon.producer.contract import ALLOWED_LENGTHS
    d = cfg.DEFAULT.detectors
    for a in ALLOWED_LENGTHS:
        for b in ALLOWED_LENGTHS:
            r = analytic_score_variance(a) / analytic_score_variance(b)
            assert d.d3_low_ratio <= r <= d.d3_high_ratio, (a, b, r)


def test_d3_would_fire_on_a_wide_length_sweep_so_length_is_a_census_axis():
    """A world at L=16 beside worlds at L=64 gives ratio 4.0 > 3.0. The
    signal is a length artefact, not structure. The producer's ALLOWED_LENGTHS
    is what keeps it out; widening it must widen the census first."""
    d = cfg.DEFAULT.detectors
    r = analytic_score_variance(16) / analytic_score_variance(64)
    assert r > d.d3_high_ratio
