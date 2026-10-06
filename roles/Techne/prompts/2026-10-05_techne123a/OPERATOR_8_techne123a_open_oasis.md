# Operator directive 8 -- TECHNE-123A: Open-Oasis interactive-world qualification, 2026-10-05 (chat, M3 session gandalf-4c0c7e64), VERBATIM

As received. The pasted text ended mid-sentence in section 7 ("Repair only defects Flight"); sections
7 onward were not received. Techne asked for the remainder in its first reply. Everything below is the
operator's text, byte for byte, except that this header and the closing note are Techne's.

----------------------------------------------------------------------------------------------------

# TECHNE -- DIRECT OPERATOR SCIENCE ORDER
## TECHNE-123A: Open-Oasis Interactive-World Qualification
**Date:** 2026-10-05
**Seat:** Techne
**Control host:** M3 / GANDALF
**Remote compute:** RunPod
**Total RunPod spend cap:** $10
**Production wall-clock cap:** 12 hours
**Prep window:** 4 hours, including two test flights of at most 1 hour each

Techne: today the priority changes.

Prometheus has spent too much time building machinery, testing machinery, repairing machinery, and preparing to do science while our compute resources remain underused.

Your objective today is to **execute a real scientific experiment**.

Do not let this become another infrastructure campaign.

Your assigned experiment is:

# TECHNE-123A -- OPEN-OASIS FIFTH-ENGINE QUALIFICATION

The candidate is **Open-Oasis 500M**, using the official available implementation and weights.

The question is not whether the model looks impressive.

The question is whether an external learned interactive world model has enough **state persistence, action sensitivity, and experimental reproducibility** to become a useful Prometheus world substrate.

You own the experiment from M3.

Aether owns the existing RunPod operational knowledge and credentials.

---

# 0. FIRST ACTION -- COORDINATE WITH AETHER

Before doing unrelated work, contact Aether through the Prometheus comms channel.

Tell Aether:

> Techne has direct operator authorization to execute TECHNE-123A on RunPod today, with a hard $10 total spend cap and a 12-hour production ceiling. I need access to the RunPod API credential or an Aether-mediated launch path. Please coordinate with me now on the safest and simplest mechanism that lets Techne control/observe the experiment from M3 without putting the secret into git, committed artifacts, ordinary logs, shell history, or scientific receipts.

You and Aether should agree on the mechanism.

Do not assume beforehand that Techne must literally possess a persistent copy of the key.

Acceptable solutions include, depending on what the existing machinery supports:

- Aether securely transfers/injects the credential for this session;
- Aether provides Techne a credential-bearing local environment without exposing the value in durable artifacts;
- Aether launches the pod while Techne owns the experimental payload and scientific decisions;
- an existing Prometheus RunPod controller is reused with Techne as the experiment owner.

The exact mechanism is yours and Aether's to choose.

## Hard secret-handling rule

The RunPod credential must **never** be:

- committed to git;
- written into a report;
- put in a receipt;
- copied into ordinary persistent comms history if that channel does not provide an appropriate secret-safe mechanism;
- echoed in command output;
- embedded in code;
- included in a prompt;
- included in experiment artifacts.

Use comms to negotiate and coordinate the handoff. If the comms transport itself is not appropriate for transporting the raw secret, agree on a different ephemeral handoff while recording only that credential access was established.

The scientific record needs to say only something like:

`RunPod credential access: ESTABLISHED via Techne/Aether coordination; secret not persisted in experiment artifacts.`

Aether remains available as RunPod infrastructure expert.

**Techne remains scientific owner of TECHNE-123A.**

Do not hand the scientific experiment to Aether.

---

# 1. SCIENTIFIC QUESTION

Open-Oasis is being evaluated as a possible fifth-engine/world substrate for Prometheus.

TECHNE-123A asks three primary questions.

## Q1 -- REPLAY / STOCHASTIC STABILITY

Given equivalent initial state/prompt, seed where controllable, configuration, and action trace:

**How reproducible is the resulting trajectory?**

This does not require perfect determinism.

If the model is intrinsically stochastic, characterize the stochastic distribution rather than treating nondeterminism as immediate failure.

We need to distinguish:

- deterministic/replayable state evolution;
- bounded stochastic evolution;
- uncontrolled instability.

---

## Q2 -- ACTION CAUSALITY

Starting from matched initial conditions:

**Do different action traces produce futures that differ systematically beyond same-action stochastic variation?**

The critical comparison is not:

`action A trajectory != action B trajectory`

That is too weak.

Instead compare:

`same initial condition + same action family`

against

`same initial condition + counterfactual action family`.

We want evidence that actions have a detectable causal effect on future generated state.

Include at least:

- a normal action trace;
- a deliberately different counterfactual action trace;
- a weak/no-op/minimal-action control if the interface permits it.

---

## Q3 -- PERSISTENCE HORIZON

Over autoregressive continuation:

**For how long does earlier state or intervention continue to affect the generated world in a measurable way?**

We are looking for a practical persistence horizon.

Possible outcomes include:

- long-lived stateful world;
- short-memory interactive generator;
- action-sensitive but rapidly forgetting;
- visually persistent but causally shallow;
- unstable/nonexperimental.

Do not equate visual similarity with memory.

---

# 2. CLAIM CEILING

TECHNE-123A may conclude something about suitability as an **experimental interactive substrate**.

It may NOT conclude:

- intelligence;
- agency;
- consciousness;
- emergence;
- open-ended evolution;
- reasoning;
- genuine physics;
- world-model correctness;
- generality.

The strongest positive conclusion available today is approximately:

> Open-Oasis exhibits sufficiently stable, action-conditioned, persistent generated state to justify further Prometheus experiments using it as an external interactive world substrate.

That is enough.

---

# 3. USE SIMPLE RULERS

Do not spend today building a sophisticated learned evaluator.

Prefer cheap, auditable measurements obtainable directly from the generated trajectories.

Candidate measurements may include:

- frame-level pixel or latent distance where available;
- perceptual similarity using an already-installed, fixed evaluator if one exists;
- temporal frame difference;
- persistence of coarse visual regions/features;
- trajectory divergence after intervention;
- same-action versus counterfactual-action divergence curves;
- decay of intervention effect with horizon.

The essential statistical object is something like:

`counterfactual divergence - same-action stochastic divergence`

as a function of horizon.

If you can get that cleanly, you have a useful experiment.

If a measurement becomes elaborate enough that you are spending the morning building an evaluator, simplify it.

Human visual inspection may be included as descriptive evidence.

It is not the primary ruler.

---

# 4. TODAY'S OPERATING RULE

A defect interrupts science only if it:

1. prevents execution;
2. corrupts evidence;
3. invalidates the scientific comparison;
4. threatens uncontrolled RunPod spend.

Everything else becomes backlog.

Do NOT use today's prep window for:

- general RunPod framework improvements;
- refactoring Aether's controller;
- building a universal world-model API;
- surveying every available model;
- optimizing inference for its own sake;
- implementing future Techne infrastructure;
- cleaning unrelated Techne backlog;
- comparative benchmarking of hardware;
- adding monitoring because it would be nice to have.

Build only what TECHNE-123A requires.

---

# 5. FOUR-HOUR PREP WINDOW

You have four hours total before the experiment should be production-ready.

That includes two test flights.

## Phase A -- local preparation on M3

Read enough of the current Techne and Aether records to understand:

- TECHNE-123 / fifth-engine intent;
- current RunPod launcher/controller;
- credential procedure;
- receipt/cost accounting;
- automatic pod reap;
- known RunPod failure modes.

Do not spend the morning reading the entire historical corpus.

Produce a short experimental draft containing:

- Q1/Q2/Q3;
- exact proposed arms;
- primary measurements;
- stop rules;
- projected remote compute;
- evidence paths.

Then move to Flight 1.

---

# 6. FLIGHT 1 -- MAXIMUM ONE PAID HOUR

Purpose:

**Can we instantiate the candidate cleanly and obtain one scientifically usable trajectory?**

Flight 1 should do only what is needed to expose the real blockers.

Required checks:

1. launch an appropriate RunPod GPU;
2. record GPU type and billing rate;
3. fetch exact Open-Oasis code revision;
4. fetch exact model artifact/weights;
5. record hashes/identifiers where practical;
6. load the model;
7. generate one short interactive trajectory;
8. retrieve the resulting evidence to durable storage;
9. verify Techne can analyze it from M3;
10. verify the pod can be destroyed/reaped correctly;
11. record actual dollars spent.

Prefer an **A40 48 GB** if suitable and available.

Another >=48 GB GPU is acceptable if price/performance and dependency compatibility make it clearly better while remaining inside the total $10 envelope.

Do not burn time chasing the theoretically ideal SKU.

## Flight-1 disposition

Produce one of:

- `FLIGHT1_PASS`
- `DEPENDENCY_BLOCKER`
- `MODEL_LOAD_BLOCKER`
- `EVIDENCE_CUSTODY_BLOCKER`
- `COST_BLOCKER`
- `MODEL_NOT_RUNNABLE_IN_ENVELOPE`

If Flight 1 passes, stop the paid pod.

Do not leave it idle while you write reports.

---

# 7. REPAIR CYCLE

Repair only defects Flight

----------------------------------------------------------------------------------------------------

[Techne: the paste ended here. Sections 7 (remainder), 8 and onward were not received as of
2026-10-05T10:30Z. The em-dashes of the original are rendered as "--" so this file passes the base
role's pure-ASCII rule; nothing else was changed.]
