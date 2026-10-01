"""N17e: re-assay the 7ae3 founder, the side-switch morphs (49->5C/59) and the 3 one-bit-reachable supercritical
neighbours (44->AC, 43->81, 43->C3) against REALIZED partners: genome + carried registers drawn from W2-14's
founder-free BASE background bank (epochs 10-299), with the donor's context either ZERO or a bank context.
W2-14 found partner register state is the single largest lever on lineage outcomes, so uniform-random RAND
contexts (N17c/d) may mislead. Copy errors off; random side; N interactions per arm on a shared panel."""
import json, pickle, random, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C

N = 1000
VARS = [("founder", None, None), ("49-5c", 49, 0x5C), ("49-59", 49, 0x59),
        ("44-ac", 44, 0xAC), ("43-81", 43, 0x81), ("43-c3", 43, 0xC3)]


def main():
    banks = pickle.load(open(HERE.parent / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
    r = C.runner_for_spec(C.run_ds.DONOR)
    F = C.run_ds.donor_genome()
    rng = random.Random("N17e")
    pan = []
    for _ in range(N):
        ep = rng.randrange(10, 300)
        y, cy = banks[ep][rng.randrange(len(banks[ep]))]
        ep2 = rng.randrange(10, 300)
        _, cx = banks[ep2][rng.randrange(len(banks[ep2]))]
        pan.append((y, cy, cx, rng.randrange(2)))
    out = {}
    for name, p, v in VARS:
        g = bytearray(F)
        if p is not None:
            g[p] = v
        g = bytes(g)
        row = {}
        for dctx in ("ZERO", "BANK"):
            m = k = c0 = c1 = n0 = n1 = 0
            for y, cy, cx, s in pan:
                sx = C.ZERO if dctx == "ZERO" else cx
                o = C.outcome(r, g, y, s, sx, cy, 0.0, None)
                m += o["m_base"]; k += o["keep"]
                if s == 0:
                    n0 += 1; c0 += o["conv"]
                else:
                    n1 += 1; c1 += o["conv"]
            row[dctx] = {"m_base": m / N, "keep": k / N, "conv_side0": c0 / max(n0, 1), "conv_side1": c1 / max(n1, 1)}
        out[name] = row
    (HERE / "bank_assay.json").write_text(json.dumps(out, indent=1))
    for k, v in out.items():
        print(k, v)


if __name__ == "__main__":
    main()
