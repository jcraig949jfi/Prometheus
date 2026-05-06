# TRACE Preservation Audit — BIND/EVAL bound symbols

**Date:** 2026-05-05
**Auditor:** Techne
**Scope:** Pre-Tier-0 step 0c per substrate v2.3 §6.0 + Aporia Study 12 open question.
**Question:** *Do BIND/EVAL-bound proof tactics preserve content-addressed provenance through TRACE, or does TRACE see only outer calls?*
**Verdict:** **Invariant HOLDS.** Documented as a load-bearing property. One adjacent gap surfaced (BIND/EVAL evidence does not currently carry caveats); flagged as follow-up, NOT a TRACE bug.

---

## TL;DR

Content-addressed provenance is preserved through TRACE for BIND/EVAL-bound symbols. The chain works as follows:

1. **`BindEvalKernelV2.BIND`** mints a CLAIM whose `evidence` dict contains `callable_hash` (sha256 of the callable's source via `inspect.getsource`).
2. **`SigmaKernel.PROMOTE`** scrapes 64-char-hex strings out of the claim's evidence into the resulting Symbol's `provenance` list (canonical kernel behavior; line ~830 of `sigma_kernel.py`).
3. **`SigmaKernel.TRACE(symbol)`** walks `symbol.def_hash → symbols.provenance_children` recursively.
4. The callable_hash IS in the symbol's provenance. When `walk(callable_hash)` runs, the lookup in the `symbols` table fails (the callable's source is not a substrate Symbol — it's external code), and the walker correctly tags the node `{"hash": ..., "type": "external"}`.

This is the intended behavior. The audit's finding is that the **substrate distinguishes "internal" provenance (kernel-tracked symbols whose lineage continues to recurse) from "external" provenance (content-addressed but not substrate-resident)**, and BIND/EVAL bindings correctly fall into the latter category for the callable's source while remaining FULLY in the former category for downstream symbols that depend on the binding.

---

## What was audited

### Code paths examined

| File | Lines | What I looked at |
|---|---|---|
| `sigma_kernel/sigma_kernel.py` | 999–1058 | `SigmaKernel.TRACE` implementation — walks def_hash + provenance, extracts caveats + precision_metadata from def_blob, cycle-safe via visited set. |
| `sigma_kernel/sigma_kernel.py` | ~820–900 (PROMOTE) | The provenance-scraping step: 64-char-hex strings in evidence are pulled into the Symbol's provenance list. |
| `sigma_kernel/bind_eval_v2.py` | 136–280 (BIND) | Mints a CLAIM via `kernel.CLAIM(...)` with evidence dict carrying `callable_hash` + cost_model + postconditions + authority_refs. Claim → FALSIFY → GATE → PROMOTE produces the binding Symbol. |
| `sigma_kernel/bind_eval_v2.py` | 280–500 (EVAL) | Reads a binding by ref, mints an EVAL claim whose evidence carries the binding's def_hash + input_hash + output_hash. PROMOTE scrapes both hashes into the EVAL Symbol's provenance. |
| `sigma_kernel/test_bind_eval_v2.py` | 580–620 | Existing test (`test_trace_walks_bind_to_eval_chain`) that confirms TRACE walks across BIND→EVAL chains. Test passes today. |

### What I did not need to look at

- `sigma_kernel/bind_eval.py` (v1 — superseded by v2 per the 2026-05-03 team review).
- The Postgres-side TRACE behavior (the Sqlite TRACE is the canonical implementation; Postgres is a future-port concern documented separately in `PRECISION_METADATA_SPEC.md`).

---

## Three TRACE chain scenarios (analysis)

### Scenario A: TRACE from a downstream symbol that depends on a BIND'd callable

```
my_downstream_symbol
  └── (def_blob references binding_symbol's def_hash via TRACE-scrapeable evidence)
binding_symbol
  └── provenance: [callable_hash, input_hash_of_BIND_verdict, ...]
       ├── walk(callable_hash) → {"type": "external"}   [callable source — not substrate]
       └── walk(input_hash_of_BIND_verdict) → {"type": "external"}   [verdict input hash — not substrate]
```

**Audit finding:** TRACE walks `my_downstream_symbol → binding_symbol` correctly because the binding_symbol's def_hash IS a substrate Symbol. From `binding_symbol`, TRACE reaches the callable_hash, which is correctly tagged "external" because the callable source is not a Symbol.

This is the desired behavior. The callable source is external code (potentially in a third-party library); it should NOT be recursively walked. But its hash IS preserved in the trail, so an auditor can verify "this binding references callable with hash X, and X has not changed since BIND time."

### Scenario B: TRACE from an EVAL Symbol

```
eval_symbol (from EVAL of my_binding on input X producing output Y)
  └── provenance: [binding_symbol.def_hash, input_hash, output_hash, eval_verdict_input_hash]
       ├── walk(binding_symbol.def_hash) → recurses into binding_symbol (Scenario A continues)
       ├── walk(input_hash) → {"type": "external"}   [input data — not substrate]
       ├── walk(output_hash) → {"type": "external"}   [output data — not substrate]
       └── walk(eval_verdict_input_hash) → {"type": "external"}
```

**Audit finding:** EVAL's provenance correctly includes the binding's def_hash AS A SUBSTRATE SYMBOL (recursive walk continues from there) and the input/output/verdict hashes as external content-addressed leaves. Confirmed by reading bind_eval_v2.py EVAL implementation + the existing `test_trace_walks_bind_to_eval_chain` test that asserts the binding Symbol appears in the EVAL Symbol's TRACE walk.

### Scenario C: TRACE from a chain of BINDs (BIND_A → BIND_B that calls A's binding)

```
binding_B_symbol
  └── provenance: [callable_hash_B, bind_A_callable_hash_referenced_inside_B, ...]
       ├── walk(callable_hash_B) → {"type": "external"}
       └── walk(bind_A_callable_hash_referenced_inside_B) → {"type": "external"}
              [unless B's callable explicitly references A's binding by symbol ref —
               in which case A's def_hash IS in B's provenance and recurses]
```

**Audit finding:** Chain-of-BINDs preserves provenance correctly when one binding's callable explicitly references the other binding by name (the binding's def_hash gets scraped into evidence). When one binding references another only via callable source mention (string match), the relationship is NOT captured in TRACE — that would require source analysis the substrate does not perform.

This is documented as a known limitation. Callers wanting B → A traceability should explicitly reference A's binding-symbol-ref in B's `authority_refs` parameter to BIND, which IS scraped into provenance.

---

## Caveats and precision_metadata propagation through TRACE

Re-reading `sigma_kernel.py` lines 1027–1054: TRACE extracts caveats and precision_metadata from each visited Symbol's `def_blob` (parsed as JSON) and includes them in the returned tree.

```python
if isinstance(blob, dict) and "caveats" in blob:
    cv = blob["caveats"]
    if isinstance(cv, list):
        caveats = [str(c) for c in cv]
if isinstance(blob, dict) and "precision_metadata" in blob:
    pm = blob["precision_metadata"]
    if isinstance(pm, dict):
        precision_metadata = dict(pm)
```

`collect_caveats(symbol)` (lines 1060–1080) walks the TRACE tree and unions all caveats across visited nodes — this is the "citation-grade caveat" helper.

**Audit finding:** caveats and precision_metadata propagate correctly through TRACE for any Symbol whose def_blob includes them. **However**, the BIND/EVAL evidence dict (built in `bind_eval_v2.BIND` lines 179–187) does NOT currently include a `caveats` key. So a BIND'd Symbol's def_blob will NOT carry caveats unless the caller explicitly passes them through some other mechanism.

This is an adjacent gap, not a TRACE bug. See "Follow-up issue" below.

---

## Conclusion

> **The TRACE-preservation invariant for BIND/EVAL holds.** Content-addressed provenance from BIND'd callables and EVAL'd evaluations IS preserved through TRACE walks. Callable sources are correctly tagged as "external" leaves rather than being recursively walked (which is the right behavior — they are not substrate data). Downstream symbols depending on bindings via authority_refs get correct recursive traversal. Caveats and precision_metadata propagate through TRACE for any Symbol whose def_blob carries them.

**Status:** Documented invariant. No code change required.

**Test coverage:** Existing `test_bind_eval_v2.py::test_trace_walks_bind_to_eval_chain` validates the BIND → EVAL recursive walk. Existing `test_caveats.py::test_trace_propagates_caveats` validates caveat propagation. Existing `test_precision_metadata.py::test_trace_propagates_precision_metadata` validates precision_metadata propagation. No new tests required for this audit.

---

## Follow-up issue (NOT a TRACE bug; flagged for v2.3 Tier 1 work)

**Issue:** `BindEvalKernelV2.BIND` and `BindEvalKernelV2.EVAL` build their CLAIM evidence dict without including a `caveats` field. So a binding/evaluation Symbol's def_blob will not carry caveats unless the caller threads them in via some other mechanism.

**Impact:** Caveats associated with a BIND/EVAL operation (e.g., "this binding bypasses authority validation", "this evaluation used a stale catalog snapshot") are not propagated to downstream symbols via TRACE.

**Severity:** Low for v0.5/v1.0 work — current callers do not attach BIND-time caveats. Medium for v1.0+ when authority_refs become more nuanced.

**Recommendation:** When P3 MethodSpec lands (Day 5), add an optional `caveats: list[str]` parameter to `BindEvalKernelV2.BIND` and `EVAL`. The MethodSpec.drift_channel will likely surface intensional-vs-behavioural drift caveats that should attach at BIND time. The change is one extra dict key + one new parameter; backwards-compatible.

**Tracking:** logged here for v2.3 Tier 1 backlog. Not blocking Pre-Tier-0 completion.

---

## Architectural commitment (locked)

This audit codifies the following as a substrate-grade invariant going forward:

> **Every BIND/EVAL operation preserves content-addressed provenance through TRACE. Bound callable sources are tagged as "external" leaves (correctly — they are not substrate data); their hashes are preserved. Downstream symbols that depend on a binding via `authority_refs` have a recursive TRACE walk that reaches the binding Symbol and beyond.**

Future BIND/EVAL extensions (e.g., proof-primitive sub-namespace per substrate v2.3 §8 control-plane vs data-plane lock-in) MUST preserve this invariant. Any change to BIND/EVAL evidence shape or PROMOTE provenance-scraping rules requires:

1. A re-run of this audit's three scenarios.
2. Updated tests covering the new shape's TRACE walk.
3. A commit message that explicitly references this audit doc.

---

*— Techne, 2026-05-05*
