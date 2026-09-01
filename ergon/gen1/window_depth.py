"""Ergon Gen-1: how deep is D-5's memory, in tasks?

D-5's VERDICT.md already flagged saturation QUALITATIVELY, in its note to a
successor: "design task ecologies where library content cannot saturate."
Nothing quantified it, because the trajectory was never persisted. It is now.

This computes, exactly and from the persisted records alone:
  - the admission position of every artifact in each terminal library
  - therefore the DEPTH of memory the frozen I0 policy actually retains
  - the fraction of the developmental history that is absent from the library
    at the moment the endpoint is measured
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PERSISTED = os.path.join(HERE, 'persisted')


def main():
    print('=== MEMORY DEPTH OF THE FROZEN I0 POLICY ===')
    print('(cap 64, most-recent-first eviction, ~4.03 admissions/task)\n')
    rows = []
    for j in range(5):
        p = os.path.join(PERSISTED, 'library_lineage_%d.json' % j)
        if not os.path.exists(p):
            raise ValueError('missing persisted record: %s' % p)
        rec = json.load(open(p, encoding='utf-8'))
        evs = sorted(rec['events'], key=lambda e: e['position'])
        last_pos = evs[-1]['position']

        # admission position of each artifact hash (latest admission wins,
        # matching update_library's move-to-end on readmission)
        admitted_at = {}
        for e in evs:
            for a in e['admissions']:
                admitted_at[a['artifact_hash']] = e['position']

        final_hashes = [e['artifact_hash'] for e in
                        sorted(rec['final_library'],
                               key=lambda x: x['position_in_library'])]
        positions = [admitted_at[h] for h in final_hashes if h in admitted_at]
        if len(positions) != len(final_hashes):
            raise ValueError('lineage %d: %d of %d terminal artifacts have no '
                             'admission event' % (j, len(final_hashes) -
                                                  len(positions),
                                                  len(final_hashes)))
        oldest = min(positions)
        depth = last_pos - oldest + 1
        forgotten = oldest            # positions 0..oldest-1 fully evicted
        rows.append({'lineage': j, 'last_position': last_pos,
                     'oldest_surviving_admission': oldest,
                     'memory_depth_tasks': depth,
                     'positions_fully_forgotten': forgotten,
                     'fraction_history_absent': forgotten / (last_pos + 1.0)})
        print('lineage %d: terminal library spans admission positions %d..%d'
              % (j, oldest, max(positions)))
        print('           memory depth = %d of %d tasks; positions 0..%d are '
              'entirely absent (%.0f%% of the lineage)'
              % (depth, last_pos + 1, oldest - 1,
                 100.0 * forgotten / (last_pos + 1.0)))

    depths = [r['memory_depth_tasks'] for r in rows]
    absent = [r['fraction_history_absent'] for r in rows]
    print('\nmemory depth across lineages ... %s tasks (mean %.1f)'
          % (depths, sum(depths) / 5.0))
    print('history absent at endpoint ..... %.0f%%-%.0f%% (mean %.0f%%)'
          % (100 * min(absent), 100 * max(absent),
             100 * sum(absent) / 5.0))
    print('\nREADING: under the frozen policy the library is a ROLLING WINDOW')
    print('over the most recent ~%d tasks, not an accumulation over 58.'
          % (sum(depths) / 5.0))
    print('D-5 flagged saturation qualitatively; this is its depth.')

    out = os.path.join(HERE, 'window_depth.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'per_lineage': rows,
                   'mean_depth_tasks': sum(depths) / 5.0,
                   'mean_fraction_history_absent': sum(absent) / 5.0}, f,
                  indent=1)
        f.flush()
    print('\nwrote', out)


if __name__ == '__main__':
    main()
