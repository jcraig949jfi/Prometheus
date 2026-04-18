"""Agent-side symbol resolver. Read-only helpers over base Redis.

Usage:
    from agora.symbols import resolve, resolve_meta, by_type, refs_to

    spec = resolve('NULL_BSWCD')          # full JSON dict
    meta = resolve_meta('NULL_BSWCD')     # HASH fields as dict
    datasets = by_type('dataset')         # set of names
    f011_syms = refs_to('F011')           # symbols referencing F011
"""
import json
import os
import redis


_client = None


def _get_redis():
    global _client
    if _client is None:
        host = os.environ.get('AGORA_REDIS_HOST', '192.168.1.176')
        port = int(os.environ.get('AGORA_REDIS_PORT', '6379'))
        password = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')
        _client = redis.Redis(host=host, port=port, password=password, decode_responses=True)
    return _client


def resolve(name):
    """Return full dict for a symbol, or None if not in Redis."""
    r = _get_redis()
    raw = r.get(f'symbols:{name}:def')
    if raw is None:
        return None
    return json.loads(raw)


def resolve_meta(name):
    """Return metadata hash for a symbol (cheap — no full def). Returns None if absent."""
    r = _get_redis()
    h = r.hgetall(f'symbols:{name}:meta')
    if not h:
        return None
    # Inflate references from comma-separated string
    if 'references' in h:
        h['references'] = [x for x in h['references'].split(',') if x]
    if 'version' in h:
        try:
            h['version'] = int(h['version'])
        except ValueError:
            pass
    return h


def by_type(type_name):
    """Set of symbol names of the given type."""
    r = _get_redis()
    return r.smembers(f'symbols:by_type:{type_name}')


def refs_to(id_or_name):
    """Set of symbol names that reference the given id (F-id, P-id, Pattern, or symbol name)."""
    r = _get_redis()
    return r.smembers(f'symbols:refs:{id_or_name}')


def all_symbols():
    """Set of all promoted symbol names."""
    r = _get_redis()
    return r.smembers('symbols:all')


def exists(name):
    r = _get_redis()
    return r.sismember('symbols:all', name)
