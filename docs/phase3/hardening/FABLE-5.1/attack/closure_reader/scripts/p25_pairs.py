"""World two of ladder.py (the unseen pair), as the author wrote it: one more organism.

SCHEMA_CACHE keeps every whole table it has seen, like TABLE_CACHE, and has a fixed inherited list of 512 ways to
build a candidate from what it keeps: c o inverse(b) o a for every ordered triple of kept tables. It never reads a
label, has no notion of a pair, and chooses among its 512 inherited alternatives by elimination on the trials it sees.
"""
from drv import *

N = ladder.N


class SchemaCache(ladder.PairElim):
    def recall(self, label):
        tabs = list(self.tables.values())                    # labels are not used
        self.cands = []
        for a in tabs:
            for b in tabs:
                inv = [0] * N
                for x, y in enumerate(b):
                    inv[y] = x
                for c in tabs:
                    self.cands.append([c[inv[a[x]]] for x in range(N)])
        return self.next_guess()

    def next_guess(self):
        self.cands = [g for g in self.cands if all(g[x] == y for x, y in self.seen.items())]
        return self.cands[0] if self.cands else None


for name, make in (("ELIM", ladder.PairElim), ("TABLE_CACHE (256 re-indexings of one table)", ladder.TableCache),
                   ("COMPOSER (reads the labels)", ladder.Composer),
                   ("SCHEMA_CACHE (512 inherited triples, no labels)", SchemaCache)):
    full = ladder.certificate(ladder.run_pairs(make, 300, ladder.SHOWN))
    ctrl = ladder.certificate(ladder.run_pairs(make, 300, ladder.CONTROL))
    print("%-48s unseen pair %5.2f %-9s | after the control history %5.2f %-9s (threshold %.2f)"
          % (name, full["mean"], full["answer"], ctrl["mean"], ctrl["answer"], full["threshold"]))
print("inherited alternatives of SCHEMA_CACHE on the ninth family: %d (%.1f bits)" % (8 ** 3, 9.0))

# world one, more lives: the 16-offset keeper against the bound
for lives in (300, 1000, 4000):
    rows = ladder.run(ladder.Keeper, lives, "ROTATION")
    cert = ladder.certificate([r[2] for r in rows])
    print("world one, KEEPER (16 inherited offsets), ROTATION, %4d lives: mean %.2f threshold %.2f -> %s"
          % (lives, cert["mean"], cert["threshold"], cert["answer"]))
