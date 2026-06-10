"""Validator for harmonia/primitives/lattice_void_miner.py (Proposal B engine).

Per feedback_validators_ship_with_docs: the miner makes structured claims
(exact hold counts, certificates, triviality classes); this file is the
paired validator committed alongside it.

The load-bearing test is factored-equals-direct: the miner's histogram-
factored exhaustive evaluation must produce IDENTICAL integer hold counts to
a brute-force nested loop over raw object values using the authoritative
theseus relation evaluator. Same algorithm, same range, same zero-handling
(feedback_track_d_replication_discipline).

Run:  python harmonia/experiments/test_lattice_void_miner.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from theseus.generators.a3_functional_identity import OPERATORS                 # noqa: E402
from theseus.generators.a1_catalog_cross_product import (                       # noqa: E402
    _load_catalog, _get_int, _evaluate_relation,
    KNOT_INTEGER_INVARIANTS, EC_INTEGER_INVARIANTS, RELATIONS,
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH                      # noqa: E402
from harmonia.primitives.lattice_void_miner import (                            # noqa: E402
    LatticeSpec, evaluate_lattice, cell_id, certificate, verify_certificate,
    null_pigeonhole, null_constant_side, void_jaccard_comparator, mine,
)

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


def build_a3_spec() -> LatticeSpec:
    knots = _load_catalog(KNOTS_DB_PATH)
    ecs = _load_catalog(BSD_RICH_DB_PATH)
    side_a = {ki: [v for v in (_get_int(k, ki) for k in knots) if v is not None]
              for ki in KNOT_INTEGER_INVARIANTS}
    side_b = {ei: [v for v in (_get_int(e, ei) for e in ecs) if v is not None]
              for ei in EC_INTEGER_INVARIANTS}
    return LatticeSpec(
        side_a_name="knot", side_b_name="ec",
        side_a=side_a, side_b=side_b,
        operators=dict(OPERATORS), relations=tuple(RELATIONS),
        eval_relation=_evaluate_relation,
    )


def test_factored_equals_direct(spec, cells):
    """Exact integer equality of hold counts: factored vs brute force, on a
    seeded random subset of 48 cells spanning all relations."""
    rng = random.Random(20260610)
    by_rel = {}
    for c in cells:
        by_rel.setdefault(c["rel"], []).append(c)
    sample = []
    for rel, cs in by_rel.items():
        sample.extend(rng.sample(cs, min(12, len(cs))))
    all_ok = True
    for c in sample:
        f = spec.operators[c["f"]]
        g = spec.operators[c["g"]]
        va = spec.side_a[c["inv_a"]]
        vb = spec.side_b[c["inv_b"]]
        direct = 0
        for a in va:
            fa = f(a)
            for b in vb:
                if spec.eval_relation(fa, g(b), c["rel"]):
                    direct += 1
        if direct != c["hold_count"] or len(va) * len(vb) != c["n_eval"]:
            all_ok = False
            print(f"    MISMATCH {cell_id(c)}: direct={direct} "
                  f"factored={c['hold_count']}")
    check(f"factored == direct on {len(sample)} cells (exact integer counts)",
          all_ok)


def test_certificate_soundness(spec, mined):
    """Every exact void must carry a verified certificate (the product-measure
    theorem says certificate-less voids are bugs)."""
    voids = mined["voids"]
    bad = [v for v in voids
           if v["certificate"] is None or not v["certificate_verified"]]
    check(f"all {len(voids)} exact voids have verified certificates",
          not bad, f"{len(bad)} certificate-less/unverified voids: "
                   f"{[v['cell_id'] for v in bad[:5]]}")
    t4 = [v for v in voids if v["triviality_class"] == "T4_NO_CERTIFICATE_BUG"]
    check("no T4 (certificate-less) class assigned", not t4,
          f"{[v['cell_id'] for v in t4[:5]]}")


def test_certificate_completeness(spec, cells):
    """Converse direction: a constructible+verified certificate must imply an
    exact void (verify checks all set pairs hold, which forces hold_rate==1)."""
    rng = random.Random(7)
    sample = rng.sample(cells, 300)
    bad = []
    for c in sample:
        cert = certificate(spec, c)
        if cert is not None and verify_certificate(spec, c, cert):
            if not c["is_exact_void"]:
                bad.append(cell_id(c))
    check("verified certificate => exact void (300-cell sample)", not bad,
          str(bad[:5]))


def test_pigeonhole_mod3_absdiff(spec):
    """The reconciliation keystone: (mod_3, mod_3, abs_diff_le_3) is
    unviolable for ANY integers -- enumeration over the full codomain
    {0,1,2}^2 plus the generic probe."""
    m3 = spec.operators["mod_3"]
    enum_ok = all(abs(a - b) <= 3 for a in range(3) for b in range(3))
    cell = {"f": "mod_3", "g": "mod_3", "inv_a": "determinant",
            "inv_b": "conductor", "rel": "abs_diff_le_3"}
    probe = null_pigeonhole(spec, cell)
    check("(mod_3, mod_3, abs_diff_le_3) unviolable by codomain enumeration",
          enum_ok)
    check("(mod_3, mod_3, abs_diff_le_3) flagged T1 by pigeonhole null",
          probe["killed"])
    # Negative control: equal_mod_2 over mod_3 outputs IS violable (0 vs 1).
    check("negative control: (mod_3, mod_3, equal_mod_2) NOT pigeonhole",
          not null_pigeonhole(spec, dict(cell, rel="equal_mod_2"))["killed"])


def test_jaccard_comparator():
    claim = {"c1": "VOID", "c2": "VOID", "c3": "NONVOID", "c4": "NONVOID"}
    exact = {"c1": "VOID", "c2": "VOID", "c3": "NONVOID", "c4": "NONVOID"}
    a, d, n = void_jaccard_comparator(claim, exact)
    check("jaccard: identical void sets -> agreement 1.0", a == 1.0 and d == 0)
    miss = {"c1": "VOID", "c2": "NONVOID", "c3": "NONVOID", "c4": "NONVOID"}
    a, d, n = void_jaccard_comparator(claim, miss)
    check("jaccard: half-missed voids -> agreement 0.5", abs(a - 0.5) < 1e-9 and d == 1)
    # The imbalance trap the default comparator falls into: a baseline that
    # never says VOID has 0 agreement here, not ~1.0.
    nothing = {k: "NONVOID" for k in claim}
    a, d, n = void_jaccard_comparator(claim, nothing)
    check("jaccard: all-NONVOID baseline -> agreement 0.0 (imbalance guard)",
          a == 0.0 and n == 2)


def test_determinism(spec):
    c1 = evaluate_lattice(spec)
    c2 = evaluate_lattice(spec)
    check("evaluate_lattice deterministic", c1 == c2)


def test_certificate_sabotage(spec, cells):
    """Panel-mandated regression (2026-06-10, CODE lens): verify_certificate
    must REJECT garbage certificates — v1 ignored its cert argument."""
    void = next(c for c in cells if c["is_exact_void"])
    cert = certificate(spec, void)
    check("sabotage control: genuine certificate verifies",
          verify_certificate(spec, void, cert))
    sabotaged = []
    if cert["form"] == "DIVIDES_GCD":
        sabotaged.append(dict(cert, gcd_b=cert["gcd_b"] + 1))
    if cert["form"] == "INTERVAL_WIDTH":
        sabotaged.append(dict(cert, K=cert["K"] - 1))
    sabotaged.append(dict(cert, form="SINGLETON_EQUAL", constant=999))
    sabotaged.append(dict(cert, form="NOT_A_FORM"))
    sabotaged.append(None)
    bad = [s for s in sabotaged if verify_certificate(spec, void, s)]
    check(f"sabotage: {len(sabotaged)} garbage certificates all rejected",
          not bad, f"accepted: {bad}")


def test_constant_side_detects_nf(spec, cells):
    """nf_class_number is constant 1 on its 8 defined knots: every cell over
    it must trip the constant-side null on side A with identity op."""
    target = next(c for c in cells
                  if c["inv_a"] == "nf_class_number" and c["f"] == "identity"
                  and c["inv_b"] == "rank" and c["g"] == "identity"
                  and c["rel"] == "divides")
    res = null_constant_side(spec, target)
    check("constant-side null fires on nf_class_number (raw constant == 1)",
          res["killed"] and "raw column is constant" in res["detail"],
          res["detail"])
    check("nf_class_number cell is an exact void (1 divides everything)",
          target["is_exact_void"],
          f"hold_rate={target['hold_rate']}")


def main():
    print("== lattice_void_miner validator ==")
    spec = build_a3_spec()
    cells = evaluate_lattice(spec)
    n_expect = (len(spec.operators) ** 2 * len(spec.side_a) * len(spec.side_b)
                * len(spec.relations))
    check(f"cell count == {n_expect} (full lattice)", len(cells) == n_expect,
          f"got {len(cells)}")

    test_factored_equals_direct(spec, cells)
    test_determinism(spec)
    test_certificate_sabotage(spec, cells)
    test_pigeonhole_mod3_absdiff(spec)
    test_jaccard_comparator()
    test_constant_side_detects_nf(spec, cells)
    test_certificate_completeness(spec, cells)

    print("  (mining for certificate-soundness test...)")
    mined = mine(spec)
    test_certificate_soundness(spec, mined)

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
