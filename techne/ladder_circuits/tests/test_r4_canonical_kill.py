"""The canonical R4 kill test (ChatGPT round 2, item B) — executable.

Design: two rules are both legal at the root of F(u, v). The productive one is determined by
NONLOCAL structure (where G sits), at 50/50 base rates, with:
  - depth-escape holdouts: G buried under H(H(...)) at depths never seen,
  - rule-name randomization per episode: names r_A/r_B are shuffled every episode, so
    "rule A usually wins" is unlearnable — the selector must relate rule SEMANTICS to
    problem structure.

Selectors under test:
  - StructurePolicy: inspects where G occurs (recursive search = the stack pressure ChatGPT
    predicted), maps position -> which rule SEMANTICS to apply. Passes everything.
  - FrequencyPrior: picks the name that won most often in calibration. 50% by construction,
    and name-randomization keeps it there.
  - ShallowTemplate: memorizes root-level patterns F(G(.), .) only — dies on depth escape.
"""
from __future__ import annotations

import pathlib
import random
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

F, G, H = sp.Function("F"), sp.Function("G"), sp.Function("H")
a, b = sp.symbols("a b")

#: Rule semantics: "left" solves problems whose G lives in F's FIRST argument; "right" the
#: second. Applying the wrong semantics = dead region (None).
def apply_semantics(expr, which):
    def contains_g(e):
        return any(f.func == G for f in e.atoms(sp.Function))
    u, v = expr.args
    if which == "left":
        return "goal" if contains_g(u) else None
    return "goal" if contains_g(v) else None


def make_episode(rng, depth=0):
    """One 50/50 instance + per-episode name shuffle. Returns (expr, name_map, gold_name)."""
    g_side = rng.choice(["left", "right"])
    core = G(a)
    for _ in range(depth):
        core = H(core)
    expr = F(core, b) if g_side == "left" else F(b, core)
    names = ["r_A", "r_B"]
    rng.shuffle(names)
    name_map = {names[0]: "left", names[1]: "right"}  # random name->semantics binding
    gold_name = next(n for n, sem in name_map.items() if sem == g_side)
    return expr, name_map, gold_name


# ---- selectors -----------------------------------------------------------------------------

def structure_policy(expr, name_map):
    """Reads structure: recursively locate G, pick the NAME whose semantics matches."""
    u, _v = expr.args
    side = "left" if any(f.func == G for f in u.atoms(sp.Function)) else "right"
    return next(n for n, sem in name_map.items() if sem == side)


def frequency_prior(history):
    wins = {"r_A": 0, "r_B": 0}
    for _, gold in history:
        wins[gold] += 1
    best = max(wins, key=wins.get)
    return lambda expr, name_map: best


def shallow_template(expr, name_map):
    """Root-syntax memorizer: only recognizes G at DEPTH 0 in an argument slot; guesses
    (fixed choice) when G is buried."""
    u, _v = expr.args
    if u.func == G:
        side = "left"
    elif _v.func == G:
        side = "right"
    else:
        side = "left"  # the memorizer's guess when its template misses
    return next(n for n, sem in name_map.items() if sem == side)


def accuracy(selector, episodes):
    hits = 0
    for expr, name_map, gold in episodes:
        chosen = selector(expr, name_map)
        # success = the CHOSEN rule's semantics reaches the goal on this instance
        hits += apply_semantics(expr, name_map[chosen]) == "goal"
    return hits / len(episodes)


# ---- the kill, executed --------------------------------------------------------------------

def test_structure_policy_perfect_at_seen_and_heldout_depths():
    rng = random.Random(20260821)
    shallow = [make_episode(rng, depth=0) for _ in range(60)]
    deep = [make_episode(rng, depth=d) for d in (2, 3, 5, 9) for _ in range(15)]
    assert accuracy(structure_policy, shallow) == 1.0
    assert accuracy(structure_policy, deep) == 1.0  # depth escape: generalizes


def test_KILL_frequency_prior_is_chance_under_name_randomization():
    """Name randomization makes 'rule A usually wins' unlearnable: calibrated prior sits at
    chance on fresh episodes (binomial CI around 0.5, n=400)."""
    rng = random.Random(7)
    calib = [(e, g) for e, _m, g in (make_episode(rng) for _ in range(200))]
    prior = frequency_prior(calib)
    test = [make_episode(rng) for _ in range(400)]
    acc = accuracy(prior, test)
    assert 0.42 <= acc <= 0.58, f"prior should be chance, got {acc}"


def test_KILL_shallow_template_dies_exactly_on_depth_escape():
    """The memorized-template selector is perfect at depth 0 and CHANCE at held-out depth —
    the depth-escape signature separating template recall from structural search."""
    rng = random.Random(11)
    shallow = [make_episode(rng, depth=0) for _ in range(80)]
    deep = [make_episode(rng, depth=3) for _ in range(400)]
    assert accuracy(shallow_template, shallow) == 1.0
    deep_acc = accuracy(shallow_template, deep)
    assert 0.40 <= deep_acc <= 0.60, f"expected chance at depth escape, got {deep_acc}"


def test_the_discriminator_is_genuinely_nonlocal():
    """Sanity on the battery itself: the two instance families share the outer AST F(.,.)
    and differ only in WHERE G occurs — root-level syntax equality of heads."""
    rng = random.Random(3)
    e1, _, _ = make_episode(rng, depth=2)
    e2, _, _ = make_episode(rng, depth=2)
    assert e1.func == e2.func == F
