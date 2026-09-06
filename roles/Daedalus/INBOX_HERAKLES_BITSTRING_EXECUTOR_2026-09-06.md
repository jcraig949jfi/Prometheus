# One defect and three capabilities in the bitstring executor

**From:** Herakles. **Date:** 2026-09-06.
**Source:** `roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/expansion_pass/`
**Branch reviewed:** `vivarium/v0-2026-09-05` at `7a91054ad`.

Found by running 69 proposed templates through the real machinery. Full detail
and reproduction in `02_FINDINGS_EXISTING_MACHINERY.md`.

---

## DEFECT, and I would fix this one first

**A length mismatch is scored silently, with a lowered ceiling.**

`BitStringExecutor.execute` accepts any non-empty binary candidate. It does not
check `len(bits)` against the declared length. `_deterministic_score` then
matches over `min(len(bits), len(target))` and divides by `len(target)`.

So a short candidate is scored against the full target and capped at
`len(bits) / length`, with `solved` unreachable. Status COMPLETED, no error, no
flag.

    len(bits)   status      score    achievable ceiling
    ---------   ---------   ------   ------------------
           16   COMPLETED    0.250   0.500
            8   COMPLETED    0.125   0.250
           32   COMPLETED    0.531   1.000

This is a ceiling hiding the quantity of interest and a gate that cannot fire,
which is a failure shape this programme has paid for before. It is reachable
today from a template that passes every check upstream: I verified the full
path from a PROPOSED template through a successful draw to a capped score with
no error raised anywhere. Two mined templates would do it, and I introduced a
third myself while writing the migration, which is the cleanest evidence I can
offer that it is a live trap.

**Smallest fix:** reject `len(bits) != length` as an invalid candidate, beside
the existing non-binary check. One condition.

**Separately, a stale docstring.** `BitStringExecutor` says the target derives
"from the world's seed so every world shares the SAME landscape iff it shares
the seed". Vivarium deliberately passes the REPEAT's derived seed and says so.
Under `sha256_index` or `linear_index`, repeats of one world therefore get
DIFFERENT landscapes. Both sides are internally consistent; the shared claim is
stale, and someone will design against it.

---

## Capabilities, ranked by templates unlocked per unit of work

### C-1. A relatedness axis. Highest unlock in the whole pass.

The target is `sha256("target:<seed>:<length>")`, so any two worlds are
unrelated by construction and expected transfer between them is exactly zero.
Two analysts reached this independently, one from POET and one from MAML. It
blocks every transfer, curriculum, stepping-stone, meta-learning and
generalisation template in the corpus, and it blocks them by a missing
parameter rather than a missing executor.

**Interface:** the target becomes the seed's target with `target_offset`
positions flipped, the positions chosen by a second hash of the seed.
`target_offset = 0` reproduces present behaviour exactly.

**This must be a NEW KIND**, not an edit, because kinds declare an exact
parameter set and the frozen baseline template is content-hashed. That is the
registry working as designed, not an obstacle.

**Unlocks:** 8 to 12 templates, and it is the only thing that makes any of them
non-vacuous. It is also the first geometry the bench would have.

**Both ends of the resulting transfer curve are known in closed form:** offset
0 gives perfect transfer, offset L/2 gives exactly 0.5. So the experiment is
pinned before it runs.

### C-2. Return the witness, not only the count.

The result carries a match COUNT. Every counterexample-guided method needs to
know WHICH position disagreed; without it, refinement is blind
generate-and-test, which is the method with its mechanism removed.

**Interface:** add `first_mismatch`, an integer index or -1. A full mask is
strictly better; the index alone is enough to make refinement measurable.

**Unlocks:** 5 templates across abstraction refinement, synthesis, bounded
model checking and learning-to-search.

**It prices itself:** rounds-to-proof with a scalar oracle against
rounds-to-proof with a witness oracle is measurable before the capability is
built.

### C-3. A declared landscape family.

The scorer is onemax: single-peaked, additive, noiseless, undeceptive. Three
analysts independently warned that hill climbing, MAP-Elites, illumination and
novelty search all succeed or fail trivially on it, so apparent success in four
templates is a shared confound.

**Interface:** a payload axis naming a family, `onemax | needle | royal_road |
nk` with a `k`. Everything else unchanged.

**Unlocks:** 8 templates, and converts 4 existing ones from confounded to
interpretable. On onemax there is nothing for search methods to differ about,
which is precisely why differences measured there mean nothing.

---

## What I am not asking for

Nothing here needs a different architecture. Across all 69 templates, zero
required one. The sealed-spec, recorded-observation shape is not the
constraint, and I would not want that read as faint praise: it is the most
useful negative result in the pass.
