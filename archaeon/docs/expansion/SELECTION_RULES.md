# How diversity survives selection — reviewable rules

Annex to `archaeon/docs/ROADMAP.md` §Diversity. Drafted 2026-09-07 by
Archaeon. Every number below is a **human choice**, named as such, carried in
a versioned policy file, and changeable only by a new policy version. Nothing
here is scored by a model. Nothing here is a verdict.

The failure these rules exist to prevent has a shape: an established family
(today, `evaluate_bitstring`) produces fossils, fossils produce signals,
signals direct experiments back into the same family, and every new family
starves before it has enough rows for a detector to be eligible on it. Under
that loop the menu grows on paper and the corpus stays a monoculture. The
health report already flags `KIND_MONOCULTURE`; these rules are what a flag is
for.

---

## R1. Bounded exploration allocation (the novelty reserve)

**Rule.** Each lane's daily quota is partitioned into an *established* share
and a *reserve* share. The reserve may be drawn only by templates whose family
is **young** or **thin**:

    young   admitted within the last 90 days
    thin    fewer than N_thin executed rows in this lane (N_thin = 24, human
            choice: one eligible D3 region at four observations per world and
            six worlds)

Established families draw only from the established share. If no young or
thin family is admitted, the reserve is **not** given to established families;
it is left unspent and the unspent count is recorded in the census. An unspent
reserve is a measurement that the menu has stopped growing, and it must stay
visible rather than be absorbed.

    reserve fraction   1 of 6 daily draws per lane   (human choice; policy
                       `allocation.reserve.v0`)

**Why bounded, not weighted.** A weight lets an established family win the
draw on a bad day for the reserve; a partition cannot. `menu.coverage.v0`
(1/(1+uses) weighting) remains a *named* policy for choosing *among*
reserve-eligible templates, never for deciding whether the reserve is spent.

**Interaction with M-SIGNAL.** Both M-SIGNAL arms run on their own lanes with
their own frozen universe; the reserve applies inside each arm identically, so
it cannot favour a policy.

**Recorded per draw.** `allocation_share ∈ {established, reserve}`, the family
age and row count at draw time, and the policy version — in
`source_evidence`, never in the sealed spec.

---

## R2. Retention: behaviourally distinct organisms and informative failures

**Rule.** Each admitted family declares, at admission, a **descriptor set**:
a small list of named, computable features of an executed organism or run.
Descriptors are chosen by a human, written in the family's registry file,
versioned, and never learned.

Examples of the shape (each family writes its own):

    bitstring family      length; Hamming distance to target (fixed-target
                          series only); run-length profile of the candidate
    program family        opcode histogram; halted / step-budget exhausted;
                          output signature; trace length
    controller family     memory bits read; action entropy; visited-cell count;
                          episode return
    replicator family     genome length; lineage depth; replication rate;
                          resource share

**Archive.** Per family, a retention archive keyed by the descriptor cell
(descriptors binned by human-declared edges). Capacity per cell is bounded:

    cap per cell            4         (human choice)
    eviction                oldest first, EXCEPT that an *informative failure*
                            is never evicted by a success

An **informative failure** is a run that (a) fired a detector, (b)
contradicted its own pre-registered prediction (`FALSIFIED` where `SURVIVED`
was predicted, or the reverse), or (c) is the first occupant of its cell. It is
retained ahead of any success in the same cell.

**Retention is a pointer, not a copy.** The archive stores observation
references (world id, observation id, event_seq, spec_hash) and the descriptor
vector; the fossil stays where it is. Nothing is re-attributed.

**What the archive is not.** It is not a quality-diversity algorithm and it
does not steer selection on its own. It is what a region-directed template may
draw a *seed* from when a detector fires on a cell, and it is what the health
report counts. Steering through it is a named policy, compared against the
frozen random control like any other.

---

## R3. Comparison inside tasks; coverage without a universal score

**Rule.** Performance is compared only **within a task family** that has a
registered measurement (SFE measurement identity: `<kind>.<field>`,
direction, range). There is no cross-family scalar. Any report that ranks
families by a single number is out of policy.

**Portfolio coverage** is reported as counts, never as a score:

    families admitted / executed (≥1 attested row) / detector-eligible
    occupied descriptor cells per family, over declared cells
    fraction of the reserve spent, per lane, per week
    templates admitted in the last 90 days; draws from them

Coverage grows when a new cell is occupied or a new family becomes
detector-eligible. Coverage does not grow when an established family adds rows
to an occupied cell. Archive size and class count are reported beside coverage
and are **not** coverage.

---

## R4. Variation in labels, encodings, or seeds is not behavioural difference

**Rule.** Two runs count as behaviourally different only if an **intervention**
changes the outcome distribution under matched seeds. Concretely, a family may
claim two organisms (or two templates) are distinct only after:

1. **The exchangeability null passes.** Every family ships a template that
   varies a label/encoding/seed axis and is declared, in advance, to carry no
   effect (`bitstring.exchangeability_null.v0` is the bitstring family's; each
   family writes its own, e.g. renaming opcodes under a bijection, permuting
   grid coordinates under a symmetry, relabelling lineages). A detector firing
   on that template is an instrument defect, not a finding.
2. **The intervention separates.** With seeds matched, removing or altering the
   mechanism (memory off, interaction disabled, rewrite rule changed, K=0 on
   an NK landscape) changes the measured outcome by more than the
   exchangeability null's spread.

Distinctness established this way is recorded with the intervention that
established it. Distinctness asserted from labels, from an LLM description, or
from descriptor distance alone is not recorded.

---

## R5. Matched nulls and controls are conditions of admission

**Rule.** No family is admitted to the *directed* menu (the one a fired
detector may draw from) without:

    a known-answer null      the exchangeability template above
    a mechanism control      the family's declared intervention that removes
                             the mechanism the family exists to study
    a matched random control the family's own frozen random template, drawn
                             over the same universe as any directed policy

A family may be admitted to the *random* menu with only the null; it cannot
be *directed into* until all three exist. Archive size, class count, cell
occupancy, and "it looks diverse" are not admission evidence for any of the
three.

---

## R6. Transfer only through declared mappings

**Rule.** Transfer is a property of an **organism that carries state** between
two worlds, not of two worlds. A transfer claim requires:

    an organism with declared state that crosses (Proteus specimens are the
      only such organisms today; a stateless candidate cannot transfer)
    a declared mapping between the two worlds' observation and action spaces
      (`mapping_id`, human-written, versioned; identity mapping allowed and
      must be declared as identity)
    a comparison family (SFE `families(kind=comparison)`) whose arms are
      "carried state" vs "reset state", same world pair, same seeds

There is no universal genome. A family whose organisms cannot be mapped into
another's interfaces does not transfer, and that is recorded as *no declared
mapping*, not as failed transfer.

The flipped-hash relatedness axis (Herakles C-1) is a **world** relation; it
becomes a transfer experiment only when an organism with state is placed on it.
Without one, the transfer curve is pinned analytically at both ends and
measures the hash.

---

## R7. Research leads, held as leads

- **Repertoire preservation** (MAP-Elites-style archives, novelty archives):
  R2 is deliberately the passive half only. An *active* illumination policy is
  a named selection policy to be compared against frozen random on a family
  with a declared landscape (C-3), not before.
- **Environment–agent co-development** (POET, minimal-criterion coevolution):
  requires both a stateful organism and a parameterised world family with a
  declared difficulty axis; neither exists yet. Reopen when the spatial
  stateful family has its mechanism control demonstrated.

---

## R8. What LLMs may and may not do here

May: propose templates and descriptor sets (as PROPOSED), translate a field's
experiment into the registry shape, organise the crosswalk, generate candidate
explanations for a fired detector (recorded as candidates).

May not: choose the reserve fraction, set descriptor edges, decide distinctness,
adjudicate a null, or rank families. A "promise" score does not exist in this
program.

**Rejection vs deferral.** A family, mechanism, or field is *rejected* only on a
precise claim with applicable evidence or derivation and a bounded conclusion
(e.g. "on a hashed target the bits axis carries no information about the
marginal score; derivation: Binomial(L, 1/2)"). Everything else — cost,
missing support, incomplete design, an unsuccessful mapping — is *deferred*,
with the reopening condition written beside it.

---

## Policy file

    archaeon/policies/allocation.reserve.v0.json
      { "reserve_draws_per_day": 1, "quota_per_day": 6, "young_days": 90,
        "thin_rows": 24, "cap_per_cell": 4, "chosen_by": "<operator>",
        "chosen_on": "<date>" }

Not written until the operator sets the numbers; the values above are
Archaeon's recommendation.
