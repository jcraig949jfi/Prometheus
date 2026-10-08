"""BEL-48H W5 block 2 analysis (rules: prereg s8; committed before the runs).   python3 analyze_w5b2.py RESULTS OUT"""
import json, sys
from collections import Counter, defaultdict
from analyze_w1 import mcnemar_exact
from analyze_w2 import wilson
from analyze_w3 import classify


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    pairs = defaultdict(dict)
    for r in R:
        pairs[r["pair"]][r["arm"]] = r
    org = lambda r: bool((r.get("origin") or {}).get("origin_event"))
    ps = [v for v in pairs.values() if len(v) == 2]
    po = sum(1 for v in ps if org(v["preserve"]) and not org(v["zero"])); zo = sum(1 for v in ps if org(v["zero"]) and not org(v["preserve"]))
    out = {"n": len(R) + len(voids), "voids": len(voids), "pairs": len(ps),
           "origin_runs": {a: sum(org(v[a]) for v in ps) for a in ("preserve", "zero")},
           "wilson": {a: wilson(sum(org(v[a]) for v in ps), len(ps)) for a in ("preserve", "zero")},
           "mcnemar": {"preserve_only": po, "zero_only": zo, "p": mcnemar_exact(po, zo)},
           "causes": {a: dict(Counter(classify(v[a]["origin"]["origin_event"])["cause"] for v in ps if org(v[a]))) for a in ("preserve", "zero")},
           "pathways": {a: dict(Counter(classify(v[a]["origin"]["origin_event"])["pathway"] for v in ps if org(v[a]))) for a in ("preserve", "zero")},
           "uptake_bytes_total": {a: sum((v[a]["origin"]["O"] or {}).get("uptake_bytes", 0) for v in ps) for a in ("preserve", "zero")},
           "extinct": {a: sum(v[a]["summary"]["extinct"] for v in ps) for a in ("preserve", "zero")}}
    out["W5-P4"] = {"holds": out["mcnemar"]["p"] < 0.05 and po > zo, **out["mcnemar"]}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
