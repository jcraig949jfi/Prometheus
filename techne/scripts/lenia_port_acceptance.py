"""Executor-domain acceptance for the numpy Lenia port (Harmonia STANDING_RULES A4; operator review
2026-09-18 item (b)): instantiate EVERY 2D lifeform in the pinned catalogue (specimen lenia-chan-2019,
Python/animals.json) on Lenia2D and step it once; exact accepted / refused counts with reasons.
No score, no aliveness judgement: only "does the executor accept this point of the domain".
Run: python techne/scripts/lenia_port_acceptance.py --out techne/acquisition/poet_alife/PORT_ACCEPTANCE_<date>.json
"""
from __future__ import annotations
import argparse, collections, hashlib, json, pathlib, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE.parent))
from techne.fossils import vault
import techne107_asal_observer as port


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--world", type=int, default=128); a = ap.parse_args()
    animals = vault.body_dir("lenia-chan-2019") / "upstream" / "tree" / "Python" / "animals.json"
    cat = json.load(open(animals, encoding="utf-8"))
    rows, reasons = [], collections.Counter()
    t0 = time.time()
    for e in cat:
        if not isinstance(e, dict) or "params" not in e or "cells" not in e:
            continue
        code = e.get("code", "?")
        p = dict(e["params"])
        row = {"code": code, "R": p.get("R"), "T": p.get("T"), "b": str(p.get("b")), "kn": p.get("kn", 1), "gn": p.get("gn", 1), "accepted": False, "reason": None}
        try:
            if any(ch in str(e["cells"]) for ch in "%#@"):   # 3D/4D delimiters: not a 2D lifeform
                raise ValueError("not_2d")
            pat = port.rle2arr_2d(e["cells"])
            if pat.shape[0] > a.world or pat.shape[1] > a.world:
                raise ValueError("pattern_larger_than_world_%d" % a.world)
            sim = port.Lenia2D(a.world, p)
            A = sim.step(sim.place(pat))
            if not np.isfinite(A).all():
                raise ValueError("non_finite_after_one_step")
            row["accepted"] = True
        except Exception as ex:                             # noqa: BLE001 -- every refusal is a row
            row["reason"] = ("%s: %s" % (type(ex).__name__, str(ex)))[:120]
            reasons[row["reason"].split(":")[0] + ":" + row["reason"].split(":")[1].strip()[:40] if ":" in row["reason"] else row["reason"]] += 1
        rows.append(row)
    acc = sum(r["accepted"] for r in rows)
    kn_gn = collections.Counter((r["kn"], r["gn"]) for r in rows if r["accepted"])
    out = {"schema": "techne.lenia_port.acceptance/1", "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "catalogue": {"specimen": "lenia-chan-2019", "file": "Python/animals.json", "sha256": hashlib.sha256(animals.read_bytes()).hexdigest(), "entries_with_params_and_cells": len(rows)},
           "port": {"script": "techne/scripts/techne107_asal_observer.py", "sha256_lf": hashlib.sha256(open(HERE.parent / "techne107_asal_observer.py", "rb").read().replace(b"\r\n", b"\n")).hexdigest(),
                    "supports": "kn 1-4, gn 1-3, fractional rings, world %d" % a.world},
           "accepted": acc, "refused": len(rows) - acc, "refusal_reasons": dict(reasons.most_common()),
           "accepted_by_kn_gn": {"%s/%s" % k: v for k, v in sorted(kn_gn.items())}, "seconds": round(time.time() - t0, 1), "rows": rows}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("accepted", acc, "refused", len(rows) - acc, "of", len(rows), "| reasons", dict(reasons.most_common(6)), "| %.1fs" % out["seconds"])


if __name__ == "__main__":
    main()
