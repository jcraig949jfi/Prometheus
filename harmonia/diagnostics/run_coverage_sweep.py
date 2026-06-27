"""run_coverage_sweep.py — run the reusable coverage diagnostic across every
instrument and emit the sweep table.

Instruments measured (vocabulary extracted from the ACTUAL code, not described):
  1. EC void-miner (a3/EC-rich diagonal)   -> coverage_diagnostic.ec_*  (regression)
  2. a3 cross-product knot x EC            -> PROOF-DEAD (product-measure theorem)
  3. Apollo Frame-H primitive set          -> 24 typed primitives
  4. Icarus R0-R12 reasoning ladder        -> 13 frozen rungs

Each curated target list is ILLUSTRATIVE, hand-curated, and stated as such. The
robust signal is the SHAPE (perfect-in-class + zero-out-of-class = ceiling),
not the exact coverage percentage. [feedback_distinguish_B1_B2]

Run:
    PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/diagnostics/run_coverage_sweep.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from harmonia.diagnostics.coverage_diagnostic import (   # noqa: E402
    HypothesisClassSpec, Target, coverage, render,
    ec_catalog_spec_and_targets,
)

OUT = Path(__file__).parent / "coverage_sweep_results.json"


# ---------------------------------------------------------------------------
# Instrument 2: a3 catalog cross-product (knot x EC). PROOF-DEAD.
# The product-measure theorem (lattice_void_miner.py header) proves the joint
# distribution of (inv_a(obj_a), inv_b(obj_b)) under cross-product pairing is
# the PRODUCT of marginals: every exact void is a set-level statement about two
# single-catalog value ranges, never a knot<->EC correspondence. The class can
# express NO genuine cross-domain law by construction. B1_EXHAUSTED_BY_PROOF.
# ---------------------------------------------------------------------------
def a3_cross_spec_and_targets():
    from theseus.generators.a3_functional_identity import OPERATORS
    from theseus.generators.a1_catalog_cross_product import (
        RELATIONS, KNOT_INTEGER_INVARIANTS, EC_INTEGER_INVARIANTS)
    n_ops, n_rel = len(OPERATORS), len(RELATIONS)
    n_pairs = len(KNOT_INTEGER_INVARIANTS) * len(EC_INTEGER_INVARIANTS)
    class_size = n_ops * n_ops * n_pairs * n_rel

    spec = HypothesisClassSpec(
        instrument_name="a3 cross-product (knot x EC functional identity)",
        vocabulary={
            "operators": list(OPERATORS.keys()),
            "relations": list(RELATIONS),
            "knot_invariants": list(KNOT_INTEGER_INVARIANTS),
            "ec_invariants": list(EC_INTEGER_INVARIANTS),
        },
        class_size=class_size,
        claim_shape="rel(f(inv_i(knot)), g(inv_j(EC))) over the FULL knot x EC "
                    "cross-product (independent objects)",
        breadth="narrow",
        proof_dead=True,
        proof_note="product-measure theorem: cross-product pairing makes the "
                   "joint = product of marginals; every exact void is a "
                   "single-catalog set-fact, NEVER a knot<->EC correspondence "
                   "(lattice_void_miner.py decision procedure, validated 34/34)",
        notes="the marginal-pairing null is DEGENERATE by theorem; no void can "
              "ever carry cross-domain content",
    )
    # Curated 'targets' = the kinds of structure a knot/EC cross instrument would
    # need to express to be a discovery engine. ALL out-of-class: the theorem
    # forbids any genuine cross-object joint law from this pairing.
    targets = [
        Target("Any genuine knot<->EC numerical correspondence", "PROOF_DEAD",
               note="product-measure theorem: joint = product of marginals; "
                    "no cross-object content possible from independent pairing"),
        Target("In-catalog marginal set-fact (e.g. 'all knot determinants odd')",
               "UNARY",
               note="a single-catalog property; the only 'content' a void can "
                    "cite — and it is a fact about ONE catalog, not a relation"),
        Target("Cross-object pairing (isogeny/twist orbits)", "CROSS_OBJECT",
               note="would need a NON-product pairing (the diagonal), which is a "
                    "DIFFERENT instrument; the cross-product cannot express it"),
        Target("Distributional knot-vs-EC law (spectra, sequences)",
               "DISTRIBUTIONAL", note="sequence/distribution, not two scalars"),
        Target("Real-valued knot/EC invariant relation (hyperbolic volume vs "
               "regulator)", "REAL_VALUED", note="non-integer; outside the lattice"),
    ]
    return spec, targets


# ---------------------------------------------------------------------------
# Instrument 3: Apollo Frame-H primitive set (typed composition substrate).
# Hypothesis class = the 24 typed primitives + the type-compatibility lattice
# that governs which can be wired together. A 'law/capability' is expressible
# iff it can be assembled from these primitives respecting types. Curated
# target list = a spread of reasoning capabilities across domains. We tag each
# by whether the primitive set + typed wiring can express it, and if not, the
# axis (mostly COMPOSITIONAL: needs a primitive or a wiring shape not present).
# ---------------------------------------------------------------------------
def apollo_spec_and_targets():
    from apollo.src.primitive_types import PRIMITIVE_TYPES
    prims = sorted(PRIMITIVE_TYPES)
    out_types = {v[1] for v in PRIMITIVE_TYPES.values()}

    spec = HypothesisClassSpec(
        instrument_name="Apollo Frame-H primitive set (typed composition)",
        vocabulary={
            "primitives": prims,
            "output_types": sorted(out_types),
        },
        class_size=len(prims),   # fixed finite vocabulary; chains explode but the
                                 # binding constraint is the 24-primitive alphabet
        claim_shape="a typed DAG composed from a fixed alphabet of "
                    f"{len(prims)} primitives, wired under a coarse numeric/"
                    "bool/str type lattice",
        breadth="narrow",
        notes="the type lattice (int/float/probability/bool/str/list/graph) is "
              "coarse; many capabilities need primitives or types not in the set",
    )
    # Curated reasoning-capability targets (illustrative). 'found' marks the ones
    # Apollo demonstrably assembled (per memory: forward_chain/typed-state
    # compositions; bayesian_update; fencepost). Out-of-class -> the axis.
    targets = [
        Target("Logical entailment (modus ponens chain)", "IN_CLASS", found=True,
               note="modus_ponens + negate + check_transitivity present & typed"),
        Target("Bayesian belief update", "IN_CLASS", found=True,
               note="bayesian_update primitive present, probability-typed"),
        Target("Fencepost / off-by-one counting", "IN_CLASS", found=True,
               note="fencepost_count + all_but_n present"),
        Target("Constraint satisfaction over a finite domain", "IN_CLASS",
               found=True, note="solve_constraints + pigeonhole_check present"),
        Target("Forward-chaining multi-step deduction (R2 transformer)",
               "IN_CLASS", found=True,
               note="dag_traverse/topological_sort chainable under types "
                    "(Apollo R2 keystone, 2026-06-09)"),
        Target("Theory-of-mind nested belief (Sally-Anne, 2nd order)", "IN_CLASS",
               found=False, note="sally_anne_test + track_beliefs present but "
                                  "untyped ('any'); higher-order nesting unproven"),
        Target("Probabilistic graphical-model inference (junction tree)",
               "ARITY_GE_3", note="needs joint over many nodes; no primitive "
                                  "composes graph + probability jointly"),
        Target("Real-valued optimization / gradient reasoning", "REAL_VALUED",
               note="no continuous-optimization primitive; type lattice has "
                    "float but no optimizer op"),
        Target("Natural-language semantic parsing", "RELATION_OOV",
               note="no parsing primitive; str-typed ops are prompt fragments"),
        Target("Recursive / self-referential reasoning (fixpoint)",
               "COMPOSITIONAL", note="DAG substrate is acyclic; no recursion/"
                                     "fixpoint wiring shape in the composition op"),
        Target("Analogical mapping across domains", "COMPOSITIONAL",
               note="no structure-mapping primitive; would need a new op + a "
                    "cross-representation type"),
        Target("Continuous temporal/dynamical simulation", "REAL_VALUED",
               note="temporal_order is discrete-categorical; no ODE/sim op"),
    ]
    return spec, targets


# ---------------------------------------------------------------------------
# Instrument 4: Icarus R0-R12 reasoning ladder (capability vocabulary).
# Hypothesis class = the 13 frozen rungs. A reasoning capability is
# 'expressible/locatable' iff it maps onto a rung the ladder can falsification-
# test. Curated targets = a spread of reasoning capabilities. The ladder is
# unusually BROAD (it spans pattern-response through open-ended research), so
# the interesting question is whether the SURVEYED capabilities mostly land
# on a rung (broad coverage -> not a ceiling) or fall between/outside rungs.
# ---------------------------------------------------------------------------
def icarus_spec_and_targets():
    from agents.icarus.ladder import TIER_LADDER
    rungs = [t.tier_id for t in TIER_LADDER]

    spec = HypothesisClassSpec(
        instrument_name="Icarus R0-R12 reasoning ladder",
        vocabulary={"rungs": rungs,
                    "rung_names": [t.name for t in TIER_LADDER]},
        class_size=len(rungs),
        claim_shape="a single ordinal capability tier R0..R12, each with a "
                    "frozen falsification test (perturbation that lower tiers fail)",
        breadth="broad",
        notes="ordinal/1-D ladder: spans pattern-response -> open-ended research; "
              "broad in capability range but 1-dimensional (no orthogonal axes "
              "in THIS module; the F/M/H dimensions live elsewhere)",
    )
    # Curated reasoning-capability targets. 'found' = the ladder has a rung that
    # cleanly locates+falsification-tests it. Most land ON a rung (broad class).
    # Out-of-class = capabilities the 1-D ordinal ladder cannot place.
    targets = [
        Target("Paraphrase-robust single operation", "IN_CLASS", found=True,
               note="R1 local operation; R0/R1 falsification tests"),
        Target("Multi-step chaining with distractor", "IN_CLASS", found=True,
               note="R2 multi-step execution"),
        Target("Constraint tracking + inconsistency rejection", "IN_CLASS",
               found=True, note="R3 (Icarus validated R0-R3 climb, 2026-05-29)"),
        Target("Strategy selection by structure", "IN_CLASS", found=True,
               note="R4"),
        Target("Counterfactual branch maintenance", "IN_CLASS", found=True,
               note="R5 (cleared 2026-06-10)"),
        Target("Error localization + local repair", "IN_CLASS", found=True,
               note="R6 (interface walls fixed 2026-06-15)"),
        Target("Representation re-encoding", "IN_CLASS", found=False,
               note="R8 rung exists; not yet reached/validated"),
        Target("Load-bearing compositional synthesis", "IN_CLASS", found=False,
               note="R9 rung exists; falsification test defined; not reached"),
        Target("Epistemic self-modeling (knows what it lacks)", "IN_CLASS",
               found=False, note="R10 rung exists; not reached"),
        Target("Open-ended research under falsification", "IN_CLASS", found=False,
               note="R12 rung exists; not reached"),
        Target("Parallel/ensemble reasoning (many lenses at once)", "OTHER",
               note="orthogonal to the ordinal ladder; a panel/breadth axis, "
                    "not a single tier — the 1-D rung vocabulary can't place it"),
        Target("Calibration / confidence quality as a graded measure", "OTHER",
               note="a continuous quality axis, not an ordinal rung; lives in "
                    "the orthogonal M-dimension, absent from THIS module"),
    ]
    return spec, targets


# ---------------------------------------------------------------------------
def main():
    cases = [
        ("EC_void_miner_catalog", *ec_catalog_spec_and_targets()),
        ("a3_cross_product", *a3_cross_spec_and_targets()),
        ("apollo_primitives", *apollo_spec_and_targets()),
        ("icarus_ladder", *icarus_spec_and_targets()),
    ]
    reports = {}
    for key, spec, targets in cases:
        rep = coverage(spec, targets)
        print(render(rep))
        print()
        reports[key] = rep.to_dict()

    # Sweep table (markdown rows -> stdout + json).
    print("=" * 74)
    print("SWEEP TABLE")
    print("=" * 74)
    hdr = ("instrument", "class_size", "cover%", "in-recall", "out%",
           "top axes", "verdict")
    print(f"{hdr[0]:<34} {hdr[1]:>9} {hdr[2]:>6} {hdr[3]:>9} {hdr[4]:>5}  {hdr[6]}")
    for key, r in reports.items():
        rec = "n/a" if r["in_class_recall"] is None else f"{r['in_class_recall']:.0%}"
        cov = f"{r['expressible_fraction']:.0%}"
        outp = f"{r['out_of_class_fraction']:.0%}"
        print(f"{r['instrument'][:34]:<34} {r['class_size']:>9} {cov:>6} "
              f"{rec:>9} {outp:>5}  {r['verdict']}")

    OUT.write_text(json.dumps(reports, indent=1), encoding="utf-8")
    print(f"\nWrote {OUT}")
    return reports


if __name__ == "__main__":
    main()
