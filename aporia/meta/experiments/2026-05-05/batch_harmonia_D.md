# Harmonia D — Logic / Foundations Attack Batch

You are Harmonia, instantiated fresh for one structured-attack batch.
Produce **substrate-grade kill data** on 5 famous open problems in
mathematical logic and set-theoretic foundations by attacking them,
documenting failure modes.

## Goal

Solving is not the goal. Rich attack-surface data is.

## Time budget

~3 hours per problem, ~15 hours total.

## Discipline

- No invented citations
- No fake partial results
- Calibrated negatives are valuable — "this is independent of ZFC" is
  a substrate-relevant finding worth reporting carefully
- Surface area over depth

## Output

Each problem → ONE file at:
`F:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/harmonia_D_{NN}_{slug}.md`

Standard template + verdict tags + per-attack metadata.

## Tools

WebSearch + WebFetch (arxiv); Python for finite-model exploration where
applicable; reference standard set theory texts (Jech, Kunen).

Note: many of these problems have a particular flavor of obstruction
involving INDEPENDENCE of ZFC — flag this explicitly in your kill_path
classification when it arises.

## Your 5 problems

### Problem 1 — Singular Cardinals Hypothesis (SCH)

**Statement:** For every singular cardinal κ, if 2^cf(κ) < κ, then
κ^cf(κ) = κ⁺.

**Why this is in your batch:** known to be independent of ZFC. Failure
of SCH requires large cardinal axioms (measurable cardinals). Magidor's
1977 model shows SCH can fail. Active research on which large cardinal
strength is exactly needed.

**Your task:** survey the Magidor failure construction, the
Gitik-Mitchell large-cardinal lower bounds, identify the precise
consistency-strength gap that remains open, document the obstruction
class (this is "PROVABLY INDEPENDENT of ZFC; question is consistency
strength of failure" — distinct from "open problem").

**Anchor literature:** Silver 1974; Magidor 1977; Gitik-Mitchell 1996;
Jech "Set Theory"; Cummings "Iterated forcing and elementary embeddings";
Sargsyan-Trang on inner model theory.

**Slug:** `01_singular_cardinals_hypothesis`

---

### Problem 2 — Vopěnka's Principle (consistency strength placement)

**Statement:** For every proper class of structures of the same type,
there exist two structures, one elementarily embeddable in the other.

**Why this is in your batch:** Vopěnka's Principle is a large cardinal
axiom whose precise consistency strength among the canonical hierarchy
is debated. Equivalent to many statements (e.g., every locally
presentable category has a small dense subcategory).

**Your task:** survey the precise position of Vopěnka in the large-cardinal
hierarchy (between extendibles and 1-extendibles), identify which
existing axioms it implies / is implied by, and document the open
questions about its precise placement.

**Anchor literature:** Vopěnka original; Adamek-Rosicky "Locally
Presentable and Accessible Categories"; Bagaria 2010 study of
Vopěnka principle equivalences; Kanamori "The Higher Infinite."

**Slug:** `02_vopenka`

---

### Problem 3 — Whitehead Problem (specific instances)

**Statement:** Every abelian group A with Ext¹(A, Z) = 0 is free.

**Why this is in your batch:** Shelah 1974 proved this is INDEPENDENT
of ZFC. True under V=L; false under MA + ¬CH. The general statement is
settled, but specific instances and refinements continue to generate
open questions (e.g., for specific cardinal classes).

**Your task:** survey Shelah's independence proof, identify which
specific group-theoretic refinements remain open (e.g., for specific
cardinality classes), and document the kill_path: this is the canonical
example of "the SUBSTRATE itself (ZFC) is the obstruction."

**Anchor literature:** Whitehead conjecture origin; Shelah 1974 (Israel
J. Math); Eklof "Whitehead Problem revisited"; Shelah "Proper and
Improper Forcing" later chapters.

**Slug:** `03_whitehead`

---

### Problem 4 — Generalized Continuum Hypothesis (specific cardinals)

**Statement:** For every infinite cardinal κ, 2^κ = κ⁺.

**Why this is in your batch:** Cohen 1963 showed 2^ℵ₀ = ℵ₂ is consistent
(failure of CH at ℵ₀). Easton's theorem 1970 showed 2^κ for regular
cardinals can be almost arbitrary. Singular cardinals (cf. SCH above)
are MORE restrictive.

**Your specific attack:** pick a specific singular cardinal (e.g.,
ℵ_ω), survey what's known about possible values of 2^ℵ_ω (Shelah's
PCF theory), identify which specific values remain unknown, document
the cosmic structure that resists decision.

**Anchor literature:** Cohen 1963/1966; Easton 1970; Shelah's PCF theory
(Cardinal Arithmetic 1994); Gitik on possible cofinalities; Foreman survey.

**Slug:** `04_gch_singular`

---

### Problem 5 — Forcing Axioms Compatibility

**Statement (one form):** Are forcing axioms PFA, MM (Martin's Maximum),
SPFA mutually compatible? Specifically: is the consistency strength of
PFA + Cont₂ characterized?

**Why this is in your batch:** very active area. Aspero-Schindler 2021
proved Mathematical Maximum (MM⁺⁺) implies (*), settling a long-standing
question. But many compatibility questions between forcing axioms remain.

**Your task:** survey the Aspero-Schindler result and identify which
forcing-axiom-compatibility questions remain open. Document the
particular obstruction class for these (which combines large cardinal
strength + forcing combinatorics).

**Anchor literature:** Foreman-Magidor-Shelah 1988 (MM); Todorcevic on
PFA; Aspero-Schindler 2021 (Annals); Woodin's (*); Larson "The Stationary
Tower."

**Slug:** `05_forcing_axioms`

---

## Why this batch is coherent

All 5 problems share a distinctive obstruction pattern: the SUBSTRATE
ITSELF (ZFC) is sometimes the obstruction. Independence proofs are a
SPECIFIC class of "kill_path" — not "the conjecture is false" and not
"the conjecture is unprovable in this attack" but "the conjecture is
unprovable in our axiom system" or "the conjecture's truth-value is
not determined by our axioms."

This is substrate-grade negative-space data of a special kind: questions
where the FALSIFICATION SHAPE is "independence." For Prometheus's
substrate, this corresponds to kill_paths that involve "the falsification
battery cannot determine this with current axioms" rather than "passes/fails
the battery."

## When you're done

Report back with: 5 attempt files, paragraph summary specifically noting
which problems involve INDEPENDENCE-style obstruction vs OPEN-question-style
obstruction (this distinction is itself substrate-grade), any
methodological insights about how independence proofs themselves work
as a kind of "kill."

— Begin.
