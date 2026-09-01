"""Developmental run (the H3 lineage). Produces the hoard + relational history that every
hoard-bearing arm later shares, and the meta-selected z genomes (Z0 and Z1).

Phases (sequential; state saved to runs/dev_state.json after each):
  A : solve DEV tier1 blind (z=None), record passes, retain artifacts.
  B : Z1 meta-search on DEV tier2 discovery subset -> provisional genome zB. Z0 ditto.
  C : full DEV tier2 with zB, record passes, retain.
  D : Z1 meta-search again (revision allowed, P7) on DEV tier2+tier3 subset -> final z*.
  E : full DEV tier3 with z*, record, retain. Freeze everything.

Retention rule (frozen): from each SOLVED episode -> witness, every prefix subprogram of
the witness, ancestor-chain programs, and 60 uniform archive samples; dedup by behavior,
entries capped at COMPOSE_MAXLEN. The final bag is copied byte-identically to H1/H2.

All oracle calls are metered per phase. DEV only; CONF/ALIEN/STRUCT/NEG are never touched.
"""
import json, random, sys, time
from multiprocessing import Pool
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S
import arena as A
import zsig as Z

BUDGET = 200_000
SEEDS = 12
META_GENOMES = 40
META_SEEDS = 2
META_BUDGET = 100_000
STATE = 'F:/SerendipityA/runs/dev_state.json'

_G = {}


def _init(state_blob, genome, table_kind):
    """Pool worker init: rebuild hoard + z from the serialized state."""
    _G['hoard'] = A.Hoard.load(state_blob['hoard'])
    hist = A.History.load(state_blob['history'])
    _G['z'] = None
    if genome is not None:
        tabs = Z.tables_from_history(hist) if table_kind == 'hist' else Z.tables_from_hoard(_G['hoard'])
        _G['z'] = Z.make_z(tuple(genome), tabs)


def _run_one(job):
    tid, target, n_out, seed, budget = job
    hist = A.History()
    r = A.search(tuple(int(x, 16) for x in target), n_out, budget, seed,
                 _G['hoard'], z=_G['z'], record=hist)
    ret = dict(tid=tid, seed=seed, solved=r['solved'], calls=r['calls'], gen=r['gen'])
    if r['solved']:
        ret['hist'] = hist.dump()
        ret['witness'] = [list(i) for i in r['witness']]
        ret['chain'] = [[list(i) for i in p] for p in r['chain']]
        rng = random.Random(seed ^ 0xA5A5)
        arch = r['archive']
        samp = [arch[rng.randrange(len(arch))] for _ in range(min(60, len(arch)))]
        ret['retain'] = [[list(i) for i in p] for p in samp]
    return ret


def retain_from(res, hoard):
    w = tuple(tuple(i) for i in res['witness'])
    hoard.add(w)
    for i in range(1, len(w)):
        hoard.add(w[:i])
    for p in res.get('chain', []):
        hoard.add(p)
    for p in res.get('retain', []):
        hoard.add(p)


def load_state():
    return json.load(open(STATE))


def save_state(st):
    json.dump(st, open(STATE, 'w'))


def tasks_by(tasks, family, tier):
    return [t for t in tasks if t['family'] == family and t['tier'] == tier]


def run_block(tasks, state, genome, table_kind, seeds, budget, procs=10):
    jobs = [(t['id'], t['target'], t['n_out'], (hash(t['id']) & 0xffff) * 1000 + s, budget)
            for t in tasks for s in range(seeds)]
    with Pool(procs, initializer=_init, initargs=(state, genome, table_kind)) as pool:
        return pool.map(_run_one, jobs, chunksize=1)


def phase_A():
    tasks = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    tier1 = tasks_by(tasks, 'DEV', 1)
    hoard, hist = A.Hoard().freeze(), A.History()
    meter, solves = 0, 0
    t0 = time.time()
    for seed in range(SEEDS):
        order = tier1[seed % len(tier1):] + tier1[:seed % len(tier1)]
        for t in order:
            r = A.search(tuple(int(x, 16) for x in t['target']), t['n_out'], BUDGET,
                         seed * 7919 + (hash(t['id']) & 0xffff), hoard, z=None, record=hist)
            meter += r['calls']
            if r['solved']:
                solves += 1
                res = dict(witness=[list(i) for i in r['witness']],
                           chain=[[list(i) for i in p] for p in r['chain']])
                rng = random.Random(seed ^ 0x5A5A)
                arch = r['archive']
                res['retain'] = [[list(i) for i in arch[rng.randrange(len(arch))]]
                                 for _ in range(min(60, len(arch)))]
                retain_from(res, hoard)
                hoard.freeze()
    st = dict(phase='A', hoard=hoard.dump(), history=hist.dump(),
              meter=dict(A=meter), log=dict(A=dict(episodes=SEEDS * len(tier1),
                                                   solves=solves, wall=round(time.time() - t0))))
    save_state(st)
    print('[A] episodes=%d solves=%d hoard=%d recur_keys=%d meter=%d wall=%.0fs'
          % (SEEDS * len(tier1), solves, hoard.n, len(hist.recur), meter, time.time() - t0))


def meta_search(state, disc_tasks, table_kind, label, rng_seed):
    """Z0/Z1 meta-search: sample genomes, score each by solves on discovery tasks."""
    rng = random.Random(rng_seed)
    genomes = list({Z.rand_genome(rng) for _ in range(META_GENOMES * 3)})[:META_GENOMES]
    best, rows = None, []
    meter = 0
    for g in genomes:
        res = run_block(disc_tasks, state, g, table_kind, META_SEEDS, META_BUDGET)
        meter += sum(r['calls'] for r in res)
        ns = sum(r['solved'] for r in res)
        mc = sum(r['calls'] for r in res) / len(res)
        rows.append(dict(genome=list(g), solves=ns, mean_calls=mc))
        key = (ns, -mc)
        if best is None or key > best[0]:
            best = (key, g)
    rows.sort(key=lambda r: (-r['solves'], r['mean_calls']))
    print('[%s] top5: %s' % (label, [(r['genome'], r['solves']) for r in rows[:5]]))
    return best[1], rows, meter


def phase_B():
    st = load_state()
    tasks = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    disc = tasks_by(tasks, 'DEV', 2)[:6]
    gB, rowsB, m1 = meta_search(st, disc, 'hist', 'Z1-meta-B', 101)
    g0, rows0, m0 = meta_search(st, disc, 'hoard', 'Z0-meta-B', 101)
    st['zB'] = list(gB)
    st['z0'] = list(g0)
    st['meta_B'] = dict(z1_rows=rowsB, z0_rows=rows0)
    st['meter']['B_z1'] = m1
    st['meter']['B_z0'] = m0
    st['phase'] = 'B'
    save_state(st)
    print('[B] zB=%s z0=%s meter z1=%d z0=%d' % (gB, g0, m1, m0))


def phase_C():
    st = load_state()
    tasks = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    t2 = tasks_by(tasks, 'DEV', 2)
    res = run_block(t2, st, st['zB'], 'hist', SEEDS, BUDGET)
    hoard = A.Hoard.load(st['hoard'])
    hist = A.History.load(st['history'])
    for r in res:
        if r['solved']:
            hist.merge(A.History.load(r['hist']))
            retain_from(r, hoard)
    hoard.freeze()
    st['hoard'] = hoard.dump()
    st['history'] = hist.dump()
    st['meter']['C'] = sum(r['calls'] for r in res)
    ns = sum(r['solved'] for r in res)
    st['log']['C'] = dict(episodes=len(res), solves=ns)
    st['phase'] = 'C'
    save_state(st)
    print('[C] dev tier2: %d/%d episodes solved  hoard=%d  recur_keys=%d'
          % (ns, len(res), hoard.n, len(hist.recur)))


def phase_D():
    st = load_state()
    tasks = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    disc = tasks_by(tasks, 'DEV', 2)[6:10] + tasks_by(tasks, 'DEV', 3)[:6]
    gD, rowsD, m1 = meta_search(st, disc, 'hist', 'Z1-meta-D', 202)
    # revision rule: keep zB unless zD strictly beats it on the same block
    resB = run_block(disc, st, st['zB'], 'hist', META_SEEDS, META_BUDGET)
    m1 += sum(r['calls'] for r in resB)
    sB = sum(r['solved'] for r in resB)
    sD = max(r['solves'] for r in rowsD)
    st['zstar'] = list(gD) if sD > sB else st['zB']
    st['meta_D'] = dict(rows=rowsD, zB_score=sB, zD_score=sD)
    st['meter']['D'] = m1
    st['phase'] = 'D'
    save_state(st)
    print('[D] zB=%s score=%d | zD best=%d -> zstar=%s' % (st['zB'], sB, sD, st['zstar']))


def phase_E():
    st = load_state()
    tasks = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    t3 = tasks_by(tasks, 'DEV', 3)
    res = run_block(t3, st, st['zstar'], 'hist', SEEDS, BUDGET)
    hoard = A.Hoard.load(st['hoard'])
    hist = A.History.load(st['history'])
    for r in res:
        if r['solved']:
            hist.merge(A.History.load(r['hist']))
            retain_from(r, hoard)
    hoard.freeze()
    st['hoard'] = hoard.dump()
    st['history'] = hist.dump()
    st['meter']['E'] = sum(r['calls'] for r in res)
    ns = sum(r['solved'] for r in res)
    st['log']['E'] = dict(episodes=len(res), solves=ns)
    st['phase'] = 'E-FROZEN'
    save_state(st)
    print('[E] dev tier3: %d/%d episodes solved  final hoard=%d  recur_keys=%d  FROZEN'
          % (ns, len(res), hoard.n, len(hist.recur)))
    print('[meter] %s' % st['meter'])


if __name__ == '__main__':
    {'A': phase_A, 'B': phase_B, 'C': phase_C, 'D': phase_D, 'E': phase_E}[sys.argv[1]]()
