"""T3 (wave 0) — cross-version resolution policy tests.

Codifies the five-rule policy from
harmonia/memory/symbols/protocols/cross_version_resolution.md as
executable assertions. The mechanism ships under T1
(agora/symbols/manifest.py); these tests validate the policy as
deployed, including the T3-added session-level cross-version tracker
in resolve.py.

Uses live Redis but only READ operations (no symbol state mutation).
"""
import warnings

import pytest

from agora.symbols import (
    parse_session_manifest, resolve_with_manifest,
    expand_references, contract_references, find_conflicts,
    manifest_frontmatter, round_trip_ok,
    CrossVersionConflict, reset_cross_version_tracker,
    resolve,
)


# ---------- Rule 1 (explicit wins over implicit) ----------

def test_rule_1_explicit_wins_in_resolve():
    """resolve_with_manifest ignores manifest when @v<N> is explicit."""
    manifest = {'NULL_BSWCD': 2}
    # Explicit @v1 is honored regardless of manifest's v2 binding
    explicit = resolve_with_manifest('NULL_BSWCD@v1', manifest)
    bare = resolve_with_manifest('NULL_BSWCD', manifest)
    assert explicit is not None and bare is not None
    assert explicit['version'] == 1
    assert bare['version'] == 2


# ---------- Rule 2 (manifest binds bare names) ----------

def test_rule_2_bare_name_binds_to_manifest():
    manifest = {'NULL_BSWCD': 1}
    data = resolve_with_manifest('NULL_BSWCD', manifest)
    assert data is not None
    assert data['version'] == 1


def test_rule_2_bare_name_no_manifest_entry_falls_through():
    """Bare name missing from manifest uses resolve(latest) with warning."""
    manifest = {}
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        data = resolve_with_manifest('NULL_BSWCD', manifest)
    assert data is not None
    # Latest is v2 currently; caller still got a result
    assert data['version'] >= 1
    # resolve() emits a UserWarning for missing version
    assert any(
        'without version' in str(warning.message)
        for warning in w
    )


# ---------- Rule 3 (conflicts detected, not repaired) ----------

def test_rule_3_expand_warns_on_conflict():
    """expand_references warns when inline @v disagrees with manifest."""
    manifest = {'NULL_BSWCD': 2}
    text = 'Old finding used NULL_BSWCD@v1 but new code uses NULL_BSWCD.'
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        out = expand_references(text, manifest)
    conflicts = [x for x in w if issubclass(x.category, CrossVersionConflict)]
    assert len(conflicts) == 1
    # Bare NULL_BSWCD -> NULL_BSWCD@v2 (manifest wins for bare)
    assert 'NULL_BSWCD@v2' in out
    # Inline NULL_BSWCD@v1 preserved
    assert 'NULL_BSWCD@v1' in out


def test_rule_3_contract_preserves_explicit_mismatch():
    """contract_references preserves @v<M> when M != manifest[N]."""
    manifest = {'NULL_BSWCD': 2}
    text = 'Older audit cites NULL_BSWCD@v1 (kept as-is).'
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        out = contract_references(text, manifest)
    # Explicit @v1 kept
    assert 'NULL_BSWCD@v1' in out
    # Warning surfaced
    assert any(issubclass(x.category, CrossVersionConflict) for x in w)


def test_rule_3_find_conflicts_returns_list_without_warning():
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    text = 'NULL_BSWCD@v1 and PATTERN_30@v1 appear; other NULL_BSWCD bare.'
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        conflicts = find_conflicts(text, manifest)
    # find_conflicts must NOT emit warnings (contrast with expand_references)
    assert not any(issubclass(x.category, CrossVersionConflict) for x in w)
    # Exactly one conflict (PATTERN_30@v1 matches manifest, no conflict)
    assert len(conflicts) == 1
    assert conflicts[0]['name'] == 'NULL_BSWCD'
    assert conflicts[0]['inline_version'] == 1
    assert conflicts[0]['manifest_version'] == 2


# ---------- Rule 4 (session-level multi-version is legal) ----------

def test_rule_4_multi_version_legal_but_visible():
    """resolve() at two distinct versions for same name emits warning on
    the second call (visibility only; multi-version is allowed)."""
    reset_cross_version_tracker()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        # First resolve — no conflict warning
        d1 = resolve('NULL_BSWCD', version=1)
        no_conflict_yet = [
            x for x in w if issubclass(x.category, CrossVersionConflict)
        ]
        assert len(no_conflict_yet) == 0
        # Second resolve at different version — fires CrossVersionConflict
        d2 = resolve('NULL_BSWCD', version=2)
    assert d1 is not None and d2 is not None
    conflicts = [x for x in w if issubclass(x.category, CrossVersionConflict)]
    assert len(conflicts) == 1
    assert 'v1' in str(conflicts[0].message) or 'v2' in str(conflicts[0].message)


def test_rule_4_same_version_twice_no_warning():
    """Resolving the same (name, version) twice does not spam warnings."""
    reset_cross_version_tracker()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        resolve('NULL_BSWCD', version=2)
        resolve('NULL_BSWCD', version=2)
        resolve('NULL_BSWCD', version=2)
    conflicts = [x for x in w if issubclass(x.category, CrossVersionConflict)]
    assert len(conflicts) == 0


# ---------- manifest round-trip ----------

def test_manifest_round_trip_expansion_is_stable():
    """Canonical session form is BARE-alias prose; expand+contract must round-trip."""
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    canonical_bare = 'Apply NULL_BSWCD and PATTERN_30 to F043.'
    ok, diag = round_trip_ok(canonical_bare, manifest)
    assert ok, diag


def test_manifest_parse_all_forms():
    # Block-style mapping
    m1 = parse_session_manifest('---\nuses:\n  NULL_BSWCD: 2\n  PATTERN_30: 1\n---\n')
    assert m1 == {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    # List-of-references
    m2 = parse_session_manifest(['NULL_BSWCD@v2', 'PATTERN_30@v1'])
    assert m2 == {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    # Dict
    m3 = parse_session_manifest({'NULL_BSWCD': 2, 'PATTERN_30': 'v1'})
    assert m3 == {'NULL_BSWCD': 2, 'PATTERN_30': 1}


def test_manifest_frontmatter_canonical_output():
    manifest = {'PATTERN_30': 1, 'NULL_BSWCD': 2}
    out = manifest_frontmatter(manifest)
    # Alphabetical order
    assert out.index('NULL_BSWCD') < out.index('PATTERN_30')


# ---------- Worked test case from cross_version_resolution.md §Worked test case ----------

def test_worked_case_stale_v1_alongside_fresh_v2():
    """The canonical scenario: session cites old F043 retraction using
    NULL_BSWCD@v1 while fresh sweep code uses NULL_BSWCD (bound to v2
    by manifest). Expected: v1 reference preserved; bare rewritten to v2;
    exactly one conflict warning."""
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    body = (
        'Retrospective: F043 was retracted on 2026-04-19 when NULL_BSWCD@v1 '
        'failed to break the algebraic coupling (PATTERN_30 Level-3). '
        'The current sweep under NULL_BSWCD catches Level-3 at ingest; '
        'PATTERN_30 sweeps run on every promotion.'
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        expanded = expand_references(body, manifest)
    # Exactly ONE conflict warning (the NULL_BSWCD@v1 citation)
    conflicts = [x for x in w if issubclass(x.category, CrossVersionConflict)]
    assert len(conflicts) == 1, (
        f'expected 1 conflict for NULL_BSWCD@v1 vs manifest v2, '
        f'got {len(conflicts)}: {[str(c.message) for c in conflicts]}'
    )
    # Explicit v1 preserved
    assert 'NULL_BSWCD@v1' in expanded
    # Bare NULL_BSWCD (the one after "under") rewritten to v2
    # PATTERN_30 bare also rewritten to v1
    assert 'NULL_BSWCD@v2' in expanded
    assert 'PATTERN_30@v1' in expanded
    # No bare NULL_BSWCD or PATTERN_30 left unversioned
    import re
    assert not re.search(r'\bNULL_BSWCD\b(?!@v)', expanded)
    assert not re.search(r'\bPATTERN_30\b(?!@v)', expanded)


# ---------- Rule 5 (no auto-coerce, documented behavior) ----------

def test_rule_5_no_automatic_coercion_between_versions():
    """resolve() returns exactly the version requested; the symbol
    registry does not wrap, cast, or compose values across versions."""
    d1 = resolve('NULL_BSWCD', version=1)
    d2 = resolve('NULL_BSWCD', version=2)
    assert d1 is not None and d2 is not None
    assert d1['version'] == 1
    assert d2['version'] == 2
    # Versions differ (meaning the registry didn't silently return the same thing)
    assert d1['version_timestamp'] != d2['version_timestamp']
