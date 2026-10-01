"""W2-37: Newcombe (1998) hybrid score interval (method 10) for p1 - p2, two independent proportions; Wilson 95% per arm."""
import math
Z = 1.959963984540054


def wilson(x, n, z=Z):
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def newcombe(x1, n1, x2, n2, z=Z):
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson(x1, n1, z)
    l2, u2 = wilson(x2, n2, z)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return d, lo, hi


def verdict(lo, hi, tol=0.05):
    if lo > -tol and hi < tol:
        return "PASSED"
    if hi < -tol or lo > tol:
        return "KILLED"
    return "UNRESOLVED"


if __name__ == "__main__":
    # Newcombe 1998 Table II example check: 56/70 vs 48/80 -> 0.2000 (0.0524, 0.3339)
    print(newcombe(56, 70, 48, 80))
    print(newcombe(9, 10, 3, 10))  # Newcombe 1998 example: 0.6 (0.1705, 0.8090)
