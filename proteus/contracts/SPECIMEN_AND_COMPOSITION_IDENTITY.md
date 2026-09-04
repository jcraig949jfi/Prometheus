# Specimen, registry, primitive, composition and ablation identity — V0

Normative for anything that ships a Proteus specimen across a component boundary.
Status: contract. Implementation: `proteus/compose/segments.py`, `proteus/foundry/identity.py`.
Golden vectors: `proteus/compose/GOLDEN_VECTORS.json` (self-verifying, no Proteus import needed).

Everything below is measured on the committed registry
(`registry_id b15e0a7f5f2dcb99b8b28c73a99441d8d53e82b1bae42fddd5e274eeef396917`, 64 specimens)
unless stated otherwise. Numbers reproduce with the scripts named beside them.

---

## 1. Canonical serialisation — the whole rule

```
canonical_bytes(obj) = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=True).encode("utf-8")
digest(obj)          = sha256(canonical_bytes(obj)).hexdigest()      # lowercase, no prefix
blob_hash            = "sha256:" + digest(manifest)                  # the SFE boundary form
```

Keys sorted lexicographically at every depth, no whitespace, non-ASCII escaped, UTF-8.
No caller needs to know anything else. `GOLDEN_VECTORS.json` ships, for each vector, the document,
the exact byte string that was hashed, its byte length, and the digest — so a consumer in any
language reproduces a digest with sha256 and a canonical-JSON serialiser alone.

**Line endings never enter an identity.** `organism_id` hashes bytes held in memory, never a file.
Document hashes are a separate matter and are pinned by `.gitattributes eol=lf`.

## 2. The four identities, and what each does NOT cover

| Identity | Hashed over | Answers |
|---|---|---|
| `segment_id` | `{schema_version, words}` | which exact primitive |
| `organism_id` | the manifest | which exact player bytes |
| `composition_id` | glue + ordered components + envelope | which parts, in which order, in which envelope |
| `entry_id` | the registry entry's intrinsic view | which player **under which interpretation** |

`composition_id` and `organism_id` are both recorded and neither substitutes for the other:
concatenation is not injective on component boundaries, so two different compositions can emit the
same manifest. A label attached to a segment is **not** hashed — renaming a primitive must never
change its identity.

## 3. REGISTRY IDENTITY — the load-bearing gap, quantified

`organism_id` hashes the manifest **only**. The manifest carries `schema_version` and does **not**
carry `runtime_hash` or `affordance_hash`. The runtime decodes every instruction as
`op = word mod N_OPCODES`, and `N_OPCODES` lives in the affordance table — outside the hashed bytes.

Measured (`proteus/integration/measure_registry_identity.py`), probing a table that gains one
opcode (25 → 26), which is the smallest possible amendment:

```
organism_id changes ............................. NO
instructions that re-decode ..................... 961 / 1013   = 94.87%
per-organism fraction, median ................... 1.0000
organisms completely unaffected ................. 1 / 64
```

**So the same `organism_id` denotes a different program under a different affordance table, and
almost every instruction changes meaning.** `organism_id` pins BYTES, not EXECUTION.

`entry_id` *does* pin execution: its intrinsic view covers `runtime_hash`, `affordance_hash`,
`grammar_hash`, `grammar_version` and `manifest_schema_version` (verified, recomputes on all 64).

### The rule that follows

> A specimen quoted by `organism_id` alone is **under-specified for replay**. The replayable
> identity is the triple
> `(organism_id, runtime_hash, affordance_hash)`, or equivalently `(organism_id, entry_id)`.

Registry interpretation affects execution, so registry identity belongs in the replay contract and
must never be left as ambient checkout state. Current values:

```
runtime_hash     73f110e21b9df879...   (sha256 over LF-normalised affordances.py + vm.py
                                        + the affordance hash)
affordance_hash  f1607ee8be680acc...
manifest schema  proteus.player_manifest.v0
```

## 4. What changes which identity

| Operation | `segment_id` | `organism_id` | `composition_id` | `entry_id` |
|---|---|---|---|---|
| any genome word changes | yes | yes | yes | yes |
| reordering components | — | yes | yes | yes |
| renaming a component slot | no | no | **yes** | yes |
| changing the envelope (regs/tape/budget/persist/out_cap/writable) | no | yes | yes | yes |
| attaching a label to a segment | no | no | no | no |
| writing anything into `extrinsic` (incl. phenotype) | no | no | no | **no** |
| amending the affordance table | no | **no** | no | yes |
| amending `vm.py` or `affordances.py` | no | **no** | no | yes |

The two bold `no`s in the `organism_id` column are section 3's gap, stated as a table.
`extrinsic` is the one open namespace; nothing written there can move an identity, and a test
asserts it.

## 5. PRIMITIVE IDENTITY — structural, not semantic

A **segment** is a contiguous run of whole instructions (4 words each). That is the smallest thing
the frozen runtime can be said to contain. Nothing in the contract knows or asks what a segment
computes; V0 primitive identity is purely structural, which directive section 5 permits.

A segment satisfies the six operational requirements:

| Requirement | Mechanism | Verified by |
|---|---|---|
| reconstruct it | `decompose()` re-hashes the composed bytes and refuses on mismatch | 200/200 exact |
| insert it | `compose()` | 200/200 |
| remove it | `ablate()` — NOP-substitution, position preserving | 200/200 structurally exact |
| hold it fixed | other components byte-identical under ablation | asserted per report |
| mutate something else | ablation/mutation ranges are declared and disjoint | asserted per report |
| identify it in a composition | `components[].segment_id` + `offset_instructions` | round-trip |

## 6. COMPOSITION IDENTITY — concatenation, and nothing more

V0 admits exactly one glue, `concat.v0`: components laid end to end, no separator, executed from
`ip = 0` with `ip` advancing by 4 and wrapping modulo `tape_words`. This is the only join that
needs **no new runtime semantics**, which is why it is the only one built. A graph language,
dispatcher or conditional glue is deliberately not built: directive section 6 says not to until
A+B proves it necessary, and A+B does not.

A composition document answers every required question:

```
which exact A ....... components[i].segment_id
which exact B ....... components[j].segment_id
ordering/topology ... components[].offset_instructions (total order; concat only)
glue ................ "concat.v0"
resulting bytes ..... manifest.genome, and organism_id = digest(manifest)
deterministic? ...... yes; compose() is a pure function of (components, envelope, glue)
own identity? ....... composition_id
reconstructable? .... decompose(), which re-hashes and refuses on any mismatch
```

`A+B ≠ B+A`: verified as a golden vector (`organism_id_AB != organism_id_BA`).

**Prepared for, not implemented:** `A+B+C` works today (compose takes an ordered list of any
length). `A→B` / `B→A` as *control-flow* composition, conditional activation and world-conditioned
activation are **not** implemented and would each require a new declared glue.

## 7. EXACT ABLATION — and the residual confound

**Ablation is NOP-substitution, never deletion.** Deleting a component's words would shift every
later component's tape address. The runtime addresses the tape by `r[b] mod tape_words` (LD/ST)
and jumps by signed instruction offsets, so a shift silently changes what every surviving
instruction reads and where every jump lands — the ablated system would differ in the removed
component *and* in the addresses of everything after it. NOP-substitution preserves length,
offsets, the envelope, and every other component's words byte for byte.

`ablation_report()` returns one of three verdicts and never a bare boolean:

* `EXACT` — structurally clean **and** alias-invariant.
* `CONFOUNDED_BY_DATA_CHANNEL` — structurally clean, but the transcript moved under the alias
  differential.
* `STRUCTURALLY_INEXACT` — something outside the declared range changed. Should be unreachable;
  it exists so that it cannot fail silently.

### Why a structural check is not sufficient: the NOP-alias differential

The genome is copied into the tape (`vm.Player.fresh_state`), so **an opcode word is also a datum**
that `LD` can read. Substituting it changes that datum's value. Since every word `w` with
`w mod N_OPCODES == 0` decodes to NOP, ablating to `0`, `25` and `50` are three operations that are
**instruction-identical and data-distinct**. If their transcripts disagree, the ablation perturbed
a data channel and "A+B minus A" is not "the same system with only A removed".

Measured on the committed specimens, class-level knockout
(`proteus/integration/measure_ablation_exactness.py`):

```
organism-class pairs tested ..................... 343
identical transcript under all three aliases .... 342
CONFOUNDED (transcript depends on the null value)   1   (0.29%, halt_yield, 1 organism)
```

Measured on constructed A+B compositions (`proteus/compose/run_ab_readiness.py`, 200 pairs):

```
ablation certified EXACT ........................ 200/200
decompose exact ................................. 200/200
```

**The certificate is ensemble-relative and is a LOWER BOUND on confounding.** It detects a data
dependence only if that dependence reaches the transcript on the probes actually run. The gate is
proven able to fail: `test_data_channel_confound_is_detected_when_present` constructs a reader that
`LD`s its neighbour's opcode word and asserts `CONFOUNDED_BY_DATA_CHANNEL` with 3 distinct
transcripts.

## 8. Operand positions — read the runtime, not the prose

`affordances.py`'s module docstring states that `c` is the immediate for `LDC`. **The runtime
disagrees**: `vm.py` `op == 3` executes `regs[a] = bw & MASK32`, so the immediate is read from
operand slot **b** (word `ip+2`). The TABLE row (`"a,imm"`) is correct; the prose above it is not.

This is not fixable in place. `runtime_hash` is a sha256 over the whole LF-normalised
`affordances.py`, docstring included, so correcting the sentence would change the runtime identity
and therefore the interpretation identity of every frozen specimen. It is recorded here and in
`test_composition.py` instead, and **anyone hand-writing a genome must encode from `vm.py`**.

Correct encodings for the operands most likely to be hand-written:

```
LDC r[a] = imm      [3, a, imm, 0]        immediate in slot b
MOV r[a] = r[b]     [4, a, b,   0]
LD  r[a] = tape[r[b]]   [5, a, b, 0]
ST  tape[r[a]] = r[b]   [6, a, b, 0]
JMP ip += 4*off     [18, 0, off, 0]       signed offset in slot b
JZ  if r[a]==0      [19, a, off, 0]
OUT ch r[b] << r[a] [23, a, b,  0]
```
