"""Third-family reachability certificate (AMENDMENT 7 section B).

Run BEFORE any evolutionary/search run of slice 3. Evaluates S1-S5 for every
family in the frozen catalog, in lexicographic order, and selects the FIRST
family that satisfies all five. Transplant performance plays no part: no arm
has been executed at this point.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import basis_v2 as B    # noqa: E402
import basis_v3 as V    # noqa: E402
import engine as E      # noqa: E402

DEV_N = 2
VALIDATION_N = 300
SOLVE = 0.99
COMPOSE_BUDGET = 5 * 10 ** 6
ORGAN_BUDGET = 100000
SLICE2C_FAMILIES = ("list_sum", "list_prod_mod")


def _acc(source, instances):
    art = E.Artifact.from_modules(
        dict(E.base_image(), search=E.base_image()["search"] + source))
    r = E.Recipient.fresh(seed=11)
    r.load(art)
    return r.run_tasks(instances, E.Escrow(10 ** 7))["accuracy"]


def certify(family):
    seed = E.tribunal_entropy("v3cert-" + family, 0)
    dev = V.tasks(family, DEV_N, seed)
    val = V.tasks(family, VALIDATION_N, seed + 1)
    long_val = V.tasks(family, VALIDATION_N, seed + 2, V.EXTRAPOLATION_LENGTHS)
    rec = {"family": family}

    rec["S1_unseen_in_slice2c"] = family not in SLICE2C_FAMILIES

    # S2 basis insufficiency, with and without the trailing parameter
    s2 = {}
    for label, with_last in (("without_last", False), ("with_last", True)):
        vecs, golds = [], []
        for t in dev:
            nums = [int(v) for v in re.findall(r"-?\d+", t["prompt"])]
            row = nums[:E.TERMINALS] + ([nums[-1]] if with_last else [])
            while len(row) < E.TERMINALS:
                row.append(0)
            vecs.append(row)
            golds.append(t["gold"])
        esc = E.Escrow(COMPOSE_BUDGET)
        got = E._compose_v2(vecs, golds, esc, COMPOSE_BUDGET)
        acc = _acc(E._discovered_solver_source(family, got[0]), val) if got else None
        s2[label] = {"found": bool(got), "validated_accuracy": acc,
                     "solves": bool(acc is not None and acc >= SOLVE)}
    rec["S2_basis_insufficient"] = dict(
        s2, **{"pass": not (s2["without_last"]["solves"] or s2["with_last"]["solves"])})

    # S3 reachable with the organ plus admissible hole fillings
    esc2 = E.Escrow(ORGAN_BUDGET)
    found = V.search_organ_holes(family, dev, esc2, ORGAN_BUDGET)
    acc3 = _acc(found[0]["source"], val) if found else None
    long3 = _acc(found[0]["source"], long_val) if found else None
    rec["S3_reachable_with_organ"] = {
        "holes": ({"init": found[0]["init"], "body": found[0]["body"],
                   "final": found[0]["final"]} if found else None),
        "charges": esc2.spent,
        "validated_accuracy": acc3,
        "pass": bool(found and acc3 is not None and acc3 >= SOLVE),
    }

    # S4 independently falsifiable, S5 variable-length extrapolation
    rec["S5_extrapolates"] = {"accuracy_at_extrapolation": long3,
                              "pass": bool(long3 is not None and long3 >= SOLVE)}
    if rec["S3_reachable_with_organ"]["pass"]:
        art = E.Artifact.from_modules(
            dict(E.base_image(), search=E.base_image()["search"] + found[0]["source"]),
            generation=E.FROZEN_GENERATION)
        trib = V.Tribunal3.after_freeze(art, family)
        sc = trib.score(art)
        # a hostile tribunal must also REJECT something: the decorative fossil
        sham_art = E.Artifact.from_modules(
            dict(E.base_image(), search=E.base_image()["search"] + E.shortcut_solver_source()),
            generation=E.FROZEN_GENERATION)
        sham_sc = V.Tribunal3.after_freeze(sham_art, family).score(sham_art)
        rec["S4_falsifiable"] = {
            "correct_solver": sc,
            "rejects_a_non_solver": sham_sc["held_out_extrapolation"] < 0.10,
            "pass": bool(sc["counterexample_accuracy"] >= SOLVE and sc["metamorphic_pass"]
                         and sham_sc["held_out_extrapolation"] < 0.10),
        }
    else:
        rec["S4_falsifiable"] = {"pass": False, "note": "not reachable, not evaluated"}

    rec["ADMISSIBLE"] = bool(rec["S1_unseen_in_slice2c"]
                             and rec["S2_basis_insufficient"]["pass"]
                             and rec["S3_reachable_with_organ"]["pass"]
                             and rec["S4_falsifiable"]["pass"]
                             and rec["S5_extrapolates"]["pass"])
    return rec


def main():
    rows = []
    selected = None
    for fam in sorted(V.CATALOG):          # lexicographic, declared in advance
        r = certify(fam)
        rows.append(r)
        if r["ADMISSIBLE"] and selected is None:
            selected = fam
            break                           # FIRST admissible family wins
    out = {
        "written_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "organ_sha256": json.loads((HERE / "ORGAN_2026-09-22.json").read_text())["organ_sha256"],
        "catalog": sorted(V.CATALOG),
        "selection_rule": "lexicographic; first family satisfying S1-S5; "
                          "transplant performance plays no part",
        "examined_in_order": [r["family"] for r in rows],
        "selected_family": selected,
        "verdict": ("SELECTED " + selected) if selected else "NO_ADMISSIBLE_THIRD_FAMILY",
        "candidates": rows,
        "status": "CERTIFICATE ONLY -- no arm has been executed",
    }
    (HERE / "THIRD_FAMILY_CERTIFICATE_2026-09-22.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if selected else 2


if __name__ == "__main__":
    raise SystemExit(main())
