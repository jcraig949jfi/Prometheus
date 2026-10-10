"""PAN-09: arXiv intake through export.arxiv.org/api/query (Atom), one connection,
4 s between calls (ToU: 1 request / 3 s across all machines; 75 percent rule).

Each seed query (pan/frontier/seeds.json) is run newest-first; an item surfaced by
several queries carries all their tags. Key arXiv ids from the research report are
fetched by id_list. Versions are folded: source_id is the id without "vN".
"""
import json
import re
import xml.etree.ElementTree as ET

from . import Client, finish_run, new_run, seeds

API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom",
      "o": "http://a9.com/-/spec/opensearch/1.1/"}


def parse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    total = root.findtext("o:totalResults", default="0", namespaces=NS)
    out = []
    for e in root.findall("a:entry", NS):
        idurl = e.findtext("a:id", default="", namespaces=NS)
        m = re.search(r"abs/([^v]+?)(v\d+)?$", idurl)
        if not m:
            continue
        aid = m.group(1)
        cats = [c.get("term") for c in e.findall("a:category", NS)]
        prim = e.find("x:primary_category", NS)
        out.append(dict(source_id=aid, version=m.group(2), title=" ".join((e.findtext("a:title", "", NS)).split()),
                        summary=" ".join((e.findtext("a:summary", "", NS)).split()),
                        authors=[a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)],
                        categories=cats, primary_cat=prim.get("term") if prim is not None else None,
                        published_at=e.findtext("a:published", None, NS), updated_at=e.findtext("a:updated", None, NS),
                        url="https://arxiv.org/abs/" + aid,
                        comment=e.findtext("x:comment", None, NS), doi=e.findtext("x:doi", None, NS),
                        journal_ref=e.findtext("x:journal_ref", None, NS)))
    return int(total or 0), out


def upsert(cur, items, tag, run_id, source="arxiv"):
    from psycopg2.extras import execute_values
    if not items:
        return 0
    rows = [(source, it["source_id"], it["title"], it["summary"], it["authors"], it["categories"], it["primary_cat"],
             it["published_at"], it["updated_at"], it["url"], [tag], json.dumps({}), run_id,
             json.dumps({k: it.get(k) for k in ("version", "comment", "doi", "journal_ref")})) for it in items]
    execute_values(cur, """
        insert into pan.frontier_item (source, source_id, title, summary, authors, categories, primary_cat,
            published_at, updated_at, url, query_tags, signals, run_id, raw) values %s
        on conflict (source, source_id) do update set title=excluded.title, summary=excluded.summary,
            authors=excluded.authors, categories=excluded.categories, primary_cat=excluded.primary_cat,
            updated_at=excluded.updated_at, raw=excluded.raw, last_seen_at=now(),
            query_tags=(select array_agg(distinct t) from unnest(pan.frontier_item.query_tags || excluded.query_tags) t)""",
                   rows, page_size=500)
    return len(rows)


def run(max_results=200, include_authors=True, include_ids=True, out=print):
    from .. import db
    sd = seeds()
    lim = sd["limits"]["arxiv"]
    run_id = new_run("frontier-arxiv", dict(max_results=max_results, authors=include_authors, ids=include_ids))
    cl = Client("arxiv", run_id, lim["min_interval_s"])
    counts = dict(queries={}, ids=0, failed=[])
    queries = dict(sd["arxiv_queries"])
    if include_authors:
        queries.update(sd["arxiv_author_queries"])
    with db.cursor() as cur:
        for tag, q in queries.items():
            r = cl.get(API, params=dict(search_query=q, start=0, max_results=max_results, sortBy="submittedDate",
                                        sortOrder="descending"))
            if r is None:
                counts["failed"].append(tag)
                out("  {} FAILED".format(tag))
                continue
            total, items = parse(r.content)
            n = upsert(cur, items, tag, run_id)
            cl.log[-1] = cl.log[-1][:5] + (n,) + cl.log[-1][6:]
            counts["queries"][tag] = dict(total=total, fetched=n)
            out("  {:<26} total {:>6}  fetched {:>4}".format(tag, total, n))
        if include_ids:
            ids = sd["key_arxiv_ids"]
            for i in range(0, len(ids), 50):
                part = ids[i:i + 50]
                r = cl.get(API, params=dict(id_list=",".join(part), max_results=len(part)))
                if r is None:
                    counts["failed"].append("ids[{}]".format(i))
                    continue
                _, items = parse(r.content)
                counts["ids"] += upsert(cur, items, "KEY_ID_REPORT", run_id)
            out("  key ids: {} of {} resolved".format(counts["ids"], len(ids)))
        cl.flush(cur)
        cur.execute("select count(*) from pan.frontier_item where source='arxiv'")
        counts["arxiv_items_total"] = cur.fetchone()[0]
    finish_run(run_id, counts, "OK" if not counts["failed"] else "PARTIAL")
    out(json.dumps({k: counts[k] for k in ("ids", "failed", "arxiv_items_total")}))
    return counts
