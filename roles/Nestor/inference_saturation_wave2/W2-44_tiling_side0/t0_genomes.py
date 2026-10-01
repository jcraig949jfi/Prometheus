"""W2-44 t0: load the founder (7ae3 implant), the in-world rotated chain genomes used by W2-35 s4
(first child / last node of each rotated deepest chain, from W2-17 r3_out), print frame, hex, and
disassembly of founder and each genome in its own coordinates and de-rotated into founder coordinates.
python -B t0_genomes.py -> t0_genomes.json"""
import json, sys, pathlib
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
sys.path.insert(0, str(W2 / "W2-35_rotation_leak"))
from frames import frame, IMP  # noqa
sys.path.insert(0, str(W2 / "W2-24_keep_variant"))
from tvm import C  # noqa
Z = C.Z8PLAIN
F = C.run_ds.donor_genome()
assert F == IMP, "donor != implant"
a5 = json.loads((W2 / "W2-35_rotation_leak" / "a5_chains.json").read_text())
r3 = W2 / "W2-17_runaway_departure" / "r3_out"
G = {"founder": F}
rows = []
for row in a5["deepest_chain_per_run"]:
    rows.append({k: row[k] for k in row if k in ("label", "frame_first", "frame_last")})
    if row["frame_first"].startswith("ROT"):
        d = json.loads((r3 / (row["label"] + ".json")).read_text())
        ch = d["deepest"][0]["chain"]
        G[row["label"] + "_first"] = bytes.fromhex(d["births"][str(ch[1])]["g"])
        G[row["label"] + "_last"] = bytes.fromhex(d["births"][str(ch[-1])]["g"])
def derot(g, s):  # founder coords: y[i] = g[(i+s)%64]
    return bytes(g[(i + s) % 64] for i in range(64))
out = {}
for k, g in G.items():
    s, c, c0 = frame(g)
    y = derot(g, s)
    out[k] = {"frame": [s, c, c0], "hex": g.hex(), "derot_hex": y.hex(),
              "diff_vs_founder_derot": [i for i in range(64) if y[i] != F[i]]}
    print("==", k, s, c, c0, g.hex())
    print("   derot diffs at", out[k]["diff_vs_founder_derot"])
for a, t in Z.dis(F):
    print("%3d %s %s" % (a, F[a:a+1].hex(), t))
(HERE / "t0_genomes.json").write_text(json.dumps({"rows": rows, "G": out}, indent=1))
