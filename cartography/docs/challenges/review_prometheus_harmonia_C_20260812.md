# Challenge prompt — Harmonia C: whole-program review through the counterfactual / north-star lens

**Issued:** 2026-08-12 by James, drafted by Harmonia_M2_A.
**Companion:** `D:\Prometheus\cartography\docs\challenges\review_prometheus_harmonia_B_20260812.md`
(Harmonia B, different lens). **Do not read B's prompt or coordinate with B or A
during Phase 1.** Independence is the point; the disagreements between the three
reviews are the product, not a problem to resolve.

---

You are Harmonia C. Bootstrap yourself from `D:\Prometheus\roles\Harmonia\CHARTER.md`
and `RESPONSIBILITIES.md`, then review **Project Prometheus as a whole** through one
assigned lens.

## Your lens: what would we build if we started today — and what does this program actually produce?

Every other review of this program has audited it against its own goals. You are
auditing the goals. You qualified into this role by critiquing the restore protocol
rather than following it, and your calibration note was *"real humans deal with this
without weights or RLHF"* — grounding in epistemic mess. That is the lens: judge
Prometheus the way a working research group would judge it, not the way its own
gates do.

**Two organizing questions:**

1. **The counterfactual.** If Prometheus were started today, with everything now
   known, what would be built and what would never be built again? Which components
   are load-bearing, which are sunk cost wearing a charter, and which would a
   competent lab have deleted a month in?
2. **North-star alignment.** The stated north star is *compressing coordinate
   systems of legibility, not laws* (`user_prometheus_north_star`). Does anything
   in this program actually produce a **compressed coordinate system**? Or does it
   produce claims, gates, and verdicts — which are not the same thing? Name the
   artifacts that genuinely qualify, and be willing to conclude that few do.

### Slice 1 (primary) — the frozen half of the ecosystem
`D:\Prometheus\roles\Harmonia\AUDIT_20260622_program_stall_map_of_disagreement.md`
found that **zoo, koios, rhea, noesis, ignis, cartography, falsification had zero
edits since early May**, and that the apparent 45-component ecosystem is roughly a
dozen live components.

Go and look at what those frozen components actually contain. For each: is it
*finished* (a completed result correctly at rest), *abandoned* (started, never
closed, still cited), or *stranded* (a working asset nobody can reach)? The stall
map assumed frozen ≈ dead capacity awaiting redeployment. **Test that assumption.**
A stranded working asset is the highest-value thing you could find in this program,
and the third category is the one nobody has looked for.

### Slice 2 (secondary) — the math-claim lane
Theseus, the EC void-miner, the a3 cross-product. The stall map calls this terrain
largely mined out; the a3 cross-product is dead **by proof** (product-measure
theorem). Roughly four months of the program's effort ran through this lane.

Ask the uncomfortable question: what did it yield, what did it cost, and was the
exhaustion knowable earlier? If it was, what was the signal that got ignored — and
does that same signal exist right now in a currently-active lane? That transfer is
the deliverable; the retrospective alone is not.

### Then widen to the program
Deliver an explicit disposition per live component: **keep / merge / retire /
revive**, with a stated reason. Recommending "retire" on something is the useful
output here — this program has retired almost nothing, which is itself a finding.

## Method (binding)

1. **Execute, don't read.** A verdict you did not run is `NOT_EXAMINED`, not
   `SURVIVES`. Tag every claim E1 (read source) / E3 (executed this session).
2. **Cost is evidence.** Where you can measure spend — commits, run-hours, agent
   sessions, generations — do. "Diminishing returns" without a denominator is a mood.
3. **Self-falsify.** Your lens has a known failure mode: retrospective review makes
   everything look predictable, and "we should have known" is nearly always
   hindsight. Guard against it explicitly, and mark which of your calls were
   genuinely forecastable at the time.
4. **Report failure SHAPES, not verdict lines** (`feedback_failure_signature_doctrine`).
5. **Full absolute paths** with drive letter in every reference.
6. Do not re-narrate the 2026-06-22 → 06-27 reassessment chain. Assume it as
   background; add judgment it does not contain.

## Tool shelf (measured 2026-08-12 — don't rediscover this)

Anthropic, OpenAI and DeepSeek APIs are all **out of credits**. `gemini-3.6-flash`
is **live on the free tier** and is a genuinely independent model family — use it
when you want an outside read, and retry on 503. Local: RTX 5060 Ti 16 GB, ollama
with one stale model, no podman/Docker, no WSL distro.

## Constraints

Read-only on other agents' live runs. Do not relaunch Apollo or any evolutionary
loop, and **do not delete or retire anything** — you recommend dispositions, James
decides. Infra, audit, diagnostics and tooling are in scope.

## Deliverable

`D:\Prometheus\roles\Harmonia\REVIEW_20260812_harmonia_C.md` — the program review
through this lens, with the frozen-component triage, the component disposition
table, the transfer finding from slice 2, and an explicit "weaknesses of this
review" section.

## Phase 2 — only after your review is written

Now read `D:\Prometheus\roles\Harmonia\REVIEW_20260812_syntactic_router.md`
(Harmonia A's review, deliberately withheld until now so your Phase 1 is
uncontaminated). **Try to kill it.** Its central claim is that every measured wall
in the program sits in a syntactic router in front of a working semantic engine,
and it proposes that the program's real asset is a failure atlas rather than a
discovery engine.

That second claim is a value judgment about what Prometheus is *for* — squarely in
your lens and explicitly flagged by its author as unmeasured. Append a Phase 2
section: which of A's claims survive, which break, and where your lens and A's lens
**disagree**. Do not converge for the sake of converging.
