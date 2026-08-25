"""Step 2 preflight — population, degeneracy, and the parent-resolution question.

Runs BEFORE any estimator is fitted. Reports only population facts and structural checks; it
fits nothing and reads no holdout.

THE DESIGN QUESTION IT EXISTS TO SETTLE. The action is `mutation_side` -- which side of the pair
was mutated. A child row carries the state AFTER that mutation. Predicting the action from the
child's own fields is therefore LEAKAGE, not navigation: the mutated side is the one that changed,
and a model can learn to spot the changed object rather than to choose it. A navigational
(state, action, outcome) triple needs the PARENT's pre-decision state:

    S = parent's (catalog_a/b, invariant_a/b, object_a/b, value_a/b)
    A = child's mutation_side          (chosen at S)
    Y = child's holds                  (terminus)

So the triple only exists if `parent_record_id` RESOLVES -- if the parent record is present in the
corpus and carries a state. Pass 2 tests exactly that against a random sample of parent ids. If
parents do not resolve inside c1, the pre-registered experiment cannot be run on c1 rows alone and
the resolution target must be found before anything else is measured.

    python charon/step2/preflight_step2.py
"""
import collections
import glob
import json
import os
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent
SHARDS = sorted(glob.glob(str(HERE / "shards" / "c1-*.jsonl")))
REL = "equal_mod_2"
SAMPLE_PARENTS = 20_000
random.seed(20260825)          # fixed: Date/random are not free variables in a filed preflight

A_BIT = {"a": 1, "b": 2}
HOLD_BIT = {"a": 4, "b": 8}


def h64(s):
    return int(s[:16], 16) if s else 0


def main():
    rows = 0
    act = collections.Counter()
    hold = collections.Counter()
    act_hold = collections.Counter()
    parent = {}                     # pid8 -> packed bits
    no_parent = 0
    parent_ids = []                 # reservoir for pass 2
    seen_par = 0
    state_key_present = collections.Counter()

    for sh in SHARDS:
        with open(sh, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                if d.get("relation") != REL:
                    continue
                rows += 1
                a = d.get("mutation_side")
                y = d.get("holds")
                act[a] += 1
                hold[y] += 1
                act_hold[(a, bool(y))] += 1
                for k in ("catalog_a", "invariant_a", "object_a", "value_a",
                          "catalog_b", "invariant_b", "object_b", "value_b"):
                    if d.get(k) is not None:
                        state_key_present[k] += 1
                pid = d.get("parent_record_id")
                if not pid:
                    no_parent += 1
                    continue
                seen_par += 1
                if len(parent_ids) < SAMPLE_PARENTS:
                    parent_ids.append(pid)
                elif random.random() < SAMPLE_PARENTS / seen_par:
                    parent_ids[random.randrange(SAMPLE_PARENTS)] = pid
                k = h64(pid)
                bits = parent.get(k, 0)
                if a in A_BIT:
                    bits |= A_BIT[a]
                    if y:
                        bits |= HOLD_BIT[a]
                parent[k] = bits

    both = sum(1 for b in parent.values() if (b & 3) == 3)
    divergent = sum(1 for b in parent.values()
                    if (b & 3) == 3 and bool(b & 4) != bool(b & 8))
    maj = max(act.values()) / rows if rows else 0

    out = {
        "population": {
            "generator": "c1", "relation": REL,
            "rows_EXACT": rows,
            "rows_without_parent_pointer": no_parent,
            "distinct_parents": len(parent),
            "parents_with_BOTH_actions": both,
            "parents_DIVERGENT (both actions, different outcome)": divergent,
        },
        "preregistered_claim": {
            "rows": 411_580, "parent_states": 222_715,
            "both_actions": 47_389, "divergent": 27_370,
        },
        "ratios_measured_over_preregistered": {
            "rows": round(rows / 411_580, 2),
            "parents": round(len(parent) / 222_715, 2),
            "both_actions": round(both / 47_389, 2) if both else 0,
            "divergent": round(divergent / 27_370, 2) if divergent else 0,
        },
        "action_distribution": dict(act),
        "outcome_distribution": {str(k): v for k, v in hold.items()},
        "action_x_outcome": {f"{a}|holds={h}": n for (a, h), n in sorted(act_hold.items(),
                                                                        key=lambda x: str(x[0]))},
        "attainable_range": {
            "floor_majority_action_rate": round(maj, 6),
            "note": "ceiling (within-state-cell majority) requires resolved PARENT states; "
                    "computed only after parent resolution is confirmed",
        },
        "degeneracy": {
            "outcome_constant": len(hold) < 2,
            "action_constant": len(act) < 2,
            "divergent_subset_empty": divergent == 0,
            "state_fields_populated": dict(state_key_present),
        },
    }
    print(json.dumps(out, indent=2))
    (HERE / "preflight_pass1.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    (HERE / "parent_sample.json").write_text(json.dumps(parent_ids), encoding="utf-8")
    print(f"\nwrote preflight_pass1.json and parent_sample.json ({len(parent_ids)} ids)")


if __name__ == "__main__":
    main()
