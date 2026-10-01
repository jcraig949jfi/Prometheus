"""W2-41 a4: realized (in-world) behaviour of the 7ae3 family vs the static profile, and a per-interaction
context swap. For every recorded interaction of a 7ae3-family organism (r1_out rows: pre-genome, carried context,
ACTUAL partner genome + partner carried context, side), re-run it statically (copy errors off) with
  (i) the actual carried context, (ii) ZERO, (iii) a BANK context (N17e-style draw),
and record conv (FID>=0.9 partner half), conv_prom (p11-promoted, = world credit), keep (FID). Compare with the
world's own outcome (births credited, keep). Genome classes: EXACT founder; MORPH = family genome that is a static
side-0 converter (ZERO ctx, 40 bank partners, conv0 >= 0.5); C3/AC/5C/C3+AC by bytes 43/44/49; OTHER family.
python -B a4_inworld.py -> a4_inworld.json"""
import gzip, json, pathlib, pickle, random, sys, time, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
sys.path.insert(0, str(W / "W2-24_keep_variant"))
from q1_trace import panel  # noqa: E402
from tvm import C  # noqa: E402

CTL = {"CNR_s4", "XH2N_s9", "XTK_14", "CRW_35", "CRW_47", "CRW_71", "CRW_79", "CRW_107", "CRW_66", "CRW_91", "CRW_85"}
r = C.runner_for_spec(C.run_ds.DONOR)
F = C.run_ds.donor_genome()
pan40 = panel()[:40]
banks = pickle.load(open(W / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
rng = random.Random("W2-41a4")
SC = {}


def static_c0(g):
    if g not in SC:
        SC[g] = sum(C.outcome(r, g, y, 0, C.ZERO, cy, 0.0, None)["conv"] for y, cy, _c, _s in pan40) / 40
    return SC[g]


def gclass(g):
    if g == F:
        return "EXACT_F"
    tag = []
    if g[43] == 0xC3:
        tag.append("C3")
    if g[44] == 0xAC:
        tag.append("AC")
    if g[49] == 0x5C:
        tag.append("5C")
    if static_c0(g) >= 0.5:
        return "MORPH_s0conv" + ("(" + "+".join(tag) + ")" if tag else "")
    return "OTHER_fam" + ("(" + "+".join(tag) + ")" if tag else "")


def main():
    c0 = time.process_time()
    agg = collections.defaultdict(lambda: collections.Counter())
    flips = []
    for p in sorted((HERE / "r1_out").glob("*.json.gz")):
        d = json.load(gzip.open(p, "rt"))
        grp = "CTL" if d["label"] in CTL else "RUN"
        for e, oid, born, side, gi, regs, fz, fc, pgi, pregs, pfz, pfc, nb, ncb, keep in d["rows"]:
            g, y = bytes.fromhex(d["genomes"][gi]), bytes.fromhex(d["genomes"][pgi])
            act, cy = (regs, bool(fz), bool(fc)), (pregs, bool(pfz), bool(pfc))
            ep = rng.randrange(10, 300)
            bx = banks[ep][rng.randrange(len(banks[ep]))][1]
            oa = C.outcome(r, g, y, side, act, cy, 0.0, None)
            oz = C.outcome(r, g, y, side, C.ZERO, cy, 0.0, None)
            ob = C.outcome(r, g, y, side, bx, cy, 0.0, None)
            cl = gclass(g)
            for key in ((grp, cl, side), ("ALL", cl, side), (grp, "FAMILY", side), ("ALL", "FAMILY", side)):
                a = agg[key]
                a["n"] += 1
                a["world_birth"] += nb > 0
                a["world_cbirth"] += ncb > 0
                a["world_keep"] += keep
                for tag, o in (("act", oa), ("zero", oz), ("bank", ob)):
                    a[tag + "_conv"] += o["conv"]
                    a[tag + "_convprom"] += o["conv_prom"]
                    a[tag + "_keep"] += o["keep"]
                a["act_ne_zero_conv"] += oa["conv"] != oz["conv"]
                a["act_ne_zero_keep"] += oa["keep"] != oz["keep"]
            if oa["conv"] != oz["conv"] and len(flips) < 60:
                flips.append({"run": d["label"], "e": e, "side": side, "class": cl,
                              "ndiff_vs_F": sum(a != b for a, b in zip(g, F)), "ctx": [regs, fz, fc],
                              "conv_act": oa["conv"], "conv_zero": oz["conv"],
                              "diff": {j: "%02x>%02x" % (F[j], g[j]) for j in range(64) if g[j] != F[j]}})
    out = {"agg": {"|".join(map(str, k)): dict(v) for k, v in sorted(agg.items())}, "flips": flips,
           "static_c0_cache": len(SC), "cpu_s": round(time.process_time() - c0, 1)}
    (HERE / "a4_inworld.json").write_text(json.dumps(out, indent=1))
    for k, v in sorted(agg.items()):
        if k[0] == "ALL" or k[1] in ("FAMILY", "EXACT_F"):
            n = v["n"]
            print(k, "n", n, "world_birth %.3f" % (v["world_birth"] / n), "world_keep %.3f" % (v["world_keep"] / n),
                  "| conv act %.3f zero %.3f bank %.3f | prom act %.3f | keep act %.3f zero %.3f | flips conv %d keep %d" % (
                      v["act_conv"] / n, v["zero_conv"] / n, v["bank_conv"] / n, v["act_convprom"] / n,
                      v["act_keep"] / n, v["zero_keep"] / n, v["act_ne_zero_conv"], v["act_ne_zero_keep"]))
    print("cpu", out["cpu_s"])


if __name__ == "__main__":
    main()
