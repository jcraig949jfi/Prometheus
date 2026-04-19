r"""Canonical serialization + hashing for dataset snapshots.

Design goals:
- byte-deterministic across Python versions on the same data
- byte-deterministic across platforms (Windows / POSIX)
- portable to a second implementation without importing this module
  (the spec is simple enough to reimplement)
- stable under column reorder (snapshot hash depends on column NAMES,
  not column positions — the canonical form sorts columns alphabetically)

Canonicalization spec (v1):
    1. Sort DataFrame columns alphabetically by column name
    2. For each row in the DataFrame's existing row order (do NOT resort rows;
       the canonical SQL is expected to ORDER BY deterministic columns):
       a. For each column in alpha order:
          - float: render with repr() (Python's round-trip stable form)
          - pd.NA or None or nan: render as the literal string "null"
          - int: render as str(value)
          - str: double-quoted, with backslash, double-quote, newline, tab escaped
          - list/array (e.g. bad_primes): JSON with sort_keys=True
          - dict: JSON with sort_keys=True
          - other: error with descriptive message
       b. Join column values with tab
    3. Join rows with newline
    4. Encode as UTF-8 bytes
    5. sha256 the result

If this spec proves insufficient we bump to v2 canonicalization; the current
snapshot block records which canonicalization version was used.
"""
import hashlib
import json
from datetime import datetime, timezone


CANONICALIZATION_VERSION = 'agora_csv_jsonl_v1'


def _render_cell(value):
    """Render one cell value as a deterministic string."""
    if value is None:
        return 'null'
    try:
        import pandas as pd
        if pd.isna(value):
            return 'null'
    except Exception:
        pass
    if isinstance(value, float):
        # repr() is round-trip stable and locale-independent
        return repr(value)
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        # Double-quote and escape backslash / double-quote / newline / tab
        escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
        return '"' + escaped + '"'
    if isinstance(value, (list, tuple)):
        # Recursively render each element; whole array rendered as JSON
        return json.dumps(list(value), sort_keys=True, separators=(',', ':'), default=_json_default)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(',', ':'), default=_json_default)
    # Unknown type — last-resort stringify with class name for auditability
    return json.dumps({'_type': type(value).__name__, '_repr': repr(value)}, sort_keys=True)


def _json_default(v):
    """JSON fallback for non-serializable types."""
    try:
        import numpy as np
        if isinstance(v, np.integer):
            return int(v)
        if isinstance(v, np.floating):
            return float(v)
        if isinstance(v, np.ndarray):
            return v.tolist()
    except ImportError:
        pass
    return str(v)


def canonicalize(df):
    """Serialize a pandas DataFrame to deterministic UTF-8 bytes."""
    try:
        import pandas as pd  # noqa: F401
    except ImportError:
        raise ImportError('canonicalize() requires pandas')

    if df is None or len(df.columns) == 0:
        return b''

    sorted_cols = sorted(df.columns)
    header = '\t'.join(sorted_cols)
    lines = [header]
    for _, row in df.iterrows():
        cells = [_render_cell(row[c]) for c in sorted_cols]
        lines.append('\t'.join(cells))
    text = '\n'.join(lines)
    return text.encode('utf-8')


def hash_dataset(df):
    """Return sha256 hex of canonicalized dataset bytes."""
    return hashlib.sha256(canonicalize(df)).hexdigest()


def capture_snapshot(sql, conn, canonicalization=CANONICALIZATION_VERSION, sample_note=''):
    """Execute SQL, canonicalize results, return snapshot dict ready for symbol frontmatter.

    Returns:
        {
            'type': 'row_bytes_sha256',
            'value': '<64-hex-char sha256>',
            'captured_at': '<ISO-8601 UTC>',
            'n_rows_exact': int,
            'n_columns': int,
            'columns_sorted': [...],
            'canonicalization': 'agora_csv_jsonl_v1',
            'sample_note': <free-text>,
            'bytes_size': int,
        }
    """
    import pandas as pd
    df = pd.read_sql(sql, conn)
    n_rows = len(df)
    n_cols = len(df.columns)
    sorted_cols = sorted(df.columns)
    raw = canonicalize(df)
    digest = hashlib.sha256(raw).hexdigest()
    return {
        'type': 'row_bytes_sha256',
        'value': digest,
        'captured_at': datetime.now(timezone.utc).isoformat(),
        'n_rows_exact': n_rows,
        'n_columns': n_cols,
        'columns_sorted': sorted_cols,
        'canonicalization': canonicalization,
        'sample_note': sample_note,
        'bytes_size': len(raw),
    }


def verify_snapshot(sql, conn, expected_hash, expected_n_rows=None):
    """Re-run SQL and check whether current result matches expected snapshot.

    Returns a dict:
        {
            'match': bool,
            'actual_hash': '<64-hex>',
            'expected_hash': '<64-hex>',
            'actual_n_rows': int,
            'expected_n_rows': int or None,
            'checked_at': '<ISO-8601>',
        }

    A mismatch is not automatically an error — it may mean the underlying data
    source has updated. Caller decides whether to treat as drift or as failure.
    """
    import pandas as pd
    df = pd.read_sql(sql, conn)
    actual = hashlib.sha256(canonicalize(df)).hexdigest()
    match = (actual == expected_hash)
    if match and expected_n_rows is not None:
        match = match and (len(df) == expected_n_rows)
    return {
        'match': match,
        'actual_hash': actual,
        'expected_hash': expected_hash,
        'actual_n_rows': len(df),
        'expected_n_rows': expected_n_rows,
        'checked_at': datetime.now(timezone.utc).isoformat(),
    }
