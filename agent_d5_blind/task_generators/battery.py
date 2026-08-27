"""Battery composer + oracle-side difficulty strata. Spec: PREREG-TASKS s6.

Strata are functions of generator/oracle properties ONLY (witness length,
composition depth, family) — never of navigator outcomes. Battery acceptance
additionally rejects tasks outside the calibrated feasibility band using
FROZEN M0 calibration on ENGINEERING seeds (constitution s19) — that rejection
rule is part of the frozen generator config, applied identically before any
evidence run.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from families import gen_task


def stratum(task):
    w = len(task['witness'])
    if w <= 4:
        return 'EASY'
    if w <= 8:
        return 'MEDIUM'
    if w <= 14:
        return 'HARD'
    return 'VERY_HARD'


def compose(family_quotas, seed_base, stratum_quotas=None, max_scan=2000):
    """Deterministically scan seeds from seed_base filling per-family (and
    optional per-family-stratum) quotas. Returns (tasks, manifest)."""
    tasks, manifest = [], []
    for fam, quota in family_quotas.items():
        got = {}
        n = 0
        for off in range(max_scan):
            if n >= quota:
                break
            t = gen_task(fam, seed_base + off)
            st = stratum(t)
            if stratum_quotas and fam in stratum_quotas:
                cap = stratum_quotas[fam].get(st, 0)
                if got.get(st, 0) >= cap:
                    continue
            got[st] = got.get(st, 0) + 1
            n += 1
            tasks.append(t)
            manifest.append({'family': fam, 'seed': t['seed'], 'stratum': st,
                             'wlen': len(t['witness']),
                             'domain_size': len(t['table'])})
        if n < quota:
            raise RuntimeError(f'{fam}: only {n}/{quota} tasks in {max_scan} seeds')
    return tasks, manifest


def write_manifest(manifest, path):
    json.dump({'n': len(manifest), 'tasks': manifest}, open(path, 'w'), indent=1)
