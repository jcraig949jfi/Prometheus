"""The circuit registry — reasoning circuits written against the interface only.

A circuit sees a compiled table and nothing else. It cannot read a rulebook,
cannot know which game it is in, cannot reference a card name or a die face. That
restriction is the whole point: a circuit that needs game-specific knowledge to
work is not a transferable circuit, and forbidding it at the type level means the
bench cannot accidentally credit one.

Two axes, kept separate because cycle 002 measured them carrying wildly different
shares of a world's difficulty (86% of Martian Dice's residual was on SELECT and
essentially none on STOP):

    SELECT(cw, s, opts) -> chosen option
    STOP(cw, s, select) -> True to bank

Identifiers stay ugly (charter v1 §6). English names are conveniences attached
after the fact and are never the canonical handle.
"""
from __future__ import annotations

REGISTRY: dict = {}


def circuit(rid: str, axis: str, doc: str, transferable: bool = True):
    def deco(fn):
        fn.rid, fn.axis, fn.doc = rid, axis, doc
        REGISTRY[rid] = {"id": rid, "axis": axis, "doc": doc, "fn": fn,
                         "transferable": transferable}
        return fn
    return deco


# ==========================================================================
# SELECT circuits
# ==========================================================================

@circuit("r0010", "SELECT", "bank the most right now: take the option with the "
                            "highest immediate pot")
def select_greedy_pot(cw, s, opts):
    return max(opts, key=lambda x: cw.pot[x])


@circuit("r0011", "SELECT", "preserve capacity: take the option that consumes the "
                            "least irreversible capacity, ties to immediate pot")
def select_min_consumption(cw, s, opts):
    return max(opts, key=lambda x: (-cw.cons.get((s, x), 0.0), cw.pot[x]))


@circuit("r0012", "SELECT", "one-ply lookahead: take the option whose single next "
                            "draw has the best greedy expected pot")
def select_one_ply(cw, s, opts):
    return max(opts, key=lambda x: _one_draw_ev(cw, x))


@circuit("r0013", "SELECT", "null circuit: take the first option in enumeration "
                            "order, reading nothing about the state", transferable=False)
def select_null(cw, s, opts):
    return opts[0]


@circuit("r0014", "SELECT", "spend capacity only when it pays: take the option "
                            "maximising pot gain per unit capacity consumed")
def select_pot_per_capacity(cw, s, opts):
    def key(x):
        gain = cw.pot[x] - cw.pot[s]
        spent = cw.cons.get((s, x), 0.0)
        return gain / spent if spent > 1e-12 else (gain + 1e6)
    return max(opts, key=key)


def _one_draw_ev(cw, s):
    """Expected pot after ONE more draw under greedy play, from s.

    MEMOISED ON THE COMPILED WORLD, and it matters more than it looks. The value
    depends only on `s`, but `select_one_ply` calls it once per OPTION per state,
    so without a cache a single policy evaluation costs
    O(states x draws x options^2). Flip 7 and Martian Dice are small enough that
    this never showed; Can't Stop is 68,873 states x 126 rolls x ~6 options and
    the run wedged there for the better part of an hour looking merely slow.

    The cache lives on the compiled world rather than in an `lru_cache` because
    hashing these state tuples through a bounded cache was measured SLOWER than
    recomputation elsewhere in this bench - a plain dict keyed by state avoids
    both problems.
    """
    memo = getattr(cw, "_one_draw_memo", None)
    if memo is None:
        memo = cw._one_draw_memo = {}
    v = memo.get(s)
    if v is not None:
        return v
    if cw.forced[s]:
        memo[s] = cw.pot[s]
        return memo[s]
    total = 0.0
    for p, opts in cw.trans.get(s, ()):
        if not opts:
            continue
        total += p * max(cw.pot[x] for x in opts)
    memo[s] = total
    return total


# ==========================================================================
# STOP circuits
# ==========================================================================

@circuit("r0003", "STOP", "myopic one-step rule: stop iff P(death) * pot >= "
                          "E[immediate gain]. Cycle 002's transferring circuit.")
def stop_myopic(cw, s, select):
    if cw.forced[s]:
        return True
    pot = cw.pot[s]
    p_dead = 0.0
    e_gain = 0.0
    for p, opts in cw.trans.get(s, ()):
        if not opts:
            p_dead += p
            continue
        e_gain += p * (cw.pot[select(cw, s, opts)] - pot)
    return not (e_gain > p_dead * pot)


@circuit("r0004", "STOP", "floor: never bank voluntarily, ride to forced end or death",
         transferable=False)
def stop_never(cw, s, select):
    return cw.forced[s]


@circuit("r0005", "STOP", "floor: bank at the first opportunity", transferable=False)
def stop_always(cw, s, select):
    return True


@circuit("r0007", "STOP", "survival rule: stop once the chance of surviving one "
                          "more draw falls below one half")
def stop_survival_half(cw, s, select):
    if cw.forced[s]:
        return True
    p_dead = sum(p for p, opts in cw.trans.get(s, ()) if not opts)
    return p_dead >= 0.5


@circuit("r0015", "STOP", "two-ply myopic: stop iff continuing for TWO draws under "
                          "greedy play has negative expected change")
def stop_myopic_two(cw, s, select):
    if cw.forced[s]:
        return True
    pot = cw.pot[s]
    val = 0.0
    for p, opts in cw.trans.get(s, ()):
        if not opts:
            continue
        nxt = select(cw, s, opts)
        val += p * (_one_draw_ev(cw, nxt) if not cw.forced[nxt] else cw.pot[nxt])
    return not (val > pot)


def stop_threshold(T: float, label: str):
    """Bank once the pot reaches T.

    FITTED PER WORLD and therefore marked non-transferable: T is swept and the
    best value kept. That makes it the strongest cheap baseline available, which
    is exactly what a genuinely transferable circuit should have to beat --
    `feedback_counter_baseline_discriminator`: the bar is never "beats random".
    """
    def f(cw, s, select):
        return cw.forced[s] or cw.pot[s] >= T
    f.rid, f.axis, f.doc = label, "STOP", f"fitted pot threshold T={T:.4g}"
    return f


SELECT_CIRCUITS = [v["fn"] for v in REGISTRY.values() if v["axis"] == "SELECT"]
STOP_CIRCUITS = [v["fn"] for v in REGISTRY.values() if v["axis"] == "STOP"]


def optimal_select(V, W):
    def f(cw, s, opts):
        return max(opts, key=lambda x: W.get(x, cw.pot[x]))
    f.rid, f.axis, f.doc = "OPTIMAL", "SELECT", "exact optimal, read off the DP table"
    return f


def optimal_stop(V, W):
    """Optimal GIVEN OPTIMAL CONTINUATION — a real caveat, not a footnote.

    Bolted onto a cheap SELECT circuit this is mismatched and can score slightly
    worse than a myopic stopper that at least evaluates the continuation it will
    actually receive. Cycle 002 measured -0.0005 doing exactly that. An ablation
    that swaps one component for a component optimised against a different
    partner is not a clean decomposition, and the bench reports rather than
    smooths it.
    """
    def f(cw, s, select):
        if cw.forced[s]:
            return True
        return cw.pot[s] >= V.get(s, 0.0)
    f.rid, f.axis, f.doc = "OPTIMAL", "STOP", "exact optimal, read off the DP table"
    return f
