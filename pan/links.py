"""Reference graph over the catalog (charter C4): which artifacts cite which.

A citation is a file path written in an artifact's text that resolves to a git
artifact at the catalog SHA: exactly (repository-relative), or relative to the
citing file's directory. Bare names ("README.md") are ambiguous and are not
linked. Backslashes and a leading "./" are normalised.

ORACLE (spot, not total): a planted chunk citing two known paths must produce
exactly those two links (tests/test_links.py) -- the extractor alone, no database.
"""
import json
import posixpath
import re
import time

PATH = re.compile(r"(?<![\w./\\-])((?:[\w.@+-]+[/\\])+[\w.@+-]+\.(?:md|py|json|jsonl|txt|csv|tsv|sql|yaml|yml|toml|"
                  r"ps1|sh|bat|cmd|html|tex|ipynb|rs|js|ts|npz|npy|parquet|gz|log|pdf|lean|cfg|ini))(?![\w])")


def mentions(text):
    out = {}
    for m in PATH.finditer(text or ""):
        p = m.group(1).replace("\\", "/")
        while p.startswith("./"):
            p = p[2:]
        out[p] = out.get(p, 0) + 1
    return out


def resolve(mention, src_path, known):
    """(dst_path, how) or (None, None). `known` is the set of catalogued git paths."""
    if mention in known:
        return mention, "exact"
    rel = posixpath.normpath(posixpath.join(posixpath.dirname(src_path), mention))
    if rel in known and not rel.startswith(".."):
        return rel, "relative"
    return None, None


def run(out=print):
    from psycopg2.extras import execute_values
    from . import db
    t0 = time.time()
    with db.cursor() as cur:
        cur.execute("select path, artifact_id from pan.artifact where source='git'")
        ids = dict(cur.fetchall())
    known = set(ids)
    links = {}
    conn = db.connect()
    try:
        cur = conn.cursor("pan_links_scan")
        cur.itersize = 20000
        cur.execute("""select a.artifact_id, a.path, c.body from pan.chunk c join pan.artifact a
                       on a.artifact_id = c.artifact_id where a.source in ('git', 'comms')""")
        n = 0
        for aid, path, body in cur:
            n += 1
            for mtn, cnt in mentions(body).items():
                dst, how = resolve(mtn, path if not path.startswith("comms:") else "", known)
                if dst and ids[dst] != aid:
                    key = (aid, ids[dst])
                    e = links.setdefault(key, [0, how])
                    e[0] += cnt
    finally:
        conn.close()
    with db.cursor(statement_timeout_ms=900000) as cur:
        cur.execute("truncate pan.link")
        execute_values(cur, "insert into pan.link (src_id, dst_id, n_mentions, how) values %s",
                       [(s, d, v[0], v[1]) for (s, d), v in links.items()], page_size=10000)
        cur.execute("select count(*), count(distinct src_id), count(distinct dst_id) from pan.link")
        total, srcs, dsts = cur.fetchone()
    res = dict(chunks_scanned=n, links=total, citing=srcs, cited=dsts, seconds=round(time.time() - t0, 1))
    out(json.dumps(res))
    return res


def refs_cli(path, k=40):
    """Who cites PATH (backlinks) and what PATH cites (forward links), oldest first."""
    from . import db
    with db.cursor() as cur:
        cur.execute("select artifact_id from pan.artifact where path=%s", (path,))
        r = cur.fetchone()
        if not r:
            print("not in the catalog:", path)
            return
        aid = r[0]
        for title, q in (("CITED BY", """select a.path, a.kind, a.seat, coalesce(a.first_commit_at, a.last_commit_at), l.n_mentions
                                         from pan.link l join pan.artifact a on a.artifact_id=l.src_id where l.dst_id=%s"""),
                         ("CITES", """select a.path, a.kind, a.seat, coalesce(a.first_commit_at, a.last_commit_at), l.n_mentions
                                      from pan.link l join pan.artifact a on a.artifact_id=l.dst_id where l.src_id=%s""")):
            cur.execute("select count(*) from (" + q + ") x", (aid,))
            total = cur.fetchone()[0]
            cur.execute(q + " order by 4 nulls last limit %s", (aid, k))
            rows = cur.fetchall()
            print("== {} ({} total{})".format(title, total, ", first {} shown".format(len(rows)) if total > len(rows) else ""))
            for p, kind, seat, when, n in rows:
                print("  {}  [{} {} x{}]  {}".format(str(when)[:10], kind, seat or "-", n, p))
