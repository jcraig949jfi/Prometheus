"""Symbol registry — shared agent vocabulary via Redis (base operations only).

See harmonia/memory/symbols/README.md for schema + promotion policy.

Public helpers:
    push_symbol(md_path) — parse MD, write to Redis (promotion step)
    resolve(name) — GET full JSON def from Redis
    resolve_meta(name) — HGETALL frontmatter hash
    by_type(type) — SMEMBERS names of that type
    refs_to(id_or_name) — SMEMBERS names that reference this id
    all_symbols() — SMEMBERS symbols:all

Redis key layout (base-Redis only: strings, hashes, sets):
    symbols:all                     SET of promoted names
    symbols:<NAME>:meta             HASH of frontmatter fields (flat strings)
    symbols:<NAME>:def              STRING containing full JSON blob
    symbols:by_type:<type>          SET of names
    symbols:refs:<id>               SET of symbol names referencing <id>
"""
from .parse import parse_md, load_symbol
from .push import (
    push_symbol, update_status,
    SymbolValidationError, SymbolImmutabilityError,
)
from .resolve import (
    resolve, resolve_at, resolve_meta,
    get_latest_version, all_versions, check_version,
    get_status, get_successor, SymbolArchivedError,
    reset_cross_version_tracker,
    by_type, refs_to, refs_to_any, all_symbols, exists,
    parse_reference, validate_reference_string,
)
from .manifest import (
    parse_session_manifest, resolve_with_manifest,
    expand_references, contract_references,
    find_conflicts, manifest_frontmatter, round_trip_ok,
    CrossVersionConflict,
)

__all__ = [
    'parse_md', 'load_symbol',
    'push_symbol', 'update_status',
    'SymbolValidationError', 'SymbolImmutabilityError', 'SymbolArchivedError',
    'resolve', 'resolve_at', 'resolve_meta',
    'get_latest_version', 'all_versions', 'check_version',
    'get_status', 'get_successor',
    'by_type', 'refs_to', 'refs_to_any', 'all_symbols', 'exists',
    'parse_reference', 'validate_reference_string',
    # T1 session manifest
    'parse_session_manifest', 'resolve_with_manifest',
    'expand_references', 'contract_references',
    'find_conflicts', 'manifest_frontmatter', 'round_trip_ok',
    'CrossVersionConflict',
    # T3 cross-version tracker
    'reset_cross_version_tracker',
]
