"""Dataset snapshot + resolution primitives for the idempotence mandate.

See harmonia/memory/symbols/protocols/dataset_snapshot_v1.md for the protocol.

Core discipline: a `dataset` symbol at version >= 2 carries a `snapshot` block
containing a content hash of the rows the symbol's canonical query returns at
a specific instant. Two agents running the same symbol at different times and
on different machines get the same rows iff the snapshot matches. If it doesn't,
they are not running against the same data and the SIGNATURE is not
reproducible.

Public helpers:
    canonicalize(df) -> bytes           # stable CSV serialization
    hash_dataset(df) -> str             # sha256 of canonicalization
    capture_snapshot(sql, conn) -> dict # run SQL, hash results, return snapshot dict
    verify_snapshot(sql, conn, expected_hash) -> dict  # re-run and compare
"""
from .snapshot import (
    canonicalize,
    hash_dataset,
    capture_snapshot,
    verify_snapshot,
)

__all__ = [
    'canonicalize', 'hash_dataset',
    'capture_snapshot', 'verify_snapshot',
]
