"""Instrument validation battery (constitution section 45; PREREG-TASKS s8).

Seven synthetic cases with KNOWN intended classifications. The E/R/F
instrumentation must classify all of them correctly before the evidence
battery freezes. Case 3 uses ablated physics (no length growth) where
unreachability is provable; case 4 uses a validation-scoped length cap (2)
where inexpressibility is provable by exhaustive enumeration — the evidence
battery itself never claims NOT_EXPRESSIBLE without proof, it says UNKNOWN.
"""
import sys, os, json, itertools, random
ROOT = os.path.join(os.path.dirname(__file__), '..')
for d in ('substrate', 'mutation', 'task_generators', 'exact_oracle',
          'reachability_oracle', 'navigators'):
    sys.path.insert(0, os.path.join(ROOT, d))
from rm_vm import run, OPS, PALETTE
from families import gen_task
from oracle import solves
from reachability import classify, classify_ablated_no_growth
from m0 import M0_SUITE

D4 = [(x,) for x in range(4)]


def _all_instructions():
    out = []
    for op, kind in OPS.items():
        for a in range(8):
            if kind == 'reg':
                out.extend((op, a, b) for b in range(8))
            elif kind == 'const':
                out.extend((op, a, c) for c in range(len(PALETTE)))
            elif kind == 'jump':
                out.extend((op, a, k) for k in range(1, 9))
            else:
                out.append((op, a, 0))
    return out


def enumerate_len_le2_behaviors():
    """All behaviors over D4 of programs with length <= 2 (exhaustive)."""
    instrs = _all_instructions()
    behaviors = set()
    for i1 in instrs:
        behaviors.add(tuple(run((i1,), x)[0] for x in D4))
    for i1 in instrs:
        for i2 in instrs:
            behaviors.add(tuple(run((i1, i2), x)[0] for x in D4))
    return behaviors


def main():
    report = {}

    # Case 1: expressible + reachable + easy TO FIND. Findability is
    # per-task heterogeneous even at depth 1 (measured 2026-08-27: SHRC 8/8,
    # MULC3 0/8 at 8000), so 'easy' is selected by engineering probe (2
    # screening seeds) and VALIDATED on fresh navigator seeds — this validates
    # the harness, not a scientific claim.
    easy = []
    for s in range(1500, 1600):
        t = gen_task('F1', s)
        if len(t['witness']) > 4:
            continue
        probe = [M0_SUITE['M0c-RX'](t, random.Random(9000 + s * 2 + j), 2000)['solved']
                 for j in range(2)]
        if all(probe):
            easy.append(t)
        if len(easy) == 5:
            break
    ok1 = all(solves(t['witness'], t) and
              classify(t, t['witness'])['status'] == 'REACHABLE' for t in easy)
    fresh1 = sum(any(M0_SUITE['M0c-RX'](t, random.Random(1600 + i * 3 + j),
                                        2000)['solved'] for j in range(2))
                 for i, t in enumerate(easy))
    report['case1_easy'] = {'n': len(easy), 'classified_ok': ok1,
                            'fresh_seed_found': fresh1,
                            'pass': ok1 and len(easy) == 5 and fresh1 >= 4}

    # Case 2: expressible + reachable + hard to find (long F2 witnesses)
    hard = [t for s in range(1500, 1600)
            for t in [gen_task('F2', s)] if len(t['witness']) >= 16][:5]
    ok2 = all(solves(t['witness'], t) and
              classify(t, t['witness'])['status'] == 'REACHABLE' for t in hard)
    solved2 = sum(M0_SUITE['M0c-RX'](t, random.Random(1700 + i), 2000)['solved']
                  for i, t in enumerate(hard))
    report['case2_hard'] = {'n': len(hard), 'classified_ok': ok2,
                            'm0_solved_at_2000': solved2,
                            'pass': ok2 and solved2 <= 1}

    # Case 3: expressible under full physics, UNREACHABLE under ablated
    # physics — provable: minimal witness > 2 (checked exhaustively below).
    le2 = enumerate_len_le2_behaviors()
    case3 = []
    for s in range(1500, 1560):
        t = gen_task('F1', s)
        vec4 = tuple(out for (inp, out), _ in zip(t['table'], range(4)))
        if len(t['witness']) >= 4 and vec4 not in le2:
            case3.append(t)
        if len(case3) == 3:
            break
    ok3 = all(classify_ablated_no_growth(t, t['witness'])['status'] == 'UNREACHABLE'
              and classify(t, t['witness'])['status'] == 'REACHABLE'
              for t in case3)
    report['case3_ablated_unreachable'] = {'n': len(case3), 'pass': ok3 and len(case3) == 3}

    # Case 4: NOT_EXPRESSIBLE under the validation-scoped cap (len <= 2,
    # domain D4): random palette tables provably absent from the exhaustive
    # length<=2 behavior set.
    rng = random.Random(1800)
    found, checked = 0, 0
    while found < 3 and checked < 200:
        tab = tuple(PALETTE[rng.randrange(len(PALETTE))] for _ in range(4))
        checked += 1
        if tab not in le2:
            found += 1
    report['case4_scoped_unexpressible'] = {
        'found': found, 'checked': checked,
        'le2_behavior_count': len(le2), 'pass': found == 3}

    # Case 5: structure-shared sequence — witnesses share H template fragments
    # (over compositions of depth >= 2; depth-1 witnesses are too short to
    # carry shared fragments)
    f1s = [t for s in range(1500, 1560)
           for t in [gen_task('F1', s)] if len(t['witness']) >= 4][:10]
    def frags(w):
        return {tuple(w[i:i + 2]) for i in range(len(w) - 1)}
    shared = 0
    for a, b in itertools.combinations(f1s, 2):
        if frags(a['witness']) & frags(b['witness']):
            shared += 1
    report['case5_shared_structure'] = {'pairs_sharing_fragments': shared,
                                        'pairs': 45, 'pass': shared >= 10}

    # Case 6: unrelated sequence — CTRL content constants approx independent
    ctrls = [gen_task('CTRL', s) for s in range(1500, 1520)]
    ys = [tuple(t['gen_meta']['ys']) for t in ctrls]
    dup = len(ys) - len(set(ys))
    report['case6_unrelated'] = {'content_dups': dup, 'n': len(ys),
                                 'pass': dup <= 2}

    # Case 7: negative-transfer sequence — oracle-side poison labels exist,
    # learner views are shape-identical to F1/F2 views
    negs = [gen_task('NEGX', s) for s in range(1500, 1510)]
    from families import learner_view
    ok7 = all(t['gen_meta'].get('poisoned') for t in negs) and \
        all(set(learner_view(t).keys()) == {'domain', 'table'} for t in negs)
    report['case7_negative_transfer'] = {'n': len(negs), 'pass': ok7}

    report['ALL_PASS'] = all(v['pass'] for k, v in report.items()
                             if isinstance(v, dict))
    out = os.path.join(ROOT, 'results', 'instrument_validation.json')
    json.dump(report, open(out, 'w'), indent=1)
    print(json.dumps({k: (v['pass'] if isinstance(v, dict) else v)
                      for k, v in report.items()}, indent=1))
    return report


if __name__ == '__main__':
    main()
