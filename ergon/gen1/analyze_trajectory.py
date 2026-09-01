"""Ergon Gen-1: what the persisted trajectory actually contains.

Two jobs.

1. STATE THE STRENGTH OF CHECK E. Agreement on an unsolved row (solved=False,
   first_solve=None, evals=30000) is nearly free -- most arms produce it. The
   informative comparisons are the SOLVED rows and, far more so, the terminal
   library, which matches only if every mutation draw agreed. Report both so a
   reader can discount the cheap part.

2. CHECK THE 08-31 PRE-SCREEN AGAINST MEASURED DATA. That pre-screen estimated
   saturation position, admissions per task and turnover from the evidence
   ledger's library_size_at_start column. The persisted trajectory now measures
   them directly. Where estimate and measurement disagree, the measurement wins
   and the disagreement is reported.
"""
import json
import os

import d5_paths

HERE = os.path.dirname(os.path.abspath(__file__))
PERSISTED = os.path.join(HERE, 'persisted')
LIB_CAP = 64


def load_records():
    recs = []
    for j in range(5):
        p = os.path.join(PERSISTED, 'library_lineage_%d.json' % j)
        if not os.path.exists(p):
            raise ValueError('no persisted record for lineage %d at %s' % (j, p))
        recs.append(json.load(open(p, encoding='utf-8')))
    return recs


def ledger_rows():
    rows = []
    with open(os.path.join(d5_paths.LEDGERS, 'm1_rows.jsonl'),
              encoding='utf-8') as f:
        for line in f:
            rows.append(json.loads(line))
    if not rows:
        raise ValueError('evidence ledger returned zero rows')
    return rows


def main():
    recs = load_records()
    rows = ledger_rows()

    # ---- 1. strength of check E --------------------------------------
    solved = [r for r in rows if r['solved']]
    unsolved = [r for r in rows if not r['solved']]
    print('=== CHECK E: what was actually compared ===')
    print('ledger rows ................ %d' % len(rows))
    print('  solved (informative) ..... %d  (%.1f%%)'
          % (len(solved), 100.0 * len(solved) / len(rows)))
    print('  unsolved (cheap match) ... %d  (%.1f%%)'
          % (len(unsolved), 100.0 * len(unsolved) / len(rows)))
    fs = sorted(r['first_solve'] for r in solved)
    if fs:
        print('  first_solve range ........ %d..%d (each an exact integer match)'
              % (fs[0], fs[-1]))
    n_geno = sum(len(r['final_library']) for r in recs)
    n_instr = sum(len(e['genotype']) for r in recs for e in r['final_library'])
    print('terminal libraries ......... %d ordered genotypes, %d instructions'
          % (n_geno, n_instr))
    print('  -> the load-bearing part: matches only if every draw agreed\n')

    # ---- 2. measured trajectory vs the 08-31 pre-screen ---------------
    print('=== TRAJECTORY, MEASURED (08-31 pre-screen estimate in brackets) ===')
    sat_positions, adm_tot, ev_tot, readm_tot = [], [], [], []
    for r in recs:
        evs = sorted(r['events'], key=lambda e: e['position'])
        sat = next((e['position'] for e in evs
                    if e['library_after_size'] >= LIB_CAP), None)
        sat_positions.append(sat)
        adm = sum(e['admission_count'] for e in evs)
        ev_ = sum(e['eviction_count'] for e in evs)
        readm = sum(1 for e in evs for a in e['admissions'] if a['readmission'])
        adm_tot.append(adm)
        ev_tot.append(ev_)
        readm_tot.append(readm)
        print('lineage %d: saturates at position %s | admissions %d '
              '(%.2f/task) | evictions %d | readmissions %d'
              % (r['lineage'], sat, adm, adm / len(evs), ev_, readm))

    n_tasks = len(recs[0]['events'])
    print('\nsaturation positions ....... %s   [pre-screen said 15-16]'
          % sat_positions)
    print('admissions per task ........ %.2f mean          [pre-screen said ~4.05]'
          % (sum(adm_tot) / (5.0 * n_tasks)))
    print('evictions per lineage ...... %.1f mean          [pre-screen said ~171]'
          % (sum(ev_tot) / 5.0))
    print('turnover (evictions/cap) ... %.2fx              [pre-screen said ~2.67x]'
          % (sum(ev_tot) / 5.0 / LIB_CAP))
    print('readmissions (dedup hits) .. %d total across 5 lineages' % sum(readm_tot))

    # ---- 3. what a retention policy would have to work with ----------
    print('\n=== RETENTION READOUT: variation available to a policy ===')
    all_scores, lengths, uniq = [], [], set()
    for r in recs:
        for e in r['events']:
            for a in e['admissions']:
                if a['source_score'] is not None:
                    all_scores.append(a['source_score'])
                lengths.append(a['length'])
                uniq.add(a['artifact_hash'])
    all_scores.sort()
    print('distinct artifacts admitted  %d' % len(uniq))
    print('admitted-artifact score      min %d / median %d / max %d'
          % (all_scores[0], all_scores[len(all_scores) // 2], all_scores[-1]))
    print('admitted-artifact length     min %d / median %d / max %d'
          % (min(lengths), sorted(lengths)[len(lengths) // 2], max(lengths)))

    # survival: how long does an admitted artifact stay resident?
    lifetimes = []
    for r in recs:
        evs = sorted(r['events'], key=lambda e: e['position'])
        admitted_at = {}
        for e in evs:
            for a in e['admissions']:
                admitted_at[a['artifact_hash']] = e['position']
            for h in e['evictions']:
                if h in admitted_at:
                    lifetimes.append(e['position'] - admitted_at.pop(h))
        for h, pos in admitted_at.items():
            lifetimes.append(evs[-1]['position'] - pos)   # survived to the end
    lifetimes.sort()
    print('artifact lifetime (tasks)    min %d / median %d / max %d'
          % (lifetimes[0], lifetimes[len(lifetimes) // 2], lifetimes[-1]))

    out = os.path.join(HERE, 'trajectory_summary.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'ledger_rows': len(rows), 'solved_rows': len(solved),
                   'terminal_genotypes': n_geno,
                   'terminal_instructions': n_instr,
                   'saturation_positions': sat_positions,
                   'admissions_total': adm_tot, 'evictions_total': ev_tot,
                   'readmissions_total': readm_tot,
                   'distinct_artifacts_admitted': len(uniq),
                   'lifetime_median': lifetimes[len(lifetimes) // 2],
                   'lifetime_max': lifetimes[-1]}, f, indent=1)
        f.flush()
    print('\nwrote', out)


if __name__ == '__main__':
    main()
