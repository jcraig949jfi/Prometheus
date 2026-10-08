"""Architecture mining for runs that MAINTAIN competence.  python -B arch_mine.py <EXP> <ARM> [max_genomes_per_run]

For each run of the arm whose final CS > 0: the final competent genomes (detail file), weighted by count.
  identity     per-position identity to CT_UA, summarized by region (copier 0-6, routine 7-38, padding 39-63);
               population conservation profile (share of competent genomes equal to CT_UA at each position)
  robustness   single-byte robustness of the dominant competent genome vs CT_UA's (0.6887 overall, 0.3822 routine)
  copier       P-11 conversion + task retention through the real pair path (arch.copier)
  families     distinct competent genomes, the dominant genome's share, Hamming distance from CT_UA
Writes runs/<EXP>/ARCH_<ARM>.json.
"""
from __future__ import annotations

import gzip
import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arch  # noqa: E402
import fh  # noqa: E402

CT = fh.PLANTS["CT_UA"]


def mine(exp, arm, kmax=3):
    d = HERE / "runs" / exp
    out = []
    prof_num = [0] * 64
    prof_den = 0
    for p in sorted(d.glob("%s_*.json" % arm)):
        if p.name.endswith(".detail.json.gz"):
            continue
        r = json.loads(p.read_text())
        if r["CS"] <= 0:
            continue
        det = json.load(gzip.open(d / ("%s_%d.detail.json.gz" % (arm, r["seed"])), "rt"))
        gens = sorted(det["competent_genomes_final"].items(), key=lambda kv: -kv[1])
        tot = sum(c for _g, c in gens)
        for gh, c in gens:
            g = bytes.fromhex(gh)
            prof_den += c
            for j in range(64):
                prof_num[j] += c * (g[j] == CT[j])
        dom = bytes.fromhex(gens[0][0])
        rec ={"seed": r["seed"], "CS": r["CS"], "n_competent_families": len(gens), "dominant_share": round(gens[0][1] / tot, 3),
               "dominant_hamming_to_CT_UA": sum(dom[j] != CT[j] for j in range(64)),
               "dominant_identity": arch.diff_map(dom, CT), "dominant_hex": dom.hex()}
        rb = arch.robustness(dom)
        rec["dominant_robustness"] = {"all": rb["all"], "by_region": rb["by_region"]}
        rec["dominant_copier"] = arch.copier(dom, 20)
        rec["top_families"] = [{"hamming": sum(bytes.fromhex(g)[j] != CT[j] for j in range(64)), "count": c,
                                "diff_pos": [j for j in range(64) if bytes.fromhex(g)[j] != CT[j]]}
                               for g, c in gens[:kmax]]
        out.append(rec)
    prof = [round(prof_num[j] / prof_den, 3) if prof_den else None for j in range(64)]
    res = {"exp": exp, "arm": arm, "runs_with_final_competence": len(out), "runs": out,
           "conservation_profile_vs_CT_UA": prof,
           "conservation_by_region": {k: round(sum(prof[j] for j in rg) / len(rg), 3) if prof_den else None
                                      for k, rg in arch.REG.items()},
           "ref_CT_UA_robustness": {"all": 0.6887, "routine": 0.3822}}
    (d / ("ARCH_%s.json" % arm)).write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    res = mine(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
    print(json.dumps({k: v for k, v in res.items() if k not in ("runs", "conservation_profile_vs_CT_UA")}, indent=1))
    for r in res["runs"]:
        print(r["seed"], "CS", r["CS"], "fam", r["n_competent_families"], "dom share", r["dominant_share"],
              "ham", r["dominant_hamming_to_CT_UA"], "robust", r["dominant_robustness"], "copier", r["dominant_copier"])
