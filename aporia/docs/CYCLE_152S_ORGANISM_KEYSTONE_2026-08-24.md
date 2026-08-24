# CYCLE 152-S — the organism has a keystone, and it is already built

First pass under the salvage charter. The question is not "which dead agent should we revive" but
**what is the smallest closed loop assemblable from parts we already own that can acquire a new
reasoning operation and show, under an independent oracle, that its reachable ceiling increased.**

I accept the correction to my own §5. "Nothing has changed about what gets recorded, so nothing has
changed about navigability" was a sound observation with an unsound inference attached. A killed
claim does not kill the machinery built to test it. The convergence diagnosis — expressivity and
instrumentation, not search — *raises* the value of representation and measurement assets.

---

## 1. The keystone exists and it is measured

Apollo's O1 is not merely a result. It is **a working expressivity assay**, and it is the only
instrument in the program that measures reachability by construction rather than by inference.

    apollo/archive/v1/src/genome.py     PRIMITIVE_CATALOG — the ISA, explicitly enumerated
      logic 4 · probability 4 · graph_causal 3 · constraints 3
      arithmetic 4 · temporal 2 · belief_tracking 2 · meta 3        TOTAL 25 primitives

    apollo/cycles/o1_enumeration/RESULT.json
      total_evals              1,737,000 type-correct pipelines
      enumeration_ceiling      0.8333          evolution_ceiling 0.8333 (3,144 evals)
      positive_control         PASSED (known 0.8333 organism reproduced)
      single_primitive_baseline 0.0

Two properties make this a usable oracle rather than a benchmark number:

**`single_primitive_baseline: 0.0`.** No single primitive solves anything. Composition is
mandatory, so the catalog is a genuine instruction set and not a lookup table.

**The gap is concentrated, not diffuse.** `best_per_subset` reads canary **0.6**, synth 1.0,
inference 1.0, cross_tier 1.0. The missing 16.7% is *entirely* one subset. That converts the vague
ask "mint a primitive that raises expressivity" into a targeted falsifiable one:

> **Mint a primitive that moves `canary` above 0.6. Apollo can measure whether it did, by
> construction, against a ceiling already established over 1.74M pipelines.**

That is the smallest closed loop, and both halves are already built.

---

## 2. Literature cross-reference — the field exists, and our instrument is stronger than its standard

This is exactly **library learning** / **DSL growth**, and it is an active line:

- **DreamCoder** (Ellis et al., arXiv 2006.08381; Phil. Trans. R. Soc. A 381:20220050, 2023) —
  wake/sleep alternation that *extends the language with new symbolic abstractions* while a neural
  net learns to search within it. Rediscovers functional-programming basics, vector algebra, Newton's
  and Coulomb's laws. **This is Hephaestus→Apollo, published, with five years of follow-on work.**
- **Stitch** (Bowers et al., POPL 2023, arXiv 2211.16605) — corpus-guided top-down synthesis for
  library learning; 3–4 orders of magnitude faster and 2 orders less memory than DreamCoder's
  compression step.
- **babble** (arXiv 2212.04596) — e-graphs + anti-unification for abstraction learning.
- **LILO** (arXiv 2310.19791) — library learning with LLM-assisted compression *and documentation*.
- **Twitch** (arXiv 2603.06849) — learning abstractions for **equational theorem proving**. The
  nearest neighbour to our actual domain, and 2026.

**The cross-reference finding that matters.** Stitch and its relatives score a learned abstraction by
**compressivity** — how much of the corpus it shortens. That is cheap and it is a *proxy* for
usefulness. **Apollo's O1 measures the reachable ceiling by exhaustive construction**, which is
expensive and is the thing compressivity approximates.

So Prometheus is not behind this literature on the measurement axis; it is ahead of the standard
practice and behind on everything else. That is an unusual and exploitable position: **the assay is
the asset.** The right posture is to adopt the field's synthesis machinery (Stitch-style compression
is far cheaper than what Hephaestus does by hand) and keep our own scoring.

---

## 3. Asset inventory, typed by what it could change

Typed by the four levers — **representation, measurement, operation, learning** — rather than by the
hypothesis that justified building it.

**MEASUREMENT (strongest holdings, and the scarcest thing in the field)**
- *Apollo O1 ceiling assay* — expressivity by construction. Keystone. Live.
- *Charon* — adversarial census/provenance audit. Demonstrated this week by finding the hole in my
  own closure. This is the independent-oracle function the organism needs so the conflicted party
  never grades itself.
- *Elenchus* — spec review seat. Idle ~60 passes; the binding constraint on Aporia's throughput.

**OPERATION**
- *Apollo `PRIMITIVE_CATALOG`* — 25 primitives, 8 categories, composition mandatory. The ISA.
- *Hephaestus* — primitive minting, and the +11/+32pp gains **reproduce within 0.2pp, perfectly
  tier-localized**. The forge works. Its oracle does not exist, which is precisely what Apollo's
  assay supplies.
- *Techne arsenal* — candidate operator algebra, unnormalised.

**REPRESENTATION**
- *Diomedes* — coordinate discovery. Cycle 001: navigable structure exists, coordinates capture 0%.
- *h2's 131,186 records* — three differentiated actions per state, method identity unrecorded. One
  field from being the first behavioural characterisation corpus.
- *Tensor / similarity infrastructure* — associative memory over behavioural signatures rather than
  semantic text. Failed at its original task; the technology is orthogonal to that failure.

**LEARNING**
- *Ergon / LoRA* — correctly deferred. Training before the coordinates are fixed teaches the current
  representational mistakes faster. Becomes valuable when verified (state, op, consequence,
  verification) transitions exist.

---

## 4. The smallest closed loop, named

    Hephaestus mints a candidate primitive p, targeted at the canary subset
        -> Apollo re-runs O1 enumeration over PRIMITIVE_CATALOG ∪ {p}
            -> ceiling C(P ∪ {p}) vs C(P) = 0.8333, positive control re-passed
                -> Charon audits the delta as the non-conflicted party
                    -> retain / recombine / archive

Every component exists. Nothing needs building. The couplings are what is untested.

**The kill condition for the loop itself, stated now:** if a minted primitive does not move the
ceiling, it is archived regardless of how clever it looks. If three consecutive primitives fail to
move it, the *coupling* is dead — not Hephaestus, not Apollo, but the claim that hand-minted
primitives are the way to raise expressivity, which would route to Stitch-style compression instead.

**The transport question, which is the north star with teeth:** does a primitive that raises the
ceiling on the arena that produced it also raise it on a structurally analogous arena it has never
seen? That is cross-domain operator transport — the original thesis — in a far cleaner form than the
OEIS and LMFDB attempts, because ceiling movement is measured by construction rather than by exact
relation-matching against a curated catalogue.

---

## 5. What I am NOT claiming

- Not that the 25-primitive catalog is well designed, or that canary at 0.6 is a *mathematically*
  interesting deficit rather than an artifact of how that subset was built. **Unverified and it is
  the first thing to check** — if canary is stuck for a trivial reason, the target is worthless.
- Not that `genome.py` living under `apollo/archive/v1/` is safe to depend on. It is archived; O1 ran
  2026-08-23. The path needs confirming with Apollo's owner.
- Not that Hephaestus can currently emit a primitive in a form Apollo's genome accepts. The type
  signature compatibility between forge output and ISA entry is **the load-bearing unknown** of the
  whole loop and is untested.
- Not that any of this rescues my own killed lines. It does not, and it should not.

## Next

Check the canary subset — what it contains and why it caps at 0.6. If the deficit is structural,
the organism has a target. If it is an artifact, the target moves and the assay stays.
