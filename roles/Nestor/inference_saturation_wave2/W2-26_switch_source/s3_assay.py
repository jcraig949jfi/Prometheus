"""W2-26 s3: static side-0 / side-1 conversion assay of every genome involved in a switch edge (s2), on the
W2-3 common harness (C.outcome, stock VM, copy errors off) against the W2-14 BASE background bank panel
(epochs 10-299, partner genome + carried registers), N = 400 per side, donor context ZERO and the donor's
ACTUAL carried context at the switch interaction (from the replay). Then a causal attribution per edge: if P is a
side-0 non-converter and k@E2 a side-0 converter, apply each differing byte of k@E2 to P singly; the first single
byte that alone makes P a converter (conv0 >= 0.5) names the causal source.
python -B s3_assay.py -> s3_assay.json"""
import json, pathlib, pickle, random, sys, collections
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C  # noqa: E402

N = 400
banks = pickle.load(open(HERE.parent / "W2-14_F_calibration" / "banks.pkl", "rb"))["BASE"]
r = C.runner_for_spec(C.run_ds.DONOR)
F = C.run_ds.donor_genome()
rng = random.Random("W2-26")
PAN = []
for _ in range(N):
    ep = rng.randrange(10, 300)
    PAN.append(banks[ep][rng.randrange(len(banks[ep]))])
CACHE = {}


def conv(g, side, sx=C.ZERO):
    key = (g, side, None if sx is C.ZERO else json.dumps(sx))
    if key in CACHE:
        return CACHE[key]
    c = 0
    for y, cy in PAN:
        c += C.outcome(r, g, y, side, sx, cy, 0.0, None)["conv"]
    CACHE[key] = c / N
    return CACHE[key]


def fam(g, imp):
    best = max((sum(g[(i + s) % 64] == imp[i] for i in range(64)), s) for s in range(64))
    f0 = sum(a == b for a, b in zip(g, imp))
    if f0 >= 51:
        return "7ae3"
    if best[0] >= 51:
        return "7ae3-shift"
    return "foreign"


def main():
    d = json.loads((HERE / "s2_switch_diffs.json").read_text())
    imp = bytes.fromhex(json.loads((HERE / "s1_out" / "CRW_85.json").read_text())["implant"])
    assert imp == F, "implant != W2-3 donor genome"
    rows = []
    for e in d["edges"]:
        Pg, kE2 = bytes.fromhex(e["Pg"]), bytes.fromhex(e["kE2"])
        dctx = e["kk_dctx"]
        sx = (dctx[0], bool(dctx[1]), bool(dctx[2]))
        row = {k: e[k] for k in ("run", "cls", "k", "kk", "e1", "e2", "inwin", "ndiff")}
        row["P_fam"], row["k_fam"] = fam(Pg, imp), fam(kE2, imp)
        row["P_c0"], row["P_c1"] = conv(Pg, 0), conv(Pg, 1)
        row["k_c0"], row["k_c1"] = conv(kE2, 0), conv(kE2, 1)
        row["k_c0_actctx"] = conv(kE2, 0, sx) if dctx[0] is not None else row["k_c0"]
        row["pos"] = e["pos"]
        cause = None
        if row["P_c0"] < 0.5 and row["k_c0"] >= 0.5:
            for j in sorted(e["pos"], key=int):
                g = bytearray(Pg); g[int(j)] = kE2[int(j)]
                if conv(bytes(g), 0) >= 0.5:
                    cause = {"pos": int(j), "from": "%02x" % Pg[int(j)], "to": "%02x" % kE2[int(j)],
                             "src": e["pos"][j], "bits": bin(Pg[int(j)] ^ kE2[int(j)]).count("1")}
                    break
            if cause is None:
                cause = "multi"
        row["cause"] = cause
        rows.append(row)
    (HERE / "s3_assay.json").write_text(json.dumps({"N": N, "rows": rows}))
    print(len(rows), "edges assayed; cache", len(CACHE))


if __name__ == "__main__":
    main()
