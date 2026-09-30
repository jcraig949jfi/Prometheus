"""Pilot evaluator -> PILOT.json. Criterion as fixed in NOTES.md."""
import json
import os
import sys

import common as c

HERE = os.path.dirname(os.path.abspath(__file__))


def load(fn):
    rows = [json.loads(l) for l in open(os.path.join(HERE, fn), encoding='utf-8')]
    by = {}
    for r in rows:
        for cf in r['configs']:
            by.setdefault(r['arm'], {}).setdefault((cf['k'], cf['T'], cf['t']), []).append(cf)
    return rows, by


def pc_check(pc):
    checks = []
    for (k, T, t) in c.CONFIGS:
        if not c.pc_eligible(k, T):
            continue
        cfs = pc[(k, T, t)]
        go = c.mean([x['gamma_oracle'] for x in cfs])
        gu = cfs[0]['gamma_uniform_true']
        target = 2.0 / c.D_of(k)
        ratio = go / gu
        checks.append({'k': k, 'T': T, 't': t, 'gamma_oracle': go, 'gamma_uniform_true': gu,
                       'ratio': ratio, 'target_2_over_D': target,
                       'rel_err': abs(ratio - target) / target,
                       'within_10pct': abs(ratio - target) <= 0.10 * target,
                       'within_20pct': abs(ratio - target) <= 0.20 * target,
                       'oracle_stopped_early_any': any(x['oracle_stopped_early'] for x in cfs)})
    return checks


def arm_ratios(armd):
    ratio, spread = {}, {}
    for cfg in c.CONFIGS:
        cfs = armd[cfg]
        g = c.mean([x['gamma'] for x in cfs])
        go = c.mean([x['gamma_oracle'] for x in cfs])
        ratio[cfg] = (g / go) if (g is not None and go) else None
        per_seed = [x['gamma'] / x['gamma_oracle'] for x in cfs if x['gamma'] is not None and x['gamma_oracle']]
        spread[cfg] = (min(per_seed), max(per_seed)) if per_seed else None
    return ratio, spread


def main():
    attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rows, by = load('pilot_rows.jsonl')
    checks = pc_check(by['POSITIVE_CONTROL'])
    pos = all(ch['within_10pct'] for ch in checks)
    cr, _ = arm_ratios(by['CHEAT'])
    nr, nspread = arm_ratios(by['NULL_TWIN'])
    cheat = c.arm_criterion(cr)
    null = c.arm_criterion(nr)
    out = {
        'positive_meets_success': pos,
        'cheat_detected': cheat['meets'],
        'null_twin_meets_success': null['meets'],
        'pilot_pass': bool(pos and cheat['meets'] and not null['meets']),
        'stats': {
            'positive_control_checks': checks,
            'cheat': {'criterion': cheat, 'ratio': {str(k): v for k, v in cr.items()}},
            'null_twin': {'criterion': null, 'ratio': {str(k): v for k, v in nr.items()},
                          'per_seed_ratio_range': {str(k): v for k, v in nspread.items()},
                          'matched_to': 'oracle (pilot; no treatment exists)'},
            'n_rows': len(rows),
            'cpu_seconds_pilot_run': rows[0]['cpu_seconds_total_run'],
        },
        'attempt': attempt,
    }
    json.dump(out, open(os.path.join(HERE, 'PILOT.json'), 'w', encoding='utf-8'), indent=1)
    print(json.dumps({k: out[k] for k in ('positive_meets_success', 'cheat_detected',
                                          'null_twin_meets_success', 'pilot_pass')}))
    for ch in checks:
        print(ch['k'], ch['T'], ch['t'], round(ch['ratio'], 3), round(ch['target_2_over_D'], 3),
              round(ch['rel_err'], 3), ch['oracle_stopped_early_any'])
    print('cheat', cheat)
    print('null', null)


if __name__ == '__main__':
    main()
