"""Per-carrier-screen hazard (model M1's lambda) in the NEUTRAL pilot vs the soup on the same seeds.
Computational artificial life; nothing biological. Output neutral_lambda.json."""
import glob, json
import acc_lib as A
SOUP = {"DENSE": A.W1 / "x_dd_dense_copy" / "results" / "DENSE_COPY_{c}_{s}.json",
        "PLANT": A.P2 / "x_p2_plant" / "results" / "{c}_{s}.json",
        "PLAIN": A.W1 / "x_dd_dense_copy" / "results" / "PLAIN_{c}_{s}.json"}
MAP = {"DENSE": ("RANDOM", "DENSE"), "PLANT": ("PLANT", "STOCK"), "PLAIN": ("RANDOM", "STOCK")}
def ex(cps):
    E = 0
    for c in sorted(cps, key=lambda c: c["epoch"]):
        E += c["L1c"]
        if c["L2"] > 0:
            return 1, E
    return 0, E
out = {}
for arm, (mat, vm) in MAP.items():
    n_ev = n_E = s_ev = s_E = 0
    for f in glob.glob(str(A.HERE / "results_neutral" / (mat + "_*.json"))):
        x = json.load(open(f))
        e, E = ex(x["arms"][vm]); n_ev += e; n_E += E
        sp = json.load(open(str(SOUP[arm]).format(c=x["cell"], s=x["seed"])))["checkpoints"]
        e, E = ex(sp); s_ev += e; s_E += E
    out[arm] = {"neutral": {"events": n_ev, "carrier_exposure": n_E, "lambda": n_ev / n_E if n_E else None},
                "soup_same_seeds": {"events": s_ev, "carrier_exposure": s_E, "lambda": s_ev / s_E if s_E else None}}
(A.HERE / "neutral_lambda.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
