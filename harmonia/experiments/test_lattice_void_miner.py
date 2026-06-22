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
    null_tautology, null_theorem_pigeonhole, evaluate_diagonal_lattice,
)

# Mazur (1977): the order of E(Q)_tors lies in {1..10, 12}. Finite stand-in for
# the THEOREM-true domain of the EC `torsion` invariant (used by T1b tests).
MAZUR_TORSION = (tuple(range(1, 11)) + (12,), "Mazur (1977): |E(Q)_tors| in {1..10,12}")

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


def _mazur_spec(domain_theorems=None, tautology_check=None):
    """Synthetic Mazur-shaped cross-product: mod_3(knot_inv) vs log2_floor(tors),
    abs_diff_le_3. side A spans all mod-3 residues; side B is exactly the
    Mazur-realizable torsion orders. The (mod_3, log2_floor, abs_diff_le_3) cell
    is an exact void that plain pigeonhole MISSES (2**20 -> log2_floor 20) but
    the Mazur-restricted theorem-pigeonhole catches."""
    return LatticeSpec(
        side_a_name="knot", side_b_name="ec",
        side_a={"kinv": list(range(1, 30))},
        side_b={"tors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]},
        operators={k: OPERATORS[k] for k in ("identity", "mod_3", "log2_floor")},
        relations=("abs_diff_le_3", "divides", "equal", "equal_mod_2"),
        eval_relation=_evaluate_relation,
        domain_theorems=domain_theorems or {},
        tautology_check=tautology_check,
    )


_MAZUR_CELL = "mod_3|log2_floor|kinv|tors|abs_diff_le_3"


def test_t1b_theorem_pigeonhole():
    """The owed §4 upgrade: the Mazur interval cell routes to T3 with no domain
    theorem (genuine-looking marginal fact) and to T1b once Mazur is injected
    (population-true, theorem-explained). Same cell, knowledge-dependent class."""
    spec_naive = _mazur_spec()
    naive = {v["cell_id"]: v for v in mine(spec_naive)["voids"]}
    check("Mazur cell is an exact void", _MAZUR_CELL in naive,
          f"voids: {list(naive)[:6]}")
    if _MAZUR_CELL in naive:
        check("Mazur cell classes as T3 WITHOUT a domain theorem",
              naive[_MAZUR_CELL]["triviality_class"] == "T3_MARGINAL_FACT",
              naive[_MAZUR_CELL]["triviality_class"])
        check("plain pigeonhole MISSES the Mazur cell (feeds 2**20 to torsion)",
              not null_pigeonhole(spec_naive, naive[_MAZUR_CELL]["cell"])["killed"])

    spec_mazur = _mazur_spec(domain_theorems={"tors": MAZUR_TORSION})
    mz = {v["cell_id"]: v for v in mine(spec_mazur)["voids"]}
    if _MAZUR_CELL in mz:
        check("Mazur cell reclasses to T1b WITH Mazur injected",
              mz[_MAZUR_CELL]["triviality_class"] == "T1b_THEOREM_PIGEONHOLE",
              mz[_MAZUR_CELL]["triviality_class"])
        check("T1b void cites the Mazur theorem",
              MAZUR_TORSION[1] in mz[_MAZUR_CELL]["nulls"]["theorem_pigeonhole"]["theorems"],
              str(mz[_MAZUR_CELL]["nulls"]["theorem_pigeonhole"]["theorems"]))

    # Negative control: a divides-cell where Mazur is NOT load-bearing must stay
    # off T1b. divides(identity(kinv), identity(tors)) fails for arbitrary
    # integers even within the Mazur domain (2 does not divide every order).
    neg = {"f": "identity", "g": "identity", "inv_a": "kinv",
           "inv_b": "tors", "rel": "divides"}
    check("negative control: divides cell NOT theorem-pigeonhole under Mazur",
          not null_theorem_pigeonhole(spec_mazur, neg)["killed"])
    check("theorem-pigeonhole is inert when domain_theorems empty",
          not null_theorem_pigeonhole(spec_naive, neg)["killed"]
          and "no domain theorems" in null_theorem_pigeonhole(spec_naive, neg)["detail"])


def test_t0_tautology():
    """T0 guards self-test generators (b1: predicted==actual from one flip
    table). Two routes: injected tautology_check, and the built-in structural
    detector (same (op,invariant) both sides + reflexive relation)."""
    # Injected route: a constant 'divides' void that WOULD be T2, but the spec
    # declares the two sides are one computation -> must classify T0 first.
    def tcheck(c):
        return ("b1: predicted and actual are one flip-table computation"
                if {c["inv_a"], c["inv_b"]} <= {"predicted", "actual"} else None)
    spec = LatticeSpec(
        side_a_name="run", side_b_name="run",
        side_a={"predicted": [1, 1, 1, 1]}, side_b={"actual": [3, 6, 9, 12]},
        operators={"identity": OPERATORS["identity"]},
        relations=("divides",), eval_relation=_evaluate_relation,
        tautology_check=tcheck,
    )
    voids = {v["cell_id"]: v for v in mine(spec)["voids"]}
    cid = "identity|identity|predicted|actual|divides"
    check("T0: injected tautology_check beats T2 on a declared self-comparison",
          cid in voids and voids[cid]["triviality_class"] == "T0_TAUTOLOGY",
          str({k: v["triviality_class"] for k, v in voids.items()}))

    # Structural route: same (op, invariant) both sides + reflexive relation.
    struct_cell = {"f": "identity", "g": "identity", "inv_a": "x",
                   "inv_b": "x", "rel": "equal"}
    sspec = LatticeSpec(
        side_a_name="s", side_b_name="s", side_a={"x": [5]}, side_b={"x": [5]},
        operators={"identity": OPERATORS["identity"]},
        relations=("equal",), eval_relation=_evaluate_relation,
    )
    check("T0: structural detector fires on reflexive self-comparison",
          null_tautology(sspec, struct_cell)["killed"])
    # Negative controls: distinct invariants stay silent.
    check("T0 negative: distinct columns are not a tautology",
          not null_tautology(sspec, dict(struct_cell, inv_b="y"))["killed"])
    # Reflexivity gate: a NON-reflexive relation must keep the structural
    # detector silent even on identical (op, invariant) sides. (All four a3
    # relations are reflexive, so a custom strict-less relation is needed to
    # exercise this branch.)
    def strict_less(a, b, rel):
        return a < b
    nr_spec = LatticeSpec(
        side_a_name="s", side_b_name="s", side_a={"x": [5]}, side_b={"x": [5]},
        operators={"identity": OPERATORS["identity"]},
        relations=("strict_less",), eval_relation=strict_less,
    )
    check("T0 negative: non-reflexive relation -> structural detector silent",
          not null_tautology(nr_spec, dict(struct_cell, rel="strict_less"))["killed"])
    check("T0 inert by default (no tautology_check, distinct a3 columns) "
          "-> a3 backward-compatible",
          not null_tautology(build_a3_spec(),
                             {"f": "identity", "g": "identity",
                              "inv_a": "determinant", "inv_b": "rank",
                              "rel": "equal"})["killed"])


def test_d_theorem_diagonal():
    """Diagonal D_THEOREM refinement: a marginal diagonal void that holds over
    the Mazur domain is population-true (D_THEOREM); a genuine within-object
    joint law (rad|n) stays D_JOINT regardless of any domain theorem."""
    ops = {k: OPERATORS[k] for k in ("identity", "mod_3", "log2_floor")}
    # rad|n: radical divides the integer -- a real within-object law. Not a
    # set-product fact (rad=10 does not divide n=12), so D_JOINT.
    side_joint = {"n": [12, 18, 20, 30, 50], "rad": [6, 6, 10, 30, 10]}
    jcells = evaluate_diagonal_lattice(
        side_joint, ops, ("divides",), _evaluate_relation,
        n_perms=50, domain_theorems={"n": MAZUR_TORSION})
    rad_n = next((c for c in jcells if c["inv_a"] == "rad" and c["inv_b"] == "n"
                  and c["f"] == "identity" and c["g"] == "identity"
                  and c["rel"] == "divides"), None)
    check("diagonal rad|n is an exact void", rad_n and rad_n["is_exact_void"])
    if rad_n and rad_n["is_exact_void"]:
        check("rad|n stays D_JOINT (real joint law, theorem cannot relabel it)",
              rad_n["joint_class"] == "D_JOINT", rad_n.get("joint_class"))

    # Marginal interval void over a Mazur-bounded torsion column -> D_THEOREM
    # with theorem; plain D_MARGINAL without.
    side_marg = {"tors": [1, 2, 4, 8, 12, 3, 5, 1, 2, 10],
                 "res": [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]}
    args = (side_marg, ops, ("abs_diff_le_3",), _evaluate_relation)
    with_thm = evaluate_diagonal_lattice(*args, n_perms=50,
                                         domain_theorems={"tors": MAZUR_TORSION})
    no_thm = evaluate_diagonal_lattice(*args, n_perms=50)

    def pick(cells):
        return next((c for c in cells if c["inv_a"] == "tors" and c["inv_b"] == "res"
                     and c["f"] == "log2_floor" and c["g"] == "identity"
                     and c["rel"] == "abs_diff_le_3"), None)
    ct, cn = pick(with_thm), pick(no_thm)
    check("marginal interval cell is an exact void", ct and ct["is_exact_void"])
    if ct and ct["is_exact_void"]:
        check("marginal cell -> D_THEOREM when Mazur supplied",
              ct["joint_class"] == "D_THEOREM", ct.get("joint_class"))
        check("D_THEOREM cites the theorem",
              MAZUR_TORSION[1] in ct.get("theorems_cited", []),
              str(ct.get("theorems_cited")))
        check("same cell -> D_MARGINAL when no theorem supplied "
              "(diagonal backward-compatible)",
              cn["joint_class"] == "D_MARGINAL", cn.get("joint_class"))


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
    test_t1b_theorem_pigeonhole()
    test_t0_tautology()
    test_d_theorem_diagonal()

    print("  (mining for certificate-soundness test...)")
    mined = mine(spec)
    test_certificate_soundness(spec, mined)

    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
