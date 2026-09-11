"""ERGON PROJECT 3 -- shared execution for the experiment and its controls.

The Gen-1B runner (ergon/gen1b/gen1_run.py, blob
577125847aabf6a3087d06935e39701cffc751be, unchanged since Gen-1B) is imported
UNCHANGED and `run_lineage` is called verbatim for every experimental arm.
Project 1 (ergon/gen2/p1_run.py) established the pattern; this module adds
two things:

  1. A process pool over lineages. Every lineage is an independent unit of
     inference (its own nav_base and policy rng, pure functions of the
     lineage index inside the frozen runner), so distributing lineages over
     worker processes changes no number. The Credit context patches module
     globals (physics.mutate, rm_fast.FastTask.dist) and each worker process
     has its own interpreter, so patches never cross lineages.
  2. The CHEAT arm for the cheat control (base s2: "success deliberately
     injected"). `run_lineage_planted` copies the frozen runner's loop
     verbatim and, immediately before task i for i in `plant`, admits the
     oracle-side WITNESS of that task (families.gen_task(...)['witness'], a
     genotype that solves the task by construction) into the library under
     the I0 policy. The witness is oracle information that NO experimental
     arm ever sees; it exists only to show the measurement channel can see a
     retention effect of known size. The experimental arms never call this
     function.

Seed spaces (lineage index L; nav_base = 200000 + 1000 L, policy rng
50000 + L inside the frozen runner):
    Gen-1B      L in   0..29
    Project 1   L in 100..199
    Project 3 cheat controls   L in 200..299   (this module, CHEAT_START)
    Project 3 experiment       L in 300..399   (p3_run.py, EXP_START)
No lineage index is shared between any two of these.
"""
import json
import os
import random
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen1b import gen1_run as G          # noqa: E402  frozen runner
import rm_fast                                  # noqa: E402
import m1 as M1                                 # noqa: E402
from families import gen_task                   # noqa: E402

CHEAT_START = 200
EXP_START = 300
FROZEN_RUNNER_BLOB = '577125847aabf6a3087d06935e39701cffc751be'


def nav_base(L):
    return 200000 + 1000 * L


def battery_and_ref():
    tasks = G.battery()
    t0 = tasks[0]
    tt = gen_task(t0['family'], t0['seed'])
    ref = rm_fast.FastTask({'domain': tt['domain'], 'table': tt['table']})
    return tasks, ref


def run_lineage_planted(tasks, arm, lineage, nb, budget, ref, plant):
    """The frozen runner's loop, copied verbatim, plus the plant. Used ONLY by
    the cheat control. `arm` is the policy label the library runs under
    (I0); the summary carries the plant so the row can never be mistaken
    for an experimental one."""
    rng = random.Random(50000 + lineage)
    lib = G.PolicyLibrary(arm, rng, ref)
    rows = []
    planted = []
    with G.Credit(lib):
        for i, m in enumerate(tasks):
            t = gen_task(m['family'], m['seed'])
            v = {'domain': t['domain'], 'table': t['table']}
            lib.task_index = i
            if i in plant:
                ft_plant = rm_fast.FastTask(v)
                assert ft_plant.dist(t['witness']) == 0, 'witness must solve'
                lib.admit([t['witness']], ft_plant)
                planted.append({'i': i, 'lib_size_after_plant': len(lib)})
            size0 = len(lib)
            res = M1.m1_rx(v, random.Random(nb + i), budget, lib)
            rows.append({'arm': arm, 'lineage': lineage, 'i': i,
                         'family': m['family'], 'seed': m['seed'],
                         'solved': res['solved'],
                         'first_solve': res['first_solve'],
                         'evals': res['evals'], 'lib_size_at_start': size0,
                         'planted': i in plant})
            ft = rm_fast.FastTask(v)
            lib.admit(M1.admissions(res, v), ft)
    final = [G.artifact_hash(g) for g in lib]
    summary = {
        'arm': arm, 'lineage': lineage, 'plant': sorted(plant),
        'planted': planted,
        'solved': sum(1 for r in rows if r['solved']), 'n_tasks': len(rows),
        'cfr': sum(1 for r in rows if r['solved']) / len(rows),
        'evictions': lib.evictions, 'fallbacks': lib.fallbacks,
        'final_library': final,
        'n_artifacts_seen': len(lib.fp),
    }
    return rows, summary


def _work(job):
    """One (label, arm, L) unit. Writes rows_<label>_<L>.jsonl and
    summary_<label>_<L>.json into out; returns (label, L, cfr, seconds)."""
    label, arm, L, budget, out, plant = job
    sp = os.path.join(out, 'summary_%s_%d.json' % (label, L))
    if os.path.exists(sp):
        return label, L, json.load(open(sp, encoding='utf-8'))['cfr'], 0.0
    tasks, ref = battery_and_ref()
    nb = nav_base(L)
    ts = time.time()
    if plant:
        rows, summary = run_lineage_planted(tasks, arm, L, nb, budget, ref,
                                            set(plant))
    else:
        rows, summary = G.run_lineage(tasks, arm, L, nb, budget, ref)
    summary['seconds'] = round(time.time() - ts, 1)
    summary['nav_base'] = nb
    summary['label'] = label
    summary['frozen_runner_blob'] = FROZEN_RUNNER_BLOB
    with open(os.path.join(out, 'rows_%s_%d.jsonl' % (label, L)), 'w',
              encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + '\n')
    json.dump(summary, open(sp, 'w', encoding='utf-8'), sort_keys=True)
    return label, L, summary['cfr'], summary['seconds']


def run_jobs(jobs, workers, log=print):
    """Run the job list over a pool; every result is on disk before it is
    reported. Returns {(label, L): cfr}."""
    os.makedirs(jobs[0][4], exist_ok=True)
    start = time.time()
    done = {}
    with Pool(processes=workers) as pool:
        for k, (label, L, cfr, secs) in enumerate(
                pool.imap_unordered(_work, jobs), 1):
            done[(label, L)] = cfr
            if k % 10 == 0 or k == len(jobs):
                log('  %3d/%d  %s L%d cfr %.3f (%.0fs)   [%.1f min elapsed]'
                    % (k, len(jobs), label, L, cfr, secs,
                       (time.time() - start) / 60))
    return done
