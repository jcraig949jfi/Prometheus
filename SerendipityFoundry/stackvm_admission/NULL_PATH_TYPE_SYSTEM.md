# Null-Path Type System

Enforces Constitutional Rule A in code rather than in prose.

> **HINDSIGHT IN THE HYPOTHESIS IS FREE. HINDSIGHT IN THE NULL IS FATAL.**

## Why this is a type system and not a policy

The formal content of Rule A: a candidate `c` is corpus-measurable. If the
null distribution **given** `c` does not depend on the corpus, then for **any**
corpus-measurable selection rule, `P(reject | H0(c), c) <= 1/K`. No
multiplicity correction is owed for the search, however many millions of
hypotheses it examined. That is why aggressive archaeology is licensed at all.

The premise is "the null does not depend on the corpus". If the reference
sampler, matching law, context family, exclusions, or stopping rule is fitted
to the corpus, the premise fails and the bound is void — silently, with every
record looking correct. A prior review established that schema separation of
record *files* is theater with respect to this failure, because the
corpus-derived number does not appear in a field named "historical statistic";
it appears as a **sampler parameter**, which the schema regards as legitimate.

So the enforcement point is the null path itself.

## The four tags

| tag | meaning | legal on null path |
|---|---|---|
| `SPEC_DERIVED` | read from interpreter / opcode / operator **source**: the design of the instrument, never an observation from it | yes |
| `PROTOCOL_CONSTANT` | fixed by the admission protocol independently of this substrate's history | yes |
| `EXTERNAL_RANDOMNESS` | beacon-derived, created after the registration commit | yes |
| `CORPUS_DERIVED` | computed from, fitted to, selected because of, or justified by recorded outcomes | **NO — type error** |

## The null path

All fourteen fields must be present and tagged; an **unlisted extra field is
refused**, because an undeclared knob is how a corpus-derived value hides:

`reference_sampler`, `reference_config`, `context_family`, `context_arity`,
`matching_law`, `role_rule`, `tie_rule`, `betting_rule`, `exclusions`,
`stopping_rule`, `observable`, `max_steps`, `n_references`, `n_blocks`.

## Enforcement, and its limits

**Enforced at construction (`provenance.NullPath`):**
1. `CORPUS_DERIVED` anywhere → `ProvenanceError`.
2. Untagged raw value → refused.
3. Missing field → refused.
4. Undeclared extra field → refused.
5. `SPEC_DERIVED` without `source_file` + `source_symbol` → refused (a spec
   claim with no citation is an assertion, not provenance).
6. Empty justification → refused (an unstated reason is indistinguishable from
   a corpus-derived one).

**Verified on demand (`verify_spec_citation`):** the cited file exists, still
hashes to its pinned value, and contains the cited symbol.

**NOT ENFORCED — the residual, stated plainly.** *A tag is not
self-certifying.* A determined registrant can cite a real symbol for a value
they chose for corpus reasons. The hostile suite demonstrates the three
surviving channels and the checks that catch each:

* **A2 — true citation, false value.** Config mislabelled `SPEC_DERIVED` with
  a real symbol but doctored numbers. Caught only by **comparing the value to
  the cited spec symbol**, which the constructor does not yet do (the hostile
  test does). *Fix: value-vs-spec comparison in the constructor.*
* **B2 — late-fixed protocol constant.** The same value relabelled
  `PROTOCOL_CONSTANT`. Caught by `fixed_at_seq`: a constant fixed **after**
  corpus inspection is provenance-suspect and must be declared as such.
* **C1 — sampler selection.** Each of R1/R2/R3 is individually corpus-free,
  but **choosing among them because the candidate looks extreme under one** is
  null-fitting by selection, and no per-value tag can see it. *Fix: the
  sampler must be pre-registered before candidate inspection.* This is the
  deepest residual and it is a protocol requirement, not a type check.
* **D2 — derived-feature laundering.** "Length is a spec quantity" is true;
  the *band boundaries* are corpus-derived. A spec-legitimate feature can
  carry a corpus-fitted threshold. Caught by requiring thresholds to be
  separately tagged.
* **F2 — self-incriminating justification.** A `PROTOCOL_CONSTANT` whose own
  justification text cites the corpus. Machine-checkable by scanning
  justification strings for corpus references — cheap, and it works, but only
  against honest self-description.

## Results

`hostile_null.py`: **13 / 13 attacks defended** across corpus-fitted reference
laws, parameter-value encoding of corpus observations, sampler-selection
smuggling, tag stripping, derived-feature laundering, undeclared knobs,
context gerrymandering, and support-preserving doctored laws.

The one attack class the type system does **not** decide is deterministic
verdict precomputation (E1) — that is an empirical property measured by the
verdict-entropy harness, and the finding there is that the **level check**,
not entropy, is what refuses it. See `VERDICT_ENTROPY_THEORY.md`.
