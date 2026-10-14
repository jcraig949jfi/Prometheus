"""PAN-17: incremental refresh of the catalog to the current origin/main.

  1. git fetch (in this worktree; never pull), resolve origin/main
  2. if the catalog is already at that SHA: a no-op, reported as such
  3. repository tree -> pan.artifact (upsert; rows absent from the tree removed); then the access rules
     (classify, refuse) before anything is read or indexed
  4. commits -> pan.commit (new ones only; oracle as in commits.py)
  5. chunk only blobs whose indexed_blob differs
  6. embed only chunks / documents without a vector for the current models
  7. rebuild the in-process vector caches from shards filtered by the ids that
     exist in Postgres now (stale shard rows from re-chunked files are dropped)

Productivity signal (base role rule 8): commits_new, artifacts_changed,
chunks_new, vectors_new. A refresh that changes nothing says "no-op" with the
SHA it checked; it is not reported as work.
"""
import json
import subprocess
import time

from . import REPO


HOLDERS_SQL = """select a.application_name, coalesce(host(a.client_addr), 'local'), a.state,
                         extract(epoch from now() - a.xact_start)::int,
                         left(regexp_replace(a.query, '\\s+', ' ', 'g'), 120)
                    from pg_locks l join pg_stat_activity a on a.pid = l.pid
                   where l.relation = '{s}.lexeme_df'::regclass and l.granted and a.pid <> pg_backend_pid()"""


def rebuild_lexeme_df(conn=None, schema="pan", lock_timeout="10s", attempts=3, pause_s=10, report=None):
    """Rebuild {schema}.lexeme_df beside the live table, then swap it in.

    Before 2026-10-14 this was truncate + insert in one transaction, so every full-text search
    waited for the whole rebuild (40 s normally, 130-165 s on a loaded host). Now only the
    renames take the exclusive lock. lock_timeout bounds each swap attempt: a pending exclusive
    lock would also queue new readers, so if a long reader holds the table the attempt gives up,
    the holders are recorded, and the swap is retried after pause_s; after `attempts` failures
    the old table stays until the next refresh (one swap timed out on 2026-10-14 07:41Z, holder
    unknown -- hence the record). The table comment is carried over (LIKE does not copy it); the
    table has no grants beyond its owner (checked 2026-10-14).
    Returns the number of lexemes, or None if every swap attempt timed out. If `report` is a
    dict it receives swap_attempts and blockers (application, client, state, xact age s, query)."""
    import time
    from psycopg2.errors import LockNotAvailable
    from . import db
    report = report if report is not None else {}
    report.update(swap_attempts=0, blockers=[])
    own = conn is None
    conn = conn or db.connect(statement_timeout_ms=1800000)
    s = schema
    try:
        cur = conn.cursor()
        cur.execute("select obj_description('{}.lexeme_df'::regclass)".format(s))
        comment = cur.fetchone()[0]
        cur.execute("drop table if exists {s}.lexeme_df_new".format(s=s))
        cur.execute("create table {s}.lexeme_df_new (like {s}.lexeme_df including all)".format(s=s))
        cur.execute("insert into {s}.lexeme_df_new select word, ndoc, nentry from ts_stat('select tsv from {s}.chunk')"
                    .format(s=s))
        n = cur.rowcount
        conn.commit()
        for attempt in range(1, attempts + 1):
            report["swap_attempts"] = attempt
            try:
                cur.execute("set local lock_timeout = %s", (lock_timeout,))
                cur.execute("alter table {s}.lexeme_df rename to lexeme_df_old".format(s=s))
                cur.execute("alter table {s}.lexeme_df_new rename to lexeme_df".format(s=s))
                cur.execute("drop table {s}.lexeme_df_old".format(s=s))
                cur.execute("alter index if exists {s}.lexeme_df_new_pkey rename to lexeme_df_pkey".format(s=s))
                if comment:
                    cur.execute("comment on table {s}.lexeme_df is %s".format(s=s), (comment,))
                conn.commit()
                break
            except LockNotAvailable:
                conn.rollback()
                cur.execute(HOLDERS_SQL.format(s=s))
                report["blockers"].extend(list(r) for r in cur.fetchall())
                conn.commit()
                if attempt == attempts:
                    cur.execute("drop table if exists {s}.lexeme_df_new".format(s=s))
                    conn.commit()
                    return None
                time.sleep(pause_s)
        cur.execute("analyze {s}.lexeme_df".format(s=s))
        conn.commit()
        return n
    except Exception:
        conn.rollback()
        raise
    finally:
        if own:
            conn.close()


def run(out=print, embed_chunks=True, embed_docs=True):
    from . import chunker, commits, db, embed, inventory, search
    t0 = time.time()
    subprocess.run(["git", "fetch", "-q", "origin"], cwd=REPO, timeout=120, check=False)
    head = subprocess.run(["git", "rev-parse", "origin/main"], cwd=REPO, capture_output=True, text=True,
                          timeout=60, check=True).stdout.strip()
    with db.cursor() as cur:
        cur.execute("select max(repo_sha), count(*) from pan.artifact where source='git'")
        cat, n_before = cur.fetchone()
    if cat == head:
        # the comms/Moonshot indexes ran just before this (python -m pan refresh): classify what they added
        from . import access
        acc = access.apply_rules(out=lambda *_: None)
        res = dict(noop=True, sha=head, access_newly_classified=sum(v.get("newly_classified", 0) for v in acc.values()),
                   seconds=round(time.time() - t0, 1))
        out(json.dumps(res))
        return res
    with db.cursor() as cur:
        cur.execute("select path, blob_sha from pan.artifact where source='git'")
        before = dict(cur.fetchall())
    # 3. tree -> artifacts, via the inventory's repo writer only (no fs walk, no cluster scan)
    _rows = []
    for path, bsha, size in inventory.repo_tree(head):
        kind, seat, top, e = inventory.classify(path, head)
        _rows.append(dict(path=path, blob_sha=bsha, size_bytes=size, kind=kind, seat=seat, top_dir=top, ext=e))
    changed = sum(1 for r in _rows if before.get(r["path"]) != r["blob_sha"])
    removed = len(set(before) - {r["path"] for r in _rows})
    _upsert_repo(_rows, head)
    # 3b. access rules BEFORE anything reads or indexes a new file (PAN-42/45): a new file matching a CLASSIFY rule
    # would otherwise sit at the default class PROGRAM -- visible at generator clearance -- until someone ran
    # `pan access apply`; REFUSE rules mark refused files indexed so the chunker never opens them
    from . import access
    acc = access.apply_rules(out=lambda *_: None)
    # 4. commits
    c = commits.run(head, out=lambda *_: None)
    # 5. chunks for changed blobs only
    ch = chunker.run(out=lambda *_: None)
    # 6. vectors for what has none
    ev = embed.run(out=lambda *_: None) if embed_chunks else {"embedded": 0}
    ed = embed.run_docs(out=lambda *_: None) if embed_docs else {"embedded": 0}
    # 6b. derived tables that depend on chunks: lexeme frequencies (full-text cap) and links
    lx_t = time.time()
    lx_report = {}
    lexemes = rebuild_lexeme_df(report=lx_report)
    from . import links
    lk = links.run(out=lambda *_: None)
    derived_s = round(time.time() - lx_t, 1)
    # 7. caches rebuilt against the ids that exist now
    search._CACHE.clear()
    search._DCACHE.clear()
    search.load_matrix(embed.default_model(), refresh=True)
    res = dict(noop=False, from_sha=cat, to_sha=head, artifacts_changed=changed, artifacts_removed=removed,
               commits_total=c.get("commits"), chunks_new=ch.get("chunks"), files_rechunked=ch.get("files_chunked"),
               chunk_vectors_new=ev.get("embedded"), doc_vectors_new=ed.get("embedded"), links=lk.get("links"),
               derived_seconds=derived_s, lexemes=lexemes, lexdf_swap_attempts=lx_report.get("swap_attempts"),
               lexdf_blockers=lx_report.get("blockers"),
               access_newly_classified=sum(v.get("newly_classified", 0) for v in acc.values()),
               seconds=round(time.time() - t0, 1))
    out(json.dumps(res))
    return res


def _upsert_repo(rows, sha):
    import datetime as dt
    from psycopg2.extras import execute_values
    from . import db, host
    run_id = "refresh-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    with db.cursor(statement_timeout_ms=900000) as cur:
        cur.execute("insert into pan.run (run_id, kind, host, git_sha) values (%s,'refresh',%s,%s)",
                    (run_id, host(), sha))
        execute_values(cur, """
            insert into pan.artifact (source, host, path, repo_sha, blob_sha, size_bytes, ext, kind, seat, top_dir, run_id, updated_at)
            values %s
            on conflict (source, host, path) do update set repo_sha=excluded.repo_sha, blob_sha=excluded.blob_sha,
              size_bytes=excluded.size_bytes, ext=excluded.ext, kind=excluded.kind, seat=excluded.seat,
              top_dir=excluded.top_dir, run_id=excluded.run_id, updated_at=now()""",
            [("git", "repo", r["path"], sha, r["blob_sha"], r["size_bytes"], r["ext"], r["kind"], r["seat"],
              r["top_dir"], run_id, dt.datetime.now(dt.timezone.utc)) for r in rows], page_size=5000)
        cur.execute("delete from pan.artifact where source='git' and host='repo' and repo_sha <> %s", (sha,))
        removed = cur.rowcount
        cur.execute("update pan.run set finished_at=now(), status='OK', counts=%s where run_id=%s",
                    (json.dumps({"artifacts": len(rows), "removed": removed}), run_id))
