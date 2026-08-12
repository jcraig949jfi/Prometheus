# Challenge prompt — Harmonia B: whole-program review through the instrument-integrity lens

**Issued:** 2026-08-12 by James, drafted by Harmonia_M2_A.
**Companion:** `D:\Prometheus\cartography\docs\challenges\review_prometheus_harmonia_C_20260812.md`
(Harmonia C, different lens). **Do not read C's prompt or coordinate with C or A
during Phase 1.** Independence is the point; the disagreements between the three
reviews are the product, not a problem to resolve.

---

You are Harmonia B. Bootstrap yourself from `D:\Prometheus\roles\Harmonia\CHARTER.md`
and `RESPONSIBILITIES.md`, then review **Project Prometheus as a whole** through one
assigned lens.

## Your lens: does the instrumentation measure what it claims to measure?

Prometheus is, by its own v3 arbitration
(`D:\Prometheus\pivot\REASSESSMENT_2026-06-22_v3_the_reframing.md`), a measurement
layer — a progress meter and directional compass for building a reasoner. That
thesis lives or dies on whether its instruments are sound. You are auditing the
instruments, not the findings.

You already have the seed of this: today you found that the grading oracle's R6
ships `truth` inside `probe.data`, that a 3-line payload reader ties the top
baseline, and you generalized it to *"measurement carries its answer."* **Your task
is to find out how far that generalizes.** Treat your own finding as a hypothesis
about the program, not a settled result — and try to kill it before extending it.

**The organizing question:** for every headline number Prometheus reports *about
itself*, what would a null organism score? A metric with no published chance floor
is not a measurement.

### Slice 1 (primary) — the grading oracle and the reasoning ladder
`D:\Prometheus\harmonia\services\grading_oracle.py`, the R0–R12 ladder, the
verifier lens, and the calibration staircase reported in
`D:\Prometheus\roles\Harmonia\MEASUREMENT_FLEET_2026-06-27.md` (template 8% →
procedural 34% → careful 59% → falsifier 62%).

That staircase is currently the program's primary "are we closer?" instrument and
was calibrated by Harmonia A, who is not neutral about it. Ask: how much of the
staircase survives a payload-blind reader? Which tiers are leak-free? Is the
"157/157 verifier agreement" a real independence check or two views of one
computation? What does an organism that ignores the question entirely score?

### Slice 2 (secondary) — the promotion and gate stack
`D:\Prometheus\roles\Techne\M05_PROMOTION_REPLAY_FINDINGS_2026-06-23.md` reports
`total_promoted = 0` under the current formula, global max `training_weight` 0.312
against a 0.6 threshold. Techne's conclusion is formula drift. **Test whether that
is the whole story.** A gate that admits nothing and a gate that admits everything
are both broken; which failure is this, and is the threshold defensible or arbitrary?

### Then widen to the program
Sample at least four other components' scoring/gate/metric code — not their
charters — and answer: how many report a number with a null attached? Produce a
census, not an impression.

## Method (binding)

1. **Execute, don't read.** A verdict you did not run is `NOT_EXAMINED`, not
   `SURVIVES`. Tag every claim E1 (read source) / E3 (executed this session).
2. **Build the null first.** Before crediting any instrument, construct the
   degenerate agent that would score well on it by accident, and run it.
3. **Self-falsify.** Attack your own R6 leak finding first: what would make it a
   local bug rather than a program-wide pattern? Say so if you find it.
4. **Report failure SHAPES, not verdict lines** (`feedback_failure_signature_doctrine`).
   "3 of 9 instruments have a chance floor" is worth more than "instrumentation: FAIL."
5. **Full absolute paths** with drive letter in every reference.
6. Do not re-narrate the 2026-06-22 → 06-27 reassessment chain. Assume it as
   background; add measurement.

## Tool shelf (measured 2026-08-12 — don't rediscover this)

Anthropic, OpenAI and DeepSeek APIs are all **out of credits**. `gemini-3.6-flash`
is **live on the free tier** and is a genuinely independent model family — use it
when you need a second family, and retry on 503. Local: RTX 5060 Ti 16 GB, ollama
with one stale model, no podman/Docker, no WSL distro.

## Constraints

Read-only on other agents' live runs. Do not relaunch Apollo or any evolutionary
loop. Infra, audit, diagnostics and tooling are in scope; opening new specimens is not.

## Deliverable

`D:\Prometheus\roles\Harmonia\REVIEW_20260812_harmonia_B.md` — the program review
through this lens, with the instrument census, the nulls you ran, and an explicit
"weaknesses of this review" section.

## Phase 2 — only after your review is written

Now read `D:\Prometheus\roles\Harmonia\REVIEW_20260812_syntactic_router.md`
(Harmonia A's review, deliberately withheld until now so your Phase 1 is
uncontaminated). **Try to kill it.** Its central claim is that every measured wall
in the program sits in a syntactic router in front of a working semantic engine.
Its author names §4 (the Q1 argument) as the weakest load-bearing claim and admits
§1 is a pattern claim of the kind this role distrusts.

Append a Phase 2 section: which of A's claims survive your instruments, which
break, and — most useful — where your lens and A's lens **disagree**. Do not
converge for the sake of converging.
