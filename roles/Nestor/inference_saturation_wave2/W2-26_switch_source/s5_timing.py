"""W2-26 s5: morph timing vs the burst, all 23 s1 replays (12 runaways, 11 controls) + optional XTKU seeds.
Per run, in birth order (epoch, then oid):
  e27_fam / e27_all  epoch of the 27th causal birth in the founder family (child anc 0) / anywhere
  e_d20              epoch at which the world's causal depth first reaches 20 (exact, from the birth log)
  first S0 edge      first causal birth with parent at side 0 (any genotype; family only)
  first morph        first causal birth with parent at side 0 whose parent genome is a STATIC side-0 converter
                     (conv0 >= 0.5, common.outcome, BASE bank panel N = 100), split:
                       M7  parent 7ae3-family (>= 51/64 implant bytes at shift 0)
                       MA  any genotype
                     each with the family / world causal-birth count before it.
python -B s5_timing.py [extra labels] -> s5_timing.json"""
import json, pathlib, pickle, random, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
sys.path.insert(0, str(HERE.parent / "W2-17_runaway_departure"))
import common as C  # noqa: E402
from r2_replay import RUNS  # noqa: E402

N = 100
banks = pickle.load(open(HERE.parent / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
r = C.runner_for_spec(C.run_ds.DONOR)
IMP = C.run_ds.donor_genome()
rng = random.Random("W2-26-s5")
PAN = []
for _ in range(N):
    ep = rng.randrange(10, 300)
    PAN.append(banks[ep][rng.randrange(len(banks[ep]))])
CACHE = {}


def conv0(g):
    if g not in CACHE:
        CACHE[g] = sum(C.outcome(r, g, y, 0, C.ZERO, cy, 0.0, None)["conv"] for y, cy in PAN) / N
    return CACHE[g]


def main(labels):
    out = {}
    for label in labels:
        d = json.loads((HERE / "s1_out" / (label + ".json")).read_text())
        B = sorted(((v["e"], int(k), v) for k, v in d["births"].items() if v["c"]))
        dep = {}
        nfam = nall = 0
        o = {"label": label, "rec_depth": d["recorded_final_depth"], "stop": d["epochs_replayed"],
             "e27_fam": None, "e27_all": None, "e_d20": None, "S0_any": None, "S0_fam": None,
             "M7": None, "MA": None, "M7_fam": None, "MA_fam": None}
        for e, k, v in B:
            dep[k] = dep.get(v["p"], 0) + 1
            fam = v["anc"] == 0
            snap = {"e": e, "n_fam_before": nfam, "n_all_before": nall, "k": k}
            if v["pside"] == 0:
                if o["S0_any"] is None:
                    o["S0_any"] = snap
                if fam and o["S0_fam"] is None:
                    o["S0_fam"] = snap
                need = [x for x in ("M7", "MA", "M7_fam", "MA_fam") if o[x] is None and (fam or not x.endswith("fam"))]
                if need:
                    g = bytes.fromhex(v["dg"])
                    c = conv0(g)
                    if c >= 0.5:
                        is7 = sum(a == b for a, b in zip(g, IMP)) >= 51
                        for x in need:
                            if x.startswith("MA") or is7:
                                o[x] = dict(snap, conv0=c, f0=sum(a == b for a, b in zip(g, IMP)))
            nall += 1
            nfam += fam
            if nfam == 27 and o["e27_fam"] is None:
                o["e27_fam"] = e
            if nall == 27 and o["e27_all"] is None:
                o["e27_all"] = e
            if dep[k] >= 20 and o["e_d20"] is None:
                o["e_d20"] = e
        o["n_fam_total"], o["n_all_total"] = nfam, nall
        out[label] = o
        f = lambda x: "-" if x is None else "e%d/f%d" % (x["e"], x["n_fam_before"])
        print(label, "e27f", o["e27_fam"], "e27a", o["e27_all"], "d20", o["e_d20"], "S0any", f(o["S0_any"]),
              "S0fam", f(o["S0_fam"]), "M7", f(o["M7"]), "MA", f(o["MA"]), "M7fam", f(o["M7_fam"]), "MAfam", f(o["MA_fam"]),
              flush=True)
    (HERE / "s5_timing.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(list(RUNS) + sys.argv[1:])
