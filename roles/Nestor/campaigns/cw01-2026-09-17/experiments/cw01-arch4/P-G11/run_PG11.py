"""P-G11 [T-X12 / T-X17; deformation R; runs FIRST in cycle 6]: do the temporal geometries survive changes
of RULER, DOSE, SAMPLING CONVENTION and PLACEMENT?

Rulers on the same constructions: self-displacement (reference), reward change vs the episode's expected
answers, answered-share change, normalised output-word distance. Conventions: episode family index 1 with
E 16 (P-F02's, CRN), index 2 with E 16, index 1 with E 32. Placements: the 7 positions; doses 1-4; order
variants. Full curves kept under every ruler and convention. Cluster assignment = nearest P-F02 centroid;
agreement with the reference assignment against a label-permutation band; per-shape survival.
Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ticks as TK             # noqa: E402
import manifold as MF          # noqa: E402
A, L = CM.A, CM.L
KEYS, POS, DOSES = MF.KEYS, MF.POS, MF.DOSES

PID, TID = "P-G11", "T-X12"
RULERS = ("disp", "reward", "answered", "outdist")
CONV = {"i1e16": (1, 16), "i2e16": (2, 16), "i1e32": (1, 32)}
VMAX = 15.0


def build(index, E):
    W = {"W0D1": A.episodes_for(A.ENVS["W0"], A.CAMPAIGN_SEED, "train", index, E), "W0D2": A.episodes_for(TK.W0D2, A.CAMPAIGN_SEED, "train", index, E), "K2": A.episodes_for(A.ENVS["W2_K2"], A.CAMPAIGN_SEED, "train", index, E)}
    V = {}
    for w, eps in W.items():
        V[w] = {"base": [TK.clone(e) for e in eps]}
        for _, pos in [x for x in POS if x[0] == w]:
            for n in DOSES:
                out = []
                for ep in eps:
                    puts, asks = TK.put_ticks(ep), TK.ask_ticks(ep)
                    at = {"before_first_ask": asks[0], "between_puts": puts[1] if len(puts) > 1 else puts[0], "before_first_put": puts[0], "before_second_ask": asks[1] if len(asks) > 1 else asks[0]}[pos]
                    out.append(TK.insert(ep, at, [[]] * n))
                V[w]["%s.n%d" % (pos, n)] = out
    w0 = TK.w0_variants(W["W0D1"])
    V["W0D1"]["order_ne"], V["W0D1"]["order_en"] = w0["ne"], w0["en"]
    return W, V


def answers_with_correct(m, eps):
    """answers + per-ask correctness and answered flags in one pass (C1.answers semantics)."""
    from proteus.foundry.vm import Player, Meter
    player = Player(m)
    ans, corr = [], []
    for ei, ep in enumerate(eps):
        st = player.fresh_state()
        rng = A.SplitMix64(A.seed_from("wse.vmrng", 0, ei))
        for ti, words in enumerate(ep.ticks):
            player.begin_tick(st)
            outs, _ = player.run_tick(st, [words], 1, rng, meter=Meter())
            if ti in ep.expected:
                a = outs[0][0] if outs[0] else None
                ans.append(a)
                corr.append(int(a is not None and a == ep.expected[ti]))
    return ans, corr


def rulers(a0, c0, a1, c1, pos_k2=None):
    if pos_k2 is not None:
        a0, c0, a1, c1 = a0[pos_k2::2], c0[pos_k2::2], a1[pos_k2::2], c1[pos_k2::2]
    n = max(1, len(a0))
    disp = sum(1 for x, y in zip(a1, a0) if x != y) / n
    rew = abs(sum(c1) - sum(c0)) / n
    ans = abs(sum(x is not None for x in a1) - sum(x is not None for x in a0)) / n
    pairs = [(x, y) for x, y in zip(a1, a0) if x is not None and y is not None]
    od = float(np.mean([min(abs(x - y), VMAX) / VMAX for x, y in pairs])) if pairs else 0.0
    return {"disp": disp, "reward": rew, "answered": ans, "outdist": od}


def job(j):
    p = j["program"]
    m = A.canonical(p["manifest"])
    out = {"pid": p["organism_id"], "lineage": p["lineage"], "curves": {}}
    for cname, (index, E) in CONV.items():
        W, V = build(index, E)
        vec = {r: {} for r in RULERS}
        for w in W:
            a0, c0 = answers_with_correct(m, V[w]["base"])
            silent = not any(x is not None for x in a0)
            for k, eps in V[w].items():
                if k == "base":
                    continue
                name = "%s.%s" % (w, k)
                if silent:
                    for r in RULERS:
                        vec[r][name] = float("nan")
                    continue
                a1, c1 = answers_with_correct(m, eps)
                pk = (0 if k.startswith("before_first_ask") else 1) if (w == "K2" and (k.startswith("before_first_ask") or k.startswith("before_second_ask"))) else None
                rr = rulers(a0, c0, a1, c1, pk)
                for r in RULERS:
                    vec[r][name] = rr[r]
        out["curves"][cname] = {r: [vec[r][k] for k in KEYS] for r in RULERS}
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "R", "scope": CM.SCOPE, "claim_type": "ruler-deformation", "rulers": RULERS, "conventions": CONV, "positions": POS, "doses": DOSES, "keys": KEYS,
                         "programs": "P-F02 census minus the P-F03 tops (parents, walkers 4/8/16, C4-08 tops) plus every member of clusters 0 and 4",
                         "assignment": "nearest P-F02 centroid (L1 over finite components) for each ruler x convention; the reference is disp / i1e16",
                         "readouts": ["agreement with the reference assignment per ruler x convention vs a 2000-label-permutation band", "per-shape survival share (members of each reference cluster keeping their cluster)", "per-ruler, per-shape mean curves (kept raw)"],
                         "reading": "SURVIVES if agreement is above the permutation band under every ruler and convention and every non-immune shape keeps >= 2/3 of its members under every ruler; BREAKS_UNDER_<x> otherwise, recorded per ruler / convention / shape",
                         "material_rule": "always material: the survival table is the result", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    progs = [p for p in MF.census_programs() if not p["organism_id"].startswith("pf03")]
    with A.pool(8) as ex:
        rows = list(ex.map(job, [{"program": p} for p in progs]))
    cents = MF.centroids()
    ref = {}
    for r in rows:
        v = r["curves"]["i1e16"]["disp"]
        ref[r["pid"]] = MF.nearest(v)[0] if all(x == x for x in v) else None
    table, survival, meancurves = {}, {}, {}
    rng = np.random.Generator(np.random.PCG64(0))
    for cname in CONV:
        for ruler in RULERS:
            asg = {}
            for r in rows:
                v = r["curves"][cname][ruler]
                asg[r["pid"]] = MF.nearest(v)[0] if all(x == x for x in v) else None
            pids = [p for p in asg if asg[p] is not None and ref[p] is not None]
            agree = float(np.mean([asg[p] == ref[p] for p in pids]))
            labs = np.array([ref[p] for p in pids])
            null = np.array([np.mean(rng.permutation(labs) == np.array([asg[p] for p in pids])) for _ in range(2000)])
            table["%s|%s" % (cname, ruler)] = {"agreement": agree, "p95": float(np.percentile(null, 95)), "clears": bool(agree > np.percentile(null, 95)), "n": len(pids)}
            surv = {}
            for c in cents:
                mem = [p for p in pids if ref[p] == c]
                surv[MF.SHAPE[c] + "#%d" % c] = {"n": len(mem), "kept": float(np.mean([asg[p] == c for p in mem])) if mem else None}
            survival["%s|%s" % (cname, ruler)] = surv
            meancurves["%s|%s" % (cname, ruler)] = {MF.SHAPE[c] + "#%d" % c: [float(np.nanmean([r["curves"][cname][ruler][i] for r in rows if ref[r["pid"]] == c])) if any(ref[r["pid"]] == c for r in rows) else None for i in range(len(KEYS))] for c in cents}
    breaks = []
    for key, t in table.items():
        if not t["clears"]:
            breaks.append(key + ": agreement below band")
        for sh, s in survival[key].items():
            if s["kept"] is not None and not sh.startswith("immune") and s["n"] >= 5 and s["kept"] < 2 / 3:
                breaks.append("%s: %s keeps %.2f" % (key, sh, s["kept"]))
    reading = "SURVIVES" if not breaks else "BREAKS: " + "; ".join(breaks[:12])
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "agreement": table, "survival": survival, "mean_curves": meancurves, "keys": KEYS, "n_programs": len(rows), "material": True, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "ruler x dose x convention x placement: %s; agreement %s; survival (non-immune) %s"
                      % (reading, {k: (round(v["agreement"], 3), v["clears"]) for k, v in table.items()}, {k: {s: round(x["kept"], 2) for s, x in v.items() if x["kept"] is not None and not s.startswith("immune")} for k, v in survival.items()}), True, detail={"agreement": table, "survival": survival})
    L.append_evidence("T-X17", PID, "cross: the manifold %s under four rulers and three conventions" % ("SURVIVES" if not breaks else "BREAKS (%d)" % len(breaks)), True)
    print("DONE %s (%.0f s) %s" % (reading, time.time() - t0, {k: round(v["agreement"], 3) for k, v in table.items()}))


if __name__ == "__main__":
    main()
