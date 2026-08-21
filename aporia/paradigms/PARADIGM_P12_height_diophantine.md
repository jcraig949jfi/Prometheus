# PARADIGM P12 — Height and Diophantine Geometry (worked example + decision tree + code skeleton)

Aporia P86, 2026-08-21. Source: taxonomy P12; DR grounding 00051 (uniform
bounded heights frontier — OPENED and key points read: Dimitrov-Gao-Habegger
rank-uniform bounds; Uniform Mordell-Lang via Gao-Ge-Kuhne; explicitization
push via Arakelov). Consumer: Learner corpus type C. Emitted to
paradigm_trees.jsonl.

**The move**: assign arithmetic SIZE to points; finiteness and structure follow
from how height grows (verb: MEASURE-ARITHMETIC-SIZE; payoff verb:
BOUND-THE-INFINITE-BY-GROWTH-RATES).

## 1. Worked example — EXECUTED (`paradigm_p12_worked_example.py`)

The height machine's signature: on 37a1 (smallest rank-1 conductor), multiples
of the generator P=(0,0) computed in EXACT rational arithmetic (full
Weierstrass chord-tangent law with the a1/a3 terms carried — dropping them is
the classic trap), on-curve invariant asserted at every step, group law gated
on a longhand tangent construction (2P=(1,0)).

Result: naive height h(nP) grows quadratically — log-log exponent **2.0083**
(n=5..24), h(nP)/n² converging (last-3 spread 1.1%) to **ĥ(P) ≈ 0.0510** —
the canonical height EMERGING from arithmetic rather than being asserted.
Verdict: **HEIGHT-QUADRATIC**. By n=24 the x-coordinate has ~13-digit
numerator: the exponential explosion of point sizes IS the finiteness
engine (only finitely many points fit under any height bound).

## 2. Decision tree

- Q1: Are the objects POINTS (or cycles) on an arithmetic variety where a
  height function exists (Weil machine, canonical, Faltings)? — NO: heights
  measure arithmetic size; purely analytic/combinatorial objects need other
  paradigms.
- Q1 YES — Q2: Does the question reduce to a HEIGHT BOUND (finiteness =
  bounded height + Northcott; equidistribution = height limits)? — NO: height
  is bookkeeping here, not leverage; exit.
- Q2 YES — Q3: Is the height COMPUTABLE for your instances (exact arithmetic
  or certified approximation)? — NO: the paradigm's frontier (explicit
  Arakelov constants, per report 00051) is exactly this gap; record as typed
  residue.
- Q3 YES — EXECUTE: compute heights with an on-variety invariant gate at
  every arithmetic step; growth exponents FITTED, not assumed; a canonical
  height quoted without its convergence trace is a transcription.

## 3. Code skeleton

```python
def height_attack(gen, add_law, on_variety, height_fn, n_max=24):
    """P12 template. Every arithmetic step gated on-variety; growth exponent
    fitted from the trace; the ratio sequence IS the canonical object."""
    cur, hs = None, []
    for n in range(1, n_max + 1):
        cur = add_law(cur, gen)
        assert on_variety(cur), f"step {n} left the variety — law fault"
        hs.append(height_fn(cur))
    ratios = [h / (i + 1) ** 2 for i, h in enumerate(hs)]
    return {"heights": hs, "hhat_trace": ratios,
            "converged": abs(ratios[-1] - ratios[-2]) / ratios[-1] < 0.02}
```

## 4. Catalog assignment

Primary: CAT-MATH-0026/0193 (uniformity IS this paradigm — report 00051 maps
its 2021-26 frontier), 0136 (abc is a height inequality), 0143 (Bombieri-Lang),
0505 (Morton-Silverman — dynamical heights, conditional per 00051). Secondary:
0063 (regulator = height pairing determinant). Anti-assignment: 0060/0062/0370
(zeros have no arithmetic height), 0137 (congruence checks).

## Provenance and honesty

The quadratic growth is Néron-Tate theory; the content is the exact-arithmetic
instrument (Fractions, invariant-gated law, longhand gate) and ĥ emerging from
a convergence trace rather than a table. The grounding report was opened this
pass (the P84 shortcut retired) and its frontier map is folded into Q3 and the
0026/0193 assignment note.
