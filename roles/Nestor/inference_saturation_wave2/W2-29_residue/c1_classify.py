"""W2-29 c1: genotype classification of every recorded lineage genome in genomes_*.jsonl (separate process from the sims).
side-0 morph := conv_side0 >= 0.5 and conv_side1 < 0.5 on a fixed 16-partner bank panel (common.outcome, donor ZERO ctx,
partner bank regs, copy errors off). CONFIRMED := also the first LDIR run by side 0's own context, with g at side 0
(W2-24 tvm.pair_t, partner = panel[0]), has DE (dst) == 0x40. Controls: founder (neg), 44->AC, 49->5C (pos).
python -B c1_classify.py TAG [TAG...] -> c1_classes.json  (cached by genome hex)"""
import json, pickle, random, sys, pathlib, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
sys.path.insert(0, str(HERE.parent / "W2-24_keep_variant"))
import common as C
import tvm
banks = pickle.load(open(HERE.parent / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
r = C.runner_for_spec(C.run_ds.DONOR)
rng = random.Random("W2-29")
PAN = []
for _ in range(16):
    ep = rng.randrange(10, 300)
    PAN.append(banks[ep][rng.randrange(len(banks[ep]))])


def classify(g):
    c0 = c1 = 0
    for y, cy in PAN:
        c0 += C.outcome(r, g, y, 0, C.ZERO, cy)["conv"]
        c1 += C.outcome(r, g, y, 1, C.ZERO, cy)["conv"]
    out = {"c0": c0 / 16, "c1": c1 / 16}
    out["side0"] = out["c0"] >= 0.5 and out["c1"] < 0.5
    out["de"] = None
    if out["side0"] or g in CTRL_SET:
        y, cy = PAN[0]
        ld = tvm.pair_t(r, g, y, C.ZERO, cy)[6]
        own = [x for x in ld if x[0] == 0]
        out["de"] = own[0][3] if own else None
    out["confirmed"] = bool(out["side0"] and out["de"] == 0x40)
    return out


Fg = C.run_ds.donor_genome()
CTRL = {"founder": Fg}
for name, p, v in (("44-ac", 44, 0xAC), ("49-5c", 49, 0x5C), ("43-c3", 43, 0xC3)):
    g = bytearray(Fg); g[p] = v; CTRL[name] = bytes(g)
CTRL_SET = set(CTRL.values())

if __name__ == "__main__":
    t0 = time.process_time()
    path = HERE / "c1_classes.json"
    cache = json.load(open(path)) if path.exists() else {}
    ctrl = {k: classify(g) for k, g in CTRL.items()}
    print("controls", ctrl, flush=True)
    todo = set()
    for tag in sys.argv[1:]:
        for l in open(HERE / ("genomes_%s.jsonl" % tag)):
            d = json.loads(l)
            todo.add(d["founder"])
            todo.update(x[0] for x in d["genomes"])
    todo -= set(cache)
    print("to classify", len(todo), flush=True)
    for k, h in enumerate(sorted(todo)):
        cache[h] = classify(bytes.fromhex(h))
    json.dump({"controls": ctrl, "founder_hex": Fg.hex(), "cpu_s": round(time.process_time() - t0, 1)},
              open(HERE / "c1_controls.json", "w"), indent=1)
    json.dump(cache, open(path, "w"))
    print("done", len(cache), "cpu %.1f" % (time.process_time() - t0))
