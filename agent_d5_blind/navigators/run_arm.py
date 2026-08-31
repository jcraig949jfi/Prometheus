"""Evidence/engineering arm runner: one arm x one battery -> JSONL rows.

Row schema (one line per task attempt):
{run_id, mode, arm, lineage, family, seed, stratum, wlen, domain_size,
 solved, first_solve, evals, ladder:{rung:bool}, nav_seed}

Rows are appended atomically per task (document-as-you-go); a run is resumable
by skipping (arm, lineage, family, seed) tuples already present.
"""
import sys, os, json, argparse, random
HERE = os.path.dirname(__file__)
for d in ('..\\task_generators', '..\\substrate', '..\\mutation', '..\\exact_oracle'):
    sys.path.insert(0, os.path.join(HERE, d))
sys.path.insert(0, HERE)
from families import gen_task
from battery import stratum
from m0 import M0_SUITE


def run_battery(arm, manifest, ladder, lineage, nav_seed_base, out_path,
                mode, run_id, extra_kwargs=None):
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path, encoding='utf-8'):
            r = json.loads(line)
            done.add((r['arm'], r['lineage'], r['family'], r['seed']))
    fn = M0_SUITE[arm] if arm in M0_SUITE else None
    assert fn is not None, f'unknown arm {arm}'
    top = max(ladder)
    with open(out_path, 'a', encoding='utf-8') as f:
        for i, m in enumerate(manifest):
            key = (arm, lineage, m['family'], m['seed'])
            if key in done:
                continue
            t = gen_task(m['family'], m['seed'])
            nav_seed = nav_seed_base + i
            res = fn(t, random.Random(nav_seed), top, **(extra_kwargs or {}))
            fs = res['first_solve']
            row = {'run_id': run_id, 'mode': mode, 'arm': arm,
                   'lineage': lineage, 'family': m['family'], 'seed': m['seed'],
                   'stratum': stratum(t), 'wlen': len(t['witness']),
                   'domain_size': len(t['table']), 'solved': res['solved'],
                   'first_solve': fs, 'evals': res['evals'],
                   'ladder': {str(b): (fs is not None and fs <= b) for b in ladder},
                   'nav_seed': nav_seed}
            f.write(json.dumps(row) + '\n')
            f.flush()
            print(m['family'], m['seed'], row['stratum'], 'solved' if res['solved']
                  else 'unsolved', fs, flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--ladder', default='1000,3000,10000,30000')
    ap.add_argument('--lineage', type=int, default=0)
    ap.add_argument('--nav-seed-base', type=int, required=True)
    ap.add_argument('--mode', choices=['engineering', 'evidence'], required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    man = json.load(open(a.manifest))['tasks']
    ladder = [int(x) for x in a.ladder.split(',')]
    run_battery(a.arm, man, ladder, a.lineage, a.nav_seed_base, a.out,
                a.mode, a.run_id)
