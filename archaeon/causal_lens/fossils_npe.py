"""Target C: replay NPE H2 RESERVOIR arms exactly as frozen (MANIFEST_FROZEN.json), observe, apply the frozen NPE lens.
    python -m archaeon.causal_lens.fossils_npe [--bundles 2] [--workers 6] [--smoke]
Raw replay records -> C:/Prometheus-data/evidence/portability01_2026-09-26/npe/ ; lens summaries -> archaeon/causal_lens/out/npe/.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EVID = Path(r"C:\Prometheus-data\evidence\portability01_2026-09-26\npe")
OUT = REPO / "archaeon/causal_lens/out/npe"
MAN = REPO / "roles/Nestor/campaigns/z80atlas-verify-2026-09-22/MANIFEST_FROZEN.json"


def arms(nb: int):
    m = json.loads(MAN.read_text(encoding="utf-8")); out = []
    for b in m["bundles"]:
        if b["hypothesis_id"] != "H2": continue
        a0 = b["arms"][0]; cell = a0["cell"] if isinstance(a0["cell"], dict) else eval(a0["cell"])
        if cell.get("structure") != "RESERVOIR": continue
        for a in b["arms"]:
            c = a["cell"] if isinstance(a["cell"], dict) else eval(a["cell"]); kw = a["kwargs"] if isinstance(a["kwargs"], dict) else eval(a["kwargs"])
            out.append({"specimen": b["specimen"], "arm": a["arm"], "cell": c, "seed": int(a["seed"]), "tier": a["tier"], "kwargs": kw})
        if len({x["specimen"] for x in out}) >= nb: break
    return out


def one(job, max_epochs=None):
    from archaeon.causal_lens.adapters import npe as A
    t0 = time.time(); kw = dict(job["kwargs"])
    if max_epochs: kw["max_epochs"] = max_epochs
    rec = A.replay(job["cell"], job["seed"], job["tier"], kw); rec["wall_s"] = round(time.time() - t0, 1)
    name = "%s__%s" % (job["specimen"], job["arm"])
    if not max_epochs:
        EVID.mkdir(parents=True, exist_ok=True)
        (EVID / (name + ".replay.json")).write_text(json.dumps({"job": job, **{k: v for k, v in rec.items() if k != "summary"},
                                                               "summary": rec["summary"]}, default=str), encoding="utf-8")
    L = A.lens(rec)
    return name, {"job": {k: job[k] for k in ("specimen", "arm", "seed", "tier")}, "wall_s": rec["wall_s"], "lineage_n": len(rec["lineage"]),
                  "founders": L["founders"], "hu_origin_classes": sorted(set(L["hu_origin"].values())), "events": L["events"]}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    nb = int(argv[argv.index("--bundles") + 1]) if "--bundles" in argv else 2
    wk = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 6
    jobs = arms(nb)
    if "--smoke" in argv:
        name, r = one(jobs[1], max_epochs=40); print(name, r["wall_s"], r["lineage_n"], len(r["events"]), r["hu_origin_classes"]); return
    OUT.mkdir(parents=True, exist_ok=True); res = {}
    with ProcessPoolExecutor(wk) as ex:
        for name, r in ex.map(one, jobs): res[name] = r; print(name, r["wall_s"], r["lineage_n"], flush=True)
    (OUT / "NPE_LENS_EVENTS.json").write_text(json.dumps(res, default=str) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
