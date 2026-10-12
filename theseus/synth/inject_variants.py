"""THESEUS-44: injection sets separating lane timing from matter content.

Prereg: roles/Theseus/prereg/2026-10-09_inject_timing/PREREG.md.

  M0  the inject_M genomes with generation set to 0 (content kept; they no longer open the
      DEEP lanes at gen 1 -- generation 0 is not DEEP-eligible).
  R   per inject_M row (in order), one viable random-arm genome ('rand' provenance: no
      collision-generated law, no G0 rule) from theseus/controls/arms_v0_2a_2026-10-08.jsonl
      (same g0_readers + cond_ops config), rule count within 1, task J < .6, not reused, seeded
      order 20261011; given the matched M row's generation (lane timing kept, content removed).
"""

import json

import numpy as np

from . import task_comp as tcm

SRC_M = "theseus/archive/inject_M_v0_2t0_2026-10-08.jsonl"
SRC_R = "theseus/controls/arms_v0_2a_2026-10-08.jsonl"


def main():
    M = [json.loads(l) for l in open(SRC_M, encoding="utf-8")]
    R = [json.loads(l) for l in open(SRC_R, encoding="utf-8")]
    R = [r for r in R if r["arm"] == "R" and r["viable"]]
    R = [R[i] for i in np.random.default_rng(20261011).permutation(len(R))]
    M0 = [{**m, "id": m["id"].replace("INJ-M-", "INJ-M0-"), "generation": 0,
           "meta": {**m["meta"], "generation_recorded": m["generation"], "variant": "M0"}} for m in M]
    used, RR, jc = set(), [], {}
    for m in M:
        nr = len(m["genome"]["rules"])
        pick = None
        for r in R:
            if r["id"] in used or abs(len(r["genome"]["rules"]) - nr) > 1:
                continue
            if r["id"] not in jc:
                jc[r["id"]] = tcm.J(r["genome"])
            if jc[r["id"]] < tcm.SOLVER:
                pick = r
                break
        if pick is None:
            raise SystemExit(f"no R match for {m['id']}")
        used.add(pick["id"])
        RR.append({"id": f"INJ-R-{pick['id']}", "genome": pick["genome"], "generation": m["generation"],
                   "meta": {"matched_to": m["id"], "source": SRC_R, "source_id": pick["id"], "J": jc[pick["id"]],
                            "variant": "R"}})
    for name, rows in (("M0", M0), ("R", RR)):
        with open(f"theseus/archive/inject_{name}_v0_2t0_2026-10-08.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(json.dumps({"M0": len(M0), "R": len(RR), "R_J": [round(r["meta"]["J"], 3) for r in RR],
                      "R_rules_minus_M": [len(r["genome"]["rules"]) - len(m["genome"]["rules"]) for r, m in zip(RR, M)]}))


if __name__ == "__main__":
    main()
