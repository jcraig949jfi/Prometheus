"""Step 3: census of CVT-R-counted rows that do NOT carry the parent's variant (record seed, certified side, RAND).
For each such row: is (i, x) in the recurring class; signature size; does the variant lineage sit on a fixed point
(child g2 == g3 in >= 2 draws); fidelity of the variant lineage to the variant parent; is the base a replicator."""
import json, pathlib
from collections import Counter
from _cvtx import A, ROWS, cvt_full, make_step, cr_index, fid, certs

OUT = pathlib.Path(__file__).with_suffix(".json")


def main():
    panel = [r for r in ROWS if r["vm"] == "DENSE" and r["P11"]["certified"] and len(r["P11"]["certified_sides"]) == 1]
    tot = Counter()
    per = []
    for r in panel:
        G = bytes.fromhex(r["hex"]); s = r["P11"]["certified_sides"][0]
        P = A.params(r["vm"], r["cell"]); _, _, z = A.env(r["vm"], r["cell"])
        rows, base, lins = cvt_full(make_step(z, P, s, r["hex"]), G, r["hex"])
        cr = cr_index(rows)
        bad = []
        for j in cr:
            i, x, d = rows[j]
            lin = lins[j]
            rg = 2 if d[2] == d[1] else 3
            carried = [sum(lin[k][g][i] == x for k in range(3)) - sum(base[k][g][i] == x for k in range(3)) >= 2
                       for g in (0, 1, rg)]
            if all(carried):
                continue
            Gv = G[:i] + bytes([x]) + G[i + 1:]
            bad.append({"i": i, "x": x, "orig": G[i], "variant_in_class": dict(d[1]).get(i) == x,
                        "carried_g1_g2_grec": carried, "class_size": len(d[1]),
                        "variant_fixed_point": sum(lin[k][1] == lin[k][2] for k in range(3)) >= 2,
                        "variant_fid_to_Gv_g2": round(sum(fid(lin[k][1], Gv) for k in range(3)) / 3, 3),
                        "base_fid_g2": round(sum(fid(base[k][1], G) for k in range(3)) / 3, 3)})
        tot["genomes"] += 1
        tot["cr_rows"] += len(cr)
        tot["noncarried_rows"] += len(bad)
        tot["genomes_with_noncarried"] += bool(bad)
        tot["genomes_accept_only_via_noncarried"] += bool(cr) and len(bad) == len(cr)
        tot["noncarried_variant_absent_from_class"] += sum(not b["variant_in_class"] for b in bad)
        if bad:
            per.append({"key": r["key"], "side": s, "cr": len(cr), "noncarried": bad[:10], "n_noncarried": len(bad)})
    OUT.write_text(json.dumps({"totals": tot, "per_genome": per}, indent=1))
    print(dict(tot))


if __name__ == "__main__":
    main()
