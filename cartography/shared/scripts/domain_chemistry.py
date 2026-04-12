#!/usr/bin/env python3
"""
Chemistry Domain — First battery run on QM9 (134K molecules).
Tests BREAK_SYMMETRY in molecular science.

Key question: does functional_group → HOMO-LUMO gap show the same
non-stationarity as SC_class → Tc?
"""
import sys, os, csv
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

_scripts = str(Path(__file__).resolve().parent)
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)

from battery_v2 import BatteryV2
bv2 = BatteryV2()
DATA = Path(__file__).resolve().parent.parent.parent
rng = np.random.default_rng(42)

def eta_sq(values, labels, min_group=5):
    values = np.array(values, dtype=float)
    groups = defaultdict(list)
    for v, l in zip(values, labels):
        groups[l].append(v)
    valid = {k: np.array(v) for k, v in groups.items() if len(v) >= min_group}
    if len(valid) < 2: return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)

# ============================================================
# Load QM9
# ============================================================
print("=" * 100)
print("CHEMISTRY DOMAIN: QM9 (134K molecules)")
print("=" * 100)

qm9_path = DATA / "chemistry/data/qm9.csv"
molecules = []
with open(qm9_path, "r") as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    print(f"  Columns: {cols}")
    for row in reader:
        try:
            smiles = row.get("smiles", "")
            mol = {"smiles": smiles}
            for prop in cols:
                if prop != "smiles" and prop != "mol_id":
                    try: mol[prop] = float(row[prop])
                    except: mol[prop] = row[prop]
            molecules.append(mol)
        except:
            pass

print(f"  Loaded {len(molecules)} molecules")
print(f"  Properties: {[c for c in cols if c not in ('smiles', 'mol_id')]}")

# ============================================================
# Derive categorical features from SMILES
# ============================================================
print(f"\n  Deriving molecular descriptors from SMILES...")

def classify_molecule(smiles):
    """Simple SMILES-based classification."""
    features = {}

    # Element composition
    import re
    atoms = re.findall(r'[A-Z][a-z]?', smiles)
    features["n_heavy_atoms"] = len(atoms)
    features["has_N"] = "N" in smiles
    features["has_O"] = "O" in smiles
    features["has_F"] = "F" in smiles
    features["has_S"] = "S" in smiles

    # Functional groups (simple pattern matching)
    features["has_ring"] = "1" in smiles or "2" in smiles  # ring closure digits
    features["has_double_bond"] = "=" in smiles
    features["has_triple_bond"] = "#" in smiles
    features["has_aromatic"] = any(c.islower() and c.isalpha() for c in smiles)  # lowercase = aromatic

    # Coarse chemical class
    if features["has_aromatic"]:
        features["class"] = "aromatic"
    elif features["has_ring"]:
        features["class"] = "cyclic"
    elif features["has_double_bond"] or features["has_triple_bond"]:
        features["class"] = "unsaturated"
    else:
        features["class"] = "saturated"

    # Heteroatom class
    heteroatoms = set()
    if features["has_N"]: heteroatoms.add("N")
    if features["has_O"]: heteroatoms.add("O")
    if features["has_F"]: heteroatoms.add("F")
    if features["has_S"]: heteroatoms.add("S")
    features["heteroatom_class"] = "_".join(sorted(heteroatoms)) if heteroatoms else "CH_only"

    # Size bin
    n = features["n_heavy_atoms"]
    if n <= 5: features["size_bin"] = "tiny"
    elif n <= 10: features["size_bin"] = "small"
    elif n <= 15: features["size_bin"] = "medium"
    elif n <= 20: features["size_bin"] = "large"
    else: features["size_bin"] = "xlarge"

    return features

for m in molecules:
    m.update(classify_molecule(m["smiles"]))

class_dist = Counter(m["class"] for m in molecules)
hetero_dist = Counter(m["heteroatom_class"] for m in molecules)
print(f"  Chemical classes: {dict(class_dist)}")
print(f"  Heteroatom classes: {dict(hetero_dist.most_common(8))}")

# ============================================================
# Battery: class → HOMO-LUMO gap (the SC_class → Tc analog)
# ============================================================
print(f"\n" + "-" * 100)
print("TEST: chemical_class → gap (HOMO-LUMO gap = the Tc analog)")
print("-" * 100)

# Find gap column
gap_col = None
for c in ("gap", "homo_lumo_gap", "HOMO-LUMO_gap", "lumo", "mu"):
    vals = [m.get(c) for m in molecules[:10] if m.get(c) is not None]
    if vals:
        gap_col = c
        break

if gap_col is None:
    # Compute gap from HOMO and LUMO if available
    homo_col = [c for c in cols if "homo" in c.lower()]
    lumo_col = [c for c in cols if "lumo" in c.lower()]
    print(f"  HOMO cols: {homo_col}, LUMO cols: {lumo_col}")
    if homo_col and lumo_col:
        gap_col = "computed_gap"
        for m in molecules:
            try:
                m["computed_gap"] = float(m.get(lumo_col[0], 0)) - float(m.get(homo_col[0], 0))
            except:
                m["computed_gap"] = None

if gap_col:
    gap_vals = [m[gap_col] for m in molecules if m.get(gap_col) is not None]
    print(f"  Using: {gap_col} (n={len(gap_vals)})")
    print(f"  Gap range: {min(gap_vals):.4f} to {max(gap_vals):.4f}, mean={np.mean(gap_vals):.4f}")
else:
    # Fallback: use any available numeric property
    for prop in cols:
        if prop not in ("smiles", "mol_id"):
            vals = [m.get(prop) for m in molecules[:100] if isinstance(m.get(prop), (int, float))]
            if len(vals) > 50:
                gap_col = prop
                gap_vals = [m[gap_col] for m in molecules if isinstance(m.get(gap_col), (int, float))]
                print(f"  Fallback property: {gap_col} (n={len(gap_vals)})")
                break

if gap_col and gap_vals:
    class_labels = [m["class"] for m in molecules if m.get(gap_col) is not None]
    hetero_labels = [m["heteroatom_class"] for m in molecules if m.get(gap_col) is not None]
    size_labels = [m["size_bin"] for m in molecules if m.get(gap_col) is not None]

    # 1. Chemical class → gap
    eta_class, n_c, k_c = eta_sq(gap_vals, class_labels)
    v24, r24 = bv2.F24_variance_decomposition(gap_vals, class_labels)
    print(f"\n  eta²(class → {gap_col}): {eta_class:.4f} (n={n_c}, k={k_c})")
    print(f"  F24: {v24}")

    # 2. Heteroatom class → gap
    eta_hetero, n_h, k_h = eta_sq(gap_vals, hetero_labels)
    print(f"  eta²(heteroatom_class → {gap_col}): {eta_hetero:.4f} (n={n_h}, k={k_h})")

    # 3. Size bin → gap
    eta_size, n_s, k_s = eta_sq(gap_vals, size_labels)
    print(f"  eta²(size_bin → {gap_col}): {eta_size:.4f} (n={n_s}, k={k_s})")

    # 4. BREAK_SYMMETRY test: class → gap across size bins
    print(f"\n  BREAK_SYMMETRY: class → {gap_col} across size bins")
    v25b, r25b = bv2.F25b_model_transportability(gap_vals, class_labels, size_labels)
    print(f"  F25b: {v25b}")
    print(f"  Main R²: {r25b.get('weighted_r2_main', 0):.4f}")
    print(f"  Interaction R²: {r25b.get('weighted_r2_interaction', 0):.4f}")

    # 5. Within-size-bin class → gap
    print(f"\n  Within-size-bin eta²(class → {gap_col}):")
    for sb in sorted(set(size_labels)):
        sub = [molecules[i] for i in range(len(molecules)) if molecules[i].get(gap_col) is not None and molecules[i]["size_bin"] == sb]
        if len(sub) >= 50:
            sub_vals = [m[gap_col] for m in sub]
            sub_labels = [m["class"] for m in sub]
            eta_sub, n_sub, k_sub = eta_sq(sub_vals, sub_labels)
            print(f"    {sb:10s}: eta²={eta_sub:.4f} (n={n_sub}, k={k_sub})")

    # 6. Interaction decomposition (variance decomposition like Tc)
    print(f"\n  Variance decomposition:")
    def one_hot(labels, n_rows):
        unique = sorted(set(labels))
        mat = np.zeros((n_rows, max(len(unique)-1, 1)))
        for i, l in enumerate(labels):
            idx = unique.index(l)
            if idx > 0 and idx-1 < mat.shape[1]:
                mat[i, idx-1] = 1
        return mat

    n_g = len(gap_vals)
    gap_arr = np.array(gap_vals)
    X_class = one_hot(class_labels, n_g)
    X_size = one_hot(size_labels, n_g)
    X_hetero = one_hot(hetero_labels, n_g)

    ss_total = np.sum((gap_arr - np.mean(gap_arr))**2)

    for name, X_a, X_b in [
        ("class only", X_class, None),
        ("hetero only", X_hetero, None),
        ("size only", X_size, None),
        ("class + size", np.column_stack([X_class, X_size]), None),
        ("class + hetero", np.column_stack([X_class, X_hetero]), None),
        ("class + size + hetero", np.column_stack([X_class, X_size, X_hetero]), None),
    ]:
        X = np.column_stack([np.ones(n_g), X_a])
        beta = np.linalg.lstsq(X, gap_arr, rcond=None)[0]
        r2 = 1 - np.sum((gap_arr - X @ beta)**2) / ss_total
        print(f"    {name:30s}: R²={r2:.4f}")

    # 7. Primitive tagging
    tags = bv2.tag_primitive({
        "name": f"class->{gap_col}",
        "eta2": eta_class,
        "has_interaction": v25b != "UNIVERSAL",
        "rank_stable": False,
        "is_identity": False,
        "functional_form": "",
        "is_cross_domain": False,
        "involves_eigenvalues": False,
    })
    print(f"\n  Primitive tags: {', '.join(f'{t}({c:.1f})' for t, c in tags)}")

    # 8. Permutation null
    null_etas = []
    labels_arr = np.array(class_labels)
    for _ in range(200):
        shuffled = labels_arr.copy()
        rng.shuffle(shuffled)
        ne, _, _ = eta_sq(gap_vals, shuffled.tolist())
        null_etas.append(ne)
    null_etas = np.array(null_etas)
    z = (eta_class - np.mean(null_etas)) / np.std(null_etas) if np.std(null_etas) > 0 else 0
    print(f"\n  Permutation null: mean={np.mean(null_etas):.4f}, z={z:.1f}")

print(f"\n" + "=" * 100)
print("CHEMISTRY DOMAIN SUMMARY")
print("=" * 100)
