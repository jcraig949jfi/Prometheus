"""`python -m pan pivot PATH` -- everything Pan knows around one artifact, in one screen
(charter C4: "quickly pivot when an experiment fails or succeeds").

Sections (each a pointer list, never a verdict):
  WHAT IT IS      kind, seat, first/last commit, title
  LINEAGE         who cites it (backlinks) and what it cites, oldest first
  CHANGED WITH    files that change in the same commits (co-change share)
  NEAREST HERE    nearest artifacts by document vector (falls back to chunk vectors)
  NEAREST OUTSIDE nearest papers in the frontier corpus (same vector space)
"""
import numpy as np


def run(path, k=8):
    from . import db, embed, search
    with db.cursor() as cur:
        cur.execute("""select artifact_id, kind, seat, first_commit_at, last_commit_at, title, n_chunks
                       from pan.artifact where path=%s""", (path,))
        a = cur.fetchone()
    if not a:
        print("not in the catalog:", path)
        return
    aid, kind, seat, first, last, title, n = a
    print("== WHAT IT IS\n  {}  [{} {}] first {} last {} chunks {}\n  {}".format(
        path, kind, seat or "-", str(first)[:10], str(last)[:10], n, (title or "")[:110]))
    with db.cursor() as cur:
        for name, q in (("CITED BY", "select a.path, a.kind, a.seat, coalesce(a.first_commit_at, a.last_commit_at) "
                                     "from pan.link l join pan.artifact a on a.artifact_id=l.src_id where l.dst_id=%s"),
                        ("CITES", "select a.path, a.kind, a.seat, coalesce(a.first_commit_at, a.last_commit_at) "
                                  "from pan.link l join pan.artifact a on a.artifact_id=l.dst_id where l.src_id=%s")):
            cur.execute("select count(*) from (" + q + ") x", (aid,))
            total = cur.fetchone()[0]
            cur.execute(q + " order by 4 nulls last limit %s", (aid, k))
            print("== LINEAGE: {} ({})".format(name, total))
            for p, kd, st, when in cur.fetchall():
                print("  {}  [{} {}]  {}".format(str(when)[:10], kd, st or "-", p))
    rows = search.cochange(path, k)
    print("== CHANGED WITH ({} shown)".format(len(rows)))
    for p, together, share in rows:
        print("  {:>4} x  {:>5}  {}".format(together, share, p))
    print("== NEAREST HERE")
    try:
        from . import pgvec
        if pgvec.backend() == "pg":
            v = pgvec.stored_vector("doc", embed.DOC_MODEL, aid)
            pos = [0] if v is not None else []
            if v is not None:
                order = [i for i, _ in pgvec.knn("doc", embed.DOC_MODEL, v, k + 1) if i != aid][:k]
        else:
            ids, m = search.load_doc_matrix(embed.DOC_MODEL)
            pos = np.where(ids == aid)[0]
            if len(pos):
                sc = m.astype(np.float32) @ m[pos[0]].astype(np.float32)
                order = [int(ids[i]) for i in np.argsort(-sc)[: k + 1] if int(ids[i]) != aid][:k]
        if len(pos):
            with db.cursor() as cur:
                cur.execute("select artifact_id, path, kind, seat from pan.artifact where artifact_id = any(%s)", (order,))
                meta = {r[0]: r for r in cur.fetchall()}
            for i in order:
                r = meta.get(i)
                if r:
                    print("  [{} {}]  {}".format(r[2], r[3] or "-", r[1]))
        else:
            search.similar_cli(path, k=k)
    except Exception as e:
        print("  (vector neighbours unavailable on this host: {}: {})".format(type(e).__name__, e))
    print("== NEAREST OUTSIDE (exploratory; cited-paper recall@10 0.348)")
    try:
        from .frontier import query
        query.like_cli(path, k=min(k, 6))
    except Exception as e:
        print("  (unavailable on this host: {}: {})".format(type(e).__name__, e))
