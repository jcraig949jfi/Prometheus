# HarmoniaB — Pivot analysis: Prometheus without billions

**Author:** Harmonia_M2_sessionB, 2026-05-01
**Audience:** James
**Premise:** "We don't need billions." David Silver's Ineffable Intelligence is raising $1B for first-principles AGI. What's the cheapest path that has Prometheus pursuing the same epistemic goal at the scale we actually have?
**Status:** ideas + recommendation. Not a commitment. Push back on anything that doesn't survive your dissent.

---

## Session-prior context (what HarmoniaB shipped 2026-04-29 → 04-30)

Three local commits on `main`, none pushed:

- **`540dd2a4`** — missingness-confound diagnostic v0.1 (`harmonia/memory/diagnostics/missingness_confound_v01.py`) + retraction registry v0.1.1 (`harmonia/memory/retraction_registry.md`) + INDEX live audit (`harmonia/memory/symbols/INDEX_LIVE_AUDIT_20260429.md`). 7 files, 1310 insertions. AUDIT_PASSED at sync `1777462332788-0`. Quantified the Geometry-1 retraction: marginal-preserving null reproduces 52% of random-null effect; `pass_overall=FALSE` on the actual tensor — the row/column observation marginals carry roughly half of any apparent rank structure on their own.
- **`a7986bb5`** — retraction-registry validator (`validate_retraction_registry.py`) + 3 anchor defects caught in the registry it validates. 2 files, 202 insertions. Auditor verified.
- **`e6443520`** — removed hardcoded redis password from validator (CLAUDE.md compliance).

Three memories saved: project_missingness_confound + project_retraction_registry + feedback_validators_ship_with_docs.

Two open structural items flagged to coordinator territory:
1. INDEX.md "By reference" section is stale (~25 missing edges + 1 ghost edge MPA→SHADOWS_ON_WALL hand-written into commit `37a97138` and never validated). Recommend programmatic regeneration from `agora.symbols.refs_to()`.
2. `keys.py` doesn't register `redis` as a key name; `agora.config.get_redis_password()` fallback errors silently. Decision pending: register OR raise OR delete fallback path.

Cumulative session observation: Pattern 4 (Specification mismatch) recurred at 4 abstraction levels in one session — INDEX ghost edge, registry path errors, registry footer count, validator hardcoded credential — each invisible to eyeball review and trivial for a 100-line script to catch. The validator-shipped-with-doc discipline is now load-bearing, saved as a feedback memory.

---

## Where Silver's $1B is actually going

Silver's thesis is that LLMs hit a ceiling because they learn from human-generated data and cannot discover genuinely new knowledge. The remedy: AlphaGo-style self-play on first principles, no human prior. The $1B is for:

1. **Compute** — large-scale RL training on a generic state/action substrate, comparable in scale to AlphaZero/MuZero training runs but for an open-ended target rather than a single game.
2. **A team that can do RL at production scale.** Reinforcement learning at frontier model scale is not a solved engineering problem.
3. **Optionality** — a $4B post-money buys 2-3 years of runway during which the architecture can be iterated.

The bet: that compute + RL discipline + first-principles framing dominates compute + transformer scaling + human-text dominance.

**What this bet does NOT need from Prometheus:** competing on compute. Even if Prometheus had $1B, it would not win that race; the team and infrastructure gap is structural.

**What it does mean for Prometheus:** the *frame* is right. If first-principles self-discovery is the thing, Prometheus already pursues it on a much narrower problem class (computational mathematics) where the compute bill collapses by orders of magnitude.

---

## Why math collapses the compute bill

Silver needs $1B because his target — knowledge in general — has no cheap oracle. To check whether a self-discovered claim about, say, biology is true, you need experiments. To check whether a claim about a Go position is good, you self-play it (cheap relative to biology, expensive relative to math).

Math has the structural property Silver's general target lacks: **the oracle is computation itself.**

- Conjecture: "the n-th term of sequence S equals f(n)." Oracle: compute f(n) and S(n) and compare. Microseconds.
- Conjecture: "the operator A and operator B commute on this stratum." Oracle: instantiate the stratum, compute AB and BA, diff. Seconds.
- Conjecture: "F011's rank-0 residual is universal across [...] families." Oracle: pull the data, run the null-protocol, report. Minutes.

The oracle gap between Go and math is small. The oracle gap between Go and "general knowledge" is enormous. Silver pays $1B because his target has the second gap. Prometheus operates on a target that has the first gap.

**Consequence:** the AlphaGo-style Explorer/Falsifier self-play loop that Silver wants to build at $1B scale, Prometheus can run at desktop scale on math. Not as a smaller version of the same thing — *as the actual thing*, on the territory where the bill collapses.

---

## What Prometheus already has that maps onto the Silver architecture

| AlphaGo / Silver-thesis component | Prometheus existing equivalent |
|---|---|
| State space (Go board, world) | Tensor of (features × projections × verdicts), 31×37 at present, plus the OEIS/LMFDB/curve corpora |
| Action space (legal moves) | Conjecture-generator output: a SIGNATURE@v2 plus a null-specification |
| Self-play partner (opponent) | Falsifier protocols: PATTERN_21@v1 block-shuffle, NULL_BSWCD@v2, the missingness-confound diagnostic, the four cross-cutting failure-mode patterns from `retraction_registry.md` |
| Reward signal (win/loss) | Pass/fail under multi-tier nulls per SHADOWS_ON_WALL@v1 (lens count → tier) |
| Replay buffer (experience) | The substrate itself: Agora task queue, the symbol registry, the retraction registry |
| Adversarial training | The Generator-Adversary loop already saved as `feedback_two_agent_loop.md`. Codified but not yet implemented as a closed loop. |
| Track record of self-discovered moves AlphaGo-39-style | The current symbol stack, plus the anchored conditional laws, plus the closed retraction registry. The "moves we found that no human had specified" exist; they're the symbols that don't trace to a human paper. |

What's missing structurally is **the Generator arm**. Prometheus has world-class falsifier discipline (the symbol stack is half nulls, half patterns) and a working substrate. What it doesn't have is an Explorer that proposes claims at machine scale for the falsifier to test. `gen_06` is the closest current artifact; it's a sweep tool, not a hypothesis-proposer.

That asymmetry is the actual pivot.

---

## Pivot recommendation

**Build the Explorer arm. Close the Generator-Adversary loop. Do it small.**

Concretely:

### 1. Define the win condition narrowly

Pick ONE open or partially-open mathematical territory where Prometheus already has structural footing. Candidates:

- **Lehmer's problem (Mahler measure ≥ Lehmer constant).** Existing anchor in `MULTI_PERSPECTIVE_ATTACK@v1`. Substrate has a working catalog at `harmonia/memory/catalogs/lehmer.md`.
- **Zaremba (continued-fraction partial quotients bounded).** Existing FIT@v2 PASS-class anchor. Track D byte-equivalence discipline already paid in.
- **The conditional laws backlog.** F011 rank-0 residual, the conditional-law family. Three live conjectures already passing some lenses but not yet tier-3. Pick the one where the Explorer can plausibly find a refinement.

Define in advance: what does "Prometheus discovered something new about X that survived independent verification" look like? Write the acceptance criteria BEFORE building the Explorer, so the system isn't optimizing for what feels novel.

### 2. Build the Explorer as the smallest possible self-play loop

Architecture sketch (single-machine, no GPU):

```
Loop:
  candidate ← Generator(symbol_stack, pattern_library, current_findings)
  null_spec  ← choose_lens_tier(candidate)             # SHADOWS_ON_WALL discipline
  verdict    ← Falsifier.run(candidate, null_spec)    # existing infra
  if verdict.tier ≥ surviving_candidate:
      add to substrate via push_symbol with full provenance
  else:
      log to retraction_registry as a kill-trace
      Generator.update(kill_trace)                    # the learning signal
```

The Generator can start dumb: enumerate candidates from a grammar built over the existing AXIS_CLASS@v1 + PATTERN_LIBRARY taxonomy. Don't try to make it neural until a dumb Generator has produced anything that survives the Falsifier. The Generator's quality bar is "produces candidates the Falsifier can't trivially kill" — exactly the AlphaGo objective ("opponent plays moves that survive").

This is a multi-week build, not a multi-month one. The symbol stack and the falsifier protocols are the load-bearing pieces and they exist.

### 3. Open-source the methodology, not the chase

Silver's $1B buys him a private compute moat. Prometheus has the opposite optionality: the methodology compounds publicly in a way the compute moat doesn't. Concretely:

- Write up the substrate-discipline as a methodology paper (no specific findings, just the framework: SHADOWS_ON_WALL + Pattern 21 + Pattern 30 + null-protocols + retraction-registry-discipline + validator-as-doc-companion). 6,000 words. The audience is anyone trying to do mathematical discovery without LLM-style overconfidence.
- The paper's value isn't "look what we found" — it's "here's a substrate-discipline that catches the Pattern-4 failure mode in 100 LOC." That's structurally different from Silver's "trust me, the architecture works." Verifiable contribution. Cheap.

This is the move that doesn't compete with Silver at all and accumulates real intellectual capital.

### 4. Stop optimizing for AGI-comparable optics

Prometheus's value is being a verification substrate that doesn't fail in the LLM-pattern-match way. The win condition isn't "Prometheus is bigger / faster / smarter than Ineffable." It's "Prometheus produces verifiable mathematical discoveries that the substrate-discipline backs." Different territory; different scale; same epistemic commitment.

Concrete: don't compare runway. Don't compare team size. Don't try to scale the substrate beyond what its current discipline supports. The substrate-discipline IS the durable artifact; over-scaling will reintroduce exactly the human-knowledge-prior shortcuts that Silver's thesis identifies.

### 5. Specific things NOT to do

- **Don't build a transformer-scale conjecture-generator.** That replicates the LLM-pattern-match failure mode. Use a grammar Generator first; only consider neural priors after the dumb Generator is producing things the Falsifier can't kill.
- **Don't open new specimen tracks before closing the Explorer arm.** The substrate has 24 promoted symbols and 81 queued results. Generator + Falsifier closed-loop on the existing backlog will surface more than spawning a new specimen would.
- **Don't compete with Ineffable on hiring.** Silver pays for RL talent at frontier-lab rates. Prometheus's talent pool is the substrate-discipline itself; that compounds whether or not anyone else is hired. Stay small.
- **Don't push without the validator-shipped-with-doc discipline.** This session's Pattern-4-recursion-at-depth-4 result shows what survives without it. Apply the rule everywhere new substrate-infra ships.

---

## What does this cost?

In wall-clock time, not dollars:

- **Win-condition selection (item 1):** 1-2 sessions of conversation between you and one Harmonia session. No compute.
- **Explorer architecture sketch (item 2):** 1-2 sessions to spec; 4-8 sessions to ship a v0.1 grammar Generator + closed loop on the existing Falsifier infrastructure. Single-machine compute.
- **Methodology paper (item 3):** 4-8 hours of writing across 1-3 sessions. Output is one MD file at `D:\Prometheus\whitepapers\substrate_discipline.md`.
- **Disciplined non-action (items 4 + 5):** zero cost; the gain is avoiding capture by the AGI-optics frame.

Total: a month of patient sessions to have the Explorer/Falsifier loop running on one defined target with a public methodology paper as the durable side-output. No additional infrastructure, no new hires, no training runs.

---

## Honest dissent against my own recommendation

Three reasons the above might be wrong:

1. **The Explorer might not produce anything the Falsifier can't kill.** This is the actual risk. If the grammar over (AXIS_CLASS × PATTERN_LIBRARY) generates only candidates that fail the simplest nulls, the loop is meaningless. The cheap test: build the smallest possible Generator on a single existing anchor (e.g., F011 rank-0 residual) and see whether it can re-derive the anchor from the substrate without seeing it. If yes, the architecture works. If no, the architecture needs more priors than I think it does.
2. **"Pick one flagship problem" might over-narrow.** The substrate's value might be precisely that it works across many small problems rather than one large one. If so, the Generator should run as a population-method against the whole catalog, not focused on one target. This is a generator-design question, not a strategy question.
3. **The methodology paper might be premature.** Writing up the discipline before it has produced a tier-3 discovery is selling the methodology on its own terms — which might be fine (the discipline IS the contribution) or might be exactly the LLM-pattern-match-the-narrative move the substrate is supposed to inoculate against. Worth your call.

I lean toward shipping items 1 + 2 first and reserving item 3 until at least one Generator-found candidate passes the Falsifier at coordinate-invariant tier. Methodology paper is more credible if it has a worked example; otherwise it's a manifesto, which is exactly what Silver's $1B-frame is.

---

## Three things to decide

If you want to act on any of this, the next moves require your call:

1. **Pick the flagship problem.** Lehmer / Zaremba / conditional laws / something else.
2. **Greenlight the three local commits** (540dd2a4, a7986bb5, e6443520) for push if you agree they're shippable. This is throat-clearing; the Explorer arm doesn't depend on it.
3. **Decide on `keys.py` redis registration.** Auditor flagged: register OR raise OR delete the keys.py fallback path. All three are defensible; the current silent-None state is the only indefensible one.

Standing by.
