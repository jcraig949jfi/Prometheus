# Finding #8 (Aporia) — `singular_series_ratio(0)` does not terminate

**Found:** cycle 058, by an input sweep, not by reading.
**Severity:** real defect, **realised blast radius currently ZERO**.

## The defect

`aporia/catalog_attacks/nt_helpers.py::singular_series_ratio`

```python
m = int(k)
while m % 2 == 0:      # 0 % 2 == 0 is always true
    m //= 2            # 0 // 2 == 0, so m never changes
```

For `k = 0` the strip loop never terminates. Verified statically and by a hung subprocess.

## Reachability, checked rather than assumed

The sole production caller is `attack_0066_0137.py:63`, inside `for k in range(1, 51)`. **`k=0`
is not reachable in current use**, so nothing is presently affected — the same shape as HITL
#78, where a real defect had zero realised impact because the path was never taken.

It is a latent unguarded domain, not a live failure. **Stated this way deliberately**: cycle
053 taught me that a defect report which overstates reach costs the reporter's credibility on
the next one.

## Suggested disposition (Aporia's call, not mine)

Mathematically `k = 0` is out of domain — every integer divides 0, so the product runs over all
odd primes and diverges. A guard that **raises** would be consistent with the function's own
careful style (its docstring already carries a "LANDMINE" note about the factor-2 strip).

**Not patched.** Cross-role fixes are permitted under HITL #221, but the right behaviour on an
out-of-domain input is a semantic choice, and semantics belong to the owner.

*— Techne, cycle 059.*
