"""CHOICE-POINT CENSUS on c1 — the denominator the navigation thesis actually needs.

Prompted by external review, 2026-08-25 (Class III input, Class I output). The reviewer's central
objection, which I accept: *a transition graph is not a navigation graph.* You can have strong
P(next | current) while carrying no information about argmax_a P(success | current, a). So
"181,424,844 parent-linked rows" is an upper bound on navigational observations, NOT a count of
decisions. Everything that is not a choice point is trajectory data.

Computed here without any new corpus scan (c1 shards are already on disk):

  k_P            distinct COMPLETED interventions A+ = (side, replacement object) per parent
  decision-bearing parents   k_P >= 2 AND outcomes differ across A+
  side-only divergent        the weaker notion used so far (>=2 sides, outcomes differ)
  (P,A) collision rate       fraction of (parent, side) groups containing MULTIPLE outcomes
                             -> identical recorded decisions, materially different outcomes
                             -> the recorded action does not specify the intervention (Q4)
  dH                         H(outcome | P,A) - H(outcome | P,A+): outcome variation the LOGGER
                             collapsed by recording only the side, not the replacement
  irreducible regret LB      per parent, (best outcome over observed A+) minus (best outcome
                             reachable by a policy that can only choose the SIDE). Arithmetic
                             only, no model. Decision information mathematically unavailable
                             from the recorded action vocabulary.

RECOVERING THE COMPLETED ACTION. `mutation_side` names which side was mutated; the replacement is
that side's object IN THE CHILD. So A+ is recoverable from child rows alone -- no parent join,
no new scan.

MEMORY NOTE (correction to the first version of this script, which I killed at 15.4 GB): the
first cut held nested defaultdict/Counter objects for both the equal_mod_2 and all-relations
passes simultaneously. Rewritten to intern replacement objects to ints, pack (side, replacement)
into one int key, store outcome tallies as a 2-element list rather than a Counter, and run ONE
population per invocation, writing its result before the next begins.

    python charon/step2/choice_point_census.py [equal_mod_2|ALL]
"""
import collections
import glob
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SHARDS = sorted(glob.glob(str(HERE / "shards" / "c1-*.jsonl")))


def H2(n0, n1):
    n = n0 + n1
    if n <= 0:
        return 0.0
    h = 0.0
    for c in (n0, n1):
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def census(rel_filter, label):
    par = {}                       # pid_int -> {packed_action: [n_false, n_true]}
    obj_id = {}                    # replacement object -> small int
    seen = set()
    rows = 0
    for sh in SHARDS:
        with open(sh, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                if rel_filter and d.get("relation") != rel_filter:
                    continue
                a, y = d.get("mutation_side"), d.get("holds")
                pid, rid = d.get("parent_record_id"), d.get("record_id")
                if a not in ("a", "b") or y is None or not pid or not rid:
                    continue
                p = int(pid[:16], 16)
                r = int(rid[:16], 16)
                k = (r << 64) | p
                if k in seen:
                    continue
                seen.add(k)
                rows += 1
                repl = d.get("object_a") if a == "a" else d.get("object_b")
                oid = obj_id.get(repl)
                if oid is None:
                    oid = obj_id[repl] = len(obj_id)
                key = (oid << 1) | (0 if a == "a" else 1)
                acts = par.get(p)
                if acts is None:
                    acts = par[p] = {}
                t = acts.get(key)
                if t is None:
                    acts[key] = [0, 0]
                    t = acts[key]
                t[1 if y else 0] += 1

    n_par = len(par)
    kP = collections.Counter()
    decision_bearing = side_divergent = 0
    pa_groups = pa_multi = 0
    hA_num = hAplus_num = wtot = 0.0
    regret_sum = regret_n = 0.0
    # DEGENERACY GUARD. H(Y|P,A+) computed over all cells is ~0 BY CONSTRUCTION when almost
    # every (P,A+) cell holds one row: a singleton cell has zero entropy mechanically. The fair
    # comparison is restricted to cells that actually repeat, so these are tracked separately.
    aplus_cells = aplus_cells_ge2 = 0
    hA2_num = hA2plus_num = w2tot = 0.0
    pa_ge2 = pa_multi_ge2 = 0

    for p, acts in par.items():
        kP[min(len(acts), 6)] += 1
        side = {0: [0, 0], 1: [0, 0]}
        any_true = any_false = False
        for key, t in acts.items():
            s = key & 1
            side[s][0] += t[0]
            side[s][1] += t[1]
            any_false |= t[0] > 0
            any_true |= t[1] > 0
            hAplus_num += (t[0] + t[1]) * H2(t[0], t[1])
            aplus_cells += 1
            if t[0] + t[1] >= 2:
                aplus_cells_ge2 += 1

        live = [s for s in (0, 1) if side[s][0] + side[s][1] > 0]
        for s in live:
            n0, n1 = side[s]
            pa_groups += 1
            if n0 and n1:
                pa_multi += 1
            w = n0 + n1
            hA_num += w * H2(n0, n1)
            wtot += w
            if w >= 2:                      # fair denominator: groups that actually repeat
                pa_ge2 += 1
                if n0 and n1:
                    pa_multi_ge2 += 1
                hA2_num += w * H2(n0, n1)
                w2tot += w
                for key, t2 in acts.items():
                    if (key & 1) == s:
                        hA2plus_num += (t2[0] + t2[1]) * H2(t2[0], t2[1])

        if len(acts) >= 2 and any_true and any_false:
            decision_bearing += 1
        if len(live) == 2:
            ma = side[0][1] / (side[0][0] + side[0][1])
            mb = side[1][1] / (side[1][0] + side[1][1])
            if (ma == 1.0 and mb == 0.0) or (ma == 0.0 and mb == 1.0):
                side_divergent += 1
            # irreducible regret: best single completed intervention vs best side-only policy
            best_aplus = 1.0 if any_true else 0.0
            regret_sum += best_aplus - max(ma, mb)
            regret_n += 1

    out = {
        "population": label,
        "rows_deduplicated": rows,
        "parents": n_par,
        "distinct_replacement_objects": len(obj_id),
        "k_P_distribution (distinct completed interventions per parent, 6+ bucketed)":
            {str(k): v for k, v in sorted(kP.items())},
        "parents_with_k_P_ge_2": sum(v for k, v in kP.items() if k >= 2),
        "DECISION_BEARING_parents (k_P>=2 and outcomes differ)": decision_bearing,
        "decision_bearing_fraction_of_parents": round(decision_bearing / max(n_par, 1), 6),
        "side_only_divergent_parents": side_divergent,
        "(P,A)_groups": pa_groups,
        "(P,A)_groups_with_MULTIPLE_outcomes": pa_multi,
        "(P,A)_collision_rate": round(pa_multi / max(pa_groups, 1), 6),
        "(P,A+)_cells": aplus_cells,
        "(P,A+)_cells_with_ge2_rows": aplus_cells_ge2,
        "(P,A+)_repeat_rate": round(aplus_cells_ge2 / max(aplus_cells, 1), 6),
        "DEGENERACY_WARNING": "H(Y|P,A+) over ALL cells is ~0 by construction when (P,A+) cells "
                              "are singletons; use the _repeats_only figures below",
        "(P,A)_groups_with_ge2_rows": pa_ge2,
        "(P,A)_ge2_with_MULTIPLE_outcomes": pa_multi_ge2,
        "(P,A)_collision_rate_among_REPEATED_groups": round(pa_multi_ge2 / max(pa_ge2, 1), 6),
        "H(outcome|P,A)_repeats_only": round(hA2_num / max(w2tot, 1), 6),
        "H(outcome|P,A+)_repeats_only": round(hA2plus_num / max(w2tot, 1), 6),
        "dH_repeats_only": round((hA2_num - hA2plus_num) / max(w2tot, 1), 6),
        "H(outcome|P,A)": round(hA_num / max(wtot, 1), 6),
        "H(outcome|P,A+)": round(hAplus_num / max(wtot, 1), 6),
        "dH_collapsed_by_logging_only_the_side": round((hA_num - hAplus_num) / max(wtot, 1), 6),
        "irreducible_regret_lower_bound": round(regret_sum / max(regret_n, 1), 6),
        "irreducible_regret_n_parents": int(regret_n),
    }
    print(json.dumps(out, indent=2), flush=True)
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "equal_mod_2"
    rel = None if which == "ALL" else which
    res = census(rel, f"c1 x {which}")
    path = HERE / f"choice_point_census_{which}.json"
    path.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("\nwrote", path.name, flush=True)


if __name__ == "__main__":
    main()
