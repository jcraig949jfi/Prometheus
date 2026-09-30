"""PHASE 1 pilot: POSITIVE_CONTROL (BTW), NULL_TWIN (bulk-deletion twin,
eps calibrated per L), CHEAT (success injected into the observable).
No treatment s95/ratio is computed here (NOTES A2)."""
import json, sys, time
import numpy as np
import core
from analysis import summarize

ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
SEEDS = range(5)
ARM_CODE = {'POSITIVE_CONTROL': 1, 'NULL_TWIN': 2, 'CHEAT': 2, 'TREATMENT': 3, 'CONTROL': 4}


def seed_of(arm, s, li):
    return 1000 * ARM_CODE[arm] + 10 * s + li


def main():
    t0 = time.process_time()
    calib = {}
    for L in core.LS:
        eps, m0, trace = core.calibrate_eps(L)
        calib[L] = dict(eps=eps, target_mean_nonempty=m0, trace=trace)
    with open('calibration.json', 'w') as f:
        json.dump(dict(attempt=ATTEMPT, calib={str(k): v for k, v in calib.items()}), f, indent=1)
    params = dict(theta=3, burn=core.BURN_IN, measured=core.MEASURED, Ls=list(core.LS),
                  check_every=core.CHECK_EVERY)
    with open('pilot_rows.jsonl', 'w') as f:
        for s in SEEDS:
            row = dict(arm='POSITIVE_CONTROL', seed_index=s, attempt=ATTEMPT, params=params, per_L={})
            for li, L in enumerate(core.LS):
                sd = seed_of('POSITIVE_CONTROL', s, li)
                row['per_L'][str(L)] = dict(seed=sd, **summarize(core.btw(L, sd)['sizes']))
            f.write(json.dumps(row) + '\n'); f.flush()
        for s in SEEDS:
            tw = dict(arm='NULL_TWIN', seed_index=s, attempt=ATTEMPT, params=params, per_L={})
            ch = dict(arm='CHEAT', seed_index=s, attempt=ATTEMPT, params=params, per_L={},
                      injection='sizes * (L/16)^2 applied to the NULL_TWIN size stream')
            for li, L in enumerate(core.LS):
                sd = seed_of('NULL_TWIN', s, li)
                eps = calib[L]['eps']
                r = core.decoder(L, 3, eps, sd)
                sizes = r.pop('sizes')
                tw['per_L'][str(L)] = dict(seed=sd, eps=eps, **summarize(sizes), **r)
                ch['per_L'][str(L)] = dict(seed=sd, eps=eps, **summarize(sizes * (L // 16) ** 2))
            f.write(json.dumps(tw) + '\n'); f.write(json.dumps(ch) + '\n'); f.flush()
    cpu = time.process_time() - t0
    with open(f'pilot_cpu_attempt{ATTEMPT}.json', 'w') as f:
        json.dump(dict(cpu_seconds=cpu, core_minutes=cpu / 60), f)
    print('pilot done cpu_s', round(cpu, 2))


if __name__ == '__main__':
    main()
