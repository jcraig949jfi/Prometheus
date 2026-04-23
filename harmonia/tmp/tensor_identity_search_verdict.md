# Tensor Identity Search — MVP Verdict (v2, post-canonicalizer test)

**Author:** Harmonia_M2_sessionA, 2026-04-23
**Context:** James asked for an MVP of all three shapes (gen_12 spec, stoa/ideas doc, 2×2 pilot), then a weighing. v1 of this doc framed the pilot result as "we rediscovered Strassen." James pushed back: the object being searched was mis-specified. A follow-up canonicalizer test confirmed it. This is v2 with the corrected framing.

---

## The finding, stated correctly

On 2×2 matrix multiplication over ℝ:

- A 60-line ALS + multi-restart stack reached Strassen's **orbit** reliably: 6/20 random seeds converged to residual < 1e-8 at rank 7 in 1.4 seconds; 4 seeds hit machine precision (< 1e-10). Theorem: all rank-7 decompositions of 2×2 matmul are `(GL(2) × GL(2) × GL(2)) × S_7 × scale-gauge`-equivalent to Strassen. So all four seeds plus Strassen himself are one mathematical object in five coordinate frames.

- A v1 canonicalizer (scale gauge + sign gauge + permutation lex-sort) produced **five different canonical hashes** for those five decompositions. Integer-fractions: ALS seeds 0.02–0.16, Strassen 1.00.

This is not "we rediscovered Strassen." It is **"orbit-level convergence without canonical representatives."** The search finds the orbit; it does not find the Strassen representative *within* the orbit. The v1 canonicalizer confirms it: the orbit is bigger than scale + sign + permutation, and the missing piece — the T-stabilizer basis change — is where most of its size lives for structured tensors like matmul.

The rank-6 impossibility is also an empirical anchor: 20 seeds at rank 6 produced residuals clustered exactly at 1.000, matching the Winograd 1971 lower bound. That becomes a regression test for any future search primitive (anything reporting residual < 1e-6 at rank 6 has a bug, not a finding).

---

## What each MVP delivered, reassessed

### (a) `docs/prompts/gen_12_tensor_identity_search.md`

**Delivered v0.1** listed orbit equivalence as Gate 2 among four gates — positioning the canonicalizer as *a filter inside the search pipeline*. **Delivered v0.2** (after empirical evidence) reframes the canonicalizer as the pipeline spine: every module — search primitives, MAP-Elites cells, catalog lookup, gates, objectives — sees canonical representatives, not raw factor triples. MVP exit criteria reordered to put canonicalizer v2 first as hard blocker. Rank-6 impossibility promoted to regression test.

**What v0.2 still does not resolve:** whether a v2 canonicalizer is tractable for the 2×2 case, let alone 3×3. That's the next empirical check.

### (b) `stoa/ideas/2026-04-23-sessionA-tensor-identity-search.md`

**Delivered v1** listed six open questions. **Delivered v2** (post-pilot update) retains those questions but sharpens the hinge: "is a v2 canonicalizer tractable for 2×2 matmul first?" replaces "is it tractable at Laderman scale?" — a calibration-first version of the same question. The original discussion is retained unmodified for audit, under a pivot header.

### (c) `harmonia/tmp/tensor_pilot_2x2_matmul.py` + `canonicalize_test.py`

**Delivered:** two empirical artifacts. The pilot found orbit convergence; the canonicalizer test falsified the claim that v1 canonicalization suffices. Together they produced the evidence that drove the spec v0.1 → v0.2 reframe and the `orbit_vs_representative.md` note.

This is falsification-first working as designed. v0.1 framed the architecture incorrectly; the pilot let reality push back inside 2 seconds of compute; v0.2 corrects the architecture. The pre-commit hold that James imposed was the discipline that made the correction possible before it hardened into substrate.

### (d — new) `harmonia/memory/architecture/orbit_vs_representative.md`

**Delivered v0.1:** substrate-primitive spec for the canonicalizer. Defines the symmetry group (scale + sign + permutation + T-stabilizer GL), scopes v1 (shipped, empirically insufficient) vs v2 (pending), and pins the hash contract (invariance, separation, tolerance, cheap, versioned). Calibration anchor defined in terms of the 2×2 pilot, not in terms of future Laderman work.

---

## The question under the original question — refined

James's push sharpened the finding:

> Search is easy; representation is the problem.

This reframes the whole direction. It is not *"build a search stack + orbit filter."* It is *"build an orbit-class substrate whose representative-finding is what the search instrument produces."* The search primitives (GA, MAP-Elites, ALS, structured integer) are cheap; the load-bearing infrastructure is the canonicalizer (and its hash contract), which quotients the cover down to the base space we actually care about.

This has a cleaner Prometheus shape than v0.1. It is a **coordinate-systems-of-legibility** play (per the north-star doc) at the decomposition level. An orbit class is the object that is legible; an orbit point is a shadow of it. The canonicalizer is the primitive that lifts shadows to objects.

---

## Recommendation — corrected

**Invest in the orbit canonicalizer first, separately from gen_12.**

Concrete next-tick-scale work items, in strict order:

1. **Canonicalizer v2 for 2×2 matmul.** Implement a candidate Step 3 (T-stabilizer basis alignment — candidate strategies listed in `orbit_vs_representative.md`); test on the 4 ALS-converged seeds from the pilot. Pass condition: all 4 seeds hash to the same canonical form, AND that form recovers Strassen under a nearest-integer orbit-internal probe. This is a bounded test: 1–2 ticks of work, clean pass/fail outcome, no dependency on other Tier-2 work.
2. **Only if (1) passes:** draft `multilinear_map@v1` and `decomposition@v1` symbol candidates in `symbols/CANDIDATES.md`, including the `canonical_hash` and `canonicalizer_version` fields in `decomposition`.
3. **Only if (1) and (2) pass:** extend canonicalizer v2 attempt to 3×3 matmul (rank 23 Laderman). The scaling behavior is the determining test for whether gen_12 is a v1.0-ready generator or stays a DRAFT-level research item.
4. **Only then:** touch the search-primitive layer. ALS alone is sufficient as a search primitive for calibration; the GA + MAP-Elites additions are post-canonicalizer enrichments, not the critical path.

**Rejected / deprioritized:** building the search primitive layer first. That was the v0.1 framing and the empirical evidence refutes it. Every additional search primitive added before canonicalizer v2 just produces more orbit-points in different bases, which we then cannot compare.

**Secondary:** post the stoa/ideas doc (updated) for sessionB / auditor / Kairos-style dissent. Hinge question has shifted — responders should be reacting to the current orbit-first framing, not the v0.1 four-gates framing.

---

## What this direction can carry

James's closing framing — "*search is easy; representation is the problem. That's the kind of result that can carry an entire project if you lock in the right abstraction now*" — is the load-bearing claim. I'll signal that I agree with it in the following way: the orbit canonicalizer as a substrate primitive is **domain-agnostic**. It works identically for:

- Matmul tensors at any `n × n`
- Determinant / Pfaffian / permanent tensors
- Structure tensors of Lie / Clifford algebras
- Polynomial multiplication tensors (Karatsuba, Toom-Cook)
- Any multilinear map with a nontrivial symmetry group on its factor spaces

Every one of these has a public calibration anchor. Every one of them is a place where an "orbit class catalog" is a well-defined deliverable. The canonicalizer is the primitive that makes all of these expressible in one substrate. If it works for 2×2 matmul first and 3×3 matmul second, the rest is mostly engineering.

This is exactly the shape of compounding that `user_prometheus_north_star.md` names ("compressing coordinate systems of legibility, not laws"): the canonicalizer is one coordinate system that many problems collapse into.

---

## Artifact inventory

- `docs/prompts/gen_12_tensor_identity_search.md` — DRAFT v0.2 (reframed)
- `stoa/ideas/2026-04-23-sessionA-tensor-identity-search.md` — v2 with pivot header
- `harmonia/memory/architecture/orbit_vs_representative.md` — v0.1 (new, substrate-primitive note)
- `harmonia/tmp/tensor_pilot_2x2_matmul.py` — pilot script
- `harmonia/tmp/tensor_pilot_2x2_matmul_results.json` — pilot results
- `harmonia/tmp/canonicalize_test.py` — multi-seed hash collision test
- `harmonia/tmp/tensor_identity_search_verdict.md` — this doc

---

## Meta: what this episode taught about MVP discipline

The v0.1 framing was coherent and would have carried a spec to ship. The empirical pilot + canonicalizer test together took ~10 minutes of compute and writing and exposed the mis-specification. The lesson is not "always run the empirical check" (already doctrine); it is **"pre-commit holds are cheap and load-bearing at abstraction-boundary points."** James's hold-off-on-committing call is what let the correction happen before the wrong abstraction hardened.

Memorial-worthy lesson for cross-session reuse: when an MVP produces a positive signal that is one reframe away from a negative signal, the pre-commit hold at the abstraction boundary is the deciding factor for whether the project gets the right substrate shape or the almost-right shape. (Candidate for `feedback_mvp_pre_commit_holds.md` — will draft if the lesson replicates.)
