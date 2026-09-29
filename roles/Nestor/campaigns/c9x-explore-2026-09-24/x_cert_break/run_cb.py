"""X-CERT-BREAK (EXPLORE, INSTRUMENT / ruler localization; child of X-CORE-TIME). Declared before running.

Open instrument question since X-ATOMIC-RANDOM: in runaway populations the founder's CERTIFIED causal
lineage (P-11 edges only) stops at depth 5-22 while the anc marker says ~100% of the population
descends from the founder. anc passes on every accepted pair-tape replication event; the edge is
causal only if P-11 passes (C2 donor rebuilds a randomized victim, C4 donor authorship, C5 the
donor-disabled control does NOT reach donor-likeness). Question: how often are replication events
in a runaway uncertified, when, and which P-11 criterion fails?

Sample: the first 6 C-CORE runaway runs by seed (7ae3's cell, ATOMIC, 7ae3 founder), replayed
untagged with the X-DONOR-SWAP ATOMIC runner; world depth must equal the C-CORE record.
Every birth passed to _lin_birth is counted by epoch window W1 = [0,100), W2 = [100,500),
W3 = [500, end]: total, causal (P-11 pass), and for non-causal births with a P-11 record, which of the
C2/C4/C5 majorities failed; also the median ordinary fid_init (victim's similarity to the donor
before the event) for causal and non-causal births.
INVALID if any replay depth differs from its record.
Classification: SIGNAL if in >= 5 of 6 runs the non-causal share of births in W3 is >= 0.5 AND one
criterion is failed by >= 70% of W3 non-causal births (pooled); CLEAN_NULL if in >= 5 of 6 runs the
non-causal share in W3 is < 0.1; WEAK_SIGNAL otherwise.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
CK = HERE.parent / "c_core"
sys.path.insert(0, str(HERE.parent / "x_donor_swap"))
C9 = HERE.parent.parent / "z80atlas-verify-2026-09-22"
sys.path.insert(0, str(C9))
SPEC = "7ae3f9c1437c8000-s54765-tL-a0"


def plan():
    res = json.loads((CK / "RESULTS.json").read_text())
    run = sorted((r for r in res if r["depth"] >= 20 and r["anc0_share"] >= 0.9), key=lambda r: r["seed"])
    return [(r["seed"], r["depth"]) for r in run[:6]]


def win(e):
    return "W1" if e < 100 else "W2" if e < 500 else "W3"


def job(args):
    seed, recorded = args
    import world
    import run_ds
    arm = run_ds.cells()[SPEC]
    stats = {w: {"births": 0, "causal": 0, "noncausal_with_p11": 0, "fail_C2": 0, "fail_C4": 0, "fail_C5": 0,
                 "fid_init_causal": [], "fid_init_noncausal": []} for w in ("W1", "W2", "W3")}

    class Cb(run_ds.runner_cls(world)):
        def _lin_birth(self, child, parent, niche, fid, span, causal, causal_pred=None, p11_rec=None):
            s = stats[win(self.epoch)]
            s["births"] += 1
            fi = p11_rec.get("fid_init_ordinary") if p11_rec else None
            if causal:
                s["causal"] += 1
                if fi is not None:
                    s["fid_init_causal"].append(fi)
            elif p11_rec is not None:
                s["noncausal_with_p11"] += 1
                for c in ("C2", "C4", "C5"):
                    if not p11_rec.get(c, True):
                        s["fail_" + c] += 1
                if fi is not None:
                    s["fid_init_noncausal"].append(fi)
            super()._lin_birth(child, parent, niche, fid, span, causal, causal_pred, p11_rec)

    r = Cb(dict(arm["cell"], atlas_axis="NONE"), seed, tier=arm["tier"],
           implant="ACTUAL_GENOME", implant_bytes=run_ds.donor_genome())
    out = r.run()
    for s in stats.values():
        for k in ("fid_init_causal", "fid_init_noncausal"):
            v = s.pop(k)
            s["median_" + k] = round(statistics.median(v), 4) if v else None
    rec = {"seed": seed, "depth": out["max_causal_replication_depth"], "recorded_depth": recorded, "windows": stats}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / ("%d.json" % seed)).write_text(json.dumps(rec))
    return rec


def main():
    todo = plan()
    done = {p.stem for p in (HERE / "results").glob("*.json")} if (HERE / "results").exists() else set()
    with mp.Pool(6, maxtasksperchild=1) as pool:
        list(pool.imap_unordered(job, [t for t in todo if str(t[0]) not in done]))
    res = [json.loads(p.read_text()) for p in sorted((HERE / "results").glob("*.json"))]
    mism = [r["seed"] for r in res if r["depth"] != r["recorded_depth"]]
    share = {r["seed"]: (1 - r["windows"]["W3"]["causal"] / r["windows"]["W3"]["births"]) if r["windows"]["W3"]["births"] else 0.0
             for r in res}
    nc = sum(r["windows"]["W3"]["noncausal_with_p11"] for r in res)
    fails = {c: sum(r["windows"]["W3"]["fail_" + c] for r in res) for c in ("C2", "C4", "C5")}
    top = max(fails.values()) / nc if nc else 0.0
    hi = sum(v >= 0.5 for v in share.values())
    lo = sum(v < 0.1 for v in share.values())
    cls = ("INVALID" if mism or len(res) != len(todo) else "SIGNAL" if hi >= 5 and top >= 0.7 else
           "CLEAN_NULL" if lo >= 5 else "WEAK_SIGNAL")
    summ = {"classification": cls, "replay_mismatches": mism,
            "W3_noncausal_share": {k: round(v, 4) for k, v in share.items()},
            "W3_pooled_noncausal_with_p11": nc, "W3_pooled_criterion_failures": fails,
            "W3_top_criterion_share": round(top, 4), "runs": res}
    (HERE / "SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
