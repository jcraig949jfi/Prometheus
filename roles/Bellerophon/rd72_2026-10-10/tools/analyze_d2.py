"""BEL-RD-72 D2 analysis (rules: BEL_RD72_PREREG.md s8; committed before any D2 run).   python3 analyze_d2.py RESULTS OUT
Per substrate, paired by seed: origins per arm; one-sided sign tests on discordant pairs:
  D2-P1  block_ldir > normal            (protecting precursors from imports raises origination)
  D2-P2  block_ldir > block_noldir      (the effect is specific to the precursor marker)
The precursor-damage account HOLDS in a substrate if P1 and P2 both have p < 0.05; it must hold in BOTH substrates.
Reported: block_all > normal (replication of D1 / BEL-48H), block_noldir vs normal, import-execution dose per arm."""
import json, sys
from collections import Counter, defaultdict
from analyze_d1 import one_sided


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    org = lambda r: bool((r.get("origin") or {}).get("origin_event"))
    out = {"n": len(R) + len(voids), "voids": len(voids), "substrates": {}}
    holds = []
    for s in sorted({r["cell"] for r in R}):
        pairs = defaultdict(dict)
        for r in R:
            if r["cell"] == s:
                pairs[r["pair"]][r["arm"]] = r
        ps = [v for v in pairs.values() if len(v) == 4]
        def test(a, b):
            x = sum(1 for v in ps if org(v[a]) and not org(v[b])); y = sum(1 for v in ps if org(v[b]) and not org(v[a]))
            return {"a_only": x, "b_only": y, "p": one_sided(x, y)}
        dose = {a: dict(sum((Counter({k: v for k, v in ((r.get("origin") or {}).get("O") or {}).items() if k.startswith("import_exec") or k == "blocked_bytes"})
                             for v in ps for r in [v[a]]), Counter())) for a in ("normal", "block_all", "block_ldir", "block_noldir")}
        d = {"pairs": len(ps), "origins": {a: sum(org(v[a]) for v in ps) for a in ("normal", "block_all", "block_ldir", "block_noldir")},
             "D2-P1": test("block_ldir", "normal"), "D2-P2": test("block_ldir", "block_noldir"),
             "all_vs_normal": test("block_all", "normal"), "noldir_vs_normal": test("block_noldir", "normal"), "dose": dose}
        d["holds"] = d["D2-P1"]["p"] < 0.05 and d["D2-P2"]["p"] < 0.05
        holds.append(d["holds"]); out["substrates"][s] = d
    out["D2"] = {"holds": all(holds) if holds else "NOT_TESTABLE", "per_substrate": holds}
    json.dump(out, open(outp, "w"), indent=1); print(json.dumps(out, indent=1)); return out


if __name__ == "__main__":
    main(*sys.argv[1:3])
