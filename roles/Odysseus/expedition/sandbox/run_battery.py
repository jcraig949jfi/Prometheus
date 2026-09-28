"""Run the battery on a set of arms. Usage:
    python3 run_battery.py known      -> known_answer_rerun.json, compared to the fixture known_answer.json
                                         (--overwrite-fixture to replace the fixture deliberately)
    python3 run_battery.py unplanted  -> unplanted.json   (refuses unless the gate passed)
Stdlib only; 4 worker processes.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402

N_WORLDS = int(os.environ.get('SANDBOX_N', '20'))
SEEDS = [1000 + i for i in range(N_WORLDS)]
KNOWN = ['P', 'P4', 'N_a', 'N_b', 'C', 'P_sigma']
UNPLANTED = ['U_sigma', 'U_id', 'U_frozen', 'U_unread', 'U_norec']


def _job(args):
    arm, seed = args
    t = time.time()
    out, st = B.battery_world(arm, seed)
    out['sec'] = time.time() - t
    return out, st


def run_arms(arms):
    jobs = [(a, s) for a in arms for s in SEEDS]
    with Pool(4) as pool:
        res = pool.map(_job, jobs, chunksize=1)
    by = {a: [] for a in arms}
    states = {a: [] for a in arms}
    for (a, s), (out, st) in zip(jobs, res):
        by[a].append(out)
        states[a].append(st)
    # fresh-world transfer (world i record -> world i+1), reported only
    for a in arms:
        if states[a][0]['p']['record_mode'] != 'normal':
            continue
        n = len(states[a])
        for i in range(n):
            by[a][i]['D_fw'] = B.fresh_world_transfer(states[a][i], states[a][(i + 1) % n])
    return by


def gate(dec):
    P, N_a, N_b, C, P4 = dec['P'], dec['N_a'], dec['N_b'], dec['C'], dec['P4']
    order = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']
    rank = lambda h: -1 if h is None else order.index(h)
    crit = {
        'P_awards_R0_R3': rank(P['highest']) >= 3,
        'P_not_R4_R5': not P['tests']['R4'] and not P['tests']['R5'],
        'P_qualifier_INSTALLED': dec['convention_P']['qualifier'] == 'INSTALLED',
        'N_a_nothing_above_R0': rank(N_a['highest']) <= 0,
        'N_b_nothing_above_R0': rank(N_b['highest']) <= 0,
        'C_fails_R3': not C['tests']['R3'],
        'C_fails_R3_on_content_with_R2_awarded': rank(C['highest']) == 2 and
            (not C['tests']['R3_perm'] or not C['tests']['R3_rand']),
        'AA_valid_all_arms': all(dec[a]['aa_valid'] for a in KNOWN),
    }
    return {'criteria': crit, 'PASS': all(crit.values()),
            'secondary_P4_R4_awarded': P4['tests']['R4']}


def main():
    which = sys.argv[1]
    t0 = time.time()
    if which == 'known':
        by = run_arms(KNOWN)
        dec = {a: B.decide(by[a]) for a in KNOWN}
        dec['convention_P'] = B.convention(dec['P'], dec['P_sigma'])
        g = gate(dec)
        out = {'arms': KNOWN, 'n_worlds': N_WORLDS, 'decisions': dec, 'gate': g,
               'per_world': by, 'wall_sec': time.time() - t0}
        path = os.path.join(HERE, 'known_answer.json')
        if os.path.exists(path) and '--overwrite-fixture' not in sys.argv:
            # cold-start gap G2 (2026-09-28): never destroy the fixture; re-runs are compared to it
            with open(path) as f:
                fixture = json.load(f)
            same = json.dumps(fixture['per_world'], sort_keys=True) == json.dumps(json.loads(json.dumps(by)), sort_keys=True)
            out['matches_fixture'] = same
            print('per-world values match known_answer.json:', same)
            path = os.path.join(HERE, 'known_answer_rerun.json')
    else:
        with open(os.path.join(HERE, 'known_answer.json')) as f:
            ka = json.load(f)
        if not ka['gate']['PASS']:
            sys.exit('GATE FAILED: unplanted run refused')
        by = run_arms(UNPLANTED)
        pristine = B.summ([w['window']['ceil_intact'] for w in by['U_norec']])['mean']
        dec = {a: B.decide(by[a], pristine_ceiling=pristine) for a in ('U_sigma', 'U_id', 'U_frozen')}
        dec['convention_U'] = B.convention(dec['U_id'], dec['U_sigma'])
        dec['baselines'] = {a: {'ceil': B.summ([w['window']['ceil_intact'] for w in by[a]]),
                                'speed': B.summ([w['window']['speed_intact'] for w in by[a]]),
                                'evo_success_last100': B.summ([w['evo_success_last100'] for w in by[a]])}
                            for a in UNPLANTED}
        out = {'status': 'EXPLORATORY', 'arms': UNPLANTED, 'n_worlds': N_WORLDS,
               'generations': B.GENS_UNPLANTED, 'decisions': dec, 'per_world': by,
               'wall_sec': time.time() - t0}
        path = os.path.join(HERE, 'unplanted.json')
    with open(path, 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True, default=str)
    print(path, 'wall', round(time.time() - t0, 1))
    if which == 'known':
        print(json.dumps(out['gate'], indent=1))
        for a in KNOWN:
            print(a, dec[a]['highest'], dec[a]['tests'])


if __name__ == '__main__':
    main()
