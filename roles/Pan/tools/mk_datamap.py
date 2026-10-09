"""Datasets behind the Prometheus Data Map dashboard (https://claude.ai/artifact/WygNq5aG2tp4xFiDJxYZCE):
seven JSON files built from the live catalog, the newest inventory run and the committed control results.

Usage (Pan venv, EW_DB_HOST set):  python roles/Pan/tools/mk_datamap.py OUT_DIR
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

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(W, "datamap_out")
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


if __name__ == "__main__":
    main()
