# Archaeon roadmap

Working document. Revised 2026-09-06 after operator review; **revised
2026-09-07 with the diversity and expansion section (§D, below) after the
Herakles mining and expansion passes.** Organised around the three challenges
placed on this seat, **preceded by the delegation the first draft omitted: to
Archaeon itself.** History is preserved; nothing below §D was rewritten.

The one design idea that runs through everything: **LLMs and humans shape the
menu offline; the tick draws from the menu deterministically.** That line keeps
the selection policy falsifiable while letting the menu grow from every source.

---

## D. Diversity and expansion — what SFE could newly host (2026-09-07)

Supporting evidence and detail: `archaeon/docs/expansion/ANNEX.md` (index),
with the 69-entry crosswalk, the assets audit, the source inventory, the
branch designs, the shared-infrastructure design, the selection rules, the
dependency graph, the work packages, and the decisions register.

### D.0 Starting point, by revision

Engine `sfe/` at `be65b0efa` — **v7 is live on M1** (schema 7 confirmed by
the probe on 2026-09-07); read scopes replace group grants; the arm is sealed
on the family member record (`642736763`). Vivarium at `19e13e5b1`, with a
campaign branch (`621bdfeb9`) carrying E1 `design_hash`, E6 selection
families and E16 within-run `aggregate`. PEW at `ec49be22d`. Harmonia's
ruling `5759518f0`: arm ruling confirmed with two conditions (ordering proof;
a traversable link), three analysis levels named, D3 admitted for region
discrimination on a frozen corpus with one number Archaeon must explain, and
an M-SIGNAL skeleton with every number blank until a corpus exists. Archaeon
at `073091863` merged with main. The 2026-09-06 reports are inputs; every
claim here was re-checked against these revisions.

**Live release condition today:** v7 live ✓ · granted readback ✗ (the read
surface answers with zero rows: no scope has been granted to Archaeon's
client) · arm-bound PEW round trip ✗ (blocked on the grant and on WP-0c).
The blocker has moved from Daedalus to a grant Harmonia must run, and to
Vivarium writing one arm value into both seals.

### D.1 Established · inferred · proposed · unresolved

**Established (measured, cited in the annex).**
- One world is integrated and qualified: the 24-bit seeded onemax. Three
  kinds exist. Everything else in the repo is at most runnable in isolation.
- The bitstring bench has an analytic null: against a fresh hashed target,
  any candidate's score is Binomial(L, ½)/L. Scoped to that sampling design —
  it says nothing about information against a *fixed* target, where one
  score is an exact Hamming distance.
- Of the 69 mined proposals, 7 name an implemented kind, 0 build today; 50
  carry destroyed values, 5 of which are entailed by surviving text. The
  matrix's 31 mechanism tags are an implementation index, not scientific
  equivalence: the crosswalk keeps every entry's question and semantics.
- The record can already hold witnesses, bounded trajectories and lineage
  pointers (untyped free JSON in `content`, no cap); typed cross-object links
  are thin (`fork`; `source_set` on an analysis). PEW is reference-only by
  doctrine.
- There is **no runnable Avida or Tierra** in the repo; `ergon/avida2003/` is a
  dossier plus an unbuilt 2005 tarball of the wrong version, frozen by ruling.
- The only spatial, stateful substrate with real organisms is the 1993-95
  EvCA density-classification specimen (rule tables + numpy verifier,
  verified by execution).
- 75% of the 64 frozen Proteus specimens are world-blind under the current
  input channel (Harmonia 09-05); usable population is 7 ordered pairs.
- No qualified neutral variation operator exists anywhere in the repo.

**Inferred (from the above, by Archaeon).** The common layer is already
common (sealed spec, budget, provenance outside the hash, observation
reference, measurement identity, analysis families); no universal organism or
world type is needed or wanted. Transfer is a property of an organism with
state, so relatedness (Herakles C-1) waits on one. The cross-observation
statistic (C-5) needs a home, not a rule, and the home exists.

**Proposed (this roadmap).** Four diversity branches plus a calibration
class; a first portfolio of three families; eight rules for how diversity
survives selection; twelve decisions with recommendations; twenty-nine work
packages with owners and acceptance artifacts.

**Unresolved (named, with owner).** D-2 units for generations/episodes
(Harmonia, Daedalus); D-4 backend reproducibility grading (Vivarium,
Harmonia); D-5 analysis-family convention (Harmonia); D-6 the reserve and
descriptor numbers (operator); D-8 the Proteus input channel (Proteus,
Harmonia); D-11 the population route (spike first); WP-0d D3's null fire
rate (Archaeon, before M-SIGNAL).

### D.2 The branches (detail: `expansion/BRANCHES.md`)

- **A. Interacting landscapes** (17 entries) — NK landscape kind
  `nk_landscape_v0(bits, length, k)`; k = 0 is the built-in mechanism
  control; permutation of loci is the exchangeability null; the contribution
  vector is the family's witness. First bounded experiment: fixed-target
  series at k ∈ {0,2,4}, random queries, D3 eligibility per k against the
  null. Question not stipulated: whether an epistatic fossil record carries
  region structure a directed policy can exploit and k = 0 does not.
- **B. Symbolic execution** (17) — `program_eval_v0` on the Proteus VM
  (already integrated via the arena, replay-proven), returning outputs,
  trace digest and the **witness** (the input on which the program is wrong).
  Opcode-bijection null; witness-withheld control. First experiment:
  two-arm rounds-to-match with vs without the witness, same deterministic
  proposal rule — C-2 priced before it is used anywhere else. Organism claims
  wait on PATH B (D-8).
- **C. Spatial, stateful** (10) — `ca_density_v0` from the EvCA verifier:
  local observation, action changes the neighbours' next observation, the
  lattice is the memory; six historical genomes as fixed organisms; the
  reflection/complement symmetries are a literature-known null; r = 0 and
  T = 1 are the remove-interaction and remove-memory controls. First
  experiment: random rules vs historical genomes, witnesses (misclassified
  initial conditions) and one space-time digest preserved. A rediscovery of
  particle strategies would be a calibration anchor, recorded as such.
- **D. Population ecology** (7) — nothing runnable; begins with a two-day
  spike (build Avida 2.2 / sketch a replicator soup / compile hct01.c; run
  each twice under one seed; compare digests) before any route is chosen.
  Needs `generation` as a unit and a neutral kernel qualified by detailed
  balance before any diversity claim.
- **E. Numeric calibration** (13) and **other** (5) — instrument checks with
  analytic answers, and program-level questions routed to Aporia.

**Organism diversity, plainly:** bitstrings, rule tables, and
producer-proposed programs are the organisms this roadmap can stand up; the
64 specimens are a panel of fixed artifacts until the input channel widens;
replicator genomes wait on a kernel. LLM models or prompt variants are not
organisms.

### D.3 Smallest shared infrastructure (detail: `expansion/INFRASTRUCTURE.md`)

Common and already existing: sealed inputs, declared budget, provenance
outside the hash, observation references, reproducibility literal, analysis
families, arm seal, cross-seat read. Family-specific and never homogenised:
state model, lifecycle, action/observation semantics — declared by a per-kind
`result_schema` and registered measurements, nothing else. Raw material
(witness, bounded trajectory, relatedness, lineage, consumed prior
observation) fits the record today; two doctrine decisions (D-1, D-2). Eight
contract changes, all additive except the external-backend contract, which is
new and scoped to one qualified tool. C-0 and C-6 done; C-3 promoted (it is
Branch A's entry); C-2 required by B; C-1 deferred behind a stateful
organism; C-4 legitimate, graded by double-run, not assumed; C-5 closed as a
home.

### D.4 How diversity survives selection (detail: `expansion/SELECTION_RULES.md`)

R1 a bounded novelty reserve per lane (1 of 6 draws; unspent is recorded, not
absorbed) · R2 retention by human-declared descriptors with informative
failures never evicted by successes · R3 comparison only within a task
family; coverage as counts, never a universal score · R4 distinctness only by
intervention under matched seeds, after the family's exchangeability null ·
R5 null + mechanism control + frozen random control as conditions of
admission to the directed menu · R6 transfer only through declared mappings
carried by an organism with state · R7 repertoire and co-development held as
leads · R8 LLMs propose and translate; rejection needs a precise claim and
derivation; everything else is deferral with a reopening condition.

### D.5 First portfolio (recommendation)

    static structured      A  nk_landscape_v0            Daedalus exec + Vivarium kind
    symbolic               B  program_eval_v0 (Proteus VM) Proteus lib + Vivarium kind
    stateful interaction   C  ca_density_v0 (EvCA)        Herakles lib + Vivarium kind
    population ecology     D  spike WP-P0 first; Avida does NOT make it earlier

Why this composition: A is the cheapest world with the phenomenon and a
one-parameter control; B reuses the only integrated, replay-proven
interpreter and prices C-2; C is the only spatial substrate that is runnable
and verified today, comes with real organisms and a literature anchor, and
has single-parameter interaction and memory controls. The `ludus/arena`
worlds are the retained alternative for C (reopen when a test suite exists);
`genesis` SlotVM for A (reopen if NK cannot separate methods). Each family
ships its null, its control and its frozen random template before its first
experiment, and each first experiment is an M-SIGNAL-shaped round on that
family's own frozen corpus. Demonstrating the capability (replay-identical
executions, preserved witnesses, a control that removes the mechanism) is
separated from qualifying any conclusion; no positive effect, transfer, or
novelty is required to call a family faithfully implemented.

### D.6 Gates preserved

M-ELIGIBLE and M-SIGNAL keep their meanings and order. Integrity repairs
required by every branch (WP-0a–0f) are separated from branch-only
dependencies; expansion design and the three family builds proceed while
calibration continues. S17 predicts fragility and is never a weak-signal
detector; D1–D6 detect effect presence and are qualified by Harmonia one at a
time (today: D3, region discrimination only). Conclusions about the bitstring
bench are scoped to fresh-target sampling; a scalar score against a fixed
target already supports informative interventions, and the witness changes
the feedback, not the existence of information. Known-answer calibrations
qualify instruments and never establish discovery. The design owner has now
declared the three levels for M-ELIGIBLE (`campaign.check()["levels"]`):
randomized and analysed at WORLD, n = 4 per arm, eligibility not contrast.

**How fossils influence selection, and how that is evaluated.** Per family:
a qualified detector fires on a region → the family's directed template takes
the region (or the witness) as its parameter → the directed order and the
frozen random order are both committed against the family's frozen corpus
and universe → equal budget → Harmonia adjudicates the pre-registered
endpoint. Adding richer worlds alone does not close this loop; WP-X7 closes
it per family and is a prerequisite of each first experiment.

### D.7 Beyond the current architecture or resources

Closed-loop adaptive runs (policy inside the seal as a deterministic program
— an executor, but it must be declared as moving the policy inside the
seal); organisms that read fossils (a program-level doctrine change, not a
build); continuous non-seeded environments (admissible only under the backend
contract with per-observation grading, never as a replay-based family);
perceptual input to organisms (needs an organism-side interface first);
long open-ended evolution runs (compute; the GPU ceiling is 3–4B parameters
and irrelevant here, but host CPU-days are real); and the widening of the
Proteus input channel, which is long and not Archaeon's.

### D.8 Sequence for this section

    NOW    WP-0d (D3 null number) · WP-0e (kind-generic builder) · WP-X6
           (reserve policy file, numbers from the operator) — Archaeon
           requests filed: Herakles, Vivarium, Daedalus, Harmonia, Mnemosyne,
           Proteus (INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md)
    NEXT   WP-C1 and WP-A1 (the two cheapest worlds), WP-0f, WP-X1 ruling;
           then A2/C2 templates PROPOSED for admission
    THEN   WP-B1 once Proteus ships the VM as a library; WP-P0 spike
    THEN   first experiments A3, C3, B3 as M-SIGNAL-shaped rounds
    later  A4, C4, P1–P3, X2 (only with a tool that passed the double-run)

---

## 0. Delegated to Archaeon (the three issues in its own lane)

**0a. D2/D4 had a structural eligibility blocker, not a data shortage.** The
Proteus chart assigned one player per *world* from the manifest artifact,
excluded worlds holding several, and made each world a region — so two players
could never share a comparison region, and no number of added worlds or
specimens could fix it. The exclusion was honest; its consequence was stronger
than "we need more data".

*Done:* `sfe.spec_players.v0` attributes the player **per observation** from
the experiment's sealed `spec.pew.players`. Two players can now share a region;
a multi-player declaration is left unattributed and *counted*, never resolved
by taking the first. Measured: 21 of 3005 attested experiments declare
players, 10 non-empty, so eligibility is ~0 and is reported as such.
*Remaining:* a **comparison mapping** — region must eventually be a declared
comparison (SFE `families(kind='comparison')`), not a world. Contract with
Daedalus pending (§Delegations).

**0b. A detected signal does not change the experiment.** The producer records
the fired detector as the *reason* and draws the same random experiment.
Documented honestly, but without a milestone menu growth could continue
indefinitely without ever establishing whether fossil information improves
selection.

*Milestone M-SIGNAL (explicit, below):* connect a qualified signal to an
executable intervention, then compare against a **frozen random baseline**
under equal budget; Harmonia adjudicates.

**0c. Fire-and-forget was worded too broadly.** Vivarium owns execution
lifecycle — unchanged. But banning later correlation with completed fossils
would make selection policies unevaluable.

*Done:* charter and reader docstrings reworded (operation, not evaluation);
`source_evidence` now carries `policy_version`, `template_id`,
`selection_basis`; Vivarium asked to carry the first two into the PEW
producer block. The tick path still never asks what became of a proposal.

**0d. Cross-seat corpus access was missing from the list.** Daedalus's
contract §2: Archaeon's identity can read none of the 2,937 attested
observations that belong to `harmonia-m2`.

*Done (interim, as Daedalus specified):* the reader now applies a **declared
client-name set** and `evidence_class='ENGINE_WORK_RESULT'` in SQL, inside one
transaction, after a `schema_version` guard, and records the population in
every corpus window and census row. Measured: 61 attested observations from 13
test-harness clients (`vivarium-selftest` ×24, demo, crashtest, livebar, probe)
had been pooled in as science. *Remaining:* the deliberate read grant is
Daedalus's; width requested in `roles/Daedalus/INBOX_ARCHAEON_READ_GRANT_AND_FAMILIES.md`.

---

## Corrections to the work order (operator, 2026-09-06)

- **SFE already supports multiple observations** via
  `record_observation(replication=True)` with compositional
  `REPLICATION_DIMENSIONS`. "Build multi-observation worlds" becomes:
  **Vivarium implements the repeated-execution contract; Daedalus verifies the
  existing semantics and fills demonstrated gaps.**
- **SFE already has `families` / `family_members`** (kinds `campaign |
  analysis | comparison | selection`; roles `planned | executed | abandoned |
  selected | alternative`). `topology_group := family_id` is **withdrawn** and
  remains a design suggestion pending Daedalus's contract; `topology_group`
  participates in sharing machinery.
- `selection` families with `selected`/`alternative` are the engine-side twin of
  the queue's candidate set. Vivarium asked to bind the two.
- The S17 direction warning stands: the frozen ledger specifies *lower*
  `serial_ac` as fragile. Archaeon preserves the measured rule; Harmonia
  reconciles the mechanism explanation.

---

## First coordinated milestone — M-ELIGIBLE

    2 declared comparison groups × 2 arms × 2 worlds × 4 ORDERED observations
    = 32 observations across 8 worlds
    comparable measurements · arm identity preserved in the fossil ·
    sufficient variation for the frozen features to distinguish groups

Then **Archaeon reruns Stage 0 unchanged.** That establishes *eligibility*.
Whether S17 transfers is a subsequent experiment, not this one.

Owners: Vivarium (repeated execution, family binding), Daedalus (verify
`replication=True` ordering; comparison-family arm contract), Archaeon (issue
the family through the normal producer path as `source_reason='human'`; rerun
Stage 0). Blocked until the first two land.

---

## M-SIGNAL — does fossil information improve selection?

The milestone 0b demands, stated so it can be measured rather than assumed:

1. **A qualified signal maps to an executable intervention.** A fired detector
   names a region and a probe kind (`RESAMPLE_REGION`, `BISECT_BOUNDARY`, …).
   Each probe kind needs an executable template whose parameter space contains
   the region's coordinates. Today none does — `archaeon.probe.v0` had no
   executor and is retired. So: one template per probe kind, each backed by a
   Vivarium-implemented kind, parameterised by region coordinates.
2. **Frozen random baseline.** `random.v0` is frozen now and stays as the
   control. A signal-directed policy is a *second* named policy
   (`signal.v0`), never a modification of the first.
3. **Equal budget, separate lanes, FROZEN CORPUS.** Both policies read the
   SAME recorded corpus snapshot (`corpus_hash`) and the SAME eligible
   candidate universe (`universe_hash`), and both FULL orders are committed to
   the queue as candidate sets before anything executes
   (`archaeon/producer/universe.py`). Selected and alternative identities are
   preserved through E6 into SFE `selection` families and the exported
   evidence. This makes the first campaign a precise test of selection from
   EXISTING fossil information; adapting to arriving results is a later,
   different experiment.
4. **Endpoint pre-registered.** Failures discovered per experiment executed
   (S18's), computed from PEW by `policy_version` — which is why 0c matters.
5. **Harmonia adjudicates.** Archaeon runs the arms and reports; it does not
   score its own policy.

**Three levels, named before power.** The minimum fixture is 32 observations,
8 worlds, 2 comparison families. Harmonia must state which level is
*selected*, which is *randomized*, and which is *analyzed* before any power
calculation; S18's 0.288 → 0.462 was at the (claim, dimension) level and does
not transfer to another unit unexamined. At six per day per lane the campaign
is weeks, not days — which is fine, and is why the census exists.

**"Stage 0 unchanged"** means the frozen predictor and the gate are unchanged
(`INSTRUMENT_VERSION`, `GATE_VERSION`). The corpus ADAPTER necessarily changes
to consume the family contract and is versioned and verified separately
(`ADAPTER_VERSION`: v1 raw, v2 declared tenancy, v3 pending families/arm).

**Release condition** (operator, 2026-09-06): sealed arm binding → granted
readback with Archaeon's credentials, LIVE → one complete arm-bound PEW round
trip → release the remaining M-ELIGIBLE requests.
`python -m archaeon.producer.readback_probe` reports each. **Status
2026-09-07:** v7 live; readback answers with zero rows (no scope granted to
Archaeon's client yet — Harmonia runs the grant); no arm-bound round trip.

---

## Challenge 1 — the signal campaign

*Little data for a long time; target mostly undefined.*

**Reframe.** The first deliverable is the **instrument** that would notice
signal if it were there, running continuously, plus a written account of what
enrichment would let it see more.

**Done:** `archaeon.substrate_census` — one row per tick (rows, regions,
attributed players, tenancy, per-detector eligible/total/cause, S17 units,
wishlist). `census.series()` is the campaign's chart.

**Next:** a `--census-series` CLI; Stage 0 rerun recorded into the census on a
schedule; wishlist entries marked DONE with the commit that did it; new
charts as the substrate adds fields (`resources_used`, `ecology`, players).

**Working looks like:** the census chart has a slope; a detector that was NOT
ELIGIBLE at the start becomes eligible; wishlist entries close.

---

## Challenge 2 — random science

*A menu plus a deterministic draw.*

**Next: the experiment template registry.** Templates are data:

    archaeon/templates/<template_id>.json
    { template_id, kind (Vivarium-implemented to be ADMITTED),
      param_space: { world:   { seed_root: <form> },
                     payload: { <kind param>: <form>, ... } },
        forms: constant | choices | int_range | uniform_bits | from_region
        (a FLAT param_space is accepted and normalised: seed_root -> world,
         everything else -> payload; the 2026-09-06 example omitted this
         and 69 templates were written flat against it),
      origin {source: RNG|HUMAN|LLM|LITERATURE|CHAOS,
                           field, reference, proposed_by},
      status PROPOSED|ADMITTED|RETIRED, admitted_by, admitted_at, rationale }

Draw = (template, params), both seeded and recorded. Admission is a human act;
the inbox is never drawn from. A PROPOSED template whose kind Vivarium does not
implement **is** an expansion request. `random.v0` becomes
`bitstring.uniform.v0` in the registry, frozen, as the baseline for M-SIGNAL.

Then: CHAOS mutation (proposes, never admits); coverage-weighted template
draw; discipline-mined templates via a seat with Deep Research.

**Menu-growth metric:** templates admitted per month; fraction of draws from
templates admitted in the last 90 days. A flat line is the failure mode.

---

## Challenge 3 — program expansion

**Next: program-health / monoculture report** — weekly, from queue + PEW:
distinct kinds and templates, parameter entropy per axis, outcome
distribution, execution-failure fraction. Flags are measurements with stated
thresholds, never verdicts. **Expansion register** at
`roles/Archaeon/EXPANSIONS.md`, each entry with the measurement, the lane, the
detector or template it unblocks, and a status.

---

## Delegations (current, measured)

- **Vivarium:** carry `policy_version`/`template_id` into PEW producer block;
  repeated execution via SFE `replication=True`; bind candidate sets to
  `selection` families; retire `archaeon.probe.v0` entry.
  → `roles/Vivarium/INBOX_ARCHAEON_PROVENANCE_AND_REPEAT.md`
- **Daedalus:** read grant (width stated); comparison-family arm contract;
  verify ordered `replication=True` semantics.
  → `roles/Daedalus/INBOX_ARCHAEON_READ_GRANT_AND_FAMILIES.md`
- **Mnemosyne (PEW):** what an encounter fossilizes (`players`/`ecology`/
  `resources_used` are 0/5452 in prod); `phenotype.score` on 2/6006.
- **Players:** 2/64 specimens crossed into SFE; lineages of size 1.
- **Harmonia:** adopt-or-replace D1–D6; nulls per template; S17 wording;
  adjudicate M-SIGNAL.
- **Literature mining:** per discipline, the smallest bench experiment and the
  smallest bench gap → PROPOSED templates (after the registry exists).

---

## Sequence

    DONE   0a 0c 0d (interim) · census · scheduled-task deploy · registry with
           bitstring.uniform.v0 frozen · health report + expansion register ·
           CHAOS · coverage draw (named, off) · region-directed template form +
           bitstring.resample_region.v0 PROPOSED · M-ELIGIBLE requests built and
           validating against Vivarium v3 · isolated worktree
    NOW    M-ELIGIBLE: arm ruling CONFIRMED (Harmonia 5759518f0) and BOUND
           (Daedalus 642736763, v7 LIVE be65b0efa); levels DECLARED by the
           design owner (2026-09-07); waiting on the grant instance
           (Harmonia) and one arm value in both seals (Vivarium, WP-0c);
           then issue on the operator's word, rerun Stage 0 UNCHANGED and
           report eligible units + remaining blockers
    NOW    §D.8 — the diversity sequence runs beside this, not behind it
    NEXT   comparison-family reader over SFE families/read grant when the
           contract and grant land; admit bitstring.resample_region.v0 (operator)
           so a fired D3/D5 directs; triage Herakles's 69 inbox templates into
           the expansion register by bench gap
    THEN   M-SIGNAL: Harmonia qualifies the first directed detector and
           preregisters endpoint/unit/budget/stopping rule; eval lanes;
           matched, separately versioned random control if the universe grows
    later  detectors re-qualified against Harmonia's definitions
