"""D003-10 / H-D4-36 -- reproduce the mechanism x substrate_class gap table
from the committed V0 curation and test whether the program_ecology (PE)
"missing cells" are more empty than label sparsity alone predicts.

Inputs (read-only, repo @ b960d1a42600e17128f6270282b30e8e6abb5086):
  evidence_wiki/gold/curation_v1.json@b960d1a42
  evidence_wiki/benchmarks/gap_prospective_v1.json@b960d1a42

Stdlib + numpy only. NOT RUN by the author (worker had no code execution).
The hand-derived values quoted in REPORT.md are what this script should
print; any mismatch falsifies the corresponding claim.

Deciding outputs:
  (1) CHECK_SNAPSHOT: n_observed_cells == 57 and
      22*13 - 57 - 5 == 224 (gap_prospective_v1.json n_unobserved_cells_eligible).
      If true, the V1-C snapshot is exactly the V0 81-finding curation.
  (2) CHECK_SCORES: every slate_public score == mech_tot * sub_tot
      computed from curation_v1.json.
  (3) CHECK_ORDER: slate_public[0:5] are the 5 largest weights, in
      descending order (=> public order and scores reveal the sealed
      'marginal' slate).
  (4) NULL_PE: permutation null for the number of empty PE cells and per-cell
      P(empty), shuffling substrate labels across findings (keeps each
      finding's mechanism set and each substrate's finding count fixed).
      A PE cell is a *statistically* surprising gap only if P(empty) < 0.05.
      Hand Poisson approximation (REPORT.md): E[#empty PE cells] ~ 8.0 vs
      observed 11; per-cell P(empty) confound 0.16, negative_evidence_reuse /
      transfer_mediation / native_vocabulary 0.27, instrument_tautology 0.35,
      seed_instability / circular_verification 0.77.
"""
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent  # set to repo root when running
CUR = ROOT / "evidence_wiki/gold/curation_v1.json"
GAP = ROOT / "evidence_wiki/benchmarks/gap_prospective_v1.json"
PE = "program_ecology"
BURNED = {  # V0-era MISSING_CELL registrations (CASE_STUDIES_V0.md:75-81)
    ("confound_conditioning", PE), ("negative_evidence_reuse", PE),
    ("projection_equivalence", "lmfdb_arithmetic"),
    ("accessibility_geometry", "llm_probe_band"), ("transfer_mediation", PE),
}


def load():
    cur = json.loads(CUR.read_text(encoding="utf-8"))
    gap = json.loads(GAP.read_text(encoding="utf-8"))
    return cur, gap


def tables(cur):
    mechs = list(cur["dim_terms"]["mechanism"])
    subs = list(cur["dim_terms"]["substrate_class"])
    cell = Counter()
    for fid, a in cur["assignments"].items():
        for m in a["mechanism"]:
            cell[(m, a["substrate_class"])] += 1
    mt, st = Counter(), Counter()
    for (m, s), v in cell.items():
        mt[m] += v
        st[s] += v
    return mechs, subs, cell, mt, st


def main():
    cur, gap = load()
    mechs, subs, cell, mt, st = tables(cur)
    n_obs = len(cell)
    unobs = [(m, s) for m in mt for s in st if (m, s) not in cell]
    print("labels", sum(cell.values()), "findings", len(cur["assignments"]))
    print("CHECK_SNAPSHOT observed", n_obs, "unobserved", len(unobs),
          "eligible(after burned)", len([c for c in unobs if c not in BURNED]),
          "committed", gap["n_unobserved_cells_eligible"])

    w = {c: mt[c[0]] * st[c[1]] for c in unobs}
    ok = True
    for row in gap["slate_public"]:
        c = (row["coords"]["mechanism"], row["coords"]["substrate_class"])
        if w.get(c) != row["score"]:
            ok = False
            print("score mismatch", c, w.get(c), row["score"])
    print("CHECK_SCORES", ok)

    elig = sorted([c for c in unobs if c not in BURNED], key=lambda c: -w[c])
    top5 = [w[c] for c in elig[:5]]
    first5 = [r["score"] for r in gap["slate_public"][:5]]
    print("CHECK_ORDER top5 weights", top5, "public[0:5]", first5,
          "equal", sorted(top5) == sorted(first5))

    pe_empty = [m for m in mechs if (m, PE) not in cell]
    print("PE observed mechanisms", sorted(m for m in mechs if (m, PE) in cell))
    print("PE empty mechanisms", pe_empty)

    # Poisson approximation (matches REPORT.md hand computation)
    N = sum(cell.values())
    lam = {m: mt[m] * st[PE] / N for m in mechs}
    print("POISSON E[#empty PE]", round(sum(math.exp(-lam[m]) for m in mechs), 3))
    for m in pe_empty:
        print("  POISSON P(empty)", m, round(math.exp(-lam[m]), 3))

    # Permutation null: shuffle substrate labels across findings
    fids = list(cur["assignments"])
    mech_sets = [cur["assignments"][f]["mechanism"] for f in fids]
    sub_labels = np.array([cur["assignments"][f]["substrate_class"] for f in fids])
    rng = np.random.default_rng(20260930)
    R = 20000
    n_empty = np.zeros(R, dtype=int)
    empty_hits = Counter()
    for r in range(R):
        perm = rng.permutation(sub_labels)
        seen = set()
        for ms, s in zip(mech_sets, perm):
            if s == PE:
                seen.update(ms)
        e = [m for m in mechs if m not in seen]
        n_empty[r] = len(e)
        empty_hits.update(e)
    obs = len(pe_empty)
    print("NULL_PE observed_empty", obs, "null_mean", n_empty.mean().round(3),
          "P(null >= observed)", (n_empty >= obs).mean().round(4))
    for m in pe_empty:
        print("  NULL P(empty)", m, round(empty_hits[m] / R, 4))


if __name__ == "__main__":
    main()
