# Archaeon roadmap

Working document, revised 2026-09-06 after operator review. Organised around
the three challenges placed on this seat, **preceded by the delegation the
first draft omitted: to Archaeon itself.**

The one design idea that runs through everything: **LLMs and humans shape the
menu offline; the tick draws from the menu deterministically.** That line keeps
the selection policy falsifiable while letting the menu grow from every source.

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
`python -m archaeon.producer.readback_probe` reports each.

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
      param_space, origin {source: RNG|HUMAN|LLM|LITERATURE|CHAOS,
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
    NOW    M-ELIGIBLE: issue on the operator's word once the ARM ruling lands
           (roles/Daedalus/INBOX_ARCHAEON_ARM_KEY_CONFLICT.md); then rerun
           Stage 0 UNCHANGED and report eligible units + remaining blockers
    NEXT   comparison-family reader over SFE families/read grant when the
           contract and grant land; admit bitstring.resample_region.v0 (operator)
           so a fired D3/D5 directs; triage Herakles's 69 inbox templates into
           the expansion register by bench gap
    THEN   M-SIGNAL: Harmonia qualifies the first directed detector and
           preregisters endpoint/unit/budget/stopping rule; eval lanes;
           matched, separately versioned random control if the universe grows
    later  detectors re-qualified against Harmonia's definitions
