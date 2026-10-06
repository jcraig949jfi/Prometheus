"""PTE-C2A admission (CPU only; no search). P / R / V per candidate, on 128 fresh worlds per candidate.

usage: python admit.py FAMILY START STOP OUTFILE

Candidates: the W2-AD seeded sampler (census.candidate: C1 A0 dial ranges + the C2 genome spec, economy off),
unchanged; these cells were never searched by C1. For each candidate:
  P  stratum (RELAY: every world >= 2 transport hops), reachability (no impossible world), and the joint ceiling
     (W2-AD w2ad_ceil.joint_ceiling = min of lcwake/LC2k/epidemic/w2u/task2_timing bounds) >= threshold, with the
     ceiling computed on THE SAME worlds as the plant (so a plant above it is a bound violation, not a world draw).
     threshold: RELAY max(A90(.55, K), A90(.55, K/2)) + .05 (all trials and late half); FLIP max(.90, A90(.75)+.05).
  R  plant designs scored with the competence-class ruler (c2a_common.competence) + must-fail ablation
     (RELAY sensor_off; FLIP teacher_off) which must NOT be TRUE.
  V  adversaries (c2a_common.ADVERSARIES) must all be FALSE under the same ruler; an INDETERMINATE adversary
     fails V (conservative).
  ceiling violation: plant all-trials mean > ceiling + max(.01, 2.605 * pair SE)  -> STOP condition (s22).
"""
import os
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"       # admission is CPU work (operator order s20)
HERE = os.path.dirname(os.path.abspath(__file__))
W2 = os.path.join(HERE, "..", "..", "research", "harvest", "wave2")
for d in ("W2-AD", "W2-B", "W2-P", "W2-U", "W2-L", "W2-M", "W2-J"):
    sys.path.insert(0, os.path.join(W2, d))
import w2ad_common  # noqa: E402,F401  (sets CPU threads; asserts no GPU)
import census  # noqa: E402  (W2-AD sampler + thresholds; read-only)
import w2ad_ceil as WC  # noqa: E402
import attain as AT  # noqa: E402
sys.path.insert(0, HERE)
import c2a_common as C  # noqa: E402
import json  # noqa: E402
import numpy as np  # noqa: E402

ROLE = {"RELAY": "RELAY-mh", "FLIP": "FLIP"}
ABL = {"RELAY": C.sensor_off, "FLIP": C.teacher_off}


def thresholds(fam, env):
    K = census.K_scored(env)
    a90 = lambda thr, k: AT.min_true_to_cross(thr, C.P_ADMIT, k, "lo_gt", 0.9)
    if fam == "RELAY":
        return {"SIGNAL_all": a90(.55, K) + .05, "SIGNAL_late": a90(.55, K // 2) + .05}
    return {"B": max(0.90, a90(0.75, K) + 0.05)}


def admit_one(fam, i):
    t0 = time.time()
    c = census.candidate(fam, i)
    ph = C.Physics.from_dict(c["physics"]).validate()
    env = C.envs.EnvSpec(**c["env"])
    seeds = C.admit_seeds(fam, i)
    rc = WC.joint_ceiling(ph, env, seeds)
    th = thresholds(fam, env)
    h = rc["hops"]
    rec = {"cid": c["cid"], "i": i, "family": fam, "levels": c["levels"], "env_levels": c["env_levels"],
           "physics": c["physics"], "env": c["env"], "ceiling": rc["ceiling"], "binding": rc["binding"],
           "ceiling_components": rc["components"], "hops": h, "thresholds": th,
           "admit_seed_base": [C.C2A_NS, C.ADMIT_KEY, C.FAM_ID[fam], i]}
    rec["stratum_ok"] = (h["min_hops"] >= 2) if fam == "RELAY" else True
    rec["reach_ok"] = h["impossible_pairs"] == 0
    rec["ceil_ok"] = bool(rc["ceiling"] >= max(th.values()))
    rec["P_ok"] = bool(rec["stratum_ok"] and rec["reach_ok"] and rec["ceil_ok"])
    if not rec["P_ok"]:
        rec["verdict"] = "P-CAPPED" if (rec["stratum_ok"] and rec["reach_ok"]) else "OUT_OF_STRATUM"
        rec["wall_s"] = round(time.time() - t0, 2)
        return rec
    names, gens, edits = [], [], []
    for nm, fn in C.PLANTS[fam].items():
        g = fn(ph)
        names += [nm, nm + "|ablate"]; gens += [g, g]; edits += [None, ABL[fam]]
    for nm, fn in C.ADVERSARIES[fam].items():
        names.append("adv:" + nm); gens.append(fn(ph)); edits.append(None)
    pt, ep = C.eval_programs(ph, env, seeds, gens, device="cpu", edits=edits)
    res = {nm: C.competence(ROLE[fam], pt[k], ep) for k, nm in enumerate(names)}
    plants = {}
    for nm in C.PLANTS[fam]:
        r, a = res[nm], res[nm + "|ablate"]
        se = float(np.std(C.pairs_of(pt[names.index(nm)], ep.scored), ddof=1) / np.sqrt(C.P_ADMIT))
        viol = bool(r["all"]["mean"] > rc["ceiling"] + max(0.01, C.MARGIN_SE * se))
        plants[nm] = {"ruler": C.slim(r), "ablate": C.slim(a), "ablate_ok": a["status"] != "TRUE",
                      "pass": bool(r["status"] == "TRUE" and a["status"] != "TRUE"), "above_ceiling": viol,
                      "lines": C.nlines(gens[names.index(nm)])}
    advs = {nm[4:]: C.slim(res[nm]) for nm in names if nm.startswith("adv:")}
    if fam == "FLIP":                     # anti-copy = per-trial complement of the copy adversary
        k = names.index("adv:relay_latch_copy")
        b, chg, same = C.flip_B_pairs(pt[k], ep, anti=True)
        rr = C._r3(b, C.B_CUT)
        advs["anti_copy(analytic)"] = {"status": rr["decided"], "B": {"mean": rr["mean"], "lo99": rr["lo99"],
                                       "chg": chg, "same": same}}
    rec["plants"] = plants
    rec["adversaries"] = advs
    # latch_once is a once-per-episode latch only without decay: with decay_shift > 0 its negative latch decays
    # to 0 and re-arms, so it relays every trial (dev admission RELAY-0027: .78) -- a working relay, not a
    # property-free shortcut. Declared at Flight 1, before any search: V uses it only at decay_shift == 0.
    v_scope = {k: True for k in advs}
    if ph.decay_shift > 0 and "latch_once" in v_scope:
        v_scope["latch_once"] = False
    rec["V_scope"] = v_scope
    rec["V_ok"] = all(v["status"] == "FALSE" for k, v in advs.items() if v_scope[k])
    rec["violation"] = any(p["above_ceiling"] for p in plants.values())
    por = [nm for nm in C.PLANT_OF_RECORD_ELIGIBLE[fam] if plants[nm]["pass"]]
    rec["plant_of_record"] = por[0] if por else None
    rec["R_ok"] = rec["plant_of_record"] is not None
    if rec["violation"]:
        rec["verdict"] = "CEILING_VIOLATION"
    elif not rec["R_ok"]:
        rec["verdict"] = "R-NOT-ESTABLISHED"
    elif not rec["V_ok"]:
        rec["verdict"] = "V-FAILED"
    else:
        rec["verdict"] = "ADMITTED"
    rec["wall_s"] = round(time.time() - t0, 2)
    return rec


if __name__ == "__main__":
    fam, a, b, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    have = set()
    if os.path.exists(out):
        have = {json.loads(l)["i"] for l in open(out) if l.strip()}
    with open(out, "a") as fh:
        for i in range(a, b):
            if i in have:
                continue
            r = admit_one(fam, i)
            fh.write(json.dumps(r, default=C._jd) + "\n"); fh.flush()
            print(r["cid"], r["verdict"], round(r["ceiling"], 3), r.get("plant_of_record"), r["wall_s"], flush=True)
