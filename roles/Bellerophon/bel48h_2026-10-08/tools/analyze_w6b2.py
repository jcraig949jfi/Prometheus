"""BEL-48H W6 block 2 analysis (rules: prereg s11; committed before the runs).  python3 analyze_w6b2.py RESULTS EVENTS_DIR PLAN OUT"""
import gzip, json, pathlib, sys
from collections import defaultdict
from analyze_w1 import mcnemar_exact


def main(res, evdir, planp, outp):
    sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
    from prometheus.z80atlas.world import Config
    from belinst import Func
    fP = Func(Config(reproduction="ENDOGENOUS_PARTIAL", physics="v2"))
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    by = defaultdict(lambda: defaultdict(dict))
    for r in R:
        by[r["cell"]][r["pair"]][r["arm"]] = r
    fa = lambda r: r["heredity"]["first_func"] is not None
    out = {"n": len(R) + len(voids), "voids": len(voids), "variants": {}}
    allok = {"P1": True, "P2": True, "P3": True, "P4": True}
    for cell, pairs in sorted(by.items()):
        arms = ("AB", "A", "B", "none", "AB_zero", "AB_copy")
        cnt = {a: sum(1 for v in pairs.values() if a in v and fa(v[a])) for a in arms}
        n = len(pairs)
        def mc(x, y):
            xo = sum(1 for v in pairs.values() if x in v and y in v and fa(v[x]) and not fa(v[y]))
            yo = sum(1 for v in pairs.values() if x in v and y in v and fa(v[y]) and not fa(v[x]))
            return {"AB_only": xo, "other_only": yo, "p": mcnemar_exact(xo, yo)}
        comp_ok = comp_n = 0
        for v in pairs.values():
            r = v.get("AB")
            if r is None or not fa(r):
                continue
            f = pathlib.Path(evdir) / (r["id"] + ".jsonl.gz")
            if not f.exists():
                continue
            evs = [json.loads(l) for l in gzip.open(f, "rt")]
            if not evs:
                continue
            e = evs[0]
            child = bytes.fromhex(e["tape"]); vec = e["vec"]
            wonly = bytes(0 if vec[i] == "T" else b for i, b in enumerate(child))
            tonly = bytes.fromhex(e["target_tape"]) if e.get("target_tape") else b""
            comp_n += 1
            comp_ok += (fP(child) and not fP(wonly) and (not tonly or not fP(tonly)))
        mAZ = mc("AB", "AB_zero"); mAC = mc("AB", "AB_copy")
        p1 = cnt["AB"] >= 0.8 * n and all(cnt[a] <= 0.1 * n for a in ("B", "none"))      # A alone is reported (W2: A completes against random background)
        p2 = mAZ["p"] < 0.05 and mAZ["AB_only"] > mAZ["other_only"]
        p3 = mAC["p"] < 0.05 and mAC["AB_only"] > mAC["other_only"]
        p4 = comp_n > 0 and comp_ok >= 0.8 * comp_n
        for k_, v_ in (("P1", p1), ("P2", p2), ("P3", p3), ("P4", p4)):
            allok[k_] = allok[k_] and v_
        out["variants"][cell] = {"pairs": n, "func_any": cnt, "AB_vs_zero": mAZ, "AB_vs_copy": mAC,
                                 "first_event_two_source": [comp_ok, comp_n], "P1": p1, "P2": p2, "P3": p3, "P4": p4}
    for k_ in allok:
        out["G-" + k_] = {"holds_all_variants": allok[k_]}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:5])
