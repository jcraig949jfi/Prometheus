"""Storage benchmark: Zarr + Kuzu + DuckDB at scale."""
import time, os, shutil
import numpy as np
import psutil

process = psutil.Process(os.getpid())
def mem_mb():
    return process.memory_info().rss / 1024 / 1024

print("=== STORAGE BENCHMARK ===")
print(f"Baseline memory: {mem_mb():.0f} MB")

# Test data
N_ORGANISMS = 100
N_FEATURES = 50
N_COMPOSITIONS = 100_000

features = np.random.randn(N_ORGANISMS, N_FEATURES).astype(np.float32)
scores = np.random.rand(N_COMPOSITIONS).astype(np.float32)
signatures = np.random.randn(N_COMPOSITIONS, N_FEATURES).astype(np.float32)
keys = [f"chain_{i}" for i in range(N_COMPOSITIONS)]

print(f"Test data: {N_ORGANISMS} organisms, {N_COMPOSITIONS:,} compositions")
print(f"Memory after gen: {mem_mb():.0f} MB")
print()

# ============================================================
# ZARR
# ============================================================
import zarr

zarr_path = "organisms/_bench.zarr"
shutil.rmtree(zarr_path, ignore_errors=True)
print("--- ZARR v3 (tensor storage) ---")

t0 = time.time()
root = zarr.open_group(zarr_path, mode="w")
root.create_array("features", data=features)
root.create_array("scores", data=scores)
root.create_array("signatures", data=signatures, chunks=(10000, N_FEATURES))
print(f"  Write 100K: {time.time()-t0:.3f}s")

t0 = time.time()
root2 = zarr.open_group(zarr_path, mode="r")
f = np.array(root2["features"])
s = np.array(root2["scores"])
g = np.array(root2["signatures"])
print(f"  Read all: {time.time()-t0:.3f}s")

t0 = time.time()
# Zarr v3: resize + write instead of append
root_rw = zarr.open_group(zarr_path, mode="r+")
old_len = root_rw["scores"].shape[0]
root_rw["scores"].resize(old_len + 1000)
root_rw["scores"][old_len:] = np.random.rand(1000).astype(np.float32)
print(f"  Append 1K: {time.time()-t0:.3f}s")

t0 = time.time()
top_idx = np.argsort(s)[-100:]
top_sigs = g[top_idx]
print(f"  Slice top 100: {time.time()-t0:.3f}s")

# Checkpoint save (re-write entire dataset)
t0 = time.time()
root_rw.create_array("scores_checkpoint", data=scores, overwrite=True)
print(f"  Checkpoint save 100K scores: {time.time()-t0:.3f}s")

sz = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(zarr_path) for f in fn)
print(f"  Disk: {sz/1024/1024:.1f} MB | Memory: {mem_mb():.0f} MB")
shutil.rmtree(zarr_path, ignore_errors=True)
print()

# ============================================================
# DUCKDB
# ============================================================
import duckdb

duck_path = "organisms/_bench.duckdb"
if os.path.exists(duck_path):
    os.remove(duck_path)
print("--- DUCKDB (analytical queries) ---")

ddb = duckdb.connect(duck_path)
ddb.execute("""CREATE TABLE compositions (
    id INTEGER, chain_key VARCHAR, score FLOAT,
    novelty FLOAT, resonance FLOAT, cycle INTEGER
)""")

# Bulk insert via numpy arrays (much faster than executemany)
t0 = time.time()
ddb.execute("""INSERT INTO compositions
    SELECT i, 'chain_' || i::VARCHAR, s, n, r, i / 500
    FROM (SELECT unnest(range(100000)) as i,
          unnest($1) as s, unnest($2) as n, unnest($3) as r)
""", [scores.tolist(), np.random.rand(N_COMPOSITIONS).tolist(), np.random.rand(N_COMPOSITIONS).tolist()])
print(f"  Bulk insert 100K: {time.time()-t0:.3f}s")

t0 = time.time()
r = ddb.execute("SELECT COUNT(*), AVG(score), MAX(score) FROM compositions").fetchone()
print(f"  Aggregate: {time.time()-t0:.3f}s -> count={r[0]}, avg={r[1]:.3f}, max={r[2]:.3f}")

t0 = time.time()
r = ddb.execute("SELECT chain_key, score FROM compositions ORDER BY score DESC LIMIT 10").fetchall()
print(f"  Top-10: {time.time()-t0:.3f}s")

t0 = time.time()
r = ddb.execute("SELECT cycle, COUNT(*), AVG(score) FROM compositions GROUP BY cycle ORDER BY cycle").fetchall()
print(f"  Group-by (200 groups): {time.time()-t0:.3f}s")

# Transactional append
t0 = time.time()
ddb.execute("BEGIN TRANSACTION")
ddb.execute("""INSERT INTO compositions VALUES
    (100001, 'new_chain', 0.99, 0.88, 0.77, 999)""")
ddb.execute("COMMIT")
print(f"  Single transactional insert: {time.time()-t0:.3f}s")

# Batch append
t0 = time.time()
ddb.execute("""INSERT INTO compositions
    SELECT 100000 + i, 'batch_' || i::VARCHAR, random(), random(), random(), 999
    FROM (SELECT unnest(range(10000)) as i)
""")
print(f"  Batch append 10K: {time.time()-t0:.3f}s")

# Checkpoint
t0 = time.time()
ddb.execute("CHECKPOINT")
print(f"  Checkpoint (force WAL flush): {time.time()-t0:.3f}s")

sz = os.path.getsize(duck_path)
print(f"  Disk: {sz/1024/1024:.1f} MB | Memory: {mem_mb():.0f} MB")
ddb.close()
os.remove(duck_path)
print()

# ============================================================
# KUZU
# ============================================================
import kuzu

kuzu_path = "organisms/_bench.kuzu"
shutil.rmtree(kuzu_path, ignore_errors=True)
print("--- KUZU (graph) ---")

t0 = time.time()
db = kuzu.Database(kuzu_path)
conn = kuzu.Connection(db)
conn.execute("CREATE NODE TABLE Organism(name STRING, PRIMARY KEY(name))")
conn.execute("CREATE NODE TABLE Comp(key STRING, score DOUBLE, PRIMARY KEY(key))")
conn.execute("CREATE REL TABLE EDGE(FROM Organism TO Organism, weight DOUBLE)")
print(f"  Schema: {time.time()-t0:.3f}s")

# Batch insert organisms
t0 = time.time()
for i in range(N_ORGANISMS):
    conn.execute(f"CREATE (o:Organism {{name: 'org_{i}'}})")
print(f"  Insert {N_ORGANISMS} organisms: {time.time()-t0:.3f}s")

# Batch insert compositions (limited to 10K for speed)
t0 = time.time()
for i in range(10000):
    conn.execute(f"CREATE (c:Comp {{key: 'comp_{i}', score: {float(scores[i])}}})")
print(f"  Insert 10K compositions: {time.time()-t0:.3f}s")

# Insert edges
t0 = time.time()
inserted = 0
for i in range(2000):
    a, b = np.random.randint(0, N_ORGANISMS), np.random.randint(0, N_ORGANISMS)
    if a != b:
        try:
            conn.execute(
                f"MATCH (a:Organism {{name: 'org_{a}'}}), (b:Organism {{name: 'org_{b}'}}) "
                f"CREATE (a)-[:EDGE {{weight: {np.random.rand():.4f}}}]->(b)"
            )
            inserted += 1
        except:
            pass
print(f"  Insert {inserted} edges: {time.time()-t0:.3f}s")

# Graph query
t0 = time.time()
result = conn.execute(
    "MATCH (a:Organism)-[r:EDGE]->(b:Organism) "
    "WHERE a.name = 'org_0' RETURN b.name, r.weight ORDER BY r.weight DESC LIMIT 10"
)
rows = result.get_as_df()
print(f"  Neighbor query: {time.time()-t0:.3f}s, {len(rows)} results")

# Score query
t0 = time.time()
result = conn.execute(
    "MATCH (c:Comp) WHERE c.score > 0.95 RETURN c.key, c.score ORDER BY c.score DESC LIMIT 10"
)
rows = result.get_as_df()
print(f"  Filter query (score>0.95): {time.time()-t0:.3f}s, {len(rows)} results")

sz = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(kuzu_path) for f in fn)
print(f"  Disk: {sz/1024/1024:.1f} MB | Memory: {mem_mb():.0f} MB")
shutil.rmtree(kuzu_path, ignore_errors=True)
print()

print("=== SUMMARY ===")
print("Zarr:   Best for tensors (fast array I/O, chunked, append-friendly)")
print("DuckDB: Best for analytics (fast aggregation, transactional, SQL)")
print("Kuzu:   Best for graph traversal (neighbor queries, Cypher)")
print("Recommendation: Zarr for tensor data + DuckDB for results + Kuzu for Lattice graph")
