"""PAN-20: index the comms message history (read-only) so the program's conversation
is searchable beside its files.

Each comms.messages row becomes a pan.artifact with source='comms', host='M1',
path='comms:#<id>', kind='comms_<kind>', seat = the sender's seat, title = the
subject, last_commit_at = created_at, blob_sha = the message's own sha256 (so an
unchanged message is never re-chunked). Bodies are chunked like Markdown. Nothing
is written to schema comms.

ORACLE: after a run, the number of comms artifacts equals count(*) of
comms.messages read in the same transaction snapshot.
"""
import datetime as dt
import json
import re
import time

from . import host

SENDER = re.compile(r"^([A-Za-z0-9_-]+)")


def run(out=print):
    from psycopg2.extras import execute_values
    from . import chunker, db
    t0 = time.time()
    run_id = "comms-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    conn = db.connect()
    try:
        cur = conn.cursor()
        cur.execute("set transaction isolation level repeatable read")
        cur.execute("insert into pan.run (run_id, kind, host) values (%s,'comms-index',%s)", (run_id, host()))
        cur.execute("""select id, created_at, sender, recipients, kind, subject, body, sha256 from comms.messages
                       order by id""")
        msgs = cur.fetchall()
        cur.execute("select path, blob_sha from pan.artifact where source='comms'")
        have = dict(cur.fetchall())
        todo = [m for m in msgs if have.get("comms:#{}".format(m[0])) != m[7]]
        rows = []
        for mid, created, sender, rcpt, kind, subj, body, sha in todo:
            m = SENDER.match(sender or "")
            rows.append(("comms", "M1", "comms:#{}".format(mid), sha, sha, len(body.encode("utf-8")), "",
                         "comms_" + kind, m.group(1) if m else None, "comms", created, subj[:200], True,
                         run_id))
        if rows:
            execute_values(cur, """
                insert into pan.artifact (source, host, path, repo_sha, blob_sha, size_bytes, ext, kind, seat, top_dir,
                                          last_commit_at, title, is_text, run_id) values %s
                on conflict (source, host, path) do update set blob_sha=excluded.blob_sha, size_bytes=excluded.size_bytes,
                    kind=excluded.kind, seat=excluded.seat, last_commit_at=excluded.last_commit_at,
                    title=excluded.title, run_id=excluded.run_id, updated_at=now()""", rows, page_size=1000)
            cur.execute("select path, artifact_id from pan.artifact where source='comms' and path = any(%s)",
                        ([r[2] for r in rows],))
            ids = dict(cur.fetchall())
            chunks, upd = [], []
            for mid, created, sender, rcpt, kind, subj, body, sha in todo:
                aid = ids["comms:#{}".format(mid)]
                head = "{} -> {} [{}] {}".format(sender, ",".join(rcpt or []), kind, subj)[:300]
                text = (body or "").replace("\x00", "").replace("\r\n", "\n")
                pieces = chunker.split(text, ".md") or [(1, 1, "", "")]
                for o, (ls, le, h, b) in enumerate(pieces):
                    chunks.append((aid, o, ls, le, (head + (" > " + h if h else ""))[:400], b or subj, len(b or subj)))
                upd.append((aid, len(pieces), sha))
            cur.execute("delete from pan.chunk where artifact_id = any(%s)", ([u[0] for u in upd],))
            execute_values(cur, """insert into pan.chunk (artifact_id, ord, line_start, line_end, heading, body, n_chars)
                                   values %s""", chunks, page_size=1000)
            execute_values(cur, """update pan.artifact a set n_chunks = v.n, indexed_blob = v.b
                                   from (values %s) as v(id, n, b) where a.artifact_id = v.id""", upd)
        cur.execute("select count(*) from pan.artifact where source='comms'")
        n_art = cur.fetchone()[0]
        ok = n_art == len(msgs)
        counts = dict(messages=len(msgs), indexed_now=len(todo), comms_artifacts=n_art, oracle_ok=ok,
                      seconds=round(time.time() - t0, 1))
        cur.execute("update pan.run set finished_at=now(), status=%s, counts=%s where run_id=%s",
                    ("OK" if ok else "FAILED", json.dumps(counts), run_id))
        conn.commit()
    finally:
        conn.close()
    out(json.dumps(counts))
    return counts
