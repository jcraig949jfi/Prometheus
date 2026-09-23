# Operator directive, 2026-09-21: APHRODITE -- LOCAL ENGINE (verbatim)

Logged unedited, including the framing that preceded the directive block.
Smart quotes and dashes are the operator's own. Nothing is paraphrased.

---

Nestor and Archaeon are tied up.  Let’s see if we can grind through this, iterstively.  Produce external reviews incrementally.  Use TDD where you can.

Yes. In fact, I think that may be the cleaner move.

For Aphrodite’s question, the engine is mostly a substrate for producing and receiving separable improvements. It does not need to be fast, frontier-grade, or even particularly capable. It needs to be auditable. A crude local engine could actually improve the science by making state, compute, serialization, reset, and transplantation much easier to control.

The only thing to be careful about is the frozen preregistration. I’d separate two decisions:

* She can build the local engine immediately. That doesn’t consume Campaign 1 data and doesn’t require Archaeon or Nestor.
* Whether that engine becomes the confirmatory C1 substrate depends on the frozen substrate-selection rule. If the existing rule doesn’t permit it, using it for C1 would require a dated pre-data amendment. Since no C1 data exists, that’s scientifically legitimate—but it should be explicit rather than smuggled in as “just implementation.”

I would make the engine almost aggressively simple. One local model or worker, one fixed improver loop, five editable modules because that’s already your artifact definition, strict generation boundaries, full reset between recipients, no network, sealed evaluator, hard token/step/time accounting, and a single canonical serialization format for the five modules. The entire engine should fit comfortably enough in one head that Vivarium can say exactly what persisted and Harmonia can meter every operation.

The design objective should not be “make a good local agent.” It should be:

Make the smallest engine in which an evolutionary lineage can produce a bounded artifact, that artifact can be extracted, and a completely fresh recipient can either benefit from it or not.

That suggests an engine with four very hard boundaries:

1. Worker — does the task.
2. Improver — proposes changes to the five modules.
3. Artifact vault — contains only the generation-8 module bytes.
4. Evaluator — invisible to worker and improver except for whatever scalar feedback the prereg permits.

Everything else should be disposable.

And “slow” barely matters. If a lineage takes 45 minutes instead of 3 minutes, that’s an economics problem. If it takes 10 hours, that’s a sample-size problem. Neither changes the causal question. Your positive control already tells you whether the substrate is so weak that the experiment is insensitive.

There is even a scientific advantage to using a weak substrate. Suppose a tiny, mediocre worker produces an artifact that improves another fresh tiny, mediocre worker. That’s arguably cleaner evidence for transferable machinery than showing that an already enormous pretrained system can squeeze another three points out of itself. The inherited competence of the base model becomes a smaller part of the story.

I’d therefore stop thinking of Nestor’s benchmark as a prerequisite for whether Aphrodite can do science. It was answering an engineering/economic question: which available substrate gives us the most experiment for the budget? That’s useful, but it shouldn’t hold the scientific program hostage.

I would give her this directive:

APHRODITE — LOCAL ENGINE

Build the cheapest self-contained local engine capable of executing the frozen Campaign 1 causal structure.

Optimize for auditability, reset integrity, transplantability and experimental throughput—not benchmark quality.

Requirements:

* fully local/offline during experimental execution;
* fresh recipient creation from a canonical base image;
* exactly defined editable machinery;
* byte-canonical generation-8 artifact extraction;
* hash-before/hash-after transplant;
* no donor state outside that artifact;
* identical loader path for scratch/sham/positive/transplant;
* strict compute escrow beneath the improver;
* deterministic seeds where the substrate permits them;
* exhaustive receipts for every read/write crossing the donor-recipient boundary;
* positive control must demonstrate that the substrate is capable of expressing a detectable transferable improvement.

Do not optimize the engine after looking at Campaign 1 outcomes.

Build it, qualify its mechanics, measure its economics, and report whether it can support the frozen experiment at a useful lineage count.

Do not run C1 until its status relative to the frozen substrate-selection rule is explicitly resolved.

And if her local machine only supports, say, 16 or 24 lineages rather than 64, I wouldn’t automatically reject it. I’d rather have 24 extremely clean transplants next week than a theoretically optimal substrate blocked behind other 72-hour campaigns.

The deepest point is yours: the engine is not the product. The causal artifact is. Aphrodite should be permitted to make the engine as ugly and cheap as necessary, provided the membrane around that artifact is beautiful.
