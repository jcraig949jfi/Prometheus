"""Check how many zeros are available for EC and MF L-functions in LMFDB."""
import psycopg2
import json

conn = psycopg2.connect(
    host='devmirror.lmfdb.xyz', port=5432,
    dbname='lmfdb', user='lmfdb', password='lmfdb',
    connect_timeout=15
)
cur = conn.cursor()

# Check lfunc_lfunctions for EC L-functions: how many zeros?
print("=== EC L-function zeros (via lfunc_lfunctions, degree=2, motivic_weight=1) ===")
cur.execute("""
    SELECT label, jsonb_array_length(positive_zeros) as n_zeros
    FROM lfunc_lfunctions
    WHERE degree = 2 AND motivic_weight = 1
    AND positive_zeros IS NOT NULL
    ORDER BY conductor
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} zeros")

# Distribution of zero counts for degree=2, motivic_weight=1
print("\n=== Distribution of zero counts (EC L-functions) ===")
cur.execute("""
    SELECT jsonb_array_length(positive_zeros) as n_zeros, COUNT(*)
    FROM lfunc_lfunctions
    WHERE degree = 2 AND motivic_weight = 1
    AND positive_zeros IS NOT NULL
    GROUP BY jsonb_array_length(positive_zeros)
    ORDER BY 1
    LIMIT 20
""")
for row in cur.fetchall():
    print(f"  {row[0]} zeros: {row[1]} L-functions")

# Check lfunc_data for the same (new table)
print("\n=== lfunc_data: zeros availability ===")
cur.execute("""
    SELECT label, array_length(positive_zeros_mid, 1) as n_zeros
    FROM lfunc_data
    WHERE degree = 2 AND motivic_weight = 1
    AND positive_zeros_mid IS NOT NULL
    ORDER BY conductor
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} zeros")

# Sample: get 100+ zeros for a well-known EC
print("\n=== Sample: zeros for 2-11-11.a-r0-0-0 (11.a) ===")
cur.execute("""
    SELECT positive_zeros 
    FROM lfunc_lfunctions 
    WHERE label LIKE '2-11-%%'
    LIMIT 1
""")
row = cur.fetchone()
if row and row[0]:
    zeros = row[0]
    print(f"  Total zeros stored: {len(zeros)}")
    print(f"  First 5: {zeros[:5]}")
    print(f"  Last 5: {zeros[-5:]}")

# Check lfunc_instances to link EC labels to L-function labels
print("\n=== lfunc_instances sample ===")
cur.execute("""
    SELECT * FROM lfunc_instances LIMIT 5
""")
desc = cur.description
for row in cur.fetchall():
    for d, v in zip(desc, row):
        print(f"  {d.name}: {str(v)[:80]}")
    print()

conn.close()
