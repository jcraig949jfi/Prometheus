"""W0 world RETAIN-1 and its isomer panel: one bit held across a gap, in four unlike toy physics.

The world. An episode shows a cue bit, then `gap` distractor bits, then a probe. The organism's
action at the probe is its answer. The cue is uniform and independent of everything after it, so a
policy that carries nothing across the gap scores exactly 1/2. That is the exact rate every ruler
here is scored against. It is a property of the generator, argued here and not tested into
existence: the faults below break it on purpose.

The runtime contract. A physics supplies reset, step, capture, restore and native. It does not
supply registers, modules or a split into fast and persistent state. The four positives hold the
bit in a stored word, in an attractor, in a packet in flight, and in a spatial pattern. Each has a
matched impostor: the same kind of machine, holding something other than the cue.
"""
from .stats import khash


class Obs:
    __slots__ = ("kind", "value", "clock", "mark")

    def __init__(self, kind, value, clock, mark):
        self.kind, self.value, self.clock, self.mark = kind, value, clock, mark


class World:
    """RETAIN-1. Every keyword but `gap` is a fault planted on purpose."""

    def __init__(self, gap=6, leak_clock=None, leak_key=None, cue_from_distractors=None, writable_mark=False,
                 keep_mark=False, skip_reset=False):
        self.gap = gap
        self.leak_clock = leak_clock            # "parity", "bit1" or "bit3": the cue follows a readable counter
        self.leak_key = leak_key                # "plain", "inverted" or "partial": the probe carries the answer
        self.cue_from_distractors = cue_from_distractors    # "last2": xor of the last two; "all": parity of all
        self.writable_mark = writable_mark      # the environment keeps what the organism writes
        self.keep_mark = keep_mark              # and does not clear it between episodes
        self.skip_reset = skip_reset            # the harness forgets to reset the organism
        self.episodes = 0
        self.draws = 0
        self.mark = None

    def draw(self, seed):
        """Next bit of the world's random stream for this episode."""
        self.draws += 1
        return khash(seed, self.draws) & 1

    def episode(self, org, seed, observer=None, cue=True, force_bit=None, interrupt=None):
        """One episode. Returns the cue bit, the answer, the trajectory and the final state.

        The trajectory holds, for every step: what the world delivered, the organism's native state
        after the step, and its native state again after the observer (if any) has been called. The
        final state is the organism's native state and the world's mark, draw count and episode count.
        """
        self.draws = 0
        if not self.keep_mark:
            self.mark = None
        if not self.skip_reset:
            org.reset()
        planned = [self.draw(seed) for _ in range(self.gap)] if self.cue_from_distractors else None
        if force_bit is not None:
            bit = force_bit
        elif self.cue_from_distractors == "last2":
            bit = planned[-1] ^ planned[-2]
        elif self.cue_from_distractors == "all":
            bit = sum(planned) & 1
        elif self.leak_clock == "parity":
            bit = self.episodes & 1
        elif self.leak_clock in ("bit1", "bit3"):
            bit = (self.episodes >> int(self.leak_clock[3])) & 1
        else:
            bit = self.draw(seed)
        shown = {None: None, "plain": bit, "inverted": 1 - bit,
                 "partial": bit if khash(seed, 4242) % 5 < 2 else None}[self.leak_key]
        kinds = [("CUE", bit) if cue else ("BLANK", None)] + [("DISTRACT", None)] * self.gap + [("PROBE", shown)]
        answer, trace = None, []
        for t, (kind, value) in enumerate(kinds):
            if kind == "DISTRACT":
                value = planned[t - 1] if planned is not None else self.draw(seed)
            obs = Obs(kind, value, self.episodes if self.leak_clock else t, self.mark)
            action = org.step(obs)
            if isinstance(action, tuple) and action[0] == "WRITE" and self.writable_mark:
                self.mark = action[1]
            if kind == "PROBE":
                answer = action
            after_step = org.native()
            if observer is not None:
                observer(self, seed, t, org)
            trace.append((obs.kind, obs.value, obs.clock, obs.mark, after_step, org.native()))
            if interrupt and t in interrupt:
                org = interrupt[t](org) or org
        self.episodes += 1
        return {"bit": bit, "answer": answer, "trace": tuple(trace),
                "final": (org.native(), self.mark, self.draws, self.episodes)}


# ---------------------------------------------------------------- four positives

class Register:
    """A stored word."""
    physics = "REGISTER"

    def __init__(self):
        self.w = None

    def reset(self):
        self.w = None

    def step(self, obs):
        if obs.kind == "CUE":
            self.w = obs.value
        if obs.kind == "PROBE":
            return self.w or 0

    def capture(self):
        return (self.w,)

    def restore(self, state):
        self.w = state[0]

    def native(self):
        return (self.w,)


class Attractor:
    """One saturating unit that reinforces its own sign. The bit is which basin it sits in."""
    physics = "ATTRACTOR"

    def __init__(self):
        self.a = 0

    def reset(self):
        self.a = 0

    def step(self, obs):
        if obs.kind == "CUE":
            self.a += 4 if obs.value else -4
        elif obs.kind == "DISTRACT":
            self.a += 1 if obs.value else -1
        if self.a > 0:
            self.a = min(8, self.a + 2)
        elif self.a < 0:
            self.a = max(-8, self.a - 2)
        if obs.kind == "PROBE":
            return 1 if self.a > 0 else 0

    def capture(self):
        return (self.a,)

    def restore(self, state):
        self.a = state[0]

    def native(self):
        return (self.a,)


class PacketRing:
    """Three forwarding nodes and a packet in flight. No node stores anything; the bit is in the queue."""
    physics = "PACKET"

    def __init__(self):
        self.queue = []

    def reset(self):
        self.queue = []

    def step(self, obs):
        self.queue = [[(pos + 1) % 3, payload] for pos, payload in self.queue]
        if obs.kind == "CUE":
            self.queue.append([0, obs.value])
        if obs.kind == "PROBE":
            return self.queue[0][1] if self.queue else 0

    def capture(self):
        return tuple(tuple(p) for p in self.queue)

    def restore(self, state):
        self.queue = [list(p) for p in state]

    def native(self):
        return tuple(tuple(p) for p in self.queue)


class Lattice:
    """A ring of eight cells under local majority. The bit is the domain; single flips are repaired."""
    physics = "LATTICE"
    N = 8

    def __init__(self):
        self.cells, self.t = [0] * self.N, 0

    def reset(self):
        self.cells, self.t = [0] * self.N, 0

    def perturb(self, obs):
        if obs.kind == "CUE":
            self.cells = [obs.value] * self.N
        elif obs.kind == "DISTRACT" and obs.value:
            self.cells[self.t % self.N] ^= 1

    def step(self, obs):
        self.perturb(obs)
        c, n = self.cells, self.N
        self.cells = [1 if c[i - 1] + c[i] + c[(i + 1) % n] >= 2 else 0 for i in range(n)]
        self.t += 1
        if obs.kind == "PROBE":
            return 1 if 2 * sum(self.cells) > n else 0

    def capture(self):
        return (tuple(self.cells), self.t)

    def restore(self, state):
        self.cells, self.t = list(state[0]), state[1]

    def native(self):
        return (tuple(self.cells), self.t)


# ---------------------------------------------------------------- four matched impostors
# Each answers a different function of the distractors, so that their scores are not one series.

class RegisterImpostor(Register):
    """Has the word, stores the last distractor in it."""

    def step(self, obs):
        if obs.kind == "DISTRACT":
            self.w = obs.value
        if obs.kind == "PROBE":
            return self.w or 0


class AttractorImpostor(Attractor):
    """One basin only: it climbs to the positive side whatever the cue was."""

    def step(self, obs):
        self.a = min(8, self.a + 2)
        if obs.kind == "PROBE":
            return 1


class PacketImpostor(PacketRing):
    """The packet circulates, and the first hop after launch overwrites its payload with the local input."""

    def step(self, obs):
        self.queue = [[(pos + 1) % 3, payload] for pos, payload in self.queue]
        if obs.kind == "CUE":
            self.queue.append([0, None])
        elif obs.kind == "DISTRACT":
            self.queue = [[pos, obs.value if payload is None else payload] for pos, payload in self.queue]
        if obs.kind == "PROBE":
            return (self.queue[0][1] or 0) if self.queue else 0


class LatticeImpostor(Lattice):
    """The same ring, and every input repaints the whole domain with the majority of the last three inputs."""

    def __init__(self):
        self.cells, self.t, self.last = [0] * self.N, 0, ()

    def reset(self):
        self.cells, self.t, self.last = [0] * self.N, 0, ()

    def perturb(self, obs):
        if obs.kind in ("CUE", "DISTRACT"):
            self.last = (self.last + (obs.value,))[-3:]
            self.cells = [1 if 2 * sum(self.last) > len(self.last) else 0] * self.N

    def capture(self):
        return (tuple(self.cells), self.t, self.last)

    def restore(self, state):
        self.cells, self.t, self.last = list(state[0]), state[1], state[2]

    def native(self):
        return (tuple(self.cells), self.t, self.last)


PANEL = {
    "REGISTER": (Register, RegisterImpostor),
    "ATTRACTOR": (Attractor, AttractorImpostor),
    "PACKET": (PacketRing, PacketImpostor),
    "LATTICE": (Lattice, LatticeImpostor),
}


# ---------------------------------------------------------------- known answers near the threshold

class FadingRegister(Register):
    """A weak positive: a stored word that is lost when the first three distractors are all ones.

    Lost in one episode of eight and then right by luck half the time: exact rate 15/16.
    """

    def __init__(self):
        self.w, self.seen = None, 0

    def reset(self):
        self.w, self.seen = None, 0

    def step(self, obs):
        if obs.kind == "CUE":
            self.w = obs.value
        elif obs.kind == "DISTRACT":
            self.seen = (self.seen + 1) if (obs.value and self.seen >= 0) else -1
            if self.seen == 3:
                self.w = None
        if obs.kind == "PROBE":
            return self.w or 0

    def capture(self):
        return (self.w, self.seen)

    def restore(self, state):
        self.w, self.seen = state

    def native(self):
        return (self.w, self.seen)


class Inverter(Register):
    """Holds the cue perfectly and answers its complement. It carries the bit: it is no impostor."""

    def step(self, obs):
        if obs.kind == "CUE":
            self.w = obs.value
        if obs.kind == "PROBE":
            return 1 - (self.w or 0)


def scripted(k):
    """A fixture, not an organism: holds the cue, answers it in its first k episodes and its complement after."""
    count = [0]

    class Scripted(Register):
        def step(self, obs):
            if obs.kind == "CUE":
                self.w = obs.value
            if obs.kind == "PROBE":
                count[0] += 1
                return (self.w or 0) if count[0] <= k else 1 - (self.w or 0)

    return Scripted


class LateBinder(Register):
    """A fixture for the swap ruler. It holds the cue in a field the swap does not move, and writes it into the
    word only at its fifth step. A swap of the word before that step moves nothing; after it, the cue."""

    def __init__(self):
        self.w, self.held, self.t = None, None, 0

    def reset(self):
        self.w, self.held, self.t = None, None, 0

    def step(self, obs):
        if obs.kind == "CUE":
            self.held = obs.value
        if self.t == 4:
            self.w = self.held
        self.t += 1
        if obs.kind == "PROBE":
            return self.w or 0

    def capture(self):
        return (self.w, self.held, self.t)

    def restore(self, state):
        self.w, self.held, self.t = state

    def native(self):
        return (self.w, self.held, self.t)


def weak_carrier(period=5):
    """Carries the cue in one episode of `period` and answers 0 otherwise. Too weak to exclude the class."""
    count = [0]

    class WeakCarrier(Register):
        def step(self, obs):
            if obs.kind == "CUE":
                self.w = obs.value
                count[0] += 1
            if obs.kind == "PROBE":
                return (self.w or 0) if count[0] % period == 0 else 0

    return WeakCarrier


# ---------------------------------------------------------------- policies that carry nothing

class Constant(Register):
    """Always answers 0."""

    def step(self, obs):
        if obs.kind == "PROBE":
            return 0


class ClockReader(Register):
    """Answers the parity of whatever clock the world shows."""

    def step(self, obs):
        if obs.kind == "PROBE":
            return obs.clock & 1


class KeyReader(Register):
    """Answers whatever the probe itself carries."""

    def step(self, obs):
        if obs.kind == "PROBE":
            return obs.value or 0


class WorldParker(Register):
    """Writes the cue on the environment and reads it back. Holds nothing itself."""

    def step(self, obs):
        if obs.kind == "CUE":
            return ("WRITE", obs.value)
        if obs.kind == "PROBE":
            return obs.mark or 0


class ClockBit3Reader(Register):
    """Answers the fourth bit of the clock. On no baseline list; shows a known escape is real."""

    def step(self, obs):
        if obs.kind == "PROBE":
            return (obs.clock >> 3) & 1


class Recorder(Register):
    """Records everything the world shows after the cue, and nothing of the cue. Feeds the fitted tables."""

    def __init__(self):
        self.w, self.seen = None, []

    def reset(self):
        self.w, self.seen = None, []

    def step(self, obs):
        if obs.kind in ("DISTRACT", "PROBE"):
            self.seen.append((obs.kind, obs.value, obs.clock, obs.mark))
        if obs.kind == "PROBE":
            return 0


BASELINES = {"CONSTANT": Constant, "CLOCK": ClockReader, "KEY_READER": KeyReader, "WORLD_PARKER": WorldParker,
             "LAST_DISTRACTOR": RegisterImpostor}


# ---------------------------------------------------------------- runtimes broken on purpose

class LeakyResetRegister(Register):
    """Fault: reset leaves the word in place."""

    def reset(self):
        pass


class SneakyRegister(Register):
    """Fault: reset clears the word and keeps a carry that native() hides; it shows only when a cue arrives."""

    def __init__(self):
        self.w, self.carry, self.cue = None, 0, 0

    def reset(self):
        self.w = None

    def step(self, obs):
        if obs.kind == "CUE":
            self.w, self.cue = obs.value ^ self.carry, obs.value
        if obs.kind == "PROBE":
            if self.w is not None:
                self.carry = self.cue
            return self.w or 0


class BlankCarry(Register):
    """Fault: an episode with no cue leaves a hidden flag that flips the next cue."""

    def __init__(self):
        self.w, self.flag = None, 0

    def reset(self):
        self.w = None

    def step(self, obs):
        if obs.kind == "BLANK":
            self.flag = 1
        if obs.kind == "CUE":
            self.w, self.flag = obs.value ^ self.flag, 0
        if obs.kind == "PROBE":
            return self.w or 0


class SleeperRegister(Register):
    """Fault the reset gate does not catch: a hidden carry that is used two episodes later, not one."""

    def __init__(self):
        self.w, self.old, self.older = None, 0, 0

    def reset(self):
        self.w = None

    def step(self, obs):
        if obs.kind in ("CUE", "BLANK"):
            use, self.older, self.old = self.older, self.old, (obs.value or 0)
            self.w = None if obs.kind == "BLANK" else obs.value ^ use
        if obs.kind == "PROBE":
            return self.w or 0


class EveryThirdReset(Register):
    """Fault the reset gate does not catch: reset is sound twice and leaks on every third call."""

    def __init__(self):
        self.w, self.calls = None, 0

    def reset(self):
        self.calls += 1
        if self.calls % 3:
            self.w = None


class HiddenCounter(Register):
    """Fault the restart gate does not catch: a count of episodes that capture omits, native() hides, and that
    turns the answer round from the second episode on. Within one episode nothing shows."""

    def __init__(self):
        self.w, self.episodes = None, 0

    def reset(self):
        self.w = None
        self.episodes += 1

    def step(self, obs):
        if obs.kind == "CUE":
            self.w = obs.value
        if obs.kind == "PROBE":
            return (self.w or 0) if self.episodes < 2 else 1 - (self.w or 0)


class LatticeKeepsClock(Lattice):
    """Fault: reset clears the cells and keeps the step counter."""

    def reset(self):
        self.cells = [0] * self.N


def faulty_from(k, base, fault):
    """A fixture: instances of `base` until the k-th is made, instances of `fault` from then on.

    The gates make a fixed number of instances per seed, so this plants a fault that the first seed
    does not show.
    """
    count = [0]

    def make():
        count[0] += 1
        return (fault if count[0] >= k else base)()

    return make


class PacketRingBadCapture(PacketRing):
    """Fault: the captured state omits the packets in flight."""

    def capture(self):
        return ()


class AttractorStaleRestore(Attractor):
    """Fault: restore does nothing."""

    def restore(self, state):
        pass


class PacketAppendRestore(PacketRing):
    """Fault: restore adds to whatever is already there."""

    def restore(self, state):
        self.queue = self.queue + [list(p) for p in state]


class RegisterKeepIfSet(Register):
    """Fault: restore fills an empty word and leaves a stale one in place."""

    def restore(self, state):
        if self.w is None:
            self.w = state[0]


class LatticeLateBadCapture(Lattice):
    """Fault: capture drops the step counter, late in the gap only."""

    def capture(self):
        return (tuple(self.cells), self.t if self.t <= 5 else 0)


class LatticeEndBadCapture(Lattice):
    """Fault: capture drops the step counter after the last step only."""

    def capture(self):
        return (tuple(self.cells), self.t if self.t <= self.N - 1 else 0)


def score(make, seeds, **world):
    """Correct answers of a fresh organism per seed, in one world."""
    w = World(**world)
    return sum(1 for s in seeds if (lambda r: r["answer"] == r["bit"])(w.episode(make(), s)))
