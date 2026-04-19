# Track A — Methodology Tightener

**Role:** Methodology Tightener (combines A1 null-protocol + A2 algebraic-identity audit)
**Delegated:** 2026-04-19 by Harmonia sessionA
**Status:** in flight
**Expected deliverables:**
  - `harmonia/memory/symbols/protocols/null_protocol_v1.md`
  - `cartography/docs/cell_null_classification.json`
  - `harmonia/memory/algebraic_coupling_audit.md`
  - `NULL_PROTOCOL_READY` + `IDENTITY_AUDIT_READY` sync messages

---

## Paste-ready prompt

```
You are [Harmonia sessionD or Mnemosyne] — whichever has tick budget.
Role: Methodology Tightener. Combined job: define the null-protocol
discipline and sweep for algebraic-identity coupling before the next
volume push.

Working directory: Prometheus clone. Pull latest first.

Read first:
  harmonia/memory/decisions_for_james.md  — retraction cascade from
      external review (F043 etc.); the critique motivating this role
  harmonia/memory/pattern_library.md     — Pattern 30 DRAFT is the
      diagnostic check you'll apply
  harmonia/memory/TENSOR_REDIS.md
  harmonia/memory/symbols/NULL_BSWCD.md   — v2 spec
  harmonia/memory/build_landscape_tensor.py  — F-ID descriptions

Redis access:
  from agora.tensor import features, feature_meta, resolve_cells,
                           resolve_row
  from agora.symbols import resolve

Task A1 — Null protocol per claim class (primary deliverable):
  Write harmonia/memory/symbols/protocols/null_protocol_v1.md that
  lists each of the five claim classes we have F-IDs for, and for
  each class, specifies which null operator is appropriate:
    - Class 1 (moment/ratio under conductor scaling): NULL_BSWCD@v2
      with stratifier=conductor_decile
    - Class 2 (rank-slope interaction): NULL_BSWCD@v2 with
      stratifier=rank_bin (NOT conductor — the claim is about rank
      structure)
    - Class 3 (stratum-uniform claims like F015 sign): NULL_BSWCD@v2
      with stratifier=the-stratum-being-tested
    - Class 4 (construction-biased samples like F044 rank-4 curves):
      NULL_BSWCD is INSUFFICIENT. Document that a
      frame-based resample or a model-based null is required; flag
      any current +1 or +2 cells on such features as PROVISIONAL
      pending better null
    - Class 5 (algebraic-identity claims): NO null applies. Refuse
      to run. Flag for Pattern 30 check instead.

  For each existing +2 cell in the tensor, tag it in the JSON sidecar
  (cartography/docs/cell_null_classification.json) with its claim
  class per above. Any +2 cell whose null was NULL_BSWCD@v2 with
  stratifier=conductor but whose claim is actually class 2, 3, or 4:
  flag for re-audit.

Task A2 — Algebraic-identity sweep (parallel):
  Walk every F-ID description. Apply Pattern 30 DRAFT's diagnostic
  checklist:
    1. Write Y in terms of observable atomic quantities
    2. Does X (or log X) appear as a term or factor?
    3. If yes, is the coefficient non-zero?
    4. If yes, the correlation is algebraic rearrangement, not evidence

  Output harmonia/memory/algebraic_coupling_audit.md with one entry
  per F-ID:
    F-id: <status> (CLEAN | COUPLED | PARTIAL)
    If COUPLED or PARTIAL: cite the algebraic relation and recommend
      action (retract, restate, or add definitional-dependence
      annotation).

  Expected candidates to examine closely (based on which features
  involve BSD factors, Euler products, or rearrangements):
  F003 full-BSD identity, F005 high-Sha parity, F011 (the layer
  split is interpretive but not identity-coupled), F041a moment
  ratios, F045 isogeny murmuration. F043 is already retracted;
  confirm no sibling specimens exist.

Constraints:
  - Do NOT open new specimens
  - Do NOT demote or promote any cells unilaterally — flag for
    conductor (sessionA) review instead
  - Output is documentation + classification, not re-audit execution
  - If Task A2 reveals another F043-class specimen, the retraction
    is sessionA's call, not yours

Output:
  - harmonia/memory/symbols/protocols/null_protocol_v1.md (new)
  - cartography/docs/cell_null_classification.json (new)
  - harmonia/memory/algebraic_coupling_audit.md (new)
  - Commit prefix: "Methodology tightener:"
  - NULL_PROTOCOL_READY + IDENTITY_AUDIT_READY messages on
    agora:harmonia_sync with summary counts (how many cells need
    re-audit; how many F-IDs need retraction review)

Charter context: wave 1 produced one retraction (F043) after external
review; this role prevents the same class of failure from recurring
in wave 2 before we scale density.
```

---

## Background motivation

Derived from external methodological review of `docs/map_building_first_wave.md` (commits 45fd79d5 → df20f900). The review established:

1. Some existing `+2` cells used `NULL_BSWCD@v2[stratifier=conductor_decile]` even when the underlying claim was about rank structure or construction-biased samples — wrong null for the claim class. `+2` cells are therefore not currently cross-row comparable.

2. F043 was retracted as an algebraic-identity artifact (BSD rearrangement). We have no systematic check that other F-IDs are free of similar coupling. A one-time sweep with Pattern 30 DRAFT's diagnostic catches any sibling specimens before wave 2 scales the mistake.

Track A is a prerequisite to Track C (density push). Filling cells with the wrong null creates more retractions later.
