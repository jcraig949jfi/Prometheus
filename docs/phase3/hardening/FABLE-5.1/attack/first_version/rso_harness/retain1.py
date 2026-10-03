"""W0 world RETAIN-1 and its isomer panel: one bit held across a gap, in four unlike toy physics.

The world. An episode shows a cue bit, then `gap` distractor bits, then a probe. The organism's
action at the probe is its answer. The cue is uniform and independent of everything after it, so a
policy that carries nothing across the gap scores exactly 1/2. That is the exact bound every ruler
here is scored against.

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
    """RETAIN-1. The three keyword faults make a world that is solved without retention."""

    def __init__(self, gap=6, leak_clock=False, leak_key=False, writable_mark=False, skip_reset=False):
        self.gap = gap
        self.leak_clock = leak_clock            # fault: the bit follows a counter the organism can read
        self.leak_key = leak_key                # fault: the probe carries the answer
        self.writable_mark = writable_mark      # fault: the environment keeps what the organism writes
        self.skip_reset = skip_reset            # fault: the harness forgets to reset the organism
        self.episodes = 0
        self.draws = 0
        self.mark = None

    def draw(self, seed):
        """Next bit of the world's random stream for this episode."""
        self.draws += 1
        return khash(seed, self.draws) & 1

    def episode(self, org, seed, observer=None, cue=True, force_bit=None, interrupt=None):
        """One episode. Returns the cue bit, the answer, and the trajectory.

        The trajectory holds, for every step, what the world delivered and the organism's native state
        after it. Both halves matter: an observer can disturb the world in a way this organism ignores.
        """
        self.draws, self.mark = 0, None
        if not self.skip_reset:
            org.reset()
        if force_bit is not None:
            bit = force_bit
        elif self.leak_clock:
            bit = self.episodes & 1
        else:
            bit = self.draw(seed)
        kinds = [("CUE", bit) if cue else ("BLANK", None)]
        kinds += [("DISTRACT", None)] * self.gap
        kinds += [("PROBE", bit if self.leak_key else None)]
        answer, trace = None, []
        for t, (kind, value) in enumerate(kinds):
            if kind == "DISTRACT":
                value = self.draw(seed)
            obs = Obs(kind, value, self.episodes if self.leak_clock else t, self.mark)
            action = org.step(obs)
            if isinstance(action, tuple) and action[0] == "WRITE" and self.writable_mark:
                self.mark = action[1]
            if kind == "PROBE":
                answer = action
            trace.append((obs.kind, obs.value, obs.clock, obs.mark, org.native()))
            if observer is not None:
                observer(self, seed, t, org)
            if interrupt and t in interrupt:
                org = interrupt[t](org) or org
        self.episodes += 1
        return {"bit": bit, "answer": answer, "trace": tuple(trace)}


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
    """The packet circulates, and every hop overwrites its payload with the local input."""

    def step(self, obs):
        self.queue = [[(pos + 1) % 3, payload] for pos, payload in self.queue]
        if obs.kind == "CUE":
            self.queue.append([0, obs.value])
        elif obs.kind == "DISTRACT":
            self.queue = [[pos, obs.value] for pos, _ in self.queue]
        if obs.kind == "PROBE":
            return self.queue[0][1] if self.queue else 0


class LatticeImpostor(Lattice):
    """The same ring with no repair: every input repaints the whole domain."""

    def perturb(self, obs):
        if obs.kind in ("CUE", "DISTRACT"):
            self.cells = [obs.value] * self.N


PANEL = {
    "REGISTER": (Register, RegisterImpostor),
    "ATTRACTOR": (Attractor, AttractorImpostor),
    "PACKET": (PacketRing, PacketImpostor),
    "LATTICE": (Lattice, LatticeImpostor),
}


# ---------------------------------------------------------------- policies that need no retention

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


BASELINES = {"CONSTANT": Constant, "CLOCK": ClockReader, "KEY_READER": KeyReader, "WORLD_PARKER": WorldParker,
             "LAST_DISTRACTOR": RegisterImpostor}


# ---------------------------------------------------------------- runtimes broken on purpose

class LeakyResetRegister(Register):
    """Fault: reset leaves the word in place."""

    def reset(self):
        pass


class PacketRingBadCapture(PacketRing):
    """Fault: the captured state omits the packets in flight."""

    def capture(self):
        return ()


class AttractorStaleRestore(Attractor):
    """Fault: restore does not overwrite the unit."""

    def restore(self, state):
        pass


def score(make, seeds, **world):
    """Correct answers of a fresh organism per seed, in one world."""
    w = World(**world)
    return sum(1 for s in seeds if (lambda r: r["answer"] == r["bit"])(w.episode(make(), s)))
