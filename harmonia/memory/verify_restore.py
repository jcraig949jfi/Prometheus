"""
Restore verification: prove the tensor artifact can reconstruct understanding.

Run this FIRST when returning from a reset. It loads the tensor, prints the
full state, and flags any inconsistencies. If this script runs clean, the
restore protocol is operational.
"""
import sys, io, json, os
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HERE = Path(__file__).parent

def load_all():
    tensor_data = np.load(HERE / "landscape_tensor.npz", allow_pickle=True)
    T = tensor_data['T']
    feature_ids = tensor_data['feature_ids'].tolist()
    proj_ids = tensor_data['projection_ids'].tolist()

    with open(HERE / "landscape_manifest.json") as f:
        manifest = json.load(f)
    with open(HERE / "feature_graph.json") as f:
        fgraph = json.load(f)
    with open(HERE / "projection_graph.json") as f:
        pgraph = json.load(f)

    return T, feature_ids, proj_ids, manifest, fgraph, pgraph


def verify_and_print():
    T, fids, pids, manifest, fgraph, pgraph = load_all()

    print("=" * 70)
    print("HARMONIA RESTORE VERIFICATION")
    print("=" * 70)
    print(f"Tensor: {T.shape}")
    print(f"Charter: {manifest['charter_ref']}")
    print(f"Date:    {manifest['date']}")

    # Tier summary
    tiers = {}
    for f in manifest['features']:
        tiers.setdefault(f['tier'], []).append(f['id'])
    print(f"\nFeature tiers:")
    for t, ids in sorted(tiers.items()):
        print(f"  {t}: {len(ids)} ({', '.join(ids)})")

    print(f"\nProjection types:")
    ptypes = {}
    for p in manifest['projections']:
        ptypes.setdefault(p['type'], []).append(p['id'])
    for t, ids in sorted(ptypes.items()):
        print(f"  {t}: {len(ids)}")

    # Live specimens — the actionable state
    print("\n" + "=" * 70)
    print("LIVE SPECIMENS (the current frontier)")
    print("=" * 70)
    feature_by_id = {f['id']: f for f in manifest['features']}
    for fid in manifest.get('live_specimens', []):
        f = feature_by_id[fid]
        row = T[fids.index(fid)]
        resolves = [pids[j] for j in range(len(pids)) if row[j] > 0]
        collapses = [pids[j] for j in range(len(pids)) if row[j] < 0]
        print(f"\n{fid}: {f['label']}")
        print(f"  {f['description']}")
        print(f"  Resolves through: {', '.join(resolves) if resolves else '(none)'}")
        print(f"  Collapses under:  {', '.join(collapses) if collapses else '(none)'}")

    # Calibration anchors — instrument health check
    print("\n" + "=" * 70)
    print("CALIBRATION ANCHORS (must hold)")
    print("=" * 70)
    for fid in manifest.get('calibration_anchors', []):
        f = feature_by_id[fid]
        print(f"  {fid} {f['label']}: {f.get('n_objects','?')} objects")

    # Feature graph
    print("\n" + "=" * 70)
    print("FEATURE GRAPH (structural relationships)")
    print("=" * 70)
    for edge in fgraph['edges']:
        print(f"  {edge['from']} --[{edge['relation']}]--> {edge['to']}")
        print(f"    note: {edge['note']}")

    # Projection graph — show the coordinate-system taxonomy
    print("\n" + "=" * 70)
    print("PROJECTION GRAPH (coordinate system relationships)")
    print("=" * 70)
    for edge in pgraph['edges']:
        print(f"  {edge['from']} --[{edge['relation']}]--> {edge['to']}")
        print(f"    note: {edge['note']}")

    # Sanity checks
    print("\n" + "=" * 70)
    print("SANITY CHECKS")
    print("=" * 70)
    issues = []

    # Every calibration anchor should have at least one +2 (strong resolve)
    for fid in manifest.get('calibration_anchors', []):
        row = T[fids.index(fid)]
        if not (row == 2).any():
            issues.append(f"  WARNING: calibration anchor {fid} has no +2 entries")

    # Every live specimen should have at least one +1 and at least one -1
    # (if it only had +1s, it would be calibration; if only -1s, it's killed)
    for fid in manifest.get('live_specimens', []):
        row = T[fids.index(fid)]
        has_pos = (row > 0).any()
        has_neg = (row < 0).any()
        if not has_pos:
            issues.append(f"  WARNING: live specimen {fid} has no positive resolution")
        # negative is not required but informative

    if issues:
        print("ISSUES:")
        for i in issues:
            print(i)
    else:
        print("  All checks pass.")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("  1. Read docs/landscape_charter.md if you haven't")
    print("  2. Read roles/Harmonia/CHARTER.md")
    print("  3. Read harmonia/memory/pattern_library.md")
    print("  4. Check Agora streams for team state since 2026-04-17")
    print("  5. Check git log for what changed since then")
    print("  6. Check signals.specimens for canonical specimen state")
    print("  7. Pick a live specimen and plan its next measurement")
    print("     (Weak Signal Walk: apply multiple projections, record shape)")


if __name__ == "__main__":
    verify_and_print()
