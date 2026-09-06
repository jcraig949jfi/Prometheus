# The degeneracy guard has a hole, and one capability unlocks 22 templates

**From:** Herakles. **Date:** 2026-09-06.
**Source:** `roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/expansion_pass/`
**Branch reviewed:** `vivarium/v0-2026-09-05` at `7a91054ad`.

---

## DEFECT. `degenerate_by_construction` misses every stateful kind under reset

Surfaced independently by two analysts; verified here by execution.

`repeat_plan` computes:

    degenerate = (how == "constant" and rep["count"] > 1
                  and rep["state"] == "reset"
                  and not (kind.stateful if kind else False))

The last term excludes stateful kinds. But `state = "reset"` already means no
state carries between repeats, so a stateful kind under reset behaves exactly
like a stateless one. The exclusion is wrong in precisely the case the guard
exists to catch.

Measured, constant seed derivation, `state = reset`, count 4:

    kind                 flagged   four displacements
    ------------------   -------   --------------------------
    evaluate_bitstring   True      (stateless, correctly caught)
    random_walk_v0       False     0.473975951 four times, identical

Within-world variance is exactly zero and the bench reports the spec as
non-degenerate. The docstring says the computation is "arithmetic, not a
judgement". The arithmetic is simply incomplete.

**Smallest fix:** drop the `not kind.stateful` term. `state == "reset"` is
sufficient alone. Under `persist` the term does no work anyway, because the
repeats genuinely differ.

**Why it matters:** this is the guard whose entire purpose is to stop a
zero-variance experiment being read as a measured null. Two mined templates are
exposed to it.

---

## A second thing worth knowing about `random_walk_v0`

`step_scale` is a pure rescaling, not an independent axis. At a fixed seed,
`displacement / step_scale` is constant to ten decimal places across a 73-fold
range, because the scale multiplies every increment identically.

    step_scale   displacement    displacement / step_scale
    ----------   -------------   -------------------------
           0.1     +0.26428096          +2.6428095958
           1.0     +2.64280960          +2.6428095958
           7.3    +19.29251005          +2.6428095958

So the walk has ONE informative payload axis, `steps`, plus the seed. A
template sweeping `step_scale` within a seed manufactures perfectly correlated
observations, which a variance-based detector can read as structure. D3 reads a
variance ratio and D6 reads a jump against a pooled SD; both are exposed.

This is not a code defect. It is a template rule worth stating once, in the
registry README, rather than rediscovering per template: sweep `steps` and the
seed, hold `step_scale` fixed, and if you must sweep it, divide by it first.

The good news is that the walk's analytic null is exact and free: displacement
has mean 0 and variance `steps * step_scale^2 / 3`. That makes it a genuine
calibration instrument for the bench's own random source, and the only exercise
of the `state=persist` path.

---

## CAPABILITY. An orchestrated external backend. Largest single unlock.

Of 69 templates, 22 prefer this route: the science already exists as a tool,
and the bench needs only to call it, bound its budget, and fossilize what came
back. That is the largest count of any route in the matrix.

**Interface:** a kind `external_backend_v0` with payload `tool_id`,
`input_digest`, `budget_seconds`. The executor runs a registered tool, records
exit status, a digest of the output, and a declared reproducibility grade. The
tool registry is data, exactly as the template registry is.

**Existing assets it would reach, which I checked before proposing anything
new:** `ergon/avida2003/` already holds recovered Avida material with artifacts
and build deliverables, so the digital-evolution family routes there rather
than to a new executor. `ludus/` holds atlas_of_worlds, arena and baselines and
is the obvious home for a grid or arena world. `incubation/` holds substrate
machinery with a passed gate history.

**The risk I want named rather than discovered:** this is the capability most
likely to import irreproducibility. Most backends will not be
BIT_DETERMINISTIC. The grade must be recorded per OBSERVATION, not per tool, or
the fossil record will carry a reproducibility claim it cannot support.

**It is also the only route to symbolic, programmatic and spatial modalities**,
and it reaches them by orchestration rather than reimplementation, which is why
it is cheap despite being the biggest item.

---

## Not asked for

Across all 69 templates, ZERO required a substantially different architecture.
The sealed-spec, recorded-observation shape held up against every discipline on
the list. That is worth recording as a result rather than an absence.
