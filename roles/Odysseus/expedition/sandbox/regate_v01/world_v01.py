"""[regate_v01 COPY of ../world.py: adds colony-biased and calendar physics,
planted genome schedules and planted kinds T, DECOY, CAL. Additions only.]
Endogenous world-record sandbox: the world (physics + organisms). Stdlib only.

Layout of responsibility (the forbidden-information guarantee, DESIGN.md s4):
  * organism_choose / organism_write are the ONLY code that decides organism
    behaviour. They are pure functions of (genome, local observation, physical
    coin draws). They receive no world object, no seed, no id, no label, no
    evaluator state, no hidden environment variable and nothing about the
    future. tests/test_mechanics.py checks their code objects reference only
    their arguments and a whitelist of constants.
  * step() is the physics. It builds each observation from the organism's own
    nest record (the physical cells), and nothing else.
  * everything under state['ev'] is evaluator-side bookkeeping (provenance,
    individual ids). step() writes it but never reads it into an observation.

State is a plain dict; snapshot()/restore() deep-copy it including both RNG
states, so every probe is an exact replay.
"""
import copy
import random

BLANK = -1
EXPLORE_LEVELS = (0.0, 0.05, 0.2, 0.5)

# genome layout (flat tuple of ints)
G_READ = 0            # 0/1
G_EXPL = 1            # index into EXPLORE_LEVELS
G_CHOOSE = 2          # (A+1)^K entries -> site
# followed by: waddr, write table (S*2 entries -> 0 noop, 1 erase, 2+a write symbol a)

DEFAULTS = dict(
    S=4, G=4, N=24, K=2, A=4,
    base=0.10, reward=1.00, c_read=0.02, c_write=0.05,
    eps=0.01, p_switch=0.10, biased=False,
    mig=0.02, mu=0.02, group_every=20,
    planted=False,        # clonal replacement, no mutation, no selection
    record_mode='normal', # 'normal' | 'unreadable' | 'none'
    frozen_reader=False,  # reader genes never mutate (U_frozen)
)


def layout(p):
    nchoose = (p['A'] + 1) ** p['K']
    i_waddr = G_CHOOSE + nchoose
    i_write = i_waddr + 1
    length = i_write + p['S'] * 2
    ranges = [2, len(EXPLORE_LEVELS)] + [p['S']] * nchoose + [p['K']] + [p['A'] + 2] * (p['S'] * 2)
    return nchoose, i_waddr, i_write, length, ranges


def obs_index(obs, A):
    """Record tuple (symbols or BLANK) -> choose-table index."""
    idx = 0
    for c in obs:
        idx = idx * (A + 1) + (c + 1)
    return idx


# ---------------------------------------------------------------- organisms
# These two functions are the whole organism. Arguments are everything an
# organism can know. Do not add arguments without updating DESIGN.md s4.

def organism_choose(genome, obs_idx, coin, rand_site):
    """-> (site, read_flag). obs_idx: index of the locally read record tuple
    (all-BLANK if the organism does not read or reads return nothing).
    coin, rand_site: physical noise drawn by the world for this organism."""
    if coin < EXPLORE_LEVELS[genome[1]]:
        return rand_site
    return genome[2 + obs_idx]


def organism_write(genome, i_write, site, found):
    """-> (action, address). action 0 noop, 1 erase, 2+a write symbol a.
    i_write is a genome-layout constant, not information about the world."""
    return genome[i_write + site * 2 + (1 if found else 0)], genome[i_write - 1]


# ---------------------------------------------------------------- world

def new_world(seed, params=None, genomes=None, sigma=None):
    """genomes: optional list (len G) of lists (len N) of genome tuples.
    None -> uniformly random genomes (unplanted)."""
    p = dict(DEFAULTS)
    if params:
        p.update(params)
    nchoose, i_waddr, i_write, length, ranges = layout(p)
    rng_init = random.Random(seed * 7919 + 1)
    st = {
        'p': p, 'gen': 0,
        'rng_phys': random.Random(seed * 7919 + 2),
        'rng_bio': random.Random(seed * 7919 + 3),
        'record': [[BLANK] * p['K'] for _ in range(p['G'])],
        's': [rng_init.randrange(p['S']) for _ in range(p['G'])],
        's_last': None,
        'sigma': list(sigma) if sigma is not None else list(range(p['A'])),
        'writes_suppressed': False,
        'colonies': [],
        'energy_acc': [0.0] * p['G'],
        'ev': {'next_uid': 0, 'wlog': [[[] for _ in range(p['K'])] for _ in range(p['G'])],
               'last_write': [[-10**9] * p['K'] for _ in range(p['G'])],
               'max_writer_uid': [-1] * p['G']},
    }
    if p['frozen_reader'] and genomes is None:
        shared = [rng_init.randrange(r) for r in ranges[:G_CHOOSE + nchoose]]
    for g in range(p['G']):
        col = []
        for i in range(p['N']):
            if genomes is not None:
                gen_t = tuple(genomes[g][i])
            else:
                gen_t = [rng_init.randrange(r) for r in ranges]
                if p['frozen_reader']:
                    gen_t[:G_CHOOSE + nchoose] = shared
                gen_t = tuple(gen_t)
            uid = st['ev']['next_uid']
            st['ev']['next_uid'] += 1
            col.append([gen_t, uid, uid])   # genome, founder id, individual id
        st['colonies'].append(col)
    return st


def _rng_copy(r):
    n = random.Random()
    n.setstate(r.getstate())
    return n


def snapshot(st):
    """Exact structural copy (genomes and log entries are immutable tuples)."""
    new = dict(st)
    new['p'] = dict(st['p'])
    new['rng_phys'] = _rng_copy(st['rng_phys'])
    new['rng_bio'] = _rng_copy(st['rng_bio'])
    new['record'] = [list(r) for r in st['record']]
    new['s'] = list(st['s'])
    new['s_last'] = None if st['s_last'] is None else list(st['s_last'])
    new['sigma'] = list(st['sigma'])
    new['colonies'] = [[list(o) for o in col] for col in st['colonies']]
    new['energy_acc'] = list(st['energy_acc'])
    ev = st['ev']
    new['ev'] = {'next_uid': ev['next_uid'],
                 'wlog': [[list(c) for c in g] for g in ev['wlog']],
                 'last_write': [list(x) for x in ev['last_write']],
                 'max_writer_uid': list(ev['max_writer_uid'])}
    for k, v in st.items():
        if k not in new or new[k] is v and isinstance(v, (list, dict, set)):
            new[k] = copy.deepcopy(v)
    return new


restore = snapshot


def _mutate(genome, ranges, mu, rng, lo):
    g = None
    for j in range(lo, len(genome)):
        if rng.random() < mu:
            if g is None:
                g = list(genome)
            g[j] = rng.randrange(ranges[j])
    return genome if g is None else tuple(g)


def step(st):
    """One generation. Returns per-colony foraging success rates (None for an
    empty colony)."""
    p = st['p']
    S, G, K, A = p['S'], p['G'], p['K'], p['A']
    nchoose, i_waddr, i_write, length, ranges = layout(p)
    rb, rp = st['rng_bio'], st['rng_phys']
    ev = st['ev']
    mode = p['record_mode']
    blank_idx = obs_index((BLANK,) * K, A)
    sigma = st['sigma']
    succ = []
    energies = []
    for g in range(G):
        col = st['colonies'][g]
        rec = st['record'][g]
        if not col:
            succ.append(None)
            energies.append([])
            continue
        # all reads see the record as the previous (dead) generation left it
        phys_idx = obs_index(rec, A) if mode == 'normal' else blank_idx
        sg = st['s'][g]
        en = []
        nfound = 0
        writes = []
        for org in col:
            genome = org[0]
            cost = 0.0
            if genome[G_READ] and mode != 'none':
                oi = phys_idx
                cost += p['c_read'] * K
            else:
                oi = blank_idx
            coin = rb.random()
            rs = rb.randrange(S)
            site = organism_choose(genome, oi, coin, rs)
            found = (site == sg)
            if found:
                nfound += 1
            act, addr = organism_write(genome, i_write, site, found)
            if act:
                if mode != 'none':
                    cost += p['c_write']
                writes.append((act, addr, org))
            en.append(p['base'] + (p['reward'] if found else 0.0) - cost)
        rb.shuffle(writes)
        if mode != 'none' and not st['writes_suppressed']:
            for act, addr, org in writes:
                rec[addr] = BLANK if act == 1 else sigma[act - 2]
                ev['wlog'][g][addr].append((st['gen'], org[1], org[2]))
                ev['last_write'][g][addr] = st['gen']
                if org[2] > ev['max_writer_uid'][g]:
                    ev['max_writer_uid'][g] = org[2]
        succ.append(nfound / len(col))
        energies.append(en)
    # physics: noise, then environment redraw (fixed number of draws per gen,
    # independent of organisms, so twin/probe arms share the event stream)
    for g in range(G):
        for c in range(K):
            u = rp.random()
            v = rp.randrange(A + 1) - 1
            if u < p['eps']:
                st['record'][g][c] = v
    st['s_last'] = list(st['s'])
    for g in range(G):
        u = rp.random()
        r = rp.randrange(S - 1)
        b = rp.random()
        if u < p['p_switch']:
            if p['biased']:
                st['s'][g] = 0 if b < 0.7 else 1 + r
            elif p.get('biased_colony'):
                # coldstart_A-001 physics: colony g favours site g (same draws)
                st['s'][g] = g if b < 0.7 else (r if r < g else r + 1)
            elif p.get('calendar'):
                # regate_v01 CAL physics: colony g favours (g + epoch) mod S,
                # epoch of the generation the new s serves (same draws)
                f = (g + epoch(st['gen'] + 1)) % S
                st['s'][g] = f if b < 0.7 else (r if r < f else r + 1)
            else:
                st['s'][g] = r if r < st['s'][g] else r + 1
    # reproduction
    if any(st['colonies']):
        _reproduce(st, energies, ranges, nchoose)
    # trim provenance log to last 100 generations
    lim = st['gen'] - 100
    for g in range(G):
        for c in range(K):
            wl = ev['wlog'][g][c]
            if wl and wl[0][0] < lim:
                ev['wlog'][g][c] = [w for w in wl if w[0] >= lim]
    st['gen'] += 1
    return succ


EPOCH_LEN = 50
EPOCH_OFFSET = 25


def epoch(t):
    """regate_v01 calendar epoch (physics/experimenter side only)."""
    return (t + EPOCH_OFFSET) // EPOCH_LEN


def _reproduce(st, energies, ranges, nchoose):
    p = st['p']
    G, N = p['G'], p['N']
    ev = st['ev']
    rb = st['rng_bio']
    cols = st['colonies']
    for g in range(G):
        if energies[g]:
            st['energy_acc'][g] += sum(energies[g]) / len(energies[g])
    if p['planted'] and p.get('schedule'):
        # regate_v01: clonal genome SCHEDULE keyed by the clock (a cheat's
        # installed machinery; organisms still see nothing but their record)
        sch = p['schedule']
        ph = sch[epoch(st['gen'] + 1) % len(sch)]
        new = [[[ph[g][i], o[1], 0] for i, o in enumerate(col)] for g, col in enumerate(cols)]
    elif p['planted']:
        new = [[[o[0], o[1], 0] for o in col] for col in cols]
    else:
        cum = []
        for g in range(G):
            acc, c = 0.0, []
            for e in energies[g]:
                acc += max(e, 0.01)
                c.append(acc)
            cum.append(c)
        lo = (G_CHOOSE + nchoose) if p['frozen_reader'] else 0
        new = []
        for g in range(G):
            col = []
            for i in range(N):
                h = g
                if rb.random() < p['mig']:
                    h = rb.randrange(G - 1)
                    h = h if h < g else h + 1
                if not cols[h]:
                    h = g
                par = rb.choices(cols[h], cum_weights=cum[h])[0]
                col.append([_mutate(par[0], ranges, p['mu'], rb, lo), par[1], 0])
            new.append(col)
        if p['group_every'] and (st['gen'] + 1) % p['group_every'] == 0:
            ea = st['energy_acc']
            worst = min(range(G), key=lambda g: (ea[g], g))
            best = max(range(G), key=lambda g: (ea[g], -g))
            if worst != best:
                new[worst] = [[o[0], o[1], 0] for o in new[best]]
            st['energy_acc'] = [0.0] * G
    for col in new:
        for o in col:
            o[2] = ev['next_uid']
            ev['next_uid'] += 1
    st['colonies'] = new
    if p['planted'] and p['group_every'] and (st['gen'] + 1) % p['group_every'] == 0:
        st['energy_acc'] = [0.0] * G


def run(st, gens, snap_every=None, snap_from=None, snaps=None):
    out = []
    for _ in range(gens):
        if snaps is not None and snap_every and st['gen'] >= snap_from and st['gen'] % snap_every == 0:
            snaps[st['gen']] = snapshot(st)
        out.append(step(st))
    if snaps is not None and snap_every and st['gen'] % snap_every == 0:
        snaps[st['gen']] = snapshot(st)
    return out


# ---------------------------------------------------------------- plants
# Planted genomes are ordinary genomes in the same genome space: the plant is
# content (table entries), never extra machinery.

def _blank_genome(p):
    nchoose, i_waddr, i_write, length, ranges = layout(p)
    return [0] * length, nchoose, i_waddr, i_write


def planted_genomes(kind, p=None):
    q = dict(DEFAULTS)
    if p:
        q.update(p)
    S, A, K, G, N = q['S'], q['A'], q['K'], q['G'], q['N']
    assert S == 4 and A == 4 and K == 2
    g0, nchoose, i_waddr, i_write = _blank_genome(q)
    g0[G_READ] = 1
    g0[G_EXPL] = 2   # explore 0.2
    cells = [BLANK] + list(range(A))

    def choose_table(fn):
        t = []
        for c0 in cells:
            for c1 in cells:
                t.append(fn(c0, c1))
        return t

    def writer_P(gg):
        gg[i_waddr] = 0
        for site in range(S):
            gg[i_write + site * 2 + 0] = 0          # fail -> noop
            gg[i_write + site * 2 + 1] = 2 + site   # found -> write enc(site)=site
        return gg

    def with_choose(gg, fn):
        gg[G_CHOOSE:G_CHOOSE + nchoose] = choose_table(fn)
        return tuple(gg)

    decode_P = lambda c0, c1: c0 if c0 != BLANK else 0
    if kind == 'P':
        one = with_choose(writer_P(list(g0)), decode_P)
        return [[one] * N for _ in range(G)]
    if kind == 'N_a':
        one = with_choose(writer_P(list(g0)), lambda c0, c1: 0)
        return [[one] * N for _ in range(G)]
    if kind == 'C':
        one = with_choose(writer_P(list(g0)), lambda c0, c1: 0 if c0 != BLANK else 1)
        return [[one] * N for _ in range(G)]
    if kind == 'N_b':
        pop = []
        for i in range(N):
            gg = list(g0)
            gg[i_waddr] = 0
            for j in range(S * 2):
                gg[i_write + j] = 2 + (i % A)   # constant symbol, ignores site/found
            pop.append(with_choose(gg, decode_P))
        return [list(pop) for _ in range(G)]
    if kind == 'P4':
        def dec(c0, c1):
            hi = c0 if c0 in (0, 1) else 0
            lo = c1 if c1 in (0, 1) else 0
            return 2 * hi + lo
        pop = []
        for i in range(N):
            gg = list(g0)
            caste = i % 2
            gg[i_waddr] = caste
            for site in range(S):
                bit = (site >> 1) if caste == 0 else (site & 1)
                gg[i_write + site * 2 + 0] = 0
                gg[i_write + site * 2 + 1] = 2 + bit
            pop.append(with_choose(gg, dec))
        return [list(pop) for _ in range(G)]
    if kind == 'T':
        # coldstart_A-001 NEST TAG: colony g writes constant g into cell 0
        pops = []
        for g in range(G):
            gg = list(g0)
            gg[i_waddr] = 0
            for j in range(S * 2):
                gg[i_write + j] = 2 + g
            pops.append([with_choose(gg, decode_P)] * N)
        return pops
    if kind == 'DECOY':
        # regate_v01 cheat 2: caste A (even i) writes constant nest tag g into
        # cell 0; caste B (odd i) writes the site it found into cell 1 (fail ->
        # noop). Readers decode cell 0 only.
        pops = []
        for g in range(G):
            pop = []
            for i in range(N):
                gg = list(g0)
                if i % 2 == 0:
                    gg[i_waddr] = 0
                    for j in range(S * 2):
                        gg[i_write + j] = 2 + g
                else:
                    gg[i_waddr] = 1
                    for site in range(S):
                        gg[i_write + site * 2 + 0] = 0
                        gg[i_write + site * 2 + 1] = 2 + site
                pop.append(with_choose(gg, decode_P))
            pops.append(pop)
        return pops
    if kind.startswith('CAL_phase'):
        # regate_v01 cheat 1 (one phase of the schedule): colony g writes the
        # constant symbol (g + phase) mod A into cell 0; readers decode as P
        ph = int(kind[len('CAL_phase'):])
        pops = []
        for g in range(G):
            gg = list(g0)
            gg[i_waddr] = 0
            for j in range(S * 2):
                gg[i_write + j] = 2 + (g + ph) % A
            pops.append([with_choose(gg, decode_P)] * N)
        return pops
    raise ValueError(kind)
