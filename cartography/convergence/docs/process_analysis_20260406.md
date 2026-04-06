# Process Analysis — 2026-04-06
## 37 cycles, 80 threads, 63K tokens analyzed

---

## CRITICAL ISSUES (fix now)

### 1. LLM passes string placeholders instead of real data to search functions
**Evidence:** oeis_find_containing 78% empty, oeis_terms 73% empty. The LLM writes
`"integers": "[list of knot determinants]"` instead of actual numbers.
**Impact:** 78% of OEIS cross-domain searches are wasted.
**Fix:** Pre-populate search params with real data from prior search results.
When the hypothesis references knot determinants, inject the actual determinant
list from knots_determinant_list() into the search params before dispatch.
This is a search-plan enrichment step — computational, no LLM needed.

### 2. Battery skips on 75% of threads due to insufficient numerical data
**Evidence:** 37/50 threads skip battery. Most are "Insufficient numerical data."
**Impact:** Only 25% of threads get real statistical testing.
**Fix:** The _extract_numerical_groups function needs more strategies. Currently
it only finds paired arrays from rank_comparison or conductor_distribution.
Add: extract from knots_determinant results, from fungrim symbol counts,
from ANTEDB bound values. Any two numerical arrays from different datasets
should be battery-testable.

### 3. JSON parse failures waste 19% of token budget
**Evidence:** 12 retries across 37 cycles = 12K tokens wasted.
**Impact:** ~19% of total tokens spent on retries.
**Fix:** Two approaches: (a) Use structured output mode for providers that
support it (OpenAI has json_mode). (b) Better prompt engineering — shorter,
more constrained, with a working example in the prompt.

## MODERATE ISSUES (fix this week)

### 4. Dead search functions pollute the search space
**Evidence:** oeis_keyword 100% empty (corrupted names.gz), knots_crossing
100% empty (LLM passes strings). These waste search slots.
**Fix:** Disable oeis_keyword until names.gz is fixed. Add type coercion
for knots_crossing (cast string to int). Track per-function success rates
and auto-disable functions below 10% success after 20+ calls.

### 5. lmfdb_neighbors always errors (14/21 = 67% error rate)
**Evidence:** LLM invents labels like "sample_label" that don't exist.
**Fix:** Remove from LLM prompt or require labels from a prior search result.
This function only works as a chained query, not standalone.

### 6. Battery data extraction too narrow
**Evidence:** Only recognizes values_r0/values_r1 and bin count arrays.
**Impact:** New datasets (knots, fungrim, antedb) never produce battery-testable data.
**Fix:** Add extraction strategies for each new dataset:
  - KnotInfo: determinant array vs conductor array (cross-dataset)
  - Fungrim: symbol frequency vector per module (distribution test)
  - ANTEDB: numerical bound values (exponent comparison)

## INSTRUMENTATION TO ADD

### 7. Per-function success rate tracking
Track: calls, successes, empties, errors per search function across cycles.
Auto-flag functions with <20% success rate. Log to tensor_review.

### 8. Hypothesis quality score
Track: what % of a hypothesis's searches returned useful data?
A hypothesis where 3/3 searches work is higher quality than 1/3.
Log this as "search_plan_quality" in the cycle log.

### 9. Branch outcome tracking
Track: which branch types (refinement, normalization_pivot, adjacent_parameter,
cross_family, data_refinement) produce surviving hypotheses in downstream cycles?
This tells us which branching rules are productive.

### 10. Token waste categorization
Break down token spend: generation (useful), retries (waste), NLI checks (cheap gate).
Target: <10% waste rate.

---

## PRIORITY ORDER
1. Fix string placeholder injection (biggest waste)
2. Add battery extraction for new datasets
3. Enable JSON mode for OpenAI
4. Disable/fix broken search functions
5. Add per-function success tracking
6. Add branch outcome tracking
