"""Quick sample: grab zeros for a few known ECs via Lhash."""
import psycopg2

conn = psycopg2.connect(
    host='devmirror.lmfdb.xyz', port=5432,
    dbname='lmfdb', user='lmfdb', password='lmfdb',
    connect_timeout=15
)
cur = conn.cursor()

# Get Lhash values for some EC L-functions
print("=== Getting Lhash for ECs ===")
cur.execute("""
    SELECT url, "Lhash"
    FROM lfunc_instances
    WHERE type = 'ECQ'
    AND url LIKE 'EllipticCurve/Q/%%'
    LIMIT 20
""")
instances = cur.fetchall()
for row in instances:
    print(f"  {row[0]}: Lhash={row[1]}")

# Now look up zeros for these Lhash values in lfunc_lfunctions
print("\n=== Zeros for these L-functions ===")
for url, lhash in instances[:10]:
    cur.execute("""
        SELECT "Lhash", jsonb_array_length(positive_zeros), 
               conductor::text, order_of_vanishing
        FROM lfunc_lfunctions
        WHERE "Lhash" = %s
    """, (lhash,))
    row = cur.fetchone()
    if row:
        print(f"  {url}: n_zeros={row[1]}, cond={row[2]}, rank={row[3]}")
    else:
        print(f"  {url}: NOT FOUND in lfunc_lfunctions")

# Get actual zero values for one
print("\n=== Full zeros for EC 11.a ===")
cur.execute("""
    SELECT positive_zeros
    FROM lfunc_lfunctions
    WHERE "Lhash" = %s
""", (instances[0][1],))
row = cur.fetchone()
if row and row[0]:
    zeros = row[0]
    print(f"  {instances[0][0]}: {len(zeros)} zeros")
    for i, z in enumerate(zeros):
        print(f"    z[{i}] = {z}")

conn.close()
