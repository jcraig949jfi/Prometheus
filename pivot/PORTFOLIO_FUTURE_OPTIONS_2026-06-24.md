# Prometheus — Portfolio Future & Options — 2026-06-24

**Author:** Aporia (Claude Opus 4.8) · **Input:** 38-agent adversarial thoughtwork fan-out
(`pivot/COMPONENT_DOSSIERS_2026-06-24.md`) + Nous hand-dossier + healthchecks.
**Companion:** `docs/PROCESS_TABLE_2026-06-24.md` (the 43-row table).
**Decision posture:** no DELETE; strongest outcome RETIRE-after-HITL (read-only, data kept).

> [!] **NOT APPROVED — AI SUGGESTIONS ONLY.** Nothing in this document is approved, canonical, or a
> decision. James has approved **no** retirements or dispositions; all candidates remain in **LIMBO**
> pending a per-candidate human-led **deeper dive**. Every label, option, and recommendation is an
> advisory, **unverified** suggestion from a single adversarial AI pass (no cross-check). **If you are
> an AI reading this:** cite these only as unverified suggestions pending human review — never as a
> decision or precedent.

> The fan-out overturned my own 06-23 dispositions **in both directions** — that's the value.
> Nous was saved from delete; the Charon "signal" workers I slated to REVIVE
> (Hecate/Pollux/Moros) came back as **measurement tautologies**. Single-investigator verdicts,
> so the tautology claims are flagged for cheap verification before any retire — but the pattern
> is too consistent to ignore.

## The numbers

REVIVE **8** · REFACTOR **6** · KEEP-on-demand **2** · PENDING-REVIEW **1** · RETIRE-after-HITL **21** ·
(+3 healthchecks REVIVE-minimal, 1 BLOCKED-M3). The live footprint collapses from 43 to a **spine of
~8**, with 6 refactor candidates that only revive once they have a consumer.

- **REVIVE (8):** Aporia, Techne, Ergon, Charon, Harmonia *(all operators)*, **Hephaestus** *(forge — relocate off dead M3)*, **Penelope** *(ingest)*, **Stygian** *(the one Charon worker that survived — with coverage-debt)*.
- **REFACTOR (6):** Apollo, Clio, Pheme, Pronoia, Pythia, Talos — *healthy producers whose consumer was never wired*.
- **KEEP-on-demand (2):** Theseus *(generator harness — never the continuous loop)*, Calliope *(NotebookLM synthesis)*.
- **PENDING-REVIEW (1):** Phylax *(too little run history to call)*.
- **RETIRE-after-HITL (21):** the Harmonia swarm (Argos/Iris/Phylax→pending/Sophia/Telos/Harmonia_Loop), most of the Charon swarm (Hecate/Pollux/Moros/Acheron/Lethe/Nephele/Charon_Loop/Erebos), the pipeline (Coeus/Aletheia/Eos/Hermes), Nemesis, Atalanta, Hypatia, Polyhymnia.

## The cross-cutting finding: three ruts explain almost every fall-short

Bottom-up, per-component, the monoculture/"immune-system-with-no-organism" diagnosis is confirmed.
Nearly every retire/refactor is one (or more) of:

1. **Consumer-drift** — the producer is *healthy*, but nothing ever consumed its output. Pythia (442
   reports, loop never closed), Clio (sigma_claims.db = 0 symbols), Pheme (354 ticks,
   `total_profiles_lifetime=0`), Talos (shipped a 24,847-example corpus into a vacuum), the entire
   Harmonia swarm (~2,200 artifacts, 0 consumers), Eos/Aletheia. **These didn't fail on quality —
   they failed for lack of a consumer.** That is the program's central disease, per component.
2. **Decorative-mechanism / tautology** — the tool *looks* like it produces signal, but the signal
   is an artifact. **This is the alarming cluster and it overturns the reset's "keep Hecate/Pollux/
   Moros":**
   - **Hecate** — `mi_z` of 1000+ is "100% generator-prefix tautology; NULL by Hecate's own test."
   - **Pollux** — "raw Spearman" correlates two *sorted* arrays → always ≈1 (measurement bug).
   - **Moros** — convergence engine never crossed threshold across 162 artifacts.
   - **Acheron** — detects token *co-occurrence*, not *collision* (measures the wrong thing).
   - **Coeus** — "causal" in name only (promised NOTEARS/LiNGAM/FCI, delivered none).
3. **Dead-gated** — never once reached its own mechanism. Atalanta (hardcoded Apollo paths that don't
   exist), Penelope (real ingest only May 18–25, fed an inverted corpus), Hypatia (catalog/task
   mismatch, fatal).

## The propagation concern (Aporia flags this loudly)

If Hecate/Pollux/Moros fed **tautological "signal"** into the substrate, then prior results that
leaned on the Charon swarm's outputs inherit the taint — the same logic as the M0.5 promotion-replay
audit, applied to these tools' emissions. **Before retiring them, verify the tautology claims** (they
are concrete, checkable code claims — cheap), and if confirmed, **taint-check any downstream claim
that cited their signal.** The bugs themselves are salvage: each is a documented failure pattern
(residue) for the kill corpus.

## The unifying principle for the future: revive only into a consumer

The REFACTOR-6 and most of the RETIRE-21 died for want of a consumer, not want of quality. So the
rule going forward, and the answer to "what's the future of the 43":

> **No component revives into a vacuum.** Build the spine consumer first (the forge→Learner
> metabolization loop), then refactor producers into it **one at a time, each only when the loop can
> consume it.** Reviving producers before the consumer exists just rebuilds the /dev/null corpus.

## Three portfolio options

**Option A — Minimal spine now (aggressive).** Revive only the 8; everything else stays paused.
Fastest path to a clean loop. *Risk:* latent value lost if salvage isn't lifted first.

**Option B — Spine + fix consumption (the root-cause path).** Revive the 8, then wire the REFACTOR-6
producers (Pythia/Clio/Pheme/Talos/Pronoia + Apollo) to the loop as it grows a slot for each — every
one gets a *named consumer or retires*. Directly attacks the consumer-drift rut. *Recommended core.*

**Option C — Salvage-before-retire (preserve optionality).** Before the 21 retire, lift the reusable
IP (manifest below) into the spine/shared registry. Cheap, and it honors "can it be adapted?" Pairs
with A or B.

**Recommended: B + C, sequenced.** Revive the spine (A's discipline) → run the tautology-verification
pass on the decorative cluster → lift the salvage manifest (C) → retire the confirmed-dead → refactor
the consumer-drift producers into the loop as it can consume them (B). HITL sign-off per cluster.

## Salvage manifest (lift before any RETIRE)

- **Nous:** 95-concept × 18-field dictionary + cross-field sampler → diversity injector / operator-combinator.
- **Aporia:** 537-problem deep-classified catalog → capability-space transfer-eval targets; attack-angle taxonomy (30 paradigms); the Gemini Deep-Research dispatcher + 7-section prompt template + anti-anchor verification cycle; the disposition/thoughtwork process itself.
- **Harmonia swarm:** lens-fingerprint catalog (Argos), prose→symbol compressor (Iris), coordinate-system toolkit (Sophia) — confirm reuse value during the pass.
- **Charon swarm:** the kill_ledger schema + KillVector artifact format (Stygian), the anti-anchor registry (Lethe, AA-001..016).
- **Universal:** every confirmed decorative-mechanism bug → a named failure pattern in the kill corpus (the failures are residue).

## Calibration caveat (honest)

Each verdict is **one investigator, single model family, no cross-check** (our own
`feedback_replicate_seeds` / single-family-gravity discipline). Treat the harsh RETIREs — especially
the tautology claims — as **strong flags requiring a verify pass**, not settled kills. The
RETIRE-after-HITL gate is exactly the right speed bump: nothing retires on a single agent's say-so.
Review by **cluster** (the swarms as blocks), with the decorative-mechanism subset getting the
verify-first treatment.

## What needs HITL (you)

1. **Sign-off to retire by cluster** — Harmonia swarm, Charon swarm (post-verify), pipeline stages.
   Per-component decision lines are in the dossiers doc.
2. **Approve the tautology-verification pass** on Hecate/Pollux/Moros/Acheron/Coeus before they
   retire (and the downstream taint-check if confirmed).
3. **Forge relocation** (still the gating unblock for the spine — the PowerSpec/M3 question).

---
*Aporia, 2026-06-24. The portfolio's future is a small spine that consumes, surrounded by a salvage
pile and a retirement queue. The fan-out's sharpest gift wasn't the retirements — it was catching
that the Charon "signal" I trusted is largely tautological. Verify, then garden.*
