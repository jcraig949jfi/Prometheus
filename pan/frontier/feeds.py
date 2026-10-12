"""PAN-35: feed intake (charter C5) -- lab blogs, newsletters, societies and GitHub
release feeds (pan/frontier/seeds.json "feeds", copied from section (c) of the research
report). One conditional GET per feed per day (ETag / If-Modified-Since, state in
pan.feed_state), 2 s between any two calls, every call logged in pan.intake_call.

Entries land in pan.frontier_item: source 'github' for release feeds, else 'rss';
source_id = feed_id + '|' + the entry's own id (guid / atom:id, else its link);
query_tags carry FEED:<feed_id> and KIND:<kind>. published_at is the entry's own date
(published, else updated) or NULL -- never the poll time: a missing date is not "today".

Parsing is feedparser over an in-memory stream (never a bare bytes/str argument, which
feedparser would try as a URL or a local file name). Its DOCTYPE filter drops entity
declarations, so an entity-expansion bomb parses flat. A body that is not a feed (HTML
error page) yields zero entries and is recorded as a failure, not as items.
"""
import datetime as dt
import hashlib
import html
import io
import json
import re
import time
from urllib.parse import urljoin

from . import Client, finish_run, new_run, seeds

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def clean(s, cap=20000):
    return WS.sub(" ", html.unescape(TAG.sub(" ", s or ""))).strip()[:cap]


def when(st):
    """UTC datetime for a feed's struct_time, or None for a missing or placeholder date (year 1, 1970,
    far future): a sentinel is not a world date. No timestamp round trip (Windows rejects pre-1970)."""
    if not st or not (1990 <= st.tm_year <= dt.datetime.now(dt.timezone.utc).year + 1):
        return None
    return dt.datetime(*st[:6], tzinfo=dt.timezone.utc)


def release_prefix(feed):
    return "{} release: ".format(feed["feed_id"][3:].replace("/", " "))


def parse(body, feed, content_type=None):
    """(items, info) for one feed body. Pure: no network, no database."""
    import feedparser
    d = feedparser.parse(io.BytesIO(body), response_headers={"content-type": content_type} if content_type else None)
    info = dict(version=d.get("version") or "", entries=len(d.entries),
                bozo=(str(d.get("bozo_exception"))[:200] if d.get("bozo") else None))
    items = []
    for e in d.entries:
        title = clean(e.get("title"), 500)
        if feed["kind"] == "releases" and title:
            # "b11534" or "v1.2.0" says nothing alone: prefix the repository so full text can find it, with a
            # space not a slash (Postgres reads "owner/repo" as one file-path token: no lexeme for the repo name)
            title = release_prefix(feed) + title
        eid = (e.get("id") or e.get("link") or "").strip()
        if not eid:
            if not title:
                continue
            eid = "sha1:" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:16]
        summ = e.get("summary") or ""
        if not summ and e.get("content"):
            summ = e["content"][0].get("value", "")
        # dict.get bypasses feedparser's updated->published fallback mapping: each date is the one the feed wrote
        pub, upd = when(dict.get(e, "published_parsed")), when(dict.get(e, "updated_parsed"))
        authors = [a.get("name") for a in e.get("authors", []) if a.get("name")]
        items.append(dict(
            source="github" if feed["kind"] == "releases" else "rss",
            source_id="{}|{}".format(feed["feed_id"], eid)[:600],
            title=title or None, summary=clean(summ) or None,
            authors=authors or ([clean(e["author"], 200)] if e.get("author") else []),
            categories=[t.get("term") for t in e.get("tags", []) if t.get("term")][:20],
            published_at=pub or upd, updated_at=upd,
            url=urljoin(feed["url"], e["link"]) if e.get("link") else None,   # sakana.ai serves "/slug/"
            tags=["FEED:" + feed["feed_id"], "KIND:" + feed["kind"]],
            signals=dict(feed=feed["feed_id"], kind=feed["kind"]),
            raw=dict(entry_id=eid, date_basis="published" if pub else ("updated" if upd else None),
                     feed_url=feed["url"])))
    return items, info


def upsert(cur, items, run_id):
    """Insert or refresh items; returns the number newly inserted."""
    from psycopg2.extras import execute_values
    if not items:
        return 0
    rows = [(it["source"], it["source_id"], it["title"], it["summary"], it["authors"], it["categories"], None,
             it["published_at"], it["updated_at"], it["url"], it["tags"], json.dumps(it["signals"]), run_id,
             json.dumps(it["raw"])) for it in items]
    got = execute_values(cur, """
        insert into pan.frontier_item (source, source_id, title, summary, authors, categories, primary_cat,
            published_at, updated_at, url, query_tags, signals, run_id, raw) values %s
        on conflict (source, source_id) do update set title=excluded.title, summary=excluded.summary,
            authors=excluded.authors, categories=excluded.categories,
            published_at=coalesce(pan.frontier_item.published_at, excluded.published_at),
            updated_at=excluded.updated_at, url=excluded.url, signals=excluded.signals, raw=excluded.raw,
            last_seen_at=now(),
            query_tags=(select array_agg(distinct t) from unnest(pan.frontier_item.query_tags || excluded.query_tags) t)
        returning (xmax = 0)""", rows, page_size=500, fetch=True)
    return sum(1 for (ins,) in got if ins)


def dedupe(items):
    """A feed may repeat an entry id; keep the last copy (one row per source_id per statement)."""
    return list({it["source_id"]: it for it in items}.values())


FEED_KINDS = ("blog", "newsletter", "society", "releases")


def save_state(cur, fid, url, kind, final_url, etag, lastmod, status, err, n):
    """One pan.feed_state row per polled endpoint (feeds here; GitHub API endpoints in ghwatch)."""
    cur.execute("""
        insert into pan.feed_state as s (feed_id, url, kind, final_url, etag, last_modified, last_status,
            last_error, last_checked_at, last_ok_at, entries_last, consecutive_failures)
        values (%(id)s, %(url)s, %(kind)s, %(fin)s, %(etag)s, %(lm)s, %(st)s, %(err)s, now(),
                case when %(err)s is null then now() end, %(n)s, case when %(err)s is null then 0 else 1 end)
        on conflict (feed_id) do update set url=excluded.url, kind=excluded.kind,
            final_url=coalesce(excluded.final_url, s.final_url), etag=excluded.etag,
            last_modified=excluded.last_modified, last_status=excluded.last_status,
            last_error=excluded.last_error, last_checked_at=now(),
            last_ok_at=coalesce(excluded.last_ok_at, s.last_ok_at),
            entries_last=coalesce(excluded.entries_last, s.entries_last),
            consecutive_failures=case when excluded.last_error is null then 0
                                      else s.consecutive_failures + 1 end""",
                dict(id=fid, url=url, kind=kind, fin=final_url, etag=etag, lm=lastmod, st=status, err=err, n=n))


def run(force=False, only=None, out=print, feed_list=None):
    from .. import db
    sd = seeds()
    lim = sd["limits"]["feeds"]
    feeds = feed_list or [f for f in sd["feeds"] if not only or f["feed_id"] in only]
    run_id = new_run("frontier-feeds", dict(force=force, only=only, feeds=len(feeds)))
    cl = Client("feeds", run_id, lim["min_interval_s"])
    c = dict(feeds=len(feeds), polled=0, fresh_skipped=0, ok=0, not_modified=0, failed=[], entries=0, new_items=0,
             by_kind={})
    t0 = time.time()
    with db.cursor() as cur:
        cur.execute("""select feed_id, etag, last_modified, extract(epoch from now() - last_checked_at) / 3600,
                              consecutive_failures from pan.feed_state""")
        state = {r[0]: r[1:] for r in cur.fetchall()}
        for f in feeds:
            etag, lastmod, age_h, _ = state.get(f["feed_id"], (None, None, None, 0))
            if age_h is not None and float(age_h) < lim["per_feed_min_age_h"] and not force:
                c["fresh_skipped"] += 1
                continue
            hdr = {}
            if etag:
                hdr["If-None-Match"] = etag
            if lastmod:
                hdr["If-Modified-Since"] = lastmod
            r = cl.get(f["url"], headers=hdr, ok=(200, 304))
            c["polled"] += 1
            status = cl.log[-1][3]
            new, n_ent, err, fin = 0, None, None, (r.url if r is not None else None)
            if r is not None and status == 304:
                c["not_modified"] += 1
            elif r is not None:
                try:
                    items, info = parse(r.content, f, r.headers.get("Content-Type"))
                except Exception as e:      # one malformed feed is a failure row, never a crashed run
                    items, info = [], dict(version="", entries=None, bozo="{}: {}".format(type(e).__name__, e)[:200])
                n_ent = info["entries"]
                if not info["version"] and not items:
                    err = "not a feed ({})".format(info["bozo"] or "no entries")
                else:
                    items = dedupe(items)
                    new = upsert(cur, items, run_id)
                    c["ok"] += 1
                    c["entries"] += len(items)
                    c["new_items"] += new
                    c["by_kind"][f["kind"]] = c["by_kind"].get(f["kind"], 0) + new
                    etag, lastmod = r.headers.get("ETag"), r.headers.get("Last-Modified")
            else:
                err = cl.log[-1][8] or "HTTP {}".format(status)
            cl.log[-1] = cl.log[-1][:5] + (n_ent,) + cl.log[-1][6:]
            if err:
                c["failed"].append(f["feed_id"])
                etag = lastmod = None          # a failed poll never keeps a validator: next poll is a full GET
            save_state(cur, f["feed_id"], f["url"], f["kind"], fin, etag, lastmod, status, err, n_ent)
            out("  {:<44} {} {:>4} entries {:>3} new{}".format(f["feed_id"], status, n_ent if n_ent is not None else "-",
                                                             new, "  FAIL " + err if err else ""))
        cl.flush(cur)
    c["seconds"] = round(time.time() - t0, 1)
    finish_run(run_id, c, "OK" if not c["failed"] else "PARTIAL")
    out(json.dumps({k: c[k] for k in ("polled", "ok", "not_modified", "failed", "entries", "new_items", "seconds")}))
    return c


# Pages the research report found to have NO feed (section (c), "No feed found (404)"): live NEGATIVE inputs.
NEGATIVE_URLS = [dict(feed_id="NEG:ai.meta.com", url="https://ai.meta.com/blog/rss/", kind="blog"),
                 dict(feed_id="NEG:deeplearning.ai", url="https://www.deeplearning.ai/the-batch/feed/", kind="newsletter")]


def controls(out=print):
    """Live controls, written to roles/Pan/reports/controls/FEEDS_<ts>.json.
    POSITIVE every seeded feed parsed in its last poll; dated share per kind
    NEGATIVE the two report-listed no-feed URLs are failures with zero items (state rows removed after)
    CHEAT    an immediate forced re-poll inserts 0 new items (idempotent; 304s counted)
    RATE     no two feed calls closer than the configured interval (intake_call audit)"""
    from .. import REPO, db
    lim = seeds()["limits"]["feeds"]
    res = {}
    t_start = dt.datetime.now(dt.timezone.utc)
    with db.cursor() as cur:
        cur.execute("""select count(*), count(*) filter (where last_error is null and last_status in (200, 304)),
                              array_agg(feed_id) filter (where last_error is not null) from pan.feed_state
                       where feed_id not like 'NEG:%%' and kind = any(%s)""", (list(FEED_KINDS),))
        n, okn, bad = cur.fetchone()
        cur.execute("""select signals->>'kind', count(*), count(published_at) from pan.frontier_item
                       where source in ('rss', 'github') group by 1 order by 1""")
        dated = {k: dict(items=a, dated=b) for k, a, b in cur.fetchall()}
    res["POSITIVE"] = dict(feeds=n, ok=okn, failing=bad or [], dated_by_kind=dated, passed=bool(n) and okn == n)
    neg = run(force=True, out=lambda *_: None, feed_list=NEGATIVE_URLS)
    with db.cursor() as cur:
        cur.execute("select feed_id, last_status, last_error from pan.feed_state where feed_id like 'NEG:%'")
        rows = cur.fetchall()
        cur.execute("select count(*) from pan.frontier_item where source_id like 'NEG:%'")
        leaked = cur.fetchone()[0]
        cur.execute("delete from pan.feed_state where feed_id like 'NEG:%'")
    res["NEGATIVE"] = dict(rows=[list(r) for r in rows], items_inserted=neg["new_items"], items_in_table=leaked,
                           passed=len(neg["failed"]) == len(NEGATIVE_URLS) and neg["new_items"] == 0 and leaked == 0)
    again = run(force=True, out=lambda *_: None)
    res["CHEAT"] = dict(polled=again["polled"], not_modified_304=again["not_modified"], refetched_200=again["ok"],
                        new_items=again["new_items"], failed=again["failed"], passed=again["new_items"] == 0)
    with db.cursor() as cur:       # this control's own calls (NEGATIVE run, then the re-poll)
        cur.execute("""select min(gap), count(*) from (select extract(epoch from started_at - lag(started_at)
                       over (order by started_at)) as gap from pan.intake_call where source = 'feeds'
                       and started_at >= %s) g where gap is not null""", (t_start,))
        gap, pairs = cur.fetchone()
    # started_at is taken after the client's sleep, so a gap can undershoot the interval only by clock jitter
    res["RATE"] = dict(min_gap_s=round(float(gap), 3) if gap is not None else None, pairs=pairs,
                       interval_s=lim["min_interval_s"],
                       passed=gap is not None and float(gap) >= lim["min_interval_s"] - 0.05)
    res["verdict"] = {k: res[k]["passed"] for k in ("POSITIVE", "NEGATIVE", "CHEAT", "RATE")}
    d = REPO / "roles" / "Pan" / "reports" / "controls"
    p = d / "FEEDS_{}.json".format(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8", newline="\n")
    out(json.dumps(res["verdict"]))
    out("wrote {}".format(p))
    return res
