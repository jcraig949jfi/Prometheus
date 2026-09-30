"""PKG-F v9b: v9 with a STRICTER veto (alpha = .01), precommitted after v9's Z1 miss. Worlds are INDEPENDENT: 8
distinct fresh seeds 9_800_090-097 per world type, generator alternating cp/tt by seed, so no two worlds share a walk.
DETECTION ONLY on N5 / F3 / F2 twins / partial rho = .5. The script writes results/pkgf_cp5b.json itself."""
import json, os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.arc3.pkgf_cp5 import last_regime_start
from ensorain.arc3.pkgf_cp4 import stream

if __name__ == "__main__":
    t0 = time.time(); rows = []
    for kind in ("N5", "F3", "F2", "PARTIAL.5"):
        for sd in range(9_800_090, 9_800_098):
            g = "cp" if sd % 2 == 0 else "tt"
            A, y = stream(kind, sd, g); st = last_regime_start(A, y, sd, alpha=0.01)
            rows.append(dict(kind=kind, gen=g, seed=sd, cp_frac=round(st / len(y), 3)))
            print(kind, g, sd, "cp_frac", rows[-1]["cp_frac"], "%.0fs" % (time.time() - t0), flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), alpha_veto=0.01, rows=rows), open(os.path.join(os.path.dirname(__file__), "results", "pkgf_cp5b.json"), "w"), indent=1)
    for kind in ("N5", "F3", "F2", "PARTIAL.5"):
        v = [r["cp_frac"] for r in rows if r["kind"] == kind]
        print(kind, "detected", sum(x > 0 for x in v), "/", len(v), "in [.6,.75]:", sum(.6 <= x <= .75 for x in v), v)
