"""Sync a symbol MD file to Redis (promotion step).

Base Redis only: SET, HSET, SADD. No modules required.

Usage:
    python -m agora.symbols.push harmonia/memory/symbols/NULL_BSWCD.md
    python -m agora.symbols.push harmonia/memory/symbols/*.md

A symbol with version=0 is DRAFT; push_symbol skips it (MD is still in
git; Redis sync only on promotion).
"""
import json
import os
import sys
from pathlib import Path

import redis

from .parse import load_symbol


def _get_redis():
    host = os.environ.get('AGORA_REDIS_HOST', '192.168.1.176')
    port = int(os.environ.get('AGORA_REDIS_PORT', '6379'))
    password = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')
    return redis.Redis(host=host, port=port, password=password, decode_responses=True)


def push_symbol(md_path, r=None, force=False):
    """Sync one symbol MD to Redis. Returns action taken: 'pushed' | 'skipped_draft' | 'unchanged'.

    Parameters:
        md_path: path to the symbol MD
        r: Redis client (auto-constructed if None)
        force: push even if version=0
    """
    if r is None:
        r = _get_redis()

    sym = load_symbol(md_path)
    name = sym['name']
    version = sym['version']

    if version == 0 and not force:
        return 'skipped_draft', name

    # Build the def JSON
    def_json = json.dumps(sym, ensure_ascii=False, sort_keys=True)

    # Check if unchanged
    existing = r.get(f'symbols:{name}:def')
    if existing == def_json and not force:
        return 'unchanged', name

    # Write def string
    r.set(f'symbols:{name}:def', def_json)

    # Flat meta hash (strings only)
    meta = {
        'name': name,
        'type': sym['type'],
        'version': str(version),
        'proposed_by': sym.get('proposed_by') or '',
        'promoted_commit': sym.get('promoted_commit') or '',
        'redis_key': sym.get('redis_key') or '',
        'implementation': sym.get('implementation') or '',
        'references': ','.join(sym.get('references') or []),
        'md_path': sym.get('md_path', ''),
    }
    # Delete old meta then rewrite (prevents stale fields)
    r.delete(f'symbols:{name}:meta')
    if meta:
        r.hset(f'symbols:{name}:meta', mapping=meta)

    # Index sets
    r.sadd('symbols:all', name)
    r.sadd(f'symbols:by_type:{sym["type"]}', name)

    # References index. Clear old refs first by walking existing.
    # (Cheap: we just reverse-index each reference.)
    for ref in (sym.get('references') or []):
        r.sadd(f'symbols:refs:{ref}', name)

    return 'pushed', name


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
        elif '*' in arg:
            # Let shell globs expand; a literal * here is leftover
            continue
        else:
            paths.append(p)
    # filter out README.md and INDEX.md (not symbols themselves)
    paths = [p for p in paths if p.name not in ('README.md', 'INDEX.md')]
    for p in paths:
        try:
            action, name = push_symbol(p, r=r)
            print(f'{action:16s} {name} ({p.name})')
        except Exception as e:
            print(f'ERROR            {p.name}: {e}', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv)
