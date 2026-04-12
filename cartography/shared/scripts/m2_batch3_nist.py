#!/usr/bin/env python3
"""
M2 Batch 3: NIST atomic spectral enrichment (C1)
Test: Config enrichment — F17 with atomic number Z as confound
"""
import sys, os, json, re
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

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
    if len(valid) < 2:
        return float("nan"), 0, 0
    all_v = np.concatenate(list(valid.values()))
    gm = np.mean(all_v)
    ss_total = np.sum((all_v - gm)**2)
    ss_between = sum(len(v) * (np.mean(v) - gm)**2 for v in valid.values())
    return ss_between / ss_total if ss_total > 0 else 0, len(all_v), len(valid)


# ============================================================
# Load NIST atomic data
# ============================================================
print("=" * 100)
print("M2 BATCH 3: NIST ATOMIC SPECTRAL TEST")
print("=" * 100)

nist_path = DATA / "physics/data/nist_asd/all_elements.json"
if not nist_path.exists():
    # Try alternate locations
    alt_paths = [
        DATA / "physics/data/nist_asd.json",
        DATA / "physics/data/atomic/nist_asd.json",
    ]
    for p in alt_paths:
        if p.exists():
            nist_path = p
            break

print(f"\nLoading NIST data from {nist_path}...")

if not nist_path.exists():
    print("  NIST data not found. Checking what's available...")
    physics_data = DATA / "physics/data"
    if physics_data.exists():
        import glob
        files = glob.glob(str(physics_data / "**/*.json"), recursive=True)
        nist_files = [f for f in files if "nist" in f.lower() or "atomic" in f.lower() or "element" in f.lower()]
        print(f"  Found: {nist_files[:10]}")
    print("  SKIP: No NIST atomic data available\n")
    # Fall through to summary with skip
    nist_data = None
else:
    nist_data = json.load(open(nist_path, encoding="utf-8"))
    print(f"  Loaded NIST data: {type(nist_data)}")

if nist_data and isinstance(nist_data, dict):
    # Extract spectral lines per element with their electron configurations
    print(f"  Elements: {len(nist_data)}")

    # Build: for each spectral line, record (element, config, wavelength, Z)
    lines = []
    for elem_name, elem_data in nist_data.items():
        if isinstance(elem_data, dict):
            z = elem_data.get("atomic_number", elem_data.get("Z", 0))
            spec_lines = elem_data.get("lines", elem_data.get("spectral_lines", []))
            if isinstance(spec_lines, list):
                for line in spec_lines:
                    if isinstance(line, dict):
                        wl = line.get("wavelength", line.get("obs_wl", line.get("ritz_wl")))
                        config = line.get("configuration", line.get("conf", line.get("lower_conf", "")))
                        if wl and config:
                            try:
                                wl = float(str(wl).replace(",", "").strip("[]() "))
                                lines.append({"element": elem_name, "Z": z, "config": str(config), "wl": wl})
                            except:
                                pass

    print(f"  Spectral lines with config: {len(lines)}")

    if len(lines) > 100:
        # TEST C1: Config enrichment — do lines sharing a config have more similar wavelengths?
        print(f"\n  TEST C1: Electron configuration -> wavelength")

        # eta^2: config → wavelength
        wl_vals = [l["wl"] for l in lines]
        config_labels = [l["config"] for l in lines]
        eta_config, n_config, k_config = eta_sq(wl_vals, config_labels)

        v24, r24 = bv2.F24_variance_decomposition(wl_vals, config_labels)
        v24b, r24b = bv2.F24b_metric_consistency(wl_vals, config_labels)

        print(f"  Raw eta^2(config -> wavelength) = {eta_config:.4f} (n={n_config}, k={k_config})")
        print(f"  F24: {v24}")
        print(f"  F24b: {v24b}")

        # F17 confound: Z (atomic number) as confound
        # Partial: config → wavelength | Z
        z_vals = np.array([l["Z"] for l in lines], dtype=float)
        wl_arr = np.array(wl_vals, dtype=float)

        # Regress wavelength on Z, take residuals
        mask = np.isfinite(z_vals) & np.isfinite(wl_arr) & (z_vals > 0)
        z_clean = z_vals[mask]
        wl_clean = wl_arr[mask]
        config_clean = [config_labels[i] for i in range(len(mask)) if mask[i]]

        X = np.column_stack([np.ones(len(z_clean)), z_clean])
        beta = np.linalg.lstsq(X, wl_clean, rcond=None)[0]
        wl_resid = wl_clean - X @ beta

        eta_partial, n_p, k_p = eta_sq(wl_resid, config_clean)
        print(f"  Partial eta^2(config -> wavelength | Z) = {eta_partial:.4f} (n={n_p}, k={k_p})")
        print(f"  Reduction: {(1 - eta_partial / eta_config) * 100:.0f}%" if eta_config > 0 else "")

        # Also: Z → wavelength (how much does Z explain?)
        r_z_wl = np.corrcoef(z_clean, wl_clean)[0, 1]
        print(f"  r(Z, wavelength) = {r_z_wl:.4f}, R^2 = {r_z_wl**2:.4f}")

        # Element enrichment: eta^2(element → wavelength)
        elem_labels = [l["element"] for l in lines]
        eta_elem, n_e, k_e = eta_sq(wl_vals, elem_labels)
        print(f"  eta^2(element -> wavelength) = {eta_elem:.4f} (n={n_e}, k={k_e})")

        # Partial: config → wavelength | element
        elem_means = defaultdict(list)
        for v, e in zip(wl_vals, elem_labels):
            elem_means[e].append(v)
        elem_means = {k: np.mean(v) for k, v in elem_means.items()}
        wl_resid_elem = np.array([v - elem_means[e] for v, e in zip(wl_vals, elem_labels)])
        eta_config_elem, _, _ = eta_sq(wl_resid_elem, config_labels)
        print(f"  Partial eta^2(config -> wavelength | element) = {eta_config_elem:.4f}")

        # Classification
        print(f"\n  CLASSIFICATION:")
        if eta_partial < 0.01:
            print(f"  Config enrichment is ENTIRELY mediated by Z. NEGLIGIBLE after confound.")
        elif eta_partial < eta_config * 0.5:
            print(f"  Config enrichment PARTIALLY mediated by Z ({(1-eta_partial/eta_config)*100:.0f}% reduction).")
            print(f"  Classification: TENDENCY (reduced but survives)")
        else:
            print(f"  Config enrichment SURVIVES Z control ({(1-eta_partial/eta_config)*100:.0f}% reduction).")
            print(f"  Classification: {'LAW' if eta_partial >= 0.14 else 'CONSTRAINT' if eta_partial >= 0.01 else 'TENDENCY'}")
    else:
        print("  Insufficient spectral lines for analysis")

elif nist_data and isinstance(nist_data, list):
    print(f"  NIST data is a list of {len(nist_data)} items")
    if nist_data:
        print(f"  First item keys: {list(nist_data[0].keys()) if isinstance(nist_data[0], dict) else 'not dict'}")
    print("  Need to adapt parser to this format. SKIP for now.")
else:
    print("  No usable NIST data. SKIP.\n")

print()
print("=" * 100)
print("M2 BATCH 3 COMPLETE")
print("=" * 100)
