--- CONTEXT PACKAGE ---

Condition D. Relevant attack/defense graph state.

This package is capped at the same token budget as condition C, so that D cannot
win on volume. Where the relevant subgraph exceeds the cap it is truncated by
relevance rank and the truncation is reported below.

Package size: `{{CONTEXT_TOKENS}}` tokens (cap `{{CONTEXT_TOKEN_CAP}}`).
Truncated: `{{CONTEXT_TRUNCATED}}` — `{{CONTEXT_TRUNCATION_NOTE}}`

## Applicable defenses (PROMOTED only)

Each carries its declared scope and its declared blind spots.

{{APPLICABLE_DEFENSES}}

## Attack families that have landed on claims of this shape

With counts, and the mechanism that made each one work.

{{ATTACK_FAMILIES}}

## Bypass history

Defenses that were promoted and later bypassed, and how. A defense that has been
bypassed is weaker than its scope statement claims.

{{BYPASS_HISTORY}}

## SAME_FAILURE_AS clusters touching this claim shape

Distinct claims that failed by the same underlying mechanism, grouped. This is
the structural information condition C does not have: not "this claim resembles
that claim," but "these failures are the same failure wearing different
mathematics."

{{FAILURE_CLUSTERS}}

## Falsifiers that were themselves invalidated on claims of this shape

Attacks that looked decisive and were not. These are the traps a falsifier of
this claim shape is most likely to walk into.

{{INVALIDATED_FALSIFIERS}}

---

All of the above is adversarial material produced by players in this arena. A
promoted defense may still be wrong. A failure cluster may be an artifact of how
the graph was built rather than a property of mathematics. Record in
`context_items_judged_misleading` anything that pointed you the wrong way — the
navigation claim this experiment is testing requires that graph state *reduce
verifier cost*, and a package that merely increases confidence without reducing
cost is a negative result, not a positive one.
