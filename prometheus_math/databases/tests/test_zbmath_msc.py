"""Tests for the MSC2020 hierarchy embedded in pm.databases.zbmath.

Project #48 (techne backlog) — full leaf-code expansion. Source of truth
is the AMS-published CSV at https://msc2020.org/MSC_2020.csv (snapshot
2026-04-25). This module verifies the four math-tdd categories
(authority / property / edge / composition) for the new public API:

    msc_codes(level)
    msc_descriptions(level)
    msc_lookup(code)
    msc_subtree(parent_code)
    msc_path(code)
    msc_search(query, max_results)

Authority references:
  - AMS MSC2020, https://mathscinet.ams.org/msnhtml/msc2020.pdf
  - AMS / zbMATH joint CSV, https://msc2020.org/MSC_2020.csv
  - zbMATH classification browser, https://zbmath.org/classification/

Note on top-level count: the published MSC2020 has 63 top-level subjects
(00, 01, 03, 05, 06, 08, 11..20, 22, 26, 28, 30..35 less 36, 37, 39..49
less 48, 51..58 less 56, 59, 60, 62, 65, 68, 70, 74, 76, 78, 80..86 less
84, 87..89, 90..94, 97). The numeric range nominally suggests 64 but
several positions are unallocated; this test asserts the exact 63.
"""
from __future__ import annotations

import re
import time

import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math.databases import zbmath as zb


# ===========================================================================
# Authority tests (≥3) — values cross-checked against the AMS MSC2020 spec.
# ===========================================================================


def test_authority_11g05_elliptic_curves_over_global_fields():
    """MSC 11G05 = "Elliptic curves over global fields".

    Reference: AMS MSC2020 Section 11G "Arithmetic algebraic geometry
    (Diophantine geometry)", entry 11G05. Cross-checked against
    https://msc2020.org/MSC_2020.csv (row "11G05" --
    "Elliptic curves over global fields [See also 14H52]"; the bracketed
    cross-reference is stripped for the canonical description).
    """
    info = zb.msc_lookup("11G05")
    assert info["code"] == "11G05"
    assert info["level"] == "leaf"
    assert info["description"] == "Elliptic curves over global fields"


def test_authority_11_top_level_is_number_theory():
    """MSC top-level "11" = "Number theory".

    Reference: AMS MSC2020, top-level list. CSV row "11-XX" -> "Number theory".
    """
    info = zb.msc_lookup("11")
    assert info["code"] == "11"
    assert info["level"] == "top"
    assert info["description"] == "Number theory"


def test_authority_top_level_count_matches_msc2020_spec():
    """MSC2020 has exactly 63 top-level subjects.

    Reference: AMS MSC2020 published table; 64 numeric slots are reserved
    in the 00..97 range but only 63 are allocated as of the 2020 revision.
    Cross-checked against the row-shape "NN-XX" in
    https://msc2020.org/MSC_2020.csv (63 such rows).
    """
    tops = zb.msc_codes(level="top")
    assert len(tops) == 63, f"expected 63 top-level MSC subjects, got {len(tops)}"


def test_authority_total_leaf_codes_meets_lower_bound():
    """MSC2020 has ~6000 leaf codes; our embedded snapshot covers >=5500.

    Reference: AMS MSC2020 CSV (https://msc2020.org/MSC_2020.csv) has
    6006 5-character codes (5503 of shape NNAdd plus 503 of shape NN-dd).
    """
    leaves = zb.msc_codes(level="leaf")
    assert len(leaves) >= 5500, f"expected >=5500 leaves, got {len(leaves)}"


def test_authority_00a35_methodology_of_mathematics():
    """MSC 00A35 = "Methodology of mathematics".

    Reference: AMS MSC2020 Section 00A "General and miscellaneous specific
    topics", entry 00A35.
    """
    info = zb.msc_lookup("00A35")
    assert info["code"] == "00A35"
    assert info["level"] == "leaf"
    assert info["description"] == "Methodology of mathematics"


def test_authority_subject_11g_arithmetic_algebraic_geometry():
    """MSC 11G = "Arithmetic algebraic geometry (Diophantine geometry)".

    Reference: AMS MSC2020 row "11Gxx".
    """
    info = zb.msc_lookup("11G")
    assert info["code"] == "11G"
    assert info["level"] == "subject"
    assert "Arithmetic algebraic geometry" in info["description"]


# ===========================================================================
# Property tests (≥3) — invariants over many inputs.
# ===========================================================================


def test_property_leaf_codes_are_5_chars():
    """Every leaf code is exactly 5 characters wide.

    Two valid leaf shapes coexist: NNAdd (e.g. "11G05") and NN-dd
    (e.g. "00-01"). Both are 5 characters.
    """
    leaves = zb.msc_codes(level="leaf")
    bad = [c for c in leaves if len(c) != 5]
    assert not bad, f"non-5-char leaf codes: {bad[:5]}"


def test_property_subject_codes_are_3_chars():
    """Every subject code is exactly 3 characters wide (NNA).

    Reference shape: NN<letter>, e.g. "11G", "05A".
    """
    subjects = zb.msc_codes(level="subject")
    bad = [c for c in subjects if len(c) != 3 or not re.match(r"^\d\d[A-Z]$", c)]
    assert not bad, f"malformed subject codes: {bad[:5]}"


def test_property_top_codes_are_2_chars():
    """Every top-level code is exactly 2 digits wide."""
    tops = zb.msc_codes(level="top")
    bad = [c for c in tops if len(c) != 2 or not c.isdigit()]
    assert not bad, f"malformed top codes: {bad[:5]}"


def test_property_all_descriptions_non_empty_strings():
    """For every code at every level, the description is a non-empty str."""
    for level in ("top", "subject", "leaf"):
        d = zb.msc_descriptions(level=level)
        assert isinstance(d, dict) and d
        bad = [k for k, v in d.items() if not (isinstance(v, str) and v.strip())]
        assert not bad, f"empty descriptions at level={level}: {bad[:3]}"


@given(
    code=st.sampled_from(["11G05", "00A35", "14H52", "60J05", "11-01"]),
    style=st.sampled_from(["upper", "lower", "padded", "mixed"]),
)
@settings(max_examples=40, deadline=None)
def test_property_lookup_is_case_and_whitespace_insensitive(code, style):
    """msc_lookup tolerates case and surrounding whitespace.

    Property: lookup(code) == lookup(transformed(code)) for any of the
    cosmetic transformations a user might apply.
    """
    canonical = zb.msc_lookup(code)
    if style == "upper":
        probe = code.upper()
    elif style == "lower":
        probe = code.lower()
    elif style == "padded":
        probe = f"  {code}  "
    else:
        probe = f" {code.lower()} "
    other = zb.msc_lookup(probe)
    assert other["code"] == canonical["code"]
    assert other["description"] == canonical["description"]


def test_property_every_leaf_has_a_known_top_parent():
    """Every leaf code's two-digit prefix corresponds to an existing top.

    Composition-style invariant: the parent of every leaf is in TOP.
    """
    tops = set(zb.msc_codes(level="top"))
    leaves = zb.msc_codes(level="leaf")
    bad = [c for c in leaves if c[:2] not in tops]
    assert not bad, f"orphaned leaves: {bad[:5]}"


# ===========================================================================
# Edge-case tests (≥3).
# ===========================================================================


def test_edge_lookup_unknown_code_raises_keyerror():
    """Unknown codes raise KeyError with an informative message."""
    with pytest.raises(KeyError) as exc:
        zb.msc_lookup("99Z99")
    assert "99Z99" in str(exc.value) or "unknown" in str(exc.value).lower()


def test_edge_lookup_empty_string_raises_valueerror():
    """Empty / whitespace-only input raises ValueError, not KeyError."""
    with pytest.raises(ValueError):
        zb.msc_lookup("")
    with pytest.raises(ValueError):
        zb.msc_lookup("   ")


def test_edge_subtree_of_nonexistent_returns_empty():
    """Asking for the subtree of a non-existent code yields []."""
    assert zb.msc_subtree("99") == []
    assert zb.msc_subtree("99Z") == []


def test_edge_search_empty_query_raises():
    """Empty / whitespace-only query raises ValueError (don't return everything)."""
    with pytest.raises(ValueError):
        zb.msc_search("")
    with pytest.raises(ValueError):
        zb.msc_search("   ")


def test_edge_unknown_level_raises_valueerror():
    """level='unknown' raises ValueError listing the valid choices."""
    with pytest.raises(ValueError) as exc:
        zb.msc_codes(level="unknown")
    msg = str(exc.value).lower()
    assert "level" in msg
    for ok in ("leaf", "subject", "top"):
        assert ok in msg


def test_edge_lookup_unallocated_subject_raises_keyerror():
    """Inputs that look like codes but aren't (e.g. '11W99') raise KeyError.

    11W is not an allocated MSC2020 subject letter (11A, 11B, 11C, 11D,
    11E, 11F, 11G, 11H, 11J, 11K, 11L, 11M, 11N, 11P, 11R, 11S, 11T,
    11U, 11Y, 11Z are the allocated ones).
    """
    with pytest.raises(KeyError):
        zb.msc_lookup("11W99")


# ===========================================================================
# Composition tests (≥2) — chain APIs against each other.
# ===========================================================================


def test_composition_path_last_element_matches_lookup():
    """msc_path(c)[-1] is the (code, description) pair msc_lookup returns.

    Composition: msc_path is the unrolled ancestor chain ending at the
    looked-up node, so the last element must be self-consistent with
    msc_lookup. This catches off-by-one and stale-cache bugs.
    """
    for code in ("11G05", "00A35", "14H52", "60J05", "11-01"):
        info = zb.msc_lookup(code)
        path = zb.msc_path(code)
        last_code, last_desc = path[-1]
        assert last_code == info["code"]
        assert last_desc == info["description"]
    # And the path length matches the level depth.
    assert len(zb.msc_path("11")) == 1
    assert len(zb.msc_path("11G")) == 2
    assert len(zb.msc_path("11G05")) == 3


def test_composition_search_finds_known_code():
    """msc_search('elliptic curves') surfaces 11G05.

    Composition: msc_search reads from the same description corpus
    msc_lookup operates on, so they must agree.
    """
    hits = zb.msc_search("elliptic curves", max_results=50)
    assert isinstance(hits, list) and hits
    codes = [h["code"] for h in hits]
    assert "11G05" in codes, f"11G05 missing from elliptic-curves search: {codes[:10]}"
    # And every hit's description actually contains the substring.
    for h in hits:
        assert "elliptic curve" in h["description"].lower()


def test_composition_every_top_has_at_least_one_leaf():
    """Composition: every top-level subject has at least one leaf descendant.

    Cross-checks subtree() against msc_codes('top') -> there are no
    orphan top-level subjects in MSC2020.
    """
    tops = zb.msc_codes(level="top")
    for t in tops:
        sub = zb.msc_subtree(t)
        assert sub, f"top-level {t!r} has no leaves in subtree"
        # And every returned leaf actually starts with `t`.
        bad = [c for c in sub if not c.startswith(t)]
        assert not bad, f"subtree({t}) leaked unrelated codes: {bad[:3]}"


def test_composition_subtree_of_subject_is_subset_of_top_subtree():
    """Composition: leaves under '11G' are a subset of leaves under '11'."""
    g = set(zb.msc_subtree("11G"))
    eleven = set(zb.msc_subtree("11"))
    assert g, "expected non-empty subtree for 11G"
    assert g.issubset(eleven), f"11G subtree leaks outside 11: {g - eleven}"


# ===========================================================================
# Performance gate
# ===========================================================================


def test_msc_search_runs_under_one_second():
    """Substring search over the full ~6000-leaf corpus must finish in <1s."""
    t0 = time.perf_counter()
    hits = zb.msc_search("group", max_results=50)
    elapsed = time.perf_counter() - t0
    assert hits  # sanity
    assert elapsed < 1.0, f"msc_search took {elapsed:.2f}s, expected <1s"
