"""Independent implementation of 'composition on an unseen pair' (document 3, section 9), from the prose.

Not copied from ladder.py. Own RNG (random.Random), own organisms.
World: per life three random permutations of 16 symbols (tables L_j) and three more (moves P_k).
A family is a pair (j,k) shown as a label; its map is x -> P_k[L_j[x]]. A trial shows x, asks y, reveals y;
each x once, random order. The life shows eight of nine pairs and then the ninth.
"""
import math
import random
import sys
from itertools import product

N = 16
H16 = sum(1.0 / k for k in range(1, N + 1))


def threshold(n, alpha=1e-6):
    return H16 + N * math.sqrt(math.log(1 / alpha) / (2 * n))


def inv(t):
    out = [0] * N
    for x, y in enumerate(t):
        out[y] = x
    return out


# ----------------------------------------------------------------------------- organisms

class Elim:
    """Carries nothing between families. Guesses the smallest unused symbol."""
    name = "ELIM"

    def begin_life(self, inherited=None):
        self.inherited = inherited
        self.tables = {}
        self.order = []

    def begin_family(self, label):
        self.label = label
        self.used = set()
        self.seen = {}
        self.plan = self.recall(label)

    def recall(self, label):
        return None

    def replan(self):
        return None

    def predict(self, x):
        if self.plan is not None:
            g = self.plan[x]
            if g is not None and g not in self.used:
                return g
        for o in range(N):
            if o not in self.used:
                return o

    def learn(self, x, y):
        self.used.add(y)
        self.seen[x] = y
        if self.plan is not None and self.plan[x] != y:
            self.plan = self.replan()

    def end_family(self):
        t = [self.seen[x] for x in range(N)]
        self.tables[self.label] = t
        self.order.append(t)


class CandCache(Elim):
    """Keeps every whole table seen; on a new family tries a list of candidate tables, selected by feedback only."""

    def candidates(self, label):
        return []

    def recall(self, label):
        self.cands = self.candidates(label)
        return self.cands[0] if self.cands else None

    def replan(self):
        seen = self.seen
        self.cands = [g for g in self.cands if all(g[x] == y for x, y in seen.items())]
        return self.cands[0] if self.cands else None

    def learn(self, x, y):
        self.used.add(y)
        self.seen[x] = y
        if self.plan is not None and self.plan[x] != y:
            # incremental filter on the newest pair is enough: survivors already agree with older pairs
            self.cands = [g for g in self.cands if g[x] == y]
            self.plan = self.replan()


class CacheRot(CandCache):
    name = "TABLE_CACHE rot/offset (256 per table)"

    def candidates(self, label):
        return [[(t[(x + r) % N] + c) % N for x in range(N)] for t in self.order for r in range(N) for c in range(N)]


class CacheXor(CandCache):
    name = "TABLE_CACHE xor/xor (256 per table)"

    def candidates(self, label):
        return [[t[x ^ r] ^ c for x in range(N)] for t in self.order for r in range(N) for c in range(N)]


class CacheAffine(Elim):
    """Every stored table under x -> a*x + r and y -> b*y + c (a, b odd): 16384 inherited re-indexings per table.
    Candidates are evaluated on demand; selection is by feedback only."""
    name = "TABLE_CACHE affine/affine (16384 per table)"
    odd = [1, 3, 5, 7, 9, 11, 13, 15]

    def recall(self, label):
        self.cands = [(ti, a, r, b, c) for ti in range(len(self.order)) for a in self.odd for r in range(N)
                      for b in self.odd for c in range(N)]
        return True if self.cands else None

    def value(self, cand, x):
        ti, a, r, b, c = cand
        return (b * self.order[ti][(a * x + r) % N] + c) % N

    def predict(self, x):
        if self.plan is not None and self.cands:
            g = self.value(self.cands[0], x)
            if g not in self.used:
                return g
        for o in range(N):
            if o not in self.used:
                return o

    def learn(self, x, y):
        self.used.add(y)
        self.seen[x] = y
        if self.plan is not None and self.cands:
            order, out = self.order, []
            for cand in self.cands:
                ti, a, r, b, c = cand
                if (b * order[ti][(a * x + r) % N] + c) % N == y:
                    out.append(cand)
            self.cands = out


class SameRow(CandCache):
    name = "guess the last table of the same row (2,1)"

    def candidates(self, label):
        return [self.order[-1]] if self.order else []


class SameCol(CandCache):
    name = "guess the tables that share the move (0,2),(1,2)"

    def candidates(self, label):
        return [t for lab, t in self.tables.items() if lab[1] == label[1]]


class PairCompose(CandCache):
    name = "all two-table combinations a.b, a.b^-1, a^-1.b (no labels)"

    def candidates(self, label):
        out = []
        ts = self.order
        invs = [inv(t) for t in ts]
        for i, a in enumerate(ts):
            for j, b in enumerate(ts):
                if i == j:
                    continue
                out.append([a[b[x]] for x in range(N)])
                out.append([a[invs[j][x]] for x in range(N)])
                out.append([invs[i][b[x]] for x in range(N)])
        return out


class TripleBrute(CandCache):
    """A table cache whose inherited re-indexer is 'a . b^-1 . c over every triple of stored tables'.
    No labels read, no notion of table or move. 8*7*7 = 392 inherited alternatives at most, selected by feedback."""
    name = "TABLE_CACHE with 392 inherited recombinations a.b^-1.c (no labels)"

    def candidates(self, label):
        ts = self.order
        invs = [inv(t) for t in ts]
        out = []
        n = len(ts)
        for i in range(n):
            for j in range(n):
                if j == i:
                    continue
                for k in range(n):
                    if k == j:
                        continue
                    a, bi, c = ts[i], invs[j], ts[k]
                    out.append([a[bi[c[x]]] for x in range(N)])
        return out


class Composer(Elim):
    """Label-based: for (j,k) use (j2,k) . (j2,k2)^-1 . (j,k2)."""
    name = "COMPOSER (labels; three tables)"

    def recall(self, label):
        j, k = label
        for j2 in range(3):
            for k2 in range(3):
                if j2 == j or k2 == k:
                    continue
                a, b, c = self.tables.get((j, k2)), self.tables.get((j2, k2)), self.tables.get((j2, k))
                if a and b and c:
                    bi = inv(b)
                    return [c[bi[a[x]]] for x in range(N)]
        return None


class Hardwired22(Elim):
    """One inherited formula for one label: (1,2) . (1,1)^-1 . (2,1) when the label is (2,2). Nothing else."""
    name = "one hard-wired formula for label (2,2)"

    def recall(self, label):
        if label != (2, 2):
            return None
        a, b, c = self.tables.get((2, 1)), self.tables.get((1, 1)), self.tables.get((1, 2))
        if a and b and c:
            bi = inv(b)
            return [c[bi[a[x]]] for x in range(N)]
        return None


class OneTableOneRelabel(Elim):
    """Memory: the previous family's table and the output relabelling seen three families earlier. No labels.
    A cache of ONE table with ONE re-indexing, the re-indexing acquired in this life (44 bits), not inherited."""
    name = "one cached table + one ACQUIRED relabelling (period-3 habit, no labels)"

    def begin_life(self, inherited=None):
        Elim.begin_life(self, inherited)
        self.relabels = []

    def recall(self, label):
        n = len(self.order)                      # index of the family that is starting
        if n >= 4:
            q = self.relabels[n - 4]             # the relabelling that led from family n-4 to family n-3
            prev = self.order[-1]
            return [q[prev[x]] for x in range(N)]
        return None

    def end_family(self):
        t = [self.seen[x] for x in range(N)]
        if self.order:
            pi = inv(self.order[-1])
            self.relabels.append([t[pi[y]] for y in range(N)])     # q with t = q . prev
        self.tables[self.label] = t
        self.order.append(t)


class PartialComposer(Composer):
    """Composes, and keeps only m entries of the composed table."""

    def __init__(self, m):
        self.m = m
        self.name = "COMPOSER that keeps %d of 16 composed entries" % m

    def recall(self, label):
        full = Composer.recall(self, label)
        if full is None:
            return None
        return [full[x] if x < self.m else None for x in range(N)]

    def predict(self, x):
        if self.plan is not None:
            g = self.plan[x]
            if g is not None:
                return g
            reserved = set(v for xx, v in enumerate(self.plan) if v is not None and xx not in self.seen)
            for o in range(N):
                if o not in self.used and o not in reserved:
                    return o
        for o in range(N):
            if o not in self.used:
                return o

    def learn(self, x, y):
        self.used.add(y)
        self.seen[x] = y


class Hider(Elim):
    """Inherits the answer table of the ninth pair (possible only where the harness leaks or reuses keys)."""
    name = "HIDER of an inherited answer"

    def recall(self, label):
        return list(self.inherited) if (self.inherited is not None and label == (2, 2)) else None


class Sandbagger(Hider):
    """Hider that uses the inherited answer only when the life looked like the main history:
    eight families seen and the move label 2 met before."""
    name = "SANDBAGGING HIDER (reads the control from labels and length)"

    def recall(self, label):
        if label != (2, 2) or self.inherited is None:
            return None
        looks_main = len(self.order) >= 8 and any(lab[1] == 2 for lab in self.tables)
        return list(self.inherited) if looks_main else None


# ----------------------------------------------------------------------------- world

ALL = [(j, k) for j in range(3) for k in range(3)]


def life(make, rng, history, held=(2, 2), mode="main", leak=None):
    """One life. Returns the score of 16 on the held-out pair.
    mode 'main': history then held, same keys.
    mode 'fresh': history from other keys (same labels), held pair from the real keys (irrelevant history).
    leak: None, or a fixed (L, P) reused by the harness and inherited by the organism."""
    if leak is None:
        L = [rng.sample(range(N), N) for _ in range(3)]
        P = [rng.sample(range(N), N) for _ in range(3)]
        inherited = None
    else:
        L, P = leak
        inherited = [P[held[1]][L[held[0]][x]] for x in range(N)]
    if mode == "fresh":
        L2 = [rng.sample(range(N), N) for _ in range(3)]
        P2 = [rng.sample(range(N), N) for _ in range(3)]
    else:
        L2, P2 = L, P
    org = make()
    org.begin_life(inherited)
    right = 0
    for (j, k) in list(history) + [held]:
        last = (j, k) == held
        Lx, Px = (L, P) if last else (L2, P2)
        org.begin_family((j, k))
        right = 0
        for x in rng.sample(range(N), N):
            y = Px[k][Lx[j][x]]
            right += (org.predict(x) == y)
            org.learn(x, y)
        org.end_family()
    return right


def run(make, lives, history_fn, seed, **kw):
    rng = random.Random(seed)
    scores = []
    for _ in range(lives):
        hist, held = history_fn(rng)
        scores.append(life(make, rng, hist, held, **kw))
    return scores


def h_main(rng):
    return [p for p in ALL if p != (2, 2)], (2, 2)


def h_main_shuffled(rng):
    h = [p for p in ALL if p != (2, 2)]
    rng.shuffle(h)
    return h, (2, 2)


def h_control_move(rng):          # the author's control: the move of the ninth pair is never shown
    return [(j, k) for j in range(3) for k in range(2)], (2, 2)


def h_control_table(rng):         # the control the author lists as still needed: the table is never shown
    return [(j, k) for j in range(2) for k in range(3)], (2, 2)


def h_random_held(rng):
    held = rng.choice(ALL)
    h = [p for p in ALL if p != held]
    return h, held


def stat(scores):
    n = len(scores)
    m = sum(scores) / n
    var = sum((s - m) ** 2 for s in scores) / (n - 1)
    return m, math.sqrt(var / n)


def line(name, scores):
    m, se = stat(scores)
    thr = threshold(len(scores))
    print("  %-72s mean %6.3f  se %.3f  n %5d  thr %.2f  %s" % (name, m, se, len(scores), thr,
                                                              "CARRIED" if m >= thr else "NOT_SHOWN"))
    sys.stdout.flush()
    return m


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    print("H16 = %.6f ; threshold at n=300, alpha=1e-6: %.4f ; log2(16!) = %.2f bits"
          % (H16, threshold(300), math.log2(math.factorial(16))))
    if which in ("all", "base"):
        print("\n[1] the author's four numbers, my implementation (n = 300 and n = 4000)")
        for n in (300, 4000):
            for cls in (Elim, CacheRot, Composer):
                if cls is CacheRot and n > 300:
                    n_eff = 1000
                else:
                    n_eff = n
                line(cls.name + " | ninth pair", run(cls, n_eff, h_main, 11))
                line(cls.name + " | control (move withheld)", run(cls, n_eff, h_control_move, 12))
    if which in ("all", "attack"):
        print("\n[2] attempts to beat the bound on the ninth pair without composing three tables")
        line(CacheXor.name, run(CacheXor, 1000, h_main, 21))
        line(SameRow.name, run(SameRow, 4000, h_main, 22))
        line(SameCol.name, run(SameCol, 4000, h_main, 23))
        line(PairCompose.name, run(PairCompose, 1500, h_main, 24))
        line(CacheAffine.name, run(CacheAffine, 150, h_main, 25))
        print("\n[3] organisms that do use three families, in ways the document does not list")
        line(TripleBrute.name, run(TripleBrute, 1000, h_main, 31))
        line(TripleBrute.name + " | control (move withheld)", run(TripleBrute, 1000, h_control_move, 32))
        line(TripleBrute.name + " | shuffled order of the eight", run(TripleBrute, 1000, h_main_shuffled, 33))
        line(TripleBrute.name + " | held-out pair drawn per life", run(TripleBrute, 1000, h_random_held, 34))
        line(OneTableOneRelabel.name, run(OneTableOneRelabel, 2000, h_main, 35))
        line(OneTableOneRelabel.name + " | control (move withheld)", run(OneTableOneRelabel, 2000, h_control_move, 36))
        line(Hardwired22.name, run(Hardwired22, 2000, h_main, 37))
        line(Hardwired22.name + " | held-out pair drawn per life", run(Hardwired22, 2000, h_random_held, 38))
        line(Composer.name + " | held-out pair drawn per life", run(Composer, 2000, h_random_held, 39))
        line(Composer.name + " | control (table withheld)", run(Composer, 2000, h_control_table, 40))
        for m in (1, 2, 3, 4, 8):
            line(PartialComposer(m).name, run(lambda m=m: PartialComposer(m), 3000, h_main, 50 + m))
    if which in ("all", "leak"):
        print("\n[4] a harness that reuses one key for every life (the fault of fire tests B and D of run 4)")
        rng = random.Random(99)
        leak = ([rng.sample(range(N), N) for _ in range(3)], [rng.sample(range(N), N) for _ in range(3)])
        for cls in (Hider, Sandbagger):
            line(cls.name + " | ninth pair", run(cls, 300, h_main, 61, leak=leak))
            line(cls.name + " | author's control (move withheld, six families)", run(cls, 300, h_control_move, 62, leak=leak))
            line(cls.name + " | control by irrelevant keys (same labels, eight families)",
                 run(cls, 300, h_main, 63, leak=leak, mode="fresh"))
        line(Composer.name + " | control by irrelevant keys (fresh keys per life)", run(Composer, 2000, h_main, 64, mode="fresh"))
        line(Elim.name + " | first family of a life (score on (0,0))", run(Elim, 4000, lambda r: ([], (0, 0)), 65))
