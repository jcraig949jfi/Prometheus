"""Probe of the order-4 key world as specified in document 3, section 9 (my own implementation; the author has not built it).

World: life -> E epochs -> F families -> 16 trials. L uniform permutation per life, rotation s per epoch, offset o per
family. y = L[(x + s) mod 16] + o mod 16; each x once per family, random order; y revealed after the answer.
"""
import random
from fractions import Fraction

N, E, F = 16, 3, 4
H16 = float(sum(Fraction(1, k) for k in range(1, N + 1)))


class Elim:
    """Carries nothing across any family boundary."""
    name = "ELIM (carries nothing)"

    def begin_life(self): pass
    def begin_epoch(self): pass
    def begin_family(self): self.used = set()
    def predict(self, x): return min(o for o in range(N) if o not in self.used)
    def learn(self, x, y): self.used.add(y)
    def end_family(self): pass


class Cache(Elim):
    """Task cargo and a fixed inherited re-indexer. It keeps ONE solved family (a 16-entry answer table) for the rest
    of the life and tries the 256 inherited re-indexings (rotate input, shift output) of that table. It has no notion
    of epochs and never learns anything after its first family."""
    name = "CACHE (one cached family table + fixed 256-way re-indexer)"

    def begin_life(self): self.table = None

    def begin_family(self):
        self.used, self.seen = set(), {}
        self.cands = [(r, c) for r in range(N) for c in range(N)] if self.table else []

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


class Acq3(Cache):
    """Built for order 3 as document 3 describes it: learns the epoch's map, solves for the offset only, and drops the
    map at the epoch boundary."""
    name = "ACQ3 (offset-only solver, drops its table at the epoch boundary)"

    def begin_epoch(self): self.table = None

    def begin_family(self):
        self.used, self.seen = set(), {}
        self.cands = [(0, c) for c in range(N)] if self.table else []


class Acq3Keep(Acq3):
    """The same offset-only solver that simply does not forget at a boundary it was never told about."""
    name = "ACQ3-KEEP (offset-only solver, never drops its table)"

    def begin_epoch(self): pass


def run(org, lives, epoch_object, rng):
    first_first = later_first_epoch = first_later = later_later = 0
    n_ff = n_lf = n_fl = n_ll = 0
    for _ in range(lives):
        L = list(range(N))
        rng.shuffle(L)
        org.begin_life()
        for e in range(E):
            s = rng.randrange(N)
            org.begin_epoch()
            for f in range(F):
                o = rng.randrange(N)
                org.begin_family()
                xs = list(range(N))
                rng.shuffle(xs)
                score = 0
                for x in xs:
                    if epoch_object == "rotation":
                        y = (L[(x + s) % N] + o) % N
                    else:                       # the epoch object is a second output offset
                        y = (L[x] + s + o) % N
                    score += org.predict(x) == y
                    org.learn(x, y)
                org.end_family()
                if e == 0 and f == 0: first_first += score; n_ff += 1
                elif e == 0: later_first_epoch += score; n_lf += 1
                elif f == 0: first_later += score; n_fl += 1
                else: later_later += score; n_ll += 1
    return first_first / n_ff, later_first_epoch / n_lf, first_later / n_fl, later_later / n_ll


print("H_16 = %.4f (the exact nothing-carried bound; document 3 says 3.38)" % H16)
for epoch_object in ("rotation", "second offset"):
    print("\nepoch-level hidden object: %s   (E=%d epochs, F=%d families, 3000 lives each)" % (epoch_object, E, F))
    print("  %-66s %9s %14s %16s" % ("organism", "1st fam", "ORDER-3 cert", "ORDER-4 cert"))
    print("  %-66s %9s %14s %16s" % ("", "of life", "later fam, e1", "1st fam, later e"))
    for org in (Elim(), Acq3(), Acq3Keep(), Cache()):
        a, b, c, d = run(org, 3000, epoch_object, random.Random(20261002))
        print("  %-66s %9.2f %14.2f %16.2f" % (org.name, a, b, c))
