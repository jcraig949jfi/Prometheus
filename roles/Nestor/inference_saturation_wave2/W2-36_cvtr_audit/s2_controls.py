"""Step 2: reachability / soundness controls for CVT-R (original rule, certs.py:69-73) and the repaired rule R*.
Each control x arm (RAND = world order with random victims, HALT = all-0x76 victims = no partner run) x 9 seeds
(record-style sid = hex, then hex:reseed0..7). Constructed genomes are hand-written instruments (z8.asm).

POSITIVE  SF7_*      8 state-free 7ae3 genomes of W2-4 (side 0, cell 7ae3)
          E700_*     the 8 epoch-700 genomes (set c), cell 7ae3, side 0
          CT_UA      W2-10 copier+task genome (ffa6), sides 0 and 1
          HH         constructed 64-byte pure self-copier (block H twice)
NEGATIVE  q1:59      recorded lineage-collapse genome (7ae3, side 1)
          FILL       constructed self-blanker: child = 00 x 64 whatever the parent is
          HALFBLANK  constructed: front half X copies only the back half H twice; child = HH, never the parent
          SWITCH     constructed: a genuine self-copier with one selector byte (site 7): variant x^0x01 switches
                     the copy source to the resident block H, so the variant lineage settles on HH and never
                     carries the variant byte. Row-level control (the genome also has genuine rows).
"""
import json, pathlib, random, sys, time
from _cvtx import A, ROWS, run_one, row, certs
import z8 as z8_plain

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(__file__).with_suffix(".json")
K = 8


def pad(b, n, seed):
    rng = random.Random(seed)
    b = bytearray(b)
    while len(b) < n:
        b.append(rng.randrange(256))
    return bytes(b)


def asm(s):
    return z8_plain.asm(s)[0]


H_SRC = "SELF\nLD A,L\nXOR 0x40\nLD E,A\n.db 0xE5\nHALT\n"
SEL_SRC = ("SELF\nLD A,L\nXOR 0x40\nLD E,A\nLD A,%d\nADD A,A\nADD A,A\nADD A,A\nADD A,A\nADD A,A\n"
           "AND 0x20\nADD A,L\nLD L,A\n.db 0xE5\nHALT\n")
FILL_SRC = "SELF\nLD A,L\nXOR 0x40\nLD L,A\nLD E,A\nINC E\nLD (HL),0\nLD BC,63\n.db 0xE5\nHALT\n"


def constructs():
    H = pad(asm(H_SRC), 32, "W2-36-H")
    out = {"HH": H + H,
           "SWITCH": pad(asm(SEL_SRC % 0), 32, "W2-36-S") + H,
           "HALFBLANK": pad(asm(SEL_SRC % 1), 32, "W2-36-S") + H,
           "FILL": pad(asm(FILL_SRC), 64, "W2-36-F")}
    assert asm(SEL_SRC % 0)[7] == 0x00 and asm(SEL_SRC % 1)[7] == 0x01   # selector immediate is byte 7
    return out


def controls():
    C = []
    w4 = json.loads((HERE.parent / "W2-4_causal_minimality" / "w4_results.json").read_text())["genomes"]
    for e in w4:
        if e["grp"] == "SF" and e["cell"] == "C7":
            C.append(("POS", e["id"], bytes.fromhex(e["hex"]), "7ae3", [0]))
    for r in ROWS:
        if r["set"] == "c":
            C.append(("POS", "E700_" + r["key"].split(":")[-1], bytes.fromhex(r["hex"]), "7ae3", [0]))
    W10 = "ED327DEE405FE5DB0047DB004FDB005779FE02380E78A9477AFE00782802C625D3007678D3007679A4B8C83F4C602745135FECC26DAE628982C868A00D767F86"
    C.append(("POS", "CT_UA", bytes.fromhex(W10), "ffa6", [0, 1]))
    K_ = constructs()
    C.append(("POS", "HH", K_["HH"], "ffa6", [0, 1]))
    r59 = row("b:q1_competent:59")
    C.append(("NEG", "q1:59", bytes.fromhex(r59["hex"]), r59["cell"], [1]))
    for k in ("FILL", "HALFBLANK", "SWITCH"):
        C.append(("NEG" if k != "SWITCH" else "ROWNEG", k, K_[k], "ffa6", [0]))
    return C


def main():
    t0 = time.time()
    res = []
    for role, name, G, cell, sides in controls():
        P = A.params("DENSE", cell); _, _, z = A.env("DENSE", cell)
        assert len(G) == P["n"], (name, len(G), P["n"])
        for side in sides:
            for arm in ("RAND", "HALT"):
                seeds = [G.hex()] + [G.hex() + ":reseed%d" % j for j in range(K)]
                per = []
                for sid in seeds:
                    o = run_one(G, "DENSE", cell, side, sid, arm, P, z, keep=(name == "SWITCH"))
                    rec = {k: o[k] for k in ("CVTR_accept", "CVTR_n", "CVTR_classes", "base_fid_floor_ok",
                                             "cr_variant_in_sig", "cr_inherited", "cr_variant_fid_ok",
                                             "RSTAR_accept", "RSTAR_n", "RSTAR_classes")}
                    rec["base_fid_draw0"] = o["base_fid_by_draw_gen"][0]
                    rec["CVT1_n"], rec["CVT2_n"] = o["score"]["CVT1"]["n"], o["score"]["CVT2"]["n"]
                    if name == "SWITCH" and sid == seeds[0]:
                        rows, base, lins = o["_rows"], o["_base"], o["_lins"]
                        j = next(j for j, r_ in enumerate(rows) if r_[0] == 7 and r_[1] == 0x01)
                        d = rows[j][2]
                        rec["selector_row"] = {
                            "defined_by_gen": [bool(s) for s in d],
                            "recurs": bool(d[1]) and (d[2] == d[1] or d[3] == d[1]),
                            "variant_in_sig": bool(d[1]) and dict(d[1]).get(7) == 0x01,
                            "child_g2_draw0_eq_HH": lins[j][0][1] == constructs()["HH"],
                            "byte7_in_children_g1_g4_draw0": [c[7] for c in lins[j][0]]}
                    per.append(rec)
                o_n = sum(p["CVTR_accept"] for p in per[1:])
                r_n = sum(p["RSTAR_accept"] for p in per[1:])
                res.append({"role": role, "name": name, "cell": cell, "side": side, "arm": arm,
                            "record_seed": {"CVTR": per[0]["CVTR_accept"], "RSTAR": per[0]["RSTAR_accept"]},
                            "CVTR_reseed_accepts": o_n, "RSTAR_reseed_accepts": r_n, "per_seed": per})
                print(role, name, side, arm, "CVTR", per[0]["CVTR_accept"], o_n, "/8  R*", per[0]["RSTAR_accept"],
                      r_n, "/8  n", per[0]["CVTR_n"], "inh", per[0]["cr_inherited"], "baseOK",
                      per[0]["base_fid_floor_ok"], "CVT1/2", per[0]["CVT1_n"], per[0]["CVT2_n"], flush=True)
    OUT.write_text(json.dumps({"constructs": {k: v.hex() for k, v in constructs().items()},
                               "cpu_seconds": round(time.time() - t0, 1), "rows": res}, indent=0))


if __name__ == "__main__":
    main()
