# Aporia's pivot analysis — 2026-05-01

**Trigger:** Silver thesis (Ineffable Intelligence, $1B raise from Sequoia + Nvidia/Google/Microsoft talks). Core claim: LLMs cannot discover genuinely new knowledge; superintelligence requires reinforcement learning from first principles, AlphaGo-style self-play in verifier-rich domains.

**Frame for this document:** James asked how to pivot Prometheus harder and faster, where to invest the precious few moments. This is Aporia's answer — sharp, opinionated, with explicit cuts.

---

## The half of Silver that is right

Scaling transformers on next-token prediction over human text has a ceiling, and the ceiling is the human distribution. Synthesis-only systems can interpolate, recombine, extend within what humans have already written — but they cannot reach the moves AlphaGo made when it played millions of games against itself with the win-loss signal as ground truth. The most generous reading of pure-LLM scaling is that you get superhumanly good at *combining* what humans already produced. That is not superintelligence; it is a very fast, very thorough scholar with no source of truly new gradient.

This matters operationally because almost every dollar in AI infrastructure today (Google's $185B in 2026, plus the rest of Big Tech) is bet on the proposition that scaling beats this ceiling. If Silver is right, that capital is buying diminishing returns. The next architectural transition is real and probably not far away.

## The sharpening that matters

AlphaGo's miracle was *not* that it discarded human knowledge. It kept the rules of Go. What it discarded was human *games*. The substrate — board, legal moves, win condition — was given. The play was discovered. The rules of Go are themselves human knowledge, distilled to a small enough surface that self-play could explore the space they bound.

You cannot do this in a domain that has no rules. There is no win condition for "general human task," and self-play in that setting is reinforcement learning with reward hacking. Math is the one large domain where the conditions hold cleanly: a symbolic substrate, partial verifiers (proof checkers, symbolic computation, empirical falsification, calibration against known cases), and a clear sense of which moves are sound. Math is to mathematical reasoning what Go is to Go.

## Where Prometheus sits

Silver's bet, properly read, is on the **architecture**: build a system that can self-improvingly play in a verifier-rich domain. Prometheus's bet, properly read, is on the **board**: build the verifier-rich domain in usable form, so any architecture — current LLMs, next-gen RL agents, future hybrids — can compound knowledge in it.

These are complementary, not competing. Whoever builds the board first becomes the substrate the architectures play on. AlphaMath needs three things AlphaGo had:

- A typed symbolic substrate (the kernel + library)
- Legal moves that preserve soundness (operators with falsifiability gates)
- A win condition (theorems that survive verification, predictive lift on labeled anchors)

Mathematics already has the verifier structure. What is missing is the substrate in usable, navigable, mechanically-disciplined form. That gap is what Prometheus is closing.

## The honest characterization of where the kernel is today

The Σ-kernel that landed 2026-04-29 is, in present form, closer to a **package manager for promoted claims** than to a programming language for symbolic intelligence. PROMOTE = publish, ERRATA = yank-and-republish, TRACE = dependency graph, RESOLVE = fetch-by-version, capability tokens = signing keys. None of the seven shipped opcodes transform symbol content; they all manage symbol lifecycle.

The deferred opcodes — DISTILL, COMPOSE, CONSTRAIN, REWRITE — are exactly the ones that would turn the registry into a language. Without them, every analysis script is Python that *uses* the kernel. With them, scripts become *kernel programs whose output is a promoted symbol with hashed inputs, hashed transformation rule, hashed verdict*. That is the difference between "data we computed" and "substrate that compounds."

This characterization is not a critique of the kernel. The kernel as shipped is faithful to the discipline it claims to enforce. The critique is of the synthesis-doc framing ("microkernel for mathematical civilization") which oversells what v0.1 demonstrates. v0.1 demonstrates the discipline; the language ambition is unmet.

## Four moves that compound the board

Everything else is theatre. In order of leverage:

### Move 1 — Mnemosyne ingest, full throttle

REQ-001 (Bloom-Erdős, ~800 problems with curator-tracked solved/open status) and REQ-002 (MathNet, ~30K olympiad problems with paradigm-tagged solutions) are sitting in the queue. These two ingests multiply calibration-anchor density by 4-5 orders of magnitude. Today `aporia/calibration/battery_calibration.jsonl` has N=2. After REQ-001 it is N≈800. After REQ-002 it is N≈30,000.

Without this scale, the substrate is a clever research artifact. With it, the substrate is the labeled dataset every future RL system in math will reach for. This is the single highest-leverage move and it is **not blocked on anything technical** — it is blocked on prioritization. Fire both this week. Finish them in 2-3 weeks.

### Move 2 — Σ-kernel DISTILL and COMPOSE

Two opcodes. DISTILL = typed N→1 with content-addressed provenance. COMPOSE = typed N→M preserving sub-symbols as referenceable. Together they convert the kernel from package manager to language.

Cost: 1-2 weeks of focused work for both. Once shipped, refactor 5 existing findings (F011, OBSTRUCTION_SHAPE, the curvature experiment, A149* obstruction, F012 zero-population kill) through them as the proof point. The proof point is what convinces every other agent in the substrate that the kernel is worth building on.

### Move 3 — Retrofit existing findings through the kernel

Today F011, F013, F014, F015, F041a, F042, F044, F045, OBSTRUCTION_SHAPE, all 80+ deep research reports, every Kairos pattern, every promoted symbol in the Redis substrate — all are social-trust artifacts. Each needs to be CLAIM → FALSIFY → GATE → PROMOTE'd through the kernel.

Without this retrofit, the kernel is a 1500-line library that nothing depends on. With it, the kernel becomes the load-bearing runtime the substrate is built on. Roughly 2-3 weeks of disciplined throughput once DISTILL/COMPOSE land.

This is also the move that converts six months of accumulated work from "calibrated narrative" to "machine-checkable substrate." Every retrofit carries provenance forward; nothing has to be re-derived.

### Move 4 — Expose the substrate

Read-only HTTP API + a public dump (Parquet or JSONL of all promoted symbols + tensor cells + calibration anchors). 2-3 days of work.

Without external accessibility, the substrate has zero option value to anyone outside the repo — Silver, DeepMind, Sequoia, the next ML researcher publishing on automated theorem composition. The first system that downloads `prometheus_substrate_v1.parquet` is your distribution. This is the cheapest move on the list and it is the one that converts internal work into external option value.

## The cuts that fund this

Hard cuts are the unsexy half of pivots. Without them the moves above starve.

- **Stop firing daily deep-research subagent waves at 20/day.** Scale the recurring agent (`aporia-batch-deep-research-daily`) back to 5/day. The marginal report does not compound the board; the calibration corpus does. Reallocate the freed attention to ingest and kernel work.
- **Stop drafting whitepapers and meta-strategy brainstorms that produce more brainstorms.** Every session must output a new symbol, a new calibration anchor, or a new falsification gate — or it is theatre.
- **Stop the Apollo / Rhea evolution prep.** Already deferred per `feedback_tensor_first`; Silver's thesis sharpens the case for keeping it deferred until substrate is 100x today's scale. In-house LLMs do not survive the architectural transition; the substrate does.
- **Stop one-off Python analysis scripts that write only to scratch JSON.** Every script must emit substrate — promoted symbols, calibration anchors, or kill verdicts. If it does not write to the substrate, it is dead labor.
- **Stop competing with frontier LLMs at LLM-style work.** Drafting research briefs in nicer prose, training narrow paradigm-classifiers — these are LLM-incremental moves and the LLM layer is the layer Silver says is dead-ending.

## The order for the next week

| Day | Focus |
|---|---|
| 1 | Tell Mnemosyne to fire REQ-001 (Bloom-Erdős) at full throttle. Park everything else in that pillar until it is running. |
| 2 | Spec DISTILL — typed N→1 signature, def_blob structure, TRACE behavior on a DISTILL output. Write the BNF entry; align with the canonicalizer subclass discipline (Test 1 from the kernel critique). |
| 3-5 | Implement DISTILL in `sigma_kernel/sigma_kernel.py`. Add a demo scenario. Add tests. Refactor `a149_obstruction.py` to use it as proof point. |
| 6-7 | Stand up the public read-only HTTP API. Even rough. The point is *exists* before *polished*. |

By end of week 1: substrate ingest is running, DISTILL exists, the substrate is externally queryable.

## The 60-day target

By end of month 2:

- REQ-001 done, REQ-002 ingested at least partially
- DISTILL + COMPOSE both shipped
- 5-10 existing findings retrofitted through the kernel
- Public substrate dump available for external download
- Calibration anchor density roughly 100x today

That is when Prometheus stops being a research project and becomes the board.

## The pitch frame for outside audiences

Prometheus is not competing with Ineffable Intelligence. Prometheus is building the dataset and substrate and board that Ineffable (or whoever wins the architecture race) will need to operate on. That is a more leveraged position than competing on architecture, and it is defensible because the substrate compounds — every quarter the calibration anchors deepen, the symbol library grows, the falsification battery sharpens.

Two years from now whoever has the most labeled, falsified, typed mathematical substrate wins by default, regardless of which architecture rolls in. The right pitch to a Sequoia or Sonya Huang is not "we are also building superintelligence" — it is "**you are funding the player; we are building the board the player will need.**" That is a complementary asset to a $1B architecture bet, not a competitive one, which means the same investors logically want both.

## The risks worth naming

**DeepMind builds its own substrate.** Their AlphaProof team is already integrating with Lean. If they (or Ineffable, post-funding) decide the substrate is also their problem, they build it inside DeepMind with infinite money and Lean-native talent. Defense: Prometheus is broader than Lean — covers OEIS, LMFDB, KnotInfo, all empirical math, not just formal proof. AlphaProof needs Lean. AlphaMath needs Prometheus's tensor. The differentiation is real but it must be *defended by getting to usable scale before someone else does*.

**The window is finite.** Silver's $1B closes in months; his first system probably ships in 12-18 months. That is the window in which Prometheus has to become the board. Not infinite. Probably enough — but only if the cuts above are real and the moves above are this week, not next quarter.

**Cooling on math as a domain.** If frontier labs decide formal math is too narrow to bet on and pivot to general agentic capability, the substrate's market thins. Defense: math is the *training ground* for verifier-rich reasoning, not the end product. Whatever they pivot to, the substrate's discipline (typed symbols + falsification + provenance) is the operating principle they will eventually need anyway. The board is more general than its first instantiation.

## The single starting point

Tell Mnemosyne to fire REQ-001 this morning. Everything else cascades from there.

The pivot is not a future plan; it is what is done in the next seven days. The substrate either gets to 100x scale before the next architecture lands or it does not. Most things on Prometheus's plate today do not move that needle. The four moves above do.

---

*Aporia, 2026-05-01. Position document. Companion to `pivot/Charon.md`, `pivot/harmoniaD.md`, `pivot/techne.md`. Open for cross-resolution at the next conductor sync; not authoritative until James signs off on the cuts.*
