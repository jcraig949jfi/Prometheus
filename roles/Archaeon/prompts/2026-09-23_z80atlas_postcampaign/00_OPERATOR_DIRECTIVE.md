# ARCHAEON BOOT DIRECTIVE -- 2026-09-23
# Z80 x ATLAS POST-CAMPAIGN REPAIR + TARGETED FALSIFICATION
#
# This is the active directive for the next Archaeon session.
# Session context: worktree D:\Prometheus-worktrees\archaeon-wse-2026-09-16
#   branch archaeon/wse-2026-09-16 (already merged to main at bcb9f22ad)
# The 72-hour campaign is complete and committed. Main is current.
# Start fresh from main on the next session; the worktree can be rebuilt.
# Key artifacts already committed to main:
#   archaeon/z80atlas/campaign/CAMPAIGN_PACKET.md   (the completed packet)
#   archaeon/z80atlas/campaign/PACKET.json
#   archaeon/z80atlas/pivot/Z80ATLAS_REVIEW_2026-09-22.md (review packet)
#   archaeon/z80atlas/campaign/ATLAS_INDEX.jsonl    (per-run index)
#   archaeon/z80atlas/campaign/RUNS.jsonl           (run log)
#   archaeon/z80atlas/campaign/GRAMMAR_FROZEN.json  (grammar digest 63ffdeca16db3333)
#   Per-run artifacts: archaeon/z80atlas/campaign/runs/<family>/<run_id>/
# DO NOT re-run the 72-hour campaign. Do not alter historical records.
# Comms: EW_DB_HOST=192.168.1.202 (M1 Postgres, as always).
# Timestamps from `date -u` only.
#
# --------------------------------------------------------------------------

ARCHAEON -- Z80 x ATLAS POST-CAMPAIGN REPAIR + TARGETED FALSIFICATION

The 72-hour Z80 x Atlas campaign is complete. Do not rerun it, rewrite it,
or alter its historical evidence.

A post-campaign audit found a load-bearing instrumentation defect in the
spontaneous_replication signal.

The late-stage transplant constructor injects evolved tapes into the new
world and then sets:

    init = "random"

The engine's spontaneous_replication predicate tests init == "random" but
does not exclude transplanted ancestry.

The committed packet shows that all 26 runs flagged spontaneous_replication
are transplant verification runs:

  * 10 transplant:same
  * 12 transplant:environment_swap
  * 4 transplant:world_swap
  * 0 fresh-seed verification runs
  * 0 primary exploration runs

Therefore the campaign currently establishes zero verified de-novo
spontaneous replication events.

The 26 runs remain valid evidence of transplanted-lineage reproductive
persistence/robustness. They must not be discarded. They must be
reclassified.

Your job has four phases.


PHASE 1 -- PRESERVE THE ORIGINAL EVIDENCE
------------------------------------------

Treat the completed 72-hour campaign as immutable historical evidence.

Do not:
  * edit historical RECEIPT.json, SPEC.json, telemetry, snapshots, events,
    or run records;
  * change the frozen grammar digest;
  * silently regenerate the original packet in place;
  * delete the 26 flagged runs;
  * change thresholds to obtain a desired result.

Record the defect explicitly as a post-campaign instrumentation finding.

Produce an audit receipt that identifies:
  1. the exact code path that creates transplant verification specs;
  2. the exact code path that initializes transplanted tapes;
  3. the exact predicate that labeled the run spontaneous;
  4. why those three together produce the false classification;
  5. the complete list of affected run IDs.

The old packet remains historical.

Create corrected/adjudicated artifacts under a new clearly named
post-campaign directory or filename.


PHASE 2 -- REPAIR PROVENANCE
------------------------------

Repair Archaeon's world/engine instrumentation so replication provenance is
causal, not inferred from the nominal init label.

Use the Bellerophon/BEE-side implementation in prometheus/z80atlas/ as a
reference for the mechanism, but implement and test it natively in Archaeon's
harness.

At minimum, distinguish initial organisms originating from:
  * random initialization;
  * seeded replicator initialization;
  * transplanted lineage initialization.

Track genetic ancestry through reproduction.

A replication event may be called spontaneous_replication only if the
replicating genetic lineage has no seeded or transplanted ancestor.

Do not merely add:

    and not spec.get("transplant")

to the existing predicate and call the problem solved.

The invariant must survive descendants, overwrites, partial copies,
migrations, and other reproduction mechanisms. Provenance has to travel with
genetic material far enough to answer:

    Did this replicator descend causally/genetically from material
    deliberately inserted by the experimenter?

Add explicit machine-readable fields such as the equivalent of:
  * origin class;
  * genetic lineage ID;
  * seeded/transplanted ancestry boolean;
  * first replicator ancestry;
  * ancestry depth or lineage chain where practical.

The exact schema is yours, but ambiguity is not acceptable.

Required tests

Before touching any scientific result, construct tests proving at least:
  1. random organism -> random descendant -> qualifying replicator may be
     spontaneous;
  2. seeded replicator -> descendants can never be spontaneous;
  3. transplanted replicator -> descendants can never be spontaneous;
  4. transplanted lineage surviving many generations remains
     provenance-tagged;
  5. world swap does not erase provenance;
  6. environment/task swap does not erase provenance;
  7. migration does not erase provenance;
  8. endogenous overwrite/copy cannot turn inserted ancestry into random;
  9. true independently arising random lineage remains distinguishable from
     an inserted lineage in the same world;
  10. old false-positive pattern is caught by a regression test.

Run the existing full self-test suite afterward.

No scientific run proceeds unless all provenance tests and existing tests pass.


PHASE 3 -- RE-ADJUDICATE THE 72-HOUR CAMPAIGN WITHOUT RE-RUNNING IT
----------------------------------------------------------------------

Using the preserved campaign records, produce a corrected post-campaign
interpretation.

At minimum:

A. Reclassify the 26 events

   Classify them as something like:

       transplanted_lineage_replication

   or another precise term.

   Do not call them spontaneous, de-novo, abiogenic, or random-origin
   replication.

   State plainly:

       verified de-novo spontaneous replication in the completed campaign = 0

   unless preserved evidence demonstrates otherwise under the repaired
   provenance definition.

B. Recompute family mechanical scores

   spontaneous_replication carried weight 5.

   Recompute the top-family table with the invalid flag removed.

   Do not overwrite historical scores. Report:
     * original score;
     * corrected score;
     * which flag changed;
     * corrected ordering.

   Pay particular attention to:
     * 2ace470e5c47
     * 5b237a475b69
     * e8394eee206d
   Their original score 17 should not survive solely because of the invalid
   spontaneous flag.

   Preserve whatever other signals remain.

C. Preserve the transplant result

   Separately characterize what the 26 runs genuinely establish.

   For each relevant family, report whether transplanted organisms:
     * persisted;
     * reproduced endogenously;
     * retained task competence;
     * survived same-world transplant;
     * survived world swap;
     * survived environment/task swap;
     * survived physics swap if applicable.

   Do not downgrade a genuine transplantation result merely because its
   label was wrong.

D. Reframe topology cautiously

   The campaign shows a strong association with the niches regime, but niches
   also unlocks migration, reservoir, and some environmental structures.

   Use the terminology:

       niches-regime association

   until topology itself is isolated.

   Do not claim a pure topology causal effect from the adaptive 72-hour
   campaign.

E. Reframe recombination cautiously

   Audit the matched-control construction around recombination.

   If changing reproduction from EXTERNAL to endogenous also necessarily
   removes recombination because of grammar constraints, document that as a
   confound.

   Do not claim a clean causal recombination effect from those rows.

Produce:

    Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_<date>.md

and a machine-readable companion JSON.


PHASE 4 -- RUN A SMALL, FIXED, PRE-REGISTERED DE-NOVO REPLICATION EXPERIMENT
-------------------------------------------------------------------------------

Do not launch another open-ended 72-hour adaptive campaign.

The survey has already done its job: it identified a candidate region.

Now test the candidate directly.

Scientific question

    Under candidate structural conditions identified by the campaign, can a
    genuinely random population generate a self-sustaining endogenous
    replicator without any seeded or transplanted genetic material?

Core candidate

Start from the strongest relevant structural neighborhood centered on:
  * world.topology = niches
  * reproduction = ENDOGENOUS_COPY
  * init = random

Use the campaign's best-supported neighboring settings to instantiate
candidate cells, but do not simply choose one winning family and call it
the answer.

Pre-register the exact configurations before observing outcomes.

Experimental design

Use fixed allocation.

  No adaptive promotion.
  No family scoring that changes allocation.
  No transplants.
  No seeded replicators.
  No warm starts.
  No reuse of evolved tapes.
  No manual intervention after results begin.

Every replicate gets equal compute within its arm.

Run enough independent seeds to estimate an actual event frequency rather
than produce anecdotes.

Target an initial screen on the order of 8-16 independent seeds per
configuration if computationally reasonable.

If the candidate region contains multiple plausible configurations, prefer a
small factorial/ablation set rather than a single hand-picked winner.

At minimum include:
  1. candidate niches condition;
  2. a topology-matched ablation where possible;
  3. well-mixed comparison;
  4. any minimal condition needed to separate topology from
     migration/reservoir effects.

Hold everything else identical wherever the grammar permits.

If the current grammar cannot isolate topology from the coupled variables,
report DESIGN_NOT_IDENTIFIABLE rather than improvising.

Primary endpoint

The primary endpoint is not "many births."

It is:

    emergence of an endogenous replicating lineage whose genetic provenance
    contains no seeded or transplanted material, which persists for a
    pre-registered minimum period/population criterion and meets the frozen
    fidelity criterion.

Pre-register the exact numerical criterion before running.

The criterion must include ancestry/provenance.

Record the first qualifying replicator's:
  * tape/genome;
  * lineage;
  * full available ancestry;
  * first replication time;
  * reproduction mechanism;
  * fidelity;
  * population trajectory;
  * persistence duration;
  * niche/location history;
  * task competence, if any.

Controls

Include positive controls proving the reproduction machinery remains
operational.

Include a negative/provenance control demonstrating that an injected
replicator is correctly identified as inserted rather than spontaneous.

Do not let the control contaminate treatment worlds.

Outcome language

Allowed outcomes include:
  * REPRODUCIBLE_DE_NOVO_REPLICATION
  * RARE_DE_NOVO_EVENT
  * NO_DETECTABLE_DE_NOVO_REPLICATION
  * INSTRUMENT_FAILURE
  * DESIGN_NOT_IDENTIFIABLE

Do not manufacture significance from a zero/one-event result.

If zero events occur, calculate the corresponding event-rate bound/interval
from the actual number of independent trials.

If events occur, report the denominator prominently.


STOP CONDITIONS
----------------

Stop and report rather than patching mid-run if:
  * provenance tests fail;
  * the grammar cannot produce a clean comparison;
  * old campaign artifacts required for re-adjudication are missing;
  * positive controls fail;
  * the candidate experiment accidentally receives inserted tapes;
  * random initialization is not actually random-only;
  * a threshold or endpoint would need to change after seeing results.

Any repair after preregistration requires a new preregistration and a new
run identity.


FINAL REPORT
-------------

Return one concise review packet containing:
  1. defect diagnosis;
  2. regression test demonstrating the old bug;
  3. repair commit/hash;
  4. full test results;
  5. list of all 26 reclassified runs;
  6. original versus corrected top-family ranking;
  7. corrected interpretation of 5b237a475b69;
  8. niches-regime analysis;
  9. recombination confound analysis;
  10. targeted experiment preregistration;
  11. targeted experiment results;
  12. exact numerator/denominator for genuine de-novo replication;
  13. evidence pointers for every positive event;
  14. explicit recommendation for the next scientific move.

The purpose of this round is not to rescue the spontaneous-replication claim.

The purpose is to determine whether there is a real phenomenon underneath
the false label.

A clean null result is a successful result.
