"""Known-answer distinctness calibration (frozen in pan/tests/negspace_prereg.json). Every pair's label is known by
construction, not by any evaluator:

  EQUIVALENT   the same mechanism under a representation change (list / deque / ring / full history / renaming);
               identical behavior on every input, all code exercised by the suite
  DISTINCT     superficially similar code that behaves differently under an intervention in the suite (one-token
               delay change, persistence without use, reset on zero, environmental storage under a world wipe,
               a horizon cap visible only on the long stream)
  CHEAT        a known mechanism dressed as new: renaming, executed no-op machinery, helper methods, dead methods;
               a correct evaluator must NOT call these DISTINCT
  UNRESOLVED   the pair differs only on inputs or times OUTSIDE the suite (t >= 1000, x >= 10, step 10**6, a wipe
               after t > 50), in code the suite never executes; the honest answer is UNKNOWN

Scoring (frozen): EQUIVALENT pairs need verdict EQUIVALENT; DISTINCT pairs need DISTINCT; CHEAT pairs need anything
but DISTINCT; UNRESOLVED pairs need UNKNOWN.
"""
import textwrap


def _s(code):
    return textwrap.dedent(code).strip() + "\n"


M = {}
M["list"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.buf = [0, 0, 0]
        def step(self, x):
            self.buf.append(x)
            return self.buf.pop(0)
''')
M["deque"] = _s('''
    from collections import deque

    class Mechanism:
        def __init__(self, world):
            self.q = deque([0] * 3)
        def step(self, x):
            self.q.append(x)
            return self.q.popleft()
''')
M["ring"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.ring = [0, 0, 0]
            self.i = 0
        def step(self, x):
            out = self.ring[self.i]
            self.ring[self.i] = x
            self.i = (self.i + 1) % 3
            return out
''')
M["history"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.seen = []
        def step(self, x):
            self.seen.append(x)
            t = len(self.seen) - 1
            return self.seen[t - 3] if t >= 3 else 0
''')
M["history_neg"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.seen = []
        def step(self, x):
            self.seen.append(x)
            return self.seen[-4] if len(self.seen) > 3 else 0
''')
M["list_renamed"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.memory = [0, 0, 0]
        def step(self, value):
            self.memory.append(value)
            return self.memory.pop(0)
''')
M["world"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.world = world
            self.t = 0
        def step(self, x):
            self.world[self.t] = x
            y = self.world.get(self.t - 3, 0)
            self.t += 1
            return y
''')
# failure classes (each violates the contract under some intervention in the suite)
M["off_by_one"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.buf = [0, 0]
        def step(self, x):
            self.buf.append(x)
            return self.buf.pop(0)
''')
M["off_by_one_ring"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.ring = [0, 0]
            self.i = 0
        def step(self, x):
            out = self.ring[self.i]
            self.ring[self.i] = x
            self.i = (self.i + 1) % 2
            return out
''')
M["no_use"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.buf = [0, 0, 0]
        def step(self, x):
            self.buf.append(x)
            self.buf.pop(0)
            return x
''')
M["no_use_deque"] = _s('''
    from collections import deque

    class Mechanism:
        def __init__(self, world):
            self.hist = deque(maxlen=8)
        def step(self, x):
            self.hist.append(x)
            return x
''')
M["reset_zero"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.buf = [0, 0, 0]
        def step(self, x):
            if x == 0:
                self.buf = [0, 0, 0]
            self.buf.append(x)
            return self.buf.pop(0)
''')
M["reset_zero_deque"] = _s('''
    from collections import deque

    class Mechanism:
        def __init__(self, world):
            self.q = deque([0] * 3)
        def step(self, x):
            if x == 0:
                self.q = deque([0] * 3)
            self.q.append(x)
            return self.q.popleft()
''')
M["cap100"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.seen = []
        def step(self, x):
            if len(self.seen) < 100:
                self.seen.append(x)
            t = len(self.seen) - 1
            return self.seen[t - 3] if t >= 3 else 0
''')
# cheats (known mechanisms dressed as new)
M["cheat_list"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.store = [0, 0, 0]
            self.counter = 0
            self.trace = []
        def step(self, item):
            self.counter += 1
            self.trace = self.trace[-5:] + [item]
            self.store.append(item)
            return self.store.pop(0)
''')
M["cheat_deque"] = _s('''
    from collections import deque

    class Mechanism:
        def __init__(self, world):
            self.lane = deque([0] * 3)
            self.shadow = deque(maxlen=10)
        def step(self, x):
            z = (x * 1) + 0
            self.shadow.append(z)
            self.lane.append(z)
            return self.lane.popleft()
''')
M["cheat_ring"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.cells = [0, 0, 0]
            self.cursor = 0
        def _advance(self):
            self.cursor = (self.cursor + 1) % len(self.cells)
        def step(self, signal):
            emitted = self.cells[self.cursor]
            self.cells[self.cursor] = signal
            self._advance()
            return emitted
''')
M["cheat_off_by_one"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.pipe = [0, 0]
            self.energy = 1.0
        def step(self, x):
            self.energy = self.energy * 0.99 + 0.01
            self.pipe.append(x)
            return self.pipe.pop(0)
''')
M["cheat_history_dead"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.seen = []
        def unused_diagnostics(self):
            return sum(self.seen) / max(1, len(self.seen))
        def step(self, x):
            self.seen.append(x)
            t = len(self.seen) - 1
            return self.seen[t - 3] if t >= 3 else 0
''')
M["cheat_world"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.world = world
            self.t = 0
        def step(self, x):
            self.world["_meta"] = self.t
            self.world[self.t] = x
            y = self.world.get(self.t - 3, 0)
            self.t += 1
            return y
''')
# unresolved (differ only outside the suite, in code the suite never executes)
M["history_cap1000"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.seen = []
        def step(self, x):
            if len(self.seen) < 1000:
                self.seen.append(x)
            else:
                return 0
            t = len(self.seen) - 1
            return self.seen[t - 3] if t >= 3 else 0
''')
M["list_alpha"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.buf = [0, 0, 0]
        def step(self, x):
            if x >= 10:
                return x
            self.buf.append(x)
            return self.buf.pop(0)
''')
M["deque_wrap"] = _s('''
    from collections import deque

    class Mechanism:
        def __init__(self, world):
            self.q = deque([0] * 3)
            self.n = 0
        def step(self, x):
            self.n += 1
            if self.n == 10 ** 6:
                self.q = deque([0] * 3)
            self.q.append(x)
            return self.q.popleft()
''')
M["world_late_wipe"] = _s('''
    class Mechanism:
        def __init__(self, world):
            self.world = world
            self.t = 0
        def step(self, x):
            if not self.world and self.t > 50:
                self.t += 1
                return -1
            self.world[self.t] = x
            y = self.world.get(self.t - 3, 0)
            self.t += 1
            return y
''')

PAIRS = [
    # (pair_id, category, a, b)
    ("E1", "EQUIVALENT", "list", "deque"),
    ("E2", "EQUIVALENT", "list", "ring"),
    ("E3", "EQUIVALENT", "list", "history"),
    ("E4", "EQUIVALENT", "deque", "ring"),
    ("E5", "EQUIVALENT", "list", "list_renamed"),
    ("E6", "EQUIVALENT", "off_by_one", "off_by_one_ring"),
    ("E7", "EQUIVALENT", "no_use", "no_use_deque"),
    ("E8", "EQUIVALENT", "history", "history_neg"),
    ("D1", "DISTINCT", "list", "off_by_one"),
    ("D2", "DISTINCT", "list", "no_use"),
    ("D3", "DISTINCT", "list", "reset_zero"),
    ("D4", "DISTINCT", "list", "world"),
    ("D5", "DISTINCT", "history", "cap100"),
    ("D6", "DISTINCT", "ring", "off_by_one_ring"),
    ("D7", "DISTINCT", "no_use", "off_by_one"),
    ("D8", "DISTINCT", "deque", "reset_zero_deque"),
    ("C1", "CHEAT", "list", "cheat_list"),
    ("C2", "CHEAT", "deque", "cheat_deque"),
    ("C3", "CHEAT", "ring", "cheat_ring"),
    ("C4", "CHEAT", "off_by_one", "cheat_off_by_one"),
    ("C5", "CHEAT", "history", "cheat_history_dead"),
    ("C6", "CHEAT", "world", "cheat_world"),
    ("U1", "UNRESOLVED", "history", "history_cap1000"),
    ("U2", "UNRESOLVED", "list", "list_alpha"),
    ("U3", "UNRESOLVED", "deque", "deque_wrap"),
    ("U4", "UNRESOLVED", "world", "world_late_wipe"),
]

# which mechanisms satisfy the contract under the suite (checked by a control, not assumed)
CONTRACT_OK = {"list", "deque", "ring", "history", "history_neg", "list_renamed", "cheat_list", "cheat_deque",
               "cheat_ring", "cheat_history_dead", "history_cap1000", "list_alpha", "deque_wrap",
               "world", "cheat_world", "world_late_wipe", "cap100"}
# the known failure classes (the negative-space library for the A-D experiment): one reference per class
FAILURE_CLASSES = {"F-delay-off-by-one": "off_by_one", "F-persistence-without-use": "no_use",
                   "F-reset-on-zero": "reset_zero", "F-environmental-storage-not-wipe-robust": "world",
                   "F-horizon-cap": "cap100"}
FAILURE_TEXT = {  # what arm B is told (descriptions only; never code)
    "F-delay-off-by-one": "Recalling the wrong lag (two steps back instead of three) fails the contract.",
    "F-persistence-without-use": "Storing history but returning the current input: the history persists but is never used.",
    "F-reset-on-zero": "Clearing the memory whenever the input is 0 loses information the contract needs.",
    "F-environmental-storage-not-wipe-robust": "Keeping the history only in the shared world dict: it satisfies the task, but a world wipe erases it.",
    "F-horizon-cap": "Recording only the first 100 steps: it satisfies short tasks, but fails after step 100.",
}
GIVEN_FAILURES = ("F-delay-off-by-one", "F-persistence-without-use", "F-reset-on-zero")      # library for arms B, C
WITHHELD_FAILURES = ("F-environmental-storage-not-wipe-robust", "F-horizon-cap")           # held back: rediscovery is measured
KNOWN_SUPPORTED = {"S-internal-buffer": "list"}                                              # positive geometry


def correct(category, verdict):
    if category == "EQUIVALENT":
        return verdict == "EQUIVALENT"
    if category == "DISTINCT":
        return verdict == "DISTINCT"
    if category == "CHEAT":
        return verdict != "DISTINCT"
    if category == "UNRESOLVED":
        return verdict == "UNKNOWN"
    raise ValueError(category)
