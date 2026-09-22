"""Round-2 Step A: offline per-IC re-derivation of the founding fossils.

For every COMPLETED ca_density_v0 row with transform "none": regenerate
each repeat's initial conditions from (repeat seed, density block j ->
seed+j, n_ic, n_cells) exactly as vivarium/viv/ca_density.py does, re-run
herakles.evca.core.classify, and REQUIRE the recomputed at_T accuracy and
correct-mask digest to equal the fossil's (instrument check). Only then is
the per-IC table (rule, N, ensemble, nominal d, realised k, success)
trusted. CHEAT-A perturbs the seed and must break the match.

Output: roles/Theophrastus/crucible/round2/per_ic.jsonl (one row per IC)
and per_ic_validation.json (per-row match record).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from herakles.evca import core                     # noqa: E402
from theophrastus.ledger import Ledger             # noqa: E402

OUT = REPO / "roles" / "Theophrastus" / "crucible" / "round2"


def regenerate(payload: dict, seed: int) -> np.ndarray:
    dens = [None if d is None else float(d) for d in payload["ic_density_set"]]
    blocks = [core.make_ics(payload["n_ic"], payload["n_cells"], int(seed) + j, density=d)
              for j, d in enumerate(dens)]
    return np.concatenate(blocks, axis=0) if len(blocks) > 1 else blocks[0]


def per_ic_rows(row: dict, *, seed_offset: int = 0) -> tuple:
    """Return (per-IC records, validation record). seed_offset != 0 is the
    CHEAT-A path and must fail validation."""
    p = row["cell"]["coordinates"]
    payload = {"rule_hex": p["mechanism"]["rule_hex"], "n_cells": p["world"]["n_cells"],
               "steps": p["world"]["steps"], "n_ic": p["pressure"]["n_ic"],
               "ic_density_set": p["pressure"]["ic_density_set"]}
    table = core.decode_table(payload["rule_hex"])
    dens = payload["ic_density_set"]
    recs, val = [], {"row_id": row["row_id"], "labels": row["labels"], "repeats": [],
                     "all_match": True}
    for rep in row["work_result"]["repeats"]:
        seed = int(rep["seed"]) + seed_offset
        ics = regenerate(payload, seed)
        res = core.classify(table, ics, payload["steps"], witness_limit=0)
        fossil = rep["result"]
        match = (abs(res["accuracy"] - fossil["accuracy_at_T"]) < 1e-12
                 and res["correct_mask_digest"] == fossil["mask_digest_at_T"])
        val["repeats"].append({"repeat_index": rep["repeat_index"], "seed": seed,
                               "acc_recomputed": res["accuracy"],
                               "acc_fossil": fossil["accuracy_at_T"],
                               "digest_match": res["correct_mask_digest"] == fossil["mask_digest_at_T"],
                               "match": match})
        val["all_match"] &= match
        if not match:
            continue
        # per-IC success: recompute the correctness vector (classify does not return it)
        target = core.majority_target(ics)
        final = core.evolve(ics, table, payload["steps"])
        ones = final.sum(axis=1)
        correct = np.where(target == 1, ones == payload["n_cells"], ones == 0)
        k = ics.sum(axis=1)
        n_ic = payload["n_ic"]
        for i in range(ics.shape[0]):
            recs.append({"row_id": row["row_id"], "rule": row["labels"]["mechanism"],
                         "N": payload["n_cells"], "ensemble": row["labels"]["pressure"],
                         "seed_root": row["labels"]["seed_root"],
                         "repeat": rep["repeat_index"], "ic": i,
                         "nominal_d": dens[i // n_ic], "k": int(k[i]),
                         "signed_m": float(k[i] / payload["n_cells"] - 0.5),
                         "m": abs(float(k[i] / payload["n_cells"] - 0.5)),
                         "abs_count_margin": int(abs(2 * int(k[i]) - payload["n_cells"])),
                         "success": bool(correct[i])})
    return recs, val


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    led = Ledger()
    rows = [r for r in led.read("rows") if r["status"] == "COMPLETED"
            and r["labels"]["intervention"] == "NONE" and r.get("phase") != "replay"]
    allrecs: List[dict] = []
    vals: List[dict] = []
    for r in rows:
        recs, val = per_ic_rows(r)
        vals.append(val)
        allrecs.extend(recs)
        print("[dissect] %-40s match=%s n_ic=%d" % (r["labels"]["mechanism"] + "/" + r["labels"]["world"]
                                                     + "/" + r["labels"]["pressure"] + "/s%d" % r["labels"]["seed_root"],
                                                     val["all_match"], len(recs)), flush=True)
    # CHEAT-A: perturbed seed on the first row must fail
    cheat_recs, cheat_val = per_ic_rows(rows[0], seed_offset=7)
    cheat = {"cheat": "CHEAT-A perturbed seed (+7)", "row_id": rows[0]["row_id"],
             "expected": "no match", "all_match": cheat_val["all_match"],
             "caught": not cheat_val["all_match"], "records_emitted": len(cheat_recs)}
    with (OUT / "per_ic.jsonl").open("w", encoding="utf-8") as f:
        for rec in allrecs:
            f.write(json.dumps(rec) + "\n")
    summary = {"rows": len(rows), "rows_all_match": sum(1 for v in vals if v["all_match"]),
               "per_ic_records": len(allrecs), "cheat_a": cheat, "validation": vals}
    (OUT / "per_ic_validation.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "validation"}, indent=1))
    return 0 if summary["rows_all_match"] == len(rows) and cheat["caught"] else 1


if __name__ == "__main__":
    sys.exit(main())
