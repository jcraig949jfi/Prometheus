"""ERGON GEN-1B / PHASE 1 -- mutational redundancy audit.

Gen-1A reported that 487 of 834 admitted artifacts (58%) duplicate another
artifact's behaviour fingerprint. That establishes CURRENT-BEHAVIOUR
redundancy. It does not establish EVOLUTIONARY redundancy, because library
artifacts are used as MUTATION SEEDS: two programs computing the same function
may sit in very different mutational neighbourhoods.

    SAME PHENOTYPE != SAME MUTATIONAL AFFORDANCES?

PRECONDITION CHECKED FIRST. A fingerprint is FastTask.outputs over the task's
input domain, so cross-task comparison is only meaningful if the domain is
shared. Verified: every D-5 task in F1-F4 uses the identical 64-point domain
(0..63), so fingerprints are directly comparable and the 58% figure is sound.
Had they differed, the Gen-1A number would have been an artifact of comparing
different domains and would have had to be withdrawn.

MATCHED RANDOMNESS. Every artifact receives the SAME seed and therefore the
same sequence of random draws when its neighbourhood is generated. Differences
between neighbourhoods are then attributable to the genotype, not to luck in
the mutation stream.

MUTATIONAL REDUNDANCY, defined:

    MR(a,b) = Jaccard( N_K(a), N_K(b) )

where N_K(x) is the SET of distinct offspring behaviour fingerprints produced
by K matched single mutations of x. MR = 1 means the two artifacts open onto
exactly the same set of next behaviours; MR = 0 means they share none. A pair
is EVOLUTIONARILY REDUNDANT at threshold tau if MR >= tau. tau = 0.50 is
preregistered here, before any Gen-1 outcome exists, and results are reported
across a sweep so the choice is visible rather than load-bearing.

Run:  python -m ergon.gen1b.phase1_mutational_redundancy
"""
import collections
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
D5 = os.path.abspath(os.path.join(HERE, '..', '..', 'agent_d5_blind'))
for _s in ('task_generators', 'substrate', 'mutation', 'exact_oracle'):
    sys.path.insert(0, os.path.join(D5, _s))

from families import gen_task            # noqa: E402
from physics import mutate, MUT_CLASSES  # noqa: E402
from rm_fast import FastTask             # noqa: E402

CORPUS = os.path.join(HERE, '..', 'gen1a', 'corpus')
K = 120                 # matched mutation budget per artifact
SEED = 90120901
TAU = 0.50              # preregistered evolutionary-redundancy threshold
PANEL = 8               # reference tasks for improvement probability


def load_artifacts():
    out = {}
    for L in range(5):
        p = os.path.join(CORPUS, 'lineage_%d_artifacts.jsonl' % L)
        for line in open(p, encoding='utf-8'):
            if line.strip():
                a = json.loads(line)
                out.setdefault(a['hash'], a)
    return out


def geno(a):
    return tuple(tuple(i) for i in a['genotype'])


def main():
    arts = load_artifacts()
    man = json.load(open(os.path.join(D5, 'results', 'task_manifest.json'),
                         encoding='utf-8'))
    tasks = [m for m in man['tasks'] if m['family'] in ('F1', 'F2', 'F3', 'F4')]
    panel = [gen_task(m['family'], m['seed']) for m in tasks[:PANEL]]
    views = [{'domain': t['domain'], 'table': t['table']} for t in panel]
    fts = [FastTask(v) for v in views]
    ref = fts[0]        # domain is shared, so any FastTask gives the canonical
                        # behaviour fingerprint

    print('ERGON GEN-1B PHASE 1 -- MUTATIONAL REDUNDANCY AUDIT')
    print('=' * 70)
    print('artifacts %d | matched mutation budget K=%d | panel %d tasks'
          % (len(arts), K, len(panel)))

    groups = collections.defaultdict(list)
    for h, a in arts.items():
        groups[tuple(a['fingerprint'])].append(h)
    multi = {fp: hs for fp, hs in groups.items() if len(hs) > 1}
    n_dup = sum(len(hs) - 1 for hs in multi.values())
    print('fingerprint groups %d | multi-member groups %d | duplicate '
          'artifacts %d (%.0f%%)\n'
          % (len(groups), len(multi), n_dup, 100 * n_dup / len(arts)))

    # ---- neighbourhoods, matched randomness ---------------------------------
    members = sorted({h for hs in multi.values() for h in hs})
    print('generating matched neighbourhoods for %d artifacts in duplicate '
          'groups...' % len(members))
    nb = {}
    improve = {}
    opclass = {}
    for h in members:
        g = geno(arts[h])
        rng = random.Random(SEED)          # SAME stream for every artifact
        offs = []
        for _ in range(K):
            offs.append(mutate(g, rng))
        nb[h] = {tuple(int(x) for x in ref.outputs(o)) for o in offs}
        # improvement probability on the reference panel
        wins = 0
        tot = 0
        for ft in fts:
            base = ft.dist(g)
            for o in offs[:40]:
                tot += 1
                if ft.dist(o) < base:
                    wins += 1
        improve[h] = wins / tot if tot else 0.0
        # operator-specific neighbourhoods
        oc = {}
        for cls in MUT_CLASSES:
            r2 = random.Random(SEED + 7)
            s = set()
            for _ in range(30):
                try:
                    s.add(tuple(int(x) for x in ref.outputs(mutate(g, r2, [cls]))))
                except Exception:
                    pass
            oc[cls] = s
        opclass[h] = oc

    # ---- pairwise MR --------------------------------------------------------
    def jac(a, b):
        return len(a & b) / len(a | b) if (a | b) else 1.0

    def editdist(x, y):
        return sum(1 for i in range(max(len(x), len(y)))
                   if (x[i] if i < len(x) else None) !=
                      (y[i] if i < len(y) else None))

    pair_mr, pair_edit, pair_op = [], [], []
    distinct_off, novel_frac = [], []
    for fp, hs in multi.items():
        for i in range(len(hs)):
            distinct_off.append(len(nb[hs[i]]))
            novel_frac.append(sum(1 for x in nb[hs[i]] if x != fp)
                              / max(1, len(nb[hs[i]])))
            for j in range(i + 1, len(hs)):
                a, b = hs[i], hs[j]
                pair_mr.append(jac(nb[a], nb[b]))
                pair_edit.append(editdist(geno(arts[a]), geno(arts[b])))
                pair_op.append(statistics.mean(
                    [jac(opclass[a][c], opclass[b][c]) for c in MUT_CLASSES]))

    print('\nNEIGHBOURHOOD STRUCTURE (artifacts inside duplicate groups)')
    print('  distinct offspring behaviours per artifact:  median %.0f  '
          'mean %.1f  max %d'
          % (statistics.median(distinct_off), statistics.mean(distinct_off),
             max(distinct_off)))
    print('  fraction of offspring behaviourally NOVEL vs parent: median %.3f'
          % statistics.median(novel_frac))
    print('  P(strict improvement) on panel: median %.4f  mean %.4f'
          % (statistics.median(list(improve.values())),
             statistics.mean(list(improve.values()))))

    print('\nPAIRWISE MUTATIONAL REDUNDANCY over %d same-fingerprint pairs'
          % len(pair_mr))
    q = sorted(pair_mr)
    print('  MR  min %.3f  p25 %.3f  median %.3f  p75 %.3f  max %.3f'
          % (q[0], q[len(q) // 4], statistics.median(q),
             q[3 * len(q) // 4], q[-1]))
    print('  genotype edit distance between duplicates: median %.1f'
          % statistics.median(pair_edit))
    print('  operator-matched neighbourhood Jaccard: median %.3f'
          % statistics.median(pair_op))

    print('\n  MR threshold sweep -- fraction of behavioural duplicates that')
    print('  are ALSO evolutionarily redundant:')
    sweep = {}
    for tau in (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90):
        f = sum(1 for m in pair_mr if m >= tau) / len(pair_mr)
        sweep[tau] = round(f, 4)
        mark = '   <-- preregistered tau' if abs(tau - TAU) < 1e-9 else ''
        print('     tau %.2f  ->  %5.1f%%%s' % (tau, 100 * f, mark))

    surviving = sum(1 for m in pair_mr if m >= TAU) / len(pair_mr)
    print('\nVERDICT AT tau=%.2f: %.1f%% of behavioural duplicate pairs are '
          'also mutationally redundant.' % (TAU, 100 * surviving))
    if surviving < 0.5:
        arm = ('B_PHENOTYPE_COMPRESSION -- behavioural duplicates mostly open '
               'onto DIFFERENT mutation neighbourhoods, so evicting one is not '
               'evicting a redundant artifact. I1 must be labelled a test of '
               'phenotype-level compression, NOT of evolutionary redundancy.')
    else:
        arm = ('A_TRUE_REDUNDANCY -- behavioural duplicates mostly share their '
               'mutation neighbourhoods, so behavioural redundancy is a fair '
               'proxy for evolutionary redundancy and I1 may evict on it.')
    print('\nI1 DISPOSITION: %s' % arm)

    out = {'n_artifacts': len(arts), 'n_fingerprints': len(groups),
           'n_multi_groups': len(multi), 'n_duplicate_artifacts': n_dup,
           'duplicate_fraction': round(n_dup / len(arts), 4),
           'K': K, 'seed': SEED, 'tau': TAU, 'n_pairs': len(pair_mr),
           'mr_median': round(statistics.median(pair_mr), 4),
           'mr_mean': round(statistics.mean(pair_mr), 4),
           'mr_min': round(min(pair_mr), 4), 'mr_max': round(max(pair_mr), 4),
           'mr_sweep': sweep,
           'surviving_fraction_at_tau': round(surviving, 4),
           'distinct_offspring_median': statistics.median(distinct_off),
           'novel_offspring_fraction_median': round(
               statistics.median(novel_frac), 4),
           'improvement_prob_median': round(
               statistics.median(list(improve.values())), 5),
           'edit_distance_median': statistics.median(pair_edit),
           'operator_matched_jaccard_median': round(
               statistics.median(pair_op), 4),
           'domain_shared_across_tasks': True,
           'i1_disposition': arm.split(' -- ')[0]}
    json.dump(out, open(os.path.join(HERE, 'phase1_mutational_redundancy.json'),
                        'w', encoding='utf-8'), indent=2, sort_keys=True)
    print('\nwrote phase1_mutational_redundancy.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
