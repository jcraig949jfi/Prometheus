"""Check distribution of zero counts in lfunc_lfunctions for EC L-functions."""
import psycopg2

conn = psycopg2.connect(
    host='devmirror.lmfdb.xyz', port=5432,
    dbname='lmfdb', user='lmfdb', password='lmfdb',
    connect_timeout=15
)
cur = conn.cursor()

# Distribution of zero counts for EC L-functions (origin starts with EllipticCurve/Q)
print("=== Zero count distribution for EC L-functions ===")
cur.execute("""
    SELECT jsonb_array_length(positive_zeros) as n_zeros, COUNT(*)
    FROM lfunc_lfunctions
    WHERE origin LIKE 'EllipticCurve/Q/%%'
    AND positive_zeros IS NOT NULL
    GROUP BY jsonb_array_length(positive_zeros)
    ORDER BY 1
""")
total = 0
for row in cur.fetchall():
    print(f"  {row[0]:>3d} zeros: {row[1]:>6d} L-functions")
    total += row[1]
print(f"  Total: {total}")

# Same for modular forms
print("\n=== Zero count distribution for MF L-functions ===")
cur.execute("""
    SELECT jsonb_array_length(positive_zeros) as n_zeros, COUNT(*)
    FROM lfunc_lfunctions
    WHERE origin LIKE 'ModularForm/GL2/Q/%%'
    AND positive_zeros IS NOT NULL
    GROUP BY jsonb_array_length(positive_zeros)
    ORDER BY 1
""")
total = 0
for row in cur.fetchall():
    print(f"  {row[0]:>3d} zeros: {row[1]:>6d} L-functions")
    total += row[1]
print(f"  Total: {total}")

conn.close()
