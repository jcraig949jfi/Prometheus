"""G1 V0-integrity check + tensor learning-curve milestone entry (charter s12).

G1: (a) V0 artifact files unchanged since the V0 commit; (b) the V0 evidence
snapshot refactors to the SAME reproducibility hash recorded in
ew.derived_artifacts at V0 time.
Learning curve: current-corpus stats appended to tensor_learning_curve.json.
No tensor rescue: numbers are recorded, not optimized.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from ew import compiler, db  # noqa: E402

V0_COMMIT = "c711c5bf6"
V0_FILES = ["evidence_wiki/benchmarks/results_v0.json",
            "evidence_wiki/gold/curation_v1.json",
            "evidence_wiki/gold/harvest_a.jsonl",
            "evidence_wiki/gold/harvest_b.jsonl",
            "evidence_wiki/gold/harvest_c.jsonl",
            "evidence_wiki/docs/CASE_STUDIES_V0.md"]


def main():
    out = {"generated": time.strftime("%Y-%m-%d %H:%M:%S")}
    diff = subprocess.run(["git", "diff", "--name-only", V0_COMMIT, "HEAD", "--"]
                          + V0_FILES, capture_output=True, text=True,
                          cwd=HERE.parent)
    out["G1_files_unchanged"] = diff.stdout.strip() == ""
    out["G1_changed_files"] = diff.stdout.split()

    conn = db.connect()
    with db.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.snapshots WHERE view_name='evidence_v1' "
                    "ORDER BY canonical_revision ASC LIMIT 1")
        snap0 = cur.fetchone()
        cur.execute("SELECT * FROM ew.derived_artifacts WHERE kind='cp' AND "
                    "snapshot_id=%s AND params->>'rank'='6' AND "
                    "params->>'seed'='0' ORDER BY created_at ASC LIMIT 1",
                    (snap0["snapshot_id"],))
        art0 = cur.fetchone()
    ref = compiler.factor(conn, snap0["snapshot_id"], "cp", 6, seed=0,
                          persist=False)
    out["G1_v0_snapshot"] = snap0["snapshot_id"]
    out["G1_repro_sha_match"] = bool(art0) and \
        ref["repro_sha256"] == art0["repro_sha256"]

    # ------------------------- learning-curve milestone on CURRENT corpus
    from ew import coords
    coords.generate(conn, "evidence_v1")
    snap = compiler.compile(conn, "evidence_v1", {})
    s, modes, dicts, coo, vals, eids = compiler.load_snapshot(conn, snap["snapshot_id"])
    shape = [len(dicts[m]) for m in modes]
    T = compiler._dense(modes, dicts, coo, vals)
    p = T.flatten() / T.sum()
    p = p[p > 0]
    entry = {
        "date": time.strftime("%Y-%m-%d"),
        "snapshot_id": snap["snapshot_id"],
        "canonical_revision": snap["canonical_revision"],
        "n_coordinates": int(snap["coord_count"]),
        "modes": dict(zip(modes, shape)),
        "dense_cells": int(np.prod(shape)),
        "density": float(snap["coord_count"] / np.prod(shape)),
        "occupied_cells": int((T > 0).sum()),
        "entropy_bits": float(-(p * np.log2(p)).sum()),
        "reconstruction_error": {},
        "cp_seed_stability": None,
        "milestone_note": "pre-250 baseline; G6 reopens at >=1000 real coordinates",
    }
    for method in ("cp", "tucker", "tt"):
        errs = {}
        for rank in (2, 4, 6, 8):
            try:
                r = compiler.factor(conn, snap["snapshot_id"], method, rank,
                                    seed=0, persist=False)
                errs[rank] = round(r["relative_error"], 4)
            except Exception as e:
                errs[rank] = f"error: {e}"
        entry["reconstruction_error"][method] = errs
    from scipy.optimize import linear_sum_assignment
    base = compiler.factor(conn, snap["snapshot_id"], "cp", 6, seed=0, persist=False)
    sims = []
    for seed in (1, 2, 3):
        alt = compiler.factor(conn, snap["snapshot_id"], "cp", 6, seed=seed,
                              persist=False)
        A = np.concatenate([np.array(f) for f in base["_payload"]["factors"]])
        B = np.concatenate([np.array(f) for f in alt["_payload"]["factors"]])
        A /= (np.linalg.norm(A, axis=0, keepdims=True) + 1e-12)
        B /= (np.linalg.norm(B, axis=0, keepdims=True) + 1e-12)
        C = A.T @ B
        ri, ci = linear_sum_assignment(-np.abs(C))
        sims.append(float(np.abs(C[ri, ci]).mean()))
    entry["cp_seed_stability"] = round(float(np.mean(sims)), 4)

    curve_path = HERE / "benchmarks" / "tensor_learning_curve.json"
    curve = json.loads(curve_path.read_text()) if curve_path.exists() else {"milestones": []}
    curve["milestones"].append(entry)
    curve_path.write_text(json.dumps(curve, indent=1), encoding="utf-8")
    out["learning_curve_entry"] = entry
    (HERE / "benchmarks" / "g1_integrity_v1.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    conn.close()


if __name__ == "__main__":
    main()
