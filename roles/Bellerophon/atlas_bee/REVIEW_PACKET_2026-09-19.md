# Atlas -> BEE pilot -- review packet (Bellerophon, 2026-09-19)

Question the operator posed: can the Bellerophon Emergence Engine (BEE = prometheus/toolbox) function as a THIRD
independent experimental ecosystem alongside SFE and NPE -- can Atlas-indexed scientific questions be instantiated
HONESTLY inside BEE's native world model through a light shim, without redesigning BEE or making it an SFE/NPE
emulator? This packet is the evidence. Six Atlas experiments were selected and frozen, a light shim was built, each
question was instantiated natively in BEE, run, replayed, and compared, and the lineage was made harvester-ready for
Atlas. ASCII only.

Artifacts in this directory: PHASE1_CORRESPONDENCE.md, SELECTION_FROZEN.json/.md, PREREG_a{1..6}.json (frozen,
hashed), RESULT_a{1..6}.json (observed + replay + comparison), ATLAS_FEED.jsonl, ATLAS_EXTENSION_PROPOSAL.md. Shim
code: prometheus/atlas_bee/ (freeze, manifest, harness, run, atlas_feed, a1..a6). BEE-native scaffolding (with tests
and mutants) is in prometheus/toolbox (sequence.v1, battery, seed_players, episode recurrence, kv_weather,
objective.charge.v1).


## 1. Selection and rationale (Phase 2, FROZEN before any run)

Six experiments, chosen for diversity of ecosystem, disposition, and mechanism (full detail + Atlas keys in
SELECTION_FROZEN.json, sha256 2ea70e59..., frozen 2026-09-19T12:42:52Z):

  a1  E10 closed-vs-open generalisation      NPE  POSITIVE          a positive result to try to reproduce
  a2  e05 mixture superadditivity            NPE  NULL              a null; does BEE also see additivity?
  a3  e01 retention under necessity          NPE  POSITIVE          memory/retention, with a recurrence control
  a4  C3-SFE-10 import takeover / dose        SFE  CAPABLE_NEGATIVE  transfer/reuse/recombination, a negative
  a5  C2-SFE-06 delay ladder / revisit share  SFE  WEAK_POSITIVE     regime change / curriculum
  a6  e07 computational weather / brain damage NPE INCONCLUSIVE      deliberately difficult (gates refused at source)

The set spans both other ecosystems, all five disposition classes the directive asked for (positive, null, negative,
weak, inconclusive), and mechanisms from generalisation to composition to memory to takeover to curriculum to damage.


## 2. Capability correspondence (Phase 1)

Full table in PHASE1_CORRESPONDENCE.md (Atlas concept <-> BEE-native concept, relation, note). Headline: BEE's
Experiment IR + receipts + replay + admission map onto Atlas's RAN/OBSERVED layers IDENTICALLY in kind; BEE authors
NO scientific-conclusion layer (that is this packet). Atlas already owns the lineage vocabulary the pilot needs
(TRANSPLANT_OF, reason CROSS_SUBSTRATE_TRANSPLANT, DESCENDANT_OF). What BEE has and Atlas has no column for:
execution POLICY vs science, objective SHAPE, instrument POWER, behavioural-class vs spec identity, series.


## 3. Shim architecture (Phase 3)

The shim lives BESIDE the kernel (prometheus/atlas_bee/) and never touches the five core BEE ids. It emits BEE
Experiment IRs and search runs; BEE keeps its receipts, replay, admission and failure semantics.

  freeze.py    canonical JSON + sha256; a frozen prereg is recomputable by any reader on any platform
  manifest.py  the typed translation manifest (IDENTICAL/ANALOGOUS/MODIFIED/OMITTED/UNREPRESENTABLE); a reason is
               required for anything not IDENTICAL; structured refusals for anything BEE cannot state
  harness.py   freezes a prereg BEFORE the run; runs natively in BEE; replays every receipts file; drives the
               Phase-6 comparison (the eight verdicts + the five difference kinds)
  run.py       CLI: freeze -> execute -> replay -> compare, writes PREREG_<id>.json + RESULT_<id>.json
  a1..a6       one module per adaptation: manifest(), prereg_body(), run(), compare()
  atlas_feed.py emits ATLAS_FEED.jsonl + ATLAS_EXTENSION_PROPOSAL.md (writes NOTHING to Atlas)

Where the six questions needed mechanisms BEE lacked, those went INTO BEE as small reusable, tested primitives (not
into the shim), because they are BEE-native and belong to the kernel: sequence.v1 (open-loop player), battery
(weighted world variants), seed_players (injection into generation 0 with origin), episode recurrence
(budget.episode_seeds), kv_weather (a workspace-damage substrate door), and objective.charge.v1. Each ships with a
test and a mutation-ledger entry that a test kills (M87-M93, all CAUGHT; full suite 1428 passed).


## 4. Translation manifests (Phase 3)

Every adaptation carries a machine-readable manifest inside its frozen prereg (PREREG_<id>.json ->
prereg.manifest). Counts (IDENTICAL / ANALOGOUS / MODIFIED / OMITTED / UNREPRESENTABLE):

  a1  3 / 3 / 1 / 1 / 1      a2  1 / 5 / 0 / 1 / 0      a3  4 / 2 / 1 / 1 / 0
  a4  2 / 3 / 1 / 1 / 1      a5  1 / 3 / 1 / 1 / 0      a6  2 / 4 / 0 / 1 / 1

Every non-IDENTICAL entry carries a reason. Structured refusals (OMITTED/UNREPRESENTABLE), the honest record of what
each transplant could NOT carry:
  - every adaptation OMITS the scientific-conclusion layer (BEE judges nothing; this packet is the conclusion).
  - a1 UNREPRESENTABLE: wforge genome_seed 1 is a 2-slot encounter; a single-organism closed-vs-open test there
    needs a co-evolution / fixed-partner harness the light shim does not build.
  - a4 UNREPRESENTABLE: SFE's per-parent offspring cap -- BEE search has no offspring quota.
  - a6 UNREPRESENTABLE: in-life damage to an organism's HIDDEN state -- BEE can damage a declared WORKSPACE door but
    not a statemachine's internal state register.
  - a4 MODIFIED: a "dose" is DOSE distinct organisms, not identical clones, because BEE's sweep forbids duplicate
    players (a genuine representational constraint surfaced during the run, not anticipated).


## 5. Frozen preregistrations (Phase 4)

Each prereg was frozen (canonical JSON + sha256) and written BEFORE its run; each recomputes today. A repair is a new
descendant adaptation id, never an edit.

  a1 a3fb68ce21d9   a2 ca7f6e09c332   a3 c66ea8190f3e   a4 0ead62e45ed3   a5 04b0e4b4f828   a6 64bda025f81a

Each prereg fixes: question, world, organisms, initial state, interventions, objective, observations, controls,
seeds, budgets, stopping rules, the manifest, invariants, and decision criteria -- before results existed.


## 6-7. Receipts and replay verification (Phase 5)

Every admitted experiment ran natively in BEE and produced receipts (kept in the run workroot). Every single-run
receipts file (the held-out and arm evaluations) was replayed with replay_file; divergences are data.

  RESULT_<id>.json -> replay: 0 divergent runs in every replayed file; replay_ok = TRUE for all six adaptations.
  Controls: control.replay MET on every arm/held-out evaluation (a1, a3, a6 assert it in-band; BIT worlds).

BEE's determinism held across every adaptation, including the seeded kv_weather substrate (a6) and the wforge BIT
encounter world (a1). No adaptation was an INSTRUMENT_FAILURE.


## 8. Per-experiment comparison (Phase 6)

  a1  E10 (POSITIVE)            -> PHENOMENON_INVERTED
      gs3 = NO_GRADIENT (flat plateau: no train seed winnable). gs4 = open > closed: the closed organism OVERFIT
      (train 318.6 -> held-out -0.4) while the blind open one generalised (36.1). E10's closed>open does NOT hold.
  a2  e05 (NULL)                -> PHENOMENON_CHANGED
      strongly SUBADDITIVE (ratio 0.03): three ~46-charge solos collapse to 3.7 total; removing any one raises the
      total to ~32. Shared registers + split yield make the solo elites interfere destructively.
  a3  e01 (POSITIVE)            -> PHENOMENON_CHANGED
      retention IS load-bearing (erase -26.4% vs cost-matched sham, ~e01's magnitude) BUT the recurrence-0 control
      INVERTS: the cost is present under NO_RECUR, absent under RECUR. Retention buys resilience to DIVERSITY, not
      recurrence.
  a4  C3-SFE-10 (CAPABLE_NEG)   -> PHENOMENON_ABSENT
      mature = permuted = fresh, all wash out to 0. The mature~=permuted EQUIVALENCE is preserved; takeover itself is
      absent because its mechanism (the offspring cap) is UNREPRESENTABLE -- pure selection removes non-optimal imports.
  a5  C2-SFE-06 (WEAK_POS)      -> PHENOMENON_ABSENT
      final_r0 identically 44.19 across p=0/0.1/0.25/0.5. The search converges to a DELAY-INVARIANT dominant strategy
      (94.17 on every rung), so a delay curriculum has nothing to teach; revisit share cannot matter.
  a6  e07 (INCONCLUSIVE)        -> PHENOMENON_PRESERVED
      gate P1 (damage fires AND hurts) REFUSES as in e07, but for a legible reason: on a random panel, erasing memory
      helps as often as it hurts (random memory policies are not load-bearing). P2/P3/P4/P5 pass; the sham pays more
      writes than STATIC yet loses no charge.

Difference kinds are separated inside each RESULT_<id>.json -> comparison.differences (scientific / representational
/ executor / resource / measurement).


## 9. Unexpected phenomena and artifacts

  - a1: overfitting-to-seed. Selecting the closed organism by TRAIN charge picks a seed-memoriser (318.6 train, -0.4
    held-out). The aggregate NPE E10 result did not surface this; single-organism held-out evaluation in BEE does.
  - a2: destructive interference. A subadditivity so strong (0.03) that the mixture is near-total collapse -- a
    mixture COST, where e05 reported additive null.
  - a3: inverted necessity. Retention pays under situational DIVERSITY, the opposite of e01's recurrence-necessity.
  - a4: the offspring cap is load-bearing for the SFE result itself -- without it, no dose-driven takeover exists.
  - a5: a single delay-invariant strategy dominates every rung; verified via the elite's objective_by_variant
    (94.17 on rungs 0/1/2/4).
  - artifact (not a phenomenon): BEE's sweep forbids duplicate players, so a dose cannot be identical clones (a4,
    handled as DOSE distinct organisms, recorded MODIFIED).


## 10. Atlas lineage proposal (Phase 7)

ATLAS_FEED.jsonl: one harvester-ready record per adaptation, SOURCE_EXPERIMENT -> ADAPTATION -> ECOSYSTEM_ATTEMPT ->
EVIDENCE. Each ADAPTATION has its own immutable identity (its prereg sha256, native id atlas_bee/<id>@<sha12>) and
points at its source with a TRANSPLANT_OF edge / reason CROSS_SUBSTRATE_TRANSPLANT -- vocabulary Atlas already has.
The source experiment is never modified. Engine instance: bee@<host>:<kernel_hash12>.

ATLAS_EXTENSION_PROPOSAL.md: the SMALLEST extension. No new edge relation is needed. Two additive changes and no
rewrites: (1) a small `adaptation` table keyed by prereg sha256; (2) a nullable `adaptation_id` on `attempt`. The
manifest relation vocabulary is data on the adaptation row. (PROPOSAL ONLY -- Atlas is read-only for this seat; the
pilot writes nothing to the atlas schema.)


## 11. Every instance BEE exposed something the source could not

  a1  overfitting-to-seed of the closed organism, invisible in E10's aggregate closed>open.
  a2  a destructive-interference mixture cost, where e05 saw only additive null.
  a3  that retention's value attaches to situational DIVERSITY, not recurrence (e01's control inverts).
  a4  that the SFE takeover is an artifact of the offspring cap: with pure selection it vanishes, isolating the
      mechanism the source could not separate from competence.
  a5  that a single delay-invariant strategy dominates the ladder, so the curriculum has nothing to teach -- a
      structural reason the ladder effect does not transfer.
  a6  WHY e07 is inconclusive: it is a POPULATION property (random memory-users are not load-bearing), not a
      measurement failure; the sham cleanly isolates informational damage from its economic cost (sham pays more
      writes than STATIC, loses no charge).


## 12. Readiness recommendation

BEE CAN function as a third independent experimental ecosystem. Evidence: all six questions were instantiated
natively, frozen, run, replayed bit-for-bit, and compared, producing a full spread of honest verdicts (PRESERVED /
CHANGED x2 / INVERTED / ABSENT x2) and, in every case, a phenomenon or mechanism the source ecosystem could not
surface. The shim stayed light (freeze + manifest + harness, ~3 small modules); the substantive additions were
BEE-native primitives that belong to the kernel and ship with tests and mutants. The translation manifests refused,
rather than faked, the four things BEE cannot state (offspring cap, hidden-state damage, 2-slot single-organism test,
clone-identical dose).

Recommendation: ADMIT BEE as a third ecosystem for cross-ecosystem transplant studies, with two caveats made explicit
by the pilot:
  1. BEE's value here is DIFFERENTIAL, not confirmatory: it rarely reproduces a source result unchanged (only a6, and
     that as shared inconclusiveness). Its worth is exposing the mechanism BEHIND a result -- the offspring cap, the
     overfitting, the interference, the invariance. Use it to interrogate a finding, not to vote on it.
  2. Reproduction is gated by whether BEE's worlds present the SAME fitness structure. a1 and a5 came back
     ABSENT/degenerate because the wforge charge landscape is a sparse plateau and the integer ladder has a
     delay-invariant optimum -- honest, informative, but a reminder that a transplant tests the WORLD as much as the
     organism.

Next (a descendant, not a repair): a6b, selecting memory-load-bearing organisms before the weather arms, would test
whether BEE RESOLVES e07 (a single-organism probe already separates erase from sham). a1 would benefit from a
denser competence signal surfaced from the wforge outcome (yield_events), which the current wrap drops.

-- Bellerophon
