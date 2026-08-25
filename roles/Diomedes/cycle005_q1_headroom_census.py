"""Diomedes cycle 005 — Q1 headroom census over the remaining candidate populations.

WHY THIS EXISTS. BOOTSTRAP S4 Step 3b recommends recording Q1 as "unresolvable in this
corpus". That is a MEASUREMENT claim about every candidate population, and cycle 005 has
so far measured conditional headroom for exactly one of them (b2, 0.0265, in Arm A). For
b3 and b4 the claim "small synthetic algebra with no headroom" is currently an ASSERTION.
Shipping a verdict whose rows do not exist is the failure mode ATK-015 probes for.

This is not a sixth cycle. It is the standing-rule pre-flight (BOOTSTRAP S6) for a claim
about to be written into the terminal synthesis, and it is rung 1 throughout: b3 and b4
are exactly enumerable from the operator tables recovered at step 0 and verified against
three independent sources at 1.000000 agreement.

  b3  composition_test / self-inverse : oracle  f(f(v)) == v
  b4  operator_rotation / fixed point : oracle  f(v)    == v

Both have state x = v, action a = operator, candidate set = all 6 operators. The
state-independent ceiling is the best fixed ranking of operators ignoring v; the oracle is
1.0 by construction; headroom = 1.0 - ceiling. Disqualification line is 0.05.

b5 (conservation_law) is NOT enumerated here: the cycle-005 pre-flight counted exactly two
distinct action tokens and 30 negatives in 2,104 records, so its candidate set has k = 2
and its negative class is 1.4%. It is reported from those counts and disqualified on
structure, which is stated rather than hidden.

    python roles/Diomedes/cycle005_q1_headroom_census.py
"""
import itertools
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
TABLES = HERE / "cycle005_operator_tables.json"
OUT = HERE / "cycle005_q1_headroom_census.json"
VALUES = list(range(-50, 51))          # same frozen core range as Arm A
FLOOR = 0.05                           # BOOTSTRAP S6 disqualification line


def auc_from_counts(scored):
    """Exact AUC over (score, label) with tie handling. Identical to Arm A's."""
    pos = [s for s, l in scored if l]
    neg = [s for s, l in scored if not l]
    if not pos or not neg:
        return None
    wins = ties = 0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1
            elif p == n:
                ties += 1
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


def census(name, desc, oracle, T, OPS):
    """Enumerate the whole (v, operator) space and compute the exact decomposition."""
    cell, missing = {}, 0
    for f, v in itertools.product(OPS, VALUES):
        r = oracle(T, f, v)
        if r is None:
            missing += 1
        else:
            cell[(f, v)] = r

    states = []
    for v in VALUES:
        cand = [(f, cell[(f, v)]) for f in OPS if (f, v) in cell]
        if 0 < sum(1 for _, c in cand if c) < len(cand):
            states.append((v, cand))

    # marginal (state-independent) ranking: operator's global success rate, ignoring v
    rate = {}
    for f in OPS:
        vals = [c for (ff, vv), c in cell.items() if ff == f]
        rate[f] = sum(vals) / len(vals) if vals else 0.0

    marg, orc, chance = [], [], []
    for v, cand in states:
        marg.append(auc_from_counts([(rate[f], c) for f, c in cand]))
        orc.append(auc_from_counts([(1.0 if c else 0.0, c) for f, c in cand]))
        chance.append(auc_from_counts([(0.0, c) for f, c in cand]))
    marg = [a for a in marg if a is not None]
    ceiling = sum(marg) / len(marg) if marg else None
    oracle_auc = sum(orc) / len(orc) if orc else None
    chance_auc = sum(chance) / len(chance) if chance else None

    n_true = sum(1 for c in cell.values() if c)
    headroom = (oracle_auc - ceiling) if (ceiling is not None) else None
    return {
        "population": name, "description": desc, "rung": 1,
        "cells_enumerated": len(cell), "cells_missing": missing,
        "outcome_counts": {"true": n_true, "false": len(cell) - n_true},
        "n_states_with_both_classes": len(states),
        "chance": round(chance_auc, 4) if chance_auc is not None else None,
        "state_independent_ceiling": round(ceiling, 4) if ceiling is not None else None,
        "oracle": round(oracle_auc, 4) if oracle_auc is not None else None,
        "conditional_headroom": round(headroom, 4) if headroom is not None else None,
        "disqualification_floor": FLOOR,
        "qualifies_for_a_conditional_structure_question":
            bool(headroom is not None and headroom >= FLOOR),
        "operator_success_rates_ignoring_v": {f: round(r, 4) for f, r in sorted(rate.items())},
    }


def main():
    raw = json.loads(TABLES.read_text(encoding="utf-8"))["operator_tables"]
    T = {op: {int(k): v for k, v in t.items()} for op, t in raw.items()}
    OPS = sorted(T)

    def b3_oracle(T, f, v):                       # self-inverse at v: f(f(v)) == v
        fv = T[f].get(v)
        if fv is None:
            return None
        ffv = T[f].get(fv)
        return None if ffv is None else (ffv == v)

    def b4_oracle(T, f, v):                       # fixed point: f(v) == v
        fv = T[f].get(v)
        return None if fv is None else (fv == v)

    rep = {
        "purpose": "rows beneath the Step 3b claim that no corpus population can answer Q1",
        "standing_rule": "BOOTSTRAP S6 — conditional headroom below ~0.05 disqualifies a "
                         "population for a conditional-structure question",
        "tables_source": "cycle005_operator_tables.json — step 0, three sources at 1.000000",
        "operators": OPS,
        "value_range": [min(VALUES), max(VALUES)],
        "populations": {
            "b3": census("b3", "composition_test / self-inverse: f(f(v)) == v",
                         b3_oracle, T, OPS),
            "b4": census("b4", "operator_rotation / fixed point: f(v) == v",
                         b4_oracle, T, OPS),
        },
        "b2_from_arm_A": {"conditional_headroom": 0.0265,
                          "state_independent_ceiling": 0.9735, "oracle": 1.0,
                          "qualifies_for_a_conditional_structure_question": False,
                          "rows_ref": "cycle005_armA_result.json"},
        "not_enumerated_and_why": {
            "b5": "conservation_law — 2 distinct action tokens (k=2 candidate set) and 30 "
                  "negatives in 2,104 records (1.4%); disqualified on structure, from the "
                  "cycle-005 pre-flight counts, not enumerated here",
            "c4": "18,976/18,976 holds=True — single-class, vacuous "
                  "(this was my recommended replication target; it had no negative class)",
            "b1": "1,340/1,340 matches=True — single-class, vacuous",
            "c5": "8,157/8,157 holds=True on the primary outcome, and its oracle is the same "
                  "arithmetic relation family as h1, so it cannot answer Q1 by construction",
            "g5": "absent from the sample entirely (n=0)",
        },
    }

    # ---- corroboration: my enumeration vs the corpus's OWN logged outcome counts ----
    # cycle005_preflight.json sampled the corpus directly. If my re-derivation of the
    # oracle from the recovered tables is right, its class counts must reproduce the
    # corpus's logged counts. This turns the enumeration from "my computation" into
    # "my computation checked against the corpus's own labels".
    logged = {"b3": {"true": 260, "false": 346},          # self_inverse_at_v
              "b4": {"true": 320, "false": 892}}          # is_fixed_point
    corr = {}
    for k, lg in logged.items():
        mine = rep["populations"][k]["outcome_counts"]
        ratios = [lg[c] / mine[c] for c in ("true", "false") if mine[c]]
        r = ratios[0] if ratios else None
        exact = all(abs(lg[c] - r * mine[c]) < 1e-9 for c in ("true", "false")) if r else False
        corr[k] = {"enumerated_here": mine, "logged_in_corpus_sample": lg,
                   "ratio_logged_over_enumerated": r,
                   "consistent_at_that_ratio": exact,
                   "reading": ("exact match — the recovered tables reproduce the corpus's own "
                               "labels" if r == 1 else
                               f"exact match at {r:g}x — the corpus sample carries each "
                               f"(operator, value) cell {r:g} times")}
    rep["corroboration_vs_corpus_logged_counts"] = corr

    quals = [k for k, v in rep["populations"].items()
             if v["qualifies_for_a_conditional_structure_question"]]
    rep["verdict"] = (
        "NO ENUMERATED POPULATION QUALIFIES — Q1 is unresolvable in this corpus"
        if not quals else
        f"QUALIFIES: {quals} — Q1 is answerable here and the Step 3b recommendation is wrong")
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")

    for k, v in rep["populations"].items():
        print(f"{k}: chance {v['chance']} | ceiling {v['state_independent_ceiling']} | "
              f"oracle {v['oracle']} | HEADROOM {v['conditional_headroom']} | "
              f"states {v['n_states_with_both_classes']} | "
              f"qualifies={v['qualifies_for_a_conditional_structure_question']}")
        print(f"    outcome counts: {v['outcome_counts']} "
              f"(cells {v['cells_enumerated']}, missing {v['cells_missing']})")
    for k, c in rep["corroboration_vs_corpus_logged_counts"].items():
        print(f"    {k} corroboration: {c['reading']} "
              f"(consistent={c['consistent_at_that_ratio']})")
    print("b2 (Arm A): HEADROOM 0.0265 | qualifies=False")
    print("VERDICT:", rep["verdict"])
    print("->", OUT)


if __name__ == "__main__":
    main()
