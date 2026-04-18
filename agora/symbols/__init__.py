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
from .push import push_symbol
from .resolve import resolve, resolve_meta, by_type, refs_to, all_symbols

__all__ = [
    'parse_md', 'load_symbol',
    'push_symbol',
    'resolve', 'resolve_meta', 'by_type', 'refs_to', 'all_symbols',
]
