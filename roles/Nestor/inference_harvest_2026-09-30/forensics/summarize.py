"""Aggregate core_map.json (Q1, Q2, Q4) into summary.json and print the tables used in FORENSIC_FUNCTIONAL_CORE.md.

    python -B summarize.py
"""
from __future__ import annotations

import collections
import json
import pathlib
import statistics as S

HERE = pathlib.Path(__file__).resolve().parent
ROLES = ("COPY", "DEST", "SRC", "COUNT", "SELF", "EXEC_PRE", "EXEC_POST", "EXEC_NOCOPY", "EXEC_BY_PARTNER", "NOT_EXEC")


def q(xs):
    xs = sorted(xs)
    if not xs:
        return None
    return {"n": len(xs), "min": xs[0], "p25": xs[len(xs) // 4], "median": S.median(xs), "p75": xs[(3 * len(xs)) // 4],
            "max": xs[-1], "mean": round(S.mean(xs), 2)}


def group(rows):
    nn = [r["n_necessary"] for r in rows]
    bm = [r["beyond_motif"] for r in rows]
    rc = collections.Counter()
    for r in rows:
        rc.update(r["role_counts"])
    tot = sum(rc.values())
    has = {k: sum(1 for r in rows if r["role_counts"].get(k)) for k in ROLES}
    setby = collections.Counter()
    for r in rows:
        sb = r["trace"].get("set_by_genome")
        if sb is None:
            setby["no_copy_in_trace"] += 1
            continue
        for k in ("DEST", "SRC", "COUNT"):
            setby[k + ("_genome" if sb[k] else "_world")] += 1
    copyop = collections.Counter(r["trace"].get("copy_op") for r in rows)
    setter_de = collections.Counter(r["trace"].get("setter_ops", {}).get("E") for r in rows)
    setter_d = collections.Counter(r["trace"].get("setter_ops", {}).get("D") for r in rows)
    div = [r["div"]["best"]["donor_loci"] for r in rows]
    return {"n": len(rows), "necessary": q(nn), "necessary_hist": dict(sorted(collections.Counter(nn).items())),
            "beyond_motif": q(bm), "beyond_motif_hist": dict(sorted(collections.Counter(bm).items())),
            "role_totals": {k: rc.get(k, 0) for k in ROLES}, "role_share": {k: round(rc.get(k, 0) / tot, 3) for k in ROLES} if tot else {},
            "genomes_with_role": has, "register_source": dict(setby), "main_copy_op": dict(copyop),
            "E_setter_op": dict(setter_de.most_common(8)), "D_setter_op": dict(setter_d.most_common(8)),
            "motif_size": q([len(r["trace"]["motif_positions"]) for r in rows]),
            "donor_loci": q(div), "painters_le8": sum(d <= 8 for d in div), "copiers_ge48": sum(d >= 48 for d in div),
            "donor_zero_bytes": q([r["div"]["donor_zero_bytes"] for r in rows]),
            "donor_distinct_values": q([r["div"]["donor_distinct_values"] for r in rows]),
            "fid90_draws": q([r["div"]["n_draws_fid90"] for r in rows]),
            "collapse": q([r["n_collapse"] for r in rows]), "collapse_hist": dict(sorted(collections.Counter(r["n_collapse"] for r in rows).items())),
            "base_rate": q([r["base_rate"] for r in rows]),
            "collapse_roles": dict(collections.Counter(r["roles"][str(p)] for r in rows for p in r["collapse"])),
            "pre_kinds": dict(sum((collections.Counter(r["trace"].get("pre_kinds", {})) for r in rows), collections.Counter())),
            "side": dict(collections.Counter(r["trace"].get("side") for r in rows)),
            "reg_at_copy": {"HL_mod128_eq_side_base": sum((r["trace"].get("HL", -1) % 128) in (0, 64) for r in rows if "HL" in r["trace"]),
                            "DE_zero_world": sum(not r["trace"].get("set_by_genome", {}).get("DEST") for r in rows)}}


def main():
    d = json.load(open(HERE / "core_map.json"))
    rows = d["rows"]
    comp = [r for r in rows if r["competent"]]
    out = {"meta": d["meta"], "sampled": len(rows), "competent_on_rescreen": len(comp),
           "not_competent": [(r["vm"], r["cell"], r["origin_run"], r["hex"][:16]) for r in rows if not r["competent"]],
           "by_src": {"%s/%s/%s" % k: v for k, v in collections.Counter((r["src"], r["vm"], r["cell"]) for r in rows).items()}}
    dense = [r for r in comp if r["vm"] == "DENSE"]
    out["ALL_DENSE"] = group(dense)
    out["DENSE_corpus"] = group([r for r in dense if r["src"] == "corpus"])
    out["E700"] = group([r for r in dense if r["src"] == "16000006_e700"])
    out["STATE_FREE"] = group([r for r in dense if r["state_free"]])
    out["NOT_STATE_FREE"] = group([r for r in dense if not r["state_free"]])
    out["PLAIN"] = group([r for r in comp if r["vm"] == "PLAIN"]) if any(r["vm"] == "PLAIN" for r in comp) else None
    for c in ("7ae3", "ffa6"):
        out["DENSE_" + c] = group([r for r in dense if r["cell"] == c])
    out["sf_counts"] = {"dense_state_free": sum(r["state_free"] for r in dense), "dense_n": len(dense),
                        "by_cell": {c: [sum(r["state_free"] for r in dense if r["cell"] == c), sum(r["cell"] == c for r in dense)]
                                    for c in ("7ae3", "ffa6")},
                        "e700": [sum(r["state_free"] for r in dense if r["src"] == "16000006_e700"),
                                 sum(r["src"] == "16000006_e700" for r in dense)]}
    # position-level: which roles are necessary in SF but absent in non-SF
    for tag in ("STATE_FREE", "NOT_STATE_FREE"):
        g = [r for r in dense if r["state_free"] == (tag == "STATE_FREE")]
        out[tag + "_explicit"] = {
            "dest_set_by_genome": sum(bool(r["trace"].get("set_by_genome", {}).get("DEST")) for r in g),
            "src_set_by_genome": sum(bool(r["trace"].get("set_by_genome", {}).get("SRC")) for r in g),
            "count_set_by_genome": sum(bool(r["trace"].get("set_by_genome", {}).get("COUNT")) for r in g),
            "DEST_necessary": sum(r["role_counts"].get("DEST", 0) > 0 for r in g),
            "SRC_necessary": sum(r["role_counts"].get("SRC", 0) > 0 for r in g),
            "COUNT_necessary": sum(r["role_counts"].get("COUNT", 0) > 0 for r in g),
            "n": len(g)}
    for tag, g in (("ALL_DENSE", dense), ("STATE_FREE", [r for r in dense if r["state_free"]]),
                   ("NOT_STATE_FREE", [r for r in dense if not r["state_free"]]),
                   ("E700", [r for r in dense if r["src"] == "16000006_e700"])):
        sl = [r["slice"] for r in g if r.get("slice")]
        nc, cc = collections.Counter(), collections.Counter()
        for x in sl:
            nc.update(x["necessary_class_counts"])
            cc.update(x["collapse_class_counts"])
        wr = [set(x["world_regs_at_copy"]) for x in sl]
        out[tag + "_slice"] = {
            "n": len(sl), "necessary_class_totals": dict(nc), "collapse_class_totals": dict(cc),
            "world_regs_none": sum(not w for w in wr), "world_regs_only_BC": sum(bool(w) and w <= {"B", "C"} for w in wr),
            "world_D_or_E": sum(bool(w & {"D", "E"}) for w in wr), "world_H_or_L": sum(bool(w & {"H", "L"}) for w in wr),
            "world_A": sum("A" in w for w in wr), "world_E": sum("E" in w for w in wr), "world_L": sum("L" in w for w in wr),
            "world_E_or_L": sum(bool(w & {"E", "L"}) for w in wr),
            "control_world_regs_any": sum(bool(x["control_world_regs"]) for x in sl),
            "ld_de_nn_is_E_setter": sum(r["trace"].get("setter_ops", {}).get("E") == "11" for r in g),
            "D_never_written": sum(r["trace"].get("setter_ops", {}).get("D") is None for r in g),
            "necessary_in_slice_or_copy": q([x["necessary_class_counts"].get("DATA_SLICE", 0) + x["necessary_class_counts"].get("COPY", 0)
                                             + x["necessary_class_counts"].get("DATA_READ", 0) for x in sl]),
            "collapse_outside_slice": q([sum(v for k, v in x["collapse_class_counts"].items() if k not in ("DATA_SLICE", "COPY", "DATA_READ"))
                                         for x in sl]),
            "slice_size": q([x["slice_size"] for x in sl]), "slice_instr_count": q([len(x["slice_instr"]) for x in sl])}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
