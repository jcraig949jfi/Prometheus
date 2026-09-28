"""S7 full matched-compute run (PREREG.md in this directory, frozen before any run).
Pristine baseline arm of C3-SFE-04 at G=200, N=200, E=16, seeds 1001..1012, targets W1_d8 then W1_d16.
Each result is appended to full_run.jsonl and flushed as it completes. EXPLORATORY.
    python3 -B full_run.py   (from the repository root)"""
import json, multiprocessing as mp, os, sys, time
sys.path.insert(0, '.')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'full_run.jsonl')

def one(job):
    from archaeon.campaign3.c3_sfe04 import run_target, TARGETS
    target, seed = job
    t = {x.name: x for x in TARGETS}[target]
    t0 = time.time()
    r = run_target({'arm': 'baseline', 'spec': t.knobs(), 'seed': seed, 'N': 200, 'E': 16, 'G': 200, 'manifests': None})
    r.pop('_res', None)
    return {'target': target, 'seed': seed, 'competence_heldout': r.get('competence_heldout'),
            'first_foothold_gen': r.get('first_foothold_gen'), 'reader': (r.get('competence_heldout') or 0) >= 0.9,
            'wall_s': round(time.time() - t0, 1)}

if __name__ == '__main__':
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            d = json.loads(l); done.add((d['target'], d['seed']))
    jobs = [(t, s) for t in ('W1_d8', 'W1_d16') for s in range(1001, 1013) if (t, s) not in done]
    with mp.Pool(3) as pool, open(OUT, 'a') as f:
        for res in pool.imap_unordered(one, jobs):
            f.write(json.dumps(res) + '\n'); f.flush()
