"""The fixed job manifest. After freeze the runner consumes THIS and nothing else.

WHY. The predecessor allocated by percentage under a UCB producer with an exploration
floor, which means what ran depended on what had already run. For a search that is the
right design. For a verification campaign it destroys the guarantee the campaign exists
to provide: a preregistered hypothesis tested on a preregistered sample.

So every run is enumerated here before launch: hypothesis, bundle, cell or specimen,
seed, arm, tier and budget, and the control relationship each arm stands in. The whole
thing is hashed. After freeze there is no UCB, no promotion, no exploration floor, no
replacement sampling and no result-dependent allocation. The 24-hour deadline is a
maximum envelope, not permission to invent work: if the manifest finishes early the
campaign stops.

If smoke timings show the manifest cannot finish with safe drain margin, it is reduced
BEFORE freeze by SCALE_RULE below, and the power calculation is rerun.
"""
from __future__ import annotations

import hashlib
import json

import grammar as G
import specimens

PROTOCOL_VERSION = "cycle9-verify-2-candidate"   # S4 candidate, 2026-09-23; NOT FROZEN

# Reduction rule, declared before any timing is measured so the reduction cannot be
# chosen to protect a preferred result: seeds are dropped from the LARGEST hypothesis
# first, uniformly across its arms, never by dropping an arm or a block, and never
# below MIN_SEEDS. Dropping an arm would break a bundle; dropping a block would change
# which question is asked.
SCALE_RULE = ("drop seeds uniformly from the largest hypothesis first; never drop an arm "
              "or a block; never go below MIN_SEEDS per arm")
MIN_SEEDS = 5

# Default sizing. Smoke timings decide whether these survive to freeze.
# S4 candidate (operator directive 2026-09-23): enlarge unevenly. H1 unchanged. H2 more
# seeds, but ONLY for P-11-surviving specimens (panel rebuilt, see specimens.manifest_p11).
# H3 moderately more shared-seed exposure. H4 NOT enlarged: the S1-B autopsy found its
# endogenous arm cannot reproduce (C9-D07), which is the directive's redesign exception.
SIZE = {"H1_seeds": 60, "H2_seeds": 16, "H3_seeds": 24, "H4_seeds": 16}
TIER = {"H1": "S", "H2": "M", "H3": "M", "H4": "L"}


def _cell(**kw):
    base = {"world": "GRID", "environment": "STATIC", "representation": "Z8_32",
            "reproduction": "EXTERNAL", "self_location": "PRIMITIVE",
            "copy_primitive": "BYTEWISE", "pressure": "EXPLICIT_FITNESS",
            "structure": "WELL_MIXED", "task_transform": "ADD1",
            "read_order": "ANSWER_BEFORE_READ", "bridge": "VALLEY",
            "seeding": "RANDOM", "mutation_operator": "BOTH",
            "mutation_locality": "LOCAL", "mutation_rate": "MID", "atlas_axis": "NONE"}
    base.update(kw)
    return base


# --------------------------------------------------------------------- H1
def h1_bundles(n_seeds):
    """2 x 2: output gate x cue-consumption cost, on ONE fixed task.

    read_order is HELD FIXED at ANSWER_BEFORE_READ across all four arms. It is not a
    factor here and must not become one: FORCED_READ sets base = v XOR key and passes a
    three-element input vector, so switching it changes the target and the input
    construction, and the arms would no longer be the same experiment. The intervention
    is entirely in the output discipline and the price of consuming the cue.
    """
    cell = _cell()
    arms = [("gate_off_cost_vm", "UNRESTRICTED", "VM"),
            ("gate_on_cost_vm", "GATED", "VM"),
            ("gate_off_cost_free", "UNRESTRICTED", "FREE"),
            ("gate_on_cost_free", "GATED", "FREE")]
    out = []
    for s in range(n_seeds):
        seed = 9_100_000 + s
        out.append({
            "hypothesis_id": "H1", "pair_seed": seed,
            "factor_deltas": {"output_gate": ["UNRESTRICTED", "GATED"],
                              "cue_cost": ["VM", "FREE"]},
            "held_fixed": ["inputs", "expected", "task_transform", "bridge", "read_order",
                           "population", "seed", "vm_semantics"],
            "expected_cardinality": len(arms),
            "arms": [{"arm": name, "cell": cell, "seed": seed, "tier": TIER["H1"],
                      "kwargs": {"output_gate": gate, "cue_cost": cost}}
                     for name, gate, cost in arms],
            "control_relationship": "factorial; gate_off_cost_vm is the reference cell",
        })
    return out


# --------------------------------------------------------------------- H2
def h2_bundles(n_seeds):
    """Per specimen: in situ, actual-genome reimplant, length-matched random implant.

    B and C share background and RNG seed and differ ONLY in the implanted bytes, which
    is what separates "this genome propagates" from "this world produces depth".
    """
    panel = specimens.manifest_p11()
    out = []
    for sp in panel["specimens"]:
        for s in range(n_seeds):
            seed = 9_200_000 + s
            out.append({
                "hypothesis_id": "H2", "pair_seed": seed,
                "specimen": sp["run_id"], "stratum": sp["stratum"],
                "factor_deltas": {"implant": ["NONE", "ACTUAL_GENOME", "RANDOM_MATCHED"]},
                "held_fixed": ["cell", "background_population", "rng_seed", "genome_length"],
                "expected_cardinality": 3,
                "arms": [
                    {"arm": "A_in_situ", "cell": sp["cell"], "seed": seed,
                     "tier": TIER["H2"], "kwargs": {}},
                    # The implanted bytes are IN the manifest (and so in its hash):
                    # the donor genome of the specimen's first P-11-causal event. Resolving
                    # them at run time from the predecessor's first_replicator would
                    # implant the donor of the first PREDECESSOR-criterion event instead,
                    # and would depend on gitignored per-run files (C9-D06).
                    {"arm": "B_reimplant_actual", "cell": sp["cell"], "seed": seed,
                     "tier": TIER["H2"], "kwargs": {"implant": "ACTUAL_GENOME",
                                                    "implant_source": sp["run_id"],
                                                    "implant_hex": sp["genome_hex"]}},
                    {"arm": "C_reimplant_random", "cell": sp["cell"], "seed": seed,
                     "tier": TIER["H2"], "kwargs": {"implant": "RANDOM_MATCHED",
                                                    "implant_len": sp["genome_len"]}},
                ],
                "control_relationship": "C is the length-matched null for B",
                "primary_endpoint": "max_causal_replication_depth",
            })
    return out, panel


# --------------------------------------------------------------------- H3
def h3_cells():
    """Frozen by rule: the RESERVOIR cells among the admissible specimen strata.

    Chosen from the predecessor record before launch and recorded here, so there is no
    adaptive replacement of cells after results arrive.
    """
    # S4: PINNED. These were the RESERVOIR specimens of the rev-B H2 panel (hash 005a495c...).
    # H3 used to re-derive them from the H2 panel on every build, so rebuilding H2 from
    # P-11 survivors would have silently replaced H3's cells - a coupling nothing
    # declared (C9-D09). H3 asks about the easy niche, not about pair-tape copying, so its
    # cells are pinned here verbatim, independent of H2.
    return [dict(run_id=r, cell=c) for r, c in H3_CELLS]


H3_CELLS = (
    ("42b011dfbda8be17-s60842-tL-a0",
     {"atlas_axis": "RECOMBINATION", "bridge": "NEUTRAL_BRIDGE", "copy_primitive": "BLOCK",
      "environment": "STATIC", "mutation_locality": "LOCAL", "mutation_operator": "BOTH",
      "mutation_rate": "HIGH", "pressure": "PREDATION", "read_order": "ANSWER_BEFORE_READ",
      "representation": "Z8_64", "reproduction": "PAIR_EXECUTION", "seeding": "RANDOM",
      "self_location": "PRIMITIVE", "structure": "RESERVOIR", "task_transform": "XOR5A",
      "world": "PAIR_TAPE"}),
    ("54e9cd610c16e9ba-s28950-tL-a0",
     {"atlas_axis": "RECOMBINATION", "bridge": "NEUTRAL_BRIDGE", "copy_primitive": "BLOCK",
      "environment": "STATIC", "mutation_locality": "LOCAL", "mutation_operator": "BOTH",
      "mutation_rate": "HIGH", "pressure": "PREDATION", "read_order": "ANSWER_BEFORE_READ",
      "representation": "Z8_SLOTTED", "reproduction": "PAIR_EXECUTION", "seeding": "RANDOM",
      "self_location": "PRIMITIVE", "structure": "RESERVOIR", "task_transform": "ADD1",
      "world": "PAIR_TAPE"}),
    ("f42f2adef369af16-s8750-tL-a0",
     {"atlas_axis": "RECOMBINATION", "bridge": "NEUTRAL_BRIDGE", "copy_primitive": "BLOCK",
      "environment": "RESOURCE_LIMITED", "mutation_locality": "LOCAL",
      "mutation_operator": "BOTH", "mutation_rate": "HIGH", "pressure": "PREDATION",
      "read_order": "ANSWER_BEFORE_READ", "representation": "Z8_SHARED",
      "reproduction": "PAIR_EXECUTION", "seeding": "RANDOM", "self_location": "NONE",
      "structure": "RESERVOIR", "task_transform": "XOR5A", "world": "PAIR_TAPE"}),
)


def h3_bundles(n_seeds):
    out = []
    for sp in h3_cells():
        base = dict(sp["cell"])
        for s in range(n_seeds):
            seed = 9_300_000 + s
            out.append({
                "hypothesis_id": "H3", "pair_seed": seed, "source_specimen": sp["run_id"],
                "factor_deltas": {"structure": ["RESERVOIR", "NICHES_HIGH_MIG"],
                                  "migration": ["ON", "OFF"]},
                "held_fixed": ["task", "representation", "reproduction", "pressure", "seed"],
                "expected_cardinality": 3,
                "arms": [
                    {"arm": "A_easy_plus_migration", "cell": dict(base, structure="RESERVOIR"),
                     "seed": seed, "tier": TIER["H3"], "kwargs": {}},
                    {"arm": "B_homogeneous_same_migration",
                     "cell": dict(base, structure="NICHES_HIGH_MIG"),
                     "seed": seed, "tier": TIER["H3"], "kwargs": {}},
                    {"arm": "C_easy_no_migration", "cell": dict(base, structure="RESERVOIR"),
                     "seed": seed, "tier": TIER["H3"], "kwargs": {"migration_disabled": True}},
                ],
                "control_relationship": "A vs B isolates the easy niche; A vs C isolates migration",
                "primary_endpoint": "has_reservoir_certificate",
            })
    return out


# --------------------------------------------------------------------- H4
H4_CELL = {"world": "GRAPH", "environment": "COEVO_ENV", "representation": "Z8_64",
           "reproduction": "ENDOGENOUS_PARTIAL", "self_location": "PRIMITIVE",
           "copy_primitive": "BLOCK", "pressure": "NONE_IMPLICIT",
           "structure": "NICHES_PERIODIC_MIG", "task_transform": "ADD1",
           "read_order": "FORCED_READ", "bridge": "VALLEY", "seeding": "SEEDED_READER",
           "mutation_operator": "BOTH", "mutation_locality": "STRUCTURAL",
           "mutation_rate": "HIGH", "atlas_axis": "NONE"}
H4_SOURCE = "64dea50f417efb02-s1203-tL-a0"


def h4_bundles(n_seeds):
    blocks = {
        "A_historical": H4_CELL,
        "B_random_seeding": dict(H4_CELL, seeding="RANDOM"),
        "C_static_env": dict(H4_CELL, environment="STATIC"),
        "D_topology_comparator": dict(H4_CELL, structure="NICHES_HIGH_MIG"),
    }
    out = []
    for bname, cell in blocks.items():
        for s in range(n_seeds):
            seed = 9_400_000 + s
            out.append({
                "hypothesis_id": "H4", "block": bname, "pair_seed": seed,
                "source_run": H4_SOURCE,
                "factor_deltas": {"reproduction": ["ENDOGENOUS_PARTIAL", "EXTERNAL"]},
                "held_fixed": ["cell_except_reproduction", "seed"],
                "expected_cardinality": 2,
                "arms": [
                    {"arm": "endogenous", "cell": cell, "seed": seed, "tier": TIER["H4"],
                     "kwargs": {}},
                    {"arm": "external", "cell": dict(cell, reproduction="EXTERNAL"),
                     "seed": seed, "tier": TIER["H4"], "kwargs": {}},
                ],
                "control_relationship": "matched exogenous control on the same seed",
            })
    return out


# --------------------------------------------------------------------- build
def build(size=None):
    size = dict(SIZE, **(size or {}))
    h1 = h1_bundles(size["H1_seeds"])
    h2, panel = h2_bundles(size["H2_seeds"])
    h3 = h3_bundles(size["H3_seeds"])
    h4 = h4_bundles(size["H4_seeds"])
    bundles = h1 + h2 + h3 + h4
    n_runs = sum(b["expected_cardinality"] for b in bundles)
    body = {"protocol_version": PROTOCOL_VERSION,
            "grammar_hash": G.grammar_hash(),
            "specimen_panel_hash": panel["panel_hash"],
            "size": size, "scale_rule": SCALE_RULE, "min_seeds": MIN_SEEDS,
            "n_bundles": len(bundles), "n_runs": n_runs,
            "by_hypothesis": {"H1": len(h1), "H2": len(h2), "H3": len(h3), "H4": len(h4)},
            "bundles": bundles}
    body["manifest_hash"] = hashlib.sha256(
        json.dumps({k: v for k, v in body.items() if k != "manifest_hash"},
                   sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    return body


def validate(m):
    """Every arm must name a cell the grammar admits, and every bundle must be honest
    about its own cardinality."""
    bad = []
    for b in m["bundles"]:
        if len(b["arms"]) != b["expected_cardinality"]:
            bad.append((b["hypothesis_id"], b.get("pair_seed"), "cardinality mismatch"))
        for a in b["arms"]:
            if not G.is_valid(a["cell"]):
                bad.append((b["hypothesis_id"], a["arm"],
                            "invalid cell: %s" % G.violations(a["cell"])))
    return bad


if __name__ == "__main__":
    m = build()
    bad = validate(m)
    print(json.dumps({k: m[k] for k in ("protocol_version", "grammar_hash",
                                        "specimen_panel_hash", "manifest_hash",
                                        "n_bundles", "n_runs", "by_hypothesis")}, indent=1))
    print("validation problems:", len(bad))
    for b in bad[:10]:
        print("   ", b)
