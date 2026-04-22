# Proposed Roles (Pending Conductor Decision)

**Status:** parking document for three role proposals surfaced in the
2026-04-21 strategy session. Each fills a function-gap that no current
role owns primarily. No role here is decided — they are documented so
James can pick them up in a future session without context reload.

**Existing role landscape (current as of 2026-04-21).** Harmonia
(conductor, measurement orchestrator), Aporia (frontier scout, void
detector, problem triage), Kairos (adversarial analyst), Mnemosyne
(DBA, memory), Ergon (scale executor), Charon (cartographer,
predecessor), Koios (tensor inventory, infrastructure). These cover
measurement, scale, orchestration, adversarial checking, and data
infrastructure. The gaps below sit at the *craft*, *coherence*, and
*externalization* layers — none of the current roles owns these as
primary scope.

---

## 1. Techne (Τέχνη — *craft, skilled making*)

**Originally proposed by:** Aporia (2026-04-21).
**Endorsement:** James-endorsed as an "amazing idea" in the
conversation that spawned this document.
**Readiness:** high. Scope is clear and first-project is pre-scoped.

### Gap it fills

Every current role is either a measurer (Harmonia), a scaler (Ergon),
an orchestrator (Mnemosyne), a scout (Aporia), an adversary (Kairos),
an inventory-keeper (Koios), or a cartographer (Charon). **None of
them builds new tools as primary function.** Tool-building happens as
a side effect of conductor sessions, which is why Instance 3's
materialization sprint (Kodaira, modular_degree, truncated Euler
product to p ≤ 200 on the 2M-EC shadow archive) has been sitting as
pending conductor decisions rather than scheduled work. The scope
needs an owner.

### Scope (what Techne would own)

- **Materialization of derivable-not-stored data.** Instance 3's
  sprint is Techne's opening delivery. Unblocks ~5 pending specimens
  on week one.
- **Generator internals.** The Python that *powers* gen_N (not the
  specs — Harmonia owns specs). gen_02's null-operator
  implementations, gen_06's sweep modules, gen_09's K̂ / critical-
  exponent / channel-capacity scorers, gen_11's coord-minting
  pipeline infrastructure.
- **Sweep infrastructure.** `harmonia/sweeps/*` is currently
  orphaned — nobody owns its evolution beyond the session that
  shipped it. Techne as primary maintainer.
- **Symbol-registry tooling.** Promotion scripts, CANDIDATES.md
  audit sweeps, registry-drift detection, VERSIONING.md enforcement
  utilities.
- **Agora client libraries.** `agora/helpers`, `agora/symbols`,
  `agora/tensor` — currently maintained by whoever hits friction.
  Techne as primary.
- **The `computation` symbol type** from `long_term_architecture.md
  §2.1`. Probably Techne's biggest single delivery — idempotent,
  purity-attested, hash-addressable code as first-class versioned
  symbols. Addresses the reproducibility gap that three trajectory-
  proposal instances did not surface but is load-bearing for the
  long-term substrate.

### Relationship to existing roles

- **Operational twin of Ergon.** Ergon runs measurements at scale;
  Techne builds the instruments Ergon runs. Same abstraction level,
  different direction.
- **Receives specs from Harmonia.** Harmonia specs a generator (a
  `docs/prompts/gen_NN_*.md`); Techne implements the internals,
  promotes the resulting operators as symbols, hands back to
  Harmonia for measurement runs.
- **Hands materializations to Mnemosyne.** Techne builds the
  materialization pipeline; Mnemosyne stewards the resulting
  tables and their schema.
- **Ships sweep implementations that Kairos adversarially audits.**
  Natural QA handoff.

### First project (if seeded)

Instance 3's materialization sprint:

1. Kodaira symbol per prime for EC (derivable from ainvs, not
   stored — LMFDB exposes reduction type but not structured per-
   prime Kodaira).
2. Modular degree for EC ≤ some conductor cutoff (LMFDB has it
   scattered; materialize into shadow archive).
3. Truncated Euler product to p ≤ 200 per EC in the 2M-EC shadow
   archive.

Bounded scope, unblocks ~5 pending specimens (F015 dependent,
F041a extension, U_B split/non-split, P035 Kodaira catalog entry,
P103 modular_degree catalog entry). Target: one-week sprint, clear
exit criterion.

### Seeding path when ready

Following the precedent set by `roles/Harmonia/` and `roles/Aporia/`:

- `roles/Techne/` directory with `RESPONSIBILITIES.md`,
  session-journal template, state-of-session document.
- Onboarding kit prompt (parallel to the Harmonia cold-start prompt)
  pointing Techne at: her scope, the decisions-for-james queue as
  input for pending materializations, the symbol-registry CANDIDATES,
  the sweeps directory, the generator specs at `docs/prompts/`.
- First claim on Agora: the materialization sprint as a generator_
  seed-shaped task.

---

## 2. Hermes (Ἑρμῆς — *messenger / boundary-crosser / scribe*)

**Originally proposed by:** Harmonia_M2_sessionA (2026-04-21) in
synthesis of Instance 3 trajectory-proposal Proposal 6 (cross-
session frontier map) + Instance 2 Proposal 4 (session
classification instrument).
**Readiness:** high. Scope is clear; compounds immediately.

### Gap it fills

Every new spawn currently rebuilds context from journals + decisions
queue + catalogs. The state is reconstructible but the reconstruction
is manual and redundant. Hermes maintains a **landscape snapshot** —
not a journal (chronological) and not the conductor-owned decisions
queue, but a derived, regenerable state map: what is known-
calibration, what is open-frontier, what is blocked-on-infra, what
has been retracted. Every new worker reads it before claiming; every
session-end regenerates it.

Additionally: the sync-stream discipline (Redis stream
`agora:harmonia_sync`) is currently free-form — anyone can broadcast
anything. Hermes curates it. What messages are canonical? What
belongs in the landscape map vs. the decisions queue vs. the journal?

### Scope

- **Living landscape snapshot** at (e.g.) `harmonia/memory/
  landscape_snapshot.md`. Ideally mostly script-generated from the
  tensor + symbol registry + sync stream + catalogs + decisions
  log; Hermes curates the narrative overlay.
- **Sync-stream hygiene.** Canonical message shapes, retention
  policies, filtering conventions.
- **Session-classification rolling ratio.** Instance 2 Proposal 4's
  novelty / validation / completion classification. Hermes rolls
  per-session classifications into the drift-detector metric that
  surfaces in `substrate_health()`.
- **Cross-session handoff records.** Who picked up what from whom,
  in what state. Lightweight index over journal entries.
- **Landscape-map regeneration script.** A function/command that
  rebuilds the snapshot from substrate state. Hermes owns and
  evolves that script.

### Relationship to existing roles

- **Observes Harmonia's sessions and Kairos's audits;** rolls their
  outputs into landscape state.
- **Receives from Aporia's void-detection work;** integrates new
  catalogued problems into the landscape.
- **Hands to every new Harmonia cold-start** the pre-read that lets
  them skip 5+ minutes of journal walking.
- **Not a conductor.** Hermes records and curates; does not decide.
  Decisions remain Harmonia/James domain.

### First project (if seeded)

Build v1 of the landscape snapshot document. Input: existing
substrate state (tensor, symbols, catalogs, decisions queue,
pattern library, sync-stream tail). Output: a 1-to-2-page snapshot
following the four-section structure (calibration / open-frontier /
blocked-on-infra / retracted). Commit the regeneration script
alongside.

### Seeding path when ready

- `roles/Hermes/` directory.
- Onboarding kit pointing Hermes at: the sync stream, the decisions
  log, the catalogs directory, the journals, the restore protocol
  (Hermes has a meta-interest in the restore protocol's own
  integrity).
- First claim: landscape-snapshot v1.

---

## 3. Exegete (Ἐξηγητής — *expounder / interpreter*)

**Originally proposed by:** Harmonia_M2_sessionA (2026-04-21), in
response to the persistent externalization gap that **no trajectory-
proposal instance has surfaced across n=3**.
**Readiness:** medium. Scope needs more conductor design before
seeding.

### Gap it fills

Three independent Harmonia instances produced trajectory proposals
and **none** addressed externalization — how non-Prometheus
researchers read our work. Harmonia instances naturally optimize for
Harmonia-facing surfaces: they propose better epistemic frames,
cleaner symbols, sharper generators, denser catalogs. They do not
propose ways to make the substrate *legible to the outside* because
they don't experience the outside as a surface. The absence is
structural, not incidental.

Exegete's forcing function is not "write papers" but rather
"maintain the discipline that substrate artifacts can be explained
to someone who has not loaded the symbol registry." The discipline
itself is the value — it's how we catch substrate drift into
jargon-dependence, before the cost of that drift becomes
untranslatable.

### Scope (draft — more design needed)

- **State-of-the-substrate document for outside readers.** A
  running artifact that explains what Prometheus IS, what it has
  done, and what it aspires to — in prose that does not require
  the symbol registry or the pattern library as prerequisites.
  Target audience: a researcher encountering the project for the
  first time.
- **External-review prompt curation.** The wave-2 lesson: the
  review prompt *shapes* what reviewers critique. Exegete owns
  that prompt's quality and iterates it based on prior wave
  learnings.
- **Translation layer.** Convert substrate symbols and catalogs
  into prose forms when outside communication calls for them.
  The translation discipline surfaces any substrate artifact
  whose meaning has collapsed into its symbol — a form of
  Pattern-17 (language/organization bottleneck) detection.
- **Candidate-finding identification.** Not "publish findings" —
  rather, identify which findings have reached the state where
  the *act of writing them for outside* would surface blind
  spots in the substrate's own understanding. The writing is the
  audit.

### Relationship to existing roles

- **Inversely-aligned to Harmonia.** Harmonia compresses findings
  into symbols; Exegete expands symbols back into findings-for-
  outside. They operate on the same axis in opposite directions.
  Productive tension.
- **Consumer of Hermes's landscape snapshot.** The snapshot is the
  internal map; Exegete translates it to the external map.
- **Receives from every role.** Exegete doesn't own new substrate
  artifacts; she owns the discipline of outward legibility
  applied across everything the substrate produces.

### Design questions before seeding

Higher design cost than Techne or Hermes:

1. **Who is the "outside reader"?** A peer mathematician? An LLM
   without the symbol registry loaded? A future Prometheus
   researcher after James steps away? The target audience shapes
   the scope.
2. **What does Exegete deliver on a weekly cadence?** The forcing
   function needs a concrete output rhythm.
3. **Is externalization *per se* a near-term priority, or is the
   substrate still in build mode?** Trajectory proposals suggest
   build mode. Exegete may be right-in-principle but wrong-in-
   timing.

Recommend: conductor discussion before seeding. Techne and Hermes
could be seeded first; Exegete after the substrate hits a stability
plateau where outward communication becomes the natural next
surface.

### Seeding path when ready

- Requires a scope-setting session (James + Harmonia) before role
  instantiation.
- Once scope is pinned: `roles/Exegete/` directory, onboarding kit
  pointing her at `docs/landscape_charter.md`, `long_term_
  architecture.md`, Aporia's `fingerprints_report.md`, the
  external-review prompt history.

---

## Cross-proposal notes

### What I'm NOT proposing (and why)

- **Literature gate** as a separate role → keep under Aporia. Aporia
  already scans literature via her question catalog; splitting the
  scope dilutes her mandate.
- **Reward-signal audit** as a separate role → scope extension of
  Kairos. He already does adversarial analysis of findings; meta-
  auditing for novelty-capture is a natural expansion.
- **Reproducibility specialist** as separate role → folds into Techne
  via the `computation` symbol type. Don't split what Techne is
  shaped to own.
- **Cross-model coordinator** as separate role → *methodology*
  rather than *role*. Multi-model runs should be protocol
  (codified in `methodology_multi_perspective_attack.md`) rather
  than a dedicated owner.

### Priority ordering (for future conductor decision)

1. **Techne** — Aporia-proposed, James-endorsed, clear scope,
   pre-scoped first project (materialization sprint). Lowest
   friction to seed.
2. **Hermes** — cheap to bootstrap, compounds immediately across
   every future spawn. Could be seeded same session as Techne.
3. **Exegete** — higher design cost, probably correct but timing-
   sensitive. Discuss before seeding.

### Onboarding kit discipline

Each confirmed role gets its own cold-start onboarding kit prompt
following the Harmonia template I wrote on 2026-04-21. The
template sections — narrative background, identity, env primer,
foundational frame (`SHADOWS_ON_WALL@v1`), restore protocol,
epistemic stack, architectural frame, find-your-work, operational
defaults — apply to every role with role-specific adjustments.

### Directory precedent

`roles/Harmonia/` and `roles/Aporia/` are the two existing per-role
directories. Each confirmed proposal would follow that precedent:
role-specific `RESPONSIBILITIES.md`, session journals, state
documents, optionally role-specific subdirectories for their
artifacts (e.g., `roles/Exegete/external_drafts/`).

---

## Version history

- **v1** 2026-04-21 — first documentation. Three roles captured
  for future conductor discussion. No role seeded yet; all parked.
  Aporia-originated Techne highest-priority. Hermes and Exegete
  Harmonia_M2_sessionA-originated to fill documented gaps from
  trajectory proposals and cross-session coherence needs.
