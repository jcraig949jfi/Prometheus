# In Case of API Emergency, Break Glass

*When the NVIDIA API is down and the forge pipeline is dead, use the Augment API fallback.*

---

## What This Is

The forge pipeline (Nous → Coeus → Hephaestus → Nemesis) normally uses the NVIDIA API (Qwen 397B) to generate reasoning tool code. When that API is down (timeouts, rate limits, outages), the pipeline produces nothing.

**The fix: Use Augment API (auggie-sdk) as a code generator.** Same prompts, same validation, same battery — just a different backend. This was discovered on 2026-03-28 when the NVIDIA API hit 91% timeout rate. Opus-forged tools (via Augment API) scored 74% accuracy (highest in the library) vs 0.5% forge rate from the degraded NVIDIA API.

---

## Two Modes: Fallback vs Primary

### Mode 1: Fallback (`--use-aggie-api`)
**When to use:** NVIDIA API is degraded (high timeout rate) but still partially responding.

```bash
run_forge_pipeline.bat --use-aggie-api --aggie-model sonnet4.5
```

- Try NVIDIA first on every forge attempt
- Only switch to Augment API when NVIDIA times out after all retries
- Conservative approach: preserves NVIDIA preference, uses Augment as a safety net
- Token burn: Low (only on NVIDIA failures)
- Status: "Augment API fallback ENABLED"

### Mode 2: Primary (`--force-aggie`)
**When to use:** NVIDIA API is completely down or you want to benchmark/test with Augment tokens.

```bash
run_forge_pipeline.bat --force-aggie --aggie-model sonnet4.5
```

- Skip NVIDIA API entirely
- Use Augment API for all forge attempts
- Aggressive approach: full pipeline continuity even if NVIDIA is unavailable
- Token burn: Continuous (every forge uses Augment)
- Status: "!!! AUGMENT API PRIMARY MODE (skip NVIDIA) !!!"

### Choosing a Model

Available models via auggie-sdk: `haiku4.5`, `sonnet4.5` (default), `sonnet4`, `gpt5`

- **haiku4.5:** Fast, cheap, lower quality. Good for rapid iteration / backlog clearing.
- **sonnet4.5:** Balanced. Recommended for production use (best forge quality observed so far).
- **sonnet4:** Earlier version; not recommended unless you have specific reason.
- **gpt5:** Premium model. Reserved for critical gaps or benchmark runs.

---

## How It Works: Automatic Fallback (Recommended for Most Cases)

**You don't need to manually launch agents or write code.**

When you run with `--use-aggie-api` or `--force-aggie`, Hephaestus automatically:

1. **Generates code prompts** from Nous concepts (using multi-frame architecture: Frame E/F/G default)
2. **Calls Augment API** when NVIDIA fails (fallback mode) or for all forges (primary mode)
3. **Validates** the generated code against the 89-category trap battery
4. **Logs results** to ledger.jsonl with reason (api_call_failed, validation errors, trap_battery_failed, or forged)

**Data is already saved:** Nous has 5,700+ responses; Coeus has 4,000+ enrichments. You just need to generate code.

### When Automatic Fallback Isn't Enough

If you need to **manually forge tools** for specific gaps (e.g., when NVIDIA is down AND Augment is also rate-limited):

1. **Read the coverage map** at `docs/coverage_map.md` — shows gaps and which categories need coverage.
2. **Read the multi-strategy forge design** at `docs/multi_strategy_forge.md` — defines 7 frames (E/F/G default).
3. **Write tools directly** using Frame E/F/G (computational architecture).
4. **Validate** against the battery using the test harness.

The tooling for this exists; ask if you need to activate manual forge mode.

---

## Current State (as of 2026-03-29)

### Coverage: 89/89 Tier 1 + 19 Tier 2 = 108 categories

All Tier 1 gaps are closed. The Tier 2 battery (19 computation-first categories) is live and should be used for validation of all new tools.

**Best tool:** `frame_e_v3_definitive` at **0.679 weighted score** (computation-first architecture). This overtook the previous best regex elite (0.654 weighted).

**197 passing tools total** across forge/, forge_v2/, forge_v5/, forge_v7/.

**The Squad (5 tools that cover 75 Tier 1 categories):**
1. Active Inference + FEP + Model Checking (40 cats)
2. Analogical Reasoning + Hebbian + FEP (7 cats)
3. Analogical Reasoning + Dialectics + Mechanism Design (1 cat)
4. Active Inference + Kolmogorov + FEP (1 cat)
5. Info Theory + Abductive Reasoning + Sensitivity Analysis (19 cats — the forge survivor)

**v7 tools (16 Opus-forged tools covering remaining Tier 1 categories):**
- 3 causal tools at 74% accuracy (best in library for single-category)
- Direction composition, fencepost, liar detection at 100%
- ToM information asymmetry, strategic deception cracked

**Tier 2 battery** — 19 categories requiring genuine computation (register machines, belief tracking, constraint satisfaction, recursive evaluation, counterfactual dependency, Bayesian updates, etc.). Regex tools score ~20% on these; computation-first tools score ~55%.

**For emergency forging, use Frame E prompt** (not Frame A/B). Frame E produces computation-first tools that parse prompts into formal intermediate representations and execute algorithms. This is the architecture that wins on weighted scoring.

### File Locations

| Path | What |
|------|------|
| `agents/hephaestus/forge/` | v1 original tools (362) |
| `agents/hephaestus/forge_v2/` through `forge_v7/` | CAITL-improved + Opus-forged |
| `agents/hephaestus/src/test_harness.py` | Validation + trap battery |
| `agents/hephaestus/src/trap_generator.py` | 28 base generators |
| `agents/hephaestus/src/trap_generator_extended.py` | 61 extended generators (89 total categories) |
| `agents/hephaestus/src/prompts.py` | Multi-frame prompt templates (A-G; E/F/G are default) |
| `agents/hephaestus/ledger.jsonl` | Global forge ledger |
| `agents/nous/runs/` | 5,740+ saved Nous responses |
| `agents/coeus/enrichments/` | 4,000+ Coeus enrichments |
| `docs/coverage_map.md` | Full coverage analysis |
| `docs/multi_strategy_forge.md` | Four-frame architecture |
| `docs/tool_library_census.md` | Complete library classification |

### The 89-Category Battery

```
Formal Logic (13) | Arithmetic (9) | Probabilistic (4) | Temporal (12)
Causal (10) | ToM (10) | Compositional (8) | Spatial (3) | Set Theory (2)
Cognitive Biases (7) | Meta-Reasoning (7) | Linguistic (6) | Trick (1)
```

Tier A (parsing, 77 cats): deterministic correct answer from structure.
Tier B (judgment, 16 cats): recognizing ambiguity, presupposition, insufficiency.

### Key Findings

- **344 tools collapse to 19 unique behavioral profiles** (94.5% redundancy)
- **The monoculture was caused by the pipeline**, not the concepts — same NCD-backbone architecture regardless of concept triple
- **Multi-frame forge fixes this** — different frames (structural/constructive/dynamics/judgment) produce different architectures
- **Opus-forged tools outperform API-forged tools** (74% vs 54% best accuracy)
- **Tier B honesty: 0.993** (tools correctly signal uncertainty on ambiguous questions)
- **Tier A honesty: 0.100** (tools overconfident on parsing traps they get wrong)

---

## Quick Start

### Scenario A: NVIDIA is Degraded (High Timeout Rate)
```bash
run_forge_pipeline.bat --use-aggie-api --aggie-model sonnet4.5
```
- Pipeline continues with Augment as safety net
- Low token burn (Augment only used when NVIDIA fails)
- Monitor ledger.jsonl: watch for api_call_failed entries to decrease

### Scenario B: NVIDIA is Down Completely
```bash
run_forge_pipeline.bat --force-aggie --aggie-model sonnet4.5
```
- Full pipeline continuity via Augment API
- Continuous token burn
- Same forge quality as fallback mode
- Leave running until NVIDIA recovers

### Scenario C: NVIDIA + Augment Both Down (Emergency Mode)
1. Read `docs/coverage_map.md` → identify gaps
2. Manually launch 2-3 agents to write tools to `forge_v9/`
3. Run validation battery (ask for test harness setup)
4. Commit results

**In all cases: the ledger tracks everything.** Check `agents/hephaestus/ledger.jsonl` for the reason each attempt succeeded or failed.
