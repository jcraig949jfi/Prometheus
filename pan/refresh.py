"""PAN-17: incremental refresh of the catalog to the current origin/main.

  1. git fetch (in this worktree; never pull), resolve origin/main
  2. if the catalog is already at that SHA: a no-op, reported as such
  3. repository tree -> pan.artifact (upsert; rows absent from the tree removed)
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
        res = dict(noop=True, sha=head, seconds=round(time.time() - t0, 1))
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
    # 4. commits
    c = commits.run(head, out=lambda *_: None)
    # 5. chunks for changed blobs only
    ch = chunker.run(out=lambda *_: None)
    # 6. vectors for what has none
    ev = embed.run(out=lambda *_: None) if embed_chunks else {"embedded": 0}
    ed = embed.run_docs(out=lambda *_: None) if embed_docs else {"embedded": 0}
    # 7. caches rebuilt against the ids that exist now
    search._CACHE.clear()
    search._DCACHE.clear()
    search.load_matrix(embed.default_model(), refresh=True)
    res = dict(noop=False, from_sha=cat, to_sha=head, artifacts_changed=changed, artifacts_removed=removed,
               commits_total=c.get("commits"), chunks_new=ch.get("chunks"), files_rechunked=ch.get("files_chunked"),
               chunk_vectors_new=ev.get("embedded"), doc_vectors_new=ed.get("embedded"),
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
