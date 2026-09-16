"""THEO-REQ-002 (comms #240): per-parameter AXIS annotation on kind
contracts. Descriptive only: no hash, no validation, no executor reads it.

    POSITIVE   ca_density_v0 declares an axis for every parameter, printed
               by `viv.cli kinds`; axis_of() answers from the contract
    NEGATIVE   an unannotated kind answers UNCLASSIFIED for every parameter
               (a statement, never a default); the spec hash of a payload
               is unchanged by the annotation's presence
    CHEAT      an axis naming a non-parameter, or an unknown axis word, is
               refused at registration (the registry cannot carry a lie)
"""
from __future__ import annotations

import dataclasses

import pytest

from viv import kinds as _kinds
from viv import spec as _spec


def test_positive_ca_density_every_parameter_has_an_axis():
    k = _kinds.get("ca_density_v0")
    assert set(k.axes) == set(k.params)
    assert k.axis_of("rule_hex") == "mechanism"
    assert k.axis_of("transform") == "intervention"
    assert {k.axis_of(p) for p in ("radius", "n_cells", "steps")} == {"world"}
    assert {k.axis_of(p) for p in ("ic_density_set", "n_ic", "success_criterion")} == {"pressure"}


def test_positive_the_cli_prints_the_axes(capsys):
    from viv import cli as _cli
    _cli.cmd_kinds(None, None)
    out = capsys.readouterr().out
    assert "axes    ic_density_set=pressure" in out
    assert "rule_hex=mechanism" in out


def test_negative_unannotated_kinds_say_unclassified():
    k = _kinds.get("random_walk_v0")
    assert k.axes == {}
    assert k.axis_of("steps") == _kinds.UNCLASSIFIED


def test_negative_the_annotation_changes_no_hash():
    from tests.test_wp0f_fixtures import FIXTURES, _spec_for
    kind, payload, seed, _ = next(f for f in FIXTURES if f[0] == "ca_density_v0")
    spec = _spec_for(kind, payload, seed)
    h = _spec.spec_hash(spec)
    k = _kinds.get(kind)
    bare = dataclasses.replace(k, axes={})
    assert _spec.spec_hash(spec) == h            # the hash never read the kind
    assert bare.check(dict(payload)) == k.check(dict(payload)) == []


def test_cheat_an_axis_on_a_non_parameter_is_refused():
    k = _kinds.get("random_walk_v0")
    with pytest.raises(ValueError) as exc:
        dataclasses.replace(k, axes={"nonesuch": "world"})
    assert "non-parameters" in str(exc.value)


def test_cheat_an_unknown_axis_word_is_refused():
    k = _kinds.get("random_walk_v0")
    with pytest.raises(ValueError) as exc:
        dataclasses.replace(k, axes={"steps": "vibe"})
    assert "unknown axis" in str(exc.value)
