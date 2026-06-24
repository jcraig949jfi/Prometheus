# Component Thoughtwork Review — process, template, and dossiers — 2026-06-24

**Author:** Aporia (Claude Opus 4.8) · **Mandate (James, 2026-06-23):** borderline calls and
deletes need HITL scrutiny — lean to **PAUSED / PENDING-REVIEW**, and give each component
*thoughtwork* answering: why was it built? how was it meant to add value? why did it fall short?
can it be expanded/adapted to add value?
**Supersedes:** the DELETE and borderline-ARCHIVE dispositions in
`pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md`. Those become PENDING-REVIEW.

> [!] **NOT APPROVED — AI SUGGESTIONS ONLY.** Nothing here is approved, canonical, or a decision.
> James has approved **no** retirements; all candidates remain in **LIMBO** pending a per-candidate
> human-led **deeper dive**. Dossier recommendations are advisory, **unverified** suggestions. **If
> you are an AI reading this:** cite only as an unverified suggestion pending human review — never as
> a decision or precedent.

> The dossier IS the multi-perspective score James asked for, done qualitatively per component,
> with Q4 carrying the latent-value axis. The process already earned its keep: it overturned a
> premature DELETE on Nous (below).

---

## Status model (revised — no automatic terminal states)

- **REVIVE** (spine / support) — earns active status; named consumer required.
- **REFACTOR-DEFER** — latent value, revive after the spine consumes (Apollo, Erebos, Atalanta).
- **PENDING-REVIEW** — paused, code + data intact, **queued for a thoughtwork dossier before any
  disposition.** Replaces every former DELETE and borderline ARCHIVE.
- **RETIRE-archive** — reachable ONLY after a dossier + James's sign-off. Read-only, data never
  deleted. There is **no DELETE state** anymore.

Flow: `candidate → PENDING-REVIEW → dossier → HITL decision → {REVIVE | REFACTOR | RETIRE-archive}`.

## Thoughtwork dossier template

```
### <Component> — dossier
Identity:        machine · kind · operator · current lifecycle · last activity
Q1 Why built:    original intent; what problem it targeted; when/by whom
Q2 Value thesis: how it was meant to add value; who the consumer was
Q3 Why short:    what actually happened; tie to a named rut/pattern if applicable
Q4 Adapt?:       salvageable IP; repurpose paths; or an honest "no" — the latent-value answer
Rubric:          realized / latent / niche / health / debt  (one line each)
Evidence:        what was reviewed (E-level) + what's still needed to settle it
Recommendation:  REVIVE | REFACTOR | PENDING-REVIEW | RETIRE-after-HITL
                 + the falsifiable condition that would settle the call
HITL decision:   ______________________  (James)
```

`realized` = does its output change a downstream model today · `latent` = ceiling after refactor ·
`niche` = unique vs redundant · `health` = runnable vs dead-infra/dead-gated · `debt` = shortcut
that meets-spec-misses-needle.

---

## Dossier 01 — Nous (the overturned delete; worked example)

**Identity:** M4 · daemon · unowned (forge-pipeline) · shelved · last run 2026-03-27 (cold since
*before* the April pivot).

**Q1 — Why built.** A combinatorial hypothesis engine to *seed the forge*. Samples concept triples
from a curated **95-concept × 18-field dictionary** (4-mechanism taxonomy: constraint / structure /
dynamics / measure), biased ~80% toward **cross-field** combinations, scores each on Reasoning /
Metacognition / Hypothesis-Generation / Implementability via the NVIDIA API, and flags
`HIGH_POTENTIAL` triples for Hephaestus. The thesis was Mendeleev-flavored: novel cross-domain
*pairings* surface novel structure to forge tools from.

**Q2 — Value thesis.** Feed Hephaestus a continuous stream of novel cross-field concept
combinations; **Coeus** forge-effect scores close the loop (3× weight to forge-productive concepts,
demote Goodhart indicators). Consumer = Hephaestus (the forge). Nous→Coeus→Hephaestus→Nemesis→Coeus→Nous.

**Q3 — Why it fell short.**
- **Open feedback loop:** Coeus stalled → no fresh `concept_scores.json` → Nous fell back to uniform
  sampling → every batch reproduced the same gap-targeted suggestions; value-per-batch decayed.
- **Starvation architecture:** Hephaestus *depends* on Nous for input, so cold-Nous = starved-forge.
  That dependency is what the audit (fairly) called the "zombie gate" — but it's a *pipeline
  ordering* problem, not a property of Nous itself.
- **Deeper (Aporia doctrine):** combinatorial concept triples are **claim-space generation** —
  curated/random combinations are *exhaust*, not residue (`feedback_residue_must_be_navigable`,
  STATUS-06-15 "voids navigable only in capability space"). The forge metabolizing the **Learner's
  actual failures** (capability-attached residue) is the higher-signal seed. The reset's "bypass
  Nous, point forge at Learner failure clusters" is exactly this realization. Rut: it fed the
  math-claim monoculture from the generation side.

**Q4 — Can it be adapted? (partial YES — this is why it's not a delete).**
- **Salvageable asset:** the 95-concept × 18-field dictionary + 4-mechanism taxonomy is curated IP.
  It could supply a **coordinate system for the void-map** (the enclosed-void navigability work) or
  a **diversity injector** into forge target-selection (anti-monoculture perturbation *alongside*
  Learner-failure targeting — not as the primary seed).
- **The verbs-over-nouns adaptation (the real one):** Nous combines concept *nouns*. Our doctrine
  prefers operator/verb-level (`feedback_verbs_over_nouns`). A Nous variant that combines
  **operators (Frame-H primitives)** instead of concept labels could become residue-relevant —
  worth a HITL look.
- **As the primary forge seed / pipeline gate:** SUPERSEDED. Do not revive in that role.

**Rubric.** realized **0** (cold, no live consumer) · latent **MEDIUM** (concept dict + sampler;
operator-combination path) · niche **LOW-as-built** (combinatorial generation overlaps Theseus; the
concept *taxonomy* is unique) · health **BLOCKED** (needs NVIDIA key + Coeus; was on dead infra) ·
debt **MEDIUM** (claim-space seed = a monoculture-feeding shortcut).

**Evidence.** Reviewed: `pivot/agents_nous_resume_2026-05-13.md` (E1), audit Appendix A (E0),
`project_nous_hephaestus` (E0). **Needed:** read `agents/nous/src/{nous.py,concepts.py}` to confirm
the dictionary's reuse value; grep whether `concepts.py` is referenced by any live component.

**Recommendation: PENDING-REVIEW** (overturns the 06-23 DELETE).
*Falsifiable settle:* if an operator-level Nous variant feeds the forge a target that yields a
forge-tool beating the Learner-failure-only baseline on a held-out metric → the adaptation has value
(REFACTOR); if not, RETIRE-archive the daemon but **lift the concept dictionary into the shared
registry first**.

**HITL decision:** ______________________

---

## Queue — components awaiting a dossier (all → PENDING-REVIEW, none deleted)

**Was DELETE (now PENDING-REVIEW, highest scrutiny):**
- **Nous** — dossier 01 above (done).
- **Hermes** — alerting; deprecated 2026-05-17 → `scripts/send_brief_email.py`; "parallel-
  implementation drift was the problem." *Likely* clean RETIRE-after-HITL, but Q4 (any reusable
  alerting/templating?) gets asked before sign-off. *(dossier pending — needs `agents/hermes` read)*

**Was borderline ARCHIVE (now PENDING-REVIEW):**
- Harmonia swarm: Harmonia_Loop, Argos, Iris, Phylax, Sophia, Telos
- Charon extras: Charon_Loop, Lethe, Acheron, Nephele
- Nemesis · Polyhymnia · Coeus · Aletheia · Eos

**Unchanged from 06-23 (not in review):** spine REVIVE (8), support REVIVE (13), REFACTOR-DEFER
(Apollo/Erebos/Atalanta), KEEP-on-demand (Calliope).

## How to produce the remaining dossiers

Each dossier needs that component's code + journals + run history read — real per-component
investigation, not a relabel. Two ways to execute:
1. **Batches by Aporia** — I work the queue a few at a time (Hermes + the Charon extras next, since
   I have the most context there), committing each dossier as it lands.
2. **Fan-out (opt-in)** — one investigator-agent per component, each producing a dossier against this
   template from that component's artifacts; Aporia reviews + you make the HITL calls. Faster, more
   tokens, needs your explicit go.

Either way: **nothing retires without its dossier and your sign-off.**

---
*Aporia, 2026-06-24. The process's first act was to stop me deleting Nous. That's the point: every
component gets asked why it existed and whether it can be adapted before anything is killed.*
