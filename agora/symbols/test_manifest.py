"""Tests for session-manifest parser (T1, wave 0).

Pure-python tests for parse_session_manifest / expand_references /
contract_references / find_conflicts / round_trip_ok / manifest_frontmatter.
No live Redis needed for these.

validate_reference_string with manifest is tested against a monkey-patched
all_symbols() to avoid needing Redis.

Run: python agora/symbols/test_manifest.py
"""
from __future__ import annotations

import io
import sys
import warnings
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agora.symbols.manifest import (
    parse_session_manifest,
    expand_references,
    contract_references,
    find_conflicts,
    round_trip_ok,
    manifest_frontmatter,
    CrossVersionConflict,
)


# ---------------------------------------------------------------------------
# parse_session_manifest
# ---------------------------------------------------------------------------

def test_parse_from_dict_form():
    fm_text = "---\nuses:\n  NULL_BSWCD: 2\n  PATTERN_30: 1\n  SHADOWS_ON_WALL: 1\n---\nbody here\n"
    m = parse_session_manifest(fm_text)
    assert m == {'NULL_BSWCD': 2, 'PATTERN_30': 1, 'SHADOWS_ON_WALL': 1}, m
    print("  [ok] parse from dict-block form")


def test_parse_from_list_form():
    fm_text = "---\nuses: [NULL_BSWCD@v2, PATTERN_30@v1]\n---\nbody\n"
    m = parse_session_manifest(fm_text)
    assert m == {'NULL_BSWCD': 2, 'PATTERN_30': 1}, m
    print("  [ok] parse from list-of-refs form")


def test_parse_direct_dict():
    m = parse_session_manifest({'NULL_BSWCD': 2, 'PATTERN_30': 'v1', 'FOO': '@v3'})
    assert m == {'NULL_BSWCD': 2, 'PATTERN_30': 1, 'FOO': 3}, m
    print("  [ok] parse direct dict with mixed int/str/prefixed forms")


def test_parse_direct_list():
    m = parse_session_manifest(['NULL_BSWCD@v2', 'PATTERN_30@v1'])
    assert m == {'NULL_BSWCD': 2, 'PATTERN_30': 1}, m
    print("  [ok] parse direct list")


def test_parse_empty():
    assert parse_session_manifest("no frontmatter here") == {}
    assert parse_session_manifest("---\nfoo: bar\n---\n") == {}  # no `uses:`
    assert parse_session_manifest({}) == {}
    assert parse_session_manifest([]) == {}
    print("  [ok] parse empty / absent")


def test_parse_rejects_bad_version():
    try:
        parse_session_manifest({'NULL_BSWCD': 'v0'})
    except ValueError as e:
        assert 'must be >= 1' in str(e), e
        print("  [ok] rejects version 0")
        return
    raise AssertionError('expected ValueError on version 0')


def test_parse_rejects_bad_list_item():
    try:
        parse_session_manifest(['not a ref'])
    except ValueError as e:
        assert 'NAME@v<N>' in str(e), e
        print("  [ok] rejects malformed list item")
        return
    raise AssertionError('expected ValueError on bad list item')


# ---------------------------------------------------------------------------
# expand / contract round-trip
# ---------------------------------------------------------------------------

def test_expand_basic():
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    bare = "The NULL_BSWCD test on F043 showed a PATTERN_30 Level-3 coupling."
    out = expand_references(bare, manifest)
    assert 'NULL_BSWCD@v2' in out
    assert 'PATTERN_30@v1' in out
    assert 'F043' in out  # un-manifested, left bare
    print(f"  [ok] expand: {out!r}")


def test_expand_leaves_already_qualified_alone():
    manifest = {'NULL_BSWCD': 2}
    text = "Already-qualified NULL_BSWCD@v2 should stay as-is."
    out = expand_references(text, manifest)
    # Should have exactly one @v2, not v2@v2
    assert out.count('NULL_BSWCD@v2') == 1, out
    assert 'NULL_BSWCD@v2@v2' not in out
    print("  [ok] expand preserves already-qualified references")


def test_expand_does_not_eat_longer_identifier():
    # NULL_BSWCD_EXT is a different hypothetical symbol — must not be
    # rewritten to NULL_BSWCD@v2_EXT.
    manifest = {'NULL_BSWCD': 2}
    text = "NULL_BSWCD_EXT is different from NULL_BSWCD."
    out = expand_references(text, manifest)
    assert 'NULL_BSWCD_EXT' in out
    assert 'NULL_BSWCD@v2_EXT' not in out
    assert out.count('NULL_BSWCD@v2') == 1
    print(f"  [ok] expand doesn't truncate longer identifiers: {out!r}")


def test_contract_basic():
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    qualified = "The NULL_BSWCD@v2 test on F043 showed a PATTERN_30@v1 Level-3 coupling."
    out = contract_references(qualified, manifest)
    assert 'NULL_BSWCD@v2' not in out
    assert 'PATTERN_30@v1' not in out
    assert 'NULL_BSWCD' in out
    assert 'PATTERN_30' in out
    print(f"  [ok] contract: {out!r}")


def test_contract_preserves_override():
    manifest = {'NULL_BSWCD': 2}
    # Inline @v1 disagrees with manifest — must be preserved
    text = "Historical note: NULL_BSWCD@v1 was the original, now NULL_BSWCD holds at v2."
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        out = contract_references(text, manifest)
        assert 'NULL_BSWCD@v1' in out, out
        assert any(issubclass(x.category, CrossVersionConflict) for x in w), w
    print("  [ok] contract preserves inline override + warns")


def test_round_trip_stable():
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    # Canonical form = bare-with-manifest
    canonical = "Run NULL_BSWCD on F011; PATTERN_30 fires at Level-3 on F043."
    ok, diag = round_trip_ok(canonical, manifest)
    assert ok, diag
    print(f"  [ok] round-trip: {diag}")


def test_round_trip_with_unknown_names_stable():
    manifest = {'NULL_BSWCD': 2}
    canonical = "NULL_BSWCD on F011 flags an F043 issue; UNKNOWN_SYMBOL@v3 bypasses."
    ok, diag = round_trip_ok(canonical, manifest)
    assert ok, diag
    print(f"  [ok] round-trip with unknown symbols: {diag}")


# ---------------------------------------------------------------------------
# find_conflicts
# ---------------------------------------------------------------------------

def test_find_conflicts_hits():
    manifest = {'NULL_BSWCD': 2}
    text = "v2 in prose, but NULL_BSWCD@v1 inline and NULL_BSWCD@v2 inline."
    conflicts = find_conflicts(text, manifest)
    assert len(conflicts) == 1, conflicts
    assert conflicts[0]['name'] == 'NULL_BSWCD'
    assert conflicts[0]['inline_version'] == 1
    assert conflicts[0]['manifest_version'] == 2
    print(f"  [ok] find_conflicts: {conflicts}")


def test_find_conflicts_none():
    manifest = {'NULL_BSWCD': 2}
    text = "NULL_BSWCD@v2 matches the manifest."
    assert find_conflicts(text, manifest) == []
    print("  [ok] find_conflicts empty when aligned")


# ---------------------------------------------------------------------------
# manifest_frontmatter
# ---------------------------------------------------------------------------

def test_manifest_frontmatter_round_trip():
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1, 'SHADOWS_ON_WALL': 1}
    fm = manifest_frontmatter(manifest)
    # Re-parse the emitted form
    reparsed = parse_session_manifest(fm + 'body\n')
    assert reparsed == manifest, (fm, reparsed)
    print(f"  [ok] frontmatter emit → parse round-trip")


def test_manifest_frontmatter_sorted():
    manifest = {'ZETA': 1, 'ALPHA': 1}
    fm = manifest_frontmatter(manifest)
    # ALPHA should appear before ZETA
    assert fm.index('ALPHA') < fm.index('ZETA'), fm
    print("  [ok] frontmatter output is alpha-sorted for reproducibility")


# ---------------------------------------------------------------------------
# expand_references conflict warning
# ---------------------------------------------------------------------------

def test_expand_conflict_warns():
    manifest = {'NULL_BSWCD': 2}
    text = "A legacy sentence mentioning NULL_BSWCD@v1 inline."
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        expand_references(text, manifest)
        assert any(issubclass(x.category, CrossVersionConflict) for x in w), w
    print("  [ok] expand emits CrossVersionConflict on inline@v disagreement")


# ---------------------------------------------------------------------------
# validate_reference_string with manifest (no Redis needed via monkey-patch)
# ---------------------------------------------------------------------------

def test_validate_with_manifest_no_redis():
    # Monkey-patch _get_redis to return a fake client exposing only what
    # validate_reference_string needs: smembers('symbols:all') -> set of names.
    # The submodule `agora.symbols.resolve` is shadowed in the package
    # namespace by the same-named function (imported in __init__.py), so
    # we reach it through sys.modules to get the real module object.
    import sys as _sys
    resolve_mod = _sys.modules['agora.symbols.resolve']

    class _FakeRedis:
        def __init__(self, names):
            self._names = set(names)
        def smembers(self, key):
            if key == 'symbols:all':
                return self._names
            return set()

    original = resolve_mod._get_redis
    try:
        resolve_mod._get_redis = lambda: _FakeRedis({'NULL_BSWCD', 'PATTERN_30', 'F011'})
        # Without manifest: bare NULL_BSWCD is a violation
        text = "The NULL_BSWCD test PATTERN_30 triggered."
        violations = resolve_mod.validate_reference_string(text, strict=False)
        names_violated = {v['name'] for v in violations}
        assert 'NULL_BSWCD' in names_violated
        assert 'PATTERN_30' in names_violated
        # With manifest: NULL_BSWCD is declared, PATTERN_30 not
        manifest = {'NULL_BSWCD': 2}
        violations2 = resolve_mod.validate_reference_string(text, strict=False, manifest=manifest)
        names_violated2 = {v['name'] for v in violations2}
        assert 'NULL_BSWCD' not in names_violated2, names_violated2
        assert 'PATTERN_30' in names_violated2, names_violated2
        print(f"  [ok] validate_reference_string with manifest skips declared names")
    finally:
        resolve_mod._get_redis = original


# ---------------------------------------------------------------------------
# Integration: a realistic inter-agent message
# ---------------------------------------------------------------------------

def test_realistic_inter_agent_message():
    """The canonical real-world use: a session handoff message uses bare
    aliases under a manifest; the downstream parser reconstructs versions."""
    handoff = (
        "---\n"
        "uses:\n"
        "  NULL_BSWCD: 2\n"
        "  PATTERN_30: 1\n"
        "  SHADOWS_ON_WALL: 1\n"
        "---\n"
        "Session handoff 2026-04-22. Ran NULL_BSWCD on F013 under stratifier=rank; \n"
        "PATTERN_30 emitted BLOCK at Level-3 for F043 (algebraic coupling with BSD). \n"
        "Per SHADOWS_ON_WALL, single-lens claim — lens count = 1, verdict = shadow.\n"
        "Next: run NULL_BSWCD@v1 as a regression check for continuity (explicit override).\n"
    )
    manifest = parse_session_manifest(handoff)
    assert manifest == {'NULL_BSWCD': 2, 'PATTERN_30': 1, 'SHADOWS_ON_WALL': 1}

    # Strip frontmatter; get the body for reference-expansion
    body_start = handoff.index('---\n', 4) + 4
    body = handoff[body_start:]

    # Conflict-detect: the inline NULL_BSWCD@v1 is flagged against manifest NULL_BSWCD: 2
    conflicts = find_conflicts(body, manifest)
    assert len(conflicts) == 1, conflicts
    assert conflicts[0] == {
        'name': 'NULL_BSWCD',
        'inline_version': 1,
        'manifest_version': 2,
        'position': conflicts[0]['position'],  # don't pin exact pos
    }

    # expand_references turns bare refs into qualified form, warns on inline mismatch
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        expanded = expand_references(body, manifest)
        assert any(issubclass(x.category, CrossVersionConflict) for x in w)
        assert 'NULL_BSWCD@v2' in expanded
        assert 'PATTERN_30@v1' in expanded
        assert 'SHADOWS_ON_WALL@v1' in expanded
        # The explicit override should be preserved as NULL_BSWCD@v1
        assert 'NULL_BSWCD@v1' in expanded

    print(f"  [ok] realistic inter-agent round-trip + override preservation")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    test_parse_from_dict_form,
    test_parse_from_list_form,
    test_parse_direct_dict,
    test_parse_direct_list,
    test_parse_empty,
    test_parse_rejects_bad_version,
    test_parse_rejects_bad_list_item,
    test_expand_basic,
    test_expand_leaves_already_qualified_alone,
    test_expand_does_not_eat_longer_identifier,
    test_contract_basic,
    test_contract_preserves_override,
    test_round_trip_stable,
    test_round_trip_with_unknown_names_stable,
    test_find_conflicts_hits,
    test_find_conflicts_none,
    test_manifest_frontmatter_round_trip,
    test_manifest_frontmatter_sorted,
    test_expand_conflict_warns,
    test_validate_with_manifest_no_redis,
    test_realistic_inter_agent_message,
]


def main():
    print(f"[test_manifest] running {len(TESTS)} tests...")
    passed = 0
    failed = []
    for t in TESTS:
        try:
            print(f"[{t.__name__}]")
            t()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed.append((t.__name__, str(e)))
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            failed.append((t.__name__, f'{type(e).__name__}: {e}'))
    print()
    print(f"{passed}/{len(TESTS)} passed.")
    if failed:
        print("FAILED:")
        for name, err in failed:
            print(f"  - {name}: {err}")
        sys.exit(1)
    print("all green.")


if __name__ == '__main__':
    main()
