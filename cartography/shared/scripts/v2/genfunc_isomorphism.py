"""
Generating Function Isomorphism — Cross-Recurrence Identity Detection
=====================================================================
Challenge R3-8: Different recurrences can produce the SAME rational generating
function G(x) = P(x)/Q(x) when reduced to lowest terms. This script detects
such isomorphisms, revealing deeper combinatorial equivalences.

Pipeline:
1. Load sequences with known linear recurrences from S33 cache
2. Load initial terms from OEIS stripped data
3. For each sequence: compute generating function G(x) = P(x)/Q(x)
4. Reduce to lowest terms using polynomial GCD (sympy exact arithmetic)
5. Cluster by reduced generating function
6. Find cross-recurrence matches (different Q, same reduced G)
7. Deep dive into Collatz cluster (105 members)

Usage:
    python genfunc_isomorphism.py
"""

import gzip
import json
import time
from collections import defaultdict, Counter
from fractions import Fraction
from pathlib import Path

from sympy import Poly, Symbol, gcd, ZZ, QQ, Rational, factorint
from sympy.polys.polyerrors import GeneratorsNeeded

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
S33_FILE = ROOT / "cartography" / "convergence" / "data" / "recursion_operator_signatures.jsonl"
OEIS_STRIPPED = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_NEW = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
COLLATZ_FILE = Path(__file__).resolve().parent / "collatz_family_results.json"
OUT_FILE = Path(__file__).resolve().parent / "genfunc_isomorphism_results.json"

x = Symbol('x')

# ---------------------------------------------------------------------------
# Berlekamp-Massey (integer exact version)
# ---------------------------------------------------------------------------

def berlekamp_massey_int(seq):
    """Berlekamp-Massey over rationals. Returns coeffs c_1..c_d such that
    a(n) = c_1*a(n-1) + c_2*a(n-2) + ... + c_d*a(n-d).
    Returns (coeffs_as_Fraction_list, degree) or ([], 0) on failure."""
    n = len(seq)
    if n == 0:
        return [], 0
    s = [Fraction(v) for v in seq]
    # c is the connection polynomial (1, c_1, c_2, ...)
    c = [Fraction(1)]
    b = [Fraction(1)]
    l_deg = 0
    m = 1
    d_val = Fraction(1)
    for i in range(n):
        disc = s[i]
        for j in range(1, l_deg + 1):
            if j < len(c):
                disc += c[j] * s[i - j]
        if disc == 0:
            m += 1
        elif 2 * l_deg <= i:
            t = list(c)
            coef = -disc / d_val
            while len(c) < len(b) + m:
                c.append(Fraction(0))
            for j in range(len(b)):
                c[j + m] += coef * b[j]
            l_deg = i + 1 - l_deg
            b = t
            d_val = disc
            m = 1
        else:
            coef = -disc / d_val
            while len(c) < len(b) + m:
                c.append(Fraction(0))
            for j in range(len(b)):
                c[j + m] += coef * b[j]
            m += 1
    # Connection polynomial: c[0]=1, c[1]..c[l_deg]
    # Recurrence: a(n) + c[1]*a(n-1) + ... + c[l_deg]*a(n-l_deg) = 0
    # So a(n) = -c[1]*a(n-1) - ... - c[l_deg]*a(n-l_deg)
    coeffs = [-c[j] for j in range(1, l_deg + 1)]
    return coeffs, l_deg


def verify_recurrence_exact(seq, coeffs, degree):
    """Check recurrence over exact rationals."""
    if degree == 0 or not coeffs:
        return False
    n = len(seq)
    if degree >= n:
        return False
    for i in range(degree, min(n, degree + max(20, n // 2))):
        predicted = sum(coeffs[j] * Fraction(seq[i - j - 1]) for j in range(degree))
        if predicted != Fraction(seq[i]):
            return False
    return True


# ---------------------------------------------------------------------------
# Generating function computation (exact rational arithmetic)
# ---------------------------------------------------------------------------

def compute_genfunc(initial_terms, rec_coeffs, degree):
    """Compute rational generating function G(x) = P(x)/Q(x).

    Given recurrence a(n) = c_1*a(n-1) + ... + c_d*a(n-d) with initial terms
    a(0), ..., a(d-1):

    The denominator (in x-space) is:
        Q(x) = 1 - c_1*x - c_2*x^2 - ... - c_d*x^d

    The numerator P(x) is determined by:
        P(x) = Q(x) * G(x) truncated to degree < d
        i.e., P(x) = sum_{n=0}^{d-1} p_n * x^n
        where p_n = a(n) - sum_{k=1}^{n} c_k * a(n-k)

    Returns (P_poly, Q_poly) as sympy Poly objects over QQ, or None on failure.
    """
    if degree <= 0 or len(initial_terms) < degree:
        return None

    def to_rational(v):
        """Convert int, float, or Fraction to sympy Rational."""
        if isinstance(v, Fraction):
            return Rational(v.numerator, v.denominator)
        return Rational(v)

    # Build Q(x) = 1 - c_1*x - c_2*x^2 - ... - c_d*x^d
    q_coeffs = {0: Rational(1)}
    for k in range(1, degree + 1):
        q_coeffs[k] = -to_rational(rec_coeffs[k - 1])

    # Build P(x) numerator
    # p_n = a(n) - sum_{k=1}^{n} c_k * a(n-k)
    p_coeffs = {}
    for n in range(degree):
        pn = to_rational(initial_terms[n])
        for k in range(1, n + 1):
            pn -= to_rational(rec_coeffs[k - 1]) * to_rational(initial_terms[n - k])
        if pn != 0:
            p_coeffs[n] = pn

    try:
        Q = Poly(sum(coeff * x**power for power, coeff in q_coeffs.items()), x, domain='QQ')
        if p_coeffs:
            P = Poly(sum(coeff * x**power for power, coeff in p_coeffs.items()), x, domain='QQ')
        else:
            P = Poly(Rational(0), x, domain='QQ')
        return P, Q
    except (GeneratorsNeeded, Exception):
        return None


def reduce_genfunc(P, Q):
    """Reduce P(x)/Q(x) to lowest terms using polynomial GCD."""
    if P.is_zero:
        return P, Q
    try:
        g = gcd(P, Q)
        if g.is_one or g.is_zero:
            return P, Q
        P_red = Poly(P.as_expr() // g.as_expr(), x, domain='QQ')
        Q_red = Poly(Q.as_expr() // g.as_expr(), x, domain='QQ')
        return P_red, Q_red
    except Exception:
        return P, Q


def poly_signature(P, Q):
    """Create a canonical string signature for a reduced generating function.
    Normalizes so that leading coeff of Q is positive."""
    if Q.is_zero:
        return None
    # Get coefficients as rationals
    q_lc = Q.LC()
    if q_lc < 0:
        P = Poly(-P.as_expr(), x, domain='QQ')
        Q = Poly(-Q.as_expr(), x, domain='QQ')
        q_lc = Q.LC()
    # Normalize: make Q monic by dividing both by q_lc
    if q_lc != 1:
        P_expr = P.as_expr() / q_lc
        Q_expr = Q.as_expr() / q_lc
        try:
            P = Poly(P_expr, x, domain='QQ')
            Q = Poly(Q_expr, x, domain='QQ')
        except Exception:
            pass
    p_str = str(P.as_expr())
    q_str = str(Q.as_expr())
    return f"({p_str})/({q_str})"


def char_poly_signature(rec_coeffs, degree):
    """Create a canonical signature for the characteristic polynomial.
    Char poly: x^d - c_1*x^{d-1} - ... - c_d"""
    coeffs_str = ",".join(str(Rational(c)) for c in rec_coeffs)
    return f"d{degree}:[{coeffs_str}]"


def minimal_char_poly_signature(rec_coeffs, degree):
    """Like char_poly_signature but strip trailing zeros to get minimal form."""
    # Strip trailing zero coefficients
    coeffs = list(rec_coeffs)
    while coeffs and Fraction(coeffs[-1]) == 0:
        coeffs.pop()
    min_deg = len(coeffs)
    if min_deg == 0:
        return "d0:[]"
    coeffs_str = ",".join(str(Rational(c)) for c in coeffs)
    return f"d{min_deg}:[{coeffs_str}]"


# ---------------------------------------------------------------------------
# OEIS data loaders
# ---------------------------------------------------------------------------

def load_oeis_terms():
    """Load all OEIS sequences from stripped_new.txt or stripped_full.gz."""
    seqs = {}
    src = OEIS_STRIPPED_NEW
    if src.exists():
        print(f"  Loading OEIS from {src.name} ...")
        with open(str(src), "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(" ", 1)
                if len(parts) < 2:
                    # Try comma-separated with A-number prefix
                    if line.startswith("A") and "," in line:
                        idx = line.index(",")
                        sid = line[:idx].strip()
                        rest = line[idx:].strip().strip(",")
                    else:
                        continue
                else:
                    sid = parts[0].strip()
                    rest = parts[1].strip().strip(",")
                if not sid.startswith("A"):
                    continue
                try:
                    terms = [int(t) for t in rest.split(",") if t.strip()]
                except ValueError:
                    continue
                if len(terms) >= 4:
                    seqs[sid] = terms
        print(f"  Loaded {len(seqs)} sequences")
        return seqs

    # Fallback to gzipped
    src = OEIS_STRIPPED
    if not src.exists():
        print("  ERROR: No OEIS data found")
        return seqs
    print(f"  Loading OEIS from {src.name} ...")
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
            try:
                terms = [int(t) for t in parts[1].strip().strip(",").split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) >= 4:
                seqs[sid] = terms
    print(f"  Loaded {len(seqs)} sequences")
    return seqs


def load_s33_recurrences():
    """Load cached BM recurrence results."""
    results = {}
    if not S33_FILE.exists():
        print(f"  WARNING: S33 file not found at {S33_FILE}")
        return results
    with open(S33_FILE, "r") as f:
        for line in f:
            obj = json.loads(line)
            if obj.get("is_linear_recurrence") and obj.get("characteristic_coeffs"):
                results[obj["seq_id"]] = {
                    "degree": obj["recurrence_degree"],
                    "coeffs": obj["characteristic_coeffs"],
                }
    print(f"  Loaded {len(results)} S33 recurrences")
    return results


def load_collatz_members():
    """Load Collatz cluster member IDs from C17 results."""
    if not COLLATZ_FILE.exists():
        return []
    with open(COLLATZ_FILE, "r") as f:
        data = json.load(f)
    return [s["seq_id"] for s in data.get("sequences", [])]


# ---------------------------------------------------------------------------
# Mod-p fingerprint
# ---------------------------------------------------------------------------

def mod_p_fingerprint(terms, p, length=20):
    """First `length` terms mod p."""
    return tuple(t % p for t in terms[:length])


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print("=" * 72)
    print("R3-8: Generating Function Isomorphism Detection")
    print("=" * 72)

    # ── Step 1: Load data ──────────────────────────────────────────────────
    print("\n[1] Loading data ...")
    s33 = load_s33_recurrences()
    oeis = load_oeis_terms()
    collatz_ids = set(load_collatz_members())
    print(f"  Collatz cluster: {len(collatz_ids)} members")

    # ── Step 2: Compute generating functions ───────────────────────────────
    print("\n[2] Computing generating functions (exact rational arithmetic) ...")
    genfunc_results = {}  # seq_id -> (P, Q, P_red, Q_red, sig, char_sig)
    skipped = Counter()
    processed = 0

    # Also run BM on Collatz members not in S33
    collatz_not_in_s33 = collatz_ids - set(s33.keys())
    if collatz_not_in_s33:
        print(f"  Running BM on {len(collatz_not_in_s33)} Collatz members not in S33 cache ...")
        for sid in collatz_not_in_s33:
            if sid not in oeis:
                continue
            terms = oeis[sid]
            if len(terms) < 10:
                continue
            coeffs, deg = berlekamp_massey_int(terms)
            if deg > 0 and deg <= len(terms) // 3:
                coeffs_f = [float(c) for c in coeffs]
                s33[sid] = {"degree": deg, "coeffs": coeffs_f}

    # Expand: run BM on additional OEIS sequences not in S33
    # Focus on sequences with enough terms for low-degree recurrences
    extra_candidates = [sid for sid in oeis if sid not in s33 and len(oeis[sid]) >= 20]
    extra_candidates.sort()  # deterministic order
    MAX_EXTRA = 50000
    extra_candidates = extra_candidates[:MAX_EXTRA]
    print(f"  Running BM on {len(extra_candidates)} additional OEIS sequences ...")
    extra_found = 0
    for i, sid in enumerate(extra_candidates):
        terms = oeis[sid]
        coeffs, deg = berlekamp_massey_int(terms[:60])  # limit terms for speed
        if deg > 0 and deg <= 12 and deg <= len(terms) // 3:
            if verify_recurrence_exact(terms, coeffs, deg):
                s33[sid] = {"degree": deg, "coeffs_exact": coeffs, "recomputed": True}
                extra_found += 1
        if (i + 1) % 10000 == 0:
            print(f"    {i+1}/{len(extra_candidates)} scanned, {extra_found} recurrences found ...")
    print(f"  Extra recurrences found: {extra_found}")

    # Instead of trusting S33 float coefficients, re-run BM on the integer
    # sequences directly.  This gives exact Fraction coefficients.
    print(f"  Re-running BM on {len(s33)} S33 sequences for exact coefficients ...")
    recomputed = 0
    for sid in list(s33.keys()):
        if sid not in oeis:
            continue
        terms = oeis[sid]
        old_deg = s33[sid]["degree"]
        if old_deg > 20:
            continue
        if len(terms) < max(10, 2 * old_deg + 4):
            continue
        coeffs, deg = berlekamp_massey_int(terms)
        if deg > 0 and deg <= old_deg + 2 and deg <= len(terms) // 3:
            s33[sid] = {"degree": deg, "coeffs_exact": coeffs, "recomputed": True}
            recomputed += 1
    print(f"  Recomputed: {recomputed}")

    total = len(s33)
    report_interval = max(1, total // 20)

    for sid, rec in s33.items():
        if sid not in oeis:
            skipped["no_oeis_terms"] += 1
            continue
        terms = oeis[sid]

        # Use recomputed exact coefficients if available
        if rec.get("recomputed"):
            degree = rec["degree"]
            rec_coeffs = rec["coeffs_exact"]  # already Fraction
        else:
            degree = rec["degree"]
            coeffs_raw = rec["coeffs"]
            if degree > 20:
                skipped["degree_too_high"] += 1
                continue
            # Convert float coefficients: round to integer if close
            try:
                rec_coeffs = []
                for c in coeffs_raw:
                    rounded = round(c)
                    if abs(c - rounded) < 1e-6:
                        rec_coeffs.append(Fraction(rounded))
                    else:
                        rec_coeffs.append(Fraction(c).limit_denominator(10**9))
            except (ValueError, OverflowError):
                skipped["bad_coeffs"] += 1
                continue

        if degree > 20:
            skipped["degree_too_high"] += 1
            continue

        if len(terms) < degree:
            skipped["too_few_terms"] += 1
            continue

        initial = terms[:degree]

        # Verify recurrence holds exactly
        if not verify_recurrence_exact(terms, rec_coeffs, degree):
            skipped["recurrence_fails"] += 1
            continue

        # Compute generating function
        result = compute_genfunc(initial, rec_coeffs, degree)
        if result is None:
            skipped["genfunc_fail"] += 1
            continue

        P, Q = result
        P_red, Q_red = reduce_genfunc(P, Q)
        sig = poly_signature(P_red, Q_red)
        char_sig = char_poly_signature(rec_coeffs, degree)

        if sig is None:
            skipped["sig_fail"] += 1
            continue

        min_char_sig = minimal_char_poly_signature(rec_coeffs, degree)

        genfunc_results[sid] = {
            "P_str": str(P.as_expr()),
            "Q_str": str(Q.as_expr()),
            "P_red_str": str(P_red.as_expr()),
            "Q_red_str": str(Q_red.as_expr()),
            "genfunc_sig": sig,
            "char_poly_sig": char_sig,
            "min_char_poly_sig": min_char_sig,
            "degree": degree,
            "rec_coeffs": [str(c) for c in rec_coeffs],
        }
        processed += 1
        if processed % report_interval == 0:
            print(f"    {processed}/{total} processed ...")

    print(f"  Processed: {processed}")
    print(f"  Skipped: {dict(skipped)}")

    # ── Step 3: Cluster by reduced generating function ─────────────────────
    print("\n[3] Clustering by reduced generating function ...")

    gf_clusters = defaultdict(list)  # genfunc_sig -> [seq_ids]
    char_clusters = defaultdict(list)  # char_poly_sig -> [seq_ids]

    for sid, info in genfunc_results.items():
        gf_clusters[info["genfunc_sig"]].append(sid)
        char_clusters[info["char_poly_sig"]].append(sid)

    n_gf_clusters = len(gf_clusters)
    n_char_clusters = len(char_clusters)
    print(f"  Generating function clusters: {n_gf_clusters}")
    print(f"  Recurrence (char poly) clusters: {n_char_clusters}")
    print(f"  Compression ratio: {n_char_clusters / max(1, n_gf_clusters):.3f}")

    # Multi-member GF clusters
    multi_gf = {sig: sids for sig, sids in gf_clusters.items() if len(sids) > 1}
    print(f"  GF clusters with 2+ members: {len(multi_gf)}")
    print(f"  Largest GF cluster: {max(len(v) for v in gf_clusters.values()) if gf_clusters else 0}")

    # ── Step 4: Cross-recurrence matches ───────────────────────────────────
    print("\n[4] Finding cross-recurrence generating function matches ...")
    cross_matches = []
    for sig, sids in multi_gf.items():
        # Get distinct characteristic polynomials in this cluster
        char_polys_in_cluster = set()
        for sid in sids:
            char_polys_in_cluster.add(genfunc_results[sid]["char_poly_sig"])
        if len(char_polys_in_cluster) > 1:
            cross_matches.append({
                "genfunc_sig": sig,
                "n_sequences": len(sids),
                "n_distinct_char_polys": len(char_polys_in_cluster),
                "sequences": sids,
                "char_polys": list(char_polys_in_cluster),
            })

    print(f"  Cross-recurrence matches: {len(cross_matches)}")
    for cm in sorted(cross_matches, key=lambda x: -x["n_sequences"])[:10]:
        print(f"    {cm['genfunc_sig'][:60]}... : {cm['n_sequences']} seqs, {cm['n_distinct_char_polys']} char polys")

    # ── Step 5: Collatz cluster deep dive ──────────────────────────────────
    print("\n[5] Collatz cluster generating function analysis ...")
    collatz_gf = {}
    collatz_in_results = 0
    for sid in collatz_ids:
        if sid in genfunc_results:
            collatz_in_results += 1
            info = genfunc_results[sid]
            collatz_gf[sid] = info["genfunc_sig"]

    collatz_distinct_gf = set(collatz_gf.values())
    print(f"  Collatz members with computed GF: {collatz_in_results}")
    print(f"  Distinct reduced generating functions: {len(collatz_distinct_gf)}")

    # Group Collatz by GF
    collatz_gf_groups = defaultdict(list)
    for sid, sig in collatz_gf.items():
        collatz_gf_groups[sig].append(sid)

    print(f"  GF group sizes: {sorted([len(v) for v in collatz_gf_groups.values()], reverse=True)[:20]}")

    # Check for sequences OUTSIDE Collatz sharing a GF with Collatz members
    collatz_outsiders = {}
    for sig in collatz_distinct_gf:
        all_with_sig = gf_clusters.get(sig, [])
        outside = [s for s in all_with_sig if s not in collatz_ids]
        if outside:
            collatz_outsiders[sig] = outside

    print(f"  GFs shared with non-Collatz sequences: {len(collatz_outsiders)}")
    for sig, outsiders in list(collatz_outsiders.items())[:5]:
        collatz_in = [s for s in gf_clusters[sig] if s in collatz_ids]
        print(f"    GF: {sig[:50]}...")
        print(f"      Collatz: {collatz_in[:5]}")
        print(f"      Outside: {outsiders[:5]}")

    # ── Step 6: Mod-p fingerprint test for cross-matches ───────────────────
    print("\n[6] Mod-p fingerprint tests for cross-recurrence matches ...")
    modp_results = []
    for cm in cross_matches[:50]:
        sids = cm["sequences"]
        for p in [2, 3, 5, 7, 11]:
            fps = {}
            for sid in sids:
                if sid in oeis:
                    fp = mod_p_fingerprint(oeis[sid], p)
                    fps[sid] = fp
            if len(fps) >= 2:
                unique_fps = len(set(fps.values()))
                if unique_fps < len(fps):
                    # Some share mod-p fingerprints
                    fp_groups = defaultdict(list)
                    for sid, fp in fps.items():
                        fp_groups[fp].append(sid)
                    shared = {str(k): v for k, v in fp_groups.items() if len(v) > 1}
                    if shared:
                        modp_results.append({
                            "genfunc_sig": cm["genfunc_sig"][:80],
                            "prime": p,
                            "shared_fingerprints": len(shared),
                            "examples": {k: v[:3] for k, v in list(shared.items())[:3]},
                        })

    print(f"  Cross-matches with shared mod-p fingerprints: {len(modp_results)}")
    for mr in modp_results[:5]:
        print(f"    GF {mr['genfunc_sig'][:40]}... mod {mr['prime']}: {mr['shared_fingerprints']} shared groups")

    # ── Step 7: Famous sequence surprises ──────────────────────────────────
    print("\n[7] Checking for famous sequence surprises ...")
    famous = {
        "A000045": "Fibonacci",
        "A000079": "Powers of 2",
        "A000225": "2^n - 1 (Mersenne)",
        "A000027": "Natural numbers",
        "A000290": "Squares",
        "A000217": "Triangular numbers",
        "A000204": "Lucas numbers",
        "A001906": "F(2n) (even Fibonacci)",
        "A001519": "F(2n-1) (odd Fibonacci)",
        "A000032": "Lucas numbers",
        "A000129": "Pell numbers",
        "A001045": "Jacobsthal numbers",
        "A000930": "Narayana's cows",
        "A000073": "Tribonacci",
        "A000108": "Catalan",
        "A001333": "Numerators of sqrt(2) convergents",
        "A000984": "Central binomial coefficients",
        "A001109": "a(n) such that a(n)^2 is triangular",
        "A002378": "Oblong (pronic) numbers",
        "A005408": "Odd numbers",
    }

    famous_matches = []
    for fid, fname in famous.items():
        if fid in genfunc_results:
            sig = genfunc_results[fid]["genfunc_sig"]
            cluster = gf_clusters.get(sig, [])
            partners = [s for s in cluster if s != fid]
            if partners:
                famous_matches.append({
                    "famous_id": fid,
                    "famous_name": fname,
                    "genfunc_sig": sig,
                    "n_partners": len(partners),
                    "partners": partners[:10],
                    "same_char_poly": [
                        s for s in partners
                        if genfunc_results[s]["char_poly_sig"] == genfunc_results[fid]["char_poly_sig"]
                    ][:5],
                    "diff_char_poly": [
                        s for s in partners
                        if genfunc_results[s]["char_poly_sig"] != genfunc_results[fid]["char_poly_sig"]
                    ][:5],
                })

    print(f"  Famous sequences sharing GF with others: {len(famous_matches)}")
    for fm in famous_matches:
        same = len(fm["same_char_poly"])
        diff = len(fm["diff_char_poly"])
        print(f"    {fm['famous_id']} ({fm['famous_name']}): {fm['n_partners']} partners ({same} same recurrence, {diff}+ different)")

    # ── Step 7b: Denominator-only clustering (mod numerator scaling) ──────
    print("\n[7b] Denominator-only clustering (detecting sequences with same Q_red) ...")
    denom_clusters = defaultdict(list)
    for sid, info in genfunc_results.items():
        denom_clusters[info["Q_red_str"]].append(sid)

    multi_denom = {d: sids for d, sids in denom_clusters.items() if len(sids) > 1}
    print(f"  Denominator clusters with 2+ members: {len(multi_denom)}")

    # Cross-recurrence via denominator: same reduced Q but different original Q
    denom_cross = []
    denom_cross_genuine = []  # Genuinely different minimal recurrences
    for denom_str, sids in multi_denom.items():
        char_polys_here = set(genfunc_results[s]["char_poly_sig"] for s in sids)
        min_char_polys_here = set(genfunc_results[s]["min_char_poly_sig"] for s in sids)
        degrees_here = set(genfunc_results[s]["degree"] for s in sids)
        if len(char_polys_here) > 1 or len(degrees_here) > 1:
            entry = {
                "Q_red": denom_str,
                "n_sequences": len(sids),
                "n_char_polys": len(char_polys_here),
                "n_min_char_polys": len(min_char_polys_here),
                "n_degrees": len(degrees_here),
                "degrees": sorted(degrees_here),
                "sequences": sids[:15],
                "char_polys": list(char_polys_here)[:10],
                "min_char_polys": list(min_char_polys_here)[:10],
            }
            denom_cross.append(entry)
            if len(min_char_polys_here) > 1:
                denom_cross_genuine.append(entry)

    print(f"  Cross-recurrence denominator matches: {len(denom_cross)}")
    print(f"  GENUINE cross-recurrence (different minimal char poly): {len(denom_cross_genuine)}")
    for dc in sorted(denom_cross, key=lambda x: -x["n_sequences"])[:5]:
        print(f"    Q_red={dc['Q_red'][:50]} : {dc['n_sequences']} seqs, {dc['n_min_char_polys']} minimal char polys")
    print(f"  Genuine cross-recurrence examples:")
    for dc in sorted(denom_cross_genuine, key=lambda x: -x["n_sequences"])[:10]:
        print(f"    Q_red={dc['Q_red'][:50]} : {dc['n_sequences']} seqs, {dc['n_min_char_polys']} minimal char polys")
        for mcp in dc["min_char_polys"][:5]:
            print(f"      {mcp}")

    # ── Step 7b2: Collatz via denominator ─────────────────────────────────
    # The Collatz denominator is (1-x^2)^2 = 1 - 2x^2 + x^4
    # After reduction, some members reduce to (1-x^2) or (1-x) or even 1
    collatz_denom_dist = Counter()
    for sid in collatz_ids:
        if sid in genfunc_results:
            collatz_denom_dist[genfunc_results[sid]["Q_red_str"]] += 1
    print(f"\n  Collatz denominator distribution after reduction:")
    for q, cnt in collatz_denom_dist.most_common(10):
        print(f"    {q}: {cnt}")
        # Check how many non-Collatz share this denominator
        if q in denom_clusters:
            outside = [s for s in denom_clusters[q] if s not in collatz_ids]
            if outside:
                print(f"      -> {len(outside)} non-Collatz sequences share this denominator")

    # ── Step 7b3: Mod-p test on top denominator cross-matches ──────────────
    print("\n  Mod-p fingerprint test on denominator cross-matches ...")
    denom_modp_results = []
    for dc in sorted(denom_cross, key=lambda x: -x["n_sequences"])[:20]:
        sids = dc["sequences"]
        for p in [2, 3, 5]:
            fps = {}
            for sid in sids:
                if sid in oeis:
                    fps[sid] = mod_p_fingerprint(oeis[sid], p, length=30)
            if len(fps) >= 2:
                fp_groups = defaultdict(list)
                for sid, fp in fps.items():
                    fp_groups[fp].append(sid)
                shared = {k: v for k, v in fp_groups.items() if len(v) > 1}
                # Check if shared groups span different char polys
                for fp_val, fp_sids in shared.items():
                    char_polys_in = set(genfunc_results[s]["char_poly_sig"] for s in fp_sids if s in genfunc_results)
                    if len(char_polys_in) > 1:
                        denom_modp_results.append({
                            "Q_red": dc["Q_red"][:60],
                            "prime": p,
                            "n_seqs_sharing_fp": len(fp_sids),
                            "n_char_polys": len(char_polys_in),
                            "example_seqs": fp_sids[:5],
                            "fingerprint": str(fp_val[:10]),
                        })
    print(f"  Cross-char-poly mod-p matches: {len(denom_modp_results)}")
    for mr in denom_modp_results[:5]:
        print(f"    Q_red={mr['Q_red'][:40]} mod {mr['prime']}: {mr['n_seqs_sharing_fp']} seqs, {mr['n_char_polys']} char polys")

    # ── Step 7c: Reduction analysis — how much did GCD cancel? ─────────────
    print("\n[7c] Reduction analysis (GCD cancellation statistics) ...")
    reduced_count = 0
    degree_reductions = Counter()
    for sid, info in genfunc_results.items():
        q_orig_deg = info.get("degree", 0)
        # Parse Q_red degree from the string — count 'x' powers
        q_red_str = info["Q_red_str"]
        if q_red_str == "1":
            q_red_deg = 0
        else:
            try:
                q_red_poly = Poly(q_red_str, x, domain='QQ')
                q_red_deg = q_red_poly.degree()
            except Exception:
                q_red_deg = q_orig_deg
        if q_red_deg < q_orig_deg:
            reduced_count += 1
            degree_reductions[(q_orig_deg, q_red_deg)] += 1

    print(f"  Sequences with GCD reduction: {reduced_count} / {len(genfunc_results)}")
    print(f"  Degree reductions (orig -> red): count")
    for (d_orig, d_red), cnt in sorted(degree_reductions.items(), key=lambda x: -x[1])[:15]:
        print(f"    {d_orig} -> {d_red}: {cnt}")

    # ── Step 8: Build top cross-recurrence examples ────────────────────────
    print("\n[8] Top cross-recurrence examples ...")
    top_cross = sorted(cross_matches, key=lambda x: -x["n_sequences"])[:25]
    detailed_cross = []
    for cm in top_cross:
        detail = {
            "genfunc_sig": cm["genfunc_sig"],
            "n_sequences": cm["n_sequences"],
            "n_char_polys": cm["n_distinct_char_polys"],
            "char_polys": cm["char_polys"],
            "sequences_by_char_poly": {},
        }
        for cp in cm["char_polys"]:
            sids_with_cp = [s for s in cm["sequences"] if genfunc_results[s]["char_poly_sig"] == cp]
            detail["sequences_by_char_poly"][cp] = sids_with_cp[:5]
        detailed_cross.append(detail)
        if len(detailed_cross) <= 5:
            print(f"    GF: {cm['genfunc_sig'][:60]}")
            for cp, sids in detail["sequences_by_char_poly"].items():
                print(f"      {cp}: {sids[:3]}")

    # ── Compile results ───────────────────────────────────────────────────
    elapsed = time.time() - t0
    print(f"\n{'=' * 72}")
    print(f"COMPLETED in {elapsed:.1f}s")
    print(f"{'=' * 72}")

    results = {
        "challenge": "R3-8",
        "title": "Generating Function Isomorphism — Cross-Recurrence Identity Detection",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "sequences_processed": processed,
            "skipped": dict(skipped),
            "genfunc_clusters": n_gf_clusters,
            "char_poly_clusters": n_char_clusters,
            "compression_ratio": round(n_char_clusters / max(1, n_gf_clusters), 4),
            "multi_member_gf_clusters": len(multi_gf),
            "cross_recurrence_matches": len(cross_matches),
            "modp_shared_fingerprints": len(modp_results),
            "elapsed_seconds": round(elapsed, 1),
        },
        "collatz_analysis": {
            "members_with_gf": collatz_in_results,
            "distinct_reduced_gf": len(collatz_distinct_gf),
            "gf_group_sizes": sorted([len(v) for v in collatz_gf_groups.values()], reverse=True),
            "gf_shared_with_outsiders": len(collatz_outsiders),
            "outsider_examples": {
                sig[:80]: {
                    "collatz_members": [s for s in gf_clusters[sig] if s in collatz_ids][:5],
                    "outside_members": outsiders[:5],
                }
                for sig, outsiders in list(collatz_outsiders.items())[:10]
            },
        },
        "denominator_cross_matches": sorted(denom_cross, key=lambda x: -x["n_sequences"])[:30],
        "genuine_cross_recurrence_matches": sorted(denom_cross_genuine, key=lambda x: -x["n_sequences"])[:30],
        "n_genuine_cross_recurrence": len(denom_cross_genuine),
        "collatz_denominator_distribution": dict(collatz_denom_dist),
        "denom_modp_cross_results": denom_modp_results[:30],
        "reduction_stats": {
            "sequences_with_gcd_reduction": reduced_count,
            "total_sequences": len(genfunc_results),
            "reduction_rate": round(reduced_count / max(1, len(genfunc_results)), 4),
            "degree_reductions": {f"{d_orig}->{d_red}": cnt for (d_orig, d_red), cnt in sorted(degree_reductions.items(), key=lambda x: -x[1])[:20]},
        },
        "cross_recurrence_examples": detailed_cross,
        "famous_sequence_matches": famous_matches,
        "modp_fingerprint_results": modp_results[:30],
        "largest_gf_clusters": [
            {
                "genfunc_sig": sig,
                "size": len(sids),
                "sequences": sids[:20],
                "n_char_polys": len(set(genfunc_results[s]["char_poly_sig"] for s in sids)),
            }
            for sig, sids in sorted(multi_gf.items(), key=lambda x: -len(x[1]))[:30]
        ],
    }

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")

    # Print summary
    print(f"\n{'-' * 72}")
    print("SUMMARY")
    print(f"{'-' * 72}")
    print(f"  Sequences processed:          {processed}")
    print(f"  Generating function clusters:  {n_gf_clusters}")
    print(f"  Recurrence clusters:           {n_char_clusters}")
    print(f"  Compression (char/gf):         {n_char_clusters / max(1, n_gf_clusters):.3f}")
    print(f"  Cross-recurrence matches:      {len(cross_matches)}")
    print(f"  Collatz distinct GFs:          {len(collatz_distinct_gf)}")
    print(f"  Collatz GFs shared outside:    {len(collatz_outsiders)}")
    print(f"  Famous seq GF partners:        {len(famous_matches)}")
    print(f"  Denominator cross-matches:     {len(denom_cross)}")
    print(f"  Genuine cross-recurrence:      {len(denom_cross_genuine)}")
    print(f"  GCD reductions:                {reduced_count}")


if __name__ == "__main__":
    main()
