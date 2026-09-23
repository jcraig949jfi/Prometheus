"""C0m: mechanism-level attack on the frozen law (roles/Cosmos/campaigns/c0m/PREREG.md).

  python -m prometheus.cosmos.c0m <c0b_campaign_out_dir> <out_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.contract import coords_of, terminals_for
from prometheus.cosmos.miner import law_from_json
from prometheus.cosmos.pipeline import Chamber
from prometheus.cosmos.store import Store
from prometheus.cosmos.substrates import visible


def _ba(p, y):
    p, y = np.asarray(p, bool), np.asarray(y)
    return float(0.5 * ((p & (y == 1)).sum() / max(1, (y == 1).sum()) + (~p & (y == 0)).sum() / max(1, (y == 0).sum())))


def main(c0b, out):
    out = Path(out)
    law_row = [l for l in Store(Path(c0b) / "store").laws() if l["freeze_hash"]][0]
    L = law_from_json(law_row["body"]["law"])
    cmap = law_row["body"]["cmap"]
    fam = visible()["regs"]
    st = Store(out / "store")
    st.receipts.append("c0m_start", {"law_id": law_row["law_id"], "freeze_hash": law_row["freeze_hash"]})
    ch = Chamber([fam], store=st, campaign="c0m")
    rng = np.random.default_rng(20260925)
    sp = fam.space()
    rows = []
    for _ in range(300):
        p1 = {k: v[rng.integers(len(v))] for k, v in sp.items()}
        p1 = {k: (float(x) if isinstance(x, (float, np.floating)) else int(x)) for k, x in p1.items()}
        p3 = dict(p1, code=3)
        r1 = ch.observe("regs", p1, purpose="c0m:code1")
        r3 = ch.observe("regs", p3, purpose="c0m:code3", parent=r1["world_id"], edge_kind="DEFORMATION_OF",
                        delta={"knob": "code", "from": 1, "to": 3})
        c1, c3 = coords_of(fam, p1, cmap), coords_of(fam, p3, cmap)
        c3_wrong = dict(coords_of(fam, dict(p1), cmap), C=c3["C"])     # code-3 cost, code-1 hazard
        X = lambda c: {k: np.array([c[k]]) for k in terminals_for(cmap)}
        rows.append({"p": p1, "y1": r1["y"], "y3": r3["y"], "m1": r1["margin"], "m3": r3["margin"],
                     "pred1": bool(L.predict(X(c1))[0]), "pred3": bool(L.predict(X(c3))[0]),
                     "pred3_wrongN": bool(L.predict(X(c3_wrong))[0]), "c3": c3})
    y1 = [r["y1"] for r in rows]
    y3 = [r["y3"] for r in rows]
    res = {"n": len(rows), "pays_rate_code1": float(np.mean(y1)), "pays_rate_code3": float(np.mean(y3)),
           "BA_code1": _ba([r["pred1"] for r in rows], y1), "BA_code3": _ba([r["pred3"] for r in rows], y3),
           "BA_code3_with_code1_hazard": _ba([r["pred3_wrongN"] for r in rows], y3),
           "verdict_changed_by_mechanism": int(sum(a != b for a, b in zip(y1, y3)))}
    res["M1"] = "PASS" if res["BA_code3"] >= 0.90 else "FAIL"
    res["M2"] = "PASS" if res["BA_code3"] >= res["BA_code1"] - 0.05 else "FAIL"
    res["errors_code3"] = [r for r in rows if r["pred3"] != bool(r["y3"])][:30]
    st.receipts.append("c0m_result", {k: v for k, v in res.items() if k != "errors_code3"})
    st.commit()
    (out / "C0M.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "errors_code3"}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
