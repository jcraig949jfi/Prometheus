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
    run_id = "commits-{}-{}".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ"), host().lower())
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
        # oracle: every commit reachable from the SHA is present
        cur.execute("select count(*) from pan.commit where sha = any(%s)", ([c["sha"] for c in commits],))
        have = cur.fetchone()[0]
        ok = (have == expect == len(commits))
        cur.execute("""update pan.artifact a set first_commit_at = x.first, last_commit_at = x.last, last_commit_sha = x.sha
                       from (select cf.path, min(c.committed_at) as first, max(c.committed_at) as last,
                                    (array_agg(c.sha order by c.committed_at desc))[1] as sha
                             from pan.commit_file cf join pan.commit c on c.sha = cf.sha group by cf.path) x
                       where a.source = 'git' and a.path = x.path""")
        stamped = cur.rowcount
        counts = dict(commits=len(commits), file_changes=len(files), rev_list=expect, present=have,
                      oracle_ok=ok, artifacts_stamped=stamped, with_seat=sum(1 for c in commits if c["seat"]),
                      seconds=round(time.time() - t0, 1))
        cur.execute("update pan.run set finished_at=now(), status=%s, counts=%s where run_id=%s",
                    ("OK" if ok else "FAILED", json.dumps(counts), run_id))
    out(json.dumps(counts))
    if not ok:
        raise SystemExit("ORACLE FAILED: pan.commit has {} of {} commits reachable from {}".format(have, expect, full))
    return counts
