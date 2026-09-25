# OPERATOR DIRECTIVE -- 2026-09-24 -- ARCHAEON ENVIRONMENTAL GATING CAUSAL ASSAY (verbatim)

Captured by Archaeon session m2-db608f52. Text below is the operator's, unedited.

---

ARCHAEON — ENVIRONMENTAL GATING CAUSAL ASSAY

The previous round is closed.

Accepted facts from the completed work:

* The original spontaneous-replication claim was invalidated and repaired.
* The seeded-world moat ledger is CLOSED:
    * 932/932 relevant runs replayed byte-identically.
    * 828 seeded moat_advantage flags qualified.
    * 104 were void from inserted-witness-only ancestry.
    * lower and upper ranking bounds agree on the 33-family top tier.
* The random-tape census is complete and preregistered:
    * 24 million random tapes;
    * vmcopy32 exact self-copier density ≈ 9.6e-6;
    * 96 exact vmcopy32 copiers / 10M;
    * ≈99% input-gated;
    * 82/96 exact copiers gate at input byte 128;
    * the historical 84616cf8257b_s1_cont specimen is an ordinary member of this architecture class, not a special target;
    * z80 strata produced zero copiers;
    * observed campaign survival is consistent with a rare initial-tape lottery.
* The adaptive sampler defect is repaired.
* The support/identifiability preflight is now a launch gate.
* The campaign evidence has a verified local evidence bundle, but still needs an off-machine copy.

This round is NOT another Atlas search, NOT another family-ranking campaign, and NOT an attempt to reproduce 84616cf8257b.

The scientific question is now narrower:

Does access to a small set of environmental input values causally control whether random vmcopy32 self-copiers can establish persistent reproductive lineages?

The census suggests yes.

Now falsify that mechanism.

0. FIRST: OFF-MACHINE EVIDENCE COPY

Before spending compute, make one verified off-machine copy of:

C:\Prometheus-data\evidence\z80atlas_campaign_2026-09-19\

Preferred destination: M1 if an already-authorized Prometheus transfer path exists.

Do not invent credentials, expose secrets, or block the scientific round indefinitely if no authorized path exists.

If transfer is possible:

1. copy the complete frozen evidence bundle;
2. preserve filenames and manifest;
3. verify every file against the existing manifest after transfer;
4. record:
    * source;
    * destination;
    * file count;
    * byte count;
    * manifest SHA;
    * verification result;
5. do not make the remote copy writable by the experiment.

If no authorized off-machine path exists, record OFF_MACHINE_COPY_BLOCKED with the exact missing dependency and continue. Do not improvise cloud credentials.

1. NEW CAMPAIGN IDENTITY

Environmental inflow changes the world mechanics.

Therefore this assay requires:

* a new experiment/campaign identity;
* a new grammar/mechanism digest;
* its own preregistration;
* its own result directory;
* no modification of the completed Z80 × Atlas campaign.

Do not call this a continuation of the 72-hour campaign.

The historical census and campaign are frozen inputs to the design.

2. CENTRAL DESIGN PRINCIPLE: PAIRED RANDOM TAPE STREAMS

Chance variation in which random tapes appear must NOT be allowed to masquerade as an environmental effect.

For every replicate block, generate one preregistered random vmcopy32 inflow tape stream.

Use the IDENTICAL tape sequence in every environmental arm of that replicate.

The arms may differ only in the environmental input transformation specified below.

Use separate RNG streams for at least:

* random inflow tapes;
* environmental inputs;
* world stochasticity/mutation where applicable.

Record their seeds separately.

Changing an environmental arm must not alter which tapes enter the corresponding paired worlds.

Add a regression test proving paired arms receive byte-identical inflow tape sequences.

3. MINIMAL RANDOM-INFLOW MECHANISM

Do not redesign the ecology.

Add the smallest mechanism needed to expose a persistent world to a fixed stream of fresh random tapes.

Use dedicated inflow/inlet cells or an equivalently isolated mechanism such that:

* inflow never overwrites an established organism outside the designated inlet;
* the number/timing of offered random tapes is fixed independently of population size;
* occupancy differences between arms cannot silently change the number of random tapes tested;
* inflow founders are explicitly provenance-labelled random_inflow;
* descendants retain that ancestry;
* simply occupying an inlet cell does NOT count as establishment;
* a lineage must reproduce out of the inlet and establish outside it to count.

The exact engineering implementation is yours, but the assay must have a fixed and arm-independent denominator:

random tapes introduced

not merely elapsed epochs.

Before the experiment, test that inflow itself does not change the RNG stream of the existing engine except through the explicitly isolated inflow RNG.

4. ENVIRONMENTAL ARMS

Use vmcopy32 only.

Hold reproduction physics, genome size, mutation mechanism, resource rules, topology, inflow rate, tape streams, and all other environmental parameters fixed.

Primary arms:

U — UNIFORM

Input byte sampled uniformly over 0..255.

This is the baseline.

BAND-BLOCK — GATE BAND REMOVED

Same base environmental RNG stream as U, but values 120..135 are deterministically mapped/rejected according to a preregistered RNG-neutral transform so those values never reach organisms.

The transform must not consume a variable number of world RNG draws.

SHAM-BLOCK — EQUAL-SIZED NON-GATE BAND REMOVED

Exclude a 16-byte interval containing no or minimal exact-copier gates according to the already-frozen census.

Choose and record this interval BEFORE any ecology result is observed.

This controls for merely narrowing the input alphabet.

128-BLOCK — DOMINANT GATE REMOVED

Exclude input byte 128 while otherwise preserving the input distribution as closely as possible.

This tests the dominant census mechanism directly.

RESCUE-128

Start from BAND-BLOCK, but restore byte 128 at its uniform marginal frequency of 1/256.

Do not restore the rest of 120..135.

This is the critical rescue arm.

If the census mechanism is causal, removing the gate should suppress establishment and restoring only the dominant gate should recover part of it.

If all five arms cannot be made comparable without introducing additional mechanics, stop with DESIGN_NOT_IDENTIFIABLE rather than silently changing the comparison.

5. DO NOT TARGET THE HISTORICAL SPECIMEN

84616cf8257b_s1_cont is a specimen and positive reference only.

Do NOT:

* seed its tape;
* search mutations around its tape;
* tune the environment to input 121 because that specimen uses 121;
* optimize toward its architecture;
* use its success as a promotion signal.

The gate band comes from the full frozen random-tape census, especially the population-level concentration at 128.

The assay is about an architecture class, not one fossil.

6. PRE-EXPERIMENT RULERS AND CONTROLS

Before any treatment world runs, all of these must pass.

A. Tape-stream pairing

For every replicate block, all five arms receive exactly the same inflow tapes in exactly the same order.

B. Input transforms

Over a large dry-run stream:

* U is uniform over 0..255.
* BAND-BLOCK contains zero 120..135 values.
* SHAM-BLOCK contains zero values from its frozen sham band.
* 128-BLOCK contains zero 128 values.
* RESCUE-128 contains no 120..135 values except 128 and contains 128 at the preregistered rate.

C. Known copier controls

Use several independently discovered census copiers as controls, not only 84616.

At minimum include:

* common 128-gated copiers;
* non-128 gated copiers if present;
* a non-copier;
* the historical specimen only as one reference among these.

Show before treatment that:

* a 128-gated copier can reproduce under U;
* it cannot use its missing gate under 128-BLOCK/BAND-BLOCK;
* RESCUE-128 restores the opportunity;
* the sham exclusion does not eliminate the same copier solely through alphabet narrowing.

These controls do not count as treatment results.

D. Provenance

Inserted controls must never be scored as de-novo/random-inflow establishment.

E. Support/identifiability preflight

The new launch preflight must PASS.

PASS_WITH_RESTRICTIONS is not sufficient for this experiment.

Do not use --accept-preflight to waive a restriction.

Fix the design or stop.

7. FIXED ALLOCATION

No adaptive promotion.
No early family ranking.
No arm gets extra compute because it looks promising.
No threshold changes after observation.
No optional “one more seed.”

Use paired replicate blocks.

A reasonable initial design is:

* 16 paired replicate blocks;
* all 5 arms in every block;
* identical inflow tape stream within block;
* fixed tape exposure per arm.

Choose the exact tape exposure before launch using:

* the frozen copier census rate;
* measured world throughput;
* the available bounded runtime.

The exposure should be large enough that the uniform arm is expected to encounter many latent exact copier tapes, not zero or one.

Do not power the design using the historical 1-survivor estimate alone.

The census density is the primary planning quantity.

Record the expected number of exact-copier arrivals per replicate before launching.

8. OBSERVABILITY: LATENT OPPORTUNITY VS ECOLOGICAL SUCCESS

For every inflow tape, optionally/classificationally evaluate it with the already-frozen offline census ruler without affecting the world.

Record whether the incoming tape is:

* non-copier;
* near copier;
* exact copier;
* exact gated copier;
* its gate set;
* whether its gate is available in that environmental arm.

This gives two separate quantities:

Opportunity

How many latent reproductive tapes entered?

Conversion

How many became established lineages?

The primary analysis must not confuse these.

Because the same tapes are paired across arms, latent opportunity should be identical except for gate availability.

9. PRIMARY ENDPOINT

Define ESTABLISHED_RANDOM_INFLOW_LINEAGE before launch.

It must require all of:

1. ancestry contains only random/random-inflow founders;
2. lineage has left the designated inlet region;
3. endogenous reproduction has occurred;
4. all original members of the relevant inflow arrival are dead;
5. descendants persist for at least a preregistered multiple of max_age;
6. lineage reaches either:
    * a preregistered minimum population fraction, or
    * a preregistered generation-depth + persistence criterion;
7. establishment is not maintained solely by continued fresh inflow of the same tape, because inflow tapes are independently random.

Do not require mean fidelity >=0.9 as the only primary definition.

The previous campaign already showed that a biologically meaningful persistent lineage can have low global mean fidelity.

Record fidelity as a phenotype, not as a gate that automatically erases the phenomenon.

10. SECONDARY ENDPOINTS

For every established lineage record:

* first inflow tape;
* tape SHA;
* gate set from the frozen offline ruler;
* input that produced first successful copy;
* first reproduction epoch;
* generation depth;
* population trajectory;
* persistence duration;
* exact/near-copy fraction;
* lineage diversity;
* dominant descendant tapes;
* mutation path;
* task/environment interaction;
* whether descendants retain the original gating;
* whether gating broadens, narrows, shifts, or disappears.

Also record:

* exact copier arrivals per million inflow tapes;
* gated copier arrivals per million;
* establishment per million inflow tapes;
* establishment per latent exact copier;
* extinction time distributions;
* time from copier arrival to establishment.

11. PRIMARY CAUSAL CONTRASTS

Preregister these before running:

1. U vs BAND-BLOCK
    * Does removing the census gate band suppress lineage establishment?
2. U vs SHAM-BLOCK
    * Is any suppression specific to the gate band rather than alphabet reduction?
3. U vs 128-BLOCK
    * How much of the effect is carried by the dominant byte 128 gate?
4. BAND-BLOCK vs RESCUE-128
    * Does restoring one mechanistically predicted byte rescue establishment?

The RESCUE comparison is especially important.

A mechanism is much more convincing if:

remove predicted gate -> effect disappears
and
restore predicted gate -> effect returns.

Use paired-block statistics wherever possible because the same inflow tapes occur in all arms.

Do not reduce the result to five unrelated binomial rates if the paired structure contains more information.

12. FALSIFIERS

The environmental-gating hypothesis is weakened or killed if any of these occur:

* BAND-BLOCK establishes lineages at the same paired rate as U despite copier gates being unavailable;
* SHAM-BLOCK suppresses establishment as strongly as BAND-BLOCK;
* 128-BLOCK has no effect despite most latent exact copiers requiring 128;
* RESCUE-128 fails to restore any establishment opportunity where 128-gated latent copiers are known to have entered;
* established lineages arise predominantly from tapes classified as non-copiers and use unrelated mechanisms;
* input gating disappears once ecology is instrumented correctly;
* the apparent effect is explained by changed tape exposure, occupancy, resource supply, mutation budget, or RNG consumption.

Any of those is scientifically useful.

Do not rescue the hypothesis with new post-hoc arms.

13. IMPORTANT POSSIBILITY: ECOLOGY MAY DISCOVER SOMETHING BETTER

Do not force every surviving lineage into the census copier taxonomy.

If a random inflow lineage establishes through a mechanism not recognized by the offline copier ruler:

* preserve it;
* classify it separately;
* reconstruct ancestry;
* disassemble it;
* test it under counterfactual input streams;
* label it NOVEL_REPRODUCTIVE_MECHANISM_CANDIDATE.

Do not change the primary endpoint or treatment allocation because of it.

This is where anti-gravity matters most.

14. DECISION RULE AFTER THE ASSAY

At close, distinguish at least these outcomes:

GATING_CAUSALLY_SUPPORTED

Gate removal suppresses establishment in the paired comparison, sham removal does not, and rescue restores the predicted opportunity.

GATING_PARTIALLY_SUPPORTED

One or more contrasts support gating, but rescue/specificity is incomplete.

GATING_NOT_SUPPORTED

The predicted environmental manipulation does not materially change establishment.

ALTERNATE_MECHANISM_OBSERVED

Persistent random-origin lineages establish primarily by a different mechanism.

NO_ESTABLISHMENT_AT_TESTED_EXPOSURE

No arm produces established lineages despite adequate latent-copier exposure.

DESIGN_OR_INSTRUMENT_FAILURE

A ruler, provenance invariant, pairing condition, or preflight fails.

Do not force a binary answer if the result falls between these.

15. WHAT COMES AFTER — DO NOT RUN IT YET

Do NOT immediately launch the general random-inflow ecology.

This assay decides whether environmental input gating is a causal lever.

After closure:

* if gating is supported, the next open-ended ecology should deliberately vary environmental information structure while remaining mechanism-agnostic;
* if gating is not supported, the random-inflow ecology should not be built around the copier-gate story;
* if a novel mechanism appears, preserve it and let that result redirect the next design.

No next campaign launches without operator review.

16. DELIVERABLES

Return one self-contained review packet containing:

1. off-machine evidence-copy status;
2. new campaign identity and grammar digest;
3. prereg commit, proving it predates treatment runs;
4. exact five-arm design;
5. frozen sham interval and why it was selected;
6. tape-stream pairing proof;
7. input-transform validation;
8. support/identifiability preflight;
9. control results;
10. number of inflow tapes per arm;
11. number of latent exact/gated copiers encountered;
12. established lineage numerator/denominator by arm;
13. paired causal contrasts;
14. rescue result;
15. every established lineage with evidence pointers;
16. any novel reproductive mechanisms;
17. falsifiers that fired;
18. explicit verdict among the categories above;
19. recommendation for whether a general random-inflow ecology is now justified.

Commit and push all code, preregistration, rulers, compact results, and review artifacts.

Large run state may remain outside Git, but must receive manifests and hashes.

A null result is acceptable.

The question is not whether we can make a copier live.

The question is whether the environment supplies a causal key that turns latent random reproductive machinery into an established lineage.
