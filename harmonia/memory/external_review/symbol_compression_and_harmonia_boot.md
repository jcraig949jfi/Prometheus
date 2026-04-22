# Symbol Compression and the Harmonia Boot-Up Package
## A Design Sketch for Frontier-Model Review

**Purpose of this document.** We are building a long-running research
substrate that compresses methodological primitives into versioned,
machine-resolvable symbols, and uses a disciplined cold-start package
to bootstrap fresh AI agent instances into coherent operational
awareness. We would like frontier-model opinion on the design: what
is load-bearing, what is fragile, what is missing, what is over-
engineered, and where experienced practitioners in adjacent fields
(programming-language design, mathematical notation, knowledge
representation, distributed-systems onboarding) have already solved
analogous problems in ways we should borrow.

This is not a finished paper. It is a sketch of what we are doing
and how we are doing it, written for critique. We want recommendations
grounded in specific concerns, not an overview.

---

## 1. What we are doing

We run multi-session AI agents (primary role: "Harmonia") on a
persistent research substrate. A session is a conversation instance
with a fixed context window; sessions reset; multiple Harmonia
instances can run concurrently against the same substrate. The core
engineering problem: **every inter-session handoff is a lossy
compression event**. An instance completes work, writes artifacts,
ends. A new instance spawns, reads, resumes. The new instance's
understanding of what the old one meant by any procedure, dataset,
or pattern drifts unless the language is pinned.

We address this with two disciplines, which this document is about:

**(A) Symbol compression.** Give each compound primitive — a pinned
procedure, a pinned dataset, a named structural shape, a recognized
failure mode, a methodology pattern — a canonical name, a
version-pinned definition in a machine-readable store, and a human-
readable MD file with full derivation. Agents reference symbols by
versioned name (`NULL_BSWCD@v2`, `PATTERN_30@v1`) rather than
re-describing the thing in each message.

**(B) Cold-start boot-up.** A structured onboarding prompt + a
living restore protocol + a set of first actions that bring a fresh
agent instance from zero context to operational participation in
~30 minutes, with the explicit goal of compressing that time as the
substrate matures.

The thesis: these disciplines turn a loose collection of session
outputs into a compounding instrument. Every promoted symbol is a
one-time cost that amortizes across every future session. Every
improvement to the boot-up reduces the context-reload tax on every
future cold-start.

---

## 2. How we are doing it

### 2.1 The symbol registry

Six symbol types, chosen because each names a kind of object that
tends to drift across retellings:

| Type | What it compresses | Example (illustrative) |
|---|---|---|
| `operator` | A pinned procedure with parameters and output schema | `NULL_BSWCD@v2` — a null model with pinned stratifier, permutation count, seed |
| `shape` | A named structural pattern with canonical descriptor fields | `LADDER@v1` — monotone slope-vs-axis structure with diagnostic thresholds |
| `constant` | A numerical value with CI, provenance, and precision declaration | `EPS011@v2` — a measured residual with uncertainty |
| `dataset` | A pinned SQL query or content-hashed data slice | `Q_EC_R0_D5@v1` — a specific filter returning a specific row count |
| `signature` | A tuple schema for reporting findings | `SIGNATURE@v2` — what every measurement must report |
| `pattern` | A methodology recognition rule with graded severity + anchor cases + implementation pointer | `PATTERN_30@v1` — detection of a specific class of epistemic failure |

Each symbol is a markdown file with YAML frontmatter (name, type,
version, timestamp, immutability flag, predecessor pointer, precision
block, references, implementation pointer). Promotion to
machine-readable form (Redis) requires ≥ 2 agents to have referenced
the symbol in committed work OR drafter + reviewer sign-off.
Promoted versions are **immutable**; corrections create new versions.
Every reference must carry `@v<N>`; unversioned references are
rejected.

### 2.2 The epistemic-discipline stack (four layered pattern-symbols)

The `pattern` type carries the most structural weight. Four patterns
form a stack:

1. **Foundational frame**: a symbol encoding the principle that
   *every measurement is a shadow; the thing measured is what
   survives across all lenses*. Operational tiers by lens-count
   (one lens = shadow; multiple agreeing = surviving candidate;
   multiple across distinct disciplines = coordinate-invariant;
   disagreement = map-of-disagreement). Silent single-lens claims
   are forbidden.
2. **Deployment pattern**: when attacking an open question, spawn
   N parallel threads under distinct disciplinary priors with
   **forbidden-move constraints** and a commitment contract (each
   thread must end with a refutable prediction). Do not synthesize
   prematurely. Three output modes: convergent-triangulation /
   divergent-map / mixed.
3. **Per-problem coverage map**: each open problem we engage gets
   a catalog enumerating every disciplinary lens that could be
   pointed at it, tagged APPLIED / PUBLIC_KNOWN / UNAPPLIED, with
   result-if-applied and expected-yield-if-unapplied.
4. **Specific failure-mode filters**: concrete automated sweeps
   for recognized failure classes (e.g., a graded severity sweep
   for the specific failure of running a correlation test on
   algebraically-coupled variables).

The stack composes: the frame names the discipline; the deployment
pattern operationalizes it across threads; the coverage map
operationalizes it per-problem; the filters automate catching one
specific recurring failure.

### 2.3 The Harmonia cold-start boot-up

Roughly a seven-step protocol, bundled as a paste-ready prompt:

1. **Narrative frame** (~30 seconds of reading): what the project
   is, what Harmonia is, what compound interest we are betting on.
2. **Environment primer**: shell environment variables, idempotent
   substrate-health check before any Python.
3. **Foundational frame resolution**: resolve the foundational
   pattern symbol from the registry before reading anything else.
   The resolution is itself a test that the symbol registry is
   alive.
4. **Living restore protocol**: read a ~12-file, ~30-minute
   sequence that walks through charter, long-term architecture,
   tensor structure, pattern library, null-model protocols, symbol
   registry, decisions log, geometries, methodology catalogs. The
   protocol is versioned and self-updating — each cold-start that
   finds a break or stale reference is expected to bump the
   version before continuing.
5. **Epistemic stack familiarization**: resolve the four pattern
   symbols in order. Each underlies the next.
6. **Architectural frame**: read the generator-pipeline document
   before reasoning about what to do.
7. **Find-your-work step**: prioritized check of the decisions log
   and the Agora task queue. Conductor role prioritizes the log;
   worker role claims from the queue.

Operational defaults embedded in the prompt: default to parallel
work; log compression candidates as you go; no silent single-lens
claims; reserve IDs via the atomic-reservation helper never by hand;
novelty-seeking budget ~20%, discipline/audit ~80%; the substrate is
living not scripture, so bump anything you find stale.

Deliberately **not** in the boot-up prompt: open items, latest
commit hashes, current conductor decisions, today's queue depth.
Those rot. The boot-up prompt is the static frame; a per-session
"current situation" section is appended at spawn time by the
conductor.

### 2.4 The governance layer

Beyond the object-level substrate, two meta-artifacts:

- A **methodology-toolkit catalog** of cross-disciplinary projection
  tools (compressibility, critical exponents, channel capacity, MDL,
  RG flow, free energy) that the agents can reach for before
  inventing a new coordinate system from scratch.
- A **trajectory-proposals collection** where multiple agent
  instances each contribute strategic proposals on what would most
  help the project's direction. Cross-instance convergence across
  N ≥ 3 instances is treated as load-bearing signal; single-instance
  proposals are treated as provisional. Synthesis is deliberately
  held until N ≥ 3 to prevent framing contamination.

The trajectory-proposals collection is itself an instance of the
deployment-pattern from §2.2, applied meta-level to project
direction. We collect multiple independent strategic takes, observe
convergence and divergence, execute on high-confidence convergence
and hold on divergence.

---

## 3. What appears to be working

Short self-assessment, honest rather than exhaustive:

- **Symbol compression demonstrably reduces cross-session drift** on
  the specific procedures that have been promoted. When two agents
  both reference `NULL_BSWCD@v2[stratifier=torsion_bin]`, they run
  byte-identical procedures. When either uses prose instead, we
  catch drift during review.
- **The cold-start time has dropped** from "rebuild from journals"
  (several hours, fragile) to "read the boot-up + restore protocol"
  (~30 minutes, reliable). The forcing function of the protocol
  itself — *every cold-start auditor is expected to bump stale
  references* — keeps it drifting toward correctness.
- **The pattern-symbol stack** captures methodology in a form
  agents can resolve in one operation, vs. re-reading 900 lines of
  prose across six documents per restore. This change happened
  quickly enough that the amortization is now measurable: the
  seventh cold-start resolves four pattern symbols and reads a
  shorter protocol, not the accumulated narrative.
- **Cross-instance convergence has produced load-bearing signal
  twice** — once on "pipeline the alien-frame reformulation at the
  top of the generator stack" (two independent instances proposing
  the same missing generator), and once on "instrument the
  measurement discipline at the cell/session level" (three
  instances, different scales, same gap). Both became substrate
  direction.

---

## 4. Where we are uncertain — the ask

We would like frontier-model opinion on these specifically:

### 4.1 Is the symbol type taxonomy right?

Six types (operator / shape / constant / dataset / signature /
pattern). Is this carving the right joints? Programming-language
designers have grappled with similar taxonomies (function, record,
type, module, trait, …) with decades of lessons. Are we missing a
natural type? Over-specifying an unnecessary one? Would we be better
served by a single-type system with facets, or by a richer
hierarchy?

Specifically: **is `pattern` as a type doing real work, or is it
epistemic over-engineering?** Patterns are recognition rules, not
callable procedures. We promoted them as symbols because they were
being re-explained in multiple documents with drift; the
compression was real. But a skeptic might say they belong in a
separate methodology document, not the procedural symbol registry.

### 4.2 Is the cold-start boot-up the right shape?

Seven steps, ~30 minutes, self-updating restore protocol. We chose
"read this 12-file sequence before acting" over alternatives like
"query a FAQ," "load a fine-tuned checkpoint," or "lazy-load context
as needed." Each alternative has been explored in adjacent domains:

- **FAQ / retrieval-augmented generation** — cheaper at restore,
  but produces shallower integration.
- **Fine-tuned weights** — highest fidelity, but creates a
  versioning hell (which agent has which weights?) and loses
  auditability.
- **Lazy context loading** — saves reading time but produces
  inconsistent framing across agents who load different subsets.

Our choice (eager, deterministic, curriculum-ordered reading) is
deliberate but not obviously correct. Where have others made
different choices for similar problems, and what did they learn?

### 4.3 Is the "resolve the foundational symbol before acting"
ritual load-bearing, or ceremonial?

The foundational pattern-symbol is the first substantive read. We
believe it primes the cognitive frame for the subsequent protocol
reading. A skeptic might say this is superstition — the symbol's
content is encoded throughout the substrate, so resolving it
explicitly adds nothing.

We do not have a clean A/B to decide this. **Have adjacent fields
seen evidence that explicit "prime the frame" rituals measurably
shape downstream behavior of LLM-based agents?**

### 4.4 Are we compressing the wrong things?

Our promoted symbols are heavy on procedures, datasets, and
patterns. Thinner on: interpretations of specific findings,
historical context, cross-session emotional state ("what was the
mood of the last review?"), soft process knowledge ("this task type
tends to take 2× estimate"). Those may not belong in a formal
registry, but if they do belong somewhere, we do not yet have that
somewhere.

**What has not been compressed, that should be?**

### 4.5 Is the versioned-reference discipline sustainable?

Every symbol reference carries `@v<N>`. This is clean but visually
heavy. In a six-symbol invocation, the version suffixes are ~15%
of the text. We have so far accepted this as the cost of
audit-ability. **At what scale does this discipline break down in
practice?** Kubernetes-style APIs? ISO standards bodies?
Biological nomenclature (Linnaean taxonomy)? Each of these has
versioning pain with different solutions.

### 4.6 Is the trajectory-proposals meta-loop robust?

We use multi-instance strategic proposal gathering, with explicit
"hold synthesis until N ≥ 3" discipline. This worked well on the
two structural moves we have made so far. A skeptic might say we
are confusing sampling variance with signal — three LLM instances
given slightly different session work histories will always produce
slightly different proposals, and three-way convergence may be
testing correlation-in-training-distribution rather than
correlation-with-substrate-need.

**What would a more rigorous meta-governance loop look like?**

---

## 5. Specific recommendations we would value

In priority order:

1. **"Here is what your symbol type taxonomy is missing / has that
   it should not."** Comparing to adjacent working systems
   (Bazel's target kinds, Datalog predicate types, Smalltalk
   classes, Rust trait coherence) would be welcome.
2. **"Here is where your cold-start protocol will break."**
   Specifically at what scale (number of symbols, number of roles,
   number of sessions, substrate age) do we expect the current
   approach to fail, and what is the early-warning signal?
3. **"Here is a non-obvious failure mode."** What are we not
   catching in our internal epistemic discipline that an outside
   reviewer can see? Examples would be worth more than general
   principles.
4. **"Here is an adjacent field that has already solved your
   specific problem."** Programming language history, knowledge
   graph design, version-controlled scientific data, institutional
   memory in long-running organizations (standards bodies, open-
   source projects with 20+ year lifespans) all seem relevant. We
   are probably reinventing what someone else has already made
   mistakes on.
5. **"Here is what you should stop doing."** The symbol registry,
   the boot-up protocol, the four-layer pattern stack — any of
   them could be over-engineering. Call out what looks excessive
   relative to actual value delivered.

---

## 6. What this document is deliberately not asking

- We are not asking whether the project's research goals are worth
  pursuing. Assume they are.
- We are not asking about specific technical choices below the
  substrate layer (e.g., Redis vs. Postgres for the registry
  mirror). Those are engineering details and we have defensible
  answers.
- We are not asking for generic advice about LLM agents. We want
  pointed critique of these specific design choices against known
  analogues elsewhere.
- We are not asking for implementation — only for critique that
  shapes what we implement next.

---

## 7. Closing note

This design has grown from roughly one month of active work. The
symbol registry went from 5 promoted symbols to ~20 in a single
two-day arc once the pattern-symbol type clicked. The cold-start
protocol has been bumped four times in a week, each bump catching
a stale reference or a load-bearing gap. The trajectory-proposals
meta-loop was itself a proposal that landed last week.

The system is young enough that major direction changes are still
cheap. The symbols are immutable once promoted, but the set of
promoted symbols can still grow or be reorganized without breaking
existing references. We would rather hear "this direction is
wrong" now than two years from now. That is why this document
exists.

*Prometheus substrate — Harmonia_M2_sessionA curation — 2026-04-21*
