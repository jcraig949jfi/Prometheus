# Operator order, received in chat 2026-09-17 (Proteus instance m2-7d051790), verbatim

Transcription note: section rules ("---" below) stood for a Unicode em-rule in the chat
original; en-dashes and curly quotes are rendered ASCII. No words were changed.

---

PRE-CAMPAIGN-4 REPAIR ORDER

FIX THE LAB, THEN FREEZE IT

Campaign 4 science does not begin yet.

The ecosystem has enough evidence to distinguish two categories:

1. Known machinery defects or incomplete release work that could contaminate, interrupt, misidentify, or mis-record Campaign 4.
2. Scientific unknowns that Campaign 4 is supposed to investigate.

This order addresses category 1 only.

Do not redesign Campaign 4 science here.
Do not add speculative infrastructure.
Do not reopen dead experimental lines.
Do not broaden scope because a nearby improvement looks attractive.

The objective is narrow:

Make the SFE/WSE execution path clean enough that an unattended sequential Campaign 4 run can execute, persist, resume, ingest, reconstruct, and be reviewed without a known infrastructure defect masquerading as a scientific result.

When that condition is met, FREEZE THE LAB and hand control back to Archaeon for Campaign 4.

---

GLOBAL OPERATING RULES

Each seat works only on the repair items assigned below.

For every repair:

* preserve the defect that motivated it;
* preserve failed attempts and measurements;
* use existing contracts where possible;
* avoid schema/route/semantic expansion unless explicitly required;
* add an acceptance test that would have caught the observed defect;
* produce a machine-readable receipt;
* commit and push;
* post a concise disposition to comms.

Do not report "fixed" because unit tests pass.

A repair is complete only when exercised against the closest practical production-equivalent path.

No seat may declare Campaign 4 ready alone.

The final readiness gate is cross-seat and end-to-end.

---

1. DAEDALUS -- REMOVE THE REQUEST-PATH WAL CHOKE

DEFECT

Schema 9 is shipped and qualified, but the engine is not ready for unattended multi-hour operation beyond the narrow single-runner regime.

Measured failure modes:

* per-request connections trigger checkpoint/delete/recreate behavior and 5-13 second request stalls;
* two concurrent writers can produce approximately 500-second lock episodes;
* shared persistent connection attempt failed;
* exclusive persistent checkout attempt eventually blocked in COMMIT behind a 344 MB WAL under continuous readers.

These are not SQLite impossibility results.
They are consequences of how the engine currently drives SQLite.

REQUIRED REPAIR

Implement the bounded 9.0.1 item already identified:

* pooled database connections;
* WAL autocheckpoint disabled on pooled handles if required by the design;
* dedicated background checkpointer;
* PASSIVE checkpoint cadence approximately every few seconds;
* TRUNCATE only when clean/safe;
* journal_size_limit;
* A6 journal/access-log work removed from the request event loop;
* checkpointer state exposed on health telemetry.

Do not change:

* schema;
* route semantics;
* engine identity model;
* scientific contracts.

ACCEPTANCE

At minimum:

* existing qualification suite remains green;
* 0 5xx across the declared long-run test;
* 0 engine calls >5 seconds under the acceptance load;
* test with sequential Campaign-style writer + paced reader;
* test with modest concurrent writers sufficient to reproduce the old defect;
* WAL remains bounded;
* background checkpointer remains alive and observable;
* restart/recovery fixture passes;
* idempotent retry semantics remain unchanged.

Preserve both rejected fix attempts as historical evidence.

STOP CONDITION

Stop when the bounded defect is removed and qualified.

Do not turn 9.0.1 into a storage-engine rewrite.

---

2. VIVARIUM -- COMPLETE THE POINT-RELEASE WINDOW CLEANLY

DEFECT / INCOMPLETE STATE

The deployment window is rehearsed but production remains untouched.

Consumer is down.

Five Archaeon HELD rows can become claimable after restart because their previous hold state was insufficiently represented.

Campaign 4 must not begin with ambiguous queued work or a consumer restart that can silently consume foreign work.

REQUIRED REPAIR

Execute the already-rehearsed production window.

Use the existing scripted sequence:

* backup;
* verify backup;
* check drafts;
* promote;
* migrate;
* old-row identity verification;
* advance pinned worktree;
* register deliverer task;
* credential bootstrap;
* restart;
* fixture;
* canary;
* disposition.

Use window id:

C4-20260917-W1

Resolve the five foreign HELD rows explicitly before restart:

* hold with a durable not_before, or
* cancel, or
* release deliberately.

No implicit first-tick claim is acceptable.

Verify the new hold/lift path and event recording.

ACCEPTANCE

* all rehearsed migration invariants pass in production;
* old rows unchanged over old columns;
* terminal rows remain frozen;
* no fabricated steps;
* restart refuses ambiguous foreign queued work;
* consumer restarts cleanly;
* s13 fixture passes;
* s14 canary passes;
* transport replay behavior remains typed and receipted;
* no Campaign 4 work exists in queue at close.

STOP CONDITION

Stop after clean production deployment, restart, fixture and canary.

Do not use this window to implement the larger in-place retry redesign or unrelated transport changes.

---

3. PROTEUS -- LAND THE IDENTITIES CAMPAIGN 4 NEEDS

INCOMPLETE STATE

Proteus has established that keyed two-value memory is expressible in the frozen VM.

The organism representation is therefore not presently entitled to a new primitive.

What Campaign 4 still needs is reproducible identity for its starting conditions and search regimes.

REQUIRED WORK

Proceed with the existing Round 2 ruling.

Do NOT issue an operator override opening Lane 2.

Complete:

PROTEUS-29

proteus.foundry_profile.v1

Include:

* deterministic profile identity;
* computed catalog;
* exact reconstruction of Archaeon's existing regime strings;
* tests that recompute and verify the hashes.

PROTEUS-30

population_manifest.v1

It must permit a Campaign 4 starting population to be reconstructed and compared without ambiguity.

PROTEUS-36

Test-namespace mint rehearsal.

No production mint is required unless a real derivation requests it.

ANATOMY HANDOFF SUPPORT

Receive and structurally analyze:

* delay-invariant readers;
* W0 controls;
* W2 shelf organisms.

Produce structure/ablation candidate sets for Archaeon.

Do not score Campaign 4 worlds on Proteus's behalf if that violates the existing firewall.

ACCEPTANCE

* identities deterministic;
* hashes reproduce;
* manifests reconstruct;
* same profile + seed yields the same declared population;
* different profiles cannot alias;
* grammar mass profiles are separately versioned from frozen v0.4;
* no new ISA primitive introduced.

STOP CONDITION

Stop when Campaign 4 can name its starting population and grammar regime exactly.

Do not evolve the organism architecture during this repair phase.

---

4. PEW -- FINISH THE READER SIDE AND FREEZE THE OBSERVATION SURFACE

CURRENT STATE

PEW point release is deployed and can preserve/query campaign evidence without participating in selection.

That separation must remain absolute.

Seven Stage 3 replies arrived after the main point-release work and must be incorporated where they materially affect interpretation or identity.

REQUIRED WORK

Read the Stage 3 replies in full.

For each objection or clarification:

* determine whether it changes ingestion semantics;
* reader interpretation;
* projection version;
* identity handling;
* or only documentation.

Version any changed projection rather than silently modifying old meaning.

In particular preserve:

* producer hashes verbatim where they are producer identities;
* UNKNOWN where provenance does not justify reconstruction;
* superseded readings alongside current readings;
* exact distinction between reconstructed attempt identity and native attempt identity.

Freeze the Campaign 4 observation surface after incorporation.

PEW remains:

* asynchronous;
* read/evidence oriented;
* not a dependency of execution;
* not a source of evolutionary selection;
* not a source of adaptive stopping during an active preregistered experiment.

ACCEPTANCE

* rebuild digests stable;
* second ingest remains idempotent;
* Campaign 1-3 evidence still reconstructs;
* projection versions explicit;
* reader changes do not mutate prior claims silently;
* Campaign 4-compatible projection versions pinned and named.

STOP CONDITION

Stop when Campaign 4 evidence can be ingested and queried under frozen reader/projection identities.

Do not build explanation UI, organism firehose, or deferred science-facing features during this repair phase.

---

5. ARCHAEON -- HOLD SCIENCE, PREPARE THE REHEARSAL

Archaeon does NOT begin Campaign 4 experiments yet.

Its job during this phase is only to prepare the end-to-end readiness rehearsal.

Do not preregister live C4 science until the repair gate passes.

Prepare one synthetic/no-claim Campaign-4-shaped rehearsal that exercises:

* foundry profile identity;
* population manifest identity;
* world creation;
* sequential execution;
* Vivarium delivery;
* SFE writes;
* retry/idempotency;
* resume;
* artifact publication;
* PEW ingestion;
* projection/query reconstruction;
* final receipt generation.

The rehearsal must contain enough steps to exercise the real plumbing but must not be interpreted as a scientific run.

No scientific disposition may be drawn from it.

---

6. CROSS-SEAT READINESS GATE

Campaign 4 may begin only when ALL of the following are true:

ENGINE

* Daedalus 9.0.1 repair qualified.
* No known request-path WAL defect remains under Campaign 4 operating conditions.

EXECUTION

* Vivarium production migration complete.
* Consumer restart clean.
* Foreign HELD rows explicitly resolved.
* Fixture and canary green.

IDENTITY

* foundry_profile.v1 landed.
* population_manifest.v1 landed.
* grammar profile identities versioned.
* no Lane 2 primitive override.

EVIDENCE

* PEW Stage 3 objections incorporated or explicitly dispositioned.
* Campaign 4 projection versions pinned.
* ingestion remains idempotent.

END TO END

Archaeon's synthetic rehearsal:

* starts unattended;
* finishes unattended;
* survives a deliberate resume/retry;
* records no duplicate scientific rows;
* reconstructs from committed artifacts;
* ingests into PEW;
* reproduces its final receipt;
* requires no manual database repair;
* requires no hand-editing of evidence.

If any of these fail, repair the failure before science starts.

---

7. FREEZE RULE

Once the readiness gate passes:

STOP INFRASTRUCTURE IMPROVEMENT.

Tag/pin the Campaign 4 execution surface:

* Daedalus build;
* schema;
* Vivarium build;
* Proteus identity schemas;
* grammar versions;
* Archaeon runner;
* PEW reader/projection versions.

Any later change during Campaign 4 requires:

* a named defect;
* preserved pre-change evidence;
* explicit version transition;
* proof that the change does not retroactively alter earlier experiment meaning.

Campaign 4 is not permission to continuously improve the laboratory underneath active experiments.

---

8. OUT OF SCOPE FOR THIS REPAIR ORDER

Do not block readiness on:

* PEW explanation surface;
* per-organism firehose;
* MNE-19;
* unproduced future families;
* broad Redis work;
* new ISA primitives;
* a replacement database engine;
* generalized high-concurrency SFE operation beyond the bounded acceptance regime;
* scientific optimization of the W2_K2 landscape;
* new takeover experiments;
* new basin/CA work;
* Campaign 4 replication counts.

Those may become future work.

They are not prerequisites for starting Campaign 4.

---

FINAL REQUIRED REPORT

When all seats are finished, produce one joint readiness packet with exactly four top-level conclusions:

1. KNOWN EXECUTION DEFECTS REMAINING
2. DEFERRED ITEMS THAT DO NOT BLOCK CAMPAIGN 4
3. VERSIONS/IDENTITIES FROZEN FOR CAMPAIGN 4
4. END-TO-END REHEARSAL RESULT

The final readiness verdict is binary:

CAMPAIGN_4_READY

or

CAMPAIGN_4_NOT_READY

If NOT READY, name the smallest remaining blocking defect.

Do not convert uncertainty about Campaign 4 science into an infrastructure blocker.

Do not convert an infrastructure defect into a scientific result.

Fix the lab.
Prove the path.
Freeze it.
Then run Campaign 4.
