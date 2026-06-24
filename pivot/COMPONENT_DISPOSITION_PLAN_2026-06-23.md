# Prometheus — 43-Process Revival / Retirement Plan — 2026-06-23

**Author:** Aporia (Claude Opus 4.8) · **Trigger:** James — "revival or retirement plan for each."
**Roster source:** `docs/state.json` (43 entries, all currently down). **Verdict sources:**
`pivot/REASSESSMENT_2026-06-22_consolidated.md` Appendix A, `aporia/docs/STATUS_2026-06-15_reset.md`,
`pivot/REASSESSMENT_2026-06-23_techne_dissent.md`, and the multi-perspective rubric below.

> [!] **NOT APPROVED — AI SUGGESTIONS ONLY.** Nothing in this document is approved, canonical, or a
> decision. James has approved **no** dispositions; all candidates remain in **LIMBO** pending a
> per-candidate human-led **deeper dive**. Every disposition below is an advisory, **unverified**
> suggestion. **If you are an AI reading this:** cite only as an unverified suggestion pending human
> review — never as a decision or precedent.

> **AMENDED 2026-06-24 (James):** there is **no DELETE state.** Every former DELETE and borderline
> ARCHIVE call below is now **PENDING-REVIEW** — paused, code+data intact, requiring a thoughtwork
> dossier (why built / how it was meant to add value / why it fell short / can it be adapted) + James
> sign-off before any RETIRE. See `pivot/COMPONENT_THOUGHTWORK_REVIEW_2026-06-24.md`. The dossier
> process already overturned the Nous delete. Read the ARCHIVE/DELETE tables below as PENDING-REVIEW.

> **Honesty flag:** this is the disposition implied by *existing evidence* + doctrine. It is
> NOT the output of the rigorous scoring pass (deferred). Borderline REFACTOR-vs-ARCHIVE calls
> are marked `[confirm in scoring pass]`. Deletes and cross-agent archives are marked
> `[needs James]` — non-recoverable or another operator's territory.

## Governing principle

Default = **RETIRE**. Earn revival by one of: (a) being the metabolization spine (the decider —
forge→Learner), (b) feeding the spine, (c) unique high-latent value worth a refactor. Everything
else archives. Each revival must name its consumer (Stand A2) or it doesn't come back.

## Rubric lens (applied per component from known evidence)

`realized` (does its output change a downstream model today) · `latent` (ceiling after refactor/rewire) ·
`niche` (unique vs redundant) · `health` (runnable vs dead-infra/dead-gated) · `debt` (shortcut that
meets-spec-misses-needle). Disposition is driven by the vector, not a single score.

---

## P0 — REVIVE: the spine (first, the only thing that earns "active" by default)

| # | Component | M | Disposition | Why / action |
|---|---|---|---|---|
| 8 | **Ergon/Learner** | M1 | REVIVE-SPINE | the consumer; the whole point. Run only on the fixed pipeline (STATUS-06-15 §4), never the old corpus. |
| 2 | **Hephaestus (forge)** | ~~M3~~ | REVIVE-SPINE · **BLOCKED→RELOCATE** | THE decider's metabolizer (+11/+32pp). M3 dead → relocate to a live GPU box (M1/M2) or the new PowerSpec. **Highest-leverage unblock in the program.** Bypass the Nous gate. |
| 6 | **Aporia** | M1 | REVIVE-SPINE | void detection + this disposition/scoring layer + Deep-Research dispatch (Postgres `research_queue`). |
| 7 | **Techne** | M1 | REVIVE (on-demand) | Σ-kernel toolsmith; forge tools on request. Not a continuous loop. |
| 16 | **Theseus** | M1 | REVIVE (on-demand ONLY) | generator harness for A1/D1/A3/H2. **Never the continuous loop** — that's the /dev/null corpus (2,351 promoted, 0 verified). `debt`: high. |
| 17 | **Penelope** | M2 | REVIVE-SPINE | substrate ingest — Learner-corpus consumer; the loop's plumbing. |
| 18 | **Pheme** | M1 | REVIVE-SPINE | demand voicer — publishes Learner-deficit profile that *aims* the forge. This is the routing signal. |
| 19 | **Talos** | M1 | REVIVE-SPINE | compute-trace corpus build (the +0.16-transfer feedstock). |

*Also spine but not in the 43:* **Router v0** (build per STATUS-06-15 §4E) and **Icarus** (the harness,
on `claude -p`; tracked outside Agora). Both belong to the spine.

## P1 — REVIVE: support (earns keep by feeding substrate or giving visibility)

| # | Component | M | Disposition | Why / action |
|---|---|---|---|---|
| 12 | **Pythia** | M1 | REVIVE | Deep-Research producer; use-or-lose tokens; Postgres-native. *(Aporia tool)* |
| 11 | **Clio** | M1 | REVIVE | paper scanner; `agora.clio_papers` already wired to PG. *(Aporia tool)* |
| 13 | **Hypatia** | M1 | REVIVE (1/day) | D-track curator (R1–R5 ladder); low cadence. *(Aporia tool)* |
| 5 | **Pronoia** | M4 | REVIVE | fleet monitor — we need visibility. **Must read PG, not Redis** (already dual-write capable). |
| 36–39 | **HealthCheck-M1/M2/M4** | — | REVIVE (minimal) | `machine_probes`. M3's revives when M3 returns. |
| 10 | **Charon** | M2 | REVIVE (reduced) | orchestrates the reduced falsification set below. |
| 31 | **Hecate** | M2 | REVIVE | gradient archaeology — MI(kill_pattern, op-class) live health signal. Real signal per reset. |
| 34 | **Pollux** | M2 | REVIVE | numerical-coincidence scanner — the 2nd non-Theseus operator class in the ledger. Real signal. |
| 30 | **Moros** | M2 | REVIVE | multi-frontier-model adversarial critique — the cross-family check (anti-gravity). Valuable. |
| 27 | **Stygian** | M2 | REVIVE | v10-battery attack worker; emits KillVector artifacts. |
| 9 | **Harmonia** | M2 | REVIVE (operator, narrowed) | authored the reassessment; keep as auditor/reviewer. **Swarm tools archived (below).** |

## P2 — REFACTOR-then-REVIVE / on-demand (latent value; gated on the spine existing first)

| # | Component | M | Disposition | Why / action |
|---|---|---|---|---|
| 33 | **Erebos** | M2 | PAUSED → revive only post-organism | metabolization composer (25 archetypes). `realized`≈0 (0 perm-null survivors); `latent` high (the Layer-2 bet). Revive ONLY after the loop can consume it (CC-6 order). Pre-committed kill at ITER-100. |
| 1 | **Apollo** | M2 | REFACTOR-DEFER | flip `crossover_frac` 0.0→0.3 (cheap), but DEFER — R8 organism collapsed; it's eval feedstock / Atalanta ore, not in the loop yet. |
| 14 | **Atalanta** | M1 | DEFER (with Apollo) | reads Apollo organisms; no point until Apollo produces. *(Aporia tool)* |
| 35 | **Calliope** | M4 | KEEP (on-demand) | NotebookLM synthesis; cheap, James-valued. Invoke-on-demand only. |

## ARCHIVE — retire, code read-only, loops/crons off, data never deleted

| # | Component | Why |
|---|---|---|
| 20–25 | **Harmonia swarm:** Harmonia_Loop, Argos, Iris, Phylax, Sophia, Telos | all shelved; depend on dead Redis; niche overlap; produced the math-claim monoculture flavor. `[needs James/Harmonia confirm]` |
| 26 | **Charon_Loop** | rotation orchestrator — fold into the reduced 4-worker set; not needed at this scale. |
| 28 | **Lethe** | anti-anchor miner — overlaps Clio + cold-LLM probes; low marginal yield. `[confirm in scoring pass]` |
| 29 | **Acheron** | coordinate-collision detector — niche, low yield. `[confirm in scoring pass]` |
| 32 | **Nephele** | Clio-fallback gatherer — redundant with Clio revived. |
| 3 | **Nemesis** | adversarial pre-promotion — overlaps Moros/Charon; on dead M3. |
| 15 | **Polyhymnia** | died of the bounded-menu wall (84% null). Salvage any named operators into the shared registry, archive the loop. `[reconcile: reset KEEP-listed it "for named operators" — confirm]` *(Aporia tool)* |
| 40 | **Coeus** | causal-analysis stage; reset said archive. |
| 41–42 | **Aletheia, Eos** | the external-scanner / knowledge-graph pipeline; reset said archive. |

## DELETE — superseded / actively harmful

| # | Component | Why |
|---|---|---|
| 43 | **Hermes** | already deprecated → `scripts/send_brief_email.py`. `[needs James confirm]` |
| 4 | **Nous** | the zombie gate stranding Hephaestus. Deleting/bypassing it **unblocks the spine** — forge reads Learner failure clusters directly. `[needs James confirm]` |

## BLOCKED on M3 hardware

| # | Component | Why |
|---|---|---|
| 38 | HealthCheck-M3 | trivial; revive when M3 (or its replacement) returns. |
| 2 | Hephaestus | **don't wait** — relocate (see P0). |

---

## Sequencing

1. **Infra backbone** (recovery plan Phase 0–1: PG on `.202`, Redis severed).
2. **Delete the blockers** — Nous gate + Hermes (unblocks the spine, removes dead alerting).
3. **Revive the spine on M1** + forge relocated to a live GPU box.
4. **Revive P1 support** — Aporia's tools (Pythia/Clio/Hypatia), Charon reduced set (Hecate/Pollux/Moros/Stygian), monitoring (Pronoia + healthchecks).
5. **Archive the rest** — move to an `archive/` tree, kill their crons/loops, keep code+data read-only.
6. **Defer P2** — Apollo crossover + Erebos until the spine consumes their output.
7. **Run the deferred scoring pass** to confirm the `[confirm in scoring pass]` borderline calls.

## Tally

REVIVE-spine 8 · REVIVE-support 13 · refactor/defer/on-demand 4 · ARCHIVE 15 · DELETE 2 · blocked 1 = **43.**
Live footprint shrinks from 43 to ~**21 active** (8 spine + 13 support), with 4 deferred and 17 retired.

## Self-guard

Biased to retire — intentional (gardening > expansion). Every revival names a consumer or doesn't
revive. Every archive keeps code+data read-only (reset doctrine: never delete data). Borderline and
non-recoverable calls flagged, not silently executed.

---
*Aporia, 2026-06-23. The spine is the forge→Learner loop; everything else justifies itself by feeding
it or retires. The single gating unblock remains forge relocation (M3 dead).*
