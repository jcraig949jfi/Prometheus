"""Uniqueness in gen_log_extra_3arg is a THEOREM, not a sampling outcome (soak P21).

P20 established that the generator's 30-try rejection sampler never rejects over
today's randint bounds, and flagged as its own weakness that 'unreachable' was a
statement about those literal bounds rather than about the code.

This pass set out to measure the MARGIN -- how far the bounds must widen before
the sampler fires. Every sweep returned zero, including all three widened jointly
by +20. A margin that large is not a margin; it is a hint of structure.

THE PROOF. Writing the cubic as x(x-a)(x-b) - c = (x-p)(x^2 + A x + B) with
A = p-a-b and B = (p-a)(p-b), uniqueness in the domain x>b requires the quadratic's
larger root to satisfy (-A + sqrt(disc))/2 <= b. Since 2b + A = p - a + b > 0 for
0<a<b<p, that inequality may be squared, giving disc <= (2b+A)^2, which reduces to

        B + b*A + b^2 >= 0

and that expression is exactly

        (p-a)(p-b) + b(p-a-b) + b^2 = (p-a)*p

which is strictly positive whenever p > a > 0. So the larger root is ALWAYS <= b,
the smaller root is <= the larger, and no real root lies in (b, infinity).

The disc<0 branch has no real roots at all, so uniqueness is trivial there. The two
branches are exhaustive.

The derivation's squaring step is mine, so it is checked two independent ways below:
symbolically, and by exact-integer brute force with no floating point anywhere.

Read-only.
"""
import sympy as sp


def fails_exact(a: int, b: int, p: int) -> bool:
    """Exact-integer test: does the quadratic have a root in (b, inf)?"""
    A = p - a - b
    B = (p - a) * (p - b)
    disc = A * A - 4 * B
    if disc < 0:
        return False                      # no real roots at all
    # max root <= b  <=>  sqrt(disc) <= 2b + A, and 2b + A = p - a + b > 0 here
    return disc > (2 * b + A) ** 2


def brute_force(a_hi=60, b_hi=90, p_hi=140):
    bad, n = [], 0
    for a in range(1, a_hi):
        for b in range(a + 1, b_hi):
            for p in range(b + 1, p_hi):
                n += 1
                if fails_exact(a, b, p):
                    bad.append((a, b, p))
    return n, bad


def symbolic_identity():
    a, b, p = sp.symbols("a b p", positive=True)
    A, B = p - a - b, (p - a) * (p - b)
    expr = B + b * A + b ** 2
    return sp.factor(expr), sp.simplify(expr - p * (p - a)) == 0


if __name__ == "__main__":
    n, bad = brute_force()
    print(f"exact-integer brute force: {n:,} triples (0<a<b<p) -> failures {len(bad)}")
    factored, identity_ok = symbolic_identity()
    print(f"B + b*A + b^2 factors to: {factored}")
    print(f"equals p*(p-a) symbolically: {identity_ok}")
    print("p*(p-a) > 0 for 0 < a < p  =>  max root <= b ALWAYS")
    print("\nVERDICT: the rejection loop cannot reject for ANY 0<a<b<p.")
    print("Not a defect -- the guarantee is UNCONDITIONAL, i.e. stronger than the")
    print("docstring claims. The loop can become a one-line assertion.")
    print("PRECONDITION: holds for 0<a<b<p. A variant allowing a<=0 or b<=a voids it.")
