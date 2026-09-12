"""ERGON PROJECT 3 -- gate-fire worlds for the I3 - I0 instrument (ERGON-17).

Before any live reading, the frozen inference path (p3_analyze.decide) is
fed per-lineage CFRs from CONSTRUCTED worlds in which the truth about MRU is
known by construction. Every world must be called correctly or the
instrument may not read the experiment. These are independently generated
controls exercising the exact inference path (seat constraint 2): the
simulator below shares no code with the frozen runner and no code with the
statistic; it only produces the two CFR vectors the statistic consumes.

The simulator: a library of cap 64 under FIFO (MRU: evict the oldest) or
RANDOM eviction; each task admits 5 artifacts (the frozen D-5 admission
count: solver + up to 4). A task is solved if (a) its base draw succeeds
(one common draw per task per lineage, shared by both arms, so the arms are
paired the way the real arms share nav_base), flipped independently per arm
with probability EPS so the paired delta has a per-lineage SD near the
measured 3.6-4.3 pp; or (b) the task DEPENDS on an artifact admitted D tasks
earlier and that artifact is still resident. Only (b) differs between arms,
and it differs because of eviction alone.

Worlds and the verdict each MUST receive:

    HARMFUL       tasks 20..41 depend on the artifact admitted 20 tasks
                  earlier (100 admissions ago, beyond a 64-cap FIFO, so MRU
                  never has it; RANDOM keeps it with probability about
                  (63/64)^100 = 0.21)            -> MRU_HARMFUL
    HARMLESS      no task depends on residency    -> RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER
    MRU_BETTER    tasks 2..41 depend on the artifact admitted 2 tasks
                  earlier (10 admissions ago: always resident under FIFO,
                  lost by RANDOM about 15% of the time) -> MRU_BETTER_THAN_RANDOM
    TIED          HARMLESS with EPS = 0 (arms identical) -> INDETERMINATE (all tied)
    SHORT         HARMFUL truncated to 50 lineages -> INDETERMINATE (eligibility)

Run:  python -m ergon.gen3.gatefire_p3     writes gatefire_p3.json
"""
import json
import os
import random
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen3.p3_analyze import decide    # noqa: E402  the exact path

N_TASKS = 42
CAP = 64
ADMIT = 5
BASE_P = 0.30
EPS = 0.034          # per-arm independent flip -> delta SD about 4 pp
N_LINEAGES = 100
SEED = 20260911

WORLDS = {
    'HARMFUL': {'depend': 20, 'eps': EPS, 'n': N_LINEAGES,
                'expect': 'MRU_HARMFUL'},
    'HARMLESS': {'depend': None, 'eps': EPS, 'n': N_LINEAGES,
                 'expect': 'RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER'},
    'MRU_BETTER': {'depend': 2, 'eps': EPS, 'n': N_LINEAGES,
                   'expect': 'MRU_BETTER_THAN_RANDOM'},
    'TIED': {'depend': None, 'eps': 0.0, 'n': N_LINEAGES,
             'expect': 'INDETERMINATE'},
    'SHORT': {'depend': 20, 'eps': EPS, 'n': 50,
              'expect': 'INDETERMINATE'},
}


def simulate_lineage(policy, depend, eps, common, arm_rng):
    """Returns CFR for one lineage under `policy` in {'MRU', 'RANDOM'}.
    `common` is the lineage's shared randomness (base draws, admission ids);
    `arm_rng` is the arm's own stream (flips, random eviction)."""
    lib = []                      # list of artifact ids, oldest first
    admitted_at = {}              # task -> the id of its first admission
    solved = 0
    for i in range(N_TASKS):
        ok = common['base'][i]
        if arm_rng.random() < eps:
            ok = not ok
        if depend is not None and i >= depend:
            need = admitted_at[i - depend]
            if need in lib:
                ok = True
        solved += 1 if ok else 0
        for k in range(ADMIT):
            aid = (i, k)
            if k == 0:
                admitted_at[i] = aid
            lib.append(aid)
            while len(lib) > CAP:
                if policy == 'MRU':
                    lib.pop(0)
                else:
                    lib.pop(arm_rng.randrange(len(lib)))
    return solved / N_TASKS


def run_world(name, spec):
    rng = random.Random(SEED)
    cfr_mru, cfr_rnd = [], []
    for L in range(spec['n']):
        common = {'base': [rng.random() < BASE_P for _ in range(N_TASKS)]}
        # arm streams are pure functions of (world, lineage, arm); a str
        # seed is hashed by random.Random with sha512, not the salted hash()
        r_mru = random.Random('%s-%d-MRU' % (name, L))
        r_rnd = random.Random('%s-%d-RANDOM' % (name, L))
        cfr_mru.append(simulate_lineage('MRU', spec['depend'], spec['eps'],
                                        common, r_mru))
        cfr_rnd.append(simulate_lineage('RANDOM', spec['depend'], spec['eps'],
                                        common, r_rnd))
    r = decide(cfr_mru, cfr_rnd, n_perm=20000, n_boot=10000)
    return {'world': name, 'spec': {k: v for k, v in spec.items()},
            'verdict': r['verdict'], 'expected': spec['expect'],
            'called_correctly': r['verdict'] == spec['expect'],
            'mean_pp': r.get('mean_pp'), 'se_pp': r.get('se_pp'),
            'ci95_pp': r.get('ci95_pp'), 'p': r.get('p'),
            'signs': r.get('signs'), 'rationale': r['rationale'],
            'cfr_mru': cfr_mru, 'cfr_random': cfr_rnd}


def main():
    out = []
    print('ERGON PROJECT 3 -- GATE-FIRE WORLDS FOR THE I3 - I0 INSTRUMENT')
    print('=' * 70)
    for name, spec in WORLDS.items():
        w = run_world(name, spec)
        out.append(w)
        stat = ('' if w['mean_pp'] is None else
                ' mean %+.2f pp SE %.2f pp CI [%+.2f, %+.2f] p %.4f'
                % (w['mean_pp'], w['se_pp'], w['ci95_pp'][0],
                   w['ci95_pp'][1], w['p']))
        print('  %-11s -> %-45s %s%s' % (
            name, w['verdict'], 'OK  ' if w['called_correctly'] else 'FAIL',
            stat))
    all_ok = all(w['called_correctly'] for w in out)
    print('\nALL WORLDS CALLED CORRECTLY: %s' % all_ok)
    json.dump({'seed': SEED, 'n_tasks': N_TASKS,
               'cap': CAP, 'admit_per_task': ADMIT, 'base_p': BASE_P,
               'eps': EPS, 'all_called_correctly': all_ok, 'worlds': out},
              open(os.path.join(HERE, 'gatefire_p3.json'), 'w',
                   encoding='utf-8'), indent=1, sort_keys=True)
    print('wrote gatefire_p3.json')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
