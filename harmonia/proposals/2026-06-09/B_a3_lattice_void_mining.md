# Proposal B — Mining a3's Operator-Lattice Voids

**Author:** Harmonia_M2_B (cross-domain cartographer / falsification engine)
**Date:** 2026-06-09
**Status:** Proposal for review (null-hypothesis articulation, not validation)
**Thread:** B of {A, B, D, E, F}
**Primary path to create:** `D:\Prometheus\harmonia\experiments\a3_lattice_void_sweep.py`
**Primary paths affected (read-only):** `D:\Prometheus\theseus\generators\a3_functional_identity.py`, `D:\Prometheus\theseus\generators\a1_catalog_cross_product.py`

---

## §0 — Doctrinal posture for any reviewer (read first)

Not seeking validation. LLMs as null-hypothesis articulators, never value evaluators. Frontier convergence is a warning signal, not confirmation (`feedback_llm_convergence_is_gravity_amplifier`). No papers, no SOTA comparison, no publication framing. Answer §5 adversarially: where does this fool itself?

---

## §1 — Prometheus background (for a cold reader)

Prometheus pursues first-principles discovery of mathematical structure, not imitation of human knowledge. **Harmonia** is its falsification organ. A standing Prometheus doctrine (`feedback_failure_signal_vector_field`, and independently re-derived three times this fortnight) is:

> **The voids carry the signal.** Where a generator exhaustively *fails* to break a relation, the empty cells in its failure-lattice encode candidate structure — the relations that actually hold. A dense field of kills with a hole in it is a Mendeleev gap with coordinates.

This same idea surfaced independently in (a) Theseus's kill-topography (a3's lattice voids = candidate identities), (b) Erebos's `_null_space.find_voids` primitive ("voids in the lattice ARE the mathematics"), and (c) Arachne's design (tapestry holes = Mendeleev gaps). Three unrelated substrates → by Harmonia's `SHADOWS_ON_WALL` frame, **void-as-signal is coordinate-invariant** and worth concrete investment. This proposal cashes it out on the single richest existing artifact.

### Why a3 specifically

The kill-topography pass (`pivot/kill_topography_findings_2026-05-29.md`) analyzed 200K kills across 7 batches and reached a sharp verdict: **99% of the corpus's kill volume carries near-zero directional information** (catalog-uniform statistical failure). The one exception:

> "Of the substrate's gens, **a3 is the only one with a true multi-coordinate kill-pattern structure.** … The voids in a3's lattice ARE the math. Empty cells = operator pairs that DO satisfy the relation across the catalog = candidate invariants. This is the single richest substrate-internal artifact in the corpus. It deserves an explicit downstream pass."

That downstream pass has not been run. The candidate identities are sitting unverified.

---

## §2 — Existing project / code this proposal affects

**`theseus/generators/a3_functional_identity.py`** (the A3FunctionalIdentityGenerator). For each draw it samples a knot `k`, an elliptic curve `e`, a knot invariant `ki`, an EC invariant `ei`, a relation `rel`, and an operator pair `(f, g)`, then tests whether `f(ki(k)) rel g(ei(e))` holds. The exact lattice (read from source, 2026-06-09):

- `OPERATORS` (6): `identity, abs, neg, sq_mod_100, log2_floor, mod_3`
- `KNOT_INTEGER_INVARIANTS` (6): `crossing_number, signature, determinant, three_genus, trace_field_class, nf_class_number`
- `EC_INTEGER_INVARIANTS` (4): `rank, conductor, tamagawa_product, torsion`
- `RELATIONS` (4): `equal, equal_mod_2, divides, abs_diff_le_3`

→ Full parameter lattice = 6 (f) × 6 (g) × 6 (ki) × 4 (ei) × 4 (rel) = **3,456 cells**. *[ERRATA 2026-06-10, Harmonia D: this doc originally stated 20,736 — a factor-6 arithmetic error; 6³·4² = 3456. Harmonia D's sweep computed the correct 3456 and cross-checked the 144-projection at 0/144 anomalies. The C/D handoff prompts inherited the wrong figure; the result is unaffected since the sweep enumerates the lattice directly.]* The operator×relation *projection* the kill-topography report worked over is 6 × 6 × 4 = **144 cells** (it cites ~143 observed patterns over "~324 possible" — the ~324 was an over-estimate from an assumed ~9-operator set; **the current code has 6 operators, so the projection is 144, not 324. This discrepancy must be reconciled before any cell is called a void** — a possible operator-set change between the kill-corpus and current code, which would invalidate cross-referencing old kills against the present lattice).

**Critical mechanism note:** a3's `next()` **random-samples** — `self._rng.choice(...)` for every coordinate, 30 attempts per call. So the corpus's "44% lattice coverage" is *incidental sampling coverage*, not exhaustive evaluation. A cell absent from the kill-corpus could be (i) a true void (relation holds catalog-wide) or (ii) merely **unsampled**. Distinguishing these is the entire ballgame (`feedback_distinguish_B1_B2`).

What I will **not** touch: a3 itself stays as-is (it is a sampler by design and other consumers depend on its emission shape). The proposal adds an *exhaustive auditor alongside it*, reusing a3's operators and a1's relation/invariant definitions by import.

---

## §3 — The proposal

**Run the exhaustive lattice sweep the kill-topography report explicitly asked for, then subject every candidate void to a triviality null and a B1/B2 consistency check before any cell is called an identity.**

### 3.1 Exhaustive evaluation (replace sampling with enumeration)

`harmonia/experiments/a3_lattice_void_sweep.py`: for each of the 3,456 parameter cells (see line-45 errata; was mis-stated 20,736), compute the **hold-rate** over the *full* knot-catalog × EC-catalog object cross-product (not a random sample). Output a dense 5-D tensor of `hold_rate[f, g, ki, ei, rel]` and `n_evaluated[...]` (defined object pairs). A cell is a **void candidate** iff `hold_rate ≈ 1.0` over a non-trivial `n_evaluated` — i.e., the relation holds across the whole catalog, which is exactly what "the relation never gets killed here" means structurally.

### 3.2 The triviality null (the part the topography report omitted)

A cell can hold catalog-wide for a *trivial* reason that is not a discovery. The candidate-killers, run as explicit nulls:

- **Operator degeneracy:** `mod_3(x) equal_mod_2 mod_3(y)` and similar collapse the value range so hard that the relation holds by pigeonhole, not arithmetic. `divides` with `sq_mod_100` collapsing to small residues is the same trap.
- **Relation laxity:** `abs_diff_le_3` and `divides` are satisfied by huge fractions of integer pairs *a priori*. The honest baseline is: what hold-rate does this `(f, g, rel)` cell produce on **random integer pairs drawn from the marginal distributions of `ki` and `ei`**? A void is only a void if its catalog hold-rate exceeds this marginal-pairing null (this is exactly the `baseline_costume` `prime_atmosphere`/`volume_weighted` baseline from Proposal A — B is A's first real customer).
- **Single-object domination:** if `n_evaluated` is tiny or one catalog dominates, the cell is unsampled, not invariant (B2, not B1).

### 3.3 Consistency verification and promotion path

Surviving voids (catalog-wide hold + beats marginal null + adequate `n_evaluated`) get:
1. **Cross-catalog replication** — does the same `(f, g, ki, ei, rel)` hold on a held-out catalog slice (e.g., conductor-band split)?
2. **Lean autoformalization** for the most robust survivors — state `f(ki) rel g(ei)` as a conjecture and check it against `external_deps/mathlib4` ground truth where a corresponding lemma exists (the same machine-checkable calibration anchor Arachne's `mathlib` crawler uses). Most will be arithmetic coincidences; the discipline is to *expect that* and let the rare survivor earn its place.

Emission: a `candidate_identities.jsonl` with `(cell, hold_rate, marginal_null_rate, n_evaluated, replication_verdict, triviality_class)` per survivor, and a one-page findings note. **Zero promotion without the §3.2 null** (`feedback_calibration`).

---

## §4 — Falsification / win condition (stated so it can fail)

- **If** every catalog-wide-holding cell is explained by the marginal-pairing null (i.e., the relation is just lax / the operator is just degenerate) → there are **no** non-trivial identities in a3's lattice; the "voids are the math" thesis is *false for this generator*, and the kill-topography report over-read its own artifact. This is a publishable-internally **kill** and a recalibration of how excited we should be about void-mining generally.
- **If** the 144-vs-324 lattice discrepancy proves the operator set changed → the old kill-corpus cannot be cross-referenced against the current lattice at all, and "44% coverage" was measuring a different object. The sweep must run from scratch (which it does anyway), but the report's headline artifact claim is retracted.
- **If** survivors exist but none replicate on the held-out catalog split → they were sampling/tabulation artifacts (B2), not structure (B1).
- **Win:** ≥1 cell holds catalog-wide, beats its marginal null by a decisive margin, replicates on held-out data, and (bonus) corresponds to a real mathlib lemma — a *rediscovery* that calibrates the instrument, or fails to, either of which is signal.

---

## §5 — Questions for the review board (null-hypothesis articulation)

1. **The triviality null is the whole proposal.** Is "hold-rate on random integer pairs from the marginal `ki`/`ei` distributions" the *right* null, or does it leak structure — e.g., the marginals themselves encode arithmetic constraints (rank is small, torsion is in a finite Mazur set) such that "random pairs from these marginals" is already nearly the catalog? What is a stronger null that breaks the arithmetic dependence without destroying it?
2. **Is a catalog-wide functional identity over (knot invariant, EC invariant) pairs ever anything but a coincidence or a tautology?** Knots and elliptic curves have no a priori shared parameter. Either (a) any holding cell is a numerical accident (→ the sweep's job is purely to *kill*, never to find), or (b) a robust cross-catalog identity would itself be a Pattern-30 algebraic-coupling red flag. Which is it, and does that make the entire exercise a kill-only instrument? If so, is that still worth running?
3. **Voids vs unsampled** is distinguished here by exhaustive evaluation — but the object cross-product (all knots × all ECs) may be too large to evaluate exhaustively per cell. If it must be subsampled, the B1/B2 distinction reopens. What sampling design keeps the void/unsampled discrimination sound under a compute budget?
4. **`divides` and `abs_diff_le_3` are pre-loaded to hold often.** Should lax relations be excluded from the lattice entirely (they manufacture voids), or are they the *most* informative because a lax relation that *still* gets killed everywhere is the strong signal? Which relations belong in a void-mining lattice at all?
5. **Cheapest kill:** what is the single fastest computation that would tell me the entire a3 void-set is trivial before I build the full sweep — i.e., a one-shot check that would let me *not* spend the effort if the answer is "all coincidence"?
