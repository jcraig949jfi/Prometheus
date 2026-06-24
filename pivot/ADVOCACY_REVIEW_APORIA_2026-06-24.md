# Owning-Agent Advocacy Review — Aporia components — 2026-06-24

**Owning agent / advocate:** Aporia (Claude Opus 4.8) · **Decider:** James.
**Model (James, 2026-06-24):** the *owning agent* reviews what it built, with an intentional bias
toward preservation, and advocates a path forward. If the advocate convinces James there is a valuable
path, the component gets **another month of life to demonstrate value** against a falsifiable target.
If marginal, the question is *what would make it valuable.* This is the **counterweight** to the
adversarial fan-out dossiers (`pivot/COMPONENT_DOSSIERS_2026-06-24.md`): prosecution vs defense, James
judges. Nothing here is approved.

> **Honest-advocate stance.** Preservation bias is by design, but an advocate who fights equally for
> everything is useless. I argue **STRONG-KEEP** for 2, **KEEP-IF-REFACTORED** for 1, and
> **CONCEDE-WITH-SALVAGE** for 2 — so that when I say "keep," it means something. Each keeper carries a
> falsifiable 30-day demo (by **2026-07-24**) with a named consumer and a kill condition.

## The advocacy ledger template (reusable by any owning agent)

```
### <Component> — <STRONG-KEEP | KEEP-IF-REFACTORED | CONCEDE-WITH-SALVAGE>
Prosecution (fan-out verdict): <the adversarial call + its core charge>
The case (how it enriches Prometheus): <concrete program value, not hype>
Honest current state: <engage the charge — what's true, what's broken>
Improvement path: <specific changes that make it valuable>
30-day demo (by DATE): <falsifiable success criterion + NAMED consumer>
Kill condition: <what failure at month-end looks like -> retire>
Salvage IP (if it retires): <specific reusable assets>
Advocate's verdict: <one line>
```

The demo must name a **consumer** and a **measurable delta**, not "more time." The kill condition is
pre-committed so the month is a real test, not a reprieve.

---

## STRONG-KEEP

### Pythia (Deep Research dispatcher) — STRONG-KEEP
**Prosecution:** REFACTOR — producer healthy, 442 reports, but the consumption loop was never closed;
55/55 audited reports have `actual_delta:null`; idle 24 days.
**The case.** Pythia converts the **use-or-lose** Gemini Deep Research budget (20 tokens/day) into
substrate. Every day it's dark, that budget *pumpkins* — pure waste at near-zero marginal cost to run.
The prosecution's own finding is the advocacy: *the producer is healthy; only the consumer is missing.*
That's a wiring job, not a redesign. And it already sits on a **442-report corpus** that is directly
mineable as anti-anchor / calibration-anchor candidates for the Learner — latent value already paid for.
**Honest current state.** The dispatch contract (named consumer + expected delta) was *specced and never
wired*; `pythia_notify_requesters.py` / `dr_inbox/` don't exist; the yield audit is an empty skeleton.
Real, and all on the *consumption* side.
**Improvement path.** (1) Wire the existing `pythia_dispatch_contract_schema.md` into `dispatch_one()` —
refuse any dispatch that doesn't name a consumer + a falsifiable `expected_delta`. (2) Point Pythia
*exclusively* at the spine: dispatch only false-anchor / retraction-pattern prompts whose reports feed
the Hephaestus→Learner kill-geometry / anti-anchor corpus. (3) Mine the existing 442 reports as a one-shot
anti-anchor harvest while the loop rewires.
**30-day demo (by 2026-07-24):** ≥10% of dispatched reports record a concrete `actual_delta` (a kill-ledger
entry, an anchor demotion, or a Learner-corpus row) attributable to a **named consumer**, AND the 442-report
back-corpus yields ≥5 verified anti-anchor candidates that reach `techne/registry/anti_anchors.jsonl`.
**Kill condition:** after 30 days `actual_delta` stays ~0/N (matching today's 0/55) → the producer is
decorative; retire the auto-dispatch cadence and rotate the token budget elsewhere.
**Salvage IP:** 442-report corpus; the dispatch-contract schema (reusable by *any* producer); the
throttle/backoff/timeout logic; the `agora.research_queue` schema; 370-entry tier-sorted seed queue.
**Verdict:** the cheapest keeper in the program — wasted free tokens + a healthy producer one wiring job
away from a consumer. Fight for it.

### Clio (literature inflow / paper scanner) — STRONG-KEEP (narrower)
**Prosecution:** REFACTOR — pipeline dead-ends (`sigma_claims.db` = 0 symbols), claim-space exhaust,
daemon dead since 05-30.
**The case.** Clio is the substrate's **standing inflow from the frontier** — and its uniquely valuable
slice is *falsification-signal* papers: withdrawals, counterexamples, errata. Those are **not** claim-space
exhaust — they are exactly the anti-anchor residue the program prizes (the Saxl/Lee-withdrawal pattern that
the anti-anchor verification cycle exists to catch). A standing watcher for "what the literature just
*un-proved*" is a real, unique enrichment.
**Honest current state.** The code is healthy (87 tests pass, fail-soft, MemoryError-hardened), but the
Sigma promotion path it feeds is *vacuous* (no `sigma` schema), so generic claim-mining dead-ends. The
prosecution is right that *generic* paper-claim mining is exhaust.
**Improvement path.** Drop the vacuous sigma path. (1) Refactor Clio to surface **falsification-signal**
papers into the Learner negative-corpus / anti-anchor pipeline. (2) **Pheme-gate** the query menu — mine
the literature the forge is currently *failing* on, turning generic generation into targeted residue-hunting.
**30-day demo (by 2026-07-24):** ≥1 Clio-sourced falsification-signal item (withdrawal/counterexample)
becomes a verified anti-anchor OR produces a Learner behavior delta that survives an ablation.
**Kill condition:** zero Clio-sourced items consumed by the spine in the cycle → confirmed exhaust; fold the
mining tier into a single standby (Nephele) and archive.
**Salvage IP:** 13-query paradigm-mapped taxonomy; arxiv Atom parser + polite fetcher; MemoryError-tolerant
dedup index; the kill-path templates encoding "a theorem is not killed by a counterexample"; 181-paper corpus.
**Verdict:** keep — but only the falsification-signal + Pheme-gated refactor; the generic version is exhaust.

## KEEP-IF-REFACTORED

### Hypatia (D-track reasoning-ladder curator) — KEEP-IF-REFACTORED
**Prosecution:** RETIRE — *fatal* catalog/task mismatch (backlog is 532/537 **open conjectures** but the
prompt asks to decompose **proofs**; the model confabulated a ladder for a different theorem). Consumer dir
never built; output JSONL malformed.
**The case.** The **R1–R5 reasoning ladder** is genuinely load-bearing IP — it's substrate type D, the
Learner curriculum's *difficulty axis*, and it ties directly to the capability-space transfer eval (R3 "THE
WALL" / M0). The ladder taxonomy is worth keeping regardless of Hypatia's fate.
**Honest current state.** As-built, Hypatia is broken in a structural way, not a tuning way — you cannot
decompose proofs of unproven conjectures, so it confabulates, which would *poison* a Learner corpus. The
prosecution's RETIRE is correct *for the loop as built.* I do not contest it.
**Improvement path (the re-aim that rescues it).** Stop generating fresh claim-space. **Re-aim Hypatia at
the spine's own kill-geometry:** decompose the Learner's *survived and killed proof attempts* into R1–R5
ladders. That is capability-attached (residue, not exhaust), dodges the open-conjecture confabulation
entirely, and feeds the decider directly. (Plus: fix the JSONL cite-leak; build the ingester.)
**30-day demo (by 2026-07-24):** a Learner trained with R1–R5 ladders derived from its *own* attempt-traces
beats the same Learner without them on a held-out transfer slice, surviving an ablation.
**Kill condition:** ladders remain confabulated/unparseable OR no ablation-surviving delta → RETIRE the loop,
lift the ladder taxonomy.
**Salvage IP:** the R1–R5 taxonomy; the well-built low-cadence daemon scaffold (lock/state/anti-silence);
8 genuine literature surveys.
**Verdict:** retire the loop-as-built, but the ladder is too valuable to lose — fund the kill-geometry re-aim,
not a revive-as-is.

## CONCEDE-WITH-SALVAGE

### Atalanta (E-track primitive hunter) — CONCEDE-WITH-SALVAGE
**Prosecution:** RETIRE — dead-gated; 354/354 ticks `UPSTREAM_NOT_FOUND` (hardcoded Apollo paths that never
existed); gated on Apollo, which is itself deferred.
**Honest concession.** I will not special-plead this one. Atalanta's entire purpose is mining Apollo's
evolved organisms for substrate-E primitives — and Apollo is deferred (R8 organism collapsed). There is
*nothing to hunt* until Apollo produces a validated organism stream. An independent month-of-life case would
be theater. **Archive read-only, revive only when Apollo does** — and even then, fix the upstream paths and
automate the (currently manual) Techne ingestion arm first.
**Salvage IP:** the `aggregate_primitive_signals` composite-mining algorithm; the evidence-anchored Type-E
DR template (anti-gravity guard: every candidate must cite real organism IDs); the schema-tolerant Apollo-log
parser. Lift these into whatever eventually consumes Apollo organisms.
**Verdict:** concede — couple its fate to Apollo's; don't keep it breathing in a vacuum.

### Polyhymnia (named-operator scour) — CONCEDE-WITH-SALVAGE (redirect)
**Prosecution:** RETIRE — bounded-menu wall: 1 of 17 scours ever shipped, 84% null, self-improver is 5/6
no-op logging stubs.
**Honest concession + redirect.** This is the **gen-30 wall** the program knows by heart (`feedback_gen_30_wall`):
the fix is *never* a deeper menu for one agent. Reviving Polyhymnia-as-is is the exact anti-pattern, so I
won't advocate it. BUT — Polyhymnia is the *explicitly designated chassis* for **Arachne**, the population of
crawlers that branch/die/diversify (the doctrinally-correct menu-growth answer, per
`math_crawlers_epiphany_2026-06-04`). The value isn't the agent; it's the **chassis + the 2,415 tesserae +
the self-improving-daemon pattern** as Arachne's seed.
**Improvement path:** lift the scour chassis (`scours/_base.py`, `tensor.py`), the tesserae corpus, and the
SelfImprovingDaemon adoption pattern (minus the 5 stub adaptations) into Arachne; retire the single-agent loop.
**Salvage IP:** scour interface + sparse content-addressed tensor; 2,415 deduped tesserae + 8 axis registries
(open-vocabulary taxonomy seed); the self-improving-daemon template; the unshipped game/lens designs.
**Verdict:** concede the single agent; advocate the **chassis-into-Arachne** path as the real future.

---

## Summary for James

| Component | Fan-out (prosecution) | Aporia (defense) | The ask |
|---|---|---|---|
| Pythia | REFACTOR | **STRONG-KEEP** | wire the consumer; 30-day actual_delta ≥10% demo |
| Clio | REFACTOR | **STRONG-KEEP** (narrow) | falsification-signal + Pheme-gated refactor |
| Hypatia | RETIRE | **KEEP-IF-REFACTORED** | re-aim at kill-geometry; retire the loop-as-built |
| Atalanta | RETIRE | **CONCEDE** | couple to Apollo; lift IP |
| Polyhymnia | RETIRE | **CONCEDE (redirect)** | lift chassis into Arachne |

**Where these enrich Prometheus, in one breath:** Pythia turns free, expiring external compute into
anti-anchor/calibration substrate; Clio is the standing watcher for what the literature just *un-proved*
(the anti-anchor residue stream); Hypatia's R1–R5 ladder is the Learner's difficulty axis and the
capability-eval rung; Atalanta and Polyhymnia are IP donors to Apollo-consumption and Arachne respectively.

**My honest bottom line:** two of the five (Pythia, Clio) deserve a real month with a falsifiable target,
and the demos are cheap (wiring, not invention). Hypatia deserves a month *only* if re-aimed at the spine —
the loop-as-built should retire. The last two I concede; their value is salvage, not a heartbeat. If you
greenlight, I'll wire the Pythia consumer first (highest value, lowest cost, and it stops wasting the daily
token budget today).

---
*Aporia, 2026-06-24. Defense to the fan-out's prosecution. Nothing approved; each keeper carries a
pre-committed kill condition so the month is a test, not a reprieve.*
