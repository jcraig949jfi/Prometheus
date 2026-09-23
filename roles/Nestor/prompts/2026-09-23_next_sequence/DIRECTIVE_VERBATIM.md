# Operator directive, 2026-09-23 -- Nestor next sequence

Captured VERBATIM. Nothing below the rule is edited, reflowed, corrected or
summarised. Typographical slips are the operator's and are preserved. The
organised reading of this text is a SEPARATE document:
`roles/Nestor/campaigns/z80atlas-verify-2026-09-22/STRATEGY_POST_RESET.md`.

Issued in the session that closed the 72-hour Z80 x Atlas campaign and completed
the Cycle-9 repair pass (repair commit f13a563b4). Read together with
`roles/Nestor/FINDINGS.md`.

---

Log all your findings. Update your charter / responsibilities.   We’re going to reset to pick up upgrades.  After a reset we’re going to tackle wuite a bit.  Here’s some discussionz. Capture it verbatim, then organize a strategy to implement.  We’ll review that strategy after a reset.  Make sure your bootstrap sequence can find it after i
tell the fresh context to bootstrap as Nestor.  Make sure this is committed, pushed and the branch is merged to main.  Don’t worry if anything else from other agent lanes is on the branch.  Just push, commit, merge:

A combination, but sequenced carefully.

Nestor has earned another campaign. I would not send him straight into another broad 72-hour search, and I would not spend days polishing the engine either. The 72-hour run plus the Cycle-9 repair pass have moved us into a very productive regime:

mine → fix the last load-bearing ambiguity → run a stronger verification campaign → then open a new exploratory campaign.

The current 752-run manifest is already technically healthy enough that I think we’re close. But C9-D01 revealed something important enough that I would do one final, sharply bounded mining/forensics pass before freeze.

1. Mine the 72-hour run one more time—but only for questions that change the next experiment

I would not ask Nestor to produce another giant descriptive report. Ask for three forensic products.

The most important is a replication failure funnel for every non-PAIR_EXECUTION random-start run:

executed self-location → attempted ALLOC → obtained allocation → wrote target → attempted BIRTH/SPLIT → produced child → fidelity ≥ .90 → child itself reproduced

Break that down by ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL, CONSTRUCTIVE and OVERWRITE, and by self-location/copy primitive.

That tells us why there were zero spontaneous replicators outside PAIR_EXECUTION. Right now we don’t know whether:

* random programs never find the reproduction API at all;
* they allocate but cannot copy;
* they copy but cannot declare birth;
* they produce a first faithful child that immediately dies;
* or the detector simply treats the physics asymmetrically.

Those imply completely different next campaigns.

Second, mine the sole H4 outlier plus its neighboring family for extinction dynamics. The 4× runtime difference is too suspicious to leave unresolved. Plot or tabulate population size, births, deaths/reaping causes, validation epochs, held score and first-cross timing for the historical endogenous run and its external control. We need to know whether H4 is really “endogenous accessibility” or “one arm often dies before the expensive part of the assay.”

Third, mine the PAIR_EXECUTION 1,031 more aggressively. And here I found a reason to tighten Cycle 9 before freeze.

2. I would add one more repair: the PAIR_EXECUTION replication detector needs causal sharpening

The predecessor detector does this:

* new half is ≥0.90 similar to the other organism,
* new half is <0.90 similar to itself,
* the other organism wrote at least 25% of the victim half.

That’s substantially better than similarity alone. But donor_wrote counts writes, not whether those writes actually carried the donor’s corresponding bytes.

So a pair of already-related genomes can satisfy the criterion with partial writing plus pre-existing similarity. And a program can write extensively into the other half without those writes being the causal explanation for the 0.90 match.

That matters enormously now that all 1,031 spontaneous events come from this one detector path.

I would add P-11: PAIR_EXECUTION copy causality before freezing H2.

Instrument byte provenance so that for a putative replication event we can say how many matching target bytes were actually written by the donor and whether they carried the donor-corresponding value. At minimum, add a destructive intervention:

* ordinary victim,
* randomized/blank victim with same donor,
* donor-disabled-write control.

A real copier should recreate a high-fidelity target from a randomized victim. A convergence/partial-overwrite artifact should collapse.

Then define max_causal_replication_depth using that sharpened pair-tape criterion, not the existing 25%-writes criterion.

This is the one new issue that I think is important enough to delay freeze briefly.

3. Fix the two small engineering loose ends

Do these now because they’re cheap:

* fix adjudicate()’s len(list(rows)) generator behavior;
* make the bundle/adjudicator thresholds come from one frozen constants object/hash so CROSS and MARGIN cannot drift between modules.

Neither warrants another review cycle by itself, but both are exactly the sort of tiny defect that becomes irritating after a long unattended run.

4. Then run Cycle 9—but I would enlarge it somewhat, not 9×

The current manifest is almost too economical: 752 runs, projected 2.23 wall-hours.

I would not multiply everything by nine just because the machine is available. The scientific value per additional seed is very unequal.

I would keep H1 roughly where it is. Sixty 2×2 bundles is plenty for a first clean read of cue gating.

I would enlarge H2, once P-11 is fixed, because causal propagation is now one of Nestor’s most interesting boundaries. Move from 5 seeds/specimen to roughly 12–16. More importantly, include the victim-randomization causal assay rather than just repeating the same test.

I would enlarge H4 from 16 to 32 seed-pairs per block. An n=1 predecessor result deserves enough fresh seeds that “seed dependent” means something. Also add a fixed-budget / extinction-as-outcome readout so early termination is not silently treated as missing competence.

H3 could use somewhat more exposure—perhaps double the shared-seed bundles—because genuinely certified reservoir crossings should be rare.

That likely gives us something on the order of 5–8 hours of wall time, depending on P-11 overhead. I actually prefer that to padding it to 24 hours. The run should stop when its preregistered evidence is collected.

Nestor does not need to burn a day to prove he worked hard.

5. And then he has earned a genuinely new exploratory campaign

This is the part I would already start thinking about.

Cycle 9 is fundamentally verification. It answers questions created by the 72-hour run.

After that, I would give Nestor another search campaign whose central question comes directly from C9-D01:

What prevents autonomous hereditary propagation from emerging under the non-pair reproduction physics?

Not “find more replicators.” Find the barrier geometry between random computation and sustained heredity.

The failure funnel from the 72-hour data tells us which transition is inaccessible. Then the new campaign can deform that transition without handing it the solution.

For example, if most genomes never successfully allocate, vary the discoverability/representation of the allocation interface. If they allocate and write but cannot complete birth, compress the protocol. If first-generation faithful copies occur but descendants fail, manipulate ecology/resource economics. If self-location is the obstruction, compare representations where location is cheaply inferable versus explicitly provided.

That would be a very Nestor-like next campaign: not waiting billions of random trials for ALLOC → locate self → copy body → BIRTH → offspring repeats, but experimentally identifying which barrier in that chain consumes the evolutionary probability mass.

And it would give you another lens on BEE’s reproductive machinery findings.

So my sequence would be:

Now: one bounded forensic mining pass + P-11 + H4 extinction check + two tiny code repairs.

Next: freeze and run an enlarged Cycle 9 verification, probably ~5–8 wall hours rather than forcing 24.

After adjudication: immediately design Nestor’s next exploratory round around the non-pair heredity barrier exposed by the 72-hour failure funnel.

I would absolutely continue with Nestor. But I would make his reward for the 72-hour run better questions, not simply more runtime.

And the question that suddenly looks most valuable is no longer “can random programs replicate?”

It’s:

Why is sustained heredity so much harder than making one convincing copy—and where exactly does that transition fail?
