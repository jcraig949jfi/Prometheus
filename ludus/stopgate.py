"""Cycle 002 preflight — apply GATE-W1 to the stochastic-stopping family.

Cycle 001 killed three authored worlds because a four-line heuristic played them
optimally. Charter v2 §17 nominates push-your-luck as the first natural family.
Before a season of simulators is built on that nomination, the same question is
put to it: **can a cheap policy already play these games?**

Two measures, reported separately because they answer different things:

  EV RETENTION   cheap policy's expected score / optimal expected score, both
                 computed by EXACT policy evaluation over the full state space.
                 This is the measure that matters in a stochastic world: an agent
                 that picks the optimal action 70% of the time but loses 1% of
                 value has not demonstrated anything a threshold cannot do.
  ACTION GAP     1 - P[cheap action == optimal action], the r0001 analogue,
                 kept so cycle 001 and cycle 002 stay comparable.

The action gap is reported under TWO weightings, and the difference between them
is itself a finding worth watching. Cycle 001's §5.3 defect was uniform sampling
over reachable states, which over-weighted positions no competent play ever
visits and inflated a reading by 0.5. So states are weighted by their
**visitation probability under optimal play**, with the uniform number printed
beside it rather than instead of it.

Pre-registered admission criteria, fixed before the numbers were computed:

  * a world is NOT measurable at the stopping decision if the best cheap policy
    retains >= 0.98 of optimal EV;
  * the r0001-comparable bar stays gap >= 0.20 on visitation-weighted states.

No model calls. Everything here is a DP table.
"""
from __future__ import annotations

import collections
import json
import pathlib
from datetime import datetime, timezone

from ludus.stopworlds import (F7_BONUS_AT, F7_COUNTS, LEDGER, MD_CLAIMABLE,
                              Flip7, MartianDice, RULES_AUDIT, _md_roll_dist,
                              flip7_continue_ev, solve_flip7, solve_martian)

MD_IDX = {"ray": 1, "human": 2, "cow": 3, "chicken": 4}


# --------------------------------------------------------------------------
# FLIP 7 — cheap policies. Each maps a state to True (flip again) or False (bank).
# --------------------------------------------------------------------------

def f7_always_flip(w, s):
    return True


def f7_myopic(w, s):
    """The textbook one-step rule: flip iff the expected immediate change is
    positive. Not naive -- it correctly accounts for losing the whole pot."""
    remaining = sum(F7_COUNTS.values()) - len(s)
    if remaining <= 0:
        return False
    p_bust = sum(F7_COUNTS[r] - 1 for r in s) / remaining
    e_gain = sum(F7_COUNTS[r] / remaining * r for r in F7_COUNTS if r not in s)
    return e_gain > p_bust * sum(s)


def f7_threshold(T):
    def f(w, s):
        return sum(s) < T
    f.__name__ = f"f7_threshold_{T}"
    return f


def f7_count(K):
    def f(w, s):
        return len(s) < K
    f.__name__ = f"f7_count_{K}"
    return f


def f7_evaluate(w: Flip7, policy) -> dict:
    """Exact policy evaluation, plus the visitation measure under that policy."""
    memo, visits = {}, collections.defaultdict(float)
    order = sorted((s for s in _f7_states()), key=lambda s: -len(s))
    for s in order:
        if w.terminal(s):
            memo[s] = float(w.score_if_stop(s))
            continue
        if not policy(w, s):
            memo[s] = float(w.pot(s))
            continue
        ev = 0.0
        for p, nxt, _ in w.outcomes(s):
            if nxt is None:
                continue
            ev += p * (w.score_if_stop(nxt) if w.terminal(nxt) else memo[nxt])
        memo[s] = ev
    # forward pass for visitation mass at DECISION states
    front = {w.initial(): 1.0}
    while front:
        nxt_front = collections.defaultdict(float)
        for s, m in front.items():
            if w.terminal(s) or m <= 1e-12:
                continue
            visits[s] += m
            if not policy(w, s):
                continue
            for p, nxt, _ in w.outcomes(s):
                if nxt is not None:
                    nxt_front[nxt] += m * p
        front = nxt_front
    return {"ev": memo[w.initial()], "visits": dict(visits)}


def _f7_states():
    import itertools
    return [frozenset(c) for k in range(len(F7_COUNTS) + 1)
            for c in itertools.combinations(F7_COUNTS, k)]


# --------------------------------------------------------------------------
# MARTIAN DICE — cheap policies need TWO rules: which symbol to claim, and
# whether to stop. That second decision axis is what makes this world
# structurally unlike Flip 7 despite sharing the CONTINUE/STOP surface.
# --------------------------------------------------------------------------

def md_claim_most(state, roll):
    """Claim whatever symbol you rolled most of. The obvious cheap rule."""
    t, r, h, c, ch = roll
    best, bestn = None, 0
    for sym, got in (("ray", r), ("human", h), ("cow", c), ("chicken", ch)):
        if got == 0 or state[MD_IDX[sym]] > 0:
            continue
        if got > bestn:
            best, bestn = sym, got
    return best


def md_claim_rays_first(state, roll):
    """Take rays if you still need them to beat the tanks, else take the most."""
    t, r, h, c, ch = roll
    tanks = state[0] + t
    if r > 0 and state[1] == 0 and state[1] + r <= tanks + 2:
        return "ray"
    return md_claim_most(state, roll)


def md_stop_threshold(T):
    def f(w, sp):
        return w.score_if_stop(sp) >= T
    f.__name__ = f"md_stop_at_{T}"
    return f


def md_stop_dice(K):
    def f(w, sp):
        return w.dice_left(sp) <= K and w.score_if_stop(sp) > 0
    f.__name__ = f"md_stop_dice_le_{K}"
    return f


def md_myopic(w, sp):
    """FLIP 7's WINNING RULE, TRANSPLANTED. Stop iff one more roll has negative
    expected immediate change: P(turn dies) * pot > E[score gained | survives].

    This is charter §22's critical cell -- different surface (dice, aliens,
    livestock vs cards and numbers), candidate-same mechanism (CONTINUE/STOP
    under evolving risk). If the family in §17 is real, the rule that retains
    0.9991 of optimal in Flip 7 should carry. Nothing about it is tuned to
    Martian Dice; the transplant is deliberately naive.
    """
    n = w.dice_left(sp)
    if n == 0:
        return True
    pot = w.score_if_stop(sp)
    p_dead, e_gain = 0.0, 0.0
    for roll, p in _md_roll_dist(n):
        t, r, h, c, ch = roll
        base = (sp[0] + t, sp[1], sp[2], sp[3], sp[4])
        sym = md_claim_most(base, roll)
        if sym is None:
            p_dead += p
            continue
        nxt = list(base)
        nxt[MD_IDX[sym]] += {"ray": r, "human": h, "cow": c, "chicken": ch}[sym]
        e_gain += p * (w.score_if_stop(tuple(nxt)) - pot)
    return not (e_gain > p_dead * pot)


def md_claim_rays_until_safe(state, roll):
    """Take rays while you are still behind the tanks, then take the most."""
    t, r, h, c, ch = roll
    tanks = state[0] + t
    if r > 0 and state[1] == 0 and state[1] < tanks:
        return "ray"
    return md_claim_most(state, roll)


def md_claim_score_max(state, roll):
    """Claim whichever symbol adds the most to the score right now."""
    t, r, h, c, ch = roll
    best, bestv = None, -1
    for sym, got in (("ray", r), ("human", h), ("cow", c), ("chicken", ch)):
        if got == 0 or state[MD_IDX[sym]] > 0:
            continue
        v = 0 if sym == "ray" else got
        if v > bestv:
            best, bestv = sym, v
    return best


def md_evaluate(w: MartianDice, claim_rule, stop_rule) -> dict:
    memo: dict = {}

    def W(sp):
        if w.dice_left(sp) == 0:
            return float(w.score_if_stop(sp))
        if stop_rule(w, sp):
            return float(w.score_if_stop(sp))
        return V(sp)

    def V(s):
        if s in memo:
            return memo[s]
        memo[s] = 0.0                      # guard; states form a DAG by dice used
        n = w.dice_left(s)
        if n == 0:
            memo[s] = float(w.score_if_stop(s))
            return memo[s]
        total = 0.0
        for roll, p in _md_roll_dist(n):
            t, r, h, c, ch = roll
            base = (s[0] + t, s[1], s[2], s[3], s[4])
            sym = claim_rule(base, roll)
            if sym is None:
                continue                   # turn busts, contributes 0
            sp = list(base)
            sp[MD_IDX[sym]] += {"ray": r, "human": h, "cow": c, "chicken": ch}[sym]
            total += p * W(tuple(sp))
        memo[s] = total
        return total

    return {"ev": V(w.initial())}


# --------------------------------------------------------------------------

def f7_action_gap(w, opt, policy):
    """Gap under uniform and under optimal-play visitation weighting."""
    opt_visits = f7_evaluate(w, lambda _w, _s: _f7_opt_action(_w, opt, _s))["visits"]
    agree_u = tot_u = 0
    agree_w = tot_w = 0.0
    for s in _f7_states():
        if w.terminal(s):
            continue
        o = _f7_opt_action(w, opt, s)
        a = policy(w, s)
        tot_u += 1
        agree_u += (o == a)
        m = opt_visits.get(s, 0.0)
        tot_w += m
        agree_w += m * (o == a)
    return (round(1 - agree_u / tot_u, 4),
            round(1 - agree_w / tot_w, 4) if tot_w else None)


def _f7_opt_action(w, opt, s):
    return flip7_continue_ev(w, opt, s) > w.pot(s)


def main() -> None:
    w7, wm = Flip7(), MartianDice()
    opt7 = solve_flip7(w7)
    optm = solve_martian(wm)
    ev7_star, evm_star = opt7[w7.initial()], optm[wm.initial()]

    out = {"purpose": "GATE-W1 applied to charter v2 §17's stochastic-stopping family",
           "no_model_calls": True,
           "preregistered_criteria": {
               "not_measurable_if_best_cheap_EV_retention_ge": 0.98,
               "r0001_comparable_bar_action_gap_ge": 0.20,
               "weighting": "visitation probability under optimal play; uniform "
                            "reported beside it, never instead of it"},
           "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "FLIP7": {"optimal_ev": round(ev7_star, 4), "policies": {}},
           "MARTIAN_DICE": {"optimal_ev": round(evm_star, 4), "policies": {}},
           "rules_audit": RULES_AUDIT}

    print(f"FLIP7  optimal EV = {ev7_star:.4f}")
    cands = [("always_flip", f7_always_flip), ("myopic_one_step", f7_myopic)]
    cands += [(f"threshold_{T}", f7_threshold(T)) for T in (10, 15, 20, 25, 30, 35)]
    cands += [(f"count_{K}", f7_count(K)) for K in (3, 4, 5, 6)]
    for nm, pol in cands:
        ev = f7_evaluate(w7, pol)["ev"]
        gu, gw = f7_action_gap(w7, opt7, pol)
        out["FLIP7"]["policies"][nm] = {"ev": round(ev, 4),
                                        "ev_retention": round(ev / ev7_star, 4),
                                        "action_gap_uniform": gu,
                                        "action_gap_visitation": gw}
        print(f"  {nm:18s} EV={ev:7.4f}  retention={ev/ev7_star:.4f}  "
              f"gap_uniform={gu:.4f}  gap_visitation={gw:.4f}")

    print(f"\nMARTIAN_DICE  optimal EV = {evm_star:.4f}")
    mcands = []
    for cn, cr in (("most", md_claim_most), ("rays_first", md_claim_rays_first)):
        for T in (2, 3, 4, 5, 6):
            mcands.append((f"{cn}+stop_at_{T}", cr, md_stop_threshold(T)))
        for K in (0, 2, 4, 6):
            mcands.append((f"{cn}+stop_dice<={K}", cr, md_stop_dice(K)))
    for cn, cr in (("most", md_claim_most), ("rays_until_safe", md_claim_rays_until_safe),
                   ("score_max", md_claim_score_max)):
        mcands.append((f"{cn}+MYOPIC_TRANSPLANT", cr, md_myopic))
    for T in (2, 3):
        for K in (2, 4):
            mcands.append((f"score_max+stop_at_{T}_or_dice<={K}", md_claim_score_max,
                           (lambda T=T, K=K: (lambda w, sp: w.score_if_stop(sp) >= T
                                              or (w.dice_left(sp) <= K
                                                  and w.score_if_stop(sp) > 0)))()))
    for nm, cr, sr in mcands:
        ev = md_evaluate(wm, cr, sr)["ev"]
        out["MARTIAN_DICE"]["policies"][nm] = {
            "ev": round(ev, 4), "ev_retention": round(ev / evm_star, 4)}
        print(f"  {nm:24s} EV={ev:7.4f}  retention={ev/evm_star:.4f}")

    for k in ("FLIP7", "MARTIAN_DICE"):
        best = max(v["ev_retention"] for v in out[k]["policies"].values())
        out[k]["best_cheap_retention"] = best
        out[k]["measurable_at_stopping_decision"] = best < 0.98
        print(f"\n{k}: best cheap retention {best:.4f} -> "
              f"{'MEASURABLE' if best < 0.98 else 'NOT MEASURABLE'}")

    LEDGER.mkdir(parents=True, exist_ok=True)
    p = LEDGER / "cycle002_stopgate.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {p}")


if __name__ == "__main__":
    main()
