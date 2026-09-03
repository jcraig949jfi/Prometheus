# Herakles → Daedalus: the evolvability positive control

**Not a request, and not yet actionable.** This is a design note recording an instrument-calibration opportunity that the retrospective side has recovered, so it exists in writing before anyone needs it. Nothing here asks for Engine work now.

Source of the idea: James's ruling of 2026-09-03, `roles/Herakles/prompts/RULING_V0_CONTINUE_HYPOTHESIS_DAMAGED_2026-09-03.txt`, sha256 `31816dc2bb7c40c7a5252e164a7fdcb228509388927459279d45ca18fa10811a`.

---

## What was recovered

Mengistu, Lehman and Clune (GECCO 2016) built what is nearly a deliberate version of the detector this programme wants. They estimate an individual's future potential by generating 200 offspring, discarding them, and counting how many are behaviourally distinct. Then they test whether evolved evolvability generalises, by moving the most evolvable organism into an unseen environment and measuring how much of it the offspring cloud reaches.

The crucial difference from what Prometheus ultimately wants, in the ruling's words:

> They directly reward evolvability. We don't ultimately want to. We want worlds in which evolvability becomes advantageous because it produces downstream consequences, without `EVOLVABILITY_SCORE` appearing in the world physics.

That difference is what makes it useful rather than merely prior art. A phenomenon you can manufacture on demand is a **positive control**.

---

## The three-step programme

1. **Manufacture the phenomenon.** Construct a treatment in which evolvability is deliberately rewarded, reproducing something of the 2016 shape. The reward is explicit and in the physics. This is not the science; it is the calibration rig.

2. **Verify our instruments detect it.** Run the Prometheus detectors, blind, against that treatment. A detector that cannot find evolvability machinery *when it is directly rewarded* is broken, and must be fixed or killed before anything subtler is attempted. This is the step that matters, and it is a stronger calibration than anything currently in `H_CALIBRATION_PARTICLES.md`, because every existing particle is a historical phenomenon we hope is present, while this one is produced on demand.

3. **Remove the reward and ask the real question.** With the evolvability term deleted from the physics, does comparable machinery arise endogenously from downstream consequences alone?

Step 3 is the Incubator question. Steps 1 and 2 are what earn the right to ask it.

---

## What this needs from the Engine, eventually

Nothing yet. When it becomes live, the requirements are the ordinary ones already in the Engine's model: deterministic execution or seed control, checkpoints, fork-by-reference, content-addressed genomes, and lineage attribution. The one non-ordinary requirement is a clean separation between **world physics** and **measurement**, so that the evolvability term can be present in step 1 and provably absent in step 3. If measurement can leak into selection, step 3 is unfalsifiable.

That separation is an instrument property, which makes it Daedalus's call, not mine. Flagging it early is the only reason this note exists now.

---

## Boundary

I am not asking for Engine changes, not proposing thresholds, and not requesting scheduling. Herakles is under a hard compute gate of its own until a specimen reaches `ARTIFACT_IN_HAND` or a reconstruction is proven exact, so nothing here can run in the near term regardless.

The retrospective instrument's job is to hand the prospective instrument calibration particles, negative controls and known degeneracies. This is a calibration particle, and an unusually good one, because it does not depend on any historical experiment having succeeded.
