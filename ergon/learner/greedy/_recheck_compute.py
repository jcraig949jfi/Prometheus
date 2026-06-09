"""Independent gold re-check of compute_trace.jsonl (no import of the builder)."""
import json, math, re, sys
import sympy
path = sys.argv[1] if len(sys.argv) > 1 else "F:/Prometheus/ergon/learner/greedy/corpus/compute_trace.jsonl"
rows = [json.loads(l) for l in open(path, encoding="utf-8")]
checks = {"gcd": 0, "phi": 0, "sigma": 0, "dcount": 0, "binom": 0, "modexp": 0}
bad = []
for r in rows:
    p, g = r["prompt"], r["gold_bool"]
    m = re.match(r"Claim: gcd\((\d+), (\d+)\) = (\d+)\.", p)
    if m:
        a, b, v = map(int, m.groups()); checks["gcd"] += 1
        if (math.gcd(a, b) == v) != g: bad.append(("gcd", p, g))
    m = re.match(r"Claim: Euler's totient .\((\d+)\) = (\d+)\.", p)
    if m:
        n, v = map(int, m.groups()); checks["phi"] += 1
        if (int(sympy.totient(n)) == v) != g: bad.append(("phi", p, g))
    m = re.match(r"Claim: sum of divisors .\((\d+)\) = (\d+)\.", p)
    if m:
        n, v = map(int, m.groups()); checks["sigma"] += 1
        if (int(sympy.divisor_sigma(n)) == v) != g: bad.append(("sigma", p, g))
    m = re.match(r"Claim: number of divisors d\((\d+)\) = (\d+)\.", p)
    if m:
        n, v = map(int, m.groups()); checks["dcount"] += 1
        if (int(sympy.divisor_count(n)) == v) != g: bad.append(("dcount", p, g))
    m = re.match(r"Claim: the binomial coefficient C\((\d+), (\d+)\) = (\d+)\.", p)
    if m:
        n, k, v = map(int, m.groups()); checks["binom"] += 1
        if (math.comb(n, k) == v) != g: bad.append(("binom", p, g))
    m = re.match(r"Claim: (\d+)\^(\d+) mod (\d+) = (\d+)\.", p)
    if m:
        a, b, mod, v = map(int, m.groups()); checks["modexp"] += 1
        if (pow(a, b, mod) == v) != g: bad.append(("modexp", p, g))
print("rows:", len(rows), "true:", sum(r["gold_bool"] for r in rows))
print("checks:", checks, "total checked:", sum(checks.values()))
print("MISMATCHES:", len(bad))
for b in bad[:10]:
    print("  ", b)
