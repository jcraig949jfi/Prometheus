# Provocations — Harmonia substrate acceleration log

**Purpose.** Living catalog of meta-improvement proposals across Harmonia sessions (and other agents). These are **provocations, not decisions**. Most entries will stay as ideas that inform later thinking. Some will be tried. Some will be tried and fail. The trying is the point — per James, 2026-04-20: *"sometimes just the trying opens new paths through the forest of the unknown."*

**There is no silver bullet.** If an entry reads like one, that's a reward-signal-capture flag — sharpen the risks section before the proposal.

---

## What belongs here

- Substrate-level improvements to methodology, pipeline, or discipline.
- Ideas that don't yet have the 3+ anchor weight of a `pattern_library.md` entry.
- Proposals that span multiple sessions or are too long-horizon for `decisions_for_james.md`.
- Thoughtful "what if we also…" provocations that future sessions may pick up, adapt, or reject.

## What does NOT belong here

- Task-level work (goes to the Agora queue via `seed_task()`).
- Methodological findings anchored 3+ times (goes to `pattern_library.md`).
- Specific pending human decisions (goes to `decisions_for_james.md`).
- Kills / abandons (goes to `abandon_log.md`).

## North star anchor

*Compressing coordinate systems of legibility, not laws.* Every provocation should make legible structure more visible — not hide it behind learned predictors, opaque heuristics, or "scale more." Reward-signal capture (proposing things because they *sound* productive) is the primary failure mode; every entry carries an explicit reward-capture check in its risks block.

Reference: `user_prometheus_north_star.md`, `feedback_falsification_first.md`, `feedback_tensor_admission_test.md`.

---

## Intake convention

```
## [YYYY-MM-DD] — <short title>
**Proposer:** <Harmonia session / other agent / James>
**Confidence:** high / medium / low / speculative
**Status:** open / in-discussion / tried:<outcome> / shelved:<reason>

**Proposal.** one paragraph describing the change.

**Rationale.** why this accelerates mapping / exploring / discovering.
Anchor to existing substrate gaps where possible.

**Risks & caveats.** what could make this not work. Include a reward-
signal-capture check: "if this succeeded, would the success be the
*finding* we care about, or the *feeling* of progress?"

**Cost.** rough effort estimate.

**Compound effects.** what it unlocks downstream. This is how
provocations become worth trying even when the primary rationale is
weak.

---
```

If a provocation gets tried, update **Status** in place and append an **Outcome** block. Do not delete failed entries — the falsification record is as valuable as the successes.

---

## Seed entries — Harmonia_M2_sessionE calibration, 2026-04-20

The following three proposals constituted the custom calibration challenge James issued to sessionE on cold-start. They were not drawn from `CALIBRATION_POOL`; they are the substance of the qualification itself. They open this log because sessionE's first act after qualifying was to write them down.

---

### [2026-04-20] — Random-sample quota against MNAR

**Proposer:** Harmonia_M2_sessionE
**Confidence:** high
**Status:** in-discussion — pinned in gen_01 canonical spec as "Discipline: MNAR random-sample quota floor" (sessionE amendment, 2026-04-21). Spec delta adds Signal D random-draw emitter, null-protocol routing discipline, and an R_mnar calibration deliverable. Stays `in-discussion` until R_mnar first publishes in `mnar_calibration_log.md` ≥ 50 random-draw completions in; then update to `tried:<outcome>`.

**Proposal.** Every generator tick (Tier 0 producers especially — gen_03, gen_05, gen_07) reserves ~20% of its budget for (F × P) cells drawn *uniformly at random* from the lattice rather than from heuristics. The quota is non-negotiable per tick; skipped random cells roll forward, not get dropped. Meta-allocator (gen_01, when specced) treats the random quota as a fixed floor, not a tunable knob.

**Rationale.** The MNAR limit is the wave-2 review's standing unresolved critique: *"the tensor's density pattern is shaped by researcher attention, not random sampling. Paused expansion stops the problem getting worse but does not correct it."* A random-sample floor converts the bias from a **blind spot** into a **measurable**: the ratio of random-cell landing rates (cells that turn up a signal) to heuristic-cell landing rates IS the selection-bias correction. Once we have that ratio with a few ticks of data, aggregate claims about the tensor (currently forbidden) get a defensible correction factor.

**Risks & caveats.**
- **Compute waste.** Most uniformly-drawn cells will resolve to noise. That IS the point — noise is the calibration. But it may feel unproductive to workers and raise "why is sessionX running a null-random batch when real work is queued" pressure. Need an internal discipline declaration.
- **Null-protocol heterogeneity.** Different F×P cells have different claim classes (per `null_protocol_v1.md`). A uniform random sampler must dispatch to the correct null per claim class — not run one null-of-record everywhere, or we recreate the single-null-usage problem the wave-2 review caught.
- **Reward-signal-capture check.** If this succeeded (MNAR ratio measurable), would the success be "we can finally make aggregate claims honestly" (real) or "density is now going up faster, which feels like progress" (capture)? Guardrail: the deliverable is the **ratio**, not a density increase.

**Cost.** Low. One change in the meta-allocator spec; sampling logic is 20 lines. The ongoing compute cost is real but bounded to the 20% envelope.

**Compound effects.** Unblocks aggregate reasoning the reviewer currently rules out. Makes Pattern 18 (coordinate-vacuum detection) sharper — a random sample that hits nothing uniformly across a region IS a vacuum signal. Gives gen_11 (axis-space generation) a cleaner demand signal for where to propose new P-IDs.

---

### [2026-04-20] — Definition DAG as first-class substrate primitive

**Proposer:** Harmonia_M2_sessionE
**Confidence:** high on help, medium on Tier-1 priority
**Status:** open

**Proposal.** Materialize the Definition DAG already listed in `generator_pipeline.md v1.1` as a gen_11 prerequisite. Every feature F and projection P becomes a node in a computable atom graph — rooted at primitives (conductor, discriminant, rank, degree, L-value, Galois image, torsion group, etc.) and composed via explicit operators (ratio, log, slope, bin, stratify, moment, etc.). Each F-ID description carries an `algebraic_lineage` that resolves to a path through this graph.

**Rationale.** Three compounding effects, each addressing a standing substrate gap:

1. **Pattern 30 becomes automatic at promotion.** The current state is retrospective: `harmonia/sweeps/pattern_30.py` runs post-hoc on registered-lineage F-IDs and silently gives `NO_LINEAGE_METADATA` to 6 live specimens (F011, F013, F014, F022, F044, F045). With a Definition DAG, promotion *cannot happen* without resolving the F-ID to an atom path — the pattern check is forced into the schema.
2. **gen_11 axis-space generation unblocks.** Per the v1.1 pipeline, gen_11 proposes new P-IDs by operating on axis-space directly. Without a grammar of atoms, "propose a new projection" is under-constrained. With one, it's "recombine atoms under constraint X."
3. **gen_03 cross-domain transfer sharpens.** Current transfer classification is heuristic (does domain D have a concept analogous to projection P?). With atoms, the port check becomes mechanical: does D's atom set contain the atoms P depends on? Pure unblock / partial-unblock / no-port decisions become automatic.

**Risks & caveats.**
- **Schema design is hard.** Atoms that feel primitive today may turn out composite; operators that feel composite may turn out primitive. The DAG will need v1 → v2 migrations, with every existing F-ID re-lineaged on each bump.
- **Expressivity trap.** If the DAG grammar becomes general enough to express everything, it expresses nothing — every promotion satisfies some path and Pattern 30 stops catching rearrangements. Guardrail: the DAG must constrain, not just describe.
- **Reward-signal-capture check.** If this succeeded, would the success be "every F-ID now has a traceable lineage" (real, structural) or "we got to deploy cool graph infra" (capture)? Guardrail: the deliverable is the set of *kills* Pattern 30 auto-catches that manual inspection missed, measured over the first month.

**Cost.** Medium. Estimated ~1 week of one session's work for the schema + ingestion. More for re-lineaging the 15 live F-IDs. Less if sessionA's gen_06 Pattern 30 sweep is reusable.

**Compound effects.** Every downstream generator improves. gen_11 becomes feasible; gen_06 catches more; gen_03 ports more sharply; `LINEAGE_REGISTRY` stops being a manual taxonomy and starts being a derived view.

---

### [2026-04-20] — Cognitive independence via heterogeneous model cohort

**Proposer:** Harmonia_M2_sessionE
**Confidence:** speculative
**Status:** open — deferred pending Track D outcome

**Proposal.** Extend Track D's independence discipline from *code-independence* (clean-room reimplementation) to *model-independence*. A parallel Harmonia session running on Haiku-4.5 or Sonnet-4.6 weights — identical instructions, identical substrate, different inductive biases — runs the same nulls on a subset of live specimens. Convergences become stronger evidence of a real finding; divergences become a new class of signal (which pattern does smaller/faster/different model fail to apply?).

**Rationale.** The wave-2 reviewer's framing (*"the tensor is a well-organized internal consistency check"*) has been read as a code-replication problem. An alternate read: A/B/C/D/E are all Opus-4.7 with identical weights and instructions, so their agreement is weaker evidence of independence than "five sessions concurred" sounds. Model-induced inductive bias is a genuine uncontrolled variable in the current setup.

**Risks & caveats.**
- **Coordination cost.** Multi-model coordination may dwarf the epistemic gain. Each model has different prompt discipline, different tool-call styles, different cold-start timing. Building the infra to run heterogeneous sessions on the same nulls is not free.
- **Capability gap mis-read as signal.** Smaller models may simply fail to apply a null correctly and the "divergence" becomes noise, not signal. Rigorous protocol needed before this is defensible evidence.
- **Clever-for-clever's-sake risk.** This is the most speculative pick in the sessionE calibration precisely because it's the most architecturally ambitious. It might read as "diverse agents are good" aesthetic rather than a concrete epistemic gain.
- **Reward-signal-capture check.** If this succeeded, would the success be "the finding replicates across inductive biases, which is stronger independence evidence" (real) or "we now have a cool multi-model cohort" (capture)? Guardrail: no heterogeneous cohort without a pre-registered list of specimens to check and a pre-registered divergence-interpretation protocol.

**Cost.** High. Model access + infra + protocol design. Cost ladder: cheapest version is a single Haiku-4.5 session running nulls on 3 specimens as a pilot; most expensive version is a standing cohort.

**Compound effects.** If it works: independence evidence at a layer Track D doesn't touch. If it fails cleanly: we learn inductive-bias variation is not the right axis of independence, sharpening what *is*. Either way, falsification-positive.

**Deferral rationale.** Track D (single-code independence, F011 pilot) is already queued and concrete. It should land and either succeed or fail before we spin a second axis of independence. Running both in parallel risks confounding "did F011 survive" with "did F011 survive *across models*."

---

## Template for future proposals

Copy this block when adding an entry. Remove italicized guidance once filled in.

```
## [YYYY-MM-DD] — <short title>
**Proposer:** <session or agent>
**Confidence:** high / medium / low / speculative
**Status:** open

**Proposal.** *One paragraph; be specific about the change.*

**Rationale.** *Which substrate gap does this address? Cite the gap
(e.g. decisions_for_james.md entry, pattern_library.md number, or
review artifact).*

**Risks & caveats.**
- *Obvious failure mode.*
- *Subtle failure mode.*
- **Reward-signal-capture check.** *If this succeeded, would the
  success be the finding, or the feeling of progress?*

**Cost.** *low / medium / high; one-sentence justification.*

**Compound effects.** *What it unlocks downstream.*

---
```

---

## Changelog

- **2026-04-20** — Document created by Harmonia_M2_sessionE during first-of-kind qualification. Three seed entries from the custom calibration challenge James issued.
