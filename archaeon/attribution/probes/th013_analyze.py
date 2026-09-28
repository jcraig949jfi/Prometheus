"""Analyse th013_block13 output: machinery material (IBD) vs machinery state (IBS) vs execution vs capability through time, the
five TH-013 hypotheses, and item 8 (fates of non-copier children).
    python -m archaeon.attribution.probes.th013_analyze TH013_OUT.json OUT.json
Founder machinery M_f is recomputed here by full-locus knockout (th015_archaeon.machinery); the probe's own knockout scanned
executed opcode loci only (F4).
"""
import json
import sys
from collections import Counter

from archaeon.attribution.probes.th015_archaeon import machinery, run


def main(inp, out):
    d = json.load(open(inp)); F = bytes.fromhex(d["founder"]["tape"]); Mf, Xf = machinery(F)
    rows = []
    for s in d["snapshots"]:
        ms = s["members"]
        if not ms: continue
        n = len(ms)
        def mean(f): return round(sum(f(m) for m in ms) / n, 4)
        def fmat(m, p): return m["pos"][p]["mat"].startswith("F@")
        r = {"epoch": s["epoch"], "alive": s["alive"], "n": n, "ggen_mean": mean(lambda m: m["ggen"]),
             "founder_material_any_pos": mean(lambda m: sum(fmat(m, p) for p in range(32)) / 32),
             "founder_material_same_pos": mean(lambda m: sum(m["pos"][p]["mat"] == "F@%d" % p for p in range(32)) / 32),
             "founder_material_at_Mf": mean(lambda m: sum(fmat(m, p) for p in Mf) / len(Mf)),
             "ibs_same_at_Mf": mean(lambda m: sum(m["pos"][p]["ibs_same"] for p in Mf) / len(Mf)),
             "ibs_same_all": mean(lambda m: sum(m["pos"][p]["ibs_same"] for p in range(32)) / 32),
             "new_material_kinds": dict(Counter(m["pos"][p]["mat"] for m in ms for p in range(32) if not m["pos"][p]["mat"].startswith("F@"))),
             "exact_isolated": mean(lambda m: m["self_copy_allowed"]), "birth_isolated": mean(lambda m: m["birth_allowed"]),
             "ruler": dict(Counter(m["ruler"] for m in ms)),
             "Mf_executed": mean(lambda m: sum(p in m["executed"] for p in Mf if p in Xf) / max(1, len([p for p in Mf if p in Xf]))),
             "offsets": dict(Counter(int(m["pos"][p]["mat"][2:]) - p for m in ms for p in range(32) if fmat(m, p)).most_common(4))}
        # machinery of the members themselves (full scan) on up to 2 members
        mm = [machinery(bytes.fromhex(m["tape"]))[0] for m in ms[:2] if m.get("birth_allowed")]
        r["member_machinery"] = mm
        r["member_machinery_founder_material"] = [round(sum(fmat(ms[i], p) for p in M) / len(M), 3) if M else None for i, M in enumerate(mm)]
        r["member_machinery_ibs_founder"] = [round(sum(bytes.fromhex(ms[i]["tape"])[p] == F[p] for p in M) / len(M), 3) if M else None for i, M in enumerate(mm)]
        rows.append(r)
    # capability reacquisition: a member-level capable -> incapable -> capable pattern is not trackable per oid across snapshots
    # (members differ); report the lineage-level series instead
    fates = Counter(); detail = []
    for k, t in d["tracked_noncopiers"].items():
        if t.get("holders_final", 0) == 0: f = "GONE (no living cell holds any of its material)"
        elif any(c in ("EXACT_COPIER", "NEAR_COPIER", "GATED_COPIER", "PARTIAL_COPIER") for c in t.get("holder_classes", [])):
            f = "PERSISTS IN A COPIER" if t["glin"] not in t.get("holder_glins", []) or True else ""
        else: f = "PERSISTS, NO COPIER HOLDER"
        fates[f] += 1; detail.append({"oid": k, "epoch": t["epoch"], "class": t["class"], "fate": f, "holders": t.get("holders_final"),
                                      "max_ids_retained": t.get("max_ids_retained"), "n_ids": t.get("n_ids"), "holder_classes": t.get("holder_classes")})
    res = {"founder_tape": d["founder"]["tape"], "founder_machinery_full_scan": Mf, "founder_executed_plus_M": Xf, "rows": rows,
           "births_by_mechanism": d["births_by_mechanism"], "tracked_noncopiers": len(detail), "fates": dict(fates), "fate_detail": detail[:60],
           "snapshot_series_noncopier_material_alive": [(s["epoch"], s["tracked_noncopier_material_alive"], s["tracked_total"]) for s in d["snapshots"]]}
    json.dump(res, open(out, "w"), indent=1)
    print("M_f", Mf)
    print("epoch alive  ggen  Fany  Fsame  F@Mf  IBS@Mf IBSall exact birth  Mf_exec  offsets")
    for r in rows[::max(1, len(rows) // 25)]:
        print(r["epoch"], r["alive"], r["ggen_mean"], r["founder_material_any_pos"], r["founder_material_same_pos"], r["founder_material_at_Mf"],
              r["ibs_same_at_Mf"], r["ibs_same_all"], r["exact_isolated"], r["birth_isolated"], r["Mf_executed"], r["offsets"], r["member_machinery"])
    print("fates", dict(fates))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
