"""W2-39 FROZEN K2 decision procedure (see FROZEN_PREDICTIONS.md). Usage after a world experiment:
  python -B k2_decide.py world_counts.json
world_counts.json = {"GENO": {"n": seeds, "k27": #runs B_xk>=27 by epoch 300, "k163": #runs B_xk>=163 by epoch 300,
                     "kB27": #runs B>=27 (founder control only)}, ...}   GENO in F, AC, 81, C3, C3+AC.
M* counts are read from a1_results.json (W2-39 fresh seeds 39_390_000+0..799), never re-estimated.
Bands: R1 hull = [k_lo(R1, C-), k_hi(R1_Cplus)];  R3 hull = [k_lo(R3_Cminus), k_hi(R3_Cplus)] at the world's realized m=k27.
A readout is OUTSIDE iff the world count is below the hull's low end or above its high end (least favourable to a kill)."""
import json, sys, pathlib
import band as BD
HERE = pathlib.Path(__file__).resolve().parent


def hull(est, N, m27, key_lo, key_hi, n):
    lo = BD.band(est[key_lo]["x"], est[key_lo]["n"], n)["k_lo"]
    hi = BD.band(est[key_hi]["x"], est[key_hi]["n"], n)["k_hi"]
    return lo, hi


def decide(world, mstar):
    out = {}
    f = world.get("F")
    ctrl = None
    if f is not None:
        b = BD.band(4, 128, f["n"])                     # world's historical founder 4/128 on B>=27
        ctrl = b["k_lo"] <= f["kB27"] <= b["k_hi"]
        out["positive_control"] = {"band_B27": [b["k_lo"], b["k_hi"]], "kB27": f["kB27"], "PASS": ctrl}
    for g, w in world.items():
        est = mstar[g]["estimates"]
        r1 = hull(est, None, None, "R1", "R1_Cplus", w["n"])
        r1_out = not (r1[0] <= w["k27"] <= r1[1])
        if w["k27"] == 0:
            r3, r3_out = None, False                    # R3 NOT SCORED
        else:
            r3 = hull(est, None, None, "R3_Cminus", "R3_Cplus", w["k27"])
            r3_out = not (r3[0] <= w["k163"] <= r3[1])
        v = "OUTSIDE" if (r1_out or r3_out) else "INSIDE"
        out[g] = {"R1_hull": r1, "R1_out": r1_out, "R3_hull": r3, "R3_out": r3_out, "band_verdict": v}
    morphs = [g for g in world if g != "F"]
    if ctrl is False:
        out["K2"] = "VOID (positive control failed)"
    elif any(out[g]["band_verdict"] == "OUTSIDE" for g in morphs):
        out["K2"] = "KILLED" + (" (founder arm also OUTSIDE: not morph-specific)" if out.get("F", {}).get(
            "band_verdict") == "OUTSIDE" else "")
    else:
        out["K2"] = "CONSISTENT" if ctrl is None else "PASSED-AT-BAND (no morph arm outside)"
    return out


if __name__ == "__main__":
    mstar = json.load(open(HERE / "a1_results.json"))["genotypes"]
    print(json.dumps(decide(json.load(open(sys.argv[1])), mstar), indent=1))
