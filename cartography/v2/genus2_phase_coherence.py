#!/usr/bin/env python3
"""
F5: Genus-2 Frobenius Phase Coherence.

For genus-2 curves, extract the PHASES (arguments) of Frobenius eigenvalues
from the characteristic polynomial x^4 - a_p*x^3 + b_p*x^2 - a_p*p*x + p^2.

Compute phases at primes p=3,5,7,...,97.  Measure phase coherence via
mean resultant length R = |mean(exp(i*theta_p))| across primes for each curve.
R=1 means perfect coherence, R~0 means uniformly distributed phases.

Test: Does R correlate with Sato-Tate group? With conductor?
"""

import json
import ast
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "cartography" / "lmfdb_dump" / "g2c_curves.json"
OUT_PATH = Path(__file__).resolve().parent / "genus2_phase_coherence_results.json"

PRIMES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97]


# ── point counting over F_p ───────────────────────────────────────────────

def parse_equation(eqn_str):
    """Parse LMFDB equation string '[[f_coeffs],[h_coeffs]]' into (f, h).

    Hyperelliptic model: y^2 + h(x)*y = f(x)
    f_coeffs = [a0, a1, ..., an] meaning f(x) = a0 + a1*x + ... + an*x^n
    h_coeffs = [b0, b1, ...] meaning h(x) = b0 + b1*x + ...
    """
    if isinstance(eqn_str, str):
        parts = ast.literal_eval(eqn_str)
    else:
        parts = eqn_str
    f_coeffs = parts[0]
    h_coeffs = parts[1] if len(parts) > 1 else []
    return f_coeffs, h_coeffs


def eval_poly_mod(coeffs, x, p):
    """Evaluate polynomial with given coefficients at x mod p.
    coeffs = [a0, a1, ..., an] for a0 + a1*x + ... + an*x^n.
    """
    val = 0
    xpow = 1
    for c in coeffs:
        val = (val + c * xpow) % p
        xpow = (xpow * x) % p
    return val


def count_points_Fp(f_coeffs, h_coeffs, p):
    """Count #C(F_p) for y^2 + h(x)*y = f(x), including point(s) at infinity.

    For each x in F_p, we solve y^2 + h(x)*y - f(x) = 0 mod p.
    Number of solutions: discriminant D = h(x)^2 + 4*f(x).
    If p=2, handle separately.

    For genus 2 (deg f = 5 or 6):
      - if deg f = 5 (odd): 1 point at infinity
      - if deg f = 6 (even): 0 or 2 points at infinity depending on leading coeff
    """
    count = 0

    for x in range(p):
        fx = eval_poly_mod(f_coeffs, x, p)
        hx = eval_poly_mod(h_coeffs, x, p) if h_coeffs else 0

        if p == 2:
            # Solve y^2 + hx*y - fx = 0 mod 2
            for y in range(2):
                if (y * y + hx * y - fx) % 2 == 0:
                    count += 1
        else:
            # Discriminant D = hx^2 + 4*fx mod p
            D = (hx * hx + 4 * fx) % p
            if D == 0:
                count += 1  # one solution
            else:
                # Euler criterion: D^((p-1)/2) mod p
                leg = pow(D, (p - 1) // 2, p)
                if leg == 1:
                    count += 2  # two solutions
                # else 0 solutions

    # Points at infinity
    deg_f = len(f_coeffs) - 1 if f_coeffs else 0
    deg_h = len(h_coeffs) - 1 if h_coeffs else -1

    # Remove trailing zeros to get true degree
    while deg_f >= 0 and f_coeffs[deg_f] == 0:
        deg_f -= 1
    while deg_h >= 0 and h_coeffs and h_coeffs[deg_h] == 0:
        deg_h -= 1

    if deg_f == 5:
        # Odd degree model: 1 point at infinity
        count += 1
    elif deg_f == 6:
        # Even degree: check if leading coeff of f is a QR mod p
        lead_f = f_coeffs[6] % p if len(f_coeffs) > 6 else f_coeffs[-1] % p
        # For y^2 + h(x)y = f(x), at infinity we need to check more carefully
        # but for simplified model y^2 = f(x), it's about whether f_6 is QR
        if p == 2:
            count += 2  # simplification
        else:
            # Full analysis: at infinity, discriminant of y^2 + h_deg*y - f_lead
            h_lead = h_coeffs[deg_h] % p if deg_h >= 0 and h_coeffs else 0
            # Two "points at infinity" directions, need to check each
            # For the standard LMFDB model, simplify:
            D_inf = (h_lead * h_lead + 4 * lead_f) % p
            if D_inf == 0:
                count += 1
            elif pow(D_inf, (p - 1) // 2, p) == 1:
                count += 2

    return count


def count_points_Fp2(f_coeffs, h_coeffs, p):
    """Count #C(F_{p^2}) by working in GF(p^2) = F_p[t]/(t^2 - nr)
    where nr is a fixed non-residue mod p.

    Elements represented as (a, b) meaning a + b*t.
    """
    if p == 2:
        # GF(4) = F_2[t]/(t^2+t+1)
        return _count_Fp2_char2(f_coeffs, h_coeffs)

    # Find a non-residue mod p
    nr = 2
    while pow(nr, (p - 1) // 2, p) != p - 1:
        nr += 1

    # Precompute all elements of F_{p^2}
    # Element (a,b) represents a + b*sqrt(nr)
    # Multiplication: (a1+b1*s)(a2+b2*s) = (a1*a2 + b1*b2*nr) + (a1*b2 + a2*b1)*s

    count = 0

    for xa in range(p):
        for xb in range(p):
            # Evaluate f(x) and h(x) in F_{p^2}
            fx_a, fx_b = _eval_poly_Fp2(f_coeffs, xa, xb, p, nr)
            if h_coeffs:
                hx_a, hx_b = _eval_poly_Fp2(h_coeffs, xa, xb, p, nr)
            else:
                hx_a, hx_b = 0, 0

            # Solve y^2 + h(x)*y - f(x) = 0 in F_{p^2}
            # Discriminant D = h(x)^2 + 4*f(x) in F_{p^2}
            h2_a = (hx_a * hx_a + hx_b * hx_b * nr) % p
            h2_b = (2 * hx_a * hx_b) % p
            D_a = (h2_a + 4 * fx_a) % p
            D_b = (h2_b + 4 * fx_b) % p

            # Check if D is a square in F_{p^2}
            # Every element of F_{p^2} is a square (since p^2-1 is even and
            # the squaring map is 2-to-1), EXCEPT 0 maps to 0
            # Actually: #squares in F_{p^2}* = (p^2-1)/2
            # An element d in F_{p^2}* is a square iff d^((p^2-1)/2) = 1
            # But (p^2-1)/2 = (p-1)(p+1)/2

            if D_a == 0 and D_b == 0:
                count += 1  # D=0, one solution
            else:
                # Compute D^((p^2-1)/2) in F_{p^2}
                exp = (p * p - 1) // 2
                res_a, res_b = _pow_Fp2(D_a, D_b, exp, p, nr)
                if res_a == 1 and res_b == 0:
                    count += 2
                # else 0 solutions

    # Points at infinity (same logic but over F_{p^2})
    deg_f = len(f_coeffs) - 1 if f_coeffs else 0
    while deg_f >= 0 and f_coeffs[deg_f] == 0:
        deg_f -= 1

    if deg_f == 5:
        count += 1
    elif deg_f == 6:
        lead_f = f_coeffs[-1] % p
        deg_h = len(h_coeffs) - 1 if h_coeffs else -1
        while deg_h >= 0 and h_coeffs[deg_h] == 0:
            deg_h -= 1
        h_lead = h_coeffs[deg_h] % p if deg_h >= 0 and h_coeffs else 0
        D_inf = (h_lead * h_lead + 4 * lead_f) % p
        # D_inf is in F_p subset of F_{p^2}, always a square in F_{p^2} if nonzero
        # (since F_p* elements that are non-squares in F_p become squares in F_{p^2})
        if D_inf == 0:
            count += 1
        else:
            count += 2  # always a square in F_{p^2}

    return count


def _eval_poly_Fp2(coeffs, xa, xb, p, nr):
    """Evaluate polynomial at (xa, xb) in F_{p^2} = F_p[sqrt(nr)]."""
    val_a, val_b = 0, 0
    pow_a, pow_b = 1, 0  # x^0 = 1
    for c in coeffs:
        val_a = (val_a + c * pow_a) % p
        val_b = (val_b + c * pow_b) % p
        # multiply power by x
        new_a = (pow_a * xa + pow_b * xb * nr) % p
        new_b = (pow_a * xb + pow_b * xa) % p
        pow_a, pow_b = new_a, new_b
    return val_a, val_b


def _pow_Fp2(a, b, exp, p, nr):
    """Compute (a + b*sqrt(nr))^exp in F_{p^2} via repeated squaring."""
    res_a, res_b = 1, 0
    base_a, base_b = a % p, b % p
    while exp > 0:
        if exp & 1:
            # res *= base
            new_a = (res_a * base_a + res_b * base_b * nr) % p
            new_b = (res_a * base_b + res_b * base_a) % p
            res_a, res_b = new_a, new_b
        # base *= base
        new_a = (base_a * base_a + base_b * base_b * nr) % p
        new_b = (2 * base_a * base_b) % p
        base_a, base_b = new_a, new_b
        exp >>= 1
    return res_a, res_b


def _count_Fp2_char2(f_coeffs, h_coeffs):
    """Count points over GF(4) for p=2.
    GF(4) = {0, 1, w, w+1} where w^2 + w + 1 = 0.
    Elements as (a, b) meaning a + b*w, arithmetic mod 2 with w^2 = w + 1.
    """
    count = 0
    elements = [(a, b) for a in range(2) for b in range(2)]

    for xa, xb in elements:
        fx_a, fx_b = _eval_poly_GF4(f_coeffs, xa, xb)
        hx_a, hx_b = _eval_poly_GF4(h_coeffs, xa, xb) if h_coeffs else (0, 0)

        # Solve y^2 + h(x)*y = f(x) in GF(4)
        # In char 2: y^2 + hx*y + fx = 0  (since -1=1)
        for ya, yb in elements:
            # y^2 in GF(4): (a+bw)^2 = a^2 + b^2*w^2 = a + b*(w+1) = (a+b) + b*w  (mod 2)
            y2_a = (ya + yb) % 2
            y2_b = yb
            # hx * y
            hy_a = (hx_a * ya + hx_b * yb) % 2  # real part (with w^2=w+1)
            hy_b = (hx_a * yb + hx_b * ya + hx_b * yb) % 2
            # y^2 + hx*y + fx
            res_a = (y2_a + hy_a + fx_a) % 2
            res_b = (y2_b + hy_b + fx_b) % 2
            if res_a == 0 and res_b == 0:
                count += 1

    # Infinity points for GF(4) - simplified
    deg_f = len(f_coeffs) - 1 if f_coeffs else 0
    while deg_f >= 0 and f_coeffs[deg_f] == 0:
        deg_f -= 1
    if deg_f == 5:
        count += 1
    elif deg_f == 6:
        count += 2  # both infinite points rational over GF(4)

    return count


def _eval_poly_GF4(coeffs, xa, xb):
    """Evaluate polynomial at (xa, xb) in GF(4) = F_2[w]/(w^2+w+1)."""
    val_a, val_b = 0, 0
    pow_a, pow_b = 1, 0
    for c in coeffs:
        c2 = c % 2
        val_a = (val_a + c2 * pow_a) % 2
        val_b = (val_b + c2 * pow_b) % 2
        # multiply power by x:  (pa+pb*w)(xa+xb*w)
        # = pa*xa + (pa*xb+pb*xa)*w + pb*xb*w^2
        # = pa*xa + pb*xb + (pa*xb + pb*xa + pb*xb)*w   [since w^2=w+1]
        new_a = (pow_a * xa + pow_b * xb) % 2
        new_b = (pow_a * xb + pow_b * xa + pow_b * xb) % 2
        pow_a, pow_b = new_a, new_b
    return val_a, val_b


# ── Frobenius phases ──────────────────────────────────────────────────────

def frobenius_phases(s1, s2, p):
    """Given s1=a_p, s2=b_p, compute the 4 phases of Frobenius eigenvalues.

    Char poly: T^4 - s1*T^3 + s2*T^2 - s1*p*T + p^2
    Eigenvalues have |alpha| = sqrt(p), so alpha = sqrt(p) * exp(i*theta).
    """
    coeffs = [p * p, -s1 * p, s2, -s1, 1]  # ascending order for np.roots: need descending
    poly = [1, -s1, s2, -s1 * p, p * p]
    roots = np.roots(poly)

    phases = np.angle(roots)
    # Normalize to [0, 2*pi)
    phases = phases % (2 * np.pi)
    # Sort
    phases = np.sort(phases)
    return phases


def mean_resultant_length(phases_list):
    """Compute R = |mean(exp(i*theta))| across a list of phase values.

    We use the FIRST phase from each prime (the one closest to 0) as representative,
    but also compute R for all 4 phases.
    """
    if not phases_list:
        return 0.0

    # Use all phases flattened
    all_phases = np.array(phases_list).flatten()
    R_all = np.abs(np.mean(np.exp(1j * all_phases)))

    # Use only the first (smallest) phase per prime
    first_phases = np.array([ph[0] for ph in phases_list if len(ph) > 0])
    R_first = np.abs(np.mean(np.exp(1j * first_phases))) if len(first_phases) > 0 else 0.0

    return R_all, R_first


def phase_spread(phases_list):
    """Circular standard deviation of the first phase across primes."""
    if not phases_list:
        return np.nan
    first_phases = np.array([ph[0] for ph in phases_list if len(ph) > 0])
    if len(first_phases) == 0:
        return np.nan
    R = np.abs(np.mean(np.exp(1j * first_phases)))
    # Circular std dev = sqrt(-2 * ln(R))
    if R > 0:
        return np.sqrt(-2 * np.log(R))
    return np.inf


# ── main ──────────────────────────────────────────────────────────────────

def main():
    print("Loading genus-2 curves...")
    with open(DATA_PATH) as f:
        data = json.load(f)

    records = data["records"]
    print(f"  Total records: {len(records)}")

    # Sample 1000 curves, stratified by Sato-Tate group
    # First, see what ST groups we have
    st_groups = defaultdict(list)
    for i, rec in enumerate(records):
        st = rec.get("st_group", "unknown")
        st_groups[st].append(i)

    print(f"  Sato-Tate groups found: {sorted(st_groups.keys())}")
    for st, indices in sorted(st_groups.items(), key=lambda x: -len(x[1])):
        print(f"    {st}: {len(indices)} curves")

    # Sample up to 1000 total, proportional to group size
    np.random.seed(42)
    total_to_sample = 1000
    sampled_indices = []

    # Ensure at least 1 from each group, then proportional
    remaining = total_to_sample
    for st, indices in st_groups.items():
        n = max(1, int(len(indices) / len(records) * total_to_sample))
        n = min(n, len(indices), remaining)
        chosen = np.random.choice(indices, size=n, replace=False)
        sampled_indices.extend(chosen.tolist())
        remaining -= n

    # If we still have room, fill from largest group
    if remaining > 0:
        largest_st = max(st_groups.items(), key=lambda x: len(x[1]))[0]
        already = set(sampled_indices)
        candidates = [i for i in st_groups[largest_st] if i not in already]
        extra = np.random.choice(candidates, size=min(remaining, len(candidates)), replace=False)
        sampled_indices.extend(extra.tolist())

    sampled_indices = sorted(set(sampled_indices))[:total_to_sample]
    print(f"  Sampled {len(sampled_indices)} curves")

    # Process each curve
    results = []
    n_done = 0
    n_failed = 0

    for idx in sampled_indices:
        rec = records[idx]
        label = rec.get("label", f"idx_{idx}")
        eqn = rec.get("eqn")
        if eqn is None:
            n_failed += 1
            continue

        f_coeffs, h_coeffs = parse_equation(eqn)
        bad_primes_raw = rec.get("bad_primes", [])
        if isinstance(bad_primes_raw, str):
            bad_primes = set(ast.literal_eval(bad_primes_raw))
        else:
            bad_primes = set(bad_primes_raw)

        st_group = rec.get("st_group", "unknown")
        cond = rec.get("cond", None)
        analytic_rank = rec.get("analytic_rank", None)

        phases_by_prime = []
        s1s2_by_prime = {}
        good_primes_used = []

        for p in PRIMES:
            if p in bad_primes:
                continue

            try:
                N1 = count_points_Fp(f_coeffs, h_coeffs, p)
                s1 = p + 1 - N1  # a_p

                # For small p, count over F_{p^2} to get s2 = b_p
                if p <= 47:  # F_{p^2} has p^2 elements, manageable up to ~47
                    N2 = count_points_Fp2(f_coeffs, h_coeffs, p)
                    s2 = (s1 * s1 - (p * p + 1 - N2)) // 2
                else:
                    # For larger p, F_{p^2} counting is expensive
                    # Use only s1 and estimate: s2 ~ s1^2/2 or use Weil bound
                    # Better: just skip b_p and use the factorization approach
                    N2 = count_points_Fp2(f_coeffs, h_coeffs, p)
                    s2 = (s1 * s1 - (p * p + 1 - N2)) // 2

                # Verify Weil bounds: |s1| <= 4*sqrt(p), |s2| <= 6*p
                if abs(s1) > 4 * np.sqrt(p) + 1:
                    continue  # point count error

                # Get phases
                phases = frobenius_phases(s1, s2, p)
                phases_by_prime.append(phases)
                s1s2_by_prime[str(p)] = {"s1": int(s1), "s2": int(s2),
                                          "N1": int(N1), "N2": int(N2)}
                good_primes_used.append(p)

            except Exception as e:
                continue

        if len(phases_by_prime) < 3:
            n_failed += 1
            continue

        R_all, R_first = mean_resultant_length(phases_by_prime)
        circ_std = phase_spread(phases_by_prime)

        # Also compute phase coherence between PAIRS of phases
        # The 4 roots come in conjugate pairs: theta, -theta, phi, -phi (mod 2pi)
        # So we really have 2 independent phases per prime
        # Extract the two "positive" phases (in [0, pi])
        pos_phases = []
        for phases in phases_by_prime:
            # phases in [0, 2pi), sorted. Conjugate structure means
            # if theta is a phase, 2pi-theta is too. So group them.
            in_upper = phases[phases <= np.pi]
            if len(in_upper) >= 1:
                pos_phases.append(in_upper[0])

        R_pos = np.abs(np.mean(np.exp(1j * np.array(pos_phases)))) if pos_phases else 0.0

        result = {
            "label": label,
            "st_group": st_group,
            "conductor": cond,
            "analytic_rank": analytic_rank,
            "n_good_primes": len(good_primes_used),
            "good_primes": good_primes_used,
            "R_all": float(R_all),
            "R_first": float(R_first),
            "R_positive_phase": float(R_pos),
            "circular_std": float(circ_std) if not np.isinf(circ_std) else None,
            "euler_data": s1s2_by_prime,
        }
        results.append(result)
        n_done += 1

        if n_done % 100 == 0:
            print(f"  Processed {n_done}/{len(sampled_indices)} curves...")

    print(f"  Done: {n_done} succeeded, {n_failed} failed")

    # ── Analysis ──────────────────────────────────────────────────────────
    print("\n=== ANALYSIS ===\n")

    # 1. R by Sato-Tate group
    st_R = defaultdict(list)
    st_R_pos = defaultdict(list)
    for r in results:
        st_R[r["st_group"]].append(r["R_all"])
        st_R_pos[r["st_group"]].append(r["R_positive_phase"])

    st_summary = {}
    print("R_all by Sato-Tate group:")
    for st in sorted(st_R.keys()):
        vals = np.array(st_R[st])
        vals_pos = np.array(st_R_pos[st])
        summary = {
            "n": len(vals),
            "R_all_mean": float(np.mean(vals)),
            "R_all_std": float(np.std(vals)),
            "R_all_median": float(np.median(vals)),
            "R_pos_mean": float(np.mean(vals_pos)),
            "R_pos_std": float(np.std(vals_pos)),
        }
        st_summary[st] = summary
        print(f"  {st:20s}: n={summary['n']:4d}  R_all={summary['R_all_mean']:.4f}±{summary['R_all_std']:.4f}  "
              f"R_pos={summary['R_pos_mean']:.4f}±{summary['R_pos_std']:.4f}")

    # 2. R vs conductor (Spearman correlation)
    conductors = np.array([r["conductor"] for r in results if r["conductor"] is not None])
    R_vals = np.array([r["R_all"] for r in results if r["conductor"] is not None])
    R_pos_vals = np.array([r["R_positive_phase"] for r in results if r["conductor"] is not None])

    from scipy import stats as sp_stats

    rho_cond, p_cond = sp_stats.spearmanr(conductors, R_vals)
    rho_cond_pos, p_cond_pos = sp_stats.spearmanr(conductors, R_pos_vals)
    print(f"\nR_all vs conductor:  Spearman rho={rho_cond:.4f}, p={p_cond:.2e}")
    print(f"R_pos vs conductor:  Spearman rho={rho_cond_pos:.4f}, p={p_cond_pos:.2e}")

    # 3. R vs log(conductor)
    log_cond = np.log(conductors.astype(float))
    rho_logc, p_logc = sp_stats.spearmanr(log_cond, R_vals)
    print(f"R_all vs log(cond):  Spearman rho={rho_logc:.4f}, p={p_logc:.2e}")

    # 4. R vs analytic rank
    ranks = np.array([r["analytic_rank"] for r in results if r["analytic_rank"] is not None])
    R_by_rank_vals = np.array([r["R_all"] for r in results if r["analytic_rank"] is not None])

    rank_groups = defaultdict(list)
    for r in results:
        if r["analytic_rank"] is not None:
            rank_groups[r["analytic_rank"]].append(r["R_all"])

    print(f"\nR_all by analytic rank:")
    rank_summary = {}
    for rk in sorted(rank_groups.keys()):
        vals = np.array(rank_groups[rk])
        rank_summary[str(rk)] = {
            "n": len(vals),
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
        }
        print(f"  rank {rk}: n={len(vals):4d}  R_all={np.mean(vals):.4f}±{np.std(vals):.4f}")

    if len(ranks) > 10:
        rho_rank, p_rank = sp_stats.spearmanr(ranks, R_by_rank_vals)
        print(f"  Spearman rho={rho_rank:.4f}, p={p_rank:.2e}")
    else:
        rho_rank, p_rank = None, None

    # 5. ANOVA: does ST group predict R?
    st_groups_for_anova = [np.array(st_R[st]) for st in sorted(st_R.keys()) if len(st_R[st]) >= 5]
    if len(st_groups_for_anova) >= 2:
        F_stat, p_anova = sp_stats.f_oneway(*st_groups_for_anova)
        print(f"\nANOVA (ST group -> R_all): F={F_stat:.2f}, p={p_anova:.2e}")
    else:
        F_stat, p_anova = None, None

    # 6. Kruskal-Wallis (non-parametric)
    if len(st_groups_for_anova) >= 2:
        H_stat, p_kw = sp_stats.kruskal(*st_groups_for_anova)
        print(f"Kruskal-Wallis (ST group -> R_all): H={H_stat:.2f}, p={p_kw:.2e}")
    else:
        H_stat, p_kw = None, None

    # 7. Null model: what R do we expect for random phases?
    n_primes_typical = int(np.median([r["n_good_primes"] for r in results]))
    null_R = []
    for _ in range(10000):
        random_phases = np.random.uniform(0, 2 * np.pi, size=(n_primes_typical, 4))
        null_R.append(np.abs(np.mean(np.exp(1j * random_phases.flatten()))))
    null_R = np.array(null_R)
    print(f"\nNull model (random phases, {n_primes_typical} primes x 4 phases):")
    print(f"  R_null: mean={np.mean(null_R):.4f}, std={np.std(null_R):.4f}, "
          f"95th={np.percentile(null_R, 95):.4f}")

    observed_mean_R = np.mean(R_vals)
    print(f"  Observed R_all: mean={observed_mean_R:.4f}")
    z_vs_null = (observed_mean_R - np.mean(null_R)) / np.std(null_R)
    print(f"  z-score vs null: {z_vs_null:.2f}")

    # ── Output ────────────────────────────────────────────────────────────
    output = {
        "problem": "F5: Genus-2 Frobenius Phase Coherence",
        "timestamp": datetime.now().isoformat(),
        "n_curves": len(results),
        "primes_used": PRIMES,
        "summary": {
            "by_st_group": st_summary,
            "by_rank": rank_summary,
            "R_vs_conductor": {
                "spearman_rho": float(rho_cond),
                "p_value": float(p_cond),
            },
            "R_vs_log_conductor": {
                "spearman_rho": float(rho_logc),
                "p_value": float(p_logc),
            },
            "R_vs_rank": {
                "spearman_rho": float(rho_rank) if rho_rank is not None else None,
                "p_value": float(p_rank) if p_rank is not None else None,
            },
            "anova_st_group": {
                "F_statistic": float(F_stat) if F_stat is not None else None,
                "p_value": float(p_anova) if p_anova is not None else None,
            },
            "kruskal_wallis_st_group": {
                "H_statistic": float(H_stat) if H_stat is not None else None,
                "p_value": float(p_kw) if p_kw is not None else None,
            },
            "null_model": {
                "n_primes_typical": n_primes_typical,
                "R_null_mean": float(np.mean(null_R)),
                "R_null_std": float(np.std(null_R)),
                "R_null_95th": float(np.percentile(null_R, 95)),
                "observed_R_all_mean": float(observed_mean_R),
                "z_vs_null": float(z_vs_null),
            },
        },
        "curves": results,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=1)

    print(f"\nResults saved to {OUT_PATH}")
    print(f"Total curves processed: {len(results)}")


if __name__ == "__main__":
    main()
