"""Anti-cheat probes (prereg section 10). Each prints PASS/FAIL with evidence."""
import json, sys
sys.path.insert(0, 'F:/SerendipityA/src')
import substrate as S
import arena as A
import zsig as Z


def main():
    ok = True

    def probe(name, cond, note=''):
        nonlocal ok
        ok &= bool(cond)
        print('%-42s %s  %s' % (name, 'PASS' if cond else 'FAIL', note))

    bat = json.load(open('F:/SerendipityA/runs/battery.json'))['tasks']
    st = json.load(open('F:/SerendipityA/runs/dev_state.json'))

    # 1. DEV/CONF target overlap
    dev = {tuple(t['target']) for t in bat if t['family'] == 'DEV'}
    conf = {tuple(t['target']) for t in bat if t['family'] == 'CONF'}
    probe('DEV/CONF target overlap', not (dev & conf))

    # 2. No learner-visible identity: the search job tuple carries only (target-as-oracle,
    #    n_out, seed, budget); verified structurally: Oracle exposes one bit.
    orc = A.Oracle((0x123,), 1, 5)
    try:
        r = orc(((0, 0, 0),))
        probe('oracle returns only False on miss', r is False)
    except Exception:
        probe('oracle returns only False on miss', False)

    # 3. Budget enforcement: no calls after exhaustion
    orc = A.Oracle((0x123,), 1, 2)
    orc(((0, 0, 0),)); orc(((0, 0, 1),))
    try:
        orc(((0, 0, 2),))
        probe('oracle hard-stops at budget', False)
    except A.Exhausted:
        probe('oracle hard-stops at budget', True)

    # 4. z closure holds no oracle and no targets: inspect cell contents
    hist = A.History.load(st['history'])
    z = Z.make_z(tuple(st['zstar']), Z.tables_from_history(hist))
    cells = z.__closure__ or ()
    bad = [c for c in cells if isinstance(c.cell_contents, (A.Oracle,))]
    probe('z closure contains no Oracle', not bad)
    # z-table provenance: every table key must be traceable to a recorded DEV pass
    # (recur is the superset of all record_pass wire behaviors; anc/cooc/solved derive
    # from the same calls). Coincidence with an eval-family target is reported as DATA
    # (shared hidden structure), not treated as leakage; leakage would be a key with NO
    # dev provenance.
    tabs = Z.tables_from_history(hist)
    prov = set(hist.recur) | set(hist.anc)
    orphan = [k for T in tabs for k in T if k not in prov]
    probe('every z-table key has dev-pass provenance', not orphan,
          'orphans=%d' % len(orphan))
    eval_targets = set()
    for t in bat:
        if t['family'] in ('CONF', 'ALIEN', 'STRUCT', 'NEG'):
            for x in t['target']:
                eval_targets.add(int(x, 16))
    coinc = sorted({k for T in tabs for k in T if k in eval_targets})
    dev_solved = {int(t['target'][0], 16) for t in bat if t['family'] == 'DEV'}
    print('    [data] table keys coinciding with eval-family targets: %d (%d of them are '
          'solved DEV targets = shared structure)' % (len(coinc),
          sum(1 for b in coinc if b in dev_solved)))

    # 5. hoard has no evaluation-family witness program
    wit = {tuple(tuple(i) for i in t['witness']) for t in bat
           if t['family'] in ('CONF', 'ALIEN', 'STRUCT', 'NEG')}
    hoard = A.Hoard.load(st['hoard'])
    probe('no evaluation-family witness in hoard',
          not (set(hoard.by_beh.values()) & wit))
    # ...and no hoard entry's OUTPUT equals an evaluation-family single-output target
    outleak = [b for b in hoard.by_beh if b in eval_targets]
    probe('no hoard entry outputs an eval-family target', not outleak,
          'hits=%d' % len(outleak))

    # 6. inventory identity H1/H2/H3: same state blob feeds all arms (structural: arms.py
    #    loads one hoard object per worker regardless of arm)
    src = open('F:/SerendipityA/src/arms.py').read()
    probe('arms share one hoard load path', src.count("A.Hoard.load(state['hoard'])") == 1)

    # 7. discovery/confirmation segregation: meta-search touched DEV only
    src = open('F:/SerendipityA/src/dev.py').read()
    probe('dev.py never selects CONF/ALIEN/STRUCT/NEG',
          all(f not in src for f in ("'CONF'", "'ALIEN'", "'STRUCT'", "'NEG'")))

    # 8. task/family id reaches neither search nor z: search() signature has no id param
    import inspect
    sig = inspect.signature(A.search)
    probe('search() has no task/family identity param',
          all(p not in sig.parameters for p in ('tid', 'task_id', 'family')))

    print('ALL PROBES:', 'PASS' if ok else 'FAIL')
    json.dump(dict(all_pass=bool(ok)), open('F:/SerendipityA/runs/anticheat.json', 'w'))


if __name__ == '__main__':
    main()
