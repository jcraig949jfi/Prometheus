"""G6 and G8. Observer, reset and restart torture; and closure of the world against a list of baselines.

Every G6 check compares whole runs: what the world delivered at each step, the organism's native
state after it, and the final state of both. Scores are not enough. A positive that holds its bit
robustly gives the same answer whether or not an observer disturbed the world; a stored word does
not even change its own state; and a disturbance after the last step shows only in the final state.

G8 runs a LIST of policies that carry nothing across the gap. It does not range over the class. The
statement that no such policy beats one half is a property of the generator and has to be derived.
The list catches the leaks it was written for, and a fitted table catches any leak that is a
function of what the world shows after the cue. Anything else escapes; meta.known_escapes pins one.
"""
from . import stats
from .retain1 import BASELINES, Recorder, World, score
from .verdict import BLOCKED, FAIL, INDETERMINATE, PASS, Result

REQUIRED_BASELINES = ("CONSTANT", "CLOCK", "KEY_READER", "WORLD_PARKER", "TABLE")
MARGIN = 0.1            # a baseline is at the bound if its rate is shown to lie within 1/2 +- MARGIN


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


def rare_observer(checked):
    """Fault the observer gate does not catch: it disturbs the world only on seeds outside those checked."""
    def factory(log):
        def observe(world, seed, t, org):
            if seed not in checked:
                world.draw(seed)
        return observe
    return factory


def observer_equivalence(make, seeds, observer_factory, compare="run"):
    """Same seed with and without the observer. Deterministic class: the whole runs must be equal."""
    for seed in seeds:
        off = World().episode(make(), seed)
        on = World().episode(make(), seed, observer=observer_factory([]))
        same = (off["answer"] == on["answer"]) if compare == "score" else (off == on)
        if not same:
            return Result("G6.observer", FAIL, "the observer changes the run (seed %d)" % seed)
    return Result("G6.observer", PASS)


# ---------------------------------------------------------------- reset and restart

def reset_closure(make, seeds, **world):
    """An episode after a reset must equal the same episode on a runtime that has never run.

    Three later episodes are tried (no cue, cue 0, cue 1) after each of two earlier cues. Compared:
    the answer, the trajectory, the organism's final state and the mark on the environment.
    """
    def later(w, org, seed, cue):
        r = w.episode(org, seed + 1, cue=cue is not None, force_bit=cue)
        return r["answer"], r["trace"], r["final"][0], r["final"][1]

    for seed in seeds:
        for cue in (None, 0, 1):
            fresh = later(World(**dict(world, skip_reset=False)), make(), seed, cue)
            for earlier in (0, 1):
                w, org = World(**world), make()
                w.episode(org, seed, force_bit=earlier)
                if later(w, org, seed, cue) != fresh:
                    return Result("G6.reset", FAIL, "state survives the reset (seed %d, earlier cue %d)" % (seed, earlier))
    return Result("G6.reset", PASS)


def restart_equivalence(make, seeds):
    """Capture at every step, restore into a runtime that has been used, continue. It must match the uncut run.

    The runtime restored into has just run an episode with the opposite cue, so a restore that merges
    with what is there, or keeps a stale value, shows.
    """
    for seed in seeds:
        whole = World().episode(make(), seed)

        def restart(org):
            used = make()
            World().episode(used, seed, force_bit=1 - whole["bit"])
            used.restore(org.capture())
            return used

        for at in range(len(whole["trace"]) - 1):
            cut = World().episode(make(), seed, interrupt={at: restart})
            if (whole["answer"], whole["trace"][at + 1:], whole["final"]) != (cut["answer"], cut["trace"][at + 1:],
                                                                             cut["final"]):
                return Result("G6.restart", FAIL, "capture and restore do not carry the state (seed %d, step %d)"
                              % (seed, at))
    return Result("G6.restart", PASS)


# ---------------------------------------------------------------- demand closure

def table_score(seeds, train_seeds, **world):
    """Score of the best function of what the world shows after the cue, fitted on other seeds."""
    def run(w, seed):
        org = Recorder()
        bit = w.episode(org, seed)["bit"]
        return tuple(org.seen), bit

    counts, w = {}, World(**world)
    for s in train_seeds:
        seen, bit = run(w, s)
        counts.setdefault(seen, [0, 0])[bit] += 1
    w, right = World(**world), 0
    for s in seeds:
        seen, bit = run(w, s)
        c = counts.get(seen, [1, 0])
        right += (1 if c[1] > c[0] else 0) == bit
    return right


def demand_closure(seeds, train_seeds, baselines=None, alpha=1e-6, margin=MARGIN, **world):
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
    if set(seeds) & set(train_seeds):
        return Result(gate, BLOCKED, "the fitted table is scored on seeds it was fitted on")
    n, scores, where = len(seeds), {}, {}
    for name, make in sorted(baselines.items()):
        scores[name] = table_score(seeds, train_seeds, **world) if name == "TABLE" else score(make, seeds, **world)
        where[name] = stats.equivalence(scores[name], n, 0.5, margin, alpha)
    solved = ["%s (%d of %d)" % (b, scores[b], n) for b in sorted(where) if where[b] == "OUTSIDE"]
    if solved:
        return Result(gate, FAIL, "the cue is available without retention to: %s" % ", ".join(solved), scores)
    open_ = [b for b in sorted(where) if where[b] == "UNDECIDED"]
    if open_:
        return Result(gate, INDETERMINATE, "%d episodes cannot show these within %.2f of one half: %s"
                      % (n, margin, ", ".join(open_)), scores)
    return Result(gate, PASS, "", scores)
