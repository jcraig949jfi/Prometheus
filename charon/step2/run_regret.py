"""Step 2 — THE REGRET EXPERIMENT on c1 x equal_mod_2.

Design fixed by charon/step2/PREREGISTRATION_c1_regret_2026-08-25.md (+ amendment 1), filed and
committed before this script was written. Nothing here re-derives the kill rule or the prediction.

  primary      REGRET  R = Y(S,A*) - Y(S,Ahat)  on DIVERGENT parents. Lower is better;
               coin-flip = 0.5, oracle = 0.0.
  policies     IMITATION      Ahat = argmax P(A|S)        (what the plan names a diagnostic)
               NAVIGATION     Ahat = argmax P(Y=1|S,A)    (plan R-C: "producing a better
                                                           outcome is navigation")
  baselines    majority action | P(A) | P(A|coarse S) | P(A|S)
  holdouts     random, parent, object-family, structural-regime   (pre-registered)
               content                                            (amendment 1, added control)
  SE           CLUSTERED on parent, over DEDUPLICATED content (prereg S2 + amendment C3).

S is the PARENT's pre-decision state. A child row stores the post-mutation state, so predicting
the action from a child's own fields is leakage, not navigation.

    python charon/step2/run_regret.py
"""
import collections
import glob
import hashlib
import json
import math
import pathlib
import random
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
REL = "equal_mod_2"
SEED = 20260825
random.seed(SEED)

PSTATE = ("catalog_a", "catalog_b", "invariant_a", "invariant_b",
          "object_a", "object_b", "value_a", "value_b")


def fold(s, salt, frac=0.3):
    """Deterministic hash split. No Date/random dependence, so the split is reproducible."""
    h = hashlib.blake2b(f"{salt}|{s}".encode(), digest_size=8).digest()
    return "test" if int.from_bytes(h, "big") / 2**64 < frac else "train"


def load_parents():
    parents = {}
    for sh in sorted(glob.glob(str(HERE / "parent_shards" / "p-*.jsonl"))):
        with open(sh, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                rid = d.get("record_id")
                if not rid:
                    continue
                k = int(rid[:16], 16)                   # ids are 64-hex; 16 is ample and compact
                if k not in parents:                    # content-addressed: first copy wins
                    parents[k] = tuple(sys.intern(str(d.get(f))) for f in PSTATE)
    print(f"parents loaded (deduplicated by record_id): {len(parents):,}")
    return parents


def load_children(parents):
    """One row per DISTINCT child record_id (amendment C3), joined to its parent's state."""
    seen = set()
    units = []
    missing = 0
    for sh in sorted(glob.glob(str(HERE / "shards" / "c1-*.jsonl"))):
        with open(sh, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                if d.get("relation") != REL:
                    continue
                rid, pid = d.get("record_id"), d.get("parent_record_id")
                a, y = d.get("mutation_side"), d.get("holds")
                if a not in ("a", "b") or y is None or not pid or not rid:
                    continue
                rid, pid = int(rid[:16], 16), int(pid[:16], 16)
                st = parents.get(pid)
                if st is None:
                    missing += 1
                    continue
                key = (rid, pid)
                if key in seen:
                    continue
                seen.add(key)
                units.append((pid, st, a, 1 if y else 0, rid))
    print(f"units (distinct child x parent edges with a resolved parent state): {len(units):,}")
    print(f"children dropped, parent state not extracted: {missing:,}")
    return units


def divergent(units):
    """Parents whose two recorded actions produced DIFFERENT outcomes."""
    by = collections.defaultdict(dict)
    for pid, st, a, y, rid in units:
        by[pid].setdefault(a, set()).add(y)
    out = {}
    diag = collections.Counter()
    for pid, acts in by.items():
        ambiguous = any(len(v) > 1 for v in acts.values())
        if ambiguous:
            # SAME side on the SAME parent produced BOTH outcomes -> the side choice does not
            # determine the outcome. This is amendment 1b (UNDER-SPECIFIED ACTION) measured
            # directly: the outcome is driven by the replacement object, which the corpus
            # records as part of the action taken but not as part of the action modelled.
            diag["action_ambiguous_parents"] += 1
        if len(acts) == 2:
            diag["both_actions"] += 1
        if len(acts) == 2 and not ambiguous:
            ya, yb = next(iter(acts["a"])), next(iter(acts["b"]))
            diag["both_actions_unambiguous"] += 1
            if ya != yb:
                out[pid] = (ya, yb)
    diag["divergent"] = len(out)
    return out, dict(diag)


def clustered_se(values_by_cluster):
    """SE of a mean, clustered on parent: n = clusters, not rows (prereg S2)."""
    m = [sum(v) / len(v) for v in values_by_cluster.values() if v]
    n = len(m)
    if n < 2:
        return float("nan"), n
    mu = sum(m) / n
    var = sum((x - mu) ** 2 for x in m) / (n - 1)
    return math.sqrt(var / n), n


def evaluate(units, div, salt, assign, label):
    """Fit on train, evaluate regret on test divergent parents.

    `assign` returns 'train' | 'test' | 'drop'. Dropping is needed for the object-family split:
    the pre-registration requires that no object VALUE appear on both sides, so a unit whose two
    objects fall on opposite sides is discarded rather than silently assigned. Discards are
    reported, never hidden (no silent caps)."""
    tr, te, dropped = [], [], 0
    for u in units:
        s = assign(u)
        if s == "drop":
            dropped += 1
        elif s == "test":
            te.append(u)
        else:
            tr.append(u)

    # --- fit on TRAIN only ---
    pA = collections.Counter()
    pA_full = collections.defaultdict(collections.Counter)
    pA_coarse = collections.defaultdict(collections.Counter)
    q_full = collections.defaultdict(lambda: collections.Counter())
    q_coarse = collections.defaultdict(lambda: collections.Counter())
    for pid, st, a, y, rid in tr:
        pA[a] += 1
        pA_full[st][a] += 1
        pA_coarse[st[:4]][a] += 1
        q_full[(st, a)][y] += 1
        q_coarse[(st[:4], a)][y] += 1
    maj = pA.most_common(1)[0][0] if pA else "a"

    def imitate(st):
        c = pA_full.get(st) or pA_coarse.get(st[:4]) or pA
        return c.most_common(1)[0][0] if c else maj

    def navigate(st):
        best, arg = None, None
        for a in ("a", "b"):
            c = q_full.get((st, a)) or q_coarse.get((st[:4], a))
            if not c:
                continue
            r = c[1] / (c[0] + c[1])
            if best is None or r > best:
                best, arg = r, a
        return arg if arg else imitate(st)

    # --- evaluate on TEST divergent parents ---
    st_by_pid, seen = {}, set()
    for pid, st, a, y, rid in te:
        st_by_pid.setdefault(pid, st)
    res = {}
    for name, pol in (("imitation", imitate), ("navigation", navigate),
                      ("majority", lambda st: maj),
                      ("coin", lambda st: "a" if random.random() < 0.5 else "b")):
        cl = collections.defaultdict(list)
        acc_cl = collections.defaultdict(list)
        for pid, st in st_by_pid.items():
            if pid not in div:
                continue
            ya, yb = div[pid]
            best = max(ya, yb)
            ahat = pol(st)
            got = ya if ahat == "a" else yb
            cl[pid].append(best - got)                       # regret in {0,1}
        se, n = clustered_se(cl)
        mean = (sum(sum(v) / len(v) for v in cl.values()) / n) if n else float("nan")
        res[name] = {"mean_regret": round(mean, 6) if n else None,
                     "clustered_SE": round(se, 6) if n == n else None,
                     "test_divergent_parents": n}

    # imitation accuracy diagnostic (never the headline -- plan R-C)
    hit = tot = 0
    for pid, st, a, y, rid in te:
        hit += (imitate(st) == a)
        tot += 1
    res["_diagnostic_action_accuracy"] = round(hit / tot, 6) if tot else None
    res["_test_rows"] = tot
    res["_train_rows"] = len(tr)
    res["_dropped_units"] = dropped
    print(f"  {label:<20} n_div_test={res['imitation']['test_divergent_parents']:>7,}  "
          f"imitation R={res['imitation']['mean_regret']}  "
          f"navigation R={res['navigation']['mean_regret']}  "
          f"coin R={res['coin']['mean_regret']}")
    return res


def main():
    parents = load_parents()
    units = load_children(parents)
    div, divdiag = divergent(units)
    print("divergence diagnostics:", json.dumps(divdiag, indent=2))

    floor = collections.Counter(u[2] for u in units)
    tot = sum(floor.values())
    ceil_num = 0
    cells = collections.defaultdict(collections.Counter)
    for pid, st, a, y, rid in units:
        cells[st][a] += 1
    for c in cells.values():
        ceil_num += max(c.values())
    attainable = {
        "floor_majority_action_rate": round(max(floor.values()) / tot, 6),
        "ceiling_within_state_cell_majority": round(ceil_num / tot, 6),
        "distinct_state_cells": len(cells),
        "mean_rows_per_state_cell": round(tot / max(len(cells), 1), 3),
    }
    print("\nattainable range:", json.dumps(attainable, indent=2))

    def by_key(keyfn, salt):
        return lambda u: fold(keyfn(u), salt)

    def object_family(u):
        """Pre-registration: no object VALUE on both sides. A unit whose two objects fall on
        opposite sides is DROPPED, not assigned."""
        fa = fold(u[1][4], "object_family")
        fb = fold(u[1][5], "object_family")
        return fa if fa == fb else "drop"

    splits = {
        "random": by_key(lambda u: f"{u[4]}|{u[0]}", "random"),
        "parent": by_key(lambda u: str(u[0]), "parent"),
        "object_family": object_family,
        "structural_regime": by_key(lambda u: "|".join(u[1][:4]), "structural_regime"),
        "content": by_key(lambda u: str(u[4]), "content"),
    }
    print("\nholdouts:")
    results = {k: evaluate(units, div, k, f, k) for k, f in splits.items()}

    out = {"population": {"units": len(units), "parents_with_state": len(parents),
                          "divergent_parents": len(div)},
           "divergence_diagnostics": divdiag,
           "attainable_range": attainable,
           "results": results,
           "notes": "regret: lower is better; coin-flip 0.5, oracle 0.0. SE clustered on parent."}
    (HERE / "regret_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nwrote regret_results.json")


if __name__ == "__main__":
    main()
