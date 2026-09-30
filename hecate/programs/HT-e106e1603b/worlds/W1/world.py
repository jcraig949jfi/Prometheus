"""PHASE 2: TREATMENT (conserving lazy decoder theta=3), CONTROL (eager
theta=1), and the three pilot arms rerun through the same code path.
eps values are read from the pilot's calibration.json (not recalibrated)."""
import json, time
import core
from analysis import summarize
from pilot import SEEDS, seed_of


def main():
    t0 = time.process_time()
    calib = json.load(open('calibration.json'))['calib']
    params = dict(burn=core.BURN_IN, measured=core.MEASURED, Ls=list(core.LS),
                  check_every=core.CHECK_EVERY)
    with open('rows.jsonl', 'w') as f:
        for arm, theta, use_eps in (('TREATMENT', 3, False), ('CONTROL', 1, False), ('NULL_TWIN', 3, True)):
            for s in SEEDS:
                row = dict(arm=arm, seed_index=s, params=dict(theta=theta, **params), per_L={})
                ch = dict(arm='CHEAT', seed_index=s, params=dict(theta=theta, **params), per_L={},
                          injection='sizes * (L/16)^2 applied to the NULL_TWIN size stream')
                for li, L in enumerate(core.LS):
                    sd = seed_of(arm, s, li)
                    eps = calib[str(L)]['eps'] if use_eps else 0.0
                    r = core.decoder(L, theta, eps, sd)
                    sizes = r.pop('sizes')
                    row['per_L'][str(L)] = dict(seed=sd, eps=eps, **summarize(sizes), **r)
                    if arm == 'NULL_TWIN':
                        ch['per_L'][str(L)] = dict(seed=sd, eps=eps, **summarize(sizes * (L // 16) ** 2))
                f.write(json.dumps(row) + '\n')
                if arm == 'NULL_TWIN':
                    f.write(json.dumps(ch) + '\n')
                f.flush()
        for s in SEEDS:
            row = dict(arm='POSITIVE_CONTROL', seed_index=s, params=params, per_L={})
            for li, L in enumerate(core.LS):
                sd = seed_of('POSITIVE_CONTROL', s, li)
                row['per_L'][str(L)] = dict(seed=sd, **summarize(core.btw(L, sd)['sizes']))
            f.write(json.dumps(row) + '\n'); f.flush()
    cpu = time.process_time() - t0
    json.dump(dict(cpu_seconds=cpu, core_minutes=cpu / 60), open('world_cpu.json', 'w'))
    print('world done cpu_s', round(cpu, 2))


if __name__ == '__main__':
    main()
