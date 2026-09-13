"""Instrument hygiene (batch 10 P2).

harvest.py carried TWO definitions each of acquire, _shell, _clip, _expect_ok and verify, with the
later ones silently winning. Nothing failed loudly; the shadowed `verify` simply reported less
detail than the one `verify_all` was actually using, and the shadowed `acquire` predated submodule
preservation entirely. A duplicate top-level definition in this instrument is a silent correctness
hazard, so it is now a test failure.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

FOSSIL_PKG = pathlib.Path(__file__).resolve().parents[1] / "fossils"
MODULES = sorted(p for p in FOSSIL_PKG.rglob("*.py") if "__pycache__" not in p.parts)


def _top_level_names(path: pathlib.Path):
    """(name -> [lineno]) for every top-level def/class in the module."""
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    out: dict[str, list[int]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.setdefault(node.name, []).append(node.lineno)
    return out


@pytest.mark.parametrize("path", MODULES, ids=lambda p: str(p.name))
def test_no_shadowed_top_level_definitions(path):
    """A later def silently replaces an earlier one; Python will not warn. This will."""
    dupes = {n: ls for n, ls in _top_level_names(path).items() if len(ls) > 1}
    assert not dupes, "%s has shadowed top-level definitions: %s" % (path.name, dupes)


def test_the_detector_actually_detects(tmp_path):
    """Control: the check must FAIL on a module that really does shadow a definition."""
    bad = tmp_path / "shadowed.py"
    bad.write_text("def f():\n    return 1\n\n\ndef f():\n    return 2\n", encoding="utf-8")
    dupes = {n: ls for n, ls in _top_level_names(bad).items() if len(ls) > 1}
    assert dupes == {"f": [1, 5]}, dupes

    good = tmp_path / "clean.py"
    good.write_text("def f():\n    return 1\n\n\ndef g():\n    return 2\n", encoding="utf-8")
    assert not {n: ls for n, ls in _top_level_names(good).items() if len(ls) > 1}


def test_harvest_keeps_the_authoritative_implementations():
    """The survivors must be the ones P2 chose on behavioural grounds, not whichever came last."""
    import inspect
    from techne.fossils import harvest

    # acquire: the submodule/preservation-aware implementation
    src_acquire = inspect.getsource(harvest.acquire)
    assert "init_submodules" in src_acquire
    assert 'rec["preservation"]' in src_acquire

    # verify: the drift-based one, which reports added/removed/modified rather than a bare hash
    src_verify = inspect.getsource(harvest.verify)
    assert "drift(" in src_verify
    assert "modified" in src_verify
