"""BEL-48H W5 block 3 analysis (rules: prereg s10; committed before the runs).   python3 analyze_w5b3.py RESULTS OUT"""
import json, sys
from collections import defaultdict
from analyze_w5 import sign_one_sided


def e_share(r):
    order = r["arm"].split("_")[1]
    em, sm = ("transplant0", "transplant1") if order == "ES" else ("transplant1", "transplant0")
    e = s = 0
    for key, n in r["census"]["func_by_founder"].items():
        parts = set(key.split("+"))
        if em in parts and sm not in parts:
            e += n
        elif sm in parts and em not in parts:
            s += n
    return (e / (e + s)) if (e + s) else None, e, s


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    by = defaultdict(dict)
    for r in R:
        by[(r["cell"], r["pair"])][r["arm"]] = r
    out = {"n": len(R) + len(voids), "voids": len(voids), "levels": {}}
    diffs_pos = diffs_neg = 0
    for lvl in ("MED", "HIGH"):
        rows = {}
        for (c, k), arms in by.items():
            if c != lvl:
                continue
            row = {}
            for cp in ("ON", "OFF"):
                v = [e_share(arms[a])[0] for a in ("%s_ES" % cp, "%s_SE" % cp) if a in arms]
                v = [x for x in v if x is not None]
                row[cp] = sum(v) / len(v) if v else None
            rows[k] = row
        on = [r["ON"] for r in rows.values() if r["ON"] is not None]
        off = [r["OFF"] for r in rows.values() if r["OFF"] is not None]
        ep = sum(1 for x in on if x > 0.5); en = sum(1 for x in on if x < 0.5)
        dp = sum(1 for r in rows.values() if r["ON"] is not None and r["OFF"] is not None and r["ON"] > r["OFF"])
        dn = sum(1 for r in rows.values() if r["ON"] is not None and r["OFF"] is not None and r["ON"] < r["OFF"])
        diffs_pos += dp; diffs_neg += dn
        out["levels"][lvl] = {"seeds": len(rows), "E_share_ON_mean": round(sum(on) / len(on), 3) if on else None,
                              "E_share_OFF_mean": round(sum(off) / len(off), 3) if off else None,
                              "ON_E_majority": ep, "ON_S_majority": en, "p_E_favoured_ON": sign_one_sided(ep, en),
                              "ON_gt_OFF": dp, "ON_lt_OFF": dn,
                              "extinct": {a: sum(1 for (c, k), arms in by.items() if c == lvl and a in arms and arms[a]["summary"]["extinct"])
                                          for a in ("ON_ES", "ON_SE", "OFF_ES", "OFF_SE")}}
    h = out["levels"].get("HIGH", {})
    out["W5-P6"] = {"holds": bool(h) and h["p_E_favoured_ON"] < 0.05, "ON_E_majority": h.get("ON_E_majority"), "ON_S_majority": h.get("ON_S_majority"), "p": h.get("p_E_favoured_ON")}
    out["W5-P7"] = {"ON_gt_OFF": diffs_pos, "ON_lt_OFF": diffs_neg, "p": sign_one_sided(diffs_pos, diffs_neg), "holds": sign_one_sided(diffs_pos, diffs_neg) < 0.05}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
