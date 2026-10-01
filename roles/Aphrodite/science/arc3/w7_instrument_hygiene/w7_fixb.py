"""W7 PKG-6 (2): what fix (b) (dev/Q2 query draw widened to 1..97) and fix (a)
(T4 v1a) do to FROZEN foundry results, on a sample.
Sample: every family whose dev-domain PRISTINE/L1 equivalence class contains a
query-1/2-divergent program (from W7_T4DEV_ROWS.jsonl), plus a deterministic
control sample of other T4-qualified families.
Per family under fix (b): Q2 size with Prov197 (same label as the foundry),
then the 4 PRISTINE and 4 L1 pilot cells (same labels) walked at 250k with
a18.fast_cost, first hit scored by T4 v1 (direct). Compared with the frozen
Q2_size / p_PRISTINE / p_L1.
Usage: python w7_fixb.py <workers> [n_controls]   -> W7_FIXB.json
"""
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from w7_common import *              # noqa: F401,F403
import tribunal_t4 as T4             # noqa: E402
import tribunal_t4_v1a as T4A        # noqa: E402
import a17_dev197 as B               # noqa: E402


def job(r):
    a18.worker_init()
    t0 = time.time()
    spec = {r["name"]: (r["body"], r["final"], r["init"])}
    prov = B.Prov197(spec)
    a17.M.use_provider(prov)
    T4.use_provider(prov)
    w = ("fold", r["init"], r["body"], r["final"])
    out = {"tag": r["_tag"], "name": r["name"], "group": r["_group"], "Q2_frozen": r["Q2_size"],
           "p_PRISTINE_frozen": r.get("p_PRISTINE"), "p_L1_frozen": r.get("p_L1")}
    size = B.qualify(prov, r["name"], r["_tag"] + "-Q2")
    out["Q2_b"] = size
    if size is None:
        out["sec"] = round(time.time() - t0, 1)
        return out
    L = libs()
    for arm in ("PRISTINE", "L1"):
        _, cs = cells(r, arm, prov, size)
        hits = []
        for c in cs:
            ch, prog = a18.fast_cost(L[arm], c, FR.ESCROW)
            q = bool(prog) and T4A.direct_score(tuple(prog), r["name"], w, "v1")["qualified"]
            hits.append({"charge": ch, "prog": list(prog) if prog else None, "T4_v1": q})
        out["cells_b_" + arm] = hits
        out["p_%s_b" % arm] = sum(h["T4_v1"] for h in hits) / 4
    out["sec"] = round(time.time() - t0, 1)
    return out


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    nctl = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    dev = {(x["tag"], x["name"]): x for x in map(json.loads, open(HERE / "W7_T4DEV_ROWS.jsonl"))}
    fams = []
    for tag in ("A19", "A20"):
        for r in rows(tag):
            d = dev.get((tag, r["name"]))
            if d and d.get("edev_q12_divergent"):
                r["_group"] = "affected"
                fams.append(r)
    ctl = sorted((r for tag in ("A19", "A20") for r in rows(tag)
                  if not (dev.get((tag, r["name"])) or {}).get("edev_q12_divergent")),
                 key=lambda r: hashlib.sha256((r["_tag"] + r["name"]).encode()).hexdigest())[:nctl]
    for r in ctl:
        r["_group"] = "control"
    fams += ctl
    print("families", len(fams), flush=True)
    res = []
    with ProcessPoolExecutor(max_workers=workers, initializer=a18.worker_init) as ex:
        futs = [ex.submit(job, r) for r in fams]
        for k, f in enumerate(as_completed(futs)):
            res.append(f.result())
            if k % 10 == 0:
                print("done", k, res[-1]["sec"], flush=True)
                (HERE / "W7_FIXB.json").write_text(json.dumps(res, indent=1))
    (HERE / "W7_FIXB.json").write_text(json.dumps(res, indent=1))
    print("done all", flush=True)
