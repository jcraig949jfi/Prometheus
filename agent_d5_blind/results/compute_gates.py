"""Mechanical gate computation from evidence rows. Frozen BEFORE any M1
evidence row was read (pre-commitment of the analysis). Spec:
PREREG-EVIDENCE.md section 5. No judgment calls; every gate reports observed
value, threshold, and distance-to-threshold in SE units (weakly-informative
labeling per section 6).
"""
import json, os, random, statistics, math, collections

HERE = os.path.dirname(__file__)
LEDGERS = os.path.join(HERE, '..', 'ledgers')
NC = ('F1', 'F2', 'F3', 'F4')
TOP = '30000'
N_PERM = 10000
PERM_SEED = 424242


def load(path):
    p = os.path.join(LEDGERS, path)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding='utf-8')]


def frac_by_task(rows, arm, fams, rung=TOP):
    per = collections.defaultdict(list)
    for r in rows:
        if r['arm'] == arm and r['family'] in fams:
            per[(r['family'], r['seed'])].append(bool(r['ladder'][rung]))
    return {k: sum(v) / len(v) for k, v in per.items()}


def cost_by_task(rows, arm, fams):
    per = collections.defaultdict(list)
    for r in rows:
        if r['arm'] == arm and r['family'] in fams and r['first_solve']:
            per[(r['family'], r['seed'])].append(r['first_solve'])
    return {k: statistics.median(v) for k, v in per.items()}


def paired_perm_p(deltas, n_perm=N_PERM, seed=PERM_SEED):
    """One-sided sign-flip permutation test: P(perm mean >= observed mean)."""
    rng = random.Random(seed)
    obs = sum(deltas) / len(deltas)
    ge = 0
    for _ in range(n_perm):
        m = sum(d if rng.random() < 0.5 else -d for d in deltas) / len(deltas)
        if m >= obs:
            ge += 1
    return obs, (ge + 1) / (n_perm + 1)


def se_of_mean(xs):
    if len(xs) < 2:
        return float('inf')
    return statistics.stdev(xs) / math.sqrt(len(xs))


def main():
    m0 = load('m0_rows.jsonl')
    m1 = load('m1_rows.jsonl')
    alien = load('alien_rows.jsonl')
    abl = load('ablation_rows.jsonl')
    out = {'gates': {}, 'notes': []}

    man = json.load(open(os.path.join(HERE, 'task_manifest.json')))
    out['gates']['G1'] = {'pass': man['n_dev'] == 58 and man['n_alien'] == 20,
                          'value': [man['n_dev'], man['n_alien']]}
    out['gates']['G2'] = {'pass': True, 'note': 'R==E theorem; uninformative'}

    m0f = frac_by_task(m0, 'M0c-RX', NC)
    g3 = sum(m0f.values()) / len(m0f) if m0f else None
    out['gates']['G3'] = {'value': g3, 'band': [0.08, 0.70],
                          'pass': g3 is not None and 0.08 <= g3 <= 0.70}

    if m1:
        m1f = frac_by_task(m1, 'M1', NC)
        keys = sorted(set(m0f) & set(m1f))
        deltas = [m1f[k] - m0f[k] for k in keys]
        obs, p = paired_perm_p(deltas)
        se = se_of_mean(deltas)
        out['gates']['G4'] = {
            'delta': obs, 'p_one_sided': p, 'n_tasks': len(keys), 'se': se,
            'margin': 0.10, 'alpha': 0.05,
            'pass': obs >= 0.10 and p < 0.05,
            'weakly_informative': abs(obs - 0.10) < se,
            'per_family': {fam: round(sum(m1f[k] - m0f[k] for k in keys
                                          if k[0] == fam) /
                                      max(1, sum(1 for k in keys if k[0] == fam)), 4)
                           for fam in NC}}

        c0 = cost_by_task(m0, 'M0c-RX', NC)
        c1 = cost_by_task(m1, 'M1', NC)
        joint = sorted(set(c0) & set(c1))
        if joint:
            hacr = statistics.median([c0[k] for k in joint]) / \
                statistics.median([c1[k] for k in joint])
            rng = random.Random(PERM_SEED + 1)
            boots = []
            for _ in range(N_PERM):
                ks = [joint[rng.randrange(len(joint))] for _ in joint]
                denom = statistics.median([c1[k] for k in ks])
                boots.append(statistics.median([c0[k] for k in ks]) / denom
                             if denom else float('inf'))
            boots.sort()
            lo, hi = boots[int(0.05 * len(boots))], boots[int(0.95 * len(boots)) - 1]
            out['gates']['G5'] = {'hacr': hacr, 'ci90': [lo, hi],
                                  'n_joint': len(joint),
                                  'pass': hacr >= 1.25 and lo > 1.0}
        else:
            out['gates']['G5'] = {'pass': False, 'note': 'no jointly solved tasks'}

        pos = {(m['family'], m['seed']): m['position'] for m in man['tasks']
               if m['battery'] == 'dev'}
        early = [m1f[k] - m0f[k] for k in keys if pos[k] < 29]
        late = [m1f[k] - m0f[k] for k in keys if pos[k] >= 29]
        if early and late:
            obs6 = sum(late) / len(late) - sum(early) / len(early)
            rng = random.Random(PERM_SEED + 2)
            allk = [(k, m1f[k] - m0f[k]) for k in keys]
            ge = 0
            for _ in range(N_PERM):
                rng.shuffle(allk)
                l = [d for _, d in allk[:len(late)]]
                e = [d for _, d in allk[len(late):]]
                if sum(l) / len(l) - sum(e) / len(e) >= obs6:
                    ge += 1
            out['gates']['G6'] = {'late_minus_early': obs6,
                                  'p': (ge + 1) / (N_PERM + 1),
                                  'pass': obs6 > 0 and (ge + 1) / (N_PERM + 1) < 0.10}

        m0c = frac_by_task(m0, 'M0c-RX', ('CTRL',))
        m1c = frac_by_task(m1, 'M1', ('CTRL',))
        ck = sorted(set(m0c) & set(m1c))
        if ck:
            cd = sum(m1c[k] - m0c[k] for k in ck) / len(ck)
            out['gates']['G8'] = {'ctrl_delta': cd, 'n': len(ck),
                                  'pass': cd <= 0.15}

    if alien:
        a0 = frac_by_task(alien, 'M0c-RX', ('ALIEN',))
        a1 = frac_by_task(alien, 'M1-frozen', ('ALIEN',))
        ak = sorted(set(a0) & set(a1))
        if ak:
            deltas = [a1[k] - a0[k] for k in ak]
            obs, p = paired_perm_p(deltas, seed=PERM_SEED + 3)
            out['gates']['G7'] = {'delta': obs, 'p': p, 'n': len(ak),
                                  'se': se_of_mean(deltas),
                                  'pass': obs >= 0.10 and p < 0.05}

    if abl and m1 and 'G4' in out['gates'] and out['gates']['G4'].get('delta'):
        adv = out['gates']['G4']['delta']
        rets = {}
        for arm in ('M1-random-library', 'M1-shuffled-history'):
            af = frac_by_task(abl, arm, NC)
            ks = sorted(set(af) & set(m0f))
            if ks:
                d = sum(af[k] - m0f[k] for k in ks) / len(ks)
                rets[arm] = d / adv if adv else float('inf')
        if rets:
            out['gates']['G9'] = {'retention': rets, 'g4_adv': adv,
                                  'pass': all(v < 0.5 for v in rets.values())}

    g = out['gates']
    verdict = 'INCOMPLETE'
    if all(k in g for k in ('G1', 'G3', 'G4')):
        if not (g['G1']['pass'] and g['G3']['pass']):
            verdict = 'TASK_BATTERY_INVALID'
        elif not g['G4']['pass']:
            verdict = 'NO_HISTORY_ADVANTAGE'
        else:
            verdict = 'HISTORY_FINDABILITY_ADVANTAGE'
            if g.get('G5', {}).get('pass'):
                verdict = 'HISTORY_COST_ADVANTAGE'
            if g.get('G6', {}).get('pass'):
                verdict = 'DEVELOPMENTAL_ACCELERATION'
            if g.get('G7', {}).get('pass'):
                verdict = 'FROZEN_TRANSFER_ADVANTAGE'
            if g.get('G8', {}).get('pass') and g.get('G9', {}).get('pass') \
                    and g.get('G7', {}).get('pass'):
                verdict = 'CAUSALLY_REUSED_DEVELOPMENTAL_STRUCTURE'
    out['verdict'] = verdict
    json.dump(out, open(os.path.join(HERE, 'gates_verdict.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1, default=str))


if __name__ == '__main__':
    main()
