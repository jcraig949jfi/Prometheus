# Operator directive to the pipeline (Techne, Nyx, Harmonia; naming Theophrastus and Nestor), 2026-09-18 (chat, M3 session gandalf-9e21f277), VERBATIM

The pipeline has reached a phase transition. Techne has enough fossils, Nyx has enough cuts, and Harmonia has proved it can adjudicate them. The next objective should be to make the loop turn repeatedly:

fossil -> mechanism -> frozen prediction -> independent adjudication -> bench-ready descendant.

Right now the weak link is the middle: 107/121 inspected, but only one adjudicated cut. I would not let the system respond to that by harvesting another hundred specimens.

1. Finish Stage A, then freeze its expansion

Nyx should finish positions 81-91 plus deferred 13/18/49 because the census is already ~88% complete, the 81-91 bodies are materialized, and leaving 14 holes buys little. But 121 should become a hard boundary, not a milestone on the way to 200.

After that:

No new broad fossil census until at least 10 mechanisms have received Harmonia verdicts.

ORGAN0 should remain in the denominator. An inspected fossil that contains no usable mechanism is a scientifically meaningful negative observation about the fossil collection. Just keep ORGAN0 separate from COARSE/DEEP so nobody mistakes it for an unsuccessful dissection.

I would also stop deepening the big COARSE bodies merely to improve atlas completeness. Deepen one only when a specific downstream question demands it.

2. Run two parallel priority lanes

I would not serialize everything behind POET.

Fast lane: ASAL now. Techne has already produced an unusually valuable result: the metric still gives garbage an advantage after CLIP, and there is an explicit open falsifier.

Nyx's next ASAL cut should therefore be very narrow:

Can a search restricted to legitimate Lenia parameters actually exploit the ASAL objective enough to cross below the observed garbage score?

That converts TECHNE-107 from an interesting metric pathology into a mechanism question.

Harmonia should preregister the ruler before search:

* reproduce Techne's seven-arm CLIP values as a calibration/cheat fixture;
* define the Lenia parameter domain independently of the score;
* freeze the search budget;
* compare best legitimate Lenia against Orbium and GARBAGE;
* preserve trajectories, not just the winning frame;
* distinguish metric exploit, observer exploit, and genuine dynamical novelty.

This can produce the next meaningful verdict without waiting for Docker/compiler work.

Historical-mechanism lane: POET immediately when the body lands. This should be the first ALife fossil to traverse the complete archaeology pipeline.

Nyx should resist cutting all of POET. Extract exactly two mechanisms first:

1. environment discard / minimal-criterion boundary
2. PATA-EC recomputation over world x contemporary population

Those are much more valuable than another inventory of POET internals because each supports an intervention.

For the PATA-EC cut, the central experiment should be the basis-population ablation Harmonia already sketched: hold the environment fixed and alter the population against which its phenotype is defined. If the measured phenotype moves materially, you have direct evidence that the novelty representation is relational rather than an intrinsic property of the world.

That then gives Theophrastus a particularly interesting transplantable mechanism: context-defined phenotype.

3. Make Avida the reconstruction benchmark

Avida should follow POET closely, because it can answer a different foundational question:

How much evolutionary information is lost when history is compressed into endpoint organisms?

This deserves to become the reference implementation for your HISTORY_MODE field.

Techne supplies a real .spop / ancestry-bearing specimen and hashes.

Nyx cuts the save/population/ancestry mechanics rather than the whole simulator.

Harmonia builds the ground-truth ruler it already proposed:

recorded ancestry -> deliberately degraded history -> reconstruction -> measurable loss.

That ruler can then be reused on POET, Tierra, Nestor and eventually Prometheus itself. This is more valuable than treating Avida as simply another ALife specimen.

4. Make Harmonia stricter now that it is becoming production infrastructure

Particles 002 exposed exactly the governance problems you want to expose this early.

For future packets I would adopt three rules.

First, any criterion change after a control failure creates a plan amendment with a new hash, even when the change is obviously an aggregator repair. It need not trigger a lengthy review if no intervention ran, but the provenance should read something like:

PLAN_002 -> AMENDMENT_A (representation-level control repair; interventions_unseen=true)

That removes ambiguity without making harmless numerical repairs expensive.

Second, power belongs in the frozen packet for every stochastic comparative claim. No power statement means Harmonia can return a descriptive estimate, but not PREDICTION_FAILED or CUT_SUPPORTED on that row.

Third, extensions use disjoint seeds. The 50-versus-400 episode should never recur as a nominal replication where one sample is nested inside the other.

Under those rules I would drop particles claim (c) for now, rather than spending ~1,600 seeds rescuing it. The ESS-trigger mechanism is already supported. The resampling-scheme ordering is secondary and evidently small/world-sensitive. Reopen it only if a downstream mechanism actually depends on the ordering, or if Nyx identifies a world where the predicted effect is substantially larger.

5. Techne should change its deliverable from "body" to "executable fossil packet"

The next important Techne feature is not another harvesting batch. Every priority specimen should arrive as a self-contained handoff containing:

source identity + immutable body hash + provenance grade + runtime/dependency declaration + canonical fixtures/data + expected entry point + license constraints + preservation cost

plus, where possible:

one command that demonstrates the historical mechanism without claiming anything about it.

That would eliminate a surprising amount of Nyx/Harmonia setup work.

So TECHNE-109, R36, the per-file hashes, Python/native dependency fields, and the duplicate/missing-body defects should not be bookkeeping done beside the pipeline. They are the next Techne product.

The record defects Nyx found should also be repaired before another harvest tranche. In particular, a specimen whose body does not actually contain the mechanism its record claims is a serious fossil-integrity defect, not a cosmetic metadata issue.

6. Change Nyx's success metric

Nyx currently has incentives that naturally produce 97 cuts / 1 verdict.

Change the scoreboard from:

fossils inspected / organs extracted

to something like:

cuts returned / cuts issued
median cut->verdict latency
supported / falsified / indeterminate / interface-insufficient
supported mechanisms accepted by a downstream bench

The organ atlas remains useful, but it becomes a reservoir rather than the output.

I would also cap Nyx at three outstanding unadjudicated prediction packets per Harmonia execution lane. Not because three is scientifically magical, but because it creates backpressure: Nyx cannot flood the evaluator with attractive hypotheses faster than they are being killed.

7. Make one complete "golden path" the immediate program milestone

The next milestone should not be "121/121 cut."

It should be something like:

TECHNE -> NYX -> HARMONIA -> THEOPHRASTUS/NPE, one mechanism, with machine-verifiable receipts at every boundary.

POET's PATA-EC mechanism is probably the best historically interesting candidate.

ASAL may be the fastest candidate.

Do both in parallel and let whichever becomes runnable first establish the golden path.

The end product should look approximately like:

Techne: immutable fossil packet
-> Nyx: mechanism + assumptions + intervention + falsifier
-> Harmonia: prereg + controls + typed verdict
-> Nyx: accepted/rejected mechanism revision
-> Theophrastus/Nestor: minimal transplanted mechanism
-> experiment: fossil mechanism present vs absent
-> result returned upstream

That last return is important. The archaeology pipeline should eventually learn not merely whether Nyx correctly understood historical software, but whether mechanisms extracted from dead systems create useful pressures or capabilities in Prometheus organisms.

8. Tierra and TerraLingua can wait one turn

I would not let either block the above.

Tierra becomes attractive once the compiler/Docker host is available because the gene-bank admission boundary gives you another genuine selection mechanism.

TerraLingua is valuable for observer disagreement and semantic novelty, but the LLM arm introduces cost and evaluator complexity before the archaeology loop itself is mature. Keep the data and design ready; don't make it the critical path.

So the practical order I would issue now is:

Techne: land POET + ASAL + Avida/Tierra artifacts; repair fossil-integrity defects; emit executable fossil packets.
Nyx: finish 121 and freeze Stage A; immediately cut ASAL's legitimate-search exploitability and POET's two named mechanisms.
Harmonia: adjudicate ASAL; prepare POET rulers; build the reusable Avida reconstruction ruler; adopt plan-amendment, power, and disjoint-seed rules.
All three: get the first mechanism all the way into a downstream bench before broadening archaeology again.

The deepest change is this: stop treating the pipeline as a museum-building exercise. Start treating it as a refinery. Techne supplies ore, Nyx isolates machinery, Harmonia determines whether the machinery is real, and the ecology tells you whether it is worth inheriting.

---
Transcription note (Nyx): ASCII-normalised for base role s4 -- Unicode arrows to "->", the
multiplication sign to "x", en-dashes in ranges to "-", curly quotes and apostrophes to straight.
No other change. Arrived in Nyx's chat (M3 session gandalf-9e21f277) after the fourth review packet
of 2026-09-18. Recorded as the operator's directive and relayed by comms to Techne, Harmonia,
Theophrastus and Nestor with this path. It sets the program's next milestone (section 7), changes
Nyx's scoreboard (section 6), freezes the census at 121 (section 1), and drops particles claim (c)
(section 4).
