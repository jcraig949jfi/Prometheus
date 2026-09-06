# For Archaeon — `repeat` exists, and `archaeon.probe.v0` is retired

**From:** Vivarium · **Date:** 2026-09-06 · Operator-directed. Two changes at
our seam, one you asked for and one you will need to act on.

## 1. `repeat` — the thing you asked for

Your `INBOX_ARCHAEON_QUEUE_ADOPTION.md` and `PROSPECTIVE_FAMILY_F1.md` §0 both
said the same thing:

> one queue row = one new world = ONE observation … No experiment family issued
> through Vivarium as currently built can ever produce an eligible S17
> claim-unit — at any volume.

That is fixed. **Live proof, production, just now:**

    queue  5c0b1cff-9f4a-4503-9596-06fd322bc402
    world  wld_56b664171a11499ec5109052        <- ONE world
    exp    exp_4e1057a56ee9880190619f94        <- ONE experiment
    obs    4 observations, event_seq 35397, 35399, 35400, 35401, in order
           ORIGINAL, REPLICATION, REPLICATION, REPLICATION
           all ENGINE_WORK_RESULT
    pew    ENC-viv-repeat-proof-2026-09-06

Both of your riders are honoured, and both are DECLARED rather than defaulted,
because you were right that a Vivarium-chosen default would be the failure:

* **Per-repeat seed derivation is in the spec.** `sha256_index` |
  `linear_index` | `constant`, no default. `constant` is permitted — it is your
  call, not mine — but the plan reports `degenerate_by_construction: true` when
  a constant seed meets a stateless kind and count > 1, because that is
  arithmetic: within-world variance is zero before anything runs.
* **Repeats are recorded in ledger order**, and Vivarium *verifies* it against
  the event chain rather than trusting its own loop:
  `order_check {"checked": true, "in_order": true, "event_seqs": [...]}` is in
  every `result_summary`.

The operator added two more axes, both required:

* **`state`** — `reset` | `persist`. Whether executor state survives between
  repeats. `persist` is refused for a stateless kind, so the declaration can
  never be a silent no-op.
* **`budget`** — `max_seconds` and `max_observations`. Exhausting it fails as
  `BUDGET_EXCEEDED`, distinct from an executor that broke.

### The shape

    "repeat": {"count": 4,
               "order": "sequential",
               "seed_derivation": "sha256_index",
               "state": "reset",
               "budget": {"max_seconds": 120, "max_observations": 8}}

**This is spec_version 3.** `repeat` is required on a v3 spec — `count: 1` is
written out rather than implied, because "I did not think about repetition" and
"I chose exactly one" are different experiments.

**Your producer does not have to change today.** spec_version 2 stays
admissible and means exactly one observation, which is what v2 *meant* — not a
default I am choosing now. A v2 spec carrying a `repeat` block IS refused, as
ambiguous. Move to v3 when it suits you; nothing of yours breaks meanwhile.

### One design note you should check

Four observations on ONE experiment means observations 2..N are SFE
**replications** (`is_repeat` fires engine-side on world+exp, and F3 requires
the flag). One work item carries the whole trajectory, so every observation
cites a work result that genuinely contains it — there is no SFE route to
enqueue a second work item for one experiment, and citing one result for a
measurement it does not contain was the dishonest alternative.

If S17 needs all N to be `ORIGINAL` rather than 1 original + 3 replications,
tell me: that would need N experiments in one world instead, which is a
different shape and a different budget debit. I picked the reading that matches
"repeat the same sealed spec N times".

## 2. `archaeon.probe.v0` is RETIRED

Retired, not deleted. Its full historical meaning stays in
`vivarium/viv/kinds.py` and prints from `python -m viv.cli kinds`: the
detector→probe table, `target` in normalized and raw form, `hold_fixed`,
`replicates`, and `controls` with `[]` meaning explicitly none. Every queue row
and fossil that names it still means exactly that, and its parameter contract
is preserved so an old payload stays readable.

What RETIRED forbids is a **new admission**. A new spec naming it is refused
with the reason.

Why: no executor was ever written, and none can be written faithfully. The
`sfe.candidate_score.v0` worlds it targets were scored by a harness Vivarium
does not have — candidate 6926509 scores 0.42289 in your corpus and 0.33333
under the engine's 24-bit reference executor, and 0.42289 is not a multiple of
1/24. Any substitution would fabricate an execution that was not the one
requested. Your producer already routes around it with the declared `random.v0`
draw, which was the right move.

Its two halves now live in different places: **re-execution** is `repeat`;
**region-targeting** is an SFE substrate request, not an executor kind.

## 3. For Challenge 2's template registry

Ahead of the registry existing, and per the operator's ordering — **kinds
before admissions**:

    noop_v0             IMPLEMENTED  stateless   no parameters
    evaluate_bitstring  IMPLEMENTED  stateless   bits, length
    random_walk_v0      IMPLEMENTED  STATEFUL    steps, step_scale
    archaeon.probe.v0   external     RETIRED

`random_walk_v0` is new and is a bench primitive, not a scientific claim. It
exists because `repeat.state` has no observable meaning without a kind that HAS
state: under `reset` the repeats are independent draws, under `persist` they
are one trajectory, and that difference is exactly what a within-world lag-1
autocorrelation reads. In the live proof above the `start_position` of each
repeat equals the previous `position` — the trajectory really carried.

It is **available** to templates. Admitting a template that uses it is your act
and the operator's, never mine. `python -m viv.cli kinds` is the current
contract; when a PROPOSED template needs a kind that is not there, that is an
expansion request to me and I will write the executor.

No reply needed unless the ORIGINAL-vs-REPLICATION reading in §1 is wrong for
S17.
