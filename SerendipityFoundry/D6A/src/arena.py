"""Shared arena for every hoard-bearing arm (v2, per PREREG AMENDMENT 1).

One proposal physics, one oracle, one selection interface. The ONLY thing that differs
between arms is the scoring function `z` handed to `search()`:

    H1 / M1-HOARD : z = None   -> every draw is uniform (k collapses to 1)
    H2            : z from SHUFFLED relational history
    H3 / M1-REL   : z from INTACT relational history
    RAND-Z        : z from a random genome, intact tables
    Z0-z          : z from hoard-intrinsic tables only

Interface (uniform): wherever the physics draws an artifact (archive parent, hoard
operand, candidate submitted to the oracle) a z-bearing arm draws K_TOURN and keeps
argmax z. z can never call the oracle, read the target, or see task identity.
"""
import random, sys
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S

K_TOURN = 32           # fixed by step-8 validation + mech_probe, frozen (AMENDMENT 3)
CAND_BATCH = 1         # z acts at artifact-draw tournaments only, frozen (AMENDMENT 3)
COMPOSE_MAXLEN = 12    # length cap on hoard entries so compositions fit L<=32 (frozen)
ARCHIVE_CAP = 4000
ZCACHE_CAP = 300_000


class Solved(Exception):
    pass


class Exhausted(Exception):
    pass


class Oracle:
    """The only task-level feedback channel. Returns one bit and counts every call."""
    __slots__ = ('target', 'n_out', 'budget', 'calls', 'witness')

    def __init__(self, target, n_out, budget):
        self.target = target
        self.n_out = n_out
        self.budget = budget
        self.calls = 0
        self.witness = None

    def __call__(self, prog):
        if self.calls >= self.budget:
            raise Exhausted()
        self.calls += 1
        if S.behavior(prog, self.n_out) == self.target:
            self.witness = prog
            raise Solved()
        return False


# --------------------------------------------------------------------------- hoard

class Hoard:
    """A bag of artifacts with NO relations. Deduplicated by output behavior (intrinsic)."""

    def __init__(self):
        self.by_beh = {}
        self.items = []
        self.n = 0

    def add(self, prog):
        prog = tuple(tuple(i) for i in prog)
        if not prog or len(prog) > COMPOSE_MAXLEN:
            return
        b = S.behavior(prog)[0]
        cur = self.by_beh.get(b)
        if cur is None or len(prog) < len(cur):
            self.by_beh[b] = prog

    def freeze(self):
        self.items = list(self.by_beh.values())
        self.n = len(self.items)
        return self

    def sample(self, rng, zf=None, k=1):
        if self.n == 0:
            return None
        if zf is None:
            return self.items[rng.randrange(self.n)]
        best, bs = None, None
        for _ in range(k):
            p = self.items[rng.randrange(self.n)]
            s = zf(p)
            if bs is None or s > bs:
                bs, best = s, p
        return best

    def dump(self):
        return sorted([hex(b), [list(i) for i in p]] for b, p in self.by_beh.items())

    @staticmethod
    def load(d):
        h = Hoard()
        for b, p in d:
            h.by_beh[int(b, 16)] = tuple(tuple(i) for i in p)
        return h.freeze()


# ---------------------------------------------------------------- relational history

class History:
    """Machine-native relations accumulated across developmental episodes.

    recur : wire behavior -> number of episodes whose passing artifact contained it.
    anc   : behavior -> occurrences on the ancestral chain of a pass.
    cooc  : ordered behavior pair -> co-occurrence as wires inside one passing artifact.
    solved: behaviors that were themselves a passing artifact's first output.

    No English labels, no task ids, no family ids, no target information.
    """

    def __init__(self):
        self.recur, self.anc, self.cooc, self.solved = {}, {}, {}, set()
        self.episodes = 0

    def record_pass(self, witness, chain):
        self.episodes += 1
        seen = set(S.evaluate(witness)[S.N_IN:])
        for b in seen:
            self.recur[b] = self.recur.get(b, 0) + 1
        ws = sorted(seen)
        for i, a in enumerate(ws):
            for b in ws[i + 1:]:
                self.cooc[(a, b)] = self.cooc.get((a, b), 0) + 1
        self.solved.add(S.behavior(witness)[0])
        for p in chain:
            b = S.behavior(p)[0]
            self.anc[b] = self.anc.get(b, 0) + 1

    def merge(self, other):
        self.episodes += other.episodes
        for k, v in other.recur.items():
            self.recur[k] = self.recur.get(k, 0) + v
        for k, v in other.anc.items():
            self.anc[k] = self.anc.get(k, 0) + v
        for k, v in other.cooc.items():
            self.cooc[k] = self.cooc.get(k, 0) + v
        self.solved |= other.solved

    def shuffled(self, rng):
        """H2 null: keep every relation VALUE, destroy which behavior it attaches to."""
        h = History()
        h.episodes = self.episodes
        for src, dst in ((self.recur, 'recur'), (self.anc, 'anc')):
            keys, vals = list(src), list(src.values())
            rng.shuffle(vals)
            setattr(h, dst, dict(zip(keys, vals)))
        keys, vals = list(self.cooc), list(self.cooc.values())
        rng.shuffle(vals)
        h.cooc = dict(zip(keys, vals))
        pool = list(self.recur)
        h.solved = set(rng.sample(pool, min(len(self.solved), len(pool)))) if pool else set()
        return h

    def dump(self):
        return dict(episodes=self.episodes,
                    recur={hex(k): v for k, v in self.recur.items()},
                    anc={hex(k): v for k, v in self.anc.items()},
                    cooc=[[hex(a), hex(b), v] for (a, b), v in self.cooc.items()],
                    solved=[hex(x) for x in self.solved])

    @staticmethod
    def load(d):
        h = History()
        h.episodes = d['episodes']
        h.recur = {int(k, 16): v for k, v in d['recur'].items()}
        h.anc = {int(k, 16): v for k, v in d['anc'].items()}
        h.cooc = {(int(a, 16), int(b, 16)): v for a, b, v in d['cooc']}
        h.solved = {int(x, 16) for x in d['solved']}
        return h


# ------------------------------------------------------------ proposal physics (frozen)

def _tpick(pop, scores, rng, k):
    """Tournament-k over a scored population; scores precomputed (identical z values)."""
    if scores is None:
        return pop[rng.randrange(len(pop))]
    bi = rng.randrange(len(pop))
    for _ in range(k - 1):
        i = rng.randrange(len(pop))
        if scores[i] > scores[bi]:
            bi = i
    return pop[bi]


def propose(rng, hoard, hscores, archive, ascores, k=1):
    """Identical distribution for every arm; z only biases WHICH artifact fills a slot."""
    r = rng.random()
    if archive and r < 0.35:
        par = _tpick(archive, ascores, rng, k)
        return S.mutate(par, rng), par
    if r < 0.70 and hoard.n:
        a = _tpick(hoard.items, hscores, rng, k)
        b = _tpick(hoard.items, hscores, rng, k)
        p = S.combine(a, b, rng.randrange(S.N_OPS))
        return (p, None) if len(p) <= S.LMAX else (S.random_program(rng, 2, 12), None)
    if archive and r < 0.90:
        par = _tpick(archive, ascores, rng, k)
        if hoard.n:
            b = _tpick(hoard.items, hscores, rng, k)
            p = S.combine(par, b, rng.randrange(S.N_OPS))
            if len(p) <= S.LMAX:
                return p, par
        return S.mutate(par, rng), par
    return S.random_program(rng, 2, 12), None


# ------------------------------------------------------------------- the search loop

def search(target, n_out, budget, seed, hoard, z=None, k=K_TOURN, cand_batch=CAND_BATCH, record=None):
    """Returns dict(solved, calls, gen, witness, archive, chain)."""
    rng = random.Random(seed)
    orc = Oracle(target, n_out, budget)
    hscores = [z(p) for p in hoard.items] if (z is not None and hoard.n) else None
    ascores = [] if z is not None else None
    archive, seen, parent_of = [], set(), {}
    gen = 0
    try:
        while True:
            if z is None:
                cand, par = propose(rng, hoard, None, archive, None)
                gen += 1
                cscore = None
            else:
                cand = par = None
                cscore = None
                for _ in range(cand_batch):
                    c, pr = propose(rng, hoard, hscores, archive, ascores, k)
                    s = z(c)
                    if cscore is None or s > cscore:
                        cand, par, cscore = c, pr, s
                gen += cand_batch
            orc(cand)
            b = S.behavior(cand, n_out)
            if b not in seen:
                seen.add(b)
                if len(archive) < ARCHIVE_CAP:
                    archive.append(cand)
                    if ascores is not None:
                        ascores.append(cscore)
                else:
                    i = rng.randrange(ARCHIVE_CAP)
                    archive[i] = cand
                    if ascores is not None:
                        ascores[i] = cscore
                if par is not None:
                    parent_of[cand] = par
    except Solved:
        chain, cur = [], orc.witness
        while cur in parent_of and len(chain) < 64:
            cur = parent_of[cur]
            chain.append(cur)
        if record is not None:
            record.record_pass(orc.witness, chain)
        return dict(solved=True, calls=orc.calls, gen=gen,
                    witness=orc.witness, archive=archive, chain=chain)
    except Exhausted:
        return dict(solved=False, calls=orc.calls, gen=gen,
                    witness=None, archive=archive, chain=[])
