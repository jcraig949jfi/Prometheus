"""regate_v01 runner. Single process, stdlib only. Never writes outside this directory.

    PYTHONDONTWRITEBYTECODE=1 python3 run_regate.py gate       -> gate_v01.json
    PYTHONDONTWRITEBYTECODE=1 python3 run_regate.py unplanted  -> unplanted_v01.json
        (refuses unless gate_v01.json says PASS; order and hard stop per PREREG s6)
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import battery_v01 as B  # noqa: E402

assert os.path.dirname(os.path.abspath(B.__file__)) == HERE
SEEDS = [1000 + i for i in range(20)]
ORIG_ARMS = ['P', 'P4', 'N_a', 'N_b', 'C', 'P_sigma']
NEW_ARMS = ['T', 'P_cb', 'CAL', 'P_cal', 'DECOY']
ORDER = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']
rank = lambda h: -1 if h is None else ORDER.index(h)
NEW_KEYS = ('H_hist', 'H_alt', 'H_same', 'H_cell0', 'H_cell1', 'H_ncells', 'E0', 'e0_acc_intact',
            'e0_acc_episode', 'sec')


def flat(d, pre=''):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, pre + k + '.'))
        else:
            out[pre + k] = v
    return out


def compare(mine, ref):
    a, b = flat(mine), flat(ref)
    n, bad = 0, []
    for k in sorted(b):
        if k.split('.')[-1] == 'sec':
            continue
        if k not in a:
            bad.append((k, None, b[k]))
            continue
        x, y = a[k], b[k]
        n += 1
        if isinstance(x, float) or isinstance(y, float):
            if x is None or y is None or abs(x - y) > 1e-12:
                bad.append((k, x, y))
        elif x != y:
            bad.append((k, x, y))
    return n, bad


def run_arm(arm, seeds, log=True):
    out, states = [], []
    for s in seeds:
        t = time.time()
        o, st = B.battery_world(arm, s)
        o['sec'] = time.time() - t
        out.append(o)
        states.append(st)
        if log:
            print(arm, s, round(o['sec'], 1), 'H', o.get('H_hist') if o.get('H_hist') is None else round(o['H_hist'], 3),
                  'E0', round(o.get('E0', 0), 3), 'Dep', round(o.get('D_episode', 0), 3), flush=True)
    return out, states


def add_fw(out, states):
    n = len(states)
    if states[0]['p']['record_mode'] == 'normal':
        for i in range(n):
            out[i]['D_fw'] = B.fresh_world_transfer(states[i], states[(i + 1) % n])


def gate():
    t0 = time.time()
    with open(os.path.join(ORIG, 'known_answer.json')) as f:
        ka = json.load(f)
    by = {}
    for a in ORIG_ARMS + NEW_ARMS:
        out, states = run_arm(a, SEEDS)
        add_fw(out, states)
        by[a] = out
    # G0 identity vs fixture
    ident = {}
    for a in ORIG_ARMS:
        n, bad = 0, []
        for mine, ref in zip(by[a], ka['per_world'][a]):
            n1, b1 = compare(mine, ref)
            n += n1
            bad += [(mine['seed'],) + x for x in b1]
        orig_dec = B.decide([{k: v for k, v in w.items() if k not in NEW_KEYS} for w in by[a]])
        ident[a] = {'n_values': n, 'n_mismatch': len(bad), 'first': bad[:5],
                    'orig_decide_same': orig_dec['highest'] == ka['decisions'][a]['highest'] and
                    orig_dec['tests'] == ka['decisions'][a]['tests']}
    dec = {a: B.decide_v01(by[a]) for a in ORIG_ARMS + NEW_ARMS}
    dec['convention_P'] = B.convention(dec['P'], dec['P_sigma'])
    dec['convention3_P'] = B.convention3(dec['P'], dec['P_sigma'])
    P, C, T, CAL, DEC = dec['P'], dec['C'], dec['T'], dec['CAL'], dec['DECOY']
    crit = {
        'G0_identity': all(v['n_mismatch'] == 0 and v['orig_decide_same'] for v in ident.values()),
        'G1_P_R3': rank(P['highest']) >= 3,
        'G1_P_not_R4_R5': not P['tests']['R4'] and not P['tests']['R5'],
        'G1_P_INSTALLED': dec['convention_P']['qualifier'] == 'INSTALLED',
        'G2_N_a_le_R0': rank(dec['N_a']['highest']) <= 0,
        'G3_N_b_le_R0': rank(dec['N_b']['highest']) <= 0,
        'G4_C_R2_fails_R3_on_content': rank(C['highest']) == 2 and not C['tests']['R3'] and
            (not C['tests']['R3_perm'] or not C['tests']['R3_rand']),
        'G5_AA_valid_all': all(dec[a]['aa_valid'] for a in ORIG_ARMS + NEW_ARMS),
        'G6_P_cb_R3': rank(dec['P_cb']['highest']) >= 3,
        'G7_P_cal_R3': rank(dec['P_cal']['highest']) >= 3,
        'G8_T_caught': not T['tests']['R0'] and not T['tests']['R3'] and not T['tests']['H_hist'],
        'G9_CAL_caught_by_H': not CAL['tests']['R3'] and not CAL['tests']['H_hist'],
        'G10_DECOY_R2_not_R3': rank(DEC['highest']) == 2 and not DEC['tests']['R3'],
    }
    preserved = {a: {'fixture': ka['decisions'][a]['highest'], 'repaired': dec[a]['highest'],
                     'same': ka['decisions'][a]['highest'] == dec[a]['highest']} for a in ORIG_ARMS}
    g = {'criteria': crit, 'PASS': all(crit.values()), 'secondary_P4_R4': dec['P4']['tests']['R4'],
         'original_verdicts_preserved': all(v['same'] for v in preserved.values()), 'preserved': preserved}
    out = {'gate': g, 'identity': ident, 'decisions': dec, 'per_world': by,
           'wall_sec': time.time() - t0, 'python': sys.version}
    with open(os.path.join(HERE, 'gate_v01.json'), 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print(json.dumps(g, indent=1))
    print({a: (v['n_values'], v['n_mismatch'], v['orig_decide_same']) for a, v in ident.items()})
    for a in ORIG_ARMS + NEW_ARMS:
        d = dec[a]
        st = {k: (round(v['mean'], 3), round(v['lo'], 3), round(v['hi'], 3)) for k, v in d['stats'].items()
              if v and k in ('D0', 'E0', 'H_hist', 'D1', 'D2', 'Dp', 'Dr', 'D_episode', 'D_AA', 'H_cell0', 'H_cell1')}
        print(a, 'highest', d['highest'], 'orig_rules', d['highest_orig_rules'], st)
    print('wall', round(out['wall_sec'], 1))


def unplanted():
    t0 = time.time()
    with open(os.path.join(HERE, 'gate_v01.json')) as f:
        if not json.load(f)['gate']['PASS']:
            sys.exit('GATE FAILED: unplanted run refused')
    with open(os.path.join(ORIG, 'unplanted.json')) as f:
        ref = json.load(f)
    LIMIT = float(os.environ.get('REGATE_LIMIT_SEC', '1e9'))
    plan = [('U_sigma', [1016])] + [('U_sigma', [s for s in SEEDS if s != 1016])] + \
           [('U_id', SEEDS), ('U_frozen', SEEDS)]
    by = {}
    done_all = True
    path = os.path.join(HERE, 'unplanted_v01.json')

    def dump(extra):
        o = {'status': 'EXPLORATORY', 'per_world': by, 'wall_sec': time.time() - t0}
        o.update(extra)
        with open(path, 'w') as f:
            json.dump(o, f, indent=1, sort_keys=True, default=str)
    for arm, seeds in plan:
        for s in seeds:
            if time.time() - t0 > LIMIT:
                done_all = False
                break
            o, _ = B.battery_world(arm, s)
            refw = [w for w in ref['per_world'][arm] if w['seed'] == s][0]
            refw = {k: v for k, v in refw.items() if k != 'D_fw'}
            n, bad = compare(o, refw)
            o['identity_n'], o['identity_mismatch'] = n, len(bad)
            by.setdefault(arm, []).append(o)
            print(arm, s, 'id', n, len(bad), 'D0', round(o['D0'], 3), 'H', o.get('H_hist'),
                  'E0', round(o['E0'], 3), 'D1', round(o['D1'], 3), 'Dep', round(o['D_episode'], 3),
                  round(time.time() - t0), flush=True)
            dump({'complete': False})
    dec = {}
    for arm, ws in by.items():
        ws = sorted(ws, key=lambda w: w['seed'])
        by[arm] = ws
        if len(ws) >= 2:
            dec[arm] = B.decide_v01(ws)
            dec[arm]['n'] = len(ws)
    if 'U_id' in dec and 'U_sigma' in dec:
        dec['convention3_U'] = B.convention3(dec['U_id'], dec['U_sigma'])
    dump({'complete': done_all, 'decisions': dec})
    for a, d in dec.items():
        if isinstance(d, dict) and 'highest' in d:
            print(a, d['n'], d['highest'], d['highest_orig_rules'],
                  {k: (round(v['mean'], 3), round(v['lo'], 3), round(v['hi'], 3)) for k, v in d['stats'].items()
                   if v and k in ('D0', 'E0', 'H_hist', 'D1', 'D2', 'Dp', 'Dr', 'D_episode')})
    print('wall', round(time.time() - t0, 1), 'complete', done_all)


if __name__ == '__main__':
    {'gate': gate, 'unplanted': unplanted}[sys.argv[1]]()
