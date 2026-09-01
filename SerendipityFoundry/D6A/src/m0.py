"""M0 - strongest reasonable HISTORY-FREE search under exact-only (PASS/FAIL) feedback.

The oracle returns a boolean and nothing else. It counts calls and hard-stops at budget.
Three components share the budget equally; M0 solves a task if any component solves it.
No component ever sees the target, a distance, a partial score, or any task identity.
"""
import json, random, sys, os, time
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S

BUDGET = 200_000
SEEDS = 12


class Solved(Exception):
    pass


class Exhausted(Exception):
    pass


class Oracle:
    """The ONLY task-level feedback channel in the experiment."""
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
        return False                      # <- exactly one bit, and it is always this bit


def comp_uniform(orc, rng, n):
    for _ in range(n):
        orc(S.random_program(rng, 2, 12))


def comp_walk(orc, rng, n, restart=2000):
    cur = S.random_program(rng, 2, 12)
    orc(cur)
    for i in range(1, n):
        cur = S.random_program(rng, 2, 12) if i % restart == 0 else S.mutate(cur, rng)
        orc(cur)


def comp_novelty(orc, rng, n, cap=20000):
    """Archive search driven by INTRINSIC behavioral novelty (own traces only)."""
    a = S.random_program(rng, 2, 12)
    orc(a)
    arch = [a]
    seen = {S.behavior(a, orc.n_out)}
    for _ in range(1, n):
        p = S.mutate(arch[rng.randrange(len(arch))], rng)
        orc(p)
        b = S.behavior(p, orc.n_out)
        if b not in seen:
            seen.add(b)
            if len(arch) < cap:
                arch.append(p)
            else:
                arch[rng.randrange(cap)] = p


COMPONENTS = (comp_uniform, comp_walk, comp_novelty)


def run_seed(target, n_out, seed, budget=BUDGET):
    share = budget // len(COMPONENTS)
    calls = 0
    for ci, comp in enumerate(COMPONENTS):
        orc = Oracle(target, n_out, share)
        rng = random.Random((seed << 8) ^ ci)
        try:
            comp(orc, rng, share)
        except Solved:
            return True, calls + orc.calls, ci
        except Exhausted:
            pass
        calls += orc.calls
    return False, calls, -1


def run_task(t):
    target = tuple(int(x, 16) for x in t['target'])
    res = [run_seed(target, t['n_out'], s) for s in range(SEEDS)]
    return dict(id=t['id'], family=t['family'], tier=t['tier'],
                solved=[r[0] for r in res], calls=[r[1] for r in res],
                via=[r[2] for r in res], rate=sum(r[0] for r in res) / len(res))


def main():
    tasks = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    t0 = time.time()
    from multiprocessing import Pool
    with Pool(max(1, (os.cpu_count() or 4) - 1)) as pool:
        out = pool.map(run_task, tasks, chunksize=1)
    json.dump(out, open('F:/SerendipityA/runs/m0.json', 'w'))
    agg = {}
    for r in out:
        agg.setdefault((r['family'], r['tier']), []).append(r['rate'])
    print('M0  budget=%d/seed  seeds=%d  wall=%.0fs' % (BUDGET, SEEDS, time.time() - t0))
    for k in sorted(agg):
        v = agg[k]
        print('  %-7s tier%d  n=%2d  solve_rate=%.3f  tasks_ever_solved=%d/%d'
              % (k[0], k[1], len(v), sum(v) / len(v), sum(1 for x in v if x > 0), len(v)))
    conf = [r['rate'] for r in out if r['family'] == 'CONF']
    d1 = [r['rate'] for r in out if r['family'] == 'DEV' and r['tier'] == 1]
    d3 = [r['rate'] for r in out if r['tier'] == 3 and r['family'] in ('DEV', 'CONF')]
    print('GATE V2 dev tier1 in [0.10,0.90]: %.3f -> %s' %
          (sum(d1) / len(d1), 0.10 <= sum(d1) / len(d1) <= 0.90))
    print('GATE V3 tier3 <= 0.15          : %.3f -> %s' %
          (sum(d3) / len(d3), sum(d3) / len(d3) <= 0.15))
    print('GATE V4 CONF  <= 0.15          : %.3f -> %s' %
          (sum(conf) / len(conf), sum(conf) / len(conf) <= 0.15))


if __name__ == '__main__':
    main()
