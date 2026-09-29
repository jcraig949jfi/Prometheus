"""Deep block, Block A: adversarial edge cases for the E-002 proposal C-OP' (implemented from E-002 RESULT.md text; the worker did not
code C-OP' itself). Units are abstract heritable positions; a parent is a tuple of unit states; the child records, per unit, the parent
the operator copied it from (FLOW) and the resulting state.
C-OP' (as proposed): (1) collapse identical contributors (self-cross -> single parent); (2) exclude inert units (a == b at the unit);
(3) exchangeable operator: ILL_POSED unless the difference-making share clears the operator null Binomial(nd, 1/2) at alpha (two-sided);
then the majority contributor; (4) privileged operator: fall back to the declared rule (MAJORITY over factual shares);
(5) any unit with unknown provenance among difference-making units -> NOT_IDENTIFIABLE."""
import json
import math


def p2(k, n):
    pk = math.comb(n, k)
    return min(1.0, sum(math.comb(n, j) for j in range(n + 1) if math.comb(n, j) <= pk) / 2 ** n)


def cop_prime(a, b, flow, alpha=0.005, exchangeable=True):
    if a == b: return {"answer": "a(=b) single parent", "nd": 0}
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    if any(flow[i] is None for i in diff): return {"answer": "NOT_IDENTIFIABLE", "nd": len(diff)}
    k = sum(1 for i in diff if flow[i] == "a"); nd = len(diff)
    if not exchangeable:
        tot = len(a); fa = sum(1 for f in flow if f == "a")
        return {"answer": "a" if fa > tot / 2 else ("b" if fa < tot / 2 else "ILL_POSED"), "nd": nd, "k": k, "rule": "privileged fallback MAJORITY(flow)"}
    p = p2(k, nd)
    return {"answer": ("a" if k > nd / 2 else "b") if p < alpha else "ILL_POSED", "nd": nd, "k": k, "p": round(p, 5)}


def case(name, a, b, flow, note, **kw):
    r = cop_prime(a, b, flow, **kw)
    child = tuple(a[i] if f == "a" else b[i] for i, f in enumerate(flow)) if all(f in ("a", "b") for f in flow) else None
    r.update({"case": name, "child_equals_a": child == a if child else None, "flow_share_a": round(sum(f == "a" for f in flow) / len(flow), 3), "note": note})
    return r


def main():
    n = 16; A = tuple(range(n)); B_far = tuple(100 + i for i in range(n))
    B_near = tuple(A[i] if i >= 3 else 200 + i for i in range(n))            # differs from A at 3 units
    B_one = tuple(A[i] if i != 0 else 999 for i in range(n))                   # differs at 1 unit
    out = [
        case("E1 exact copy of a, parents far apart", A, B_far, ["a"] * n, "child == a; nd = 16"),
        case("E1b exact copy of a, parents CLOSE (nd=3)", A, B_near, ["a"] * n, "child == a exactly, yet nd = 3 can never clear alpha"),
        case("E2 self-cross", A, A, ["a"] * 8 + ["b"] * 8, "one parent"),
        case("E3 asymmetric operator, 9/16 from a", A, B_far, ["a"] * 9 + ["b"] * 7, "privileged operator: C-OP' falls back to MAJORITY", exchangeable=False),
        case("E3b asymmetric operator, 'departure from null' misapplied", A, B_far, ["a"] * 14 + ["b"] * 2,
             "if the operator gives a 90% on average, a 14/16 child is TYPICAL; the unbiased-null test in (b) calls it decided, a null "
             "at p_a = 0.9 would call it indistinguishable; (b) has no defined null for privileged operators"),
        case("E4 flow of identical material dominates", A, B_one, ["a"] + ["b"] * 15, "15/16 units copied from b but only the 1 differing unit counts; the child is a"),
        case("E5 narrow margin: 12/16 distinguishing units from a", A, B_far, ["a"] * 12 + ["b"] * 4, "child carries 75% of a's distinguishing material"),
        case("E5b 13/16", A, B_far, ["a"] * 13 + ["b"] * 3, "one unit more"),
        case("E6 missing provenance at a differing unit", A, B_far, ["a"] * 15 + [None], "evidence incomplete"),
    ]
    # E7 neutral differences: phenotype reads only units 0..3; parents differ at all 16
    expressed = range(4)
    flow = ["a"] * 4 + ["b"] * 12
    r = case("E7 parents differ materially, only 4 units expressed", A, B_far, flow, "child's phenotype is exactly a's (all expressed units from a); material 12/16 from b")
    r["phenotype_equals_a"] = all(flow[i] == "a" for i in expressed); out.append(r)
    for r in out: print(json.dumps(r))
    return out


if __name__ == "__main__":
    main()
