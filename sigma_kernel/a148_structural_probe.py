#!/usr/bin/env python3
"""
A148 vs A149 structural probe.

The A149 signature returned 0 matches in A148. This script asks WHY:
is A148 covering structurally different territory than A149, or is the
signature too narrow even for an in-family A148 obstruction?
"""

from collections import Counter, defaultdict
from a149_obstruction import (
    parse_step_set, features_of, load_jsonl, ASYMPTOTIC,
    UNANIMOUS_BATTERY, load_kill_verdicts,
)


def load_family(prefix):
    rows = load_jsonl(ASYMPTOTIC)
    out = []
    for r in rows:
        sid = r.get("seq_id", "")
        if not sid.startswith(prefix):
            continue
        steps = parse_step_set(r.get("name", ""))
        if not steps:
            continue
        f = features_of(steps)
        r["_features"] = f
        out.append(r)
    return out


def step_count_dist(family):
    return Counter(r["_features"]["n_steps"] for r in family)


def neg_x_dist_for_5step(family):
    return Counter(r["_features"]["neg_x"] for r in family
                   if r["_features"]["n_steps"] == 5)


def diag_neg_dist_for_5step(family):
    c = Counter()
    for r in family:
        if r["_features"]["n_steps"] == 5:
            c[r["_features"]["has_diag_neg"]] += 1
    return c


def kill_pattern_dist(family, kills):
    """Distribution of how many of the F1+F6+F9+F11 battery fire per seq."""
    c = Counter()
    for r in family:
        sid = r["seq_id"]
        if sid in kills:
            n = len(UNANIMOUS_BATTERY & kills[sid])
            c[n] += 1
    return c


def main():
    a148 = load_family("A148")
    a149 = load_family("A149")
    kills = load_kill_verdicts()

    print(f"\n=== Step-count distribution ===")
    print(f"  {'n_steps':<10} {'A148':>8} {'A149':>8}")
    sc148 = step_count_dist(a148)
    sc149 = step_count_dist(a149)
    keys = sorted(set(sc148) | set(sc149))
    for k in keys:
        print(f"  {k:<10} {sc148.get(k, 0):>8} {sc149.get(k, 0):>8}")

    print(f"\n=== neg_x distribution among 5-step walks ===")
    n148 = neg_x_dist_for_5step(a148)
    n149 = neg_x_dist_for_5step(a149)
    print(f"  {'neg_x':<10} {'A148':>8} {'A149':>8}")
    for k in sorted(set(n148) | set(n149)):
        print(f"  {k:<10} {n148.get(k, 0):>8} {n149.get(k, 0):>8}")

    print(f"\n=== has_diag_neg distribution among 5-step walks ===")
    d148 = diag_neg_dist_for_5step(a148)
    d149 = diag_neg_dist_for_5step(a149)
    print(f"  {'diag_neg':<10} {'A148':>8} {'A149':>8}")
    for k in (False, True):
        print(f"  {str(k):<10} {d148.get(k, 0):>8} {d149.get(k, 0):>8}")

    print(f"\n=== Kill-pattern distribution (count of F1+F6+F9+F11 firing) ===")
    print(f"  Battery members fired:  {'A148':>8} {'A149':>8}")
    kp148 = kill_pattern_dist(a148, kills)
    kp149 = kill_pattern_dist(a149, kills)
    for k in (0, 1, 2, 3, 4):
        print(f"  {k} of 4 fired      {kp148.get(k, 0):>8} {kp149.get(k, 0):>8}")
    print(f"  Total evaluated     {sum(kp148.values()):>8} {sum(kp149.values()):>8}")

    # Identify A148 sequences with at least 3-of-4 kills - "near-unanimous"
    print(f"\n=== A148 'near unanimous' sequences (>=3 of F1+F6+F9+F11) ===")
    near = []
    for r in a148:
        sid = r["seq_id"]
        if sid not in kills: continue
        hit = UNANIMOUS_BATTERY & kills[sid]
        if len(hit) >= 3:
            near.append((sid, sorted(hit), r["_features"]))
    if near:
        for sid, hits, f in near[:15]:
            print(f"  {sid}  hits={hits}  "
                  f"steps={f['n_steps']} neg_x={f['neg_x']} "
                  f"pos_x={f['pos_x']} diag_neg={f['has_diag_neg']}")
    else:
        print("  (none found - A148 simply does not get killed by this battery)")

    # What kill_tests DO fire on A148?
    print(f"\n=== What kill_tests fire on A148 (top 10 most-frequent) ===")
    test_counter = Counter()
    a148_seqids = {r["seq_id"] for r in a148}
    for sid, tests in kills.items():
        if sid in a148_seqids:
            for t in tests:
                test_counter[t] += 1
    for t, c in test_counter.most_common(10):
        marker = "  <-- in unanimous battery" if t in UNANIMOUS_BATTERY else ""
        print(f"  {t:<32} {c:>4}{marker}")


if __name__ == "__main__":
    main()
