"""R36 fixtures (Amendment 3): the four invariances the amendment names, plus the refusals."""
from __future__ import annotations

import json

import pytest

from techne.fossils import world_manifest as wm

BASE = {"name": "w", "class": "native_python", "architecture": "x86_64",
        "interpreter": {"implementation": "CPython", "version": "3.11.9"},
        "packages": [{"name": "numpy", "version": "1.26.4"}, {"name": "SciPy", "version": "1.16.3"}, {"name": "Z3_Solver", "version": "5.1.0.0"}],
        "toolchains": [{"class": "compiler", "name": "gcc", "version": "12.2.0"}, {"class": "assembler", "name": "as", "version": "2.40"}],
        "env": [{"name": "LANG", "value": "C"}, {"name": "A", "value": "1"}]}


def test_different_input_ordering_same_id():
    a = json.loads(json.dumps(BASE))
    b = json.loads(json.dumps(BASE))
    b["packages"].reverse(); b["toolchains"].reverse(); b["env"].reverse()
    assert wm.world_id(a) == wm.world_id(b)


def test_crlf_vs_lf_serialization_same_id():
    lf = wm.canonical_bytes(BASE).decode("utf-8")
    crlf = lf.replace("\n", "\r\n")
    assert wm.world_id(wm.parse_manifest_text(crlf)) == wm.world_id(wm.parse_manifest_text(lf)) == wm.world_id(BASE)
    assert wm.canonical_bytes(BASE).endswith(b"\n") and not wm.canonical_bytes(BASE).endswith(b"\n\n")
    assert b"\r" not in wm.canonical_bytes(BASE)


def test_different_image_witness_same_world_id():
    """The witness is not in the manifest, so it cannot move the id; and putting it in is refused."""
    a = wm.world_id(BASE)
    with pytest.raises(ValueError):
        wm.world_id({**BASE, "image_digest": "sha256:abc"})
    with pytest.raises(ValueError):
        wm.world_id({**BASE, "host": "GANDALF"})
    assert wm.world_id(BASE) == a


def test_different_package_version_different_id():
    b = json.loads(json.dumps(BASE))
    b["packages"][0]["version"] = "1.26.5"
    assert wm.world_id(BASE) != wm.world_id(b)
    c = json.loads(json.dumps(BASE))
    c["packages"].append({"name": "extra", "version": "0.1"})
    assert wm.world_id(BASE) != wm.world_id(c)


def test_name_normalization_and_version_strings():
    d = wm.canonical_dict(BASE)
    names = [p["name"] for p in d["packages"]]
    assert names == sorted(names) and "scipy" in names and "z3-solver" in names
    assert all(isinstance(p["version"], str) for p in d["packages"])
    e = json.loads(json.dumps(BASE)); e["packages"][0]["version"] = 1.26
    assert wm.world_id(e) == wm.world_id({**BASE, "packages": [{"name": "numpy", "version": "1.26"}] + BASE["packages"][1:]})


def test_this_interpreter_world_has_no_ephemeral_keys_and_is_stable():
    w = wm.this_interpreter_world("test-world")
    assert wm.world_id(w) == wm.world_id(w)
    assert not (set(w) & wm.EPHEMERAL_KEYS)
    wit = wm.runtime_witness_for_this_interpreter()
    assert wit["pip_freeze_sha256"] and "n_distributions" in wit
