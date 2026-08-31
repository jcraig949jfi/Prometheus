"""Mechanical G0 verdict from results/substrate_preflight.json against the
FROZEN gates of PREREG-PREFLIGHT.md section 5. No judgment calls in here."""
import json, os, sys

GATES = {
    'G0a_min_classes': 120,
    'G0b_min_pf2_reach': 0.30,
    'G0c_min_navigators': 2, 'G0c_nav_reach': 0.25, 'G0c_max_ratio': 3.0,
    'G0d_max_rel_drop': 0.80,
    'G0e_max_pp_delta': 0.25,
}


def evaluate(path):
    r = json.load(open(path))
    a = r['assays']
    out = {'gates': {}, 'inputs': {}}

    pf1 = a['PF1']['distinct_classes']
    out['inputs']['PF1_classes'] = pf1
    out['gates']['G0a'] = pf1 >= GATES['G0a_min_classes']

    pf2 = a['PF2']['reach_rate']
    out['inputs']['PF2_reach'] = pf2
    out['gates']['G0b'] = pf2 >= GATES['G0b_min_pf2_reach']

    navs = {n['navigator']: n['reach_rate'] for n in a['PF3']['navigators']}
    out['inputs']['PF3_reach'] = navs
    ok_count = sum(1 for v in navs.values() if v >= GATES['G0c_nav_reach'])
    live = [v for v in navs.values() if v >= 0.05]
    ratio = (max(live) / min(live)) if live else float('inf')
    out['inputs']['PF3_ratio'] = round(ratio, 3)
    out['gates']['G0c'] = (ok_count >= GATES['G0c_min_navigators']
                           and ratio <= GATES['G0c_max_ratio'])

    best = a['PF4']['best_navigator']
    base = navs[best]
    drops = {ab['ablated']: (base - ab['reach_rate']) / base if base else 1.0
             for ab in a['PF4']['ablations']}
    out['inputs']['PF4_base'] = {best: base}
    out['inputs']['PF4_rel_drops'] = {k: round(v, 3) for k, v in drops.items()}
    out['gates']['G0d'] = all(v <= GATES['G0d_max_rel_drop'] for v in drops.values())

    pf5 = a['PF5']['reach_rate']
    out['inputs']['PF5_reach'] = pf5
    out['gates']['G0e'] = abs(pf5 - pf2) <= GATES['G0e_max_pp_delta']

    out['G0'] = all(out['gates'].values())
    out['verdict'] = 'G0_PASS' if out['G0'] else 'SUBSTRATE_INVALID'
    out['frozen_gates'] = GATES
    out['main_comparator_frozen'] = max(navs, key=navs.get)
    return out


if __name__ == '__main__':
    here = os.path.dirname(__file__)
    path = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(here, '..', 'results', 'substrate_preflight.json')
    v = evaluate(path)
    outp = os.path.join(here, '..', 'results', 'g0_verdict.json')
    json.dump(v, open(outp, 'w'), indent=1)
    print(json.dumps(v, indent=1))
