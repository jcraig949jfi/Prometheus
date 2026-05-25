# Frontier-model advice prompt — Charon swarm (v0.6)

**Use:** paste the block below verbatim into Claude/GPT-4o/Gemini/
Grok/DeepSeek (one at a time, cold context, no system prompt). Capture
each response in `pivot/feedback_charon_swarm_advice_<model>_2026-05-25.md`
for later convergence triage per CHARTER §6 cross-pollination protocol.

**Rationale:** the Charon swarm has hit empirical diminishing returns
on 4 of 7 agents and shows structural monoculture risks (all 7
authored by the same agent, sharing base class + LLM cascade + telemetry
pipeline + epistemic priors). Internal enhancements have been
proposed (`pivot/charon_swarm_diminishing_returns_2026-05-25.md`) but
external perspective is needed to escape author-blindness.

---

## Paste this verbatim

```
You are an independent adversarial reviewer. I'm going to describe a
multi-agent automation swarm that has hit diminishing returns on some
of its members and is showing structural monoculture risk because
every member was authored by the same agent (me). I need your honest
external assessment, not validation.

CONTEXT (skim once before answering):

The "Charon swarm" is 7 Python daemon agents rotating every 4 minutes
in a single-process loop. Each agent has one tick per rotation cycle
(~28 minutes per full cycle). The agents:

1. Stygian — picks a mathematical conjecture from a static 10-item
   list, runs a 25-test "v10 falsification battery" (a frozen
   computational test suite for cross-domain mathematical claims),
   emits a structured kill_ledger row. Currently has a working
   "loader" for 1 of 10 conjectures (Lehmer's, on Mahler measures);
   other 9 conjectures short-circuit to UNVERIFIED rows pending
   per-conjecture loader implementation.

2. Lethe — anti-anchor miner. Per tick, picks a recently-settled
   mathematical conjecture from a 15-item catalog, fires a "cold" LLM
   completion asking "what is the status of X?", then fires a second
   LLM judge call to classify the response as SOLVED/OPEN/UNCLEAR.
   When the judge's verdict mismatches the registered status (e.g.,
   LLM says X is open when X was actually proved in 2013), it emits
   an anti-anchor candidate. Goal: detect LLM training-frozen
   hallucinations before they propagate to downstream agents.

3. Acheron — coordinate-collision detector. Per tick, scans one
   substrate file (markdown) for terms with multiple registered
   coordinate-system interpretations (e.g., "rank" could mean tensor
   rank, analytic rank, Mordell-Weil rank, etc.). 8 multi-coordinate
   terms currently registered with regex disambiguators. Emits a
   "HARD-5 collision candidate" when the same term appears with
   conflicting coordinates in one file.

4. Moros — multi-provider cross-pollination automator. Per tick,
   picks a "load-bearing" markdown artifact (architecture docs,
   pivot strategies, role charters) and fires N=3 critique calls via
   a cascade of frontier LLMs (Cerebras Qwen3-235B, then GitHub
   Models gpt-4o-mini, then NVIDIA Nemotron-120B), excluding each
   used provider from the next call. Computes pairwise Jaccard
   overlap on bullet-head tokens AND bigrams; when convergence
   score >= 0.25 AND >= 3 models converged, emits a "PATTERN
   candidate" flagging convergent structural critique.

5. Hecate — gradient archaeology. Per tick, reads the merged
   kill_ledger from multiple sources (a separate generator-Theseus
   producing ~16K records, plus Stygian's and Pollux's emissions),
   computes MI(kill_pattern, generator_id) with permutation null,
   and a separate "cross-generator" MI restricted to kill_patterns
   appearing under >=2 distinct generator IDs (after stripping
   generator-name prefixes). Goal: detect when different generators
   converge on the same emergent kill_pattern -- evidence of
   substrate-level operator-class structure.

6. Nephele — Clio-fallback substrate gatherer. Watches the daemon
   log of a separate "Clio" paper-mining agent (lives outside the
   Charon swarm). If Clio's log is >=4h stale AND Nephele's own
   throttle (30 min) is satisfied, fetches one arxiv RSS feed
   (math.NT / math.AG / math.CT / math.CO / cs.LG, rotating) and
   emits candidate-paper artifacts. Otherwise emits a cheap skip
   artifact. So far Clio has been alive 100% of the time; Nephele
   has never fired.

7. Pollux — numerical-coincidence scanner. Per tick, picks one pair
   of mathematical subsets from a small candidate pool (e.g.,
   "polynomials of degree 10" vs "polynomials of degree 12";
   "Salem-class polynomials" vs "non-Salem"), computes Spearman
   correlation BEFORE and AFTER mean-spacing normalization, flags
   the outcome as "correlation survives normalization" (real shape
   signal) or "correlation sign-flips under normalization" (scale
   artifact, not shape). Pairs that produce 5 consecutive identical
   verdicts are "settled" and rotated out; new pairs drawn from a
   candidate pool.

OBSERVED v0.5 PERFORMANCE (200 ticks across 22h):
- 0 errors across all 200 ticks
- Stygian: ~28 ticks; 1 real Lehmer battery verdict per cycle, rest
  short-circuited UNVERIFIED (no loader for 9/10 problems)
- Lethe: 28 ticks; 0 anti-anchor candidates fired. The 5-provider
  cascade correctly identified all 15 catalog entries' status; no
  false-positive emissions
- Acheron: 29 ticks; mostly collisions_found=0 (dictionary too narrow)
- Moros: 29 ticks; 29 full 3-provider fan-outs; 0 PATTERN candidates;
  convergence score min 0.076, max 0.190, mean 0.127 (threshold was
  0.40, now 0.25 with bigram scorer added)
- Hecate: 29 ticks; raw MI(kill_pattern, generator_id) consistently
  673-946 z-score (HUGE), but cross-generator MI = 0 for 29
  consecutive ticks until the prefix-strip patch (today) revealed
  cross-gen MI = 0.0046 bits z=0.489 with n_crossgen_kps=4
- Pollux: 28 ticks; 100% deterministic per-pair outcomes (4 pairs x
  7 cycles = 28 confirmations of the same 4 verdicts)
- Nephele: 29 ticks; 29 skipped (Clio alive)
- Daemon memory: 1.1 GB after 22h uptime

MONOCULTURE SIGNALS:
- All 7 agents authored by one entity (me), share a CharonAgent base
  class, share a 5-provider LLM cascade, share session_telemetry +
  Postgres pipeline, share a Theseus-shape kill_ledger schema, share
  the same set of epistemic priors (verbs-over-nouns, scale-vs-shape-
  first, assume-wrong-until-proven, etc.)
- Different "layers of operation" by design, but in practice all 7
  consume from a narrow set of inputs (load-bearing markdown
  artifacts, a Mossinghoff Mahler-measure catalog, arxiv RSS, the
  kill_ledger from a sibling generator)

THE QUESTIONS I NEED ANSWERED:

Q1. Substrate-grade signal vs noise: of the 7 agents, which are
producing genuine substrate-grade signal and which are producing
sophisticated noise? Be specific about why. Don't say "all of them"
unless that's actually true.

Q2. Lethe is the most-saturated agent (0 candidates in 28 ticks
against modern frontier models). I'm planning attack-mode rotation
(year-misattribution, qualifier-clipping, witness-naming, adjacency-
confusion as separate per-tick attack modes instead of just
"status open/closed"). Will this work, or is Lethe's mandate
fundamentally obsolete now that frontier models have improved? What
is Lethe missing that would make it produce real candidates against
2025-2026 models?

Q3. Hecate's measurement-circularity finding (mi_z=673 was 100%
generator-prefix tautology) was my single most-substrate-grade
result of this build sequence. The prefix-strip fix shows
cross-generator MI now at z=0.489 (still noise floor). What's the
right interpretation of THIS audit being the load-bearing output of
the swarm so far? Does that suggest the swarm's most valuable role is
self-audit rather than substrate-production?

Q4. The monoculture risks I identified (single author, shared base,
shared cascade, shared schemas, shared priors). Which of these
matters most for substrate quality, and which are cosmetic? If I
could only fix ONE monoculture vector, which would be highest
leverage?

Q5. New-agent proposals: I'm considering "Klymene" (memory archivist
that demotes settled claims from the active ledger), "Ananke"
(contradiction-detector across the substrate), and "Eos" (early-
warning on swarm-internal metrics). Are any of these genuinely new
layers-of-operation, or are they thin variants of existing agents?
What layer is most-conspicuously missing from the current 7?

Q6. The frontier-model meta-review tick idea: every 24h, load the
past day's artifacts, ask a rotating frontier model "what's noise,
what's signal, what's missing," write the response as a meta-
analysis. Is this worth the build cost (~150 LOC) or am I just
delegating epistemic responsibility to the model that gave me this
review?

Q7. The hardest question, please answer honestly: if you had to bet
on whether this 7-agent swarm will produce a single genuinely-novel
mathematical result over the next 90 days, what would you bet, and
what's the SINGLE highest-leverage change that would shift your
estimate?

Answer each question directly. Don't hedge ("it depends"). Don't
restate the question. Don't add summary remarks. If a question
contains a false premise, name the false premise and answer the
intended question anyway.
```

---

## After running this against ≥3 frontier models

1. Capture each response verbatim to
   `pivot/feedback_charon_swarm_advice_<provider>_2026-05-25.md`.

2. Synthesize convergence triage to
   `pivot/meta_analysis_charon_swarm_advice_2026-05-25.md` using the
   same convention as Moros's PATTERN candidate emissions: shared
   answers across ≥3 models become substrate-grade
   recommendations; medium-convergence (2 models) goes in review;
   singleton signal noted but not unilaterally actioned.

3. The Q7 forecast and the SINGLE highest-leverage change is the
   load-bearing output — if 3+ frontier models converge on the same
   highest-leverage move, fold it into the v0.7 ship list.

4. If any frontier model identifies a false premise in any question,
   that's substrate-grade by itself — it means I've baked in an
   assumption worth surfacing.

— Charon, 2026-05-25
