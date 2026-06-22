# Audit — Instrument Monoculture & the Expressiveness Ceiling

**Author:** Harmonia_M2_A · **Date:** 2026-06-22
**Frame:** program-wide reassessment (James: "stalled out a bit — diminishing
returns, monocultures")
**Method:** executing lens (re-ran everything; did not trust cached verdicts)
**Artifacts:**
`D:\Prometheus\harmonia\experiments\hypothesis_class_coverage_audit.py`,
`D:\Prometheus\harmonia\experiments\hypothesis_class_coverage_results.json`

---

## What this is NOT

This is **not** a refutation of sessionD. The EC-rich "0 novel within-object
laws" result is internally sound — re-validated this session under the executing
lens (`validate_ec_rich_diagonal.py` **16/16**, `validate_b_results.py` **29/29**,
`test_lattice_void_miner.py` **34/34**). The miner is a correct decision
procedure within its scope. sessionD even named the binding gaps (sha_an unary
property; sign-variant fan-out). The author was not monocultural.

The **strategy** was. This audit is about the instrument, not the worker.

---

## The finding (one sentence)

The recurring "0 novel laws" across a3 → EC-4 → EC-9 is a **B2 result**
(instrument cannot express the law) wearing **B1** clothing (terrain is flat):
the void-miner's hypothesis class can express only **25 % (4/16)** of surveyed
known elliptic-curve structure, it **found every in-catalog law it could express
(2/2) and zero it could not (0/12)** — the exact signature of a ceiling, not an
exhausted terrain.

## Failure shapes (per `feedback_failure_signature_doctrine` — not verdict lines)

1. **The instrument is a monoculture of one hypothesis class.** Every claim the
   miner can emit has the fixed shape `rel(f(inv_i(O)), g(inv_j(O)))` —
   pairwise, integer-valued, same-object, `rel ∈ {equal, equal_mod_2, divides,
   abs_diff_le_3}`. Class size 10,368 cells, but the *shape* never varies. We
   have been widening the **inputs** (4 → 9 integer invariants; a3 → EC → knot
   lattices) while the **hypothesis class** — the actual binding constraint —
   stayed fixed. Adding integer invariants moves along a flat coverage curve.

2. **The 75 % it cannot see fails along six distinct axes**, none fixable by more
   integer invariants:
   - `CROSS_OBJECT` (3): modularity, isogeny-invariance of conductor, torsion ↪
     E(F_p). The diagonal pairs each object only with itself.
   - `RELATION_OOV` (3): Szpiro/abc ratio bound, Kodaira types, prime-support
     set-equality. Not one of the four scalar relations.
   - `UNARY` (2): Mazur torsion bound, |Sha| a perfect square. Single-invariant
     properties; only *injectable* (T1b), never *discoverable*.
   - `DISTRIBUTIONAL` (2): Sato-Tate, root-number-as-product-over-primes.
   - `ARITY_GE_3` (1): Ogg's formula (3 per-prime quantities).
   - `REAL_VALUED` (1): the BSD formula itself (regulator, period, L-value).

3. **The two laws it keeps "finding" are the two it can express AND has an
   invariant for** — `torsion | ∏c_p` and `rad(N) | N`. Both definitional/known.
   The diminishing-returns curve is not the terrain running out; it is the
   instrument re-finding its same two expressible facts under more operator
   variants (the sign-variant fan-out sessionD measured: 2 laws → 50 cells).

4. **Same failure primitive as Apollo FP-003 (`expressiveness_ceiling`).**
   Apollo's composition stall looked like Goodhart but was an expressiveness
   ceiling (confirmed by executing lens, 2026-06-15). Harmonia's void-miner
   stall looks like terrain exhaustion but is the same ceiling. **Two
   independent agents, rate-limited by the same FP.** That is the strongest
   single datum for the reassessment: the program-level stall is most likely an
   **expressiveness-ceiling phenomenon across instruments**, not exhaustion of
   mathematical or reasoning terrain. (Cross-ref: Harmonia E's failure-primitive
   atlas, FP-003.)

## What separates B1 from B2 here (the diagnostic, per `feedback_distinguish_B1_B2`)

The coverage measure IS the separator. A genuinely flat terrain would show the
instrument finding *some* in-class laws and missing *some* in-class laws (search
insufficiency). Instead: **in-class ∧ in-catalog → found 2/2; out-of-class →
found 0/12.** Perfect recall inside the class, zero possibility outside it. The
"0 novel" is therefore uninformative about whether novel EC structure exists; it
is informative only that *the pairwise-integer-diagonal shadow is fully explained
by two known facts.* SHADOWS_ON_WALL, applied to our own ruler.

## So what (actionable, falsifiable)

The fix is **not** more integer invariants. It is hypothesis-class diversity:

- **A unary-property miner** (closes 2 axes: Mazur, Sha-square) — sessionD
  already nominated this; it is the cheapest coverage gain.
- **Real-valued lattice** with tolerance relations (regulator, height, period,
  L-values) — opens REAL_VALUED + the abc/Szpiro ratio bounds.
- **Cross-object pairing** (isogeny class / quadratic-twist orbits as the pairing
  instead of the identity diagonal) — the g1 Galois-twist target gestures at
  this but still uses pairwise integer invariants.
- **Arity-3 relations** (a small, curated set — Ogg-shape) before brute n-ary.

**Reusable meta-instrument:** `hypothesis_class_coverage_audit.py` is not
EC-specific in spirit. The same coverage measure should be run on the **other**
instruments — a3/knot miners, Apollo's primitive set, Icarus's ladder rungs — to
test whether "instrument monoculture" is the program-wide stall mechanism or
just an EC artifact. That is the falsifiable next step: **if every instrument
tops out at a similar low coverage via similar axes, the reassessment verdict is
"diversify hypothesis classes," not "find new terrain."**

## Honest limits of THIS audit (falsification-first on my own work)

- The 16-law table is hand-curated; the exact **25 %** is illustrative, not
  canonical. The robust claim is the *structure* (deep laws out-of-class via 6
  axes; perfect in-class recall), which survives reasonable edits to the list.
- "Out of class" ≠ "miner is broken." Within its class it is sound. The critique
  is of the fixed class, not the code.
- One strong data point (EC). The program-wide claim is a **hypothesis** until
  the coverage diagnostic is run on the other instruments. Stated as such.

---

*Harmonia A, 2026-06-22. The instrument is the product; this measures the
instrument.*
