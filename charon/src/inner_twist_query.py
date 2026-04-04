"""
North Star Experiment 2: Inner Twist Query
==========================================
Pull inner twist data for the 163 EC-proximate dim-2 forms.

Inner twists tie modular forms to base forms with trivial character.
If the 163 all have inner twists, the spectral similarity to ECs may
be algebraically explained: they twist back to forms that ARE EC-associated.

Test: Do forms with inner twists cluster differently in zero space?
      Does inner twist structure predict EC-proximity?
"""

import duckdb
import numpy as np
import requests
import json
import time
import logging
from collections import Counter
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"
REPORT_PATH = Path(__file__).parent.parent / "reports"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.inner_twist')


def get_163_labels():
    """Get LMFDB labels for the 163 Type B dim-2 wt-2 forms."""
    duck = duckdb.connect(str(DB_PATH), read_only=True)

    # Type B from disagreement atlas, cross with modular_forms for dim/weight
    rows = duck.execute("""
        SELECT da.object_id, da.label, da.conductor, da.zero_coherence,
               mf.dim, mf.weight, mf.char_order
        FROM disagreement_atlas da
        JOIN modular_forms mf ON da.object_id = mf.object_id
        WHERE da.disagreement_type = 'B'
          AND mf.dim = 2 AND mf.weight = 2
        ORDER BY da.zero_coherence
    """).fetchall()
    duck.close()
    return rows


def query_lmfdb_inner_twists(label):
    """Query LMFDB API for inner twist data of a modular form."""
    # LMFDB API: /api/mf_newforms/?label=X
    url = f"https://www.lmfdb.org/api/mf_newforms/?label={label}&_fields=label,inner_twists,is_cm,is_rm,cm_discs,rm_discs,self_twist_discs,char_order"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('data'):
                return data['data'][0]
        return None
    except Exception as e:
        log.warning(f"Failed to query {label}: {e}")
        return None


def main():
    rows = get_163_labels()
    log.info(f"Found {len(rows)} Type B dim-2 wt-2 forms")

    if not rows:
        log.error("No Type B dim-2 forms found!")
        return

    # Sample: query first 50 from LMFDB (rate limit aware)
    results = []
    n_query = min(len(rows), 50)
    log.info(f"Querying LMFDB for inner twist data on {n_query} forms...")

    for i, (oid, label, cond, coherence, dim, wt, char_ord) in enumerate(rows[:n_query]):
        # LMFDB MF labels: need the newform label (e.g., "100.2.a.a")
        # Our labels might be full or partial — try direct query
        lmfdb_data = query_lmfdb_inner_twists(label)
        result = {
            'object_id': oid,
            'label': label,
            'conductor': cond,
            'coherence': coherence,
            'char_order': char_ord,
            'inner_twists': None,
            'is_cm': None,
            'is_rm': None,
            'self_twist_discs': None,
        }
        if lmfdb_data:
            result['inner_twists'] = lmfdb_data.get('inner_twists')
            result['is_cm'] = lmfdb_data.get('is_cm')
            result['is_rm'] = lmfdb_data.get('is_rm')
            result['self_twist_discs'] = lmfdb_data.get('self_twist_discs')
            log.info(f"  [{i+1}/{n_query}] {label}: inner_twists={result['inner_twists']}, "
                     f"CM={result['is_cm']}, RM={result['is_rm']}, "
                     f"self_twist={result['self_twist_discs']}")
        else:
            log.info(f"  [{i+1}/{n_query}] {label}: no LMFDB data")

        results.append(result)
        time.sleep(0.5)  # Rate limiting

    # Analyze
    log.info("\n" + "=" * 60)
    log.info("INNER TWIST ANALYSIS")
    log.info("=" * 60)

    has_data = [r for r in results if r['inner_twists'] is not None]
    log.info(f"Successfully queried: {len(has_data)}/{len(results)}")

    if has_data:
        n_with_twists = sum(1 for r in has_data if r['inner_twists'] and len(r['inner_twists']) > 1)
        n_cm = sum(1 for r in has_data if r['is_cm'])
        n_rm = sum(1 for r in has_data if r['is_rm'])
        twist_counts = Counter(len(r['inner_twists']) if r['inner_twists'] else 0 for r in has_data)

        log.info(f"With inner twists (>1): {n_with_twists}/{len(has_data)}")
        log.info(f"CM forms: {n_cm}/{len(has_data)}")
        log.info(f"RM forms: {n_rm}/{len(has_data)}")
        log.info(f"Inner twist count distribution: {dict(twist_counts)}")

        # Self-twist discriminants
        all_discs = []
        for r in has_data:
            if r['self_twist_discs']:
                all_discs.extend(r['self_twist_discs'])
        if all_discs:
            log.info(f"Self-twist discriminants: {Counter(all_discs).most_common(10)}")

    # Save results
    out_path = REPORT_PATH / "inner_twist_163_2026-04-03.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    log.info(f"\nResults saved to {out_path}")

    # Character order distribution
    char_dist = Counter(r['char_order'] for r in results)
    log.info(f"Character order distribution: {dict(char_dist)}")


if __name__ == "__main__":
    main()
