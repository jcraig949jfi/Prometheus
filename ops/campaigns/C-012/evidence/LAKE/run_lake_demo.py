"""C-012-T005 bounded demonstration: materialize the qualification evidence (schema moonshot_qual, run Q20261010A)
into Pan's lake through Pan's own functions, namespace "moonshot", tables prefixed qual_ (contract s6; Pan #2004).

Order (so the crash-replay check means something on a fresh lake):
  1. crash run   -- a separate process materializes and dies before the qual_trace_lines commit (qual_epochs
                    committed, nothing after it);
  2. normal run  -- a fresh process resumes from each table's own watermark; oracle must be OK everywhere;
  3. repeat run  -- appends nothing; oracle OK.
Then: the lake's table listing (pan.iceberg.tables), the catalogue view, and Moonshot's logged reports.
Run with Moonshot's lake venv on M2:
    EW_DB_HOST=192.168.1.202 C:/Prometheus-data/moonshot/venv/Scripts/python.exe run_lake_demo.py --out DIR
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
SCHEMA, NAMESPACE, PREFIX = "moonshot_qual", "moonshot", "qual_"

CHILD = """
import json, sys
sys.path.insert(0, {repo!r})
from moonshot.nf import materialize as Mz
crash = sys.argv[1] or None
try:
    rep = Mz.materialize({schema!r}, namespace={ns!r}, prefix={prefix!r}, settle_s=60, _crash_before=crash)
    print(json.dumps({{"ok": True, "report": rep}}, default=str))
except Mz.InjectedCrash as e:
    print(json.dumps({{"ok": False, "crashed": str(e)}}))
    sys.exit(3)
"""


def child(crash=""):
    code = CHILD.format(repo=str(REPO), schema=SCHEMA, ns=NAMESPACE, prefix=PREFIX)
    r = subprocess.run([sys.executable, "-c", code, crash], cwd=str(REPO), capture_output=True, text=True,
                       timeout=600, env=dict(os.environ))
    out = r.stdout.strip().splitlines()
    return {"exit_code": r.returncode, "result": json.loads(out[-1]) if out else None, "stderr_tail": r.stderr[-1500:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(REPO))
    from moonshot.nf import pg
    admin = pg.connect()
    pg.init_schema(admin, SCHEMA)                 # additive and idempotent: catalog_v + record_materialization
    admin.close()
    rec = {"schema": SCHEMA, "namespace": NAMESPACE, "prefix": PREFIX, "interpreter": sys.executable,
           "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "steps": {}}
    rec["steps"]["1_crash_run"] = child("trace_lines")
    from pan import iceberg
    rec["after_crash_tables"] = iceberg.tables(namespace=NAMESPACE)
    rec["steps"]["2_normal_run"] = child()
    rec["steps"]["3_repeat_run"] = child()
    rec["lake_tables"] = iceberg.tables(namespace=NAMESPACE)
    reader = pg.Moonshot(pg.connect(), SCHEMA, "reader", "Themis")
    rec["catalog_v"] = [list(map(str, r)) for r in
                        reader.select("SELECT object_sha256, kind, title, summary, published_at, ref FROM {s}.catalog_v "
                                      "ORDER BY ref")]
    rec["logged_reports"] = reader.materializations()
    reader.close()
    rec["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (out / "LAKE_DEMO.json").write_text(json.dumps(rec, indent=1, default=str, sort_keys=True) + "\n",
                                        encoding="utf-8", newline="\n")
    s = rec["steps"]
    print("crash run:", s["1_crash_run"]["exit_code"], s["1_crash_run"]["result"])
    print("tables after crash:", [(t["table"], t["records"]) for t in rec["after_crash_tables"]])
    for k in ("2_normal_run", "3_repeat_run"):
        rep = (s[k]["result"] or {}).get("report") or {}
        print(k, s[k]["exit_code"], {t: (v["appended"], v["lake"], v["postgres"], v["oracle"])
                                     for t, v in (rep.get("tables") or {}).items()})
    print("lake tables:", [(t["table"], t["records"], t["snapshots"]) for t in rec["lake_tables"]])
    print("catalog_v rows:", len(rec["catalog_v"]), "| logged reports:", len(rec["logged_reports"]))


if __name__ == "__main__":
    main()
