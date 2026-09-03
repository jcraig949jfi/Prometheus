"""SELECTION-REPLAYABILITY AUDIT + REGISTERED CONDITIONAL LEVEL CERTIFICATE.

Two executable pieces:

(1) SR-CLASSIFICATION of every stackvm-v1 selection channel (mission section 5)
    SR0 exactly replayable | SR1 stochastically replayable |
    SR2 partially replayable | SR3 non-replayable.
    "Probably equivalent" is not replayable.

(2) THE REGISTERED CONDITIONAL LEVEL CERTIFICATE (RCLC), the constructive
    proposal from independent review. The prior theory asserted a POINTWISE
    level premise ("for every c, P_U(phi(c,U)=1) <= alpha") and called it
    unverifiable. It is not unverifiable -- it is EXACTLY COMPUTABLE BEFORE
    THE BEACON, because c is already known (D-measurable) and the law of U is
    declared in the registration. Evaluating alpha(c) = P_U(phi(c,U)=1)
    requires no fresh randomness; the beacon is needed only for the single
    real draw. For a single-byte intervention on a 64-byte artifact the whole
    support is 64*255 = 16,320 mutants and alpha(c) is computed EXACTLY.

    Two consequences the review draws out, both adopted here:
      * sup over c is the WRONG premise: it is unattainable (equals 1) for
        most useful tests, so it would reject valid tests while admitting
        invalid ones. The needed premise is the level AT THE REALIZED c.
      * certifying a 1/K tail costs ~K evaluations, so CERTIFICATION COST
        LOWER-BOUNDS THE PRICE. That is the correct economics for a
        conserved budget.

    The Court debits max(alpha_nominal, alpha_hat_upper).
"""
from __future__ import annotations

import hashlib
import json
import math
import sys

sys.path.insert(0, "F:/SerendipityD")

SR0, SR1, SR2, SR3 = "SR0", "SR1", "SR2", "SR3"

CHANNEL_SR = [
    ("M1_generator", SR0,
     "operator config recorded verbatim AND hashed; op+seed on every artifact "
     "event; source_tree_hash single-valued (50b5c232) across all 261 "
     "experiments -- the code did not change during the era"),
    ("M2_population_schedule", SR0,
     "driver, budget and seed recorded per experiment; 27 distinct seeds"),
    ("M3_survivor_selection", SR1,
     "operator, tie_break_policy, tie_break_key, root_seed, candidate_pool_hash "
     "and candidate/rejected id lists are all recorded. BUT 85 of 87 selections "
     "were fully tied, so the winner is a seeded_uniform draw OVER THE REALIZED "
     "POOL: perturbing pool membership by one member re-randomizes the winner "
     "with probability 1/(m+1). Trajectory replay is therefore pool-conditional, "
     "not free-running -- SR1, not SR0"),
    ("M4_archive", SR2,
     "archive rule is deterministic and single-valued (simple_grid, reject "
     "reason always 'not_better'). BUT insertion eligibility depends on a "
     "scored fitness, and a wall-clock abort yields fitness=None -> "
     "detail='no_fitness' -> never inserted, never an elite, never nominated. "
     "Whether an evaluation walls is a function of host CPU contention, not of "
     "(code, inputs, max_steps)"),
    ("M5_run_nomination", SR0,
     "EXPERIMENT_FINISHED.best_artifact_id is an explicit, frozen, "
     "deterministic max-of-N nomination, recorded per run"),
    ("M6_task_filter", SR1,
     "terrain/battery fully specified and hashed (train_battery_hash, "
     "heldout_battery_hash); replayable as a procedure, though corpus-material "
     "as a scientific reference"),
    ("H1_era_restart", SR3,
     "no recorded rule for why the map_elites era began after observing the "
     "objective_ga era"),
    ("H2_archaeological_mining", SR3,
     "adaptive, model-driven, interactive; branch points depended on "
     "intermediate results never logged as a rule; the analysis itself "
     "declared the effective hypothesis count NOT ESTIMABLE. Critically, the "
     "mining read the raw JSONL ledger files directly, bypassing any query "
     "interface, so no access log bounds the consulted sigma-field"),
    ("H3_claim_wording", SR3, "no recorded rule"),
    ("S1_spec_menu", SR2,
     "repairable to SR0-equivalent by BEACON_SELECTED_FROM_COMMITTED_MENU, but "
     "only if every member is individually valid AND the claim is invariant "
     "across members"),
]

# The semantics hazard, verified in source, that bounds M4's classification.
SEMANTICS_HAZARD = {
    "mechanism": "wall-clock abort removes an evaluation from nomination "
                 "eligibility entirely",
    "code_evidence": [
        "adapter.py:215  elif last.halt == 'wall': walled += 1",
        "adapter.py:237-239  returns exact_success=None, cases_passed=None, "
        "fitness=None, behavior=None",
        "archives/simple_grid.py:69  ArchiveDecision(inserted=False, "
        "detail='no_fitness')",
        "adapter.py:184,264  time.perf_counter() -- host wall clock",
    ],
    "empirical_in_corpus": "ZERO executions carry a wall detail and ZERO "
                           "ARCHIVE_REJECTs carry detail='no_fitness' "
                           "(71,683 executions examined)",
    "why_that_is_not_reassuring":
        "the era declared adapter_version 0.1.0, and the current source states "
        "that 0.1.0 COUNTED A WALLED CASE AS SIMPLY 'NOT PASSED'. Under the "
        "era's own semantics a wall therefore leaves a record "
        "INDISTINGUISHABLE from ordinary step-exhaustion. The absence of "
        "TIMEOUT records is consistent both with 'no wall ever occurred' and "
        "with 'walls occurred and were silently scored'. THE CHANNEL IS "
        "UNFALSIFIABLE FROM THE RECORD.",
    "consequence": "M4 cannot be raised above SR2 on the evidence available.",
}


# --------------------------------------------------------------------------
# (2) The Registered Conditional Level Certificate
# --------------------------------------------------------------------------
def rclc_exact_single_byte(code: bytes, decide, max_steps=2000, ctx=(1, 2, 3)):
    """EXACT alpha(c) for a single-byte-intervention test.

    Enumerates the ENTIRE support of U: every (position, replacement byte).
    No sampling, no genericity premise, no 'for a typical program'. Returns
    the exact rejection probability of the declared test at the realized c.
    """
    from foundry.engines.gp.stackvm import vm
    base = vm.run_program(code, ctx, max_steps=max_steps)
    n = len(code)
    total = 0
    hits = 0
    for pos in range(n):
        for b in range(256):
            if b == code[pos]:
                continue
            m = bytearray(code)
            m[pos] = b
            total += 1
            if decide(base, vm.run_program(bytes(m), ctx, max_steps=max_steps)):
                hits += 1
    return {"support_size": total, "hits": hits,
            "alpha_exact": (hits / total) if total else 0.0}


def clopper_pearson_upper(hits, n, conf=0.95):
    """One-sided upper bound; used when exact enumeration is impractical."""
    if hits == 0:
        return 1.0 - (1.0 - conf) ** (1.0 / n)
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        # P(X <= hits | n, mid)
        s = sum(math.comb(n, k) * mid ** k * (1 - mid) ** (n - k)
                for k in range(hits + 1))
        if s > 1 - conf:
            lo = mid
        else:
            hi = mid
    return hi


def demo_rclc():
    """Reproduce the review's DEAD-CODE counterexample and show the RCLC
    catching it -- the case where a sincerely-believed 'pointwise' level is
    wrong by three orders of magnitude at the selected candidate."""
    from foundry.engines.gp.stackvm import vm

    def inert(base, mut):
        return (mut.steps == base.steps and mut.output == base.output
                and mut.halt == base.halt)

    out = {}
    # (i) a generic program: most single-byte edits change the trace
    generic = bytes(hashlib.sha256(b"generic").digest() * 2)[:64]
    out["generic_64B"] = rclc_exact_single_byte(generic, inert)
    # (ii) a candidate a corpus search can easily surface: almost all bytes
    #      are never executed, because the program halts immediately.
    #      opcode 28 = JMP; a 2-byte prefix that jumps to itself, then 62
    #      bytes of unreachable padding.
    dead = bytes([vm.OP["JMP"], 0]) + bytes(62)
    out["mostly_dead_64B"] = rclc_exact_single_byte(dead, inert)
    return out


def main():
    print("=" * 78)
    print("SELECTION-REPLAYABILITY AUDIT")
    print("=" * 78)
    counts = {}
    for cid, sr, why in CHANNEL_SR:
        counts[sr] = counts.get(sr, 0) + 1
        print("  %-26s %-4s %s" % (cid, sr, why[:44]))
    print()
    print("  class counts:", counts)
    print("  WORST LOAD-BEARING CLASS: SR3 (H1, H2, H3)")
    print()
    print("  SEMANTICS HAZARD bounding M4:")
    print("   ", SEMANTICS_HAZARD["empirical_in_corpus"])
    print("    BUT:", SEMANTICS_HAZARD["why_that_is_not_reassuring"][:200])

    print("\n" + "=" * 78)
    print("REGISTERED CONDITIONAL LEVEL CERTIFICATE (exact, pre-beacon)")
    print("=" * 78)
    d = demo_rclc()
    for name, r in d.items():
        print("  %-18s support=%-6d hits=%-6d alpha_exact=%.4f"
              % (name, r["support_size"], r["hits"], r["alpha_exact"]))
    g = d["generic_64B"]["alpha_exact"]
    x = d["mostly_dead_64B"]["alpha_exact"]
    print()
    print("  A registrant proving a level 'pointwise' from a GENERICITY")
    print("  premise ('a typical 64-byte program has few inert bytes') would")
    print("  price this test at ~%.4f. At the candidate a corpus search can" % g)
    print("  actually surface, the true level is %.4f -- a factor of %.0fx."
          % (x, (x / g) if g > 0 else float('inf')))
    print("  THE CERTIFICATE IS COMPUTED BEFORE THE BEACON, FROM c AND THE")
    print("  DECLARED LAW OF U ALONE. It needs no fresh randomness, and it")
    print("  refuses the mispriced test at registration.")
    print("=" * 78)
    return {"sr": counts, "rclc": d}


if __name__ == "__main__":
    main()
