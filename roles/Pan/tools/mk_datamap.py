"""Datasets behind the Prometheus Data Map dashboard (https://claude.ai/artifact/WygNq5aG2tp4xFiDJxYZCE):
JSON files built from the live catalog, the newest inventory run and the committed control results.

Usage (Pan venv, EW_DB_HOST set):  python roles/Pan/tools/mk_datamap.py OUT_DIR [--only architecture|review|fleet]
then upload each OUT_DIR/*.json as a dashboard asset and point its dataset at the new url.
"""
import collections
import json
import os
import sys

W = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, W)
os.environ.setdefault("EW_DB_HOST", "192.168.1.202")

import pyarrow.parquet as pq  # noqa: E402
from pan import db, iceberg, lake  # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
OUT = next((a for a in ARGS if a != ONLY), os.path.join(W, "datamap_out"))
os.makedirs(OUT, exist_ok=True)
CTL = os.path.join(W, "roles", "Pan", "reports", "controls")


def dump(name, rows):
    with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=0)
    print(name, len(rows))


def main():
    inv = sorted((lake() / "inventory").glob("inv-*"))[-1]
    fs = pq.read_table(str(inv / "fs_files.parquet")).to_pylist()
    roots = collections.defaultdict(lambda: [0, 0, None])
    for r in fs:
        a = roots[r["root"]]
        a[0] += 1
        a[1] += r["size_bytes"]
        a[2] = max(a[2] or r["mtime"], r["mtime"])

    def label(root):
        if root.endswith("(untracked)"):
            return "Untracked files in the M2 checkout", "cold"
        if root.endswith("Prometheus_data_backup"):
            return "Backup root on M2", "cold"
        if root.startswith("C:"):
            return "Campaign evidence on M2 (NVMe)", "warm"
        return "Engine data on M2 (HDD)", "warm"

    stores = [dict(store=label(k)[0], gb=round(v[1] / 1e9, 2), objects=v[0], newest=str(v[2])[:10],
                   **{"class": label(k)[1]}) for k, v in roots.items()]
    with db.cursor() as cur:
        cur.execute("select sum(size_bytes), count(*) from pan.artifact where source='git'")
        b, n = cur.fetchone()
        stores.append({"store": "Repository at origin/main", "gb": round(float(b) / 1e9, 2), "objects": n,
                       "newest": None, "class": "hot"})
        for dbn, cls, nm in (("prometheus_fire", "hot", "Program database (M1)"),
                             ("prometheus_sci", "hot", "Science database (M1)"),
                             ("lmfdb", "reference", "LMFDB reference database (M1)")):
            cur.execute("select coalesce(sum(total_bytes),0), count(*) from pan.pg_relation where dbname=%s", (dbn,))
            b, n = cur.fetchone()
            stores.append({"store": nm, "gb": round(float(b) / 1e9, 2), "objects": n, "newest": None, "class": cls})
    dump("stores", sorted(stores, key=lambda s: -s["gb"]))

    month = collections.Counter()
    for r in fs:
        if r["root"].endswith("(untracked)") or r["root"].endswith("backup"):
            month[r["mtime"].strftime("%Y-%m")] += r["size_bytes"]
    dump("untracked_by_month", [dict(month=k, gb=round(v / 1e9, 2)) for k, v in sorted(month.items()) if k >= "2026-01"])

    ext = collections.defaultdict(lambda: [0, 0])
    for r in fs:
        if r["root"].endswith("(untracked)"):
            a = ext[r["ext"] or "(none)"]
            a[0] += 1
            a[1] += r["size_bytes"]
    dump("untracked_by_type", [dict(type=k, gb=round(v[1] / 1e9, 2), files=v[0])
                               for k, v in sorted(ext.items(), key=lambda kv: -kv[1][1])[:8]])

    tables = []
    with db.cursor() as cur:
        cur.execute("""select c.relname, c.reltuples::bigint, pg_total_relation_size(c.oid) from pg_class c
                       join pg_namespace n on n.oid=c.relnamespace where n.nspname='pan' and c.relkind='r'
                       and c.relname not in ('migration','run','intake_call') order by 3 desc limit 12""")
        for nm, est, b in cur.fetchall():
            tables.append(dict(table="pan." + nm, layer="Postgres (M1)", rows=int(est), mb=round(float(b) / 1e6, 1)))
    for t in iceberg.tables():
        tables.append(dict(table=t["table"], layer="Iceberg (lake on M2)", rows=int(t["records"]), mb=None))
    dump("pan_tables", tables)

    def hybrid(f, k="all"):
        with open(os.path.join(CTL, f), encoding="utf-8") as fh:
            return round(json.load(fh)["summary"]["hybrid"][k][0], 3)
    ret = [dict(run="v0", set="Dev (Pan-written)", n=22, r10=hybrid("CONTROLS_20261009T1117Z.json"),
                r1=hybrid("CONTROLS_20261009T1117Z.json", "r1")),
           dict(run="v1", set="Held-out H1 (Pan-written)", n=20,
                r10=hybrid("CONTROLS_20261009T1141Z_v1-HELDOUT-VERDICT.json"),
                r1=hybrid("CONTROLS_20261009T1141Z_v1-HELDOUT-VERDICT.json", "r1")),
           dict(run="v2", set="Held-out H2 (Pan-written)", n=20,
                r10=hybrid("CONTROLS_20261009T1227Z_VERDICT-H2-v2b-doc-m3.json"),
                r1=hybrid("CONTROLS_20261009T1227Z_VERDICT-H2-v2b-doc-m3.json", "r1"))]
    with open(os.path.join(CTL, "V21_SUMMARY.json"), encoding="utf-8") as fh:
        s = json.load(fh)["v21CB200"]
    ret += [dict(run="v1", set="CB-200 (other seats)", n=200, r10=s["v1"]["all"], r1=s["v1"]["r1"]),
            dict(run="v2", set="CB-200 (other seats)", n=200, r10=s["v2"]["all"], r1=s["v2"]["r1"])]
    dump("retrieval", ret)

    with db.cursor() as cur:
        cur.execute("""select replace(model,'ollama:',''), sum(ok::int), count(*),
                              round(percentile_cont(0.5) within group (order by tok_per_s)::numeric, 1)
                       from pan.model_bench group by 1 order by 2 desc, 4 desc""")
        dump("models", [dict(model=r[0].split("@")[0], config=r[0].split("@")[1], passed=int(r[1]), probes=int(r[2]),
                             tok_s=float(r[3])) for r in cur.fetchall()])

    # measured values from roles/Pan/reports/COLD_DATA_CONVERSION_SAMPLE_2026-10-09.md
    dump("cold_conversion", [
        dict(family="formula_triage.jsonl", source_gb=0.36, form="typed (full file)", ratio=14.19, projected_gb=0.026),
        dict(family="hmf_hecke_eigenvalues.jsonl", source_gb=74.08, form="verbatim text", ratio=4.01, projected_gb=18.49),
        dict(family="formula_trees.jsonl", source_gb=36.89, form="verbatim text", ratio=15.54, projected_gb=2.37),
        dict(family="openwebmath_formulas.jsonl", source_gb=13.91, form="typed", ratio=10.34, projected_gb=1.35)])


def architecture():
    """Nodes and edges of Pan's data system for the dashboard diagram. The topology is fixed here (it is the
    design, roles/Pan/docs/DATA_ARCHITECTURE.md); every number in a label is read live."""
    import subprocess
    with db.cursor() as cur:
        def one(sql):
            cur.execute(sql)
            return cur.fetchone()[0]
        n = dict(blobs=one("select count(*) from pan.artifact where source='git'"),
                 commits=one("select count(*) from pan.commit"),
                 comms=one("select count(*) from pan.artifact where source='comms'"),
                 relations=one("select count(*) from pan.pg_relation"),
                 links=one("select count(*) from pan.link"),
                 chunks=one("select count(*) from pan.chunk"),
                 vectors=one("select count(*) from pan.embedding") + one("select count(*) from pan.doc_embedding"),
                 frontier=one("select count(*) from pan.frontier_item"),
                 bench=one("select count(*) from pan.code_bench") + one("select count(*) from pan.model_bench"),
                 pan_gb=float(one("""select coalesce(sum(pg_total_relation_size(c.oid)), 0) from pg_class c join
                                     pg_namespace n on n.oid = c.relnamespace where n.nspname = 'pan'
                                     and c.relkind in ('r', 'm')""")) / 1e9)
    inv = sorted((lake() / "inventory").glob("inv-*"))[-1]
    fs = pq.read_table(str(inv / "fs_files.parquet"), columns=["root", "size_bytes"]).to_pylist()
    n["untracked_gb"] = sum(r["size_bytes"] for r in fs if r["root"].endswith("(untracked)")) / 1e9
    n["fs_files"] = len(fs)
    tabs = iceberg.tables()
    n["ice_tables"] = len(tabs)
    n["result_rows"] = next((int(t["records"]) for t in tabs if t["table"] == "pan.result_rows"), 0)
    try:
        out = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=30).stdout
        n["ollama"] = max(0, len([ln for ln in out.splitlines() if ln.strip()]) - 1)
    except Exception:
        n["ollama"] = 0
    with open(os.path.join(W, "pan", "frontier", "seeds.json"), encoding="utf-8") as fh:
        sd = json.load(fh)
    n["feeds"], n["owners"] = len(sd["feeds"]), len(sd["github_owners"])

    def f(x):
        return "{:,}".format(x)
    L = ["Where data comes from", "What Pan runs (python -m pan ...)", "Where it lands", "How it is reached",
         "Who uses it"]
    nodes = [
        (0, "repo", "Git", "Git repository", "{} files at origin/main, {} commits".format(f(n["blobs"]), f(n["commits"]))),
        (0, "m2files", "M2", "Files on M2", "{} files inventoried; {:.0f} GB untracked in the checkout".format(
            f(n["fs_files"]), n["untracked_gb"])),
        (0, "dbs", "M1", "Program databases", "{} relations in prometheus_fire, prometheus_sci, lmfdb".format(
            f(n["relations"]))),
        (0, "comms", "M1", "Seat comms queue", "{} messages between seats".format(f(n["comms"]))),
        (0, "outside", "Outside", "Outside research",
         "arXiv, Hugging Face, {} lab and release feeds, {} GitHub owners".format(n["feeds"], n["owners"])),
        (0, "ollama", "M2", "Local models (Ollama)", "{} models served on M2 (one 16 GB GPU; larger ones spill to RAM)".format(n["ollama"])),
        (1, "refresh", "M2", "refresh", "catalog, commits, text chunks, vectors, links; changed files only"),
        (1, "inventory", "M2", "inventory", "every file and table: size, type, last touched"),
        (1, "consolidate", "M2", "consolidate", "result files to typed rows, checked by line and byte counts"),
        (1, "intake", "M2", "frontier intake", "daily, polite, every outside call logged"),
        (1, "bench", "M2", "benchmarks", "models scored by running tests, on public and on the program's own code"),
        (2, "pg", "M1", "Postgres schema pan",
         "{:.1f} GB: catalog, {} chunks, {} links, {} outside items, {} bench rows".format(
             n["pan_gb"], f(n["chunks"]), f(n["links"]), f(n["frontier"]), f(n["bench"]))),
        (2, "iceberg", "M2", "Iceberg + Parquet lake",
         "{} tables ({} result rows); catalog in Postgres, files on M2 NVMe".format(n["ice_tables"], f(n["result_rows"]))),
        (2, "vectors", "M2", "Vector caches", "{} vectors searched in memory (no pgvector on M1 yet)".format(
            f(n["vectors"]))),
        (3, "search", "M2", "pan search, pivot, refs", "ranked file pointers in seconds instead of scanning the repo"),
        (3, "frontierq", "M1", "Outside-work search + digest", "{} papers, posts and repos; daily digest".format(
            f(n["frontier"]))),
        (3, "reports", "Git", "Reports and this dashboard", "status reports, verdicts, review packets"),
        (4, "seats", "Git", "Every seat and the operator", "the pan-search skill; questions answered from the index"),
    ]
    edges = [("repo", "refresh"), ("comms", "refresh"), ("m2files", "inventory"), ("dbs", "inventory"),
             ("repo", "consolidate"), ("outside", "intake"), ("ollama", "bench"), ("repo", "bench"),
             ("refresh", "pg"), ("refresh", "vectors"), ("inventory", "pg"), ("inventory", "iceberg"),
             ("consolidate", "iceberg"), ("intake", "pg"), ("intake", "iceberg"), ("bench", "pg"),
             ("pg", "search"), ("vectors", "search"), ("pg", "frontierq"), ("pg", "reports"), ("iceberg", "reports"),
             ("search", "seats"), ("frontierq", "seats"), ("reports", "seats")]
    rows = [dict(kind="node", id=i, layer=layer, layer_name=L[layer], host=h, title=t, detail=d)
            for layer, i, h, t, d in nodes]
    ids = {r["id"] for r in rows}
    assert all(a in ids and b in ids for a, b in edges)
    rows += [dict(kind="edge", source=a, target=b) for a, b in edges]
    dump("architecture", rows)


def review():
    """PAN-37 review queue for the dashboard: the top of pan.review_unit and smell prevalence. Signals, never
    verdicts; nothing is dispatched (QUESTIONS.md Q-011)."""
    kinds = {"abs_path": "Hard-coded path", "lan_ip": "Hard-coded LAN address", "bare_except": "Bare except",
             "except_pass": "except Exception: pass", "shell_true": "shell=True", "eval_exec": "eval / exec",
             "long_function": "Function over 150 lines", "syntax_error": "Does not parse"}
    with db.cursor() as cur:
        cur.execute("""select path, coalesce(seat, ''), commits_7d, commits_30d, tested_by, smells, score, repo_sha
                       from pan.review_unit where score > 0 order by score desc, commits_7d desc, path limit 20""")
        rows = cur.fetchall()
        dump("review_queue", [dict(path=p, seat=s, commits_7d=a7, commits_30d=a30, tested_by=tb,
                                   smells=", ".join(kinds.get(k, k) for k in sorted(sm)), score=sc, repo_sha=sha[:9])
                              for p, s, a7, a30, tb, sm, sc, sha in rows])
        cur.execute("""select k, count(*), count(*) filter (where commits_30d > 0) from pan.review_unit,
                       jsonb_object_keys(smells) k group by 1 order by 2 desc""")
        dump("review_smells", [dict(kind=kinds.get(k, k), modules=int(n), changed_30d=int(c))
                               for k, n, c in cur.fetchall()])


def fleet_tabs():
    """PAN-38 Machines and Pantheon tabs: the register merged with probes (pan.fleet.machines) and seat activity
    (pan.fleet.seats). Run `python -m pan fleet probe` first for fresh measurements."""
    import subprocess
    from pan import fleet
    ms = fleet.machines()
    names = {m["host"]: m["name"] for m in ms}
    keep = ("name", "host", "label", "family", "status", "last_seen", "seen_by", "os", "hardware", "model_measured",
            "cpu", "cores", "threads", "ram_gb", "gpu", "vram_gb", "cuda", "disk", "disk_total_gb", "free_gb",
            "free_where", "ip", "tags", "seats_7d", "n_seats_7d", "fabric_workers", "specs", "checked_at", "mismatch",
            "notes")
    dump("machines", [{k: m.get(k) for k in keep} for m in ms])
    rows, meta = fleet.seats()
    for r in rows:
        r["last_machine"] = names.get(r["last_machine"], r["last_machine"])
    dump("seats", rows)
    with db.cursor() as cur:
        cur.execute("""select count(*) from comms.agents where status = 'active'
                       and coalesce(last_active_at, 'epoch') < now() - interval '24 hours'""")
        meta["comms_active_but_idle_24h"] = cur.fetchone()[0]
        cur.execute("select max(probed_at) from pan.host_probe where ok")
        t = cur.fetchone()[0]
        meta["last_probe_at"] = fleet._iso(t)
    meta["register_changed"] = subprocess.run(
        ["git", "-C", W, "log", "-1", "--format=%cs", "HEAD", "--", fleet.DOC], capture_output=True, text=True).stdout.strip()
    meta["machines_unprobed_no_hostkey"] = ", ".join(
        m["host"].lower() for m in ms if m["family"] == "Linux" and m["specs"] == "register only")
    dump("fleet_meta", [meta])


if __name__ == "__main__":
    if ONLY == "architecture":
        architecture()
    elif ONLY == "review":
        review()
    elif ONLY == "fleet":
        fleet_tabs()
    else:
        main()
        architecture()
        review()
        fleet_tabs()
