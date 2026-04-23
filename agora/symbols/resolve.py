"""Agent-side symbol resolver. Read-only helpers over base Redis.

Versioned access (preferred):
    spec = resolve('NULL_BSWCD', version=1)          # specific immutable version
    spec = resolve_at('NULL_BSWCD@v1')               # parse reference form

Latest (convenience, with warning):
    spec = resolve('NULL_BSWCD')                      # latest + prints warning

Version management:
    latest = get_latest_version('NULL_BSWCD')         # int
    all_versions('NULL_BSWCD')                        # [1, 2, ...]
    needs_upgrade, latest = check_version('NULL_BSWCD', cached=1)

Discovery:
    by_type('dataset')                                # {'Q_EC_R0_D5', ...}
    refs_to('F011@c1abdec43')                         # versioned reverse index
    refs_to_any('F011')                               # all references regardless of version suffix
    all_symbols()                                     # all promoted names
"""
import json
import os
import re
import sys
import warnings

import redis


_client = None
_REF_PATTERN = re.compile(r'^(?P<name>[A-Za-z0-9_-]+)@v(?P<version>\d+)$')


class SymbolArchivedError(LookupError):
    """Raised when resolve() encounters an archived symbol and
    include_archived=False. Carries the symbol name and any successor pointer."""
    def __init__(self, name, successor=None):
        self.name = name
        self.successor = successor
        msg = f'{name} is archived.'
        if successor:
            msg += f' Successor: {successor}.'
        msg += ' Pass include_archived=True to resolve anyway.'
        super().__init__(msg)


# T3 (wave 0) — cross-version-in-session detector.
# Tracks which versions of each symbol name have been resolved in this process.
# When a second distinct version appears for the same name, emit a
# CrossVersionConflict (UserWarning subclass, defined in manifest.py). Rule 4 of
# cross_version_resolution.md: multi-version is legal; this warning provides
# visibility, not enforcement.
_seen_versions: dict = {}


def _register_resolved_version(name: str, version: int) -> None:
    """Track resolved (name, version) pairs and emit CrossVersionConflict on
    a second distinct version. Called by resolve() after a successful fetch."""
    seen = _seen_versions.setdefault(name, set())
    if version in seen:
        return
    seen.add(version)
    if len(seen) == 2:
        # Local import to avoid circular import (manifest imports from resolve)
        from .manifest import CrossVersionConflict
        other = next(iter(seen - {version}))
        warnings.warn(
            f'CROSS_VERSION_CONFLICT: {name} resolved at v{other} earlier this '
            f'session and now at v{version}. Multi-version is legal (Rule 4 of '
            f'cross_version_resolution.md) but surfaced for visibility.',
            CrossVersionConflict, stacklevel=3,
        )


def reset_cross_version_tracker() -> None:
    """Clear the per-process cross-version tracker. Test helper."""
    _seen_versions.clear()


def _get_redis():
    global _client
    if _client is None:
        host = os.environ.get('AGORA_REDIS_HOST', '192.168.1.176')
        port = int(os.environ.get('AGORA_REDIS_PORT', '6379'))
        password = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')
        _client = redis.Redis(host=host, port=port, password=password, decode_responses=True)
    return _client


def resolve(name, version=None, include_archived=False):
    """Return full dict for a symbol at the given version, or None if absent.

    Accepts either:
      - resolve('NAME', version=N)  — explicit version kwarg
      - resolve('NAME@vN')          — canonical reference form (dispatches to resolve_at)
      - resolve('NAME')             — latest + UserWarning (discipline violation)

    Lifecycle behavior (T2, wave 0):
      - If the symbol's status is `deprecated`, emit DeprecationWarning with
        the successor pointer. Resolution still succeeds.
      - If status is `archived`, raise SymbolArchivedError unless
        include_archived=True, in which case resolution succeeds with a warning.
    """
    if '@v' in name:
        if version is not None:
            raise ValueError(
                f'resolve: both reference-form name ({name!r}) and version '
                f'kwarg ({version}) provided; pass exactly one.'
            )
        return resolve_at(name, include_archived=include_archived)
    r = _get_redis()
    if version is None:
        latest = r.get(f'symbols:{name}:latest')
        if latest is None:
            return None
        warnings.warn(
            f'resolve({name!r}) called without version. Returning latest (v{latest}). '
            f'Versioning discipline requires explicit @v<N>.',
            UserWarning, stacklevel=2,
        )
        version = int(latest)
    raw = r.get(f'symbols:{name}:v{version}:def')
    if raw is None:
        return None
    # T3: register the (name, version) pair for cross-version-in-session detection.
    _register_resolved_version(name, version)
    # Lifecycle gate — check status AFTER we know the symbol exists.
    status = r.get(f'symbols:{name}:status') or 'active'
    successor = r.get(f'symbols:{name}:successor')
    if status == 'archived' and not include_archived:
        raise SymbolArchivedError(name, successor=successor)
    if status == 'deprecated':
        warnings.warn(
            f'{name}@v{version} is deprecated.'
            + (f' Successor: {successor}.' if successor else '')
            + ' Update references to the successor.',
            DeprecationWarning, stacklevel=2,
        )
    elif status == 'archived' and include_archived:
        warnings.warn(
            f'{name}@v{version} is archived; resolving under include_archived=True.',
            DeprecationWarning, stacklevel=2,
        )
    return json.loads(raw)


def resolve_at(reference, include_archived=False):
    """Resolve a reference in the canonical 'NAME@vN' form."""
    m = _REF_PATTERN.match(reference)
    if not m:
        raise ValueError(
            f'resolve_at: expected NAME@v<N> form, got {reference!r}'
        )
    return resolve(m.group('name'), version=int(m.group('version')),
                   include_archived=include_archived)


def get_status(name):
    """Return the lifecycle status of a symbol ('active'|'deprecated'|'archived').

    Returns 'active' as the default when the key is absent (for symbols
    promoted before the status field was added). Returns None only if the
    symbol is not promoted at all.
    """
    r = _get_redis()
    if not r.sismember('symbols:all', name):
        return None
    return r.get(f'symbols:{name}:status') or 'active'


def get_successor(name):
    """Return the successor pointer for a deprecated/archived symbol, or None."""
    r = _get_redis()
    return r.get(f'symbols:{name}:successor')


def resolve_meta(name, version=None):
    """Return meta HASH for a symbol at the given version. Versioned key required.

    Accepts reference-form 'NAME@vN' in the name argument, same as resolve().
    """
    if '@v' in name:
        if version is not None:
            raise ValueError(
                f'resolve_meta: both reference-form name ({name!r}) and version '
                f'kwarg ({version}) provided; pass exactly one.'
            )
        m = _REF_PATTERN.match(name)
        if not m:
            raise ValueError(f'resolve_meta: expected NAME@v<N> form, got {name!r}')
        name, version = m.group('name'), int(m.group('version'))
    r = _get_redis()
    if version is None:
        latest = r.get(f'symbols:{name}:latest')
        if latest is None:
            return None
        warnings.warn(
            f'resolve_meta({name!r}) called without version. Returning latest.',
            UserWarning, stacklevel=2,
        )
        version = int(latest)
    h = r.hgetall(f'symbols:{name}:v{version}:meta')
    if not h:
        return None
    if 'references' in h:
        h['references'] = [x for x in h['references'].split(',') if x]
    if 'version' in h:
        try:
            h['version'] = int(h['version'])
        except ValueError:
            pass
    if h.get('previous_version') == '':
        h['previous_version'] = None
    elif h.get('previous_version') is not None:
        try:
            h['previous_version'] = int(h['previous_version'])
        except ValueError:
            pass
    return h


def get_latest_version(name):
    """Return the latest promoted version integer for this symbol, or None."""
    r = _get_redis()
    v = r.get(f'symbols:{name}:latest')
    return int(v) if v is not None else None


def all_versions(name):
    """Return sorted list of all promoted version ints for this symbol."""
    r = _get_redis()
    raw = r.zrange(f'symbols:{name}:versions', 0, -1)
    return sorted(int(x) for x in raw)


def check_version(name, cached):
    """Compare a cached version against the current latest.

    Returns (needs_upgrade: bool, latest_version: int | None).
    If latest is None, the symbol is not in Redis (name unknown).
    """
    latest = get_latest_version(name)
    if latest is None:
        return False, None
    return cached < latest, latest


def by_type(type_name):
    """Set of symbol names of the given type."""
    r = _get_redis()
    return r.smembers(f'symbols:by_type:{type_name}')


def refs_to(reference):
    """Return versioned-reference strings that point at this specific version.

    Argument is of form 'NAME@v<N>' or 'F<id>@c<commit>'.
    """
    r = _get_redis()
    return r.smembers(f'symbols:refs:{reference}')


def refs_to_any(prefix):
    """Return all versioned-reference strings whose reference name begins with prefix."""
    r = _get_redis()
    out = set()
    for key in r.scan_iter(match=f'symbols:refs:{prefix}*'):
        for member in r.smembers(key):
            out.add(member)
    return out


def all_symbols():
    """Set of all promoted symbol names."""
    r = _get_redis()
    return r.smembers('symbols:all')


def exists(name):
    r = _get_redis()
    return r.sismember('symbols:all', name)


def parse_reference(reference):
    """Parse 'NAME@vN' into (name, version). Raises ValueError if malformed."""
    m = _REF_PATTERN.match(reference)
    if not m:
        raise ValueError(
            f'parse_reference: expected NAME@v<N> form, got {reference!r}'
        )
    return m.group('name'), int(m.group('version'))


def validate_reference_string(text, strict=True, manifest=None):
    """Validate that a text's mentions of symbol names carry @v<N>.

    Scans `text` for bare symbol names (by checking against all_symbols())
    NOT followed by @v<digits>. Returns a list of violations.
    If strict=True, raises ValueError on any violation.

    Manifest integration (T1, wave 0):
      If `manifest` is provided (dict NAME -> version, from
      agora.symbols.manifest.parse_session_manifest), bare names that
      are covered by the manifest are NOT violations — the manifest
      is the declaration of authoritative versions for this session.
      Bare names NOT covered by the manifest remain violations.

      Typical call pattern:
          from agora.symbols.manifest import parse_session_manifest
          manifest = parse_session_manifest(session_output_text)
          violations = validate_reference_string(body_text, manifest=manifest)
    """
    r = _get_redis()
    names = r.smembers('symbols:all')
    covered = set(manifest.keys()) if manifest else set()
    violations = []
    for name in names:
        if name in covered:
            continue  # manifest-declared: bare form is legal
        # Match bare name NOT followed by @v
        pattern = re.compile(r'\b' + re.escape(name) + r'(?!@v)\b')
        for m in pattern.finditer(text):
            violations.append({
                'name': name,
                'position': m.start(),
                'context': text[max(0, m.start()-30):min(len(text), m.end()+30)],
            })
    if strict and violations:
        raise ValueError(f'Unversioned symbol references found: {len(violations)} violation(s). First: {violations[0]}')
    return violations
