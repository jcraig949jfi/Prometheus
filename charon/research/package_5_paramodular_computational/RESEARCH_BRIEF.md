# Research Package 5: Paramodular Conjecture — Computational Status
## Priority: HIGH — validates or invalidates our killed hypothesis

---

## Research Question

What is the current state of computational verification of the Paramodular Conjecture (Brumer-Kramer)? What conductor range has been checked? What methods were used? Did anyone use L-function zeros in the verification?

## Context

We found 163 weight-2 dim-2 modular forms with EC-like zero distributions. We tested them against genus-2 curves and the paramodular interpretation was killed — but one council member (Claude) pointed out our test was flawed: we compared degree-2 L-functions (classical MFs) to degree-4 L-functions (genus-2 curves), which is geometrically meaningless. We need to know what the correct test would look like.

## Specific Questions

1. For what range of conductors has the Paramodular Conjecture been computationally verified? Is conductor ≤ 5000 within the verified range?

2. What methods are used to verify paramodular correspondence? Do any involve comparing zero statistics between the paramodular form and the abelian surface?

3. The Jacobian of a genus-2 curve is an abelian surface. Its L-function is degree 4 and sometimes factors as a product of two degree-2 L-functions. When it factors, the factors correspond to elliptic curves (Eichler-Shimura). How common is this factoring at small conductor?

4. For non-simple abelian surfaces (where the Jacobian is isogenous to a product of elliptic curves), the paramodular form should be related to the classical modular forms of the two elliptic curve factors. Is there a computational database of these "decomposable" cases?

5. Recent work by Poor, Yuen, and others on computing paramodular forms — what conductor range have they reached? What L-function data is available for these forms?

## Key Starting Papers
- Brumer, Kramer — "Paramodular abelian varieties of odd conductor" (2019)
- Poor, Yuen — "Paramodular cusp forms" (2015)
- Farmer, Koutsoliotas, Lemurell — "Varieties via their L-functions" (2019)
- Any LMFDB documentation on genus-2 L-function computation methodology
