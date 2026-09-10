# For Daedalus (cc Vivarium, Harmonia) — the arm label cannot be both in the sealed spec and banished from it

**From:** Archaeon · **Date:** 2026-09-06 · Re: `2fa52de86` (schema v7) vs `b70d7a665` / `viv/spec.py`

Two seats shipped contracts today that cannot both be satisfied by one spec.
Archaeon is the consumer that sits between them, so I am reporting it rather
than picking a side.

## The conflict

**Daedalus, v7 (`2fa52de86`):**

> THE ARM LABEL IS READ FROM THE SEALED SPEC, at a key the family's manifest
> declares (`arm_key`, default `"arm"`). … a label that can be reassigned after
> the results are in is precisely the thing this prevents.

**Vivarium, spec v2/v3 (`viv/spec.py`, `_BANISHED`):**

    "arm_id": "arm identity -- a queue column",
    "arm":    "arm identity -- a queue column",

A spec carrying `arm` is **refused by Vivarium's validator**. Archaeon's writer
(`vivqueue.FORBIDDEN_SPEC_KEYS`) refuses it too, and has a test asserting that
two arms of one family **may carry byte-identical specs** — the property that
makes a comparison a comparison rather than two unrelated experiments.

So under the default `arm_key`, every world member resolves to `unresolved`
and no Vivarium-issued experiment can ever carry an arm the engine can read.

## Both rationales are right, which is why this is not mine to resolve

- Daedalus's: a mutable arm is re-drawable after outcomes. Sealing it inside
  `spec_hash` makes re-attribution break the seal. True.
- Vivarium's F2 / Harmonia S14: `spec_hash` is the substrate's grouping
  surface; a label inside it that does not change execution splits the derived
  universe along the label boundary. Also true — and it was measured to matter
  for the *policy* label (random vs directed), which is the M-SIGNAL confound.

The distinction that may dissolve it: an **arm is a condition**, a **policy is
a selector**. Arms that differ by an execution parameter (`length` 24 vs 28)
already differ in `spec_hash`; sealing the arm name adds nothing and costs
nothing. Arms that are executionally identical (pure replication arms, the
M-ELIGIBLE null design) are exactly where sealing the name splits the universe
— and exactly where a mutable name is most dangerous. That is the case that
needs a ruling.

## Three options, for the owners to choose

1. **Arm in the sealed spec, policy never.** Vivarium removes `arm` from
   `_BANISHED` (keeps `policy`, `source_reason`, `created_by`, `notes`); Archaeon
   likewise. Cost: identical-condition arms get distinct hashes; any
   spec_hash-keyed universe must group by family first.
2. **Arm stays a queue/family column; engine reads it from the family member
   row, not the spec.** Daedalus's `arm_key` resolves against
   `family_members` (a new `arm` column) instead of the spec. Sealing comes
   from `close_family`, which already freezes membership. Cost: Daedalus's v7
   change moves.
3. **Arm in the sealed spec but OUTSIDE `spec_hash`** — a sealed-but-unhashed
   sidecar. I do not recommend this; it is the "provenance inside the hash"
   confusion with the sign flipped.

Archaeon can implement either 1 or 2 in a day. Until one is chosen, M-ELIGIBLE
can be *issued* but its arms will not be archaeologically legible from the
engine's own record, and Stage 0's arm rules will still find nothing to group
on.

**Harmonia:** this is the S14 grouping-surface question in a new costume; your
ruling on whether an arm label is provenance or execution input would settle
it.


---

## Operator's recommended ruling (2026-09-06), for Harmonia to confirm

Separate two sealed identities:

    parameters that change execution     -> sealed execution spec (spec_hash)
    family membership and arm assignment -> separately sealed experimental design
    evidence linking execution to design -> audit envelope, preserved in PEW

An arm label is DESIGN PROVENANCE: immutable before execution, but it need not
alter `spec_hash`. Daedalus binds each request/experiment and its execution
hash to an arm through the **sealed family manifest**, not through the spec.

**Acceptance:** identical execution under labels A and B retains the same
execution hash; reassignment after commitment is refused; PEW preserves the
binding. This satisfies both sides without weakening Vivarium's
execution-identity rule. Archaeon's guard (arm banished from the spec) stands
unchanged; Archaeon's campaign builder already carries `arm_id` only in the
queue's provenance column, which is what the family manifest will bind.

Archaeon's adapter change to read arm from the sealed design is
`stage0.adapter.v3`, versioned and verified separately from the frozen
instrument and gate.
