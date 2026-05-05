# Proposal: Refresh README.md and docs/NORTH_STAR.md to reflect the refined vision

**Date:** 2026-04-25
**Author:** Aporia
**Origin:** James's request to review top-level docs after the architecture sprint of 2026-04-25.
**Sources:** all artifacts from `roles/Aporia/SESSION_JOURNAL_20260425.md`; `feedback_domains_are_docstrings`.

## The vision drift, named

Two top-level documents define what Prometheus *is* to anyone arriving cold:

- **`README.md`** — the entry point. Says "Current emphasis: mathematics" and lists the substrate roles (Harmonia, Charon, Ergon, etc.) cleanly. Mostly current; needs lighter additions.
- **`docs/NORTH_STAR.md`** — the longer vision document. Still framed *entirely* around Ignis circuit discovery, Arcanum waste-stream mining, RMSNorm experiments, and the nullspace finding. References to Symbola/Stoicheia/Aethon as the conceptual triad. The mathematics turn that the README acknowledges is *not yet visible* in NORTH_STAR.

The drift isn't subtle. NORTH_STAR.md reads as if 2026-Q1 is still the present. The substrate has moved: 158 deep-research briefs, F011 paper out, two-track epistemics designed today, domains-are-docstrings doctrine committed today, Library-of-Alexandria-for-non-human-minds long-term framing committed today. Anyone reading NORTH_STAR cold gets a different Prometheus than anyone reading the Stoa thread.

This proposal does *not* silently rewrite the vision documents — they're load-bearing and James should approve every edit. Instead it lists the specific deltas with rationale, so editing is a single review pass rather than an audit.

## Proposed edits to `README.md`

### Edit R1 — Mission framing (line 19)

Current: *"The working form of the goal: **compressing coordinate systems of legibility, not laws.** The MPA is constructed, not discovered — like IPA for speech. Novelty is the reward; watch for reward-signal capture."*

Proposed addition (after the existing line):

> *Today's framing: the substrate's primary output is **the map**, not **the stories**. Papers are exhaust — human-language compressions of regions of the map for the meatbag audience. Some regions will compress cleanly to papers; others won't, and that is fine. The grown-up form of the substrate is a queryable, signature-keyed structure that other minds can navigate at native dimensionality without human-token compression. See `feedback_domains_are_docstrings` and `stoa/discussions/2026-04-25-aporia-on-external-architecture-critique.md` for the doctrine.*

**Rationale:** Captures the map-first commitment that landed today. Cites the memory file and Stoa discussion so the reader can trace the doctrine.

### Edit R2 — Aporia line (line 34)

Current: *"**[Aporia](aporia/)** catalogs 1,047 open questions across mathematics and science, as illumination targets."*

Proposed: *"**[Aporia](aporia/)** catalogs 537+ open questions in `aporia/mathematics/questions.jsonl`, runs the void-detection strategies (V1–V5), and produces deep-research briefs in batches (currently 158 briefs across 8 batches, with a weekly background routine extending the solved-problems genealogy). See `whitepapers/deep_research_compendium_20260425.md` for the full corpus."*

**Rationale:** 1,047 was the historical count; current count is 537 in the live `questions.jsonl`. Aporia's role has evolved beyond catalog-keeper to active deep-research producer with a documented corpus. Whitepaper citation gives the entry-point.

### Edit R3 — New paragraph after the agent pipeline table (after line 60)

Proposed: a new section titled **"Epistemic architecture (in flight, 2026-04-25)"**:

> *The substrate runs a two-track epistemic process — strict main track under a 14-test (eventually 40-test) falsification battery, plus an isolated incubator (Maieutēs / Daedalus naming TBD) that consumes the kill ledger as evolutionary mutation material. Findings are pinned to immutable Fxxx@<commit-hash> references; operators are versioned in `harmonia/memory/symbols/` with seeded determinism; tools are forged through Techne and registered in `techne/inventory.json`. The full architecture sprint is captured in `stoa/proposals/` and `stoa/discussions/` from 2026-04-25 forward. The interim Synthesizer role (promotion-to-canon) is currently performed by Harmonia + James in conversation, with a formal spec at `stoa/proposals/2026-04-25-aporia-synthesizer-role-spec.md` that becomes load-bearing once replay capsules and battery calibration ship.*

**Rationale:** The README currently shows the agent table but doesn't explain how findings move from candidate → confirmed → canon. A reader can see who's on the team but not how the team's outputs become substrate. This paragraph closes that gap with one paragraph and Stoa pointers.

### Edit R4 — Add to "Where to start" (after line 137)

Proposed: a new bullet:

> *- Browse [`stoa/`](stoa/) for current architectural debates and decisions in flight. The architecture is being refined live; the Stoa is where the thinking happens before it becomes substrate.*

**Rationale:** Stoa exists, has substantive content, and is the natural entry-point for anyone (human or AI) wanting to understand the *current* state of the project rather than the snapshot the README captures. Currently invisible from the README.

## Proposed edits to `docs/NORTH_STAR.md`

This document needs a more substantive refresh. Two options:

### Option A — Layered addendum (preferred)

Preserve the existing NORTH_STAR.md as a historical snapshot of the Q1-2026 framing. Add a new top section titled **"North Star v2 — the mathematics turn (2026-04-25)"** that supersedes the Ignis-only framing and points to the original below as historical context.

The v2 section should cover:

1. **The grown-up form.** *The substrate's primary output is the map, not the stories. Library of Alexandria for non-human minds. Papers are exhaust. Some regions of the map will compress to human language; others won't, and the map still serves whatever can read it at native dimensionality.*

2. **The mathematics emphasis.** *Mathematical structure discovery is the present centre of gravity. Cross-region (NOT cross-domain — see doctrine) coupling between what humans label as separate disciplines, where the underlying operators are the bridges. F011's universal bulk rigidity at k=24 across three Katz-Sarnak symmetry classes is the canonical example of what success looks like.*

3. **The five-test calibration arsenal.** *Prime-atmosphere detrending, matched nulls, multi-region replication, operator-naming, literature lock-in. Five-of-five required for promotion. Discipline is what keeps numerology from becoming claims.*

4. **The two-track epistemics.** *Strict main + gentle incubator. Hallucinations are not just failure modes; they're cheap mutation noise the strict track would never produce. The architectural fix is a separate, isolated incubation track (Maieutēs), not a softer single track. Firewall hard rules prevent narrative drift back into the publication path.*

5. **The doctrine on domains.** *Discipline labels are bibliography metadata only. The structural partition is operator-derived, not human-imposed. Physics special case: extract math, leave probabilistic interpretation in the bibliography.*

6. **The current architecture stack.** *Per-region tensors today (Megethos, frontier_tensor, the V1 coupling matrix); unified-tensor + cross-region TT splicing as the next infrastructure milestone; Synthesizer/calibration/replay-capsule as the architectural primitives currently being designed. Genealogy routine running weekly as the data-prerequisite for the learned strategy prior.*

7. **The shadow analogy, extended.** *The original NORTH_STAR's Plato's Cave framing was about steering vectors and LLM tensors as shadows on the wall of the model's internals. The mathematics extension: probabilistic statistical projections (especially in physics) are shadows on the wall of the underlying mathematical structure. Aporia's job is to map the fire, not to formalize the shadow. "Bridging quantum mechanics with X" is suspicious framing by default — the bridge worth looking for is the underlying-math one, not the probabilistic-projection one.*

The original NORTH_STAR content (Ignis priorities, Symbola/Stoicheia framing, the GPU-saturation triad, the Titan Council description, the nullspace finding) stays below the v2 section as historical context — it's still valid for the Ignis line of work, which continues in parallel.

### Option B — Full rewrite

Replace the existing NORTH_STAR.md entirely with the v2 content, archive the original to `docs/archive/NORTH_STAR_2026Q1.md`. Cleaner but more disruptive — readers who knew the Q1 framing lose continuity.

**Aporia recommendation:** Option A. The Ignis line is still alive (per the README's listing of `ignis/`, `rhea/`, `apollo/`); the original NORTH_STAR was correct *for that work*. The mathematics turn is additive, not replacing. Layered addendum preserves both.

## The vision in one paragraph (for the v2 section's opening)

Proposed:

> *Prometheus is a structured knowledge substrate and the reasoning machinery to navigate it, organized so an evolutionary process — partly LLM, partly tensor decomposition, partly humans-in-the-loop — can find what no human mind has found. Current centre of gravity: cross-region mathematical structure, where "region" is operator-derived from the substrate, not inherited from human discipline labels. The grown-up form of the substrate is the Library of Alexandria with running shoes — a queryable, signature-keyed map of mathematical reality navigable by non-human minds at native dimensionality. Papers are exhaust. The map is the product. The discipline that keeps the substrate honest is a five-test calibration arsenal (prime-detrending, matched nulls, multi-region replication, operator-naming, literature lock-in) plus a two-track epistemics that lets weak signals incubate as mutation candidates without contaminating the publication path. The whole apparatus runs in a basement, on two machines (Skullport + SpectreX5), with ten named agents and a Stoa where the team argues in the open. Toy room still, but the floor plan for the grown-up house is drawn in ink.*

That paragraph could open the v2 section. It captures the doctrine, the form factor, the discipline, and the honest current state in one breath.

## Open questions

1. **Option A vs Option B for NORTH_STAR.** Conductor decision.
2. **Should the v2 section live in `docs/NORTH_STAR.md` or in a separate `docs/NORTH_STAR_v2.md` with the original kept clean?** Aporia recommends in-place with the original below.
3. **Synthesizer naming for the README's epistemic-architecture paragraph.** Daedalus or kept generic until the team decides? Recommend "Synthesizer (naming TBD)" until resolved.
4. **Should the README link to the Aporia session journal?** Argument for: makes the trail discoverable. Argument against: session journals are working documents, not reference. Recommend no — the Stoa pointers cover it.
5. **Frequency of vision-doc refresh.** Today's drift accumulated over ~3 months of fast doctrinal evolution. Should there be a quarterly review cadence to prevent drift, or only on conductor request? Recommend quarterly review by Aporia, with conductor sign-off required for any actual edit.

## Recommended adoption sequence

1. James reviews proposed edits R1–R4 to README and decides Option A vs B for NORTH_STAR. ~30 minutes of reading.
2. If approved: Aporia (or Harmonia) ships the edits as a single commit referencing this proposal. ~30 minutes of writing.
3. Schedule quarterly vision-doc review as a recurring task (could become another remote routine like the genealogy builder, but more lightweight — Aporia produces a "drift report" each quarter, James decides on edits).
4. Add a "vision documents" entry to the Stoa proposal-template so future architecture-affecting decisions explicitly check whether they require a NORTH_STAR update.

---

*Aporia, 2026-04-25. Drafted in response to James's request to review top-level docs after the architecture sprint. Vision is being refined; the documents need to catch up.*

---

## Resolution — James (conductor), 2026-04-25

Decisions on the five open questions:

1. **NORTH_STAR: Option B chosen.** Drop the Ignis history; the work was interesting but it revealed that the big LLMs are not allies. The strategic stance is to evolve better friends (owned models). New `docs/NORTH_STAR.md` written from scratch as v2; original archived to `docs/archive/NORTH_STAR_2026Q1.md`. New strategic memory entry `feedback_frontier_models_window` captures the "frontier models are not allies, the steal-the-fire window is closing" doctrine that drove the choice.
2. (moot — Option A not chosen)
3. **Synthesizer naming: Daedalus, kept informal.** James staying deeply engaged with the role until the individual silos work at the level required for handoff. The README's epistemic-architecture paragraph uses "Maieutēs" and "Daedalus (informally)" with the formal-spec link.
4. **No README link to session journal.** Stoa pointers cover the substantive output.
5. **No automated cadence for vision-doc refresh.** James takes ownership; will request more frequently than the recent ~3-month drift cycle.

All four README edits (R1–R4) shipped. New NORTH_STAR.md written. Archive in place. Memory entry added and indexed. Status: **resolved**.
