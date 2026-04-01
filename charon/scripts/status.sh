#!/usr/bin/env bash
# Charon status dashboard — quick check on the landscape state
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

python -c "
import duckdb
from charon.src.config import DB_PATH

con = duckdb.connect(str(DB_PATH), read_only=True)

print('=' * 60)
print('CHARON LANDSCAPE STATUS')
print('=' * 60)

# Object counts
for row in con.execute('''
    SELECT object_type, COUNT(*), AVG(coefficient_completeness)
    FROM objects GROUP BY object_type ORDER BY object_type
''').fetchall():
    print(f'  {row[0]:20s}: {row[1]:>8,} objects, avg completeness {row[2]:.1%}')

total = con.execute('SELECT COUNT(*) FROM objects').fetchone()[0]
print(f'  {\"TOTAL\":20s}: {total:>8,}')

# Bridges
bridges = con.execute('SELECT COUNT(*) FROM known_bridges').fetchone()[0]
print(f'\n  Known bridges:       {bridges:>8,}')

# Landscape
landscape = con.execute('SELECT COUNT(*) FROM landscape').fetchone()[0]
if landscape > 0:
    clusters = con.execute('SELECT COUNT(DISTINCT cluster_id) FROM landscape').fetchone()[0]
    print(f'  Landscape points:    {landscape:>8,}')
    print(f'  Clusters:            {clusters:>8,}')

# Hypothesis queue
hyp = con.execute('''SELECT status, COUNT(*) FROM hypothesis_queue GROUP BY status''').fetchall()
if hyp:
    print(f'\n  Hypothesis queue:')
    for row in hyp:
        print(f'    {row[0]:15s}: {row[1]:>6,}')

# Failures
failures = con.execute('''SELECT failure_type, COUNT(*) FROM failure_log GROUP BY failure_type''').fetchall()
if failures:
    print(f'\n  Failure log:')
    for row in failures:
        print(f'    {row[0]:20s}: {row[1]:>6,}')

# Ingestion log
latest = con.execute('''SELECT source_table, rows_inserted, status, completed_at
    FROM ingestion_log ORDER BY id DESC LIMIT 5''').fetchall()
if latest:
    print(f'\n  Recent ingestions:')
    for row in latest:
        print(f'    {row[0]:30s}: {row[1] or 0:>8,} rows [{row[2]}]')

print('=' * 60)
con.close()
"
