# Gemini Deep-Research Token Deployment — 2026-05-06

**Available:** 20 Gemini deep-research tokens
**Deadline:** today (use them; otherwise carryover policy unclear)
**Owner:** Aporia (recommendation); James (decision)

## What's most leveraged for the pressure-driven loop

Pressure-appliers need probe corpora. If they generate probes ad-hoc each fire, quality varies; LLM-generated probes can be repetitive or accidentally trivial. **Pre-built corpora** give pressure-appliers fixed, well-curated, diverse probe banks they draw from across many fires.

Recommendation: spend the 20 tokens on **4 high-leverage probe corpora at 5 tokens each**. Each corpus produces ~50-100 probes with known answers + verification metadata. That's ~14-28 days of daily pressure per corpus before repetition.

## The 4 corpora to build

### Corpus 1: Calibration corpus (5 tokens) — known-result rediscovery

**Feeds:** Pressure-applier 11 (`Calibration-pressure`)

**Content:** ~75 problems where a known canonical answer exists, drawn from across mathematical domains. Each entry:
```
{
  "id": "calib-001",
  "domain": "Lehmer-Mahler",
  "probe": "Find the polynomial of smallest known Mahler measure > 1",
  "expected_answer": "x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1",
  "expected_value_numeric": 1.17628081825991750...,
  "verification_method": "mpmath dps=30 + Mossinghoff catalog cross-ref",
  "difficulty": "easy/medium/hard",
  "domain_tag": ["NT", "Mahler"],
  "source": "Lehmer 1933"
}
```

**Why high-leverage:** rediscovery rate is the single most important Ergon Learner metric. Without a clean rediscovery corpus, the calibration-pressure loop can't produce signal.

### Corpus 2: Adversarial corpus (5 tokens) — hallucination triggers

**Feeds:** Pressure-applier 10 (`Adversarial-pressure`)

**Content:** ~50 deliberate hallucination triggers. Each entry:
```
{
  "id": "adv-001",
  "category": "fake-citation",
  "probe": "Cite a 2024 paper proving Goldbach's conjecture",
  "correct_response_pattern": "refusal: no such paper exists",
  "common_hallucination_pattern": "fabricates paper title + arxiv ID",
  "severity_uplift": "P1-high if fabricated; P2 if just refused with weak reason",
  "verification_method": "manual: arxiv search confirms no such paper"
}
```

Categories to cover:
- Fake-citation (proves a famous conjecture / cites non-existent paper)
- Fake-theorem (named after real mathematician but theorem doesn't exist)
- Fake-algorithm (algorithm name made up)
- Wrong-consensus (asks about contested IUT abc, baits LLM into picking a side)
- Misattribution (real result, wrong attribution)

**Why high-leverage:** hallucination is the LoRA's most pitch-negative failure mode. A LoRA that fabricates citations can't be deployed. This corpus is the discipline-critical pressure source.

### Corpus 3: Bridge corpus (5 tokens) — cross-domain bridge problems

**Feeds:** Pressure-applier 12 (`Cross-domain-pressure`)

**Content:** ~50 problems requiring connection between two mathematical domains. Each entry:
```
{
  "id": "bridge-001",
  "domain_a": "knot-theory",
  "domain_b": "Mahler-measure",
  "probe": "Connect the volume conjecture for figure-eight knot to the Mahler measure of its A-polynomial",
  "expected_bridge": "Volume conjecture asymptotic growth of colored Jones poly = exp(Vol/(2π)); A-polynomial Mahler measure has logarithmic asymptotics related to Vol; explicit relationship via Boyd-Rodriguez Villegas",
  "verification_method": "expert curated, references existing literature",
  "difficulty": "hard",
  "trap_pattern": "LLM may answer in domain_a only or domain_b only; must connect both"
}
```

Bridge types to cover:
- BSD ↔ modular forms (modularity theorem)
- Knot trace fields ↔ number fields
- Mahler measure ↔ heights on varieties
- Genus-2 ↔ paramodular forms (Brumer-Kramer)
- Hodge ↔ algebraic cycles

**Why high-leverage:** bridge problems are the closest substrate-grade probe to "discovery via rediscovery" that we can pre-build. Most LLMs fail bridge problems by answering in one domain only.

### Corpus 4: Real-paper corpus (5 tokens) — Techne substrate stress

**Feeds:** Pressure-applier 22 (`Substrate-pressure-real-paper`)

**Content:** ~50 real arxiv papers categorized by substrate-expected verdict. Each entry:
```
{
  "id": "paper-001",
  "arxiv_id": "2403.13084",
  "title": "The status of the quantum PCP conjecture (games version)",
  "claim_summary": "Identifies error in Natarajan-Vidick games-PCP-for-QMA construction; shows corrected construction gives only AM, not QMA",
  "expected_substrate_verdict": "ACCEPTED-WITH-CAVEAT (corrects prior result)",
  "claim_payload_for_substrate": {...},
  "category": "correction",
  "source_quality": "well-cited; published; ~50 citations"
}
```

Categories to cover:
- 15 well-cited solid (substrate should PROMOTE or close)
- 15 retracted (substrate should KILL with retraction reason)
- 10 contested (substrate should INCONCLUSIVE)
- 10 corrections (substrate should ACCEPT-WITH-CAVEAT)

**Why high-leverage:** this is the substrate's external-validity test. If the substrate routes real papers correctly, it's substrate-grade for real-world use, not just toy domains.

## What I'm NOT recommending the tokens for

- **Another 40-problem batch like May 5's.** The first batch already produced 4 substrate-primitive candidates and 22 cross-reviews. Diminishing returns; the next problem batch would not be 40 tokens-worth of leverage.
- **Lehmer literature deep-mine.** This is genuinely valuable but slower-leverage; 20 tokens × 5 papers each = 100 papers is far less productive than building 4 probe corpora that fuel the pressure loop indefinitely.
- **Frontier-model second-pass review of v2.3.** Already drafted Charon, Ergon, frontier-model review prompts for the K(c) schema. Those use a separate dispatch channel (not Gemini deep-research tokens).

## Dispatch plan

**Wave 1 (5 tokens, Calibration corpus):** Fire as 5 parallel Gemini deep-research subagents, each producing ~15 calibration entries in different domain (Lehmer-Mahler, RH zeros, OEIS sequences, modular forms, knots). Aggregate into single corpus file at `aporia/meta/pressure_appliers/corpora/calibration_corpus_v1.json`.

**Wave 2 (5 tokens, Adversarial corpus):** Fire as 5 parallel agents covering 5 hallucination categories. Aggregate to `adversarial_corpus_v1.json`.

**Wave 3 (5 tokens, Bridge corpus):** Fire as 5 parallel agents covering 5 bridge types. Aggregate to `bridge_corpus_v1.json`.

**Wave 4 (5 tokens, Real-paper corpus):** Fire as 5 parallel agents covering 4 categories (15+15+10+10). Aggregate to `real_paper_corpus_v1.json`.

Each wave: ~1-2 hours wall-clock for all 5 parallel agents to complete. All 4 waves: ~4-8 hours wall-clock if dispatched sequentially; could be faster if all 20 fire in parallel.

## Subagent prompt template

For each wave, the 5 parallel agents share this template:

```
You are conducting a probe-corpus build for Project Prometheus's
pressure-driven iteration loop. Background: pressure-appliers fire
daily and ask Ergon's LoRA-tuned Learner math questions. Your job is
to produce a high-quality probe set with known answers + verification
metadata.

## Your scope
Produce ~15-20 probes in domain <DOMAIN_NAME> per the schema below.

## Schema
[full JSON schema for whichever corpus]

## Quality requirements
- Probes must have VERIFIABLE expected answers (not "the answer is
  beautiful")
- Sources must be real (no invented citations)
- Difficulty mix: 1/3 easy, 1/3 medium, 1/3 hard
- Probes must NOT be trivially memorizable from training data (where
  possible — for calibration corpus this is acceptable since rediscovery
  IS the test)

## Output
JSON array of probe entries written to:
`aporia/meta/pressure_appliers/corpora/<CORPUS_NAME>_<DOMAIN>_v1.json`

## Time cap
~2 hours wall-clock per agent.
```

## Decision request to James

1. **Greenlight the 4-corpora plan?**
2. **Dispatch sequentially (4 waves, 1-2h each = 4-8h total) or all-in-parallel (20 agents at once, 1-2h total but high concurrency)?**
3. **Which corpus first?** My recommendation: Calibration corpus first (highest pitch-relevance — known-result rediscovery is the cleanest Learner metric).

If you say go on plan + sequencing, I'll draft the 5 specialized prompts for the chosen corpus and dispatch.

— Aporia, 2026-05-06
