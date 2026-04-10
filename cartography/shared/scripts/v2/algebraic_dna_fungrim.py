"""
Algebraic DNA × Fungrim — Mod-p Fingerprints of Algebraic Family Clusters
==========================================================================
Challenge C11: For each algebraic family cluster (shared characteristic
polynomial from Berlekamp-Massey), find connected Fungrim formulas and
compute mod-p fingerprints on the OEIS sequence terms.

Hypothesis: sequences sharing a characteristic polynomial AND connected
to Fungrim formulas will share mod-p fingerprints at rates exceeding
random baseline — revealing the "generating equation" behind each family.

Pipeline:
1. Load polynomial clusters from C08 results (recurrence_euler_factor_results.json)
2. Load Fungrim index + extract OEIS↔Fungrim links from source
3. Load OEIS sequence terms from stripped_new.txt
4. For each cluster: find Fungrim-connected sequences, compute mod-p fingerprints
5. Compare family-connected vs random fingerprint sharing rates
6. Special attention to Fibonacci (x^2-x-1), Collatz-related, Euler factor matches

Usage:
    python algebraic_dna_fungrim.py
"""

import gzip
import json
import math
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
C08_RESULTS = V2_DIR / "recurrence_euler_factor_results.json"
S33_FILE = ROOT / "cartography" / "convergence" / "data" / "recursion_operator_signatures.jsonl"
FUNGRIM_INDEX = ROOT / "cartography" / "fungrim" / "data" / "fungrim_index.json"
FUNGRIM_FORMULAS_DIR = ROOT / "cartography" / "fungrim" / "data" / "pygrim" / "formulas"
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OEIS_STRIPPED_GZ = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_FB = ROOT / "cartography" / "oeis" / "data" / "stripped.gz"
OEIS_FORMULAS = ROOT / "cartography" / "oeis" / "data" / "oeis_formulas.jsonl"
OEIS_NAMES = ROOT / "cartography" / "oeis" / "data" / "oeis_names.json"
OUT_FILE = V2_DIR / "algebraic_dna_fungrim_results.json"

PRIMES = [2, 3, 5, 7, 11]
FINGERPRINT_LEN = 20  # evaluate first 20 terms

# ---------------------------------------------------------------------------
# Berlekamp-Massey (from S33 extractor)
# ---------------------------------------------------------------------------
def berlekamp_massey(sequence):
    """Minimal LFSR via Berlekamp-Massey. Returns (coeffs, degree)."""
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


def verify_recurrence(sequence, coeffs, degree):
    """Check if recurrence reproduces the sequence."""
    if degree == 0 or not coeffs:
        return False
    n = len(sequence)
    if degree >= n:
        return False
    check_start = degree
    check_end = min(n, degree + max(20, n // 2))
    errors = 0
    for i in range(check_start, check_end):
        predicted = 0.0
        for j in range(degree):
            if j < len(coeffs):
                predicted -= coeffs[j] * sequence[i - j - 1]
        actual = float(sequence[i])
        tol = max(1.0, abs(actual) * 1e-6)
        if abs(predicted - actual) > tol:
            errors += 1
    max_errors = max(1, (check_end - check_start) // 10)
    return errors <= max_errors


def extract_char_poly(terms):
    """Run BM on integer terms and return (coeffs_tuple, degree) or None."""
    if len(terms) < 10:
        return None
    coeffs, deg = berlekamp_massey(terms)
    if deg < 2 or deg > 20:
        return None
    if not verify_recurrence(terms, coeffs, deg):
        return None
    # Round to integers
    int_coeffs = []
    for c in coeffs:
        r = round(c)
        if abs(c - r) > 0.01:
            return None
        int_coeffs.append(r)
    return tuple(int_coeffs), deg


# ---------------------------------------------------------------------------
# Load OEIS sequence terms
# ---------------------------------------------------------------------------
def load_oeis_terms(min_length=5, max_seqs=None):
    """Load OEIS sequences from stripped files. Returns {seq_id: [terms]}."""
    seqs = {}

    # Try plain text first, then gzipped
    if OEIS_STRIPPED.exists():
        print(f"  Loading OEIS terms from {OEIS_STRIPPED.name}...")
        with open(str(OEIS_STRIPPED), "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(" ", 1)
                if len(parts) < 2:
                    continue
                seq_id = parts[0]
                terms_str = parts[1].strip().strip(",")
                if not terms_str:
                    continue
                try:
                    terms = [int(x) for x in terms_str.split(",") if x.strip()]
                except ValueError:
                    continue
                if len(terms) >= min_length:
                    seqs[seq_id] = terms
                if max_seqs and len(seqs) >= max_seqs:
                    break
    else:
        src = OEIS_STRIPPED_GZ if OEIS_STRIPPED_GZ.exists() else OEIS_STRIPPED_FB
        if src.exists():
            print(f"  Loading OEIS terms from {src.name}...")
            with gzip.open(str(src), "rt", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split(" ", 1)
                    if len(parts) < 2:
                        # Try comma-separated: A000001 ,0,1,1,...
                        m = re.match(r"(A\d+)\s*,(.+)", line)
                        if m:
                            seq_id = m.group(1)
                            terms_str = m.group(2).strip().strip(",")
                        else:
                            continue
                    else:
                        seq_id = parts[0]
                        terms_str = parts[1].strip().strip(",")
                    if not terms_str:
                        continue
                    try:
                        terms = [int(x) for x in terms_str.split(",") if x.strip()]
                    except ValueError:
                        continue
                    if len(terms) >= min_length:
                        seqs[seq_id] = terms
                    if max_seqs and len(seqs) >= max_seqs:
                        break
        else:
            print("  WARNING: No OEIS stripped file found.")
    print(f"  Loaded {len(seqs)} sequences")
    return seqs


# ---------------------------------------------------------------------------
# Load polynomial clusters from C08
# ---------------------------------------------------------------------------
def load_clusters():
    """Load algebraic family clusters from C08 results."""
    if not C08_RESULTS.exists():
        print(f"  ERROR: C08 results not found at {C08_RESULTS}")
        return []
    data = json.load(open(str(C08_RESULTS)))
    clusters = data.get("polynomial_clusters", {})
    top = clusters.get("top_clusters", [])
    total = clusters.get("total_clusters", 0)
    print(f"  Loaded {len(top)} top clusters (from {total} total)")
    return top


# ---------------------------------------------------------------------------
# Extract OEIS↔Fungrim links from Fungrim source
# ---------------------------------------------------------------------------
def extract_fungrim_oeis_links():
    """
    Parse Fungrim Python formula files to find SloaneA references.
    Returns:
        oeis_to_modules: {seq_id: [module_names]}
        oeis_to_symbols: {seq_id: [symbol_names]}
        module_to_oeis: {module_name: [seq_ids]}
        formula_oeis_refs: [{module, seq_ids, symbols}]
    """
    oeis_to_modules = defaultdict(set)
    oeis_to_symbols = defaultdict(set)
    module_to_oeis = defaultdict(set)
    formula_refs = []

    # Also build symbol-to-module and module-to-symbol maps from fungrim_index
    if FUNGRIM_INDEX.exists():
        idx = json.load(open(str(FUNGRIM_INDEX)))
        formulas_list = idx.get("formulas", [])
        module_stats = idx.get("module_stats", {})
    else:
        formulas_list = []
        module_stats = {}

    # Parse source files for SloaneA references
    sloane_re = re.compile(r'SloaneA\(\s*"?(A?\d+)"?\s*')
    oeis_url_re = re.compile(r'oeis\.org/(A\d+)')

    if FUNGRIM_FORMULAS_DIR.exists():
        for py_file in sorted(FUNGRIM_FORMULAS_DIR.glob("*.py")):
            module_name = py_file.stem
            text = py_file.read_text(encoding="utf-8", errors="ignore")

            # Find SloaneA references
            for m in sloane_re.finditer(text):
                raw = m.group(1)
                if raw.startswith("A"):
                    seq_id = raw
                else:
                    seq_id = f"A{int(raw):06d}"
                oeis_to_modules[seq_id].add(module_name)
                module_to_oeis[module_name].add(seq_id)

            # Find oeis.org URL references
            for m in oeis_url_re.finditer(text):
                seq_id = m.group(1)
                oeis_to_modules[seq_id].add(module_name)
                module_to_oeis[module_name].add(seq_id)

    # Convert sets to sorted lists
    oeis_to_modules = {k: sorted(v) for k, v in oeis_to_modules.items()}
    module_to_oeis = {k: sorted(v) for k, v in module_to_oeis.items()}

    # Build symbol connection: which Fungrim symbols correspond to OEIS sequences
    # Known mappings from integer_sequences.py
    known_symbol_map = {
        "A000040": ["PrimeNumber"],
        "A000041": ["PartitionsP"],
        "A000045": ["Fibonacci"],
        "A000110": ["BellNumber"],
        "A000142": ["Factorial"],
        "A000720": ["PrimePi"],
        "A000793": ["LandauG"],
    }

    # Extend with module-level symbol associations
    for f_rec in formulas_list:
        mod = f_rec.get("module", "")
        symbols = f_rec.get("symbols", [])
        if mod in module_to_oeis:
            for seq_id in module_to_oeis[mod]:
                for sym in symbols:
                    oeis_to_symbols[seq_id].add(sym)

    for seq_id, syms in known_symbol_map.items():
        for s in syms:
            oeis_to_symbols[seq_id].add(s)

    oeis_to_symbols = {k: sorted(v) for k, v in oeis_to_symbols.items()}

    print(f"  Fungrim OEIS links (direct): {len(oeis_to_modules)} sequences referenced")
    print(f"  Fungrim modules with OEIS refs: {len(module_to_oeis)}")
    print(f"  Sequences with symbol connections: {len(oeis_to_symbols)}")

    return oeis_to_modules, oeis_to_symbols, module_to_oeis, formulas_list


# ---------------------------------------------------------------------------
# Broader OEIS→Fungrim bridges via OEIS formula text keyword matching
# ---------------------------------------------------------------------------
# Fungrim module names map to keywords in OEIS formula text
FUNGRIM_KEYWORD_MAP = {
    "fibonacci": ["fibonacci", "lucas", "golden ratio", "phi", "F(n)", "L(n)"],
    "golden_ratio": ["golden ratio", "phi", "(1+sqrt(5))/2"],
    "bernoulli_numbers": ["bernoulli", "B(n)", "B_n", "Bernoulli number"],
    "bell_numbers": ["bell number", "Bell(n)", "B_n"],
    "partitions": ["partition", "p(n)", "partitions of n"],
    "dedekind_eta": ["dedekind eta", "eta function", "eta("],
    "eisenstein": ["eisenstein", "E_2", "E_4", "E_6", "E_8"],
    "modular_j": ["j-invariant", "j-function", "klein j", "j(tau)"],
    "riemann_zeta": ["zeta(", "riemann zeta", "zeta function"],
    "jacobi_theta": ["jacobi theta", "theta function", "theta("],
    "chebyshev": ["chebyshev", "Chebyshev"],
    "prime_numbers": ["prime", "p(n)", "pi(n)", "primepi"],
    "totient": ["euler totient", "phi(n)", "euler phi"],
    "stirling_numbers": ["stirling number", "stirling("],
    "gamma": ["gamma function", "Gamma("],
    "exp": ["exponential", "e^", "exp("],
    "sine": ["sin(", "cos(", "trigonometric"],
    "atan": ["arctan", "atan("],
    "log": ["logarithm", "log(", "ln("],
    "legendre_polynomial": ["legendre polynomial", "P_n("],
    "factorial": ["factorial", "n!", "binomial"],
    "weierstrass_elliptic": ["weierstrass", "elliptic", "wp("],
    "legendre_elliptic": ["elliptic integral", "elliptic function"],
    "dirichlet": ["dirichlet", "L-function", "L-series"],
    "modular_transformations": ["modular form", "modular function", "cusp form"],
}

def build_keyword_bridges(oeis_to_modules):
    """
    Scan OEIS formula text for Fungrim-related keywords.
    Returns expanded oeis_to_modules dict.
    """
    expanded = defaultdict(set)
    for k, v in oeis_to_modules.items():
        for mod in v:
            expanded[k].add(mod)

    if not OEIS_FORMULAS.exists():
        print("  WARNING: OEIS formulas file not found, skipping keyword bridging")
        return {k: sorted(v) for k, v in expanded.items()}

    print("  Scanning OEIS formula text for Fungrim keyword bridges...")
    n_new = 0
    seen_seqs = set()
    with open(str(OEIS_FORMULAS), "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            seq_id = rec.get("seq_id", "")
            formula = rec.get("formula", "").lower()
            if not formula or not seq_id:
                continue
            for module, keywords in FUNGRIM_KEYWORD_MAP.items():
                for kw in keywords:
                    if kw.lower() in formula:
                        if (seq_id, module) not in seen_seqs:
                            expanded[seq_id].add(module)
                            seen_seqs.add((seq_id, module))
                            n_new += 1
                        break

    print(f"  Keyword bridging added {n_new} new (seq, module) links")
    print(f"  Total sequences with Fungrim bridges: {len(expanded)}")
    return {k: sorted(v) for k, v in expanded.items()}


# ---------------------------------------------------------------------------
# Build broader OEIS→Fungrim connections via shared mathematical concepts
# ---------------------------------------------------------------------------
def build_symbol_bridge(clusters, oeis_to_modules, oeis_to_symbols, module_to_oeis, formulas_list):
    """
    For sequences not directly referenced in Fungrim, connect via module:
    - If a sequence is in a Fibonacci-family cluster, connect it to the 'fibonacci' module
    - If a sequence shares characteristic polynomial with one that IS in Fungrim, inherit the link
    """
    # Map from char_poly tuple to module connections
    poly_to_modules = defaultdict(set)

    for cluster in clusters:
        coeffs = tuple(cluster["char_poly_coeffs"])
        seqs = cluster["sequences"]
        # Check if any sequence in this cluster is directly in Fungrim
        for seq_id in seqs:
            if seq_id in oeis_to_modules:
                for mod in oeis_to_modules[seq_id]:
                    poly_to_modules[coeffs].add(mod)

    # Known polynomial → module mappings
    KNOWN_POLY_MODULES = {
        (-1, -1): ["fibonacci", "golden_ratio"],  # x^2 - x - 1 = Fibonacci
        (-1, 0): ["integer_sequences"],  # period-2 sequences
    }
    for coeffs, mods in KNOWN_POLY_MODULES.items():
        for m in mods:
            poly_to_modules[coeffs].add(m)

    poly_to_modules = {k: sorted(v) for k, v in poly_to_modules.items()}
    return poly_to_modules


# ---------------------------------------------------------------------------
# Mod-p fingerprint
# ---------------------------------------------------------------------------
def mod_p_fingerprint(terms, p, length=FINGERPRINT_LEN):
    """Compute mod-p fingerprint from sequence terms."""
    usable = terms[:length]
    if len(usable) < 5:
        return None
    return tuple(t % p for t in usable)


def fingerprint_vector(terms, primes=PRIMES, length=FINGERPRINT_LEN):
    """Compute full fingerprint vector: concatenation of mod-p fingerprints."""
    fps = {}
    for p in primes:
        fp = mod_p_fingerprint(terms, p, length)
        if fp is None:
            return None
        fps[p] = fp
    return fps


# ---------------------------------------------------------------------------
# Fingerprint sharing analysis
# ---------------------------------------------------------------------------
def compute_sharing_rate(fp_pairs):
    """
    Given list of (fp_dict_1, fp_dict_2) pairs, compute per-prime sharing rates.
    Sharing = fraction of positions where mod-p residues agree.
    """
    if not fp_pairs:
        return {}

    per_prime = {p: [] for p in PRIMES}
    for fp1, fp2 in fp_pairs:
        for p in PRIMES:
            if p in fp1 and p in fp2:
                v1, v2 = fp1[p], fp2[p]
                min_len = min(len(v1), len(v2))
                if min_len == 0:
                    continue
                matches = sum(1 for i in range(min_len) if v1[i] == v2[i])
                per_prime[p].append(matches / min_len)

    result = {}
    for p in PRIMES:
        vals = per_prime[p]
        if vals:
            result[p] = {
                "mean_sharing": sum(vals) / len(vals),
                "n_pairs": len(vals),
                "exact_matches": sum(1 for v in vals if v > 0.99),
            }
    return result


def exact_fingerprint_match_rate(fps_list, primes=PRIMES):
    """For a list of fingerprint dicts, fraction of pairs with exact match per prime."""
    n = len(fps_list)
    if n < 2:
        return {}
    result = {}
    for p in primes:
        matches = 0
        total = 0
        for i in range(n):
            for j in range(i + 1, n):
                if p in fps_list[i] and p in fps_list[j]:
                    total += 1
                    if fps_list[i][p] == fps_list[j][p]:
                        matches += 1
        result[p] = {"exact_match_rate": matches / total if total > 0 else 0, "n_pairs": total}
    return result


# ---------------------------------------------------------------------------
# Euler factor detection
# ---------------------------------------------------------------------------
def is_ec_euler_factor(coeffs):
    """Check if degree-2 polynomial x^2 + c1*x + c0 has form x^2 - a_p*x + p."""
    if len(coeffs) != 2:
        return None
    c0, c1 = coeffs[0], coeffs[1]
    # Constant term should be prime
    p = abs(c0)
    if p < 2:
        return None
    # Check if p is prime
    if p > 1000000:
        return None
    if not is_prime_small(p):
        return None
    a_p = -c1
    if abs(a_p) > 2 * math.sqrt(p):
        return None
    return {"prime": p, "a_p": a_p}


def is_genus2_euler_factor(coeffs):
    """Check if degree-4 polynomial matches genus-2 Euler factor symmetry."""
    if len(coeffs) != 4:
        return None
    c0, c1, c2, c3 = coeffs
    # x^4 + c3*x^3 + c2*x^2 + c1*x + c0
    # Genus-2: x^4 - a*x^3 + b*x^2 - a*p*x + p^2
    # So c0 = p^2, c3 = -a, c1 = -a*p = c3*p
    p_sq = abs(c0)
    p = round(math.sqrt(p_sq))
    if p < 2 or p * p != p_sq:
        return None
    if not is_prime_small(p):
        return None
    a = -c3
    if abs(c1 - (-a * p)) > 0.5:
        return None
    return {"prime": p, "a": a, "b": c2}


def is_prime_small(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("C11: Algebraic DNA × Fungrim — Mod-p Fingerprint Analysis")
    print("=" * 70)

    # 1. Load polynomial clusters
    print("\n[1] Loading algebraic family clusters from C08...")
    clusters = load_clusters()
    if not clusters:
        print("  FATAL: No clusters found. Exiting.")
        return

    # 2. Load Fungrim data
    print("\n[2] Loading Fungrim data and extracting OEIS links...")
    oeis_to_modules, oeis_to_symbols, module_to_oeis, formulas_list = extract_fungrim_oeis_links()

    # 2b. Expand bridges via OEIS formula keyword matching
    print("\n[2b] Expanding bridges via OEIS formula keywords...")
    oeis_to_modules = build_keyword_bridges(oeis_to_modules)

    # 3. Build broader bridges
    print("\n[3] Building symbol bridges...")
    poly_to_modules = build_symbol_bridge(clusters, oeis_to_modules, oeis_to_symbols, module_to_oeis, formulas_list)
    print(f"  Polynomials with Fungrim module connections: {len(poly_to_modules)}")

    # 4. Load OEIS terms
    print("\n[4] Loading OEIS sequence terms...")
    oeis_terms = load_oeis_terms(min_length=5)

    # 4b. Run BM on Fungrim-referenced sequences not already in clusters
    print("\n[4b] Running Berlekamp-Massey on Fungrim-linked sequences...")
    cluster_seq_ids = set()
    for cl in clusters:
        for s in cl["sequences"]:
            cluster_seq_ids.add(s)
    fungrim_seq_ids = set(oeis_to_modules.keys())
    new_bm_seqs = fungrim_seq_ids - cluster_seq_ids
    new_bm_seqs = [s for s in new_bm_seqs if s in oeis_terms and len(oeis_terms[s]) >= 15]
    print(f"  Running BM on {len(new_bm_seqs)} Fungrim-linked sequences not in C08 clusters...")

    # Build extended clusters: poly_tuple -> [seq_ids]
    extended_poly_map = defaultdict(list)
    for cl in clusters:
        key = tuple(cl["char_poly_coeffs"])
        extended_poly_map[key].extend(cl["sequences"])

    n_new_clustered = 0
    for seq_id in new_bm_seqs:
        result = extract_char_poly(oeis_terms[seq_id])
        if result is not None:
            coeffs_tuple, deg = result
            extended_poly_map[coeffs_tuple].append(seq_id)
            n_new_clustered += 1

    # Rebuild clusters list with extended data
    extended_clusters = []
    for coeffs_tuple, seq_list in sorted(extended_poly_map.items(), key=lambda x: -len(x[1])):
        extended_clusters.append({
            "char_poly_coeffs": list(coeffs_tuple),
            "degree": len(coeffs_tuple),
            "n_sequences": len(seq_list),
            "sequences": seq_list[:50],  # cap at 50 for memory
            "is_ec_euler": False,
            "is_genus2_euler": False,
        })
    print(f"  BM clustered {n_new_clustered} new sequences")
    print(f"  Extended cluster count: {len(extended_clusters)} (was {len(clusters)})")
    clusters = extended_clusters

    # 5. Compute fingerprints per cluster
    print("\n[5] Computing mod-p fingerprints per algebraic family cluster...")

    cluster_results = []
    family_fp_pairs = []  # (fp1, fp2) for sequences in same family with Fungrim connection
    all_fps = []  # all fingerprints for null baseline

    # Collect which sequences are Fungrim-connected (directly or via keyword bridge)
    fungrim_connected = set(oeis_to_modules.keys())
    print(f"  Total Fungrim-connected sequences: {len(fungrim_connected)}")

    n_clusters_with_fungrim = 0
    n_clusters_with_fingerprints = 0
    fibonacci_result = None
    collatz_result = None
    euler_factor_clusters = []

    for ci, cluster in enumerate(clusters):
        coeffs = tuple(cluster["char_poly_coeffs"])
        degree = cluster["degree"]
        seqs = cluster["sequences"]  # note: this is top-20 only from C08
        n_seq = cluster["n_sequences"]

        # Check for Fungrim connections
        direct_refs = [s for s in seqs if s in fungrim_connected]
        module_connection = poly_to_modules.get(coeffs, [])

        # Find all Fungrim formulas touching this cluster's modules
        connected_formula_count = 0
        connected_symbols = set()
        if module_connection:
            for mod in module_connection:
                for f_rec in formulas_list:
                    if f_rec.get("module") == mod:
                        connected_formula_count += 1
                        for s in f_rec.get("symbols", []):
                            connected_symbols.add(s)

        has_fungrim = len(direct_refs) > 0 or len(module_connection) > 0
        if has_fungrim:
            n_clusters_with_fungrim += 1

        # Compute fingerprints for all sequences in this cluster
        fps_in_cluster = []
        for seq_id in seqs:
            if seq_id in oeis_terms:
                fp = fingerprint_vector(oeis_terms[seq_id])
                if fp is not None:
                    fps_in_cluster.append((seq_id, fp))
                    all_fps.append(fp)

        if len(fps_in_cluster) >= 2:
            n_clusters_with_fingerprints += 1

        # Compute within-cluster fingerprint sharing
        within_sharing = {}
        if len(fps_in_cluster) >= 2:
            fps_only = [fp for _, fp in fps_in_cluster]
            within_sharing = exact_fingerprint_match_rate(fps_only)

            # Collect pairs for family-connected analysis
            if has_fungrim:
                for i in range(len(fps_only)):
                    for j in range(i + 1, len(fps_only)):
                        family_fp_pairs.append((fps_only[i], fps_only[j]))

        # Check Euler factor
        euler_info = None
        if degree == 2:
            euler_info = is_ec_euler_factor(list(coeffs))
        elif degree == 4:
            euler_info = is_genus2_euler_factor(list(coeffs))
        if euler_info:
            euler_factor_clusters.append({
                "char_poly_coeffs": list(coeffs),
                "degree": degree,
                "euler_info": euler_info,
                "n_sequences": n_seq,
                "fungrim_modules": module_connection,
                "sample_seqs": seqs[:5],
            })

        # Build result record
        char_poly_str = format_poly(coeffs)
        result = {
            "char_poly_coeffs": list(coeffs),
            "char_poly_str": char_poly_str,
            "degree": degree,
            "n_sequences": n_seq,
            "sample_sequences": seqs[:10],
            "fungrim_direct_refs": direct_refs,
            "fungrim_modules": module_connection,
            "connected_formula_count": connected_formula_count,
            "connected_symbols": sorted(connected_symbols)[:20],
            "n_fingerprinted": len(fps_in_cluster),
            "within_cluster_sharing": within_sharing,
            "is_euler_factor": euler_info is not None,
            "euler_factor_info": euler_info,
        }
        cluster_results.append(result)

        # Tag special families
        if coeffs == (-1, -1):
            fibonacci_result = result
        # Collatz: look for x^4 - 2x^2 = coeffs [0, -2, 0, 0] or similar
        if coeffs in [(-2, 0, -2, 0), (0, -2, 0, 0), (0, -2, 0, 1)]:
            collatz_result = result

    # 6. Null baseline: random pairs
    print("\n[6] Computing null baseline (random pairings)...")
    n_null_trials = min(10000, len(all_fps) * (len(all_fps) - 1) // 2)
    random_fp_pairs = []
    if len(all_fps) >= 2:
        for _ in range(n_null_trials):
            i, j = random.sample(range(len(all_fps)), 2)
            random_fp_pairs.append((all_fps[i], all_fps[j]))

    family_sharing = compute_sharing_rate(family_fp_pairs)
    random_sharing = compute_sharing_rate(random_fp_pairs)

    # Also compute exact match rates
    family_exact = {}
    random_exact = {}
    for p in PRIMES:
        # Family pairs
        fam_exact_ct = 0
        fam_total = 0
        for fp1, fp2 in family_fp_pairs:
            if p in fp1 and p in fp2:
                fam_total += 1
                if fp1[p] == fp2[p]:
                    fam_exact_ct += 1
        family_exact[str(p)] = {
            "exact_matches": fam_exact_ct,
            "total_pairs": fam_total,
            "rate": fam_exact_ct / fam_total if fam_total > 0 else 0,
        }

        # Random pairs
        rand_exact_ct = 0
        rand_total = 0
        for fp1, fp2 in random_fp_pairs:
            if p in fp1 and p in fp2:
                rand_total += 1
                if fp1[p] == fp2[p]:
                    rand_exact_ct += 1
        random_exact[str(p)] = {
            "exact_matches": rand_exact_ct,
            "total_pairs": rand_total,
            "rate": rand_exact_ct / rand_total if rand_total > 0 else 0,
        }

    # 7. Find most interesting connections
    print("\n[7] Identifying most interesting family-formula connections...")
    interesting = []
    for cr in cluster_results:
        score = 0
        if cr["fungrim_direct_refs"]:
            score += 10 * len(cr["fungrim_direct_refs"])
        if cr["fungrim_modules"]:
            score += 5 * len(cr["fungrim_modules"])
        if cr["is_euler_factor"]:
            score += 20
        if cr["connected_formula_count"] > 0:
            score += cr["connected_formula_count"]
        # Bonus for within-cluster sharing
        for p_str, info in cr["within_cluster_sharing"].items():
            if isinstance(info, dict) and info.get("exact_match_rate", 0) > 0.1:
                score += 10
        cr["interest_score"] = score
        if score > 0:
            interesting.append(cr)

    interesting.sort(key=lambda x: -x["interest_score"])

    # 8. Special: Fibonacci deep dive
    print("\n[8] Special family analysis...")
    fib_deep = None
    if fibonacci_result:
        fib_seqs = fibonacci_result["sample_sequences"]
        fib_fps = []
        for seq_id in fib_seqs:
            if seq_id in oeis_terms:
                fp = fingerprint_vector(oeis_terms[seq_id])
                if fp is not None:
                    fib_fps.append({"seq_id": seq_id, "fingerprint": {str(p): list(fp[p]) for p in fp}})
        fib_sharing = exact_fingerprint_match_rate([fp_dict for _, fp_dict in [(s["seq_id"], fingerprint_vector(oeis_terms[s["seq_id"]])) for s in fib_fps if s["seq_id"] in oeis_terms] if fp_dict])

        fib_deep = {
            "char_poly": "x^2 - x - 1",
            "n_sequences": fibonacci_result["n_sequences"],
            "fungrim_modules": fibonacci_result["fungrim_modules"],
            "fungrim_direct_refs": fibonacci_result["fungrim_direct_refs"],
            "connected_formulas": fibonacci_result["connected_formula_count"],
            "sample_fingerprints": fib_fps[:5],
            "within_sharing": fib_sharing,
        }
        print(f"  Fibonacci: {fibonacci_result['n_sequences']} seqs, "
              f"{fibonacci_result['connected_formula_count']} formulas, "
              f"modules: {fibonacci_result['fungrim_modules']}")

    collatz_deep = None
    if collatz_result:
        collatz_deep = {
            "char_poly_coeffs": collatz_result["char_poly_coeffs"],
            "n_sequences": collatz_result["n_sequences"],
            "fungrim_modules": collatz_result["fungrim_modules"],
            "fungrim_direct_refs": collatz_result["fungrim_direct_refs"],
            "connected_formulas": collatz_result["connected_formula_count"],
        }
        print(f"  Collatz candidate: {collatz_result['n_sequences']} seqs, "
              f"modules: {collatz_result['fungrim_modules']}")
    else:
        print("  Collatz family: no exact match in top clusters")
        # Search for Collatz-adjacent
        for cr in cluster_results:
            if cr["degree"] == 4 and abs(cr["char_poly_coeffs"][1]) == 2:
                collatz_deep = {
                    "note": "Closest match (not exact Collatz)",
                    "char_poly_coeffs": cr["char_poly_coeffs"],
                    "n_sequences": cr["n_sequences"],
                    "sample_sequences": cr["sample_sequences"][:5],
                }
                break

    # 8b. Separate analysis: direct Fungrim refs vs keyword-only
    print("\n[8b] Direct vs keyword-only Fungrim connection analysis...")
    direct_fungrim_set = set()
    for f_data in [oeis_to_modules]:
        # The original direct refs were from extract_fungrim_oeis_links before keyword expansion
        pass
    # Re-extract direct refs for comparison
    direct_oeis_refs = set()
    sloane_re2 = re.compile(r'SloaneA\(\s*"?(A?\d+)"?\s*')
    oeis_url_re2 = re.compile(r'oeis\.org/(A\d+)')
    if FUNGRIM_FORMULAS_DIR.exists():
        for py_file in sorted(FUNGRIM_FORMULAS_DIR.glob("*.py")):
            text = py_file.read_text(encoding="utf-8", errors="ignore")
            for m in sloane_re2.finditer(text):
                raw = m.group(1)
                if raw.startswith("A"):
                    direct_oeis_refs.add(raw)
                else:
                    direct_oeis_refs.add(f"A{int(raw):06d}")
            for m in oeis_url_re2.finditer(text):
                direct_oeis_refs.add(m.group(1))

    # Pairs where at least one member is directly in Fungrim
    direct_family_pairs = []
    keyword_only_pairs = []
    for ci, cluster in enumerate(clusters):
        coeffs = tuple(cluster["char_poly_coeffs"])
        seqs = cluster["sequences"]
        fps_in_cl = []
        has_direct = False
        for seq_id in seqs:
            if seq_id in oeis_terms:
                fp = fingerprint_vector(oeis_terms[seq_id])
                if fp is not None:
                    fps_in_cl.append(fp)
                    if seq_id in direct_oeis_refs:
                        has_direct = True
        if len(fps_in_cl) >= 2:
            for i in range(min(len(fps_in_cl), 10)):
                for j in range(i + 1, min(len(fps_in_cl), 10)):
                    if has_direct:
                        direct_family_pairs.append((fps_in_cl[i], fps_in_cl[j]))
                    else:
                        keyword_only_pairs.append((fps_in_cl[i], fps_in_cl[j]))

    direct_sharing = compute_sharing_rate(direct_family_pairs)
    keyword_sharing = compute_sharing_rate(keyword_only_pairs)
    print(f"  Direct Fungrim pairs: {len(direct_family_pairs)}")
    print(f"  Keyword-only pairs: {len(keyword_only_pairs)}")
    for p in PRIMES:
        ds = direct_sharing.get(p, {}).get("mean_sharing", 0)
        ks = keyword_sharing.get(p, {}).get("mean_sharing", 0)
        rs = random_sharing.get(p, {}).get("mean_sharing", 0)
        print(f"    mod {p:2d}: direct={ds:.4f}  keyword={ks:.4f}  random={rs:.4f}")

    # 9. Compile report
    elapsed = time.time() - t0

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"  Total clusters analyzed: {len(clusters)}")
    print(f"  Clusters with Fungrim connections: {n_clusters_with_fungrim}")
    print(f"  Clusters with 2+ fingerprints: {n_clusters_with_fingerprints}")
    print(f"  Euler factor clusters: {len(euler_factor_clusters)}")
    print(f"  Family-connected pairs: {len(family_fp_pairs)}")
    print(f"  Random baseline pairs: {len(random_fp_pairs)}")

    print("\n  Fingerprint sharing (family-connected vs random):")
    for p in PRIMES:
        fam = family_sharing.get(p, {})
        rnd = random_sharing.get(p, {})
        fam_mean = fam.get("mean_sharing", 0)
        rnd_mean = rnd.get("mean_sharing", 0)
        excess = fam_mean - rnd_mean if rnd_mean > 0 else 0
        print(f"    mod {p:2d}: family={fam_mean:.4f}  random={rnd_mean:.4f}  excess={excess:+.4f}")

    print("\n  Exact fingerprint match rates:")
    for p in PRIMES:
        fe = family_exact.get(str(p), {})
        re_ = random_exact.get(str(p), {})
        print(f"    mod {p:2d}: family={fe.get('rate',0):.4f} ({fe.get('exact_matches',0)}/{fe.get('total_pairs',0)})  "
              f"random={re_.get('rate',0):.6f} ({re_.get('exact_matches',0)}/{re_.get('total_pairs',0)})")

    print(f"\n  Top 10 most interesting connections:")
    for cr in interesting[:10]:
        print(f"    {cr['char_poly_str']:30s}  "
              f"seqs={cr['n_sequences']:4d}  "
              f"modules={cr['fungrim_modules']}  "
              f"direct={cr['fungrim_direct_refs']}  "
              f"formulas={cr['connected_formula_count']}  "
              f"euler={cr['is_euler_factor']}")

    # Build output JSON
    output = {
        "challenge": "C11",
        "title": "Algebraic DNA x Fungrim -- Mod-p Fingerprints of Algebraic Family Clusters",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "total_clusters": len(clusters),
            "clusters_with_fungrim": n_clusters_with_fungrim,
            "clusters_with_fingerprints": n_clusters_with_fingerprints,
            "euler_factor_clusters": len(euler_factor_clusters),
            "family_pairs_analyzed": len(family_fp_pairs),
            "random_baseline_pairs": len(random_fp_pairs),
            "oeis_sequences_loaded": len(oeis_terms),
        },
        "fingerprint_sharing": {
            "family_connected": {str(p): family_sharing.get(p, {}) for p in PRIMES},
            "random_baseline": {str(p): random_sharing.get(p, {}) for p in PRIMES},
            "exact_match_family": family_exact,
            "exact_match_random": random_exact,
        },
        "fibonacci_family": fib_deep,
        "collatz_family": collatz_deep,
        "euler_factor_clusters": euler_factor_clusters[:20],
        "top_interesting_connections": [
            {k: v for k, v in cr.items() if k != "within_cluster_sharing"}
            for cr in interesting[:30]
        ],
        "all_cluster_results": [
            {
                "char_poly_str": cr["char_poly_str"],
                "degree": cr["degree"],
                "n_sequences": cr["n_sequences"],
                "fungrim_direct_refs": cr["fungrim_direct_refs"],
                "fungrim_modules": cr["fungrim_modules"],
                "connected_formula_count": cr["connected_formula_count"],
                "is_euler_factor": cr["is_euler_factor"],
                "interest_score": cr.get("interest_score", 0),
            }
            for cr in cluster_results
        ],
        "direct_vs_keyword": {
            "direct_pairs": len(direct_family_pairs),
            "keyword_only_pairs": len(keyword_only_pairs),
            "direct_sharing": {str(p): direct_sharing.get(p, {}) for p in PRIMES},
            "keyword_sharing": {str(p): keyword_sharing.get(p, {}) for p in PRIMES},
        },
        "elapsed_seconds": round(elapsed, 2),
    }

    with open(str(OUT_FILE), "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to {OUT_FILE}")
    print(f"  Elapsed: {elapsed:.1f}s")


def format_poly(coeffs):
    """Format characteristic polynomial coefficients as string."""
    deg = len(coeffs)
    terms = []
    # x^deg + c_{deg-1}*x^{deg-1} + ... + c_0
    terms.append(f"x^{deg}")
    for i, c in enumerate(reversed(coeffs)):
        power = deg - 1 - i
        if c == 0:
            continue
        if c > 0:
            sign = "+"
        else:
            sign = "-"
            c = -c
        if power == 0:
            terms.append(f"{sign}{c}")
        elif power == 1:
            if c == 1:
                terms.append(f"{sign}x")
            else:
                terms.append(f"{sign}{c}x")
        else:
            if c == 1:
                terms.append(f"{sign}x^{power}")
            else:
                terms.append(f"{sign}{c}x^{power}")
    return " ".join(terms)


if __name__ == "__main__":
    main()
