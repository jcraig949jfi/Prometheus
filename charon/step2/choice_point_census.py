"""CHOICE-POINT CENSUS on c1 — the denominator the navigation thesis actually needs.

Prompted by external review, 2026-08-25 (Class III input, Class I output). The reviewer's central
objection, which I accept: *a transition graph is not a navigation graph.* You can have strong
P(next | current) while carrying no information about argmax_a P(success | current, a). So
"181,424,844 parent-linked rows" is an upper bound on navigational observations, NOT a count of
decisions. Everything that is not a choice point is trajectory data.

This computes, without any new corpus scan (c1 shards are already on disk):

  k_P            distinct COMPLETED interventions A+ = (side, replacement object) per parent
  decision-bearing parents   k_P >= 2 AND outcomes differ across A+
  side-only divergent        the weaker notion used so far (>=2 sides, outcomes differ)
  (P,A) collision rate       fraction of (parent, side) groups containing MULTIPLE outcomes
                             -> identical recorded decisions, materially different outcomes
                             -> the recorded action does not specify the intervention (Q4)
  dH                         H(outcome | P,A) - H(outcome | P,A+)
                             how much outcome variation the LOGGER collapsed by recording only
                             the side and not the replacement
  irreducible regret LB      per parent: (best outcome over observed A+) minus (best outcome
                             achievable by a policy that can only choose the SIDE, i.e. the
                             better of the two side-wise means). Arithmetic only, no model.
                             This is decision information mathematically unavailable from the
                             recorded action vocabulary.

RECOVERING THE COMPLETED ACTION. `mutation_side` names which side was mutated; the replacement is
then that side's object IN THE CHILD. So A+ is recoverable from child rows alone -- no parent join
and no new scan.

    python charon/step2/choice_point_census.py
"""
import collections
import glob
import json
import math
import pathlib
import zlib

HERE = pathlib.Path(__file__).resolve().parent
SHARDS = sorted(glob.glob(str(HERE / "shards" / "c1-*.jsonl")))


def H(counter):
    n = sum(counter.values())
    if n <= 1:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in counter.values() if c)


def census(rel_filter, label):
    # parent -> {(side, replacement) : Counter(outcome)}
    par = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    seen = set()
    rows = 0
    for sh in SHARDS:
        with open(sh, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                if rel_filter and d.get("relation") != rel_filter:
                    continue
                a, y, pid, rid = (d.get("mutation_side"), d.get("holds"),
                                  d.get("parent_record_id"), d.get("record_id"))
                if a not in ("a", "b") or y is None or not pid or not rid:
                    continue
                k = (rid[:16], pid[:16])
                if k in seen:
                    continue
                seen.add(k)
                rows += 1
                repl = d.get("object_a") if a == "a" else d.get("object_b")
                p = zlib.crc32(pid[:16].encode())
                par[pid[:16]][(a, str(repl))][1 if y else 0] += 1

    n_par = len(par)
    kP = collections.Counter()
    decision_bearing = side_divergent = 0
    pa_groups = pa_multi = 0
    hA_num = hAplus_num = wtot = 0.0
    regret_lb_sum = regret_n = 0

    for pid, acts in par.items():
        kP[min(len(acts), 6)] += 1

        outs_by_side = collections.defaultdict(collections.Counter)
        for (side, repl), oc in acts.items():
            for o, c in oc.items():
                outs_by_side[side][o] += c

        # (P,A) collision: same parent, same SIDE, both outcomes observed
        for side, oc in outs_by_side.items():
            pa_groups += 1
            if len(oc) > 1:
                pa_multi += 1

        # conditional entropies, weighted by group size
        for side, oc in outs_by_side.items():
            w = sum(oc.values())
            hA_num += w * H(oc)
            wtot += w
        for (side, repl), oc in acts.items():
            hAplus_num += sum(oc.values()) * H(oc)

        # decision-bearing: >=2 completed interventions with differing outcomes
        seen_out = set()
        for oc in acts.values():
            seen_out |= set(oc)
        if len(acts) >= 2 and len(seen_out) > 1:
            decision_bearing += 1
        if len(outs_by_side) >= 2:
            sa = {s: (sum(o * c for o, c in oc.items()) / sum(oc.values()))
                  for s, oc in outs_by_side.items()}
            if len(set(round(v, 9) for v in sa.values())) > 1 or any(
                    len(oc) > 1 for oc in outs_by_side.values()):
                pass
            if len({tuple(sorted(oc)) for oc in outs_by_side.values()}) > 1:
                side_divergent += 1

        # irreducible regret lower bound (arithmetic, no model)
        if len(acts) >= 2:
            best_aplus = max(max(oc) for oc in acts.values())
            best_side = max(sum(o * c for o, c in oc.items()) / sum(oc.values())
                            for oc in outs_by_side.values())
            regret_lb_sum += best_aplus - best_side
            regret_n += 1

    out = {
        "population": label,
        "rows_deduplicated": rows,
        "parents": n_par,
        "k_P_distribution (distinct completed interventions per parent, 6+ bucketed)":
            {str(k): v for k, v in sorted(kP.items())},
        "parents_with_k_P_ge_2": sum(v for k, v in kP.items() if k >= 2),
        "DECISION_BEARING_parents (k_P>=2 and outcomes differ)": decision_bearing,
        "decision_bearing_fraction_of_parents": round(decision_bearing / max(n_par, 1), 6),
        "side_only_divergent_parents": side_divergent,
        "(P,A)_groups": pa_groups,
        "(P,A)_groups_with_MULTIPLE_outcomes": pa_multi,
        "(P,A)_collision_rate": round(pa_multi / max(pa_groups, 1), 6),
        "H(outcome|P,A)": round(hA_num / max(wtot, 1), 6),
        "H(outcome|P,A+)": round(hAplus_num / max(wtot, 1), 6),
        "dH_collapsed_by_logging_only_the_side": round((hA_num - hAplus_num) / max(wtot, 1), 6),
        "irreducible_regret_lower_bound": round(regret_lb_sum / max(regret_n, 1), 6),
        "irreducible_regret_n_parents": regret_n,
    }
    print(json.dumps(out, indent=2))
    return out


def main():
    res = {"equal_mod_2": census("equal_mod_2", "c1 x equal_mod_2"),
           "all_c1": census(None, "c1, all relations")}
    (HERE / "choice_point_census.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("\nwrote choice_point_census.json")


if __name__ == "__main__":
    main()
