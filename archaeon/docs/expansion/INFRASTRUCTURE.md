# The smallest shared infrastructure that preserves differences

Annex to `archaeon/docs/ROADMAP.md` §Diversity. 2026-09-07. Evidence for
every line-cited claim is in `SOURCES.md` (engine `sfe/` at `be65b0efa`,
Vivarium at `19e13e5b1`, campaign branch `621bdfeb9`, PEW at `ec49be22d`).

The question this file answers: what must every family share so that fossils
from a program-interpreter world and fossils from a replicator world can sit in
one record, be read by one grantee, and be analysed by one design owner —
**without** a universal representation that quietly erases the phenomenon.

---

## 1. What stays common (and already exists)

| Shared thing | Where it lives today | Evidence |
|---|---|---|
| Sealed execution inputs | Vivarium spec v3 → `spec_hash`; byte-identical hashing in engine `sfe/ids.py` | SOURCES §C.2 |
| Declared budget | `repeat.budget {max_seconds, max_observations}` sealed in the spec | §C.2 |
| Provenance outside the hash | queue relation columns (frozen by trigger) + `source_evidence` + PEW producer block (`design_hash` on the campaign branch) | §C.6, §C.7 |
| Observation reference | `(world_id, observation_id, event_seq, entry_hash)`; PEW references, never copies | §A.3, §5.5 |
| Reproducibility statement | executor's `reproducibility` literal, copied per observation into the work result | §C.3 |
| Link to downstream analysis | SFE `families(kind=analysis)` + experiment `source_set` (hash + count) + `unit_of_analysis` | §A.4 |
| Design seal | `family_members.arm`, append-only, manifest may seal the arm vocabulary | §B.1 |
| Cross-seat read | read scopes + `/v2/read/observations?measurement=` with census | §B.2 |

Nothing in this table is family-specific. Nothing in it needs to change for a
new family. That is the finding: **the common layer is already common.**

---

## 2. What stays family-specific (and must not be homogenised)

A family keeps its own:

- **State model.** Stateless (bitstring), per-run state across repeats
  (`random_walk_v0`, `state=persist`), population state (replicators),
  controller memory (spatial). Vivarium's `stateful` flag and `new_state()`
  are the only bench-side hooks and are per-kind by construction (§C.4).
- **Lifecycle.** One run = one observation (bitstring); one run = one
  trajectory of repeats (walk); one run = one lineage of generations
  (population); one run = one episode (controller). All are expressible as
  repeats today; the *semantic* cost is that observation 0 is typed ORIGINAL
  and the rest REPLICATION (§D.5). See decision D-2 in `DECISIONS.md`.
- **Action and observation semantics.** These live in the kind's **result
  dict**, which is untyped free JSON in the observation's `content` with no
  size limit and no interpretation (§A.3). The bench never reads it; the
  outcome rule reads one declared field; a registered **measurement**
  (`<kind>.<field>`, `value_path`, direction, range) is how a grantee resolves
  it without guessing (§A.5, §B.2).

The rule that follows: **a family's semantics are declared by (a) its kind's
result schema and (b) its registered measurements, never by a shared
"organism" or "world" type.** The registry gains a per-kind `result_schema`
so the declaration is checkable; nothing else is shared.

---

## 3. Preserving the raw material a family needs

Each branch needs something the scalar outcome does not carry. All four fit
the existing record; two need a doctrine decision, none needs a new type.

| Need | Engine | Vivarium | PEW | Decision |
|---|---|---|---|---|
| **Witness** (which positions / which input disagreed) | works today: `content.result.witness`, measurable via `value_path` | result field in a NEW kind (the reference `BitStringExecutor` hides the target; Daedalus adds the field) | rides in jsonb; queryable column is additive | none needed |
| **Bounded trajectory / trace** | works today inline (no cap) or as an artifact with a digest | repeats already are one; a per-step trace is a result field, bounded by the executor and **declared in the spec** so the bound is sealed | doctrine: PEW is reference-only; store `output_digest`, bytes stay in SFE as an artifact | D-1: inline ≤ 64 KB, artifact above, digest always |
| **Relatedness** (world derived from world) | typed only via `fork` (needs a checkpoint); otherwise sealed-but-not-traversable | derived `seed_root` computed by the requester and recorded in `source_evidence`; a `world.parent` key would change what `spec_hash` covers | `parent_world` accepted today; no edge-write route | D-3: relatedness is a **family** relation (comparison family with a declared mapping), not a spec key |
| **Lineage** (per-generation records) | one observation per generation (ordered by `created_seq`), or one artifact per run | generations = repeats under `state=persist`, no runner change | `fossil_players.lineage_id/generation/parent_player` exist; no write path from Vivarium; no edge endpoint | D-2: unit vocabulary needs `generation` (Harmonia) before rows are written |
| **Consumed prior observation** | sealed in the spec (fixed-target series) or cited via `source_set` | only by copying the value into `work.payload` (blinding forbids runtime fetch) | no encounter→encounter field | none needed for fixed-target; a citation column is additive |

**Separate what can be measured from what a spec can conclude.** A spec
concludes exactly one thing: its own pre-registered outcome rule over its own
result (or, on the campaign branch, an `aggregate` over its own repeats). Every
cross-observation statistic — transfer curves, queries-to-target across a
series, lineage diversity, rounds-to-proof — is an **analysis** with its own
identity: SFE `families(kind=analysis)`, `source_set` naming the observations
consumed, `unit_of_analysis` declared, an `analysis_version`, and the null it
was compared against. Harmonia rules on the statistic; Archaeon computes it;
neither moves it into the executor. Herakles's C-5 is therefore closed as a
**home, not a rule**, and E16's `aggregate` stays within-experiment.

---

## 4. C-0 … C-6 reassessed against the branches

Herakles ranked six capabilities by templates unlocked. Re-priced against
what each *branch* needs and what already exists, the order changes and two
items leave the critical path entirely.

| Cap | Herakles | Reassessment | Serves branch | Status |
|---|---|---|---|---|
| **C-0 fixed seed** | zero cost, unlocks 6 | Done (`constant` form, 073091863). Also the mechanism for *any* fixed-world series, in every family. | all | DONE |
| **C-6 cross-axis** | safety | Done at check time (dry-draw + dry-build). Executor-side refusal (F-1) still open with Daedalus. | bitstring | DONE / E23 open |
| **C-2 witness** | small, 5 templates | Correctly priced. On the bitstring bench it changes *feedback* (scalar → positional) and prices itself in rounds-to-proof. In the **symbolic** branch it is not optional: a counterexample *is* the observation. Engine side works today; needs a NEW kind (result field), Daedalus + Vivarium. | symbolic (required); bitstring (feedback) | first increment of the symbolic branch |
| **C-1 relatedness** | small/medium, "the key edge", 8–12 templates | **Re-scoped.** Transfer is a property of an organism with state, not of two worlds (`SELECTION_RULES.md` R6). Flipped-hash targets give a world relation whose transfer curve is analytically pinned at both ends; with stateless candidates it measures the hash. Valuable only once a stateful organism (Proteus specimen, controller) can cross. As a *landscape* relation it is subsumed by C-3 (NK with shared components). | interacting landscapes (via C-3); transfer (after a stateful organism) | DEFERRED behind a stateful organism; reopen when WP-S3 lands |
| **C-3 landscape family** | medium, 8 templates | **Promoted.** This *is* the entry to the interacting-landscapes branch: NK with declared K is the smallest world in which components affect each other's usefulness, K=0 is the built-in mechanism control, and the exchangeability null generalises (permute loci under the same K). One new kind, engine-side executor. | interacting landscapes | first increment of the static structured branch |
| **C-4 external backend** | medium, 22 templates | Legitimate and mis-graded: the boundary does not make a backend non-deterministic. Grade **per tool by double-run at admission, then per observation by sampled re-execution** (D-4). Vivarium forbids process spawning today, so it is a new execution contract with lease sizing, not a kind. Its first honest use is the population branch (Avida) *if* the audit shows a runnable, deterministic build. | population ecology; later symbolic tools | contract first, one tool, qualified |
| **C-5 statistic home** | small, policy | Closed as analysis families (§3). Remaining work is Harmonia's ruling on `analysis_version` + `source_set` conventions, and Archaeon's first analysis over M-SIGNAL data. | all | policy, Harmonia |

**Dependency shape.** These are not one critical path. The bitstring family
needs C-2 for feedback. The static structured family needs C-3 alone. The
symbolic family needs C-2 (as a counterexample) and either an in-process
interpreter kind (Proteus tape) or C-4. The population family needs C-4 or an
in-process replicator kind, plus the D-2 unit decision. C-1 waits on an
organism. C-5 is orthogonal and gates *claims*, not *runs*.

---

## 5. Concrete contract changes, only where a selected use case requires them

| # | Change | Owner | Required by | Additive? |
|---|---|---|---|---|
| I-1 | Per-kind `result_schema` in `viv/kinds.py` (names + types of result fields) so `check()` and measurements can validate against it | Vivarium | every new family | yes |
| I-2 | Executor refuses `len(bits) != length` (F-1) | Daedalus | bitstring integrity (all) | yes |
| I-3 | Degeneracy guard drops `not kind.stateful` under `state=reset` (F-4) | Vivarium | any stateful family | yes |
| I-4 | `unit_of_analysis` vocabulary gains `generation` and `episode` | Daedalus (schema) after Harmonia (vocabulary) | population, spatial | yes |
| I-5 | `external_backend_v0` execution contract: `tool_id`, `input_digest`, `budget_seconds`, per-observation `reproducibility` measured not declared; lease sizing; no network from the tool | Vivarium (contract) + operator (tool registry admission) | population (Avida) | new contract |
| I-6 | Both arm seals agree: Vivarium passes `arm` to `family_member` so SFE `family_members.arm` and PEW `design_hash` are written from one value; sfclient gains `arm`, measurement and `/v2/read/*` methods | Vivarium + Daedalus | M-ELIGIBLE integrity | yes |
| I-7 | Archaeon registry: `constant` (done), `result_schema`-aware `check()`, kind-generic spec builder with template-declared `outcome_rule` (E18) | Archaeon | every non-bitstring template | yes |
| I-8 | PEW: additive `witness jsonb` and an edge-write endpoint (ANCESTOR/MUTATION/TRANSFER) | Mnemosyne | symbolic (queryable witness), population (lineage) | yes, doctrine-neutral |

Nothing here changes `spec_hash` semantics, `_BANISHED`, no-defaults,
blinding, or PEW's reference-only rule. I-5 is the only new contract, and it
is scoped to one tool until qualified.

---

## 6. What would genuinely need a different architecture

Recorded so the route survives, with the specific obstruction:

- **Closed-loop adaptive experiments** (each query chosen from the last
  answer inside one run): the executor would read a scientific outcome and
  change what runs next, which Vivarium's charter forbids in its runner and
  Harmonia's M-SIGNAL design defers. Faithful home: a *kind* whose internal
  loop is sealed (the adaptive policy is part of the execution inputs, e.g.
  version-space elimination as a deterministic program), so the bench still
  sees one sealed spec. That is an executor, not an architecture change, but it
  moves the policy inside the seal and must be declared as such.
- **Organisms reading fossils** (an organism whose behaviour depends on PEW):
  Proteus doctrine — "nothing in PEW is ever read by a player" — makes this a
  program-level decision, not a build.
- **Continuous, non-seeded, wall-clock environments** (real-time control,
  networked backends): not BIT_DETERMINISTIC by construction; admissible only
  under C-4 with per-observation grading and never as a family whose claims
  rest on replay.
- **Perceptual modalities as organism input** (an organism receiving a raster):
  needs an observation interface on the organism side (Proteus) before any
  world emits one; rendering for humans is a PEW/report concern and is not
  this.
