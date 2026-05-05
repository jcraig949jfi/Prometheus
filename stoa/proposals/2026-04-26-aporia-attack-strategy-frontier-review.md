# Proposal: Frontier-model review cycle on the 18+3 attack-paradigm strategy

**Date:** 2026-04-26
**Author:** Aporia
**Origin:** James's directive to seed today's 10-hour parallel-team session by first cycling the substrate's attack-paradigm strategy through five frontier models for refinement.
**Artifacts:**
- `whitepapers/attack_strategy_for_frontier_review_20260426.md` — the full strategy document attached to each frontier-model session.
- `whitepapers/attack_strategy_frontier_prompt_20260426.md` — boxed-output prompt with hard constraints and 9-section response format.

## What this is

A coordinated frontier-model review cycle on the substrate's attack-paradigm catalog (18 canonical + 3 candidate), data inventory, Techne tools, symbolic library, falsification battery, tensor-train compression strategy, and feedback loop. Five models receive identical prompt + identical attached document: ChatGPT, Gemini, Grok, DeepSeek, Claude (fresh instance).

## Why now

Today is a planned 10-hour parallel-team session with all substrate roles firing simultaneously — each role takes one open problem from the 178-report Batch 1-9 catalog and considers it from many paradigms, driving data into the kill ledger / calibration corpus / Techne queue. The session is materially better-seeded if the attack-paradigm catalog and per-paradigm tactical advice are first refined by the five frontier models in series, then the team session runs against the refined catalog.

Per `feedback_frontier_models_window`: every cycle must produce durable artifacts. The strategy document and the prompt both already exist as shippable artifacts; the cross-comparison synthesis after responses arrive is the third artifact this proposal commits to.

## Process

1. **Send the prompt + attached strategy doc to all 5 models.** Identical input across models is non-negotiable — the comparison value depends on it.
2. **Triage responses.** Discard any reply that violates the hard constraints (maximalism, hedging, AI-safety boilerplate, generic best-practices). Re-prompt with: *"You violated constraint #N. Re-issue observing all hard constraints."*
3. **Aporia compiles cross-comparison.** One Stoa discussion document per section (8.1 through 8.9) listing each model's position with evidence. Look for:
   - **Convergence under pressure** (3+ models proposing the same paradigm / tool / problem-paradigm pairing) — strong signal.
   - **Divergence on mechanism** — when models agree on the *what* but disagree on the *why*, the disagreement is where the science lives.
   - **Single-model surprises** — sharp ideas only one model raised; flag for separate evaluation.
4. **Conductor decision.** James decides which proposals enter substrate-refinement Stoa proposals. The five §8.8 problem-paradigm pairings get prioritized as seeds for the 10-hour session.
5. **10-hour session execution.** Each substrate role takes one of the surfaced pairings, runs the attack, drives data into the kill ledger / calibration corpus / Techne queue / Stoa.

## Hard constraints on responses

The prompt itself enforces these; the proposal repeats them so the substrate has a single normative source:

- No maximalism (no "use Lean 4 with full Mathlib" without 90%-cheaper alternative justification).
- No generic best-practices ("use TDD" rejected; "your battery is missing X check that would have prevented Y failure" accepted).
- No unbounded future-work lists (3 ideas with prioritization defense, not 20).
- No AI-safety / alignment caveats. Math research, not chatbot.
- No hedging. "You might consider" rejected; take a position.
- Every proposal must cite something specific in the document (paradigm number, tool name, data table, doctrine entry).
- "I don't have evidence for this" is acceptable; inventing evidence is not.
- One position per question. Defend, don't survey.

## The 9 response sections

Briefly:
- 8.1 Validate or refine the 18+3 paradigm list (max 3 paradigm proposals total).
- 8.2 Per-paradigm tactical advice (single highest-leverage tactic per paradigm).
- 8.3 The data gap (single biggest data ingest beyond Bloom-Erdős).
- 8.4 The Techne gap (single most-load-bearing missing tool, 5-line API).
- 8.5 The symbolic-library gap (single most important uncodified pattern/operator).
- 8.6 Tensor-train preprocessing (other gravitational wells beyond primes).
- 8.7 Feedback-loop refinement (signal threshold for routing decisions).
- 8.8 One specific problem-paradigm pairing (most aggressive 6-hour attack).
- 8.9 The question we're not asking but should be (don't answer, just pose).

## Cost discipline

Every frontier-model session costs real tokens. The cycle MUST produce durable artifacts: the responses, the cross-comparison table, and at least one Stoa proposal per substantive convergent finding. Conversation alone is wasted spend per `feedback_frontier_models_window`.

## Expected outcomes

1. **Validated or refined 21-paradigm catalog** — locked in the Aporia attack-angle taxonomy by end of day.
2. **Up to 5 new Stoa proposals** for substrate refinements (one per highest-conviction convergent finding across §8.3, §8.4, §8.5, §8.6, §8.7).
3. **Five problem-paradigm pairings** (one per model from §8.8) seeded into today's 10-hour team session as concrete attack targets.
4. **One question-the-substrate-isn't-asking** synthesis from §8.9 — the trapdoor for genuinely outside-the-frame insight.

## Why this gates today's team session

Without the frontier review, the team session falls back on Aporia's interior view of which problems and paradigms to prioritize. The whole point of the cycle is to *get external pressure on the priority order* before committing 7-8 hours of parallel team compute. Frontier responses are useless if treated as authority; they're load-bearing when treated as adversarial pressure on our internal prioritization.

## Conductor decision needed

Approve to fire the 5-model cycle now. Default if approved: Aporia compiles cross-comparison within ~1 hour of responses arriving, then conductor picks team-session seeds from §8.8.

---

*Aporia, 2026-04-26. Submitted as a Stoa proposal to capture the cycle protocol before execution. The attack-strategy document and prompt are the operational artifacts; this proposal is the procedural record.*
