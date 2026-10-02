"""G6 and G8. Observer, reset and restart torture; and closure of the world against a list of baselines.

Every G6 check compares whole runs: what the world delivered at each step, the organism's native
state after the step and again after the observer, and the final state of both. Scores are not
enough. A positive that holds its bit robustly gives the same answer whether or not an observer
disturbed the world; a stored word does not even change its own state; a disturbance after the
last step shows only in the final state; and one that the organism repairs before its next step
shows only straight after the observer.

G8 runs a LIST of policies that carry nothing across the gap. It does not range over the class. The
statement that no such policy beats one half is a property of the generator and has to be derived.
The list catches the leaks it was written for. A family of small fitted tables catches a leak that
is a function of a few recent or early distractors, of the probe, or of the low bits of the clock.
With a long gap the table over all distractors cannot be fitted, and the gate then says INDETERMINATE.
A leak through a channel no table looks at escapes; meta.known_escapes pins one.
"""
from . import stats
from .retain1 import BASELINES, Recorder, World, score
from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, Result

REQUIRED_BASELINES = ("CONSTANT", "CLOCK", "KEY_READER", "WORLD_PARKER", "TABLE")
MARGIN = 0.1            # a baseline is at the bound if its rate is shown to lie within 1/2 +- MARGIN
DEMAND_ALPHA = 1e-6


# ---------------------------------------------------------------- observers

def quiet_observer(log):
    """Records native state and touches nothing."""
    def observe(world, seed, t, org):
        log.append(org.native())
    return observe


def own_stream_observer(log):
    """Clean twin of the greedy observer: it draws random numbers, from a stream of its own."""
    def observe(world, seed, t, org):
        log.append(stats.khash(seed, 777, len(log)))
    return observe


def greedy_observer(log):
    """Fault: draws from the world's random stream while recording."""
    def observe(world, seed, t, org):
        log.append((org.native(), world.draw(seed)))
    return observe


def late_observer(log):
    """Fault: draws from the world's stream only after the last distractor, where no later step shows it."""
    def observe(world, seed, t, org):
        if t >= world.gap:
            world.draw(seed)
    return observe


def writing_observer(log):
    """Fault: rewrites the organism after it has answered."""
    def observe(world, seed, t, org):
        if t == world.gap + 1 and hasattr(org, "w"):
            org.w = 1
    return observe


def counter_observer(log):
    """Fault: advances the world's episode counter."""
    def observe(world, seed, t, org):
        world.episodes += 5
    return observe


def marking_observer(log):
    """Fault: writes on the environment."""
    def observe(world, seed, t, org):
        world.mark = 1
    return observe


def healing_observer(log):
    """Fault: flips one cell of a lattice between steps; local majority repairs it before the next step."""
    def observe(world, seed, t, org):
        if hasattr(org, "cells") and t < world.gap:
            org.cells[(t + 5) % org.N] ^= 1
    return observe


def later_episodes_observer(log):
    """Fault: draws from the world's stream in every episode of a world but its first."""
    def observe(world, seed, t, org):
        if world.episodes > 0:
            world.draw(seed)
    return observe


def hidden_observer(log):
    """Fault the observer gate does not catch: writes a field of the organism that native() does not report."""
    def observe(world, seed, t, org):
        org.touched = getattr(org, "touched", 0) + 1
    return observe


def rare_observer(checked):
    """Fault the observer gate does not catch: it disturbs the world only on seeds outside those checked."""
    def factory(log):
        def observe(world, seed, t, org):
            if seed not in checked:
                world.draw(seed)
        return observe
    return factory


def observer_equivalence(make, seeds, observer_factory, compare="run"):
    """One world, every seed in turn, with and without the observer. Deterministic class: the runs must be equal."""
    if not seeds:
        return Result("G6.observer", BLOCKED, "no seeds: nothing was checked")

    def run(observer):
        w = World()
        return [w.episode(make(), seed, observer=observer) for seed in seeds]

    off, on = run(None), run(observer_factory([]))
    for seed, a, b in zip(seeds, off, on):
        same = (a["answer"] == b["answer"]) if compare == "score" else (a == b)
        if not same:
            return Result("G6.observer", FAIL, "the observer changes the run (seed %d)" % seed)
    return Result("G6.observer", PASS)


# ---------------------------------------------------------------- reset and restart

def reset_closure(make, seeds, **world):
    """An episode after a reset must equal the same episode on a runtime that has never run.

    Three later episodes are tried (no cue, cue 0, cue 1) after each of three earlier ones (cue 0, cue
    1, no cue). Compared: the answer, the trajectory, the organism's final state and the mark.
    """
    if not seeds:
        return Result("G6.reset", BLOCKED, "no seeds: nothing was checked")

    def episode(w, org, seed, cue):
        r = w.episode(org, seed, cue=cue is not None, force_bit=cue)
        return r["answer"], r["trace"], r["final"][0], r["final"][1]

    for seed in seeds:
        for cue in (None, 0, 1):
            fresh = episode(World(**dict(world, skip_reset=False)), make(), seed + 1, cue)
            for earlier in (0, 1, None):
                w, org = World(**world), make()
                episode(w, org, seed, earlier)
                if episode(w, org, seed + 1, cue) != fresh:
                    return Result("G6.reset", FAIL, "state survives the reset (seed %d, earlier cue %s)" % (seed, earlier))
    return Result("G6.reset", PASS)


def restart_equivalence(make, seeds):
    """Capture after every step, restore into a runtime that has been used, continue. It must match the uncut run.

    The runtime restored into has just run an episode with the opposite cue, so a restore that merges
    with what is there, or keeps a stale value, shows. A cut after the last step shows in the final state.
    """
    if not seeds:
        return Result("G6.restart", BLOCKED, "no seeds: nothing was checked")
    for seed in seeds:
        whole = World().episode(make(), seed)

        def restart(org):
            used = make()
            World().episode(used, seed, force_bit=1 - whole["bit"])
            used.restore(org.capture())
            return used

        for at in range(len(whole["trace"])):
            cut = World().episode(make(), seed, interrupt={at: restart})
            if (whole["answer"], whole["trace"][at + 1:], whole["final"]) != (cut["answer"], cut["trace"][at + 1:],
                                                                             cut["final"]):
                return Result("G6.restart", FAIL, "capture and restore do not carry the state (seed %d, step %d)"
                              % (seed, at))
    return Result("G6.restart", PASS)


# ---------------------------------------------------------------- demand closure

def contexts(seen):
    """Small views of what the world showed after the cue. Each is fitted as a table of its own."""
    d = tuple(v for kind, v, _, _ in seen if kind == "DISTRACT")
    probe = [(v, clock, mark) for kind, v, clock, mark in seen if kind == "PROBE"][0]
    views = {"PROBE": (probe[0], probe[2]), "CLOCK": (probe[1] & 7,), "ALL": d}
    for k in (1, 2, 3):
        views["LAST%d" % k], views["FIRST%d" % k] = d[-k:], d[:k]
    return views


def table_scores(seeds, train_seeds, **world):
    """For each view: the score of the best function of that view, fitted on other seeds.

    A view some of whose test contexts were never seen in training is not scored (None): it cannot be
    fitted with this much data, and the gate says so and does not count it as closed.
    """
    def record(which):
        w, rows = World(**world), []
        for s in which:
            org = Recorder()
            bit = w.episode(org, s)["bit"]
            rows.append((contexts(org.seen), bit))
        return rows

    train, test, out = record(train_seeds), record(seeds), {}
    for view in sorted(train[0][0]):
        counts = {}
        for views, bit in train:
            counts.setdefault(views[view], [0, 0])[bit] += 1
        if any(views[view] not in counts for views, _ in test):
            out[view] = None
            continue
        out[view] = sum(1 for views, bit in test if (1 if counts[views[view]][1] > counts[views[view]][0] else 0) == bit)
    return out


def demand_closure(seeds, train_seeds, baselines=None, alpha=DEMAND_ALPHA, margin=MARGIN, **world):
    """G8. Every baseline on the list must be SHOWN to sit at one half, within the margin.

    PASS needs an equivalence result for every baseline. FAIL needs a baseline shown to differ from
    one half, above or below: a policy that is reliably wrong has the information too. Too few
    episodes give neither, and the verdict is INDETERMINATE.
    """
    gate = "G8.demand"
    baselines = dict(BASELINES, TABLE=None) if baselines is None else baselines
    absent = [b for b in REQUIRED_BASELINES if b not in baselines]
    if absent:
        return Result(gate, BLOCKED, "required baselines not run: %s" % ", ".join(absent))
    if not seeds or set(seeds) & set(train_seeds):
        return Result(gate, BLOCKED, "no seeds, or the fitted tables are scored on seeds they were fitted on")
    n, scores, where = len(seeds), {}, {}
    for name, make in sorted(baselines.items()):
        if name == "TABLE":
            for view, k in table_scores(seeds, train_seeds, **world).items():
                scores["TABLE_" + view] = k
        else:
            scores[name] = score(make, seeds, **world)
    for name, k in scores.items():
        where[name] = "NOT_FITTED" if k is None else stats.equivalence(k, n, 0.5, margin, alpha)
    solved = ["%s (%d of %d)" % (b, scores[b], n) for b in sorted(where) if where[b] == "OUTSIDE"]
    if solved:
        return Result(gate, FAIL, "the cue is available without retention to: %s" % ", ".join(solved), scores)
    open_ = [b for b in sorted(where) if where[b] == "UNDECIDED"]
    unfitted = [b for b in sorted(where) if where[b] == "NOT_FITTED"]
    if open_ or unfitted:
        why = []
        if open_:
            why.append("%d episodes cannot show these within %.2f of one half: %s" % (n, margin, ", ".join(open_)))
        if unfitted:
            why.append("too little data to fit: %s" % ", ".join(unfitted))
        return Result(gate, INDETERMINATE, "; ".join(why), scores)
    return Result(gate, PASS, "", scores)
