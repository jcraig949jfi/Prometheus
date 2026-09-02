"""Preregistered statistics. Task is the unit; paired sign-flip permutation + bootstrap."""
import json, random, sys


def task_rates(res, arm):
    by = {}
    for r in res:
        if r['arm'] == arm:
            by.setdefault(r['tid'], []).append(r['solved'])
    return {t: sum(v) / len(v) for t, v in by.items()}


def paired(res, a, b):
    ra, rb = task_rates(res, a), task_rates(res, b)
    tids = sorted(set(ra) & set(rb))
    return [ra[t] - rb[t] for t in tids], tids


def perm_p(diffs, n=10_000, seed=1):
    rng = random.Random(seed)
    obs = sum(diffs) / len(diffs)
    hits = 0
    for _ in range(n):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs) / len(diffs)
        if s >= obs - 1e-12:
            hits += 1
    return obs, (hits + 1) / (n + 1)


def boot_ci(diffs, n=10_000, seed=2):
    rng = random.Random(seed)
    m = len(diffs)
    means = sorted(sum(diffs[rng.randrange(m)] for _ in range(m)) / m for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n)]


def test(res, a, b, label, min_eff):
    diffs, tids = paired(res, a, b)
    obs, p = perm_p(diffs)
    lo, hi = boot_ci(diffs)
    ok = obs >= min_eff and p < 0.01 and lo > 0
    print('%-28s n_tasks=%d  mean_diff=%+.3f  CI95=[%+.3f,%+.3f]  p=%.4f  min_eff=%.2f -> %s'
          % (label, len(diffs), obs, lo, hi, p, min_eff, 'PASS' if ok else 'FAIL'))
    return dict(label=label, n=len(diffs), diff=obs, ci=[lo, hi], p=p,
                min_eff=min_eff, ok=ok)


def main():
    out = []
    conf = json.load(open('F:/SerendipityA/runs/arms_CONF.json'))
    out.append(test(conf, 'H3', 'H1', 'T-P3 H3-H1 (CONF)', 0.20))
    out.append(test(conf, 'H3', 'H2', 'T-P4 H3-H2 (CONF)', 0.15))
    out.append(test(conf, 'H3', 'RANDZ', 'gateG H3-RANDZ (CONF)', 0.0))
    out.append(test(conf, 'H3', 'Z0ARM', 'Z1-vs-Z0 (CONF)', 0.0))
    try:
        alien = json.load(open('F:/SerendipityA/runs/arms_ALIEN.json'))
        out.append(test(alien, 'H3', 'H1', 'T-P5 H3-H1 (ALIEN zero-shot)', 0.15))
    except FileNotFoundError:
        pass
    try:
        struct = json.load(open('F:/SerendipityA/runs/arms_STRUCT.json'))
        d, _ = paired(struct, 'H3', 'H1')
        m = sum(d) / len(d)
        print('%-28s mean_diff=%+.3f  |diff|<=0.10 -> %s'
              % ('T-CTRL H3-H1 (STRUCT)', m, 'PASS' if abs(m) <= 0.10 else 'FAIL'))
        out.append(dict(label='T-CTRL', diff=m, ok=abs(m) <= 0.10))
    except FileNotFoundError:
        pass
    try:
        neg = json.load(open('F:/SerendipityA/runs/arms_NEG.json'))
        d, _ = paired(neg, 'H3', 'H1')
        print('%-28s mean_diff=%+.3f' % ('NEG H3-H1 (old z on alien modules)', sum(d) / len(d)))
    except FileNotFoundError:
        pass
    # Holm over the three primary confirmatory tests
    prim = [o for o in out if o['label'].startswith(('T-P3', 'T-P4', 'T-P5'))]
    prim.sort(key=lambda o: o['p'])
    alpha = 0.05
    holm = all(o['p'] < alpha / (len(prim) - i) for i, o in enumerate(prim))
    print('Holm-Bonferroni over primaries: %s' % ('PASS' if holm else 'FAIL'))
    json.dump(out, open('F:/SerendipityA/runs/stats.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
