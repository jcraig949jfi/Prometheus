AETHER — RUNPOD ENGINEERING LADDER

Aether now has two responsibilities:

1. continue its scientific work when appropriate;
2. turn everything learned from RunPod into a reusable Prometheus GPU experimentation system.

For this round, prioritize the second responsibility.

The primitive Aether science remains useful as a workload and source of realistic stress, but do not optimize this campaign around obtaining an interesting scientific result.

The objective is:

Make GPU experiments increasingly routine, observable, recoverable, scalable, economical, and portable across Prometheus seats.

We may be days, weeks, or months away from experiments where GPU operational failure would destroy genuinely valuable scientific time.

Use the barren period to build the flight system now.

⸻

NORTH STAR

A Prometheus seat should eventually be able to provide something approximately as small as:

* a module directory;
* an entrypoint;
* dependency declaration;
* GPU requirements;
* expected outputs;
* timeout/resource limits;

and receive:

* deterministic packaging;
* immutable identity;
* dry-run validation;
* cost projection;
* safe RunPod launch;
* environment/bootstrap setup;
* continuous telemetry;
* logs and artifacts;
* retries/reconciliation;
* cleanup;
* cost accounting;
* reproducible receipts;

without building or publishing a custom Docker image.

Use stock RunPod images plus runtime-deployed, checksummed module bundles unless an experiment genuinely requires a custom image.

Do not require every seat to rediscover the RunPod API, environment quirks, credential handling, artifact transport, cleanup semantics, or cost model.

Aether should absorb that complexity.

⸻

ENGINEERING PRINCIPLE

Each iteration must throw slightly more at RunPod than the previous one.

Each rung should add at least one new capability or failure mode.

Do not merely rerun the same successful experiment at increasing size.

We want a progression such as:

dry run → single small GPU → larger GPU workload → long workload → concurrent pods → reusable foreign-seat module

Every rung must leave reusable machinery behind.

⸻

BUDGET

Hard ceiling for this engineering campaign:

$5 total incremental RunPod spend.

Do not spend merely to consume the budget.

The expected useful spend should be substantially below the ceiling.

Advance rung by rung. If a rung exposes a reliability defect, repair and requalify it before increasing scale.

Record projected and measured cost separately.

Never claim provider billing reconciliation unless actual provider billing data was obtained.

⸻

ITERATION 0 — ZERO-DOLLAR DRY-RUN SYSTEM

Before launching another Pod, build a first-class dry-run path.

A dry run must perform everything possible except the Pod-creating request.

It should:

* validate the module specification;
* enumerate bundle contents;
* compute hashes;
* verify dependency declarations;
* construct the exact sanitized RunPod request;
* verify GPU SKU assumptions if discoverable read-only;
* inspect current active Pod inventory;
* calculate expected hourly cost;
* calculate expected experiment cost from workload estimates;
* validate artifact destinations;
* validate run IDs and ownership metadata;
* validate cleanup configuration;
* validate telemetry configuration;
* validate timeout/guardrails;
* validate secrets policy;
* validate bootstrap commands;
* verify that required source artifacts are actually retrievable;
* emit the complete run manifest and receipt skeleton.

The output should answer:

If we pressed GO right now, exactly what would happen?

No POST/create call may occur in dry-run mode.

Add tests proving dry run cannot create a Pod.

⸻

GENERIC MODULE CONTRACT

Define a small reusable contract for a GPU workload.

Prefer something like:

module_spec.json / module_spec.yaml

containing concepts such as:

* module name;
* module version;
* source identity;
* entrypoint;
* arguments;
* dependency specification;
* requested GPU class/capability;
* disk requirement;
* expected maximum runtime;
* artifact paths;
* telemetry hints;
* health/canary command;
* environment allowlist;
* optional application metrics;
* deterministic seed/run metadata.

Do not overdesign this.

The contract should be understandable by another seat in minutes.

A module should not need to know RunPod API details.

⸻

PACKAGE WITHOUT CUSTOM CONTAINERS

Build a generic bundler.

Input:

module directory + module spec

Output:

* deterministic archive;
* canonical manifest;
* per-file SHA256;
* bundle SHA256;
* source/git identity where available;
* dependency identity;
* bootstrap script;
* receipt template.

Support at least one path that does NOT require publishing a custom container.

Preferred architecture:

stock RunPod image → bootstrap → retrieve immutable bundle → verify hashes → install declared dependencies → scrub credentials → execute module

The transport mechanism can use the existing proven controller/artifact-serving machinery, a pinned repository artifact where appropriate, or another simple transport abstraction.

Transport must not alter module identity.

Document which bytes actually ran.

⸻

SECRETS BOUNDARY

Generalize the lesson already learned.

RunPod/API credentials belong to the controller.

Experiment code should receive only explicitly allowed environment variables.

Immediately before invoking user/module code:

* remove provider API credentials;
* construct an environment from an allowlist;
* verify forbidden credential names are absent.

Add an automated test that deliberately injects fake provider credentials and proves module code cannot read them.

Never print real credentials.

Never place credentials in argv, committed artifacts, logs, manifests, or receipts.

⸻

ITERATION 1 — TINY REAL POD

Use a cheap, short GPU run.

Purpose:

* validate package transport;
* bootstrap;
* dependency installation;
* module startup;
* telemetry;
* artifact retrieval;
* cleanup;
* cost calculation.

The workload itself should be trivial.

Measure the full timing decomposition:

* create request → Pod accepted;
* accepted → machine available;
* machine available → bootstrap start;
* bootstrap duration;
* dependency installation duration;
* workload duration;
* artifact upload/retrieval duration;
* termination duration.

This gives us the non-compute overhead model.

Produce:

cost = startup + bootstrap + compute + teardown

rather than treating hourly GPU price as the whole economics.

⸻

ITERATION 2 — SCALE UP

Run a workload large enough to exercise real GPU memory and throughput.

Aether may be the reference workload because it is already qualified.

Measure continuously:

* GPU memory used;
* GPU memory reserved/pool if available;
* GPU utilization;
* GPU temperature;
* GPU power if exposed;
* CPU utilization;
* host RAM;
* disk usage;
* artifact volume;
* application throughput;
* tick/step latency;
* warnings/errors;
* telemetry sampling overhead.

Every telemetry record must contain both:

* UTC timestamp;
* monotonic elapsed time.

Test adaptive sampling if high-frequency telemetry meaningfully perturbs throughput.

Quantify observer overhead.

⸻

ITERATION 3 — LONGER RUN AND FAILURE INJECTION

Run long enough to exercise lifecycle behavior.

During controlled dry runs/local simulation where possible, and on a cheap real Pod where necessary, test failure cases including:

* module exits nonzero;
* bootstrap dependency failure;
* hash mismatch;
* artifact server unavailable;
* artifact exceeds expected size;
* log flooding;
* controller interrupted;
* timeout reached;
* RunPod request returns ambiguous failure;
* inventory temporarily fails;
* Pod disappears unexpectedly;
* cleanup request fails transiently;
* telemetry stream is interrupted.

Do not deliberately strand paid resources.

For any uncertain Pod-creation outcome:

reconcile inventory before retrying creation.

No blind create retry.

Test that rule.

⸻

CLEANUP / OWNERSHIP

Carry forward Aether's cleanup work rather than rebuilding a weaker version.

Every created Pod must have an exact run identity and ownership record.

Maintain controller-known Pod IDs independently of list discovery.

Cleanup must handle:

* normal termination;
* experiment failure;
* controller failure;
* partial API failure;
* restart/resume.

No experiment can report CLEAN solely because a LIST omitted the Pod.

Final receipts must distinguish:

* termination request acknowledged;
* Pod observed absent;
* operational cleanup established;
* billing reconciliation established.

Those are different claims.

⸻

ITERATION 4 — SCALE OUT

After single-Pod reliability is demonstrated, run a small concurrent experiment.

Target:

2–3 Pods concurrently, within the total budget.

Use independent shards such as:

* different seeds;
* parameter slices;
* replay cases;
* benchmark sizes.

Requirements:

* unique run ID;
* unique shard ID;
* no artifact collisions;
* centralized controller ledger;
* per-Pod telemetry;
* aggregate status;
* independent cleanup tracking;
* partial-result preservation if one shard fails.

Test at least one situation where one shard fails or is deliberately given a harmless failing workload while the others complete.

The controller must not lose successful results merely because one shard fails.

This is the beginning of Prometheus GPU fan-out.

⸻

ITERATION 5 — FOREIGN-SEAT ASSAY

This is the most important reusability test.

Choose one small GPU-capable module from another Prometheus seat, preferably one not written around Aether's RunPod assumptions.

Do NOT rewrite that seat's science into Aether.

Package it through the generic module contract.

Goal:

prove another seat can use the RunPod flight system without understanding Aether's deployment internals.

Measure:

* how many seat-specific changes were required;
* which assumptions leaked through the abstraction;
* packaging effort;
* dependency problems;
* telemetry compatibility;
* artifact handling;
* cost.

If the foreign module requires extensive modification, treat that as a platform failure and improve the contract.

⸻

REUSABLE TELEMETRY SCHEMA

Create a generic telemetry envelope.

Separate:

PLATFORM

* Pod identity;
* GPU model;
* GPU memory;
* utilization;
* temperature/power where available;
* CPU/RAM/disk;
* wall time;
* estimated spend.

WORKLOAD

Module-defined metrics such as:

* tick;
* throughput;
* loss;
* candidates;
* events;
* queue depth;
* lattice activity.

ARTIFACT

* bytes written;
* upload/retrieval status;
* checksums;
* truncation;
* retention.

Do not force every scientific module into Aether's vocabulary.

Provide a small API/callback or JSON-lines interface for arbitrary workload metrics.

⸻

ECONOMICS

Build a durable cost model.

Track at least:

* $/pod-minute;
* startup overhead;
* bootstrap overhead;
* dependency-install overhead;
* compute utilization;
* $/experiment;
* $/successful experiment;
* $/unit of useful work when the workload defines one.

For Aether that may be:

$/1e9 site-ticks

For another seat it may be:

$/candidate

$/evaluation

$/simulation-step

or something else.

The platform should support workload-defined denominators.

Also record when cheap GPUs are operationally superior despite lower performance.

Do not optimize solely for $/hour.

⸻

ARTIFACT DISCIPLINE

Every real run should produce a self-contained evidence directory with:

* run manifest;
* module manifest;
* hashes;
* sanitized Pod request;
* environment/software versions;
* GPU identity;
* telemetry;
* stdout/stderr;
* workload results;
* cost calculation;
* cleanup receipt;
* artifact manifest;
* final disposition.

The evidence must be committed or durably stored according to repository policy.

Detect ignored evidence files before declaring a run complete.

Do not use git add -f as the normal solution.

⸻

RUN RECEIPTS

Create one machine-readable canonical receipt schema reusable by all seats.

Include:

* run ID;
* seat;
* module;
* git/source identity;
* bundle identity;
* RunPod Pod IDs;
* GPU;
* image;
* package/dependency identity;
* start/end;
* result;
* telemetry summary;
* artifacts;
* estimated spend;
* provider-reconciled spend if available;
* cleanup state.

Make receipts aggregatable so Atlas can eventually ingest them.

⸻

OPERATOR EXPERIENCE

The final system should converge toward commands conceptually like:

prometheus-gpu dry-run module_spec.yaml

prometheus-gpu run module_spec.yaml

prometheus-gpu status <run-id>

prometheus-gpu fetch <run-id>

prometheus-gpu cleanup <run-id>

prometheus-gpu estimate module_spec.yaml

Names are not frozen; functionality is what matters.

The operator should not manually construct RunPod JSON for ordinary experiments.

⸻

DOCUMENTATION FOR OTHER SEATS

Create a concise guide:

Aether/runpod/PROMETHEUS_GPU_RUNPOD_GUIDE.md

It should explain:

1. what the platform does;
2. how to package a module;
3. the minimal module specification;
4. how dependencies are installed;
5. how to request a GPU;
6. dry run;
7. cost estimate;
8. launch;
9. telemetry;
10. artifact retrieval;
11. cleanup;
12. failure/recovery;
13. how to add module-defined metrics;
14. how to reproduce a historical run.

Include a minimal working example that another seat can copy.

Also create:

Aether/runpod/MODULE_CONTRACT.md

Aether/runpod/TELEMETRY_SCHEMA.md

Aether/runpod/RUN_RECEIPT_SCHEMA.md

Aether/runpod/FAILURE_PLAYBOOK.md

Aether/runpod/COST_MODEL.md

Do not produce documentation disconnected from executable tooling.

Every important documented workflow should have a corresponding command/test.

⸻

DRY-RUN / CHAOS LIBRARY

Build reusable simulations/fakes so reliability work does not require money.

At minimum simulate:

* success;
* 400;
* 401/403;
* 429;
* 500;
* timeout before response;
* create accepted but response lost;
* LIST omission;
* GET disagreement;
* DELETE transient failure;
* stale telemetry;
* artifact corruption;
* checksum mismatch.

These should exercise the real controller logic, not a separate toy implementation.

The expensive cloud run should be the final confirmation, not where basic bugs are discovered.

⸻

SCIENCE DURING THIS CAMPAIGN

Aether's native-circuitry experiment may continue when useful as a representative workload.

However:

* do not modify scientific interpretation to improve platform testing;
* do not add steering merely to create a more interesting benchmark;
* do not turn platform failures into science;
* do not claim scientific progress from infrastructure scaling.

If an interesting scientific result appears incidentally, preserve it and report it separately.

The platform campaign's primary disposition concerns engineering.

⸻

SUCCESS CRITERIA

This round is successful when we have demonstrated all of the following:

1. zero-dollar dry run;
2. deterministic module packaging;
3. stock-image deployment without custom container publication;
4. one small real GPU run;
5. one substantial GPU workload;
6. long-run telemetry;
7. failure/recovery tests;
8. safe cleanup after ambiguous states;
9. 2–3 Pod fan-out;
10. another Prometheus seat's module successfully deployed through the same machinery;
11. cost curves and receipts;
12. documentation a fresh seat can actually follow.

The strongest final test is:

Can a fresh seat package and launch a GPU experiment correctly without reading Aether's implementation?

If not, iterate.

⸻

ITERATION DISCIPLINE

For each rung:

BEFORE

* preregister the operational question;
* define falsifier;
* estimate cost;
* dry run;
* verify active Pod inventory.

DURING

* telemetry live;
* cost accumulation visible;
* ownership durable;
* no blind retries.

AFTER

* retrieve artifacts;
* validate hashes;
* terminate;
* independently verify zero active Pods;
* reconcile cost as far as the provider interface permits;
* run tests;
* record defects;
* commit accepted improvements;
* write the next rung based on what was actually learned.

Every rung should leave the system more reusable than it found it.

⸻

FINAL REPORT

Create:

Aether/RUNPOD_ENGINEERING_01_2026-09-24.md

Structure it as:

CAPABILITIES ADDED

REAL RUNS

FAILURE TESTS

SCALE-UP RESULTS

SCALE-OUT RESULTS

COST MODEL

TELEMETRY

FOREIGN-SEAT ASSAY

DEFECTS FOUND AND REPAIRED

REMAINING SINGLE POINTS OF FAILURE

GUIDE FOR OTHER SEATS

NEXT SCALING BOUNDARY

Report actual spend.

Do not stop merely because one successful RunPod run works.

Iterate until the useful rungs above are completed, the $5 ceiling is reached, or a real reliability blocker requires operator attention.

Then stop.
