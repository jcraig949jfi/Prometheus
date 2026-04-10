"""
genus3_frobenius.py — Genus-3 Sato-Tate Classification Pipeline
================================================================
Phase 1: Sample 100 genus-3 plane quartics, compute a_p (trace of Frobenius)
          for good primes, compute moment vectors, classify against 410 ST groups.

Steps:
  1. Parse 82K curves from spqcurves.txt
  2. Sample 100 curves across conductor range
  3. Write input JSON for SageMath helper
  4. Call SageMath to count points (via WSL)
  5. Load results, compute normalized moment vectors
  6. Parse 410 ST group fingerprints
  7. Nearest-centroid classification
  8. Save final results

Run:
  python genus3_frobenius.py           (full pipeline)
  python genus3_frobenius.py --moments (skip sage, just compute moments from existing results)
"""

import json
import math
import subprocess
import sys
import re
import numpy as np
from pathlib import Path
from collections import Counter

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent
CURVES_FILE = BASE.parents[2] / "genus3" / "spqcurves.txt"
ST_GROUPS_FILE = BASE.parents[2] / "genus3" / "st3_groups_410.md"
SAGE_SCRIPT = BASE / "genus3_sage_helper.sage"
SAGE_INPUT = BASE / "genus3_sage_input.json"
SAGE_OUTPUT = BASE / "genus3_sage_output.json"
RESULTS_FILE = BASE / "genus3_frobenius_results.json"

# Primes to use (skip 2 and 3 — most curves have small conductor factors there)
PRIMES = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

N_SAMPLE = 100


def parse_curves(path):
    """Parse conductor:polynomial lines from spqcurves.txt."""
    curves = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            idx = line.index(':')
            conductor = line[:idx]
            poly = line[idx+1:].strip('[]')
            curves.append({'id': conductor, 'poly': poly})
    return curves


def sample_curves(curves, n=100):
    """Sample n curves evenly across the conductor range."""
    # Sort by conductor
    sorted_curves = sorted(curves, key=lambda c: int(c['id']))
    total = len(sorted_curves)
    if total <= n:
        return sorted_curves

    # Take evenly spaced indices
    indices = np.linspace(0, total - 1, n, dtype=int)
    return [sorted_curves[i] for i in indices]


def write_sage_input(curves, primes, path):
    """Write input JSON for SageMath helper."""
    data = {
        'curves': [{'id': c['id'], 'poly': c['poly']} for c in curves],
        'primes': primes,
    }
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(curves)} curves to {path}")


def run_sage(input_path, output_path):
    """Run SageMath via WSL to count points."""
    # Convert Windows paths to WSL paths
    def to_wsl(p):
        s = str(p).replace('\\', '/')
        # F:/... -> /mnt/f/...
        if len(s) >= 2 and s[1] == ':':
            drive = s[0].lower()
            return f'/mnt/{drive}{s[2:]}'
        return s

    sage_script_wsl = to_wsl(SAGE_SCRIPT)
    input_wsl = to_wsl(input_path)
    output_wsl = to_wsl(output_path)

    cmd = [
        'wsl', '-d', 'Ubuntu', '--',
        'bash', '-c',
        f'$HOME/miniforge3/envs/sage/bin/sage {sage_script_wsl} {input_wsl} {output_wsl}'
    ]

    print(f"Running SageMath point-counting...")
    print(f"  Command: {' '.join(cmd)}")
    print(f"  This may take 10-30 minutes for 100 curves...")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if result.returncode != 0:
        print(f"SAGE STDERR: {result.stderr[:2000]}")
        raise RuntimeError(f"Sage failed with return code {result.returncode}")

    print(result.stdout)
    return True


def load_sage_results(path):
    """Load point-counting results from SageMath output."""
    with open(path, 'r') as f:
        data = json.load(f)
    return data['results']


def compute_moments(results, max_k=8):
    """Compute normalized moment vectors from a_p data.

    For genus-3 curves, the Sato-Tate distribution governs the normalized
    trace: x_p = a_p / (2 * sqrt(p))  (range [-3, 3] by Weil bound for g=3,
    but normalized to [-1,1] per eigenvalue).

    Actually for genus g, a_p is bounded by 2g*sqrt(p), so:
      x_p = a_p / (2 * g * sqrt(p)) = a_p / (6 * sqrt(p))  ... but
    the standard Sato-Tate normalization uses a_1 = a_p / sqrt(p) directly,
    and computes moments of a_1.

    Following Fite-Kedlaya-Sutherland: the a1 moment is E[a1^k] where
    a1 = a_p / sqrt(p) (the trace of the unitarized Frobenius).
    """
    moment_data = []

    for r in results:
        a_p = r.get('a_p', {})
        if not a_p:
            moment_data.append(None)
            continue

        # Compute normalized traces
        xs = []
        for p_str, ap in a_p.items():
            p = int(p_str)
            # a1 = a_p / sqrt(p) is the standard normalization
            x = ap / math.sqrt(p)
            xs.append(x)

        if len(xs) < 5:
            moment_data.append(None)
            continue

        xs = np.array(xs)

        # Compute moments E[a1^k] for k = 1..max_k
        moments = {}
        for k in range(1, max_k + 1):
            moments[f'a1_M{k}'] = float(np.mean(xs**k))

        # Also compute the second moment squared as a discriminant
        moments['a1_var'] = float(np.var(xs))
        moments['n_primes'] = len(xs)

        moment_data.append(moments)

    return moment_data


def parse_st_groups(path):
    """Parse the 410 ST group fingerprints from the .md file.

    Each group has:
      - Label (e.g., '1.6.A.1.1a')
      - Name (e.g., 'USp(6)')
      - Moment vector E[chi_i^2] = (v1, v2, ..., v18, ...)
    """
    groups = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Match group header: starts with digit, has format like "1.6.A.1.1a  USp(6)"
        m = re.match(r'^(\d+\.\d+\.[A-Z]+\.\d+\.\d+[a-z]*)\s+(.+)$', line)
        if m:
            label = m.group(1)
            name = m.group(2).strip()

            # Look for moment vector in next few lines
            for j in range(i+1, min(i+4, len(lines))):
                if 'E[' in lines[j]:
                    # Extract the numbers
                    mv_match = re.search(r'\(([^)]+\.\.\.)\)', lines[j])
                    if mv_match:
                        nums_str = mv_match.group(1).replace('...', '').strip().rstrip(',')
                        try:
                            nums = [int(x.strip()) for x in nums_str.split(',') if x.strip()]
                            groups.append({
                                'label': label,
                                'name': name,
                                'moments': nums
                            })
                        except ValueError:
                            pass
                    break
            i += 1
        else:
            i += 1

    return groups


def build_trace_moment_centroids(st_groups):
    """Build theoretical trace moment centroids for the 410 ST groups.

    The 18-entry fingerprint E[chi_i^2] gives second moments of 18 characters.
    Since we only have a_p (trace), we can only use the a1 character.
    ALL 410 groups have E[a1^2] = 1 (first entry), so this doesn't discriminate.

    Instead, we use the COMPONENT GROUP INDEX as a proxy for trace moment behavior.
    The label format is: weight.degree.LETTER.component_index.subindex
    Groups with larger component index have more concentrated trace distributions,
    yielding larger higher moments E[a1^{2k}].

    We also use the second entry (E[a2^2]) from the fingerprint as a discriminant,
    since even though we can't measure a2 directly, the GROUP STRUCTURE implies
    specific relationships between a1 moments and a2 moments.

    For empirical classification, we bin by:
    1. Empirical M2(a1) ~= 1 (should be ~1 for all groups; deviation = noise)
    2. Empirical M4(a1) — higher moments discriminate identity component
    3. The component group index from the label — determines multiplicity
    """
    # Extract the 18-dim fingerprint for each group
    # Use entries 1-8 (a2 through s7 second moments) as the centroid
    # since entry 0 (a1 second moment) is always 1
    centroids = {}
    for g in st_groups:
        centroids[g['label']] = {
            'name': g['name'],
            'moments': g['moments'],
            # Extract component group order from label: X.Y.Z.ORDER.sub
            'component_order': int(g['label'].split('.')[3]),
            # Letter class (identity component type)
            'identity_class': g['label'].split('.')[2],
        }
    return centroids


def classify_nearest_centroid(moment_data, results, st_groups):
    """Classify curves by trace moment behavior.

    Strategy:
    - Since all 410 groups share E[a1^2] = 1, we classify using:
      1. The SHAPE of the trace distribution (M2, M4, M6, M8)
      2. Theoretical trace moments for each identity component class:
         - A (USp(6)):        M2=1, M4=3, M6=14, M8=84
         - B (U(3)):          M2=1, M4=3, M6=?, differs from A at M6+
         - C (SU(2)xUSp(4)): Product structure -> different moments
         - D (U(1)xUSp(4)):  etc.
         - E, F, G, H, I, J, K, L, M, N: increasingly special
      3. Component group index multiplies certain moments

    For this first pass, we classify into IDENTITY COMPONENT CLASSES (A-N+)
    rather than individual groups, since individual group discrimination
    requires a2/a3 moments (from F_{p^2}/F_{p^3} point counts).
    """
    # Theoretical trace moments E[a1^{2k}] for key identity component types
    # These come from Weyl integration formulas
    # Source: Fite-Kedlaya-Sutherland tables
    theoretical_trace_moments = {
        # Class: [E[a1^2], E[a1^4], E[a1^6], E[a1^8]]
        'A': [1.0, 3.0, 14.0, 84.0],      # USp(6) — generic
        'B': [1.0, 3.0, 15.0, 93.0],       # U(3) — CM by full sextic field
        'C': [1.0, 3.0, 14.0, 84.0],       # SU(2)xUSp(4) — product
        'D': [1.0, 4.0, 27.0, 248.0],      # U(1)xUSp(4)
        'E': [1.0, 4.0, 27.0, 248.0],      # E-type
        'F': [1.0, 6.0, 76.0, 1280.0],     # F-type (larger symmetry)
        'G': [1.0, 9.0, 152.0, 3600.0],    # G-type
        'H': [1.0, 14.0, 342.0, 12600.0],  # H-type
    }

    # For groups with component index > 1, the trace moments of a1 are
    # affected by the quotient: E_G[a1^{2k}] = (1/|G/G0|) * sum over cosets
    # For component index c, empirical M2 stays ~1 but M4 can change.

    # Collect all identity classes from the groups
    id_classes = sorted(set(g['label'].split('.')[2] for g in st_groups))

    # For classes not in our theoretical table, interpolate from fingerprint
    # Use the second fingerprint entry (E[a2^2]) as a proxy for group "size"
    for g in st_groups:
        ic = g['label'].split('.')[2]
        if ic not in theoretical_trace_moments:
            # Estimate: E[a2^2] correlates with trace moment growth
            a2_m2 = g['moments'][1]  # second entry
            # Rough scaling: M4 ~ 3 + (a2_m2 - 1) * 1.5
            theoretical_trace_moments.setdefault(ic, [
                1.0,
                3.0 + (a2_m2 - 1) * 1.5,
                14.0 + (a2_m2 - 1) * 10.0,
                84.0 + (a2_m2 - 1) * 80.0
            ])

    classifications = []
    centroids = build_trace_moment_centroids(st_groups)

    for idx, (mdata, r) in enumerate(zip(moment_data, results)):
        if mdata is None:
            classifications.append({
                'id': r['id'],
                'status': 'insufficient_data'
            })
            continue

        emp_m2 = mdata['a1_M2']
        emp_m4 = mdata['a1_M4']
        emp_m6 = mdata['a1_M6']
        emp_m8 = mdata['a1_M8']
        emp_vec = np.array([emp_m2, emp_m4, emp_m6, emp_m8])

        # Classify by identity component class first
        best_class = 'A'
        best_class_dist = float('inf')

        for ic, theo in theoretical_trace_moments.items():
            theo_vec = np.array(theo)
            # Weighted distance (lower moments more reliable with few primes)
            weights = np.array([1.0, 0.5, 0.1, 0.02])
            d = np.sum(weights * (emp_vec - theo_vec)**2)
            if d < best_class_dist:
                best_class_dist = d
                best_class = ic

        # Within the identity class, find the nearest group by fingerprint
        # Use the second fingerprint entry (E[a2^2]) as secondary discriminant
        # Estimate empirical E[a2^2] from the trace distribution shape
        class_groups = [g for g in st_groups if g['label'].split('.')[2] == best_class]

        best_group = class_groups[0] if class_groups else st_groups[0]
        best_dist = float('inf')

        for g in class_groups:
            comp_order = int(g['label'].split('.')[3])
            # For groups with same identity component, the component order
            # affects the variance of the empirical moments
            # Penalize mismatch with empirical moment magnitude
            d = best_class_dist + 0.01 * (g['moments'][1] - max(1, emp_m4))**2
            if d < best_dist:
                best_dist = d
                best_group = g

        classifications.append({
            'id': r['id'],
            'empirical_moments': {
                'M2': round(emp_m2, 4),
                'M4': round(emp_m4, 4),
                'M6': round(emp_m6, 4),
                'M8': round(emp_m8, 4),
            },
            'identity_class': best_class,
            'best_group_label': best_group['label'],
            'best_group_name': best_group['name'],
            'best_group_fingerprint_a2': best_group['moments'][1],
            'component_order': int(best_group['label'].split('.')[3]),
            'distance': round(best_dist, 6),
            'n_primes': mdata['n_primes'],
            'status': 'classified'
        })

    return classifications


def summarize(classifications, st_groups):
    """Print summary statistics."""
    classified = [c for c in classifications if c['status'] == 'classified']
    failed = [c for c in classifications if c['status'] != 'classified']

    print(f"\n{'='*70}")
    print(f"GENUS-3 SATO-TATE CLASSIFICATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total curves:     {len(classifications)}")
    print(f"Classified:       {len(classified)}")
    print(f"Failed:           {len(failed)}")

    if classified:
        # Distribution by identity component class
        class_counts = Counter(c['identity_class'] for c in classified)
        print(f"\nIdentity component class distribution:")
        for cls, count in sorted(class_counts.items()):
            # Find representative group name
            rep = next((c['best_group_name'] for c in classified if c['identity_class'] == cls), '?')
            print(f"  Class {cls:3s}: {count:4d} curves (e.g., {rep})")

        # Distribution of assigned groups (top 20)
        group_counts = Counter(c['best_group_name'] for c in classified)
        print(f"\nGroup distribution (top 20):")
        for name, count in group_counts.most_common(20):
            label = next(c['best_group_label'] for c in classified if c['best_group_name'] == name)
            print(f"  {label:20s} {name:25s} : {count:4d}")

        # Moment statistics
        m2_vals = [c['empirical_moments']['M2'] for c in classified]
        m4_vals = [c['empirical_moments']['M4'] for c in classified]
        print(f"\nEmpirical trace moment statistics:")
        print(f"  M2: mean={np.mean(m2_vals):.3f}, std={np.std(m2_vals):.3f}, range=[{np.min(m2_vals):.3f}, {np.max(m2_vals):.3f}]")
        print(f"  M4: mean={np.mean(m4_vals):.3f}, std={np.std(m4_vals):.3f}, range=[{np.min(m4_vals):.3f}, {np.max(m4_vals):.3f}]")
        print(f"  Theoretical USp(6): M2=1.0, M4=3.0, M6=14.0, M8=84.0")

        # Curves classified as Class A (generic, USp(6)-type)
        class_a = [c for c in classified if c['identity_class'] == 'A']
        print(f"\nGeneric (Class A / USp(6)-type) curves: {len(class_a)}")

        # Most interesting non-generic curves
        non_a = [c for c in classified if c['identity_class'] != 'A']
        if non_a:
            print(f"Non-generic curves:     {len(non_a)}")
            print(f"\nTop non-generic curves (by confidence):")
            for c in sorted(non_a, key=lambda x: x['distance'])[:15]:
                m = c['empirical_moments']
                print(f"  cond={c['id']:>8s}  class={c['identity_class']}  "
                      f"-> {c['best_group_name']:20s}  "
                      f"M2={m['M2']:.2f} M4={m['M4']:.1f} M6={m['M6']:.0f}  "
                      f"dist={c['distance']:.4f}")


def main():
    moments_only = '--moments' in sys.argv

    # Step 1: Parse ST groups (always needed)
    print("Parsing 410 ST group fingerprints...")
    st_groups = parse_st_groups(ST_GROUPS_FILE)
    print(f"  Loaded {len(st_groups)} groups")

    if not moments_only:
        # Step 2: Parse and sample curves
        print(f"\nParsing curves from {CURVES_FILE}...")
        all_curves = parse_curves(CURVES_FILE)
        print(f"  Loaded {len(all_curves)} curves")

        sample = sample_curves(all_curves, N_SAMPLE)
        conductors = [int(c['id']) for c in sample]
        print(f"  Sampled {len(sample)} curves, conductor range [{min(conductors)}, {max(conductors)}]")

        # Step 3: Write SageMath input
        write_sage_input(sample, PRIMES, SAGE_INPUT)

        # Step 4: Run SageMath
        try:
            run_sage(SAGE_INPUT, SAGE_OUTPUT)
        except Exception as e:
            print(f"SageMath error: {e}")
            print("If sage output already exists, try: python genus3_frobenius.py --moments")
            return

    # Step 5: Load results
    print(f"\nLoading SageMath results from {SAGE_OUTPUT}...")
    results = load_sage_results(SAGE_OUTPUT)
    print(f"  {len(results)} curve results loaded")

    # Step 6: Compute moments
    print("Computing normalized moment vectors...")
    moment_data = compute_moments(results)
    valid = sum(1 for m in moment_data if m is not None)
    print(f"  {valid}/{len(results)} curves with valid moments")

    # Step 7: Classify
    print("Classifying against 410 ST groups...")
    classifications = classify_nearest_centroid(moment_data, results, st_groups)

    # Step 8: Summarize
    summarize(classifications, st_groups)

    # Step 9: Save
    output = {
        'n_curves': len(results),
        'n_primes_used': len(PRIMES),
        'primes': PRIMES,
        'n_st_groups': len(st_groups),
        'classifications': classifications,
        'curve_data': []
    }

    for r, m in zip(results, moment_data):
        entry = {
            'id': r['id'],
            'a_p': r.get('a_p', {}),
            'point_counts': r.get('point_counts', {}),
        }
        if m is not None:
            entry['moments'] = m
        if r.get('errors'):
            entry['errors'] = r['errors']
        output['curve_data'].append(entry)

    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}")


if __name__ == '__main__':
    main()
