# SPEC — P4 scoring rule, frozen for independent implementation

**Ergon · SKULLPORT · 2026-08-25 · FROZEN.** Changes require an amendment commit that supersedes
this file by name; silent edits invalidate any comparison made against it.

**Purpose.** This is the complete written specification of the scoring rule on which P4's
four-way conclusion turns. It is written so a second party can implement it **without seeing our
implementation**, and deliberately contains **no worked examples produced by our scorer** —
examples silently transmit an author's reading of ambiguous prose, which is the correlation this
exercise exists to break.

**Two artifacts are wanted, and they test different things.** Please do not conflate them:

- **Implementation B.** Someone implements §§1–9 below, from this text and nothing else.
  Agreement with our implementation tests **coding**.
- **Derivation C.** Someone is given only §0 (the scientific question and the input/output
  semantics) and asked what scoring rule *should* exist — **without** §§4–8 and without either
  implementation. Agreement between C's derived rule and this frozen spec tests something closer
  to **construct validity**.

If only one is available, **C is the more valuable**, because our repeated failures have been
failures of defect-class discovery rather than of coding.

---

## 0. The scientific question and the semantics (this section is what Derivation C receives)

A generator emitted a mathematical claim that was **rejected**. The claim is a relation asserted
between two catalog invariants — e.g. *"invariant X of object P stands in relation ρ to invariant
Y of object Q"* — and it failed.

We want to know two things:

1. **Q1.** If we had changed exactly **one** of the generator's decisions, would the claim have
   come closer to holding?
2. **Q2.** Does the *stored record of the failure* tell us **which** single change to make —
   over and above everything we would know without that record?

A "decision" is one field of the generator's own parameterisation: which relation, which
invariant on each side, which object on each side. Alternatives are **executed exactly** by
looking values up in the frozen catalogs; nothing is estimated and no model is consulted.

**What is needed is a scalar per candidate change, measuring how close the claim came to
holding**, so that the best single change is well defined and "did it improve" is answerable
even when the claim still fails. Given that, `A*` is the best available single change, and Q2 is
a prediction problem: rank the candidates, and see whether the failure record helps.

*(Derivation C: please stop reading here and write down what you think the scoring rule, tie
policy, aggregation and exclusions should be. Then compare.)*

---

## 1. INPUT SCHEMA

One **record** (a rejected claim):

| field | type | missing allowed | notes |
|---|---|---|---|
| `record_id` | string | no | unique |
| `generator_id` | string | no | stratum label; **not** an input to any predictor |
| `relation` | enum | no | one of `equal`, `equal_mod_2`, `divides`, `abs_diff_le_3` |
| `catalog_a`, `catalog_b` | string | no | e.g. `knot`, `ec` |
| `invariant_a`, `invariant_b` | string | no | key into the catalog entry |
| `object_a`, `object_b` | string | no | catalog entry identifier |
| `holds` | bool | no | as recorded by the generator |

One **catalog**: `{schema_version:int, n_entries:int, entries:[ {id, <invariant>: value, ...} ]}`.
Invariant values are integers or reals, or **absent** on a given entry.

A **candidate** is a record with exactly one of
`{relation, invariant_a, invariant_b, object_a, object_b}` replaced.

---

## 2. TARGET — what counts as the true "best local repair"

`A*` is the admissible candidate with the **maximum margin** `m` (§4). It is defined **per
record**, over that record's admitted candidate set (§3), including the **unchanged record
itself** as a candidate — so `A*` may be "change nothing", and `improvement = m(A*) − m(record)`
is then exactly `0`.

---

## 3. ADMISSIBILITY — which candidates exist at all

A candidate is admitted only if **all** hold:

1. the replaced value lies in its domain: `relation` ∈ the four; `object_*` ∈ that catalog's
   entries; `invariant_*` ∈ the set of invariant keys **present on at least one entry** of that
   catalog;
2. **both** invariant values resolve to a number on their respective objects;
3. the margin for the candidate's relation is defined (§4 — note `divides` with divisor `0`).

A candidate failing any of these is **DROPPED and COUNTED** by reason. It is never imputed,
never scored `0`, and never treated as "no improvement" — those are three different things and
collapsing them is a defect.

**Candidate cap.** Each of the five fields is capped at **200** candidates, sampled with a fixed
seed **from the whole domain** (not the first 200). The cap and the drawn fraction are reported.
Consequence to state, not bury: Q1 measures a **sampled** neighbourhood, so its answer is a
**lower bound** on whether an improving change exists.

---

## 4. SCORE — the margin `m`

Let `a` and `b` be the two resolved invariant values. Larger `m` is better; `m ≥ 0` iff the
relation holds.

```
equal          m = -|a - b|
abs_diff_le_3  m =  3 - |a - b|
divides        m = -( |a| mod |b| )      ; UNDEFINED if b == 0  -> candidate DROPPED (§3.3)
equal_mod_2    m = -( (a - b) mod 2 )    ; Python-style mod: result in {0, 1}
```

- Arithmetic is on the values **as stored**; no unit conversion, no normalisation, no rounding.
- If either value is non-integral, `equal`, `abs_diff_le_3` use real arithmetic; `divides` and
  `equal_mod_2` require both values integral — otherwise **DROPPED and COUNTED**.
- **`m` is never compared across relations.** See §7.

---

## 5. PREDICTION — what a candidate system emits

For one record, a **total ordering** (ranking) of that record's admitted candidate set. A system
may instead emit a real-valued score per candidate, from which the ranking is derived; ties in
emitted scores are resolved as in §6.

A system may emit `ABSTAIN` for a record instead of a ranking (§8).

---

## 6. TIES

**In the target.** If several candidates share the maximum margin, **all** of them are `A*` — the
target is a **set**. `top1_correct = 1` iff the system's rank-1 candidate is a member of that set.
`rank_of_A*` = the **best** (lowest) rank the system assigns to any member.

**In the prediction.** Ties in a system's emitted scores are broken by **ascending candidate id**,
where the candidate id is the deterministic string
`f"{field}={new_value}"` sorted lexicographically. Rationale: a fixed, content-independent
tie-break, so tie behaviour cannot be tuned. A system that emits a total ordering directly is
taken as-is.

**Random tie-breaking is not permitted** for any scored system, including baselines. The uniform
random baseline draws its *ranking* from a seeded RNG, which is a different thing and is declared
in §9.

---

## 7. AGGREGATION

**Per relation, always. A figure pooled across relations must not be computed** — the four
margins live on different scales and different populations, and combining them is a
naive-score-combination error.

Within a relation:

- `Q1_share` = (# records with `improvement > 0`) / (# scored records). **Macro over generator
  strata**: compute per stratum, then take the **unweighted mean across strata**, so a
  million-row stratum cannot silently define the result. The micro (row-weighted) value is
  reported beside it; they are not interchangeable and both are required.
- `Q2_top1` = mean `top1_correct`. Same macro-over-strata rule.
- `Q2_mean_rank` = mean `rank_of_A*`, and `Q2_mrr` = mean `1 / rank_of_A*`.

**Standard errors** are computed **over generator strata** (the unit at which the macro mean is
taken), not over rows. A per-row SE on a statistic whose unit is the stratum overstates precision.

**Splits.** Held-out evaluation is grouped by **generator AND by object**: no object appearing in
a training record may appear in a held-out record. Grouping by row is prohibited.

---

## 8. ABSTAINS AND INVALID OUTPUTS

| case | treatment |
|---|---|
| `ABSTAIN` on a record | excluded from `Q2_top1` and the rank statistics; **counted and reported** as `n_abstain`; still counted in `Q1` |
| ranking omits admitted candidates | **INVALID** — the record scores as an error, is counted as `n_invalid`, and the run is flagged |
| ranking includes non-admitted candidates | **INVALID**, same treatment |
| system errors / times out | `n_invalid` |
| record has **zero** admitted candidates | excluded from every statistic; counted as `n_no_neighbourhood` |
| record has exactly one admitted candidate (itself) | `Q1` counts it as no-improvement; excluded from `Q2` (ranking is vacuous) |

**An abstain is never scored as a wrong answer, and never as a right one.** A system that
abstains on everything must produce `n_abstain = N` and no `Q2` figure, not a `Q2` of `0`.

---

## 9. THE COMPARISON SET

Every one of these is scored **by this same rule**, with the **same model class, training budget
and tuning procedure** as the system under test. A tuned treatment against an untuned baseline
measures tuning.

| id | information available |
|---|---|
| B1 | uniform random ranking, seeded |
| B2 | stratum-modal intervention; failure record **not** used |
| B3 | magnitude only: orders of magnitude of the two values |
| B4 | **context-only**: every covariate available at decision time **except** the stored failure record |
| B5 | **context-only local-neighbour**: what repair worked for nearby cases, non-failure coordinates only |
| B6 | **matched shuffled-residue**: identical representation, dimensionality, missingness and pipeline, with the failure record permuted among matched records |
| T | the system under test: context **+** the stored failure record |

**Headline quantities:**

```
Δ_context = T − B4        # does the failure record add information at all?
Δ_matched = T − B6        # does the CORRECT failure-to-case correspondence add information?
```

**T is positive only if `Δ_context > 0` and `Δ_matched > 0`**, both by more than the §7 SE.
Beating B1, B2, B3, B5 is necessary and insufficient.

---

## 10. OUTPUT — required sufficient statistics

Per relation × per stratum × per system:

```
n_records · n_scored · n_abstain · n_invalid · n_no_neighbourhood
n_candidates_admitted · n_candidates_dropped_by_reason{domain, unresolved_value,
                        undefined_margin, non_integral}
candidate_cap · drawn_fraction
Q1_share_micro · Q1_share_macro
Q2_top1 · Q2_mean_rank · Q2_mrr
```

**PER-ROW CONTRIBUTIONS ARE MANDATORY**, not optional, and are the primary comparison artifact:

```
record_id · relation · stratum · m_record · m_Astar · improvement
            |A*_set| · predicted_rank_1_id · top1_correct · rank_of_A*
            admitted_count · dropped_count · abstained
```

Two implementations agreeing on `Q2_top1 = 0.5271` is **weak** evidence. Agreement on the whole
vector of per-row decisions is the comparison that matters, and disagreements on individual rows
are the diagnostic. Please emit the row table.

---

## 11. Notes for the independent implementer

- Implement from this text. Do **not** read `ergon/probe/` sources for P4.
- Where this spec is **ambiguous, do not resolve it silently** — record the ambiguity and your
  choice. An ambiguity found here is a more valuable result than a matching number, because it
  is a defect in the specification rather than in a program, and specification defects are the
  class our own controls cannot catch.
- Deterministic given (records, catalogs, seed). Any nondeterminism is a defect.
- No LLM anywhere in the scoring path.

---

*Ergon · SKULLPORT · 2026-08-25 · frozen for independent implementation.*
