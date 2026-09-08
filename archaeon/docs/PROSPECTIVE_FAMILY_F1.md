# Prospective family F1 — specification (NOT executed)

**Purpose.** Flip the Stage 0 gate by *creating* archaeologically legible
structure, rather than by weakening the gate or inventing relationships after
the fact.

**Endpoint (verbatim from the directive):**

> Can a prospectively declared experiment family pass through Vivarium,
> fossilize its actual structure, and later yield ≥2 naturally eligible S17
> claim-units without Archaeon inventing any relationship after the fact?

This is a test of whether the **substrate becomes interrogable**. It is *not* a
test of whether S17 predicts, and nothing in F1 is tuned to make it predict.

---

## 0. BLOCKER — F1 cannot run on the current Vivarium build

`vivarium/viv/runner.py::run()` calls `c.create_world(...)` on every row and
records exactly one `c.observation(...)`. There is no path that reuses a world.

    one queue row  =  one new world  =  ONE observation

S17's `features()` computes lag-1 serial autocorrelation **within a world**
(`if len(w) > 3`), so a world needs **≥4 observations**. A world can never hold
more than one. Therefore:

> **No experiment family issued through Vivarium as currently built can ever
> produce an eligible S17 claim-unit — at any volume, for any budget.**
> 1000 rows would give 1000 worlds of 1 observation and eligibility would
> still be exactly zero.

This is a capability gap, not a parameter. **The required capability:** a
declared **repeat count** producing N observations inside ONE world from one
accepted request.

`repeat` is an **execution input** — it changes what is executed — so it belongs
*inside* `experiment_spec` and *inside* `spec_hash`. It is not provenance and
must not be smuggled into a column. Two further requirements, both consequences
of Vivarium's own F3 ("no defaults for any value a result depends on"):

1. **The per-repeat seed derivation must be declared in the spec.** If every
   repeat reuses one seed, all N values are identical, within-world variance is
   0, and `serial_ac`/`within_between` are degenerate — an eligible-looking unit
   carrying no information. Vivarium must not choose this derivation.
2. **Repeats must be recorded in ledger order**, since a trajectory is what the
   lag-1 feature reads.

Preferred over the alternative of letting a row target an existing `world_id`:
that would create cross-row ordering dependencies and let a later row attach
itself to an earlier world, reintroducing exactly the retrospective grouping
this contract forbids.

Everything below is specified against a build that has `repeat`.

---

## 1. Shape

Meets every stated minimum, with nothing to spare:

    2 families × 4 worlds/family × (2 arms × 2 worlds/arm) × 4 observations/world
      = 8 queue rows  (repeat = 4)
      = 8 worlds, 32 observations
      = 2 candidate S17 claim-units  (one per family)

Requirement check: ≥2 comparable groups ✓ (2) · ≥4 scored worlds per group ✓ (4)
· ≥2 worlds per arm ✓ (2) · ≥4 observations per world ✓ (4).

Two families rather than one because **an ordering over a single unit carries no
information** — Stage 0 already treats one unit as not orderable, and that case
is pinned by a test.

## 2. Declaration (all before execution, all in columns)

    row  family_id  arm_id  world.seed_root  payload.length  repeat
    ---  ---------  ------  ---------------  --------------  ------
     1   fam-F1-A   arm-a       910001             24           4
     2   fam-F1-A   arm-a       910002             24           4
     3   fam-F1-A   arm-b       910003             28           4
     4   fam-F1-A   arm-b       910004             28           4
     5   fam-F1-B   arm-a       910005             24           4
     6   fam-F1-B   arm-a       910006             24           4
     7   fam-F1-B   arm-b       910007             28           4
     8   fam-F1-B   arm-b       910008             28           4

`family_id` and `arm_id` are **columns**, never spec fields. `seed_root`,
`length` and `repeat` are **spec fields**, because each changes what is executed.

**The arm contrast is `length` 24 vs 28, chosen for neutrality.** For a onemax
landscape with a seed-derived target the expected score is ≈0.5 at either
length, so the contrast is not engineered to produce an effect — it makes the
arms genuinely distinct declared conditions without manufacturing fragility.
Within an arm the two worlds differ only in `seed_root`: independent
realizations of one condition, which is what a replicate is.

Because every spec differs (distinct seeds), no two rows are byte-identical and
`replication_of` is **not** exercised by F1 — there is no double-submission
ambiguity to resolve. It is exercised in the integration tests instead.

## 3. Issuance

- `source_reason = 'human'`. **F1 is not an Archaeon autonomous proposal.** No
  fossil directed it — Stage 0 found none could — so it is operator-directed
  seeding, and labelling it `exploration` would misattribute the decision to a
  policy that did not make it. It therefore does not consume Archaeon's
  autonomous quota, which is the correct reading of "human-created experiments
  do not count against the quota".
- `created_by = 'archaeon'` — Archaeon wrote the rows; `source_reason` records
  that a human chose to run them.
- Registered as **one candidate set of 8, all 8 retained**, in one transaction.
  Nothing is cancelled: every candidate was selected, and `viv.candidate_sets`
  will show `registered=8, cancelled=0, retained=8`. An honest set, not a
  performance of selection.
- `request_key` per row, so a resubmission is refused idempotently.

## 4. What must be true afterwards for F1 to have succeeded

Mechanical, checkable, and none of it requires S17 to predict anything:

1. 8 rows reach `completed`; any `failed` row is visible in the queue **and** in
   PEW (needs Vivarium Tier 1 item 6 — see §4 of the contract).
2. SFE holds 8 worlds, each with ≥4 scored observations in ledger order.
3. The declared family/arm structure is **recoverable from the fossil record**
   without consulting the queue — see §5, which is unresolved.
4. `archaeon.stage0_fragility_survey` returns **PASS** with
   `eligible_claim_units ≥ 2` and ≥1 dimension `ordering_meaningful`.
5. Archaeon invented no relationship: every grouping used by the survey traces
   to a pre-execution declaration.

Explicitly **not** a success criterion: that the S17 rules rank the two units
correctly, or at all. Two units cannot support an AUC, and F1 is not a
prediction test.

## 5. UNRESOLVED — how family/arm reaches the fossil record

This is the one genuine ambiguity remaining, and it would contaminate
attribution if guessed at.

Stage 0's arm rules read **SFE**, not the queue. Today the only grouping surface
SFE publishes is `worlds.topology_group`, and there is no per-world arm field
(`worlds.name` is being removed from the spec by Vivarium F2, and parsing a
composite name would be "inferring a contrast from a name", which the directive
forbids).

Three options, none of which I should choose alone:

- **(a) `topology_group := family_id`,** plus one SFE `lineage_edge` per world
  recording arm membership (`src=world → dst=arm_id`, `relation='IN_ARM'`).
  `lineage_edges` is SFE's declared reference DAG, documented as *"the ONLY
  source of lineage — never reconstructed after the fact"*, which is exactly the
  right semantics. Needs **Daedalus**.
- **(b) PEW-side only:** carry `family_id`/`arm_id` in the encounter `producer`
  block. Needs **Mnemosyne**. Weaker: `producer` is free-form jsonb, so it is a
  convention rather than a typed fact.
- **(c) Queue-only,** with the survey joining the queue to SFE by
  `sfe_experiment_id`. Honest and needs no other seat, but it makes the *queue*
  part of the fossil record, which contradicts "PEW/SFE fossilize what
  happened" — and a future archaeologist reading only PEW/SFE would see 8
  ungrouped worlds.

**Attribution risk if unresolved:** under (c) the grouping is legible only to a
reader who has the queue. Under (a) it is legible from the substrate alone,
which is what "archaeologically legible" means. I recommend **(a)**, but it
changes how Vivarium creates worlds and touches Daedalus's engine semantics, so
it needs both seats' consent before F1 is issued.

Until this is settled, F1 would fossilize its *observations* but not its
*structure* — and Stage 0 would still return KILL, because the arm rules would
find nothing to group on.

## 6. Cost

8 rows, `repeat=4`, one globally-running experiment at a time
(`active_singleton`). No cadence cost (`source_reason='human'`). Order of
minutes of execution, not days.
