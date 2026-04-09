"""
Fire All Extractors — Run every signature strategy on targeted formulas.
=========================================================================
34 lenses on 400 formulas. Then match. Then battery. Then shadow tensor.

Usage:
    python fire_all_extractors.py                    # full run
    python fire_all_extractors.py --max 50           # test with 50 formulas
    python fire_all_extractors.py --oeis-only        # just OEIS extractors
"""

import argparse
import importlib
import json
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "cartography" / "convergence" / "data"
LAYER2 = Path(__file__).resolve().parent

# All extractors grouped by input type
TREE_EXTRACTORS = [
    ("S9_symmetry", "symmetry_signatures"),
    ("S13_discriminant", "discriminant_signatures"),
    ("S14_newton_polytope", "newton_polytope"),
    ("S15_groebner", "groebner_signatures"),
    ("S18_tropical", "tropical_signatures"),
    ("S19_ade_singularity", "ade_singularity_signatures"),
    ("S22_operadic", "operadic_signatures"),
    ("S23_convexity", "convexity_signatures"),
    ("S31_functional_eq", "functional_equation_signatures"),
    ("S32_coeff_field", "coefficient_field_signatures"),
    ("S34_categorical", "categorical_equivalence_signatures"),
]

OEIS_EXTRACTORS = [
    ("S5_spectral", "spectral_signatures"),
    ("S6_phase_space", "phase_space_signatures"),
    ("S24_info_theoretic", "info_theoretic_signatures"),
    ("S25_renormalization", "renormalization_signatures"),
    ("S27_arithmetic_dynamics", "arithmetic_dynamics_signatures"),
    ("S28_resurgence", "resurgence_signatures"),
    ("S33_recursion_operator", "recursion_operator_signatures"),
]

EVAL_EXTRACTORS = [
    ("S1_complex_plane", "complex_plane_signatures"),
    ("S2_fractional_deriv", "fractional_derivative_signatures"),
    ("S3_mod_p", "mod_p_signatures"),
    ("S7_padic", "padic_signatures"),
    ("S8_morse", "morse_level_set_signatures"),
    ("S10_galois", "galois_group_signatures"),
    ("S11_monodromy", "monodromy_signatures"),
    ("S12_zeta", "zeta_function_signatures"),
    ("S20_diff_galois", "diff_galois_signatures"),
    ("S21_automorphic", "automorphic_signatures"),
    ("S26_spectral_curve", "spectral_curve_signatures"),
]


def run_extractor(name, module_name, max_formulas, extractor_type):
    """Run a single extractor and return (name, success, elapsed, n_results, error)."""
    t0 = time.time()
    try:
        # Build command args — try the flag each script expects
        if module_name == "info_theoretic_signatures":
            args = ["--max-seqs", str(max_formulas), "--max-formulas", str(max_formulas)]
        elif extractor_type == "oeis":
            args = ["--max", str(max_formulas)]
        else:
            args = ["--max-formulas", str(max_formulas)]

        # Import and run via subprocess to isolate failures
        import subprocess
        script = LAYER2 / f"{module_name}.py"
        if not script.exists():
            return (name, False, 0, 0, f"script not found: {script.name}")

        result = subprocess.run(
            [sys.executable, str(script)] + args,
            capture_output=True, text=True, timeout=300,
            cwd=str(LAYER2),
            env={**__import__('os').environ, "PYTHONUNBUFFERED": "1"},
        )

        elapsed = time.time() - t0

        # Check output file
        out_file = DATA / f"{module_name.replace('_signatures', '_signatures')}.jsonl"
        # Try common output file names
        for suffix in [f"{module_name}.jsonl", f"{module_name.replace('_signatures', '_signatures')}.jsonl"]:
            candidate = DATA / suffix
            if candidate.exists():
                out_file = candidate
                break

        n_results = 0
        if out_file.exists():
            try:
                n_results = sum(1 for _ in open(out_file))
            except Exception:
                pass

        if result.returncode != 0:
            error_lines = result.stderr.strip().split('\n')[-3:]
            return (name, False, elapsed, n_results, '\n'.join(error_lines))

        return (name, True, elapsed, n_results, None)

    except subprocess.TimeoutExpired:
        return (name, False, time.time() - t0, 0, "TIMEOUT (300s)")
    except Exception as e:
        return (name, False, time.time() - t0, 0, str(e))


def main():
    parser = argparse.ArgumentParser(description="Fire All Extractors")
    parser.add_argument("--max", type=int, default=500,
                        help="Max formulas/sequences per extractor (default: 500)")
    parser.add_argument("--oeis-only", action="store_true",
                        help="Only run OEIS extractors")
    parser.add_argument("--tree-only", action="store_true",
                        help="Only run tree-based extractors")
    parser.add_argument("--eval-only", action="store_true",
                        help="Only run eval-based extractors")
    args = parser.parse_args()

    extractors = []
    if not (args.oeis_only or args.tree_only or args.eval_only):
        extractors += [(n, m, "tree") for n, m in TREE_EXTRACTORS]
        extractors += [(n, m, "oeis") for n, m in OEIS_EXTRACTORS]
        extractors += [(n, m, "eval") for n, m in EVAL_EXTRACTORS]
    else:
        if args.tree_only:
            extractors += [(n, m, "tree") for n, m in TREE_EXTRACTORS]
        if args.oeis_only:
            extractors += [(n, m, "oeis") for n, m in OEIS_EXTRACTORS]
        if args.eval_only:
            extractors += [(n, m, "eval") for n, m in EVAL_EXTRACTORS]

    print("=" * 70)
    print(f"  FIRE ALL EXTRACTORS — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Extractors: {len(extractors)}")
    print(f"  Max per extractor: {args.max}")
    print("=" * 70)

    results = []
    n_success = 0
    n_fail = 0
    total_signatures = 0

    for i, (name, module, etype) in enumerate(extractors):
        print(f"\n  [{i+1}/{len(extractors)}] {name} ({etype})...")
        name_r, success, elapsed, n_results, error = run_extractor(
            name, module, args.max, etype)

        results.append({
            "name": name_r, "success": success, "elapsed": round(elapsed, 1),
            "n_results": n_results, "error": error,
        })

        if success:
            n_success += 1
            total_signatures += n_results
            print(f"    OK  {elapsed:.1f}s  {n_results:,} signatures")
        else:
            n_fail += 1
            err_short = (error or "unknown")[:80]
            print(f"    FAIL  {elapsed:.1f}s  {err_short}")

    # Save results
    report_file = DATA / f"extractor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "max_per_extractor": args.max,
            "n_extractors": len(extractors),
            "n_success": n_success,
            "n_fail": n_fail,
            "total_signatures": total_signatures,
            "results": results,
        }, f, indent=2)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  EXTRACTION COMPLETE")
    print(f"  Success: {n_success}/{len(extractors)}")
    print(f"  Failed:  {n_fail}/{len(extractors)}")
    print(f"  Total signatures: {total_signatures:,}")
    print(f"  Report: {report_file}")

    if n_fail > 0:
        print(f"\n  === FAILURES ===")
        for r in results:
            if not r["success"]:
                print(f"    {r['name']:30s} {(r['error'] or '')[:60]}")

    # Top producers
    print(f"\n  === TOP PRODUCERS ===")
    for r in sorted(results, key=lambda x: -x["n_results"])[:10]:
        if r["n_results"] > 0:
            print(f"    {r['name']:30s} {r['n_results']:>8,} sigs  {r['elapsed']:>6.1f}s")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    main()
