"""CLI: capture or verify a dataset snapshot against the LMFDB mirror.

Usage:
    python -m agora.datasets capture Q_EC_R0_D5     # run the query, compute hash, print YAML snapshot block
    python -m agora.datasets verify Q_EC_R0_D5      # compare current query result to the promoted snapshot

The capture command does NOT modify the symbol MD file. It prints the
snapshot block to stdout so the operator can paste it into the MD and
promote a new dataset symbol version (e.g. Q_EC_R0_D5@v2).

The verify command reports MATCH / DRIFT and exits with code 0 / 1.
"""
import argparse
import json
import os
import sys

from . import capture_snapshot, verify_snapshot


def _get_conn():
    """Connect to the LMFDB Postgres mirror using standard env credentials.

    Env vars:
        AGORA_PG_HOST     (default 192.168.1.176)
        AGORA_PG_PORT     (default 5432)
        AGORA_PG_DB       (default prometheus_sci)
        AGORA_PG_USER     (required)
        AGORA_PG_PASSWORD (required)
    """
    try:
        import psycopg2
    except ImportError:
        raise ImportError('capture/verify requires psycopg2-binary')
    host = os.environ.get('AGORA_PG_HOST', '192.168.1.176')
    port = int(os.environ.get('AGORA_PG_PORT', '5432'))
    dbname = os.environ.get('AGORA_PG_DB', 'prometheus_sci')
    user = os.environ.get('AGORA_PG_USER')
    password = os.environ.get('AGORA_PG_PASSWORD')
    if not user or not password:
        raise RuntimeError('set AGORA_PG_USER and AGORA_PG_PASSWORD env vars')
    return psycopg2.connect(
        host=host, port=port, dbname=dbname, user=user, password=password,
    )


def _load_dataset_symbol(name):
    """Load a dataset symbol via agora.symbols."""
    try:
        from agora.symbols import resolve
    except ImportError:
        raise ImportError('agora.symbols not importable from project root')
    sym = resolve(name)
    if sym is None:
        # Try reading the MD directly (pre-promoted drafts)
        from agora.symbols.parse import load_symbol
        from pathlib import Path
        candidate = Path('harmonia/memory/symbols') / f'{name}.md'
        if candidate.exists():
            return load_symbol(candidate)
        raise RuntimeError(f'symbol {name!r} not found in Redis or on disk')
    return sym


def _extract_canonical_sql(sym):
    """Pull the canonical SQL from a dataset symbol.

    By convention the SQL lives in a 'Data / implementation' section or a
    'Canonical SQL' section, as a fenced code block with language 'sql'.
    """
    sections = sym.get('sections', {})
    for key in ('Data / implementation', 'Canonical SQL', 'Data', 'Implementation'):
        body = sections.get(key)
        if not body:
            continue
        # Find ```sql ... ``` fence
        if '```sql' in body:
            start = body.find('```sql') + len('```sql')
            end = body.find('```', start)
            if end > start:
                return body[start:end].strip()
    raise RuntimeError('canonical SQL not found in symbol sections')


def cmd_capture(args):
    sym = _load_dataset_symbol(args.name)
    sql = _extract_canonical_sql(sym)
    conn = _get_conn()
    try:
        snapshot = capture_snapshot(sql, conn, sample_note=args.note or '')
    finally:
        conn.close()
    # Emit as YAML-like block suitable for pasting into symbol frontmatter
    print('# Paste this snapshot block into the dataset symbol frontmatter:')
    print('snapshot:')
    for key in ('type', 'value', 'captured_at', 'n_rows_exact', 'n_columns',
                'canonicalization', 'sample_note', 'bytes_size'):
        print(f'  {key}: {snapshot[key]!r}' if isinstance(snapshot[key], str)
              else f'  {key}: {snapshot[key]}')
    print('  columns_sorted:')
    for col in snapshot['columns_sorted']:
        print(f'    - {col}')
    # Also emit JSON for machine consumption
    if args.json:
        print()
        print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


def cmd_verify(args):
    sym = _load_dataset_symbol(args.name)
    sql = _extract_canonical_sql(sym)
    snapshot = sym.get('sections', {}).get('snapshot')  # parse-level
    # Fall back to frontmatter-stored snapshot dict
    snap_obj = sym.get('snapshot')
    if snap_obj is None:
        # maybe the symbol has a top-level 'snapshot' in its frontmatter;
        # our parser may have surfaced it differently
        raise RuntimeError(
            f'symbol {args.name!r} has no snapshot block; either it predates '
            'snapshot discipline (v1) or the parser did not surface it'
        )
    expected_hash = snap_obj.get('value')
    expected_n_rows = snap_obj.get('n_rows_exact')
    conn = _get_conn()
    try:
        result = verify_snapshot(sql, conn, expected_hash, expected_n_rows)
    finally:
        conn.close()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['match'] else 1


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd', required=True)

    cap = sub.add_parser('capture', help='capture snapshot from a dataset symbol')
    cap.add_argument('name', help='dataset symbol name (e.g. Q_EC_R0_D5)')
    cap.add_argument('--note', default='', help='free-text sample_note')
    cap.add_argument('--json', action='store_true', help='also emit JSON')

    ver = sub.add_parser('verify', help='verify current DB state against promoted snapshot')
    ver.add_argument('name', help='dataset symbol name')

    args = parser.parse_args(argv[1:])
    if args.cmd == 'capture':
        return cmd_capture(args)
    if args.cmd == 'verify':
        return cmd_verify(args)
    parser.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
