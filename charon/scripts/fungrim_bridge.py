"""
Fungrim Bridge Analysis — Charon
Test whether Fungrim formulas encode numerical values matching EC L-values or knot Mahler measures.

Hypothesis P4.1: Fungrim's "silent island" status is a feature-space problem, not genuine isolation.
"""

import json
import re
import sys
import os
import numpy as np
from collections import defaultdict

import psycopg2
import mpmath

mpmath.mp.dps = 50  # 50 decimal places

OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fungrim_bridge.json")

# ──────────────────────────────────────────────────────────────────────────────
# 1. Known mathematical constants (name -> (value, is_trivial))
#    "trivial" = appears so universally that matching it proves nothing
# ──────────────────────────────────────────────────────────────────────────────

KNOWN_CONSTANTS = {
    "pi": (float(mpmath.pi), True),
    "e": (float(mpmath.e), True),
    "log(2)": (float(mpmath.log(2)), True),
    "log(3)": (float(mpmath.log(3)), True),
    "log(10)": (float(mpmath.log(10)), True),
    "sqrt(2)": (float(mpmath.sqrt(2)), True),
    "sqrt(3)": (float(mpmath.sqrt(3)), True),
    "sqrt(5)": (float(mpmath.sqrt(5)), True),
    "golden_ratio": (float(mpmath.phi), True),
    "euler_gamma": (float(mpmath.euler), True),
    "catalan": (float(mpmath.catalan), True),
    "apery_zeta3": (float(mpmath.zeta(3)), False),  # Apery's constant
    "zeta(2)": (float(mpmath.pi**2 / 6), True),  # = pi^2/6
    "zeta(4)": (float(mpmath.pi**4 / 90), True),
    "zeta(5)": (float(mpmath.zeta(5)), False),
    "zeta(6)": (float(mpmath.pi**6 / 945), True),
    "zeta(7)": (float(mpmath.zeta(7)), False),
    "pi^2": (float(mpmath.pi**2), True),
    "pi^3": (float(mpmath.pi**3), True),
    "pi^4": (float(mpmath.pi**4), True),
    "1/pi": (float(1/mpmath.pi), True),
    "log(pi)": (float(mpmath.log(mpmath.pi)), True),
    "e*pi": (float(mpmath.e * mpmath.pi), False),
    "pi*sqrt(2)": (float(mpmath.pi * mpmath.sqrt(2)), False),
    "pi*sqrt(3)": (float(mpmath.pi * mpmath.sqrt(3)), False),
    # Khinchin, Glaisher-Kinkelin, etc.
    "khinchin": (float(mpmath.khinchin), False),
    "glaisher": (float(mpmath.glaisher), False),
    # L-function related constants
    "L_chi4_1": (float(mpmath.catalan), False),  # L(chi_4, 1) = Catalan (well, beta(1))
    "dirichlet_beta_2": (float(mpmath.catalan), False),
}

# ──────────────────────────────────────────────────────────────────────────────
# 2. LaTeX → mpmath evaluator (best-effort for simple closed-form expressions)
# ──────────────────────────────────────────────────────────────────────────────

def try_parse_latex_value(latex: str) -> list:
    """
    Attempt to extract numerical value(s) from a Fungrim LaTeX equation.
    Returns list of (side_label, float_value) or empty list if unparseable.
    """
    # Strategy: look for patterns we can safely evaluate
    # We target formulas of form LHS = RHS where one side is a known expression

    results = []

    # Skip formulas with free variables, implications, conditions, sums, integrals, limits
    skip_patterns = [
        r'\\implies', r'\\iff', r'\\text\{', r'\\sum_', r'\\prod_',
        r'\\int_', r'\\lim_', r'\\infty', r'\\ldots', r'\\sim',
        r'\\le\b', r'\\ge\b', r'\\ne\b', r'<', r'>',
        r'\\forall', r'\\exists', r'\\in\b',
        r'\\operatorname\{zeros', r'\\operatorname\{poles',
        r'\\operatorname\{Re\}', r'\\operatorname\{Im\}',
        r'\\operatorname\{RH\}',
        r'\\operatorname\{Branch', r'\\operatorname\{Essential',
        r'\\mathbb\{', r'\\subset',
        # Free variable indicators
        r'[^a-z]n[^a-z]', r'[^a-z]s[^a-z]', r'[^a-z]x[^a-z]',
        r'[^a-z]t[^a-z]', r'[^a-z]z[^a-z]',
    ]

    for pat in skip_patterns:
        if re.search(pat, latex):
            return []

    # Must contain '='
    if '=' not in latex:
        return []

    # Try to evaluate the entire expression using known substitutions
    # First, split on '='
    parts = latex.split('=')
    if len(parts) != 2:
        return []

    for i, part in enumerate(parts):
        val = try_eval_latex_expr(part.strip())
        if val is not None and np.isfinite(val):
            results.append((f"side_{i}", val))

    return results


def try_eval_latex_expr(expr: str) -> float:
    """Try to evaluate a LaTeX expression to a float."""

    # Clean up LaTeX
    s = expr
    s = re.sub(r'\\left|\\right|\\!|\\,|\\;|\\:|\\quad|\\qquad', '', s)
    s = re.sub(r'\\bigg?[lr]?', '', s)
    s = s.replace('\\cdot', '*')
    s = s.replace('\\times', '*')

    # Replace known constants
    s = re.sub(r'\{\\pi\}', '(pi)', s)
    s = re.sub(r'\\pi', '(pi)', s)
    s = s.replace('\\gamma', '(euler)')
    s = s.replace('\\varphi', '(phi)')

    # Replace \frac{a}{b} -> (a)/(b)
    # This is tricky with nested braces, do iteratively
    for _ in range(10):
        m = re.search(r'\\frac\{([^{}]*)\}\{([^{}]*)\}', s)
        if m:
            s = s[:m.start()] + f'(({m.group(1)})/({m.group(2)}))' + s[m.end():]
        else:
            break

    # Replace \sqrt{x} -> sqrt(x)
    for _ in range(5):
        m = re.search(r'\\sqrt\{([^{}]*)\}', s)
        if m:
            s = s[:m.start()] + f'sqrt({m.group(1)})' + s[m.end():]
        else:
            break

    # Replace {x}^{y} -> (x)**(y) and x^{y} -> x**(y)
    for _ in range(10):
        m = re.search(r'\{([^{}]*)\}\^\{([^{}]*)\}', s)
        if m:
            s = s[:m.start()] + f'(({m.group(1)})**({m.group(2)}))' + s[m.end():]
        else:
            break
    for _ in range(5):
        m = re.search(r'(\w+)\^\{([^{}]*)\}', s)
        if m:
            s = s[:m.start()] + f'(({m.group(1)})**({m.group(2)}))' + s[m.end():]
        else:
            break

    # Replace \zeta(n) for specific integer n
    m = re.search(r'\\zeta\((\d+)\)', s)
    if m:
        n = int(m.group(1))
        s = s[:m.start()] + f'zeta({n})' + s[m.end():]

    # Replace \log(x)
    s = re.sub(r'\\log', 'log', s)
    s = re.sub(r'\\ln', 'log', s)
    s = re.sub(r'\\exp', 'exp', s)
    s = re.sub(r'\\sin', 'sin', s)
    s = re.sub(r'\\cos', 'cos', s)
    s = re.sub(r'\\tan', 'tan', s)
    s = re.sub(r'\\operatorname\{atan\}', 'atan', s)
    s = re.sub(r'\\operatorname\{asin\}', 'asin', s)
    s = re.sub(r'\\operatorname\{acos\}', 'acos', s)

    # Clean remaining LaTeX
    s = re.sub(r'\\[a-zA-Z]+', '', s)  # remove remaining commands
    s = s.replace('{', '(').replace('}', ')')
    s = s.replace(')(', ')*(')

    # Add multiplication between number and (
    s = re.sub(r'(\d)\(', r'\1*(', s)
    s = re.sub(r'\)(\d)', r')*\1', s)
    s = re.sub(r'\)\(', r')*(', s)

    # Remove empty parens and spaces
    s = s.strip()
    if not s or s in ('', '()', '0'):
        return None

    # Only allow safe characters
    safe = set('0123456789.+-*/() ')
    safe_funcs = ['pi', 'euler', 'phi', 'sqrt', 'log', 'exp', 'sin', 'cos', 'tan',
                  'atan', 'asin', 'acos', 'zeta']

    # Build evaluation namespace
    ns = {
        'pi': mpmath.pi,
        'euler': mpmath.euler,
        'phi': mpmath.phi,
        'sqrt': mpmath.sqrt,
        'log': mpmath.log,
        'exp': mpmath.exp,
        'sin': mpmath.sin,
        'cos': mpmath.cos,
        'tan': mpmath.tan,
        'atan': mpmath.atan,
        'asin': mpmath.asin,
        'acos': mpmath.acos,
        'zeta': mpmath.zeta,
        'G': mpmath.catalan,  # Catalan's constant often written as G
    }

    try:
        # Safety check: no imports, no builtins
        val = eval(s, {"__builtins__": {}}, ns)
        return float(val)
    except:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# 3. Load EC L-values from LMFDB
# ──────────────────────────────────────────────────────────────────────────────

def load_ec_lvalues(limit=100000):
    """Load EC L(E,1) values for rank-0 curves."""
    print(f"Loading EC L-values (limit={limit})...")
    conn = psycopg2.connect(
        host='localhost', port=5432, user='postgres',
        password='prometheus', dbname='lmfdb'
    )
    cur = conn.cursor()
    cur.execute(f"""
        SELECT CAST(leading_term AS double precision), origin
        FROM lfunc_lfunctions
        WHERE origin LIKE 'EllipticCurve/Q/%%'
          AND order_of_vanishing = '0'
        LIMIT {limit}
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Loaded {len(rows)} EC L-values")
    return {row[1]: row[0] for row in rows if row[0] is not None}


# ──────────────────────────────────────────────────────────────────────────────
# 4. Load Mahler measures
# ──────────────────────────────────────────────────────────────────────────────

def load_mahler_measures():
    """Load knot Mahler measures from precomputed JSON."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mahler_measures.json")
    with open(path) as f:
        data = json.load(f)
    # Use log_mahler_root as the canonical value
    measures = {}
    for entry in data:
        name = entry['name']
        for key in ['log_mahler_root', 'log_mahler_num', 'mahler_root', 'mahler_num']:
            if key in entry and entry[key] is not None:
                measures[f"{name}_{key}"] = entry[key]
    print(f"  Loaded {len(measures)} Mahler measure values from {len(data)} knots")
    return measures


# ──────────────────────────────────────────────────────────────────────────────
# 5. Load and parse Fungrim formulas
# ──────────────────────────────────────────────────────────────────────────────

def load_fungrim():
    """Load all Fungrim equations and attempt evaluation."""
    print("Loading Fungrim formulas...")
    conn = psycopg2.connect(
        host='localhost', port=5432, user='postgres',
        password='prometheus', dbname='prometheus_sci'
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT fungrim_id, module, formula_text, formula_type
        FROM analysis.fungrim
        WHERE formula_type = 'equation'
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Loaded {len(rows)} equations")

    evaluated = []
    failed = 0
    for fid, module, text, ftype in rows:
        vals = try_parse_latex_value(text)
        if vals:
            for label, val in vals:
                if abs(val) > 1e-15:  # skip near-zero
                    evaluated.append({
                        "fungrim_id": fid,
                        "module": module,
                        "formula_text": text[:200],
                        "side": label,
                        "value": val,
                    })
        else:
            failed += 1

    print(f"  Evaluated {len(evaluated)} values from {len(rows)} equations ({failed} unparseable)")
    return evaluated


# ──────────────────────────────────────────────────────────────────────────────
# 6. Matching engine
# ──────────────────────────────────────────────────────────────────────────────

def is_trivial_value(val, tol=1e-6):
    """Check if a value is a trivial constant (integer, simple pi multiple, etc.)."""
    abs_val = abs(val)
    # Small integers
    if abs_val < 100 and abs(abs_val - round(abs_val)) < tol:
        return True
    # Simple rational multiples of pi: n*pi/m for n,m in 1..20
    pi_val = float(mpmath.pi)
    for num in range(1, 21):
        for den in range(1, 21):
            if abs(abs_val - pi_val * num / den) < tol:
                return True
    # Simple powers of e, sqrt(n) for small n
    for base in [float(mpmath.e), float(mpmath.sqrt(2)), float(mpmath.sqrt(3)),
                 float(mpmath.sqrt(5)), float(mpmath.phi), float(mpmath.log(2)),
                 float(mpmath.log(3)), float(mpmath.euler), float(mpmath.catalan)]:
        if abs(abs_val - base) < tol:
            return True
        for mult in range(2, 10):
            if abs(abs_val - base * mult) < tol:
                return True
    # pi^n for small n
    for n in range(2, 6):
        pn = float(mpmath.pi**n)
        for den in range(1, 100):
            if abs(abs_val - pn / den) < tol:
                return True
    return False


def find_matches(fungrim_vals, ec_lvals, mahler_vals, tol=1e-6):
    """Find numerical matches between Fungrim values and target sets."""

    results = {
        "ec_matches": [],
        "ec_matches_nontrivial": [],
        "mahler_matches": [],
        "mahler_matches_nontrivial": [],
        "constant_matches_trivial": [],
        "constant_matches_nontrivial": [],
    }

    # Build sorted arrays for fast matching
    ec_items = list(ec_lvals.items())  # (origin, value)
    ec_values = np.array([v for _, v in ec_items])

    mahler_items = list(mahler_vals.items())  # (name, value)
    mahler_values = np.array([v for _, v in mahler_items])

    for entry in fungrim_vals:
        val = entry["value"]
        abs_val = abs(val)
        trivial = is_trivial_value(val, tol)

        # Match against known constants
        for cname, (cval, is_trivial_const) in KNOWN_CONSTANTS.items():
            if abs(abs_val - abs(cval)) < tol or (abs(cval) > 1e-10 and abs(abs_val / abs(cval) - 1) < tol):
                match = {
                    "fungrim_id": entry["fungrim_id"],
                    "module": entry["module"],
                    "formula_text": entry["formula_text"],
                    "value": val,
                    "matched_constant": cname,
                    "constant_value": cval,
                    "abs_diff": abs(abs_val - abs(cval)),
                }
                if is_trivial_const:
                    results["constant_matches_trivial"].append(match)
                else:
                    results["constant_matches_nontrivial"].append(match)

        # Match against EC L-values
        if len(ec_values) > 0:
            diffs = np.abs(ec_values - abs_val)
            best_idx = np.argmin(diffs)
            if diffs[best_idx] < tol:
                match_entry = {
                    "fungrim_id": entry["fungrim_id"],
                    "module": entry["module"],
                    "formula_text": entry["formula_text"],
                    "value": val,
                    "matched_ec": ec_items[best_idx][0],
                    "ec_lvalue": ec_items[best_idx][1],
                    "abs_diff": float(diffs[best_idx]),
                    "is_trivial_value": trivial,
                }
                results["ec_matches"].append(match_entry)
                if not trivial:
                    results["ec_matches_nontrivial"].append(match_entry)

        # Match against Mahler measures
        if len(mahler_values) > 0:
            diffs = np.abs(mahler_values - abs_val)
            best_idx = np.argmin(diffs)
            if diffs[best_idx] < tol:
                match_entry = {
                    "fungrim_id": entry["fungrim_id"],
                    "module": entry["module"],
                    "formula_text": entry["formula_text"],
                    "value": val,
                    "matched_knot": mahler_items[best_idx][0],
                    "mahler_value": mahler_items[best_idx][1],
                    "abs_diff": float(diffs[best_idx]),
                    "is_trivial_value": trivial,
                }
                results["mahler_matches"].append(match_entry)
                if not trivial:
                    results["mahler_matches_nontrivial"].append(match_entry)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# 7. Permutation null test
# ──────────────────────────────────────────────────────────────────────────────

def permutation_null(fungrim_values, target_values, tol=1e-6, n_perms=1000):
    """
    Test whether the observed match count exceeds null expectation.
    Null: draw random values from the target value range and count matches.
    This tests whether Fungrim values hit the target set more than random
    values drawn from the same numerical range would.
    """
    if len(fungrim_values) == 0 or len(target_values) == 0:
        return {"observed": 0, "null_mean": 0, "null_std": 0, "z_score": 0, "p_upper": 1.0}

    fv = np.array(fungrim_values)
    tv = np.array(target_values)
    tv_sorted = np.sort(tv)

    # Filter out trivial integers (0, 1, 2, 3, -1, etc.)
    nontrivial_mask = np.array([abs(v) > 3.5 or (abs(v - round(v)) > 1e-10) for v in fv])
    fv_nt = fv[nontrivial_mask]

    if len(fv_nt) == 0:
        return {"observed": 0, "null_mean": 0, "null_std": 0, "z_score": 0, "p_upper": 1.0,
                "note": "all fungrim values are trivial integers"}

    # Observed matches (nontrivial values only)
    observed = 0
    for v in fv_nt:
        idx = np.searchsorted(tv_sorted, abs(v))
        for check_idx in [max(0, idx-1), min(len(tv_sorted)-1, idx)]:
            if abs(tv_sorted[check_idx] - abs(v)) < tol:
                observed += 1
                break

    # Null: replace Fungrim values with random draws from same range
    rng = np.random.default_rng(42)
    vmin, vmax = tv.min(), tv.max()
    null_counts = []
    for _ in range(n_perms):
        fake_fv = rng.uniform(vmin, vmax, size=len(fv_nt))
        count = 0
        for v in fake_fv:
            idx = np.searchsorted(tv_sorted, v)
            for check_idx in [max(0, idx-1), min(len(tv_sorted)-1, idx)]:
                if abs(tv_sorted[check_idx] - v) < tol:
                    count += 1
                    break
        null_counts.append(count)

    null_counts = np.array(null_counts)
    null_mean = null_counts.mean()
    null_std = null_counts.std() if null_counts.std() > 0 else 1e-10
    z = (observed - null_mean) / null_std
    p = np.mean(null_counts >= observed)

    return {
        "observed": int(observed),
        "nontrivial_fungrim_values": int(len(fv_nt)),
        "null_mean": float(null_mean),
        "null_std": float(null_std),
        "z_score": float(z),
        "p_upper": float(p),
    }


# ──────────────────────────────────────────────────────────────────────────────
# 8. Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("CHARON — Fungrim Bridge Analysis")
    print("Testing P4.1: Do Fungrim formulas encode EC L-values or Mahler measures?")
    print("=" * 70)

    # Load data
    fungrim_vals = load_fungrim()
    ec_lvals = load_ec_lvalues(limit=100000)
    mahler_vals = load_mahler_measures()

    # Find matches
    print("\nMatching Fungrim values against targets (tol=1e-6)...")
    matches = find_matches(fungrim_vals, ec_lvals, mahler_vals, tol=1e-6)

    print(f"\n--- Results ---")
    print(f"  Fungrim values evaluated:       {len(fungrim_vals)}")
    print(f"  EC L-values loaded:             {len(ec_lvals)}")
    print(f"  Mahler measure values loaded:   {len(mahler_vals)}")
    print(f"  Trivial constant matches:       {len(matches['constant_matches_trivial'])}")
    print(f"  Non-trivial constant matches:   {len(matches['constant_matches_nontrivial'])}")
    print(f"  EC L-value matches (all):       {len(matches['ec_matches'])}")
    print(f"  EC L-value matches (nontrivial):{len(matches['ec_matches_nontrivial'])}")
    print(f"  Mahler matches (all):           {len(matches['mahler_matches'])}")
    print(f"  Mahler matches (nontrivial):    {len(matches['mahler_matches_nontrivial'])}")

    # Filter trivial matches (integers 0,1,2,3 etc.)
    def is_nontrivial(val):
        return abs(val) > 3.5 or abs(val - round(val)) > 1e-10

    ec_nontrivial = [m for m in matches['ec_matches'] if is_nontrivial(m['value'])]
    mahler_nontrivial = [m for m in matches['mahler_matches'] if is_nontrivial(m['value'])]
    ec_trivial = [m for m in matches['ec_matches'] if not is_nontrivial(m['value'])]
    mahler_trivial = [m for m in matches['mahler_matches'] if not is_nontrivial(m['value'])]

    print(f"  EC matches (nontrivial):        {len(ec_nontrivial)}")
    print(f"  EC matches (trivial int):       {len(ec_trivial)}")
    print(f"  Mahler matches (nontrivial):    {len(mahler_nontrivial)}")
    print(f"  Mahler matches (trivial int):   {len(mahler_trivial)}")

    # Detail nontrivial EC or Mahler matches
    if ec_nontrivial:
        print("\n  === EC L-value matches (NONTRIVIAL) ===")
        for m in ec_nontrivial:
            # Check if this is just a common constant in disguise
            val = m['value']
            common_note = ""
            for cname, (cval, _) in KNOWN_CONSTANTS.items():
                if abs(abs(val) - abs(cval)) < 1e-6:
                    common_note = f" [NOTE: ~{cname}]"
                    break
            # Check simple fractions of pi
            for num in range(1, 20):
                for den in range(1, 20):
                    if abs(abs(val) - float(mpmath.pi) * num / den) < 1e-6:
                        common_note = f" [NOTE: ~{num}*pi/{den}]"
                        break
            print(f"    {m['fungrim_id']} [{m['module']}]: val={m['value']:.10f} "
                  f"= L({m['matched_ec']}) = {m['ec_lvalue']:.10f} "
                  f"(diff={m['abs_diff']:.2e}){common_note}")

    if mahler_nontrivial:
        print("\n  === Mahler measure matches (NONTRIVIAL) ===")
        for m in mahler_nontrivial:
            print(f"    {m['fungrim_id']} [{m['module']}]: val={m['value']:.10f} "
                  f"= M({m['matched_knot']}) = {m['mahler_value']:.10f} (diff={m['abs_diff']:.2e})")

    if matches['constant_matches_nontrivial']:
        print("\n  === Non-trivial constant matches ===")
        for m in matches['constant_matches_nontrivial'][:20]:
            print(f"    {m['fungrim_id']} [{m['module']}]: val={m['value']:.10f} "
                  f"= {m['matched_constant']} = {m['constant_value']:.10f}")

    # Permutation null tests — only on nontrivial values
    print("\n--- Permutation null tests (1000 permutations, nontrivial values only) ---")
    fv_array = [abs(e["value"]) for e in fungrim_vals if not is_trivial_value(e["value"])]
    print(f"  Nontrivial Fungrim values: {len(fv_array)}")

    # EC null
    ec_null = permutation_null(
        fv_array, list(ec_lvals.values()), tol=1e-6, n_perms=1000
    )
    print(f"  EC L-values:  observed={ec_null['observed']}, "
          f"null={ec_null['null_mean']:.2f}+/-{ec_null['null_std']:.2f}, "
          f"z={ec_null['z_score']:.2f}, p={ec_null['p_upper']:.4f}")

    # Mahler null
    mahler_null = permutation_null(
        fv_array, list(mahler_vals.values()), tol=1e-6, n_perms=1000
    )
    print(f"  Mahler:       observed={mahler_null['observed']}, "
          f"null={mahler_null['null_mean']:.2f}+/-{mahler_null['null_std']:.2f}, "
          f"z={mahler_null['z_score']:.2f}, p={mahler_null['p_upper']:.4f}")

    # Verdict — only nontrivial matches count
    print("\n--- VERDICT ---")
    ec_interesting = len(matches['ec_matches_nontrivial']) > 0 and ec_null['z_score'] > 3
    mahler_interesting = len(matches['mahler_matches_nontrivial']) > 0 and mahler_null['z_score'] > 3

    if ec_interesting:
        print("  EC L-values: SIGNAL DETECTED (z > 3)")
    else:
        print("  EC L-values: No signal above null expectation")

    if mahler_interesting:
        print("  Mahler measures: SIGNAL DETECTED (z > 3)")
    else:
        print("  Mahler measures: No signal above null expectation")

    if not ec_interesting and not mahler_interesting:
        print("  P4.1 NEGATIVE: Fungrim's isolation is NOT explained by hidden numerical bridges")
        print("  The silence is genuine — Fungrim formulas don't encode specific L-values or Mahler measures")
        print("  (Trivial constant matches like pi, zeta(2) etc. are expected and uninformative)")

    # Build output
    output = {
        "hypothesis": "P4.1: Fungrim formulas encode EC L-values or knot Mahler measures",
        "date": "2026-04-15",
        "fungrim_equations_total": None,  # filled below
        "fungrim_values_evaluated": len(fungrim_vals),
        "ec_lvalues_tested": len(ec_lvals),
        "mahler_measures_tested": len(mahler_vals),
        "tolerance": 1e-6,
        "matches": {
            "trivial_constants": len(matches['constant_matches_trivial']),
            "nontrivial_constants": len(matches['constant_matches_nontrivial']),
            "ec_lvalues_all": len(matches['ec_matches']),
            "ec_lvalues_nontrivial": len(matches['ec_matches_nontrivial']),
            "mahler_measures_all": len(matches['mahler_matches']),
            "mahler_measures_nontrivial": len(matches['mahler_matches_nontrivial']),
        },
        "match_details": {
            "ec_all": matches['ec_matches'],
            "ec_nontrivial": matches['ec_matches_nontrivial'],
            "mahler_nontrivial": matches['mahler_matches_nontrivial'],
            "nontrivial_constants": matches['constant_matches_nontrivial'][:50],
        },
        "null_tests": {
            "ec": ec_null,
            "mahler": mahler_null,
        },
        "verdict": {
            "ec_signal": ec_interesting,
            "mahler_signal": mahler_interesting,
            "p4_1_supported": ec_interesting or mahler_interesting,
            "interpretation": (
                "Signal detected — investigate specific matches"
                if ec_interesting or mahler_interesting
                else "P4.1 negative: Fungrim isolation is genuine, not a feature-space artifact"
            ),
        },
        "caveats": [
            "LaTeX parser handles only simple closed-form expressions",
            "Many Fungrim formulas contain free variables and cannot be evaluated to constants",
            "Tolerance 1e-6 is conservative; LMFDB leading_term has ~11 digit precision",
            "Trivial constant matches (pi, e, sqrt(2), etc.) are expected and uninformative",
        ],
    }

    # Get total equation count
    conn = psycopg2.connect(
        host='localhost', port=5432, user='postgres',
        password='prometheus', dbname='prometheus_sci'
    )
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM analysis.fungrim WHERE formula_type='equation'")
    output["fungrim_equations_total"] = cur.fetchone()[0]
    conn.close()

    # Save
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
