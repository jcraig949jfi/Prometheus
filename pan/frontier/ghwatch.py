"""PAN-36: GitHub watch (charter C5) -- the owners and repositories that section (d) of
the research report names (pan/frontier/seeds.json "github_owners", "github_repos").

Each run: one GET /users/{owner}/repos?sort=pushed per owner (their 30 most recently
pushed repositories, new ones included), then a few watched repositories that the sweep
did not cover, least recently checked first. Repositories land in pan.frontier_item as
source 'github', source_id 'repo:<owner>/<name>', published_at = created_at (when it
appeared in the world), updated_at = pushed_at; stars, language, topics in signals.

Anonymous by construction (QUESTIONS.md Q-005 default): the session ignores ~/.netrc
and the environment. The core limit (60/h) is per PUBLIC IP and shared with every host
behind it, so the run probes /rate_limit first (free), sends ETags (If-None-Match), and
stops while X-RateLimit-Remaining is still above a reserve (seeds.json limits).
"""
import datetime as dt
import json
import time

from . import Client, finish_run, new_run, seeds
from .feeds import save_state, upsert

API = "https://api.github.com"


def when(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def repo_item(r, tags):
    """A frontier item for one repository object of the GitHub REST API. Pure."""
    owner, name = r["full_name"].split("/", 1)
    desc = (r.get("description") or "").strip()
    topics = r.get("topics") or []
    summary = " | ".join(x for x in (desc, "topics: " + ", ".join(topics) if topics else "",
                                     "language: " + r["language"] if r.get("language") else "") if x)
    return dict(
        source="github", source_id="repo:" + r["full_name"],
        # owner and name as separate words: "owner/name" is one tsvector token (see feeds.release_prefix)
        title=("{} {}: {}".format(owner, name, desc) if desc else "{} {} (repository)".format(owner, name))[:500],
        summary=summary or None, authors=[owner], categories=topics[:20],
        published_at=when(r.get("created_at")), updated_at=when(r.get("pushed_at")), url=r.get("html_url"),
        tags=list(tags) + ["KIND:repo"],
        signals=dict(kind="repo", stars=r.get("stargazers_count"), forks=r.get("forks_count"),
                     language=r.get("language"), archived=r.get("archived"), fork=r.get("fork"),
                     license=(r.get("license") or {}).get("spdx_id"), pushed_at=r.get("pushed_at")),
        raw=dict(id=r.get("id"), full_name=r["full_name"], default_branch=r.get("default_branch")))


def run(force=False, out=print, owners=None, repos=None, max_repo_calls=None):
    from .. import db
    sd = seeds()
    lim = sd["limits"]["github_api"]
    owners = [o["owner"] for o in sd["github_owners"]] if owners is None else owners
    repos = [r["repo"] for r in sd["github_repos"]] if repos is None else repos
    max_repo_calls = lim["max_repo_calls_per_run"] if max_repo_calls is None else max_repo_calls
    run_id = new_run("frontier-github", dict(owners=len(owners), repos=len(repos), force=force,
                                             max_repo_calls=max_repo_calls))
    cl = Client("github_api", run_id, lim["min_interval_s"])
    cl.s.trust_env = False
    cl.s.headers["Accept"] = "application/vnd.github+json"
    c = dict(owners=len(owners), owner_ok=0, repo_ok=0, not_modified=0, fresh_skipped=0, failed=[], moved=[],
             repos_seen=0, new_items=0, rate_start=None, rate_end=None, stopped_for_rate=False)
    t0 = time.time()
    probe = cl.get(API + "/rate_limit")
    remaining = probe.json()["resources"]["core"]["remaining"] if probe is not None else 0
    c["rate_start"] = remaining
    seen = set()
    with db.cursor() as cur:
        cur.execute("""select feed_id, etag, extract(epoch from now() - last_checked_at) / 3600, last_checked_at
                       from pan.feed_state where kind in ('gh_owner', 'gh_repo')""")
        state = {r[0]: r[1:] for r in cur.fetchall()}
        # what each owner's sweep returned before: a 304 or a fresh-skip still covers those repositories
        cur.execute("""select substr(t, 10), array_agg(lower(raw->>'full_name')) from pan.frontier_item,
                              unnest(query_tags) t where source = 'github' and t like 'GH_OWNER:%%' group by 1""")
        known = {o: set(names) for o, names in cur.fetchall()}

        def poll(fid, kind, url, params=None):
            """(status, json or None); None status = not called (fresh, or the rate reserve)."""
            nonlocal remaining
            etag, age_h, _ = state.get(fid, (None, None, None))
            if age_h is not None and float(age_h) < 20.0 and not force:
                c["fresh_skipped"] += 1
                return None, None
            if remaining <= lim["reserve_remaining"]:
                c["stopped_for_rate"] = True
                return None, None
            r = cl.get(url, params=params, headers={"If-None-Match": etag} if etag else None, ok=(200, 304, 404))
            status = cl.log[-1][3]
            if r is not None and r.headers.get("X-RateLimit-Remaining") is not None:
                remaining = int(r.headers["X-RateLimit-Remaining"])
            elif status in (403, 429):
                remaining = 0                      # rate-limited: stop the run, never retry
                c["stopped_for_rate"] = True
            body = r.json() if (r is not None and status == 200) else None
            err = None if status in (200, 304) else (cl.log[-1][8] or "HTTP {}".format(status))
            if err:
                c["failed"].append(fid)
            elif status == 304:
                c["not_modified"] += 1
            n = len(body) if isinstance(body, list) else (1 if body else None)
            cl.log[-1] = cl.log[-1][:5] + (n,) + cl.log[-1][6:]
            save_state(cur, fid, url, kind, r.url if r is not None else None,
                       None if err else (r.headers.get("ETag") if status == 200 else etag), None, status, err, n)
            return status, body

        for o in owners:
            status, body = poll("ghapi:" + o, "gh_owner", "{}/users/{}/repos".format(API, o),
                                dict(sort="pushed", direction="desc", per_page=30, type="owner"))
            if status in (200, 304):
                c["owner_ok"] += 1
            if status in (None, 304):
                seen.update(known.get(o, ()))
            if body:
                items = [repo_item(r, ["GH_OWNER:" + o]) for r in body]
                c["new_items"] += upsert(cur, items, run_id)
                c["repos_seen"] += len(items)
                seen.update(r["full_name"].lower() for r in body)
            out("  owner {:<34} {} {}".format(o, status, len(body) if body else "-"))
        # watched repositories the sweep did not return, least recently checked first
        todo = [x for x in repos if x.lower() not in seen]
        todo.sort(key=lambda x: (state.get("ghrepo:" + x, (None, None, None))[2] is not None,
                                 state.get("ghrepo:" + x, (None, None, None))[2] or dt.datetime.min))
        calls = 0
        for x in todo:
            if calls >= max_repo_calls or c["stopped_for_rate"]:
                break
            status, body = poll("ghrepo:" + x, "gh_repo", "{}/repos/{}".format(API, x))
            if status is None:
                continue
            calls += 1
            if status in (200, 304):
                c["repo_ok"] += 1
            if body:
                if body["full_name"].lower() != x.lower():
                    c["moved"].append([x, body["full_name"]])     # redirect followed: the repo was renamed/moved
                c["new_items"] += upsert(cur, [repo_item(body, ["GH_WATCH"])], run_id)
                c["repos_seen"] += 1
            out("  repo  {:<34} {}".format(x, status))
        cl.flush(cur)
    c["rate_end"] = remaining
    c["seconds"] = round(time.time() - t0, 1)
    finish_run(run_id, c, "OK" if not c["failed"] else "PARTIAL")
    out(json.dumps({k: c[k] for k in ("owner_ok", "owners", "repo_ok", "not_modified", "failed", "moved", "repos_seen",
                                      "new_items", "rate_start", "rate_end", "stopped_for_rate", "seconds")}))
    return c


def controls(out=print):
    """Live controls -> roles/Pan/reports/controls/GITHUB_<ts>.json. Costs at most 4 counted calls.
    POSITIVE >= 90 percent of owners answered at their last poll; renamed watched repos listed
    NEGATIVE a nonexistent owner is a failure with 0 items (its state row removed after)
    CHEAT    a forced re-sweep of 3 owners inserts 0 new items; whether its 304s cost rate budget is recorded
    RATE     calls >= the interval apart; no run ended below the reserve without having stopped itself"""
    from .. import REPO, db
    lim = seeds()["limits"]["github_api"]
    t_start = dt.datetime.now(dt.timezone.utc)
    res = {}
    with db.cursor() as cur:
        cur.execute("""select count(*), count(*) filter (where last_error is null),
                              array_agg(feed_id) filter (where last_error is not null)
                       from pan.feed_state where kind = 'gh_owner' and feed_id not like 'ghapi:pan-nonexistent%%'""")
        n, okn, bad = cur.fetchone()
        cur.execute("""select counts from pan.run where kind = 'frontier-github' and status in ('OK', 'PARTIAL')
                       order by started_at desc limit 1""")
        last = (cur.fetchone() or [{}])[0] or {}
    res["POSITIVE"] = dict(owners=n, ok=okn, failing=bad or [], moved=last.get("moved"),
                           passed=bool(n) and okn >= 0.9 * n)
    neg = run(force=True, out=lambda *_: None, owners=["pan-nonexistent-owner-zz9q"], repos=[])
    with db.cursor() as cur:
        cur.execute("select last_status, last_error from pan.feed_state where feed_id = 'ghapi:pan-nonexistent-owner-zz9q'")
        row = cur.fetchone()
        cur.execute("delete from pan.feed_state where feed_id = 'ghapi:pan-nonexistent-owner-zz9q'")
    res["NEGATIVE"] = dict(state=list(row) if row else None, new_items=neg["new_items"], failed=neg["failed"],
                           passed=neg["failed"] == ["ghapi:pan-nonexistent-owner-zz9q"] and neg["new_items"] == 0)
    owners = [o["owner"] for o in seeds()["github_owners"]][:3]
    again = run(force=True, out=lambda *_: None, owners=owners, repos=[])
    res["CHEAT"] = dict(owners=owners, new_items=again["new_items"], not_modified_304=again["not_modified"],
                        rate_start=again["rate_start"], rate_end=again["rate_end"],
                        note="rate_start - rate_end = counted calls; 304s that do not count leave it unchanged",
                        passed=again["new_items"] == 0 and not again["failed"])
    with db.cursor() as cur:
        cur.execute("""select min(gap), count(*) from (select extract(epoch from started_at - lag(started_at)
                       over (order by started_at)) as gap from pan.intake_call where source = 'github_api'
                       and started_at >= %s) g where gap is not null""", (t_start,))
        gap, pairs = cur.fetchone()
        cur.execute("""select count(*) from pan.run where kind = 'frontier-github' and status in ('OK', 'PARTIAL')
                       and (counts->>'rate_end')::int < %s and not (counts->>'stopped_for_rate')::boolean""",
                    (lim["reserve_remaining"],))
        below = cur.fetchone()[0]
    res["RATE"] = dict(min_gap_s=round(float(gap), 3) if gap is not None else None, pairs=pairs,
                       interval_s=lim["min_interval_s"], runs_below_reserve_unstopped=below,
                       passed=gap is not None and float(gap) >= lim["min_interval_s"] - 0.05 and below == 0)
    res["verdict"] = {k: res[k]["passed"] for k in ("POSITIVE", "NEGATIVE", "CHEAT", "RATE")}
    p = REPO / "roles" / "Pan" / "reports" / "controls" / "GITHUB_{}.json".format(
        dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8", newline="\n")
    out(json.dumps(res["verdict"]))
    out("wrote {}".format(p))
    return res
