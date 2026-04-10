"""
Recurrence Operator Duality — OEIS Characteristic Polynomials vs Euler Factors
===============================================================================
Challenge C08: Do OEIS linear recurrence characteristic polynomials correspond
to Euler factors of elliptic curves or modular forms?

EC Euler factor at prime p:  x^2 - a_p*x + p,  |a_p| <= 2*sqrt(p)
Genus-2 Euler factor at p:   x^4 - a*x^3 + b*x^2 - a*p*x + p^2
                              (functional equation symmetry: c = a*p, d = p^2)

Pipeline:
1. Load S33 recursion operator signatures (50K sequences, BM-extracted)
2. For additional coverage, run BM on sequences with 30+ terms from stripped_full.gz
3. Match degree-2 polynomials against EC Euler factor form
4. Match degree-4 polynomials against genus-2 Euler factor form
5. Compute random null baseline
6. Look up LMFDB for specific matches

Usage:
    python recurrence_euler_factor_match.py
"""

import gzip
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
S33_FILE = ROOT / "cartography" / "convergence" / "data" / "recursion_operator_signatures.jsonl"
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_FB = ROOT / "cartography" / "oeis" / "data" / "stripped.gz"
OUT_FILE = Path(__file__).resolve().parent / "recurrence_euler_factor_results.json"

# ---------------------------------------------------------------------------
# Primes
# ---------------------------------------------------------------------------

def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    is_p = bytearray(b'\x01') * (n + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = bytearray(len(is_p[i*i::i]))
    return set(i for i in range(2, n + 1) if is_p[i])

PRIMES_SET = sieve_primes(100000)

def is_prime(n):
    if n < 2:
        return False
    if n <= 100000:
        return n in PRIMES_SET
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

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


# ---------------------------------------------------------------------------
# OEIS loader
# ---------------------------------------------------------------------------

def load_oeis_sequences(min_length=30, max_seqs=None):
    """Load OEIS sequences from stripped_full.gz."""
    src = OEIS_STRIPPED if OEIS_STRIPPED.exists() else OEIS_STRIPPED_FB
    if not src.exists():
        print(f"  ERROR: no OEIS stripped file found at {src}")
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
            if max_seqs and len(seqs) >= max_seqs:
                break
    return seqs


# ---------------------------------------------------------------------------
# Load S33 cached results
# ---------------------------------------------------------------------------

def load_s33_results():
    """Load cached recursion operator signatures."""
    results = {}
    if not S33_FILE.exists():
        return results
    with open(S33_FILE, "r") as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("is_linear_recurrence") and obj.get("characteristic_coeffs"):
                results[obj["seq_id"]] = {
                    "degree": obj["recurrence_degree"],
                    "coeffs": obj["characteristic_coeffs"],
                }
    return results


# ---------------------------------------------------------------------------
# Euler factor matching
# ---------------------------------------------------------------------------

def check_ec_euler_factor(a_coeff, b_coeff):
    """Check if x^2 + a*x + b matches EC Euler factor form x^2 - a_p*x + p.

    In our convention: char poly is x^2 + c0*x + c1.
    EC Euler factor: x^2 - a_p*x + p.
    So c0 = -a_p, c1 = p.
    Need: c1 is prime, and |c0| <= 2*sqrt(c1) (Hasse bound).
    """
    b_int = round(b_coeff)
    if abs(b_coeff - b_int) > 0.01:
        return None
    if b_int < 2:
        return None
    if not is_prime(b_int):
        return None
    p = b_int
    a_p = -round(a_coeff)
    if abs(a_coeff - round(a_coeff)) > 0.01:
        return None
    a_p_int = int(a_p)
    hasse_bound = 2 * math.sqrt(p)
    if abs(a_p_int) > hasse_bound:
        return None
    return {"prime": p, "a_p": a_p_int, "hasse_bound": round(hasse_bound, 4)}


def check_genus2_euler_factor(coeffs):
    """Check if degree-4 poly matches genus-2 Euler factor form.

    Char poly: x^4 + c0*x^3 + c1*x^2 + c2*x + c3
    Genus-2 Euler factor: x^4 - a*x^3 + b*x^2 - a*p*x + p^2
    So: c0 = -a, c1 = b, c2 = -a*p, c3 = p^2

    Constraints:
    - c3 = p^2 for some prime p
    - c2 = c0 * p  (functional equation symmetry: -a*p = (-a)*p)
    """
    if len(coeffs) != 4:
        return None
    c0, c1, c2, c3 = [round(c) for c in coeffs]
    # Check all are close to integers
    for i, c in enumerate(coeffs):
        if abs(c - round(c)) > 0.01:
            return None

    c3_int = int(c3)
    if c3_int < 4:  # min p^2 = 4
        return None

    # Check if c3 is a perfect square
    sqrt_c3 = int(round(math.sqrt(abs(c3_int))))
    if sqrt_c3 * sqrt_c3 != c3_int:
        return None

    p = sqrt_c3
    if not is_prime(p):
        return None

    # Functional equation symmetry: c2 = c0 * p
    c0_int = int(c0)
    c2_int = int(c2)
    if c2_int != c0_int * p:
        return None

    a = -c0_int
    b = int(c1)

    return {"prime": p, "a": a, "b": b}


# ---------------------------------------------------------------------------
# Random null baseline
# ---------------------------------------------------------------------------

def null_ec_euler_factor(n_trials=10000, coeff_range=None):
    """Generate random degree-2 polynomials and check EC Euler factor match rate."""
    if coeff_range is None:
        coeff_range = (-50, 50)
    matches = 0
    random.seed(42)
    for _ in range(n_trials):
        a = random.randint(coeff_range[0], coeff_range[1])
        b = random.randint(coeff_range[0], coeff_range[1])
        if check_ec_euler_factor(float(a), float(b)) is not None:
            matches += 1
    return matches, n_trials


def null_genus2_euler_factor(n_trials=10000, coeff_range=None):
    """Generate random degree-4 polynomials and check genus-2 match rate."""
    if coeff_range is None:
        coeff_range = (-50, 50)
    matches = 0
    random.seed(42)
    for _ in range(n_trials):
        c = [random.randint(coeff_range[0], coeff_range[1]) for _ in range(4)]
        if check_genus2_euler_factor([float(x) for x in c]) is not None:
            matches += 1
    return matches, n_trials


# ---------------------------------------------------------------------------
# LMFDB lookup (best-effort)
# ---------------------------------------------------------------------------

def lookup_lmfdb_ec(prime, a_p):
    """Try to find EC in LMFDB with given a_p at prime p.

    We use the LMFDB API if available, otherwise note the query.
    Returns label or None.
    """
    # We'll batch these and try the API; for now collect queries
    return f"EC with a_{prime} = {a_p}"


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run():
    t0 = time.time()
    print("=" * 70)
    print("  C08: Recurrence Operator Duality — OEIS vs Euler Factors")
    print("=" * 70)

    # Step 1: Load S33 cached results
    print("\n  [1] Loading S33 cached results...")
    s33 = load_s33_results()
    print(f"      {len(s33):,} sequences with verified linear recurrences")

    # Separate by degree
    deg2_from_s33 = {k: v for k, v in s33.items() if v["degree"] == 2}
    deg4_from_s33 = {k: v for k, v in s33.items() if v["degree"] == 4}
    print(f"      Degree-2: {len(deg2_from_s33):,}")
    print(f"      Degree-4: {len(deg4_from_s33):,}")

    # Step 2: Extend coverage — run BM on additional sequences not in S33
    print("\n  [2] Loading additional OEIS sequences for extended BM scan...")
    # S33 ran on first 50K; load more sequences with 30+ terms
    all_seqs = load_oeis_sequences(min_length=30, max_seqs=None)
    print(f"      {len(all_seqs):,} sequences with 30+ terms total")

    # Find sequences not in S33
    new_seqs = {k: v for k, v in all_seqs.items() if k not in s33}
    print(f"      {len(new_seqs):,} sequences not yet processed by S33")

    # Sample up to 50K new sequences for BM
    if len(new_seqs) > 50000:
        random.seed(12345)
        keys = random.sample(list(new_seqs.keys()), 50000)
        new_seqs = {k: new_seqs[k] for k in keys}
        print(f"      Sampled 50,000 for BM processing")

    print(f"      Running Berlekamp-Massey on {len(new_seqs):,} additional sequences...")
    new_linear = 0
    new_deg2 = {}
    new_deg4 = {}
    for i, (sid, terms) in enumerate(new_seqs.items()):
        coeffs, degree = berlekamp_massey(terms)
        n = len(terms)
        if degree > 0 and degree < n // 3:
            if verify_recurrence(terms, coeffs, degree):
                new_linear += 1
                rounded = [round(c, 8) for c in coeffs]
                if degree == 2:
                    new_deg2[sid] = {"degree": 2, "coeffs": rounded}
                elif degree == 4:
                    new_deg4[sid] = {"degree": 4, "coeffs": rounded}
        if (i + 1) % 20000 == 0:
            print(f"        {i+1:,} processed, {new_linear:,} linear so far...")

    print(f"      New linear recurrences: {new_linear:,}")
    print(f"      New degree-2: {len(new_deg2):,}, new degree-4: {len(new_deg4):,}")

    # Combine
    all_deg2 = {**deg2_from_s33, **new_deg2}
    all_deg4 = {**deg4_from_s33, **new_deg4}
    print(f"\n      Total degree-2: {len(all_deg2):,}")
    print(f"      Total degree-4: {len(all_deg4):,}")

    # Step 3: Match degree-2 against EC Euler factor form
    print("\n  [3] Checking degree-2 polynomials against EC Euler factor form...")
    ec_matches = []
    ec_non_matches = 0
    coeff_a_range = []
    coeff_b_range = []
    for sid, info in all_deg2.items():
        c0, c1 = info["coeffs"]
        coeff_a_range.append(round(c0))
        coeff_b_range.append(round(c1))
        result = check_ec_euler_factor(c0, c1)
        if result is not None:
            ec_matches.append({
                "seq_id": sid,
                "char_poly": f"x^2 + ({round(c0)})*x + ({round(c1)})",
                "prime": result["prime"],
                "a_p": result["a_p"],
                "hasse_bound": result["hasse_bound"],
            })
        else:
            ec_non_matches += 1

    print(f"      EC Euler factor matches: {len(ec_matches)} / {len(all_deg2)}")
    print(f"      Match rate: {100*len(ec_matches)/max(len(all_deg2),1):.2f}%")

    # Show matches
    if ec_matches:
        print(f"\n      EC Euler factor matches (showing up to 30):")
        for m in sorted(ec_matches, key=lambda x: x["prime"])[:30]:
            print(f"        {m['seq_id']}: {m['char_poly']}  "
                  f"=> p={m['prime']}, a_p={m['a_p']}")

    # Step 4: Match degree-4 against genus-2 Euler factor form
    print(f"\n  [4] Checking degree-4 polynomials against genus-2 Euler factor form...")
    g2_matches = []
    for sid, info in all_deg4.items():
        coeffs = info["coeffs"]
        result = check_genus2_euler_factor(coeffs)
        if result is not None:
            c = [round(x) for x in coeffs]
            g2_matches.append({
                "seq_id": sid,
                "char_poly": f"x^4 + ({c[0]})*x^3 + ({c[1]})*x^2 + ({c[2]})*x + ({c[3]})",
                "prime": result["prime"],
                "a": result["a"],
                "b": result["b"],
            })

    print(f"      Genus-2 Euler factor matches: {len(g2_matches)} / {len(all_deg4)}")
    print(f"      Match rate: {100*len(g2_matches)/max(len(all_deg4),1):.2f}%")

    if g2_matches:
        print(f"\n      Genus-2 Euler factor matches:")
        for m in g2_matches[:30]:
            print(f"        {m['seq_id']}: {m['char_poly']}  "
                  f"=> p={m['prime']}, a={m['a']}, b={m['b']}")

    # Step 5: Null baseline
    # Two null models:
    #   (A) Uniform over observed coefficient range
    #   (B) Distribution-matched: resample from empirical coefficient distribution
    print(f"\n  [5] Computing null baselines...")

    n_null = 10000
    random.seed(42)

    # ---- EC degree-2 null ----
    # Null A: uniform over observed range
    a_lo = max(min(coeff_a_range), -200) if coeff_a_range else -50
    a_hi = min(max(coeff_a_range), 200) if coeff_a_range else 50
    b_lo = max(min(coeff_b_range), -200) if coeff_b_range else -50
    b_hi = min(max(coeff_b_range), 200) if coeff_b_range else 200

    print(f"      Coefficient ranges: a in [{a_lo}, {a_hi}], b in [{b_lo}, {b_hi}]")

    null_ec_uniform = 0
    for _ in range(n_null):
        a = random.randint(a_lo, a_hi)
        b = random.randint(b_lo, b_hi)
        if check_ec_euler_factor(float(a), float(b)) is not None:
            null_ec_uniform += 1

    # Null B: resample from empirical distribution (shuffle a and b independently)
    null_ec_resampled = 0
    a_pool = list(coeff_a_range)
    b_pool = list(coeff_b_range)
    for _ in range(n_null):
        a = random.choice(a_pool)
        b = random.choice(b_pool)
        if check_ec_euler_factor(float(a), float(b)) is not None:
            null_ec_resampled += 1

    null_ec_rate_uniform = null_ec_uniform / n_null
    null_ec_rate_resampled = null_ec_resampled / n_null
    oeis_ec_rate = len(ec_matches) / max(len(all_deg2), 1)
    ec_excess_uniform = oeis_ec_rate / max(null_ec_rate_uniform, 1e-10)
    ec_excess_resampled = oeis_ec_rate / max(null_ec_rate_resampled, 1e-10)

    print(f"      EC null (uniform):     {null_ec_uniform}/{n_null} = {100*null_ec_rate_uniform:.2f}%")
    print(f"      EC null (resampled):   {null_ec_resampled}/{n_null} = {100*null_ec_rate_resampled:.2f}%")
    print(f"      OEIS rate:             {100*oeis_ec_rate:.2f}%")
    print(f"      Excess (vs uniform):   {ec_excess_uniform:.2f}x")
    print(f"      Excess (vs resampled): {ec_excess_resampled:.2f}x")

    # ---- Genus-2 degree-4 null ----
    if all_deg4:
        c0_pool = [round(info["coeffs"][0]) for info in all_deg4.values()]
        c1_pool = [round(info["coeffs"][1]) for info in all_deg4.values()]
        c2_pool = [round(info["coeffs"][2]) for info in all_deg4.values()]
        c3_pool = [round(info["coeffs"][3]) for info in all_deg4.values()]
        all_c_vals = c0_pool + c1_pool + c2_pool + c3_pool
        c_lo = max(min(all_c_vals), -200)
        c_hi = min(max(all_c_vals), 200)
    else:
        c0_pool = c1_pool = c2_pool = c3_pool = list(range(-50, 51))
        c_lo, c_hi = -50, 50

    null_g2_uniform = 0
    random.seed(42)
    for _ in range(n_null):
        c = [random.randint(c_lo, c_hi) for _ in range(4)]
        if check_genus2_euler_factor([float(x) for x in c]) is not None:
            null_g2_uniform += 1

    null_g2_resampled = 0
    random.seed(42)
    for _ in range(n_null):
        c = [random.choice(c0_pool), random.choice(c1_pool),
             random.choice(c2_pool), random.choice(c3_pool)]
        if check_genus2_euler_factor([float(x) for x in c]) is not None:
            null_g2_resampled += 1

    null_g2_rate_uniform = null_g2_uniform / n_null
    null_g2_rate_resampled = null_g2_resampled / n_null
    oeis_g2_rate = len(g2_matches) / max(len(all_deg4), 1)
    g2_excess_uniform = oeis_g2_rate / max(null_g2_rate_uniform, 1e-10)
    g2_excess_resampled = oeis_g2_rate / max(null_g2_rate_resampled, 1e-10)

    print(f"      G2 null (uniform):     {null_g2_uniform}/{n_null} = {100*null_g2_rate_uniform:.2f}%")
    print(f"      G2 null (resampled):   {null_g2_resampled}/{n_null} = {100*null_g2_rate_resampled:.2f}%")
    print(f"      OEIS rate:             {100*oeis_g2_rate:.2f}%")
    print(f"      G2 excess (uniform):   {g2_excess_uniform:.2f}x")
    print(f"      G2 excess (resampled): {g2_excess_resampled:.2f}x")

    # Use resampled as the primary null (more conservative)
    null_ec_rate = null_ec_rate_resampled
    null_g2_rate = null_g2_rate_resampled
    ec_excess = ec_excess_resampled
    g2_excess = g2_excess_resampled

    # Step 6: LMFDB cross-reference (best-effort API calls)
    print(f"\n  [6] LMFDB cross-reference (attempting API lookups)...")
    lmfdb_ec_hits = []
    lmfdb_g2_hits = []

    try:
        import urllib.request
        import urllib.parse

        # Try a few EC lookups
        for m in ec_matches[:20]:
            p = m["prime"]
            a_p = m["a_p"]
            # LMFDB API: search for EC with specific a_p at prime p
            url = (f"https://www.lmfdb.org/api/ec/curves/"
                   f"?ap{p}={a_p}&_fields=lmfdb_label,conductor&_limit=3")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Prometheus-Charon/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    if data.get("data"):
                        labels = [d["lmfdb_label"] for d in data["data"][:3]]
                        m["lmfdb_labels"] = labels
                        lmfdb_ec_hits.append(m)
                        print(f"        {m['seq_id']} => LMFDB: {', '.join(labels)}")
            except Exception:
                pass  # API may not support this query format

        # Try genus-2 lookups
        for m in g2_matches[:10]:
            p = m["prime"]
            # LMFDB genus-2 API
            url = (f"https://www.lmfdb.org/api/g2c/curves/"
                   f"?_fields=label&_limit=3")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Prometheus-Charon/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    # Just note we connected; actual a_p matching requires more work
            except Exception:
                pass

    except ImportError:
        print("      (urllib not available, skipping LMFDB lookups)")
    except Exception as e:
        print(f"      LMFDB lookup error: {e}")

    if lmfdb_ec_hits:
        print(f"      Found {len(lmfdb_ec_hits)} OEIS sequences with LMFDB EC matches")
    else:
        print(f"      No direct LMFDB API matches found (API format may differ)")

    # Step 7: Analyze polynomial clustering
    print(f"\n  [7] Polynomial clustering analysis...")
    poly_to_seqs = defaultdict(list)
    for sid, info in {**all_deg2, **all_deg4}.items():
        poly_key = tuple(round(c) for c in info["coeffs"])
        poly_to_seqs[poly_key].append(sid)

    clusters = [(k, v) for k, v in poly_to_seqs.items() if len(v) >= 2]
    clusters.sort(key=lambda x: -len(x[1]))
    print(f"      {len(clusters)} clusters with 2+ sequences sharing same char poly")
    for poly, seqs in clusters[:15]:
        deg = len(poly)
        poly_str = f"x^{deg}" + "".join(
            f" + ({c})*x^{deg-i-1}" if deg-i-1 > 0 else f" + ({c})"
            for i, c in enumerate(poly)
        )
        # Check if this is an Euler factor
        is_euler = ""
        if deg == 2:
            result = check_ec_euler_factor(float(poly[0]), float(poly[1]))
            if result:
                is_euler = f" [EC Euler: p={result['prime']}, a_p={result['a_p']}]"
        elif deg == 4:
            result = check_genus2_euler_factor([float(x) for x in poly])
            if result:
                is_euler = f" [Genus-2 Euler: p={result['prime']}]"
        print(f"        {poly_str}  ({len(seqs)} seqs){is_euler}")
        if len(seqs) <= 10:
            print(f"          {', '.join(seqs)}")
        else:
            print(f"          {', '.join(seqs[:8])}, ... (+{len(seqs)-8})")

    # Step 8: Compile results
    elapsed = time.time() - t0

    results = {
        "challenge": "C08",
        "title": "Recurrence Operator Duality — OEIS Characteristic Polynomials vs Euler Factors",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "coverage": {
            "total_sequences_scanned": len(s33) + len(new_seqs),
            "s33_cached": len(s33),
            "newly_scanned": len(new_seqs),
            "degree_2_polynomials": len(all_deg2),
            "degree_4_polynomials": len(all_deg4),
        },
        "ec_euler_factor": {
            "matches": len(ec_matches),
            "total_deg2": len(all_deg2),
            "match_rate": round(oeis_ec_rate, 6),
            "null_rate": round(null_ec_rate, 6),
            "excess_over_null": round(ec_excess, 4),
            "sequences": [
                {
                    "seq_id": m["seq_id"],
                    "char_poly": m["char_poly"],
                    "prime": m["prime"],
                    "a_p": m["a_p"],
                    "lmfdb_labels": m.get("lmfdb_labels", []),
                }
                for m in sorted(ec_matches, key=lambda x: x["prime"])
            ],
        },
        "genus2_euler_factor": {
            "matches": len(g2_matches),
            "total_deg4": len(all_deg4),
            "match_rate": round(oeis_g2_rate, 6),
            "null_rate": round(null_g2_rate, 6),
            "excess_over_null": round(g2_excess, 4),
            "sequences": [
                {
                    "seq_id": m["seq_id"],
                    "char_poly": m["char_poly"],
                    "prime": m["prime"],
                    "a": m["a"],
                    "b": m["b"],
                }
                for m in g2_matches
            ],
        },
        "null_baseline": {
            "n_trials": n_null,
            "ec_null_uniform": {"matches": null_ec_uniform, "rate": round(null_ec_rate_uniform, 6)},
            "ec_null_resampled": {"matches": null_ec_resampled, "rate": round(null_ec_rate_resampled, 6)},
            "genus2_null_uniform": {"matches": null_g2_uniform, "rate": round(null_g2_rate_uniform, 6)},
            "genus2_null_resampled": {"matches": null_g2_resampled, "rate": round(null_g2_rate_resampled, 6)},
            "coeff_range_a": [a_lo, a_hi],
            "coeff_range_b": [b_lo, b_hi],
            "note": "Resampled null shuffles empirical coefficient pools independently; more conservative than uniform",
        },
        "polynomial_clusters": {
            "total_clusters": len(clusters),
            "top_clusters": [
                {
                    "char_poly_coeffs": list(poly),
                    "degree": len(poly),
                    "n_sequences": len(seqs),
                    "sequences": seqs[:20],
                    "is_ec_euler": check_ec_euler_factor(
                        float(poly[0]), float(poly[1])
                    ) is not None if len(poly) == 2 else False,
                    "is_genus2_euler": check_genus2_euler_factor(
                        [float(x) for x in poly]
                    ) is not None if len(poly) == 4 else False,
                }
                for poly, seqs in clusters[:30]
            ],
        },
        "lmfdb_hits": [
            {
                "seq_id": m["seq_id"],
                "prime": m["prime"],
                "a_p": m["a_p"],
                "lmfdb_labels": m.get("lmfdb_labels", []),
            }
            for m in lmfdb_ec_hits
        ],
        "elapsed_seconds": round(elapsed, 1),
    }

    # Save
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"  {'=' * 40}")
    print(f"  Total sequences scanned:    {results['coverage']['total_sequences_scanned']:>10,}")
    print(f"  Degree-2 polynomials:       {len(all_deg2):>10,}")
    print(f"  Degree-4 polynomials:       {len(all_deg4):>10,}")
    print(f"  EC Euler factor matches:    {len(ec_matches):>10,}  "
          f"({100*oeis_ec_rate:.2f}% vs {100*null_ec_rate:.2f}% null)")
    print(f"  Genus-2 Euler matches:      {len(g2_matches):>10,}  "
          f"({100*oeis_g2_rate:.2f}% vs {100*null_g2_rate:.2f}% null)")
    print(f"  EC excess over null:        {ec_excess:>10.2f}x")
    print(f"  Genus-2 excess over null:   {g2_excess:>10.2f}x")
    print(f"  Polynomial clusters (2+):   {len(clusters):>10,}")
    print(f"  LMFDB confirmed hits:       {len(lmfdb_ec_hits):>10,}")
    print(f"  Elapsed:                    {elapsed:>9.1f}s")
    print(f"\n  Output: {OUT_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    run()
