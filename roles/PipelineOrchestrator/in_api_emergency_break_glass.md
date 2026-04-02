# In Case of API Emergency, Break Glass

*When the NVIDIA API is down and the forge pipeline is dead, Claude Code IS the forge.*

---

## What This Is

The forge pipeline (Nous → Coeus → Hephaestus → Nemesis) normally uses the NVIDIA API (Qwen 397B) to generate reasoning tool code. When that API is down (timeouts, rate limits, outages), the pipeline produces nothing.

**The fix: Claude Code agents generate the code directly.** Same prompts, same validation, same battery — just a different code generator. This was discovered on 2026-03-28 when the NVIDIA API hit 91% timeout rate. Opus-generated tools scored 74% accuracy (highest in the library) vs 0.5% forge rate from the API.

---

## How It Works

### The Data Is Already There

Nous has **5,740+ saved responses** in `agents/nous/runs/*/responses.jsonl`. Each contains:
- `concept_names`: the 3 concepts
- `response_text`: the theoretical analysis
- `score.composite_score`: quality ranking

Coeus enrichments exist for most triples in `agents/coeus/enrichments/`.

**You don't need Nous or Coeus to run.** The data is saved. You just need to generate code.

### What To Do

1. **Read the coverage map** at `docs/coverage_map.md` — it shows which categories are covered and which are gaps.

2. **Read the multi-strategy forge design** at `docs/multi_strategy_forge.md` — it defines 7 frames:
   - Frame A (legacy): Structural Parser
   - Frame B (legacy): Constructive Computer
   - Frame C (legacy): Dynamics Tracker
   - Frame D (legacy): Judgment Calibrator
   - **Frame E (default): Computational** — parse → formal representation → compute → match
   - **Frame F: Adversarial Robustness** — structure-first, surface-invariant
   - **Frame G: Metacognitive** — calibrated uncertainty, knows what it doesn't know

3. **Pick gap categories** from the coverage map and forge tools targeting them.

4. **Launch parallel agents** — each agent writes 3 tools to `agents/hephaestus/forge_v7/` (or v8, v9, etc.).

### The Prompt Template

For each agent, use this structure:

```
You are Hephaestus forging reasoning tools. Write 3 Python files to
f:\Prometheus\agents\hephaestus\forge_v{N}\

FRAME {B/C/D}: {frame description from multi_strategy_forge.md}

For each tool: deterministic Python class (numpy + stdlib only), under 200 lines,
implements evaluate(prompt, candidates) -> list[dict] and confidence(prompt, answer) -> float.

Your tool must produce a score WITHOUT NCD. NCD may be an optional tiebreaker only.

TOOL 1: {concept1}_x_{concept2}_x_{concept3}.py
Gap target: {which gap category this targets}
Build: {specific solvers needed — list the actual algorithms}
Also implement ALL standard parsers: numeric float comparison, modus tollens,
transitivity, bat-and-ball algebra, all-but-N, negation scope, SVO parsing,
base rate neglect (Bayes), temporal ordering, direction composition, fencepost,
modular arithmetic, coin flip independence, parity, pigeonhole.

{repeat for TOOL 2 and TOOL 3}

Each tool must implement _meta_confidence() for Tier B traps.
Verify each file compiles with py_compile.
```

### Validation

After agents complete, run:

```python
cd f:/Prometheus/agents/hephaestus/src
python -c "
from test_harness import load_tool_from_file
from trap_generator_extended import generate_full_battery
from pathlib import Path
from collections import defaultdict

battery = generate_full_battery(n_per_category=2, seed=42)
v7 = sorted(Path('../forge_v7').glob('*.py'))

for py in v7:
    try:
        tool = load_tool_from_file(py)
        correct = total = 0
        for t in battery:
            try:
                r = tool.evaluate(t['prompt'], t['candidates'])
                if r and r[0]['candidate'] == t['correct']:
                    correct += 1
                total += 1
            except: total += 1
        acc = correct/total if total else 0
        status = 'PASS' if acc > 0.42 else 'fail'
        print(f'{status} {py.stem:50s} acc={acc*100:.0f}%')
    except Exception as e:
        print(f'ERR  {py.stem:50s} {e}')
"
```

NCD baseline is 42% accuracy / 46% calibration. Tools must beat both to be useful.

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

If the API is down and you need to forge tools:

```
1. Read docs/coverage_map.md → identify gaps
2. Launch 5 parallel agents, each targeting 3 gap triples
3. Each agent writes to forge_v{N}/
4. Run validation script above
5. Commit results
```

That's it. You ARE the API now.
