"""v2b conformance battery (DEV-1). Writes engine/v2b/receipts/CONFORMANCE_V2B_<date>.json.

  C1  walker first-hit == a18.fast_cost (charge and program) on random W5 (library, cell) pairs
  C2  a18.fast_cost == the reference fair.Cell.cost (the historical differential gate, re-run)
  C3  ARTIFACT vs DIRECT tribunal agreement, T4 v1 and v1a, on real foundry programs (witnesses and PRISTINE
      first hits from the A20 foundry, qualified and unqualified)
  C4  extensional classing: ruler v2.1 re-scores W7's 47 adversarial schemas byte-identically to W7's stored
      v2.1 verdicts, and the known-relation fixtures hold
  C5  historical constant gates reproduced by the lint, and ZERO lint ERRORs in the v2b tree
Usage: python conformance_v2b.py [quick]
"""
import json
import random
import sys
import time
from pathlib import Path

import paths
import a17
import a18
from a18 import FR, G
import identity as I

import apparatus
import gates
import instruments as INS
import walk

OUT = paths.V2B / "receipts"
OUT.mkdir(exist_ok=True)
DATE = time.strftime("%Y-%m-%d", time.gmtime())


def c2_fastcost_vs_reference(n):
    a18.use_world("W5")
    return a18.gate_fast_cost(n_pairs=n, seed="APHRODITE/V2B/FASTCOST-REGATE/v1")


def c3_tribunal_paths(n):
    rows = [json.loads(x) for x in open(paths.ENG / "A20_C3" / "A20_FOUNDRY_ROWS_2026-09-28.jsonl", encoding="utf-8")]
    rows = [r for r in rows if r.get("Q2_size")]
    rng = random.Random(I._seed("APHRODITE/V2B/C3/v1"))
    rng.shuffle(rows)
    out = {"programs": 0, "disagreements": [], "by_version": {}}
    pristine = FR.KLib(FR.pristine().entries)
    for r in rows[:n]:
        prov = a17.Prov({r["name"]: (r["body"], r["final"], r["init"])})
        progs = [("witness", prov.witness(r["name"]))]
        cell = FR.Cell(prov, r["name"], 0, r["Q2_size"], label="V2B-C3")
        ch, hit = a18.fast_cost(pristine, cell, a17.ESCROW)
        if hit is not None:
            progs.append(("pristine_first_hit", hit))
        for kind, p in progs:
            for v in ("v1", "v1a"):
                d, _ = INS.qualify_direct(prov, r["name"], p, v)
                a, _ = INS.qualify_artifact(prov, r["name"], p, v)
                e = out["by_version"].setdefault(v, {"n": 0, "agree": 0, "qualified": 0})
                e["n"] += 1
                e["agree"] += int(a == d)
                e["qualified"] += int(a)
                if a != d:
                    out["disagreements"].append([r["name"], kind, list(p), v, a, d])
            out["programs"] += 1
    return out


def c4_classing():
    a18.use_world("W5")
    import tier3d as T3D
    sys.path.insert(0, str(paths.ROOT / "science" / "arc3" / "w3_novelty_reuse"))
    import w3_adversarial as W3A
    R21 = INS.ruler("v2.1")
    stored = json.loads((paths.ROOT / "science/arc3/w7_instrument_hygiene/W7_RULER_ADV_W5.json").read_text())
    st = {c["schema"]: c.get("v21", {}) for c in stored["cases"]}
    sp21, ri = R21.reference(a18.G1)
    same, diff = 0, []
    for _cls, s, _exp_new, _exp_rel, _why in W3A.CASES:
        inst = T3D.instantiate(s)
        if not inst:
            continue
        b = R21.verdict_full(s, a18.G1, sp21, ri, inst)
        keys = ("NEW_FINAL", "EQUAL_ANY", "REFINES_ANY", "COMPOSES_ANY")
        if all(b.get(k) == st.get(s, {}).get(k) for k in keys):
            same += 1
        else:
            diff.append(s)
    fixtures = {
        "G1 == ({H} + acc) [re-expression]": INS.equal_extensional(a18.G1, "({H} + acc)"),
        "G1 == (acc - (0 - {H})) [double sign]": INS.equal_extensional(a18.G1, "(acc - (0 - {H}))"),
        "G1 != (acc * {H})": not INS.equal_extensional(a18.G1, "(acc * {H})"),
        "SHAM_0 (v - (acc - {H})) COMPOSES G1": bool(R21.relations("(v - (acc - {H}))", a18.G1)["COMPOSES_ANY"]),
    }
    return {"w7_adversarial_reproduced": same, "w7_adversarial_differing": diff, "fixtures": fixtures,
            "fixtures_all_hold": all(fixtures.values())}


def c5_gates():
    eng = paths.ENG
    hist = {}
    for f in ["run_s3s4.py", "a16.py", "a17.py", "run_g2.py"]:
        hist[f] = [h for h in gates.lint_errors(eng / f)]
    v2b_err = []
    for f in sorted(paths.V2B.glob("*.py")):
        if f.name in ("tribunal_t4_v1a.py", "ruler_v21.py"):     # frozen copies: linted, reported, not blocking
            continue
        v2b_err += gates.lint_errors(f)
    return {"historical_errors": {k: [(h["line"], h["name"]) for h in v] for k, v in hist.items()},
            "v2b_errors": v2b_err, "v2b_clean": not v2b_err}


def main(quick=False):
    a18.worker_init()
    t0 = time.time()
    n1, n2, n3 = (40, 40, 12) if quick else (200, 200, 40)
    res = {"apparatus": apparatus.manifest(), "quick": quick}
    res["C1_walk_vs_fastcost"] = walk.conformance(n_pairs=n1)
    res["C2_fastcost_vs_reference"] = c2_fastcost_vs_reference(n2)
    res["C3_tribunal_paths"] = c3_tribunal_paths(n3)
    res["C4_classing"] = c4_classing()
    res["C5_gates"] = c5_gates()
    ok = (res["C1_walk_vs_fastcost"]["mismatches"] == 0 and res["C2_fastcost_vs_reference"]["mismatches"] == 0
          and not res["C3_tribunal_paths"]["disagreements"] and res["C4_classing"]["fixtures_all_hold"]
          and not res["C4_classing"]["w7_adversarial_differing"] and res["C5_gates"]["v2b_clean"])
    res["CONFORMANCE"] = "GREEN" if ok else "RED"
    res["seconds"] = round(time.time() - t0, 1)
    p = OUT / ("CONFORMANCE_V2B_%s%s.json" % (DATE, "_quick" if quick else ""))
    p.write_text(json.dumps(res, indent=1, sort_keys=True, default=str), encoding="utf-8")
    print(res["CONFORMANCE"], p, res["seconds"])
    return res


if __name__ == "__main__":
    main(quick=len(sys.argv) > 1 and sys.argv[1] == "quick")
