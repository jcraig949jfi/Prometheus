"""E3: FalkorDB engine configuration as a genome, under an exact-output gate.

  python -m primordial.qd.e3_run [--reps 7] [--port 6394]

Organism = (load-time genes: CACHE_SIZE, OMP_THREAD_COUNT) x (runtime genes:
RESULTSET_SIZE, TIMEOUT_DEFAULT, QUERY_MEM_CAPACITY) x (one Cypher variant per
query). Stock falkordb/falkordb:latest in container gw-sub-e (lane E private
substrate), recreated per load-time genome over the same AOF volume.

Gate: sha256 of the result ROWS (headers excluded) for every corpus query must
equal the default engine running variant 0. Performance is measured only for
what passed. The fitness here is SEPARABLE (sum over queries of the chosen
variant's time, given the engine genes), so the landscape is censused
exhaustively per factor instead of searched; evolution is for later genomes
that are not separable.

Cheat genes (must die at the gate): Q1 v3 drops DISTINCT, Q2 v3 LIMIT 5,
RESULTSET_SIZE=100, TIMEOUT_DEFAULT=1, QUERY_MEM_CAPACITY=65536.
Noise floor: the default engine is instantiated twice (first and last
restart); a gain counts only beyond the A/A spread.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import time

import numpy as np
import psutil
import redis

EXP = "E3-falkordb-config-genome"
ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "E" / f"{EXP}.jsonl"
G = "e3corpus"
CONTAINER, IMAGE = "gw-sub-e", "falkordb/falkordb:latest"
N_PERSON, N_ITEM, N_KNOWS, N_BOUGHT, CORPUS_SEED = 20_000, 5_000, 100_000, 60_000, 314159

# (query id, variant id, cheat?, cypher). Variant 0 is the reference form.
QUERIES = [
    ("Q1", 0, False, "MATCH (a:Person {city: 3})-[:KNOWS]->()-[:KNOWS]->(c) RETURN count(DISTINCT c) AS n"),
    ("Q1", 1, False, "MATCH (a:Person)-[:KNOWS]->(b)-[:KNOWS]->(c) WHERE a.city = 3 RETURN count(DISTINCT c) AS n"),
    ("Q1", 2, False, "MATCH (a:Person) WHERE a.city = 3 MATCH (a)-[:KNOWS]->(b) WITH DISTINCT b MATCH (b)-[:KNOWS]->(c) RETURN count(DISTINCT c) AS n"),
    ("Q1", 3, True, "MATCH (a:Person {city: 3})-[:KNOWS]->()-[:KNOWS]->(c) RETURN count(c) AS n"),
    ("Q2", 0, False, "MATCH (p:Person)-[:BOUGHT]->(i:Item) WHERE p.age > 40 RETURN i.id AS item, count(p) AS n ORDER BY n DESC, item ASC LIMIT 10"),
    ("Q2", 1, False, "MATCH (i:Item)<-[:BOUGHT]-(p:Person) WHERE p.age > 40 RETURN i.id AS item, count(p) AS n ORDER BY n DESC, item ASC LIMIT 10"),
    ("Q2", 2, False, "MATCH (p:Person) WHERE p.age > 40 MATCH (p)-[:BOUGHT]->(i) RETURN i.id AS item, count(p) AS n ORDER BY n DESC, item ASC LIMIT 10"),
    ("Q2", 3, True, "MATCH (p:Person)-[:BOUGHT]->(i:Item) WHERE p.age > 40 RETURN i.id AS item, count(p) AS n ORDER BY n DESC, item ASC LIMIT 5"),
    ("Q3", 0, False, "MATCH (p:Person) RETURN p.city AS c, avg(p.age) AS a, count(*) AS n ORDER BY c"),
    ("Q3", 1, False, "MATCH (p:Person) WITH p.city AS c, p.age AS age RETURN c, avg(age) AS a, count(*) AS n ORDER BY c"),
    ("Q4", 0, False, "MATCH (p:Person)-[:KNOWS]->(q:Person) WHERE p.city = q.city RETURN p.id AS x, q.id AS y ORDER BY x, y"),
    ("Q4", 1, False, "MATCH (p:Person)-[:KNOWS]->(q) WHERE q.city = p.city RETURN p.id AS x, q.id AS y ORDER BY x, y"),
    ("Q5", 0, False, "MATCH (a:Person {id: 7})-[:KNOWS*1..3]->(b) RETURN count(DISTINCT b) AS n"),
    ("Q5", 1, False, "MATCH (a:Person) WHERE a.id = 7 MATCH (a)-[:KNOWS*1..3]->(b) RETURN count(DISTINCT b) AS n"),
    ("Q6", 0, False, "UNWIND range(0, 1999) AS x MATCH (p:Person {id: x}) RETURN sum(p.age) AS s"),
    ("Q6", 1, False, "MATCH (p:Person) WHERE p.id < 2000 RETURN sum(p.age) AS s"),
]
RUNTIME_DEFAULT = {"RESULTSET_SIZE": -1, "TIMEOUT_DEFAULT": 0, "QUERY_MEM_CAPACITY": 0}
RUNTIME_GENES = [  # (name, value, cheat?)
    ("RESULTSET_SIZE", 10000, False), ("RESULTSET_SIZE", 100, True),
    ("TIMEOUT_DEFAULT", 10000, False), ("TIMEOUT_DEFAULT", 1, True),
    ("QUERY_MEM_CAPACITY", 1 << 30, False), ("QUERY_MEM_CAPACITY", 65536, True),
]
LOAD_GENES = [  # (CACHE_SIZE, OMP_THREAD_COUNT); None = stock default. First and last are the A/A pair.
    (None, None), (1, None), (100, None), (None, 1), (None, 3), (1, 1), (100, 3), (None, None),
]


def sh(*args: str, check=True) -> str:
    p = subprocess.run(["wsl.exe", "-e", *args], capture_output=True, text=True, timeout=180)
    if check and p.returncode:
        raise RuntimeError(f"{args}: {p.stderr.strip()}")
    return p.stdout


def start_engine(port: int, cache, omp) -> float:
    margs = []
    if cache is not None:
        margs += ["CACHE_SIZE", str(cache)]
    if omp is not None:
        margs += ["OMP_THREAD_COUNT", str(omp)]
    sh("docker", "rm", "-f", CONTAINER, check=False)
    t0 = time.perf_counter()
    sh("docker", "run", "-d", "--name", CONTAINER, "--restart", "unless-stopped", "--cpus", "3",
       "-p", f"127.0.0.1:{port}:6379", "-v", f"{CONTAINER}-data:/var/lib/falkordb/data",
       "--entrypoint", "redis-server", IMAGE, "--loadmodule", "/var/lib/falkordb/bin/falkordb.so", *margs,
       "--appendonly", "yes", "--dir", "/var/lib/falkordb/data")
    r = redis.Redis(port=port)
    while True:
        try:
            r.ping()
            r.execute_command("GRAPH.LIST")
            break
        except (redis.ConnectionError, redis.ResponseError, redis.TimeoutError):
            time.sleep(0.2)
    return time.perf_counter() - t0


def corpus_arrays():
    rng = np.random.Generator(np.random.PCG64(CORPUS_SEED))
    age = rng.integers(18, 81, N_PERSON)
    city = rng.integers(0, 50, N_PERSON)
    price = rng.integers(1, 1000, N_ITEM)

    def pairs(n, hi_a, hi_b, no_self):
        e = np.unique(np.stack([rng.integers(0, hi_a, 2 * n), rng.integers(0, hi_b, 2 * n)], 1), axis=0)
        if no_self:
            e = e[e[:, 0] != e[:, 1]]
        return e[rng.permutation(len(e))[:n]]

    return age, city, price, pairs(N_KNOWS, N_PERSON, N_PERSON, True), pairs(N_BOUGHT, N_PERSON, N_ITEM, False)


def corpus_fingerprint(arrs) -> str:
    h = hashlib.sha256()
    for a in arrs:
        h.update(np.ascontiguousarray(a, dtype=np.int64).tobytes())
    return h.hexdigest()


def q(r, cypher):
    return r.execute_command("GRAPH.QUERY", G, cypher)


def ensure_corpus(r) -> str:
    arrs = corpus_arrays()
    fp = corpus_fingerprint(arrs)
    if r.get("e3:fp") == fp.encode():
        return fp
    r.delete(G, "e3:fp")
    age, city, price, knows, bought = arrs
    q(r, "CREATE INDEX FOR (p:Person) ON (p.id)")
    q(r, "CREATE INDEX FOR (i:Item) ON (i.id)")
    B = 5000
    for s in range(0, N_PERSON, B):
        rows = ",".join(f"[{i},{age[i]},{city[i]}]" for i in range(s, min(s + B, N_PERSON)))
        q(r, f"UNWIND [{rows}] AS r CREATE (:Person {{id: r[0], age: r[1], city: r[2]}})")
    for s in range(0, N_ITEM, B):
        rows = ",".join(f"[{i},{price[i]}]" for i in range(s, min(s + B, N_ITEM)))
        q(r, f"UNWIND [{rows}] AS r CREATE (:Item {{id: r[0], price: r[1]}})")
    for rel, lab, e in (("KNOWS", "Person", knows), ("BOUGHT", "Item", bought)):
        for s in range(0, len(e), B):
            rows = ",".join(f"[{a},{b}]" for a, b in e[s:s + B])
            q(r, f"UNWIND [{rows}] AS e MATCH (a:Person {{id: e[0]}}), (b:{lab} {{id: e[1]}}) CREATE (a)-[:{rel}]->(b)")
    counts = q(r, "MATCH (n) RETURN count(n)")[1][0][0], q(r, "MATCH ()-[e]->() RETURN count(e)")[1][0][0]
    if counts != (N_PERSON + N_ITEM, N_KNOWS + N_BOUGHT):
        raise SystemExit(f"corpus build wrong: {counts}")
    r.set("e3:fp", fp)
    return fp


def run_query(r, cypher, reps):
    """-> (rows_sha256 | 'ERR:...', n_rows, client median ms, internal median ms, spread ms)."""
    try:
        res = q(r, cypher)  # warm-up: plan cache
    except redis.ResponseError as e:
        return f"ERR:{str(e)[:80]}", 0, None, None, None
    digest = hashlib.sha256(repr(res[1]).encode()).hexdigest()
    wall, internal = [], []
    for _ in range(reps):
        t = time.perf_counter()
        try:
            res = q(r, cypher)
        except redis.ResponseError as e:
            return f"ERR:{str(e)[:80]}", 0, None, None, None
        wall.append((time.perf_counter() - t) * 1e3)
        internal.append(float(next(s for s in res[-1] if b"internal execution time" in s).split(b":")[1].split()[0]))
        if hashlib.sha256(repr(res[1]).encode()).hexdigest() != digest:
            return "NONDETERMINISTIC", len(res[1]), None, None, None
    return digest, len(res[1]), round(float(np.median(wall)), 3), round(float(np.median(internal)), 3), \
        round(float(np.percentile(wall, 90) - np.percentile(wall, 10)), 3)


def emit(row):
    row["ts"] = time.time()
    with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--reps", type=int, default=7)
    p.add_argument("--port", type=int, default=6394)
    a = p.parse_args()
    ROWS.parent.mkdir(parents=True, exist_ok=True)
    ref: dict[str, str] = {}
    for li, (cache, omp) in enumerate(LOAD_GENES):
        boot_s = start_engine(a.port, cache, omp)
        r = redis.Redis(port=a.port)
        fp = ensure_corpus(r)
        cfg = {k.decode() if isinstance(k, bytes) else k: v for k, v in
               zip(*[iter(sum(r.execute_command("GRAPH.CONFIG", "GET", "*"), []))] * 2)}
        base = {"restart": li, "load_genes": {"CACHE_SIZE": cache, "OMP_THREAD_COUNT": omp},
                "engine_cfg": {k: cfg[k] for k in ("CACHE_SIZE", "OMP_THREAD_COUNT", "THREAD_COUNT")},
                "boot_s": round(boot_s, 2), "corpus_fp": fp}
        psutil.cpu_percent(None)
        for qid, vid, cheat, cypher in QUERIES:
            h, n, med, internal, spread = run_query(r, cypher, a.reps)
            if li == 0 and vid == 0:
                ref[qid] = h
            emit({**base, "kind": "variant", "query": qid, "variant": vid, "cheat": cheat, "rows_sha256": h,
                  "n_rows": n, "gate": h == ref[qid], "wall_ms_median": med, "internal_ms_median": internal,
                  "wall_ms_p90_p10": spread, "host_cpu_pct": psutil.cpu_percent(None)})
        if li == 0:  # runtime genes: default engine, reference variants, one gene changed at a time
            for name, val, cheat in RUNTIME_GENES:
                r.execute_command("GRAPH.CONFIG", "SET", name, val)
                for qid, vid, _, cypher in QUERIES:
                    if vid:
                        continue
                    h, n, med, internal, spread = run_query(r, cypher, a.reps)
                    emit({**base, "kind": "runtime", "gene": name, "value": val, "cheat": cheat, "query": qid,
                          "rows_sha256": h, "n_rows": n, "gate": h == ref[qid], "wall_ms_median": med,
                          "internal_ms_median": internal, "wall_ms_p90_p10": spread,
                          "host_cpu_pct": psutil.cpu_percent(None)})
                r.execute_command("GRAPH.CONFIG", "SET", name, RUNTIME_DEFAULT[name])
        print(f"restart {li} {cache=} {omp=} boot {boot_s:.1f}s done", flush=True)


if __name__ == "__main__":
    main()
