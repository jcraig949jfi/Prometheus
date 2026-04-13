"""Pairwise sweep across all live domains using Harmonia."""
import sys, os, time, json, traceback
from pathlib import Path
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure repo root is on path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(str(ROOT))

import torch
from harmonia.src.domain_index import DOMAIN_LOADERS, load_domains
from harmonia.src.engine import HarmoniaEngine
from harmonia.src.validate import validate_bond

DEAD = {'knots', 'maass', 'battery', 'dissection', 'metabolism'}
live = sorted([d for d in DOMAIN_LOADERS.keys() if d not in DEAD])
pairs = list(combinations(live, 2))

print(f"Live domains ({len(live)}): {live}")
print(f"Total pairs: {len(pairs)}")
print()

# Preload all domains once to avoid repeated disk I/O
print("Preloading all domains...")
t_load = time.time()
ALL_DOMAINS = {}
for name in live:
    try:
        ALL_DOMAINS[name] = DOMAIN_LOADERS[name]()
        print(f"  {name}: {ALL_DOMAINS[name].n_objects} objects, {ALL_DOMAINS[name].n_features} features")
    except Exception as e:
        print(f"  {name}: FAILED to load - {e}")
print(f"Loaded {len(ALL_DOMAINS)} domains in {time.time()-t_load:.1f}s")
print()

# Remove domains that failed to load
live = [d for d in live if d in ALL_DOMAINS]
pairs = list(combinations(live, 2))
print(f"Pairs after filtering: {len(pairs)}")

def run_pair(pair):
    """Run one pair through HarmoniaEngine + validate_bond."""
    a, b = pair
    try:
        engine = HarmoniaEngine(
            domains=[a, b],
            max_rank=15,
            eps=1e-3,
            scorer='phoneme',
            subsample=1000,
        )
        tt, report = engine.explore()

        # validate_bond expects domains list matching the TT
        dom_list = [engine._domain_list[0], engine._domain_list[1]]
        vr = validate_bond(tt, bond_idx=0, domains=dom_list)

        return {
            'domain_a': a,
            'domain_b': b,
            'raw_rank': report.tt_ranks[1] if len(report.tt_ranks) > 1 else 0,
            'validated_rank': vr.validated_rank,
            'top_svs': report.bonds[0].top_singular_values[:5] if report.bonds else [],
            'n_components_survived': vr.validated_rank,
            'n_components_killed': vr.raw_rank - vr.validated_rank,
            'wall_time': report.wall_time_seconds,
            'error': None,
        }
    except Exception as e:
        traceback.print_exc()
        return {
            'domain_a': a,
            'domain_b': b,
            'raw_rank': 0,
            'validated_rank': 0,
            'top_svs': [],
            'n_components_survived': 0,
            'n_components_killed': 0,
            'wall_time': 0,
            'error': str(e),
        }

# Run with ThreadPoolExecutor
print(f"\nStarting pairwise sweep with {len(pairs)} pairs, 8 workers...")
t0 = time.time()
results = []

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(run_pair, p): p for p in pairs}
    done_count = 0
    for future in as_completed(futures):
        done_count += 1
        r = future.result()
        results.append(r)
        if done_count % 20 == 0 or done_count == len(pairs):
            elapsed = time.time() - t0
            print(f"  [{done_count}/{len(pairs)}] {elapsed:.0f}s elapsed")

total_time = time.time() - t0

# Sort by validated_rank descending
results.sort(key=lambda x: (x['validated_rank'], max(x['top_svs']) if x['top_svs'] else 0), reverse=True)

# Summary
errors = [r for r in results if r['error']]
nonzero = [r for r in results if r['validated_rank'] > 0 and not r['error']]

print(f"\n{'='*80}")
print(f"PAIRWISE SWEEP COMPLETE")
print(f"{'='*80}")
print(f"Total pairs: {len(pairs)}")
print(f"Total time: {total_time:.1f}s")
print(f"Errors: {len(errors)}")
print(f"Nonzero validated bonds: {len(nonzero)}")
print()

# Bond matrix (validated ranks)
print("BOND MATRIX (validated rank, 0 = no bond):")
print(f"{'':>20s}", end="")
for d in live[:12]:
    print(f" {d[:6]:>6s}", end="")
print(" ...")
for d1 in live:
    print(f"{d1[:20]:>20s}", end="")
    for d2 in live[:12]:
        if d1 == d2:
            print(f" {'--':>6s}", end="")
        else:
            # Find this pair
            match = [r for r in results if
                     (r['domain_a'] == d1 and r['domain_b'] == d2) or
                     (r['domain_a'] == d2 and r['domain_b'] == d1)]
            if match:
                v = match[0]['validated_rank']
                print(f" {v:>6d}", end="")
            else:
                print(f" {'?':>6s}", end="")
    print()

# Top 20 strongest bonds
print(f"\nTOP 20 STRONGEST BONDS:")
print(f"{'Rank':>4s}  {'Domain A':>20s} <-> {'Domain B':<20s}  Raw  Val  Top SV")
print("-" * 80)
for i, r in enumerate(results[:20]):
    if r['error']:
        continue
    sv_str = f"{r['top_svs'][0]:.4f}" if r['top_svs'] else "N/A"
    print(f"{i+1:>4d}  {r['domain_a']:>20s} <-> {r['domain_b']:<20s}  "
          f"{r['raw_rank']:>3d}  {r['validated_rank']:>3d}  {sv_str}")

# Cross-category analysis
MATH = {'number_fields', 'elliptic_curves', 'modular_forms', 'genus2', 'belyi',
        'bianchi', 'groups', 'lattices', 'polytopes', 'oeis', 'fungrim', 'dirichlet_zeros', 'ec_zeros'}
PHYSICS = {'rmt', 'phase_space', 'dynamics', 'spectral_sigs', 'codata', 'pdg_particles'}
CHEMISTRY = {'chemistry', 'materials'}
CHAOS = {'charon_landscape', 'operadic_sigs'}

def categorize(d):
    if d in MATH: return 'math'
    if d in PHYSICS: return 'physics'
    if d in CHEMISTRY: return 'chemistry'
    if d in CHAOS: return 'chaos'
    return 'other'

print(f"\nCROSS-CATEGORY BONDS (validated_rank > 0):")
print(f"{'Domain A':>20s} ({'cat':>7s}) <-> {'Domain B':<20s} ({'cat':<7s})  Val  Top SV")
print("-" * 90)
cross_bonds = []
for r in results:
    if r['error'] or r['validated_rank'] == 0:
        continue
    ca = categorize(r['domain_a'])
    cb = categorize(r['domain_b'])
    if ca != cb:
        cross_bonds.append(r)
        sv_str = f"{r['top_svs'][0]:.4f}" if r['top_svs'] else "N/A"
        print(f"{r['domain_a']:>20s} ({ca:>7s}) <-> {r['domain_b']:<20s} ({cb:<7s})  "
              f"{r['validated_rank']:>3d}  {sv_str}")

print(f"\nTotal cross-category bonds: {len(cross_bonds)}")

# Save results
output = {
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'live_domains': live,
    'dead_domains': list(DEAD),
    'n_pairs': len(pairs),
    'total_time_seconds': total_time,
    'n_errors': len(errors),
    'n_nonzero_bonds': len(nonzero),
    'n_cross_category_bonds': len(cross_bonds),
    'results': results,
}

outpath = Path(__file__).parent / 'sweep_29domains.json'
with open(outpath, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to {outpath}")
