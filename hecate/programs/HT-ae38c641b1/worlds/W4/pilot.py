"""Phase 1 pilot: POSITIVE_CONTROL (oracle + uniform), CHEAT, NULL_TWIN
(matched to the oracle's split-depth sequence; see NOTES.md).
One row per arm x seed in pilot_rows.jsonl, flushed."""
import json
import os
import sys
import time

import common as c

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPT = int(sys.argv[1]) if len(sys.argv) > 1 else 1


def main():
    t0 = time.process_time()
    per = {arm: {s: [] for s in c.SEEDS} for arm in ('POSITIVE_CONTROL', 'CHEAT', 'NULL_TWIN')}
    for (k, T, t) in c.CONFIGS:
        w = c.World(k, T, t)
        u = c.run_uniform(w)
        g_ut = c.fit_gamma(u['B'], u['area_true'])
        g_us = c.fit_gamma(u['B'], u['area_sound'])
        base = {'k': k, 'T': T, 't': t, 'lambdaT': c.lamT(k, T), 'D': c.D_of(k)}
        for s in c.SEEDS:
            o = c.run_oracle(w, s)
            g_o = c.fit_gamma(o['B'], o['area'])
            g_o_up = c.fit_gamma(o['B'], o['area'], upper_half=True)
            per['POSITIVE_CONTROL'][s].append(dict(base, uniform=u, gamma_uniform_true=g_ut,
                                                   gamma_uniform_sound=g_us,
                                                   gamma_uniform_true_upper=c.fit_gamma(u['B'], u['area_true'], True),
                                                   oracle={'B': o['B'], 'area': o['area']},
                                                   gamma_oracle=g_o, gamma_oracle_upper=g_o_up,
                                                   oracle_stopped_early=o['stopped_early'],
                                                   oracle_max_depth=o['max_depth']))
            n = c.run_null(w, s, o['depth_seq'])
            per['NULL_TWIN'][s].append(dict(base, trace=n, gamma=c.fit_gamma(n['B'], n['area']),
                                            gamma_oracle=g_o, matched_to='oracle'))
            r = c.cheat_r(k, T)
            ca = [a ** r for a in o['area']]
            per['CHEAT'][s].append(dict(base, trace={'B': o['B'], 'area': ca}, injected_r=r,
                                        gamma=c.fit_gamma(o['B'], ca), gamma_oracle=g_o))
        print(k, T, t, 'done %.1fs' % (time.process_time() - t0), flush=True)
    params = {'KS': c.KS, 'TS': c.TS, 'ROTS': c.ROTS, 'CHECKPOINTS': c.CHECKPOINTS,
              'UNIFORM_LEVELS': c.UNIFORM_LEVELS, 'TRUTH_DEPTH': c.TRUTH_DEPTH,
              'PAD': c.PAD, 'kept_digits': 'even', 'attempt': ATTEMPT}
    cpu = time.process_time() - t0
    with open(os.path.join(HERE, 'pilot_rows.jsonl'), 'w', encoding='utf-8') as f:
        for arm, d in per.items():
            for s, cfgs in d.items():
                f.write(json.dumps({'arm': arm, 'seed': s, 'attempt': ATTEMPT, 'params': params,
                                    'cpu_seconds_total_run': cpu, 'configs': cfgs}) + '\n')
                f.flush()
    print('cpu seconds', cpu)


if __name__ == '__main__':
    main()
