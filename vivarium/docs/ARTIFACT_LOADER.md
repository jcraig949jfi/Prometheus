# The artifact loader

*Vivarium, 2026-09-09. H0–H5 design v0.1, contract C1. Implements the loader
vertical slice: the first thing that has ever reached a Vivarium executor from
outside its own sealed spec.*

## The sentence the whole thing turns on

> A slot names bytes by their **digest**; a locator says **where a copy of them
> might be found**; and preflight is the thing that refuses to let the second
> decide anything the first did not already fix.

Vivarium exists so that a difference between two arms is attributable to
SELECTION and not to execution. An artifact input is the first real chance to
reopen that hole, and the closure is arithmetic rather than diligence:

* the **digest** lives in `work.payload`, therefore inside `spec_hash`. Change
  the bytes an experiment consumes and you have changed its sealed identity.
* the **locator** is not in the spec. It rides on the queue row and reaches
  preflight only.
* preflight verifies the resolved bytes against the sealed digest. So a locator
  has exactly two possible effects: the declared bytes arrive, or the attempt is
  **rejected**. There is no third outcome in which a locator changes what the
  experiment computes.

`tests/test_h0h5_artifacts.py` asserts that by running one spec through two
different locators over byte-identical artifacts and comparing the results.

## The slot

An artifact-consuming kind declares which of its parameters are slots. A slot's
keys are exact — the same rule the payload contract already applies, one level
down:

```json
"failure_inputs": {
  "digest":         "sha256:<64 lowercase hex>",
  "artifact_type":  "failure_input_set",
  "schema_version": "1",
  "codec":          "canonical-json-v1",
  "expected_bytes": 146,
  "interface_id":   "boolean-inputs-v1"
}
```

Every value must be resolved at admission. Placeholders never enter the queue.

## The address book

A third category beside sealed input and provenance, on its own queue column
(`artifact_locators`, migration 004), keyed by digest:

```json
{"sha256:bb2e…": {"source_world": "wld_…", "source_artifact": "sha256:22e9…"}}
```

Keyed by digest and not by slot name for two reasons: a dependency four levels
into a closure addresses the same way a root does, and a book keyed by digest
cannot carry an entry the sealed spec never mentions. It is frozen by the same
trigger that freezes provenance — re-addressing a claimed row would make it a
record of two resolutions wearing one identity.

`source_world` and `source_artifact` are refused if they contain a moving name,
a pattern or a URL (`latest`, `*`, `://`, `HEAD`, `..`). C1 forbids mutable
lookups, and the only way to keep that promise is to refuse the syntax.

## Preflight, in order

Each step is a rejection condition evaluated before the next one allocates:

| # | step | refuses with |
|---|---|---|
| 1 | exact slot keys, exact locator keys, resolved values | `CONTRACT_INVALID`, `MUTABLE_LOOKUP`, `LOCATOR_MISSING` |
| 2 | debit the enforceable byte counter **before** the fetch | `BudgetExhausted` (a distinct status, not a rejection class) |
| 3 | resolve through the engine's world-scoped read | `UNAUTHORIZED`, `ABSENT` |
| 4 | size is the declared count, within per-artifact and total limits | `SIZE_MISMATCH`, `OVERSIZE` |
| 5 | bytes hash to the **sealed** digest | `DIGEST_MISMATCH` |
| 6 | decodes, and re-encodes to identical bytes | `MALFORMED` |
| 7 | the content's own header agrees with the slot | `WRONG_TYPE` |
| 8 | the interface's shape check passes | `INCOMPATIBLE_INTERFACE`, `LIMIT_EXCEEDED` |
| 9 | closure resolved, depth/count bounded, cycles refused | `MISSING_DEPENDENCY`, `DEPENDENCY_CYCLE`, `LIMIT_EXCEEDED` |
| 10 | immutable inputs constructed; the kind is called with no client | — |

A rejection is an **operational receipt**: no experiment is committed, no work
claimed, nothing measured, and therefore no observation and no fossil. That is
guaranteed by WHERE preflight runs — before the SFE commit — rather than by
anything the code promises afterwards.

## Four things worth knowing

**A digest is not authority.** Nothing fetches bytes by digest. Resolution goes
through `GET /worlds/{execution_world}/artifacts/{id}/content`, which serves
content only to a caller who owns that world. Authorization is the engine's
decision every time; the loader can ask and be refused, and nothing more.

**The cache is keyed by authorization, not by digest.** The obvious
`digest -> bytes` cache is a permission bypass: once anyone has loaded an
artifact, the next caller gets a hit and the world-scoped read that WAS the
authorization is never performed. Entries here record who was authorized for
them; a caller outside that set misses, re-resolves, and is refused by the
engine. `refused_hits` counts those events, so the receipt shows the bypass
being declined rather than asserting it cannot happen.

**Load once, then use what was verified.** The verified bytes are retained for
the attempt and handed to the kind. Preflight never verifies one fetch and
executes a second — that check/use gap is how a content-addressed store still
ends up running unverified bytes.

**A content-addressed cycle cannot be constructed at all.** A can name B only if
A's bytes contain sha256(B), and B can name A only if B's bytes contain
sha256(A); each hash is required as an input to the other's preimage. The cycle
guard is therefore defence in depth against a resolver serving bytes that do not
match their digest — and the digest check already refuses that. Saying so is
better than implying the guard is load-bearing.

## The execution world

Derived from the sealed spec, never supplied. A spec with **no** artifact slot
creates exactly the world it always did: `ISOLATED`, no budget. A spec **with**
slots gets `EXPLICIT_IMPORT_ONLY` and an enforceable `artifact_bytes` budget,
because it needs a world that can legally accept an import and a counter that
can refuse one. Both are functions of the kind's declaration, so two
byte-identical specs still produce two byte-identical worlds.

## The alpha resource profile

`python -m viv.cli limits` prints it and measures its enforcement on the host,
so the profile in the code and the profile in a document cannot drift.

    total_bytes         16 MiB     per_artifact_bytes   4 MiB
    max_items           4096       max_depth            3
    max_closure         16         max_trace_bytes      8 MiB

    enforceable   artifact_bytes, wall_seconds
    measured      cpu_seconds, peak_memory_bytes, artifact_fetches, items_loaded
    unavailable   gpu_seconds        (NOT zero)

`artifact_bytes` earns *enforceable* because it is debited on the execution
world before each fetch and the engine blocks; `wall_seconds` because the repeat
budget is checked before each repeat — it cannot interrupt one already running,
and the receipt says so. Peak memory is process-scoped and marked never
additive.

## Adding a new artifact-consuming kind

1. Add the artifact type and its interface checker to `viv/artifacts.py`
   (`ARTIFACT_TYPES`, `INTERFACES`). An interface belongs to exactly one type.
2. Register the kind in `viv/kinds.py` with `artifact_slots={...}` naming the
   payload keys that are slots, and a `result_schema`.
3. Write the executor to take `(payload, *, seed, inputs)`. It gets frozen data
   and no client. Bind it in `viv/executors.py`.
4. Pin a parity fixture in `tests/test_wp0f_fixtures.py`.

The executor is refused if it declares slots and arrives without hydration
(preflight was bypassed) or declares none and arrives with inputs (an
undeclared input is an undeclared channel).
