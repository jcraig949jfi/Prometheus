"""PROBE-01 run: the lincode family through the H5 exact reference, raw and collapsed.

Preregistration: roles/Polyhymnia/science/PROBE_01_PREREGISTRATION.md
(commit e6f0b64fb, before this file existed). Writes
roles/Polyhymnia/ledgers/probe_01_lincode_2026-09-11.json (every per-genome
reach/neutral vector, digests, the P/M table) and .md (the readout).

Usage:  python roles/Polyhymnia/science/probe_01_run.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import lincode_decoders as L                     # noqa: E402
from archaeon.producer import h5_decoders as H    # noqa: E402
from archaeon.producer import h5_reference as R   # noqa: E402

OUT_JSON = HERE.parent / "ledgers" / "probe_01_lincode_2026-09-11.json"
OUT_MD = HERE.parent / "ledgers" / "probe_01_lincode_2026-09-11.md"


def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=str(REPO), timeout=60).decode().strip()
    except Exception as e:  # pragma: no cover
        return "UNAVAILABLE: {}".format(e)


def summarize(ex, name):
    return {"decoder_id": ex["decoder_id"], "member": name, "edges": ex["edges"], "collapsed": ex["collapsed"],
            "mean_reach": ex["mean_reach"], "min_reach": ex["min_reach"], "max_reach": ex["max_reach"],
            "mean_neutral": ex["mean_neutral"],
            "reach_histogram": {str(k): v for k, v in ex["reach_histogram"].items()},
            "neutral_histogram": {str(k): v for k, v in sorted(Counter(ex["_neutral"]).items())},
            "reference_digest": ex["reference_digest"]}


def main() -> int:
    cm = R.load_class_map(REPO)
    eq = cm["equivalence"]
    members = [("direct", H.direct), ("A0_member", L.make_direct_member()), ("hamming", L.make_hamming()),
               ("random1", L.make_random(1)), ("random2", L.make_random(2)),
               ("scrambled_hamming_3", H.make_scrambled(L.make_hamming(), 3)),
               ("balanced_7", H.make_balanced(7))]
    gate = {}
    raw = {}
    col = {}
    vectors = {}
    for name, dec in members:
        gate[name] = H.check_exact(dec)
        exr = R.exact_reference(dec)
        exc = R.exact_reference(dec, equivalence=eq)
        raw[name] = summarize(exr, name)
        col[name] = summarize(exc, name)
        vectors[name] = {"reach_rules": exr["_reach"], "neutral": exr["_neutral"], "reach_classes": exc["_reach"]}
    try:
        H.check_exact(L.cheat_nonuniform)
        refusal = "FAIL: the cheat was admitted"
    except ValueError as e:
        refusal = "PASS: refused ({})".format(str(e)[:60])

    ham = raw["hamming"]
    hamc = col["hamming"]
    d = raw["direct"]
    zeros = sum(1 for g in range(4096) if vectors["hamming"]["reach_rules"][g] == 0 and vectors["hamming"]["neutral"][g] == 12)
    table = [
        ("P1 analytic", "hamming: exactly 256 genomes at reach 0 / neutral 12 (planted; cheat control)", zeros == 256, "count = {}".format(zeros)),
        ("P2 analytic", "hamming: max reach <= 11, min reach 0", ham["max_reach"] <= 11 and ham["min_reach"] == 0, "max {} min {}".format(ham["max_reach"], ham["min_reach"])),
        ("P3 analytic (corrected s7)", "hamming preimage: one component of 16, center degree 12; direct: 4-cube", all(L.preimage_components(L.make_hamming(), r) == [16] for r in range(256)), "components [16] for all 256 rules (degree structure in tests)"),
        ("P4 analytic", "scrambled(hamming) histogram and mean_neutral identical to hamming", raw["scrambled_hamming_3"]["reach_histogram"] == ham["reach_histogram"] and raw["scrambled_hamming_3"]["mean_neutral"] == ham["mean_neutral"], "identical" if raw["scrambled_hamming_3"]["reach_histogram"] == ham["reach_histogram"] else "DIFFER"),
        ("P5 analytic", "A=0 member equals h5.direct.v0 entry for entry", gate["A0_member"]["table_sha256"] == gate["direct"]["table_sha256"], "table_sha256 equal"),
        ("positive control", "direct: {8: 4096}, neutral 4.0", d["reach_histogram"] == {"8": 4096} and d["mean_neutral"] == 4.0, json.dumps(d["reach_histogram"])),
        ("gate refusal", "rule = g mod 255 refused by check_exact", refusal.startswith("PASS"), refusal),
        ("spread", "random1 != random2 on histogram or mean_neutral", (raw["random1"]["reach_histogram"], raw["random1"]["mean_neutral"]) != (raw["random2"]["reach_histogram"], raw["random2"]["mean_neutral"]), "random1 mean_neutral {} / random2 {}".format(raw["random1"]["mean_neutral"], raw["random2"]["mean_neutral"])),
        ("M1 measured", "hamming mean neutral (expected BELOW 4.0)", None, "{:.4f}; min {} max {}; histogram {}".format(ham["mean_neutral"], min(vectors["hamming"]["neutral"]), max(vectors["hamming"]["neutral"]), json.dumps(ham["neutral_histogram"]))),
        ("M2 measured", "hamming mean reach, rules (expected ABOVE 8.0)", None, "{:.4f}; histogram {}".format(ham["mean_reach"], json.dumps(ham["reach_histogram"]))),
        ("M3 measured", "hamming mean reach, 224 classes (expected below M2; vs direct not predicted)", None, "{:.4f} vs direct {:.4f}".format(hamc["mean_reach"], col["direct"]["mean_reach"])),
        ("M4 guess", "random1 / random2 mean neutral and mean reach (rules)", None, "random1 {:.4f}/{:.4f}; random2 {:.4f}/{:.4f} (min_distance {} / {})".format(raw["random1"]["mean_neutral"], raw["random1"]["mean_reach"], raw["random2"]["mean_neutral"], raw["random2"]["mean_reach"], L.make_random(1).min_distance, L.make_random(2).min_distance)),
        ("M5 measured", "class-collapsed mean reach: hamming vs balanced_7 (no prediction)", None, "hamming {:.4f} vs balanced_7 {:.4f}".format(hamc["mean_reach"], col["balanced_7"]["mean_reach"])),
    ]
    out = {
        "schema": "polyhymnia.probe_01.v0",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "preregistration": "roles/Polyhymnia/science/PROBE_01_PREREGISTRATION.md",
        "preregistration_commit": "e6f0b64fb",
        "workspace": {"head": git("rev-parse", "--short", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                      "dirty_tracked": bool(git("status", "--porcelain", "--untracked-files=no"))},
        "class_map": {"path": R.CLASS_MAP_PATH, "n_classes": cm["n_classes"], "scope": cm["scope"], "fixture_digest": cm["fixture_digest"]},
        "consumer": {"gate": "archaeon.producer.h5_decoders.check_exact", "observable": "archaeon.producer.h5_reference.exact_reference",
                     "live_slot": "archaeon.producer.campaign_h5.h5_readout (hardcoded dict)"},
        "family": {"id": "h5.lincode.v0", "hamming_rows": list(L.HAMMING_ROWS), "hamming_leaders": list(L.make_hamming().coset_leaders),
                   "random1_rows": list(L.random_rows(1)), "random2_rows": list(L.random_rows(2))},
        "gate": gate, "raw": raw, "collapsed": col,
        "table": [{"row": r, "claim": c, "result": ("PASS" if ok else "FAIL") if ok is not None else "MEASURED", "detail": det} for r, c, ok, det in table],
        "limits": "access structure at the fixture scope on the published 224-class map; no usefulness claim; the live H5-1 map is partial (232/256) and not used",
        "vectors": vectors,
    }
    OUT_JSON.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    md = ["# PROBE-01 readout: lincode decoder family through the H5 exact reference (2026-09-11)", "",
          "Preregistered at e6f0b64fb before this run. Rows: probe_01_lincode_2026-09-11.json (per-genome vectors).",
          "Class map: {} ({} classes, {})".format(R.CLASS_MAP_PATH, cm["n_classes"], cm["fixture_digest"][:23]), "",
          "member               d  mean_reach  min  max  mean_neutral  mean_reach_classes  table_sha256",
          "-------------------  -  ----------  ---  ---  ------------  ------------------  ------------"]
    dist = {"direct": 1, "A0_member": 1, "hamming": 3, "random1": L.make_random(1).min_distance, "random2": L.make_random(2).min_distance,
            "scrambled_hamming_3": "-", "balanced_7": "-"}
    for name, _ in members:
        md.append("{:19s}  {:>1}  {:10.4f}  {:3d}  {:3d}  {:12.4f}  {:18.4f}  {}".format(
            name, dist[name], raw[name]["mean_reach"], raw[name]["min_reach"], raw[name]["max_reach"],
            raw[name]["mean_neutral"], col[name]["mean_reach"], gate[name]["table_sha256"][:12]))
    md += ["", "reach histograms (rules):"]
    for name, _ in members:
        md.append("  {:19s} {}".format(name, json.dumps(raw[name]["reach_histogram"])))
    md += ["", "neutral histograms:"]
    for name, _ in members:
        md.append("  {:19s} {}".format(name, json.dumps(raw[name]["neutral_histogram"])))
    md += ["", "prediction / control table:", ""]
    for r in out["table"]:
        md.append("  {:26s} {:8s} {}".format(r["row"], r["result"], r["claim"]))
        md.append("  {:26s} {:8s} -> {}".format("", "", r["detail"]))
    md += ["", "limits: " + out["limits"], ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
