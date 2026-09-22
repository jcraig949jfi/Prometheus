"""G-R4-4: assemble primordial/ledger/qd/worlds_r4.json from the committed stage 1 and stage 2 rows.

    python -m primordial.metric.screen_run [--report]           # report only (default when anything is PENDING)
    python -m primordial.metric.screen_run --write --commit SHA  # write the file (refused while PENDING)

Every number is read from rows (never recomputed): floor_suite rows (G-R4-3-stage1), baseline rows,
floor_invariant rows (train128 learner) and the stage2_stop row (G-R4-3-stage2). A cell stage 2 never
reached gets a stage-1-only record (NOT_REACHED under every variant). The report lists survivors, HELD
cells, NOT_REACHED counts per variant, and PENDING cells with a learner cost estimate for the conductor.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from primordial.metric import screen as SC
from primordial.metric import worlds as WR

ROOT = pathlib.Path(__file__).resolve().parents[2]
STAGE1 = "primordial/ledger/rows/G/G-R4-3-stage1.jsonl"
STAGE2 = "primordial/ledger/rows/G/G-R4-3-stage2.jsonl"
LEARNER = "primordial/ledger/rows/G/G-R4-3-stage2-learner.jsonl"     # cleared learners run as their own jobs


def _rows(path) -> list[dict]:
    p = pathlib.Path(path)
    p = p if p.is_absolute() else ROOT / p
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def assemble(stage1=STAGE1, stage2=STAGE2, learner=LEARNER) -> list[dict]:
    s1, s2, sl = _rows(stage1), _rows(stage2), _rows(learner)
    suite = {(int(x["gen_seed"]), x["pressure"]): x for x in s1 if x.get("kind") == "floor_suite"}
    base = {(int(x["gen_seed"]), x["pressure"]): x for x in s2 if x.get("kind") == "baseline"}
    learn, lsrc = {}, {}
    for path, rows in ((stage2, s2), (learner, sl)):
        for x in rows:
            if x.get("kind") == "floor_invariant":
                learn[(int(x["gen_seed"]), x["pressure"])] = x
                lsrc[(int(x["gen_seed"]), x["pressure"])] = (x.get("exp_id"), str(path))
    recs = []
    for key in sorted(suite, key=lambda k: SC.order_key(suite[k])):
        src = {"floor": {"exp_id": "G-R4-3-stage1", "rows": [str(stage1)]}}
        if key in base:
            src["baseline"] = {"exp_id": "G-R4-3-stage2", "rows": [str(stage2)]}
        if key in learn:
            src["learner"] = {"exp_id": lsrc[key][0], "rows": [lsrc[key][1]]}
        recs.append(WR.cell(suite[key], base.get(key), learn.get(key), sources=src))
    return recs


def report(doc: dict) -> dict:
    act = SC.vkey(doc["q1_floor_policy"], doc["q2_policy"])
    cells = doc["cells"]
    by = {(c["world"], c["pressure"]): c for c in cells}

    def pend(keys):
        return [{"world": w, "pressure": p, "est_hours": by[(w, p)]["learner"]["est_hours"],
                 "ci95_lo": by[(w, p)]["baseline"]["ci95"][0], "bound": by[(w, p)]["floor"],
                 "gate_held64": by[(w, p)]["gate_held64"]} for w, p in keys]

    blk = WR.blocking(doc)
    non = [k for k in WR.pending(doc) if k not in blk]
    return {"cells": len(cells), "stage2_cells": sum(c["stage"] == 2 for c in cells), "active": act,
            "survived": [(c["world"], c["pressure"]) for c in cells if c["verdicts"][act]["verdict"] == "SURVIVED"],
            "held": [(c["world"], c["pressure"]) for c in cells if c["verdicts"][act]["verdict"] == "HELD"],
            "not_reached": {k: sum(c["verdicts"][k].get("cull_reason") == "NOT_REACHED" for c in cells)
                            for k in doc["variants"]},
            "pending_survivable_blocking": pend(blk), "pending_non_survivable": pend(non),
            "pending_hours_est": round(sum(by[k]["learner"]["est_hours"] for k in blk + non), 2)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage1", default=STAGE1)
    ap.add_argument("--stage2", default=STAGE2)
    ap.add_argument("--learner", default=LEARNER)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--commit", default="")
    ap.add_argument("--out", default=str(WR.WORLDS_R4))
    a = ap.parse_args(argv)
    doc = WR.build(assemble(a.stage1, a.stage2, a.learner), commit=a.commit)
    print(json.dumps(report(doc), indent=1))
    if a.write:
        if not a.commit:
            raise SystemExit("--write needs --commit (the sha holding the rows)")
        print(WR.write(doc, a.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
