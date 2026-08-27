"""Phase 0 accessibility preflight for RM-D5. Spec: PREREG-PREFLIGHT.md.

Meter: 1 evaluation = one candidate's behavior computed over the full probe set.
Every generated candidate is metered (no cache discount). For the (1+lambda)
hill-climber only, distance computation may stop early once mismatches exceed
the current best distance — an ordering-preserving optimization that changes no
decision. Population navigators use full evaluation (tournament needs total
order).

Seed offsets (base = 1000 engineering, 2000 evidence):
  PF1 walks:        base+100+i
  PF2 target walks: base+300+i   (stream A)
  PF2 navigation:   base+400+i   (stream B, independent)
  PF3 NAV-POP:      base+500+i ; NAV-RX: base+600+i
  PF4 ablations:    base+700+abl_idx*1000+i
  PF5 minimal-rep:  base+800+i
"""
import sys, os, json, argparse, random, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'substrate'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mutation'))
from rm_vm import run, behavior, behavior_class, hamming
from physics import mutate, crossover, SEED_REPERTOIRE, MUT_CLASSES

PROBE = [(x,) for x in range(64)]
MINIMAL_REPERTOIRE = [(('MOV', 0, 0),)]


def dist_capped(prog, target_vec, cap):
    """Mismatch count, early-stopped once it exceeds cap (returns cap+1)."""
    d = 0
    for x, t in zip(PROBE, target_vec):
        if run(prog, x)[0] != t:
            d += 1
            if d > cap:
                return cap + 1
    return d


def full_dist(prog, target_vec):
    return hamming(behavior(prog, PROBE), target_vec)


# ---------------- navigators (history-free) ----------------

def nav_hc(target_vec, rng, budget, repertoire, allowed=None, lam=8, stall=50):
    """(1+lambda) hill-climber with neutral drift and restart on stall.
    Returns (solved, evals_to_solve_or_None, evals_used)."""
    cur = repertoire[rng.randrange(len(repertoire))]
    bd = full_dist(cur, target_vec)
    evals = 1
    if bd == 0:
        return True, evals, evals
    no_imp = 0
    while evals < budget:
        best_c, best_d = None, bd
        for _ in range(lam):
            c = mutate(cur, rng, allowed=allowed)
            evals += 1
            d = dist_capped(c, target_vec, best_d)
            if d <= best_d:
                best_c, best_d = c, d
            if evals >= budget:
                break
        if best_c is not None:
            improved = best_d < bd
            cur, bd = best_c, best_d
            no_imp = 0 if improved else no_imp + 1
        else:
            no_imp += 1
        if bd == 0:
            return True, evals, evals
        if no_imp >= stall:
            cur = repertoire[rng.randrange(len(repertoire))]
            bd = full_dist(cur, target_vec)
            evals += 1
            no_imp = 0
            if bd == 0:
                return True, evals, evals
    return False, None, evals


def _pop_nav(target_vec, rng, budget, repertoire, use_crossover):
    """Population navigator: tournament(3) selection, 10% immigrants;
    NAV-RX additionally makes 50% of children by crossover."""
    psize = 32
    pop = [mutate(repertoire[rng.randrange(len(repertoire))], rng) for _ in range(psize)]
    evals = 0
    dists = []
    for g in pop:
        d = full_dist(g, target_vec)
        evals += 1
        if d == 0:
            return True, evals, evals
        dists.append(d)
    while evals < budget:
        children = []
        for _ in range(psize):
            if rng.random() < 0.10:
                children.append(mutate(repertoire[rng.randrange(len(repertoire))], rng))
                continue
            idxs = [rng.randrange(psize) for _ in range(3)]
            p1 = pop[min(idxs, key=lambda i: dists[i])]
            if use_crossover and rng.random() < 0.5:
                jdxs = [rng.randrange(psize) for _ in range(3)]
                p2 = pop[min(jdxs, key=lambda i: dists[i])]
                child = mutate(crossover(p1, p2, rng), rng)
            else:
                child = mutate(p1, rng)
            children.append(child)
        pop = children
        dists = []
        for g in pop:
            d = full_dist(g, target_vec)
            evals += 1
            if d == 0:
                return True, evals, evals
            dists.append(d)
            if evals >= budget:
                break
        while len(dists) < len(pop):
            dists.append(10 ** 9)
    return False, None, evals


def nav_pop(target_vec, rng, budget, repertoire, allowed=None):
    return _pop_nav(target_vec, rng, budget, repertoire, use_crossover=False)


def nav_rx(target_vec, rng, budget, repertoire, allowed=None):
    return _pop_nav(target_vec, rng, budget, repertoire, use_crossover=True)


NAVIGATORS = {'NAV-HC': nav_hc, 'NAV-POP': nav_pop, 'NAV-RX': nav_rx}


# ---------------- assays ----------------

def pf1_diversity(base, walks, walk_len):
    classes = set()
    for i in range(walks):
        rng = random.Random(base + 100 + i)
        g = SEED_REPERTOIRE[i % len(SEED_REPERTOIRE)]
        classes.add(behavior_class(behavior(g, PROBE)))
        for _ in range(walk_len):
            g = mutate(g, rng)
            classes.add(behavior_class(behavior(g, PROBE)))
    return {'walks': walks, 'walk_len': walk_len, 'distinct_classes': len(classes)}


def emit_targets(base, n_targets, walk_len=60):
    """Stream A: sample a novel NON-CONSTANT behavior class visited during each
    walk (walks are behaviorally sticky: endpoints collapse to identity/constant
    attractors, so endpoint sampling emits nothing — measured 2026-08-27 on
    engineering seeds; see BUILD_LOG). One target per walk, chosen uniformly by
    the walk's own rng among its novel visited classes."""
    seed_classes = {behavior_class(behavior(g, PROBE)) for g in SEED_REPERTOIRE}
    targets, seen = [], set(seed_classes)
    attempt = 0
    while len(targets) < n_targets and attempt < n_targets * 8:
        rng = random.Random(base + 300 + attempt)
        g = SEED_REPERTOIRE[attempt % len(SEED_REPERTOIRE)]
        novel = {}
        for _ in range(walk_len):
            g = mutate(g, rng)
            vec = behavior(g, PROBE)
            bc = behavior_class(vec)
            if bc not in seen and bc not in novel and len(set(vec)) > 1:
                novel[bc] = (vec, len(g))
        attempt += 1
        if novel:
            keys = sorted(novel)
            bc = keys[rng.randrange(len(keys))]
            vec, glen = novel[bc]
            seen.add(bc)
            targets.append({'behavior': vec, 'class': bc, 'emitter_len': glen})
    return targets


def run_navigator(name, targets, base, offset, budget, repertoire, allowed=None):
    fn = NAVIGATORS[name]
    rows = []
    for i, t in enumerate(targets):
        rng = random.Random(base + offset + i)
        solved, ets, used = fn(tuple(t['behavior']), rng, budget, repertoire, allowed=allowed)
        rows.append({'target': t['class'], 'solved': solved, 'evals_to_solve': ets,
                     'evals_used': used})
    rate = sum(r['solved'] for r in rows) / len(rows) if rows else 0.0
    return {'navigator': name, 'reach_rate': rate, 'rows': rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['engineering', 'evidence'], required=True)
    ap.add_argument('--targets', type=int, default=20)
    ap.add_argument('--budget', type=int, default=2000)
    ap.add_argument('--walks', type=int, default=200)
    ap.add_argument('--walk-len', type=int, default=150)
    ap.add_argument('--assays', default='pf1,pf2,pf3,pf4,pf5')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    base = 1000 if args.mode == 'engineering' else 2000
    assays = set(args.assays.split(','))
    t0 = time.time()
    out = {'mode': args.mode, 'seed_base': base, 'targets': args.targets,
           'budget': args.budget, 'assays': {}}

    if 'pf1' in assays:
        out['assays']['PF1'] = pf1_diversity(base, args.walks, args.walk_len)
        print('PF1 distinct classes:', out['assays']['PF1']['distinct_classes'], flush=True)

    targets = None
    if assays & {'pf2', 'pf3', 'pf4', 'pf5'}:
        targets = emit_targets(base, args.targets)
        print('targets emitted:', len(targets), flush=True)

    if 'pf2' in assays:
        r = run_navigator('NAV-POP', targets, base, 400, args.budget, SEED_REPERTOIRE)
        out['assays']['PF2'] = r
        print('PF2 NAV-POP reach:', r['reach_rate'], flush=True)

    if 'pf3' in assays:
        rows = [out['assays']['PF2']] if 'PF2' in out['assays'] else \
               [run_navigator('NAV-POP', targets, base, 400, args.budget, SEED_REPERTOIRE)]
        rows.append(run_navigator('NAV-HC', targets, base, 500, args.budget, SEED_REPERTOIRE))
        print('PF3 NAV-HC reach:', rows[-1]['reach_rate'], flush=True)
        rows.append(run_navigator('NAV-RX', targets, base, 600, args.budget, SEED_REPERTOIRE))
        print('PF3 NAV-RX reach:', rows[-1]['reach_rate'], flush=True)
        out['assays']['PF3'] = {'navigators': [{'navigator': r['navigator'],
                                                'reach_rate': r['reach_rate']} for r in rows],
                                'rows': rows}

    if 'pf4' in assays:
        best = 'NAV-HC'
        if 'PF3' in out['assays']:
            best = max(out['assays']['PF3']['navigators'], key=lambda r: r['reach_rate'])['navigator']
        abl = []
        for k, cls in enumerate(MUT_CLASSES):
            allowed = [c for c in MUT_CLASSES if c != cls]
            r = run_navigator(best, targets, base, 700 + k * 1000, args.budget,
                              SEED_REPERTOIRE, allowed=allowed)
            abl.append({'ablated': cls, 'navigator': best, 'reach_rate': r['reach_rate']})
            print(f'PF4 -{cls}: {r["reach_rate"]}', flush=True)
        out['assays']['PF4'] = {'best_navigator': best, 'ablations': abl}

    if 'pf5' in assays:
        r = run_navigator('NAV-POP', targets, base, 800, args.budget, MINIMAL_REPERTOIRE)
        out['assays']['PF5'] = r
        print('PF5 minimal-repertoire reach:', r['reach_rate'], flush=True)

    out['wall_seconds'] = round(time.time() - t0, 1)
    path = args.out or os.path.join(os.path.dirname(__file__), '..', 'results',
                                    f'substrate_preflight_{args.mode}.json')
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print('wall:', out['wall_seconds'], 's  ->', path, flush=True)


if __name__ == '__main__':
    main()
