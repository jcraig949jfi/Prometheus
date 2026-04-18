"""Agent-side tensor resolver. Read-only helpers over base Redis.

Usage:
    from agora.tensor import (
        resolve_cells, resolve_cell, features, projections,
        feature_meta, projection_meta, feature_edges, projection_edges,
        dims, tail_updates, get_version,
    )

    dims()                 # {'n_features': 25, 'n_projections': 42, ...}
    features()             # ['F001', 'F002', ..., 'F045']
    resolve_cell('F011', 'P028')    # int -2..+2 or 0 if untested
    feature_meta('F011')   # {'label': ..., 'tier': 'live_specimen', ...}
    tail_updates(count=20) # recent change events

All returns are native Python types (int, dict, list).
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


def dims():
    """Return tensor dims hash with types coerced."""
    r = _get_redis()
    h = r.hgetall('tensor:dims')
    if not h:
        return None
    for k in ('n_features', 'n_projections', 'nonzero_cells', 'version'):
        if k in h:
            try:
                h[k] = int(h[k])
            except ValueError:
                pass
    if 'density_pct' in h:
        try:
            h['density_pct'] = float(h['density_pct'])
        except ValueError:
            pass
    return h


def get_version():
    """Return current tensor version integer, or None if absent."""
    r = _get_redis()
    v = r.get('tensor:version')
    return int(v) if v is not None else None


def features():
    """Return ordered list of F-ids."""
    r = _get_redis()
    return r.lrange('tensor:features', 0, -1)


def projections():
    """Return ordered list of P-ids."""
    r = _get_redis()
    return r.lrange('tensor:projections', 0, -1)


def feature_meta(fid):
    """Return metadata dict for a feature, or None if absent."""
    r = _get_redis()
    raw = r.get(f'tensor:feature_meta:{fid}')
    if raw is None:
        return None
    return json.loads(raw)


def projection_meta(pid):
    """Return metadata dict for a projection, or None if absent."""
    r = _get_redis()
    raw = r.get(f'tensor:projection_meta:{pid}')
    if raw is None:
        return None
    return json.loads(raw)


def resolve_cell(fid, pid):
    """Return verdict int for (F, P) or 0 if the cell is not in Redis."""
    r = _get_redis()
    v = r.hget('tensor:cells', f'{fid}:{pid}')
    return int(v) if v is not None else 0


def resolve_cells():
    """Return entire tensor as dict keyed by 'F:P' -> int."""
    r = _get_redis()
    raw = r.hgetall('tensor:cells')
    return {k: int(v) for k, v in raw.items()}


def resolve_row(fid):
    """Return dict P-id -> verdict for a feature row."""
    all_cells = resolve_cells()
    out = {}
    prefix = f'{fid}:'
    for key, v in all_cells.items():
        if key.startswith(prefix):
            out[key[len(prefix):]] = v
    return out


def resolve_column(pid):
    """Return dict F-id -> verdict for a projection column."""
    all_cells = resolve_cells()
    out = {}
    suffix = f':{pid}'
    for key, v in all_cells.items():
        if key.endswith(suffix):
            out[key[:-len(suffix)]] = v
    return out


def feature_edges():
    """Return list of feature-to-feature edges."""
    r = _get_redis()
    raw = r.get('tensor:feature_edges')
    return json.loads(raw) if raw else []


def projection_edges():
    """Return list of projection-to-projection edges."""
    r = _get_redis()
    raw = r.get('tensor:projection_edges')
    return json.loads(raw) if raw else []


def tail_updates(count=10):
    """Return the most recent cell-change events from the stream."""
    r = _get_redis()
    entries = r.xrevrange('tensor:updates', count=count)
    return [{'id': eid, **fields} for eid, fields in entries]


def reconstruct_matrix():
    """Return (features_list, projections_list, 2D int matrix) from Redis.

    Useful for numpy-style analysis (rank, SVD, MPS).
    """
    import numpy as np
    fs = features()
    ps = projections()
    cells = resolve_cells()
    m = np.zeros((len(fs), len(ps)), dtype=np.int8)
    f_idx = {f: i for i, f in enumerate(fs)}
    p_idx = {p: j for j, p in enumerate(ps)}
    for key, v in cells.items():
        f, p = key.split(':', 1)
        if f in f_idx and p in p_idx:
            m[f_idx[f], p_idx[p]] = v
    return fs, ps, m
