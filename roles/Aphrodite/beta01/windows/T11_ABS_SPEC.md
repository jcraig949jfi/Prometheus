# T11 -- ABSTRACTION-ONLY CANDIDACY UNDER g10 (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 11. Frozen in DEV-11, 2026-10-05, before any T11 transfer data. Rung **R3** (selection
admits a non-generalising library), via an improver-rule change (R7 lever). Evidence tier 2.

## 1. Question
DEV-11's diagnostic (D11_DERIVATION_DIAG.json and donor entries) corrected T09/T10:
- The **MEMORISE** library (stored observed programs) wins g10's net-gain score in T09 seeds 7, 9 and 14 (also under
  g0) and in T10 seeds 6, 12, 13 and 14. It never transfers.
- Its validation savings grow with observation; derivation itself is monotone.

**Does removing non-generalising (memorised) libraries from candidacy -- a content-free rule about candidate type --
raise reusable acquisition?**

## 2. Design
- **Rule:** g11 = g10 with MEMORISE removed from the candidate set before selection. No other change. TAU 1000,
  escrow 30k, PRISTINE start, R_VAL as T51.
- **Arms (new):**
  - **g11 O4:** T09 roles;
  - **g11 O10:** T10 roles;
  - **NULL11 O10:** OFF planted under g11, the gate.
- **Baselines (existing rows, same roles, same deterministic engine):**
  - g10 O4 = T09 g10;
  - g10 O10 = T10 g10;
  - g0 O4 = T09 g0.
- **Known answers (checked in DEV-11 before freeze, beta01/runs/T11_ABS/T11_KNOWN.json): PASS.**
  - **K1:** seed 3, g11 O4 reproduces T09's g10 row exactly. MEMORISE did not win there, so nothing may change.
  - **K2:** seed 13, g11 O10 selects (v - {H}), the max net-gain schema once MEMORISE is removed (from the D11 table).
    This control could have failed.
- **Endpoint:** as T07/T09/T10. PRISTINE walks are reused from T07.
- **Exposure disclosure:**
  - The mechanism was diagnosed on 4 seeds of the same 15 (1, 6, 12, 13) at the selection-table level, and all
    T09/T10 transfer gains were known.
  - There is no fresh seed supply. That is why the readout uses all 15 seeds and pre-registers the cumulative
    comparison against g0.
  - **A positive result here is an exposed-seed result.** Its tier-2 reading is "mechanism-confirming", not
    "independently replicated".
- **Files:**
  - `engine/v2b/t11_absonly.py` sha256 f2b8442e...;
  - t10_observe.py 9ced6b98...;
  - gtc.py e097e1d4...;
  - r7e.py 42e7f387....

## 3. Measurement gate
All three must hold, otherwise MEASUREMENT_FAILED:
- K1 and K2 pass;
- NULL11 O10 selects the planted OFF schema in <= 2/15 seeds;
- total NULL11 <= total g11 O10 + 2.

## 4. Frozen readouts
Each is a one-sided paired sign test over the 15 seeds, requiring p < 0.05 AND a higher total.
- **ABSTRACTION_ONLY_POSITIVE (primary):** g11 O10 vs g10 O10.
- **Secondary:** g11 O4 vs g10 O4.
- **IMPROVER_CUMULATIVE_POSITIVE:** g11 O10 vs g0 O4. This is the full improver change since I_0 (subset criterion
  + observation breadth + abstraction-only candidacy) against the historical rule, on the same seeds and the same
  validation draw.
- **Also reported:**
  - seeds where MEMORISE is still selected (it must be 0 in g11 arms; a mechanical check);
  - per-seed selections;
  - seed 1, the validation-to-transfer mismatch between two real abstractions, which g11 does not address.

## 5. Interpretation (frozen)

| Result | Reading |
|---|---|
| PRIMARY positive | memorisation competing in selection was a binding R3 limit. An abstraction-only rule lets observation breadth convert into reusable improvement |
| CUMULATIVE positive | a measurably better improver than I_0, through three content-free rule changes, each localised by the preceding test (R7, tier 2, exposed seeds). Still first-order: NOT R8, NOT RSI |
| Neither, gate passed | removing memorisation exposes the next limit: validation-to-transfer mismatch among real abstractions (seed-1 type) and starvation (seed 12) |
| Gate failed | nothing is read |

## 6. Compute
- **Donors:** 45 (15 x 3 arms), about 1.3 core-h.
- **Walks:** new libraries only, about 0.3 core-h.
- **Budget:** the rolling 24 h was about 44 core-h at 13:45Z and falls until 14:43Z as T53 rolls off. Fits under 48.
- **Host:** HARRY1, 4 workers, threads = 1.
