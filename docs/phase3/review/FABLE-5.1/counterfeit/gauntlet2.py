"""Strict gauntlet: the section-19 protocol of RSO v0.1 with its four open choices read strictly.

The first gauntlet (gauntlet.py) showed a selector and a library builder passing the protocol. A
reviewer then showed that the pass leaned on four choices the protocol leaves open, each read
permissively: the construction budget was truncated where naive and developed differ; "fresh family"
meant a new seed of a kind already met; nothing implemented the content resets; the sham could not
fail. This file reads each strictly and asks whether a plain library learner still passes.

Strict readings, fixed in PREREG_gauntlet2.md:
  COST        savings are acquisition cost: tasks consumed until an acceptable procedure exists, with
              no budget cut-off; and lifecycle cost against a naive organism working on the targets
              alone.
  FRESH       B, D and E are kinds never met in development, with distinct function classes; C is a
              fresh family of B's kind and also a narrower family inside B's class.
  CONTENT     the harness clears every declared content store at steps 2 and 5.
  SHAM        the sham removes as many library entries as the lesion, chosen among entries the
              target does not use; a random library of equal size and a wrong-history library are
              separate donors.
Arms are separate computations: the lesion removes only the entries the target uses; rescue and
V-donor material comes from a second individual with its own history.

World. Functions on the integers mod 17, built from ADD(c), MUL(a), SQR, CUB, INV. A kind is a
template; a family is a set of tasks of one kind with random constants; a task is 12 trials with
feedback. Development: families of four "parts" (depth 2, one constant). Targets: compositions of two
parts (depth 4, two constants) that no template of depth 3 or less covers.

Organisms (all designed):
  BUILDER     fixed constructor; a library of procedures that worked. Tries the library, then pairs
              of library items, then every template of depth 1 to 4 in an inherited order.
  SELECTOR    inherits every part and every pair of parts as a ready list; experience moves the
              used entry to the front. No constructor.
and six fire tests, each built to fail one conjunct:
  STATIC      BUILDER that never writes its library                       (SAVINGS)
  WASTEFUL    BUILDER whose development tests every candidate on 40 tasks (LIFECYCLE)
  HIDDEN      BUILDER with an undeclared second copy of its library       (NESTING)
  BADSHAM     BUILDER, but the "sham" removes the entries the target uses (NESTING)
  MATURATION  BUILDER whose library becomes an inherited list of every part after any experience
                                                                          (PROVENANCE)
  MEMORISER   stores the tasks it saw; in a world that leaks the target's tasks into development it
              shows savings unless content is reset                       (SAVINGS, via CONTENT)
  OFFHISTORY  BUILDER in a world whose D and E use parts absent from its history   (REPEAT)

    python gauntlet2.py --design     design seeds; prints; writes nothing
    python gauntlet2.py              registered seeds; writes RECEIPT_gauntlet2.json
"""
import hashlib
import itertools
import json
import pathlib
import platform
import statistics
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
P = 17
T = 12                      # trials per task
TAU = 4                     # a procedure passes a task if errors <= TAU
CONFIRM = 8                 # and is accepted for a family only if it passes this many tasks in a row
N_REP = 24                  # replicates per organism
N_TEST = 30                 # test tasks for the quality of a frozen U
GOOD_MAX = 3.5              # mean errors per task at or below this: GOOD
BAD_MIN = 6.0               # at or above this: BAD
HOLDS_AT = 22               # a relation HOLDS if true in at least this many of N_REP replicates
FAILS_AT = 12               # and FAILS if true in at most this many
PRIMS = ("ADD", "MUL", "SQR", "CUB", "INV")
PARAM = {"ADD": tuple(range(P)), "MUL": tuple(range(1, P))}
MAX_DEPTH = 4
MAX_PARAMS = 2
WASTE = 40
DESIGN_BASE = 37
REGISTERED_BASE = 2026100123


def khash(*ints):
    h = hashlib.blake2b(digest_size=8)
    for v in ints:
        h.update(int(v).to_bytes(8, "little"))
    return int.from_bytes(h.digest(), "little")


def shuffled(items, *key):
    items = list(items)
    for i in range(len(items) - 1, 0, -1):
        j = khash(*key, i) % (i + 1)
        items[i], items[j] = items[j], items[i]
    return items


# ---------------------------------------------------------------- templates

_TABLES = {}


def tables(template):
    """Every function a template can express, as tuples f[0..16], in the order of its constants."""
    got = _TABLES.get(template)
    if got is None:
        got = []
        for consts in itertools.product(*[PARAM[p] for p in template if p in PARAM]):
            vals = []
            for x in range(P):
                k, v = 0, x
                for prim in template:
                    if prim == "ADD":
                        v = (v + consts[k]) % P
                        k += 1
                    elif prim == "MUL":
                        v = (v * consts[k]) % P
                        k += 1
                    elif prim == "SQR":
                        v = (v * v) % P
                    elif prim == "CUB":
                        v = (v * v * v) % P
                    else:
                        v = pow(v, P - 2, P)
                vals.append(v)
            got.append(tuple(vals))
        _TABLES[template] = got
    return got


def klass(template):
    return frozenset(tables(template))


def n_params(template):
    return sum(1 for p in template if p in PARAM)


def enumeration(order):
    """All templates of depth 1 to MAX_DEPTH with at most MAX_PARAMS constants, in an inherited order."""
    out = []
    for depth in range(1, MAX_DEPTH + 1):
        for t in itertools.product(order, repeat=depth):
            if n_params(t) <= MAX_PARAMS:
                out.append(t)
    return out


ALL_PARTS = [(a, b) for a in ("ADD", "MUL") for b in ("SQR", "CUB", "INV")] + \
            [(b, a) for a in ("ADD", "MUL") for b in ("SQR", "CUB", "INV")]


def canonical_parts():
    """Parts with distinct function classes, none contained in another."""
    keep = []
    for t in ALL_PARTS:
        c = klass(t)
        if any(c <= klass(u) for u in keep):
            continue
        keep = [u for u in keep if not klass(u) < c] + [t]
    return keep


PARTS = canonical_parts()
SHALLOW = [klass(t) for t in enumeration(PRIMS) if len(t) <= 3]


def good_target(t, chosen):
    c = klass(t)
    if any(c <= s for s in SHALLOW):
        return False            # some template of depth 3 or less already covers it
    return not any(c <= klass(u) or klass(u) <= c for u in chosen)


def covering_pairs(target, entries):
    """Ordered pairs of library entries whose composition covers the target's function class."""
    c = klass(target)
    return [(a, b) for a in entries for b in entries
            if len(a) + len(b) <= MAX_DEPTH and n_params(a + b) <= MAX_PARAMS and c <= klass(a + b)]


DEPTH2 = [t for t in enumeration(PRIMS) if len(t) == 2]


# ---------------------------------------------------------------- world

def task(kind, seed, i, pin=None):
    """Task i of a family: the hidden function and the 12 stimuli. pin fixes the first constant."""
    tb = tables(kind)
    if pin is None:
        idx = khash(seed, i, 1) % len(tb)
    else:
        n2 = len(tb) // len(PARAM[[p for p in kind if p in PARAM][0]])
        idx = (pin % (len(tb) // n2)) * n2 + khash(seed, i, 1) % n2
    return tb[idx], [1 + khash(seed, i, 2, t) % 16 for t in range(T)]


def run_task(template, f, xs, stop_after=None):
    """Errors made by a fresh learner of this template on one task. Constants are fitted exactly."""
    alive = tables(template)
    errors = 0
    for x in xs:
        if (alive[0][x] if alive else 0) != f[x]:
            errors += 1
            if stop_after is not None and errors > stop_after:
                return errors
        alive = [t for t in alive if t[x] == f[x]]
    return errors


def passes(u, kind, seed, j):
    """Does a candidate pass CONFIRM tasks of the family in a row? Returns (accepted, tasks consumed).

    One task is not enough. A template that covers half of a kind's functions passes one task half
    the time, and a long search meets several such templates before the right one. The first task
    is task j; the confirmations are tasks no other candidate uses.
    """
    used = 0
    for c in range(CONFIRM):
        f, xs = task(kind, seed, j if c == 0 else 100000 + CONFIRM * j + c)
        used += 1
        errors = u.errors(f, xs, TAU) if isinstance(u, Lookup) else run_task(u, f, xs, TAU)
        if errors > TAU:
            return False, used
    return True, used


def quality(u, kind, seed, pin=None):
    """Mean errors per task of a frozen procedure on a fresh family."""
    if u is None:
        return float(T)
    total = 0
    for i in range(N_TEST):
        f, xs = task(kind, seed, 1000 + i, pin)
        total += u.errors(f, xs) if isinstance(u, Lookup) else run_task(u, f, xs)
    return total / N_TEST


class Lookup:
    """The MEMORISER's procedure: answer from stored tasks."""

    def __init__(self, memo):
        self.memo = list(memo)

    def errors(self, f, xs, stop_after=None):
        score = [0] * len(self.memo)            # examples of this task each stored task agrees with
        errors = 0
        for x in xs:
            best, guess = -1, 0
            for i, m in enumerate(self.memo):
                if score[i] > best and x in m:
                    best, guess = score[i], m[x]
            if guess != f[x]:
                errors += 1
                if stop_after is not None and errors > stop_after:
                    return errors
            for i, m in enumerate(self.memo):
                if x in m:
                    score[i] = score[i] + 1 if m[x] == f[x] else -1000
        return errors


# ---------------------------------------------------------------- organisms

class Builder:
    """A fixed constructor and a library that experience fills. Options make the fire-test variants."""

    def __init__(self, order, write=True, hidden=False, maturation=False, wasteful=False, memoriser=False):
        self.order = tuple(order)
        self.enum = enumeration(self.order)     # inherited; never written
        self.library = []                       # V, declared: procedures that worked, most recent first
        self.acquired = {}                      # which library entry each development family produced
        self.write = write
        self.hidden = [] if hidden else None    # an undeclared copy (fire test)
        self.maturation = maturation
        self.wasteful = wasteful
        self.memo = [] if memoriser else None   # declared CONTENT store (fire test)

    def clone(self):
        c = Builder.__new__(Builder)
        c.__dict__.update(self.__dict__)
        c.library = list(self.library)
        c.acquired = dict(self.acquired)
        c.hidden = None if self.hidden is None else list(self.hidden)
        c.memo = None if self.memo is None else [dict(m) for m in self.memo]
        return c

    def reset_content(self):
        if self.memo is not None:
            self.memo = []

    def candidates(self):
        lib = list(self.library)
        if self.hidden is not None:
            lib += [t for t in self.hidden if t not in lib]
        seen, out = set(), []
        pairs = (a + b for a in lib for b in lib if len(a) + len(b) <= MAX_DEPTH and n_params(a + b) <= MAX_PARAMS)
        for c in itertools.chain(lib, pairs, self.enum):
            if c not in seen:
                seen.add(c)
                out.append(c)
        return out

    def construct(self, kind, seed, limit=None, developing=False):
        """Find a procedure for a family. Returns (procedure or None, tasks consumed)."""
        cost = 0
        if self.memo is not None and self.memo:
            look = Lookup(self.memo)
            cost += CONFIRM
            if all(look.errors(*task(kind, seed, i), TAU) <= TAU for i in range(CONFIRM)):
                return look, cost
        for j, tmpl in enumerate(self.candidates()):
            if limit is not None and cost >= limit:
                return None, cost
            if self.memo is not None and developing:
                f, xs = task(kind, seed, j)
                self.memo.append({x: f[x] for x in xs})
            ok, used = passes(tmpl, kind, seed, j)
            cost += WASTE if (self.wasteful and developing) else used
            if ok:
                if self.write:
                    for store in (self.library, self.hidden):
                        if store is not None:
                            if tmpl in store:
                                store.remove(tmpl)
                            store.insert(0, tmpl)
                    if developing:
                        self.acquired[kind] = tmpl
                return tmpl, cost
        return None, cost + 1

    def develop(self, history):
        cost = 0
        for kind, seed in history:
            cost += self.construct(kind, seed, developing=True)[1]
        if self.maturation and history:
            self.library = list(PARTS)
            self.acquired = {k: k for k in PARTS}
        return cost

    def remove(self, kinds):
        """Lesion: remove from the declared library the entries acquired for these kinds."""
        for k in kinds:
            t = self.acquired.get(k)
            if t in self.library:
                self.library.remove(t)

    def insert(self, entries):
        for t in entries:
            if t is not None and t not in self.library:
                self.library.insert(0, t)


class Selector:
    """Every part and every pair of parts inherited as a ready list; experience reorders it."""

    def __init__(self, order):
        ready = list(PARTS) + [a + b for a in PARTS for b in PARTS]
        self.library = shuffled(ready, 77, *[PRIMS.index(p) for p in order])   # inherited order
        self.acquired = {}
        self.memo = None

    def clone(self):
        c = Selector.__new__(Selector)
        c.library = list(self.library)
        c.acquired = dict(self.acquired)
        c.memo = None
        return c

    def reset_content(self):
        pass

    def construct(self, kind, seed, limit=None, developing=False):
        cost = 0
        for j, tmpl in enumerate(list(self.library)):
            if limit is not None and cost >= limit:
                return None, cost
            ok, used = passes(tmpl, kind, seed, j)
            cost += used
            if ok:
                self.library.remove(tmpl)
                self.library.insert(0, tmpl)
                if developing:
                    self.acquired[kind] = tmpl
                return tmpl, cost
        return None, cost + 1

    def develop(self, history):
        return sum(self.construct(k, s, developing=True)[1] for k, s in history)

    def remove(self, kinds):
        for k in kinds:                         # a selector cannot lose an inherited entry; it loses its place
            t = self.acquired.get(k)
            if t in self.library:
                self.library.remove(t)
                self.library.append(t)

    def insert(self, entries):
        for t in entries:
            if t in self.library:
                self.library.remove(t)
                self.library.insert(0, t)


# ---------------------------------------------------------------- the strict protocol

def setup(base, r, off_history=False):
    """The world of one replicate.

    Power maps commute, so a target can have more than one decomposition into parts. A world is
    redrawn (salt 0, 1, 2, ...) until the labels mean what they say as statements about function
    classes: exactly one ordered pair of history parts covers B; no pair of the wrong-history parts
    covers B; no pair of the random library covers B.
    """
    order = shuffled(PRIMS, base, r, 1)
    for salt in range(200):
        parts = shuffled(PARTS, base, r, 2, salt)
        hist, rest = parts[:4], parts[4:]
        targets = []
        for a, b in shuffled([(a, b) for a in hist for b in hist if a != b], base, r, 3, salt):
            t = a + b
            if not targets and covering_pairs(t, hist) != [(a, b)]:
                continue
            if good_target(t, targets):
                targets.append(t)
            if len(targets) == 3:
                break
        if len(targets) < 3:
            continue
        wrong = None
        for drop in range(len(rest)):
            cand = rest[:drop] + rest[drop + 1:]
            if not covering_pairs(targets[0], cand):
                wrong = cand
                break
        if wrong is None:
            continue
        junk = []
        for t in shuffled(DEPTH2, base, r, 8, salt):
            unrelated = not any(klass(t) <= klass(h) or klass(h) <= klass(t) for h in hist)
            if unrelated and not covering_pairs(targets[0], junk + [t]):
                junk.append(t)
            if len(junk) == len(hist):
                break
        if len(junk) < len(hist):
            continue
        if off_history:                         # fire test: D and E are built from parts never developed
            extra = []
            for t in shuffled([a + b for a in wrong for b in wrong if a != b], base, r, 4, salt):
                if good_target(t, targets[:1] + extra):
                    extra.append(t)
                if len(extra) == 2:
                    break
            if len(extra) < 2:
                continue
            targets = targets[:1] + extra
        return {"order": order, "hist": hist, "wrong": wrong, "junk": junk, "targets": targets, "salt": salt}
    raise RuntimeError("no clean world found for replicate %d" % r)


def replicate(make, base, r, bad_sham=False, leak=False, off_history=False):
    """One replicate of the strict protocol. Returns the costs and qualities of every arm."""
    s = setup(base, r, off_history)
    order, hist, wrong = s["order"], s["hist"], s["wrong"]
    kb, kd, ke = s["targets"]
    used = (kb[:2], kb[2:])                                     # the two parts B is made of
    spare = [k for k in hist if k not in used]
    seed = lambda tag, n=0: khash(base, r, tag, n)
    fam = {k: seed(10, n) for n, k in enumerate((kb, kd, ke))}
    history = shuffled([(k, seed(20, n)) for n, k in enumerate(hist)], base, r, 5)
    if leak:
        history = history + [(kb, fam[kb])]                     # the target's own tasks leak into development
    history2 = shuffled([(k, seed(21, n)) for n, k in enumerate(hist)], base, r, 6)
    wrong_history = shuffled([(k, seed(22, n)) for n, k in enumerate(wrong)], base, r, 7)
    out = {}

    for name, k in (("B", kb), ("D", kd), ("E", ke)):           # naive: no development
        out["naive_" + name] = make(order).construct(k, fam[k])[1]

    org = make(order)                                           # step 1
    out["development"] = org.develop(history)
    kept = org.clone()                                          # the same individual, content NOT reset
    org.reset_content()                                         # step 2
    post_a = org.clone()
    u_b, out["dev_B"] = org.construct(kb, fam[kb])              # step 3; u_b is then frozen (step 4)
    out["dev_B_if_content_kept"] = kept.construct(kb, fam[kb])[1]
    org.reset_content()                                         # step 5
    out["q_C_same_kind"] = quality(u_b, kb, seed(30))           # step 6
    out["q_C_narrower"] = quality(u_b, kb, seed(31), pin=seed(32))
    for name, k in (("D", kd), ("E", ke)):                      # step 12, each from the post-A state
        out["dev_" + name] = post_a.clone().construct(k, fam[k])[1]

    les = post_a.clone()                                        # step 7
    les.remove(used)
    out["lesion_B"] = les.construct(kb, fam[kb])[1]
    les2 = post_a.clone()
    les2.remove(used)
    u_les = les2.construct(kb, fam[kb], limit=out["dev_B"])[0]  # what the lesioned line builds at the intact line's cost
    out["q_C_lesioned_line"] = quality(u_les, kb, seed(30))

    sham = post_a.clone()                                       # step 8
    sham.remove(used if bad_sham else spare)
    out["sham_B"] = sham.construct(kb, fam[kb])[1]

    donor = make(order)                                         # a second individual, its own history
    donor.develop(history2)
    donor.reset_content()
    resc = post_a.clone()                                       # step 9
    resc.remove(used)
    resc.insert([donor.acquired.get(k) for k in used])
    out["rescue_B"] = resc.construct(kb, fam[kb])[1]

    recipient = make(order)                                     # step 10: V donor into a naive recipient
    recipient.insert(reversed(donor.library))
    out["v_donor_B"] = recipient.construct(kb, fam[kb])[1]

    other = make(order)                                         # step 11: wrong history
    other.develop(wrong_history)
    other.reset_content()
    out["wrong_history_B"] = other.construct(kb, fam[kb])[1]
    rnd = make(order)                                           # a random library of equal size
    rnd.insert(s["junk"])
    out["random_library_B"] = rnd.construct(kb, fam[kb])[1]
    out["world_salt"] = s["salt"]

    out["lifecycle_developed"] = out["development"] + out["dev_B"] + out["dev_D"] + out["dev_E"]
    out["lifecycle_naive"] = out["naive_B"] + out["naive_D"] + out["naive_E"]
    out["one_target_developed"] = out["development"] + out["dev_B"]    # against naive_B: the same-compute arm
    return out


CONJUNCTS = ("SAVINGS", "LIFECYCLE", "U_TRANSFER", "NESTING", "PROVENANCE", "REPEAT")


def relations(o):
    """The six conjuncts for one replicate, each a boolean."""
    slack = 2 * o["dev_B"] + 4
    return {
        "SAVINGS": 4 * o["dev_B"] <= o["naive_B"],
        "LIFECYCLE": o["lifecycle_developed"] < o["lifecycle_naive"],
        "U_TRANSFER": (o["q_C_same_kind"] <= GOOD_MAX and o["q_C_narrower"] <= GOOD_MAX
                       and o["q_C_lesioned_line"] >= BAD_MIN),
        "NESTING": (2 * o["lesion_B"] >= o["naive_B"] and o["sham_B"] <= slack and o["rescue_B"] <= slack
                    and 4 * o["v_donor_B"] <= o["naive_B"]),
        "PROVENANCE": 2 * o["wrong_history_B"] >= o["naive_B"] and 2 * o["random_library_B"] >= o["naive_B"],
        "REPEAT": 4 * o["dev_D"] <= o["naive_D"] and 4 * o["dev_E"] <= o["naive_E"],
    }


def status(count):
    return "HOLDS" if count >= HOLDS_AT else "FAILS" if count <= FAILS_AT else "INDETERMINATE"


def run_cell(make, base, **world):
    reps = [replicate(make, base, r, **world) for r in range(N_REP)]
    rels = [relations(o) for o in reps]
    counts = {c: sum(1 for x in rels if x[c]) for c in CONJUNCTS}
    states = {c: status(counts[c]) for c in CONJUNCTS}
    if all(v == "HOLDS" for v in states.values()):
        verdict = "PASS"
    elif any(v == "FAILS" for v in states.values()):
        verdict = "FAIL"
    else:
        verdict = "INDETERMINATE"
    medians = {k: statistics.median(o[k] for o in reps) for k in reps[0]}
    kept = sum(1 for o in reps if 4 * o["dev_B_if_content_kept"] <= o["naive_B"])
    one = sum(1 for o in reps if o["one_target_developed"] < o["naive_B"])
    return {"verdict": verdict, "conjuncts": states, "counts": counts, "medians": medians,
            "savings_if_content_reset_skipped": kept, "cheaper_than_naive_on_one_target_alone": one,
            "failing": sorted(c for c in CONJUNCTS if states[c] == "FAILS"), "replicates": reps}


CELLS = [
    # name, factory, world options, expected verdict, conjuncts expected to FAIL
    ("BUILDER", lambda o: Builder(o), {}, "PASS", []),
    ("SELECTOR", lambda o: Selector(o), {}, "FAIL", ["SAVINGS"]),
    ("STATIC", lambda o: Builder(o, write=False), {}, "FAIL", ["SAVINGS"]),
    ("WASTEFUL", lambda o: Builder(o, wasteful=True), {}, "FAIL", ["LIFECYCLE"]),
    ("HIDDEN", lambda o: Builder(o, hidden=True), {}, "FAIL", ["NESTING"]),
    ("BADSHAM", lambda o: Builder(o), {"bad_sham": True}, "FAIL", ["NESTING"]),
    ("MATURATION", lambda o: Builder(o, maturation=True), {}, "FAIL", ["PROVENANCE"]),
    ("MEMORISER", lambda o: Builder(o, write=False, memoriser=True), {"leak": True}, "FAIL", ["SAVINGS"]),
    ("OFFHISTORY", lambda o: Builder(o), {"off_history": True}, "FAIL", ["REPEAT"]),
]


def main(argv):
    design = "--design" in argv
    base = DESIGN_BASE if design else REGISTERED_BASE
    only = [a for a in argv[1:] if not a.startswith("--")]
    print("parts with distinct function classes: %d; candidate templates: %d" % (len(PARTS), len(enumeration(PRIMS))))
    out, ok = {}, True
    for n, (name, make, world, want, must_fail) in enumerate(CELLS):
        if only and name not in only:
            continue
        cell = run_cell(make, base + 100 * (n + 1), **world)
        m = cell["medians"]
        hit = cell["verdict"] == want and all(c in cell["failing"] for c in must_fail)
        ok = ok and hit
        out[name] = cell
        print("%-11s %-13s %s" % (name, cell["verdict"], "as expected" if hit else "NOT AS EXPECTED (wanted %s %s)" % (want, must_fail)))
        print("    " + "  ".join("%s %s %d" % (c, cell["conjuncts"][c], cell["counts"][c]) for c in CONJUNCTS))
        print("    median tasks: naive B %s, developed B %s, lesion %s, sham %s, rescue %s, V donor %s, wrong history %s, random library %s"
              % (m["naive_B"], m["dev_B"], m["lesion_B"], m["sham_B"], m["rescue_B"], m["v_donor_B"],
                 m["wrong_history_B"], m["random_library_B"]))
        print("    median tasks: development %s; lifecycle developed %s against naive %s; D %s against %s; E %s against %s"
              % (m["development"], m["lifecycle_developed"], m["lifecycle_naive"], m["dev_D"], m["naive_D"],
                 m["dev_E"], m["naive_E"]))
        print("    median errors per task of frozen U: same kind %.2f, narrower family %.2f, lesioned line %.2f; "
              "savings if the content reset is skipped: %d of %d"
              % (m["q_C_same_kind"], m["q_C_narrower"], m["q_C_lesioned_line"],
                 cell["savings_if_content_reset_skipped"], N_REP))
        print("    development plus B cheaper than naive on B alone: %d of %d; worlds redrawn (median salt): %s"
              % (cell["cheaper_than_naive_on_one_target_alone"], N_REP, m["world_salt"]))
    if "MEMORISER" in out:
        teeth = out["MEMORISER"]["savings_if_content_reset_skipped"] >= HOLDS_AT
        ok = ok and teeth
        print("content reset has teeth (MEMORISER saves in %d of %d replicates when it is skipped): %s"
              % (out["MEMORISER"]["savings_if_content_reset_skipped"], N_REP, teeth))
    print("MATCHES PREREGISTERED EXPECTATION: %s" % ok)
    if design or only:
        return 0
    receipt = {
        "what": "strict gauntlet for the recursive-sagacity criterion of RSO v0.1 section 19",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "host": platform.node(), "python": sys.version.split()[0],
        "params": {"P": P, "T": T, "TAU": TAU, "CONFIRM": CONFIRM, "N_REP": N_REP, "N_TEST": N_TEST, "GOOD_MAX": GOOD_MAX,
                   "BAD_MIN": BAD_MIN, "HOLDS_AT": HOLDS_AT, "FAILS_AT": FAILS_AT, "MAX_DEPTH": MAX_DEPTH,
                   "MAX_PARAMS": MAX_PARAMS, "WASTE": WASTE, "seed_base": REGISTERED_BASE,
                   "canonical_parts": [list(p) for p in PARTS], "candidate_templates": len(enumeration(PRIMS))},
        "source_sha256_lf": hashlib.sha256(pathlib.Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "expected": {name: {"verdict": want, "must_fail": must_fail} for name, _, _, want, must_fail in CELLS},
        "matches_expectation": ok, "gate": "PASS" if ok else "FAILED", "cells": out,
    }
    (HERE / "RECEIPT_gauntlet2.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                                encoding="ascii", newline="\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
