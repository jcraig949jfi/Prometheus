"""ec_rich_diagonal_sweep.py — EC same-object diagonal mining, RICH invariants.

Panel-ranked #1 live target (B_RESULTS §7): the EC diagonal lattice is the one
place the product-measure theorem deliberately fails, so a D_JOINT void is a
candidate WITHIN-OBJECT inter-invariant law. The 2026-06-10 pass used only 4
integer invariants (rank, conductor, tamagawa_product, torsion) and found one
law (torsion | tamagawa_product). This pass widens to 9 integer invariants by
adding the rich BSD fields:

    + sha_an            analytic |Sha| (BSD predicts a perfect square)
    + num_bad_primes    omega(conductor)
    + cm                CM discriminant (0 for non-CM; 995/1000 are 0)
    + signD             sign of the discriminant (+-1)
    + conductor_radical rad(conductor) = product of distinct bad primes

and injects Mazur (torsion order in {1..10,12}) so marginal voids that are
theorem-protected are tagged D_THEOREM rather than over-read.

FALSIFICATION-FIRST. A D_JOINT void is a CANDIDATE, not a finding. Each is
annotated with: perm-null survival rate (P(column-shuffle still voids) — 0.0 is
maximal joint signal), a degeneracy guard (is either transformed column
constant / <=2 valued? then the "joint" structure is low-information), and a
known-math tag where the law is definitional or literature-adjacent. Novel
within-object laws must clear all three to graduate; the honest default is that
they are rediscoveries or artifacts.

Emits harmonia/experiments/ec_rich_diagonal_results.json (flushed from Python,
per feedback_background_output_capture). Does NOT touch the committed Proposal B
diagonal artifact (diagonal_void_results.json) — this is a separate exploration.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from theseus.generators.a3_functional_identity import OPERATORS                 # noqa: E402
from theseus.generators.a1_catalog_cross_product import (                       # noqa: E402
    _load_catalog, _get_int, _evaluate_relation, RELATIONS,
)
from theseus.config import BSD_RICH_DB_PATH                                      # noqa: E402
from harmonia.primitives.lattice_void_miner import evaluate_diagonal_lattice     # noqa: E402

OUT = Path(__file__).parent / "ec_rich_diagonal_results.json"

# 4 original + 5 rich. conductor_radical is the high-cardinality one; cm/signD/
# sha_an are low-cardinality (degeneracy-prone) and carry that caveat.
RICH_EC_INVARIANTS = (
    "rank", "conductor", "tamagawa_product", "torsion",
    "sha_an", "num_bad_primes", "cm", "signD", "conductor_radical",
)

MAZUR = (tuple(range(1, 11)) + (12,),
         "Mazur (1977): |E(Q)_tors| in {1..10,12}")
DOMAIN_THEOREMS = {"torsion": MAZUR}


def known_math_tag(c: dict) -> str:
    """Conservative tags for D_JOINT candidates that are NOT novel: definitional
    identities or literature-adjacent laws. Empty string => not (yet) explained
    by known mathematics — the only cells worth a second look.

    NOTE on sign/operator variants (2026-06-15): the a3 operators identity/abs/
    neg/sq_mod_100 all PRESERVE PARITY, and `divides` is sign-invariant
    (b % (-a) == 0  iff  a | b). So one underlying law generates a whole family
    of cells under these operators; the tagger must recognise the family, not
    just the identity-on-identity representative — otherwise it reports the same
    law N times as 'untagged survivors' (the v1 mistake, caught on first run)."""
    a, b, rel = c["inv_a"], c["inv_b"], c["rel"]
    pair = {a, b}

    # --- conductor / radical: ONE fact (shared prime support) in two guises ---
    if pair == {"conductor", "conductor_radical"}:
        if rel == "equal_mod_2":
            return ("DEFINITIONAL: conductor == rad(conductor) (mod 2). N and "
                    "rad(N) share their prime support, so 2|N iff 2|rad(N); all "
                    "parity-preserving operators inherit it.")
        if rel == "divides" and a == "conductor_radical":
            return ("DEFINITIONAL: rad(conductor) | conductor by construction "
                    "(sign-invariant, so every neg/abs variant is the same law).")

    # --- torsion | tamagawa_product (Lorenzini 2011), any sign variant ---------
    if a == "torsion" and b == "tamagawa_product" and rel == "divides":
        return ("LITERATURE (Lorenzini 2011): |E(Q)_tors| | prod(c_p), with known "
                "exceptions below the catalog conductor floor (e.g. 11a3). Same "
                "law found in the 2026-06-10 4-invariant pass; sign-variant here.")

    # --- low-information / degenerate columns ---------------------------------
    if {"num_bad_primes", "conductor_radical"} == pair:
        return ("STRUCTURAL: num_bad_primes = omega(rad) -- count vs product of "
                "the same prime set; any size relation is a primorial fact.")
    if "cm" in pair:
        return ("DEGENERATE: cm = 0 for 995/1000 curves -- relations over it are "
                "absorbing-element facts, not joint structure.")
    if "signD" in pair:
        return "LOW-INFO: signD in {-1,1}; 2-valued column."
    if "sha_an" in pair:
        return ("LOW-INFO: sha_an = 1 for 962/1000 (BSD square, near-constant).")
    return ""


def degeneracy_flags(c: dict, side) -> dict:
    """Is the 'joint' void actually low-information? Recompute the two
    transformed columns and report unique-value counts. A column with <=2
    distinct transformed values cannot carry much joint structure regardless of
    the perm-null."""
    f, g = OPERATORS[c["f"]], OPERATORS[c["g"]]
    try:
        ua = len({f(v) for v in side[c["inv_a"]] if v is not None})
        ub = len({g(v) for v in side[c["inv_b"]] if v is not None})
    except (ValueError, OverflowError):
        ua = ub = -1
    return {"uniq_a": ua, "uniq_b": ub,
            "thin_column": ua <= 2 or ub <= 2}


def main():
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    side = {inv: [_get_int(e, inv) for e in ecs] for inv in RICH_EC_INVARIANTS}
    n_def = {inv: sum(1 for v in side[inv] if v is not None) for inv in side}

    cells = evaluate_diagonal_lattice(
        side, dict(OPERATORS), tuple(RELATIONS), _evaluate_relation,
        domain_theorems=DOMAIN_THEOREMS)

    voids = [c for c in cells if c["is_exact_void"]]
    by_jclass = Counter(c.get("joint_class") for c in voids)
    joint = [c for c in voids if c.get("joint_class") == "D_JOINT"]

    # Falsification-first triage of the candidate laws.
    for c in joint:
        c["known_math"] = known_math_tag(c)
        c["degeneracy"] = degeneracy_flags(c, side)
    # A candidate "survives to second look" only if: maximal joint signal
    # (perm-null 0), not thin, and no known-math explanation.
    survivors = [c for c in joint
                 if c["perm_null_void_rate"] == 0.0
                 and not c["degeneracy"]["thin_column"]
                 and not c["known_math"]]

    print(f"=== EC rich diagonal: {len(cells)} cells, n={len(ecs)} curves, "
          f"{len(RICH_EC_INVARIANTS)} invariants ===")
    print(f"  invariants: {RICH_EC_INVARIANTS}")
    print(f"  exact voids: {len(voids)}  by_joint_class={dict(by_jclass)}")
    print(f"\n  D_JOINT candidates ({len(joint)}; perm-null = P(survives column "
          f"shuffle), 0.0 = maximal joint signal):")
    for c in sorted(joint, key=lambda x: (x["perm_null_void_rate"],
                                          -x["degeneracy"]["uniq_a"])):
        deg = c["degeneracy"]
        tag = c["known_math"] or "** NO KNOWN-MATH TAG **"
        print(f"    {c['f']}({c['inv_a']}) {c['rel']} {c['g']}({c['inv_b']})"
              f"  perm={c['perm_null_void_rate']:.3f}"
              f"  uniq=({deg['uniq_a']},{deg['uniq_b']})"
              f"{'  [THIN]' if deg['thin_column'] else ''}")
        print(f"        {tag}")

    print(f"\n  D_THEOREM voids (population-true marginal, theorem-explained): "
          f"{by_jclass.get('D_THEOREM', 0)}")
    for c in [c for c in voids if c.get("joint_class") == "D_THEOREM"][:8]:
        print(f"    {c['f']}({c['inv_a']}) {c['rel']} {c['g']}({c['inv_b']})"
              f"  cites={c.get('theorems_cited')}")

    print(f"\n  SURVIVORS (perm-null 0, not thin, no known-math tag): "
          f"{len(survivors)}")
    for c in survivors:
        print(f"    ** {c['f']}({c['inv_a']}) {c['rel']} {c['g']}({c['inv_b']}) "
              f"uniq=({c['degeneracy']['uniq_a']},{c['degeneracy']['uniq_b']})")
    if not survivors:
        print("    (none — every maximal-signal joint void is a known/"
              "definitional law or a thin-column artifact. The honest number.)")

    out = {
        "meta": {"date": "2026-06-15", "author": "Harmonia_M2_D",
                 "design": "EC same-object diagonal, 9 integer invariants, "
                           "Mazur injected; D_JOINT = candidate within-object law",
                 "n_curves": len(ecs),
                 "invariants": list(RICH_EC_INVARIANTS),
                 "n_defined": n_def,
                 "caveats": ["EC catalog quota-stratified (rank 500/400/100)",
                             "cm/signD/sha_an are low-cardinality (degeneracy-"
                             "prone); see degeneracy flags + known_math tags",
                             "conductor floor 39 (excludes torsion|tamagawa "
                             "counterexample 11a3)"]},
        "n_cells": len(cells),
        "n_voids": len(voids),
        "by_joint_class": dict(by_jclass),
        "joint_candidates": [
            {k: c[k] for k in ("f", "g", "inv_a", "inv_b", "rel", "n_eval",
                               "perm_null_void_rate", "known_math", "degeneracy")}
            for c in sorted(joint, key=lambda x: x["perm_null_void_rate"])],
        "survivors": [c["f"] + "(" + c["inv_a"] + ") " + c["rel"] + " "
                      + c["g"] + "(" + c["inv_b"] + ")" for c in survivors],
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
