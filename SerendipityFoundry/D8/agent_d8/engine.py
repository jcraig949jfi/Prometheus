"""Search engines, history hoard, machinery construction, and metering for D-8.

LEARNER SIDE. This module must never read task['gen'], task['family'], or
task['hidden'] except inside Ctx._verify (the metered boolean oracle).

Frozen constants live in CFG and are hashed at freeze.
"""

from collections import defaultdict

from svm import rng, run as vmrun, CONST, MAXLEN

CFG = dict(
    BUDGET=10000,         # candidate evaluations per task per arm
    VCAP=50,              # max verifier submissions per task per arm
    POP=40, ELITE=2, TOUR=3, CX=0.6,
    MUT_PT=0.15, MUT_INS=0.08, MUT_DEL=0.08,
    RETR_N=200, RETR_SEEDS=10,
    HOARD_CAP=3000, HOARD_MIN_MATCH=5, HOARD_MIN_BITS=40,
    SEG_MIN=2, SEG_MAX=5, SEG_TABLE=300,
    MAC_MINLEN=3, MAC_MAXLEN=6, MAC_MINTASKS=2, MAC_K=8,
    M1_STD_P=0.55, M1_SPLICE_P=0.30,   # remaining 0.15 = macro insert
    MACRO_TOKEN_P=0.08,
    HC_STALL=200,
)

POPCNT = [bin(i).count("1") for i in range(256)]

PROBES = None


def probes():
    global PROBES
    if PROBES is None:
        r = rng("probe-inputs-v1")
        PROBES = [(r.randrange(256), r.randrange(256), r.randrange(256))
                  for _ in range(8)]
    return PROBES


class Ctx:
    """Per-(arm, task) execution context: metering, cache, verifier gate."""

    def __init__(self, task, budget, meters, collect=False):
        self.task = task
        self.B = budget
        self.meters = meters
        self.cache = {}
        self.evals = 0
        self.solved = False
        self.solution = None       # expanded tokens (tuple)
        self.solution_raw = None   # pre-expansion tokens (list), set by caller
        self.solve_evals = None
        self.vcalls = 0
        self.vfailed = set()
        self.best = 0
        self.collect = collect
        self.collected = []

    def _verify(self, prog):
        # ORACLE SIDE: boolean only; metered.
        self.vcalls += 1
        self.meters["verifier_calls"] += 1
        vs = 0
        ok = True
        for (x, y) in self.task["hidden"]:
            out, s = vmrun(prog, *x)
            vs += s
            if out != y:
                ok = False
                break
        self.meters["verifier_steps"] += vs
        return ok

    def evaluate(self, prog, retrieval=False):
        """prog: tuple of base tokens (expanded). Returns search fitness =
        bit-level agreement over the 6 revealed pairs (0..48), or -1 if the
        budget is exhausted. Exact solve still requires 6/6 byte matches
        plus verifier pass. Identical-bytes memoization is legal and
        identical across arms."""
        c = self.cache.get(prog)
        if c is not None:
            return c
        if self.evals >= self.B or self.solved:
            return -1
        self.evals += 1
        self.meters["cand_evals"] += 1
        if retrieval:
            self.meters["retrieval_evals"] += 1
        m = 0
        bits = 0
        steps = 0
        for (x, y) in self.task["revealed"]:
            out, s = vmrun(prog, *x)
            steps += s
            bits += 8 - POPCNT[out ^ y]
            if out == y:
                m += 1
        self.meters["vm_steps"] += steps
        if m > self.best:
            self.best = m
        fit = float(bits)
        solved_now = False
        if m == 6:
            if prog in self.vfailed:
                fit = 47.0
                m = 5
            elif self.vcalls < CFG["VCAP"]:
                if self._verify(prog):
                    self.solved = True
                    self.solution = prog
                    self.solve_evals = self.evals
                    solved_now = True
                else:
                    self.vfailed.add(prog)
                    fit = 47.0
                    m = 5
            # past VCAP: fitness stays 48, never verified (frozen rule)
        if self.collect:
            if solved_now:
                self.collected.append((prog, 6))
            elif m >= CFG["HOARD_MIN_MATCH"]:
                self.collected.append((prog, 5))
            elif bits >= CFG["HOARD_MIN_BITS"]:
                self.collected.append((prog, 1))
        self.cache[prog] = fit
        return fit


# ---------------------------------------------------------------- programs

def rand_tok(rnd, mach=None):
    if mach is not None and mach.use_macros and mach.macros:
        idxs = [i for i, e in enumerate(mach.macro_enabled) if e]
        if idxs and rnd.random() < CFG["MACRO_TOKEN_P"]:
            return 1000 + rnd.choice(idxs)
    i = rnd.randrange(26)
    if i == CONST:
        return 256 + rnd.randrange(256)
    return i


def random_prog(rnd, mach=None):
    n = rnd.randint(1, MAXLEN)
    return [rand_tok(rnd, mach) for _ in range(n)]


def expand(ind, mach):
    out = []
    for t in ind:
        if t >= 1000:
            if mach is not None and mach.use_macros:
                i = t - 1000
                if i < len(mach.macros) and mach.macro_enabled[i]:
                    out.extend(mach.macros[i])
        else:
            out.append(t)
    return tuple(out[:MAXLEN])


def _mut_tok(t, rnd, mach):
    """Point mutation. Literal tokens get a local +-1..8 wraparound
    perturbation half the time (generic substrate-appropriate move,
    identical across all arms)."""
    if 256 <= t < 1000 and rnd.random() < 0.5:
        d = rnd.randint(1, 8) * (1 if rnd.random() < 0.5 else -1)
        return 256 + ((t - 256 + d) & 255)
    return rand_tok(rnd, mach)


def standard_mutate(ind, rnd, mach=None):
    out = list(ind)
    for i in range(len(out)):
        if rnd.random() < CFG["MUT_PT"]:
            out[i] = _mut_tok(out[i], rnd, mach)
    if rnd.random() < CFG["MUT_INS"] and len(out) < MAXLEN:
        out.insert(rnd.randrange(len(out) + 1), rand_tok(rnd, mach))
    if rnd.random() < CFG["MUT_DEL"] and len(out) > 1:
        del out[rnd.randrange(len(out))]
    if not out:
        out = [rand_tok(rnd, mach)]
    return out


def m1_mutate(ind, rnd, mach):
    r = rnd.random()
    can_splice = mach is not None and mach.records and (
        (mach.use_segw and mach.segments) or mach.uniform_bag)
    if r < CFG["M1_STD_P"] or not can_splice:
        return standard_mutate(ind, rnd, mach)
    if r < CFG["M1_STD_P"] + CFG["M1_SPLICE_P"]:
        seg = mach.sample_segment(rnd)
        out = list(ind)
        pos = rnd.randrange(len(out) + 1)
        if rnd.random() < 0.5 and out:
            end = min(len(out), pos + len(seg))
            out[pos:end] = list(seg)
        else:
            out[pos:pos] = list(seg)
        return out[:MAXLEN] or [rand_tok(rnd, mach)]
    if mach.use_macros and mach.macros and any(mach.macro_enabled):
        idxs = [i for i, e in enumerate(mach.macro_enabled) if e]
        out = list(ind)
        out.insert(rnd.randrange(len(out) + 1), 1000 + rnd.choice(idxs))
        return out[:MAXLEN]
    return standard_mutate(ind, rnd, mach)


def fit_child(child, rnd, mach):
    """Ensure expanded length <= MAXLEN; deterministic repair."""
    for _ in range(8):
        if len(expand(child, mach)) <= MAXLEN:
            return child
        child = child[:-1] or [rand_tok(rnd, mach)]
    return child


# ---------------------------------------------------------------- machinery

class Machinery:
    """The hoard plus machine-constructed organization.

    Stored: raw records (program, weight, probe behavior) and dev solutions.
    Constructed (deterministically rebuilt from stored): bigram token-class
    statistics, empirical length/literal distributions, weighted segment
    table, promoted macro registry (the z-candidates).

    Flags select control arms; they never change the stored data."""

    def __init__(self):
        self.records = []          # dicts: prog(list), w(int), beh(tuple)
        self.beh_seen = {}
        self.solutions = {}        # task uid -> expanded token list
        self.bigram = None         # 27x27 counts (class 26 = literal)
        self.starts = None
        self.lens = None
        self.lits = None
        self.segments = []
        self.segw = []
        self.macros = []           # list of tuple(base tokens)
        self.macro_meta = []       # provenance dicts
        self.macro_enabled = []
        self.use_bigram = True
        self.use_segw = True
        self.use_macros = True
        self.use_retrieval = True
        self.uniform_bag = False

    # ---------- storage

    def add_record(self, prog, w, meters):
        beh = []
        steps = 0
        for x in probes():
            out, s = vmrun(prog, *x)
            beh.append(out)
            steps += s
        meters["hist_evals"] += 1
        meters["hist_vm_steps"] += steps
        beh = tuple(beh)
        old = self.beh_seen.get(beh)
        if old is not None:
            if len(prog) < len(old["prog"]):
                old["prog"] = list(prog)
                old["w"] = max(old["w"], w)
            else:
                old["w"] = max(old["w"], w)
            return
        rec = dict(prog=list(prog), w=w, beh=beh)
        self.records.append(rec)
        self.beh_seen[beh] = rec
        if len(self.records) > CFG["HOARD_CAP"]:
            dead = self.records.pop(0)
            self.beh_seen.pop(dead["beh"], None)

    # ---------- construction (deterministic from stored data)

    @staticmethod
    def _cls(t):
        return 26 if t >= 256 else t

    def build(self, meters):
        big = [[0.0] * 27 for _ in range(27)]
        starts = [0.0] * 27
        lens = defaultdict(float)
        lits = defaultdict(float)
        segs = defaultdict(float)
        ops = 0
        for rec in self.records:
            p = rec["prog"]
            w = float(rec["w"])
            ops += len(p)
            if not p:
                continue
            starts[self._cls(p[0])] += w
            lens[len(p)] += w
            for i, t in enumerate(p):
                if t >= 256:
                    lits[t - 256] += w
                if i + 1 < len(p):
                    big[self._cls(t)][self._cls(p[i + 1])] += w
            for L in range(CFG["SEG_MIN"], CFG["SEG_MAX"] + 1):
                for i in range(len(p) - L + 1):
                    segs[tuple(p[i:i + L])] += w
        meters["build_ops"] += ops
        self.bigram = big
        self.starts = starts
        self.lens = sorted(lens.items())
        self.lits = sorted(lits.items())
        top = sorted(segs.items(), key=lambda kv: (-kv[1], kv[0]))
        top = top[:CFG["SEG_TABLE"]]
        self.segments = [k for k, _ in top]
        self.segw = [v for _, v in top]

    def promote_macros(self, meters):
        """z-candidate registry: contiguous segments (len 3..6) appearing in
        verified solutions of >= MAC_MINTASKS distinct tasks; top MAC_K by
        (#tasks desc, length desc, lexical). Frozen predicate; purely
        machine-native (no target decomposition)."""
        seg2tasks = defaultdict(set)
        for uid, sol in sorted(self.solutions.items()):
            p = list(sol)
            meters["build_ops"] += len(p)
            for L in range(CFG["MAC_MINLEN"], CFG["MAC_MAXLEN"] + 1):
                for i in range(len(p) - L + 1):
                    seg2tasks[tuple(p[i:i + L])].add(uid)
        qual = [(len(v), len(k), k, sorted(v)) for k, v in seg2tasks.items()
                if len(v) >= CFG["MAC_MINTASKS"]]
        qual.sort(key=lambda z: (-z[0], -z[1], z[2]))
        self.macros = [k for _, _, k, _ in qual[:CFG["MAC_K"]]]
        self.macro_meta = [dict(ntasks=n, length=l, tasks=t)
                           for n, l, k, t in qual[:CFG["MAC_K"]]]
        self.macro_enabled = [True] * len(self.macros)

    def promote_macros_mirror(self, meters):
        """H-RANDOM mirror of promotion: no solutions exist, so promote the
        top-K segments (len 3..6) by weighted frequency across records."""
        segs = defaultdict(float)
        for rec in self.records:
            p = rec["prog"]
            meters["build_ops"] += len(p)
            for L in range(CFG["MAC_MINLEN"], CFG["MAC_MAXLEN"] + 1):
                for i in range(len(p) - L + 1):
                    segs[tuple(p[i:i + L])] += rec["w"]
        top = sorted(segs.items(), key=lambda kv: (-kv[1], kv[0]))
        self.macros = [k for k, _ in top[:CFG["MAC_K"]]]
        self.macro_meta = [dict(ntasks=0, length=len(k), tasks=["HRND"])
                           for k, _ in top[:CFG["MAC_K"]]]
        self.macro_enabled = [True] * len(self.macros)

    # ---------- sampling

    def gen_random(self, rnd):
        if not self.use_bigram or self.bigram is None or not self.lens:
            return random_prog(rnd, self)
        n = rnd.choices([k for k, _ in self.lens],
                        [v for _, v in self.lens])[0]
        out = []
        w = [c + 0.5 for c in self.starts]
        cls = rnd.choices(range(27), w)[0]
        out.append(self._emit(rnd, cls))
        for _ in range(n - 1):
            row = self.bigram[self._cls(out[-1])]
            w = [c + 0.5 for c in row]
            cls = rnd.choices(range(27), w)[0]
            out.append(self._emit(rnd, cls))
        return out

    def _emit(self, rnd, cls):
        if cls == 26:
            if self.lits:
                v = rnd.choices([k for k, _ in self.lits],
                                [w for _, w in self.lits])[0]
            else:
                v = rnd.randrange(256)
            return 256 + v
        return cls

    def sample_segment(self, rnd):
        if self.use_segw and self.segments:
            return rnd.choices(self.segments, self.segw)[0]
        # uniform-bag route: random substring of a random stored program
        rec = rnd.choice(self.records)
        p = rec["prog"]
        if len(p) <= CFG["SEG_MIN"]:
            return tuple(p)
        L = rnd.randint(CFG["SEG_MIN"], min(CFG["SEG_MAX"], len(p)))
        i = rnd.randrange(len(p) - L + 1)
        return tuple(p[i:i + L])

    # ---------- serialization

    def to_json(self):
        return dict(records=[dict(prog=r["prog"], w=r["w"],
                                  beh=list(r["beh"])) for r in self.records],
                    solutions={k: list(v) for k, v in self.solutions.items()})

    @classmethod
    def from_json(cls, d, meters, mirror_promotion=False):
        m = cls()
        for r in d["records"]:
            rec = dict(prog=list(r["prog"]), w=r["w"], beh=tuple(r["beh"]))
            m.records.append(rec)
            m.beh_seen[rec["beh"]] = rec
        m.solutions = {k: list(v) for k, v in d.get("solutions", {}).items()}
        m.build(meters)
        if mirror_promotion:
            m.promote_macros_mirror(meters)
        else:
            m.promote_macros(meters)
        return m

    def clone_flags(self, **flags):
        """Shallow variant sharing stored data, different control flags."""
        import copy
        m = copy.copy(self)
        m.macro_enabled = list(self.macro_enabled)
        for k, v in flags.items():
            setattr(m, k, v)
        return m


def shuffled_machinery(mach, meters):
    """H-SHUFFLE: same information mass and marginals; stored relational
    wiring permuted. Bigram rows/cols permuted by a class permutation,
    segment weights permuted among segments, macro registry replaced by
    random equal-length substrings of random records."""
    r = rng("shuffle-v1")
    m = mach.clone_flags()
    pi = list(range(27))
    r.shuffle(pi)
    big = [[0.0] * 27 for _ in range(27)]
    for a in range(27):
        for b in range(27):
            big[pi[a]][pi[b]] = mach.bigram[a][b]
    m.bigram = big
    m.starts = [0.0] * 27
    for a in range(27):
        m.starts[pi[a]] = mach.starts[a]
    m.segments = list(mach.segments)
    m.segw = list(mach.segw)
    r.shuffle(m.segw)
    mac = []
    for z in mach.macros:
        L = len(z)
        for _ in range(50):
            rec = r.choice(mach.records)
            p = rec["prog"]
            if len(p) >= L:
                i = r.randrange(len(p) - L + 1)
                mac.append(tuple(p[i:i + L]))
                break
        else:
            mac.append(tuple(z))
    m.macros = mac
    m.macro_enabled = [True] * len(mac)
    return m


# ---------------------------------------------------------------- searches

def random_search(ctx, rnd):
    while not ctx.solved and ctx.evals < ctx.B:
        p = tuple(random_prog(rnd))
        ctx.evaluate(p)
        if ctx.solved and ctx.solution == p:
            ctx.solution_raw = list(p)


def hillclimb(ctx, rnd):
    cur = random_prog(rnd)
    fc = ctx.evaluate(tuple(cur))
    if ctx.solved:
        ctx.solution_raw = list(cur)
        return
    stall = 0
    while not ctx.solved and ctx.evals < ctx.B:
        cand = standard_mutate(cur, rnd, None)
        f = ctx.evaluate(tuple(cand))
        if ctx.solved:
            ctx.solution_raw = list(cand)
            return
        if f > fc:
            cur, fc, stall = cand, f, 0
        elif f == fc:
            cur = cand
            stall += 1
        else:
            stall += 1
        if stall >= CFG["HC_STALL"]:
            cur = random_prog(rnd)
            fc = ctx.evaluate(tuple(cur))
            if ctx.solved:
                ctx.solution_raw = list(cur)
                return
            stall = 0


def _tournament(rnd, scored):
    best = None
    for _ in range(CFG["TOUR"]):
        c = scored[rnd.randrange(len(scored))]
        if best is None or c[0] > best[0]:
            best = c
    return list(best[1])


def ga(ctx, rnd, mach=None):
    """Shared GA physics. mach=None -> M0c. mach -> M1-family arm; only the
    proposal distribution differs (retrieval seeds, bigram randoms, splice,
    macro tokens), never the budget, fitness, or verifier."""
    seeds = []
    if mach is not None and mach.use_retrieval and mach.records:
        n = min(CFG["RETR_N"], len(mach.records))
        samp = rnd.sample(mach.records, n)
        scored_d = []
        for rec in samp:
            if ctx.solved or ctx.evals >= ctx.B:
                break
            p = tuple(rec["prog"])[:MAXLEN]
            m = ctx.evaluate(p, retrieval=True)
            if ctx.solved and ctx.solution == p:
                ctx.solution_raw = list(p)
                return
            scored_d.append((m, len(p), p))
        scored_d.sort(key=lambda z: (-z[0], z[1], z[2]))
        seeds = [list(z[2]) for z in scored_d[:CFG["RETR_SEEDS"]]]
    if ctx.solved or ctx.evals >= ctx.B:
        return
    pop = [list(s) for s in seeds]
    while len(pop) < CFG["POP"]:
        if mach is not None:
            pop.append(mach.gen_random(rnd))
        else:
            pop.append(random_prog(rnd))
    scored = []
    for ind in pop:
        if ctx.solved or ctx.evals >= ctx.B:
            break
        e = expand(ind, mach)
        f = ctx.evaluate(e)
        if ctx.solved and ctx.solution == e:
            ctx.solution_raw = list(ind)
            return
        scored.append((f, ind))
    while not ctx.solved and ctx.evals < ctx.B and len(scored) >= 4:
        scored.sort(key=lambda z: (-z[0], len(z[1])))
        newpop = scored[:CFG["ELITE"]]
        while (len(newpop) < CFG["POP"] and not ctx.solved
               and ctx.evals < ctx.B):
            p1 = _tournament(rnd, scored)
            p2 = _tournament(rnd, scored)
            if rnd.random() < CFG["CX"] and p1 and p2:
                i = rnd.randrange(1, len(p1) + 1)
                j = rnd.randrange(len(p2) + 1)
                child = (p1[:i] + p2[j:])[:MAXLEN] or list(p1)
            else:
                child = list(p1)
            if mach is not None:
                child = m1_mutate(child, rnd, mach)
            else:
                child = standard_mutate(child, rnd, None)
            child = fit_child(child, rnd, mach)
            e = expand(child, mach)
            f = ctx.evaluate(e)
            if f < 0:
                break
            if ctx.solved and ctx.solution == e:
                ctx.solution_raw = list(child)
                return
            newpop.append((f, child))
        scored = newpop


# ---------------------------------------------------------------- runner

def run_task(arm, task, mach=None, budget=None, collect=False):
    """One (arm, task) episode. Deterministic given (arm, task uid)."""
    meters = defaultdict(int)
    ctx = Ctx(task, budget or CFG["BUDGET"], meters, collect=collect)
    rnd = rng("search-v1", arm, task["uid"])
    if arm == "M0a":
        random_search(ctx, rnd)
    elif arm == "M0b":
        hillclimb(ctx, rnd)
    elif arm == "M0c":
        ga(ctx, rnd, None)
    else:
        ga(ctx, rnd, mach)
    macros_used = []
    if ctx.solution_raw:
        macros_used = sorted(set(t - 1000 for t in ctx.solution_raw
                                 if t >= 1000))
    row = dict(uid=task["uid"], arm=arm, solved=bool(ctx.solved),
               evals=ctx.evals, solve_evals=ctx.solve_evals,
               best=ctx.best, vcalls=ctx.vcalls,
               solution=list(ctx.solution) if ctx.solution else None,
               raw=list(ctx.solution_raw) if ctx.solution_raw else None,
               macros_used=macros_used,
               meters=dict(meters))
    return row, ctx
