"""Negative-transfer world (prereg section 9, SIGNAL_REVISION gate).

N1 (measured by arms.py NEG): frozen z* on NEG tasks vs H1 - does the old signal mislead?
N2 (this file): adaptation WITHOUT overwriting history.
    - development episodes on NEG tier2 with the CURRENT machinery (both z* and no-z,
      both metered) recording passes into a NEW history layer;
    - old history preserved; successor tables = old MERGED WITH new layer;
    - meta-select successor genome z' on a NEG tier2 discovery subset;
    - compare z' vs frozen z* vs H1 on NEG tier3 (never used for selection).
"""
import json, random, sys, time
from multiprocessing import Pool
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S
import arena as A
import zsig as Z
import dev as D

BUDGET = 200_000
SEEDS = 12
STATE = 'F:/SerendipityA/runs/dev_state.json'


def main():
    st = json.load(open(STATE))
    assert st['phase'] == 'E-FROZEN'
    tasks = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    neg2 = [t for t in tasks if t['family'] == 'NEG' and t['tier'] == 2]
    neg3 = [t for t in tasks if t['family'] == 'NEG' and t['tier'] == 3]

    # ---- N2a: development on NEG tier2 (z* arm + no-z arm), new history layer
    res_zs = D.run_block(neg2, st, st['zstar'], 'hist', SEEDS, BUDGET)
    res_no = D.run_block(neg2, st, None, 'hist', SEEDS, BUDGET)
    meter = sum(r['calls'] for r in res_zs) + sum(r['calls'] for r in res_no)
    new_hist = A.History()
    hoard = A.Hoard.load(st['hoard'])
    n_new = 0
    for r in res_zs + res_no:
        if r['solved']:
            new_hist.merge(A.History.load(r['hist']))
            D.retain_from(r, hoard)
            n_new += 1
    hoard.freeze()
    print('[N2a] NEG tier2 dev: z* solves=%d/%d  no-z solves=%d/%d  new episodes=%d'
          % (sum(r['solved'] for r in res_zs), len(res_zs),
             sum(r['solved'] for r in res_no), len(res_no), n_new))

    # successor state: old history PRESERVED, new layer merged on top
    old_hist = A.History.load(st['history'])
    comb = A.History.load(st['history'])
    comb.merge(new_hist)
    st2 = dict(st)
    st2['hoard'] = hoard.dump()
    st2['history'] = comb.dump()
    json.dump(dict(old_episodes=old_hist.episodes, new_episodes=new_hist.episodes,
                   combined=comb.episodes),
              open('F:/SerendipityA/runs/neg_layers.json', 'w'))

    # ---- N2b: meta-select successor genome on NEG tier2 discovery subset
    disc = neg2[:6]
    gP, rowsP, m2 = D.meta_search(st2, disc, 'hist', 'Z1-meta-NEG', 303)
    meter += m2
    print('[N2b] successor genome zP=%s' % (gP,))

    # ---- N2c: NEG tier3 (selection-untouched): z' vs frozen z* vs H1
    out = {}
    for label, state, genome in (('H1', st, None), ('ZSTAR', st, st['zstar']),
                                 ('ZPRIME', st2, list(gP))):
        res = D.run_block(neg3, state, genome, 'hist', SEEDS, BUDGET)
        meter += sum(r['calls'] for r in res)
        ns = sum(r['solved'] for r in res)
        by = {}
        for r in res:
            by.setdefault(r['tid'], []).append(r['solved'])
        out[label] = dict(rate=ns / len(res),
                          task_rates={t: sum(v) / len(v) for t, v in by.items()})
        print('[N2c] NEG tier3 %-6s solve_rate=%.3f (%d/%d)' % (label, ns / len(res), ns, len(res)))
    out['zprime'] = list(gP)
    out['meta_rows'] = rowsP
    out['meter'] = meter
    json.dump(out, open('F:/SerendipityA/runs/neg_revision.json', 'w'))


if __name__ == '__main__':
    main()
