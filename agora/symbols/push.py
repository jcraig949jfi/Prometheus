"""Sync a symbol MD file to Redis. Strict versioning, immutability enforced.

Keys written:
    symbols:<NAME>:v<N>:def      STRING  immutable once written
    symbols:<NAME>:v<N>:meta     HASH    immutable once written
    symbols:<NAME>:latest        STRING  mutable (the current version integer)
    symbols:<NAME>:versions      ZSET    append-only (version int scored by timestamp)
    symbols:all                  SET     append-only
    symbols:by_type:<type>       SET     append-only (membership only)
    symbols:refs:<ref>           SET     append-only, ref includes @v<N> or @c<commit>

Usage:
    python -m agora.symbols.push harmonia/memory/symbols/NULL_BSWCD.md
    python -m agora.symbols.push harmonia/memory/symbols/

Refuses:
    - Symbol without required frontmatter (version, version_timestamp, precision)
    - References missing @v<N> or @c<commit> suffix
    - Attempt to overwrite an existing symbols:<NAME>:v<N>:def with different content
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import redis

from .parse import load_symbol


REQUIRED_FIELDS = {'name', 'type', 'version', 'version_timestamp', 'precision',
                   'immutable', 'previous_version'}
VALID_REF = re.compile(r'^[A-Za-z0-9_-]+@(v\d+|c[0-9a-f]{6,40}|CURRENT)$')

# T2 (wave 0) — lifecycle statuses. Per-symbol-name mutable metadata,
# stored outside the immutable :def blob so transitions don't violate Rule 3.
VALID_STATUSES = {'active', 'deprecated', 'archived'}
# Fields excluded from the immutable def_json payload (stored in separate
# mutable keys instead). If you add mutable metadata, add it here.
MUTABLE_FIELDS = {'status', 'successor'}


class SymbolValidationError(ValueError):
    pass


class SymbolImmutabilityError(ValueError):
    pass


def _get_redis():
    host = os.environ.get('AGORA_REDIS_HOST', '192.168.1.176')
    port = int(os.environ.get('AGORA_REDIS_PORT', '6379'))
    password = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')
    return redis.Redis(host=host, port=port, password=password, decode_responses=True)


def _validate(sym, md_path):
    fm = {k: sym.get(k) for k in REQUIRED_FIELDS}

    # version must be >= 1 for promotion
    version = sym.get('version')
    if not isinstance(version, int) or version < 1:
        raise SymbolValidationError(
            f'{md_path}: version must be integer >= 1 for promotion (got {version!r})')

    # version_timestamp required, ISO-8601-ish
    ts = sym.get('version_timestamp')
    if not ts:
        raise SymbolValidationError(f'{md_path}: version_timestamp missing')
    try:
        datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except Exception:
        raise SymbolValidationError(f'{md_path}: version_timestamp not ISO-8601: {ts!r}')

    # precision required — we check presence; the shape is symbol-type-specific
    if not _has_precision(sym):
        raise SymbolValidationError(f'{md_path}: precision declaration missing')

    # immutable must be True
    if sym.get('immutable') not in (True, 'true', 'True'):
        raise SymbolValidationError(
            f'{md_path}: immutable must be true for promotion (got {sym.get("immutable")!r})')

    # previous_version: must be int or None (null)
    pv = sym.get('previous_version')
    if pv is not None and not isinstance(pv, int):
        raise SymbolValidationError(
            f'{md_path}: previous_version must be int or null (got {pv!r})')
    if version == 1 and pv is not None:
        raise SymbolValidationError(
            f'{md_path}: v1 must have previous_version: null')
    if version > 1 and pv != version - 1:
        raise SymbolValidationError(
            f'{md_path}: v{version} must have previous_version: {version-1}')

    # references: every one must match VALID_REF
    for ref in sym.get('references') or []:
        if not VALID_REF.match(ref):
            raise SymbolValidationError(
                f'{md_path}: reference {ref!r} missing @v<N> or @c<commit> suffix')


def _has_precision(sym):
    """Precision may appear either as a frontmatter key or as a dedicated MD section."""
    sections = sym.get('sections', {})
    if any('precision' in k.lower() for k in sections.keys()):
        return True
    # Also accept a 'precision' key at frontmatter level (parse.py stores scalar only)
    # The parse is loose — if the MD has a `precision:` line anywhere in frontmatter, accept.
    # A symbol-type-specific validator is future work.
    return sym.get('precision') is not None


def push_symbol(md_path, r=None, force=False):
    """Promote a symbol MD to Redis.

    Returns: (action, name, version)
        action: 'pushed_new_version' | 'unchanged' | 'skipped_draft'
    Raises: SymbolValidationError, SymbolImmutabilityError
    """
    if r is None:
        r = _get_redis()

    sym = load_symbol(md_path)

    name = sym['name']
    version = sym.get('version', 0)

    if version == 0 and not force:
        return 'skipped_draft', name, 0

    _validate(sym, md_path)

    # Extract mutable lifecycle fields BEFORE computing def_json — these
    # are stored in separate mutable Redis keys and must NOT enter the
    # frozen :def blob (Rule 3: promoted versions are immutable).
    status = sym.pop('status', None) or 'active'
    successor = sym.pop('successor', None)
    _validate_lifecycle(status, successor, md_path)

    # Canonical JSON for content-comparison (excludes mutable fields)
    def_json = json.dumps(sym, ensure_ascii=False, sort_keys=True)

    # Mutable lifecycle keys — update on every push regardless of whether
    # the :def is new or unchanged. Safe to re-write because they're outside
    # the immutable :def blob (Rule 3).
    def _write_mutable():
        r.set(f'symbols:{name}:status', status)
        if successor:
            r.set(f'symbols:{name}:successor', successor)
        else:
            r.delete(f'symbols:{name}:successor')

    # Immutability check: if this version already exists in Redis, new content must match exactly
    existing_def = r.get(f'symbols:{name}:v{version}:def')
    if existing_def is not None:
        if existing_def == def_json:
            _write_mutable()
            return 'unchanged', name, version
        else:
            raise SymbolImmutabilityError(
                f'{name}@v{version} already in Redis with different content. '
                f'To correct, create a new version (v{version+1}). '
                f'Promoted versions are immutable.'
            )

    # Write immutable version keys
    r.set(f'symbols:{name}:v{version}:def', def_json)

    meta_hash = {
        'name': name,
        'type': sym['type'],
        'version': str(version),
        'version_timestamp': sym['version_timestamp'],
        'previous_version': str(sym.get('previous_version') or ''),
        'proposed_by': sym.get('proposed_by') or '',
        'promoted_commit': sym.get('promoted_commit') or '',
        'redis_key': sym.get('redis_key') or f'symbols:{name}:v{version}:def',
        'implementation': sym.get('implementation') or '',
        'references': ','.join(sym.get('references') or []),
        'md_path': sym.get('md_path', ''),
    }
    r.hset(f'symbols:{name}:v{version}:meta', mapping=meta_hash)

    # Update mutable pointers: latest version, version history
    r.set(f'symbols:{name}:latest', str(version))

    # Timestamp score for sorted set; fallback to version number if timestamp parse fails
    try:
        score = datetime.fromisoformat(
            sym['version_timestamp'].replace('Z', '+00:00')
        ).timestamp()
    except Exception:
        score = float(version)
    r.zadd(f'symbols:{name}:versions', {str(version): score})

    # Index sets (append-only)
    r.sadd('symbols:all', name)
    r.sadd(f'symbols:by_type:{sym["type"]}', name)

    # Reverse-reference index, keyed by the versioned reference string
    for ref in (sym.get('references') or []):
        r.sadd(f'symbols:refs:{ref}', f'{name}@v{version}')

    # Mutable lifecycle keys (same helper as the unchanged-path branch).
    _write_mutable()

    return 'pushed_new_version', name, version


def _validate_lifecycle(status, successor, md_path):
    """Validate status + successor fields per T2 (wave 0) spec."""
    if status not in VALID_STATUSES:
        raise SymbolValidationError(
            f'{md_path}: status must be one of {sorted(VALID_STATUSES)} '
            f'(got {status!r})'
        )
    if status in ('deprecated', 'archived'):
        if not successor:
            raise SymbolValidationError(
                f'{md_path}: status={status!r} requires a successor field '
                f'(e.g. successor: OTHER_NAME@v1)'
            )
        if not VALID_REF.match(successor):
            raise SymbolValidationError(
                f'{md_path}: successor {successor!r} must match NAME@v<N> '
                f'or NAME@c<commit>'
            )
    elif successor:
        # Active symbols should not carry a successor (no meaning)
        raise SymbolValidationError(
            f'{md_path}: successor is only valid when status in '
            f'{{deprecated, archived}} (got status={status!r})'
        )


def update_status(name, status, successor=None, r=None):
    """Transition an existing symbol to a new lifecycle status.

    Does NOT touch the immutable :def blob. Writes only the mutable
    symbols:<NAME>:status (and successor) keys. Use this when the MD
    file is updated to reflect a status change, or to perform the
    transition without re-pushing the MD.

    Raises SymbolValidationError on bad status/successor.
    Raises ValueError if the symbol isn't promoted to Redis yet.
    """
    if r is None:
        r = _get_redis()
    _validate_lifecycle(status, successor, f'<update_status {name}>')
    if not r.sismember('symbols:all', name):
        raise ValueError(f'{name} is not promoted to Redis; cannot set status')
    r.set(f'symbols:{name}:status', status)
    if successor:
        r.set(f'symbols:{name}:successor', successor)
    else:
        r.delete(f'symbols:{name}:successor')
    return status, successor


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)
    r = _get_redis()
    paths = []
    for arg in argv[1:]:
        p = Path(arg)
        if p.is_dir():
            paths.extend(sorted(p.glob('*.md')))
        else:
            paths.append(p)
    # Exclude docs that are not symbols
    EXCLUDE = {'README.md', 'INDEX.md', 'OVERVIEW.md', 'VERSIONING.md'}
    paths = [p for p in paths if p.name not in EXCLUDE]

    rc = 0
    for p in paths:
        try:
            action, name, version = push_symbol(p, r=r)
            print(f'{action:22s} {name}@v{version} ({p.name})')
        except SymbolImmutabilityError as e:
            print(f'IMMUTABILITY_ERROR     {p.name}: {e}', file=sys.stderr)
            rc = 2
        except SymbolValidationError as e:
            print(f'VALIDATION_ERROR       {p.name}: {e}', file=sys.stderr)
            rc = 2
        except Exception as e:
            print(f'ERROR                  {p.name}: {e}', file=sys.stderr)
            rc = 1
    sys.exit(rc)


if __name__ == '__main__':
    main(sys.argv)
