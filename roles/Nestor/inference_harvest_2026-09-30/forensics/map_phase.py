"""Task 3: phase arithmetic on real donors (does pointer advance mod 128 predict self-poisoning?).

    python -B map_phase.py   -> map_phase.json

Genomes: panel A (C-ZERO-SPECIFIC) and panel B (X-P2-BRIDGE/REGSTATE) donors in cell CF; the 43 X-DD-NOCOPY-CONTEXT
donors of delegates/corpus/q3_reset.json in their own cell (7ae3 -> C7, ffa6 -> CF), which carry W1 X-DD-SELFSTATE
labels (x_dd_selfstate/results/<cell>_<seed>.json, matched by (cell, seed); q3_reset.json supplies the genome hex).
Per genome and side s in {0,1}: R = 12 chains of 8 successive interactions; the donor starts from zero registers and
carries ITS OWN registers from one interaction to the next (world CARRY runner, run_ds ATOMIC); each interaction has a
fresh uniform random partner with zero registers (choice: isolates the donor's own state from partner state); the
donor's genome is reset to its original bytes each step (no mutational drift).
Recorded: per step, conversion of the partner (world label transfer, with whole identity >= 0.9 to the donor);
at step 1: the donor's register change dE = (E_after - E_before) & 127, dL likewise (tape addresses are 7-bit),
copy_bytes (donor context) and copy_bytes mod 128.
Reload test (step 1, same partner, the world RNG re-seeded identically): E reloaded iff E_after is the same when the
donor starts with E = 0 and with E = 1 (all else zero); L likewise.
Prediction (T6 phase arithmetic): side self-OK iff (dE == 0 or E reloaded) and (dL == 0 or L reloaded), using the
modal step-1 values over the R chains.
Observed: rate1 = conversion rate at step 1; rate_later = mean conversion rate over steps 2..8;
SELF_POISON iff rate_later < 0.25 * rate1 (W1's rule, with k=1 replaced by steps 2..8); undefined if rate1 == 0.
q3 direct check: carried_states (registers after one blank-partner self-execution from zero) -> side predicted
self-OK iff (E & 127) == 0 and (L & 127) == 0 (a reload cannot be seen in this record).
"""
from __future__ import annotations

import collections
import json
import random
import time

import map_common as M

R, S = 12, 8
OUT = M.HERE / "map_phase.json"
t0 = time.process_time()
ZS = (None, 0, 0)


def step1_regs(h, g, pg, side, regs, seed):
    h.r.rng.seed(seed)
    x = h.interact(g, pg, side, d_state=(regs, 0, 0), p_state=ZS)
    return x


def genome_phase(g, cell, tag):
    h = M.Harness("CARRY", 777, cell)
    rng = random.Random(repr(("PHASE", tag)))
    out = {}
    for side in (0, 1):
        conv = [[0] * S for _ in range(R)]
        dE, dL, cb, rE, rL = [], [], [], [], []
        for c in range(R):
            st = ZS
            for k in range(S):
                pg = M.rand_genome(rng, h.n)
                if k == 0:
                    sd = rng.randrange(1 << 30)
                    x0 = step1_regs(h, g, pg, side, [0] * 8, sd)
                    xe = step1_regs(h, g, pg, side, [0, 0, 0, 1, 0, 0, 0, 0], sd)
                    xl = step1_regs(h, g, pg, side, [0, 0, 0, 0, 0, 1, 0, 0], sd)
                    ra = x0["d_state"][0] or [0] * 8
                    dE.append(ra[3] & 127)
                    dL.append(ra[5] & 127)
                    cb.append(x0["d_tel"]["copy_bytes"])
                    rE.append(((xe["d_state"][0] or [0] * 8)[3] & 127) == (ra[3] & 127))
                    rL.append(((xl["d_state"][0] or [0] * 8)[5] & 127) == (ra[5] & 127))
                    x = x0
                else:
                    x = h.interact(g, pg, side, d_state=st, p_state=ZS)
                st = x["d_state"]
                conv[c][k] = 1 if (x["p_conv"] and M.ident(x["gp"], g) >= 0.9) else 0
        mode = lambda v: collections.Counter(v).most_common(1)[0]
        mE, mL = mode(dE), mode(dL)
        relE = sum(rE) / R >= 0.5
        relL = sum(rL) / R >= 0.5
        pred_ok = (mE[0] == 0 or relE) and (mL[0] == 0 or relL)
        rate1 = sum(conv[c][0] for c in range(R)) / R
        later = sum(conv[c][k] for c in range(R) for k in range(1, S)) / (R * (S - 1))
        obs = None if rate1 == 0 else ("SELF_POISON" if later < 0.25 * rate1 else "SELF_OK")
        out[side] = {"dE_mode": mE[0], "dE_mode_share": round(mE[1] / R, 3), "dL_mode": mL[0],
                     "dL_mode_share": round(mL[1] / R, 3), "E_reload": relE, "L_reload": relL,
                     "copy_bytes_mode": mode(cb)[0], "copy_mod128_mode": mode([v % 128 for v in cb])[0],
                     "pred_self_ok": pred_ok, "rate1": round(rate1, 3), "rate_later": round(later, 3),
                     "rate_by_step": [round(sum(conv[c][k] for c in range(R)) / R, 3) for k in range(S)],
                     "obs": obs}
    # donor level (pooled over sides, as W1's label)
    r1 = (out[0]["rate1"] + out[1]["rate1"]) / 2
    rl = (out[0]["rate_later"] + out[1]["rate_later"]) / 2
    obs = None if r1 == 0 else ("SELF_POISON" if rl < 0.25 * r1 else "SELF_OK")
    copying = [s for s in (0, 1) if out[s]["rate1"] > 0]
    pred = (any(out[s]["pred_self_ok"] for s in copying) if copying else None)
    return {"sides": out, "obs_donor": obs, "pred_donor_self_ok": pred}


def table(rows, pk, ok):
    t = collections.Counter()
    for r in rows:
        p, o = r.get(pk), r.get(ok)
        if p is None or o is None:
            continue
        t[("pred_OK" if p else "pred_POISON", o)] += 1
    return {"%s|%s" % k: v for k, v in sorted(t.items())}


def main():
    A = json.loads((M.P2 / "c_zero_specific" / "DONORS.json").read_text())
    B = json.loads((M.P2 / "x_p2_bridge" / "DONORS.json").read_text())
    q3 = json.loads((M.P2 / "delegates" / "corpus" / "q3_reset.json").read_text())
    ss = {}
    for p in (M.W1 / "x_dd_selfstate" / "results").glob("*.json"):
        r = json.loads(p.read_text())
        ss[(r["cell"], r["seed"])] = r
    res = {"R": R, "S": S, "panels": {}}
    for pn, D in (("A", A), ("B", B)):
        res["panels"][pn] = []
        for i, d in enumerate(D):
            x = genome_phase(bytes.fromhex(d["hex"]), "CF", (pn, i))
            x.update({"donor": i, "hex": d["hex"]})
            res["panels"][pn].append(x)
        print(pn, "done", round(time.process_time() - t0, 1), flush=True)
    res["panels"]["Q3"] = []
    for d in q3:
        cell = "C7" if d["cell"] == "7ae3" else "CF"
        x = genome_phase(bytes.fromhex(d["donor_hex"]), cell, ("Q3", d["cell"], d["seed"]))
        lab = ss.get((d["cell"], d["seed"]))
        cs = {}
        for c in d.get("carried_states", []):
            side, regs, fz, fc = c["side_regs_BCDEHLA_fz_fc"]
            cs.setdefault(side, []).append((regs, c["count"]))
        q3pred = {}
        for side, v in cs.items():
            regs = max(v, key=lambda t: t[1])[0]         # modal carried state; BCDEHLA (no (HL) slot)
            q3pred[side] = (regs[3] & 127) == 0 and (regs[5] & 127) == 0
        x.update({"cell": d["cell"], "seed": d["seed"], "status": d["status"],
                  "w1_label": lab["label"] if lab else None, "w1_rates_by_k": lab["rates_by_k"] if lab else None,
                  "q3_selfstate_rates_by_k": d.get("selfstate_rates_by_k"),
                  "q3_carried_pred_ok_by_side": q3pred,
                  "q3_carried_pred_ok": (any(q3pred.values()) if q3pred else None)})
        res["panels"]["Q3"].append(x)
    print("Q3 done", round(time.process_time() - t0, 1), flush=True)
    allp = res["panels"]["A"] + res["panels"]["B"] + res["panels"]["Q3"]
    sides = [dict(s, pred=s["pred_self_ok"]) for r in allp for s in r["sides"].values()]
    res["tables"] = {
        "side_level_pred_vs_own_obs_all": table(sides, "pred", "obs"),
        "donor_level_pred_vs_own_obs_AB": table(res["panels"]["A"] + res["panels"]["B"], "pred_donor_self_ok", "obs_donor"),
        "donor_level_pred_vs_own_obs_Q3": table(res["panels"]["Q3"], "pred_donor_self_ok", "obs_donor"),
        "Q3_pred_vs_W1_label": table(res["panels"]["Q3"], "pred_donor_self_ok", "w1_label"),
        "Q3_own_obs_vs_W1_label": table([dict(r, p=(r["obs_donor"] == "SELF_OK") if r["obs_donor"] else None)
                                         for r in res["panels"]["Q3"]], "p", "w1_label"),
        "Q3_carried_state_pred_vs_W1_label": table(res["panels"]["Q3"], "q3_carried_pred_ok", "w1_label"),
    }
    res["cpu_s"] = round(time.process_time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps(res["tables"], indent=1))
    print("cpu", res["cpu_s"])


if __name__ == "__main__":
    main()
