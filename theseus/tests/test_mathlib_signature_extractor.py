"""Tests for theseus.scripts.mathlib_signature_extractor."""
from __future__ import annotations

import json
from pathlib import Path

from theseus.scripts.mathlib_signature_extractor import (
    DECL_PATTERNS,
    _extract_one,
    extract_all,
)


def test_decl_patterns_match_theorem(tmp_path):
    """Theorem signature extraction."""
    f = tmp_path / "Test.lean"
    f.write_text(
        "import Mathlib.Foo\n"
        "theorem my_thm (n : ℕ) : n + 0 = n := by simp\n",
        encoding="utf-8",
    )
    sigs = _extract_one(f)
    assert len(sigs) >= 1
    s = sigs[0]
    assert s["kind"] == "theorem"
    assert s["name"] == "my_thm"
    assert "n + 0 = n" in s["signature"]


def test_decl_patterns_match_lemma(tmp_path):
    f = tmp_path / "Test.lean"
    f.write_text(
        "lemma foo (a b : ℤ) : a + b = b + a := by ring\n",
        encoding="utf-8",
    )
    sigs = _extract_one(f)
    assert any(s["kind"] == "lemma" and s["name"] == "foo" for s in sigs)


def test_decl_patterns_match_def(tmp_path):
    f = tmp_path / "Test.lean"
    f.write_text(
        "def my_def (n : ℕ) : ℕ := n + 1\n",
        encoding="utf-8",
    )
    sigs = _extract_one(f)
    assert any(s["kind"] == "def" and s["name"] == "my_def" for s in sigs)


def test_extract_one_dedupes_by_name(tmp_path):
    f = tmp_path / "Test.lean"
    f.write_text(
        "theorem foo (n : ℕ) (h : n > 0) : True := by trivial\n"
        "theorem foo (n : ℕ) (h : n > 0) : True := by trivial\n",
        encoding="utf-8",
    )
    sigs = _extract_one(f)
    # Same name should dedup within one file
    assert len([s for s in sigs if s["name"] == "foo"]) == 1


def test_extract_one_skips_too_short(tmp_path):
    f = tmp_path / "Test.lean"
    f.write_text(
        "theorem x : :=\n",  # signature ":" is too short (< 10 chars)
        encoding="utf-8",
    )
    sigs = _extract_one(f)
    # May be 0 or 1 depending on whether regex captures the colon
    # but anything kept must be ≥ 10 chars
    for s in sigs:
        assert len(s["signature"]) >= 10


def test_extract_all_walks_subdirs(tmp_path, monkeypatch):
    """End-to-end: extract_all walks target subdirs and writes JSONL."""
    from theseus.scripts import mathlib_signature_extractor as mse

    # Build a fake mathlib structure
    nt = tmp_path / "NumberTheory"
    nt.mkdir()
    (nt / "Foo.lean").write_text(
        "theorem nt_thm (p : ℕ) : Nat.Prime p → p ≥ 2 := by sorry\n",
        encoding="utf-8",
    )
    # Point MATHLIB_DIR to our tmp fixture so relative_to works
    monkeypatch.setattr(mse, "MATHLIB_DIR", tmp_path)

    output_path = tmp_path / "out.jsonl"
    summary = extract_all(
        mathlib_dir=tmp_path,
        output_path=output_path,
        max_per_file=50,
    )
    assert summary["n_files"] >= 1
    assert summary["n_signatures"] >= 1
    # NumberTheory should be in by_domain
    assert "NumberTheory" in summary["by_domain"]

    # Output file exists and has valid JSONL
    lines = output_path.read_text(encoding="utf-8").strip().split("\n")
    parsed = [json.loads(l) for l in lines if l]
    assert all("name" in s for s in parsed)
    assert all("signature" in s for s in parsed)
    assert all("source_path" in s for s in parsed)


def test_extract_all_respects_max_total(tmp_path):
    """max_total caps the total signatures extracted."""
    nt = tmp_path / "NumberTheory"
    nt.mkdir()
    # 3 theorems
    (nt / "A.lean").write_text(
        "theorem a1 (n : ℕ) : n = n := by rfl\n"
        "theorem a2 (n : ℕ) : n = n := by rfl\n"
        "theorem a3 (n : ℕ) : n = n := by rfl\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "out.jsonl"
    summary = extract_all(
        mathlib_dir=tmp_path,
        output_path=output_path,
        max_total=2,
    )
    assert summary["n_signatures"] == 2
    assert summary.get("stopped") == "max_total"


def test_extract_all_missing_mathlib_returns_error(tmp_path):
    summary = extract_all(
        mathlib_dir=tmp_path / "nonexistent",
        output_path=tmp_path / "out.jsonl",
    )
    assert "error" in summary
    assert summary["n_signatures"] == 0
