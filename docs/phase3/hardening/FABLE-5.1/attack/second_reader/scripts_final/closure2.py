"""Can falsifier 6 fire, and does the new control catch every hider? A harness that reuses the life's own key
for every life (run 4's fire test B) while the control's other key is drawn per life."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, "harness")
from rso_harness import ladder as L
from rso_harness.stats import khash
N = L.N

class RepeatWatcher(L.PairElim):
    """Keeps, from one life to the next, every table it saw under each label. It uses the kept ninth table only if
    the eight tables shown in this life are the ones it saw in the life before. It combines nothing."""
    kept = {}
    def begin_life(self):
        self.tables = {}
    def candidates(self, label):
        k = RepeatWatcher.kept
        if label == L.UNSEEN and label in k and all(self.tables.get(s) == k.get(s) for s in L.SHOWN):
            return [k[label]]
        return []
    def end_family(self):
        L.PairElim.end_family(self)
        if self.label == L.UNSEEN:                      # end of the life: remember all nine tables
            RepeatWatcher.kept = dict(self.tables)

def run_pairs(make, lives, control=False, reuse="both", base=9000):
    """The author's run_pairs with the planted fault made selectable:
    reuse='both'  as in ladder.py: one key for every life, for the life's own tables AND for the control's other key
    reuse='own'   the life's own key is reused; the control's other key is drawn per life
    reuse=None    no fault"""
    scores = []
    RepeatWatcher.kept = {}
    for cls in (L.Hider, L.Sandbagger):
        cls.kept = {}
    for life in range(lives):
        org = make(); org.begin_life()
        def tables(stream, key):
            return ([sorted(range(N), key=lambda i, j=j: khash(base, key, stream, 1, j, i)) for j in range(3)],
                    [sorted(range(N), key=lambda i, k=k: khash(base, key, stream, 2, k, i)) for k in range(3)])
        own = tables(0, 0 if reuse in ("both", "own") else life)
        other = tables(1, 0 if reuse == "both" else life)
        for n, (j, k) in enumerate(L.SHOWN + [L.UNSEEN]):
            bases, moves = other if (control and (j, k) != L.UNSEEN) else own
            org.begin_family((j, k)); right = 0
            for x in sorted(range(N), key=lambda i: khash(base, life, 3, n, i)):
                y = moves[k][bases[j][x]]
                right += org.predict(x) == y
                org.learn(x, y)
            org.end_family()
        scores.append(right)
    return scores

for reuse in ("both", "own", None):
    print("planted fault: reuse = %s" % reuse)
    for name, make in (("HIDER", L.Hider), ("SANDBAGGER", L.Sandbagger), ("REPEAT_WATCHER", RepeatWatcher), ("COMPOSER", L.Composer)):
        a = L.certificate(run_pairs(make, 300, reuse=reuse)); b = L.certificate(run_pairs(make, 300, control=True, reuse=reuse))
        print("  %-15s ninth %6.2f %-9s control %6.2f %-9s -> %s" % (name, a["mean"], a["answer"], b["mean"], b["answer"], L.pair_answer(a, b)))
