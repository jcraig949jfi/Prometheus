"""
C-FP-1: Isospectral Object Detection — Charon
===============================================
Find pairs of L-functions with identical spectral fingerprints (same Lhash)
but different algebraic properties. These are the "isospectral drums" —
what the spectrum misses IS a new invariant.

The L-function hash (Lhash) encodes the first few zeros of the L-function.
Objects sharing an Lhash are numerically isospectral. If they come from
different algebraic origins (e.g., an EC and an MF, or two non-isomorphic
NF fields), the difference reveals structure invisible to the spectrum.
"""
import psycopg2
import json
import time
from collections import defaultdict, Counter

def run():
    t0 = time.time()
    conn = psycopg2.connect(
        host='localhost', port=5432,
        dbname='lmfdb', user='postgres', password='prometheus'
    )
    cur = conn.cursor()

    # ── Step 1: Find all Lhash collision groups ──
    print("=" * 70)
    print("C-FP-1: ISOSPECTRAL OBJECT DETECTION")
    print("=" * 70)

    print("\n[1/5] Finding Lhash collision groups...")
    cur.execute('''
        SELECT "Lhash", count(*) as cnt
        FROM lfunc_lfunctions
        WHERE "Lhash" IS NOT NULL AND "Lhash" != ''
        GROUP BY "Lhash"
        HAVING count(*) > 1
        ORDER BY count(*) DESC
    ''')
    collision_groups = cur.fetchall()
    total_collisions = len(collision_groups)
    total_objects_in_collisions = sum(cnt for _, cnt in collision_groups)
    max_group = collision_groups[0][1] if collision_groups else 0
    print(f"  Collision groups: {total_collisions:,}")
    print(f"  Objects in collisions: {total_objects_in_collisions:,}")
    print(f"  Largest group: {max_group}")
    print(f"  Time: {time.time()-t0:.1f}s")

    # Size distribution
    size_dist = Counter(cnt for _, cnt in collision_groups)
    print(f"\n  Group size distribution:")
    for size in sorted(size_dist.keys())[:15]:
        print(f"    size {size}: {size_dist[size]:,} groups")
    if len(size_dist) > 15:
        print(f"    ... ({len(size_dist)} distinct sizes)")

    # ── Step 2: Classify collision groups by origin diversity ──
    print(f"\n[2/5] Classifying collision groups by origin type...")

    def parse_origin_type(origin):
        """Extract the mathematical object type from the LMFDB origin string."""
        if not origin:
            return "unknown"
        parts = origin.split("/")
        if len(parts) >= 2:
            return parts[0]  # EllipticCurve, ModularForm, ArtinRepresentation, etc.
        return origin

    # Sample the top collision groups + a random sample of smaller ones
    groups_to_examine = collision_groups[:200]  # Top 200 by size
    # Also grab some size-2 groups (most common, most likely cross-origin)
    size2_groups = [g for g in collision_groups if g[1] == 2][:500]

    all_groups = list(set(groups_to_examine + size2_groups))
    print(f"  Examining {len(all_groups)} collision groups...")

    cross_origin = []  # Groups with multiple origin types
    same_origin = []   # Groups with single origin type
    cross_origin_details = []

    for i, (lhash, cnt) in enumerate(all_groups):
        if i % 100 == 0 and i > 0:
            print(f"    ... processed {i}/{len(all_groups)}")

        cur.execute('''
            SELECT origin, label, conductor, degree, "Lhash"
            FROM lfunc_lfunctions
            WHERE "Lhash" = %s
        ''', (lhash,))
        members = cur.fetchall()

        origin_types = set(parse_origin_type(m[0]) for m in members)

        if len(origin_types) > 1:
            cross_origin.append({
                'lhash': lhash,
                'count': cnt,
                'origin_types': sorted(origin_types),
                'members': [
                    {
                        'origin': m[0][:60] if m[0] else None,
                        'label': m[1],
                        'conductor': m[2],
                        'degree': m[3],
                    }
                    for m in members
                ]
            })
        else:
            same_origin.append({
                'lhash': lhash,
                'count': cnt,
                'origin_type': list(origin_types)[0] if origin_types else 'unknown',
            })

    print(f"\n  Cross-origin groups: {len(cross_origin)}")
    print(f"  Same-origin groups: {len(same_origin)}")
    print(f"  Time: {time.time()-t0:.1f}s")

    # ── Step 3: Analyze cross-origin collisions ──
    print(f"\n[3/5] Cross-origin collision analysis...")

    if cross_origin:
        # What origin pairs appear?
        pair_counts = Counter()
        for g in cross_origin:
            types = tuple(sorted(g['origin_types']))
            pair_counts[types] += 1

        print(f"  Origin-pair distribution:")
        for pair, count in pair_counts.most_common(20):
            print(f"    {' <-> '.join(pair)}: {count} groups")

        # Show examples
        print(f"\n  Example cross-origin collisions:")
        for g in cross_origin[:10]:
            print(f"\n    Lhash={g['lhash']}, {g['count']} members:")
            for m in g['members']:
                print(f"      {m['origin']} | {m['label']} | cond={m['conductor']} deg={m['degree']}")
    else:
        print("  No cross-origin collisions found in sample!")

    # ── Step 4: Analyze same-origin collisions (isomorphism classes) ──
    print(f"\n[4/5] Same-origin collision analysis...")

    same_origin_types = Counter(g['origin_type'] for g in same_origin)
    print(f"  Same-origin groups by type:")
    for ot, count in same_origin_types.most_common():
        print(f"    {ot}: {count} groups")

    # For EC same-origin collisions: these should be isogeny classes
    ec_same = [g for g in same_origin if g['origin_type'] == 'EllipticCurve']
    if ec_same:
        print(f"\n  EC same-origin collisions: {len(ec_same)} groups")
        print(f"  (Expected: isogenous curves share L-functions)")

    # ── Step 5: The interesting ones — cross-type isospectral pairs ──
    print(f"\n[5/5] Searching for the most interesting collisions...")

    # The real gold: EC <-> ArtinRepresentation, or ModularForm <-> ArtinRepresentation
    # These are instances of proven/conjectured correspondences
    interesting_pairs = [
        ('ArtinRepresentation', 'ModularForm'),
        ('EllipticCurve', 'ModularForm'),
        ('EllipticCurve', 'ArtinRepresentation'),
    ]

    for p in interesting_pairs:
        matches = [g for g in cross_origin if set(g['origin_types']) == set(p)]
        if matches:
            print(f"\n  {p[0]} <-> {p[1]}: {len(matches)} isospectral pairs!")
            for g in matches[:3]:
                print(f"    Lhash={g['lhash']}:")
                for m in g['members']:
                    print(f"      {m['origin']}")
        else:
            print(f"\n  {p[0]} <-> {p[1]}: 0 pairs in sample")

    # ── Save results ──
    results = {
        'total_collision_groups': total_collisions,
        'total_objects_in_collisions': total_objects_in_collisions,
        'max_group_size': max_group,
        'groups_examined': len(all_groups),
        'cross_origin_count': len(cross_origin),
        'same_origin_count': len(same_origin),
        'cross_origin_groups': cross_origin[:50],  # Top 50
        'same_origin_summary': dict(same_origin_types),
        'size_distribution': {str(k): v for k, v in size_dist.items()},
    }

    out_file = 'charon/data/isospectral_hunt.json'
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_file}")

    print(f"\n{'=' * 70}")
    print(f"Total time: {time.time()-t0:.1f}s")
    print(f"{'=' * 70}")

    cur.close()
    conn.close()

if __name__ == '__main__':
    run()
