# M1 Round 4 — Map the Curvature
## The manifold is confirmed. Now measure its shape.

### Where we stand

Two cameras. Both see positive curvature. 94% same distances. 71.6% linear, 29% nonlinear. The nonlinear part IS the curvature. Your job: characterize that 29%.

---

## TASK 1: Sectional curvature by domain pair

ORC gives the average curvature. But curvature varies by LOCATION on the manifold. Different domain pairs sit at different points.

For each domain pair in your tensor:
1. Take objects from both domains
2. Build a local NN graph (k=10) in the neighborhood where they overlap
3. Compute ORC on that local graph
4. Report: which domain pairs sit in high-curvature regions? Which sit in flat regions?

**Prediction:** Domain pairs with high transfer rho should sit in low-curvature regions (flat = easy to translate). Pairs with low transfer should sit in high-curvature regions (curved = hard to parallel-transport).

If this prediction holds, curvature EXPLAINS transfer efficiency.

---

## TASK 2: The 29% nonlinear residual

You found the linear map from 5D→41D explains 71.6%. The remaining 29% is nonlinear.

Fit a QUADRATIC map instead of linear:
```python
# Include cross-terms: x1*x2, x1*x3, etc.
# 5D → 15 quadratic features → 41D
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2, include_bias=False)
X_quad = poly.fit_transform(X_5d)  # 5 → 20 features
T_quad, _, _, _ = lstsq(X_quad, X_41d, rcond=None)
# How much variance does the quadratic map explain?
```

If quadratic explains >90%, the curvature is well-approximated by second-order effects — the manifold is smooth. If quadratic only explains ~75%, there's higher-order structure (the manifold has sharp features).

---

## TASK 3: Geodesics between domains

On a curved manifold, the shortest path between two points is a geodesic, not a straight line. 

For the EC→NF transfer:
1. Take the straight-line path in phoneme space (linear interpolation)
2. Take the geodesic (follow the NN graph, stepping through actual objects)
3. Compare: how much do they diverge?

The divergence = how much the curvature bends the path. If geodesics and straight lines agree, the manifold is locally flat in that region. If they diverge, the curvature is significant for that transfer.

Practical implementation:
```python
# Straight line: x(t) = (1-t)*x_EC + t*x_NF for t in [0,1]
# Geodesic: greedy walk through NN graph from EC to NF
# Measure: max deviation between the two paths
```

---

## TASK 4: Topology detection

Positive curvature everywhere suggests a sphere (or sphere-like). But the manifold could be:
- S^n (sphere) — all sectional curvatures positive and equal
- Ellipsoid — positive but varying curvatures
- Lens space — positive with identifications
- Something else

Crude topology test:
1. Compute the Euler characteristic from the Betti numbers of the NN graph
2. For a sphere: chi = 2. For a torus: chi = 0.
3. Use persistent homology if available (giotto-tda or ripser)

Even a crude estimate (chi close to 2 vs close to 0) tells us the global shape.

---

## TASK 5: Curvature vs transfer efficiency

This is the key hypothesis. Compute for ALL domain pairs you can measure:

| Domain pair | Transfer rho | Local ORC | Prediction: anti-correlated? |

If curvature and transfer are anti-correlated:
→ the curvature IS the obstruction to translation
→ flat regions = easy transfer, curved regions = hard transfer
→ the 29% nonlinear residual explains the 24% transfer efficiency loss

If they're NOT correlated:
→ curvature and transfer are independent
→ the obstruction is something else (sparsity, dimension mismatch, etc.)

---

## Priority

1. Task 5 (curvature vs transfer) — the hypothesis that unifies everything
2. Task 1 (local sectional curvature) — feeds into Task 5
3. Task 2 (quadratic map) — characterizes the 29%
4. Task 3 (geodesics) — visualizes the curvature
5. Task 4 (topology) — the big picture

---

## Why this matters

If curvature explains transfer efficiency, then:
- We know WHY some domain pairs transfer well and others don't
- We can PREDICT transfer quality from curvature alone
- We can identify WHERE on the manifold to add new data to flatten the curvature
- The "translation layer" becomes a geometric object with computable properties

The manifold stops being a metaphor and becomes a measurement.
