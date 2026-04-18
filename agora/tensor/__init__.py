"""Tensor registry — shared invariance map via Redis (base ops only).

Git remains source of truth. Redis is the read-mirror every agent
(M1 and M2) hits for live state without waiting for pull.

Public helpers:
    push_tensor()            — mirror current .npz + .json to Redis
    resolve_cells()          — dict keyed by "F:P" -> verdict int
    resolve_cell(f, p)       — verdict int or None
    features() / projections()
    feature_meta(f) / projection_meta(p)
    feature_edges() / projection_edges()
    dims()                   — cardinalities + density + updated_at + version
    tail_updates(count=10)   — recent (F, P, verdict, source) change events

Redis key layout (base Redis: strings, hashes, lists, streams):
    tensor:version                 STRING  incremented on each push
    tensor:dims                    HASH    n_features, n_projections, density, updated_at
    tensor:features                LIST    ordered F-ids (row order)
    tensor:projections             LIST    ordered P-ids (col order)
    tensor:feature_meta:<F>        STRING  JSON: {label, tier, n_objects, description}
    tensor:projection_meta:<P>     STRING  JSON: {label, type, description}
    tensor:cells                   HASH    "F:P" -> verdict int string ("-2".."+2")
    tensor:feature_edges           STRING  JSON list of {from, to, relation, note}
    tensor:projection_edges        STRING  JSON list of {from, to, relation, note}
    tensor:updates                 STREAM  each xadd: {F, P, old, new, source, at}
"""
from .push import push_tensor, TENSOR_KEY_PREFIX
from .resolve import (
    resolve_cells, resolve_cell, resolve_row, resolve_column,
    features, projections,
    feature_meta, projection_meta, feature_edges, projection_edges,
    dims, tail_updates, get_version, reconstruct_matrix,
)

__all__ = [
    'push_tensor', 'TENSOR_KEY_PREFIX',
    'resolve_cells', 'resolve_cell', 'resolve_row', 'resolve_column',
    'features', 'projections',
    'feature_meta', 'projection_meta', 'feature_edges', 'projection_edges',
    'dims', 'tail_updates', 'get_version', 'reconstruct_matrix',
]
