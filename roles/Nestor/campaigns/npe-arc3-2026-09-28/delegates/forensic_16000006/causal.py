"""Causal tests (a) knock-in, (b) revert, (c) cross-graft, (d) all start states. Thresholds: PREREG_CAUSAL.md
(written before this script ran). Writes causal.json."""
import json
import pathlib
import random
import sys

import measure as M
from kcurve import KMAX

HERE = pathlib.Path(__file__).resolve().parent
CORPUS = HERE.parents[2] / "npe-p2-endogenous-heredity-2026-09-27" / "delegates" / "corpus"
sys.path.insert(0, str(CORPUS))
import corpus_analysis as ca  # noqa: E402

TAG = "F16-CAUSAL"
KS = 25
KNOCK = {20: 0x11, 21: 0x00, 22: 0x32}


def measure(g):
    import run_nc
    world, r = M.env()
    n = r.L
    out = {}
    conds = ["FRESH"] + ["SELF%d" % k for k in range(1, KMAX + 1)] + ["CONST", "RANDOM"]
    for cond in conds:
        hits = tot = 0
        for sd in range(KS):
            for side in (0, 1):
                if cond.startswith("SELF"):
                    st = M.FRESH
                    for j in range(int(cond[4:])):
                        st = M.exec_once(g, st, side, (TAG, "pre", sd, side, j))
                else:
                    st = M.start_state(g, cond, sd, side, TAG)
                hits += bool(run_nc.copies(world, r, g, st, bytes(n), M.FRESH, side, (TAG, cond, sd, side)))
                tot += 1
        out[cond] = round(hits / tot, 4)
    f = out["FRESH"]
    out["competent"] = M.competent(g)
    out["FUNCTIONAL"] = f >= 0.25 and out["competent"]
    out["STATE_ROBUST"] = f > 0 and out["SELF1"] >= 0.25 * f
    out["FR"] = f > 0 and all(out[c] >= 0.25 * f for c in conds[1:])
    return out


def patch(g, d):
    g = bytearray(g)
    for i, b in d.items():
        g[i] = b
    return bytes(g)


def show(tag, g, m):
    print(tag, g.hex()[:16], {k: m[k] for k in ("FRESH", "SELF1", "SELF2", "CONST", "RANDOM", "FUNCTIONAL",
                                               "STATE_ROBUST", "FR")}, flush=True)


def main():
    G = json.loads((HERE / "genealogy.json").read_text())
    P7 = json.loads((HERE / "paths700.json").read_text())
    res = {"a": [], "b": [], "c": []}
    # (a) knock-in
    for h in G["d0_genomes"]:
        g0 = bytes.fromhex(h)
        gk = patch(g0, KNOCK)
        m0, mk = measure(g0), measure(gk)
        show("a:D0  ", g0, m0)
        show("a:KI  ", gk, mk)
        res["a"].append({"d0": h, "ki": gk.hex(), "ctrl": m0, "knockin": mk,
                         "counts": mk["FUNCTIONAL"] and mk["FR"], "precond_not_FR": not m0["FR"]})
    # (b) revert
    for p in P7["paths"]:
        g1 = bytes.fromhex(p["genome"])
        b1 = patch(g1, {20: 0xE2, 21: 0x1A, 22: 0xE2})
        b2 = patch(g1, {20: 0x00})
        m1, mb1, mb2 = measure(g1), measure(b1), measure(b2)
        show("b:orig", g1, m1)
        show("b:rev1", b1, mb1)
        show("b:rev2", b2, mb2)
        res["b"].append({"orig": p["genome"], "ctrl": m1, "rev1": mb1, "rev2": mb2,
                         "rev1_counts": mb1["FUNCTIONAL"] and not mb1["FR"],
                         "rev1_destructive": not mb1["FUNCTIONAL"],
                         "rev2_counts": mb2["FUNCTIONAL"] and not mb2["FR"],
                         "rev2_destructive": not mb2["FUNCTIONAL"]})
    # (c) cross-graft
    world, r = M.env()
    cand = []
    for line in open(CORPUS / "q1_partial.jsonl"):
        x = json.loads(line)
        if x["vm"] != "DENSE" or x["cell"] != "7ae3" or x["rate_full"] < 0.5 or "16000006" in x["origin_run"]:
            continue
        g = bytes.fromhex(x["hex"])
        if 0xE5 not in g and 0xE7 not in g:
            continue
        m = measure(g)
        if not (m["FUNCTIONAL"] and not m["STATE_ROBUST"]):
            continue
        ev = []
        for side in (0, 1):
            victim = bytes(random.Random(7).randrange(256) for _ in range(r.L))
            ev = ca.trace_blockcopy(world, r, g, side, victim, st=M.FRESH)
            if ev:
                break
        if not ev or ev[0]["pc_rel_own"] < 3 or ev[0]["pc_rel_own"] >= 64:
            continue
        cand.append((x, g, m, ev[0]))
        if len(cand) == 12:
            break
    for x, g, m, e in cand:
        p = e["pc_rel_own"]
        c1 = patch(g, {p - 3: 0x11, p - 2: 0x00, p - 1: 0x32})
        de = (e["HL"] + 0x40) & 0xFFFF
        c2 = patch(g, {p - 3: 0x11, p - 2: de & 0xFF, p - 1: de >> 8})
        mc1, mc2 = measure(c1), measure(c2)
        show("c:orig", g, m)
        show("c:gr1 ", c1, mc1)
        show("c:gr2 ", c2, mc2)
        res["c"].append({"orig": g.hex(), "origin_run": x["origin_run"], "blockcopy": e, "ctrl": m,
                         "graft1": mc1, "graft2": mc2,
                         "g1_counts": mc1["FUNCTIONAL"] and mc1["STATE_ROBUST"],
                         "g2_counts": mc2["FUNCTIONAL"] and mc2["STATE_ROBUST"],
                         "g1_FR": mc1["FUNCTIONAL"] and mc1["FR"], "g2_FR": mc2["FUNCTIONAL"] and mc2["FR"]})
    na = sum(x["counts"] for x in res["a"])
    nb = sum(x["rev1_counts"] for x in res["b"])
    nc = sum(x["g1_counts"] for x in res["c"])
    va = "PASS" if na >= 4 else "FAIL" if na <= 1 else "PARTIAL"
    vb = "PASS" if nb >= 6 else "FAIL" if nb <= 2 else "PARTIAL"
    vc = ("STRONG" if res["c"] and nc >= 0.5 * len(res["c"]) else "PASS" if nc >= 1 else "FAIL")
    verdict = ("SURVIVES" if va == "PASS" and vb == "PASS" and vc in ("PASS", "STRONG") else
               "KILLED" if va == "FAIL" or vb == "FAIL" else "PARTIAL")
    summ = {"a_knockin": [na, len(res["a"]), va], "b_revert1": [nb, len(res["b"]), vb],
            "b_revert2_counts": sum(x["rev2_counts"] for x in res["b"]),
            "b_destructive": [sum(x["rev1_destructive"] for x in res["b"]), sum(x["rev2_destructive"] for x in res["b"])],
            "c_graft1": [nc, len(res["c"]), vc], "c_graft2": sum(x["g2_counts"] for x in res["c"]),
            "c_graft1_FR": sum(x["g1_FR"] for x in res["c"]), "c_graft2_FR": sum(x["g2_FR"] for x in res["c"]),
            "verdict_by_prereg": verdict}
    res["summary"] = summ
    (HERE / "causal.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
