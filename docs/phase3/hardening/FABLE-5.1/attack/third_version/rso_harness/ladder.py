"""EXPLORATORY. Two key worlds, and what a score above the exact nothing-carried bound certifies.

Not gates and not registered runs. World one was written after the first adversarial reader of
this package simulated what the first draft proposed and showed that the draft misread its own
certificate. World two is the proposal that replaced it. Two more readers attacked world two; the
organisms they used against it are here beside the author's. Both worlds are kept so that the
numbers the documents quote have a receipt.

Common ground. A family has 16 trials. A trial shows x, asks for y and then reveals it; each x
appears once. For a policy to which the family's map is a uniformly random permutation, the best
expected score is elimination: H_16 = 1 + 1/2 + ... + 1/16 = 3.3807 of 16. That is exact.

WORLD ONE: TWO NESTED BOUNDARIES. A life has E epochs of F families. Hidden per life: a random
permutation L. Hidden per epoch: s. Hidden per family: o.

    ROTATION   y = L[(x + s) mod 16] + o  mod 16      (the epoch's object turns the input)
    OFFSET     y = L[x] + s + o  mod 16                (the epoch's object adds to the family's)

A mean above the bound in the first family of a later epoch certifies that information acquired
in this life crossed the epoch boundary. It is a retention certificate. It does not certify that
anything was acquired at the level of the epoch: s and o together hold 8 bits, and an organism
that carries L and tries 256 inherited re-indexings (CACHE) has them by selection. CACHE has no
notion of an epoch and learns nothing after its first family.

WORLD TWO: AN UNSEEN PAIR. Hidden per life: three random permutations L_0..L_2 and three random
permutations P_0..P_2. A family is a pair (j, k), shown as a label; its map is y = P_k[L_j[x]].
The life shows eight of the nine pairs and then the ninth, (2, 2). That map is determined by three
of the tables shown:  (2,2) = (1,2) o inverse(1,1) o (2,1).  It is NOT determined by any two of
them: given any set of shown tables that does not link table 2 to move 2, the ninth map is
uniformly random.

What a score above the bound on the ninth pair says: information from at least three families,
shown separately, was combined. It says nothing about how. SCHEMA_CACHE below reads no label and
tries the 512 ways of combining three kept tables that it was born with; it scores far above the
bound. An organism restricted to two kept tables (TWO_TABLES), or to one table and 256 fixed
re-indexings (TABLE_CACHE), stays at the bound.

The control. The eight families shown are drawn from ANOTHER key under the same labels, and the
ninth from this life's key. The organism cannot tell the two arms apart before the ninth family.
In the control the ninth map is independent of everything shown, so the bound holds for every
organism; one that beats it there did not get its answer from this life (HIDER, in a harness that
reuses one key across lives).
"""
from math import log, sqrt

from .stats import khash

N = 16
H16 = sum(1.0 / k for k in range(1, N + 1))


# ---------------------------------------------------------------- world one

class Elim:
    """Carries nothing across any family boundary."""

    def begin_life(self):
        pass

    def begin_epoch(self):
        pass

    def begin_family(self):
        self.used = set()

    def predict(self, x):
        return min(o for o in range(N) if o not in self.used)

    def learn(self, x, y):
        self.used.add(y)

    def end_family(self):
        pass


class Cache(Elim):
    """One cached family table and a fixed, inherited re-indexer: 256 ways to turn the input and shift the output."""
    moves = [(r, c) for r in range(N) for c in range(N)]

    def begin_life(self):
        self.table = None

    def begin_family(self):
        self.used, self.seen = set(), {}
        self.cands = list(self.moves) if self.table else []

    def predict(self, x):
        if self.cands:
            r, c = self.cands[0]
            guess = (self.table[(x + r) % N] + c) % N
            if guess not in self.used:
                return guess
        return min(o for o in range(N) if o not in self.used)

    def learn(self, x, y):
        self.used.add(y)
        self.seen[x] = y
        self.cands = [(r, c) for r, c in self.cands if (self.table[(x + r) % N] + c) % N == y]

    def end_family(self):
        if self.table is None:
            self.table = [self.seen[x] for x in range(N)]


class Keeper(Cache):
    """The same cache with a smaller inherited re-indexer: it can shift the output and cannot turn the input."""
    moves = [(0, c) for c in range(N)]


class Forgetful(Keeper):
    """The same, told to drop its table at every epoch boundary."""

    def begin_epoch(self):
        self.table = None


ORGANISMS = {"ELIM": Elim, "CACHE": Cache, "KEEPER": Keeper, "FORGETFUL": Forgetful}


def run(make, lives, variant, epochs=3, families=4, base=7000):
    """Per life: mean correct of 16 in (the first family of the life, later families of the first epoch,
    first families of later epochs)."""
    rows = []
    for life in range(lives):
        org = make()
        key = sorted(range(N), key=lambda i: khash(base, life, 1, i))
        org.begin_life()
        first, within, across = [], [], []
        for e in range(epochs):
            s = khash(base, life, 2, e) % N
            org.begin_epoch()
            for f in range(families):
                o = khash(base, life, 3, e, f) % N
                org.begin_family()
                right = 0
                for x in sorted(range(N), key=lambda i: khash(base, life, 4, e, f, i)):
                    y = (key[(x + s) % N] + o) % N if variant == "ROTATION" else (key[x] + s + o) % N
                    right += org.predict(x) == y
                    org.learn(x, y)
                org.end_family()
                (first if (e, f) == (0, 0) else within if e == 0 else across if f == 0 else []).append(right)
        rows.append((sum(first) / len(first), sum(within) / len(within), sum(across) / len(across)))
    return rows


def certificate(per_life, alpha=1e-6):
    """CARRIED if the mean over lives exceeds the exact bound by a distribution-free margin, else NOT_SHOWN.

    The unit is the life. Scores lie in [0, 16], so by Hoeffding the mean of n lives exceeds its
    expectation by 16 * sqrt(ln(1/alpha) / (2n)) with probability at most alpha.
    """
    n = len(per_life)
    mean = sum(per_life) / n
    threshold = H16 + N * sqrt(log(1 / alpha) / (2 * n))
    return {"mean": mean, "threshold": threshold, "answer": "CARRIED" if mean >= threshold else "NOT_SHOWN"}


def survey(lives=300):
    """World one. Every organism in both variants: its certificate within an epoch and across epochs."""
    out = {}
    for variant in ("ROTATION", "OFFSET"):
        for name, make in sorted(ORGANISMS.items()):
            rows = run(make, lives, variant)
            out["%s/%s" % (variant, name)] = {
                "first_family_mean": sum(r[0] for r in rows) / lives,
                "across_families": certificate([r[1] for r in rows]),
                "across_epochs": certificate([r[2] for r in rows])}
    return out


# ---------------------------------------------------------------- world two

SHOWN = [(j, k) for j in range(3) for k in range(3) if (j, k) != (2, 2)]
UNSEEN = (2, 2)


def compose(c, b, a):
    """c o inverse(b) o a, for three tables."""
    inverse = [0] * N
    for x, y in enumerate(b):
        inverse[y] = x
    return [c[inverse[a[x]]] for x in range(N)]


class PairElim:
    """Carries nothing from one family to the next."""

    def begin_life(self):
        self.tables = {}

    def begin_family(self, label):
        self.label, self.used, self.seen = label, set(), {}
        self.cands = self.candidates(label)
        self.guess = self.next_guess()

    def candidates(self, label):
        return []

    def next_guess(self):
        self.cands = [g for g in self.cands if all(g[x] == y for x, y in self.seen.items())]
        return self.cands[0] if self.cands else None

    def predict(self, x):
        if self.guess is not None and self.guess[x] not in self.used:
            return self.guess[x]
        return min(o for o in range(N) if o not in self.used)

    def learn(self, x, y):
        self.used.add(y)
        self.seen[x] = y
        if self.guess is not None and self.guess[x] != y:
            self.guess = self.next_guess()

    def end_family(self):
        self.tables[self.label] = [self.seen[x] for x in range(N)]


class TableCache(PairElim):
    """Keeps every whole table it has seen, and tries the 256 inherited re-indexings of each on a new family."""

    def candidates(self, label):
        if label in self.tables:
            return [self.tables[label]]
        return [[(t[(x + r) % N] + c) % N for x in range(N)]
                for t in self.tables.values() for r in range(N) for c in range(N)]


class TwoTables(PairElim):
    """Keeps every table and tries every way of combining kept tables that uses at most two of them. No labels."""

    def candidates(self, label):
        tabs = list(self.tables.values())
        return [compose(c, b, a) for a in tabs for b in tabs for c in tabs if len({id(a), id(b), id(c)}) <= 2]


class SchemaCache(PairElim):
    """Keeps every table and tries all 512 inherited ways of combining three of them. It reads no label.

    Written by the first reader against this world. It combines three acquired tables, by blind
    enumeration and feedback: a selector over inherited procedures applied to memorised tables.
    """

    def candidates(self, label):
        tabs = list(self.tables.values())
        return [compose(c, b, a) for a in tabs for b in tabs for c in tabs]


class Composer(PairElim):
    """Keeps whole tables and, for a new pair, composes the three its label points to. The step is inherited."""

    def candidates(self, label):
        if label in self.tables:
            return [self.tables[label]]
        j, k = label
        for j2 in range(3):
            for k2 in range(3):
                a, b, c = self.tables.get((j, k2)), self.tables.get((j2, k2)), self.tables.get((j2, k))
                if a and b and c and j2 != j and k2 != k:
                    return [compose(c, b, a)]
        return []


class Hider(PairElim):
    """Keeps, from one life to the next, the table it saw under each label. Useful only if the harness reuses a key."""
    kept = {}

    def begin_life(self):
        self.tables = {}

    def candidates(self, label):
        return [Hider.kept[label]] if label in Hider.kept else []

    def end_family(self):
        PairElim.end_family(self)
        Hider.kept[self.label] = self.tables[self.label]


class Sandbagger(Hider):
    """The same, and it uses what it kept only after eight families have gone by."""
    kept = {}

    def candidates(self, label):
        return [Sandbagger.kept[label]] if label in Sandbagger.kept and len(self.tables) >= 8 else []

    def end_family(self):
        PairElim.end_family(self)
        Sandbagger.kept[self.label] = self.tables[self.label]


PAIR_ORGANISMS = {"ELIM": PairElim, "TABLE_CACHE": TableCache, "TWO_TABLES": TwoTables, "SCHEMA_CACHE": SchemaCache,
                  "COMPOSER": Composer}


def run_pairs(make, lives, control=False, reuse_key=False, base=9000):
    """Per life: correct of 16 on the ninth pair, after the eight shown.

    control: the eight shown families come from another key under the same labels.
    reuse_key: a planted fault. The harness uses one key for every life.
    """
    scores = []
    for cls in (Hider, Sandbagger):
        cls.kept = {}
    for life in range(lives):
        org = make()
        org.begin_life()
        key = 0 if reuse_key else life

        def tables(stream):
            return ([sorted(range(N), key=lambda i, j=j: khash(base, key, stream, 1, j, i)) for j in range(3)],
                    [sorted(range(N), key=lambda i, k=k: khash(base, key, stream, 2, k, i)) for k in range(3)])

        own, other = tables(0), tables(1)
        for n, (j, k) in enumerate(SHOWN + [UNSEEN]):
            bases, moves = other if (control and (j, k) != UNSEEN) else own
            org.begin_family((j, k))
            right = 0
            for x in sorted(range(N), key=lambda i: khash(base, life, 3, n, i)):
                y = moves[k][bases[j][x]]
                right += org.predict(x) == y
                org.learn(x, y)
            org.end_family()
        scores.append(right)
    return scores


def pair_answer(full, control):
    """What the two arms say together."""
    if control["answer"] == "CARRIED":
        return "NOT_FROM_THIS_LIFE"
    return "COMBINED" if full["answer"] == "CARRIED" else "NOT_SHOWN"


def survey_pairs(lives=300):
    """World two. Every organism on the ninth pair, in both arms; and the two hiders in a harness that reuses a key."""
    out = {}
    for name, make in sorted(PAIR_ORGANISMS.items()):
        full, control = certificate(run_pairs(make, lives)), certificate(run_pairs(make, lives, control=True))
        out[name] = {"ninth_pair": full, "control": control, "answer": pair_answer(full, control)}
    for name, make in (("HIDER", Hider), ("SANDBAGGER", Sandbagger)):
        full = certificate(run_pairs(make, lives, reuse_key=True))
        control = certificate(run_pairs(make, lives, control=True, reuse_key=True))
        out[name + ", one key reused by the harness"] = {"ninth_pair": full, "control": control,
                                                        "answer": pair_answer(full, control)}
    return out
