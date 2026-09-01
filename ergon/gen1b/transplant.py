"""ERGON GEN-1B / PHASE 8 -- MEMORY TRANSPLANT, design and runnable pilot.

THE QUESTION Gen-1 cannot answer. Gen-1's estimand is "policy + induced
trajectory". If a policy wins, the win may be a better PERSISTENT SUBSTRATE or
merely a luckier developmental path. Those are indistinguishable inside Gen-1
because the library and the trajectory that built it are confounded by
construction.

THE TRANSPLANT SEPARATES THEM. Take the terminal library each arm produced,
FREEZE it, and hand it to a fresh searcher on a HELD-OUT battery the library
never developed against. Every arm then gets the same searcher, the same
budget, the same tasks, and the same fresh random stream. The only thing that
differs is which 64 artifacts it starts with. There is no developmental
trajectory left to take credit: the trajectory ended when the library was
frozen.

    GOOD POLICY -> LUCKY TRAJECTORY
        transplanted libraries perform alike on held-out tasks
    GOOD POLICY -> BETTER PERSISTENT SUBSTRATE
        the winning arm's libraries still win after transplant

HELD-OUT BATTERY. Gen-1 used the 42 non-control F1-F4 tasks. D-5's manifest
also contains 20 ALIEN tasks, generated from families the developmental
lineages never touched, plus CTRL and NEGX. ALIEN is the natural held-out
challenge set and was already used by D-5 for its own (failed) transfer gate
G7, so its difficulty is characterised rather than guessed.

IMPORTANT INHERITED PRIOR, and it is discouraging. D-5's G7 measured frozen
alien transfer at +5pp with p = 0.26 -- NOT ESTABLISHED. So a transplant is
being run on an axis where the accumulation effect itself did not transfer.
The transplant should be powered against a SMALLER effect than Gen-1, not a
larger one, and its most likely outcome is a null. That is stated before it
runs.

STATUS: design plus a runnable pilot. Not executed as a scored experiment
without authorisation; the brief says the deliverable here is primarily the
design.

Run (pilot):  python -m ergon.gen1b.transplant --pilot --lineages 3
"""
import argparse
import collections
import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))
from ergon.gen1a import persistence as P            # noqa: E402
sys.path.insert(0, os.path.join(P.D5, 'task_generators'))
from families import gen_task                       # noqa: E402
import m1 as M1                                     # noqa: E402

RES = os.path.join(HERE, 'gen1_results')
ARMS = ('I0', 'I1', 'I2', 'I3')
HELDOUT = ('ALIEN',)


def heldout_tasks():
    man = json.load(open(os.path.join(P.D5, 'results', 'task_manifest.json'),
                         encoding='utf-8'))
    return [m for m in man['tasks'] if m['family'] in HELDOUT]


def terminal_libraries(arm, lineages):
    """The frozen terminal library each Gen-1 lineage ended with."""
    out = {}
    for L in lineages:
        p = os.path.join(RES, 'rows_%s_%d.jsonl' % (arm, L))
        sp = os.path.join(RES, 'summary_%s_%d.json' % (arm, L))
        if not os.path.exists(sp):
            continue
        s = json.load(open(sp, encoding='utf-8'))
        out[L] = s['final_library']          # hashes; genotypes via per_artifact
    return out


def run_frozen(library, tasks, budget, seed):
    """A fresh searcher, a FROZEN library (no admission, no eviction, no
    accumulation), on held-out tasks. The library cannot change, so nothing
    developmental can happen during the measurement."""
    solved = 0
    for i, m in enumerate(tasks):
        t = gen_task(m['family'], m['seed'])
        v = {'domain': t['domain'], 'table': t['table']}
        res = M1.m1_rx(v, random.Random(seed + i), budget, list(library))
        solved += 1 if res['solved'] else 0
    return solved / len(tasks)


def design():
    return {
        'name': 'MEMORY_TRANSPLANT / RESIDUAL CAPABILITY TEST',
        'question': ('does a library produced by a superior retention policy '
                     'carry transferable capability once separated from the '
                     'developmental trajectory that created it?'),
        'estimand': ('the causal effect of LIBRARY CONTENT ALONE on held-out '
                     'findability, with the developmental trajectory removed '
                     'by freezing. This is STRICTLY NARROWER than Gen-1 and is '
                     'the reason the experiment is worth running.'),
        'design': {
            'unit': 'lineage-derived library (one per Gen-1 lineage per arm)',
            'n': '30 libraries per arm, paired by originating lineage index',
            'arms': 'the terminal libraries of I0, I1, I2, I3',
            'battery': '20 held-out ALIEN tasks, never seen by any lineage',
            'searcher': 'frozen m1_rx, library passed as a FROZEN extra_pool',
            'accumulation': 'DISABLED -- no admission, no eviction; the library '
                            'cannot change during measurement',
            'budget': '30,000 evaluations per task, identical across arms',
            'pairing': 'library from lineage L in every arm faces the same '
                       'held-out tasks with the same fresh nav seed',
            'controls': [
                'EMPTY library (the M0c-RX comparator, re-run fresh)',
                'RANDOM-GENOTYPE library, size-matched to 64',
                'SHUFFLED-CONTENT library: 64 artifacts sampled across all arms '
                'to break the policy-content relation while holding size',
            ],
        },
        'primary_endpoint': 'held-out CFR over the 20 ALIEN tasks',
        'primary_contrasts': ['best_arm - I0', 'best_arm - I3',
                              'each arm - EMPTY', 'each arm - RANDOM_LIBRARY'],
        'test': ('two-sided paired sign-flip permutation on 30 library-level '
                 'deltas, Holm across the reported contrasts'),
        'inherited_prior': ('D-5 G7 measured frozen alien transfer at +5pp, '
                            'p=0.26, NOT ESTABLISHED. The transplant is being '
                            'run on an axis where the accumulation effect did '
                            'not itself transfer, so a null is the most likely '
                            'outcome and is worth having on the record.'),
        'stop_conditions': [
            'if no Gen-1 arm separates from I0, there is no "superior policy" '
            'to transplant and the experiment reduces to a re-test of D-5 G7 -- '
            'run the EMPTY and RANDOM controls only, or do not run at all',
            'if held-out CFR is at floor (near 0) for every arm including the '
            'empty control, the battery cannot discriminate and the readout is '
            'bounded at zero -- report ALIEN_BATTERY_UNINFORMATIVE',
            'if held-out CFR is at ceiling for every arm, likewise',
        ],
        'what_it_cannot_show': (
            'a transplant null does NOT show the Gen-1 effect was unreal. It '
            'shows the effect did not survive separation from its trajectory, '
            'which is a different and narrower claim.'),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true')
    ap.add_argument('--lineages', type=int, default=3)
    ap.add_argument('--budget', type=int, default=30000)
    a = ap.parse_args()

    d = design()
    print('ERGON GEN-1B PHASE 8 -- MEMORY TRANSPLANT DESIGN')
    print('=' * 70)
    print(json.dumps(d, indent=2, sort_keys=True))

    tasks = heldout_tasks()
    print('\nheld-out battery: %d ALIEN tasks' % len(tasks))

    cost = None
    if a.pilot:
        print('\nPILOT: timing an empty-library pass to price the design')
        t0 = time.time()
        cfr = run_frozen([], tasks, a.budget, 999000)
        secs = time.time() - t0
        per_lib = secs
        total = per_lib * a.lineages * 4
        cost = {'seconds_per_library': round(per_lib, 1),
                'empty_library_heldout_cfr': round(cfr, 4),
                'projected_seconds_30_lineages_4_arms': round(per_lib * 30 * 4, 1),
                'projected_minutes': round(per_lib * 30 * 4 / 60, 1),
                'organism_evaluations': 30 * 4 * len(tasks) * a.budget}
        print('  one library over %d held-out tasks: %.1f s (empty-library '
              'CFR %.3f)' % (len(tasks), per_lib, cfr))
        print('  projected 30 lineages x 4 arms: %.1f min, %d organism-evals'
              % (per_lib * 30 * 4 / 60, 30 * 4 * len(tasks) * a.budget))
        print('  plus 3 controls x 30: %.1f min'
              % (per_lib * 30 * 3 / 60))

    out = {'design': d, 'heldout_tasks': len(tasks), 'pilot_cost': cost}
    json.dump(out, open(os.path.join(HERE, 'phase8_transplant_design.json'),
                        'w', encoding='utf-8'), indent=2, sort_keys=True)
    print('\nwrote phase8_transplant_design.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
