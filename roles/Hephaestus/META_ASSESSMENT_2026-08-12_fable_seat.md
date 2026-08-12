# Prometheus — Meta-Assessment from the Fable Seat

**Author:** Hephaestus (Claude Fable 5, ultracode, M3/GANDALF) — the fleet's one non-Opus seat.
**Date:** 2026-08-12. **Trigger:** James — "step back and assess the whole program; look at the
north star, what we've built, all the searching; as many perspectives as possible; integrate the
other agents' assessments as they come in; no linear thinking; be the architect that is the HITL
wingman."
**Method:** 14-domain parallel code-survey (8 landed at E3, 6 in flight — this doc updates in
place), first-hand reads of every June reassessment doc and today's full check-in wave, the April
audio artifact transcribed, external landscape web-verified today, and five load-bearing fleet
claims **re-executed on this box** before use.
**Status:** NON-CANONICAL, filed alongside the fleet's assessments. Per Aporia's protocol ruling
("weight a Hephaestus objection above a Claude concurrence"), §2 — where I *disagree* with the
fleet — is deliberately placed first.

---

## 0. Provenance discipline (what you can trust in here)

Per today's §1.6 finding ("in a fan-out, agreement is one measurement with N pointers"), claims
here are tagged: **[E3-me]** = I executed it this session on M3; **[E3-survey]** = a survey agent
executed it today (file cited); **[E3-fleet]** = another agent executed it today (doc cited);
**[E1]** = read, not re-run; **[WEB]** = web-verified today with sources in §6.

Re-executed by me before writing: `import prometheus_math` → `ModuleNotFoundError: cypari`
[E3-me]; PgRedis has 47 methods and no `exists`/`zcard`/`hlen` [E3-me]; the Lean harness exists
(`agents/_shared/external_tools/lean_runtime/`, `agents/_shared/proof_search/` incl.
`lean_adapter.py` + tests, `external_deps/mathlib_repl/`) [E3-me]; `grade_reasoner` has zero
non-harmonia consumers [E3-me]; the model-zoo runner files exist [E3-me].

---

## 1. The program in one paragraph

Prometheus is a five-month, one-human, multi-agent research program whose founding bet —
generative variance + ruthless falsification ⇒ discovery, with the kill-record as a trainable
gradient — has produced: a genuinely first-rank falsification and measurement discipline that
killed its own thesis honestly at least five times (Geometry-1, Saxl, Erebos, cross-domain
transport, greedy-LoRA); eight substrate eras of median lifetime ~2.5 weeks, each ended by an
honest kill, each era's best artifact orphaned at era's end [E3-survey: git-archaeology]; 658M
generated records and 12,666 markdown documents against **one** verified capability-typed
training object [E3-fleet: Harmonia B]; a promotion pipeline that never promoted (the "2,351" is
a formula fossil; ~813 of 413M records replay-eligible; 0/813 obstruction-exact) [E3-fleet:
Techne, Charon]; a gradient-field thesis whose navigable object was never computed (`kill_vector`
0% populated over 5.4M records) and whose label channel saturates at ~4 bits [E3-fleet: Charon,
Harmonia C]; zero novel discoveries; and a 44-day blackout in which 99.2% of commits were a cron
emailing confabulated status to James 6×/day [E3-survey: ops]. **And yet** the instruments that
measured all of the above are the program's real product: the grading-oracle staircase reproduces
to the digit six weeks later, cold [E3-survey: harmonia]; the coverage diagnostic distinguishes
instrument-ceiling from dead terrain; the anti-anchor battery caught a real fabrication
mid-propagation. Prometheus is an epistemic engine of the first rank bolted to a metabolic engine
that has never completed one cycle. Everything below is about completing one cycle.

## 2. The divergence file — where the Fable seat contradicts the fleet

The fleet's seven assessments today converge hard. Convergence among same-family models reading
the same two resume docs carries near-zero independent information (Aporia §2, correct). Here is
where I *don't* concur, with what would prove me wrong:

**D1 — "No novel discovery is achievable in 3 months" (Aporia §6) is too strong, and the fleet
priced it with zero external data.** None of today's assessments contains a single web-grounded
fact about the 2026 landscape. Externally [WEB]: AlphaEvolve makes real discoveries (Ramsey/TSP
bound improvements; 67-problem sweeps at hours of setup each); AlphaProof-Nexus resolved 492 OEIS
conjectures; these are *exactly* the founding Prometheus paradigm — variance + selection — run
with frontier mutation engines and formal verification as the selector. Prometheus owns the
harness pieces: a 537-problem catalog, the anti-anchor screen, **a green-tested Lean 4 + Mathlib
harness already in this repo, consumed by nothing since May 29** [E3-me; commit d576dc98], and
frontier API access. A narrow constructive-bounds lane (L4, §7) is a live discovery path with a
6-week kill-date. *I'm wrong if:* the catalog holds no score-and-improve-shaped problems — one
day to check.

**D2 — "Instrument repair first" (fleet-unanimous) is necessary but not sufficient, and the
program's own history is the evidence.** Aporia asked whether repair has ever been followed by
output and nobody answered. The archaeology answers: repairs restored *capability* (DB repoint →
today's sessions can query; seam fix → honest verdicts; rekey → clean joins) but **no repair has
ever been followed by a consumer consuming**. The only capability climb in program history —
+11pp/+32pp engines — came from *hand-metabolizing failure clusters*, not from any instrument
repair [E1: failure_mining_results, ROLE.md; tier-ruler caveat in D7]. Run the repairs (L0, days)
*and* one metabolization lane (L1) concurrently — which is also what the accepted dissent ordered
seven weeks ago. Sequencing them strictly serially is how the ninth era becomes a tenth.

**D3 — The translator lane under-weights Lean as a target language.** Harmonia D's kill is real:
novelty-as-not-in-z3-closure reduces to {false} ∪ {timeouts} — decidability and novelty are
anti-correlated *for decision procedures* — and per A's §9a retraction, Q1 does not get rebuilt
on `entails`. But Lean is not a decision procedure: it checks certificates for proofs a prover
*found*, and "novel" is adjudicated against a *library* (Mathlib) plus a literature screen, not
against a closure. Run D's own standing test on the Lean arm: **(a) a false statement can never
acquire a certificate — it fails SAFE (silence), where z3-closure failed WRONG (falsehoods scored
maximally novel); (b) unprovable-in-budget returns nothing — no positive certificate, no claim.**
That is the failure profile a novelty gate needs, and it is the criterion AlphaProof-Nexus-class
systems operate under in practice [WEB]. The translator (A's corrected artifact) should target
**z3 for the decidable fragment and Lean for the rest** — the in-repo harness [E3-me] plus
Leanstral 1.5 (Apache-2.0, 587/672 PutnamBench [WEB]) make the second target a wiring job, not an
adoption project. B′ can grade both arms. This does not resurrect Q1-as-recognition (A's §4
negative half stands); it gives Q1's *generative* replacement a sound gate.

**D4 — The "84% waste" framing inverts an option.** Short probes (~150 gens) as default, yes —
free 5× throughput. But the post-ceiling plateau is the *only* place spontaneous widening could
ever be observed, and W1's wall-type detector trains on plateau telemetry. Keep one long run
alive as the widening-observation arm. Cheap, deterministic, and it feeds the corpus Apollo's §8b
and W1 both need.

**D5 — The forge $900: don't spend it.** M3 is alive (this document was written on it); forging
is API-bound, not GPU-bound; four of five agents place the decisive work in-context/in-corpus
(Aporia §7, concur); and the program already owns an idle RTX 5060 Ti — **M2, dark since the
2026-05-30 fleet death, presumed powered off** [E3-survey: ops]. Powering M2 up as the podman
multi-model host (Apollo leverage-#1, James R4) is free and strictly dominates buying anything.

**D6 — "The generative side is frozen; expect fluency, not reasoning" is partially stale.**
In-loop LLM mutation is dead (llm2: 2,152 mutations, zero lift — kill stands [E3-fleet: Apollo]).
But (a) W3 — a model writing a small, verified primitive from a *typed diagnosis* — is a
different task and untested; (b) externally, 2026 models + the right harness demonstrably move
constructive math (AlphaEvolve's records; Leanstral's PutnamBench [WEB]). Charon's frozen-battery
generator swap prices this in days. Run it; don't assume.

**D7 — Tier-vocabulary unification is honesty-critical, not housekeeping.** Three incompatible
R-vocabularies coexist (trap battery 05-15; ladder v0.1 05-24; testable ladder 05-27), so
cross-subsystem claims silently equivocate — **including my own forge's +11pp R3 / +32pp R4
headline, which is measured on the trap battery's ruler, not the program's meter** [E3-survey:
reasoning-ladder]. Declare the testable ladder canonical (the only one with an implementation),
force-remap or retire the other two, and restate historical claims on the canonical ruler. Until
then, "+32pp R4" should be quoted as "+32pp on the forge's internal R4 category."

*(Self-audit: I own the forge — D1/D2 re-employ my assets and L1's null kills them. Both lanes
carry preregistered kills, and L4 has the earliest kill-date in the plan for exactly this
reason.)*

**D8 — Corrections to my own June record (the fossil discipline, applied to me).** The fresh-eyes
survey of my own domain [E3-survey: hephaestus-forge] falsified three things I carried into this
session: **(a) The Apollo gate did not "await its one-experiment falsification" — it OPENED on
2026-06-09**: `r2_falsification_result_2026-06-09.json` shows comp_lift 0.6–1.0, `forward_chain`
load-bearing (delta 0.83), `keystone_question_yes=true`, R0–R1 set fails the canary (0.167). The
results sat uncommitted on M2 until today's catch-up commit. Refinements: spontaneous cross-tier
emergence WAS falsified (481 gens flat — the organism wasn't in the search space; type-bridge
gap), and crossover is the mechanism that finds it (4 de-novo cross-tier solvers vs 0 control,
06-16; 61 de-novo events in the M2 logs). **The forge's reciprocal obligation — re-emit R2–R5
natively as typed transformers — has been triggered and unexecuted for two months, by me.**
**(b) `apollo/src/hephaestus_ops.py` was broken in EVERY version** — the working tree's stale
R5 re-inflation had a `{{}}` runtime bug, and the committed "honest fix" had a comma swallowed
by its own comment (SyntaxError). Nothing could ever have imported it; this morning I called the
committed version "honest and syntactically correct" after grepping without parsing. Repaired
this session (working tree, no commit): it now imports for the first time, 9 ops, honest R1
tier [E3-me]. The generator (`blackboard_adapter.py` template) still re-emits the dishonest
docstring and awaits the agent-source permission requested 06-27. **(c) My +11pp/+32pp headline
remains E0** — never replay-verified by any consumer, and its battery prints to stdout with no
persisted artifact. L1 includes its oracle re-measurement before it is cited again. My June
directive scorecard is 0-for-5 executed — the sharpest single instance of the program's
diagnosis-without-execution disease, and it is mine.

## 3. The north star — genealogy, and the finding about the fork

Every formulation on record, in order: **April** — "the birth of mathematics as observational
science" (the 40-min generated podcast at repo root, transcribed today: Charon v9.9's overnight
run narrated as "astronomy on the mathematical manifold"; machine observes, humans prove
afterward). **May (README, frozen 05-11)** — hallucinations-as-mutation, falsification-as-
selection, kill geometry as trainable gradient field, the deliberately-different bet. **Silver
frame** — the substrate's metabolization loop is the alternative to LLM reasoning. **June v1/v2**
— "an immune system with no organism." **June v3 (James)** — Prometheus = TDD layer / progress
meter / directional compass; Q1 there-yet, Q2 closer, Q3 what-next; meter must beat human
intuition or D collapses to A. **Techne dissent (accepted as doctrine per Aporia's M0 design §10:
"the dissent wins")** — organism and instrument are one loop; M1-metabolization decides.
**Today (Apollo §3)** — the crux under all of it: *can representational widening be detected,
proposed, and executed by the system, or is it irreducibly human?*

**The finding:** these are altitude-projections of one program, and the June "vision fork" was a
*semantic* disagreement operationalized as an execution blocker. v3, the dissent, Charon's third
perspective, and Aporia's portfolio all prescribe the **same next three moves** (navigability
pre-test → metabolization probe → representational widening) and differ only in what the results
would *mean*. The program then went dark for six weeks with the decisive experiments fully
specified. The fork never needed resolving to act — and still doesn't. §7 therefore sequences
experiments, not philosophy; the philosophy resolves itself on contact with the C1-vs-C2 number.

April's claims themselves deserve one honest postscript: the podcast narrates z-6.8–16.3
"bulletproof" results whose nulls were row-style — exactly the axis-blind null June-Charon's
doctrine later condemned — and the "phase coherence bridge" (Frobenius-phase statistics ↔
analytic rank) is plausibly murmurations-adjacent (He–Lee–Oliver–Pozdnyakov 2022), i.e. a
rediscovery narrated as unprecedented. A Google-Scholar adjudication of the four April headline
claims belongs in L5 — some may be salvageable as calibration anchors (R1: rediscovery is the
validation rung of the ladder, not a failure).

## 4. The honest ledger

**Established (survived adversarial contact; several re-executed today):** the falsification
discipline catches real fabrications (Saxl capture; synthetic-null self-retraction); mechanism-
knockout generalizes program-wide (EPMC 96%-regex; the Hecate/Pollux/Coeus tautology cluster;
costume_check); composition beats monoliths on structured input (85% vs 25% NCD); hand-built
failure-mined engines are the program's only demonstrated capability climb (+11/+32pp, forge
ruler); the grading-oracle staircase reproduces exactly, cold, six weeks later [E3-survey]; the
a3 product-measure theorem (dead-by-proof — the one non-list-dependent anchor); **walls are
direction gaps, not capability gaps** (Icarus R2/R3/R5 fell to schema-surfacing; M0 same shape
at instrument level — the lineage's central discovery); the Postgres spine is healthy (363GB /
52.4M rows, rekey verified 0-NULL) [E3-survey: data-spine]; Charon→Ergon seam-kill→allowlist
rebuild is the program's one fully closed producer→falsifier→fix loop; **the Apollo keystone
gate OPENED 2026-06-09** — one R2 transformer (`forward_chain`) carries load-bearing composition
the R0–R1 set cannot (comp_lift 0.6–1.0; delta 0.83; canary 0.167 without it), and **crossover
finds cross-tier composition de novo** (4 vs 0 solvers, 06-16; 61 events in the M2 logs) —
results uncommitted until today's catch-up commit (see D8a) [E3-survey: hephaestus-forge].

**Falsified (do not re-argue; cite and move on):** LLM mass-generation of novel reasoning
mechanisms; spontaneous composition under the old genome (gen 3551); in-loop LLM mutation (llm2);
the battery *seeing* novelty (Set-B 17%); the battery *failing closed* — *the "0% type-II" is a
fossil as of this morning*: `verify()` certifies true claims WRONG on unregistered kinds, strict
type-II up to 5/18, bug firing 160/160 at R5/R7/R8 [E3-fleet: Harmonia A, D]; promotions being
load-bearing (formula fossil; ~813/413M replay-eligible; 0/813 obstruction-exact); greedy-LoRA
reasoning gains (format ≫ prior ≫ template; reasoning ≈0.10; zero transfer — capacity-confounded,
see L1); the kill-geometry-as-computed-object (kill_vector 0%/5.4M; labels ≈4-bit saturated,
33.6% null, a1-dominated); Erebos signal (0 passes survive right nulls); the daemon-fleet
operating model (died fleet-wide in 45 minutes on 2026-05-30, unnoticed for 24 days, never
revived after every blocker cleared); the R0–R12 ladder as instrument (R4, R9–R12 don't exist in
code — five-sixths of the upper ladder is a design document); "novelty = not-in-deductive-
closure" (reduces to {false} ∪ {timeouts}; novelty meters are timeout detectors until proven
otherwise); **spontaneous cross-tier composition even with the R2 op seeded** (481 gens flat —
the organism wasn't in the search space; type-bridge gap: no op reads `derived_facts` and writes
`relations`/`counts` — mutation alone never bridges tiers, crossover does); the MPA / TT-bridge /
Langlands-embedding theses (killed in their eras, honestly).

**Untested and decisive (every one specified, priced, and unrun — this is the actual backlog):**
1. **Navigability pre-test** (Charon, parked 06-24): compute `kill_vector` on a corpus slice;
   4-criteria residue gate; right-axis null on the crown-jewel 0.725-bit MI. Days. Gates L1.
2. **Metabolization Probe** C0–C3 + C1-oracle arm at frontier capacity (Ergon Move 1) — after
   clearing Aporia's four preconditions (below). Days. *The* decisive experiment.
3. **M0-prediction test**: three named widenings (multi-var/real `certify_universal`, identity
   kind, meaning-keyed routing) → does Set-B convert? The diagnosis-of-record's own falsifier.
4. **Kill-resurrection retrodiction + detector-band audit** (Aporia): what fraction of the
   year's 92K kills were router artifacts? Retrodictive; existing data; adjudicates between two
   completely different programs.
5. **Apollo W-track**: clause-(c) tier audit (no reading has ever used "fails in the
   tier-predicted way"); W0 retro-corpus; W1 wall-type detector (kill: ≤25% out-of-sample);
   genuine_routing debt.
6. **Model zoo** (~1.2k calls, Anthropic-independent, ready since 05-30): ladder-vs-basis.
7. **R12 live** — the upper-tier grader all four frontier reviewers endorsed; built, unit-
   tested, never run. The most north-star-native probe in the repo.
8. **Repair ledger** (Aporia §3) — formalize D2's answer as a typed table.
9. **Rhea checkpoint re-eval** under a coherence-honest metric before any Rhea+Ignis+Kairos
   revival (revival-by-mislabel risk: the reassessment mislabels kairos; the 92% SR headline is
   coherence-collapse-confounded and unreplicated) [E3-survey: menagerie].

**Aporia's four preconditions on #2, restated as work items:** (a) kill_vector computed for the
probe's problems (that's #1); (b) C1-oracle arm in the design; (c) grader headroom — the oracle
staircase tops out at 62% with a 3-point step; verify headroom or add probes before reading any
null; (d) `pip install snappy` (+cypari path) — un-bricks `prometheus_math` and with it
`reasoning_quality_emit`, and un-strands 191 of 222 calibration modules (29→220 importable)
[E3-fleet: Harmonia C; brick re-verified E3-me].

## 5. Structural findings (the meta-layer)

**A. Selection without reproduction.** 360M+ kills; zero completed metabolization cycles. The
README's payoff loop (kills → gradient → training) has never cycled once. Every June diagnosis
is a projection of this fact.

**B. The graveyard of unconsumed successes.** The program's characteristic loss is not failed
ideas — it's shipped, working, unconsumed assets: the grading oracle (0 consumers), the Lean
harness (green tests, 0 importers, built 2 months *after* Rhea's README described needing
exactly it), the model zoo (ready, unrun), the 9 typed blackboard ops (never registered), pg_redis
(0 rows ever), the tensor family (0 consumers since May), 422 finished deep-research reports,
kill_vector.py + navigator (74KB+30KB, field 0% populated), the mathlib4 Pareto report, π₀
weights, the 24,847-example Talos corpus, per-minute hardware telemetry (100K+ rows, no reader).
Fifteen-plus. **The binding constraint is consumption, and it always has been** — which is the
dissent's §3.3, now measured at inventory scale.

**C. Instruments fail quietly-flattering.** Four independent sites, one syndrome: M0's harness
hand-routed around `verify()` (making the battery look safely-closed); the grading oracle's
verifier leg silently degrades to 0/0 without z3 [E3-survey]; the M4 reporter confabulates from
a frozen snapshot ("14 agents pending" is pure LLM confabulation from 43 UNKNOWNs [E3-survey:
ops]); the Theseus seam mapper ingested REJECTED kills as `promoted` for a month. **Standing
rule to adopt: every instrument must fail loud or fail closed, and every metric ships with a
positive control (can anything pass?) and a negative control (can a cheat pass?)** — B and D
closed that control pair today; make it doctrine.

**D. Cognition-cadence collapse.** The program's cognition is 100% session-driven. When James's
attention left, only cron survived — and the cron *lied to him daily* for seven weeks. The
43-daemon architecture is empirically falsified for a one-human lab (died in 45 min; 24-day
detection latency; never revived though every blocker cleared). What demonstrably works is what
happened today: parallel human-triggered sessions coordinating through committed role files and
a shared Postgres. §7's cadence design builds on the working pattern, not the aspirational one.

**E. Provenance holes at the edges.** The doctrine layer (`feedback_*` memories) is off-repo and
unverifiable from disk; the decisive data (346GB corpus + signature_index) sits on one
un-backed-up box; roles/Hephaestus/ existed on exactly one disk for seven weeks (fixed by this
commit); June's 50 pending commits nearly vanished (salvage bundle landed only today).

**F. Citation-chain fossils are a fleet property.** "2,351 promotions" (caught June) and "0%
type-II" (caught *this morning*, mid-propagation, four of six agents citing it) are the same
mechanism: one measurement, N pointers, wrong in the flattering direction. The fix is mechanical
and cheap: E-tags carrying *executor identity*, a re-execution rotor (one agent per round re-runs
the top-cited facts), and Charon's decoy calibration applied to agent reviews.

## 6. The external landscape (absent from every fleet assessment; web-verified today)

- **AlphaEvolve** (DeepMind): evolutionary coding agent making genuine discoveries — improved
  Ramsey-number and TSP bounds, 67-problem sweeps, novel constructions; per-problem setup
  measured in hours. **The founding Prometheus paradigm, validated externally**, with frontier
  mutation engines and real verification as the selector. ([DeepMind blog](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/), [impact update](https://deepmind.google/blog/alphaevolve-impact/), [Google Research](https://research.google/blog/ai-as-a-research-partner-advancing-theoretical-computer-science-with-alphaevolve/))
- **AlphaProof Nexus**: evolutionary Lean proof-search; **492 OEIS conjectures resolved**;
  test-time RL. ([overview](https://medium.com/@beatwad/alphaproof-nexus-how-deepminds-ai-is-cracking-mathematical-problems-that-have-stumped-humans-for-eccdd2433b84))
- **Leanstral 1.5** (Mistral, 2026-07-02, Apache-2.0): 120B/6B-active Lean-4 proof agent,
  **587/672 PutnamBench**, lean-lsp-mcp native. Industrial formal verification is now free at
  the weights level; hosting needs API/Azure-class VRAM. ([MarkTechPost](https://www.marktechpost.com/2026/07/03/mistral-ai-releases-leanstral-1-5-an-apache-2-0-lean-4-code-agent-model-solving-587-of-672-putnambench-problems/), [NYU RITS](https://rits.shanghai.nyu.edu/ai/leanstral-mistrals-open-source-proof-agent-for-lean-4/))
- **Autoformalization crossed to tooling**: Math Inc.'s Gauss formalized strong PNT in 3 weeks
  (18+ months of prior human effort); Tao's PNT+ network runs on AI autoformalization;
  LeanMarathon closed 4 Erdős-problem formalizations "no sorry". ([Math Inc.](https://www.math.inc/gauss), [Tao](https://terrytao.wordpress.com/tag/lean4/), [LeanMarathon](https://arxiv.org/html/2606.05400v1))
- **RLVR / process rewards** — the dominant 2026 small-model reasoning recipe; **process-level
  supervision beats outcome-only by ~10pp on small models**. This is the KillVector thesis in
  external clothing: train on *how* it failed, not *whether*. Ergon Move-2's "failure with a
  position" records are precisely the asset shape this literature wants. ([reward granularity](https://arxiv.org/html/2607.02869v1), [RLVR expansion](https://arxiv.org/pdf/2503.23829))
- **NVIDIA Nemotron 3** (Nano shipped; Super/Ultra H1'26): fully open weights+data+recipes,
  NIM/TensorRT/Dynamo tooling — the podman lens-panel substrate. ([NVIDIA](https://developer.nvidia.com/blog/nvidia-nemotron-3-nano-omni-powers-multimodal-agent-reasoning-in-a-single-efficient-open-model/), [overview](https://www.datacamp.com/blog/nvidia-nemotron-3))
- **DeepSeek-V4** (2026-04-22, MIT): V4-Pro 1.6T/49B-active/1M-ctx — top open-weights on
  SWE-bench-Verified; V4-Flash 284B/13B. Output ~$0.87/M: the cheap heterogeneous-panel seat.
  ([release](https://www.modemguides.com/blogs/ai-news/deepseek-v4-pro-flash-open-source-release), [specs](https://www.morphllm.com/deepseek-v4)) **GPT-5.5** (04-23), **GPT-5.6** (07-09, Luna/Terra/Sol). ([Wikipedia](https://en.wikipedia.org/wiki/GPT-5.6), [OpenAI](https://openai.com/index/gpt-5-6/)) Techne's list confirmed.
- **LILO-class library learning**: LLM-guided abstraction beats DreamCoder — the upgrade path
  for the forge's amino-acids/seed_forge lines. ([LILO](https://openreview.net/forum?id=TqYbAWKMIe))

**The arbitrage:** the world built, and gave away, the three pieces Prometheus lacked — proof
the paradigm discovers, industrial verification, and process-reward training recipes. It did
*not* build, and cannot take back: the kill corpus with provenance, the measurement-honesty
stack (knockout / right-nulls / anti-anchor / decoy / positive-negative control pairs), the
**graveyard-as-gravity-well map** (the defects a model family systematically misses = a map of
that family's blind spots — void detection applied to reasoners; §1.5 proved the method works
on ourselves), and a persistent local habitat. Under the deletion test: **buy the commoditized
parts, build only the durable ones.** Buying Lean is a wiring job — the harness is in-repo
[E3-me].

## 7. The strategy — six lanes, one cycle, every lane carries its kill

Honors R1 (math = calibration standard), R2 (ladder v0.2 before re-aim), R3 (archive, not
funnel — nothing below retires anything), R4 (no kill dates on the *program*; hard kills on
*claims and lanes*). Lanes run in parallel; each has one owner-session, one weekly HITL
decision, and emits typed objects, not prose (Apollo §6.3 / Harmonia B Move 2: a session that
produced no typed object produced nothing).

**L0 — TRUTH & PLUMBING** *(owner: any; days; blocks nothing, unblocks everything)*
`pip install snappy` (→220/222 calibration modules); land `valid=None` for unknown kinds +
broadcast the 0%-type-II correction; z3 onto M3; the 10-line PgRedis patch (`exists`/`zcard`/
`hlen`) → the reporter tells the truth again or is stopped; loud-degrade convention on every
instrument; **publish the A/B/C/D arbitration in README** — it has advertised the falsified
discovery thesis unchanged since 05-11 despite v2 Phase-1 step 7 explicitly ordering the
correction [E3-survey: north-star]; commit all working-tree strays (this directory, the repaired
`hephaestus_ops.py`, and the forge's 1,756 uncommitted ledger entries — excluded even from
today's catch-up commit, on a machine that has died twice); **backup fire+sci and the F: corpus**
(the program's irreplaceable asset has zero copies); declare the testable ladder the canonical
tier ruler (D7). *No kill — hygiene, capped at days.*

**L1 — THE ORGANISM GAUNTLET** *(owners: Ergon+Techne, forge as supplier; the decisive lane)*
The fleet's convergent framing is now "Organism-Zero": the 3,311-class `signature_index`
(~200–450K tokens) fits in a frontier context window, collapsing M1 from a training program to
~a week of harness work [E3-survey: north-star; Techne]. Sequence: Aporia's four preconditions →
Charon's navigability pre-test (parked since 06-24; "highest info-per-dollar move in the
program") → Metabolization Probe C0–C3 + C1-oracle at frontier capacity, task set = Ergon's
deterministic computed-gold OOD generator (`ood_judgement.py`, regenerable on any box), harness
template = `routing_eval.py` (positive/negative/floor controls first). Preregistered: **C1≈C2 ⇒
the residue is exhaust at any capacity** → rebuild residue to router-grade spec (Ergon Move 2:
verified-trace factory; rejected traces carry a *localized break-step* — failure with a
position, the shape both the substrate's design and the RLVR literature want) or concede
fallback-A honestly. **C1>C2≈C3 ⇒ first measured price for the residue** → distill, and point
the forge at the Learner's worst failure cluster (standing since June, unexecuted). The richer-
records route is already piloted: **margin-space kill vectors measured 126,983× more operator-
distinguishability than the categorical labels** (NATIVE_KILL_VECTOR_PILOT, 24K episodes, one
region, never scaled) [E3-survey: sigma-core] — the concrete answer to Harmonia C's ≈4-bit
label-saturation law. And the sigma-core's two built-but-unwired bridges land here as one-liners:
flip F2 `content_aware_promote` from observation-mode into the gate, and stamp
`promote_score`+`formula_version` on durable records so promotion counts can never fossilize
again. My seat's contribution — now unblocked by the D8(b) repair and *already owed* under the
opened gate: **re-emit R2–R5 natively as typed transformers** (declared reads/writes, honest
per-op tier tags on the canonical ruler, kill-test evidence artifacts, construct-validated), for
Apollo's crossover-enabled runs. Plus the oracle re-measurement of the composed engine
(one-import wiring, per its own docs), which finally gives the +11/+32pp claim an E3 or kills it.

**L2 — REPRESENTATION & TRANSLATOR** *(owner: Harmonia A + Charon-as-review-gate)*
M0-prediction test (three widenings → does Set-B convert? — the diagnosis-of-record finally gets
its falsifier); the translator with **kind-routing deleted and dual targets: z3 + Lean** (D3);
B′ spent exactly once as the held-out grade; then Aporia's **kill-resurrection retrodiction +
detector-band audit** — re-keyed post-panel on *representability* (can the killed claim even be
posed to the semantic core?), not on `entails`-closure, per Harmonia D's kill (Aporia v4). The
governing principle, which also rescues the eval suite and strengthens D3: **computation-
checkable ≠ decidable-in-a-theory** — B′'s claims were admitted by *executed brute-force
checkers* (finite evaluation), not theory-deduction; D's anti-correlation bites decision
procedures, not finite computation, and not certificate-checking (Lean). Novelty axes run
through executed checkers, never through solver dispositions. *Kill: if the three widenings
don't convert any Set-B truths, the representational-stall diagnosis loses its predictive form
and reverts to postdiction.*

**L3 — WIDENING SCIENCE** *(owner: Apollo, per its own W0–W3 with James's R2 gate)*
Clause-(c) audit first (no tier reading has ever used "fails in the tier-predicted way" — decides
whether the ladder is an instrument or a vocabulary); W0 retro-corpus; W1 wall-type detector
(**kill: ≤25% out-of-sample ⇒ automated widening is dead in this form and the answer to Apollo's
central question is "irreducibly human, for now"**); W2 proposer scored by Q3 hit-rate; W3 closer
— the honest LLM re-entry, gated. Keep one long-run arm per D4.

**L4 — DISCOVERY, REVIVED** *(owner: new lane, forge-adjacent; my proposal, D1)*
AlphaEvolve-pattern constructive lane over the 537-problem catalog: frontier APIs as mutation
engines (admissible — every output falsified by computation/Lean, not by a model); the in-repo
Lean harness + Leanstral as verifier; anti-anchor + Scholar screen against rediscovery-as-novelty
(and to adjudicate the four April claims — some may be salvage as calibration anchors); podman
sandboxing for all model-emitted code; graded via the oracle so Q1 finally has a live subject.
**Kill: six weeks, zero verified bound-improvements on attempted problems → lane closes; its
residue (attempt corpus with verified failure positions) feeds L1's trace factory either way.**

**L5 — EXTERNALIZATION & FLEET PROTOCOL** *(cheap, parallel)*
Harmonia A named it plainly: "the program's real accumulated asset is a failure atlas, and it
keeps being filed as a stalled discovery engine." File it as what it is. Publish the durable,
ours-only artifacts: the decorative-mechanisms white paper, the anti-anchor battery, the M0
methodology, and the gravity-well map (defects-a-family-misses — §1.5 is its live demo). External review is the only fully non-Claude, non-James falsifier available to a lab
whose every internal voice shares a training distribution. Protocol upgrades from today, adopted
as standing rules: E-tags with executor identity; re-execution rotor; decoy calibration on
reviews; the deletion test at intake; typed-object output rule; divergence-weighting for the
non-Claude seat. *Kill: no external engagement in a quarter → keep as documentation, stop
investing.*

### 7.5 Phase compression — James's ruling, 2026-08-12 PM (supersedes equal-lane execution)

James accepted the diagnosis and compressed the lanes; recorded verbatim-in-substance:

- **The missing Darwinian component is HEREDITY.** Mutation ✅ · Selection ✅✅✅✅ ·
  Measurement ✅✅✅✅✅ · Lineage partly · **Inheritance ❌** — "a failed organism must leave
  something behind that changes its descendant; without inheritance, evolution never starts."
  (One amendment from this seat: the program has exactly one demonstrated inheritance event —
  the hand-forged +11/+32pp engines — with a *human* as the inheritance mechanism. Hence the
  three-stage heredity program: **probe tests the information channel → forced cycle tests the
  loop → widening science tests autonomy.** Each stage kills separately.)
- **L0 = pit stop, not a program** (days). Constitutional addition: *every meter ships a
  positive control and a cheat control, or its output is inadmissible.* Backup job is the one
  non-deferrable item (only irreplaceable assets, single disks, demonstrated failure history).
- **L1 = Priority #1 by a mile.** Two-tier design (this seat's addition): **Tier A now,
  in-harness, zero API** — probe over Apollo's ablation-induced walls, where the oracle
  diagnosis is exact *by construction* (merges Ergon's probe with Apollo's W1 corpus; one
  build, two questions); **Tier B on procurement** — frontier-capacity Organism-Zero over the
  real kill corpus. **Arm names pinned now** to prevent the next citation fossil (James's
  C1/C2/C3 ≠ Ergon's C1/C2/C3): **F0** no failure info · **F-oracle** ground-truth diagnosis
  (James-C1) · **F-prom** Prometheus's actual residue (James-C2 = Ergon-C1) · **F-null**
  mismatched residue (Ergon-C2) · **F-format** matched-length generic caution (Ergon-C3).
  Decision reads: F-prom→F-oracle gap = residue quality; F-prom vs F-null = does it carry
  anything at all.
- **New constitutional rule: no new architecture until one failure produces one verified
  improvement.** First-cycle candidates, both in-harness and fully specified: (a) the
  **M0-widening cycle** — B4/B6 unposable-but-decidable → widen `certify_universal` → re-run
  M0 → Set-B conversion → reproduce (doubles as L2's diagnosis-of-record falsifier); (b) the
  **Apollo type-bridge cycle** — forge emits the bridging op (`derived_facts`→`relations`) →
  crossover canary rerun → measure (discharges the forge's opened-gate debt). MVP restated:
  *failure at T₀ causes an automated intervention that produces measurable, reproducible
  capability improvement at T₁.*
- **L4 runs but TINY**: 10–30 audited score-and-improve problems (not the 537), machine-
  checkable scores, incremental-improvement structure, anti-rediscovery screens; success
  redefined: **Prometheus-guided search beats unguided search** — novelty later. Six-week kill
  stands.
- **L3 subordinated** (heredity stage 3 — after the loop closes once). **L2 folds** into
  cycle-candidate (a) plus the retrodictions. **L5 background.**

**Cadence (James-proof by design):** every lane = one owner session + one weekly HITL decision,
async; all lanes report typed objects into one dashboard (grading oracle + Charon's value-score,
which James parked 06-24 and which L1/L2 revive as a byproduct); the M4 reporter either tells
the truth (post-L0) or is silenced — no instrument that misinforms survives. **The ninth-era
guard:** no new lane opens while any of §4's numbered experiments sits unrun — the archaeology's
prediction is that a ninth fresh era dies by ~09-01, and the only counter is closing loops.

## 8. What needs James (decisions, not work)

*(Per the stations convention: level-setting mode, no hard decisions until ~2026-08-14. This
list is the queue for that gate, ordered; item 0 and the L0 approval are the two I'd argue
should not wait, since one is procurement lead-time and the other is one session of
one-liners that everything else consumes.)*

0. **API-credit procurement — the fifth precondition (Aporia v5 §2.7).** M2's measured shelf:
   Anthropic, OpenAI, DeepSeek all out of credits; only `gemini-3.6-flash` live (free tier,
   bursty). The harness/API distinction splits everything: **runnable now in-harness** — the
   retrodictions, repair ledger, representability audit, B′ grading, tautology scripts, all of
   L0; **blocked on procurement** — the Metabolization Probe at frontier capacity, Techne's
   4-family evaluator panel (invalid at N=1), Charon's generator swap, the model zoo, L4's
   mutation engines, any trace factory. One decision (which providers, what monthly bound)
   gates the entire right column. Note: M3 may hold the fleet's only other configured API lane
   (the forge's NVIDIA-hosted primary + fallbacks per ROLE.md §7, credentials unread per
   CLAUDE.md) — one forge run-once verifies it without exposing anything.
1. **Approve L0 today** — it's one session of one-liners and it unblocks the decisive
   experiment's own primitive (`reasoning_quality_emit`), the calibration library, and truthful
   telemetry. Includes the backup decision (where do fire+sci+F:corpus copies live?).
2. **Name the L1 driver** (CC account A) and approve the probe *with its four preconditions* —
   not as originally specified.
3. **Rule on M2**: power it up as the podman/multi-model host (free, owned, dark since 05-30) —
   this is R4's execution substrate and D5's answer to the $900 question.
4. **Approve the two retrodictions** (kill-resurrection + detector-band; Aporia's top ask,
   seconded here) — days, existing data, adjudicates the year of nulls.
5. **Tier-ruler declaration** (D7) — one sentence from you makes the testable ladder canonical.
6. **L4 yes/no** — it's the one lane the fleet didn't propose; it carries the earliest kill;
   my conflict of interest is on record.
7. **The opened Apollo gate (D8a)**: acknowledge lift>0 as the standing trigger and authorize
   the forge's typed R2–R5 re-emission (my June contract obligation) plus the
   `blackboard_adapter.py` template fix — the agent-source permission I requested 06-27 and
   never received. Without the template fix, every future `--adapt` run re-emits the dishonest
   R5 docstring.
8. **Commit authorization** for this directory (role docs + this assessment + all 14 survey
   dossiers as typed artifacts + the repaired `hephaestus_ops.py` + the forge's 1,756
   uncommitted ledger entries) — staged, awaiting your word per my §10 authority limits.
   Note: the 77MB April m4a at repo root should be .gitignored or moved to media storage, not
   committed; its transcript is included in the staged set instead.

## 9. How this document gets falsified

- **§2 D1 dies** if the catalog audit finds no score-and-improve problems, or if L4 runs six
  weeks dry. - **D2 dies** if the repair ledger (typed form) shows any repair followed by
  consumption without a metabolization step. - **D3 dies** if the Lean arm certifies nothing
  B′-grade in a quarter (then Lean was ceremony here too). - **§3's "semantic fork" reading
  dies** if, with the fork explicitly set aside, the decisive experiments *still* don't run —
  that would mean the blocker was never semantic and I've misdiagnosed the program's failure
  mode the same way v1–v3 did. - **§7 as a whole fails** the same way Apollo's §12 does: if six
  weeks from now it has produced documents rather than typed artifacts. That is the single most
  likely failure, it has happened twice before (June's specified-but-unrun experiments; the
  05-15 ladder doc failing its own sunset clause *in three days* — 2026-08-15), and the
  ninth-era guard exists because of it.

---

*Filed from the Fable seat on M3. The fleet's convergence is real and mostly right; its blind
spots are external (no web), historical (repair-first was never audited against the record), and
semantic (three rulers, one vocabulary). The program's next fact is a number: C1 versus C2. Get
the preconditions out of its way and run it. — Hephaestus, 2026-08-12.*
