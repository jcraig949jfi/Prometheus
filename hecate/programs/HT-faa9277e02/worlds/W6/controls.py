"""W6 controls: POSITIVE_CONTROL, CHEAT, NULL_TWIN (no treatment code).

Frozen parameters are those of spec.json. Plasticity is never run here.

World: Gierer-Meinhardt on a 48x48 torus, per-edge activator couplings g_e
(flux D0*g_e*(a_j-a_i)), uniform inhibitor diffusion Dh.

Per seed (all arms of a seed share reference noise, lesion position and
lesion noise):
  reference: 3000 steps on g = 1 from a = h = 1 + 0.01*N(0,1)  (stream 0)
  FIXED (the spec's control, computed here as the paired baseline): settle
      1500 on g = 1 -> O; lesion; regrow 3000 on g = 1.
  POSITIVE_CONTROL: carve g from the reference map (core = z > 1; edge joining
      core and non-core -> 0.1, else 1); settle 1500 on carved g -> O; lesion;
      regrow 3000 on carved g.
  NULL_TWIN: carved g with edges fully inside the lesion permuted among
      themselves (stream 3); same O, lesion, lesion noise; regrow 3000.
  NULL_TWIN_B: a second independent permutation (stream 4); only used to put
      a twin in the arm slot of the relative clauses (twin_value of S2, S4).
  CHEAT: the NULL_TWIN regrown map with the lesion overwritten by O
      (success injected into the observable).
Observable RIF = I_MM(O_bin; R_bin) / H(O_bin) over lesion cells, each map
binarized at its own whole-field mean.

Rows -> control_rows.jsonl (flushed per row); then ATTAINABILITY.json.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 48
MU, D0, DH, DT = 2.0, 0.5, 10.0, 0.02
T_REF, T_SETTLE, T_REGROW = 3000, 1500, 3000
L = 24
LES_NOISE = 0.3
G_ACROSS = 0.1
SEEDS = list(range(10))

REVISIONS = [
    {"rev": 0, "what": "first design: open-question lesion 16x16, lesion noise 0.01, positive control 'core_low' (g=0.3 on every edge touching a core, 1 elsewhere); observable raw MM bits",
     "result": "FIXED (g=1) medium recovered r_lesion 0.86 / bits 0.43, ABOVE the positive control (bits 0.16): border pinning alone repairs a 16x16 lesion (about 2.4 wavelengths) from low noise; raw bits capped by the low entropy of sparse spot maps",
     "why_changed": "clause would be dominated by border pinning and bits not comparable across media", "rows": "revisions/rev0_core_low_L16_n0.01.jsonl"},
    {"rev": 1, "what": "observable -> RIF = MI / H(O_bin) inside lesion; tried L in {16,24} x lesion noise in {0.01,0.3} for core_low, and core_high (W1-style: core-core 5, core-boundary 0.2) at L=24, noise 0.3",
     "result": "L=24 + noise 0.3 drops FIXED RIF to 0.145; core_low PC RIF 0.20 vs twin 0.04; core_high PC 0.28 vs twin 0.08",
     "why_changed": "positive-control margin over FIXED too small (<0.14) for a clean treatment-vs-control clause", "rows": "revisions/rev1_*.jsonl"},
    {"rev": 2, "what": "carving strength variants at L=24, noise 0.3: core_low g=0.1; core_high 10/0.1; boundary-only cut (core-core 1, core-boundary 0.1)",
     "result": "boundary-only cut: PC RIF 0.381, twin 0.056, FIXED 0.145 (best separation); core_high 10/0.1: 0.27; core_low 0.1: 0.28 (twin 0.02 but PC r_lesion 0.16)",
     "why_changed": "froze boundary-only cut (g=0.1 across core boundaries) as the positive control; thresholds set below positive and above twin/FIXED", "rows": "revisions/rev2_*.jsonl"},
    {"rev": 3, "what": "final file: frozen parameters hard-coded, NULL_TWIN_B added for twin-in-arm-slot values of relative clauses, evaluator writes ATTAINABILITY.json from spec.json clauses",
     "result": "see clauses", "why_changed": "freeze", "rows": "control_rows.jsonl"},
]


def rng_for(seed, stream):
    return np.random.default_rng(np.random.SeedSequence([20260930, 6, seed, stream]))


def step(a, h, gh, gv):
    # gh[y,x]: edge (y,x)-(y,x+1); gv[y,x]: edge (y,x)-(y+1,x); torus
    fx = gh * (np.roll(a, -1, 1) - a)
    fy = gv * (np.roll(a, -1, 0) - a)
    div = fx - np.roll(fx, 1, 1) + fy - np.roll(fy, 1, 0)
    lap_h = np.roll(h, 1, 0) + np.roll(h, -1, 0) + np.roll(h, 1, 1) + np.roll(h, -1, 1) - 4 * h
    a2 = a * a
    an = a + DT * (D0 * div + a2 / h - a)
    hn = h + DT * (DH * lap_h + MU * (a2 - h))
    return np.maximum(an, 0.0), np.maximum(hn, 1e-6)


def run(a, h, gh, gv, n):
    for _ in range(n):
        a, h = step(a, h, gh, gv)
    return a, h


def carve(amap):
    z = (amap - amap.mean()) / amap.std()
    core = z > 1.0
    gh = np.where(core ^ np.roll(core, -1, 1), G_ACROSS, 1.0)
    gv = np.where(core ^ np.roll(core, -1, 0), G_ACROSS, 1.0)
    return gh.astype(float), gv.astype(float)


def lesion_mask(seed):
    r = rng_for(seed, 1)
    y0, x0 = r.integers(0, N, size=2)
    ys = (y0 + np.arange(L)) % N
    xs = (x0 + np.arange(L)) % N
    m = np.zeros((N, N), bool)
    m[np.ix_(ys, xs)] = True
    return m


def scramble_inside(gh, gv, mask, seed, stream):
    r = rng_for(seed, stream)
    inh = mask & np.roll(mask, -1, 1)
    inv = mask & np.roll(mask, -1, 0)
    gh2, gv2 = gh.copy(), gv.copy()
    vals = r.permutation(np.concatenate([gh[inh], gv[inv]]))
    nh = int(inh.sum())
    gh2[inh] = vals[:nh]
    gv2[inv] = vals[nh:]
    return gh2, gv2


def lesion(a, h, mask, seed):
    r = rng_for(seed, 2)
    a, h = a.copy(), h.copy()
    k = int(mask.sum())
    a[mask] = np.maximum(1 + LES_NOISE * r.standard_normal(k), 0.0)
    h[mask] = np.maximum(1 + LES_NOISE * r.standard_normal(k), 1e-3)
    return a, h


def _H(counts, n):
    c = counts[counts > 0]
    p = c / n
    return float(-(p * np.log2(p)).sum())


def score(O, R, mask):
    bo = (O > O.mean())[mask].astype(int)
    br = (R > R.mean())[mask].astype(int)
    n = len(bo)
    cx, cy = np.bincount(bo, minlength=2), np.bincount(br, minlength=2)
    cxy = np.bincount(2 * bo + br, minlength=4)
    mm = lambda c: _H(c, n) + ((c > 0).sum() - 1) / (2 * n * np.log(2))
    bits = mm(cx) + mm(cy) - mm(cxy)
    h_o = _H(cx, n)
    rif = bits / h_o if h_o > 0 else 0.0
    o, rr = O[mask], R[mask]
    pr = float(np.corrcoef(o, rr)[0, 1]) if o.std() > 0 and rr.std() > 0 else 0.0
    return {"rif": float(rif), "bits": float(bits), "H_O_lesion": h_o, "r_lesion": pr,
            "agree": float((bo == br).mean())}


# ---------------- evaluator (shared with the later probe) ----------------
def by_arm(rows):
    d = {}
    for r in rows:
        d.setdefault(r["arm"], {})[r["seed"]] = r
    return d


def statistic(name, arm, twin, fixed):
    seeds = sorted(arm)
    if name == "seed_mean_rif":
        return float(np.mean([arm[s]["rif"] for s in seeds]))
    if name == "seed_mean_rif_minus_twin":
        return float(np.mean([arm[s]["rif"] - twin[s]["rif"] for s in seeds]))
    if name == "seed_mean_rif_minus_fixed":
        return float(np.mean([arm[s]["rif"] - fixed[s]["rif"] for s in seeds]))
    if name == "n_seeds_rif_above_twin":
        return int(sum(arm[s]["rif"] > twin[s]["rif"] for s in seeds))
    raise KeyError(name)


def holds(v, cmp, thr):
    return {">=": v >= thr, ">": v > thr, "<": v < thr, "<=": v <= thr}[cmp]


def attainability(rows, spec):
    A = by_arm(rows)
    pos = ("POSITIVE_CONTROL", "NULL_TWIN")
    twn = ("NULL_TWIN", "NULL_TWIN_B")
    che = ("CHEAT", "NULL_TWIN")
    fixed = A["FIXED"]
    ev = lambda cl, pair: statistic(cl["statistic"], A[pair[0]], A[pair[1]], fixed)
    clauses = []
    must = {
        "S1": "treatment seed-mean RIF >= 0.25",
        "S2": "treatment RIF >= its own twin RIF + 0.15 (twin of the positive control: %.3f, so about %.2f)",
        "S3": "treatment RIF >= FIXED RIF + 0.10 (FIXED seed-mean %.3f, so about %.2f)",
        "S4": "treatment RIF above its own twin in >= 9 of 10 seeds",
    }
    twin_mean = statistic("seed_mean_rif", A["NULL_TWIN"], None, None)
    fixed_mean = float(np.mean([fixed[s]["rif"] for s in fixed]))
    must["S2"] = must["S2"] % (twin_mean, twin_mean + 0.15)
    must["S3"] = must["S3"] % (fixed_mean, fixed_mean + 0.10)
    for cl in spec["success_clauses"]:
        pv, tv = ev(cl, pos), ev(cl, twn)
        att = holds(pv, cl["comparison"], cl["threshold"])
        dis = not holds(tv, cl["comparison"], cl["threshold"])
        clauses.append({"id": cl["id"], "statistic": cl["statistic"], "comparison": cl["comparison"],
                        "threshold": cl["threshold"], "positive_value": pv, "twin_value": tv,
                        "cheat_value": ev(cl, che), "attainable": bool(att), "discriminating": bool(dis),
                        "treatment_must_reach": must[cl["id"]]})
    fails = []
    for cl in spec["failure_clauses"]:
        pv, tv, cv = ev(cl, pos), ev(cl, twn), ev(cl, che)
        fails.append({"id": cl["id"], "statistic": cl["statistic"], "comparison": cl["comparison"],
                      "threshold": cl["threshold"], "positive_value": pv, "positive_fires": bool(holds(pv, cl["comparison"], cl["threshold"])),
                      "twin_value": tv, "twin_fires": bool(holds(tv, cl["comparison"], cl["threshold"])),
                      "cheat_value": cv, "cheat_fires": bool(holds(cv, cl["comparison"], cl["threshold"]))})
    cheat_ok = all(holds(c["cheat_value"], c["comparison"], c["threshold"]) for c in clauses) and \
        not any(f["cheat_fires"] for f in fails)
    frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_ok and \
        not any(f["positive_fires"] for f in fails)
    return {"world": "W6", "triplicateId": spec["triplicateId"], "clauses": clauses,
            "failure_clauses_on_controls": fails, "cheat_detected": bool(cheat_ok), "frozen": bool(frozen),
            "fixed_control_seed_mean_rif": fixed_mean,
            "pairing": {"positive": list(pos), "twin_in_arm_slot": list(twn), "cheat": list(che)},
            "revisions": REVISIONS}


def main():
    out = os.path.join(HERE, "control_rows.jsonl")
    t0 = time.process_time()
    ones = np.ones((N, N))
    with open(out, "w") as f:
        def emit(row):
            row.update({"world": "W6"})
            f.write(json.dumps(row) + "\n")
            f.flush()
        for s in SEEDS:
            ts = time.process_time()
            r0 = rng_for(s, 0)
            a = 1 + 0.01 * r0.standard_normal((N, N))
            h = 1 + 0.01 * r0.standard_normal((N, N))
            a_ref, h_ref = run(a, h, ones, ones, T_REF)
            mask = lesion_mask(s)
            aO, hO = run(a_ref, h_ref, ones, ones, T_SETTLE)
            al, hl = lesion(aO, hO, mask, s)
            aR, _ = run(al, hl, ones, ones, T_REGROW)
            emit({"seed": s, "arm": "FIXED", **score(aO, aR, mask)})
            gh, gv = carve(a_ref)
            aO, hO = run(a_ref, h_ref, gh, gv, T_SETTLE)
            al, hl = lesion(aO, hO, mask, s)
            aR, _ = run(al, hl, gh, gv, T_REGROW)
            emit({"seed": s, "arm": "POSITIVE_CONTROL", **score(aO, aR, mask),
                  "frac_cut_edges": float(((gh < 1).sum() + (gv < 1).sum()) / (2 * N * N))})
            gh2, gv2 = scramble_inside(gh, gv, mask, s, 3)
            aT, _ = run(al, hl, gh2, gv2, T_REGROW)
            emit({"seed": s, "arm": "NULL_TWIN", **score(aO, aT, mask)})
            gh3, gv3 = scramble_inside(gh, gv, mask, s, 4)
            aT2, _ = run(al, hl, gh3, gv3, T_REGROW)
            emit({"seed": s, "arm": "NULL_TWIN_B", **score(aO, aT2, mask)})
            aC = aT.copy()
            aC[mask] = aO[mask]
            emit({"seed": s, "arm": "CHEAT", **score(aO, aC, mask), "cpu_s_seed": time.process_time() - ts})
    cpu = time.process_time() - t0
    rows = [json.loads(l) for l in open(out)]
    spec = json.load(open(os.path.join(HERE, "spec.json")))
    att = attainability(rows, spec)
    att["control_cpu_s_final_run"] = cpu
    with open(os.path.join(HERE, "ATTAINABILITY.json"), "w") as f:
        json.dump(att, f, indent=1)
    print("cpu_s_total", cpu, "frozen", att["frozen"], file=sys.stderr)
    for c in att["clauses"]:
        print(c["id"], round(c["positive_value"], 3), round(c["twin_value"], 3), c["attainable"], c["discriminating"], file=sys.stderr)


if __name__ == "__main__":
    main()
