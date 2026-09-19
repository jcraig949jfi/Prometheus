"""Every commit on every remote and local ref since --since, classified by
subject (seat, lane, instance, ids, lineage words). Local-only refs are
machine-scoped: a commit no remote ref contains is recorded as seen on
this machine, because another machine's instance cannot see it."""
from __future__ import annotations

from collections import defaultdict

from atlas import classify, db, gitsrc

VERSION = "commits/2"


def run(args) -> dict:
    since = args.since
    refs = gitsrc.refs()
    host = db.this_host()
    member = defaultdict(list)
    remote_seen = set()
    for name, sha, _date in refs:
        short = name.replace("refs/remotes/", "").replace("refs/heads/", "local:")
        for c in gitsrc.git("rev-list", "--since=" + since, sha).split():
            member[c].append(short)
            if name.startswith("refs/remotes/"):
                remote_seen.add(c)
    on_main = set(gitsrc.git("rev-list", "--since=" + since, "origin/main").split())
    shas = sorted({sha for _n, sha, _d in refs})
    out = gitsrc.git("log", "--since=" + since, "--format=%x1e%H%x1f%aI%x1f%s%x1f%b%x1d", "--name-only", *shas,
                     timeout=900)
    rows, tags = [], {}
    for rec in out.split("\x1e"):
        if not rec.strip():
            continue
        head, _, names = rec.partition("\x1d")
        sha, date, subject, body = (head.split("\x1f") + ["", "", "", ""])[:4]
        c = classify.classify_commit(subject, body)
        n_paths = len([p for p in names.splitlines() if p.strip()])
        rows.append({"sha": sha, "authored_at": date, "subject": subject[:500], "seat": c["seat"],
                     "lane": c["lane"], "instance_tag": c["instance_tag"], "session": c["session"],
                     "ids": c["ids"], "classes": c["classes"], "on_main": sha in on_main,
                     "refs_seen": sorted(member.get(sha, []))[:40],
                     "seen_on_host": None if sha in remote_seen else host,
                     "n_paths": n_paths})
        t = c["instance_tag"]
        if t:
            s = tags.setdefault(t, {"instance_tag": t, "seat": c["seat"],
                                    "host_id": classify.host_from_tag(t),
                                    "first_seen_at": date, "last_seen_at": date, "n_commits": 0})
            s["n_commits"] += 1
            s["first_seen_at"] = min(s["first_seen_at"], date)
            s["last_seen_at"] = max(s["last_seen_at"], date)
    with db.harvest("commits", VERSION, source_ref="{} refs since {}".format(len(refs), since),
                    source_sha=gitsrc.resolve("origin/main")) as h:
        with h.conn.cursor() as cur:
            h.count("git_commit", db.upsert(cur, "atlas.git_commit", rows, ["sha"], h.id))
            h.count("seat_instance", db.upsert(cur, "atlas.seat_instance", list(tags.values()),
                                               ["instance_tag"], h.id))
        h.count("local_only", sum(1 for r in rows if r["seen_on_host"]))
        return h.counts
