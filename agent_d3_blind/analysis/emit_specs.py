"""Emit machine-readable frozen specs and hashes of all frozen artifacts."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from substrates import s1_tpc, s2_flat, s3_trs, s4_rev, common  # noqa: E402
from probes import battery                                       # noqa: E402
from mutation import mutators                                    # noqa: E402
from reachability import witnesses                               # noqa: E402

RES = os.path.join(ROOT, "results")
FROZEN = ["MANIFEST.md", "PREREG-CENSUS.md", "prereg/gates.json",
          "substrates/common.py", "substrates/s1_tpc.py", "substrates/s2_flat.py",
          "substrates/s3_trs.py", "substrates/s4_rev.py", "substrates/registry.py",
          "mutation/mutators.py", "probes/battery.py", "classifiers/families.py",
          "m0/harness.py", "m0/baselines.py", "reachability/witnesses.py",
          "census/phase1_basis.py", "anti_cheat/checks.py", "analysis/verdict.py"]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    specs = {
        "value_domain": {"int_range": [-common.MAXVAL, common.MAXVAL],
                         "max_seq_len": common.MAXLEN,
                         "max_program_tokens": common.PROG_MAX,
                         "note": "a program is an element of the value domain; "
                                 "run(P, Q) with Q a program serialisation is the "
                                 "ordinary execution path (homoiconic by construction)"},
        "S1": {"name": "TPC typed point-free calculus", "fuel": s1_tpc.FUEL,
               "types": ["LL", "NN", "LN"],
               "ops": {str(k): {"name": v[0], "type": v[1], "children": list(v[2])}
                       for k, v in s1_tpc.OPS.items()},
               "token_encoding": "op_slot + 64*arg, arg in 0..7",
               "validity": "prefix-decodable well-typed term of type LL, <=32 tokens",
               "validity_closed_under_mutation": True},
        "S2": {"name": "FLAT total bytecode", "fuel": s2_flat.FUEL,
               "ops": s2_flat.OPNAMES,
               "token_encoding": "op + 24*arg, arg in 0..15",
               "validity": "any nonempty in-range tuple",
               "validity_closed_under_mutation": True},
        "S3": {"name": "TRS ordered local rewrite rules", "fuel": s3_trs.FUEL,
               "token_encoding": "0=ARROW, 1=RULESEP, t>=2 -> (kind, payload)",
               "limits": {"max_rules": s3_trs.MAX_RULES, "max_lhs": s3_trs.MAX_LHS,
                          "max_rhs": s3_trs.MAX_RHS, "payloads": s3_trs.NPAY},
               "validity": "rule shape, LHS 1..4 with >=1 CONST, RHS var indices bound",
               "validity_closed_under_mutation": False},
        "S4": {"name": "REV reversible affine register machine",
               "fuel": s4_rev.FUEL, "registers": s4_rev.R, "modulus": s4_rev.M,
               "ops": s4_rev.OPNAMES,
               "token_encoding": "op + 5*a + 30*b + 180*k",
               "validity": "any nonempty in-range tuple",
               "validity_closed_under_mutation": True,
               "note": "output arity fixed at 6; included as an adversarial control"},
    }
    json.dump(specs, open(os.path.join(RES, "substrate_specs.json"), "w"), indent=1)

    mut = {"seq_edits": mutators.SEQ_EDITS, "tree_edits": mutators.TREE_EDITS,
           "radius": "number of atomic edits composed in sequence",
           "donor_bank": {"rng": mutators.DONOR_RNG, "n": mutators.DONOR_N},
           "validity_blind": {"S2": True, "S3": True, "S4": True, "S1": False},
           "recombination": "one-point token crossover (S2/S3/S4); "
                            "type-matched subtree exchange (S1)",
           "taxonomy_free": "no operator names, consumes, or emits any "
                            "semantics-of-change category; families are recovered "
                            "offline by classifiers/families.py only"}
    json.dump(mut, open(os.path.join(RES, "mutation_specs.json"), "w"), indent=1)

    ph = {"value_probes": [list(p) for p in battery.VALUE_PROBES],
          "value_probe_hash": battery.probe_hash(battery.VALUE_PROBES),
          "ext_probes": [list(p) for p in battery.EXT_PROBES],
          "ext_probe_hash": battery.probe_hash(battery.EXT_PROBES),
          "liveness_probes": [list(p) for p in battery.LIVENESS_PROBES],
          "artifact_probe_rng": battery.ARTIFACT_PROBE_RNG,
          "witness_oracle_fps": {n: witnesses.oracle_fp(n) for n in witnesses.ORACLES}}
    json.dump(ph, open(os.path.join(RES, "probe_hashes.json"), "w"), indent=1)

    json.dump({f: sha(os.path.join(ROOT, f)) for f in FROZEN
               if os.path.exists(os.path.join(ROOT, f))},
              open(os.path.join(RES, "frozen_hashes.json"), "w"), indent=1)

    # aggregates from the ledgers, if present
    graph = {}
    tgts = {}
    for b in ("S1", "S2", "S3", "S4"):
        gp = os.path.join(ROOT, "ledgers", "graph_%s.json" % b)
        if os.path.exists(gp):
            g = json.load(open(gp))
            graph[b] = {"n_nodes": len(g["nodes"]), "n_edges": len(g["edges"]),
                        "giant_component_frac": g["giant_component_frac"],
                        "giant_component_size": g["giant_component_size"],
                        "depth_histogram": _hist(g["first_depth"])}
        lp = os.path.join(ROOT, "ledgers", "basis_%s.json" % b)
        if os.path.exists(lp):
            L = json.load(open(lp))
            tgts[b] = {"targets": L["order0"]["targets"],
                       "pool_sizes": L["order0"]["target_pool_sizes"]}
    json.dump(graph, open(os.path.join(RES, "phenotype_graph.json"), "w"), indent=1)
    json.dump(tgts, open(os.path.join(RES, "reachability_targets.json"), "w"), indent=1)

    with open(os.path.join(RES, "census_rows.jsonl"), "w") as out:
        for b in ("S1", "S2", "S3", "S4"):
            p = os.path.join(ROOT, "ledgers", "census_rows_%s.jsonl" % b)
            if os.path.exists(p):
                for line in open(p):
                    out.write(line)
    print("specs emitted")


def _hist(fd):
    h = {}
    for _k, v in fd.items():
        h[str(v)] = h.get(str(v), 0) + 1
    return h


if __name__ == "__main__":
    main()
