"""C-010-T020 independent audit beside the frozen evaluator (W2 known escape S-1): for every P-OBS, P-PRES and P-ERASE
node, the stored action arrays must have one row per declared seed group (P-OBS: per seed; P-PRES: per (warm-up, seed)
pair; P-ERASE: per (pre_a, pre_b, probe) triple) and 40 steps. It changes no gate and no class; it only reports
whether the escape is exercised in the registered bundles. Usage: python -B -m rso.witness.runs.audit_pair_shapes B..."""
import json
import os
import sys

from rso.witness import evaluate as EVW

GROUP = {"P-OBS": 1, "P-PRES": 2, "P-ERASE": 3}
ROLES = {"P-OBS": ("trace:actions_record", "trace:actions_norecord"), "P-PRES": ("trace:pres_warm", "trace:pres_fresh"),
         "P-ERASE": ("trace:probe_after_a", "trace:probe_after_b")}
STEPS = 40


def audit(roots):
    rows = []
    for root in roots:
        man = json.load(open(os.path.join(root, "MANIFEST.json"), encoding="utf-8"))
        for n in man["nodes"]:
            rec = json.loads(open(os.path.join(root, n["receipt_file"]), "rb").read().decode("utf-8"))
            pred = rec["predicate"]
            if pred not in GROUP:
                continue
            want = len(rec["seeds"]) // GROUP[pred]
            listing = {a["role"]: a for a in rec["outputs"]}
            shapes = {}
            for role in ROLES[pred]:
                arr = EVW.decode(root, listing[role])
                shapes[role] = list(arr.shape)
            ok = all(s[0] == want and s[1] == STEPS for s in shapes.values())
            rows.append({"bundle": os.path.basename(os.path.normpath(root)), "node_id": rec["node_id"], "predicate": pred,
                         "declared_groups": want, "shapes": shapes, "ok": ok})
    return rows


if __name__ == "__main__":
    out = audit(sys.argv[1:])
    print(json.dumps({"schema": "rso.witness.pair_shape_audit.v0", "all_ok": all(r["ok"] for r in out), "rows": out},
                     indent=1, sort_keys=True))
