# Tensor Identity Search as a Prometheus generator — discussion

**Author:** Harmonia_M2_sessionA, 2026-04-23 (updated later same day after empirical pilot + canonicalizer test refuted the original framing).
**Status:** idea. Parallel to a DRAFT spec at `docs/prompts/gen_12_tensor_identity_search.md` (now v0.3), a first-class substrate-primitive spec at `harmonia/memory/architecture/canonicalizer.md` (v0.1) with tensor-decomposition instance detail at `harmonia/memory/architecture/orbit_vs_representative.md` (v0.2), and a pilot + canonicalizer test at `harmonia/tmp/tensor_pilot_2x2_matmul.py` + `canonicalize_test.py`. James's seed: "evolving math" via GA + MAP-Elites over tensor-train / CP-rank decompositions of multilinear maps.

**The pivots (two, same day):**

1. *Search → representation.* A 2026-04-23 pilot refuted the original framing of gen_12 as *search with an orbit-equivalence gate*. Four ALS-converged rank-7 decompositions of 2×2 matmul, known to be in a single orbit by the Strassen equivalence theorem, hashed to **four different** v1 canonical forms; none matched Strassen's integer representative. Search is not the bottleneck; representation is.

2. *Tensor-specific note → substrate primitive.* After the reframe, canonicalization sat in a tensor-decomposition-specific note (`orbit_vs_representative.md`). James's follow-up directive escalated it to a first-class substrate primitive (`canonicalizer.md`) because the same abstraction is needed by Definition DAG (node identity), MAP-Elites (archive dedup), Pattern 30 (algebraic rearrangement equivalence), and gen_11 (distinguishing novel coordinates from re-parameterizations). Burying it in gen_12 would have locked in the wrong abstraction boundary and produced weaker re-implementations elsewhere.

The discussion questions below remain live but should be read through both reframes. Hinge question is now: *does `CANONICALIZER:tensor_decomp@v2` (T-stabilizer basis alignment on top of v1) pass its calibration anchor for 2×2 matmul? And does the same approach scale to 3×3 matmul (rank 23 Laderman)?* Calibration-first, one instance at a time.

---

## Update 2026-04-23 (post-pilot)

- Hinge question shifts from "is orbit-equivalence canonical form tractable at Laderman scale?" to **"is a v2 canonicalizer (scale + sign + permutation + T-stabilizer basis alignment) tractable for the 2×2 matmul case first, and what does that test reveal about scaling to rank 23?"** — a direct, cheap, calibration-first version of the same question.
- The attention-allocation question against gen_09 / gen_11 / Definition DAG Phase 0 remains live, sharpened by the fact that gen_12's load-bearing primitive (canonicalizer) is not part of the existing Tier-2 roster — it is a new substrate primitive alongside Definition DAG.
- The symbol-type extension question is sharpened: `decomposition@v1` must carry `(raw_factors, canonical_hash, canonicalizer_version)`, not just raw factors. The hash versioning is load-bearing because v1 and v2 canonicalizers live in disjoint hash namespaces.

---

## Original discussion (pre-reframe — retained for audit)

---

## What caught my attention

There is a well-posed mathematical landscape — low-rank decompositions of multilinear maps — where the basins of attraction are visibly rugged, the calibration anchors are public and unambiguous (Strassen, Laderman, Karatsuba), and the substrate Prometheus has been building (versioned symbols, composition hashes, Pattern 30 discipline, `PROBLEM_LENS_CATALOG` framework) maps almost 1-to-1 onto what this search would need.

That overlap is uncommon. Most generator proposals need the substrate to stretch in one direction or another. This one fits without stretching.

## Why it might matter

**The opportunity isn't replicating AlphaTensor.** AlphaTensor (2022) already used RL on this exact tensor space and rediscovered Strassen. James's framing is different — GA + MAP-Elites over (rank × field × symmetry) cells — but in the literature context that's a methodological variant, not a new landscape.

**The opportunity is orbit-equivalence discipline as a first-class substrate primitive.** AlphaTensor's headline "new" 4×4 and 5×5 decompositions were substantially orbit-variants of known ones under `(GL × GL × GL) × S_r`. Two factorizations related by invertible basis changes on each of the three tensor axes + a permutation of the rank-1 summands are the same decomposition in every mathematical sense. Counting them separately is the decomposition-level instance of Pattern 1 (Distribution/Identity Trap).

A substrate that:
- Stores each decomposition with an orbit-invariant fingerprint (a canonical form under the group action)
- Rejects new candidates whose fingerprint matches an existing catalog entry
- Is built from the ground up around versioned composition hashes and retraction-as-first-class-event

… is a substrate that does this part of the discipline correctly by construction. The Pattern 30 graded-severity framework translates directly: a decomposition equivalent to an existing one under the group action is Level 3 (REARRANGEMENT); a decomposition using factors that are themselves definitions of the target is Level 4 (IDENTITY).

**The opportunity is multi-primitive cross-validation.** GA + MAP-Elites is one search primitive. ALS + random restart is another. Gradient descent with nuclear-norm surrogate is another. Combinatorial structured search over `{-1, 0, 1, ±1/2}` is another. Running all four on the same target and asking "which rank is reached by every primitive and which only by some?" is SHADOWS_ON_WALL at the search level. That cross-primitive check is where this direction diverges from the RL-one-big-model approach and fits naturally into Prometheus's multi-lens frame.

## Concrete open questions (invite responses)

1. **Is the `multilinear_map@v1` symbol type worth the architectural cost?** The symbol registry currently has six types (operator, shape, constant, dataset, signature, pattern). Adding `multilinear_map` and `decomposition` is ~2 new types. That's a real extension; it affects the promotion workflow, the Redis schema, and the MD conventions. Alternative: treat multilinear maps and their decompositions as `constant` symbols with more structure in the body. I lean toward the new types (the structure is load-bearing) but I'd like sessionB / auditor critique before committing.

2. **Is orbit-equivalence canonical form tractable at the ranks we care about?** For rank ≤ 10, probably yes (we can implement a canonical form via Jordan normal / Smith normal reasoning on the slice structure). For rank 20+ (Laderman territory), probably not in closed form; we would need a hash-invariant built from orbit-stable numerical invariants (singular-value spectra of the three unfoldings, multi-trace invariants). This is ~50% of the infrastructure lift. If canonical form is actually impractical, Gate 2 becomes probabilistic and the epistemic standing of "novel" decompositions weakens.

3. **Is the field-versus-ring distinction pinned correctly?** AlphaTensor's strongest public results are over `F_2`, which are of interest for boolean matrix multiplication and coding but do NOT transfer to ℝ / ℚ. If Prometheus-gen_12 allows F-field searches, the catalog needs to segregate them strictly. If it restricts to ℝ / ℚ, we miss the AlphaTensor-accessible part of the map. I lean toward *both* with strict segregation in the `decomposition` symbol's `field` slot, but that doubles the calibration-anchor count.

4. **Does this compete for attention with gen_09 (cross-disciplinary transplants)?** Both are Tier-2 generators with search / optimization primitives as their core. gen_09 is already seeded. If gen_12 lands, is it competing or composing? My read: composing — gen_09 imports vocabulary (K̂, CHANNEL_CAPACITY, CONTROLLABILITY_RANK) into the shelf, and gen_12 uses the shelf tools as decomposition-quality scorers. But the attention-allocation question is live.

5. **Does this bend the substrate's "measurement, not proof" frame?** An exact decomposition over ℚ verified by symbolic multiplication IS a proof of an algebraic identity. Does that make gen_12 a theorem-prover in disguise? I don't think so — the identity is easily proved once the decomposition is exhibited; the hard part is finding the decomposition, which is empirical/search, not proof. But the framing is adjacent to the long-term architecture doc's non-goal #1 ("Proving theorems or generating novel mathematics"). Worth a deliberate read on whether it crosses or just grazes.

6. **Is "evolving math" the right meta-framing?** James's phrasing. I read it as *using evolutionary search over mathematical objects to discover compression primitives*. That's a different activity from evolutionary model-training (no loss function drifts, no curriculum). The primitives being discovered are algebraic identities, not heuristics. The substrate should probably not adopt "evolutionary math" as a literal tagline because the connotation drifts; but the mechanism (GA + MAP-Elites on factor-matrix populations) is legitimate and Prometheus-shaped.

## What I'd want someone else to say about it

- **sessionB or auditor on the symbol-type extension.** Is adding `multilinear_map` and `decomposition` to the registry a minor extension or a refactor? I believe minor — the existing types don't preclude new ones and the push/pull machinery is agnostic — but I haven't stress-tested that claim.
- **Anyone with RL or meta-learning background on the orbit-equivalence problem.** The canonical-form question is the hinge; everything else is comparatively boring engineering. If canonical form is hard, the whole proposal's rigor story weakens.
- **James on the attention-allocation question.** gen_09 seeded, gen_11 DRAFT, Definition DAG Phase 0 open, tensor-identity-search now DRAFT. Four Tier-2 fronts is a lot. Which of them is the *current* north star, and which can wait?
- **Kairos-style dissent** on "is this reward-signal capture dressed as substrate-growth?" If I'm honest, tensor decomposition is attractive because it's concrete, has clear metrics, and produces visible artifacts. Those are the textbook conditions for novelty-seeking to drift from calibration-first. A pre-committed calibration gate (rank-7 Strassen rediscovery required before any other claim) is the designed discipline; is it *enough*?

## What the 2×2 pilot will teach (and won't)

A pilot at `harmonia/tmp/tensor_pilot_2x2_matmul.py` answers *one* question: *does a dumb GA + ALS stack rediscover Strassen's rank 7 on the 2×2 matmul tensor over ℝ in a modest budget?*

It does NOT answer:
- Whether the full gen_12 architecture is worth building
- Whether orbit equivalence is tractable at Laderman scale
- Whether MAP-Elites cells reveal new structure vs confirm existing
- Whether ℝ decompositions transfer to ℚ with small-integer coefficients

What it DOES tell us:
- If rank-7 is reached reliably: the search primitive is not the bottleneck; architecture (gen_12 spec) is where attention belongs.
- If rank-7 is NOT reached reliably at this scale: the search primitive needs upgrade (better ALS, structured init, or swap to a different primitive) before architecture work matters.

That's a cheap one-bit filter on whether this whole direction is ready for further investment.

---

## References

- Strassen 1969 — rank-7 decomposition of 2×2 matmul
- Laderman 1976 — rank-23 decomposition of 3×3 matmul
- Winograd 1971 — lower bound proof that rank(2×2 matmul) ≥ 7
- Bini et al. 1979 — approximate / border-rank results
- Fawzi et al. 2022 (AlphaTensor) — RL over decomposition search space
- `docs/prompts/gen_12_tensor_identity_search.md` — parallel MVP spec
- `harmonia/tmp/tensor_pilot_2x2_matmul.py` — parallel MVP pilot
- `harmonia/memory/methodology_toolkit.md` entries 1–8 — scorer shelf this would compose with
