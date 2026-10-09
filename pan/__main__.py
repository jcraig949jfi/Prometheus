"""python -m pan <command> ...   (roles/Pan/RESPONSIBILITIES.md)

  migrate                     apply pan/migrations to the canonical cluster
  inventory [--sha REF]       PAN-01: inventory every store -> lake + schema pan
  commits [--sha REF]         PAN-06: index git history
  chunk [--limit N]           PAN-04: extract + chunk text artifacts at the catalog SHA
  embed [--model M]           PAN-05: embed chunks (GPU), store vectors
  search QUERY [opts]         hybrid full-text + vector search
  similar PATH                artifacts most like PATH
  cochange PATH               files that change in the same commits as PATH
  tables QUERY                find tables/columns on the cluster by name
  stats                       row counts per table in schema pan
  comms-index                 PAN-20: comms message history -> searchable artifacts (read-only)
  refresh                     PAN-17: catalog to current origin/main + comms, changed items only
  status                      catalog SHA vs origin/main (freshness) and the last run of each kind
  consolidate [--ext .jsonl]  PAN-16: committed JSON Lines -> Iceberg pan.result_rows + typed Parquet
  frontier arxiv|hf-models|hf-daily     PAN-09..11 intake (rate-limited, logged)
  frontier search QUERY       full-text over intake items (arXiv + HF daily papers)
  frontier models QUERY [--fits]        Hugging Face models, optionally only 16 GB-fit
  frontier embed              PAN-14: paper vectors in the repository's document-vector space
  frontier like PATH          outside papers nearest to a repository file
"""
import argparse
import os
import sys


def main(argv=None):
    os.environ.setdefault("EW_DB_HOST", "192.168.1.202")
    ap = argparse.ArgumentParser(prog="python -m pan")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("migrate")
    p = sub.add_parser("inventory")
    p.add_argument("--sha", default="origin/main")
    p.add_argument("--no-db", action="store_true")
    p = sub.add_parser("commits")
    p.add_argument("--sha", default="origin/main")
    p = sub.add_parser("chunk")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--kinds", default="")
    p = sub.add_parser("embed")
    p.add_argument("--model", default=None)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--docs", action="store_true", help="document-level vectors (v2) instead of chunk vectors")
    p = sub.add_parser("search")
    p.add_argument("query", nargs="+")
    p.add_argument("-k", type=int, default=10)
    p.add_argument("--kind")
    p.add_argument("--seat")
    p.add_argument("--path")
    p.add_argument("--since")
    p.add_argument("--mode", choices=["hybrid", "fts", "vector"], default="hybrid")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("similar")
    p.add_argument("path")
    p.add_argument("-k", type=int, default=10)
    p = sub.add_parser("cochange")
    p.add_argument("path")
    p.add_argument("-k", type=int, default=15)
    p = sub.add_parser("tables")
    p.add_argument("query")
    sub.add_parser("stats")
    sub.add_parser("status")
    sub.add_parser("comms-index")
    sub.add_parser("refresh")
    p = sub.add_parser("consolidate")
    p.add_argument("--ext", default=".jsonl")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--no-typed", action="store_true")
    p = sub.add_parser("frontier")
    p.add_argument("what", choices=["arxiv", "hf-models", "hf-daily", "search", "models", "embed", "like"])
    p.add_argument("query", nargs="*")
    p.add_argument("--max-results", type=int, default=200)
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--no-authors", action="store_true")
    p.add_argument("-k", type=int, default=15)
    p.add_argument("--fits", action="store_true", help="models: only those estimated to fit 16 GB at Q4")
    a = ap.parse_args(argv)

    if a.cmd == "migrate":
        from . import db
        db.migrate()
    elif a.cmd == "inventory":
        from . import inventory
        inventory.run(a.sha, write_db=not a.no_db)
    elif a.cmd == "commits":
        from . import commits
        commits.run(a.sha)
    elif a.cmd == "chunk":
        from . import chunker
        chunker.run(limit=a.limit, kinds=[k for k in a.kinds.split(",") if k])
    elif a.cmd == "embed":
        from . import embed
        if a.docs:
            embed.run_docs(model=a.model or embed.DOC_MODEL, limit=a.limit, batch=a.batch)
        else:
            embed.run(model=a.model, limit=a.limit, batch=a.batch)
    elif a.cmd == "search":
        from . import search
        search.cli(" ".join(a.query), k=a.k, kind=a.kind, seat=a.seat, path=a.path, since=a.since, mode=a.mode,
                   as_json=a.json)
    elif a.cmd == "similar":
        from . import search
        search.similar_cli(a.path, k=a.k)
    elif a.cmd == "cochange":
        from . import search
        search.cochange_cli(a.path, k=a.k)
    elif a.cmd == "tables":
        from . import search
        search.tables_cli(a.query)
    elif a.cmd == "comms-index":
        from . import comms_index
        comms_index.run()
    elif a.cmd == "refresh":
        from . import comms_index, refresh
        refresh.run()
        comms_index.run()
    elif a.cmd == "status":
        import subprocess
        from . import REPO, db
        with db.cursor() as cur:
            cur.execute("""select distinct on (kind) kind, run_id, git_sha, finished_at, status, counts->>'seconds'
                           from pan.run where status in ('OK','PARTIAL') order by kind, started_at desc""")
            runs = cur.fetchall()
            cur.execute("select max(repo_sha) from pan.artifact where source='git'")
            cat = cur.fetchone()[0]
        head = subprocess.run(["git", "rev-parse", "origin/main"], cwd=REPO, capture_output=True, text=True).stdout.strip()
        behind = subprocess.run(["git", "rev-list", "--count", "{}..{}".format(cat, head)], cwd=REPO,
                                capture_output=True, text=True).stdout.strip() if cat and head else "?"
        print("catalog SHA {}  origin/main {}  commits not yet indexed: {}".format((cat or "?")[:9], head[:9], behind))
        for k, rid, sha, fin, st, secs in runs:
            print("  {:<20} {:<40} {} {} {}s".format(k, rid, str(fin)[:16], st, secs))
    elif a.cmd == "consolidate":
        from . import consolidate
        consolidate.run(ext=a.ext, limit=a.limit, typed=not a.no_typed)
    elif a.cmd == "frontier":
        from .frontier import arxiv, hf, query
        if a.what == "arxiv":
            arxiv.run(max_results=a.max_results, include_authors=not a.no_authors)
        elif a.what == "hf-models":
            hf.run_models()
        elif a.what == "hf-daily":
            hf.run_daily_papers(days=a.days)
        elif a.what == "search":
            query.search_cli(" ".join(a.query), k=a.k)
        elif a.what == "models":
            query.models_cli(" ".join(a.query), k=a.k, fits=a.fits)
        elif a.what == "embed":
            query.embed_items()
        elif a.what == "like":
            query.like_cli(" ".join(a.query), k=a.k)
    elif a.cmd == "stats":
        from . import db
        with db.cursor() as cur:
            cur.execute("""select c.relname, c.reltuples::bigint, pg_size_pretty(pg_total_relation_size(c.oid))
                           from pg_class c join pg_namespace n on n.oid=c.relnamespace
                           where n.nspname='pan' and c.relkind='r' order by pg_total_relation_size(c.oid) desc""")
            for r in cur.fetchall():
                print("{:<16} {:>12} {:>10}".format(*r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
