# Prometheus x ruvnet: An Agentic Evolution Strategy

*Draft proposal — March 23, 2026*
*For James's review before any implementation begins*

---

## The Argument in One Paragraph

Prometheus has built a research pipeline that works: seven agents scan the frontier, harvest knowledge, score relevance, synthesize briefs, and archive tools. But these agents are **scripted orchestration** — subprocess chains with no memory, no self-correction, no ability to learn from experimental outcomes. Meanwhile, rUv (github.com/ruvnet) has built production-grade agentic infrastructure — swarm coordination, self-learning feedback loops, persistent multi-layer memory, and MCP-native tool exposure — that solves exactly the problems Prometheus will hit next. The proposal: adopt ruvnet's architectural patterns (not his code) to evolve Pronoia from a cron job into an autonomous research intelligence, running safely on NemoClaw models where the blast radius is contained.

---

## Part 1: What We Are vs. What They Are

### Prometheus — Depth Without Autonomy

Prometheus is a **vertical research stack**. Every piece serves one question: *how do reasoning circuits work inside language models?*

The methodology is honest science:
- CMA-ES evolves steering vectors in the residual stream (Ignis)
- A five-test falsification battery rejects 65% of candidates
- Five frontier models (the Titan Council) review findings adversarially
- The null result is reported cleanly: bypass, not precipitation, at scales below 4B

The agent pipeline (Pronoia) is real but limited:
- **Sequential subprocess chains** — Eos runs, then Aletheia runs, then Skopos scores, then Metis synthesizes
- **No inter-agent communication** — Metis reads Skopos's file output; they never negotiate
- **No persistent memory** — each cycle starts fresh; no agent remembers what it learned yesterday
- **No self-correction** — if Eos returns garbage, the pipeline dutifully processes garbage
- **No experiment planning** — agents scan and report, but never propose or execute experiments autonomously

This is fine for where we are. It got us here. But the next phase — where we need agents that *design experiments*, *interpret results*, and *redirect the search* — requires architecture we don't have.

### ruvnet — Breadth Without Depth

rUv builds **horizontal agent infrastructure**. His work is entirely at the orchestration and deployment layer:

| Project | What It Does | Stars |
|---------|-------------|-------|
| **ruflo** (Claude-Flow) | Multi-agent swarm orchestration — 60+ agents, swarm topologies, consensus, task routing | 23,800 |
| **agentic-flow** | Multi-provider agent framework — 66 agents, 213 MCP tools, SONA self-learning | 564 |
| **SAFLA** | Self-Aware Feedback Loop Algorithm — persistent memory + meta-cognitive self-reflection | — |
| **RuVector** | Self-learning vector database — HNSW + GNN refinement, 46 attention mechanisms | 3,550 |
| **onnx-agent** | DSPy-based model training pipeline with ONNX export | — |
| **SPARC** | Specification-Pseudocode-Architecture-Refinement-Completion methodology | — |

He has **zero presence** in mechanistic interpretability. No SAEs, no activation patching, no causal tracing. His "neural" components are infrastructure for agent coordination, not for understanding model internals.

### The Complementarity

This is why the pairing works:

| Capability | Prometheus | ruvnet |
|-----------|-----------|--------|
| Understanding model internals | Deep | None |
| Agent orchestration patterns | Basic (subprocess) | Production-grade (swarm) |
| Self-learning from results | None | Core feature (SAFLA, SONA) |
| Persistent agent memory | None | Four-layer architecture |
| Experiment design automation | None (human-gated) | Pattern exists (ReasoningBank) |
| MCP integration | None | 213 tools |
| Inter-agent negotiation | None | Consensus protocols |
| Falsification methodology | Rigorous | None |

We don't need his code. We need his **patterns**.

---

## Part 2: What We Can Steal (Conceptually)

### Pattern 1: Self-Learning Feedback Loops (from SAFLA)

**The problem we have:** Ignis runs CMA-ES, discovers steering vectors, the falsification battery rejects 65%. The rejection data goes nowhere. Next run, CMA-ES explores the same dead regions of activation space.

**What SAFLA does:** Four-stage cycle: Experience -> Learn -> Adapt -> Improve. A meta-cognitive engine evaluates which strategies worked and adjusts future behavior. ReasoningBank stores successful patterns and retrieves them pre-task.

**What this looks like for Prometheus:**

```
Ignis runs CMA-ES generation N
  → Falsification battery tests survivors
  → Results stored in ExperimentMemory:
    - "Layer 21, vectors aligned with anti-CoT direction: 80% pass noise gate"
    - "Layer 14, random-looking vectors: 95% fail sign-flip test"
  → Next CMA-ES generation initializes with learned priors:
    - Bias search toward anti-CoT-aligned subspace at layer 21
    - Avoid layer 14 entirely (dead zone at this scale)
    - Adjust sigma based on manifold dimensionality from previous run
```

This is **not** changing CMA-ES itself. It's wrapping it in a learning loop that remembers what the search landscape looks like.

### Pattern 2: Swarm Topology for the Titan Council (from ruflo)

**The problem we have:** The Titan Council is manually orchestrated. James writes a prompt, sends it to five models, reads five responses, synthesizes by hand. The Phalanx strategy works but doesn't scale.

**What ruflo does:** Swarm topologies — hierarchical (queen-worker), mesh (peer-to-peer), ring (pipeline). Consensus mechanisms (Raft, weighted voting). Anti-drift checkpoints.

**What this looks like for Prometheus:**

```
Skopos detects high-relevance entity (score 4+)
  → Generates Titan Council prompt (already built)
  → Dispatches to 5 NemoClaw models in parallel (mesh topology)
  → Responses collected and cross-referenced:
    - Convergence detection: did 3+ models independently suggest the same experiment?
    - Divergence flagging: where do they disagree? That's where uncertainty lives.
    - Weighted voting: Claude gets 2x weight on interpretability, DeepSeek on architecture
  → Synthesized recommendation stored in ExperimentQueue
  → Human reviews queue, approves/rejects/modifies
```

The Titans already converge independently (the nullspace finding proved this). Automating the convergence detection and synthesis is the next step.

### Pattern 3: Four-Layer Memory Architecture (from SAFLA/RuVector)

**The problem we have:** Every Pronoia cycle is stateless. Metis doesn't know that yesterday's brief already flagged the same paper. Skopos doesn't know that a technique it scored 2 last week has since appeared in three more papers and should be rescored.

**What SAFLA provides:**

| Layer | Purpose | Prometheus Application |
|-------|---------|----------------------|
| **Vector** | Semantic similarity retrieval | Store activation pattern signatures; retrieve similar past experiments |
| **Episodic** | Event sequences | "Last time we tried layer 21 injection on Qwen-1.5B, the dose-response was flat" |
| **Semantic** | Knowledge graphs | Aletheia's knowledge graph, enriched with experimental outcomes |
| **Working** | Active context with attention | Current cycle's findings + most relevant memories |

This isn't replacing Aletheia's SQLite. It's adding a layer above it that connects *literature knowledge* to *experimental outcomes* to *search strategy*.

### Pattern 4: MCP Tool Exposure (from agentic-flow)

**The problem we have:** Ignis, Arcanum, and the analysis tools are Python scripts invoked via `subprocess.run()`. If we want Claude Code to orchestrate experiments, it has to shell out.

**What MCP provides:** Model Context Protocol servers expose tools as structured APIs that Claude Code can call directly, with typed parameters and structured results.

**What this looks like:**

```python
# Instead of:
subprocess.run(["python", "ignis/src/dose_response.py", "--genome", path])

# Claude Code sees a tool:
# tool: ignis_dose_response
# params: {genome_path: str, scales: list[float]}
# returns: {peak_scale: float, is_artifact: bool, curve_type: str}
```

This is the bridge between "James runs experiments manually" and "Claude Code proposes and executes experiments with human approval."

---

## Part 3: The NemoClaw Question

### Why NemoClaw Is the Right Sandbox

The user asked about moving toward agentic models on NemoClaw. Here's my assessment:

**The case FOR:**

1. **Blast radius containment.** NemoClaw runs in NVIDIA's cloud, sandboxed. An agentic model that makes bad decisions can't corrupt local data, burn API credits on other services, or push bad commits. The sandbox is the safety net while we learn what autonomous research looks like.

2. **Access to scale.** Qwen 3.5-397B (17B active) is available on NemoClaw. If RPH is scale-dependent (and the 4B self-correction data suggests it is), the agentic model doing the *thinking* about experiments should be the biggest model we can reach. Use NemoClaw's 397B for hypothesis generation and experiment design; use local 3B-4B for actual activation probing.

3. **Cost = zero.** NemoClaw API access is free. The Titan Council currently uses Nemotron 120B, Cerebras Qwen3-235B, and Groq Llama 3.3-70B — all free tiers with rate limits. Adding NemoClaw models to the rotation costs nothing.

4. **OpenAI SDK compatible.** The existing `call_llm()` cascade pattern in every agent already works with NemoClaw. Adding new models is a config change, not a code change.

**The case AGAINST (and mitigations):**

1. **Rate limits unknown.** We don't know NemoClaw's throttle thresholds. An agentic loop that makes 50 LLM calls per cycle could hit walls fast.
   - *Mitigation:* Start with the ASSESS pattern (one LLM call per batch of 30 entities). Monitor 429s via the audit stage. Scale up gradually.

2. **Latency.** Cloud inference adds 2-10 seconds per call. An agentic planning loop with 5 sequential LLM calls adds 10-50 seconds.
   - *Mitigation:* Acceptable for research. We're not serving users in real-time. A 2-minute planning phase that produces better experiments is worth it.

3. **No fine-tuning.** NemoClaw models are inference-only. We can't train SAFLA-style adaptation into them.
   - *Mitigation:* Use prompt-based memory injection instead. Load relevant ExperimentMemory into the system prompt. This is what Metis already does with `load_project_context()`.

4. **Dependency on NVIDIA.** If NemoClaw shuts down or changes terms, we lose the agentic backbone.
   - *Mitigation:* The cascade pattern already exists. Fall back to Cerebras/Groq. The agentic patterns work with any LLM provider.

### My Recommendation

**Yes, move toward agentic models on NemoClaw.** Specifically:

- **Use Qwen 3.5-397B** for experiment design and hypothesis generation (the "research director" role)
- **Use Nemotron 120B** for entity scoring and synthesis (the "analyst" role — what Skopos and Metis already do)
- **Keep local GPU** for actual mechanistic work (TransformerLens probing, activation extraction, CMA-ES)
- **Keep the cascade** — if NemoClaw is down, fall back to Cerebras, then Groq

The split is clean: **NemoClaw thinks, local GPU experiments.**

---

## Part 4: The Proposed Architecture — "Pronoia v2"

### Phase 1: Memory Layer (Week 1)

Add persistent experimental memory to Pronoia. Not a full SAFLA implementation — a SQLite-backed memory that connects literature (Aletheia) to experiments (Ignis results) to strategy (what to try next).

```
ExperimentMemory (SQLite)
├── experiments       # What we ran, what happened
│   ├── id, model, layer, vector_hash, fitness, falsification_results
│   └── outcome: "bypass" | "precipitation" | "artifact" | "inconclusive"
├── strategy_log      # What we decided and why
│   ├── id, timestamp, decision, rationale, outcome
│   └── "Tried layer 21 because Titan Council converged on it — result was bypass"
└── search_priors     # Learned biases for CMA-ES
    ├── model, layer, subspace_direction, success_rate
    └── "Anti-CoT aligned subspace at layer 21: 80% pass falsification"
```

**What changes:** Metis and Skopos load ExperimentMemory alongside project context. The LLM sees not just "what's new in the literature" but "what we've tried and what happened."

### Phase 2: Automated Titan Dispatch (Week 2)

Evolve Skopos's `--generate-prompt` into a full Titan dispatch system:

1. Skopos generates prompt (already built)
2. Dispatch to 3-5 NemoClaw models in parallel
3. Collect responses
4. Run convergence detection: extract specific experiment proposals, find overlaps
5. Store synthesized recommendations in ExperimentQueue
6. Flag for human review

**Human gate:** Nothing executes without James approving it. The system *proposes*, James *decides*. This matches the autonomy model already in place.

### Phase 3: Experiment Proposal Loop (Week 3-4)

Add a new agent — **Athena** (goddess of strategic warfare and practical wisdom) — that:

1. Reads ExperimentMemory (what we've tried)
2. Reads Skopos alignment scores (what's relevant from the literature)
3. Reads latest Ignis results (what the data says)
4. Calls NemoClaw 397B with a structured prompt:

```
Given our experimental history, current findings, and new literature:
1. What is the highest-ROI experiment we haven't tried?
2. What specific parameters should we use? (model, layer, vector initialization)
3. What would falsify the hypothesis this experiment tests?
4. What should we expect to see if it works?
```

5. Stores proposal in ExperimentQueue with estimated VRAM, runtime, and expected outcome
6. James reviews, approves, and Ignis executes

### Phase 4: MCP Tool Layer (Week 4+)

Wrap key Ignis and analysis tools as MCP servers so Claude Code can orchestrate them directly:

- `ignis_evolve` — Run CMA-ES with specified parameters
- `ignis_falsify` — Run falsification battery on a genome
- `ignis_dose_response` — Run norm sweep
- `analysis_sae_decompose` — Decompose a vector through SAE
- `analysis_cot_patch` — Run CoT patching experiment

This is the bridge to full Claude Code orchestration. But it's Phase 4 because Phases 1-3 provide value without it.

---

## Part 5: What NOT to Do

### Don't adopt ruvnet's code

His frameworks are TypeScript/Rust, designed for web-scale deployment. Prometheus is Python, designed for research. The impedance mismatch is total. Adopt the **patterns**, not the **implementation**.

### Don't build a full swarm

ruflo's 60-agent swarm is enterprise infrastructure. Prometheus has 7 agents with clear roles. Adding swarm consensus, Byzantine fault tolerance, and gossip protocols to a research pipeline is over-engineering. We need memory and feedback loops, not distributed consensus.

### Don't remove the human gate

The autonomy model is correct: Pronoia proposes, James decides. The goal isn't full autonomy — it's **informed autonomy**. The system should surface the best experiment to run next, with evidence and expected outcomes. James decides whether to run it.

### Don't over-harden

Per the existing feedback memory: "Don't over-harden; speed of thought + HITL + Titans-in-the-loop is the accelerator." The value is in fast iteration, not bulletproof infrastructure.

---

## Part 6: Concrete First Steps

If this strategy makes sense, here's the immediate implementation order:

### Step 1: Add NemoClaw 397B to the provider cascade
- Add `qwen/qwen3.5-397b-a17b` as first-choice provider in `call_llm()` across all agents
- Monitor rate limits via the audit stage
- Takes 30 minutes

### Step 2: Build ExperimentMemory schema
- SQLite database at `agents/pronoia/data/experiment_memory.db`
- Three tables: experiments, strategy_log, search_priors
- Populate from existing Ignis results (JSON files in `ignis/src/results/`)
- Takes 2-3 hours

### Step 3: Wire ExperimentMemory into Metis and Skopos
- Add to `load_project_context()`: latest 5 experiments and their outcomes
- Skopos scoring gets "have we tested this?" context
- Takes 1 hour

### Step 4: Automated Titan Dispatch
- Extend Skopos `--generate-prompt` to send to multiple NemoClaw models
- Add convergence detection (simple: extract experiment names, count overlaps)
- Write proposals to `docs/experiment_queue/`
- Takes 3-4 hours

### Step 5: Athena agent (experiment proposer)
- New agent at `agents/athena/src/athena.py`
- Reads memory + scores + results → proposes experiments
- Human-gated: proposals queued, not executed
- Takes 4-6 hours

---

## The Bottom Line

ruvnet has solved problems we're about to have. His self-learning feedback loops, multi-layer memory architecture, and swarm coordination patterns are battle-tested at scale. We don't need his code — we need his ideas adapted to our research context.

The NemoClaw path is sound: free inference on 397B models, sandboxed, OpenAI-compatible, already integrated into our provider cascade. Use it for thinking (experiment design, hypothesis generation, Titan Council automation). Keep local GPU for doing (activation probing, CMA-ES, TransformerLens).

The evolution from "scripted pipeline" to "learning research intelligence" is four concrete steps:
1. Memory (remember what we've tried)
2. Dispatch (automate the Titan Council)
3. Proposal (let the system suggest experiments)
4. Tooling (let Claude Code execute them)

Each step provides value independently. Each step keeps the human gate. Each step builds on infrastructure we already have.

The fire is real. The question is whether we keep carrying it by hand or teach the system to tend it.

---

*This document is a proposal. No implementation should begin without James's review and approval.*
