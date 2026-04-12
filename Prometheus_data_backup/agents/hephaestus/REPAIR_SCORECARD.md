# Scrap Repair Scorecard

## Overview

**630 candidates staged** in `scrap_staging/` for repair and re-ingestion into forge.

| Category | Count | % | Repair Difficulty | Est. Token Cost |
|---|---|---|---|---|
| **Trap battery near-misses** (35-49% acc) | 349 | 55.4% | **MODERATE** | ~500/tool |
| **Syntax errors** | 67 | 10.6% | **EASY** | ~200/tool |
| **Name/import errors** | 29 | 4.6% | **TRIVIAL** | ~100/tool |
| **Unicode encoding errors** | 34 | 5.4% | **EASY** | ~150/tool |
| **Type/value errors** | 82 | 13.0% | **MODERATE** | ~400/tool |
| **Other errors** | 9 | 1.4% | **HARD** | ~800/tool |
| **Validation errors** | 17 | 2.7% | **HARD** | ~600/tool |
| **TOTAL** | **630** | **100%** | | |

---

## Detailed Breakdown

### 1. TRAP BATTERY NEAR-MISSES (349 tools, 55.4%)
These compiled and ran, but didn't pass the reasoning tests.

| Accuracy | Count | Status |
|---|---|---|
| 45-49% | 63 | Near-pass; minor logic/calibration issues |
| 40-44% | 144 | Solid foundation; missing ~5-10% on reasoning |
| 35-39% | 142 | Borderline; 5-15% gap from threshold |

**Repair approach:** Load the trap battery results, identify what the tool got wrong, patch the reasoning logic. Most are off by <10 points on accuracy.

**Example:** `ergodic_theory_x_information_theory_x_predictive_coding` — 47% acc, 60% cal. The tool's structure is sound but the scoring function is slightly miscalibrated.

**Success rate estimate:** 40-50% (some are fundamentally unsalvageable, others just need logic tweaks)

---

### 2. SYNTAX ERRORS (67 tools, 10.6%)
Parser rejects the code before it runs.

**Breakdown:**
- Unclosed parens/brackets (15 tools)
- Missing/unexpected indents (12 tools)
- Invalid expressions (40 tools)

**Repair approach:** Syntactic fixes are mechanical. An LLM with access to the error line number can usually fix in one pass.

**Example:** `adaptive_control_x_free_energy_principle_x_proof_theory`
```
validation:syntax_error: '(' was never closed (line 372)
```
One-line fix: find line 372, add missing `)`.

**Success rate estimate:** 70-80% (LLMs struggle less with syntax than logic)

---

### 3. NAME ERRORS / MISSING IMPORTS (29 tools, 4.6%)

**Breakdown:**
- `List`, `Dict`, `Tuple` not imported (18 tools)
- Other stdlib imports (11 tools)

**Repair approach:** Add missing `from typing import ...` or `from collections import ...` at the top.

**Example:** `bayesian_inference_x_genetic_algorithms_x_pragmatics`
```
validation:runtime_error: NameError: name 'List' is not defined
```
One-line fix: add `from typing import List` to imports.

**Success rate estimate:** 95%+ (trivial, only require import injection)

---

### 4. UNICODE ENCODING ERRORS (34 tools, 5.4%)

**Breakdown:**
- Windows `charmap` codec issues with Unicode chars (∈, ≥, ≤, etc.)
- UTF-8 decode errors on file read (16 tools)

**Repair approach:** Replace Unicode mathematical symbols with ASCII equivalents, or fix the encoding. Example: `∈` → `in`, `≥` → `>=`.

**Example:** `abductive_reasoning_x_free_energy_principle_x_type_theory`
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2265'
```
Fix: Replace `≥` with `>=` in the code.

**Success rate estimate:** 85-90% (straightforward character replacement)

---

### 5. TYPE & VALUE ERRORS (82 tools, 13.0%)

**Breakdown:**
- `TypeError`: subscripting floats, type mismatches on operations (28 tools)
- `ValueError`: shape mismatches (numpy), improper dimensions (54 tools)

**Repair approach:** Usually requires understanding what the code intended to do with the data. Harder than syntax errors.

**Example:** `active_inference_x_hebbian_learning_x_compositionality`
```
TypeError: unsupported operand type(s) for +: 'float' and 'list'
```
Likely needs to convert list to scalar or reshape the operation.

**Success rate estimate:** 50-60% (requires logic understanding, not just syntax)

---

### 6. OTHER/HARD ERRORS (26 tools, 4.1%)

**Breakdown:**
- `AttributeError`: None object, missing methods (12 tools)
- `KeyError`: missing dict keys (5 tools)
- Other (9 tools)

**Repair approach:** These indicate structural issues in the code. Requires deeper debugging.

**Example:** `bayesian_inference_x_criticality_x_compositionality`
```
AttributeError: 'NoneType' object has no attribute 'strip'
```
Suggests a method returned `None` when it shouldn't. Requires tracing the logic.

**Success rate estimate:** 30-40% (often symptomatic of deeper design flaws)

---

## Repair Priority (by ROI)

### TIER 1: Do first (highest ROI)
1. **Name/import errors (29)** — 95%+ pass rate, ~50 tokens each = **1,450 tokens, ~27 tools forged**
2. **Syntax errors (67)** — 70-80% pass rate, ~200 tokens each = **9,400 tokens, ~50 tools forged**
3. **Unicode errors (34)** — 85-90% pass rate, ~150 tokens each = **4,100 tokens, ~29 tools forged**

**Tier 1 subtotal:** 130 tools, ~15k tokens, expect **~106 forged** (81% success)

### TIER 2: Do next (moderate ROI)
4. **Type/value errors (82)** — 50-60% pass rate, ~400 tokens each = **32,800 tokens, ~41 tools forged**
5. **Trap battery near-misses (349)** — 40-50% pass rate, ~500 tokens each = **174,500 tokens, ~140 tools forged**

**Tier 2 subtotal:** 431 tools, ~207k tokens, expect **~181 forged** (42% success)

### TIER 3: Do if quota allows (low ROI)
6. **Hard errors (26)** — 30-40% pass rate, ~600 tokens each = **15,600 tokens, ~8 tools forged**

**Tier 3 subtotal:** 26 tools, ~15.6k tokens, expect **~8 forged** (31% success)

---

## Token Budget

- **Tier 1 (quick wins):** ~15k tokens → ~106 tools → **0.14 tokens/tool**
- **Tier 2 (moderate effort):** ~207k tokens → ~181 tools → **1.14 tokens/tool**
- **Tier 3 (hard cases):** ~15.6k tokens → ~8 tools → **1.95 tokens/tool**

**Total budget (all three):** ~238k tokens to repair ~295 tools (47% of 630).

At Haiku rates (~$0.80/1M input), that's **$0.19 for 295 new forged tools**.

Compare: forging 295 new tools from scratch = ~1.5M tokens = **$1.20**.

**Repair is 6x cheaper than forging from scratch.**

---

## Recommended Plan

### Phase 1: Tonight (before 95% quota ceiling)
- Do **nothing**. You're at 90% of 7d.
- Fire up the forge with Sonnet 4.5 on Aggie instead.

### Phase 2: Tomorrow (after 6PM reset, fresh 100% quota)
- **Batch 1:** Tier 1 repairs (130 tools, ~15k tokens, 1-2 hours)
  - These are quick wins. High pass rate.
- **Batch 2:** Monitor quota, do Tier 2 repairs (207k tokens / 630 = 33% of quota)
  - If you have room, start these. High ROI.
- **Batch 3:** Only if quota allows
  - Tier 3 is expensive and low ROI. Save for later.

### Success metric
After tomorrow's repair pass, expect ~**287 tools forged from 630 candidates** (45% recovery rate), at a total cost of ~$0.40.

---

## Notes

- The 281 **validation_error** entries in the original staging list are different — those are tools that failed *before* we could even load them. They're in the "fix first" category.
- The **349 near-misses** are golden — they're architecturally sound but just underperforming on the tests. With tweaks to their scoring/logic, many will cross 50%+ threshold.
- **Unicode errors** are a Windows-specific issue. Replacing math symbols with ASCII is a trivial post-processing step we should add to code generation.

