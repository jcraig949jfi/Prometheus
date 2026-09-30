"""PHASE 2 evaluator -> OUTCOME.json (round-1 fields; classes per PREREG,
precedence INSTRUMENT_FAIL > CONFOUNDED > SIGNAL > NULL, NOTES A5)."""
import json
from analysis import ratio_stats, ci_disjoint

LS = ('16', '32', '64')


def main():
    rows = [json.loads(l) for l in open('rows.jsonl')]
    arms = {}
    for arm in ('TREATMENT', 'CONTROL', 'NULL_TWIN', 'CHEAT', 'POSITIVE_CONTROL'):
        rs = sorted([r for r in rows if r['arm'] == arm], key=lambda r: r['seed_index'])
        st = ratio_stats([r['per_L']['16']['s95'] for r in rs], [r['per_L']['64']['s95'] for r in rs])
        for key in ('s95', 'mean_nonempty', 'var_nonempty', 'frac_nonempty', 'max',
                    'violations', 'audit_mismatch', 'logical_per_1000', 'density', 'largest_cluster_frac'):
            if key in rs[0]['per_L']['16']:
                st[key + '_by_L'] = {L: sum(r['per_L'][L][key] for r in rs) / len(rs) for L in LS}
        arms[arm] = st
    T, N, C, P, X = (arms[a] for a in ('TREATMENT', 'NULL_TWIN', 'CONTROL', 'POSITIVE_CONTROL', 'CHEAT'))
    pos = P['ratio'] >= 4
    cheat = X['ratio'] >= 4
    twin_meets = N['ratio'] >= 4
    disjoint = ci_disjoint(T['ci90'], N['ci90'])
    success = T['ratio'] >= 4 and N['ratio'] <= 2 and disjoint
    fail_clauses = dict(conserving_ratio_below_2=T['ratio'] < 2,
                        twin_ratio_within_conserving_ci=T['ci90'][0] <= N['ratio'] <= T['ci90'][1],
                        positive_control_fails=not pos)
    if not (pos and cheat):
        outcome = 'INSTRUMENT_FAIL'
    elif twin_meets:
        outcome = 'CONFOUNDED'
    elif success:
        outcome = 'SIGNAL'
    else:
        outcome = 'NULL'
    mean_match = {L: N['mean_nonempty_by_L'][L] / T['mean_nonempty_by_L'][L] for L in LS}
    var_ratio = {L: (N['var_nonempty_by_L'][L] / T['var_nonempty_by_L'][L]) if T['var_nonempty_by_L'][L] > 0 else None for L in LS}
    grows = T['ratio'] >= 2
    stupid = [
        dict(explanation='boundary walk ~L makes any size grow with L',
             status='TESTED_BY_TWIN' if grows else 'MOOT: conserving s95 does not grow with L (ratio %.3f)' % T['ratio']),
        dict(explanation='laziness backlog released as lattice fills, not criticality',
             status=('MOOT: no growing cutoff' if not grows else 'NOT_RULED_OUT') +
                    '; stationary defect density by L %s' % {L: round(T['density_by_L'][L], 4) for L in LS}),
        dict(explanation='eps matches mean but not variance',
             status='RECORDED: twin/cons mean ratio %s, variance ratio %s' % (
                 {L: round(v, 3) for L, v in mean_match.items()},
                 {L: (round(v, 3) if v is not None else None) for L, v in var_ratio.items()})),
    ]
    anomalies = []
    if any(T['audit_mismatch_by_L'][L] != 0 or T['violations_by_L'][L] != 0 for L in LS):
        anomalies.append('conserving rule shows parity violations or audit mismatch')
    for L in LS:
        if abs(mean_match[L] - 1) > 0.05:
            anomalies.append('twin mean not within 5%% of conserving at L=%s (ratio %.3f) on measurement seeds' % (L, mean_match[L]))
    if T['s95_by_L']['16'] == T['s95_by_L']['64']:
        anomalies.append('conserving s95 identical at L=16 and 64 (%.1f): percentile sits on an integer plateau' % T['s95_by_L']['16'])
    cpu = json.load(open('world_cpu.json'))['core_minutes']
    pcpu = sum(json.load(open(f))['core_minutes'] for f in __import__('glob').glob('pilot_cpu_attempt*.json'))
    out = dict(
        triplicateId='HT-e106e1603b', world='W1', outcome=outcome,
        statistics=arms,
        criterion_as_applied=dict(
            success='R_cons >= 4 AND R_twin <= 2 AND bootstrap 90% CIs disjoint; R = mean_seeds s95(64)/mean_seeds s95(16), 5 seeds',
            R_cons=T['ratio'], R_cons_ci90=T['ci90'], R_twin=N['ratio'], R_twin_ci90=N['ci90'],
            cis_disjoint=disjoint, success_met=success, failure_clauses=fail_clauses,
            R_eager_control=C['ratio'], R_positive=P['ratio'], R_cheat=X['ratio']),
        positive_control_detected=bool(pos), cheat_detected=bool(cheat),
        null_twin_meets_success=bool(twin_meets),
        stupid_explanations_status=stupid, anomalies=anomalies,
        core_minutes=round(cpu + pcpu, 4), attempts=dict(pilot=1, pilot_repairs=0, phase2=1),
        notes='Pilot passed on attempt 1 (PILOT.json). eps from pilot calibration.json, largest eps within the 5% mean band (NOTES A2). '
              'Calibration target (conserving mean) was visible in the pilot; disclosed in NOTES.md. Lens L6 recorded only.')
    json.dump(out, open('OUTCOME.json', 'w'), indent=1)
    print(outcome, json.dumps(out['criterion_as_applied']))
    for a, st in arms.items():
        print(a, round(st['ratio'], 3), [round(x, 3) for x in st['ci90']], st['s95_by_L'])
    print(anomalies)


if __name__ == '__main__':
    main()
