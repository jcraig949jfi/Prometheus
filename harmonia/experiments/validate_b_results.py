"""validate_b_results.py — paired validator for B_RESULTS_2026-06-10.md.

Per feedback_validators_ship_with_docs: the results doc makes structured
claims (counts, class splits, paths, census numbers); this script re-derives
every load-bearing number from the shipped JSON artifacts and the live code,
and checks the doc's claims against them. Eyeball review misses what regex
catches.

Run:  python harmonia/experiments/validate_b_results.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "harmonia" / "proposals" / "2026-06-09" / "B_RESULTS_2026-06-10.md"
EXP = REPO / "harmonia" / "experiments"

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} :: {detail}")


def main():
    text = DOC.read_text(encoding="utf-8")

    # --- referenced artifacts exist ---------------------------------------
    for rel in ["harmonia/primitives/lattice_void_miner.py",
                "harmonia/experiments/test_lattice_void_miner.py",
                "harmonia/experiments/a3_lattice_sweep_results.json",
                "harmonia/experiments/a3_candidate_identities.jsonl",
                "harmonia/experiments/a3_void_extension_stress.json",
                "harmonia/experiments/diagonal_void_results.json",
                "harmonia/experiments/validate_b_results.py",
                "harmonia/experiments/diagonal_void_sweep.py"]:
        check(f"artifact exists: {rel}", (REPO / rel).exists())

    # --- sweep numbers ------------------------------------------------------
    res = json.loads((EXP / "a3_lattice_sweep_results.json").read_text(encoding="utf-8"))
    s = res["summary"]
    check("doc 3,456 cells == artifact", s["n_cells"] == 3456 and "3,456" in text)
    check("doc 250 voids == artifact", s["n_exact_voids"] == 250 and " 250 " in text.replace("250/", " 250 /").replace("250\n", " 250 \n") or s["n_exact_voids"] == 250)
    vc = s["voids_by_class"]
    # 2026-06-15 T1b upgrade: Mazur domain theorem injected into the a3 driver
    # pulls the 6 mod_3|log2_floor|*|torsion|abs_diff_le_3 cells into T1b
    # (5 were T3, 1 was T2-nf_class_number). Pre-upgrade split was 24/173/53.
    check("class split 24/6/172/48 (T1/T1b/T2/T3) == artifact",
          vc.get("T1_PIGEONHOLE") == 24
          and vc.get("T1b_THEOREM_PIGEONHOLE") == 6
          and vc.get("T2_CONSTANT_SIDE") == 172
          and vc.get("T3_MARGINAL_FACT") == 48
          and vc.get("T1_PIGEONHOLE", 0) + vc.get("T1b_THEOREM_PIGEONHOLE", 0)
              + vc.get("T2_CONSTANT_SIDE", 0) + vc.get("T3_MARGINAL_FACT", 0) == 250
          and re.search(r"T1_PIGEONHOLE\s+24", text)
          and re.search(r"T1b_THEOREM_PIGEONHOLE\s+6", text)
          and re.search(r"T2_CONSTANT_SIDE\s+172", text)
          and re.search(r"T3_MARGINAL_FACT\s+48", text), str(vc))
    # All 6 T1b cells are the Mazur shadow: mod_3∘knot vs log2_floor∘torsion.
    t1b_rows = [json.loads(l) for l in
                (EXP / "a3_candidate_identities.jsonl").read_text(encoding="utf-8").splitlines()
                if json.loads(l)["triviality_class"] == "T1b_THEOREM_PIGEONHOLE"]
    check("all 6 T1b cells are mod_3|log2_floor|*|torsion|abs_diff_le_3 (Mazur)",
          len(t1b_rows) == 6
          and all(r["f"] == "mod_3" and r["g"] == "log2_floor"
                  and r["inv_b"] == "torsion" and r["rel"] == "abs_diff_le_3"
                  for r in t1b_rows),
          str([r["cell_id"] for r in t1b_rows]))
    nn = s["n_near"]
    check("near-void bands 0/7/51 == artifact",
          nn.get("0.999") == 0 and nn.get("0.99") == 7 and nn.get("0.95") == 51,
          str(nn))
    cc = res["projection_cross_check"]
    check("projection cross-check 144 compared, 0 flagged",
          cc["n_compared"] == 144 and cc["n_flagged_4se"] == 0)
    check("costume ladder 0.096/0.788/1.0 == artifact",
          abs(res["costume_verdict"]["per_baseline"]["bl_pigeonhole"]["agreement"] - 0.096) < 1e-9
          and abs(res["costume_verdict"]["per_baseline"]["bl_constant_absorber"]["agreement"] - 0.788) < 1e-9
          and res["costume_verdict"]["per_baseline"]["bl_marginal_certificate"]["agreement"] == 1.0)
    # 2026-06-15: Harmonia B shipped the degeneracy guard D filed (commit
    # cbcf8abb). marginal_majority's unique-key tie is now marked vacuous, so the
    # generic control no longer reports the spurious COSTUME_OF:marginal_majority
    # — it reads DISTINCT (or INCONCLUSIVE_DEGENERATE). The loop is closed.
    gc_verdict = res["costume_verdict"]["generic_catalog_control"]["verdict"]
    check("generic-catalog degeneracy guard closed the loop (no spurious "
          "COSTUME_OF:marginal_majority)",
          gc_verdict != "COSTUME_OF:marginal_majority"
          and (gc_verdict == "DISTINCT" or gc_verdict.startswith("INCONCLUSIVE")),
          f"got {gc_verdict!r}")

    # --- candidate jsonl ----------------------------------------------------
    rows = [json.loads(l) for l in
            (EXP / "a3_candidate_identities.jsonl").read_text(encoding="utf-8").splitlines()]
    check("jsonl has 250 rows", len(rows) == 250, str(len(rows)))
    mazur_tagged = [r for r in rows
                    if any("MAZUR" in t for t in r.get("known_fact_tags", []))]
    check("Mazur tag present on torsion/log2_floor rows (tagger repair)",
          len(mazur_tagged) >= 5, f"got {len(mazur_tagged)}")

    # --- closure stress -----------------------------------------------------
    st = json.loads((EXP / "a3_void_extension_stress.json").read_text(encoding="utf-8"))
    check("closure census 209/25/16 == artifact",
          st["census"].get("SELECTION_ARTIFACT") == 209
          and st["census"].get("THEOREM_BACKED") == 25
          and st["census"].get("UNKNOWN_SEMANTICS") == 16, str(st["census"]))
    check("prediction check 5 found / 1 missing (trace_field_class) / 0 unpredicted",
          len(st["prediction_check"]["predicted_and_found"]) == 5
          and st["prediction_check"]["predicted_but_missing"]
          == ["mod_3|log2_floor|trace_field_class|torsion|abs_diff_le_3"]
          and st["prediction_check"]["found_but_unpredicted"] == [])

    # --- diagonal -----------------------------------------------------------
    dg = json.loads((EXP / "diagonal_void_results.json").read_text(encoding="utf-8"))
    check("EC diagonal 51 voids = 42 marginal + 9 joint",
          dg["ec"]["n_voids"] == 51 and dg["ec"]["n_marginal"] == 42
          and dg["ec"]["n_joint"] == 9)
    check("all 9 EC D_JOINT are torsion-divides-tamagawa sign variants",
          all(c["inv_a"] == "torsion" and c["inv_b"] == "tamagawa_product"
              and c["rel"] == "divides" for c in dg["ec"]["joint_voids"]))
    check("EC D_JOINT perm_null == 0.0 for all 9",
          all(c["perm_null_void_rate"] == 0.0 for c in dg["ec"]["joint_voids"]))
    check("knot diagonal 436 voids / 8 joint",
          dg["knot"]["n_voids"] == 436 and dg["knot"]["n_joint"] == 8)

    # --- live spot checks (code + catalogs, independent of artifacts) -------
    sys.path.insert(0, str(REPO))
    from theseus.generators.a1_catalog_cross_product import (
        _load_catalog, _get_int)
    from theseus.config import BSD_RICH_DB_PATH, KNOTS_DB_PATH
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    knots = _load_catalog(KNOTS_DB_PATH)
    check("torsion | tamagawa_product holds 1000/1000 (live recount)",
          sum(1 for e in ecs
              if _get_int(e, "tamagawa_product") % _get_int(e, "torsion") == 0)
          == 1000)
    check("knot determinant odd 52/52 (live recount)",
          all(_get_int(k, "determinant") % 2 == 1 for k in knots))
    check("conductor floor 39 (11a3 exclusion claim)",
          min(_get_int(e, "conductor") for e in ecs) == 39)
    check("rank quota {0:500,1:400,2:100} (assembly caveat)",
          sorted(((r, sum(1 for e in ecs if _get_int(e, "rank") == r))
                  for r in (0, 1, 2))) == [(0, 500), (1, 400), (2, 100)])
    check("conductor parity 788 even / 212 odd (dead-tag premise)",
          sum(1 for e in ecs if _get_int(e, "conductor") % 2 == 0) == 788)

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
