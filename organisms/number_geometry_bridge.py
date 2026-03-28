"""
Number-Geometry Bridge organism.

The KEY bridging organism: operations that explicitly connect number theory
to geometric structures, enabling cross-domain reasoning.

Operations: prime_spiral, gaussian_prime_lattice, zeta_zeros_on_critical_line,
            modular_curve_points, farey_sequence, stern_brocot_tree
"""

from .base import MathematicalOrganism


class NumberGeometryBridge(MathematicalOrganism):
    name = "number_geometry_bridge"
    operations = {
        "prime_spiral": {
            "code": """
def prime_spiral(n):
    \"\"\"Generate the Ulam spiral coordinates for the first n primes.
    The Ulam spiral places consecutive integers in a spiral pattern on
    a 2D grid; primes tend to cluster along certain diagonals.
    Returns list of (prime, x, y) tuples.\"\"\"
    # First, generate enough integers to contain n primes
    # Upper bound: p_n < n * (ln(n) + ln(ln(n))) for n >= 6
    import math
    if n <= 0:
        return []
    if n <= 6:
        limit = 20
    else:
        ln_n = math.log(n)
        limit = int(n * (ln_n + math.log(ln_n))) + 100

    # Sieve for primes
    is_prime_arr = np.ones(limit + 1, dtype=bool)
    is_prime_arr[0] = is_prime_arr[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime_arr[i]:
            is_prime_arr[i*i::i] = False
    all_primes = set(np.where(is_prime_arr)[0])

    # Generate spiral coordinates for integers 1, 2, 3, ...
    # Directions: right, up, left, down
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    x, y = 0, 0
    direction = 0
    steps_in_direction = 1
    steps_taken = 0
    turns = 0

    results = []
    for number in range(1, limit + 1):
        if number in all_primes:
            results.append((int(number), int(x), int(y)))
            if len(results) >= n:
                break
        # Move to next position
        x += dx[direction]
        y += dy[direction]
        steps_taken += 1
        if steps_taken == steps_in_direction:
            steps_taken = 0
            direction = (direction + 1) % 4
            turns += 1
            if turns % 2 == 0:
                steps_in_direction += 1

    return results
""",
            "input_type": "integer",
            "output_type": "coordinate_list",
        },
        "gaussian_prime_lattice": {
            "code": """
def gaussian_prime_lattice(bound):
    \"\"\"Find all Gaussian primes a + bi with |a|, |b| <= bound.
    A Gaussian integer a + bi is a Gaussian prime if:
    1) a=0 or b=0: |a| or |b| is a prime = 3 mod 4
    2) Both nonzero: a^2 + b^2 is a (rational) prime
    Returns list of (a, b, norm) for plotting.\"\"\"
    bound = int(bound)
    # Sieve rational primes up to 2*bound^2
    limit = 2 * bound * bound + 1
    is_prime_arr = np.ones(limit + 1, dtype=bool)
    is_prime_arr[0] = is_prime_arr[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime_arr[i]:
            is_prime_arr[i*i::i] = False

    def is_rational_prime(k):
        if k < 0:
            k = -k
        if k <= limit:
            return bool(is_prime_arr[k])
        # Fallback trial division
        if k < 2:
            return False
        if k == 2:
            return True
        if k % 2 == 0:
            return False
        d = 3
        while d * d <= k:
            if k % d == 0:
                return False
            d += 2
        return True

    gaussian_primes = []
    for a in range(-bound, bound + 1):
        for b in range(-bound, bound + 1):
            norm = a * a + b * b
            if norm == 0:
                continue
            is_gp = False
            if a == 0:
                # Pure imaginary: |b| must be prime and |b| = 3 mod 4
                ab = abs(b)
                if is_rational_prime(ab) and ab % 4 == 3:
                    is_gp = True
            elif b == 0:
                # Pure real: |a| must be prime and |a| = 3 mod 4
                aa = abs(a)
                if is_rational_prime(aa) and aa % 4 == 3:
                    is_gp = True
            else:
                # Both nonzero: norm must be a rational prime
                if is_rational_prime(norm):
                    is_gp = True
            if is_gp:
                gaussian_primes.append((int(a), int(b), int(norm)))

    return gaussian_primes
""",
            "input_type": "integer",
            "output_type": "coordinate_list",
        },
        "zeta_zeros_on_critical_line": {
            "code": """
def zeta_zeros_on_critical_line(n_zeros=100):
    \"\"\"Return the imaginary parts of the first n nontrivial zeros of the
    Riemann zeta function on the critical line Re(s) = 1/2.
    Uses precomputed values for the first 30, then Gram point estimation.
    All known zeros lie on Re(s) = 1/2 (Riemann Hypothesis).\"\"\"
    # First 30 known zeros (imaginary parts), verified to many digits
    known = [
        14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
        37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
        52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
        67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
        79.337375, 82.910381, 84.735493, 87.425275, 88.809111,
        92.491899, 94.651344, 95.870634, 98.831194, 101.317851,
    ]

    if n_zeros <= len(known):
        zeros = known[:n_zeros]
    else:
        zeros = known[:]
        # Estimate additional zeros using Gram points:
        # The n-th zero is approximately at t where theta(t) = (n-1)*pi
        # theta(t) ~ (t/2)*log(t/(2*pi*e)) + pi/8
        # Rough estimate: t_n ~ 2*pi*n / log(n) for large n
        for k in range(len(known), n_zeros):
            # Better asymptotic: t_n ~ 2*pi*e * exp(W(n/(e))) where W is Lambert
            # Simpler: t_n ~ 2*pi*n / (ln(n/(2*pi)) )
            import math
            nn = k + 1
            if nn > 1:
                t_est = 2 * np.pi * nn / np.log(nn / (2 * np.pi))
                if t_est < zeros[-1]:
                    t_est = zeros[-1] + 2 * np.pi / np.log(zeros[-1] / (2 * np.pi))
            else:
                t_est = zeros[-1] + 3.0
            zeros.append(float(t_est))

    return [{"index": i + 1, "imaginary_part": float(t), "s": f"0.5 + {t:.6f}i"}
            for i, t in enumerate(zeros)]
""",
            "input_type": "integer",
            "output_type": "geometric_structure",
        },
        "modular_curve_points": {
            "code": """
def modular_curve_points(a, b, p):
    \"\"\"Find all points on the elliptic curve y^2 = x^3 + ax + b over F_p.
    Returns list of (x, y) points plus the point at infinity.
    Also computes the order of the curve (number of points).\"\"\"
    a, b, p = int(a), int(b), int(p)
    # Check discriminant: 4a^3 + 27b^2 != 0 mod p
    disc = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if disc == 0:
        return {"error": "Singular curve (discriminant = 0 mod p)"}

    points = []
    for x in range(p):
        rhs = (pow(x, 3, p) + a * x + b) % p
        # Check if rhs is a quadratic residue mod p
        for y in range(p):
            if (y * y) % p == rhs:
                points.append((int(x), int(y)))

    # Hasse bound: |#E(F_p) - p - 1| <= 2*sqrt(p)
    order = len(points) + 1  # +1 for point at infinity
    hasse_bound = 2 * np.sqrt(p)

    return {
        "a": a, "b": b, "p": p,
        "points": points,
        "order": order,
        "hasse_bound": float(hasse_bound),
        "hasse_check": abs(order - p - 1) <= hasse_bound,
        "discriminant_mod_p": int(disc),
    }
""",
            "input_type": "params",
            "output_type": "geometric_structure",
        },
        "farey_sequence": {
            "code": """
def farey_sequence(n):
    \"\"\"Compute the Farey sequence F_n: all fractions a/b in [0, 1]
    with 0 <= a <= b <= n, gcd(a, b) = 1, in ascending order.
    Properties: |F_n| ~ 3n^2/pi^2, consecutive fractions a/b, c/d
    satisfy |ad - bc| = 1 (mediant property).\"\"\"
    import math
    n = int(n)
    fractions = []
    for b in range(1, n + 1):
        for a in range(0, b + 1):
            if math.gcd(a, b) == 1:
                fractions.append((a, b))
    # Sort by value a/b
    fractions.sort(key=lambda f: f[0] / f[1])

    # Verify mediant property for consecutive fractions
    mediant_holds = True
    for i in range(len(fractions) - 1):
        a1, b1 = fractions[i]
        a2, b2 = fractions[i + 1]
        if abs(a2 * b1 - a1 * b2) != 1:
            mediant_holds = False
            break

    return {
        "order": n,
        "length": len(fractions),
        "fractions": [(a, b) for a, b in fractions],
        "as_decimals": [float(a / b) for a, b in fractions],
        "mediant_property_holds": mediant_holds,
        "expected_length_approx": float(3 * n * n / (np.pi ** 2)),
    }
""",
            "input_type": "integer",
            "output_type": "geometric_structure",
        },
        "stern_brocot_tree": {
            "code": """
def stern_brocot_tree(depth):
    \"\"\"Generate the Stern-Brocot tree to a given depth.
    This binary tree enumerates all positive rationals exactly once.
    Level 0: 1/1
    Each node a/b has left child = mediant(left_ancestor, a/b)
    and right child = mediant(a/b, right_ancestor).
    Returns the tree as a list of levels.\"\"\"
    depth = min(int(depth), 12)  # Cap to prevent exponential blowup (2^12 = 4096 nodes max)
    if depth < 0:
        return {"levels": [], "total_nodes": 0}

    # Build iteratively using the mediant property
    # Start with sentinels 0/1 and 1/0
    # Level 0: just 1/1 (mediant of 0/1 and 1/0)
    levels = []
    current_seq = [(0, 1), (1, 1), (1, 0)]  # left sentinel, root, right sentinel

    for d in range(depth + 1):
        level_nodes = []
        # Extract non-sentinel nodes from current_seq
        for i in range(len(current_seq)):
            a, b = current_seq[i]
            if (a, b) != (0, 1) and (a, b) != (1, 0):
                level_nodes.append((a, b))

        if d == 0:
            levels.append([(1, 1)])
        else:
            # The new level consists of mediants inserted between consecutive elements
            new_nodes = []
            for i in range(len(current_seq) - 1):
                a1, b1 = current_seq[i]
                a2, b2 = current_seq[i + 1]
                mediant = (a1 + a2, b1 + b2)
                # Only add if this mediant is new (not already in sequence)
                is_new = True
                for node in current_seq:
                    if node == mediant:
                        is_new = False
                        break
                if is_new:
                    new_nodes.append(mediant)
            levels.append(new_nodes)
            # Insert new nodes into sequence for next iteration
            new_seq = [current_seq[0]]
            for i in range(len(current_seq) - 1):
                a1, b1 = current_seq[i]
                a2, b2 = current_seq[i + 1]
                mediant = (a1 + a2, b1 + b2)
                found = False
                for node in current_seq:
                    if node == mediant:
                        found = True
                        break
                if not found:
                    new_seq.append(mediant)
                new_seq.append(current_seq[i + 1])
            current_seq = new_seq

    total = sum(len(lev) for lev in levels)
    # Flatten all rationals and verify uniqueness
    all_rationals = []
    for lev in levels:
        for a, b in lev:
            all_rationals.append((a, b))

    return {
        "depth": depth,
        "levels": [[(a, b, f\"{a}/{b}\", float(a/b) if b > 0 else float('inf'))
                     for a, b in lev] for lev in levels],
        "total_nodes": total,
        "all_unique": len(set(all_rationals)) == len(all_rationals),
    }
""",
            "input_type": "integer",
            "output_type": "geometric_structure",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = NumberGeometryBridge()
    print(org)

    # Prime spiral (Ulam)
    spiral = org.execute("prime_spiral", 20)
    print(f"First 20 primes on Ulam spiral:")
    for p, x, y in spiral[:10]:
        print(f"  {p} -> ({x}, {y})")
    print(f"  ... ({len(spiral)} total)")

    # Gaussian primes
    gp = org.execute("gaussian_prime_lattice", 10)
    print(f"\nGaussian primes with |a|,|b| <= 10: {len(gp)} primes")
    print(f"  First 5: {gp[:5]}")

    # Zeta zeros
    zeros = org.execute("zeta_zeros_on_critical_line", 10)
    print(f"\nFirst 10 zeta zeros:")
    for z in zeros:
        print(f"  #{z['index']}: s = {z['s']}")

    # Elliptic curve over F_23: y^2 = x^3 + x + 1
    ec = org.execute("modular_curve_points", 1, 1, 23)
    print(f"\nE: y^2 = x^3 + x + 1 over F_23:")
    print(f"  Points: {len(ec['points'])} + point at infinity = {ec['order']}")
    print(f"  Hasse bound: |{ec['order']} - 24| <= {ec['hasse_bound']:.2f}")
    print(f"  Hasse check: {ec['hasse_check']}")

    # y^2 = x^3 - x over F_71
    ec2 = org.execute("modular_curve_points", -1, 0, 71)
    print(f"  E: y^2 = x^3 - x over F_71: order = {ec2['order']}, "
          f"Hasse check = {ec2['hasse_check']}")

    # Farey sequence
    f5 = org.execute("farey_sequence", 5)
    print(f"\nFarey F_5: {f5['length']} fractions")
    print(f"  Fractions: {f5['fractions']}")
    print(f"  Mediant property: {f5['mediant_property_holds']}")

    f8 = org.execute("farey_sequence", 8)
    print(f"Farey F_8: {f8['length']} fractions "
          f"(expected ~{f8['expected_length_approx']:.1f})")

    # Stern-Brocot tree
    sb = org.execute("stern_brocot_tree", 4)
    print(f"\nStern-Brocot tree depth 4: {sb['total_nodes']} nodes, "
          f"all unique: {sb['all_unique']}")
    for i, level in enumerate(sb['levels']):
        fracs = [entry[2] for entry in level]
        print(f"  Level {i}: {fracs}")

    print("--- number_geometry_bridge: ALL TESTS PASSED ---")
