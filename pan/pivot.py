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


def collect(path, k=8):
    """The pivot as data (PAN-44: the CLI below and the MCP server share it). None when PATH is not in the catalog or
    not visible at the current clearance. NEAREST OUTSIDE (frontier papers) stays CLI-only."""
    from . import access, db, embed, search
    asql, aargs = access.filter_sql("a")
    with db.cursor() as cur:
        cur.execute("""select artifact_id, kind, seat, first_commit_at, last_commit_at, title, n_chunks
                       from pan.artifact a where path=%s""" + asql, [path] + aargs)
        a = cur.fetchone()
    if not a:
        return None
    aid, kind, seat, first, last, title, n = a
    out = dict(path=path, artifact_id=aid, what=dict(kind=kind, seat=seat, first_commit_at=first, last_commit_at=last,
                                                     n_chunks=n, title=title))
    with db.cursor() as cur:
        for name, q in (("cited_by", "select a.path, a.kind, a.seat, coalesce(a.first_commit_at, a.last_commit_at) "
                                     "from pan.link l join pan.artifact a on a.artifact_id=l.src_id where l.dst_id=%s" + asql),
                        ("cites", "select a.path, a.kind, a.seat, coalesce(a.first_commit_at, a.last_commit_at) "
                                  "from pan.link l join pan.artifact a on a.artifact_id=l.dst_id where l.src_id=%s" + asql)):
            cur.execute("select count(*) from (" + q + ") x", [aid] + aargs)
            total = cur.fetchone()[0]
            cur.execute(q + " order by 4 nulls last limit %s", [aid] + aargs + [k])
            out[name] = dict(total=total, rows=[dict(path=p, kind=kd, seat=st, when=when) for p, kd, st, when in cur.fetchall()])
    out["changed_with"] = [dict(path=p, together=together, share=share) for p, together, share in search.cochange(path, k)]
    try:
        from . import pgvec
        order = None
        if pgvec.backend() == "pg":
            v = pgvec.stored_vector("doc", embed.DOC_MODEL, aid)
            if v is not None:
                order = [i for i, _ in pgvec.knn("doc", embed.DOC_MODEL, v, k + 1) if i != aid][:k]
        else:
            ids, m = search.load_doc_matrix(embed.DOC_MODEL)
            pos = np.where(ids == aid)[0]
            if len(pos):
                sc = m.astype(np.float32) @ m[pos[0]].astype(np.float32)
                order = [int(ids[i]) for i in np.argsort(-sc)[: k + 1] if int(ids[i]) != aid][:k]
        if order is None:
            out["nearest_here"] = dict(note="no document vector for this artifact", rows=[])
        else:
            with db.cursor() as cur:
                cur.execute("select artifact_id, path, kind, seat from pan.artifact a where artifact_id = any(%s)" + asql,
                            [order] + aargs)
                meta = {r[0]: r for r in cur.fetchall()}
            out["nearest_here"] = dict(rows=[dict(path=meta[i][1], kind=meta[i][2], seat=meta[i][3]) for i in order if i in meta])
    except Exception as e:
        out["nearest_here"] = dict(note="vector neighbours unavailable on this host: {}: {}".format(type(e).__name__, e), rows=[])
    return out


def run(path, k=8):
    from . import access, search
    c = collect(path, k)
    if c is None:
        print("not in the catalog (or not visible at clearance {}):".format(access.current_role()), path)
        return
    w = c["what"]
    print("== WHAT IT IS\n  {}  [{} {}] first {} last {} chunks {}\n  {}".format(
        path, w["kind"], w["seat"] or "-", str(w["first_commit_at"])[:10], str(w["last_commit_at"])[:10], w["n_chunks"],
        (w["title"] or "")[:110]))
    for name, key in (("CITED BY", "cited_by"), ("CITES", "cites")):
        print("== LINEAGE: {} ({})".format(name, c[key]["total"]))
        for r in c[key]["rows"]:
            print("  {}  [{} {}]  {}".format(str(r["when"])[:10], r["kind"], r["seat"] or "-", r["path"]))
    print("== CHANGED WITH ({} shown)".format(len(c["changed_with"])))
    for r in c["changed_with"]:
        print("  {:>4} x  {:>5}  {}".format(r["together"], r["share"], r["path"]))
    print("== NEAREST HERE")
    nh = c["nearest_here"]
    if nh.get("note", "").startswith("no document vector"):
        search.similar_cli(path, k=k)
    elif nh.get("note"):
        print("  ({})".format(nh["note"]))
    for r in nh["rows"]:
        print("  [{} {}]  {}".format(r["kind"], r["seat"] or "-", r["path"]))
    print("== NEAREST OUTSIDE (exploratory; cited-paper recall@10 0.348)")
    try:
        from .frontier import query
        query.like_cli(path, k=min(k, 6))
    except Exception as e:
        print("  (unavailable on this host: {}: {})".format(type(e).__name__, e))
