# Triage of Herakles's 69 inbox templates — 2026-09-06

Measured against Vivarium's live kind registry (`evaluate_bitstring`,
`noop_v0`, `random_walk_v0`) in the merged worktree. Nothing admitted;
admission is the operator's act.

## Counts

    inbox templates                        70  (69 Herakles + 1 Archaeon)
    on an IMPLEMENTED kind                  8  (4 evaluate_bitstring, 4 random_walk_v0)
    EXPANSION-flagged (kind not implemented) 62
    REPAIRED (salvaged from a corrupted run,
      numeric axes null, never guessed)    50
    distinct expansion requests (Herakles)  28, collapsing to 7 bench gaps

The 8 runnable ones exist only because `random_walk_v0` landed this
afternoon (Vivarium `b70d7a665`). Before that the count was 1.

## The question asked: the smallest bench change enabling ONE complete, measurable experiment from the inbox

**Answer: none is required for a first one.** `falsification_walk.v0`
(Falsification-Based Search) is measurable today:

    kind          random_walk_v0        (implemented, stateful)
    result        position, displacement, start_position, steps, step_scale
    outcome_rule  field=displacement, op=">=", value=<envelope threshold>,
                  if_true=FALSIFIED (envelope violated), if_false=SURVIVED
    repeat        v3, count 4, seed_derivation sha256_index, state=persist

That is one trajectory of four attested observations whose final displacement
is checked against a declared envelope — exactly the experiment the template's
rationale describes, with no new executor and no new outcome-rule operator.
Its `param_space` has null ranges (salvaged run); the operator fills `steps`
and `step_scale` at admission — a disclosed admission-time fix, per Herakles's
own note, not a bench change.

**The smallest bench change that matters** is the one that makes the *other
three* walk templates and every repeat-based experiment measurable as
designed: Herakles's request **#22 — an outcome rule that aggregates across
repeats** (`max` / `min` / `any` / `all` over the trajectory). "Did the walk
ever exceed the envelope" is `any(displacement >= k)` over four observations,
not a check on the last one. This lives in Vivarium's `spec.py` outcome-rule
vocabulary and is the smallest possible extension of it now that `repeat`
exists. It also subsumes #25/#27's "compare across runs" for the single-arm
case. Requested of Vivarium as **E16**.

## Ranked bench gaps (from the 28 requests), smallest first

1. **#22 aggregation over repeats in `outcome_rule`** — Vivarium, small,
   unlocks 4 templates now and every future repeat design.
2. **#3/#25/#27 two-arm / cross-run comparison in `outcome_rule`** — the
   M-ELIGIBLE / M-SIGNAL analysis itself, once arms are legible; Harmonia to
   specify the comparison before Vivarium encodes it.
3. **#10/#13 seed-independent data injection** — SFE artifact as executor
   input; Daedalus + Vivarium.
4. **#8 seed → structured payload mapping** — a generator layer; sits with
   Players/Proteus.
5. **#4/#5/#24 conditional or closed-loop repeats** — a different execution
   discipline; later.
6. **#14/#15 a VM executor** — this is Proteus's tape-machine, already built;
   the gap is the binding, not the executor.
7. Everything else (differentiability, graph topology, theorem proving, MDPs)
   — real, large, and not this quarter.

## What Archaeon will do with the inbox

- Leave all 69 PROPOSED. Fill nothing. The 50 REPAIRED entries stay flagged.
- Recommend `falsification_walk.v0` as the first admission candidate, with the
  two ranges the operator must supply.
- Add E16 (aggregation over repeats) and E17 (`falsification_walk.v0`
  admission-time ranges) to the expansion register.
- Re-run this triage whenever `viv/kinds.py` changes; the count of runnable
  templates is a menu-growth measurement in its own right.

## Correction after Herakles's expansion-design pass (later, 2026-09-06)

Three claims above were wrong, and Herakles's re-examination found all three.

1. **"8 runnable" counted name matches.** `check()` validated parameter names
   only (Herakles F-2). Against a check that dry-draws and dry-builds, the
   inbox stands at: 7 name an implemented kind, 6 of those fail the draw
   (destroyed ranges), 1 draws and cannot build because no flat template
   declares `seed_root`. Runnable by Archaeon's producer today: 0 of 69.
2. **"`falsification_walk.v0` is measurable today" was false.** Archaeon's
   spec builder is hard-wired to `evaluate_bitstring`; a `random_walk_v0` spec
   cannot be built by this seat until E18. The bench change is not required;
   the Archaeon change is. And per Herakles F-5, `step_scale` must be HELD
   FIXED, not ranged — it is a pure rescaling.
3. **All 69 were flat and my registry nested.** The roadmap example did not
   show the nesting; the fault is Archaeon's. The loader now accepts both
   forms and normalises by name (`seed_root` → world, all else → payload).

What Herakles's packet adds that the bench-gap ranking missed: the smallest
capability is free (C-0, now the `constant` form), the substrate has an
analytic null (F-6; `bitstring.exchangeability_null.v0` proposed as the
known-answer case), and the crux is whether a cross-observation statistic
needs a new outcome rule or a home — it needs a home, and SFE already has one
(`families(kind=analysis)`, E25). E16 is rescoped to within-experiment
aggregation, which does not move adjudication inside the sealed spec.
