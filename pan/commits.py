"""PAN-06: index git history reachable from a SHA into pan.commit / pan.commit_file,
then stamp first/last commit times onto pan.artifact. Also writes the history
to the lake as Parquet (commits.parquet, commit_files.parquet).

Independent oracle (base role: verify the property): after loading, the
number of commits in pan.commit reachable from the SHA must equal
`git rev-list --count <sha>`; the run fails if it does not.
"""
import datetime as dt
import json
import re
import subprocess
import time

from . import REPO, host, lake

FMT = "%x1e%H%x1f%P%x1f%an%x1f%aI%x1f%cI%x1f%s%x1f%b%x1d"
SUBJ = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*)(?:\[([A-Za-z0-9_.-]+)\])?:")

# Stamp first/last commit time and the last commit's sha onto git artifacts.
# - Commit times have 1 s resolution, so several commits can share a path's latest time
#   (72 paths on 2026-10-14). The tip is then the tied commit that is not a parent of another
#   tied commit, and sha breaks any remaining tie, so the result no longer flips between runs.
# - Only rows whose values change are written (28-40 of 79,730 on 2026-10-14, instead of all).
# - Window functions only, no self-join: a self-join of the tied candidates was planned as a
#   nested loop (estimated 1 row, actually ~80k) and ran past 300 s. A candidate is a parent of
#   another tied candidate when its sha occurs in the comma-joined parents of the path's tied
#   candidates; shas are fixed-width hex, so the substring test cannot match across a comma.
# - host = 'repo' (every git artifact's host; inventory.py relies on it too) lets the join use the
#   unique (source, host, path) index: tip is underestimated (~370 rows vs ~100k), so the planner
#   picks a nested loop, which without host scanned every git row per tip row.
STAMP_SQL = """
with fc as (select cf.path, c.sha, c.committed_at, c.parents
              from {s}.commit_file cf join {s}.commit c on c.sha = cf.sha),
     w as (select path, sha, parents, committed_at,
                  min(committed_at) over (partition by path) as first,
                  max(committed_at) over (partition by path) as last
             from fc),
     cand as (select path, sha, first, last,
                     string_agg(array_to_string(parents, ','), ',') over (partition by path) as tied_parents
                from w where committed_at = last),
     tip as (select distinct on (path) path, sha, first, last from cand
              order by path, coalesce(position(sha in tied_parents), 0) > 0, sha desc)
update {s}.artifact a set first_commit_at = tip.first, last_commit_at = tip.last, last_commit_sha = tip.sha
  from tip
 where a.source = 'git' and a.host = 'repo' and a.path = tip.path
   and (a.first_commit_at, a.last_commit_at, a.last_commit_sha) is distinct from (tip.first, tip.last, tip.sha)"""


def stamp(cur, schema="pan"):
    """Stamp commit times and tip sha onto git artifacts; returns the number of rows that changed."""
    cur.execute(STAMP_SQL.format(s=schema))
    return cur.rowcount


def parse_log(sha: str):
    out = subprocess.run(["git", "-c", "core.quotepath=off", "log", "--no-renames", "--name-status",
                          "--format=" + FMT, sha], cwd=REPO, capture_output=True, timeout=1800, check=True).stdout
    text = out.decode("utf-8", "replace")
    commits, files = [], []
    for rec in text.split("\x1e"):
        if not rec.strip():
            continue
        head, _, tail = rec.partition("\x1d")
        f = head.split("\x1f")
        if len(f) < 7:
            continue
        h, parents, an, ai, ci, subj, body = f[:7]
        names = []
        for line in tail.splitlines():
            if "\t" in line:
                st, _, p = line.partition("\t")
                names.append((h, p, st))
        commits.append(dict(sha=h, parents=parents.split() if parents else [], author_name=an,
                            authored_at=ai, committed_at=ci, subject=subj.replace("\x00", ""),
                            body=body.strip().replace("\x00", ""), n_files=len(names)))
        files.extend(names)
    return commits, files


def run(sha: str = "origin/main", out=print):
    import pyarrow as pa
    import pyarrow.parquet as pq
    from psycopg2.extras import execute_values
    from . import db, inventory
    t0 = time.time()
    full = subprocess.run(["git", "rev-parse", sha], cwd=REPO, capture_output=True, text=True, timeout=60,
                          check=True).stdout.strip()
    expect = int(subprocess.run(["git", "rev-list", "--count", full], cwd=REPO, capture_output=True, text=True,
                                timeout=600, check=True).stdout.strip())
    commits, files = parse_log(full)
    seats = inventory.seats(full)
    for c in commits:
        m = SUBJ.match(c["subject"])
        c["seat"], c["instance"] = None, None
        if m and m.group(1).lower() in seats:
            c["seat"], c["instance"] = seats[m.group(1).lower()], m.group(2)
    out("parsed {} commits / {} file changes in {:.1f}s (rev-list says {})".format(len(commits), len(files),
                                                                                   time.time() - t0, expect))
    run_id = "commits-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), host().lower())
    d = lake() / "git"
    d.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(commits), d / "commits.parquet", compression="zstd")
    pq.write_table(pa.Table.from_pylist([dict(sha=a, path=b, status=c) for a, b, c in files]),
                   d / "commit_files.parquet", compression="zstd")
    with db.cursor(statement_timeout_ms=1800000) as cur:
        cur.execute("insert into pan.run (run_id, kind, host, git_sha) values (%s,'commits',%s,%s)",
                    (run_id, host(), full))
        execute_values(cur, """insert into pan.commit (sha, parents, author_name, authored_at, committed_at, subject,
                                body, seat, instance, n_files) values %s on conflict (sha) do nothing""",
                       [(c["sha"], c["parents"], c["author_name"], c["authored_at"], c["committed_at"], c["subject"],
                         c["body"], c["seat"], c["instance"], c["n_files"]) for c in commits], page_size=2000)
        execute_values(cur, "insert into pan.commit_file (sha, path, status) values %s on conflict do nothing",
                       files, page_size=10000)
    # Commit the rows, then ANALYZE, before the artifact stamp: without statistics
    # on freshly loaded tables the planner chose a nested loop over ~73k x ~60k
    # rows and ran CPU-bound for over 5 minutes (measured 2026-10-09).
    with db.cursor(autocommit=True) as cur:
        cur.execute("analyze pan.commit")
        cur.execute("analyze pan.commit_file")
        cur.execute("analyze pan.artifact")
    with db.cursor(statement_timeout_ms=1800000) as cur:
        # oracle: every commit reachable from the SHA is present
        cur.execute("select count(*) from pan.commit where sha = any(%s)", ([c["sha"] for c in commits],))
        have = cur.fetchone()[0]
        ok = (have == expect == len(commits))
        stamped = stamp(cur)    # rows that changed (before 2026-10-14: every matched row)
        counts = dict(commits=len(commits), file_changes=len(files), rev_list=expect, present=have,
                      oracle_ok=ok, artifacts_stamped=stamped, with_seat=sum(1 for c in commits if c["seat"]),
                      seconds=round(time.time() - t0, 1))
        cur.execute("update pan.run set finished_at=now(), status=%s, counts=%s where run_id=%s",
                    ("OK" if ok else "FAILED", json.dumps(counts), run_id))
    out(json.dumps(counts))
    if not ok:
        raise SystemExit("ORACLE FAILED: pan.commit has {} of {} commits reachable from {}".format(have, expect, full))
    return counts
