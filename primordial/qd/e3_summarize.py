"""Summarise E3 rows -> primordial/ledger/rows/E/E3-falkordb-config-genome.summary.json"""
from __future__ import annotations

import json
from collections import defaultdict

from primordial.qd.e3_run import LOAD_GENES, ROWS

rows = [json.loads(l) for l in open(ROWS, encoding="utf-8")]
var = [r for r in rows if r["kind"] == "variant"]
rt = [r for r in rows if r["kind"] == "runtime"]
last = len(LOAD_GENES) - 1
by = defaultdict(dict)  # (restart) -> {(q, v): row}
for r in var:
    by[r["restart"]][(r["query"], r["variant"])] = r

# gate accounting: a genome dies if ANY corpus query fails the gate
cheat_variant_rows = [r for r in var if r["cheat"]]
honest_variant_rows = [r for r in var if not r["cheat"]]
genes = defaultdict(list)
for r in rt:
    genes[(r["gene"], r["value"], r["cheat"])].append(r["gate"])
gene_verdict = [{"gene": g, "value": v, "cheat": c, "queries_failing_gate": sum(not x for x in xs),
                 "genome_survives": all(xs)} for (g, v, c), xs in genes.items()]

# A/A noise floor: same load genes, restart 0 vs last, every honest variant
aa = []
for key, r0 in by[0].items():
    r1 = by[last].get(key)
    if r1 and r0["gate"] and r1["gate"] and not r0["cheat"]:
        aa.append(max(r0["wall_ms_median"], r1["wall_ms_median"]) / min(r0["wall_ms_median"], r1["wall_ms_median"]))
aa.sort()
noise = aa[-1]
noise_ex_cold = sorted(aa)[-2]  # restart 0 ran the first query right after the corpus build

per_restart = []
for li, d in sorted(by.items()):
    qs = sorted({q for q, _ in d})
    best, v0 = {}, {}
    for q in qs:
        ok = [r for (qq, _), r in d.items() if qq == q and r["gate"] and not r["cheat"]]
        b = min(ok, key=lambda r: r["wall_ms_median"])
        best[q] = {"variant": b["variant"], "ms": b["wall_ms_median"],
                   "speedup_vs_v0": round(d[(q, 0)]["wall_ms_median"] / b["wall_ms_median"], 2)}
        v0[q] = d[(q, 0)]["wall_ms_median"]
    per_restart.append({"restart": li, "load_genes": d[(qs[0], 0)]["load_genes"],
                        "engine_cfg": d[(qs[0], 0)]["engine_cfg"], "boot_s": d[(qs[0], 0)]["boot_s"],
                        "total_ms_v0": round(sum(v0.values()), 2),
                        "total_ms_best": round(sum(b["ms"] for b in best.values()), 2), "best": best})

summary = {
    "exp_id": "E3-falkordb-config-genome",
    "cheat_variant_rows": len(cheat_variant_rows),
    "cheat_variant_rows_killed": sum(not r["gate"] for r in cheat_variant_rows),
    "honest_variant_rows": len(honest_variant_rows),
    "honest_variant_rows_killed": sum(not r["gate"] for r in honest_variant_rows),
    "runtime_genes": gene_verdict,
    "aa_ratio_max": round(noise, 3), "aa_ratio_second": round(noise_ex_cold, 3),
    "aa_ratio_median": round(aa[len(aa) // 2], 3), "aa_pairs": len(aa),
    "per_restart": per_restart,
}
out = ROWS.with_suffix(".summary.json")
out.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(summary, indent=1, sort_keys=True))
