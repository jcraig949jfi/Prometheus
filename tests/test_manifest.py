"""T1 (wave 0) — session manifest schema tests.

Exercises parse_session_manifest across input shapes, expand/contract
round-trip symmetry, CROSS_VERSION_CONFLICT detection, the validator
integration path in validate_reference_string, and resolve_with_manifest
dispatch.

Uses NULL_BOOT + NULL_PLAIN as test-subject symbols (both promoted in
Redis with status=active). No Redis state is mutated by these tests;
everything here is text-layer behavior plus a read-only resolve check.
"""
import warnings

import pytest

from agora.symbols.manifest import (
    parse_session_manifest,
    expand_references,
    contract_references,
    find_conflicts,
    manifest_frontmatter,
    round_trip_ok,
    resolve_with_manifest,
    CrossVersionConflict,
)
from agora.symbols import validate_reference_string


# ----------------------------------------------------------------------
# parse_session_manifest
# ----------------------------------------------------------------------

def test_parse_from_mapping_dict():
    m = parse_session_manifest({'NULL_BSWCD': 2, 'PATTERN_30': 1})
    assert m == {'NULL_BSWCD': 2, 'PATTERN_30': 1}


def test_parse_from_list_of_references():
    m = parse_session_manifest(['NULL_BSWCD@v2', 'PATTERN_30@v1'])
    assert m == {'NULL_BSWCD': 2, 'PATTERN_30': 1}


def test_parse_from_full_frontmatter_text():
    text = (
        '---\n'
        'uses:\n'
        '  NULL_BSWCD: 2\n'
        '  PATTERN_30: 1\n'
        '---\n'
        '\nBody begins here. The NULL_BSWCD test was ...\n'
    )
    m = parse_session_manifest(text)
    assert m == {'NULL_BSWCD': 2, 'PATTERN_30': 1}


def test_parse_from_frontmatter_dict():
    m = parse_session_manifest({'uses': {'NULL_BSWCD': 2}})
    assert m == {'NULL_BSWCD': 2}


def test_parse_accepts_v_prefix_strings():
    m = parse_session_manifest({'NULL_BSWCD': 'v2', 'PATTERN_30': '@v1'})
    assert m == {'NULL_BSWCD': 2, 'PATTERN_30': 1}


def test_parse_rejects_zero_version():
    with pytest.raises(ValueError, match='must be >= 1'):
        parse_session_manifest({'NULL_BSWCD': 0})


def test_parse_rejects_malformed_list_item():
    with pytest.raises(ValueError, match='NAME@v'):
        parse_session_manifest(['NULL_BSWCD'])  # missing @v


def test_parse_text_without_frontmatter_returns_empty():
    assert parse_session_manifest('no frontmatter here') == {}


def test_parse_text_with_empty_uses_returns_empty():
    text = '---\nuses: {}\n---\n\nbody\n'
    assert parse_session_manifest(text) == {}


# ----------------------------------------------------------------------
# expand / contract / round-trip
# ----------------------------------------------------------------------

def test_expand_adds_version_to_bare_names():
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    prose = 'The NULL_BSWCD test showed PATTERN_30 Level-3 coupling.'
    expanded = expand_references(prose, manifest)
    assert 'NULL_BSWCD@v2' in expanded
    assert 'PATTERN_30@v1' in expanded


def test_expand_leaves_non_manifest_names_alone():
    manifest = {'NULL_BSWCD': 2}
    prose = 'NULL_BSWCD and SHADOWS_ON_WALL appear.'
    expanded = expand_references(prose, manifest)
    assert 'NULL_BSWCD@v2' in expanded
    assert 'SHADOWS_ON_WALL' in expanded
    assert 'SHADOWS_ON_WALL@v' not in expanded


def test_expand_preserves_existing_versioned_refs():
    manifest = {'NULL_BSWCD': 2}
    prose = 'Running NULL_BSWCD@v2 against F011.'
    expanded = expand_references(prose, manifest)
    # Should still mention @v2 exactly once — not doubled.
    assert expanded.count('NULL_BSWCD@v2') == 1


def test_contract_strips_version_when_matches_manifest():
    manifest = {'NULL_BSWCD': 2}
    prose = 'Running NULL_BSWCD@v2 test.'
    contracted = contract_references(prose, manifest)
    assert contracted == 'Running NULL_BSWCD test.'


def test_contract_preserves_mismatched_version():
    manifest = {'NULL_BSWCD': 2}
    prose = 'Legacy NULL_BSWCD@v1 reference.'
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        contracted = contract_references(prose, manifest)
    assert 'NULL_BSWCD@v1' in contracted
    conflicts = [w for w in captured if issubclass(w.category, CrossVersionConflict)]
    assert len(conflicts) == 1


def test_round_trip_stable():
    manifest = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    # Canonical form: bare in prose, manifest declared in frontmatter.
    # Round-trip: contract(expand(x)) should equal x.
    prose = 'The NULL_BSWCD test and PATTERN_30 Level-3 analysis.'
    expanded = expand_references(prose, manifest)
    back = contract_references(expanded, manifest)
    assert back == prose


def test_round_trip_ok_helper():
    # Canonical form is BARE: round_trip_ok tests contract(expand(x)) == x
    # where x is bare-alias prose. Fully-qualified input is tested via
    # the expand/contract pair directly in test_round_trip_stable.
    manifest = {'NULL_BSWCD': 2}
    bare = 'NULL_BSWCD is the null.'
    ok, diag = round_trip_ok(bare, manifest)
    assert ok, diag


def test_round_trip_ok_refuses_preexisting_conflicts():
    manifest = {'NULL_BSWCD': 2}
    # Text contains NULL_BSWCD@v1 but manifest binds v2 — undefined.
    conflicted = 'Legacy NULL_BSWCD@v1 call.'
    ok, diag = round_trip_ok(conflicted, manifest)
    assert not ok
    assert 'conflicts' in diag


# ----------------------------------------------------------------------
# find_conflicts + CROSS_VERSION_CONFLICT warning path
# ----------------------------------------------------------------------

def test_find_conflicts_reports_disagreement():
    manifest = {'NULL_BSWCD': 2}
    prose = 'An old log says NULL_BSWCD@v1 but manifest binds v2.'
    conflicts = find_conflicts(prose, manifest)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c['name'] == 'NULL_BSWCD'
    assert c['inline_version'] == 1
    assert c['manifest_version'] == 2


def test_find_conflicts_empty_when_consistent():
    manifest = {'NULL_BSWCD': 2}
    prose = 'The NULL_BSWCD@v2 test ran.'
    assert find_conflicts(prose, manifest) == []


def test_expand_warns_on_inline_conflict():
    manifest = {'NULL_BSWCD': 2}
    prose = 'Old stale NULL_BSWCD@v1 reference.'
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        expand_references(prose, manifest)
    conflicts = [w for w in captured if issubclass(w.category, CrossVersionConflict)]
    assert len(conflicts) == 1


# ----------------------------------------------------------------------
# manifest_frontmatter emission
# ----------------------------------------------------------------------

def test_manifest_frontmatter_canonical_form():
    manifest = {'PATTERN_30': 1, 'NULL_BSWCD': 2}  # unsorted input
    fm = manifest_frontmatter(manifest)
    # Names must be sorted alphabetically for reproducibility.
    lines = fm.splitlines()
    assert lines[0] == '---'
    assert lines[1] == 'uses:'
    assert lines[2] == '  NULL_BSWCD: 2'
    assert lines[3] == '  PATTERN_30: 1'
    assert lines[4] == '---'


def test_manifest_frontmatter_empty():
    fm = manifest_frontmatter({})
    assert 'uses: {}' in fm
    assert fm.startswith('---')


def test_manifest_frontmatter_round_trips_through_parser():
    original = {'NULL_BSWCD': 2, 'PATTERN_30': 1}
    fm = manifest_frontmatter(original)
    round_tripped = parse_session_manifest(fm + 'body text\n')
    assert round_tripped == original


# ----------------------------------------------------------------------
# validate_reference_string integration
# ----------------------------------------------------------------------

def test_validator_covers_manifest_declared_bare_names():
    # NULL_BOOT is promoted; using it bare without manifest = violation.
    # With manifest covering it, violation vanishes.
    prose = 'The NULL_BOOT null ran.'
    without = validate_reference_string(prose, strict=False)
    assert any(v['name'] == 'NULL_BOOT' for v in without)
    with_manifest = validate_reference_string(
        prose, strict=False, manifest={'NULL_BOOT': 1},
    )
    assert not any(v['name'] == 'NULL_BOOT' for v in with_manifest)


def test_validator_still_catches_uncovered_names():
    # Two bare refs; manifest covers only one. Uncovered must still violate.
    prose = 'Both NULL_BOOT and NULL_PLAIN are used bare.'
    violations = validate_reference_string(
        prose, strict=False, manifest={'NULL_BOOT': 1},
    )
    assert not any(v['name'] == 'NULL_BOOT' for v in violations)
    assert any(v['name'] == 'NULL_PLAIN' for v in violations)


# ----------------------------------------------------------------------
# resolve_with_manifest routing
# ----------------------------------------------------------------------

def test_resolve_with_manifest_uses_bound_version():
    # NULL_BOOT is promoted at v1.
    m = {'NULL_BOOT': 1}
    data = resolve_with_manifest('NULL_BOOT', m)
    assert data is not None
    assert data['name'] == 'NULL_BOOT'


def test_resolve_with_manifest_passthrough_for_explicit_ref():
    data = resolve_with_manifest('NULL_BOOT@v1', {})
    assert data is not None
    assert data['name'] == 'NULL_BOOT'


def test_resolve_with_manifest_fallthrough_when_not_in_manifest():
    # Bare name, not in manifest — resolve() emits UserWarning + returns latest.
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        data = resolve_with_manifest('NULL_BOOT', {'PATTERN_30': 1})
    assert data is not None
    user_warns = [w for w in captured if issubclass(w.category, UserWarning)
                  and not issubclass(w.category, DeprecationWarning)
                  and not issubclass(w.category, CrossVersionConflict)]
    assert len(user_warns) >= 1
