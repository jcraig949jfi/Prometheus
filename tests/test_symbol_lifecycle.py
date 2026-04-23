"""T2 (wave 0) — symbol lifecycle status field tests.

Exercises the active / deprecated / archived lifecycle transitions,
their interaction with Rule 3 immutability, validator errors, and
resolver behavior (DeprecationWarning + SymbolArchivedError).

Uses NULL_BOOT as the test-subject symbol and always restores it to
status=active at the end, so the registry remains clean after the test
runs. If the test aborts mid-flight, run:
    python -c "from agora.symbols import update_status; update_status('NULL_BOOT','active',None)"
"""
import os
import warnings

import pytest

from agora.symbols import (
    resolve, update_status, get_status, get_successor,
    SymbolArchivedError, SymbolValidationError,
)


SUBJECT = 'NULL_BOOT'
DUMMY_SUCCESSOR = 'NULL_PLAIN@v1'


@pytest.fixture(autouse=True)
def _restore_active():
    """Restore NULL_BOOT to active before and after each test."""
    update_status(SUBJECT, 'active', None)
    yield
    update_status(SUBJECT, 'active', None)


def test_default_active():
    assert get_status(SUBJECT) == 'active'
    assert get_successor(SUBJECT) is None


def test_deprecated_requires_successor():
    with pytest.raises(SymbolValidationError, match='requires a successor'):
        update_status(SUBJECT, 'deprecated')


def test_deprecate_then_resolve_emits_warning():
    update_status(SUBJECT, 'deprecated', DUMMY_SUCCESSOR)
    assert get_status(SUBJECT) == 'deprecated'
    assert get_successor(SUBJECT) == DUMMY_SUCCESSOR
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        data = resolve(SUBJECT, version=1)
    assert data is not None, 'deprecated symbol should still resolve'
    dep = [w for w in captured if issubclass(w.category, DeprecationWarning)]
    assert len(dep) == 1
    assert 'deprecated' in str(dep[0].message)
    assert DUMMY_SUCCESSOR in str(dep[0].message)


def test_archived_blocks_resolve_without_flag():
    update_status(SUBJECT, 'archived', DUMMY_SUCCESSOR)
    with pytest.raises(SymbolArchivedError) as exc:
        resolve(SUBJECT, version=1)
    assert exc.value.name == SUBJECT
    assert exc.value.successor == DUMMY_SUCCESSOR


def test_archived_resolves_with_flag_and_warns():
    update_status(SUBJECT, 'archived', DUMMY_SUCCESSOR)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        data = resolve(SUBJECT, version=1, include_archived=True)
    assert data is not None
    arch = [w for w in captured if issubclass(w.category, DeprecationWarning)]
    assert len(arch) == 1
    assert 'archived' in str(arch[0].message)


def test_active_with_successor_rejected():
    with pytest.raises(SymbolValidationError, match='successor is only valid'):
        update_status(SUBJECT, 'active', DUMMY_SUCCESSOR)


def test_invalid_status_rejected():
    with pytest.raises(SymbolValidationError, match='status must be one of'):
        update_status(SUBJECT, 'retired')


def test_malformed_successor_rejected():
    with pytest.raises(SymbolValidationError, match='must match NAME'):
        update_status(SUBJECT, 'deprecated', 'NULL_PLAIN')  # missing @v


def test_update_status_unknown_symbol():
    with pytest.raises(ValueError, match='not promoted'):
        update_status('NONEXISTENT_SYMBOL_XYZ', 'active', None)


def test_rule3_preserved_across_transitions():
    """A full deprecate -> archive -> restore cycle must NOT mutate :def."""
    import json
    from agora.symbols.resolve import _get_redis
    r = _get_redis()
    version = int(r.get(f'symbols:{SUBJECT}:latest'))
    key = f'symbols:{SUBJECT}:v{version}:def'
    before = r.get(key)
    update_status(SUBJECT, 'deprecated', DUMMY_SUCCESSOR)
    after_dep = r.get(key)
    update_status(SUBJECT, 'archived', DUMMY_SUCCESSOR)
    after_arch = r.get(key)
    update_status(SUBJECT, 'active', None)
    after_restore = r.get(key)
    assert before == after_dep == after_arch == after_restore
    # And the payload is well-formed JSON throughout
    assert json.loads(before)['name'] == SUBJECT
