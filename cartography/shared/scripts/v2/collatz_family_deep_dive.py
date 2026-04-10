"""
Collatz Algebraic Family Deep Dive (Challenge C17)
===================================================
The C08 challenge discovered that x^4 - 2x^2 + 1 = (x-1)^2(x+1)^2 is shared
by 38 OEIS sequences. This script investigates whether this constitutes a
genuine "Collatz family" or is merely a collection of sequences that share
a trivial recurrence.

General solution: a(n) = (A + B*n) + (-1)^n * (C + D*n)

Recurrence: a(n) = 2*a(n-2) - a(n-4)

Usage:
    python collatz_family_deep_dive.py
"""

import gzip
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
S33_FILE = ROOT / "cartography" / "convergence" / "data" / "recursion_operator_signatures.jsonl"
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_FB = ROOT / "cartography" / "oeis" / "data" / "stripped.gz"
OEIS_NAMES = ROOT / "cartography" / "oeis" / "data" / "names.txt"
OEIS_CROSSREFS = ROOT / "cartography" / "oeis" / "data" / "oeis_crossrefs.jsonl"
C08_RESULTS = Path(__file__).resolve().parent / "recurrence_euler_factor_results.json"
OUT_FILE = Path(__file__).resolve().parent / "collatz_family_results.json"

TARGET_COEFFS = [0, -2, 0, 1]  # x^4 + 0*x^3 - 2*x^2 + 0*x + 1 = (x^2-1)^2


# ---------------------------------------------------------------------------
# Berlekamp-Massey (from C08)
# ---------------------------------------------------------------------------

def berlekamp_massey(sequence):
    """Minimal LFSR via Berlekamp-Massey."""
    n = len(sequence)
    if n == 0:
        return [], 0
    s = [float(x) for x in sequence]
    b = [1.0]
    c = [1.0]
    l_deg = 0
    m = 1
    d = 1.0
    for i in range(n):
        disc = s[i]
        for j in range(1, l_deg + 1):
            if j < len(c):
                disc += c[j] * s[i - j]
        if abs(disc) < 1e-10:
            m += 1
        elif 2 * l_deg <= i:
            t = list(c)
            coef = -disc / d
            while len(c) < len(b) + m:
                c.append(0.0)
            for j in range(len(b)):
                c[j + m] += coef * b[j]
            l_deg = i + 1 - l_deg
            b = t
            d = disc
            m = 1
        else:
            coef = -disc / d
            while len(c) < len(b) + m:
                c.append(0.0)
            for j in range(len(b)):
                c[j + m] += coef * b[j]
            m += 1
    coeffs = c[1:l_deg + 1]
    return coeffs, l_deg


# ---------------------------------------------------------------------------
# OEIS loaders
# ---------------------------------------------------------------------------

def load_oeis_sequences(min_length=8):
    """Load OEIS sequences from stripped_full.gz."""
    src = OEIS_STRIPPED if OEIS_STRIPPED.exists() else OEIS_STRIPPED_FB
    if not src.exists():
        print(f"  ERROR: no OEIS stripped file at {src}")
        return {}
    seqs = {}
    with gzip.open(str(src), "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            sid = parts[0].strip()
            if not sid.startswith("A"):
                continue
            terms_str = parts[1].strip().strip(",")
            try:
                terms = [int(t) for t in terms_str.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) >= min_length:
                seqs[sid] = terms
    return seqs


def load_names():
    """Load OEIS sequence names."""
    names = {}
    if not OEIS_NAMES.exists():
        return names
    with open(OEIS_NAMES, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) == 2 and parts[0].startswith("A"):
                names[parts[0]] = parts[1].strip()
    return names


def load_crossrefs():
    """Load OEIS cross-references as adjacency dict."""
    refs = defaultdict(set)
    if not OEIS_CROSSREFS.exists():
        return refs
    with open(OEIS_CROSSREFS, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            s, t = obj["source"], obj["target"]
            refs[s].add(t)
            refs[t].add(s)
    return refs


def load_s33_matches():
    """Load sequences matching target char poly from S33 cache."""
    matches = []
    if not S33_FILE.exists():
        return matches
    with open(S33_FILE, "r") as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("is_linear_recurrence") and obj.get("characteristic_coeffs") == TARGET_COEFFS:
                matches.append(obj["seq_id"])
    return matches


# ---------------------------------------------------------------------------
# Step 1: Find ALL 38 sequences
# ---------------------------------------------------------------------------

def find_all_collatz_family(oeis_seqs, s33_matches):
    """Reconstruct the full 38-sequence family."""
    # Start with S33 matches
    found = set(s33_matches)

    # Also scan OEIS sequences with BM to find the rest
    print(f"  S33 matches: {len(found)}")
    print(f"  Scanning OEIS for additional matches...")

    scanned = 0
    for sid, terms in oeis_seqs.items():
        if sid in found:
            continue
        if len(terms) < 30:
            continue
        coeffs, deg = berlekamp_massey(terms)
        if deg == 4:
            rounded = [round(c) for c in coeffs]
            if rounded == TARGET_COEFFS:
                # Verify recurrence
                if verify_recurrence(terms, deg=4):
                    found.add(sid)
        scanned += 1
        if scanned % 10000 == 0:
            print(f"    scanned {scanned}... found {len(found)} total")

    print(f"  Total found: {len(found)}")
    return sorted(found)


# ---------------------------------------------------------------------------
# Step 2: Verify recurrence a(n) = 2*a(n-2) - a(n-4)
# ---------------------------------------------------------------------------

def verify_recurrence(terms, deg=4):
    """Check if a(n) = 2*a(n-2) - a(n-4) holds."""
    if len(terms) < deg + 2:
        return False
    errors = 0
    checks = 0
    for i in range(4, len(terms)):
        predicted = 2 * terms[i - 2] - terms[i - 4]
        if predicted != terms[i]:
            errors += 1
        checks += 1
    return errors == 0


def verify_recurrence_detail(terms):
    """Return detailed recurrence verification info."""
    if len(terms) < 6:
        return {"holds": False, "reason": "too_few_terms", "errors": 0, "checks": 0}
    errors = 0
    checks = 0
    first_error_idx = None
    for i in range(4, len(terms)):
        predicted = 2 * terms[i - 2] - terms[i - 4]
        if predicted != terms[i]:
            errors += 1
            if first_error_idx is None:
                first_error_idx = i
        checks += 1
    return {
        "holds": errors == 0,
        "errors": errors,
        "checks": checks,
        "error_rate": errors / checks if checks > 0 else 0,
        "first_error_idx": first_error_idx,
        "holds_for_first_n": first_error_idx if first_error_idx is not None else len(terms),
    }


# ---------------------------------------------------------------------------
# Step 3: Fit (A, B, C, D) parameters
# ---------------------------------------------------------------------------

def fit_abcd(terms):
    """
    Fit a(n) = (A + B*n) + (-1)^n * (C + D*n) using least squares.
    Returns (A, B, C, D, residual_norm).
    """
    n_terms = len(terms)
    if n_terms < 4:
        return None

    # Build design matrix: columns are [1, n, (-1)^n, n*(-1)^n]
    ns = np.arange(n_terms, dtype=np.float64)
    signs = np.array([(-1) ** i for i in range(n_terms)], dtype=np.float64)

    M = np.column_stack([
        np.ones(n_terms),  # A
        ns,                # B
        signs,             # C
        ns * signs,        # D
    ])

    y = np.array(terms, dtype=np.float64)

    # Solve via least squares
    result = np.linalg.lstsq(M, y, rcond=None)
    params = result[0]  # A, B, C, D

    # Compute residuals
    predicted = M @ params
    residuals = y - predicted
    residual_norm = np.sqrt(np.sum(residuals ** 2))
    max_residual = np.max(np.abs(residuals))

    return {
        "A": float(params[0]),
        "B": float(params[1]),
        "C": float(params[2]),
        "D": float(params[3]),
        "residual_norm": float(residual_norm),
        "max_residual": float(max_residual),
        "exact_fit": max_residual < 0.5,  # integer sequences
    }


def classify_sequence(name, fit, terms):
    """Classify based on name and ABCD parameters."""
    if fit is None:
        return "unknown"

    A, B, C, D = fit["A"], fit["B"], fit["C"], fit["D"]

    # Check for exact integer parameters
    a_int = abs(A - round(A)) < 0.01
    b_int = abs(B - round(B)) < 0.01
    c_int = abs(C - round(C)) < 0.01
    d_int = abs(D - round(D)) < 0.01

    if not fit["exact_fit"]:
        return "approximate_only"

    # All zero except B -> a(n) = Bn (linear)
    if abs(A) < 0.5 and abs(C) < 0.5 and abs(D) < 0.5 and abs(B) > 0.01:
        return "trivial_linear"

    # Pure alternating: only C or D nonzero
    if abs(A) < 0.5 and abs(B) < 0.5 and (abs(C) > 0.01 or abs(D) > 0.01):
        return "trivial_alternating"

    # Only A and C nonzero -> constant + alternating constant
    if abs(B) < 0.01 and abs(D) < 0.01:
        return "trivial_constant_alternating"

    # B and D nonzero but not A, C -> n and (-1)^n * n
    if abs(A) < 0.5 and abs(C) < 0.5:
        return "linear_times_alternating"

    # General but simple integer parameters
    if a_int and b_int and c_int and d_int:
        # Check for Collatz keywords
        name_lower = name.lower() if name else ""
        if "collatz" in name_lower or "3x+1" in name_lower or "3n+1" in name_lower:
            return "collatz_adjacent"
        return "general_linear_combo"

    return "general_linear_combo"


def parameter_signature(fit):
    """Create a signature for clustering."""
    if fit is None or not fit["exact_fit"]:
        return "non_exact"
    A, B, C, D = round(fit["A"], 4), round(fit["B"], 4), round(fit["C"], 4), round(fit["D"], 4)
    # Normalize: determine which params are zero, half-integer, integer, etc.
    pattern = []
    for label, val in [("A", A), ("B", B), ("C", C), ("D", D)]:
        if abs(val) < 0.01:
            pattern.append(f"{label}=0")
        elif abs(val - round(val)) < 0.01:
            pattern.append(f"{label}=int")
        elif abs(val * 2 - round(val * 2)) < 0.01:
            pattern.append(f"{label}=half")
        elif abs(val * 4 - round(val * 4)) < 0.01:
            pattern.append(f"{label}=quarter")
        else:
            pattern.append(f"{label}=other")
    return "|".join(pattern)


# ---------------------------------------------------------------------------
# Step 4: Phase space analysis
# ---------------------------------------------------------------------------

def phase_space_analysis(terms):
    """Compute phase space properties from (a(n), a(n+1)) trajectory."""
    if len(terms) < 10:
        return None

    arr = np.array(terms, dtype=np.float64)

    # Lyapunov exponent estimate: average log|a(n+1)/a(n)|
    ratios = []
    for i in range(len(arr) - 1):
        if abs(arr[i]) > 1e-10:
            ratios.append(abs(arr[i + 1] / arr[i]))
    if ratios:
        log_ratios = [math.log(r) for r in ratios if r > 0]
        lyapunov = np.mean(log_ratios) if log_ratios else 0.0
    else:
        lyapunov = 0.0

    # Growth classification
    abs_terms = np.abs(arr)
    if len(abs_terms) > 5:
        growth_ratio = abs_terms[-1] / max(abs_terms[4], 1e-10)
        if growth_ratio > 100:
            growth_type = "divergent"
        elif growth_ratio < 0.01:
            growth_type = "convergent"
        elif abs(growth_ratio - 1) < 0.1:
            growth_type = "bounded"
        else:
            growth_type = "moderate"
    else:
        growth_type = "unknown"
        growth_ratio = 0.0

    # Oscillation: count sign changes
    sign_changes = sum(1 for i in range(len(arr) - 1) if arr[i] * arr[i + 1] < 0)
    oscillation_rate = sign_changes / max(len(arr) - 1, 1)

    # Phase space dimension estimate (consecutive differences)
    if len(arr) > 3:
        diffs = np.diff(arr)
        if np.std(diffs) > 1e-10:
            autocorr = np.corrcoef(diffs[:-1], diffs[1:])[0, 1] if len(diffs) > 2 else 0
        else:
            autocorr = 1.0
    else:
        autocorr = 0.0

    return {
        "lyapunov_estimate": float(lyapunov),
        "growth_type": growth_type,
        "oscillation_rate": float(oscillation_rate),
        "autocorrelation": float(autocorr) if not math.isnan(autocorr) else 0.0,
        "n_terms": len(terms),
    }


# ---------------------------------------------------------------------------
# Step 5: Cross-reference analysis
# ---------------------------------------------------------------------------

def cross_reference_analysis(family_ids, crossrefs):
    """Analyze cross-references among family members."""
    family_set = set(family_ids)

    # Internal edges: cross-references within the family
    internal_edges = []
    for sid in family_ids:
        for target in crossrefs.get(sid, set()):
            if target in family_set and target > sid:  # avoid duplicates
                internal_edges.append((sid, target))

    # External connections: which non-family sequences are referenced
    external_counts = defaultdict(int)
    for sid in family_ids:
        for target in crossrefs.get(sid, set()):
            if target not in family_set:
                external_counts[target] += 1

    # Connected components via BFS
    visited = set()
    components = []
    for sid in family_ids:
        if sid in visited:
            continue
        component = set()
        queue = [sid]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            component.add(node)
            for target in crossrefs.get(node, set()):
                if target in family_set and target not in visited:
                    queue.append(target)
        components.append(sorted(component))

    # Top external connections
    top_external = sorted(external_counts.items(), key=lambda x: -x[1])[:20]

    return {
        "n_internal_edges": len(internal_edges),
        "internal_edges": internal_edges[:50],
        "n_components": len(components),
        "component_sizes": [len(c) for c in components],
        "components": components,
        "top_external_refs": [{"seq": s, "count": c} for s, c in top_external],
        "is_connected": len(components) == 1,
    }


# ---------------------------------------------------------------------------
# Step 6: Collatz-specific analysis
# ---------------------------------------------------------------------------

def collatz_analysis(terms_a006370, all_terms):
    """Deep analysis of A006370 (Collatz map) specifically."""
    result = {}

    if terms_a006370 is None:
        result["a006370_present"] = False
        return result

    result["a006370_present"] = True
    result["n_terms"] = len(terms_a006370)

    # Verify recurrence
    rec = verify_recurrence_detail(terms_a006370)
    result["recurrence_detail"] = rec

    # The Collatz map is: a(n) = n/2 if n even, (3n+1)/2 if n odd
    # = n/2 if n even, (3n+1)/2 if n odd
    # As a function of n: this is NOT a linear recurrence globally.
    # But for even n: a(n) = n/2 → a(n) = 0.5 * n
    # For odd n: a(n) = (3n+1)/2 → a(n) = 1.5 * n + 0.5
    # Combined: a(n) = n/2 + (-1)^(n+1) * (n/2 + 1/4) ???
    # Actually, let's just check what happens.

    # The OEIS definition of A006370: a(n) = n/2 if n even, 3n+1 if n odd
    # Check if terms match this
    collatz_expected = []
    for n in range(len(terms_a006370)):
        if n % 2 == 0:
            collatz_expected.append(n // 2)
        else:
            collatz_expected.append(3 * n + 1)

    match_collatz_def = all(
        terms_a006370[i] == collatz_expected[i]
        for i in range(min(len(terms_a006370), len(collatz_expected)))
    )
    result["matches_collatz_definition"] = match_collatz_def

    # Check: does ABCD fit work?
    # For even n: a(n) = n/2
    # For odd n: a(n) = 3n+1
    # a(n) = (A + Bn) + (-1)^n * (C + Dn)
    # Even n ((-1)^n = 1): a(n) = (A+C) + (B+D)*n = n/2
    #   → A+C = 0, B+D = 1/2
    # Odd n ((-1)^n = -1): a(n) = (A-C) + (B-D)*n = 3n+1
    #   → A-C = 1, B-D = 3
    # Solving: A = 1/2, B = 7/4, C = -1/2, D = -5/4
    # Wait, let me redo:
    # A + C = 0 → C = -A
    # A - C = 1 → A + A = 1 → A = 1/2, C = -1/2
    # B + D = 1/2
    # B - D = 3 → 2B = 3.5 → B = 7/4, D = -5/4
    result["predicted_ABCD"] = {"A": 0.5, "B": 1.75, "C": -0.5, "D": -1.25}
    result["explanation"] = (
        "A006370 (Collatz map: n/2 if even, 3n+1 if odd) IS an exact member of "
        "the (x-1)^2(x+1)^2 family. It has the closed form "
        "a(n) = (1/2 + 7n/4) + (-1)^n*(-1/2 - 5n/4) = "
        "n/2 when n even, 3n+1 when n odd. The recurrence a(n)=2a(n-2)-a(n-4) "
        "holds exactly because both the even and odd subsequences are linear in n."
    )

    return result


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("COLLATZ ALGEBRAIC FAMILY DEEP DIVE (C17)")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------
    print("\n[1] Loading data...")
    print("  Loading OEIS sequences...")
    oeis_seqs = load_oeis_sequences(min_length=8)
    print(f"  Loaded {len(oeis_seqs)} sequences")

    print("  Loading names...")
    names = load_names()
    print(f"  Loaded {len(names)} names")

    print("  Loading S33 matches...")
    s33_matches = load_s33_matches()
    print(f"  S33 matches: {len(s33_matches)}")

    # ------------------------------------------------------------------
    # Find all 38 sequences
    # ------------------------------------------------------------------
    print("\n[2] Finding all sequences with char poly (x-1)^2(x+1)^2...")
    family_ids = find_all_collatz_family(oeis_seqs, s33_matches)
    print(f"  Family size: {len(family_ids)}")

    # ------------------------------------------------------------------
    # Analyze each sequence
    # ------------------------------------------------------------------
    print("\n[3] Analyzing each sequence...")
    family_data = []
    for sid in family_ids:
        terms = oeis_seqs.get(sid, [])
        name = names.get(sid, "Unknown")
        rec_detail = verify_recurrence_detail(terms)
        fit = fit_abcd(terms)
        classification = classify_sequence(name, fit, terms)
        phase = phase_space_analysis(terms)
        sig = parameter_signature(fit)

        entry = {
            "seq_id": sid,
            "name": name,
            "n_terms": len(terms),
            "first_terms": terms[:15],
            "recurrence_verification": rec_detail,
            "abcd_fit": fit,
            "classification": classification,
            "parameter_signature": sig,
            "phase_space": phase,
        }
        family_data.append(entry)

        status = "EXACT" if rec_detail["holds"] else f"FAILS@{rec_detail['first_error_idx']}"
        fit_status = "EXACT" if (fit and fit["exact_fit"]) else "APPROX"
        print(f"  {sid} [{status}|{fit_status}] {classification:30s} {name[:60]}")

    # ------------------------------------------------------------------
    # Clustering by parameter signature
    # ------------------------------------------------------------------
    print("\n[4] Clustering by parameter signature...")
    clusters = defaultdict(list)
    for entry in family_data:
        clusters[entry["parameter_signature"]].append(entry["seq_id"])

    print(f"  Found {len(clusters)} distinct parameter signatures:")
    for sig, members in sorted(clusters.items(), key=lambda x: -len(x[1])):
        print(f"    [{len(members):2d}] {sig}: {members[:5]}{'...' if len(members)>5 else ''}")

    # More detailed ABCD clustering: group by rounded (A,B,C,D)
    abcd_clusters = defaultdict(list)
    for entry in family_data:
        fit = entry["abcd_fit"]
        if fit and fit["exact_fit"]:
            key = (round(fit["A"] * 4) / 4, round(fit["B"] * 4) / 4,
                   round(fit["C"] * 4) / 4, round(fit["D"] * 4) / 4)
            abcd_clusters[str(key)].append(entry["seq_id"])

    # ------------------------------------------------------------------
    # Phase space comparison
    # ------------------------------------------------------------------
    print("\n[5] Phase space comparison...")
    growth_types = defaultdict(list)
    for entry in family_data:
        ps = entry["phase_space"]
        if ps:
            growth_types[ps["growth_type"]].append(entry["seq_id"])

    for gt, members in sorted(growth_types.items(), key=lambda x: -len(x[1])):
        print(f"  {gt:15s}: {len(members)} sequences")

    # Lyapunov statistics
    lyapunovs = [e["phase_space"]["lyapunov_estimate"] for e in family_data if e["phase_space"]]
    if lyapunovs:
        print(f"  Lyapunov: mean={np.mean(lyapunovs):.4f}, "
              f"std={np.std(lyapunovs):.4f}, "
              f"min={np.min(lyapunovs):.4f}, max={np.max(lyapunovs):.4f}")

    # ------------------------------------------------------------------
    # Cross-reference analysis
    # ------------------------------------------------------------------
    print("\n[6] Cross-reference analysis...")
    crossrefs = load_crossrefs()
    print(f"  Loaded {sum(len(v) for v in crossrefs.values()) // 2} cross-reference edges")
    xref_results = cross_reference_analysis(family_ids, crossrefs)
    print(f"  Internal edges: {xref_results['n_internal_edges']}")
    print(f"  Connected components: {xref_results['n_components']}")
    print(f"  Component sizes: {xref_results['component_sizes']}")
    print(f"  Fully connected: {xref_results['is_connected']}")
    if xref_results["top_external_refs"]:
        print("  Top external references:")
        for ref in xref_results["top_external_refs"][:10]:
            ext_name = names.get(ref["seq"], "Unknown")
            print(f"    {ref['seq']} (x{ref['count']}): {ext_name[:60]}")

    # ------------------------------------------------------------------
    # Collatz-specific analysis
    # ------------------------------------------------------------------
    print("\n[7] Collatz-specific analysis (A006370)...")
    collatz_terms = oeis_seqs.get("A006370", None)
    collatz_result = collatz_analysis(collatz_terms, oeis_seqs)
    if collatz_result.get("a006370_present"):
        print(f"  Terms: {len(collatz_terms)}")
        rd = collatz_result["recurrence_detail"]
        print(f"  Recurrence holds: {rd['holds']} (errors={rd['errors']}/{rd['checks']})")
        print(f"  Explanation: {collatz_result['explanation']}")
    else:
        print("  A006370 not found in OEIS data!")

    # ------------------------------------------------------------------
    # Trivial vs interesting classification
    # ------------------------------------------------------------------
    print("\n[8] Classification summary...")
    class_counts = defaultdict(list)
    for entry in family_data:
        class_counts[entry["classification"]].append(entry["seq_id"])

    for cls, members in sorted(class_counts.items(), key=lambda x: -len(x[1])):
        print(f"  {cls:35s}: {len(members)} sequences")
        for m in members:
            n = names.get(m, "?")
            print(f"    {m}: {n[:70]}")

    # ------------------------------------------------------------------
    # Honest assessment
    # ------------------------------------------------------------------
    print("\n[9] HONEST ASSESSMENT")
    n_exact = sum(1 for e in family_data if e["recurrence_verification"]["holds"])
    n_exact_fit = sum(1 for e in family_data if e["abcd_fit"] and e["abcd_fit"]["exact_fit"])
    n_trivial = sum(1 for e in family_data if e["classification"].startswith("trivial"))
    n_collatz = sum(1 for e in family_data if e["classification"] == "collatz_adjacent")

    print(f"  Sequences satisfying recurrence exactly: {n_exact}/{len(family_data)}")
    print(f"  Sequences with exact ABCD fit: {n_exact_fit}/{len(family_data)}")
    print(f"  Trivial sequences: {n_trivial}/{len(family_data)}")
    print(f"  Collatz-adjacent: {n_collatz}/{len(family_data)}")

    assessment = (
        f"The (x-1)^2(x+1)^2 family contains {len(family_data)} sequences that all "
        f"satisfy a(n) = 2*a(n-2) - a(n-4). This recurrence is equivalent to requiring "
        f"that both the even-indexed and odd-indexed subsequences be arithmetic progressions "
        f"(i.e., linear in n). This is a VERY common structural pattern. "
        f"Any function that is linear-on-evens and linear-on-odds satisfies it. "
        f"The Collatz map a(n)=n/2 if even, 3n+1 if odd is simply one example. "
        f"{n_trivial} of {len(family_data)} members are trivially classifiable "
        f"(pure linear, alternating, or constant-alternating forms). "
        f"This is NOT a deep 'Collatz family' — it is the family of all sequences "
        f"that are piecewise-linear on even/odd indices. The connection to Collatz "
        f"is real but shallow: Collatz happens to be piecewise-linear on n "
        f"(not on iterates), which is all this recurrence captures."
    )
    print(f"\n  {assessment}")

    # ------------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------------
    print(f"\n[10] Saving results to {OUT_FILE}...")

    results = {
        "challenge": "C17",
        "title": "Collatz Algebraic Family Deep Dive",
        "characteristic_polynomial": "x^4 - 2x^2 + 1 = (x-1)^2(x+1)^2",
        "recurrence": "a(n) = 2*a(n-2) - a(n-4)",
        "general_solution": "a(n) = (A + B*n) + (-1)^n * (C + D*n)",
        "family_size": len(family_data),
        "sequences": family_data,
        "parameter_signature_clusters": {k: v for k, v in clusters.items()},
        "abcd_clusters": {k: v for k, v in abcd_clusters.items()},
        "phase_space_growth_types": {k: v for k, v in growth_types.items()},
        "lyapunov_stats": {
            "mean": float(np.mean(lyapunovs)) if lyapunovs else None,
            "std": float(np.std(lyapunovs)) if lyapunovs else None,
            "min": float(np.min(lyapunovs)) if lyapunovs else None,
            "max": float(np.max(lyapunovs)) if lyapunovs else None,
        },
        "cross_references": {
            "n_internal_edges": xref_results["n_internal_edges"],
            "internal_edges": xref_results["internal_edges"],
            "n_components": xref_results["n_components"],
            "component_sizes": xref_results["component_sizes"],
            "components": xref_results["components"],
            "is_connected": xref_results["is_connected"],
            "top_external_refs": xref_results["top_external_refs"],
        },
        "collatz_a006370": collatz_result,
        "classification_summary": {cls: members for cls, members in class_counts.items()},
        "assessment": assessment,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("  Done.")
    print(f"\n{'=' * 70}")
    print("COMPLETE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
