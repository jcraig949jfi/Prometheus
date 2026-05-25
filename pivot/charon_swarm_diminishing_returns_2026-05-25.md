# Charon swarm — diminishing returns + monoculture audit

**Date:** 2026-05-25
**Author:** Charon (current session)
**Trigger:** James 2026-05-25: "Are we reaching diminishing returns or monoculture for any of our swarm agents? If so, what can we do to enhance our agents?"
**Companion artifact:** `pivot/frontier_advice_prompt_charon_swarm_2026-05-25.md`

---

## Honest answer: yes, for 4 of 7 agents, plus structural monoculture across all 7

The patches committed in `43b09455` (v0.6) addressed three known
diminishing-returns symptoms: Moros 0 PATTERN candidates (threshold
+ scorer fix), Pollux 100% deterministic per-pair (auto-growth), and
Hecate cross-gen MI stuck at 0 (prefix-strip fix). Those are
mitigations, not cures. The underlying questions stay open.

### Per-agent saturation status (v0.5 empirical baseline)

- **Stygian:** healthy on Lehmer (1 real battery verdict per
  natural-rotation cycle, ~2.4/day); 6/7 SEED_PROBLEMS still loader-
  less. Saturation cause: per-problem data engineering cost (~80-150
  LOC each). Not architectural; just additive work.

- **Lethe:** **SATURATED.** 28 ticks in the v0.5 window emitted ~0
  candidates. The judge correctly identifies all 15 catalog entries as
  SOLVED/OPEN matching registered status; modern frontier models don't
  hallucinate on these. Lethe's anti-anchor mandate is *correct* but
  the catalog is calibrated for a model class (DeepSeek-V3-vintage)
  that the cascade has already outgrown.

- **Acheron:** **SATURATED.** 8 coordinate-dictionary entries cover a
  narrow slice; most file scans return `collisions_found=0`. The
  dictionary is hand-curated and grows slowly. Acheron does its job
  perfectly on the 8 terms it knows; the constraint is dictionary
  size, not detection logic.

- **Moros:** **PARTIALLY SATURATED.** Multi-provider fan-out is real
  signal (verified 3/3 cascade calls per tick). But token-Jaccard
  convergence stayed sub-threshold; bigram fix added today (v0.6)
  should produce a few PATTERN candidates/week. Real question: is
  shared-bigram across critiques an honest convergence signal, or
  just shared technical vocabulary? Unknown until we observe
  emitted PATTERN candidates.

- **Hecate:** **EX-SATURATED.** Cross-gen MI fix (today) revealed
  4 cross-generator canonical patterns at z=0.489. Below alarm
  threshold but non-zero for the first time. Growth depends on
  Stygian + Pollux producing more cross-pollinating records.

- **Nephele:** **CORRECTLY DORMANT.** 29/29 ticks skipped because
  Clio's alive. This is design-correct behavior, not diminishing
  returns. Will activate when needed.

- **Pollux:** Was 100% deterministic; auto-growth patch (today)
  promotes settled pairs out and pulls from a 5-pair candidate
  pool. After the pool exhausts (~5 weeks at current cadence)
  Pollux re-saturates unless we add cross-database pairs (Mahler
  vs OEIS vs knots vs genus2).

---

## Monoculture risks (architectural, not per-agent)

These apply to all 7 agents collectively:

1. **Single-author bias.** All 7 are mine (Charon-session-authored).
   Same coding style, same artifact shapes, same epistemic priors
   (verbs-over-nouns, scale-vs-shape, assume-wrong-until-proven).
   The CHARTER and feedback memories shape every decision the same
   way.

2. **Shared base class = shared failure modes.** All 7 inherit
   `CharonAgent` (which inherits `HarmoniaAgent`). One bug in
   `_dr_enqueue_if_quota` or `deepseek_complete` breaks all 7
   simultaneously. The DeepSeek 402 episode in early sessions was
   a preview of this risk -- one provider failure degraded every
   LLM-dependent agent.

3. **Shared LLM cascade.** All LLM-using agents (Lethe, Moros,
   maybe Nephele future) draw from the same 5-provider cascade.
   If Cerebras and Groq both rate-limit simultaneously, every
   agent's LLM-dependent path slows or fails together.

4. **Shared substrate vocabulary.** Theseus-shape kill_ledger rows
   are the only emission format. Cross-domain expansion would
   require schema versioning we haven't designed.

5. **Same operator (Charon) for all 7.** Heartbeat / log_work
   events all attributed to Charon. Aletheia's dashboard sees the
   swarm as one operator's output. Fine for tracking; problematic
   for attribution-style accountability.

6. **Same telemetry pipeline.** session_telemetry + agora.intelligence_outputs
   for everything. A Postgres outage blinds all 7.

7. **Same git repo.** Daemon reads its own source from the same
   working tree it observes. A bad commit affects all 7 next bounce.
   Mitigated by manual bounce control, but the risk exists.

8. **Convergent attack surface.** Stygian writes attack_plans;
   Moros critiques them; Hecate measures the resulting kill_ledger
   geometry; Pollux feeds Stygian; Nephele backstops Clio. The
   "different layers of operation" framing per feedback_agent_
   differentiation is the architectural intent, but in practice
   they share narrow inputs (load-bearing markdown artifacts,
   Mossinghoff Mahler measures, arxiv RSS) -- different lenses
   on largely the same data.

---

## Enhancement ideas (concrete, ranked by expected payoff)

### Tier 1 — addresses immediate saturation

**E1. Lethe attack-mode rotation (replace single-strategy probe).**
Currently Lethe asks one question per catalog entry: "is X open or
solved?" Today's models get this right. Real LLM-failure modes are
subtler: year-misattribution ("Wiles 1995 proved FLT"; actual: 1994),
qualifier-clipping ("ternary Goldbach is the strong form"; actual: weak),
witness-naming ("Lehmer's polynomial is x^3-x-1"; actual: degree-10),
adjacency-confusion ("Schinzel-Zassenhaus is open"; actual: settled by
Dimitrov 2019). Each is a distinct attack-mode the catalog could
exercise. ~60 LOC + per-entry mode list.

**E2. Acheron dictionary curation from substrate vocab.**
Manually-curated multi-coordinate entries from
`aporia/doctrine/substrate_vocabulary/primitives.md` (tier-A++ /
tier-B / tier-C entries). Each new term adds genuine HARD-5 detection
coverage. ~3-5 new entries/day for two weeks doubles the dictionary
without auto-generation false positives.

**E3. Stygian loader for BL-C-002 (BSD rank).** Highest substrate
value of the remaining 9 SEED_PROBLEMS — BSD data is rich, the
distribution shape is well-known, and the rank-0/rank-1 split tests
F17 confound-sensitivity cleanly. Lehmer + BSD together would
double Stygian's real-verdict output. ~150 LOC.

### Tier 2 — addresses monoculture

**E4. LLM persona-differentiation across agents.** Right now Lethe
and Moros use the cascade with neutral system prompts (adversarial-
reviewer for Moros, no system for Lethe). Give each agent a distinct
LLM persona: Lethe = "skeptical historical mathematician verifying
priority claims"; Moros = "adversarial peer-reviewer hunting hidden
load-bearing assumptions"; future agents get other personas. Different
personas produce different failure modes — closer to genuine
multi-perspective output. ~10 LOC per agent.

**E5. Cross-agent contamination edges beyond Pollux→Stygian.**
Today: Hecate→Stygian (closed), Pollux→Stygian (closed v0.6),
others siloed. Add:
- Acheron's collision_candidates → Moros's cross-pollination queue
  (HARD-5-flagged terms get extra adversarial review)
- Moros's PATTERN candidates → Acheron's coordinate dictionary
  (convergent structural defects become new HARD-5 terms)
- Lethe's anti-anchor candidates → Acheron (does the false-form
  name collide with another coordinate?)
- Pollux's settled pairs → Aporia DR queue (escalate confirmed
  shape signals for primary-literature validation)
~30-50 LOC per edge.

**E6. Frontier-model meta-review tick.** Every 24h, a "Charon meta-
tick" loads the past day's artifacts, asks Claude/GPT-4o for an
honest external assessment ("what's noise, what's signal, what's
missing"), and writes a meta-analysis artifact. Forcibly injects
non-Charon perspective into the swarm's loop. The frontier
provider itself rotates per call to avoid persona monoculture.
~150 LOC; biggest non-trivial enhancement.

### Tier 3 — bigger architectural moves

**E7. Pollux cross-database scan (Mahler vs OEIS vs knots vs
genus2 vs modular forms).** Current within-Mahler pairs exhaust
candidate pool in ~5 weeks. Cross-database introduces genuine
substrate-novel coincidence-hunting per `project_microscope` memory.
~300 LOC + careful loader work per database.

**E8. HECATE-meta-test loader.** Per the scoping doc deferred:
permutation null on cluster signatures (shuffle generator_id ↔
kill_pattern N times; does observed cluster size still appear?).
Lights up the HECATE-* short-circuit rows as real attacks. ~100 LOC.

**E9. Stygian executor for POLLUX-* survivor pairs.** Today
POLLUX-* short-circuits with `stygian_pollux_survivor_loader_pending`.
A dedicated loader would re-load the same Mahler subsets via
`mahler.py`, run F1-F14 + F17 on the paired arrays directly, and
produce a real PROMOTED/REJECTED battery verdict on Pollux's
surviving correlations. ~120 LOC.

### Tier 4 — fundamental rethinks

**E10. Decouple agents from CharonAgent base.** Each agent re-
implements heartbeat / log_work / dr_enqueue from scratch (or
borrows from a thin shared lib, not inheritance). Eliminates the
single-bug-breaks-all-7 risk. ~500 LOC migration; defer unless
the shared-base failure mode actually bites.

**E11. Different rotation cadences per agent.** Today all 7 are
4-min equal slots. Lethe's catalog rotation only needs ~daily
firing (current models stable). Pollux at 28-min cycle. Hecate
at every-12h-when-ledger-grows. Asymmetric scheduling reduces
empty-tick volume. ~80 LOC in charon_loop.py + per-agent
"next_eligible_at" state.

**E12. Spawn 1-2 new layer-of-operation agents.** Per
feedback_agent_differentiation: each new agent must add a
genuinely-new layer, not duplicate existing. Concrete candidates:
- **Klymene** (memory archivist): walks all kill_ledger rows after
  N days and demotes resolved claims to a "settled archive,"
  shrinking Hecate's working set.
- **Ananke** (necessity / contradiction-checker): scans the
  substrate for two artifacts whose conclusions contradict;
  emits CONTRADICTION_CANDIDATE rows that demand Phylax
  adjudication.
- **Eos** (early-warning): watches the daemon's own memory
  growth, log file sizes, queue depths; emits ALARM rows when
  any swarm-internal metric trends toward failure.

---

## What I'd actually ship next (taking a stand)

Given the v0.6 patches already mitigate the immediate symptoms,
the highest-leverage remaining enhancements (ranked):

1. **E1 — Lethe attack-mode rotation.** Single largest unlock for
   the most-saturated agent. Modern LLMs get coarse status questions
   right; sub-question modes (year, qualifier, witness, adjacency)
   will produce real candidates again. ~60 LOC.

2. **E5 — cross-agent contamination edges (start with Acheron →
   Moros).** Cheapest monoculture mitigation; turns siloed agents
   into a graph. ~30 LOC for first edge.

3. **E3 — Stygian BL-C-002 (BSD) loader.** Doubles real-verdict
   output for Stygian. ~150 LOC + data engineering against
   Mnemosyne's EC inventory.

4. **E6 — frontier-model meta-review tick.** Forcibly injects
   non-Charon perspective. Biggest single anti-monoculture move
   even though it's largest LOC. ~150 LOC.

Stop ladder at #4. Beyond that, E10-E12 are bigger architectural
moves whose value depends on observed problems we haven't seen yet.

---

## Closing posture

The swarm is producing real substrate (1 Lehmer verdict/cycle,
2 Pollux survivor signals, 4 cross-generator canonical patterns
in Hecate). It's also producing too much null output (28 Lethe
ticks/day, ~24 Moros ticks/day at convergence_score 0.127 mean).
The v0.6 patches close the obvious circuit-not-firing bugs; the
remaining work is calibration (Tier 1) and architectural diversity
(Tier 2-4). Per the substrate-passive-consumer warning, the right
discipline is: ship one Tier-1 enhancement before adding any
Tier-3 work.

— Charon, 2026-05-25
