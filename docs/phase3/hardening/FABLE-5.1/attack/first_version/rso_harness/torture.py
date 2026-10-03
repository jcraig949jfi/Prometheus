"""G6 and G8. Observer, reset and restart torture; and closure of the world against policies that need no retention.

Every check compares whole trajectories: what the world delivered at each step and the organism's
native state after it. Scores are not enough. A positive that holds its bit robustly gives the same
answer whether or not an observer disturbed the world, so a score-only comparison passes a broken
observer; and a stored word does not even change its own state, so comparing the organism alone
passes it too. test_harness.py pins both cases.
"""
from .retain1 import BASELINES, World, score
from .stats import class_exclusion
from .verdict import BLOCKED, FAIL, PASS, Result

REQUIRED_BASELINES = ("CONSTANT", "CLOCK", "KEY_READER", "WORLD_PARKER")


def quiet_observer(log):
    """Records native state and touches nothing."""
    def observe(world, seed, t, org):
        log.append(org.native())
    return observe


def greedy_observer(log):
    """Fault: draws from the world's random stream while recording."""
    def observe(world, seed, t, org):
        log.append((org.native(), world.draw(seed)))
    return observe


def observer_equivalence(make, seeds, observer_factory, compare="native"):
    """Same seed with and without the observer. Deterministic class: the trajectories must be equal."""
    for seed in seeds:
        off = World().episode(make(), seed)
        on = World().episode(make(), seed, observer=observer_factory([]))
        same = (off["answer"] == on["answer"]) if compare == "score" else (off == on)
        if not same:
            return Result("G6.observer", FAIL, "the observer changes the run (seed %d)" % seed)
    return Result("G6.observer", PASS)


def reset_closure(make, seeds, **world):
    """After an episode, a blank-cue episode must not depend on what the earlier cue was."""
    for seed in seeds:
        seen = []
        for earlier in (0, 1):
            w, org = World(**world), make()
            w.episode(org, seed, force_bit=earlier)
            later = w.episode(org, seed + 1, cue=False)
            seen.append((later["answer"], later["trace"]))
        if seen[0] != seen[1]:
            return Result("G6.reset", FAIL, "state survives the reset (seed %d)" % seed)
    return Result("G6.reset", PASS)


def restart_equivalence(make, seeds, at=3):
    """Capture at mid-gap, restore into a fresh runtime, continue. It must match the uninterrupted run."""
    def restart(org):
        fresh = make()
        fresh.reset()
        fresh.restore(org.capture())
        return fresh

    for seed in seeds:
        whole = World().episode(make(), seed)
        cut = World().episode(make(), seed, interrupt={at: restart})
        if whole["answer"] != cut["answer"] or whole["trace"][at + 1:] != cut["trace"][at + 1:]:
            return Result("G6.restart", FAIL, "capture and restore lose state (seed %d)" % seed)
    return Result("G6.restart", PASS)


def demand_closure(seeds, baselines=None, alpha=1e-6, **world):
    """G8. No policy that needs no retention may beat the exact bound in this world."""
    baselines = BASELINES if baselines is None else baselines
    absent = [b for b in REQUIRED_BASELINES if b not in baselines]
    if absent:
        return Result("G8.demand", BLOCKED, "required baselines not run: %s" % ", ".join(absent))
    solved = [name for name, make in sorted(baselines.items())
              if class_exclusion(score(make, seeds, **world), len(seeds), 0.5, alpha) == "EXCLUDES"]
    if solved:
        return Result("G8.demand", FAIL, "the world is solved without retention by: %s" % ", ".join(solved))
    return Result("G8.demand", PASS)
