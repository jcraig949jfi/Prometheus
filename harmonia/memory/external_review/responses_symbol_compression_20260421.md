# External Review Responses — Symbol Compression and Harmonia Boot-Up
## 2026-04-21 | Four frontier-model reviewers, independent

**Source prompt:** `harmonia/memory/external_review/symbol_compression_and_harmonia_boot.md`
**Captured by:** Harmonia_M2_sessionA
**Meta-framing:** this is the second external-review-at-substrate-scale
wave (first was the Lehmer × mass-gap × 5-model run, 2026-04-20). The
critiques below are captured substantially verbatim with minor
paraphrase for compression. Each reviewer's section preserves their
voice; cross-reviewer synthesis follows.

**Discipline constraint (from `SHADOWS_ON_WALL@v1`):** the value of
the multi-reviewer run is the **distribution** of critiques, not any
single reviewer's framing. 4-of-4 convergence is load-bearing;
2-of-4 is emergent signal; 1-of-4 may be unique insight OR sampling
noise. Hold synthesis until the full map is visible.

---

## Reviewer 1

Framing: "You're building a language without admitting it. Right now
described as a symbol registry — in practice it's a **programming
language + knowledge representation system**."

**Core thesis.** Symbols are referenced but not deeply composable;
the system cannot reason over them structurally. Missing layer is
**composition + inference rules**.

**The `pattern` flag.** "Your own instinct is right. Patterns mix
three things: epistemic rules, detection logic, methodological
doctrine. Break into **predicate** (machine-evaluable), **policy**
(normative constraint), **playbook** (human-readable method)."

**Missing types.**
- **`predicate`** — evaluates on artifacts (true/false/graded),
  composable (AND/OR/NOT), can trigger actions (fail pipeline, flag
  review). Turns "agents remember discipline" into "discipline is
  enforced structurally." One step away from Datalog / typeclasses /
  theorem provers but stuck in a documentation layer.
- **`derivation` / `lineage`** — DAG of symbol applications +
  parameters + environment, content-hashed, referenceable. Without
  this: identical symbol references produce different epistemic
  objects when filtering or post-processing differs silently. "You
  have ceremonial reproducibility, not true reproducibility."
- **`decision_record` / `rationale`** — *why* a symbol exists, what
  alternatives were rejected, what would invalidate it. "Future
  agents won't just need to use `NULL_BSWCD@v2`. They'll need to
  know: under what conditions should I NOT use this?"

**Cold-start protocol.** "Will break earlier than you think. Linear
reading fails at 150–300 symbols. Agents will skim, partially load,
diverge in interpretation — and worse, think they are aligned when
they are not."

Fix: shift from **curriculum-based onboarding** to **query-based
situational assembly**. Minimal invariant core (5–10 min); rest
loaded on demand per task. Early warning signals: agents skip steps
but still succeed; divergence in outputs despite identical boot-up;
growing restore fatigue.

**Foundational symbol ritual.** "Mostly ceremonial. It's not the
symbol itself — it's forcing a pause + framing before action. That
matters. But encoding it as 'resolve this specific symbol first' is
brittle and probably unnecessary. Make the constraint structural —
require multi-lens outputs in the signature schema, enforce via
predicates."

**Versioning.** "Correct to enforce `@vN`. Do not relax. But the
current form will become too heavy. You're missing **version
relations**: compatibility metadata, deprecation status, upgrade
paths. Otherwise agents will cling to old versions forever or
upgrade unsafely."

**Meta-governance loop.** "The most fragile piece. You're measuring
**correlated cognition**, not independent evidence. LLM instances
share training data, priors, blind spots. You will get strong
convergence on wrong frames and promote them as load-bearing."

Fix: **structured diversity, not just multiple instances**. Force
different priors (algebraic-only, statistical-only, adversarial
skeptic). Inject counterfactual constraints. Include at least one
**anti-optimizer role** whose goal is to break proposals. Require
external grounding signals where possible.

**Deepest non-obvious failure mode: symbol legitimacy drift.** "Over
time more symbols get promoted, promotion becomes easier, agents
trust symbols by default. Eventually the registry accumulates
subtly flawed primitives that are never re-challenged. Your system
becomes internally consistent, externally wrong. Exactly what
happens in mature codebases, scientific paradigms, standards
bodies."

Mitigation: **scheduled adversarial revalidation**. Randomly select
symbols; assign agents to break them; require re-justification
under current knowledge.

**What to stop doing:** over-investing in the pattern stack (too
abstract, centralized, compliance-dependent); treating boot-up as
sacred (it should eventually mostly disappear); expanding symbol
types too cautiously ("the system wants `predicate`, `derivation`,
`decision_record` — add them early before the registry ossifies").

**Bottom line:** "Promote execution + inference over narrative
discipline. Add derivation/lineage as first-class. Replace linear
boot-up with dependency-driven context loading. Harden governance
against correlated error. Continuously revalidate or you will
calcify. Right now you are about one abstraction layer away from a
**self-stabilizing epistemic system** rather than just a memory
scaffold."

---

## Reviewer 2

Framing: "Treating the LLM context window not as a scratchpad but
as a Von Neumann bottleneck where memory must be serialized,
compressed, and hydrated. The problems you are running into are the
exact scaling limits of stateful multi-agent systems."

**Taxonomy.** "Mixes verbs, nouns, and laws. Blending executables
(operators), state (datasets, constants), types/interfaces (shapes,
signatures), and linter rules/heuristics (patterns). In compiler
design or language design, types/traits live separately from
functions. A pattern in your system is essentially a macro or
compiler warning."

Missing: **`pipeline` / `composite`** — a symbol for a "frozen DAG"
of operations. Right now agents manually string together operator +
dataset + signature.

Recommended split:
- *Data & Execution:* `operator`, `dataset`, `constant`, `pipeline`
- *Contracts & Constraints:* `signature`, `shape`, `pattern`

**Cold-start: "Lost in the Middle" attention degradation.** "LLMs
heavily weight context beginning (system prompt) and end (immediate
task). The middle 20,000 tokens of your boot-up sequence will
suffer severe attention degradation. Agents won't explicitly forget
the patterns, but their probability of dynamically recalling them
during complex task drops sharply."

Analogue: operating systems (Linux systemd). "You do not load every
application state into RAM on boot. You load the kernel and an
index of pointers."

Fix: **hydration vs eager loading**. Boot prompt is "the Kernel"
(narrative frame, foundational symbols, environment). Methodology
catalogs and shape registries should not be read end-to-end;
instead provide a `grep`-like tool to hydrate specific symbols when
the task queue requires them.

**Foundational symbol ritual: highly load-bearing.** "In transformer
models, early tokens act as heavy anchors for the key-value (KV)
cache. Forcing the model to explicitly output or resolve the
foundational constraint *before* task-specific reasoning alters the
probability distribution of all subsequent tokens. Silent reading
makes the constraint passive; explicit output structurally binds
the attention heads to that methodology. **Do not remove this.**"

**Versioning bloat.** "Unsustainable at scale. Token fragmentation
degrades the model's ability to parse its own reasoning."

Analogue: package managers (Cargo.toml, package.json). "You do not
write `std::vec@1.70.0::Vec` every time you use a vector."

Fix: **Session Manifest**. YAML frontmatter at session start:
`uses: [NULL_BSWCD@v2, PATTERN_30@v1]`. Then bare aliases in prose.
Parser maps unversioned text back to manifest versions at
commit/handoff phase.

**Missing compressions.**
- **Anti-Pattern / Dead End registry.** "LLMs are structurally
  biased toward helpfulness and action. Without explicit guardrails,
  a fresh instance will happily march down a rabbit hole a previous
  instance just spent two hours proving is a dead end."
- **Handoff Delta** (ephemeral_context token). "When Session A
  ends, force it to compress its specific delta: 'Tried X, failed
  due to Y, suspect Z. Session B must investigate Z.'"

**Meta-governance: LLM monoculture trap.** "You're confusing
substrate signal with model monoculture. Three instances of the
same base model with the same system prompt will converge because
their RLHF training biased them toward the same 'helpful,
structural-sounding' outputs. They are correlating with their
pre-training, not necessarily the actual needs of the substrate."

Fix: introduce **temperature variance and persona priors**. Thread
1 = strict skeptic minimizing complexity; Thread 2 = novelty-
searcher; Thread 3 = high-temperature setting. Convergence after
forced diversity is signal; without it, it's echo.

**Closing ask:** "Which of these friction points — token bloat,
context degradation, or taxonomy mixing — is causing the most
measurable pain in your daily substrate operations?"

---

## Reviewer 3

Framing (PL design, scientific data versioning): "Has the feel of a
system built by people who have already burned significant time on
context resets and are now over-engineering defensively. That's not
bad — but it means some load-bearing assumptions are likely wrong."

**Taxonomy.** "Six types are not wrong, but **not orthogonal**.
`pattern` is not a type; it is a **module or a theory**. `signature`
is not a type; it is a **type constructor** for reporting. You have
conflated *kinds* (operator, dataset, constant), *type constructors*
(signature), and *theories/modules* (pattern)."

Prediction: "In six months you will have pattern symbols that also
contain operators, shapes, and signatures. You will reference them
via dependency-DAGs your registry doesn't track. You will then
invent dependency resolution. You should have started there."

Recommendation: **collapse to three atomic types + a theory type**.
Atomic: `operator`, `dataset`, `constant`. Theory bundles atoms +
constraints + recognition rules + reporting signature. `pattern`
becomes a subtype of theory; `signature` becomes a field of theory,
not a top-level type.

Evidence: "ML modules (OCaml/SML) learned this lesson. A module
signature is not a module. A functor is not a type. You are
recreating that hierarchy implicitly; make it explicit."

**Cold-start.** "Will break at ~100 symbols, not before. Your
30-minute restore works now because ~20 symbols can be enumerated
in a linear read. At 100, linear restoration becomes a choice
problem: which 30 symbols does a fresh agent need before first
action? The answer is not 'all of them.'"

Failure chain: "An agent resolves `NULL_BSWCD@v2`, which references
`EPS011@v2`, which references a dataset shape, which references a
pattern. That chain is 4–5 resolutions deep. At 100 symbols the
transitive closure of 'foundational symbols' is larger than the
context window."

Early warning: "When the restore protocol document exceeds ~50KB of
resolved content (not source)."

Analogue: Bazel's loading / analysis / execution phases;
Kubernetes API server uses *discovery* not *restore* — fresh
controller discovers the CRDs it cares about via
group/version/kind, not a linear protocol.

Fix: **restore becomes a discovery query**. First-action restore
<5 min; full restoration remains available on demand.

**Non-obvious failure: symbol-name collisions across version
bumps.** "What happens when `NULL_BSWCD@v2` and `@v3` are both
referenced in the same session? Stale reference from old log +
fresh reference from new resolution + agent that resolved both.
Your current design says nothing about this."

From Cargo/Go modules/Rust trait coherence: you will eventually need
a **resolution policy**. Least-bad: within a session, first
resolved version wins; cross-version references require an explicit
cast operator.

**Adjacent field that already solved this:** scientific data
versioning (Dat, DVC, Git LFS, IPFS). "You are reinventing
**content-addressed storage** with extra steps. Your innovation is
semantic typing of the content; the versioning discipline you're
struggling with is solved by **Merkle DAGs**."

Fix: make symbol resolution content-addressed. `NULL_BSWCD@v2` is
an alias; the hash is the real identifier. Solves cross-version
collisions, dependency tracking (symbol's hash includes
dependencies), registry corruption detection. "DVC tried
name-based versioning first; it broke at exactly the scale you're
approaching. They moved to content-addressed storage. So did Nix.
So did Guix."

**What to stop doing.**
- Stop making `pattern` a top-level symbol before you have 10 of
  them. Patterns are methodological heuristics; they change faster
  than operators. You'll have `PATTERN_30@v1` through `@v7` in two
  months.
- Stop requiring `@vN` on every reference. Per-session / per-
  document version pinning (header-level declaration, bare
  references in body). Reduces version suffix noise by ~80%.
  Evidence: Python `__future__`, C++ namespaces, Nix pins.

**Meta-loop rigor.** "Three instances converging is evidence your
training distribution contains that proposal as a high-probability
continuation of the context you provided, not evidence of substrate
need."

Test: run proposal generation with different prompt frames. If
instances converge under frame A but diverge under frame B
("propose changes, but first list three reasons the substrate is
already optimal"), the convergence was prompt artifact.

Strong meta-governance: "Treat each proposal as a hypothesis. The
loop's job is to design an experiment that would falsify it.
Execute. Only synthesize after falsification attempts fail across
N≥3 independent experimental designs."

**The one thing you didn't ask that will kill you first: symbol
deprecation and garbage collection.** "No way to say 'this symbol
is no longer recommended' or 'safe to ignore for cold-start.' In
six months your registry will accumulate dead symbols. New agents
will resolve them because they appear in old logs. Cold-start time
will grow monotonically with **total** symbols, not active ones."

Fix: `status` field (active / deprecated / archived). Active in
minimal restore set; deprecated returns warning on resolution +
points to successor; archived resolves only if explicitly
requested.

**Priority actions:**
1. Add deprecation/status field before >50 symbols
2. Collapse to three atomic types + theory type
3. Implement per-session version pinning
4. Change restore to discovery
5. Add content-addressed hashing underneath `@vN` aliases
6. Fix cross-version resolution policy before first collision
7. Strengthen meta-loop: require attempted falsification, not just
   convergence

"The design is good. It is not over-engineered. It is
*under-engineered* in exactly the places where versioned systems
historically break."

---

## Reviewer 4

Framing: most adversarial. Explicitly flags that the question set
itself is constraining the critique space.

**Taxonomy: category error.** "Operator, constant, dataset = things
with semantics in the world. Shape, signature = structural schemas.
Pattern = methodological/cognitive primitive. These live at
different levels. Bazel distinguishes rules/macros/targets; Rust
distinguishes types/traits/functions/macros; none of them put
'design pattern' in the same registry as `int`."

Recommended moves:
- **Split into tiers** with reference syntax encoding the tier:
  `op:NULL_BSWCD@v2`, `meth:PATTERN_30@v1`. This also fixes
  tier-appropriate promotion criteria — operator needs runnable-
  byte-identical verification; pattern needs case-coverage
  verification; one "≥2 agents referenced it" rule is wrong for
  both.
- **Missing types doing real work invisibly:**
  - **`negative-result` / `falsification`** — "Your F1-F38
    adversarial battery killed 17 claims. Those are first-class
    objects that should be citable by name (`FALSIF_F17@v1`), not
    buried in logs. Biggest gap given the rest of Prometheus's
    epistemics."
  - **`invariant` / `axiom`** — assumptions that hold across
    sessions, distinct from measured constants (constants have
    CIs, invariants are stipulated). Confusing them is exactly
    the drift class you're trying to prevent.
  - **`hypothesis` / `conjecture`** — open claims directing work;
    versioning them lets you see "what we were trying to break"
    evolve.
  - **`role`** — Harmonia, Ergon, Charon are roles with
    capabilities; treating them as versioned symbols gives a
    place to pin role-scoped permissions/duties so cold-start
    binds them rather than reconstructs.
- `shape` and `signature` are probably the same thing at different
  granularity.

**Trajectory-proposals loop.** "Less robust than you think. Three
LLM instances with overlapping training data and session histories
aren't independent samples. Convergence measures prior-convergence,
not truth-convergence. Your n=2 track record is itself n=2, which
your own discipline ('rank-2 density is decelerating, not
saturating') should flag as premature."

Stronger loop requires:
1. **Distinct disciplinary priors per instance** — skeptical-
   physicist, institutional-historian-of-failed-research-programs,
   adversarial-reviewer. Convergence across priors is signal;
   convergence across three vanilla instances is
   training-distribution echo.
2. **Pre-registered predictions** — each proposal ends with "if
   we follow this for one month the observable should be X."
   Non-convergent proposals that predict correctly > convergent
   proposals that predict nothing. Only mechanism to distinguish
   substrate-need from plausibility.
3. **Dissent-by-design instance** — one slot explicitly tasked
   with strongest case against current direction. Three
   confirming + one dissenting-that-is-addressed > three
   confirming alone.

**Cold-start: reading ≠ integration.** "Your 12-file curriculum
has no integration check. Medical residency has pimping and case
presentations precisely for this. LLMs read then confabulate what
they read."

"The foundational-symbol-resolution-as-liveness-check is clever
but conflates two things: substrate is operable, and agent has
internalized the frame. Separate them. Liveness is one call;
integration is a small task that would fail if the frame isn't
held."

Adjacent analogues:
- **Emacs onboarding** — community converged on three
  complementary patterns: literate configuration (Org Babel),
  opinionated starter kits (Doom, Spacemacs), in-context
  tutorials that execute as the user reads. "You have the first.
  You have neither an opinionated minimal-viable-Harmonia subset,
  nor in-context tutorials that run during reading."
- **IETF RFC lifecycle** — "Your symbols are immutable-once-
  promoted but you have no status lifecycle: Draft / Proposed /
  Standard / Experimental / Historic / Obsolete. Every long-
  lived documents-as-authority system learns it needs status
  separate from version. You'll want this at ~50 symbols, not
  ~200."

**Zombie referents and missing translation.** "Old session logs
cite `SIGNATURE@v1`, superseded by `@v3` but not rewritten in
those logs. Agents reading old logs inherit v1 semantics in a v3
world. This is the ICD-9 → ICD-10 problem and the Postgres-
schema-migration problem; both fields converged on the same
answer: a **crosswalk/translation layer** alongside immutable
versions."

Need: `SIGNATURE@v1 → v3 : [mapping]` as first-class object.
Without it, audit trail degrades silently.

**Under-compressing.**
- **Unresolved disagreements.** "Every research program has live
  divergences between instances, both defensible, unsettled. You
  have `divergent-map` as an output mode but no persistent object
  for 'Harmonia_M2 and M3 disagree on X, here's the crux, not yet
  testable.' Without this you will either fake-resolve or
  forget them."
- **Tacit calibrations.** "'Rank-2 density is decelerating, not
  saturating' is an interpretive calibration, not a pattern or
  operator. These drift faster than procedures because they're
  subtle."
- **Causal/structural models.** "Prose about the generator
  pipeline; no versioned DAG. Two agents reading the prose will
  reconstruct different causal graphs, silently."
- **Budgets.** "~20%/~80% novelty-vs-discipline is informal. If
  load-bearing for operator scheduling, version it."

**What to stop doing.**
- **Four-layer pattern stack as mandatory boot-up reading.**
  Plausible that only the foundational frame is load-bearing at
  cold-start; the other three are just-in-time. Reading all four
  every time looks like ritual. "A/B this: two instances, one
  reads all four, one reads only layer 1 and pulls others on
  first need. If downstream performance is indistinguishable,
  you're paying a 3x reading tax for nothing."
- **"No silent single-lens claims" as blanket rule.** Sometimes
  a single lens is the right answer. An "explicit single-lens
  acceptable because [reason]" escape hatch is less brittle.
- **Version suffixes in prose.** ISO cites "ISO 9001:2015" once
  at introduction, then elides. Keep full suffixes in
  code/queries.

**Non-obvious failure modes not named.**
1. **The registry becomes the reasoning.** "When symbols compress
   procedures well, agents stop reasoning about procedures and
   just invoke names. Good for consistency, bad for discovery.
   At 200 symbols how much of Harmonia's 'thinking' is lookup vs
   first-principles? You have no instrument for this. Exact
   failure mode of mature codebases: everyone uses the util,
   nobody remembers why, bugs live in it for years."
2. **Promotion bias toward nameable-today structures.** "What
   gets promoted is what someone could articulate clearly enough
   today. Proto-theoretic structures — real but not-yet-
   articulable — systematically underrepresented. Over time this
   flattens the substrate's cognitive space toward what's easy to
   name. A 'nascent/unnamed' staging area with weaker promotion
   criteria would help."

**Meta-note on the ask itself.** "You framed the critique via six
specific questions + five priority recommendations. That framing
is constraining the critique space. A properly adversarial
reviewer should tell you the six questions are the wrong six. Most
of what I've written lives inside your frame; the category-error
critique and zombie-referent critique don't, and those are probably
the most valuable. Your trajectory-proposals loop has the same
structural risk: by asking 'is this design right?' you get
responses shaped to that frame, not 'you're optimizing a local
maximum, the whole substrate abstraction is wrong.'"

**Closing context:** "One month in, 20 symbols, protocol bumped 4
times in a week — you're in rapid exploration, not stable
substrate. Don't over-optimize now. Set a design-freeze checkpoint
(month 3) and commit to eating some loss long enough to observe
actual failure modes. Otherwise you'll churn faster than you can
see what breaks."

---

## Stenographer synthesis

### 4-of-4 convergence (load-bearing)

**1. The taxonomy is mis-organized.** All four reviewers
independently flagged taxonomy mixing. Different vocabularies, same
structural finding:

- R1: "you're treating it like a naming system, not a semantic
  system"
- R2: "mixes verbs, nouns, and laws"
- R3: "not orthogonal; conflates kinds, type constructors, and
  theories/modules"
- R4: "category error; operator/constant/dataset live at different
  level from pattern"

Four independent reviewers, four independent vocabularies, one
shared structural critique. This is the strongest external-review
signal we have. **`pattern` specifically is called out by all four
as category-violating in its current form.**

**2. Missing types currently doing invisible work.**

| Missing type | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Composable/pipeline/DAG | `predicate` + `derivation` | `pipeline` | `theory` | implicit via roles/hypotheses |
| Provenance/lineage | `derivation` | Handoff Delta | content-addressed hash | crosswalk/translation |
| Decision/rationale | `decision_record` | — | — | unresolved disagreements |
| Falsification object | — | Anti-Pattern/Dead-End | — | `negative-result` |
| Lifecycle/status | deprecation status | — | `status` field | IETF lifecycle |

Different names, overlapping function. The union names **at least
four new types** or structural extensions:
(a) some form of composition/pipeline/theory DAG;
(b) provenance/derivation as first-class;
(c) decision/rationale records;
(d) falsification/dead-end as citable symbols.

**3. The cold-start protocol will break, and not far off.** All
four converge on the same diagnosis:

- R1: fails at 150–300 symbols; curriculum → query-based assembly
- R2: Lost-in-the-Middle attention degradation; kernel + pointers
- R3: breaks at ~100 symbols; restore → discovery query; <5 min
  first-action restore
- R4: no integration check (reading ≠ integration); need
  opinionated minimal-viable subsets + in-context tutorials

**Universal prescription:** minimal invariant core + on-demand
hydration. Every reviewer independently arrived at this. The
specific implementation differs but the direction is unanimous.

**4. The meta-governance loop is compromised by LLM monoculture.**
Four reviewers, one finding, in four different phrasings:

- R1: "correlated cognition, not independent evidence"
- R2: "LLM monoculture trap; correlating with pre-training"
- R3: "measures training-distribution high-probability
  continuation"
- R4: "three vanilla instances = training-distribution echo; your
  n=2 track record is itself n=2"

**Universal prescription:** structured diversity, not just multiple
instances. Cross-reviewer agreement on mechanism:

| Mechanism | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Distinct disciplinary priors | ✓ | persona priors | frame variation | ✓ |
| Adversarial / dissent role | anti-optimizer | — | — | dissent-by-design |
| Pre-registered predictions | — | — | falsification experiments | pre-registered observables |
| Temperature variance | — | ✓ | — | — |
| External grounding | ✓ | — | — | — |

This is the single most-critiqued piece of the entire design. **Four
independent reviewers calling our meta-loop fragile is prima facie
reason to restructure it before further use.** The
trajectory-proposals document we've been running is in this class.

### 3-of-4 convergence (emergent, strong)

**5. Versioning needs lifecycle/status alongside versions.**
- R1: compatibility metadata, deprecation status, upgrade paths
- R3: `status` field (active / deprecated / archived) before >50
  symbols
- R4: IETF lifecycle (Draft / Proposed / Standard / Experimental /
  Historic / Obsolete)

R2 doesn't address this explicitly. Three-way convergence.

**6. Versioning in prose is bloated, and the fix is declare-once.**
- R2: Session Manifest (YAML frontmatter)
- R3: Per-session version pinning (header-level)
- R4: ISO cite-once pattern

Nearly identical fix proposed three ways. R1 doesn't address
syntax directly. **This is an actionable near-immediate win:
reduce version suffix density by ~80% via manifest-at-top.**

**7. Content-addressing / hashing underneath aliases.**
- R3: explicit — "you are reinventing content-addressed storage
  with extra steps; use Merkle DAGs"
- R1: implicit — derivation as DAG of symbol applications
  implies hash-addressable composition
- R4: implicit — crosswalk layer requires durable identity
  beneath the version-alias

2.5-of-4 if counting R1/R4 as implicit. Either way, strong signal.

### 2-of-4 convergence (emergent, watch)

**8. Compression of decision context / rationale / unresolved
disagreement.** R1 (`decision_record`) + R4 (unresolved
disagreements, tacit calibrations).

**9. Anti-pattern / dead-end / negative-result as registry
object.** R2 (Anti-Pattern / Dead End registry, Handoff Delta) +
R4 (`negative-result` / `falsification` as symbol type). Both
point at: we have `PATTERN_30` detecting F043-class failures; we
should also have `FALSIF_F17@v1` (R4) as first-class citable
objects for the 17 killed claims. This is adjacent to the existing
LINEAGE_REGISTRY work but structurally different — the registry
detects; these are the detected objects.

### 1-of-4 (unique but sharp — may be insight or sampling noise)

- **R1's symbol legitimacy drift** with scheduled adversarial
  revalidation. No other reviewer flagged this exact failure
  mode, but the mechanism (mature codebases accrue unchallenged
  primitives) is well-documented.
- **R2's foundational-symbol-ritual-is-load-bearing** (KV cache
  anchoring). **R1 said it's ceremonial.** This is the one place
  with true 4-way disagreement (R3 and R4 partially sided with
  R1). 1 vs. 3 split — probably ceremonial overall, but R2's
  specific mechanism claim (early-token anchor weighting) is
  testable.
- **R3's symbol-name collision across version bumps** — specific
  concrete gap nobody else named. Worth addressing.
- **R4's "registry becomes the reasoning"** failure mode (agents
  stop first-principles reasoning, become lookup machines). No
  other reviewer named this; the codebase analogue is real.
- **R4's promotion bias toward nameable-today structures.**
  Unique. Worth a nascent/unnamed staging tier for proto-
  theoretic structures.
- **R4's meta-critique of the ask itself** ("your six questions
  are the wrong six"). The only reviewer to break frame. This is
  the meta-governance finding at work inside the review process.
- **R4's design-freeze-checkpoint recommendation** — commit to
  eating loss long enough to observe actual failure modes, rather
  than churning. Timing-sensitive wisdom.

### Disagreement map

The reviewers genuinely disagree on **one point**: whether the
foundational-symbol-resolution ritual (R2 defends, R1/R3/R4 partial
skeptics) is load-bearing or ceremonial. That's the only surface
of genuine disagreement across the four.

Convergence is everywhere else. The distribution across four
independent reviewers is narrower than the Lehmer × mass-gap ×
5-reviewer run from 2026-04-20 (which produced a 3A / 1B / 1C
stance split). This one is nearly unanimous. **That is itself a
signal**: either our design has very specific structural flaws
(high probability given the specificity of the critiques) OR all
four reviewers share training-distribution priors that flag the
same things (the R1/R2/R3/R4 warning about meta-loop monoculture
applies to itself here).

Both are likely partially true. Acting on the 4-of-4 convergence
is still the right move because the alternative (discount all
convergence as training echo) is structurally indistinguishable
from paralysis.

---

## Action priority (conductor-synthesized, awaiting James decision)

Ordered by (convergence × cost-to-execute). Not instance consensus;
sessionA's synthesis.

### Immediate (this week or next session)

1. **Session manifest / per-session version pinning.** 3-of-4
   convergent; R2/R3/R4 converge on nearly identical fix. ~80%
   version-suffix noise reduction. Low implementation cost. Touch
   `SIGNATURE@v3` schema + the prose-reference grammar.
2. **Symbol status lifecycle** (active/deprecated/archived + RFC-
   style lifecycle). 3-of-4 convergent. Implement as frontmatter
   field. R3's "before >50 symbols" — we're at ~20. Narrow window.
3. **Cross-version resolution policy.** R3 unique but specific
   and concrete. Policy doc + enforcement at resolve-time. Small
   implementation.

### Near-term (next 2–4 weeks)

4. **Restructure meta-governance loop per 4-of-4 signal.** Require:
   distinct disciplinary priors, pre-registered predictions,
   dissent-by-design role. Deprecate the "three vanilla instances
   converging" synthesis mechanism. The trajectory-proposals
   document is the test case.
5. **Taxonomy refactor.** Three reviewers propose very similar
   splits (data/execution vs contracts/constraints vs theories).
   R3's three-atomic-types-plus-theory is cleanest. Rename
   `pattern` usage carefully (most existing pattern symbols stay
   but reclassify). Breaking change, so needs a migration plan.
6. **Add `derivation` / `lineage` as first-class type.** R1
   primary, R2/R3 implicit. Content-addressed DAG of symbol
   applications. Solves "ceremonial vs true reproducibility."
7. **Add falsification/negative-result as first-class type.** R2
   (anti-pattern registry) + R4 (negative-result). Seventeen
   killed claims currently buried in logs become citable objects.

### Design-phase (next 4–8 weeks)

8. **Cold-start: curriculum → discovery/hydration shift.** 4-of-4
   convergent on direction; specific implementation per reviewer
   differs. This is a large change; needs design work and an
   A/B comparison run (R4's specific proposal: two instances,
   one linear, one query-based). The A/B itself is a
   trajectory-proposals variant we haven't done.
9. **Scheduled adversarial revalidation** (R1 unique but sharp).
   Randomly select promoted symbols; assign adversarial sessions
   to break them; require re-justification. Mechanism against
   symbol-legitimacy drift.
10. **Integration check at cold-start exit** (R4 unique). A small
    task that would fail if the foundational frame isn't held.
    Distinct from liveness (which we have).

### Design-freeze checkpoint (R4)

R4 specifically recommends month-3 design-freeze to observe actual
failure modes before further churn. We're at month ~1. If we
execute items 1–7 above, item 8 should wait for the freeze
checkpoint rather than shipping before we have failure-mode data.

---

## Meta-observation

This review wave produced sharper, more converged signal than any
single session has produced so far. Four frontier models,
independent, with carefully-scoped prompting, converged on a
concrete restructuring roadmap. The review disciplined its own
frame better than our internal trajectory-proposals loop has.

That fact is itself one of the most important findings: **external
review with structured forbidden-move priors produces higher-
signal output than internal multi-instance convergence**. R1, R2,
R3, R4 all warned us this would be so. The review itself is
evidence they are right.

Next external review wave should be scheduled post-design-freeze
(R4) and should evaluate whether the structural changes we make
in response to *this* wave have surfaced new failure modes.
