"""THEO-14: re-derive Vivarium bench ca_density_v0 fossils per IC.

PREREG: roles/Theophrastus/crucible/PREREG_THEO14_CROSS_CONSUMER_2026-09-14.md
Read-only over viv.research_experiment_queue. Each repeat is regenerated
through the SAME path the wrapper uses -- make_ics per density block, then
vivarium/viv/ca_density.apply_transform on the realised sample -- so a
transformed row is matched on its own terms, not waved through by the
symmetry. Outputs under roles/Theophrastus/crucible/theo14/.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO, REPO / "vivarium"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
from viv import db as _vdb                         # noqa: E402
from viv import ca_density as _ca                  # noqa: E402
from herakles.evca import core, genomes            # noqa: E402
from theophrastus import curves as CV              # noqa: E402
from theophrastus import dissect as DS             # noqa: E402

OUT = REPO / "roles" / "Theophrastus" / "crucible" / "theo14"
HEX2NAME = {str(v["hex"]).lower(): k for k, v in genomes.GENOMES.items()}


def bench_rows():
    conn = _vdb.connect(); cur = conn.cursor()
    cur.execute("""select experiment_id, arm_id, family_id, experiment_spec, result_summary
                   from viv.research_experiment_queue
                   where experiment_spec->'work'->>'kind'='ca_density_v0' and status='completed'
                   order by finished_at""")
    return cur.fetchall()


def rederive(payload: dict, repeats: list, *, seed_offset: int = 0):
    table0 = core.decode_table(payload["rule_hex"])
    per_rep, correct_by_rep = [], []
    for rep in repeats:
        seed = int(rep["seed"]) + seed_offset
        ics = DS.regenerate(payload, seed)
        table, ics_t = _ca.apply_transform(payload["transform"], table0, ics, np)
        res = core.classify(table, ics_t, payload["steps"], witness_limit=0)
        fossil = rep["result"]
        acc_ok = abs(res["accuracy"] - fossil["accuracy_at_T"]) < 1e-12
        dig_ok = res["correct_mask_digest"] == fossil["mask_digest_at_T"]
        per_rep.append({"repeat_index": rep["repeat_index"], "seed": seed,
                        "acc_recomputed": res["accuracy"], "acc_fossil": fossil["accuracy_at_T"],
                        "accuracy_match": acc_ok, "digest_match": dig_ok})
        target = core.majority_target(ics_t)
        final = core.evolve(ics_t, table, payload["steps"])
        ones = final.sum(axis=1)
        correct = np.where(target == 1, ones == payload["n_cells"], ones == 0)
        correct_by_rep.append((ics, correct))
    return per_rep, correct_by_rep


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = bench_rows()
    vals, recs = [], []
    for eid, arm, fam, spec, rs in rows:
        payload = spec["work"]["payload"]
        repeats = rs["result"]["repeats"]
        per_rep, cbr = rederive(payload, repeats)
        ok = all(r["accuracy_match"] and r["digest_match"] for r in per_rep)
        name = HEX2NAME.get(payload["rule_hex"].lower(), "hex:" + payload["rule_hex"][:8])
        vals.append({"experiment_id": str(eid), "arm": arm, "family": fam, "rule": name,
                     "transform": payload["transform"], "n_cells": payload["n_cells"],
                     "steps": payload["steps"], "ic_density_set": payload["ic_density_set"],
                     "repeats": len(per_rep), "all_match": ok,
                     "first_mismatch": next((r for r in per_rep
                                             if not (r["accuracy_match"] and r["digest_match"])), None)})
        in_p3 = (payload["transform"] == "none" and payload["n_cells"] == 149
                 and payload["steps"] == 320 and payload["ic_density_set"] == [None] and ok)
        for (ics, correct), rep in zip(cbr, repeats):
            k = ics.sum(axis=1)
            for i in range(ics.shape[0]):
                recs.append({"experiment_id": str(eid), "arm": arm, "rule": name,
                             "transform": payload["transform"], "N": payload["n_cells"],
                             "repeat": rep["repeat_index"], "ic": i, "k": int(k[i]),
                             "m": abs(float(k[i] / payload["n_cells"] - 0.5)),
                             "signed_m": float(k[i] / payload["n_cells"] - 0.5),
                             "success": bool(correct[i]), "p3_eligible": in_p3})
    # P2 cheat
    eid, arm, fam, spec, rs = rows[0]
    cheat_rep, _ = rederive(spec["work"]["payload"], rs["result"]["repeats"], seed_offset=7)
    cheat = {"experiment_id": str(eid), "seed_offset": 7,
             "caught": not all(r["accuracy_match"] and r["digest_match"] for r in cheat_rep)}
    # P3: bench vs this seat's founding curve at identical coordinates
    mine = [r for r in CV.load() if r["N"] == 149 and r["ensemble"] == "P_iid"]
    p3 = {}
    for rule in sorted({r["rule"] for r in recs if r["p3_eligible"]}):
        A = [r for r in recs if r["p3_eligible"] and r["rule"] == rule]
        B = [r for r in mine if r["rule"] == rule]
        if not B:
            p3[rule] = {"compared": False, "why": "genome not in this seat's founding rows",
                        "bench_ics": len(A)}
            continue
        c = CV.compare(CV.table(A, lambda r: CV.bin_m(r["m"])), CV.table(B, lambda r: CV.bin_m(r["m"])))
        p3[rule] = {"compared": True, "bench_ics": len(A), "seat_ics": len(B),
                    **{k: v for k, v in c.items() if k != "rows"},
                    "pass": c["n_bins_abs_z_ge_3"] == 0}
    with (OUT / "per_ic_bench.jsonl").open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    summary = {"prereg": "roles/Theophrastus/crucible/PREREG_THEO14_CROSS_CONSUMER_2026-09-14.md",
               "rows": len(vals), "rows_all_match": sum(v["all_match"] for v in vals),
               "by_transform": dict(Counter(v["transform"] for v in vals)),
               "by_rule": dict(Counter(v["rule"] for v in vals)),
               "mismatches": [v for v in vals if not v["all_match"]],
               "P1_pass": all(v["all_match"] for v in vals),
               "P2_cheat": cheat, "P3": p3,
               "P3_pass": all(x.get("pass", True) for x in p3.values()),
               "per_ic_records": len(recs), "validation": vals}
    (OUT / "THEO14_RESULT.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "validation"}, indent=1))
    return 0 if summary["P1_pass"] and cheat["caught"] else 1


if __name__ == "__main__":
    sys.exit(main())
