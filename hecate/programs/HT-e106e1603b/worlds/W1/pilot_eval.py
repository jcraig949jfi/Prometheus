"""Pilot evaluator -> PILOT.json (NOTES A3, A4)."""
import json, sys
from analysis import ratio_stats

THRESH_SUCCESS = 4.0


def arm_ratio(rows, arm):
    rs = [r for r in rows if r['arm'] == arm]
    rs.sort(key=lambda r: r['seed_index'])
    return ratio_stats([r['per_L']['16']['s95'] for r in rs], [r['per_L']['64']['s95'] for r in rs]), rs


def main():
    rows = [json.loads(l) for l in open('pilot_rows.jsonl')]
    attempt = rows[0]['attempt']
    stats = {}
    for arm in ('POSITIVE_CONTROL', 'NULL_TWIN', 'CHEAT'):
        st, rs = arm_ratio(rows, arm)
        st['s95_by_L_mean'] = {L: sum(r['per_L'][L]['s95'] for r in rs) / len(rs) for L in ('16', '32', '64')}
        st['mean_nonempty_by_L'] = {L: sum(r['per_L'][L]['mean_nonempty'] for r in rs) / len(rs) for L in ('16', '32', '64')}
        stats[arm] = st
    calib = json.load(open('calibration.json'))['calib']
    stats['NULL_TWIN']['eps_by_L'] = {L: calib[L]['eps'] for L in calib}
    stats['NULL_TWIN']['calib_target_mean_by_L'] = {L: calib[L]['target_mean_nonempty'] for L in calib}
    stats['NULL_TWIN']['violations_by_L'] = {L: sum(r['per_L'][L]['violations'] for r in rows if r['arm'] == 'NULL_TWIN') for L in ('16', '32', '64')}
    pos = stats['POSITIVE_CONTROL']['ratio'] >= THRESH_SUCCESS
    cheat = stats['CHEAT']['ratio'] >= THRESH_SUCCESS
    twin = stats['NULL_TWIN']['ratio'] >= THRESH_SUCCESS
    out = dict(positive_meets_success=bool(pos), cheat_detected=bool(cheat),
               null_twin_meets_success=bool(twin), pilot_pass=bool(pos and cheat and not twin),
               stats=stats, attempt=attempt)
    json.dump(out, open('PILOT.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'stats'}))
    for a in stats:
        print(a, round(stats[a]['ratio'], 3), [round(x, 3) for x in stats[a]['ci90']])


if __name__ == '__main__':
    main()
