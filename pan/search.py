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


FTS_AND = """
  with q as (select websearch_to_tsquery('english', %(q)s) as tq),
  hits as (
    select c.chunk_id, c.artifact_id, c.line_start, c.line_end, c.heading,
           ts_rank_cd(c.tsv, q.tq, 32) as score, 0 as cov
    from pan.chunk c join pan.artifact a on a.artifact_id = c.artifact_id, q
    where c.tsv @@ q.tq {f}),
  best as (select distinct on (artifact_id) * from hits order by artifact_id, score desc)
  select b.chunk_id, a.path, a.kind, a.seat, a.last_commit_at, b.line_start, b.line_end, b.heading, b.score, b.cov,
         ts_headline('english', c.body, q.tq, 'MaxWords=28, MinWords=10, MaxFragments=1') as snippet
  from best b join pan.artifact a on a.artifact_id = b.artifact_id join pan.chunk c on c.chunk_id = b.chunk_id, q
  order by b.score desc limit %(k)s"""

# OR semantics (v1): any query lexeme matches; candidates ordered by cover density,
# then re-scored by COVERAGE (how many distinct query lexemes the chunk holds), with a
# minimum-should-match of 34 percent of the query's lexemes (fixed before the v1 dev runs).
# v2.1: only the `maxlex` RAREST query lexemes that occur in the corpus are used (by
# pan.lexeme_df); lexemes absent from the corpus could not match anyway.
# v0 used AND only and dropped long lexical queries (CONTROLS_20261009T1117Z).
FTS_OR = """
  with lx0 as (select distinct lexeme as l from unnest(to_tsvector('english', %(q)s))),
  lx as (select lx0.l from lx0 join pan.lexeme_df d on d.lexeme = lx0.l
         order by d.ndoc asc limit %(maxlex)s),
  q as (select string_agg(quote_literal(l), ' | ')::tsquery as tq, count(*) as n from lx),
  cand as (
    select c.chunk_id, c.artifact_id, c.line_start, c.line_end, c.heading, c.tsv,
           ts_rank_cd(c.tsv, q.tq, 32) as r
    from pan.chunk c join pan.artifact a on a.artifact_id = c.artifact_id, q
    where c.tsv @@ q.tq {f}
    order by r desc limit %(pool)s),
  sc as (select cand.*, (select count(*) from lx where cand.tsv @@ quote_literal(lx.l)::tsquery) as cov from cand),
  best as (select distinct on (artifact_id) * from sc order by artifact_id, cov desc, r desc)
  select b.chunk_id, a.path, a.kind, a.seat, a.last_commit_at, b.line_start, b.line_end, b.heading,
         (b.cov::float / greatest(q.n, 1)) + b.r as score, b.cov,
         ts_headline('english', c.body, q.tq, 'MaxWords=28, MinWords=10, MaxFragments=1') as snippet
  from best b join pan.artifact a on a.artifact_id = b.artifact_id join pan.chunk c on c.chunk_id = b.chunk_id, q
  where b.cov >= greatest(1, ceil(q.n * 0.34))
  order by b.cov desc, b.r desc limit %(k)s"""


def fts(query, k=10, kind=None, seat=None, path=None, since=None, cur=None, semantics="or", pool=4000,
        maxlex=12):
    """Best chunk per artifact. semantics='and': websearch_to_tsquery (v0);
    'or': any lexeme, ranked by coverage then cover density (v1 default)."""
    from . import db
    fsql, fargs = _filters(kind, seat, path, since)
    # _filters emits positional %s; rewrite to named parameters for this query
    names = {}
    for i, a in enumerate(fargs):
        fsql = fsql.replace("%s", "%(f{})s".format(i), 1)
        names["f{}".format(i)] = a
    sql = (FTS_OR if semantics == "or" else FTS_AND).format(f=fsql)
    params = dict(q=query, k=k, pool=pool, maxlex=maxlex, **names)
    own = cur is None
    if own:
        ctx = db.cursor(statement_timeout_ms=60000)
        cur = ctx.__enter__()
    try:
        cur.execute(sql, params)
        cols = ["chunk_id", "path", "kind", "seat", "last_commit_at", "line_start", "line_end", "heading", "score",
                "cov", "snippet"]
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
    with db.cursor() as cur:
        cur.execute("select chunk_id from pan.embedding where model = %s", (model,))
        live = np.fromiter((r[0] for r in cur.fetchall()), dtype=np.int64)
    n_db = len(live)
    shards = lake() / "vectors" / "shards" / model.replace("/", "__")
    if shards.is_dir():
        # local Parquet shards written by embed.run, COMPACTED against the chunk ids that exist
        # in the database now (re-chunked files leave stale ids in older shards); later shards
        # win for a repeated id; used only if every live id is covered (the database is the
        # cross-host truth)
        import pyarrow.parquet as pq
        ids, mats = [], []
        for f in sorted(shards.glob("*.parquet")):
            t = pq.read_table(f)
            ids.append(t.column("chunk_id").to_numpy())
            mats.append(np.asarray(t.column("vec").combine_chunks().flatten().to_numpy(zero_copy_only=False),
                                   dtype=np.float16).reshape(t.num_rows, -1))
        if ids:
            ids, m = np.concatenate(ids), np.vstack(mats)
            _, last = np.unique(ids[::-1], return_index=True)
            keep = np.sort(len(ids) - 1 - last)
            ids, m = ids[keep], m[keep]
            mask = np.isin(ids, live)
            ids, m = ids[mask], m[mask]
            if len(ids) == n_db:
                order = np.argsort(ids)
                ids, m = ids[order], m[order]
                p.parent.mkdir(parents=True, exist_ok=True)
                np.savez(p, ids=ids, m=m)
                _CACHE[model] = (ids, m)
                return _CACHE[model]
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
    from . import pgvec
    model = model or embed.default_model()
    if pgvec.backend() == "pg":
        cand = pgvec.knn("chunk", model, embed.encode_query(query, model), pool)
    else:
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


_DCACHE = {}


def load_doc_matrix(model, refresh=False):
    """(artifact_ids, float16 matrix) of document vectors; from local Parquet shards when
    their row count equals the database's, else dumped from pan.doc_embedding."""
    import numpy as np
    from . import db
    if model in _DCACHE and not refresh:
        return _DCACHE[model]
    with db.cursor() as cur:
        cur.execute("select artifact_id from pan.doc_embedding where model = %s", (model,))
        live = np.fromiter((r[0] for r in cur.fetchall()), dtype=np.int64)
    n_db = len(live)
    shards = lake() / "vectors" / "docs" / model.replace("/", "__")
    ids, m = None, None
    if shards.is_dir():
        import pyarrow.parquet as pq
        idl, ml = [], []
        for f in sorted(shards.glob("*.parquet")):
            t = pq.read_table(f)
            idl.append(t.column("artifact_id").to_numpy())
            ml.append(np.asarray(t.column("vec").combine_chunks().flatten().to_numpy(zero_copy_only=False),
                                 dtype=np.float16).reshape(t.num_rows, -1))
        if idl:
            ids, m = np.concatenate(idl), np.vstack(ml)
            # later shards supersede earlier rows for the same artifact
            _, last = np.unique(ids[::-1], return_index=True)
            keep = len(ids) - 1 - last
            ids, m = ids[keep], m[keep]
            mask = np.isin(ids, live)          # drop vectors of artifacts no longer catalogued
            ids, m = ids[mask], m[mask]
            if len(ids) != n_db:
                ids, m = None, None
    if ids is None:
        with db.cursor() as cur:
            cur.execute("select artifact_id, vec from pan.doc_embedding where model = %s", (model,))
            rows = cur.fetchall()
        ids = np.asarray([r[0] for r in rows], dtype=np.int64)
        m = np.asarray([r[1] for r in rows], dtype=np.float16) if rows else np.zeros((0, 1), np.float16)
    _DCACHE[model] = (ids, m)
    return _DCACHE[model]


def doc_vector(query, k=10, model=None, kind=None, seat=None, path=None, since=None, pool=600):
    """Artifacts ranked by cosine between the query and the document vector; each hit
    carries its first chunk as the representative passage."""
    import numpy as np
    from . import db, embed
    from . import pgvec
    model = model or embed.DOC_MODEL
    if pgvec.backend() == "pg":
        got = pgvec.knn("doc", model, embed.encode_query(query, model), min(pool, 1000))
        ids = np.asarray([g for g, _ in got], dtype=np.int64)
        scores = np.asarray([s for _, s in got], dtype=np.float32)
        top = np.arange(len(got))
    else:
        ids, m = load_doc_matrix(model)
        if len(ids) == 0:
            return []
        q = embed.encode_query(query, model)[: m.shape[1]].astype(np.float16)
        scores = (m @ q).astype(np.float32)
        top = np.argpartition(-scores, min(pool, len(scores) - 1))[:pool]
        top = top[np.argsort(-scores[top])]
    fsql, fargs = _filters(kind, seat, path, since)
    with db.cursor(statement_timeout_ms=60000) as cur:
        cur.execute("""select a.artifact_id, a.path, a.kind, a.seat, a.last_commit_at,
                              (select chunk_id from pan.chunk c where c.artifact_id=a.artifact_id order by ord limit 1),
                              a.title
                       from pan.artifact a where a.artifact_id = any(%s) {f}""".format(f=fsql),
                    [[int(ids[i]) for i in top]] + fargs)
        meta = {r[0]: r for r in cur.fetchall()}
    out = []
    for i in top:
        r = meta.get(int(ids[i]))
        if not r or r[5] is None:
            continue
        out.append(dict(chunk_id=r[5], path=r[1], kind=r[2], seat=r[3], last_commit_at=r[4], line_start=1,
                        line_end=None, heading=r[6], score=float(scores[i]), snippet=r[6] or ""))
        if len(out) >= k:
            break
    return out


def hybrid(query, k=10, rerank=None, pool=30, fts_semantics="or", docvec=None, collapse=False, **kw):
    """Reciprocal-rank fusion of the full-text, chunk-vector and (v2) document-vector
    lists, per artifact path; optionally re-ordered by a cross-encoder over the fused
    pool, then (v2) canonical-first collapse of near-duplicate candidates."""
    a = fts(query, k=max(k * 3, pool), semantics=fts_semantics, **kw)
    lists = [(a, "fts")]
    try:
        lists.append((vector(query, k=max(k * 3, pool), pool=max(400, 8 * pool), **kw), "vec"))
    except Exception as e:  # no embeddings yet, or no model on this host: degrade, and say so
        for r in a:
            r["note"] = "vector unavailable: {}".format(type(e).__name__)
    if docvec:
        try:
            lists.append((doc_vector(query, k=max(k * 3, pool), model=docvec, **kw), "doc"))
        except Exception as e:
            for r in a:
                r["note"] = "doc vector unavailable: {}".format(type(e).__name__)
    fused = {}
    for lst, tag in lists:
        for rank, r in enumerate(lst):
            e = fused.setdefault(r["path"], dict(r, rrf=0.0, via=[]))
            e["rrf"] += 1.0 / (RRF_K + rank + 1)
            e["via"].append("{}#{}".format(tag, rank + 1))
    rows = sorted(fused.values(), key=lambda r: -r["rrf"])[:max(pool, k)]
    if rerank:
        rows = rerank_rows(query, rows, rerank)
    if collapse:
        rows = collapse_copies(rows)
    return rows[:k]


def _shingles(text, n=5):
    w = [t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if t]
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def collapse_copies(rows, threshold=0.5, drop_at=0.95):
    """Canonical-first: when two candidates' passages are near-duplicates (5-word
    shingle Jaccard >= threshold), the one whose file was committed EARLIER is moved
    directly above the later one. v1's measured failure shape was the canonical
    document losing to documents that quote it."""
    from . import db
    if len(rows) < 2:
        return rows
    with db.cursor() as cur:
        cur.execute("select chunk_id, body from pan.chunk where chunk_id = any(%s)", ([r["chunk_id"] for r in rows],))
        body = dict(cur.fetchall())
        cur.execute("""select path, coalesce(first_commit_at, last_commit_at) from pan.artifact
                       where path = any(%s)""", ([r["path"] for r in rows],))
        first = dict(cur.fetchall())
    sh = {id(r): _shingles(body.get(r["chunk_id"]) or "") for r in rows}
    out = list(rows)
    moved = True
    guard = 0
    while moved and guard < 50:
        moved, guard = False, guard + 1
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                si, sj = sh[id(out[i])], sh[id(out[j])]
                if not si or not sj:
                    continue
                jac = len(si & sj) / len(si | sj)
                fi, fj = first.get(out[i]["path"]), first.get(out[j]["path"])
                if jac >= drop_at:
                    # the same text twice (e.g. one comms report fanned out to N seats): keep the
                    # earlier, drop the later, count it on the kept row
                    keep, gone = (i, j) if (fi is None or fj is None or fi <= fj) else (j, i)
                    out[keep]["copies"] = out[keep].get("copies", 0) + 1 + out[gone].get("copies", 0)
                    out.pop(gone)
                    moved = True
                    break
                if jac >= threshold and fi and fj and fj < fi:
                    r = out.pop(j)
                    r["via"] = r.get("via", []) + ["canon>{}".format(i + 1)]
                    out.insert(i, r)
                    moved = True
                    break
            if moved:
                break
    return out


_RR = {}


def rerank_rows(query, rows, model):
    """Re-order rows by a cross-encoder score of (query, path + heading + chunk body)."""
    from . import db
    if not rows:
        return rows
    if model not in _RR:
        import torch
        from sentence_transformers import CrossEncoder
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        kw = {"model_kwargs": {"torch_dtype": torch.float16}} if dev == "cuda" else {}
        _RR[model] = CrossEncoder(model, device=dev, max_length=512, **kw)
    with db.cursor() as cur:
        cur.execute("select chunk_id, body from pan.chunk where chunk_id = any(%s)", ([r["chunk_id"] for r in rows],))
        body = dict(cur.fetchall())
    pairs = [(query, "{}\n{}\n{}".format(r["path"], r.get("heading") or "", (body.get(r["chunk_id"]) or "")[:2000]))
             for r in rows]
    scores = _RR[model].predict(pairs, batch_size=32, show_progress_bar=False)
    for r, sc in zip(rows, scores):
        r["rerank"] = float(sc)
        r["via"] = r.get("via", []) + ["rr"]
    return sorted(rows, key=lambda r: -r["rerank"])


def _print(rows, as_json=False, elapsed=None):
    if as_json:
        print(json.dumps(rows, default=str, indent=1))
        return
    for i, r in enumerate(rows, 1):
        when = str(r.get("last_commit_at") or "")[:10]
        loc = "{}:{}-{}".format(r["path"], r.get("line_start"), r.get("line_end"))
        print("{:>2}. {}  [{} {} {}] {}{}".format(i, loc, r.get("kind"), r.get("seat") or "-", when,
                                                 " ".join(r.get("via", [])),
                                                 "  (+{} copies)".format(r["copies"]) if r.get("copies") else ""))
        if r.get("heading"):
            print("      # " + str(r["heading"])[:110])
        sn = " ".join(str(r.get("snippet") or "").split())
        print("      " + sn[:220])
    if elapsed is not None:
        print("({} results, {:.2f}s)".format(len(rows), elapsed))


DEFAULT_RERANK = "BAAI/bge-reranker-v2-m3"


def default_rerank():
    """The shipped default (v1, verdicts 2026-10-09: CB-200 R@10 0.765 paired-equal to v2) reranks
    with bge-reranker-v2-m3 when a CUDA GPU is present; on CPU the reranker costs ~10 s a query,
    so it is skipped there (PAN_RERANK=none forces it off, PAN_RERANK=<model> forces a model)."""
    import os
    v = os.environ.get("PAN_RERANK")
    if v:
        return None if v.lower() == "none" else v
    try:
        import torch
        return DEFAULT_RERANK if torch.cuda.is_available() else None
    except Exception:
        return None


def cli(query, k=10, mode="hybrid", as_json=False, **kw):
    t = time.time()
    if mode == "hybrid":
        kw.setdefault("rerank", default_rerank())
    rows = {"fts": fts, "vector": vector, "hybrid": hybrid}[mode](query, k=k, **kw)
    _print(rows, as_json, time.time() - t)


def similar_cli(path, k=10):
    """Artifacts nearest to PATH by mean chunk embedding."""
    import numpy as np
    from . import db, embed
    from . import pgvec
    model = embed.default_model()
    with db.cursor() as cur:
        cur.execute("""select c.chunk_id from pan.chunk c join pan.artifact a on a.artifact_id=c.artifact_id
                       where a.path = %s""", (path,))
        mine = {r[0] for r in cur.fetchall()}
    if not mine:
        print("no chunks for", path)
        return
    if pgvec.backend() == "pg":
        with db.cursor() as cur:
            cur.execute("select vec from pan.embedding where model = %s and chunk_id = any(%s)", (model, list(mine)))
            mv = np.asarray([r[0] for r in cur.fetchall()], dtype=np.float32)
        centroid = mv.mean(axis=0)
        centroid /= (np.linalg.norm(centroid) or 1.0)
        got = pgvec.knn("chunk", model, centroid, min(k * 40, 1000))
        ids = np.asarray([g for g, _ in got], dtype=np.int64)
        scores = np.asarray([s for _, s in got], dtype=np.float32)
        order = np.arange(len(got))
    else:
        ids, m = load_matrix(model)
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
                              pan.similarity(rel_name, %s) as s
                       from pan.pg_relation where rel_name operator(pan.%%) %s or rel_name ilike %s or schema_name ilike %s
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
