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


def _get_redis():
    global _client
    if _client is None:
        host = os.environ.get('AGORA_REDIS_HOST', '192.168.1.176')
        port = int(os.environ.get('AGORA_REDIS_PORT', '6379'))
        password = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')
        _client = redis.Redis(host=host, port=port, password=password, decode_responses=True)
    return _client


def resolve(name, version=None):
    """Return full dict for a symbol at the given version, or None if absent.

    If version is None, returns the latest version and emits a UserWarning
    (unversioned references violate the versioning discipline).
    """
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
    return json.loads(raw)


def resolve_at(reference):
    """Resolve a reference in the canonical 'NAME@vN' form."""
    m = _REF_PATTERN.match(reference)
    if not m:
        raise ValueError(
            f'resolve_at: expected NAME@v<N> form, got {reference!r}'
        )
    return resolve(m.group('name'), version=int(m.group('version')))


def resolve_meta(name, version=None):
    """Return meta HASH for a symbol at the given version. Versioned key required."""
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


def validate_reference_string(text, strict=True):
    """Validate that a text mentions of symbol names carry @v<N>.

    Scans `text` for bare symbol names (by checking against all_symbols())
    followed by whitespace or punctuation. Returns a list of violations.
    If strict=True, raises ValueError on any violation.
    """
    r = _get_redis()
    names = r.smembers('symbols:all')
    violations = []
    for name in names:
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
