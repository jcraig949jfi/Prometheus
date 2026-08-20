"""Which parts of P21's precondition are actually necessary? (soak P22)

P21 proved the rejection loop in gen_log_extra_3arg is dead, and attached the
precondition 0<a<b<p, warning that allowing a<=0 or b<=a would put the loop back
in play. SOAK-45 argued the precondition is the artifact a maintainer acts on --
so an overstated one marks safe edits as dangerous and leaves the real risk
unmarked.

Both halves of that warning are wrong:

    a==0            0 violations
    a<0             0 violations
    b<=a            0 violations
    p<=b            VIOLATIONS

And no simple ordering is sufficient either -- p>b AND p>0 AND p>a still leaves
violations, e.g. (a,b,p)=(-8,-15,1), where p-a+b = -6 < 0 makes the proof's
squaring step invalid.

The true frontier is the proof's own pair:  p-a+b > 0  AND  p(p-a) > 0.
0<a<b<p is SUFFICIENT (it implies both) and far from necessary.

Read-only. Exact integer arithmetic, no floats.
"""

def no_root_above_b(a: int, b: int, p: int) -> bool:
    """Exact: is the quadratic cofactor free of real roots strictly above b?"""
    A = p - a - b
    B = (p - a) * (p - b)
    disc = A * A - 4 * B
    if disc < 0:
        return True                      # no real roots at all
    s = 2 * b + A                        # need sqrt(disc) <= s
    if s < 0:
        return False                     # some root exceeds b
    return disc <= s * s


def scan(pred, label, rng=range(-15, 30)):
    tested, bad = 0, []
    for a in rng:
        for b in rng:
            for p in rng:
                if not pred(a, b, p):
                    continue
                tested += 1
                if not no_root_above_b(a, b, p):
                    bad.append((a, b, p))
    note = f"  e.g. {bad[:2]}" if bad else ""
    print(f"  {label:38s} tested {tested:>7,}  violations {len(bad):>6}{note}")
    return bad


if __name__ == "__main__":
    print("relaxing each clause of P21's stated precondition:\n")
    scan(lambda a, b, p: 0 < a < b < p, "BASELINE 0<a<b<p")
    scan(lambda a, b, p: a == 0 and 0 < b < p, "a==0  (P21 said this voids it)")
    scan(lambda a, b, p: a < 0 < b < p, "a<0   (P21 said this voids it)")
    scan(lambda a, b, p: 0 < b <= a < p, "b<=a  (P21 said this voids it)")
    scan(lambda a, b, p: 0 < a < b and 0 < p <= b, "p<=b")

    print("\nis any simple ordering sufficient?\n")
    scan(lambda a, b, p: p > b, "p>b alone")
    scan(lambda a, b, p: p > b and p > 0 and p > a, "p>b AND p>0 AND p>a")

    print("\nthe proof's own conditions:\n")
    scan(lambda a, b, p: (p - a + b) > 0 and p * (p - a) > 0, "p-a+b>0 AND p(p-a)>0")
    print("\n=> 0<a<b<p is SUFFICIENT, not necessary. Widening a is free;")
    print("   letting p fall to or below b is the edit that matters.")
    print("   Separately: if a>b were allowed, p>b no longer puts p inside")
    print("   the log domain x>max(a,b) -- a different failure from this one.")
