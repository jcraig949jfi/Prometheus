"""D001-03 analysis: can long neutral drift or duplication cross the PROTEUS-46 cliff?

NOT RUN by the author (read-only worker, no code execution). Every number this prints is a
result still to be obtained; REPORT.md quotes none of them.

Inputs (all at commit 0424c372a6bba88f50d31f3abbd8b1204871bba6; byte-identical to 6a98ef0bb for
the files PROTEUS-46 used, check with `git diff 6a98ef0bb 0424c372a -- proteus/graph proteus/eval proteus/foundry`):
    proteus/graph/witness.py      one_value_manifest, keyed_memory_manifest, run_episode
    proteus/graph/grammar.py      graph_grammar.v1 (NAMES, WEIGHTS, mutate, apply_edits)
    proteus/graph/vm.py           runtime, live_nodes
    proteus/eval/keyed_memory_witness.py   two_key_episode, all_keys_episode (probe shared)
    proteus/foundry/prng.py       SplitMix64, seed_from
    proteus/round2/PROTEUS-46_FALSIFIER.json  (the result this re-examines)

Usage:  PROMETHEUS_REPO=/path/to/checkout python3 analysis.py [--quick]

Five parts:
  A. Score the two single-edit intermediates between one_value (3/6) and keyed (6/6).
     Hand derivation in REPORT.md s4.2 says both are 0/6 (DESTROYED). A says whether that holds.
  B. Score every intermediate of the explicit five-edit duplicate-and-diverge path
     (add ST', wire address from key node 3, wire value from node 6, splice ST' in after
     ST 7, then retarget LD's address edge). Hypothesis: steps 1-4 are NEUTRAL (3/6, identical
     outputs), step 5 is 6/6. If yes, a neutral path to the summit EXISTS in graph_grammar.v1.
  C. Exact one-step probability, under the grammar's own sampling code, of each specific
     edit on that path (and of the direct two-retarget fixes). Also the exact chance that PROTEUS-46's
     random 3-step walk could hit the direct fix pair.
  D. Long neutral-drift walks from one_value: accept a child iff two_key >= 3 (mode 'score')
     or iff outputs are identical on both probes (mode 'strict'); record first step reaching 6/6.
     Control: unselected random walks of the same length.
  E. Small mutation-selection population (truncation on two_key, ties random, no parsimony).

What decides the question (fixed before any output is seen):
  * B all-neutral + final 6/6  -> the cliff is crossable by a neutral path in principle; the
    PROTEUS-46 3-step design could not see it (path length 5 > 3).
  * D: if any mode reaches 6/6 in >= 1 of N walks, the long-drift answer is YES for this
    witness, operator set and mass profile; report the hit rate with its 95% interval and
    the first-hit time distribution. If 0/N at L_MAX, report the rule-of-three upper bound
    3/N on the per-walk rate at that length; that is 'not observed', not 'impossible'.
  * Compare D-hit-rate with the unselected control: drift helps only if the neutral-accepting
    walker beats the control.
  * E is secondary (a crude stand-in for an evolutionary run; no world, neutral probe only).
"""
from __future__ import annotations

import json
import math
import os
import sys

REPO = os.environ.get("PROMETHEUS_REPO", os.getcwd())
sys.path.insert(0, REPO)

from proteus.eval import keyed_memory_witness as W0          # noqa: E402  (probe episodes)
from proteus.foundry.prng import SplitMix64, seed_from       # noqa: E402
from proteus.graph import grammar as G1                      # noqa: E402
from proteus.graph import witness as W1                      # noqa: E402
from proteus.graph.identity import hash_obj                  # noqa: E402
from proteus.graph.affordances import DATA_IN, CONTROL_OUT, N_KINDS  # noqa: E402
from proteus.graph.vm import ST, live_nodes                   # noqa: E402

QUICK = "--quick" in sys.argv
TWO, ALL = W0.two_key_episode(), W0.all_keys_episode()


def score(m):
    """Same as falsifier_46.score for the graph substrate: (two_key, all_keys, outputs)."""
    a = W1.run_episode(m, TWO)
    b = W1.run_episode(m, ALL)
    return a["correct"], b["correct"], (tuple(a["outputs"]), tuple(b["outputs"]))


ONE = W1.one_value_manifest()
KEYED = W1.keyed_memory_manifest()
P_TWO, P_ALL, P_OUT = score(ONE)


def retarget_data(m, src, dst, port):
    return G1.apply_edits(m, [{"add_data_edges": [[src, dst, port]]}])


# ------------------------------------------------------------------ A. direct two-edit path
def part_a():
    st_fix = retarget_data(ONE, 3, 7, 0)      # ST address <- key   (keyed has [3,7,0])
    ld_fix = retarget_data(ONE, 3, 9, 0)      # LD address <- key   (keyed has [3,9,0])
    both = retarget_data(st_fix, 3, 9, 0)
    rows = {}
    for name, m in (("one_value", ONE), ("st_fix_only", st_fix), ("ld_fix_only", ld_fix),
                    ("both_fixes", both), ("keyed", KEYED)):
        two, al, _ = score(m)
        rows[name] = {"two_key": two, "all_keys": al}
    rows["both_equals_keyed_hash"] = hash_obj(both) == hash_obj(KEYED)
    return rows


# ------------------------------------------------------------------ B. duplicate-and-diverge path
def part_b():
    n0 = len(ONE["nodes"])                    # 12; new ST' gets index 12
    steps = [
        ("add dormant ST' (NODE_ADD kind=ST)", [{"add_nodes": [{"kind": ST, "params": [], "persist": False}]}]),
        ("wire ST' address <- key node 3 (EDGE_ADD)", [{"add_data_edges": [[3, n0, 0]]}]),
        ("wire ST' value <- value node 6 (EDGE_ADD)", [{"add_data_edges": [[6, n0, 1]]}]),
        ("splice: retarget control (7,0,8) -> (7,0,ST') (EDGE_RETARGET)", [{"add_control_edges": [[7, 0, n0]]}]),
        ("retarget LD address (2,9,0) -> (3,9,0) (EDGE_RETARGET)", [{"add_data_edges": [[3, 9, 0]]}]),
    ]
    m, rows = ONE, []
    for label, edits in steps:
        m = G1.apply_edits(m, edits)
        two, al, out = score(m)
        cls = ("USEFUL" if two > P_TWO else "NEUTRAL" if (two == P_TWO and out == P_OUT)
               else "NEUTRAL_DIFF" if two == P_TWO else "DESTROYED" if two == 0 else "GRADED_DOWN")
        rows.append({"step": label, "two_key": two, "all_keys": al, "class": cls,
                     "st_prime_live": n0 in live_nodes(m) if len(m["nodes"]) > n0 else False})
    # variant: ST' has no control successor, so the PUT tick halts after it (also legal)
    return rows


# ------------------------------------------------------------------ C. exact per-step probabilities
def w(op):
    return dict(zip(G1.NAMES, G1.WEIGHTS))[op]


def p_retarget_data(m, src, dst, port):
    """P(one mutate() call == EDGE_RETARGET that sets data edge into (dst,port) to src).
    op_edge_retarget: uniform edge over data+control edges, then source uniform over n nodes."""
    E = len(m["data_edges"]) + len(m["control_edges"])
    n = len(m["nodes"])
    present = any(d == dst and p == port for _s, d, p in m["data_edges"])
    return w("EDGE_RETARGET") * (1.0 / E) * (1.0 / n) if present else 0.0


def p_retarget_control(m, s, port, dst):
    E = len(m["data_edges"]) + len(m["control_edges"])
    n = len(m["nodes"])
    present = any(a == s and b == port for a, b, _d in m["control_edges"])
    return w("EDGE_RETARGET") * (1.0 / E) * (1.0 / n) if present else 0.0


def p_edge_add_data(m, src, dst, port):
    n = len(m["nodes"])
    fd = G1._free_data_ports(m)
    fc = G1._free_control_ports(m, list(range(n)))
    if (dst, port) not in fd:
        return 0.0
    return w("EDGE_ADD") * (1.0 / (len(fd) + len(fc))) * (1.0 / n)


def p_node_add_kind(kind):
    return w("NODE_ADD") * (1.0 / N_KINDS)      # ST has no params, so any draw of kind ST is identical


def part_c():
    n0 = len(ONE["nodes"])
    m1 = G1.apply_edits(ONE, [{"add_nodes": [{"kind": ST, "params": [], "persist": False}]}])
    m2 = G1.apply_edits(m1, [{"add_data_edges": [[3, n0, 0]]}])
    m3 = G1.apply_edits(m2, [{"add_data_edges": [[6, n0, 1]]}])
    m4 = G1.apply_edits(m3, [{"add_control_edges": [[7, 0, n0]]}])
    direct = {"p_st_fix_one_step": p_retarget_data(ONE, 3, 7, 0),
              "p_ld_fix_one_step": p_retarget_data(ONE, 3, 9, 0)}
    # upper bound for PROTEUS-46's random 3-step walk hitting both direct fixes in some two of three
    # steps (ignores that the third step may break or reindex; so it is an upper bound)
    p1, p2 = direct["p_st_fix_one_step"], direct["p_ld_fix_one_step"]
    direct["p_3step_walk_hits_both_upper"] = 3 * 2 * p1 * p2
    direct["expected_hits_in_200_walks_upper"] = 200 * direct["p_3step_walk_hits_both_upper"]
    dup = {"p1_node_add_ST": p_node_add_kind(ST),
           "p2_edge_add_addr": p_edge_add_data(m1, 3, n0, 0),
           "p3_edge_add_value": p_edge_add_data(m2, 6, n0, 1),
           "p4_splice_control": p_retarget_control(m3, 7, 0, n0),
           "p5_ld_fix": p_retarget_data(m4, 3, 9, 0)}
    dup["product_one_specific_order"] = math.prod(dup.values())
    # competing loss: chance per step that NODE_REMOVE deletes the dormant ST' (index n0) in m1
    dup["p_node_remove_hits_STprime_in_m1"] = w("NODE_REMOVE") * (1.0 / len(m1["nodes"]))
    return {"direct_two_retarget": direct, "duplicate_and_diverge": dup}


# ------------------------------------------------------------------ D. long neutral-drift walks
def drift(mode, n_walks, l_max, label):
    hits, first = 0, []
    sizes = []
    for wi in range(n_walks):
        rng = SplitMix64(seed_from("d001-03", label, mode, wi))
        m = ONE
        for t in range(1, l_max + 1):
            child = G1.mutate(m, rng)[0]
            if len(child["nodes"]) > 200:          # stay clear of the 256-node bound
                continue
            two, _al, out = score(child)
            if two == 6:
                hits += 1
                first.append(t)
                break
            if mode == "control":
                m = child
            elif mode == "score" and two >= P_TWO:
                m = child
            elif mode == "strict" and two == P_TWO and out == P_OUT:
                m = child
        sizes.append(len(m["nodes"]))
    rate = hits / n_walks
    ub = 3.0 / n_walks if hits == 0 else None
    return {"mode": mode, "walks": n_walks, "l_max": l_max, "hits": hits, "rate": rate,
            "rule_of_three_upper_if_zero": ub, "first_hit_steps": first,
            "final_nodes_mean": sum(sizes) / len(sizes)}


# ------------------------------------------------------------------ E. tiny population
def population(pop_n, gens, label):
    rng = SplitMix64(seed_from("d001-03", label, "pop"))
    pop = [ONE] * pop_n
    fit = [P_TWO] * pop_n
    for g in range(1, gens + 1):
        kids, kf = [], []
        for _ in range(pop_n):
            parent = pop[rng.randbelow(pop_n)]
            c = G1.mutate(parent, rng)[0]
            if len(c["nodes"]) > 200:
                c = parent
            kids.append(c)
            kf.append(score(c)[0])
        allm, allf = pop + kids, fit + kf
        order = sorted(range(len(allm)), key=lambda i: (-allf[i], rng.next_u32()))
        pop = [allm[i] for i in order[:pop_n]]
        fit = [allf[i] for i in order[:pop_n]]
        if max(fit) == 6:
            return {"pop": pop_n, "gens": gens, "reached_6_at_gen": g}
    return {"pop": pop_n, "gens": gens, "reached_6_at_gen": None, "best": max(fit)}


def main():
    out = {"inputs_commit": "0424c372a6bba88f50d31f3abbd8b1204871bba6",
           "parent_one_value": {"two_key": P_TWO, "all_keys": P_ALL}}
    out["A_direct_path"] = part_a()
    out["B_duplicate_diverge_path"] = part_b()
    out["C_probabilities"] = part_c()
    n_walks, l_max = (50, 300) if QUICK else (500, 3000)
    out["D_drift"] = [drift(mode, n_walks, l_max, "graph") for mode in ("strict", "score", "control")]
    out["E_population"] = population(50 if QUICK else 200, 100 if QUICK else 1000, "graph")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
