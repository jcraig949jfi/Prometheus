"""Certify the COMBINE candidates of one R3 search unit (cap CAP, in discovery order). Writes <unit>_cert.json."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import r3_certify as C  # noqa: E402
CAP = 10
def main():
    unit, out = sys.argv[1], sys.argv[2]
    if os.path.exists(out):
        return 0
    u = json.load(open(unit))
    import r3_frontier as F
    F.set_geom(u.get("geom", "R3"))
    res = {"schema": "aether.reach01.r3.cert.v1", "unit": os.path.basename(unit), "arm": u["arm"], "op": u["op"],
           "seed": u["seed"], "certified": []}
    if u.get("combine_npz"):
        z = np.load(os.path.join(os.path.dirname(unit), u["combine_npz"]))
        for i in range(min(CAP, len(z["patches"]))):
            c = C.certify(z["patches"][i], u["op"])
            c = {k: (v if k not in ("Na", "Nb") else [list(x) for x in v]) for k, v in c.items()}
            c.update(hash=str(z["hashes"][i]), found_at_eval=int(z["evals"][i]))
            res["certified"].append(c)
    json.dump(res, open(out, "w"), indent=1)
    return 0
if __name__ == "__main__":
    sys.exit(main())
