"""Deep investigation of LMFDB zeros availability."""
import psycopg2

conn = psycopg2.connect(
    host='devmirror.lmfdb.xyz', port=5432,
    dbname='lmfdb', user='lmfdb', password='lmfdb',
    connect_timeout=15
)
cur = conn.cursor()

# lfunc_data: check for EC-related L-functions
print("=== lfunc_data sample records ===")
cur.execute("""
    SELECT label, degree, motivic_weight,
           array_length(positive_zeros_mid, 1) as n_zeros,
           conductor::text
    FROM lfunc_data
    WHERE degree = 2
    LIMIT 10
""")
for row in cur.fetchall():
    print(f"  {row[0]}: deg={row[1]}, mw={row[2]}, n_zeros={row[3]}, cond={row[4]}")

# lfunc_instances: check structure
print("\n=== lfunc_instances columns ===")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'lfunc_instances'
""")
for row in cur.fetchall():
    print(f"  {row[0]:30s} {row[1]}")

# Find EC-related instances
print("\n=== lfunc_instances for ECs ===")
cur.execute("""
    SELECT url, "Lhash", type
    FROM lfunc_instances
    WHERE url LIKE 'EllipticCurve/Q/11/%%'
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"  url={row[0]}, Lhash={row[1]}, type={row[2]}")

# Now look up that Lhash in lfunc_data
print("\n=== lfunc_data for EC 11.a via instance ===")
cur.execute("""
    SELECT ld.label, array_length(ld.positive_zeros_mid, 1) as n_zeros,
           ld.conductor::text, ld.degree
    FROM lfunc_data ld
    JOIN lfunc_instances li ON ld.label = li."Lhash"
    WHERE li.url = 'EllipticCurve/Q/11/a'
""")
for row in cur.fetchall():
    print(f"  label={row[0]}, n_zeros={row[1]}, cond={row[2]}, deg={row[3]}")

# Try: lfunc_data zero counts for degree 2
print("\n=== lfunc_data zero counts (degree=2, sample) ===")
cur.execute("""
    SELECT label, array_length(positive_zeros_mid, 1) as n_zeros
    FROM lfunc_data
    WHERE degree = 2
    AND positive_zeros_mid IS NOT NULL
    ORDER BY conductor
    LIMIT 20
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} zeros")

# Get the actual zeros for one
print("\n=== Zeros for first degree-2 L-function ===")
cur.execute("""
    SELECT label, positive_zeros_mid[1:5], array_length(positive_zeros_mid, 1)
    FROM lfunc_data
    WHERE degree = 2 AND positive_zeros_mid IS NOT NULL
    LIMIT 1
""")
row = cur.fetchone()
if row:
    print(f"  label={row[0]}, first 5 zeros={row[1]}, total={row[2]}")

conn.close()
