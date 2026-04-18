"""Mirror the current tensor artifacts to Redis.

Usage:
    python -m agora.tensor.push
    python -m agora.tensor.push --tensor-dir harmonia/memory --dry-run

Reads:
    harmonia/memory/landscape_tensor.npz     # numeric matrix
    harmonia/memory/landscape_manifest.json  # metadata
    harmonia/memory/feature_graph.json       # row-to-row edges
    harmonia/memory/projection_graph.json    # col-to-col edges

Writes:
    tensor:version                    (bumped)
    tensor:dims                       (HASH: n_features, n_projections, density, updated_at, version)
    tensor:features                   (LIST, ordered F-ids)
    tensor:projections                (LIST, ordered P-ids)
    tensor:feature_meta:<F>           (STRING, JSON)
    tensor:projection_meta:<P>        (STRING, JSON)
    tensor:cells                      (HASH, "F:P" -> verdict int string)
    tensor:feature_edges              (STRING, JSON array)
    tensor:projection_edges           (STRING, JSON array)
    tensor:updates                    (STREAM, one entry per cell that changed)

Idempotent: if called twice without changes, only the version-unchanged
dims fields and a noop update stream entry are written. If cells
changed, only those cells' updates go on the stream.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import redis


TENSOR_KEY_PREFIX = 'tensor:'


def _get_redis():
    host = os.environ.get('AGORA_REDIS_HOST', '192.168.1.176')
    port = int(os.environ.get('AGORA_REDIS_PORT', '6379'))
    password = os.environ.get('AGORA_REDIS_PASSWORD', 'prometheus')
    return redis.Redis(host=host, port=port, password=password, decode_responses=True)


def push_tensor(tensor_dir='harmonia/memory', dry_run=False, source_commit='HEAD', r=None):
    """Mirror tensor artifacts to Redis. Returns summary dict."""
    if r is None and not dry_run:
        r = _get_redis()

    td = Path(tensor_dir)
    npz_path = td / 'landscape_tensor.npz'
    manifest_path = td / 'landscape_manifest.json'
    fg_path = td / 'feature_graph.json'
    pg_path = td / 'projection_graph.json'

    for p in (npz_path, manifest_path, fg_path, pg_path):
        if not p.exists():
            raise FileNotFoundError(f'{p} not found; run build_landscape_tensor.py first')

    # Load tensor + manifest
    npz = np.load(npz_path, allow_pickle=True)
    # npz stores the tensor under 'T'; feature_ids/projection_ids are redundant with manifest
    tensor = npz['T']  # shape (n_features, n_projections)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    feature_graph = json.loads(fg_path.read_text(encoding='utf-8'))
    projection_graph = json.loads(pg_path.read_text(encoding='utf-8'))

    # manifest['features'] and ['projections'] are lists of dicts; extract IDs
    features_full = manifest.get('features', [])
    projections_full = manifest.get('projections', [])
    features_list = [f['id'] for f in features_full if 'id' in f]
    projections_list = [p['id'] for p in projections_full if 'id' in p]

    n_features = len(features_list)
    n_projections = len(projections_list)
    nonzero = int(np.count_nonzero(tensor))
    density_pct = 100.0 * nonzero / max(1, n_features * n_projections)

    summary = {
        'n_features': n_features,
        'n_projections': n_projections,
        'nonzero_cells': nonzero,
        'density_pct': round(density_pct, 2),
        'dry_run': dry_run,
    }

    if dry_run:
        summary['would_write'] = [
            f'{TENSOR_KEY_PREFIX}features ({n_features} items)',
            f'{TENSOR_KEY_PREFIX}projections ({n_projections} items)',
            f'{TENSOR_KEY_PREFIX}cells ({nonzero} non-zero + {n_features * n_projections - nonzero} zero-cells)',
            f'{TENSOR_KEY_PREFIX}feature_meta:<F> ({n_features} strings)',
            f'{TENSOR_KEY_PREFIX}projection_meta:<P> ({n_projections} strings)',
            f'{TENSOR_KEY_PREFIX}feature_edges ({len(feature_graph.get("edges", []))} edges)',
            f'{TENSOR_KEY_PREFIX}projection_edges ({len(projection_graph.get("edges", []))} edges)',
        ]
        return summary

    # Read old cells to compute change events
    old_cells = r.hgetall(f'{TENSOR_KEY_PREFIX}cells')

    # Bump version
    new_version = r.incr(f'{TENSOR_KEY_PREFIX}version')
    now = datetime.now(timezone.utc).isoformat()

    # Ordered lists (rebuilt each push; ordering is canonical)
    pipe = r.pipeline()
    pipe.delete(f'{TENSOR_KEY_PREFIX}features')
    if features_list:
        pipe.rpush(f'{TENSOR_KEY_PREFIX}features', *features_list)
    pipe.delete(f'{TENSOR_KEY_PREFIX}projections')
    if projections_list:
        pipe.rpush(f'{TENSOR_KEY_PREFIX}projections', *projections_list)
    pipe.execute()

    # Feature meta (each element of features list is already a full dict)
    for feat_info in features_full:
        fid = feat_info.get('id')
        if fid:
            r.set(
                f'{TENSOR_KEY_PREFIX}feature_meta:{fid}',
                json.dumps(feat_info, ensure_ascii=False, sort_keys=True),
            )

    # Projection meta
    for proj_info in projections_full:
        pid = proj_info.get('id')
        if pid:
            r.set(
                f'{TENSOR_KEY_PREFIX}projection_meta:{pid}',
                json.dumps(proj_info, ensure_ascii=False, sort_keys=True),
            )

    # Cells — rewrite all; emit stream events only for changed cells
    new_cells = {}
    for i, fid in enumerate(features_list):
        for j, pid in enumerate(projections_list):
            key = f'{fid}:{pid}'
            v = int(tensor[i, j])
            new_cells[key] = str(v)

    # Diff old vs new
    changes = 0
    for key, new_v in new_cells.items():
        old_v = old_cells.get(key, '0')
        if old_v != new_v:
            r.xadd(
                f'{TENSOR_KEY_PREFIX}updates',
                {
                    'F': key.split(':')[0],
                    'P': key.split(':')[1],
                    'old': old_v,
                    'new': new_v,
                    'source': source_commit,
                    'version': str(new_version),
                    'at': now,
                },
                maxlen=5000,
                approximate=True,
            )
            changes += 1

    # Write new cell hash (replace)
    r.delete(f'{TENSOR_KEY_PREFIX}cells')
    if new_cells:
        r.hset(f'{TENSOR_KEY_PREFIX}cells', mapping=new_cells)

    # Graph edges
    r.set(
        f'{TENSOR_KEY_PREFIX}feature_edges',
        json.dumps(feature_graph.get('edges', []), ensure_ascii=False, sort_keys=True),
    )
    r.set(
        f'{TENSOR_KEY_PREFIX}projection_edges',
        json.dumps(projection_graph.get('edges', []), ensure_ascii=False, sort_keys=True),
    )

    # Dims
    r.delete(f'{TENSOR_KEY_PREFIX}dims')
    r.hset(
        f'{TENSOR_KEY_PREFIX}dims',
        mapping={
            'n_features': str(n_features),
            'n_projections': str(n_projections),
            'nonzero_cells': str(nonzero),
            'density_pct': f'{density_pct:.2f}',
            'updated_at': now,
            'version': str(new_version),
            'source_commit': source_commit,
        },
    )

    summary['version'] = new_version
    summary['cells_changed'] = changes
    summary['updated_at'] = now
    return summary


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tensor-dir', default='harmonia/memory')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--source-commit', default='HEAD')
    args = parser.parse_args(argv[1:])

    summary = push_tensor(
        tensor_dir=args.tensor_dir,
        dry_run=args.dry_run,
        source_commit=args.source_commit,
    )
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main(sys.argv)
