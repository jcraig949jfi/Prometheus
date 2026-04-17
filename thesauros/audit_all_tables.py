"""
Comprehensive data audit across prometheus_sci, prometheus_fire, and lmfdb.

For every populated table, checks:
  1. Row count
  2. For each column: NULL %, distinct count, sample values
  3. For array columns: length distribution (uniformity = suspect)
  4. For numeric columns: % zeros (default-value smell)
  5. For text columns: % empty strings
  6. Constant columns (distinct=1) get flagged — often metadata-masquerading-as-data

Output: thesauros/audit_report_20260416.md

This is the P-009-pattern detector: if zeros tables had uniform length 24
across 120K rows with metadata in positions 21-24, the same disease could
exist in any table that was migrated from fixed-format source.
"""
import psycopg2
import json
from pathlib import Path
from datetime import datetime

import os
_which = os.environ.get('AUDIT_DB', 'all')
_full = {
    'prometheus_sci': dict(host='localhost', port=5432, dbname='prometheus_sci',
                           user='postgres', password='prometheus'),
    'prometheus_fire': dict(host='localhost', port=5432, dbname='prometheus_fire',
                            user='postgres', password='prometheus'),
}
if _which == 'all':
    DBS = _full
else:
    DBS = {_which: _full[_which]}

REPORT = Path(__file__).parent / "audit_report_20260416.md"


def audit_table(cur, schema, table):
    """Audit a single table. Returns dict of findings."""
    full = f'"{schema}"."{table}"'
    findings = {'schema': schema, 'table': table, 'columns': [], 'issues': []}

    # Row count
    try:
        cur.execute(f"SELECT count(*) FROM {full}")
        row_count = cur.fetchone()[0]
    except Exception as e:
        findings['issues'].append(f"ERROR reading row count: {e}")
        cur.connection.rollback()
        return findings
    findings['row_count'] = row_count
    if row_count == 0:
        findings['issues'].append("EMPTY table")
        return findings

    # Column metadata
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
    """, (schema, table))
    cols = cur.fetchall()

    for colname, dtype in cols:
        col_info = {'name': colname, 'type': dtype, 'flags': []}

        # NULL percentage
        try:
            cur.execute(f'SELECT count(*) FILTER (WHERE "{colname}" IS NULL) FROM {full}')
            null_count = cur.fetchone()[0]
        except Exception as e:
            col_info['flags'].append(f"NULL_check_error: {e}")
            cur.connection.rollback()
            findings['columns'].append(col_info)
            continue

        col_info['null_pct'] = 100.0 * null_count / row_count if row_count else 0
        if col_info['null_pct'] > 95:
            col_info['flags'].append(f"MOSTLY_NULL ({col_info['null_pct']:.0f}%)")
        elif col_info['null_pct'] == 100.0:
            col_info['flags'].append("ALL_NULL")

        # Skip more checks if all-null
        if null_count == row_count:
            findings['columns'].append(col_info)
            continue

        # Distinct count
        try:
            cur.execute(f'SELECT count(DISTINCT "{colname}") FROM {full}')
            distinct_count = cur.fetchone()[0]
        except Exception as e:
            col_info['flags'].append(f"distinct_check_error: {e}")
            cur.connection.rollback()
            findings['columns'].append(col_info)
            continue
        col_info['distinct_count'] = distinct_count

        if distinct_count == 1:
            # Get the constant value
            try:
                cur.execute(f'SELECT "{colname}" FROM {full} WHERE "{colname}" IS NOT NULL LIMIT 1')
                const_val = cur.fetchone()[0]
                col_info['flags'].append(f"CONSTANT (always {repr(const_val)[:80]})")
            except Exception:
                cur.connection.rollback()
                col_info['flags'].append("CONSTANT")

        # Numeric: check 0 percentage
        if dtype in ('integer', 'bigint', 'smallint', 'double precision', 'real', 'numeric'):
            try:
                cur.execute(f'SELECT count(*) FILTER (WHERE "{colname}" = 0) FROM {full}')
                zero_count = cur.fetchone()[0]
                zero_pct = 100.0 * zero_count / row_count
                if zero_pct > 95 and distinct_count > 1:
                    col_info['flags'].append(f"MOSTLY_ZERO ({zero_pct:.0f}%)")
                col_info['zero_pct'] = zero_pct
            except Exception:
                cur.connection.rollback()

        # Text: check empty-string percentage
        if dtype == 'text' or dtype.startswith('character'):
            try:
                cur.execute(f'SELECT count(*) FILTER (WHERE "{colname}" = \'\') FROM {full}')
                empty_count = cur.fetchone()[0]
                empty_pct = 100.0 * empty_count / row_count
                if empty_pct > 50:
                    col_info['flags'].append(f"MOSTLY_EMPTY_STR ({empty_pct:.0f}%)")
                col_info['empty_str_pct'] = empty_pct
            except Exception:
                cur.connection.rollback()

        # Array: check length uniformity (P-009 smell)
        if dtype == 'ARRAY':
            try:
                cur.execute(f"""
                    SELECT
                        min(array_length("{colname}", 1)),
                        max(array_length("{colname}", 1)),
                        count(DISTINCT array_length("{colname}", 1))
                    FROM {full} WHERE "{colname}" IS NOT NULL
                """)
                min_len, max_len, distinct_lens = cur.fetchone()
                col_info['array_min_len'] = min_len
                col_info['array_max_len'] = max_len
                col_info['array_distinct_lens'] = distinct_lens
                if distinct_lens == 1 and min_len >= 10:
                    col_info['flags'].append(
                        f"UNIFORM_ARRAY_LEN ({min_len}) — P-009 pattern candidate; check for padding/metadata"
                    )
                elif distinct_lens <= 3 and min_len >= 10:
                    col_info['flags'].append(
                        f"NEAR_UNIFORM_ARRAY_LEN ({distinct_lens} distinct lengths in [{min_len}, {max_len}])"
                    )
            except Exception as e:
                cur.connection.rollback()
                col_info['flags'].append(f"array_length_check_error: {type(e).__name__}")

        # Sample 3 values (for text and non-array types)
        if dtype not in ('ARRAY', 'jsonb'):
            try:
                cur.execute(f'SELECT "{colname}" FROM {full} WHERE "{colname}" IS NOT NULL LIMIT 3')
                samples = [repr(r[0])[:60] for r in cur.fetchall()]
                col_info['samples'] = samples
            except Exception:
                cur.connection.rollback()

        findings['columns'].append(col_info)

    return findings


def format_report(results):
    """Format findings into markdown."""
    lines = ["# Data Audit Report — 2026-04-16",
             "",
             "Comprehensive audit of prometheus_sci and prometheus_fire tables.",
             "Flags suspicious patterns: uniform array lengths (P-009 pattern), constant columns, mostly-null, mostly-zero, mostly-empty-string.",
             "",
             f"Generated: {datetime.now().isoformat()}",
             "",
             "---",
             ""]

    # Summary first
    total_issues = sum(len(t['columns']) for db in results.values() for t in db)
    total_flagged = sum(
        1 for db in results.values() for t in db
        for c in t.get('columns', []) if c.get('flags')
    )
    lines.append(f"## Summary")
    lines.append(f"- Databases audited: {len(results)}")
    lines.append(f"- Total tables: {sum(len(v) for v in results.values())}")
    lines.append(f"- Total columns: {total_issues}")
    lines.append(f"- Flagged columns: {total_flagged}")
    lines.append("")

    # Per-database sections
    for dbname, tables in results.items():
        lines.append(f"## {dbname}")
        lines.append("")
        for t in tables:
            rc = t.get('row_count', 0)
            schema_table = f"{t['schema']}.{t['table']}"
            issues = t.get('issues', [])
            flagged_cols = [c for c in t.get('columns', []) if c.get('flags')]

            if rc == 0 and not issues:
                continue  # skip empty tables entirely

            status = "EMPTY" if rc == 0 else f"{rc:,} rows"
            if flagged_cols:
                status += f" — **{len(flagged_cols)} flagged columns**"

            lines.append(f"### {schema_table} ({status})")
            lines.append("")

            if issues:
                for iss in issues:
                    lines.append(f"- **ISSUE:** {iss}")
                lines.append("")

            if flagged_cols:
                lines.append("| Column | Type | NULL% | Flags |")
                lines.append("|--------|------|-------|-------|")
                for c in flagged_cols:
                    flags_str = "; ".join(c['flags'])
                    null_pct = c.get('null_pct', 0)
                    lines.append(f"| `{c['name']}` | {c['type']} | {null_pct:.0f}% | {flags_str} |")
                lines.append("")

        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    import time
    start = time.time()
    results = {}

    for dbname, dsn in DBS.items():
        print(f"\n=== Auditing {dbname} ===")
        conn = psycopg2.connect(**dsn)
        cur = conn.cursor()

        cur.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
              AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name
        """)
        tables = cur.fetchall()
        print(f"Found {len(tables)} tables")

        db_results = []
        for schema, table in tables:
            print(f"  {schema}.{table}...", end=" ", flush=True)
            t0 = time.time()
            finding = audit_table(cur, schema, table)
            elapsed = time.time() - t0
            flags = sum(1 for c in finding.get('columns', []) if c.get('flags'))
            rc = finding.get('row_count', 0)
            print(f"{rc:,} rows, {flags} flagged ({elapsed:.1f}s)")
            db_results.append(finding)

        results[dbname] = db_results
        conn.close()

    # Write report
    REPORT.write_text(format_report(results), encoding='utf-8')
    print(f"\nReport written to {REPORT}")
    print(f"Total audit time: {time.time()-start:.0f}s")

    # Also save raw JSON for follow-up processing
    json_path = REPORT.with_suffix('.json')
    json_path.write_text(json.dumps(results, default=str, indent=2))
    print(f"Raw data: {json_path}")
