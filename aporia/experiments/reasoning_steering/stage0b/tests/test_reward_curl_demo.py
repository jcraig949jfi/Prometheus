"""TDD tests for path B: curl explains 'combined < random while single heads work'."""
import pytest

from aporia.experiments.reasoning_steering.stage0b.reward_curl_demo import (
    make_reward_scenario, ranking_qualities, curl_of, sweep_curl_vs_combination,
)


# 1. AUTHORITY — at zero cyclic weight, combining is fine; the informative head dominates.
# (Note: absolute curl is NOT ~0 even here -- a single head's sign-flow carries the
#  saturation baseline. Only RELATIVE curl movement is meaningful; see test_law.)
def test_authority_no_curl_combination_is_fine():
    recs, q = make_reward_scenario(n=40, k_cyclic=4, cyclic_weight=0.0, noise=0.05, seed=0)
    rq = ranking_qualities(recs, q)
    assert rq["best_single"] > 0.9                       # informative head tracks q
    assert rq["combined"] > 0.8                          # combination still good (no damage)
    assert rq["combined"] == pytest.approx(rq["best_single"], abs=0.15)


# 2. THE LAW — as curl rises, combination degrades below the best single head.
def test_law_curl_damages_combination():
    rows = sweep_curl_vs_combination(n=40, k_cyclic=4, noise=0.05, seed=0)
    lo, hi = rows[0], rows[-1]                            # weight 0.0 vs 2.0
    assert hi["curl"] > lo["curl"] + 0.2                 # curl rose with cyclic weight
    assert hi["combined"] < hi["best_single"]            # combining now HURTS vs best single
    assert hi["combined"] < lo["combined"]               # combined quality fell
    # the informative head itself is unharmed (the damage is in the COMBINATION)
    assert hi["best_single"] > 0.8


# 3. PROPERTY — curl and combination-damage move together across the sweep.
def test_property_curl_tracks_damage():
    rows = sweep_curl_vs_combination(n=40, k_cyclic=4, noise=0.05, seed=1)
    curls = [r["curl"] for r in rows]
    damage = [r["best_single"] - r["combined"] for r in rows]   # how much combining loses
    # monotone-ish: highest-curl row has the most damage; lowest-curl the least
    assert curls[-1] == max(curls)
    assert damage[-1] == max(damage)
    assert damage[0] == pytest.approx(min(damage), abs=1e-6)


# 4. EDGE
def test_edge_cases():
    recs, q = make_reward_scenario(n=10, k_cyclic=3, cyclic_weight=1.0, noise=0.0, seed=0)
    assert len(recs) == 10
    assert set(recs[0]["margins"]) == {"informative", "cyc0", "cyc1", "cyc2"}
