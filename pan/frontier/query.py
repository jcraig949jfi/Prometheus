"""Read side of the frontier intake: full-text over papers, and a model finder."""


def search_cli(q, k=15):
    from .. import db
    with db.cursor(statement_timeout_ms=60000) as cur:
        cur.execute("""
          with lx as (select distinct lexeme as l from unnest(to_tsvector('english', %(q)s))),
          tq as (select string_agg(quote_literal(l), ' | ')::tsquery as tq, count(*) as n from lx),
          hits as (select f.*, ts_rank_cd(f.tsv, tq.tq, 32) as r,
                          (select count(*) from lx where f.tsv @@ quote_literal(lx.l)::tsquery) as cov
                   from pan.frontier_item f, tq where f.tsv @@ tq.tq)
          select h.source, h.source_id, h.published_at::date, h.title, h.cov, tq.n, h.query_tags,
                 h.signals->>'upvotes', h.url
          from hits h, tq where h.cov >= greatest(1, ceil(tq.n * 0.34))
          order by h.cov desc, h.r desc limit %(k)s""", dict(q=q, k=k))
        from .digest import ascii_fold       # the Windows console is cp1252: print ASCII, never crash on a title
        for src, sid, pub, title, cov, n, tags, up, url in cur.fetchall():
            ident = sid if src in ("arxiv", "hf_daily") else (url or sid)    # feed ids are long; the link says more
            print("{} {:<11} {} [{}/{}] {}{}".format(src[:6], ascii_fold(ident)[:90], pub, cov, n,
                                                     ascii_fold(title)[:95], " (+{} upvotes)".format(up) if up else ""))
            print("      tags: " + ", ".join((tags or [])[:4]))


def models_cli(q, k=15, fits=False):
    from .. import db
    where = "(repo_id ilike %(p)s or %(q)s = '' or exists (select 1 from unnest(tags) t where t ilike %(p)s))"
    if fits:
        where += " and (fit->>'fits_16gb_q4')::boolean"
    with db.cursor() as cur:
        cur.execute("""select repo_id, pipeline_tag, params_total, params_basis, fit->>'est_gb_q4',
                              fit->>'reliable', license, last_modified::date, downloads, likes
                       from pan.hf_model where {} order by trending_score desc nulls last, likes desc nulls last
                       limit %(k)s""".format(where), dict(p="%" + q + "%", q=q, k=k))
        for r in cur.fetchall():
            params = "{:.1f}B".format(r[2] / 1e9) if r[2] else "?"
            print("{:<55} {:<20} {:>7} ({}) q4~{}GB rel={} lic={} mod={} dl={} likes={}".format(
                r[0][:55], (r[1] or "")[:20], params, r[3], r[4], r[5], r[6], r[7], r[8], r[9]))


def embed_items(model=None, batch=32, out=print):
    """PAN-14: vectors for frontier items (title + summary) in the SAME space as the
    repository's document vectors (embed.DOC_MODEL), so a program file and an outside
    paper can be compared directly."""
    import io
    import json
    import time
    from .. import db, embed
    model = model or embed.DOC_MODEL
    t0 = time.time()
    with db.cursor() as cur:
        cur.execute("""select item_id, source, source_id, title, summary from pan.frontier_item f where not exists
                       (select 1 from pan.frontier_embedding e where e.item_id=f.item_id and e.model=%s)
                       order by item_id""", (model,))
        rows = cur.fetchall()
    if not rows:
        out(json.dumps(dict(embedded=0, model=model)))
        return 0
    texts = ["{}\n{}".format(t or "", s or "")[:1600] for _, _, _, t, s in rows]
    vecs = embed.encode_docs(texts, model, batch=batch)
    buf = io.StringIO()
    for (iid, *_), v in zip(rows, vecs):
        buf.write("{}\t{}\t{}\t{{{}}}\n".format(iid, model, vecs.shape[1], ",".join("{:.6g}".format(x) for x in v)))
    buf.seek(0)
    with db.cursor() as cur:
        cur.copy_expert("copy pan.frontier_embedding (item_id, model, dims, vec) from stdin", buf)
    out(json.dumps(dict(embedded=len(rows), model=model, seconds=round(time.time() - t0, 1))))
    return len(rows)


def like_cli(path, k=10, model=None):
    """Outside papers nearest to a repository file (document vector vs paper vectors)."""
    import numpy as np
    from .. import db, embed, search
    model = model or embed.DOC_MODEL
    ids, m = search.load_doc_matrix(model)
    with db.cursor() as cur:
        cur.execute("select artifact_id from pan.artifact where source='git' and path=%s", (path,))
        r = cur.fetchone()
        if not r:
            print("not in the catalog:", path)
            return
        pos = np.where(ids == r[0])[0]
        if not len(pos):
            print("no document vector for", path)
            return
        q = m[pos[0]].astype(np.float32)
        cur.execute("""select f.item_id, f.source, f.source_id, f.published_at::date, f.title, e.vec
                       from pan.frontier_embedding e join pan.frontier_item f on f.item_id=e.item_id
                       where e.model=%s""", (model,))
        items = cur.fetchall()
    if not items:
        print("no frontier vectors yet (python -m pan frontier embed)")
        return
    mat = np.asarray([it[5] for it in items], dtype=np.float32)
    sc = mat @ q
    seen = set()
    for i in np.argsort(-sc):
        it = items[i]
        if it[2] in seen:          # same paper from arXiv and from HF daily
            continue
        seen.add(it[2])
        print("{:.3f} {} {:<11} {} {}".format(sc[i], it[1][:6], it[2], it[3], (it[4] or "")[:90]))
        if len(seen) >= k:
            break
