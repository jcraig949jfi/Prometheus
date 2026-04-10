"""
Gamma Wormhole — The Gamma Function as Algebraic Bridge
========================================================
Challenge C12.5 / Claude #5 Part 2

Tests whether the Gamma function carries genuine algebraic structure
across mathematical domains, or is merely notational glue.

Method:
1. Identify all Fungrim formulas using Gamma (and LogGamma, UpperGamma).
2. For each module pair (A, B) where both contain Gamma-using formulas:
   a. Extract shared symbols from Gamma-using formulas
   b. Build "operadic fingerprints" (symbol composition vectors)
   c. Compute distance between Gamma-connected cross-module formula pairs
3. Control: same module pairs, non-Gamma formula pairs
4. Compare Gamma-connected vs non-Gamma vs random distance
5. Build Gamma distance matrix: module × module

The "fingerprint" here is the symbol composition vector of each formula,
and distance is normalized Hamming distance on these vectors.

For OEIS-connected modules, we also compute mod-p fingerprints on the
actual sequence terms to test whether Gamma-connected sequences share
more arithmetic structure.

Usage:
    python gamma_wormhole.py
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
from itertools import combinations
from pathlib import Path

random.seed(42)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
FUNGRIM_INDEX = ROOT / "cartography" / "fungrim" / "data" / "fungrim_index.json"
FUNGRIM_FORMULAS_DIR = ROOT / "cartography" / "fungrim" / "data" / "pygrim" / "formulas"
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OEIS_STRIPPED_GZ = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_FB = ROOT / "cartography" / "oeis" / "data" / "stripped.gz"
OEIS_FORMULAS = ROOT / "cartography" / "oeis" / "data" / "oeis_formulas.jsonl"
OPERADIC_RESULTS = V2_DIR / "operadic_dynamics_results.json"
OUT_FILE = V2_DIR / "gamma_wormhole_results.json"

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
FINGERPRINT_LEN = 20

# Gamma function symbols (core Gamma, not Digamma/ConstGamma which are separate functions)
GAMMA_SYMBOLS = {"Gamma", "LogGamma", "UpperGamma"}
# Extended Gamma family (for sensitivity analysis)
GAMMA_EXTENDED = GAMMA_SYMBOLS | {"DigammaFunction", "DigammaFunctionZero", "ConstGamma", "StieltjesGamma"}


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_fungrim():
    """Load Fungrim index."""
    print("[1] Loading Fungrim index...")
    idx = json.load(open(str(FUNGRIM_INDEX)))
    formulas = idx["formulas"]
    bridge_symbols = idx.get("bridge_symbols", {})
    print(f"    {len(formulas)} formulas, {len(idx.get('module_stats', {}))} modules")
    return formulas, bridge_symbols


def load_operadic_results():
    """Load C12 operadic dynamics results for cross-domain bridge data."""
    if not OPERADIC_RESULTS.exists():
        print("    WARNING: operadic results not found")
        return None
    data = json.load(open(str(OPERADIC_RESULTS)))
    return data


def load_oeis_terms(max_seqs=50000):
    """Load OEIS sequences from stripped files."""
    print("[*] Loading OEIS terms...")
    seqs = {}
    src = None
    if OEIS_STRIPPED.exists():
        src = OEIS_STRIPPED
    elif OEIS_STRIPPED_GZ.exists():
        src = OEIS_STRIPPED_GZ
    elif OEIS_STRIPPED_FB.exists():
        src = OEIS_STRIPPED_FB

    if src is None:
        print("    WARNING: No OEIS stripped file found")
        return seqs

    opener = gzip.open if str(src).endswith(".gz") else open
    mode = "rt" if str(src).endswith(".gz") else "r"

    with opener(str(src), mode, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
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
            if len(terms) >= 5:
                seqs[seq_id] = terms
            if max_seqs and len(seqs) >= max_seqs:
                break

    print(f"    Loaded {len(seqs)} sequences")
    return seqs


def extract_fungrim_oeis_links():
    """Parse Fungrim source files for SloaneA references + keyword bridges."""
    print("[*] Extracting Fungrim <-> OEIS links...")
    module_to_oeis = defaultdict(set)
    sloane_re = re.compile(r'SloaneA\(\s*"?(A?\d+)"?\s*')
    oeis_url_re = re.compile(r'oeis\.org/(A\d+)')

    if FUNGRIM_FORMULAS_DIR.exists():
        for py_file in sorted(FUNGRIM_FORMULAS_DIR.glob("*.py")):
            module_name = py_file.stem
            text = py_file.read_text(encoding="utf-8", errors="ignore")
            for m in sloane_re.finditer(text):
                raw = m.group(1)
                seq_id = raw if raw.startswith("A") else f"A{int(raw):06d}"
                module_to_oeis[module_name].add(seq_id)
            for m in oeis_url_re.finditer(text):
                module_to_oeis[module_name].add(m.group(1))

    # Keyword bridges from OEIS formula text
    KEYWORD_MAP = {
        "gamma": ["gamma function", "Gamma("],
        "factorials": ["factorial", "n!", "binomial"],
        "bernoulli_numbers": ["bernoulli", "B(n)", "Bernoulli number"],
        "fibonacci": ["fibonacci", "lucas", "golden ratio"],
        "riemann_zeta": ["zeta(", "riemann zeta", "zeta function"],
        "jacobi_theta": ["jacobi theta", "theta function"],
        "eisenstein": ["eisenstein", "E_2", "E_4", "E_6"],
        "dedekind_eta": ["dedekind eta", "eta function"],
        "partitions": ["partition", "p(n)", "partitions of n"],
        "bessel": ["bessel", "J_n", "Y_n", "Bessel"],
        "legendre_elliptic": ["elliptic integral", "elliptic function"],
        "hurwitz_zeta": ["hurwitz zeta", "hurwitz"],
        "digamma_function": ["digamma", "psi("],
        "confluent_hypergeometric": ["hypergeometric", "Kummer"],
        "airy": ["airy function", "Ai(", "Bi("],
        "carlson_elliptic": ["carlson", "R_F", "R_J"],
    }

    if OEIS_FORMULAS.exists():
        n_keyword = 0
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
                for module, keywords in KEYWORD_MAP.items():
                    for kw in keywords:
                        if kw.lower() in formula:
                            module_to_oeis[module].add(seq_id)
                            n_keyword += 1
                            break
        print(f"    Keyword bridges added {n_keyword} links")

    module_to_oeis = {k: sorted(v) for k, v in module_to_oeis.items()}
    print(f"    Modules with OEIS refs: {len(module_to_oeis)}")
    for m in sorted(module_to_oeis):
        print(f"      {m}: {len(module_to_oeis[m])} sequences")
    return module_to_oeis


# ---------------------------------------------------------------------------
# Symbol-based fingerprinting
# ---------------------------------------------------------------------------
def build_symbol_universe(formulas):
    """Build sorted list of all symbols for vector encoding."""
    all_syms = set()
    for f in formulas:
        all_syms.update(f["symbols"])
    return sorted(all_syms)


def symbol_vector(formula, sym_universe):
    """Binary vector: 1 if symbol present, 0 otherwise."""
    sym_set = set(formula["symbols"])
    return tuple(1 if s in sym_set else 0 for s in sym_universe)


def hamming_distance(v1, v2):
    """Normalized Hamming distance between two binary vectors."""
    assert len(v1) == len(v2)
    n = len(v1)
    if n == 0:
        return 0.0
    return sum(1 for a, b in zip(v1, v2) if a != b) / n


def jaccard_distance(f1, f2):
    """Jaccard distance between two formula symbol sets."""
    s1 = set(f1["symbols"])
    s2 = set(f2["symbols"])
    if not s1 and not s2:
        return 0.0
    union = s1 | s2
    inter = s1 & s2
    return 1.0 - len(inter) / len(union)


# ---------------------------------------------------------------------------
# Mod-p fingerprinting (for OEIS sequences)
# ---------------------------------------------------------------------------
def mod_p_fingerprint(terms, p, length=FINGERPRINT_LEN):
    """Compute mod-p fingerprint from sequence terms."""
    usable = terms[:length]
    if len(usable) < 5:
        return None
    return tuple(t % p for t in usable)


def fingerprint_distance(terms1, terms2, p, length=FINGERPRINT_LEN):
    """Normalized Hamming distance between mod-p fingerprints."""
    fp1 = mod_p_fingerprint(terms1, p, length)
    fp2 = mod_p_fingerprint(terms2, p, length)
    if fp1 is None or fp2 is None:
        return None
    min_len = min(len(fp1), len(fp2))
    if min_len == 0:
        return None
    mismatches = sum(1 for i in range(min_len) if fp1[i] != fp2[i])
    return mismatches / min_len


def expected_random_distance(p):
    """Expected Hamming distance for random mod-p residues: (p-1)/p."""
    return (p - 1) / p


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------
def analyze_gamma_bridges(formulas, bridge_symbols):
    """
    Main analysis: compare distances between Gamma-connected vs non-Gamma
    formula pairs across module boundaries.
    """
    print("\n[2] Analyzing Gamma bridges...")

    # Partition formulas by module
    by_module = defaultdict(list)
    for f in formulas:
        by_module[f["module"]].append(f)

    # Identify Gamma-using formulas per module
    gamma_modules = set()
    gamma_by_module = defaultdict(list)
    nongamma_by_module = defaultdict(list)

    for f in formulas:
        if GAMMA_SYMBOLS & set(f["symbols"]):
            gamma_by_module[f["module"]].append(f)
            gamma_modules.add(f["module"])
        else:
            nongamma_by_module[f["module"]].append(f)

    print(f"    Gamma-using modules: {len(gamma_modules)}")
    print(f"    Gamma formulas: {sum(len(v) for v in gamma_by_module.values())}")

    # Build symbol universe for vector encoding
    sym_universe = build_symbol_universe(formulas)
    print(f"    Symbol universe: {len(sym_universe)} symbols")

    # For each module pair with Gamma formulas in both:
    # Compare Gamma-connected vs non-Gamma distances
    gamma_module_list = sorted(gamma_modules)
    pairs = list(combinations(gamma_module_list, 2))
    print(f"    Module pairs to analyze: {len(pairs)}")

    results = {}
    gamma_distances = []
    nongamma_distances = []
    random_distances = []
    pair_details = []

    for mod_a, mod_b in pairs:
        g_a = gamma_by_module[mod_a]
        g_b = gamma_by_module[mod_b]
        ng_a = nongamma_by_module[mod_a]
        ng_b = nongamma_by_module[mod_b]

        # Gamma-connected: pairs of Gamma-using formulas across modules
        g_dists = []
        for fa in g_a:
            for fb in g_b:
                d = jaccard_distance(fa, fb)
                g_dists.append(d)
                gamma_distances.append(d)

        # Non-Gamma control: pairs of non-Gamma formulas across same modules
        ng_dists = []
        # Sample to keep computation manageable
        ng_pairs_sample = min(len(ng_a) * len(ng_b), max(len(g_dists) * 3, 100))
        if ng_a and ng_b:
            for _ in range(ng_pairs_sample):
                fa = random.choice(ng_a)
                fb = random.choice(ng_b)
                d = jaccard_distance(fa, fb)
                ng_dists.append(d)
                nongamma_distances.append(d)

        # Random control: random formula pairs from any modules
        all_formulas_flat = formulas
        for _ in range(max(len(g_dists), 10)):
            fa = random.choice(all_formulas_flat)
            fb = random.choice(all_formulas_flat)
            d = jaccard_distance(fa, fb)
            random_distances.append(d)

        if g_dists:
            avg_g = sum(g_dists) / len(g_dists)
            avg_ng = sum(ng_dists) / len(ng_dists) if ng_dists else None
            pair_details.append({
                "module_a": mod_a,
                "module_b": mod_b,
                "gamma_mean_dist": round(avg_g, 6),
                "nongamma_mean_dist": round(avg_ng, 6) if avg_ng is not None else None,
                "gamma_n_pairs": len(g_dists),
                "nongamma_n_pairs": len(ng_dists),
                "gamma_closer": avg_g < avg_ng if avg_ng is not None else None,
                "delta": round(avg_ng - avg_g, 6) if avg_ng is not None else None,
            })

    # Summary statistics
    avg_gamma = sum(gamma_distances) / len(gamma_distances) if gamma_distances else None
    avg_nongamma = sum(nongamma_distances) / len(nongamma_distances) if nongamma_distances else None
    avg_random = sum(random_distances) / len(random_distances) if random_distances else None

    # Sort pair details by delta (Gamma advantage)
    pair_details.sort(key=lambda x: -(x["delta"] or 0))

    # Count how many pairs show Gamma closer
    n_gamma_closer = sum(1 for p in pair_details if p["gamma_closer"] is True)
    n_total_testable = sum(1 for p in pair_details if p["gamma_closer"] is not None)

    summary = {
        "avg_gamma_distance": round(avg_gamma, 6) if avg_gamma else None,
        "avg_nongamma_distance": round(avg_nongamma, 6) if avg_nongamma else None,
        "avg_random_distance": round(avg_random, 6) if avg_random else None,
        "n_gamma_pairs": len(gamma_distances),
        "n_nongamma_pairs": len(nongamma_distances),
        "n_random_pairs": len(random_distances),
        "gamma_closer_count": n_gamma_closer,
        "total_testable_pairs": n_total_testable,
        "gamma_closer_fraction": round(n_gamma_closer / n_total_testable, 4) if n_total_testable > 0 else None,
    }

    print(f"\n    === Symbol Distance Summary ===")
    print(f"    Gamma-connected mean distance:  {summary['avg_gamma_distance']}")
    print(f"    Non-Gamma control mean distance: {summary['avg_nongamma_distance']}")
    print(f"    Random baseline mean distance:   {summary['avg_random_distance']}")
    print(f"    Gamma closer in {n_gamma_closer}/{n_total_testable} module pairs")

    return summary, pair_details, gamma_by_module, nongamma_by_module, sym_universe


# ---------------------------------------------------------------------------
# Gamma distance matrix
# ---------------------------------------------------------------------------
def build_gamma_distance_matrix(formulas, gamma_by_module):
    """
    Build module × module distance matrix using Gamma-connected formulas.
    Entry (A, B) = mean Jaccard distance between Gamma formulas in A and B.
    """
    print("\n[3] Building Gamma distance matrix...")
    modules = sorted(gamma_by_module.keys())
    n = len(modules)
    matrix = {}

    for i, mod_a in enumerate(modules):
        for j, mod_b in enumerate(modules):
            if i == j:
                # Within-module distance
                pairs = list(combinations(gamma_by_module[mod_a], 2))
                if pairs:
                    dists = [jaccard_distance(fa, fb) for fa, fb in pairs]
                    matrix[(mod_a, mod_b)] = sum(dists) / len(dists)
                else:
                    matrix[(mod_a, mod_b)] = 0.0
            elif i < j:
                g_a = gamma_by_module[mod_a]
                g_b = gamma_by_module[mod_b]
                dists = [jaccard_distance(fa, fb) for fa in g_a for fb in g_b]
                if dists:
                    d = sum(dists) / len(dists)
                    matrix[(mod_a, mod_b)] = d
                    matrix[(mod_b, mod_a)] = d

    # Convert to serializable format
    matrix_dict = {}
    for mod_a in modules:
        row = {}
        for mod_b in modules:
            row[mod_b] = round(matrix.get((mod_a, mod_b), 1.0), 6)
        matrix_dict[mod_a] = row

    print(f"    Matrix: {n}×{n} modules")

    # Find closest and farthest pairs
    cross_pairs = []
    for i, mod_a in enumerate(modules):
        for j, mod_b in enumerate(modules):
            if i < j:
                cross_pairs.append((mod_a, mod_b, matrix.get((mod_a, mod_b), 1.0)))
    cross_pairs.sort(key=lambda x: x[2])

    print(f"\n    Top 10 closest Gamma-connected module pairs:")
    for mod_a, mod_b, d in cross_pairs[:10]:
        print(f"      {mod_a} <-> {mod_b}: {d:.4f}")

    print(f"\n    Top 10 farthest Gamma-connected module pairs:")
    for mod_a, mod_b, d in cross_pairs[-10:]:
        print(f"      {mod_a} <-> {mod_b}: {d:.4f}")

    return matrix_dict, modules, cross_pairs


# ---------------------------------------------------------------------------
# OEIS mod-p analysis (for modules with OEIS connections)
# ---------------------------------------------------------------------------
def analyze_oeis_modp(module_to_oeis, oeis_terms, gamma_modules):
    """
    For modules connected to OEIS, compute mod-p fingerprint distances
    between Gamma-connected and non-Gamma module pairs.
    """
    print("\n[4] OEIS mod-p fingerprint analysis...")

    # Only modules that are both Gamma-using and have OEIS connections
    gamma_oeis_modules = sorted(set(module_to_oeis.keys()) & gamma_modules)
    non_gamma_oeis_modules = sorted(set(module_to_oeis.keys()) - gamma_modules)

    print(f"    Gamma modules with OEIS links: {len(gamma_oeis_modules)}")
    print(f"    Non-Gamma modules with OEIS links: {len(non_gamma_oeis_modules)}")
    for m in gamma_oeis_modules:
        n_avail = sum(1 for s in module_to_oeis[m] if s in oeis_terms)
        print(f"      {m}: {len(module_to_oeis[m])} refs, {n_avail} with terms")

    if len(gamma_oeis_modules) < 2:
        print("    Not enough Gamma-OEIS modules for comparison")
        return None

    # Compute per-prime distances for Gamma-connected module pairs
    prime_results = {p: {"gamma_dists": [], "control_dists": [], "random_dists": []} for p in PRIMES}

    # Gamma-connected pairs
    gamma_pairs = list(combinations(gamma_oeis_modules, 2))
    for mod_a, mod_b in gamma_pairs:
        seqs_a = [s for s in module_to_oeis[mod_a] if s in oeis_terms]
        seqs_b = [s for s in module_to_oeis[mod_b] if s in oeis_terms]
        if not seqs_a or not seqs_b:
            continue
        for p in PRIMES:
            dists = []
            # Sample pairs
            n_sample = min(len(seqs_a) * len(seqs_b), 500)
            for _ in range(n_sample):
                sa = random.choice(seqs_a)
                sb = random.choice(seqs_b)
                d = fingerprint_distance(oeis_terms[sa], oeis_terms[sb], p)
                if d is not None:
                    dists.append(d)
            prime_results[p]["gamma_dists"].extend(dists)

    # Control: non-Gamma module pairs with OEIS
    if len(non_gamma_oeis_modules) >= 2:
        control_pairs = list(combinations(non_gamma_oeis_modules, 2))
        for mod_a, mod_b in random.sample(control_pairs, min(len(control_pairs), len(gamma_pairs))):
            seqs_a = [s for s in module_to_oeis[mod_a] if s in oeis_terms]
            seqs_b = [s for s in module_to_oeis[mod_b] if s in oeis_terms]
            if not seqs_a or not seqs_b:
                continue
            for p in PRIMES:
                dists = []
                n_sample = min(len(seqs_a) * len(seqs_b), 500)
                for _ in range(n_sample):
                    sa = random.choice(seqs_a)
                    sb = random.choice(seqs_b)
                    d = fingerprint_distance(oeis_terms[sa], oeis_terms[sb], p)
                    if d is not None:
                        dists.append(d)
                prime_results[p]["control_dists"].extend(dists)

    # Random baseline: random sequence pairs from all OEIS
    all_oeis_ids = list(oeis_terms.keys())
    for p in PRIMES:
        for _ in range(2000):
            sa = random.choice(all_oeis_ids)
            sb = random.choice(all_oeis_ids)
            d = fingerprint_distance(oeis_terms[sa], oeis_terms[sb], p)
            if d is not None:
                prime_results[p]["random_dists"].append(d)

    # Summarize
    scaling = {}
    print(f"\n    === Mod-p Distance Summary ===")
    print(f"    {'p':>4}  {'Gamma':>8}  {'Control':>8}  {'Random':>8}  {'Expected':>8}  {'G<C?':>5}")
    for p in PRIMES:
        gd = prime_results[p]["gamma_dists"]
        cd = prime_results[p]["control_dists"]
        rd = prime_results[p]["random_dists"]
        avg_g = sum(gd) / len(gd) if gd else None
        avg_c = sum(cd) / len(cd) if cd else None
        avg_r = sum(rd) / len(rd) if rd else None
        expected = expected_random_distance(p)
        closer = avg_g < avg_c if (avg_g is not None and avg_c is not None) else None

        scaling[str(p)] = {
            "gamma_mean": round(avg_g, 6) if avg_g is not None else None,
            "control_mean": round(avg_c, 6) if avg_c is not None else None,
            "random_mean": round(avg_r, 6) if avg_r is not None else None,
            "expected_random": round(expected, 6),
            "gamma_n": len(gd),
            "control_n": len(cd),
            "gamma_closer_than_control": closer,
        }
        print(f"    {p:>4}  {avg_g or 0:>8.4f}  {avg_c or 0:>8.4f}  {avg_r or 0:>8.4f}  {expected:>8.4f}  {'Y' if closer else 'N' if closer is False else '?':>5}")

    return scaling


# ---------------------------------------------------------------------------
# Shared symbol analysis: what does Gamma actually connect?
# ---------------------------------------------------------------------------
def analyze_gamma_companions(formulas, gamma_by_module):
    """
    For Gamma-using formulas across different modules, what OTHER symbols
    co-occur? These are the "cargo" Gamma carries through the wormhole.
    """
    print("\n[5] Gamma companion analysis (what does Gamma carry?)...")

    # Collect symbols that co-occur with Gamma, by module
    companion_by_module = {}
    for mod, gformulas in gamma_by_module.items():
        companions = Counter()
        for f in gformulas:
            for s in f["symbols"]:
                if s not in GAMMA_SYMBOLS:
                    companions[s] += 1
        companion_by_module[mod] = companions

    # Find symbols that travel with Gamma across multiple modules
    cross_module_companions = Counter()
    for mod, companions in companion_by_module.items():
        for sym in companions:
            cross_module_companions[sym] += 1

    # Symbols appearing with Gamma in 5+ modules
    universal_companions = {s: c for s, c in cross_module_companions.items() if c >= 5}
    print(f"    Symbols co-occurring with Gamma in 5+ modules:")
    for s, c in sorted(universal_companions.items(), key=lambda x: -x[1]):
        print(f"      {s}: {c} modules")

    # For each cross-module pair, what symbols do they SHARE through Gamma?
    modules = sorted(gamma_by_module.keys())
    bridge_cargo = []
    for i, mod_a in enumerate(modules):
        for j, mod_b in enumerate(modules):
            if i >= j:
                continue
            shared = set(companion_by_module[mod_a].keys()) & set(companion_by_module[mod_b].keys())
            shared -= GAMMA_SYMBOLS
            shared -= {"Equal", "For", "And", "Or", "Not", "This", "Where", "Implies",
                       "Element", "Set", "Domain", "Subset"}  # filter boilerplate
            if shared:
                bridge_cargo.append({
                    "module_a": mod_a,
                    "module_b": mod_b,
                    "shared_companions": sorted(shared),
                    "n_shared": len(shared),
                })

    bridge_cargo.sort(key=lambda x: -x["n_shared"])
    print(f"\n    Top 15 cross-module Gamma bridges by shared companions:")
    for bc in bridge_cargo[:15]:
        print(f"      {bc['module_a']} <-> {bc['module_b']}: {bc['n_shared']} shared symbols")
        print(f"        {bc['shared_companions'][:10]}{'...' if len(bc['shared_companions']) > 10 else ''}")

    return {
        "universal_companions": {s: c for s, c in sorted(universal_companions.items(), key=lambda x: -x[1])},
        "bridge_cargo": bridge_cargo[:50],
    }


# ---------------------------------------------------------------------------
# Extended Gamma family comparison
# ---------------------------------------------------------------------------
def compare_gamma_vs_extended(formulas):
    """Compare core Gamma vs extended Gamma family (with Digamma, ConstGamma)."""
    print("\n[6] Core Gamma vs Extended Gamma family...")

    core_modules = set()
    ext_modules = set()
    for f in formulas:
        syms = set(f["symbols"])
        if GAMMA_SYMBOLS & syms:
            core_modules.add(f["module"])
        if GAMMA_EXTENDED & syms:
            ext_modules.add(f["module"])

    ext_only = ext_modules - core_modules
    print(f"    Core Gamma modules: {len(core_modules)}")
    print(f"    Extended Gamma modules: {len(ext_modules)}")
    print(f"    Extended-only modules: {ext_only}")

    return {
        "core_modules": sorted(core_modules),
        "extended_modules": sorted(ext_modules),
        "extended_only": sorted(ext_only),
    }


# ---------------------------------------------------------------------------
# Operadic depth analysis
# ---------------------------------------------------------------------------
def analyze_operadic_depth(operadic_data, gamma_by_module):
    """
    Check if Gamma-connected bridges tend to have specific operadic depths
    from C12 results.
    """
    if operadic_data is None:
        return None

    print("\n[7] Operadic depth of Gamma bridges...")
    bridges = operadic_data.get("cross_domain_bridges", [])

    gamma_bridges = []
    nongamma_bridges = []
    gamma_module_set = set(gamma_by_module.keys())

    for b in bridges:
        ma = b.get("module_a", "")
        mb = b.get("module_b", "")
        syms_a = set(b.get("symbols_a", []))
        syms_b = set(b.get("symbols_b", []))
        dist = b.get("distance", 1.0)

        if GAMMA_SYMBOLS & (syms_a | syms_b):
            gamma_bridges.append(b)
        elif ma in gamma_module_set and mb in gamma_module_set:
            nongamma_bridges.append(b)

    if not gamma_bridges:
        print("    No Gamma bridges found in operadic results")
        return None

    gamma_dists = [b["distance"] for b in gamma_bridges]
    nongamma_dists = [b["distance"] for b in nongamma_bridges] if nongamma_bridges else []

    avg_g = sum(gamma_dists) / len(gamma_dists)
    avg_ng = sum(nongamma_dists) / len(nongamma_dists) if nongamma_dists else None

    print(f"    Gamma bridges in operadic data: {len(gamma_bridges)}")
    print(f"    Non-Gamma bridges (same modules): {len(nongamma_bridges)}")
    print(f"    Gamma avg operadic distance: {avg_g:.4f}")
    if avg_ng is not None:
        print(f"    Non-Gamma avg operadic distance: {avg_ng:.4f}")

    return {
        "n_gamma_bridges": len(gamma_bridges),
        "n_nongamma_bridges": len(nongamma_bridges),
        "gamma_avg_operadic_dist": round(avg_g, 6),
        "nongamma_avg_operadic_dist": round(avg_ng, 6) if avg_ng is not None else None,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("Gamma Wormhole — Algebraic Bridge Analysis")
    print("=" * 70)

    # Load data
    formulas, bridge_symbols = load_fungrim()
    operadic_data = load_operadic_results()

    # [2] Core analysis: Gamma vs non-Gamma symbol distances
    summary, pair_details, gamma_by_module, nongamma_by_module, sym_universe = \
        analyze_gamma_bridges(formulas, bridge_symbols)

    # [3] Distance matrix
    matrix_dict, matrix_modules, cross_pairs = build_gamma_distance_matrix(formulas, gamma_by_module)

    # [4] OEIS mod-p (if data available)
    module_to_oeis = extract_fungrim_oeis_links()
    oeis_terms = load_oeis_terms(max_seqs=50000)
    modp_scaling = analyze_oeis_modp(module_to_oeis, oeis_terms, set(gamma_by_module.keys()))

    # [5] Companion analysis
    companion_results = analyze_gamma_companions(formulas, gamma_by_module)

    # [6] Extended family
    family_results = compare_gamma_vs_extended(formulas)

    # [7] Operadic depth
    operadic_depth = analyze_operadic_depth(operadic_data, gamma_by_module)

    elapsed = time.time() - t0

    # Build results
    results = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": round(elapsed, 1),
            "n_formulas": len(formulas),
            "n_gamma_formulas": sum(len(v) for v in gamma_by_module.values()),
            "n_gamma_modules": len(gamma_by_module),
            "gamma_symbols_used": sorted(GAMMA_SYMBOLS),
        },
        "symbol_distance_summary": summary,
        "pair_details_top30": pair_details[:30],
        "gamma_distance_matrix": {
            "modules": matrix_modules,
            "distances": matrix_dict,
        },
        "modp_scaling": modp_scaling,
        "companion_analysis": companion_results,
        "gamma_family": family_results,
        "operadic_depth": operadic_depth,
        "cross_pairs_ranked": [
            {"module_a": a, "module_b": b, "distance": round(d, 6)}
            for a, b, d in cross_pairs
        ],
    }

    # Interpretation
    g_dist = summary.get("avg_gamma_distance")
    ng_dist = summary.get("avg_nongamma_distance")
    r_dist = summary.get("avg_random_distance")

    if g_dist and ng_dist:
        if g_dist < ng_dist:
            delta_pct = (ng_dist - g_dist) / ng_dist * 100
            interpretation = (
                f"Gamma IS carrying algebraic structure: Gamma-connected pairs are "
                f"{delta_pct:.1f}% closer than non-Gamma controls. "
                f"Gamma distance = {g_dist:.4f}, non-Gamma = {ng_dist:.4f}, "
                f"random = {r_dist:.4f}. "
                f"Gamma is closer in {summary['gamma_closer_count']}/{summary['total_testable_pairs']} module pairs."
            )
        else:
            interpretation = (
                f"Gamma appears to be mostly notational glue: Gamma-connected pairs "
                f"({g_dist:.4f}) are NOT closer than non-Gamma controls ({ng_dist:.4f}). "
                f"Random baseline = {r_dist:.4f}."
            )
    else:
        interpretation = "Insufficient data for comparison."

    results["interpretation"] = interpretation

    # Save
    with open(str(OUT_FILE), "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n{'=' * 70}")
    print(f"Results saved to {OUT_FILE}")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"\nINTERPRETATION: {interpretation}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
