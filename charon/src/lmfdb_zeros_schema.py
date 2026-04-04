"""Explore LMFDB PostgreSQL mirror to find where zeros are stored."""
import psycopg2

conn = psycopg2.connect(
    host='devmirror.lmfdb.xyz', port=5432,
    dbname='lmfdb', user='lmfdb', password='lmfdb',
    connect_timeout=15
)
cur = conn.cursor()

# Check lfunc_lfunctions columns
print("=== lfunc_lfunctions columns ===")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'lfunc_lfunctions'
    ORDER BY ordinal_position
""")
for row in cur.fetchall():
    print(f"  {row[0]:30s} {row[1]}")

# Check lfunc_data columns
print("\n=== lfunc_data columns ===")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'lfunc_data'
    ORDER BY ordinal_position
""")
for row in cur.fetchall():
    print(f"  {row[0]:30s} {row[1]}")

# Sample from lfunc_lfunctions to see zeros
print("\n=== Sample from lfunc_lfunctions (zero-related cols) ===")
cur.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'lfunc_lfunctions'
    AND column_name LIKE '%%zero%%'
""")
zero_cols = [r[0] for r in cur.fetchall()]
print(f"  Zero columns: {zero_cols}")

if zero_cols:
    cols = ', '.join(zero_cols)
    cur.execute(f"SELECT {cols} FROM lfunc_lfunctions LIMIT 1")
    row = cur.fetchone()
    for c, v in zip(zero_cols, row):
        val_str = str(v)[:200] if v else 'None'
        print(f"  {c}: {val_str}")

# Check if zeros are in a separate column
print("\n=== All lfunc columns with 'z' ===")
cur.execute("""
    SELECT column_name, data_type FROM information_schema.columns 
    WHERE table_name = 'lfunc_lfunctions'
    AND (column_name LIKE '%%z%%' OR column_name LIKE '%%positive%%')
""")
for row in cur.fetchall():
    print(f"  {row[0]:30s} {row[1]}")

# Sample a record
print("\n=== Sample lfunc_lfunctions record (first few cols) ===")
cur.execute("SELECT * FROM lfunc_lfunctions LIMIT 1")
desc = cur.description
row = cur.fetchone()
for d, v in zip(desc, row):
    val_str = str(v)[:100] if v else 'None'
    print(f"  {d.name:30s}: {val_str}")

conn.close()
