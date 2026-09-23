"""The canonical end-to-end check. Run after every development round:

    python -m prometheus.cosmos.runtest            (fast suite + selftest + seal + quick campaign)
    python -m prometheus.cosmos.runtest --full     (adds the slow planted-truth suite)

Writes <COSMOS_HOME>/runtest/<utc>/RUNTEST.json and RUNTEST.txt; exit 0 only if every step passed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from prometheus.cosmos import broker
from prometheus.cosmos.hashing import code_identity, cosmos_home, file_sha

REPO = Path(__file__).resolve().parents[2]
COMMITMENT = "48e709653f2bbda12c6b1d1c499d801339ec7897e9bf3081764c50691cfa8265"


def _pytest(marker: str) -> dict:
    t = time.time()
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "prometheus/cosmos/tests", "-m", marker],
                       cwd=str(REPO), capture_output=True, text=True, timeout=3600)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]
    return {"ok": r.returncode == 0, "summary": tail, "s": round(time.time() - t, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args(argv)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = cosmos_home() / "runtest" / stamp
    out.mkdir(parents=True, exist_ok=True)
    rec = {"utc": stamp, "identity": code_identity(), "steps": {}}
    rec["steps"]["tests_fast"] = _pytest("not slow")
    if a.full:
        rec["steps"]["tests_slow_planted"] = _pytest("slow")
    try:
        st = broker.selftest()
        rec["steps"]["broker_selftest"] = {"ok": all(all(v.values()) for v in st.values()), "detail": st}
    except Exception as e:
        rec["steps"]["broker_selftest"] = {"ok": False, "error": repr(e)}
    try:
        broker.load_spec(COMMITMENT)
        rec["steps"]["seal"] = {"ok": True, "spec_sha": file_sha(broker.SPEC)}
    except Exception as e:
        rec["steps"]["seal"] = {"ok": False, "error": repr(e)}
    t = time.time()
    try:
        from prometheus.cosmos.campaign0 import run
        rep = run(out / "quick_campaign", quick=True)
        g = {k: v["verdict"] for k, v in rep["gates"].items()}
        ok = rep["receipt_chain_ok"] and g["G0"] == "PASS" and g["G1"] == "PASS"
        rec["steps"]["quick_campaign"] = {"ok": ok, "gates": g, "graph": rep["graph"], "laws": rep["laws"],
                                          "mine_initial": rep["mine_initial"], "s": round(time.time() - t, 1)}
    except Exception as e:
        import traceback
        rec["steps"]["quick_campaign"] = {"ok": False, "error": traceback.format_exc()[-1500:]}
    rec["ok"] = all(v.get("ok") for v in rec["steps"].values())
    (out / "RUNTEST.json").write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    lines = ["COSMOS RUNTEST %s  %s" % (stamp, "PASS" if rec["ok"] else "FAIL"),
             "head %s dirty %s src %s" % (rec["identity"].get("git_head", "?")[:10], rec["identity"].get("cosmos_dirty"),
                                         rec["identity"]["cosmos_src_sha"][:12])]
    for k, v in rec["steps"].items():
        extra = v.get("summary") or (json.dumps(v.get("gates")) if "gates" in v else "") or v.get("error", "")[:200]
        lines.append("  %-20s %s  %s" % (k, "ok  " if v.get("ok") else "FAIL", extra))
    lines.append("receipt: " + str(out / "RUNTEST.json"))
    txt = "\n".join(lines)
    (out / "RUNTEST.txt").write_text(txt + "\n", encoding="utf-8")
    print(txt)
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
