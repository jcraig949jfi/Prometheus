"""Search over the Pan catalog: full-text (Postgres tsvector), vector (in-process
cosine over a cached matrix until pgvector exists on the cluster, Q-001), and a
hybrid of the two by reciprocal-rank fusion at the artifact level.

A hit is a retrieval result -- a pointer to path:lines at a SHA -- never
evidence for a claim (RESPONSIBILITIES.md s3).
"""
import json
import time
from pathlib import Path

from . import lake

RRF_K = 60


def _filters(kind=None, seat=None, path=None, since=None):
    sql, args = [], []
    if kind:
        sql.append("a.kind = any(%s)")
        args.append(kind.split(","))
    if seat:
        sql.append("lower(a.seat) = any(%s)")
        args.append([s.lower() for s in seat.split(",")])
    if path:
        sql.append("a.path ilike %s")
        args.append("%" + path + "%")
    if since:
        sql.append("a.last_commit_at >= %s")
        args.append(since)
    return (" and " + " and ".join(sql)) if sql else "", args


def fts(query, k=10, kind=None, seat=None, path=None, since=None, cur=None):
    """Best chunk per artifact by ts_rank_cd over websearch_to_tsquery."""
    from . import db
    fsql, fargs = _filters(kind, seat, path, since)
    sql = """
      with q as (select websearch_to_tsquery('english', %s) as tq),
      hits as (
        select c.chunk_id, c.artifact_id, c.line_start, c.line_end, c.heading,
               ts_rank_cd(c.tsv, q.tq, 32) as score
        from pan.chunk c join pan.artifact a on a.artifact_id = c.artifact_id, q
        where c.tsv @@ q.tq {f}),
      best as (select distinct on (artifact_id) * from hits order by artifact_id, score desc)
      select b.chunk_id, a.path, a.kind, a.seat, a.last_commit_at, b.line_start, b.line_end, b.heading, b.score,
             ts_headline('english', c.body, q.tq, 'MaxWords=28, MinWords=10, MaxFragments=1') as snippet
      from best b join pan.artifact a on a.artifact_id = b.artifact_id join pan.chunk c on c.chunk_id = b.chunk_id, q
      order by b.score desc limit %s""".format(f=fsql)
    own = cur is None
    if own:
        ctx = db.cursor(statement_timeout_ms=60000)
        cur = ctx.__enter__()
    try:
        cur.execute(sql, [query] + fargs + [k])
        cols = ["chunk_id", "path", "kind", "seat", "last_commit_at", "line_start", "line_end", "heading", "score",
                "snippet"]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    finally:
        if own:
            ctx.__exit__(None, None, None)


# ---------------------------------------------------------------- vectors
_CACHE = {}


def cache_path(model):
    return lake() / "vectors" / (model.replace("/", "__") + ".npz")


def load_matrix(model, refresh=False):
    """(chunk_ids, float16 matrix) for `model`, cached in the lake; rebuilt from
    pan.embedding when absent or when refresh=True."""
    import numpy as np
    if model in _CACHE and not refresh:
        return _CACHE[model]
    p = cache_path(model)
    if p.exists() and not refresh:
        z = np.load(p)
        _CACHE[model] = (z["ids"], z["m"])
        return _CACHE[model]
    from . import db
    conn = db.connect()
    try:
        cur = conn.cursor("pan_vec_dump")
        cur.itersize = 20000
        cur.execute("select chunk_id, vec from pan.embedding where model = %s order by chunk_id", (model,))
        ids, vecs = [], []
        for cid, v in cur:
            ids.append(cid)
            vecs.append(v)
    finally:
        conn.close()
    ids = np.asarray(ids, dtype=np.int64)
    m = np.asarray(vecs, dtype=np.float16) if vecs else np.zeros((0, 1), dtype=np.float16)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez(p, ids=ids, m=m)
    _CACHE[model] = (ids, m)
    return _CACHE[model]


def vector(query, k=10, model=None, kind=None, seat=None, path=None, since=None, pool=400):
    import numpy as np
    from . import db, embed
    model = model or embed.default_model()
    ids, m = load_matrix(model)
    if len(ids) == 0:
        return []
    q = embed.encode_query(query, model)
    q = q[: m.shape[1]].astype(np.float16)
    scores = (m @ q).astype(np.float32)
    top = np.argpartition(-scores, min(pool, len(scores) - 1))[:pool]
    top = top[np.argsort(-scores[top])]
    cand = [(int(ids[i]), float(scores[i])) for i in top]
    fsql, fargs = _filters(kind, seat, path, since)
    with db.cursor(statement_timeout_ms=60000) as cur:
        cur.execute("""select c.chunk_id, c.artifact_id, a.path, a.kind, a.seat, a.last_commit_at, c.line_start,
                              c.line_end, c.heading, left(c.body, 240)
                       from pan.chunk c join pan.artifact a on a.artifact_id = c.artifact_id
                       where c.chunk_id = any(%s) {f}""".format(f=fsql), [[c for c, _ in cand]] + fargs)
        meta = {r[0]: r for r in cur.fetchall()}
    out, seen = [], set()
    for cid, s in cand:
        r = meta.get(cid)
        if not r or r[1] in seen:
            continue
        seen.add(r[1])
        out.append(dict(chunk_id=cid, path=r[2], kind=r[3], seat=r[4], last_commit_at=r[5], line_start=r[6],
                        line_end=r[7], heading=r[8], score=s, snippet=" ".join((r[9] or "").split())))
        if len(out) >= k:
            break
    return out


def hybrid(query, k=10, **kw):
    """Reciprocal-rank fusion of the full-text and vector lists, per artifact path."""
    a = fts(query, k=max(k * 3, 30), **kw)
    try:
        b = vector(query, k=max(k * 3, 30), **kw)
    except Exception as e:  # no embeddings yet, or no model on this host: degrade, and say so
        b = []
        for r in a:
            r["note"] = "vector unavailable: {}".format(type(e).__name__)
    fused = {}
    for lst, tag in ((a, "fts"), (b, "vec")):
        for rank, r in enumerate(lst):
            e = fused.setdefault(r["path"], dict(r, rrf=0.0, via=[]))
            e["rrf"] += 1.0 / (RRF_K + rank + 1)
            e["via"].append("{}#{}".format(tag, rank + 1))
    return sorted(fused.values(), key=lambda r: -r["rrf"])[:k]


def _print(rows, as_json=False, elapsed=None):
    if as_json:
        print(json.dumps(rows, default=str, indent=1))
        return
    for i, r in enumerate(rows, 1):
        when = str(r.get("last_commit_at") or "")[:10]
        loc = "{}:{}-{}".format(r["path"], r.get("line_start"), r.get("line_end"))
        print("{:>2}. {}  [{} {} {}] {}".format(i, loc, r.get("kind"), r.get("seat") or "-", when,
                                               " ".join(r.get("via", []))))
        if r.get("heading"):
            print("      # " + str(r["heading"])[:110])
        sn = " ".join(str(r.get("snippet") or "").split())
        print("      " + sn[:220])
    if elapsed is not None:
        print("({} results, {:.2f}s)".format(len(rows), elapsed))


def cli(query, k=10, mode="hybrid", as_json=False, **kw):
    t = time.time()
    rows = {"fts": fts, "vector": vector, "hybrid": hybrid}[mode](query, k=k, **kw)
    _print(rows, as_json, time.time() - t)


def similar_cli(path, k=10):
    """Artifacts nearest to PATH by mean chunk embedding."""
    import numpy as np
    from . import db, embed
    model = embed.default_model()
    ids, m = load_matrix(model)
    with db.cursor() as cur:
        cur.execute("""select c.chunk_id from pan.chunk c join pan.artifact a on a.artifact_id=c.artifact_id
                       where a.path = %s""", (path,))
        mine = {r[0] for r in cur.fetchall()}
    if not mine:
        print("no chunks for", path)
        return
    pos = np.isin(ids, list(mine))
    centroid = m[pos].astype(np.float32).mean(axis=0)
    centroid /= (np.linalg.norm(centroid) or 1.0)
    scores = (m.astype(np.float32) @ centroid)
    order = np.argsort(-scores)[:k * 40]
    with db.cursor() as cur:
        cur.execute("""select c.chunk_id, a.path, a.kind, a.seat, a.last_commit_at, c.line_start, c.line_end,
                              c.heading, left(c.body, 200)
                       from pan.chunk c join pan.artifact a on a.artifact_id=c.artifact_id
                       where c.chunk_id = any(%s)""", ([int(ids[i]) for i in order],))
        meta = {r[0]: r for r in cur.fetchall()}
    rows, seen = [], {path}
    for i in order:
        r = meta.get(int(ids[i]))
        if not r or r[1] in seen:
            continue
        seen.add(r[1])
        rows.append(dict(path=r[1], kind=r[2], seat=r[3], last_commit_at=r[4], line_start=r[5], line_end=r[6],
                         heading=r[7], snippet=r[8], score=float(scores[i])))
        if len(rows) >= k:
            break
    _print(rows)


def cochange(path, k=15):
    from . import db
    with db.cursor() as cur:
        cur.execute("""with mine as (select sha from pan.commit_file where path = %s),
                       n as (select count(*)::float as n from mine)
                       select cf.path, count(*) as together, round((count(*) / n.n)::numeric, 3) as share
                       from pan.commit_file cf join mine using (sha), n
                       where cf.path <> %s group by cf.path, n.n order by together desc, cf.path limit %s""",
                    (path, path, k))
        return cur.fetchall()


def cochange_cli(path, k=15):
    rows = cochange(path, k)
    if not rows:
        print("no commits touch", path)
    for p, n, share in rows:
        print("{:>5} {:>6}  {}".format(n, share, p))


def tables_cli(query):
    from . import db
    with db.cursor() as cur:
        cur.execute("""select dbname, schema_name, rel_name, relkind, est_rows, pg_size_pretty(total_bytes),
                              similarity(rel_name, %s) as s
                       from pan.pg_relation where rel_name %% %s or rel_name ilike %s or schema_name ilike %s
                       order by s desc, total_bytes desc nulls last limit 25""",
                    (query, query, "%" + query + "%", "%" + query + "%"))
        for r in cur.fetchall():
            print("{}.{}.{} [{}] rows~{} {}".format(*r[:6]))
        cur.execute("""select dbname, schema_name, rel_name, col_name, data_type from pan.pg_column
                       where col_name ilike %s order by dbname, schema_name, rel_name limit 25""",
                    ("%" + query + "%",))
        cols = cur.fetchall()
        if cols:
            print("-- columns matching:")
            for r in cols:
                print("{}.{}.{}.{} {}".format(*r))
