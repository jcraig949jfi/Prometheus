"""PKG-F v6 control: the same partial-switch worlds (pkgf_partial.world), but the substrate is the F2_latent-selected
SELECTIVE arm (tuned on stationary worlds) instead of the F3-selected one. rho in {1, .5, .1, 0}; FRESH seeds
9_800_050-053, the same worlds as v6. The script writes results/pkgf_partial_ctrl.json itself."""
import json, os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.arc3.pkgf_partial import one

if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)
    t0 = time.time(); rows = []
    for rho in (1.0, 0.5, 0.1, 0.0):
        for g in ("cp", "tt"):
            for sd in range(9_800_050, 9_800_054):
                r = one(g, sd, rho, sub_family="F2_latent"); rows.append(r)
                print(rho, g, sd, "cp_frac", r["cp_frac"], "dAC", {k: round(v - r["AC"]["S"], 3) for k, v in r["AC"].items() if k != "S"}, flush=True)
    here = os.path.dirname(__file__)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(here, "results", "pkgf_partial_ctrl.json"), "w"), indent=1)
    print("wall", round(time.time() - t0, 1))
