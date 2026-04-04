"""Quick targeted query: how many zeros for specific EC L-functions?"""
import psycopg2
import json

conn = psycopg2.connect(
    host='devmirror.lmfdb.xyz', port=5432,
    dbname='lmfdb', user='lmfdb', password='lmfdb',
    connect_timeout=15
)
cur = conn.cursor()

# Try lfunc_data first — newer table, better indexed
print("=== Trying lfunc_data for specific labels ===")
for label in ['2-11-11.a-r0-0-0', '2-37-37.a-r1-0-0', '2-389-389.a-r2-0-0']:
    cur.execute("""
        SELECT label, array_length(positive_zeros_mid, 1)
        FROM lfunc_data WHERE label = %s
    """, (label,))
    row = cur.fetchone()
    if row:
        print(f"  {row[0]}: {row[1]} zeros")
    else:
        print(f"  {label}: not found")

# Try to find EC L-functions by origin pattern
print("\n=== Search by origin pattern ===")
cur.execute("""
    SELECT label, origin, 
           CASE WHEN positive_zeros IS NOT NULL 
                THEN jsonb_array_length(positive_zeros) END as n_zeros
    FROM lfunc_lfunctions
    WHERE origin LIKE 'EllipticCurve/Q/11%%'
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"  label={row[0]}, origin={row[1]}, n_zeros={row[2]}")

# Try the simpler approach - just grab a few by label pattern
print("\n=== L-functions with label starting with 2- (degree 2) ===")
cur.execute("""
    SELECT label, 
           CASE WHEN positive_zeros IS NOT NULL 
                THEN jsonb_array_length(positive_zeros) END as n_zeros
    FROM lfunc_lfunctions 
    WHERE label LIKE '2-11-%%'
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} zeros")

# Check lfunc_instances for EC linking
print("\n=== lfunc_instances for EllipticCurve ===")
cur.execute("""
    SELECT url, Lhash, type
    FROM lfunc_instances
    WHERE url LIKE 'EllipticCurve/Q/11/%%'
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"  url={row[0]}, Lhash={row[1]}, type={row[2]}")

conn.close()
