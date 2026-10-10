"""Catalogue Moonshot's published epochs (OP-NF2; Themis #2010/#2015, contract moonshot/nf/INTERFACE_CONTRACT.md
s6) so `pan search` and `pan pivot` find them beside files and comms. Pull model, read-only: each row of
moonshot.catalog_v (production) and moonshot_qual.catalog_v (qualification), whichever exist, becomes a
pan.artifact with source='moonshot', host='M1', path=<ref>, blob_sha=<object_sha256> (an unchanged epoch is never
re-chunked), kind=<kind>, seat='Themis' (Moonshot's owning seat), title, last_commit_at=<published_at>; title and
summary are its one chunk. Rows that left the views are removed. Nothing is written to Moonshot's schemas.

ORACLE: after a run, the number of moonshot artifacts equals the number of view rows read in the same snapshot.
"""
import datetime as dt
import json
import time

from . import host

VIEWS = ("moonshot.catalog_v", "moonshot_qual.catalog_v")


def run(out=print):
    from psycopg2.extras import execute_values
    from . import db
    t0 = time.time()
    run_id = "moonshot-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    conn = db.connect()
    try:
        cur = conn.cursor()
        cur.execute("set transaction isolation level repeatable read")
        rows, views = [], {}
        for v in VIEWS:
            cur.execute("select to_regclass(%s)", (v,))
            if cur.fetchone()[0] is None:
                views[v] = None
                continue
            cur.execute("select object_sha256, kind, title, summary, published_at, ref from {}".format(v))
            got = cur.fetchall()
            views[v] = len(got)
            rows += got
        if not any(views.values()) and all(n is None for n in views.values()):
            counts = dict(views=views, note="no catalog view exists yet", seconds=round(time.time() - t0, 1))
            conn.rollback()
            out(json.dumps(counts))
            return counts
        cur.execute("insert into pan.run (run_id, kind, host) values (%s,'moonshot-index',%s)", (run_id, host()))
        cur.execute("select path, blob_sha from pan.artifact where source='moonshot'")
        have = dict(cur.fetchall())
        live = {r[5] for r in rows}
        gone = [p for p in have if p not in live]
        if gone:
            cur.execute("""delete from pan.chunk where artifact_id in
                           (select artifact_id from pan.artifact where source='moonshot' and path = any(%s))""", (gone,))
            cur.execute("delete from pan.artifact where source='moonshot' and path = any(%s)", (gone,))
        todo = [r for r in rows if have.get(r[5]) != r[0]]
        if todo:
            execute_values(cur, """
                insert into pan.artifact (source, host, path, repo_sha, blob_sha, size_bytes, ext, kind, seat, top_dir,
                                          last_commit_at, title, is_text, run_id) values %s
                on conflict (source, host, path) do update set blob_sha=excluded.blob_sha, size_bytes=excluded.size_bytes,
                    kind=excluded.kind, last_commit_at=excluded.last_commit_at, title=excluded.title,
                    run_id=excluded.run_id, updated_at=now()""",
                [("moonshot", "M1", ref, sha, sha, len((summ or "").encode("utf-8")), "", kind, "Themis", "moonshot",
                  pub, (title or ref)[:200], True, run_id) for sha, kind, title, summ, pub, ref in todo], page_size=500)
            cur.execute("select path, artifact_id from pan.artifact where source='moonshot' and path = any(%s)",
                        ([r[5] for r in todo],))
            ids = dict(cur.fetchall())
            cur.execute("delete from pan.chunk where artifact_id = any(%s)", (list(ids.values()),))
            execute_values(cur, """insert into pan.chunk (artifact_id, ord, line_start, line_end, heading, body, n_chars)
                                   values %s""",
                           [(ids[ref], 0, 1, 1, (title or ref)[:400], summ or title or ref, len(summ or title or ref))
                            for sha, kind, title, summ, pub, ref in todo], page_size=500)
            execute_values(cur, """update pan.artifact a set n_chunks = 1, indexed_blob = v.b
                                   from (values %s) as v(id, b) where a.artifact_id = v.id""",
                           [(ids[r[5]], r[0]) for r in todo])
        cur.execute("select count(*) from pan.artifact where source='moonshot'")
        n_art = cur.fetchone()[0]
        ok = n_art == len(rows)
        counts = dict(views=views, rows=len(rows), indexed_now=len(todo), removed=len(gone), moonshot_artifacts=n_art,
                      oracle_ok=ok, seconds=round(time.time() - t0, 1))
        cur.execute("update pan.run set finished_at=now(), status=%s, counts=%s where run_id=%s",
                    ("OK" if ok else "FAILED", json.dumps(counts), run_id))
        conn.commit()
    finally:
        conn.close()
    out(json.dumps(counts))
    return counts
