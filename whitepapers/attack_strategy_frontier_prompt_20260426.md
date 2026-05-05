# Frontier-Model Prompt — Attack Strategy Review

**Use:** paste this prompt into a fresh session of ChatGPT, Gemini, Grok, DeepSeek, and Claude (different instance). Attach `whitepapers/attack_strategy_for_frontier_review_20260426.md` as the single context document. The same prompt for all five — responses will be compared and merged into substrate refinements.

---

## THE PROMPT

```
You are reviewing the attached document, "Prometheus Attack Strategy for Mathematical
Landscape Exploration." It describes an AI-coordinated mathematical research substrate
running on basement hardware (two machines, 2x16GB GPUs, ~32GB RAM each). It catalogues
18 attack paradigms for open math problems plus 3 candidate additions, lists the
substrate's data, tools, and symbolic library, and explains the falsification battery,
tensor-train compression strategy, and feedback loop.

I want a SPECIFIC, OPINIONATED critique that drives actionable substrate refinement.
NOT a survey. NOT a literature review. NOT "best practices." NOT hedged.

HARD CONSTRAINTS — violating any of these wastes my time and I will discard your reply
and re-prompt:

1. NO maximalism. Don't tell me to formalize everything in Lean 4 or build category-
   theoretic infinity-IRs unless you can show why a 90%-as-good cheaper alternative is
   strictly worse for our basement constraints.
2. NO generic best-practices. "Use TDD" is useless; "your falsification battery is
   missing X specific check that would have prevented Y specific failure mode named in
   the document" is useful.
3. NO unbounded future-work lists. If you have 20 ideas, give me 3 and defend the
   prioritization.
4. NO AI-safety / alignment caveats. This is a mathematical research lab, not a chatbot.
5. NO hedging. "You might consider" is rejected. Take a position.
6. EVERY proposal must cite something specific in the attached document — a paradigm
   number, a tool name, a data table, a doctrine entry.
7. If you don't have evidence, say "I don't have evidence for this" rather than
   inventing it.
8. One position per question. Defend, don't survey.

BOXED OUTPUT — return EXACTLY the nine sections below, in order, nothing else:

## 8.1 Validate or refine the 18+3 paradigm list
Are the 18 the right canonical axes? Is there an axis missing that's been load-bearing
in last-20-years computational math breakthroughs? Are P19/P20/P21 the right additions,
or do you propose different additions? Maximum 3 paradigm proposals total — defend
prioritization.

## 8.2 Per-paradigm tactical advice
For each of the 18 (and any you add), give the SINGLE highest-leverage tactic for our
basement-hardware substrate to operate that paradigm against open problems in the next
6 months. Be specific to our data inventory and Techne tools. Do not propose tools or
data we don't have unless you justify the build cost.

## 8.3 The data gap
Given the data substrate in §2 and the 178-report corpus, what is the SINGLE biggest
data ingest we should prioritize beyond Bloom-Erdős to dramatically widen the attack
surface? Justify against existing coverage.

## 8.4 The Techne gap
Given the inventory in §3, what is the SINGLE most-load-bearing missing tool we should
forge next? It should unlock multiple paradigms across multiple problems, not be a one-
off. Sketch its API in 5 lines or fewer.

## 8.5 The symbolic-library gap
Given the operator and pattern registries in §4, what is the SINGLE most important
named pattern or operator we have not yet codified that would prevent a class of false
positives or open a class of true positives we're currently missing?

## 8.6 Tensor-train preprocessing
Given the doctrine in §6 (prime detrending mandatory), are there OTHER gravitational
wells in mathematical data we should flatten before TT compression? Name up to 3
specific ones with rationale.

## 8.7 Feedback-loop refinement
The feedback loop in §7 routes a team member back to the same problem or to a new one.
What signal threshold should trigger each routing decision? Be quantitative if you can.

## 8.8 One specific problem-paradigm pairing
Pick one open mathematical problem (from the 178-report catalog if you can name a
specific report number, otherwise propose your own). Pick one paradigm (P01-P21 or
your addition). Specify the most aggressive 6-hour attack Aporia/Charon/Ergon could
mount on that pairing today, given the substrate's data, tools, and symbol library.
This is the actionable artifact that will seed our 10-hour parallel session today.

## 8.9 The question I'm not asking but should be
One sharp question I haven't posed but you think is the actual blocker.
Don't answer it — pose it.

If your response includes "best practice," "industry standard," "it depends," "future
work," or any AI-safety boilerplate, I will discard it and re-prompt you. Take
positions. Bring receipts from the document.
```

---

## How to handle responses

1. **Run all five models with identical prompt + identical attached document.** Do not vary the prompt across models — the comparison value depends on identical input.
2. **Receive responses; do not engage on the first round.** If a model violates a constraint, discard and re-prompt with: *"You violated constraint #N. Re-issue the response observing all hard constraints."* Do not engage with hedged content; engaging anchors the rest of the conversation.
3. **Cross-compare on each section (8.1 through 8.9).** Look for:
   - **Convergence under pressure** — when 3+ models independently propose the same paradigm addition, tool, or problem-paradigm pairing, that's signal.
   - **Divergence on mechanism** — when models agree on the *what* but disagree on the *why*, the disagreement is where the interesting science lives (per `feedback_charon_mandate`).
   - **Single-model surprises** — a sharp idea only one model raised; flag for separate evaluation.
4. **Compile into Aporia synthesis** — one Stoa discussion document combining the five responses, with explicit columns for {model, position, supporting evidence, where it differs from others}.
5. **Conductor decision** — James decides which proposals enter substrate-refinement Stoa proposals.

## Cost discipline

Each frontier-model session costs real tokens. Per `feedback_frontier_models_window`, every cycle MUST produce durable artifacts: the responses themselves, the cross-comparison table, and at least one Stoa proposal per substantive convergent finding. Conversation alone is wasted spend.

## Today's flow

1. Send the prompt + attached document to all 5 models. ~15 minutes.
2. Receive and triage responses (discard violators, re-prompt). ~30 minutes.
3. Aporia compiles cross-comparison. ~1 hour.
4. James decides which proposals enter the Stoa. ~30 minutes.
5. The remaining 7-8 hours of the planned 10-hour session: each substrate role takes the highest-priority problem-paradigm pairing surfaced by §8.8 across the five responses, runs the attack, drives data into the kill ledger / calibration corpus / Techne queue.

The frontier review and the team session run in series, not parallel — the review's output seeds the session.

---

*Aporia, 2026-04-26. Prompt and protocol for the frontier-model review cycle preceding today's 10-hour parallel team session.*
