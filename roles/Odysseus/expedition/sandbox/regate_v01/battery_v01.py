"""[regate_v01 COPY of ../battery.py: imports world_v01; adds arms T, P_cb, CAL,
P_cal, DECOY; adds history_twin (H_hist), e0_stat (E0) and decide_v01 (A8
repair). Original functions and statistics are unchanged.]
Accumulation battery (ACCUMULATION_v0 rungs R0-R5) as interventions on saved
world state. Stdlib only. Evaluator side: may read anything in the state
(hidden s, provenance); nothing here is ever passed to an organism -- probes
only edit the physical record / population and then call world.step().
"""
import random
from collections import Counter, defaultdict

import world_v01 as W

DELTA = 0.05
EVAL_SEEDS = list(range(16))
AA_SEEDS = list(range(100, 116))
WIN_SEEDS = list(range(4))
T_PERSIST = 5
F_ABLATE = 30
N_SNAPS = 20
SNAP_EVERY = 10
WINDOW = 40
RECOMPUTE_B_LITERAL = 24


# ------------------------------------------------------------ arms

def arm_config(arm, seed):
    """-> (params, genomes, sigma, generations)."""
    rs = random.Random(seed * 31 + 5)
    sig = list(range(4))
    rs.shuffle(sig)
    ident = list(range(4))
    if arm in ('T', 'P_cb', 'DECOY'):
        kind = {'T': 'T', 'P_cb': 'P', 'DECOY': 'DECOY'}[arm]
        return {'planted': True, 'biased_colony': True}, W.planted_genomes(kind), ident, 300
    if arm in ('CAL', 'P_cal'):
        prm = {'planted': True, 'calendar': True}
        if arm == 'CAL':
            sched = tuple(tuple(tuple(x) for x in W.planted_genomes('CAL_phase%d' % ph)) for ph in range(4))
            prm['schedule'] = sched
            return prm, [list(x) for x in sched[W.epoch(0) % 4]], ident, 300
        return prm, W.planted_genomes('P'), ident, 300
    if arm in ('P', 'P4', 'N_a', 'N_b', 'C', 'P_sigma'):
        kind = 'P' if arm == 'P_sigma' else arm
        prm = {'planted': True, 'biased': arm == 'C'}
        return prm, W.planted_genomes(kind), (sig if arm == 'P_sigma' else ident), 300
    gens = GENS_UNPLANTED
    if arm == 'U_sigma':
        return {}, None, sig, gens
    if arm == 'U_id':
        return {}, None, ident, gens
    if arm == 'U_frozen':
        return {'frozen_reader': True}, None, sig, gens
    if arm == 'U_unread':
        return {'record_mode': 'unreadable'}, None, sig, gens
    if arm == 'U_norec':
        return {'record_mode': 'none'}, None, sig, gens
    raise ValueError(arm)


GENS_UNPLANTED = 3000


def evolve(arm, seed):
    prm, genomes, sigma, gens = arm_config(arm, seed)
    st = W.new_world(seed, prm, genomes, sigma)
    snaps = {}
    first = gens - (N_SNAPS * SNAP_EVERY + F_ABLATE + 50)
    traj = W.run(st, gens, snap_every=SNAP_EVERY, snap_from=first, snaps=snaps)
    return st, snaps, traj


# ------------------------------------------------------------ interventions

def apply_intervention(st, kind, rng, snaps=None):
    p = st['p']
    G, K, A = p['G'], p['K'], p['A']
    rec = st['record']
    if kind == 'intact':
        pass
    elif kind == 'deleted':
        st['record'] = [[W.BLANK] * K for _ in range(G)]
    elif kind == 'del_c0':
        for g in range(G):
            rec[g][0] = W.BLANK
    elif kind == 'del_c1':
        for g in range(G):
            rec[g][1] = W.BLANK
    elif kind == 'norecord':
        p['record_mode'] = 'none'
    elif kind == 'unreadable':
        p['record_mode'] = 'unreadable'
    elif kind == 'perm':
        st['record'] = [list(rec[(g + 1) % G]) for g in range(G)]
    elif kind == 'rand':
        st['record'] = [[W.BLANK if c == W.BLANK else rng.randrange(A) for c in rec[g]] for g in range(G)]
    elif kind == 'inject':
        n = 0
        for g in range(G):
            for c in range(K):
                if st['ev']['last_write'][g][c] < st['gen'] - 20:
                    rec[g][c] = rng.randrange(A)
                    n += 1
        return n
    elif kind == 'episode':
        old = snaps[st['gen'] - 50]
        st['record'] = [list(r) for r in old['record']]
    else:
        raise ValueError(kind)
    return None


def world_salt(state):
    """Evaluator-side per-world salt for eval seeds (AMENDMENTS A1): eval noise
    must be independent across worlds, or the world-level bootstrap is invalid."""
    return state['rng_phys'].getstate()[1][0] % 1_000_003


def s1(state, kind='intact', receivers='own', seeds=EVAL_SEEDS, snaps=None):
    """Mean success of the first consumer generation after the intervention."""
    vals = []
    salt = world_salt(state) * 1000
    n_inject = None
    for sd in seeds:
        st = W.restore(state)
        if receivers == 'novel':
            G = st['p']['G']
            st['colonies'] = [[list(o) for o in state['colonies'][(g + 1) % G]] for g in range(G)]
        # producer-destroyed / receiver-never-wrote assertion
        # uids are assigned at birth, increasing; a receiver born after the
        # last write into this nest cannot have written it
        for g, col in enumerate(st['colonies']):
            mw = st['ev']['max_writer_uid'][g]
            assert all(o[2] > mw for o in col), 'receiver wrote the record it consumes'
        st['rng_bio'] = random.Random(salt + 10_000 + sd)
        r = apply_intervention(st, kind, random.Random(salt + 20_000 + sd), snaps)
        if kind == 'inject':
            n_inject = r
        succ = W.step(st)
        vals.append(sum(x for x in succ if x is not None) / len([x for x in succ if x is not None]))
    m = sum(vals) / len(vals)
    if kind == 'inject':
        return m, n_inject
    return m


def decode_acc(pairs):
    """Leave-one-out majority map record-tuple -> s."""
    if len(pairs) < 2:
        return 0.0
    by = defaultdict(Counter)
    glob = Counter()
    for r, s in pairs:
        by[r][s] += 1
        glob[s] += 1
    ok = 0
    for r, s in pairs:
        c = Counter(by[r])
        c[s] -= 1
        if sum(c.values()) > 0:
            pred = max(sorted(c), key=lambda k: c[k])
        else:
            gg = Counter(glob)
            gg[s] -= 1
            pred = max(sorted(gg), key=lambda k: gg[k])
        ok += (pred == s)
    return ok / len(pairs)


def _persist_pairs(st):
    """Remove producers, run T physics-only generations, return (record, s) pairs."""
    s_prod = list(st['s_last'])
    G = st['p']['G']
    st['colonies'] = [[] for _ in range(G)]
    for _ in range(T_PERSIST):
        W.step(st)
    return [(tuple(st['record'][g]), s_prod[g]) for g in range(G)]


def r0_stat(state, snaps):
    gens = sorted(t for t in snaps if t <= state['gen'])[-N_SNAPS:]
    intact, ablated = [], []
    for t in gens:
        intact += _persist_pairs(W.restore(snaps[t]))
        tw = W.restore(snaps[t - F_ABLATE])
        tw['writes_suppressed'] = True
        W.run(tw, F_ABLATE)
        assert tw['gen'] == t and tw['s_last'] == snaps[t]['s_last'], 'ablated twin lost the event stream'
        tw['writes_suppressed'] = False
        ablated += _persist_pairs(tw)
    a, b = decode_acc(intact), decode_acc(ablated)
    return a - b, a, b


def window(state, kind, seeds=WIN_SEEDS):
    """Dynamics continue for WINDOW generations; intervention re-applied
    before every generation. -> (ceiling, speed)."""
    ceil, rec_times = [], []
    salt = world_salt(state) * 1000
    for sd in seeds:
        st = W.restore(state)
        st['rng_bio'] = random.Random(salt + 30_000 + sd)
        st['rng_phys'] = random.Random(salt + 40_000 + sd)
        rng = random.Random(salt + 50_000 + sd)
        G = st['p']['G']
        per = [[] for _ in range(G)]
        ss = [[] for _ in range(G)]
        for t in range(WINDOW):
            if kind != 'intact':
                apply_intervention(st, kind, rng)
            for g in range(G):
                ss[g].append(st['s'][g])
            succ = W.step(st)
            for g in range(G):
                per[g].append(succ[g])
        for g in range(G):
            ceil.append(sum(per[g][WINDOW // 2:]) / (WINDOW - WINDOW // 2))
            for k in range(1, WINDOW):
                if ss[g][k] != ss[g][k - 1]:
                    j = 0
                    while k + j < WINDOW and per[g][k + j] < 0.5 and j < 10:
                        j += 1
                    rec_times.append(min(j, 10))
    speed = sum(rec_times) / len(rec_times) if rec_times else None
    return sum(ceil) / len(ceil), speed


def provenance_J(state):
    G = state['p']['G']
    f0, f1 = set(), set()
    for g in range(G):
        f0 |= {w[1] for w in state['ev']['wlog'][g][0]}
        f1 |= {w[1] for w in state['ev']['wlog'][g][1]}
    if not f0 or not f1:
        return 1.0
    return len(f0 & f1) / len(f0 | f1)


def founder_overlap(state):
    G = state['p']['G']
    vals = []
    for g in range(G):
        a = {o[1] for o in state['colonies'][g]}
        b = {o[1] for o in state['colonies'][(g + 1) % G]}
        vals.append(len(a & b) / len(a | b) if a | b else 0.0)
    return sum(vals) / len(vals)


# ------------------------------------------------------------ regate_v01 additions

def history_twin(state, snaps, n_alt=4, back=30):
    """DIFFERENT-HISTORY twin (A8; coldstart_A-001 history_twin, unchanged
    logic, plus per-cell diagnostics). Restore the snapshot `back` gens before
    S*, rerun to S* under (i) a different physics stream and (ii) the same
    physics stream with different organism coins. Mismatch rate vs the S*
    record over cells written in the last 20 gens, (i) - (ii)."""
    t0 = state['gen'] - back
    old = snaps[t0]
    G, K = state['p']['G'], state['p']['K']
    cells = [(g, c) for g in range(G) for c in range(K)
             if state['ev']['last_write'][g][c] >= state['gen'] - 20]
    if not cells:
        return None
    salt = world_salt(state) * 1000
    mis = {'alt': [0.0] * len(cells), 'same': [0.0] * len(cells)}
    for kind in ('alt', 'same'):
        for k in range(n_alt):
            tw = W.restore(old)
            if kind == 'alt':
                tw['rng_phys'] = random.Random(salt + 70_000 + k)
            else:
                tw['rng_bio'] = random.Random(salt + 80_000 + k)
            W.run(tw, back)
            for j, (g, c) in enumerate(cells):
                mis[kind][j] += (tw['record'][g][c] != state['record'][g][c]) / n_alt
    alt = sum(mis['alt']) / len(cells)
    same = sum(mis['same']) / len(cells)
    per_cell = {}
    for c in range(K):
        js = [j for j, (g, cc) in enumerate(cells) if cc == c]
        if js:
            per_cell[c] = sum(mis['alt'][j] - mis['same'][j] for j in js) / len(js)
    return {'H_hist': alt - same, 'H_alt': alt, 'H_same': same,
            'H_cell0': per_cell.get(0), 'H_cell1': per_cell.get(1), 'H_ncells': len(cells)}


def e0_stat(state, snaps, lag=50):
    """Episode test at R0's own readout: the D0 decoder on (record from t-lag,
    persisted T gens from t, producing s at t) vs intact."""
    gens = sorted(t for t in snaps if t <= state['gen'])[-N_SNAPS:]
    intact, epi = [], []
    for t in gens:
        intact += _persist_pairs(W.restore(snaps[t]))
        st = W.restore(snaps[t])
        st['record'] = [list(r) for r in snaps[t - lag]['record']]
        epi += _persist_pairs(st)
    a, b = decode_acc(intact), decode_acc(epi)
    return a - b, a, b


def battery_world(arm, seed):
    """regate_v01: original per-world probes (unchanged values) + H_hist, E0."""
    st, snaps, traj = evolve(arm, seed)
    out, st = _battery_world_orig(arm, seed, (st, snaps, traj))
    if st['p']['record_mode'] == 'normal':
        h = history_twin(st, snaps)
        if h is None:
            out.update(H_hist=None)
        else:
            out.update(h)
        e0, ea, eb = e0_stat(st, snaps)
        out.update(E0=e0, e0_acc_intact=ea, e0_acc_episode=eb)
    return out, st


def _battery_world_orig(arm, seed, evolved=None):
    """Evolve one world and run every per-world probe. Returns (stats, final_state)."""
    st, snaps, traj = evolved if evolved is not None else evolve(arm, seed)
    out = {'arm': arm, 'seed': seed, 'gen': st['gen']}
    last = traj[-100:]
    out['evo_success_last100'] = sum(sum(x for x in r if x is not None) / len(r) for r in last) / len(last)
    mode = st['p']['record_mode']
    if mode == 'normal':
        d0, a, b = r0_stat(st, snaps)
        out.update(D0=d0, acc_intact=a, acc_ablated=b)
        S = {}
        for k in ('intact', 'deleted', 'norecord', 'unreadable', 'perm', 'rand', 'episode', 'del_c0', 'del_c1'):
            S[k] = s1(st, k, snaps=snaps)
        S['inject'], n_inj = s1(st, 'inject', snaps=snaps)
        S['aa'] = s1(st, 'intact', seeds=AA_SEEDS)
        for k in ('intact', 'deleted', 'norecord', 'unreadable'):
            S['novel_' + k] = s1(st, k, receivers='novel')
        out['S1'] = S
        out['D1'] = S['intact'] - S['deleted']
        out['D2'] = S['novel_intact'] - max(S['novel_deleted'], S['novel_norecord'], S['novel_unreadable'])
        out['Dp'] = S['intact'] - S['perm']
        out['Dr'] = S['intact'] - S['rand']
        out['Di'] = (S['intact'] - S['inject']) if n_inj else None
        out['n_inject_cells'] = n_inj
        out['D_episode'] = S['intact'] - S['episode']
        out['D_AA'] = S['intact'] - S['aa']
        out['I'] = S['intact'] - S['del_c1'] - S['del_c0'] + S['deleted']
        out['Dx'] = S['intact'] - max(S['del_c1'], S['del_c0'])
        out['J'] = provenance_J(st)
        out['founder_overlap_novel'] = founder_overlap(st)
        ci, si = window(st, 'intact')
        cd, sd_ = window(st, 'deleted')
        cn, sn = window(st, 'norecord')
        out['window'] = {'ceil_intact': ci, 'speed_intact': si, 'ceil_deleted': cd, 'speed_deleted': sd_,
                         'ceil_norecord': cn, 'speed_norecord': sn}
        # genome census (diagnostic)
        pop = [o[0] for col in st['colonies'] for o in col]
        out['frac_readers'] = sum(g[W.G_READ] for g in pop) / len(pop)
    else:
        ci, si = window(st, 'intact')
        out['window'] = {'ceil_intact': ci, 'speed_intact': si}
    return out, st


def fresh_world_transfer(state_a, state_b, seeds=EVAL_SEEDS):
    """Record of world a inserted into world b (b's s set equal to a's), vs b
    with that record deleted. Receivers are b's own population."""
    vals_t, vals_d = [], []
    salt = world_salt(state_b) * 1000
    for sd in seeds:
        for kind in ('t', 'd'):
            st = W.restore(state_b)
            st['s'] = list(state_a['s'])
            st['record'] = [list(r) for r in state_a['record']] if kind == 't' else \
                [[W.BLANK] * st['p']['K'] for _ in range(st['p']['G'])]
            st['rng_bio'] = random.Random(salt + 60_000 + sd)
            succ = W.step(st)
            m = sum(succ) / len(succ)
            (vals_t if kind == 't' else vals_d).append(m)
    return sum(vals_t) / len(vals_t) - sum(vals_d) / len(vals_d)


# ------------------------------------------------------------ aggregation / decisions

def boot_ci(xs, n=2000, seed=12345):
    rng = random.Random(seed)
    m = len(xs)
    means = sorted(sum(rng.choice(xs) for _ in range(m)) / m for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def summ(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    lo, hi = boot_ci(xs)
    return {'mean': sum(xs) / len(xs), 'lo': lo, 'hi': hi, 'n': len(xs)}


def PASS(s):
    return s is not None and s['mean'] >= DELTA and s['lo'] > 0


def EQUIV(s):
    return s is not None and abs(s['mean']) < DELTA and s['lo'] > -2 * DELTA and s['hi'] < 2 * DELTA


def decide(worlds, pristine_ceiling=None):
    """worlds: list of per-world dicts of one arm (record_mode normal)."""
    T = {k: summ([w[k] for w in worlds]) for k in
         ('D0', 'D1', 'D2', 'Dp', 'Dr', 'Di', 'D_episode', 'D_AA', 'I', 'Dx', 'J', 'D_fw')
         if any(k in w for w in worlds)}
    ci = summ([w['window']['ceil_intact'] for w in worlds])
    cn = summ([w['window']['ceil_norecord'] for w in worlds])
    cd = summ([w['window']['ceil_deleted'] for w in worlds])
    tests = {}
    tests['R0'] = PASS(T['D0'])
    tests['R1'] = PASS(T['D1'])
    tests['R2'] = PASS(T['D2'])
    di_ok = True if T.get('Di') is None else EQUIV(T['Di'])
    d1m = T['D1']['mean']
    tests['R3_perm'] = PASS(T['Dp']) and T['Dp']['mean'] >= 0.5 * d1m
    tests['R3_rand'] = PASS(T['Dr']) and T['Dr']['mean'] >= 0.5 * d1m
    tests['R3_inject_equiv'] = di_ok
    tests['R3'] = tests['R3_perm'] and tests['R3_rand'] and di_ok
    tests['R4'] = PASS(T['I']) and PASS(T['Dx']) and T['J']['mean'] <= 0.2
    cstar = ci['mean'] - 0.05
    rec_lit = min(1.0, (RECOMPUTE_B_LITERAL + 1) / 4)
    rec_pc = min(1.0, (1 + 1) / 4)
    r5a = cn['mean'] < cstar - DELTA
    r5b = rec_lit < cstar - DELTA
    pc = pristine_ceiling if pristine_ceiling is not None else cn['mean']
    r5c = pc < cstar - DELTA
    tests['R5_a'], tests['R5_b_literal'], tests['R5_c'] = r5a, r5b, r5c
    tests['R5_b_perconsumer_diag'] = rec_pc < cstar - DELTA
    tests['R5'] = r5a and r5b and r5c
    ladder = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']
    highest = None
    for r in ladder:
        if tests[r]:
            highest = r
        else:
            break
    aa_ok = T['D_AA']['lo'] <= 0 <= T['D_AA']['hi']
    speed = {k: summ([w['window'][k] for w in worlds]) for k in ('speed_intact', 'speed_deleted', 'speed_norecord')}
    return {'tests': tests, 'highest': highest, 'stats': T, 'aa_valid': aa_ok,
            'ceiling': {'intact': ci, 'deleted': cd, 'norecord': cn, 'cstar': cstar,
                        'recompute_literal': rec_lit, 'recompute_perconsumer': rec_pc,
                        'pristine': pc},
            'speed': speed,
            'n_worlds_D1_gt_delta': sum(1 for w in worlds if w['D1'] > DELTA)}


def convention(dec_id, dec_sigma):
    a, b = dec_id['stats']['D1'], dec_sigma['stats']['D1']
    inv = PASS(a) and PASS(b) and abs(a['mean'] - b['mean']) < DELTA
    return {'qualifier': 'INVARIANT' if inv else 'INSTALLED',
            'benefit_present_id': PASS(a), 'benefit_present_sigma': PASS(b),
            'D1_id': a['mean'], 'D1_sigma': b['mean']}


# ------------------------------------------------------------ regate_v01 decision rules (PREREG s2)

def decide_v01(worlds, pristine_ceiling=None):
    d = decide(worlds, pristine_ceiling)
    T, t = d['stats'], dict(d['tests'])
    for k in ('H_hist', 'E0', 'H_cell0', 'H_cell1'):
        T[k] = summ([w.get(k) for w in worlds])
    d1m = T['D1']['mean']
    t['orig_R0'] = t['R0']
    t['orig_R3'] = t['R3']
    t['H_hist'] = PASS(T['H_hist'])
    t['E0'] = PASS(T['E0'])
    t['D_episode'] = PASS(T['D_episode']) and T['D_episode']['mean'] >= 0.5 * d1m
    t['R0'] = t['orig_R0'] and t['H_hist'] and t['E0']
    t['R0_literal_consumer_sens'] = t['orig_R0'] and t['H_hist'] and PASS(T['D_episode'])
    t['R3'] = t['orig_R3'] and t['H_hist'] and t['D_episode']
    ladder = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']
    highest = None
    for r in ladder:
        if t[r]:
            highest = r
        else:
            break
    d['tests'] = t
    d['highest'] = highest
    d['highest_orig_rules'] = decide(worlds, pristine_ceiling)['highest']
    d['A3_independent'] = {r: t[r] for r in ladder}
    return d


def convention3(dec_id, dec_sigma):
    """A2 3-way label (reported)."""
    a, b = dec_id['stats']['D1'], dec_sigma['stats']['D1']
    if not PASS(a) and not PASS(b):
        return 'NO-BENEFIT'
    if PASS(a) and PASS(b) and abs(a['mean'] - b['mean']) < DELTA:
        return 'INVARIANT'
    return 'INSTALLED'
