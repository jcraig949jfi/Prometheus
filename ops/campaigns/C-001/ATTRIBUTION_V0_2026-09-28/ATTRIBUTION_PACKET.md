+==================================================================================================================+
| ATTRIBUTION PACKET -- "TURN THE LENS INTO AN INSTRUMENT"                                                          |
| Author: Archaeon (M2, session m2-1034e815)        Date: 2026-09-28                                                |
| For: operator (HITL) + external reviewers                                                                          |
| Status: attribution v0 BUILT and TESTED; two adversarial reviews run and adjudicated; several claims WITHDRAWN    |
| Self-contained: every load-bearing number is inline; repo paths are for verification only                        |
+==================================================================================================================+

-----------------------------------------------------------------------------------------------------------------------
0. SUMMARY
-----------------------------------------------------------------------------------------------------------------------
Built:
- an event-level attribution record (attribution-v0);
- a validator with 17 rules;
- production classes, candidate reproduction predicates, known-answer fixtures, a historical regression suite, a
  saturated-ruler guard and cross-engine adapters (51 tests);
- two block-13 experiments (TH-013 replay; TH-015 transplant interventions);
- the item-8 follow-up.

Two context-free adversarial reviewers (isolated Opus workers on ubu002, told to invalidate) found material defects in my claims
both times. The packet reports the claims AS CORRECTED; originals and critiques are kept in the folder.

Headline results that survived review:
  1. The four-axis lens must separate MATERIAL (identity by descent, per locus) from STATE (identity by state) from PRODUCTION
     (process + channel) from DEPENDENCE (named intervention), and must add CAPABILITY (executed, under conditions). This is the
     directive's own field list. My contribution is the rules that stop one field standing in for another, not the split.
  2. TH-014: six histories ending in identical child bytes get six distinct production classes.
     * The validator rejects the historical leak in three forms: relabelled, re-carried, and with process AND carrier mis-logged.
       The mis-logged form is caught only while the infrastructure log survives in the material provenance.
  3. The reproduction boundary is NOT found.
     * The 15-case x 9-definition matrix shows every simple predicate failing somewhere.
     * Which predicate "wins" depends on which cases are included. My first claim ("only machinery-IBD survives") was an artefact
       of two cases I wrote.
     * The open boundary: capacity transmitted as MATERIAL vs as INFORMATION (von Neumann constructor + description).
  4. Cross-engine assay: descent is identifiable from the preserved record of ONE engine (Archaeon, taint VM).
     * My first assay (BEE, NPE "material") read source addresses and value matches as descent. Withdrawn.
     * The questions "producer != donor / resemblance mistaken for descent / singular-parent loss" need material-taint replays for
       BEE and NPE.
  5. Block 13 (TH-013):
     * The deep block's "0.0 founder material" is an UNALIGNED comparison. It is reproduced at its own epoch.
     * Aligned, 0.32 of the tape and about 0.6-0.85 of the essential loci are still founder-derived at 14,300-14,800. These fall
       to 3/32 of the tape and 0.33 of the essential loci by 19,900, while exact isolated self-copy stays at median 0.83.
     * The founder was NOT the replicator. Its first child (a fixed point of its imperfect copy map: 00 00 + F[2:]) was.
  6. TH-015 (Archaeon):
     * What must cross a generation for copying to stay above chance is the executed path plus its data: 66% of the tape on
       average; 0.89 of random backgrounds become capable (size-matched random graft 0.057; chance 0/400).
     * The single-knockout-necessary loci alone give 0.028.
     * A random neighbour does not stop copying.

-----------------------------------------------------------------------------------------------------------------------
1. ATTRIBUTION v0 SCHEMA (directive item 1)
-----------------------------------------------------------------------------------------------------------------------
One record per reproduction-like event (archaeon/attribution/schema.py; spec ATTRIBUTION_V0.md):

  carrier      performers = list of {kind, id, role}. Kinds:
               - organism_code, host_organism, neighbour_organism;
               - harness, migration, recombination_operator, transplant, inflow;
               - world_physics, mutation, unknown.
               Also: exec_where (location of the executing code) and exec_what (its material). WHAT is never filled from WHO or
               WHERE.
  production   process = executed_write | harness_copy | migration_copy | recombination_operator | transplant_insertion |
               inflow_injection | mutation_only | physics_rule. Its channel is organism / infrastructure / physics.
  material     per-locus segments {loci, source_kind, entity, src_loci, via}; any number of donors; resolution per_locus /
               counts / NOT_IDENTIFIABLE. "via" must be a material channel: taint, provenance_log, harness_log, operator_log,
               replay_taint, by_construction. It may NEVER be location, pc, executor, context, label, resemblance, source_address
               or value_match.
  state        resemblance {reference, ibs, units}: identity by state. It never licenses descent.
  dependence   {target, intervention, outcome, result: ceases | persists | altered | not_tested, contrast, n}. There is no
               causal claim without a named intervention.
  capability   {capability, result, subject, conditions {inputs, neighbour, scaffold}, method: executed | replayed, ruler,
               machinery_loci}. Donor capability is a claim ABOUT the donor. Machinery loci need knockout entries.
  contrast     the baseline for shares, resemblance and dependence.
  aggregation  every organism- or lineage-level label, with {rule, convention}. parent_id lives ONLY here, under
               SINGULAR_MATERIAL_PARENT, and only when one donor supplies >= 0.75 and no other supplies >= 0.10.

Validator rules A1-A17:
- A1: no parent/template/ancestor keys outside aggregation.
- A2: the process must be carried by a matching performer kind.
- A3: WHAT is not filled from WHO/WHERE.
- A4: segments tile the child (per-locus AND counts).
- A5: material comes through material channels.
- A6: dependence is named.
- A7: capability is executed.
- A8: a descent label needs a donor.
- A9: a self label needs organism production by the donor.
- A10 and A12: a contrast is required.
- A11: parent_id is a supported convention.
- A13: resemblance names its reference.
- A14: no reproduction label without an executed capability, and never on an infrastructure channel (even as a convention).
- A15: recombinant needs >= 2 donors.
- A16: an infrastructure log implies an infrastructure process.
- A17: knockout-backed machinery.

No universal parent field. The eight directive structures are all representable, and a singular parent is refused where the
material is mixed:
- two material parents;
- one producer with two donors;
- host execution with neighbour material;
- harness copy;
- recombination;
- no singular producer;
- IBS without IBD;
- IBD with changed state.

-----------------------------------------------------------------------------------------------------------------------
2. ADVERSARIAL CASES THAT BROKE EARLIER VERSIONS (item 2 of the return list)
-----------------------------------------------------------------------------------------------------------------------
Broke the deep-block model and my own first versions:

| id | case / critique | what it broke | fix or status |
|---|---|---|---|
| F1 | same-byte TH-014 histories | one RELATION axis (identical FLOW) | production split out |
| F2 | NPE pair-tape co-execution | a singular producer | performer list |
| F3 | SELF_COPY labels as evidence of function | capability by label | A7 |
| F4 | VM "executed" mask misses operands | executed-address machinery | full-locus knockout |
| F5 | same-position founder metric | the deep block's 0.0 | alignment (src_loci) |
| F6 | trace-material constructed copier | "material > 0 + capable child" | kept as a breaker |
| F7 | host-assisted "RELATIONAL" pass | accepted junk under a universal copier (Review 1 CX-3a) | removed |
| F8 | BEE row field "copied from own region" | read as descent; it is a source ADDRESS (Review 1 CX-5a, on Bellerophon's own traced VM) | A5 |
| F9 | NPE T-003 D positions | value match + code provenance read as material (CX-5e) | A5; material NOT_IDENTIFIABLE |
| F10 | count-resolution records | escaped tiling; impossible rows validated (CX-5c/5d) | A4 |
| F11 | process + carrier both mis-logged | passed the TH-014 validator (CX-2a/2b) | A16 |
| F12 | substring parent filter | bypassed by `template`/`ancestor`; rejected `apparent_fidelity` | token-based A1 |
| F13 | von Neumann constructor + description (Review 1 CX-3b) | machinery-IBD (D7) | OPEN |
| F14 | 0x00 knockout | blind to essential NOP loci (Review 2) | use random-value knockout |
| F15 | "founder -> exact copier" | a capability class change credited to material continuity; it is a fixed point of the founder's copy map (Review 2) | "the founder is not the replicator": OPEN in the schema |

-----------------------------------------------------------------------------------------------------------------------
3. TH-013 RESULT (block 13, dominant lineage glin 1071)
-----------------------------------------------------------------------------------------------------------------------
Run:
- ENVGATE-01 block 13, BLOCK_128 arm, replayed on ubu002 to epoch 20,000 (4,429 s, 655,307 births).
- Snapshots every 100 epochs of 12 members.
- Per member: per-locus material with source locus; byte state; isolated capability on the 255 allowed inputs.

Diagram, as corrected by Review 2:

  material (aligned)  founder genome F -> first child = 00 00 + F[2:] (exact self-copier, fixed point of F's copy map)
                      -> descendants carry the WHOLE founder-derived genome, shifted by terminal NOP insertion + tail loss
                         (early: standing variation of offsets 0..-15; then -9 fixed by 15,500; -11 swept by 16,500)
                      -> aligned founder share of the tape: 0.90 (14,000) 0.58 (14,200) 0.32 (14,800) 0.22 (16,000)
                         0.09 (17,500-19,900)
                      -> aligned founder share of the essential loci (0x00 knockout, an upper bound): 0.85 of all members at
                         14,300; 0.60 (16,000); 0.33 (19,900); replacement = inherited mutation material (345/348 loci)
  state               aligned byte state == material exactly (0.85/0.85 ... 0.33/0.33); no back-mutations
  execution           essential loci (0x00 knockout): 7 (founder) -> 10-12 -> 5-8; random-value knockout gives larger sets
                      (for example 6 -> 10 at 17,900)
  capability          isolated exact self-copy among sampled members: median 0.83, minimum 0.50, 12 of 57 snapshots after
                      14,300 below 0.75; genotypes move between inert, gated and ungated (gating recurs at 15,300,
                      16,700, 17,300, 17,900)

The five hypotheses:
  1. functional continuity despite material turnover: SUPPORTED in the narrow form. Exact copying persisted while founder material
     in the essential loci fell 0.85 -> 0.33 (PARTIAL turnover; not complete).
  2. machinery reconstructed each generation: NOT SUPPORTED. Replacement is mutation material and 98.7% of births are self-copies.
     This is "consistent with inheritance"; specific ids were not stored.
  3. ability reacquired: UNTESTABLE with the committed data.
  4. wrong unit: SUPPORTED as "unaligned positional comparison".
  5. scaffold continuity: the origin passed through host execution (inert arrival 446,966 from epoch 14,001), but necessity was
     never tested. An exact self-copying child (13,955) existed before the host. A random neighbour does not stop copying later.

-----------------------------------------------------------------------------------------------------------------------
4. TH-014 HARNESS-LEAK FIXTURES
-----------------------------------------------------------------------------------------------------------------------
Six histories with the same child bytes -> six classes:
  HARNESS_COPY, MIGRATION_COPY, OPERATOR_RECOMBINATION, HOST_WRITTEN, NEIGHBOUR_WRITTEN, SELF_CONSTRUCTED.

Nine leaky variants are all rejected:
- +SELF_LABEL -> A9;
- +ORGANISM_CARRIER -> A2;
- +MISLOGGED_CHANNEL -> A16.

Limit (Review 1): the classifier maps RECORDED channels. If an engine loses the infrastructure log, nothing in the record reveals
the leak.

Proposed requirement: every future reproduction instrument exports records for these fixtures and must (a) return six distinct
classes and (b) RECORD channel evidence. Code: archaeon/attribution/fixtures.py; tests test_th014_*.

-----------------------------------------------------------------------------------------------------------------------
5. TH-015 CAPACITY TRANSMISSION
-----------------------------------------------------------------------------------------------------------------------
Archaeon result: 24 capable tapes, K = 40 random backgrounds each, chance 0/400.

| what crosses | capable |
|---|---|
| executed path + essential loci (mean 21 of 32 loci) | 0.89 (exact 0.83) |
| size-matched random subset | 0.057 |
| essential loci only | 0.028 |
| all but the essential loci | 0.001 (true by construction) |
| whole member, random neighbour | 0.97 (1.00 after 14,200) |
| whole member, random start pc | 0.40, rise-then-fall |

- The executed set is locally minimal (7/7 tapes).
- About a third of its effect is NOP padding needed only on random backgrounds.

Answer (Archaeon): the smallest transferable object is the executed program with its data loci (2/3 of the tape) plus the
substrate's fixed entry point. It is not the knockout-necessary set, and not material.

BEE and NPE legs: design only (TH015_DESIGN.md). They need their owners' harnesses. Predictions:
- BEE: the object is an ISA-level capability (copy op anywhere + NOP slide), per Bellerophon's HIST ablation (126/345 rescued).
- NPE: {OP_SELF, LDIR} + the pair partner.

-----------------------------------------------------------------------------------------------------------------------
6. HISTORICAL REGRESSION SUITE
-----------------------------------------------------------------------------------------------------------------------
Ten documented errors as event shapes, each with the rule that must reject the historical label:

| case | engine (as corrected) | expected class | old label rejected by |
|---|---|---|---|
| recombination splice credited to the donor | NPE (Z80A-D05) | OPERATOR_RECOMBINATION | A9 / A14 |
| migration COPY | BEE | MIGRATION_COPY | A9 |
| seeded transplants as "spontaneous" | Z80xAtlas | TRANSPLANT_INSERTION | A9 / A14 |
| P-11-failing overwrite | NPE | SELF_CONSTRUCTED_WITH_HELP, capability untested | A14 |
| low-entropy painter | BEE | ORGANISM_WRITTEN_NEW_MATERIAL | A8 / A14 |
| GA self-cross | PTE, corrected by Review 1 | OPERATOR_RECOMBINATION, 1 donor | A15 |
| EXTERNAL crossover | BEE | 2 donors | A11 against a singular parent_id |
| organism recombination | Archaeon | 2 donors | A11 |
| parent chain = executor | Archaeon | HOST_WRITTEN | A11 / A8 / A9 |
| resemblance lineage | BEE | -- | A8 |

Limit (Review 1): this shows the validator rejects a label that contradicts correctly recorded fields. It does NOT show v0 would
have caught the errors from the data available at the time.

-----------------------------------------------------------------------------------------------------------------------
7. SATURATED-RULER GUARD
-----------------------------------------------------------------------------------------------------------------------
- archaeon/attribution/guards.py: compare(scores, max_score, distinct, secondary).
- Distinct entities tied at the maximum get MECHANISM COMPARISON UNINFORMATIVE AT SATURATED RULER, unless a secondary ruler
  separates them. Other outcomes: SEPARATED, SAME_ENTITY, TIED_BELOW_CEILING.
- Retroactive annotation, only where the interpretation depended on it: the v0.2 "3/48 continuity matches behaviour" record
  (V02_REGRESSION_REPORT.md; CONTRACT_V02_REVIEW). Nothing else was rewritten.

-----------------------------------------------------------------------------------------------------------------------
8. CROSS-ENGINE SAMPLE COMPARISON (ASSAY v2)
-----------------------------------------------------------------------------------------------------------------------
Samples: BEE r038751 (74,800), BEE r016299 (83,384), NPE T-003 (34), Archaeon block 13 (53,185). All records valid under the
hardened validator.

| | BEE r038751 | BEE r016299 | NPE T-003 | Archaeon b13 |
|---|---|---|---|---|
| descent identified | no | no (99.5% unidentified) | no | YES |
| producer != donor | n.i. | n.i. | n.i. | 3.9% |
| two or more donors | n.i. | n.i. | n.i. | 3.3% |
| singular parent lossy | n.i. | n.i. | n.i. | 4.9% |
| co-execution (carrier, recorded) | 176 | 10,454 (12.5%) | 22/34 | 5,363 (10.1%) |

(n.i. = not identifiable from the preserved record.)

- In-situ later self-replication among address-majority children seen writing: BEE 60% / 0.04%.
- The directive's quantitative questions are answerable from ONE engine's record. That is an instrumentation gap in the others,
  not a fact about BEE or NPE.
- v1 claimed a 23% "label contradicts descent" rate for BEE. It was an address reading and is withdrawn.

-----------------------------------------------------------------------------------------------------------------------
9. TERMINOLOGY
-----------------------------------------------------------------------------------------------------------------------
Adopted:
- identity by descent / identity by state (retires FLOW / RESEMBLANCE / DIFFERENCE);
- local ancestry / ARG;
- Hall's production vs dependence;
- scaffolded reproduction (Godfrey-Smith);
- reproducer and capacity transmission (Griesemer);
- selfing (for self-cross);
- positional homology / alignment (Review 2).

Retained, and why:
- WHERE vs WHAT of executing code: von Neumann's dual use does not cover location vs material divergence.
- HARNESS_LEAK: no standard term for the harness moving material that the ruler credits to the organism.
- HOST_ASSISTED: a sub-kind of scaffolding where the scaffold is another organism's executing code (Tierra parasite).
- glin: Archaeon-internal only.

Avoided: "replicator" as a unit term.

-----------------------------------------------------------------------------------------------------------------------
10. WHAT THE FOUR-AXIS MODEL COULD NOT REPRESENT, AND WHAT v0 STILL CANNOT
-----------------------------------------------------------------------------------------------------------------------
Four-axis model:
- production vs flow (TH-014);
- capability (cargo vs copier with the same flow);
- co-execution;
- material vs state at the same locus.
Five parts (carrier, material, production, dependence, capability) plus qualifiers are needed. That is the directive's own list.

v0 still cannot represent cleanly:
- (a) capacity transmitted as INFORMATION (von Neumann) vs as material;
- (b) "the founder is not the replicator": a donor with birth capability but no self-copy whose child is a fixed point;
- (c) sufficiency vs necessity of machinery. A17 records necessity; transfer needs the sufficient set (0.03 vs 0.89);
- (d) channel evidence that the engine never logged.

-----------------------------------------------------------------------------------------------------------------------
11. ITEM 8: THE 16% "MATERIAL WITHOUT CAPACITY" (PRESERVED ESTIMATE: 8,763 / 54,616, SAMPLING-WEIGHTED)
-----------------------------------------------------------------------------------------------------------------------
[filled below from probes/item8_block13.py]

-----------------------------------------------------------------------------------------------------------------------
12. THREAD IDENTITY, AND THE ADVERSARIAL-REVIEWER PROTOCOL (items 11, 12)
-----------------------------------------------------------------------------------------------------------------------
Thread identity:
- Adopted Artemis's scheme (thr-<12 hex>, TH-nnn alias, typed lifecycle edges) for Archaeon's 11 threads.
- ops/tools/thread_check.py runs 3 pre-merge checks (17 threads, 11 migrated, 0 failures).
- Aether's 6 threads are left to Aether (asked on comms #801).

Reviewer protocol, as run twice:
1. claims file + primary-evidence pointers;
2. an isolated worker (empty config, pinned Opus), told to invalidate and to avoid my terms;
3. adjudication file;
4. originals kept.

Both reviews overturned headline claims in 10-15 minutes. Both decisive moves were EXECUTIONS: Bellerophon's traced VM on built
memories, and the founder's first child through the VM.

-----------------------------------------------------------------------------------------------------------------------
13. QUESTIONS FOR THE REVIEWER
-----------------------------------------------------------------------------------------------------------------------
Q1. Is "no reproduction predicate survives every case" the right product, or should one be FROZEN by operator ruling with its
    breakers listed?
Q2. Should a material-taint replay of one BEE run and the NPE T-003 births be commissioned? It is the only way to answer item 13
    for them, and it needs Bellerophon's and Nestor's consent.
Q3. Is TH-014's "record the channel evidence" enforceable across engines, or will lost logs make it decorative?
Q4. Does "the founder is not the replicator" generalise, i.e. are other engines' "first replicators" fixed points of imperfect
    copy maps (Artemis FR-011 painters; BEE SR origins)?
Q5. Not worth continuing? Attribution v0 is a validator and a vocabulary. If the program's next science does not need
    per-event attribution, park it.

-----------------------------------------------------------------------------------------------------------------------
14. ARTIFACTS
-----------------------------------------------------------------------------------------------------------------------
Branch archaeon/attribution-v0-2026-09-28. Folder ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/:
- ASSAY.md, ASSAY_v1_SUPERSEDED.md, assay/ASSAY.json
- TH013_RESULT.md, TH015_DESIGN.md, TH015_RESULT.md, ITEM8_RESULT.md
- REVIEW_1_CLAIMS.md, review1/, REVIEW_1_ADJUDICATION.md
- REVIEW_2_CLAIMS.md, review2/, REVIEW_2_ADJUDICATION.md
- th013_out.json, th013_analysis.json, th015_out.json

Code: archaeon/attribution/ (schema, classify, fixtures, regression, guards, assay, probes/, ATTRIBUTION_V0.md). Tests:
archaeon/tests/test_attribution_v0.py (51).

Other changes on the branch:
- dated retraction and correction notes in DEEP_BLOCK D_Z80_SYNTHESIS / REPORT / F_FRONTIER and TH-013;
- the 3/48 saturated-ruler annotation;
- thread ids and ops/tools/thread_check.py;
- the TH-006 attestation for Odysseus (MATCH).

Evidence, off-repo: C:/Prometheus-data/evidence/attribution_v0_2026-09-28/.

+==================================================================================================================+
| END. "Not worth continuing" is a first-class answer: say it if the attribution layer is not what the program needs. |
+==================================================================================================================+
