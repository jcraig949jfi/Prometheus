"""PAN-28: nearest neighbours inside Postgres through the HNSW indexes of migration 012 (pgvector 0.8.7 on M1),
so vector search, pivot and `frontier like` work from any host with only psycopg2 -- no lake, no matrix download.

Backend choice (PAN_VECTOR_BACKEND = auto | local | pg): auto keeps the exact in-process matrix where a lake is
configured (M2; the numbers already measured were made that way) and uses pg everywhere else.

The ORDER BY expression must equal the index expression, (vec::pan.halfvec(N)) operator(pan.<=>) q, or the
planner falls back to an exact scan of the whole table (controls() checks the plan both ways).
"""
import json
import os

SPACES = {"chunk": ("pan.embedding", "chunk_id", 384, "embedding_hnsw_bge_small"),
          "doc": ("pan.doc_embedding", "artifact_id", 512, "doc_embedding_hnsw_qwen3"),
          "frontier": ("pan.frontier_embedding", "item_id", 512, "frontier_embedding_hnsw_qwen3")}
# hnsw.ef_search when the caller gives none. Not pgvector's 40: on real query vectors (migration 013 graph) recall@10
# was 0.797 at 40, 0.916 at 100, 0.973 at 400 (2026-10-10); 200 costs ~10-15 ms a query.
EF_DEFAULT = 200


def backend():
    b = os.environ.get("PAN_VECTOR_BACKEND", "auto")
    if b in ("local", "pg"):
        return b
    from . import lake
    try:
        lake()
        return "local"
    except RuntimeError:
        return "pg"


def _lit(q, dims):
    return "[" + ",".join(repr(float(x)) for x in list(q)[:dims]) + "]"


def knn_sql(space):
    table, idcol, dims, _ = SPACES[space]
    expr = "(vec::pan.halfvec({d})) operator(pan.<=>) %s::pan.halfvec({d})".format(d=dims)
    return "select {i}, 1 - ({e}) from {t} where model = %s order by {e} limit %s".format(i=idcol, e=expr, t=table)


def knn(space, model, q, k, ef=None, cur=None):
    """[(id, cosine)] for the k rows of `space` nearest to vector q. hnsw.ef_search = max(ef or EF_DEFAULT, k), capped at
    1000 (an HNSW scan returns at most ef_search rows)."""
    from . import db
    dims = SPACES[space][2]
    lit = _lit(q, dims)
    ef = max(ef or EF_DEFAULT, k)
    if ef > 1000:
        raise ValueError("k/ef above 1000 is beyond one HNSW scan")

    def go(c):
        c.execute("set local hnsw.ef_search = {}".format(int(ef)))
        c.execute(knn_sql(space), (lit, model, lit, k))
        return [(int(i), float(s)) for i, s in c.fetchall()]
    if cur is not None:
        return go(cur)
    with db.cursor(statement_timeout_ms=60000) as c:
        return go(c)


def stored_vector(space, model, key, cur=None):
    """The stored vector of one row (artifact's document vector, a chunk's vector), or None."""
    from . import db
    table, idcol, _, _ = SPACES[space]
    sql = "select vec from {} where {} = %s and model = %s".format(table, idcol)
    if cur is not None:
        cur.execute(sql, (key, model))
        r = cur.fetchone()
        return r[0] if r else None
    with db.cursor() as c:
        c.execute(sql, (key, model))
        r = c.fetchone()
    return r[0] if r else None


def uses_index(space, sql=None):
    """True when the planner answers `sql` (default: knn_sql) with the space's HNSW index."""
    from . import db
    table, idcol, dims, index = SPACES[space]
    model = {"chunk": "BAAI/bge-small-en-v1.5"}.get(space, "Qwen/Qwen3-Embedding-0.6B")
    lit = _lit([0.0] * (dims - 1) + [1.0], dims)
    with db.cursor() as c:
        c.execute("explain (format json) " + (sql or knn_sql(space)), (lit, model, lit, 10))
        plan = json.dumps(c.fetchone()[0])
    return index in plan


# ---------------------------------------------------------------- controls

def controls(write=True, n_queries=1000, seed=20261010, out=print):
    """Acceptance fixed in roles/Pan/docs/PGVECTOR_INSTALL_PACKET.md before the install:
    POSITIVE '[1,2,3]' <-> '[1,2,4]' = 1; RECALL mean top-10 overlap HNSW vs exact >= 0.95 on 1,000 random chunk
    vectors as queries; CHEAT a vector written after the build is found as its own nearest neighbour.
    Added: NEGATIVE the knn query is answered by the HNSW index (recall is not an exact scan in disguise) and the
    same query without the index expression is not; recall also reported without the query itself and at ef
    40/100/400; size before/after."""
    import datetime as dt
    import time
    import numpy as np
    from . import REPO, db, search
    model = "BAAI/bge-small-en-v1.5"
    res, info = [], {}
    with db.cursor() as c:
        c.execute("select '[1,2,3]'::pan.vector operator(pan.<->) '[1,2,4]'::pan.vector")
        d = float(c.fetchone()[0])
    res.append(dict(kind="POSITIVE", name="'[1,2,3]' <-> '[1,2,4]' = 1", ok=d == 1.0, detail=str(d)))
    plain = knn_sql("chunk").replace("(vec::pan.halfvec(384))", "(vec::pan.vector(384))").replace(
        "%s::pan.halfvec(384)", "%s::pan.vector(384)")
    hit, miss = uses_index("chunk"), uses_index("chunk", plain)
    res.append(dict(kind="NEGATIVE", name="knn is answered by the HNSW index; the same query without the index "
                    "expression is not", ok=hit and not miss,
                    detail="halfvec expression -> index {}; vector(384) expression -> index {}".format(hit, miss)))
    # exact reference: the in-process matrix (float16 of the same real[] values the index casts to halfvec),
    # used only if it covers exactly the rows in the database now
    ids, m = search.load_matrix(model)
    with db.cursor() as c:
        c.execute("select count(*) from pan.embedding where model = %s", (model,))
        n_db = c.fetchone()[0]
    if len(ids) != n_db:
        ids, m = search.load_matrix(model, refresh=True)
    info["rows"] = int(len(ids))
    rng = np.random.default_rng(seed)
    qi = rng.choice(len(ids), size=n_queries, replace=False)
    m32 = m.astype(np.float32)
    exact = {}
    for s in range(0, n_queries, 100):
        block = qi[s:s + 100]
        sc = m32[block] @ m32.T
        for row, i in zip(sc, block):
            top = np.argpartition(-row, 11)[:11]
            top = top[np.argsort(-row[top])]
            exact[int(i)] = ([int(ids[j]) for j in top], float(row[top[9]]), float(row[top[10]]))
    del m32
    curves = {}
    for ef in (40, 100, 400):
        strict, noself, tie, lat = [], [], [], []
        conn = db.connect()
        try:
            c = conn.cursor()
            for i in qi:
                i = int(i)
                t0 = time.perf_counter()
                got = knn("chunk", model, m[i].astype(np.float32), 11, ef=ef, cur=c)
                lat.append(time.perf_counter() - t0)
                gid = [g for g, _ in got]
                ex, s10, _ = exact[i]
                strict.append(len(set(gid[:10]) & set(ex[:10])) / 10)
                me = int(ids[i])
                a = [g for g in gid if g != me][:10]
                b = [e for e in ex if e != me][:10]
                noself.append(len(set(a) & set(b)) / 10)
                # tie-aware: a returned row counts when its HNSW cosine reaches the exact 10th score (float16 ties)
                tie.append(sum(1 for _, sc in got[:10] if sc >= s10 - 1e-3) / 10)
            conn.rollback()
        finally:
            conn.close()
        curves[ef] = dict(recall10=round(float(np.mean(strict)), 4), recall10_without_self=round(float(np.mean(noself)), 4),
                          recall10_tie_aware=round(float(np.mean(tie)), 4),
                          p50_ms=round(float(np.median(lat)) * 1000, 1), p95_ms=round(float(np.percentile(lat, 95)) * 1000, 1))
        out("ef {:>3}: recall@10 {recall10}  without self {recall10_without_self}  tie-aware {recall10_tie_aware}  "
            "p50 {p50_ms} ms  p95 {p95_ms} ms".format(ef, **curves[ef]))
    # query-style vectors (the bge query instruction, as search uses): the packet's gate above sends chunk vectors,
    # which sit where the graph was built; real queries do not (012: 0.659 at ef 40). Gate fixed 2026-10-10 AFTER
    # the first measurement, as a regression guard: recall@10 >= 0.93 at EF_DEFAULT.
    from . import embed
    texts = [q["q"] for f in ("known_answers", "heldout_answers", "heldout2_answers")
             for q in json.loads((REPO / "pan" / "tests" / (f + ".json")).read_text(encoding="utf-8"))["queries"]]
    with db.cursor() as c:
        c.execute("select setseed(0.07)")
        c.execute("""select heading from pan.chunk where heading is not null and length(heading) between 20 and 120
                     order by random() limit 438""")
        texts += [r[0].split(">")[-1].strip() for r in c.fetchall()]
    Q = np.asarray([embed.encode_query(t, model)[:384] for t in texts], dtype=np.float32)
    m32 = m.astype(np.float32)
    qex = []
    for s in range(0, len(Q), 100):
        for row in Q[s:s + 100] @ m32.T:
            top = np.argpartition(-row, 10)[:10]
            qex.append({int(ids[j]) for j in top})
    del m32
    qcurve = {}
    for ef in (40, 100, EF_DEFAULT, 400):
        conn = db.connect()
        try:
            c = conn.cursor()
            rec = np.asarray([len(e & {g for g, _ in knn("chunk", model, qv, 10, ef=ef, cur=c)}) / 10
                              for qv, e in zip(Q, qex)])
            conn.rollback()
        finally:
            conn.close()
        qcurve[ef] = dict(recall10=round(float(rec.mean()), 4), frozen62=round(float(rec[:62].mean()), 4),
                          headings=round(float(rec[62:].mean()), 4), share_below_0_8=round(float((rec < 0.8).mean()), 4))
        out("query-style ef {:>3}: {}".format(ef, qcurve[ef]))
    info["query_recall_curve"] = qcurve
    info["query_vectors"] = len(Q)
    qd = qcurve[EF_DEFAULT]
    res.append(dict(kind="POSITIVE", name="query-style recall@10 >= 0.93 at the default ef_search {} ({} query vectors: "
                    "62 frozen queries + chunk headings; gate set after the first measurement)".format(EF_DEFAULT, len(Q)),
                    ok=qd["recall10"] >= 0.93, detail="recall@10 {recall10} (frozen {frozen62}, headings {headings}, "
                    "share below 0.8 {share_below_0_8})".format(**qd)))
    r40 = curves[40]
    res.append(dict(kind="POSITIVE", name="RECALL: mean top-10 overlap HNSW vs exact >= 0.95 on {} random chunk "
                    "vectors (packet gate, default ef_search 40)".format(n_queries), ok=r40["recall10"] >= 0.95,
                    detail="recall@10 {} (without the query itself {}, tie-aware {})".format(
                        r40["recall10"], r40["recall10_without_self"], r40["recall10_tie_aware"])))
    # CHEAT: overwrite one row's vector with a fresh random unit vector inside a transaction (the index must see
    # the new tuple), ask for that vector, expect that row first; roll back
    v = rng.standard_normal(384).astype(np.float32)
    v /= np.linalg.norm(v)
    conn = db.connect()
    try:
        c = conn.cursor()
        victim = int(ids[int(rng.integers(len(ids)))])
        c.execute("update pan.embedding set vec = %s where chunk_id = %s and model = %s",
                  ([float(x) for x in v], victim, model))
        got = knn("chunk", model, v, 5, cur=c)
        conn.rollback()
    finally:
        conn.close()
    res.append(dict(kind="CHEAT", name="a vector written after the index build is its own nearest neighbour",
                    ok=bool(got) and got[0][0] == victim and got[0][1] > 0.99,
                    detail="chunk {} -> top-1 {} cosine {:.4f} (rolled back)".format(victim, got[0][0] if got else None,
                                                                                     got[0][1] if got else 0)))
    with db.cursor() as c:
        c.execute("""select indexrelid::regclass::text, pg_relation_size(indexrelid) from pg_index
                     where indexrelid::regclass::text like 'pan.%%hnsw%%'""")
        info["indexes"] = {k: int(s) for k, s in c.fetchall()}
        c.execute("""select sum(pg_total_relation_size(c.oid)) from pg_class c join pg_namespace n on n.oid = c.relnamespace
                     where n.nspname = 'pan' and c.relkind in ('r', 'm')""")
        info["pan_schema_bytes"] = int(c.fetchone()[0])
    verdict = "PASS" if all(x["ok"] for x in res) else "FAIL"
    at = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    doc = dict(control="PAN-28 pgvector HNSW", at=at, verdict=verdict, checks=res, recall_curve=curves,
               queries=n_queries, seed=seed, **info)
    if write:
        p = REPO / "roles" / "Pan" / "reports" / "controls" / "PGVECTOR_{}.json".format(at)
        p.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        out("wrote " + str(p))
    for x in res:
        out("{:<8} {:<5} {}  ({})".format(x["kind"], "PASS" if x["ok"] else "FAIL", x["name"], x["detail"]))
    out(verdict)
    return doc
