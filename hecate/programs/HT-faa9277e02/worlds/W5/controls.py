"""W5 controls: POSITIVE_CONTROL, CHEAT, NULL_TWIN (no treatment code).

Frozen parameters are those of spec.json. No waves and no STDP are simulated
here; couplings are constructed directly and only the shared read-out (the
polarity index and the pulse-transport test) is run.

World: 48x48 torus; edge e from cell i to its +x (horizontal) or +y (vertical)
neighbour j has rates r_{i->j} = D0*g_e*(1+eps_e), r_{j->i} = D0*g_e*(1-eps_e).
  da_i/dt = sum_j r_{j->i} a_j - sum_j r_{i->j} a_i      (mass conserving)
Observables per seed:
  P = sum A_e / sum |A_e| over horizontal edges, A_e = 2*D0*g_e*eps_e
  B = mean over 16 released pulses of mass(d>0) - mass(d<0) at t_test = 8,
      d = signed torus x-offset from the release column, in [-24, 23].
Arms:
  POSITIVE_CONTROL: eps_h ~ N(0.2, 0.1) clipped [-0.9, 0.9], eps_v = 0.
  NULL_TWIN: twin operator on the positive-control couplings: independent
      fair random sign on every eps (stream 2); g and |eps| unchanged.
  NULL_TWIN_B: second independent twin draw (stream 4); used only to put a
      twin in the arm slot of the relative clauses S3, S4.
  CHEAT: twin couplings, observables overwritten: A_e := |A_e| (P = 1) and
      the pulse mass at d < 0 mirrored onto d > 0.
  FLAT (instrument baseline, clause F3): eps = 0, same g.
  POSITIVE_CONTROL_REVERSED (F4 reference): positive-control eps negated,
      i.e. what a correctly written arrow looks like under reversed waves.
  CALIBRATION (diagnostic, seeds 0-4): eps_h ~ N(m, m/2) for m in
      {0.025, 0.05, 0.1}: B as a function of arrow strength.
Rows -> control_rows.jsonl (flushed per row); then ATTAINABILITY.json.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 48
D0 = 1.0
G_LOGSD = 0.3
PC_EPS_MEAN, PC_EPS_SD = 0.2, 0.1
EPS_CLIP = 0.9
DT = 0.02
T_TEST = 8.0
N_PULSE = 16
SEEDS = list(range(10))

REVISIONS = [
    {"rev": 0, "what": "first design: positive control eps_h ~ N(0.2,0.1); twin = random sign per edge; FLAT instrument check; CHEAT overwrites P and mirrors pulse mass; clauses not yet numbered",
     "result": "PC P 0.992, B 0.563; twin P 0.007, B -0.008; FLAT B -0.0004; CHEAT P 1, B 0.897",
     "why_changed": "relative clauses need a twin value in the arm slot; treatment_must_reach needs B as a function of eps"},
    {"rev": 1, "what": "added NULL_TWIN_B (second sign draw) and CALIBRATION rows (eps mean 0.025/0.05/0.1 -> B 0.076/0.153/0.301)",
     "result": "thresholds set: S1 P>=0.5, S2 B>=0.15 (= eps mean about 0.05), S3 B-twin>=0.10, S4 >=9/10 seeds",
     "why_changed": "freeze"},
    {"rev": 2, "what": "spec control changed from a 'timing-symmetric Hebb' arm (algebraically eps == 0, cannot fail, so useless as a check) to a reversed-wave control that must flip the arrow (F4: seed-mean P > -0.2 fires); added POSITIVE_CONTROL_REVERSED rows as the F4 reference; evaluator added",
     "result": "see clauses", "why_changed": "a guard that cannot fire is not a guard"},
]


def rng_for(seed, stream):
    return np.random.default_rng(np.random.SeedSequence([20260930, 5, seed, stream]))


def sym_part(seed):
    r = rng_for(seed, 0)
    gh = np.exp(G_LOGSD * r.standard_normal((N, N)))
    gv = np.exp(G_LOGSD * r.standard_normal((N, N)))
    m = (gh.sum() + gv.sum()) / (2 * N * N)
    return gh / m, gv / m


def positive_eps(seed):
    r = rng_for(seed, 1)
    eh = np.clip(PC_EPS_MEAN + PC_EPS_SD * r.standard_normal((N, N)), -EPS_CLIP, EPS_CLIP)
    return eh, np.zeros((N, N))


def twin_op(eh, ev, seed, stream=2):
    """NULL_TWIN operator: independent fair random sign per edge; g, |eps| kept."""
    r = rng_for(seed, stream)
    return r.choice([-1.0, 1.0], size=eh.shape) * np.abs(eh), r.choice([-1.0, 1.0], size=ev.shape) * np.abs(ev)


def polarity(g, e):
    A = 2 * D0 * g * e
    s = np.abs(A).sum()
    return float(A.sum() / s) if s > 0 else 0.0


def release_sites(seed):
    r = rng_for(seed, 3)
    idx = r.choice(N * N, size=N_PULSE, replace=False)
    return np.stack([idx // N, idx % N], axis=1)  # (y, x)


def run_pulses(gh, gv, eh, ev, sites):
    """Array index [y, x]. gh[y,x]: edge (y,x)->(y,x+1); gv[y,x]: edge (y,x)->(y+1,x)."""
    rf_h, rb_h = D0 * gh * (1 + eh), D0 * gh * (1 - eh)
    rf_v, rb_v = D0 * gv * (1 + ev), D0 * gv * (1 - ev)
    out_rate = rf_h + np.roll(rb_h, 1, axis=1) + rf_v + np.roll(rb_v, 1, axis=0)
    a = np.zeros((len(sites), N, N))
    for k, (y, x) in enumerate(sites):
        a[k, y, x] = 1.0
    for _ in range(int(round(T_TEST / DT))):
        inflow = np.roll(rf_h[None] * a, 1, axis=2)          # from (y,x-1) forward
        inflow += rb_h[None] * np.roll(a, -1, axis=2)       # from (y,x+1) backward
        inflow += np.roll(rf_v[None] * a, 1, axis=1)        # from (y-1,x) forward
        inflow += rb_v[None] * np.roll(a, -1, axis=1)       # from (y+1,x) backward
        a = a + DT * (inflow - out_rate[None] * a)
    return a


def bias(a, sites, mirror=False):
    xs = np.arange(N)
    bs, disp = [], []
    for k, (_, x0) in enumerate(sites):
        d = ((xs - x0 + N // 2) % N) - N // 2
        col = a[k].sum(axis=0).copy()
        if mirror:  # CHEAT: move upstream mass to the mirror-image downstream column
            for i in np.where(d < 0)[0]:
                if -d[i] <= N // 2 - 1:
                    col[(x0 - d[i]) % N] += col[i]
                    col[i] = 0.0
        tot = col.sum()
        bs.append((col[d > 0].sum() - col[d < 0].sum()) / tot)
        disp.append((col * d).sum() / tot)
    return float(np.mean(bs)), float(np.mean(disp)), float(a.sum() / len(sites))


# ---------------- evaluator (shared with the later probe) ----------------
def by_arm(rows):
    d = {}
    for r in rows:
        if r["arm"] == "CALIBRATION":
            continue
        d.setdefault(r["arm"], {})[r["seed"]] = r
    return d


def statistic(name, arm, twin, flat, control):
    seeds = sorted(arm)
    if name == "seed_mean_P":
        return float(np.mean([arm[s]["P"] for s in seeds]))
    if name == "seed_mean_B":
        return float(np.mean([arm[s]["B"] for s in seeds]))
    if name == "seed_mean_B_minus_twin":
        return float(np.mean([arm[s]["B"] - twin[s]["B"] for s in seeds]))
    if name == "n_seeds_B_above_twin":
        return int(sum(arm[s]["B"] > twin[s]["B"] for s in seeds))
    if name == "abs_seed_mean_B_flat":
        return float(abs(np.mean([flat[s]["B"] for s in sorted(flat)])))
    if name == "seed_mean_P_control":
        return float(np.mean([control[s]["P"] for s in sorted(control)]))
    raise KeyError(name)


def holds(v, cmp, thr):
    return {">=": v >= thr, ">": v > thr, "<": v < thr, "<=": v <= thr}[cmp]


def attainability(rows, spec):
    A = by_arm(rows)
    flat, ctrl = A["FLAT"], A["POSITIVE_CONTROL_REVERSED"]
    pairs = {"positive": ("POSITIVE_CONTROL", "NULL_TWIN"), "twin": ("NULL_TWIN", "NULL_TWIN_B"),
             "cheat": ("CHEAT", "NULL_TWIN")}
    ev = lambda cl, k: statistic(cl["statistic"], A[pairs[k][0]], A[pairs[k][1]], flat, ctrl)
    must = {
        "S1": "treatment seed-mean P >= 0.5 (fraction of arrow magnitude pointing downstream net of upstream)",
        "S2": "treatment seed-mean B >= 0.15; by CALIBRATION this needs a downstream-uniform eps of mean about 0.05 (eps 0.025 -> B 0.076, 0.05 -> 0.153, 0.1 -> 0.301)",
        "S3": "treatment B >= its own twin B + 0.10 (twin of the positive control has seed-mean B %.3f, so about %.2f)",
        "S4": "treatment B above its own twin B in >= 9 of 10 seeds",
    }
    twin_B = statistic("seed_mean_B", A["NULL_TWIN"], None, flat, ctrl)
    must["S3"] = must["S3"] % (twin_B, twin_B + 0.10)
    clauses = []
    for cl in spec["success_clauses"]:
        pv, tv = ev(cl, "positive"), ev(cl, "twin")
        clauses.append({"id": cl["id"], "statistic": cl["statistic"], "comparison": cl["comparison"],
                        "threshold": cl["threshold"], "positive_value": pv, "twin_value": tv,
                        "cheat_value": ev(cl, "cheat"),
                        "attainable": bool(holds(pv, cl["comparison"], cl["threshold"])),
                        "discriminating": bool(not holds(tv, cl["comparison"], cl["threshold"])),
                        "treatment_must_reach": must[cl["id"]]})
    fails = []
    for cl in spec["failure_clauses"]:
        pv, tv, cv = ev(cl, "positive"), ev(cl, "twin"), ev(cl, "cheat")
        note = None
        if cl["statistic"] == "seed_mean_P_control":
            note = "control-arm statistic: value here is from POSITIVE_CONTROL_REVERSED (a correctly written arrow under reversed waves); same for all pairings; the real control arm exists only in the probe"
        if cl["statistic"] == "abs_seed_mean_B_flat":
            note = "instrument statistic from FLAT rows; same for all pairings"
        fails.append({"id": cl["id"], "statistic": cl["statistic"], "comparison": cl["comparison"],
                      "threshold": cl["threshold"], "positive_value": pv,
                      "positive_fires": bool(holds(pv, cl["comparison"], cl["threshold"])),
                      "twin_value": tv, "twin_fires": bool(holds(tv, cl["comparison"], cl["threshold"])),
                      "cheat_value": cv, "cheat_fires": bool(holds(cv, cl["comparison"], cl["threshold"])),
                      "note": note})
    cheat_ok = all(holds(c["cheat_value"], c["comparison"], c["threshold"]) for c in clauses) and \
        not any(f["cheat_fires"] for f in fails)
    frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_ok and \
        not any(f["positive_fires"] for f in fails)
    calib = {}
    for r in rows:
        if r["arm"] == "CALIBRATION":
            calib.setdefault(str(r["eps_mean"]), []).append(r["B"])
    return {"world": "W5", "triplicateId": spec["triplicateId"], "clauses": clauses,
            "failure_clauses_on_controls": fails, "cheat_detected": bool(cheat_ok), "frozen": bool(frozen),
            "calibration_B_by_eps_mean": {k: float(np.mean(v)) for k, v in calib.items()},
            "pairing": {k: list(v) for k, v in pairs.items()}, "revisions": REVISIONS}


def main():
    out = os.path.join(HERE, "control_rows.jsonl")
    t0 = time.process_time()
    with open(out, "w") as f:
        def emit(row):
            row["world"] = "W5"
            f.write(json.dumps(row) + "\n")
            f.flush()

        def arm_row(s, arm, gh, gv, e1, e2, sites, **extra):
            ts = time.process_time()
            a = run_pulses(gh, gv, e1, e2, sites)
            B, disp, mass = bias(a, sites)
            emit({"seed": s, "arm": arm, "P": polarity(gh, e1), "P_perp": polarity(gv, e2), "B": B,
                  "mean_disp": disp, "mass_per_pulse": mass, "mean_abs_eps_h": float(np.abs(e1).mean()),
                  "cpu_s": time.process_time() - ts, **extra})
            return a

        for s in SEEDS:
            gh, gv = sym_part(s)
            sites = release_sites(s)
            eh, ev = positive_eps(s)
            th, tv = twin_op(eh, ev, s, 2)
            t2h, t2v = twin_op(eh, ev, s, 4)
            z = np.zeros_like(eh)
            arm_row(s, "POSITIVE_CONTROL", gh, gv, eh, ev, sites)
            a_twin = arm_row(s, "NULL_TWIN", gh, gv, th, tv, sites)
            arm_row(s, "NULL_TWIN_B", gh, gv, t2h, t2v, sites)
            arm_row(s, "FLAT", gh, gv, z, z, sites)
            arm_row(s, "POSITIVE_CONTROL_REVERSED", gh, gv, -eh, -ev, sites)
            Bc, dc, mc = bias(a_twin, sites, mirror=True)
            emit({"seed": s, "arm": "CHEAT", "P": polarity(gh, np.abs(th)), "P_perp": polarity(gv, tv),
                  "B": Bc, "mean_disp": dc, "mass_per_pulse": mc, "cpu_s": 0.0})
            if s < 5:
                for lvl in (0.025, 0.05, 0.1):
                    r = rng_for(s, 5)
                    ch = np.clip(lvl + (lvl / 2) * r.standard_normal((N, N)), -EPS_CLIP, EPS_CLIP)
                    arm_row(s, "CALIBRATION", gh, gv, ch, z, sites, eps_mean=lvl)
    cpu = time.process_time() - t0
    rows = [json.loads(l) for l in open(out)]
    spec = json.load(open(os.path.join(HERE, "spec.json")))
    att = attainability(rows, spec)
    att["control_cpu_s_final_run"] = cpu
    with open(os.path.join(HERE, "ATTAINABILITY.json"), "w") as f:
        json.dump(att, f, indent=1)
    print("cpu_s_total", cpu, "frozen", att["frozen"], "cheat", att["cheat_detected"], file=sys.stderr)
    for c in att["clauses"]:
        print(c["id"], round(c["positive_value"], 3), round(c["twin_value"], 3), round(c["cheat_value"], 3),
              c["attainable"], c["discriminating"], file=sys.stderr)
    for c in att["failure_clauses_on_controls"]:
        print(c["id"], round(c["positive_value"], 3), c["positive_fires"], c["cheat_fires"], file=sys.stderr)


if __name__ == "__main__":
    main()
