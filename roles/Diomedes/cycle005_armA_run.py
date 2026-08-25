"""Diomedes cycle 005 ARM A — b2 operator commutation, fully enumerated.

Executes the design frozen in CYCLE_005_PREREG_terminal.md S2. Rungs 1-4 throughout:
the whole 6 x 6 x 101 space is enumerated, every number is a count or a ratio of counts,
and the rule class is searched exhaustively rather than fitted.

Q1: does the decomposition ordering survive an oracle whose answer is NOT transparently
encoded in cheap arithmetic features?

    python roles/Diomedes/cycle005_armA_run.py
"""
import itertools
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
TABLES = HERE / "cycle005_operator_tables.json"
OUT = HERE / "cycle005_armA_result.json"
VALUES = list(range(-50, 51))          # frozen core range, 101 values


# ---------------------------------------------------------------- predicates
def predicates():
    """Frozen finite predicate list on v (prereg S2.2). Exhaustively searched."""
    P = [("const_true", lambda v: True),
         ("v_even", lambda v: v % 2 == 0),
         ("v_neg", lambda v: v < 0),
         ("v_zero", lambda v: v == 0),
         ("v_pow2", lambda v: v > 0 and (v & (v - 1)) == 0)]
    for m in (0, 1, 2):
        P.append((f"v_mod3_eq_{m}", lambda v, m=m: v % 3 == m))
    for t in (1, 2, 4, 8, 16, 32):
        P.append((f"abs_v_le_{t}", lambda v, t=t: abs(v) <= t))
    return P


def auc_from_counts(scored):
    """Exact AUC over (score, label) with tie handling. Rational-exact via counts."""
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


def main():
    tab_raw = json.loads(TABLES.read_text(encoding="utf-8"))["operator_tables"]
    T = {op: {int(k): v for k, v in t.items()} for op, t in tab_raw.items()}
    OPS = sorted(T)

    # ---------- rung 1: enumerate the whole space ----------
    # cell[(f,g,v)] = commutes?  ; skip any triple whose tables are incomplete
    comm, missing = {}, 0
    for f, g, v in itertools.product(OPS, OPS, VALUES):
        gv, fv = T[g].get(v), T[f].get(v)
        if gv is None or fv is None:
            missing += 1
            continue
        fgv, gfv = T[f].get(gv), T[g].get(fv)
        if fgv is None or gfv is None:
            missing += 1
            continue
        comm[(f, g, v)] = (fgv == gfv)
    enumerated = len(comm)

    # ---------- states: x = (v, f), actions: a = g ----------
    states = []
    for v, f in itertools.product(VALUES, OPS):
        cand = [(g, comm[(f, g, v)]) for g in OPS if (f, g, v) in comm]
        if 0 < sum(1 for _, c in cand if c) < len(cand):     # both classes present
            states.append(((v, f), cand))

    # ---------- exact ceilings ----------
    # marginal: rank g by global commute rate, ignoring v AND f
    g_rate = {g: (sum(1 for (ff, gg, vv), c in comm.items() if gg == g and c),
                  sum(1 for (ff, gg, vv) in comm if gg == g)) for g in OPS}
    marg = {g: (a / b if b else 0.0) for g, (a, b) in g_rate.items()}
    # f-conditional: rank g by commute rate given f, still ignoring v
    fg_rate = {}
    for f, g in itertools.product(OPS, OPS):
        cells = [c for (ff, gg, vv), c in comm.items() if ff == f and gg == g]
        fg_rate[(f, g)] = sum(cells) / len(cells) if cells else 0.0

    def score_arm(fn):
        vals = [auc_from_counts([(fn(x, g), c) for g, c in cand]) for x, cand in states]
        vals = [a for a in vals if a is not None]
        return round(sum(vals) / len(vals), 4), len(vals)

    a_marg, n_states = score_arm(lambda x, g: marg[g])
    a_fcond, _ = score_arm(lambda x, g: fg_rate[(x[1], g)])
    a_oracle, _ = score_arm(lambda x, g: 1.0 if comm[(x[1], g, x[0])] else 0.0)

    # ---------- rung 4: exhaustive predicate search per (f,g) ----------
    # F_applied uses ONE table application: the predicate sees g(v), not the composition.
    # F_pure sees only v and the operator identities.
    P = predicates()

    def best_pred(f, g, use_applied):
        rows = [(v, comm[(f, g, v)]) for v in VALUES if (f, g, v) in comm]
        if not rows:
            return None, 0.0
        best, bacc = None, -1.0
        for name, fn in P:
            for polarity in (True, False):
                hit = 0
                for v, c in rows:
                    arg = T[g].get(v) if use_applied else v
                    if arg is None:
                        continue
                    pred = fn(arg) if polarity else not fn(arg)
                    hit += (pred == c)
                acc = hit / len(rows)
                if acc > bacc:
                    bacc, best = acc, (name, polarity)
        return best, bacc

    rules = {"F_pure": {}, "F_applied": {}}
    for f, g in itertools.product(OPS, OPS):
        for tag, ua in (("F_pure", False), ("F_applied", True)):
            b, acc = best_pred(f, g, ua)
            rules[tag][f"{f}|{g}"] = {"predicate": b, "exact_accuracy": round(acc, 4)}

    def rule_score(tag, use_applied):
        pmap = {n: fn for n, fn in P}

        def sc(x, g):
            v, f = x
            r = rules[tag][f"{f}|{g}"]["predicate"]
            if r is None:
                return 0.0
            name, pol = r
            arg = T[g].get(v) if use_applied else v
            if arg is None:
                return 0.0
            out = pmap[name](arg)
            return 1.0 if (out if pol else not out) else 0.0
        return score_arm(sc)[0]

    a_pure = rule_score("F_pure", False)
    a_applied = rule_score("F_applied", True)

    # ---------- mandatory assertions (charter S20.3) ----------
    checks = {
        "perfect_predictor_is_1.0": a_oracle == 1.0,
        "constant_predictor_is_0.5": score_arm(lambda x, g: 1.0)[0] == 0.5,
        "monotone_invariance": score_arm(lambda x, g: marg[g])[0]
                               == score_arm(lambda x, g: 3 * marg[g] + 7)[0],
        "enumeration_complete": missing == 0,
    }

    # ---------- hand-checkable rows ----------
    hand = []
    for (v, f), cand in states[:20]:
        hand.append({"v": v, "f": f,
                     "candidates": [{"g": g, "g_of_v": T[g].get(v),
                                     "f_of_g_of_v": T[f].get(T[g].get(v)),
                                     "g_of_f_of_v": T[g].get(T[f].get(v)),
                                     "commutes": c} for g, c in cand]})

    rep = {"prereg": "CYCLE_005_PREREG_terminal.md S2", "arm": "A (b2 commutation)",
           "rungs": "1-4 (exhaustive enumeration; exhaustive rule search)",
           "enumerated_cells": enumerated, "missing_cells": missing,
           "n_states_with_both_classes": n_states,
           "decomposition": {"chance": 0.5, "marginal_ceiling": a_marg,
                             "f_conditional_ceiling": a_fcond,
                             "F_pure": a_pure, "F_applied": a_applied,
                             "oracle": a_oracle},
           "increment_applied_over_pure": round(a_applied - a_pure, 4),
           "increment_pure_over_fcond": round(a_pure - a_fcond, 4),
           "assertions": checks,
           "rules": rules, "hand_checkable_rows": hand}
    OUT.write_text(json.dumps(rep, indent=1), encoding="utf-8")

    print(f"enumerated {enumerated:,} cells, missing {missing}, states {n_states}")
    for k, v in rep["decomposition"].items():
        print(f"  {k:24s} {v}")
    print(f"  F_applied - F_pure       {rep['increment_applied_over_pure']}")
    print(f"  F_pure - f_cond_ceiling  {rep['increment_pure_over_fcond']}")
    print("assertions:", checks)
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
