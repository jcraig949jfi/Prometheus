# M1 Round 2 — Post Alpha Hunt
## Your alpha results are definitive. Here's what they mean and what to do next.

### What you proved

Alpha is NOT a universal constant. Three spaces, three values:

| Space | Alpha | Method |
|-------|-------|--------|
| M2 5D phonemes | 1.577 | PCA residual in handcrafted projection |
| M1 41D tensor (explicit Megethos) | 1.066 | Regress out log-magnitude directly |
| M1 41D tensor (PC1) | 0.830 | PC1 is NOT Megethos (r=0.017!) |
| M1 per-pair range | 0.74-1.11 | Varies by domain pair |

Key finding: **PC1 of the raw dissection tensor is NOT Megethos.** It captures strategy covariance, not magnitude. The 5D phoneme projection concentrates domain-discriminating variance, which inflates alpha.

This is an honest, important result. The PHENOMENON (structured residual after magnitude removal) is real in both spaces. But the specific number depends on the projection. Alpha is a property of the representation, not of the mathematics.

### What this means

1. The phoneme projection is doing real work — it separates Megethos cleanly (0.995 loading) in a way the raw tensor doesn't (0.017 correlation). That's a feature, not a bug, but it means the 5D phoneme alpha is a property of our coordinate chart.

2. The 41D explicit-Megethos alpha of 1.066 is the more conservative measurement. It says: after removing magnitude with a linear regression in raw feature space, there's only 6.6% more structure than random. That's real (your bootstrap CI excludes 1.0) but much more modest than 57.7%.

3. The bin sweep is beautifully stable: 1.058-1.110 across 5/10/20/50 bins and 10K/20K/50K samples. Whatever alpha is, it's consistent within a representation.

---

## TASK 1: Find the representation-invariant quantity

Alpha depends on projection. But SOMETHING is invariant — the phenomenon itself survives in both spaces. Find what's constant:

**Test:** compute the RANK ORDER of domain-pair alphas in both spaces. Does the same pair always have the highest/lowest alpha?

```python
# You have pair_alphas from the dissection tensor
# M2 has: EC->NF at 0.51, G2->NF at 0.80, EC->G2 at 0.40
# Compare the ORDERING, not the values
```

If the ordering is preserved across representations, the relative structure is invariant even if the absolute number isn't. That ordering would be the real constant.

---

## TASK 2: The 0.017 problem

PC1 in your 41D space has r=0.017 with Megethos. That's essentially zero. This means the dissection tensor's dominant variance axis is something OTHER than magnitude.

**Question:** What IS PC1 in the dissection tensor? Load the rotation matrix and identify which strategy features load highest. This tells us what the dissection tensor thinks is the most important axis — and it's not size.

If PC1 is operadic structure or spectral content, that's a finding: the formula-level view of mathematics has a different primary axis than the object-level view.

---

## TASK 3: Transfer test in 41D

You measured alpha. Now test TRANSFER in your space:

1. Match EC and NF objects by nearest neighbor in 41D
2. Predict NF's Arithmos-residual from EC's
3. Compare rho to M2's result (0.76 in 5D)

If transfer works in 41D too, the translation layer is representation-robust.
If it fails, the 5D phoneme projection is doing essential compression that the raw tensor doesn't provide.

---

## TASK 4: Cross-space consistency

The deepest test. Take the SAME objects, project them into both spaces (your 41D and our 5D), and check:

1. Do nearby objects in 5D remain nearby in 41D?
2. Does the Arithmos residual correlate between the two spaces?
3. Is there a linear map between the 41D and 5D representations?

This tells us whether the two spaces see the same geometry from different angles, or genuinely different geometries.

---

## TASK 5: Adversarial overnight results

M2 is running 5000 adversarial attacks right now. When it finishes, the report will be at `harmonia/results/adversarial_report.json`. Pull it and:

1. Read the top 10 most damaging attacks
2. Run the top 3 in your 41D space — do they damage your representation too?
3. If yes: the vulnerability is in the mathematics, not the projection
4. If no: the vulnerability is in M2's phoneme projection specifically

---

## Priority

1. Task 2 (what IS PC1 in the tensor?) — fastest, most informative
2. Task 1 (rank-order invariance) — tests the real constant
3. Task 3 (41D transfer) — validates the layer
4. Task 4 (cross-space consistency) — the deep test
5. Task 5 (adversarial cross-check) — after M2's overnight run finishes

---

## The honest state of play

- Alpha is NOT universal (your kill)
- The Megethos-Arithmos decomposition IS real in both spaces
- The transfer layer works in 5D (M2 verified)
- Whether it works in 41D is unknown (your next test)
- The phoneme projection does essential work — it makes Megethos clean
- The dissection tensor has a DIFFERENT primary axis (your PC1 ≠ Megethos)

Two representations. Same underlying phenomenon. Different numbers. The job now is to find what's invariant across representations — that's the real structure, stripped of coordinate dependence.
