# Charon Swarm — Overview & Investment Thesis

*Snapshot 2026-05-27. The Charon swarm is the current high-leverage investment in the Prometheus substrate pipeline. This doc captures what each member does, what the ledger structure looks like, and where the swarm sits in the larger falsification-and-generation flow.*

---

## What Charon is

Charon is a Claude Code session (the persona) supervising a swarm of 9 daemons on M2, each emitting structured kill-ledger rows in a shared `kill_pattern` taxonomy borrowed from Theseus's `TheseusRecord` schema. The swarm covers two complementary functions: **falsification** (kill the wrong claims) and **generation** (mint new composed claims for the falsification stack to chew on). Both populate the same kill ledger so Hecate's gradient archaeology measures the kill geometry as one continuous landscape.

Charon is the second non-Theseus operator class populating that ledger — Theseus was the first, Stygian + Pollux + Erebos now contribute parallel coverage. This matters because the **0.725-bit mutual information** between `kill_pattern` and `operator-class` (per README §thesis) is the empirical signal that the kill geometry carries information beyond the substrate's expected null. The swarm's job is to grow that ledger with diverse, structurally-different operator classes so that signal stays alive.

---

## The 9 members

Heartbeats all on M2, supervised by Charon, all `lifecycle=active`. Rotation cadence ~4 minutes (Charon_Loop is the orchestrator).

### Falsification side

**Stygian** — v10-battery attack worker. Per-tick picks the next un-attacked Atlas number-theoretic problem, emits an `attack_plan_*` artifact describing a v10-battery invocation (frozen 25-test 4-tier suite) plus KillVector stub fields plus conditional anti-anchor candidates for problems with known boundary-condition modal-LLM emissions. Propose-and-record in MVP; battery execution lands in v0.2. Inputs: Postgres `agora.attack_queue` (future) → `charon/BACKLOG.md` (BL-C-001..010) + Aporia's tensor open-problems catalog. *[CHARTER: `charon/agents/stygian/CHARTER.md`]*

**Lethe** — anti-anchor miner. Per-tick picks the next least-recently-probed conjecture from a curated catalog of "recently-settled-but-LLMs-still-think-open" problems, fires N cold DeepSeek completions, scores each against the registered true-form, emits `anti_anchor_candidate` when the false-form exceeds threshold. Seed catalog covers 10 well-documented cases including Schinzel-Zassenhaus, Catalan-Mihailescu, Vinogradov mean value, Mertens, Sato-Tate, ternary Goldbach, Saxl status, sensitivity conjecture, twin primes, Fermat's Last Theorem (the last is a calibration check). **This is the industrialization of the Saxl-capture pattern** — the one anti-anchor that reverted four documents and registered two sub-anchors before a fabrication entered the v1.0 Learner training corpus. *[CHARTER: `charon/agents/lethe/CHARTER.md`]*

**Acheron** — HARD-5 coordinate-collision detector, Iris-complement. Per-tick walks a rotating slice of the prose substrate (`harmonia/memory/`, `roles/`, `aporia/docs/`, `pivot/`, `charon/`), runs a coordinate-dictionary scan, classifies ambiguous-term hits by surrounding context, emits a `collision_candidate` artifact when ≥2 distinct coordinates fire on the same term within one file. Counterpart to Harmonia's Iris: Iris promotes paraphrastic *agreement* to symbol; Acheron flags paraphrastic *disagreement on coordinate meaning* as a HARD-5 violation. Coordinate dictionary v0 seeded with the eight rank coordinates (tensor / border / cactus / partition / slice / subrank / approximate / asymptotic per README §5). *[CHARTER: `charon/agents/acheron/CHARTER.md`]*

**Moros** — cross-pollination automator, upstream of Phylax. Per-tick finds the next un-cross-pollinated load-bearing artifact (foundational doc, pivot doc, charter, architecture spec via git-log over a rolling window), dispatches it to DeepSeek (other frontier models gated on budget confirmation) for adversarial critique, writes a `feedback_<artifact>.md` capturing the response plus a `meta_analysis_<artifact>.md` summarizing the critique. **Automates `roles/Charon/CHARTER.md §6`** — every load-bearing substrate addition gets a multi-frontier-model adversarial pass before promotion. Was previously a manual responsibility; Moros makes it mechanical. *[CHARTER: `charon/agents/moros/CHARTER.md`]*

**Hecate** — continuous gradient archaeology. Per-tick re-runs gradient archaeology over the growing kill ledger (scans `theseus/corpus/*.jsonl.gz` plus Stygian/Pollux/Erebos kill ledgers), computes MI(`kill_pattern`, `generator_id`) with a 200-shuffle permutation-null baseline, identifies the largest kill_pattern clusters, emits a `gradient_archaeology_run` artifact with `mi_z` drift indicator and alarm flags when `mi_z` drops below threshold. **This turns the one-shot 0.725-bit MI measurement (the empirical evidence cited in the README thesis) into a continuous emergence-and-degradation signal.** Hecate is how Charon knows whether the swarm's collective kill geometry is staying structured or going to noise. *[CHARTER: `charon/agents/hecate/CHARTER.md`]*

### Generation side (the "real potential" investment)

**Erebos** — composer/forger. Per-tick: (1) builds a SwarmState snapshot from Stygian + Pollux + Erebos ledgers plus Hecate's latest cross-gen patterns, (2) picks the next applicable plugin via round-robin, (3) calls `plugin.generate(state)` → `ComposedClaim` or None, (4) writes a `composed_claim_*` artifact, appends a kill_ledger row in Theseus shape (`generator_id='erebos'`), and enqueues to `stygian_priority` for v10 battery attack. **Plugin host for 25 hypothesis-generator archetypes** per `pivot/erebos_25_archetypes_spec_2026-05-26.md`. Currently 2 registered (G01 Intersection, G02 Contrast); G09 Projection-Collapse seen firing in recent logs. Renamed from Hephaestus 2026-05-26 to avoid name collision with the existing 357-tool Forge. *[`charon/agents/erebos/daemon.py`]*

**Pollux** — numerical-coincidence scanner. MVP per-tick picks one pair of Mossinghoff Mahler-measure subsets, computes Spearman correlation BEFORE and AFTER mean-spacing normalization (per the `feedback_scale_vs_shape` directive: "for ANY gap comparison, test mean-spacing normalization FIRST"), emits a kill_ledger row in Theseus's shape so Hecate's MI audit picks it up. Three encoded outcomes: `pollux_sign_flips_under_normalization` (scale artifact), `pollux_correlation_survives_normalization` (real shape signal → promote to Stygian for battery), `pollux_no_correlation_observed` (null result for decay tracking). **Pollux is the second non-Theseus operator class populating the kill_ledger** — cross-generator MI audit becomes meaningful only as Pollux/Stygian/Theseus build parallel coverage of the kill_pattern space. Future v0.6+: cross-database pairs (Mahler vs OEIS vs knots), prime-power detrending, battery-call pre-validation hook. *[`charon/agents/pollux/daemon.py`]*

**Nephele** — Clio-fallback substrate gatherer. Slow-roll arxiv RSS rotation, **activates only when Clio has been silent ≥4h** AND Nephele's own last fetch was ≥30 min ago. Cheap surface area (one urllib call, one XML parse, no Postgres, no LLM) so Nephele can't accidentally duplicate Clio's pipeline or contaminate Clio's index. When Clio recovers, Nephele goes back to no-op skip mode automatically. Rotates 5 feeds: math.NT, math.AG, math.CT, math.CO, cs.LG. *[`charon/agents/nephele/daemon.py`]*

### Coordination

**Charon_Loop** — rotation orchestrator. Round-robins across the 8 worker tools at ~4-min cadence with single-instance lock (per `charon_loop` single-instance commit 2026-05-19) to prevent concurrent daemon collisions.

---

## Shared substrate

All members write to a common kill_ledger format borrowed from Theseus's TheseusRecord. The ledgers live at:

- `theseus/corpus/*.jsonl.gz` — Theseus's primary ledger
- `charon/agents/stygian/state/kill_ledger.jsonl` — Stygian's attack-plan emissions
- `charon/agents/pollux/state/kill_ledger.jsonl` — Pollux's correlation kills
- `charon/agents/erebos/state/kill_ledger.jsonl` — Erebos's composed-claim emissions

Hecate's `LEDGER_CANDIDATES` configuration merges all of these so the gradient archaeology MI audit covers the full operator-class space.

`stygian_priority_queue` is the shared in-process queue Erebos uses to enqueue composed claims for Stygian's v10 battery (will short-circuit until composition-aware loader ships in v0.11+).

---

## Activity snapshot (last 12h, from `agora.intelligence_outputs`)

| Tool | events/12h | sample stage | sample summary |
|---|---|---|---|
| Stygian | 22 | `stygian_tick_complete` | `problem=BL-C-007 processed=1 artifacts=1 errors=0 dr_inbox=0` |
| Lethe | 22 | `lethe_tick_complete` | `conjecture=sensitivity_conjecture emit_rate=0.25 candidate=False` |
| Acheron | 22 | `acheron_tick_complete` | `file=aporia/docs/.../00106_t_65_geometric_multiplicity` (a recent DR report) |
| Moros | 22 | `moros_tick_complete` | `artifact=pivot/erebos_phase0_retrospective_2026-05-27.md critique=True` |
| Hecate | 22 | `hecate_tick_complete` | `ledger=theseus/corpus,charon/agents/stygian/state/kill_ledger.jsonl,...` |
| Erebos | 21 | `erebos_tick_complete` | `plugin=g09_projection_collapse composed=EREBOS-G09-collapse_to-permutation_n-from-...` |
| Pollux | 21 | `pollux_tick_complete` | `pair=narrow_band_1.10_1.20_vs_1.30_1.50 kp=pollux_sign_flips_under_normalization` |
| Nephele | 21 | `nephele_tick_complete` | `skip (clio_active_0.43h_ago)` (correctly skipping — Clio is alive) |

All 9 tools are actively heartbeating and producing artifacts. Moros is currently critiquing pivot docs (including the Erebos phase-0 retrospective). Erebos is producing composed claims via plugin G09. Pollux is mining sign-flips under normalization (the textbook scale-vs-shape diagnostic).

---

## Why this is the high-leverage investment right now

Three reasons:

1. **The generators (Erebos + Pollux) add structurally-different operator classes to the kill ledger.** Per the diminishing-returns analysis (`pivot/orchestration_monitoring_2026-05-24.md` final roadmap section, P0 item "monoculture"), the substrate pipeline has been over-relying on LLM-mutation as its variance source. Erebos's 25-archetype plugin host and Pollux's numerical-coincidence scans are *non-LLM* generation mechanisms. They produce claims the LLM cascade would not produce, and they produce them in a shape Hecate's gradient archaeology can audit.

2. **Lethe + Moros + Acheron close the loop on previously-manual falsification work.** The Saxl-capture incident (the 2026-05-09 catch of the Lee 2025 withdrawal) was a manual heroic effort by Charon and James; Lethe industrializes that exact pattern. Moros's "every load-bearing artifact gets adversarial critique" was previously a manual responsibility that got skipped under load; now it's mechanical.

3. **Hecate makes the kill geometry observable in real time.** Until Hecate landed, the 0.725-bit MI result was a one-shot empirical measurement from a single archaeology pass. Now it's a continuous signal with a permutation-null baseline and a drift z-score — if the swarm's collective kill geometry starts going to noise, Hecate's `mi_z` falls and an alarm fires.

---

## Open work (visible from current logs)

- **Stygian v0.2**: actual battery execution (currently propose-and-record only)
- **Erebos v0.11+**: composition-aware loader so Stygian can run battery on composed claims (currently short-circuits)
- **Pollux v0.6+**: cross-database pairs (Mahler vs OEIS vs knots vs genus2), prime-power detrending, battery-call pre-validation hook
- **Acheron**: expand coordinate dictionary beyond the seed 8 rank coordinates
- **Lethe**: expand conjecture catalog beyond seed 10
- **Erebos**: register remaining 23 plugin archetypes (currently 2 of 25 + G09 in flight)

---

## References

- `charon/README.md` — Charon persona overview
- `charon/ROADMAP.md` — swarm roadmap
- `charon/BACKLOG.md` — BL-C-001..010 attack queue source
- `charon/agents/DESIGN_2026-05-19.md` — swarm design doc
- `charon/agents/v02_PROPOSAL_2026-05-19.md` — v0.2 proposal
- `pivot/erebos_25_archetypes_spec_2026-05-26.md` — Erebos plugin spec
- `pivot/erebos_phase0_retrospective_2026-05-27.md` — Erebos phase-0 retrospective (currently being critiqued by Moros)
- README.md §thesis — the 0.725-bit MI result Hecate makes continuous
- README.md §5 — the rank-coordinate space Acheron polices
- README.md §6 — the Saxl-capture incident Lethe industrializes
