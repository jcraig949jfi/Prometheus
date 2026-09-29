"""Build the C1b summary from the run rows. Applies each specimen's A2.2/A3
NOT_ELIGIBLE list to its fresh-seed rows (same physics; the driver keyed the
lookup by '<cell>:fresh<k>' and missed it -- disclosed reporting defect)."""
import gzip
import hashlib
import json
import pathlib
import shutil
import sys

sys.path.insert(0, ".")
from prometheus.ananke import c1b_run  # noqa: E402

HOME = pathlib.Path("C:/Users/jcrai/ananke_runs/pte-c1b")
OUT = pathlib.Path("roles/Ananke/pte/c1b")
rows = [json.loads(l) for l in (HOME / "rows.jsonl").open()]
elig = json.loads((OUT / "ELIGIBILITY_dev.json").read_text())["specimens"]
raw = (HOME / "rows.jsonl").read_bytes()

rd = OUT / "c1b_rows"
rd.mkdir(exist_ok=True)
with gzip.open(rd / "rows.jsonl.gz", "wb") as f:
    f.write(raw)
shutil.copy(HOME / "DONE.json", rd / "DONE.json")
shutil.copy(HOME.parent / "pte-c1b-launch.log", rd / "launch.log")


def acc(r, k):
    a = r["arms"].get(k)
    return None if a is None else [round(x, 4) for x in a["acc"]]


S1 = [r for r in rows if r["stage"] == "S1"]
S2 = [r for r in rows if r["stage"] == "S2"]
S3 = [r for r in rows if r["stage"] == "S3"]
summ = {"raw_rows_sha256": hashlib.sha256(raw).hexdigest(), "n_rows": len(rows),
        "status": {s: sorted({r["status"] for r in rows if r["stage"] == s}) for s in ("S1", "S2", "S3")},
        "receipt_code": rows[0]["receipt"]["code"], "release": rows[0]["receipt"]["release_msg"],
        "wall_s": json.loads((HOME / "DONE.json").read_text())["wall_s"],
        "specimens": {}, "fresh": [], "recheck": []}
for r in S1:
    b = {k: v for k, v in r["booleans"].items() if not k.startswith("_")}
    e = {"mechanism": r["mechanism"], "label": r["label"], "booleans": b,
         "not_eligible": r["not_eligible"],
         "arms": {k: acc(r, k) for k in r["arms"]}, "carryover": r["carryover"]}
    if r["mechanism"] == "M3":
        e["T_positive_components"] = r["booleans"]["_positive_components"]
        e["routing"] = r["booleans"]["_routing"]
        e["rule_predicts"] = {k: r["rule_predicts"][k] for k in ("acc", "lo99", "perm_p", "map")}
        e["wording"] = r.get("wording")
    else:
        e["census"] = {k: r["census"][k] for k in ("acc", "lo99", "perm_p")}
    summ["specimens"][r["cell"]] = e
for r in S2:
    cid = r["replicates"]
    ne = elig[cid]["NOT_ELIGIBLE"]
    f = {"mechanism": r["mechanism"], "replicates": cid, "k": r["k"], "held": r["held"],
         "signal": r["signal"], "label_as_run": r.get("label")}
    if r.get("label"):
        b = r["booleans"]
        if r["mechanism"] == "M2":
            f["label_corrected"] = c1b_run.label_m2(b, ne)
        else:
            core = {k: b[k] for k in ("T", "X", "R", "M")}
            f["label_corrected"] = c1b_run.label_m3(core, ne, True)
            f["T_positive_components"] = b["_positive_components"]
        f["booleans"] = {k: v for k, v in b.items() if not k.startswith("_")}
        f["arms"] = {k: acc(r, k) for k in r["arms"]}
    summ["fresh"].append(f)
for r in S3:
    summ["recheck"].append({"cell": r["cell"], "family": r["family"],
                            "frozen_routing_C1": r["frozen_routing_C1"],
                            "C1_packet_ablation": (r.get("c1_packet_ablation") or {}).get("acc"),
                            "arms": {k: acc(r, k) for k in r["arms"]}})
(OUT / "C1B_SUMMARY.json").write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n")
for f in summ["fresh"]:
    print(f["mechanism"], f["replicates"][:8], f["k"], round(f["held"]["acc"], 3), f["signal"],
          f["label_as_run"], "->", f.get("label_corrected"))
print(summ["raw_rows_sha256"][:16], summ["n_rows"], summ["status"])
