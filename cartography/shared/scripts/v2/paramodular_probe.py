"""
Paramodular Conjecture Probe (C01)
===================================
Explores the feasibility of testing the Brumer-Kramer Paramodular Conjecture
using LMFDB Siegel modular form data and genus-2 curve Euler factors.

Key finding: LMFDB paramodular forms exist only at levels 1,2 while genus-2
conductors start at 169. Direct modularity matching is NOT possible with
current data. This script performs the feasible consistency checks:

1. Parse genus-2 Euler factors from gce_1000000_lmfdb.txt
2. Compare GL2-type curves (which should match classical forms, not paramodular)
3. Catalog what paramodular data exists and identify the gap
4. Build infrastructure for when paramodular form data at higher levels arrives
"""

import json
import ast
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent.parent  # F:/Prometheus/cartography
LMFDB = BASE / "lmfdb_dump"
G2C_DATA = BASE / "genus2" / "data" / "g2c-data"
G2C_LMFDB_TXT = G2C_DATA / "gce_1000000_lmfdb.txt"


def parse_genus2_euler_factors(max_records=None):
    """Parse genus-2 Euler factors from gce_1000000_lmfdb.txt.

    Each line has format:
    cond:cond:Lhash:min_eqn:disc_sign:igusa_clebsch:root_number:bad_lfactors:
    st_group:aut_grp:geom_aut_grp:torsion:two_selmer:has_sq_sha:loc_solv:glob_solv:
    good_lfactors

    good_lfactors: [[p, a1_p, a2_p], ...] where
    L_p(T) = 1 + a1_p*T + a2_p*T^2 + a1_p*p*T^3 + p^2*T^4
    """
    curves = []
    with open(G2C_LMFDB_TXT, 'r') as f:
        for i, line in enumerate(f):
            if max_records and i >= max_records:
                break
            line = line.strip()
            if not line:
                continue
            parts = line.split(':')
            if len(parts) < 17:
                continue
            try:
                cond = int(parts[0])
                Lhash = parts[2]
                # min_eqn is parts[3], disc_sign is parts[4]
                st_group = parts[8]
                # good_lfactors is the last field (may contain colons in list repr)
                good_str = ':'.join(parts[16:])
                good_lfactors = ast.literal_eval(good_str)

                curves.append({
                    'cond': cond,
                    'Lhash': Lhash,
                    'st_group': st_group,
                    'good_lfactors': good_lfactors,  # [[p, a1, a2], ...]
                    'is_paramodular_candidate': st_group == 'USp(4)',
                })
            except Exception as e:
                continue
    return curves


def load_smf_hecke_nf():
    """Load Siegel modular form Hecke eigenvalue data."""
    with open(LMFDB / "smf_hecke_nf.json", 'r') as f:
        data = json.load(f)
    return data['records']


def load_smf_newforms():
    """Load Siegel modular form newform metadata."""
    with open(LMFDB / "smf_newforms.json", 'r') as f:
        data = json.load(f)
    return data['records']


def load_g2c_curves():
    """Load genus-2 curve metadata from postgres dump."""
    with open(LMFDB / "g2c_curves.json", 'r') as f:
        data = json.load(f)
    return data['records']


def analyze_data_landscape():
    """Catalog what data is available and where the gaps are."""
    print("=" * 70)
    print("PARAMODULAR CONJECTURE DATA LANDSCAPE")
    print("=" * 70)

    # Siegel modular forms
    nf = load_smf_newforms()
    hecke = load_smf_hecke_nf()

    fam_counts = Counter(r['family'] for r in nf)
    print(f"\n--- Siegel Modular Forms (smf_newforms) ---")
    print(f"Total newforms: {len(nf)}")
    for f, c in fam_counts.most_common():
        name = {'K': 'Klingen', 'P': 'Paramodular', 'S': 'Saito-Kurokawa'}[f]
        print(f"  {f} ({name}): {c}")

    P_nf = [r for r in nf if r['family'] == 'P']
    P_levels = sorted(set(r['level'] for r in P_nf))
    print(f"\nParamodular form levels: {P_levels}")
    print(f"Paramodular weight distribution:")
    P_weights = Counter(str(r['weight']) for r in P_nf)
    for w, c in P_weights.most_common(10):
        print(f"  weight {w}: {c} forms")

    K_nf = [r for r in nf if r['family'] == 'K']
    K_levels = sorted(set(r['level'] for r in K_nf))
    print(f"\nKlingen form levels: {min(K_levels)} to {max(K_levels)} ({len(K_levels)} levels)")

    # Hecke eigenvalue availability
    fam_hecke = Counter(r['family'] for r in hecke)
    print(f"\n--- Hecke Eigenvalue Data (smf_hecke_nf) ---")
    print(f"Total records with eigenvalues: {len(hecke)}")
    for f, c in fam_hecke.most_common():
        print(f"  {f}: {c} records")

    P_hecke = [r for r in hecke if r['family'] == 'P']
    print(f"\nParamodular forms with lambda_p data: {len(P_hecke)}")
    P_hecke_levels = sorted(set(r['level'] for r in P_hecke))
    print(f"  at levels: {P_hecke_levels}")

    # Genus-2 curves
    g2c = load_g2c_curves()
    g2c_conds = sorted(set(r['cond'] for r in g2c))
    print(f"\n--- Genus-2 Curves (g2c_curves) ---")
    print(f"Total curves: {len(g2c)}")
    print(f"Conductor range: {min(g2c_conds)} to {max(g2c_conds)}")
    print(f"Unique conductors: {len(g2c_conds)}")

    gl2 = sum(1 for r in g2c if r['is_gl2_type'])
    usp4 = sum(1 for r in g2c if r['st_group'] == 'USp(4)')
    print(f"\nSato-Tate group distribution:")
    st_counts = Counter(r['st_group'] for r in g2c)
    for st, c in st_counts.most_common():
        print(f"  {st}: {c}")
    print(f"\nGL2-type (Klingen-relevant): {gl2}")
    print(f"USp(4) (paramodular candidates): {usp4}")

    # The gap
    print(f"\n{'=' * 70}")
    print("FUNDAMENTAL GAP:")
    print(f"  Paramodular forms available at levels: {P_levels}")
    print(f"  Genus-2 conductors start at: {min(g2c_conds)}")
    print(f"  OVERLAP: NONE")
    print(f"  Direct paramodular matching is NOT feasible with current LMFDB data.")
    print(f"{'=' * 70}")

    return {
        'P_levels': P_levels,
        'K_levels': K_levels,
        'g2c_conds': g2c_conds,
        'n_paramodular_candidates': usp4,
    }


def check_klingen_consistency():
    """For GL2-type curves, check if Klingen lifts at matching levels exist.

    GL2-type genus-2 curves correspond to pairs of elliptic curves or to
    classical modular forms. Their L-functions factor as products of GL(2)
    L-functions. The Klingen lift of the corresponding classical form should
    give a Siegel modular form at the same level.
    """
    print("\n" + "=" * 70)
    print("KLINGEN CONSISTENCY CHECK (GL2-type curves)")
    print("=" * 70)

    g2c = load_g2c_curves()
    gl2_curves = [r for r in g2c if r['is_gl2_type']]
    gl2_conds = Counter(r['cond'] for r in gl2_curves)

    nf = load_smf_newforms()
    K_nf = [r for r in nf if r['family'] == 'K']
    K_levels = set(r['level'] for r in K_nf)

    overlap_conds = set(gl2_conds.keys()) & K_levels

    print(f"GL2-type curves: {len(gl2_curves)} at {len(gl2_conds)} conductors")
    print(f"Klingen newforms at {len(K_levels)} levels")
    print(f"Overlapping conductor/levels: {len(overlap_conds)}")

    if overlap_conds:
        print(f"Examples: {sorted(overlap_conds)[:20]}")

        # For each overlapping level, count how many GL2 curves and Klingen forms
        print(f"\nLevel-by-level breakdown (first 15):")
        K_level_count = Counter(r['level'] for r in K_nf)
        for lev in sorted(overlap_conds)[:15]:
            print(f"  N={lev}: {gl2_conds[lev]} GL2-type curves, {K_level_count[lev]} Klingen forms")

    return len(overlap_conds)


def euler_factor_statistics():
    """Compute statistics on genus-2 Euler factors for paramodular candidates."""
    print("\n" + "=" * 70)
    print("GENUS-2 EULER FACTOR STATISTICS")
    print("=" * 70)

    print("Parsing genus-2 Euler factors from gce_1000000_lmfdb.txt...")
    curves = parse_genus2_euler_factors()
    print(f"Parsed {len(curves)} curves")

    usp4 = [c for c in curves if c['is_paramodular_candidate']]
    print(f"USp(4) paramodular candidates: {len(usp4)}")

    # Statistics on a_p values at small primes
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    print(f"\na_p distribution for paramodular candidates at small primes:")

    for p in primes[:6]:
        ap_vals = []
        for c in usp4:
            for pp, a1, a2 in c['good_lfactors']:
                if pp == p:
                    ap_vals.append(a1)
                    break
        if ap_vals:
            mean_ap = sum(ap_vals) / len(ap_vals)
            max_ap = max(abs(v) for v in ap_vals)
            # Hasse-Weil bound: |a_p| <= 4*sqrt(p) for genus 2
            hasse_bound = 4 * p**0.5
            violations = sum(1 for v in ap_vals if abs(v) > hasse_bound)
            print(f"  p={p:2d}: {len(ap_vals)} values, "
                  f"mean={mean_ap:.2f}, max|a_p|={max_ap}, "
                  f"Hasse bound={hasse_bound:.1f}, violations={violations}")

    # Distribution of number of good primes available
    n_primes = [len(c['good_lfactors']) for c in usp4]
    print(f"\nGood primes per curve: min={min(n_primes)}, max={max(n_primes)}, "
          f"median={sorted(n_primes)[len(n_primes)//2]}")

    # Conductor distribution of USp(4) curves
    cond_dist = Counter(c['cond'] for c in usp4)
    print(f"\nConductor distribution of USp(4) curves:")
    print(f"  Smallest: {sorted(cond_dist.keys())[:10]}")
    print(f"  Total unique conductors: {len(cond_dist)}")

    return usp4


def build_euler_factor_index(curves):
    """Build an index: conductor -> list of (Lhash, {p: (a1, a2)})."""
    index = defaultdict(list)
    for c in curves:
        if not c['is_paramodular_candidate']:
            continue
        ap_dict = {}
        for p, a1, a2 in c['good_lfactors']:
            ap_dict[p] = (a1, a2)
        index[c['cond']].append({
            'Lhash': c['Lhash'],
            'euler': ap_dict,
        })
    return dict(index)


def match_against_klingen_eigenvalues():
    """Attempt to match Klingen eigenvalues against GL2-type curve Euler factors.

    For GL2-type curves, L(C, s) = L(f, s) * L(g, s) where f, g are weight-2
    classical newforms. The Klingen lift of f has specific eigenvalue relations.

    This is a consistency check, NOT a paramodular test.
    """
    print("\n" + "=" * 70)
    print("KLINGEN vs GL2-TYPE EULER FACTOR COMPARISON")
    print("=" * 70)

    # Parse genus-2 Euler factors
    curves = parse_genus2_euler_factors()

    # Load Klingen Hecke eigenvalues
    hecke = load_smf_hecke_nf()
    K_hecke = [r for r in hecke if r['family'] == 'K' and r.get('weight') == [3, 0]]

    # Build Klingen eigenvalue lookup by level
    K_by_level = defaultdict(list)
    for r in K_hecke:
        # lambda_p gives eigenvalues at primes 2, 3, 5, 7, 11, ...
        lp = r.get('lambda_p', [])
        if not lp:
            continue
        # For dim-1 forms, each lambda_p[i] is [value]
        # For higher dim, it's [c0, c1, ...] in terms of Hecke ring generators
        if all(len(v) == 1 for v in lp[:5]):
            try:
                eigenvals = [int(v[0]) for v in lp]
            except (ValueError, TypeError):
                continue
            K_by_level[r['level']].append({
                'label': r['label'],
                'eigenvals': eigenvals,
                'maxp': r['maxp'],
            })

    print(f"Klingen [3,0] dim-1 forms with eigenvalues: "
          f"{sum(len(v) for v in K_by_level.values())} at {len(K_by_level)} levels")

    # Find GL2-type curves at Klingen levels
    # For GL2 type, st_group is not USp(4) - it's something like E_6, SU(2)xSU(2), etc.
    gl2_curves = [c for c in curves if not c['is_paramodular_candidate']]
    gl2_by_cond = defaultdict(list)
    for c in gl2_curves:
        gl2_by_cond[c['cond']].append(c)

    overlap = set(K_by_level.keys()) & set(gl2_by_cond.keys())
    print(f"GL2-type curves at Klingen levels: {len(overlap)} overlapping levels")

    # For the overlapping levels, compare
    # Note: Klingen eigenvalues relate to classical eigenvalues as:
    # lambda_p(Klingen lift of f) = a_p(f) + p + 1
    # (for weight [3,0] Klingen lift of a weight-2 classical form)
    # The genus-2 curve a_p = a_p(f) + a_p(g) (sum of classical a_p's)
    # These are DIFFERENT quantities.

    matches_found = 0
    checked = 0
    for level in sorted(overlap)[:20]:
        for curve in gl2_by_cond[level]:
            for kf in K_by_level[level]:
                checked += 1
                # Extract a_p values from curve at small primes
                primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31,
                               37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
                curve_ap = {}
                for p, a1, a2 in curve['good_lfactors']:
                    curve_ap[p] = a1

                klingen_lp = kf['eigenvals']

                # Check if curve a_p relates to Klingen eigenvalue
                # Klingen lift: lambda_p = a_p(f) + p + 1
                # So a_p(f) = lambda_p - p - 1
                n_match = 0
                n_compare = 0
                for idx, p in enumerate(primes_list):
                    if idx >= len(klingen_lp):
                        break
                    if p not in curve_ap:
                        continue
                    if p in [level] or level % p == 0:
                        continue  # skip bad primes
                    n_compare += 1
                    # Check: does a_p(curve) = lambda_p - p - 1?
                    classical_ap = klingen_lp[idx] - p - 1
                    if curve_ap[p] == classical_ap:
                        n_match += 1

                if n_compare >= 3 and n_match == n_compare:
                    matches_found += 1
                    print(f"  MATCH: level={level}, curve Lhash={curve['Lhash']}, "
                          f"Klingen={kf['label']}, {n_match}/{n_compare} primes")

    print(f"\nChecked {checked} curve-form pairs, found {matches_found} full matches")
    print("(Note: Klingen lift relation lambda_p = a_p(f) + p + 1 is for the")
    print("underlying classical form, not the genus-2 curve a_p directly.)")

    return matches_found


def summarize_feasibility():
    """Print final feasibility assessment."""
    print("\n" + "=" * 70)
    print("PARAMODULAR CONJECTURE PROBE: FEASIBILITY ASSESSMENT")
    print("=" * 70)

    print("""
STATUS: NOT FEASIBLE with current LMFDB data.

The Paramodular Conjecture (Brumer-Kramer) states:
  For every abelian surface A/Q of paramodular type with conductor N,
  there exists a weight-2 Siegel paramodular newform of level N
  whose L-function equals L(A, s).

BLOCKING ISSUE:
  - LMFDB paramodular (P) forms exist ONLY at levels 1 and 2
  - All 358 paramodular newforms have level <= 2
  - Genus-2 curve conductors range from 169 to 1,000,000
  - ZERO overlap between paramodular levels and genus-2 conductors

WHAT EXISTS:
  - 11,101 Klingen (K) newforms at 950 levels (1 to 999)
    These are LIFTS from classical forms, not genuine paramodular forms
  - 173 Saito-Kurokawa (S) newforms at level 1 only
  - 218 paramodular forms with Hecke eigenvalue data (all level 1 or 2)
  - 66,158 genus-2 curves with Euler factor data at ~24 good primes
  - 63,135 USp(4) curves (paramodular candidates)

WHAT WOULD MAKE THIS FEASIBLE:
  1. Poor-Yuen paramodular form database (levels up to ~1000)
     This is computed separately from LMFDB and contains the genuine
     paramodular forms needed for the conjecture.
  2. Direct computation of paramodular forms at specific conductor levels
     using Fourier-Jacobi expansion methods.
  3. Alternatively: trace formula methods to compute T(p) eigenvalues
     at specific levels without full Fourier expansion.

WHAT WE CAN DO NOW:
  - Parse and index all genus-2 Euler factors (DONE)
  - Consistency-check GL2-type curves against Klingen lifts
  - Build infrastructure for comparison once paramodular data arrives
  - Use Lhash values to cross-reference L-function database
""")


def main():
    print("Paramodular Conjecture Probe (C01)")
    print("=" * 70)

    # Step 1: Analyze the data landscape
    landscape = analyze_data_landscape()

    # Step 2: Check Klingen consistency
    n_overlap = check_klingen_consistency()

    # Step 3: Euler factor statistics
    usp4_curves = euler_factor_statistics()

    # Step 4: Attempt Klingen matching (consistency check only)
    if n_overlap > 0:
        matches = match_against_klingen_eigenvalues()

    # Step 5: Feasibility assessment
    summarize_feasibility()

    # Save parsed Euler factor index for future use
    print("\nBuilding Euler factor index for paramodular candidates...")
    index = build_euler_factor_index(usp4_curves)
    out_path = Path(__file__).parent / "paramodular_euler_index.json"

    # Save a summary (not all 60K+ entries - just the structure)
    summary = {
        'n_conductors': len(index),
        'n_curves': sum(len(v) for v in index.values()),
        'conductor_range': [min(index.keys()), max(index.keys())],
        'sample_conductors': {
            str(k): [{
                'Lhash': e['Lhash'],
                'euler_primes': sorted(e['euler'].keys()),
                'a2': e['euler'].get(2, None),
                'a3': e['euler'].get(3, None),
                'a5': e['euler'].get(5, None),
            } for e in v]
            for k, v in sorted(index.items())[:10]
        },
    }
    with open(out_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved Euler factor summary to {out_path}")
    print(f"  {summary['n_conductors']} conductors, {summary['n_curves']} curves")


if __name__ == '__main__':
    main()
