# Retention V0 and the raw measurement surface

Two contracts that exist to make the first A/B/A+B experiment possible, and nothing larger.
Status: contract, V0. Neither is an algorithm to optimise; both are minimums to build against.

---

# PART 1 — R ≈ 0.000001 RETENTION V0

The failure mode on the left is as fatal as the one on the right:

```
PREMATURE PRUNING                         NOISE MUSEUM
A shows no effect once -> deleted         every random component kept forever
-> the interaction that needed A          -> the reservoir is noise, and search
   can never be found                        over it is search over nothing
```

## The one idea that resolves it

**Eviction is not deletion.** The reservoir is bounded; the record is not.

```
ACTIVE RESERVOIR          bounded, capacity R_MAX. What compositions are drawn from.
ARCHIVE                   unbounded, append-only. segment_id + evaluation records only,
                          NOT the words -- a segment is reconstructible from its id via the
                          archive's own words table, ~100 bytes of record per evaluation.
```

A segment leaves the active reservoir when the reservoir is full. It never leaves the archive, and
its `segment_id` is immutable and permanently resolvable. "Evicted" therefore means *not currently
drawn from*, never *gone*, and a later directive can re-admit any archived segment by id. This is
what stops a low marginal effect in one context from becoming a permanent verdict.

## Records

Every evaluation of a segment writes one immutable record. No record is ever edited; a later
evaluation appends.

```
EvaluationRecord {
  segment_id            immutable content identity
  context_id            digest of {composition_id, envelope, ensemble_identity,
                                   world_id or null, runtime_hash, affordance_hash}
  observable            which raw observable was read (see PART 2)
  activation            ACTIVATED | NOT_ACTIVATED | INDETERMINATE_...
  marginal_effect       CHANGED | UNCHANGED | NOT_MEASURED
  ablation_verdict      EXACT | CONFOUNDED_BY_DATA_CHANNEL | STRUCTURALLY_INEXACT
  recorded_at, recorded_by
}
```

`context_id` is mandatory and is why "no effect" can never be stored as a bare fact. A record
always reads *no effect **in context C***, and C names the composition, envelope, probe ensemble and
interpretation that produced it.

**Composition-result records** are the same shape keyed on `composition_id`.
**Negative controls are records too** — a segment that showed no effect is evidence, and is
retained under a separate quota that the eviction policy may not touch.

## Deterministic eviction

When `|active| > R_MAX`, evict in this order, ascending, ties broken by `segment_id` so the policy
is reproducible from the records alone:

```
1. contexts_evaluated        DESC   evict the WELL-TESTED first, not the untested
2. distinct contexts with marginal_effect == CHANGED   ASC
3. segment_id                ASC    deterministic tie-break
```

Subject to three hard guards:

* **G-COVERAGE** — a segment with `contexts_evaluated < K_MIN` is never evictable. Untested is not
  useless. V0: `K_MIN = 3` distinct `context_id`s.
* **G-CONTROL** — segments held as negative controls occupy a reserved quota and are exempt.
* **G-NEVER-DELETE** — eviction writes an `EVICTED` record and moves the segment to the archive.
  There is no delete path in V0. A segment's words remain resolvable by `segment_id` forever.

Note the direction of rule 1: it is deliberately the **opposite** of "prune the useless". The
reservoir evicts what has been *most examined and least productive*, because that is the segment
about which the archive already knows the most, and re-admitting it later costs one lookup.

## V0 parameters (proposed, not tuned)

```
R_MAX          4096 active segments
K_MIN          3 distinct contexts before a segment is evictable
control quota  256 segments
```

These are round numbers chosen to be *sufficient for the first experiment*, and the directive says
not to optimise the retention algorithm yet. They are parameters, not findings.

## What this V0 deliberately does not solve

Open-ended evolution; a value model for segments; any rule that would let a *score* drive
retention. There is no fitness scalar anywhere in this contract, and adding one is a contract
change rather than a tuning decision.

---

# PART 2 — THE RAW MEASUREMENT SURFACE

Three levels, kept mechanically separate. Proteus supplies only the first.

```
RAW OBSERVABLE        exact, mechanical, no interpretation.        <- Proteus
DERIVED METRIC        a function of raw observables.               <- Harmonia
SCIENTIFIC INTERP.    what it means about reasoning.               <- adjudication, not here
```

## The finding that decides what must be exposed

The externally visible probe transcript — the observable the V0 signatures are built on — is
**degenerate at this scale**. Measured over the committed registry
(`proteus/compose/measure_transcript_degeneracy.py`):

| Population | Distinct transcript classes | Largest class share | Players emitting ≥1 value |
|---|---|---|---|
| 2-instruction segment players (n=56) | **3** | 87.5% | 4 / 56 |
| full committed specimens (n=64) | 12 | 60.9% | 10 / 64 |

52 of 56 segment players emit **nothing at all**; their transcript is the per-tick status word and
that is all. This is why `run_ab_readiness` found A+B differing from *both* parents in **0 / 200**
pairs: with 87.5% of players in one class there is almost nothing for a composition to differ in.
That is a fact about the **instrument**, not about composition.

The internal resource vector is not degenerate on the same population:

| Observable | Distinct classes (n=56) | Largest class share |
|---|---|---|
| probe transcript | 3 | 87.5% |
| `ops_by_category` | **37** | 10.7% |
| full meter vector | **39** | 10.7% |

**A ~13× richer surface.** Therefore:

> The first emergence measurement must read the meter vector, not the transcript alone. A
> transcript-only experiment at this scale would be measuring a near-constant.

## What Proteus exposes (all exact, all per-encounter)

From `vm.Meter.as_dict()`, already implemented and already recorded per encounter:

```
ops                              total operations executed
ops_by_category                  per affordance class -- the 37-class surface above
branches_taken                   published as proxy_search_expenditure (declared PROXY)
code_region_writes               published as proxy_adaptation_expenditure (declared PROXY)
in_reads, out_writes, out_dropped
rnd_draws
ticks, budget_exhausted_ticks
wall_s, cpu_s                    NOT deterministic; never an identity input
gpu                              literal "unavailable" -- never fabricated
footprint_words, persistent_state_words
```

Plus, from `proteus/compose/segments.py`:

```
activation_evidence()   ACTIVATED / NOT_ACTIVATED / INDETERMINATE_COMPONENT_IS_ALREADY_NOP_CLASS
ablation_report()       EXACT / CONFOUNDED_BY_DATA_CHANNEL / STRUCTURALLY_INEXACT
                        + the full structural row and the alias differential
transcript + its hash   the existing probe_transcript_equivalence class
```

## How activation is detected, and its one declared blind spot

No runtime instrumentation was added — instrumenting `vm.py` would change `runtime_hash` and
therefore the interpretation identity of every frozen specimen. Activation is a **differential**:

> If a component never executes, ablating it to NOP cannot change anything the runtime does, so
> `ops_by_category` is identical. **Any** difference therefore proves execution.

The converse holds with one exception, which is reported rather than guessed: a component whose
instructions are all already `halt_yield` class is NOP-class already, its ablation is a no-op for
the counter, and the verdict is `INDETERMINATE_COMPONENT_IS_ALREADY_NOP_CLASS`.

Verified both directions: a component behind an unconditional HALT reports `NOT_ACTIVATED`; a
reachable component reports `ACTIVATED`; 200/200 constructed A+B pairs reported `ACTIVATED`.

## What is NOT available

* **Per-instruction execution counts localised to a component.** Not available without
  instrumenting the frozen runtime. `activation_evidence` gives a binary did-it-execute, not a
  count and not a trace.
* **Composition activation ORDER.** Requires the same instrumentation. Not available.
* **Internal state transitions.** The tape and registers are not exposed per tick; only the
  end-of-tick outputs and the accumulated meter are.

Each is a genuine NO. See the readiness matrix in the closure packet for classification.

## The distinction that must survive contact

`ACTIVATED` means *instructions executed*. It does not mean the component mattered.
Measured on 200 constructed pairs: **200/200 ACTIVATED, but only 30/200 changed the transcript** —
**170/200 (85%) activated with no marginal effect on the transcript at all.** SUPPORT and
INCREMENTALITY are different questions and the surface reports them separately, by construction.
