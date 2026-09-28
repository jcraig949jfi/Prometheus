"""coldstart_A-001 runner. Single process (host is shared). Stdlib only.

    python3 run_coldstart.py repro   -> repro_known_answer.json
        imports the ORIGINAL ../world.py, ../battery.py, ../run_battery.py
        (read-only), runs the 6 known-answer arms x seeds 1000..1019 serially,
        recomputes decide/convention/gate with the original functions and
        compares every per-world number with ../known_answer.json.
    python3 run_coldstart.py cheat   -> cheat_T.json
        imports the COPIED + extended world.py/battery.py in this directory;
        first checks the copies reproduce original per-world values for P and
        C at 3 seeds (the extension must not move anything), then runs arms
        P_cb, T, T_sigma x seeds 1000..1019 and applies the frozen decide().
"""
import json
import os
import resource
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.dirname(HERE)
SEEDS = [1000 + i for i in range(int(os.environ.get('SANDBOX_N', '20')))]


def load_known():
    with open(os.path.join(ORIG, 'known_answer.json')) as f:
        return json.load(f)


def flat(d, pre=''):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, pre + k + '.'))
        else:
            out[pre + k] = v
    return out


def compare(mine, ref, skip=('sec',)):
    """-> (n_compared, list of mismatches) over all numeric per-world keys."""
    a, b = flat(mine), flat(ref)
    n, bad = 0, []
    for k in sorted(set(a) | set(b)):
        if k.split('.')[-1] in skip:
            continue
        if k not in a or k not in b:
            bad.append((k, a.get(k), b.get(k)))
            continue
        x, y = a[k], b[k]
        n += 1
        if isinstance(x, float) or isinstance(y, float):
            if x is None or y is None or abs(x - y) > 1e-12:
                bad.append((k, x, y))
        elif x != y:
            bad.append((k, x, y))
    return n, bad


def run_arm(B, arm, seeds, extra=None):
    out, states = [], []
    for s in seeds:
        t = time.time()
        o, st = B.battery_world(arm, s)
        if extra:
            extra(o, st)
        o['sec'] = time.time() - t
        out.append(o)
        states.append(st)
        print(arm, s, round(o['sec'], 2), flush=True)
    n = len(states)
    if states[0]['p']['record_mode'] == 'normal':
        for i in range(n):
            out[i]['D_fw'] = B.fresh_world_transfer(states[i], states[(i + 1) % n])
    return out


def repro():
    sys.path.insert(0, ORIG)
    import battery as B
    import run_battery as RB
    assert os.path.dirname(os.path.abspath(B.__file__)) == ORIG
    ka = load_known()
    t0 = time.time()
    by = {a: run_arm(B, a, SEEDS) for a in RB.KNOWN}
    dec = {a: B.decide(by[a]) for a in RB.KNOWN}
    dec['convention_P'] = B.convention(dec['P'], dec['P_sigma'])
    g = RB.gate(dec)
    cmp_ = {}
    for a in RB.KNOWN:
        n, bad = 0, []
        for mine, ref in zip(by[a], ka['per_world'][a]):
            n1, b1 = compare(mine, ref)
            n += n1
            bad += [(mine['seed'],) + x for x in b1]
        cmp_[a] = {'n_values_compared': n, 'n_mismatch': len(bad), 'first_mismatches': bad[:10]}
    same_dec = {a: dec[a]['highest'] == ka['decisions'][a]['highest'] and
                dec[a]['tests'] == ka['decisions'][a]['tests'] for a in RB.KNOWN}
    out = {'gate': g, 'gate_recorded': ka['gate'], 'same_gate': g == ka['gate'],
           'same_decisions': same_dec, 'per_world_compare': cmp_,
           'highest': {a: dec[a]['highest'] for a in RB.KNOWN},
           'decisions': dec, 'per_world': by, 'wall_sec': time.time() - t0,
           'peak_rss_kb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           'python': sys.version}
    with open(os.path.join(HERE, 'repro_known_answer.json'), 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: out[k] for k in ('gate', 'same_gate', 'same_decisions', 'highest', 'wall_sec',
                                          'peak_rss_kb')}, indent=1))
    print({a: (c['n_values_compared'], c['n_mismatch']) for a, c in cmp_.items()})


def cheat():
    sys.path.insert(0, HERE)
    import battery as B
    assert os.path.dirname(os.path.abspath(B.__file__)) == HERE
    ka = load_known()
    t0 = time.time()
    # 1. the extension must not move the original arms
    ident = {}
    for a in ('P', 'C'):
        for i, s in enumerate(SEEDS[:3]):
            o, _ = B.battery_world(a, s)
            ref = dict(ka['per_world'][a][i])
            ref.pop('D_fw', None)
            n, bad = compare(o, ref)
            ident['%s_%d' % (a, s)] = {'n': n, 'mismatch': bad[:5]}
    print('identity check', {k: (v['n'], len(v['mismatch'])) for k, v in ident.items()}, flush=True)

    snaps_holder = {}

    # history-twin needs snaps: re-evolve is wasteful; wrap battery_world
    orig_evolve = B.evolve

    def evolve_keep(arm, seed):
        st, snaps, traj = orig_evolve(arm, seed)
        snaps_holder['snaps'] = snaps
        return st, snaps, traj
    B.evolve = evolve_keep

    def extra(o, st):
        h, alt, same = B.history_twin(st, snaps_holder['snaps'])
        o['H_hist'] = h
        o['H_alt'] = alt
        o['H_same'] = same

    arms = ['P_cb', 'T', 'T_sigma']
    by = {a: run_arm(B, a, SEEDS, extra) for a in arms}
    dec = {a: B.decide(by[a]) for a in arms}
    dec['convention_T'] = B.convention(dec['T'], dec['T_sigma'])
    extra_stats = {a: {k: B.summ([w.get(k) for w in by[a]]) for k in
                       ('D_episode', 'D_fw', 'H_hist', 'H_alt', 'H_same', 'acc_intact', 'acc_ablated')}
                   for a in arms}
    out = {'identity_check': ident, 'decisions': dec, 'extra_stats': extra_stats,
           'highest': {a: dec[a]['highest'] for a in arms},
           'per_world': by, 'wall_sec': time.time() - t0,
           'peak_rss_kb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           'python': sys.version}
    with open(os.path.join(HERE, 'cheat_T.json'), 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    for a in arms:
        print(a, dec[a]['highest'], dec[a]['tests'])
        print('   ', {k: round(v['mean'], 3) for k, v in dec[a]['stats'].items() if v},
              {k: (round(v['mean'], 3), round(v['lo'], 3), round(v['hi'], 3))
               for k, v in extra_stats[a].items() if v})
    print(dec['convention_T'], 'wall', round(out['wall_sec'], 1), 'rss_kb', out['peak_rss_kb'])


if __name__ == '__main__':
    {'repro': repro, 'cheat': cheat}[sys.argv[1]]()
