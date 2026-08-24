# Pass 4 — the local macro mechanism examined (and it is not what I hoped), plus the e-graph fit

**Date:** 2026-08-24
**New evidence:** `apollo/src/gene_extractor.py` read in full; `apollo/cycles/o1_enumeration/RESULT.json`
config and ceiling pipeline; babble (arXiv 2212.04596) bibliographic and technical detail.

---

## 1. Correction to Pass 3 §6 — the gene extractor is not an O4 ratchet

Pass 3 recorded that `apollo/src/gene_extractor.py` contains "the O4 macro mechanism the Apollo review
proposes as *new architecture* … already in the tree in prototype form." **That was wrong, and the
error was in the direction of wishful reading.** Having now read the file, the mechanism inverts the
library-learning logic rather than implementing it.

**What `compute_portability_score` actually computes.** It starts at 1.0 and subtracts penalties from
a single method's **source text, in isolation**:

- −0.3 if any string literal ≥ 20 characters appears
- −0.2 if more than three of `not / all / every / some / true / false / yes / no / larger / smaller /
  greater / less` appear in the lowercased source
- −0.3 if the method reads any `ctx['…']` key outside the convention allowlist
  (`prompt, candidate, raw_text, parsed, score, fallback_score, _gene_trace, _final_gene_type`)
- −0.2 if any regex call has arguments longer than 30 characters

Clamped to [0, 1].

This is an **anti-overfitting heuristic** — a surface-syntax proxy for "does this tool hardcode
answers or key on English phrasing?" It is not a utility function. Critically:

> **It never looks at a corpus.** Stitch, babble, DreamCoder and LILO all compute an abstraction's
> worth *relative to a body of programs* — how much does interning this structure reduce the cost of
> describing everything else. `compute_portability_score` scores one method's text on its own. The
> two quantities are not comparable and do not measure the same kind of thing.

**And the macro path runs backwards.** From `extract_two_tier_genes`:

    if avg_portability < 0.4 and len(non_utility) > 2:
        # Low portability tool — create a macro-gene

A macro is created **because a tool's methods scored badly** — because they are too entangled and
phrase-bound to be reused as separate genes. `_create_macro_gene` then hardcodes
`portability_score=0.3` on the result.

So the local "macro" is a **containment strategy for un-portable code**: bundle what cannot be
decomposed and mark it low-value. In the library-learning lineage a structure is promoted to a named
abstraction *because it recurs and pays for itself across the corpus*. Here a structure is bundled
*because it doesn't decompose*. Same word, opposite selection pressure.

**Revised finding.** Prometheus does **not** already have an O4 macro mechanism. It has a
forge-tool decomposer with an anti-overfitting filter, unwired, whose macro branch is a fallback for
failure rather than a promotion for merit. The `reads_keys` / `writes_keys` fields are genuinely
useful scaffolding — they are the interface information any abstraction mechanism would need — but
the selection logic would have to be replaced, not extended.

This also removes the "sixth entry" I added to the pass-3 taxonomy. Portability is not an admission
criterion for a library; it is a quality filter on candidate genes. The taxonomy stays at five.

---

## 2. O1's substrate, resolved

Pass 3 flagged an apparent discrepancy: the Apollo review describes 27 operators on a blackboard,
while `apollo/src/genome.py` documents "primitive routing DAGs over 25 Frame H primitives."

`RESULT.json` settles it. O1 ran on the **blackboard substrate**, via `apollo/scripts/o1_enumerate.py`:

    config: max_k 10, orders_per_subset 48, n_transformers 15, n_tails 36

and its ceiling pipeline is blackboard operators —

    parse_box_items, op_aggregate_quantities, parse_comparison, parse_names_and_relations,
    parse_ordinal, parse_rules, forward_chain, parse_which_extreme, relations_from_facts,
    op_build_ordering, score_by_aggregate__g, score_by_comparison__g, score_by_derivab…

So there are two representations in the tree — `blackboard_ops*.py` (the v2d substrate O1 enumerated,
15 transformers + guarded scorer tails) and `genome.py`'s Frame-H catalog of 25 primitives across 8
categories. **The 0.833 expressivity ceiling is a fact about the blackboard substrate only.** Nothing
in O1 bounds what the Frame-H representation could reach. Anyone quoting "0.833 is the ceiling"
should name which substrate.

---

## 3. babble — and the best adoption finding in the study so far

**Bibliographic:** *babble: Learning Better Abstractions with E-Graphs and Anti-Unification.* David
Cao, Rose Kunkel, Chandrakana Nandi, Max Willsey, Zachary Tatlock, Nadia Polikarpova. **POPL 2023** —
the same venue and year as Stitch, from a different group. arXiv 2212.04596, 2022-12-08.

**What it does:** library learning **modulo an equational theory** (LLMT). E-graphs plus equality
saturation compactly represent the space of semantically equivalent programs within a given theory;
anti-unification finds generalized patterns that subsume multiple program variants rather than
requiring exact syntactic matches. Reported: better compression, orders of magnitude faster than the
state of the art. Selection criterion is still **compression**.

**Why this matters here, concretely.** O1 measured something that looks like noise and is actually
the key structural fact about Apollo's corpus:

> The known 10-operator subset has **166,320 valid topological orderings. 45,360 — 27.3% — reach
> 0.833.**

That is an **equivalence class of 45,360 syntactically distinct programs with identical behaviour.**
It is exactly what e-graphs exist to represent. Pointed at that corpus:

- **Stitch would see 45,360 separate programs** and try to compress across them, with the shared
  structure obscured by ordering variation. Its pruning is *syntactic pattern matching*.
- **babble, given a commutativity/independence theory over non-interfering operators, would see one
  e-class** and abstract over the whole equivalence class at once.

And the theory is not hypothetical — O1 already identified the constraint that generates it:
`relations_from_facts` **overwrites** `relations`, so it must follow `parse_names_and_relations`.
That is a dependency edge. Operators without such an edge commute. **A commutativity theory over
Apollo's blackboard operators is derivable from the existing `reads`/`writes` declarations** — the
same declarations `gene_extractor.py` already parses into `reads_keys` / `writes_keys`.

**This retires the pass-3 §7 blocker in its stated form.** The objection was "a state-mutating
pipeline is not a lambda term." True, and Stitch would struggle. But babble's whole premise is
abstraction *modulo a theory*, and read/write-set commutativity is precisely the theory a blackboard
substrate hands you for free. If any tool in this lineage fits Prometheus's representation, it is
babble, not Stitch — and no pass before this one had identified that.

**Caveat, stated plainly:** this is an argument from architecture fit, not a result. Nobody has run
babble on anything of ours. What it establishes is that the representation mismatch is *smaller than
pass 3 concluded*, and that the study was about to recommend the wrong tool.

---

## 4. Ledger of open items

**Resolved this pass:** gene_extractor's actual criterion (§1); which substrate O1 enumerated (§2);
babble's technical fit (§3).

**Still open, carried:**
- Stitch's exact default cost values. Two fetch attempts failed (arXiv PDF returned binary; the
  readthedocs *Cost Metrics* page 404'd at the guessed URL). What is established structurally —
  utility is a corpus-relative cost improvement — is enough for every argument this study currently
  makes. Downgrading to low priority rather than carrying it as a headline item.
- **Twitch rating-1 vs rating ≥ 0.9 discrepancy — deferred four times. Dropping it.** It is a
  bibliographic detail in a paper whose role in this study has been superseded by DreamProver, and
  no conclusion here rests on which figure is right. Recording the drop rather than silently letting
  it fall off: if Twitch ever becomes load-bearing, this must be reconciled first.

**New for pass 5:**
- Does the `reads`/`writes` declaration set on `blackboard_ops*.py` actually support deriving a
  commutativity theory — i.e. are the declarations complete and honest about side effects, or does
  `relations_from_facts` overwriting `relations` indicate undeclared write effects?
- LILO's AutoDoc remains the cheapest unexamined steal (flagged pass 1, untouched since).
- What DreamProver's "recursive theorem decomposition" does that Apollo's crossover does not — both
  are attempts to cross a valley single edits cannot.
