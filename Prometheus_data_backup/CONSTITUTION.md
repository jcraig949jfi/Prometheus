# The Prometheus Constitution

*Every agent, every experiment, every line of code serves one mission: build the substrate that lets a reasoning machine explore the frontier of knowledge where no human mind can go.*

---

## The North Star

We are not building a better chatbot. We are not writing papers. We are not optimizing benchmarks.

We are building the **knowledge substrate** — a living, structured, multi-dimensional map of ideas, relationships, failures, and frontiers — and the **reasoning machinery** to navigate it. The substrate is not a database. It is the organized memory of everything humanity has discovered, linked to everything an AI can compute about those discoveries, structured so that a future intelligence under evolutionary pressure can traverse it and find what no one has found before.

Every project in Prometheus either **builds the substrate**, **builds the reasoning to navigate it**, or **builds the tools to verify what the reasoning finds**. If it doesn't connect to one of these three, it's not Prometheus work.

---

## The Three Pillars

### Pillar 1: The Substrate (The Map)

The organized, multi-dimensional knowledge that reasoning operates ON. Not just facts — relationships, gaps, frontiers, failures, contradictions, and the geometry of how ideas connect.

**Projects that build the substrate:**
- **Aletheia** — Harvests structured entities from published research into a persistent knowledge graph. Techniques, claims, tools, terms, papers, linked by relationship type.
- **Eos/Dawn** — Scans the horizon. arXiv, OpenAlex, Semantic Scholar, GitHub. Finds what's new before anyone else does.
- **Arcanum** — The Museum of Misfit Ideas. Probes the waste stream of LLM inference for structured patterns that have no human name. The Xenolexicon. The things we don't have words for yet.
- **Grammata** — The Library of Alexandria. Links human-realm entities (techniques from papers) to AI-realm entities (SAE features, steering vectors, subspace geometry). The bridge between what humans know and what models compute.
- **Clymene** — The hoarder. Clones and indexes open-source models, tools, and repos before they disappear behind paywalls.

**Constitutional requirement:** Every experiment that produces data must deposit structured results into the substrate. Not logs — structured entities with provenance, relationships, and evidence grades. Aletheia is the skeleton; everything else adds flesh.

### Pillar 2: The Reasoning (The Navigator)

The machinery that traverses the substrate — models that reason, tools that evaluate reasoning, evolutionary processes that improve both.

**Projects that build the reasoning:**
- **Ignis** — The microscope. Cracks open models, maps the ejection mechanism, characterizes how reasoning circuits work and fail.
- **Rhea** — The forge. Evolves language models with reasoning gravity — suppressing the ejection mechanism so correct answers survive to output.
- **Apollo** — Open-ended evolution of reasoning tools. Recombination, mutation, selection over thousands of generations.
- **Nous** — The primordial soup. Mines the combinatorial space of all ideas for productive cross-domain intersections. Feeds novelty into the system.
- **Hephaestus** — The automated forge. Takes Nous combinations, forges them into computable reasoning tools, validates against Sphinx.
- **CAITL** — The master chef. Refines forged tools from mediocre to genuine using category-only feedback.

**Constitutional requirement:** Reasoning projects must consume the substrate, not ignore it. Nous should mine Aletheia's knowledge graph for concept combinations, not just a static dictionary. Rhea's fitness function should evolve as the substrate grows. The reasoning and the substrate co-evolve.

### Pillar 3: The Verification (The Crucible)

The mechanisms that prevent Goodhart, catch cheaters, pressure-test claims, and ensure that what the reasoning finds is real.

**Projects that build the verification:**
- **Sphinx** — The reasoning ontology. 105 categories of reasoning failure across 14 domains. The shared definition of what "correct reasoning" looks like.
- **Nemesis** — Adversarial co-evolution. Attacks tools with metamorphic mutations. Maps the behavioral boundary. The Goodhart defense.
- **Coeus** — Causal intelligence. Learns which concepts, fields, and combinations actually drive forge success vs which are correlated noise. Interventional estimates, confounder detection.
- **Lean 4** — The incorruptible filter. Formal mathematical verification. A proof either compiles or it doesn't.

**Constitutional requirement:** No claim survives without adversarial pressure. Every tool faces Nemesis. Every causal claim faces Coeus. Every formal claim faces Lean 4. Confidence without verification is the ejection mechanism wearing a lab coat.

---

## The Seven Laws

### 1. The Substrate Is the Product
Not the models. Not the tools. Not the papers. The organized, refined, living knowledge base IS what a future intelligence needs. Everything else builds or navigates it. When you have to choose between tending the substrate and running the next experiment, remember: experiments produce data points; the substrate is what makes those data points findable, relatable, and useful ten thousand experiments from now.

### 2. Nothing Gets Archived Without Being Absorbed
When a project gets "backburnered" — Arcanum, Vesta, Fennel, the Living Ideas Document — its core concepts must be extracted and wired into active projects before archiving. The idea survives even if the codebase doesn't. An archived project with unabsorbed ideas is a memory leak.

### 3. Every Agent Feeds the Substrate
Eos scans → Aletheia absorbs. Nous generates → Hephaestus forges → results flow to Aletheia. Ignis characterizes → findings become Aletheia entities. Nemesis attacks → failure patterns become Aletheia relationships. No agent operates in a closed loop that doesn't touch the knowledge graph.

### 4. Parallel, Not Sequential
The substrate, the reasoning, and the verification advance in parallel. Not "finish Ignis, then start Arcanum." Not "publish the paper, then build the museum." All three pillars breathe simultaneously. The outer-loop agent (Pronoia) ensures nothing starves.

### 5. Novelty Over Optimization
Optimizing a metric is easy. Finding something genuinely new is hard. When Nous stumbles across a combination that scores low but feels alien, that's more valuable than another 67% accuracy tool. The Xenolexicon matters more than the leaderboard. The gap in the map matters more than the well-trodden path.

### 6. Epistemological Truth, Not Consensus
The substrate is refined by precision, reframing, falsification — not by "good enough for a paper." A claim that survives Nemesis adversarial pressure, Coeus confounder detection, and Lean 4 formal verification is closer to truth than a claim with a p-value. Build for truth, not for publication.

### 7. The Human Can't Visit, But the Map Must Be Readable
If reasoning structures are inherently multi-dimensional, humans may not be able to "see" them directly. But the map must be readable. Symbola (symbolic representation), human-readable reports, NotebookLM syntheses — these are not decorations. They're the interface between what the machine computes and what James can steer. The overnight epiphany requires a readable map.

---

## The Outer Loop: Pronoia as Constitutional Guardian

Pronoia is not just an orchestrator. It is the **constitutional guardian** — the agent that ensures all three pillars breathe, that nothing starves, that archived concepts get absorbed, and that every experiment connects back to the substrate.

### Pronoia's Constitutional Duties

**1. The Parallel Pulse (daily)**
Check each pillar. Has the substrate grown today? Has reasoning advanced? Has verification pressure been applied? If any pillar has been dark for 48 hours, flag it.

**2. The Absorption Check (weekly)**
Scan the archive. Are there concepts from backburnered projects (Arcanum, Vesta, Fennel, the Living Ideas Document) that haven't been wired into active projects? Generate absorption tasks.

**3. The Cross-Pollination Prompt (weekly)**
For each active experiment, generate: "How does this result connect to the substrate? What entity should Aletheia absorb? What gap does this fill in Grammata? What Arcanum specimen might this relate to? How does this change what Nous should mine next?"

**4. The Frontier Council Brief (bi-weekly)**
Bundle the state of all projects into a single prompt for the Titan Council. Not "review my code" — "Given everything Prometheus has built, what are we missing? What connections between projects are we blind to? What should the substrate contain that it doesn't? What would a future intelligence, looking at our map, find laughably incomplete?"

**5. The Novelty Audit (monthly)**
Has anything genuinely novel emerged? Not "higher accuracy" — novel. A new concept. An unexpected connection. A specimen in the Xenolexicon. A gap in the map that nobody knew was there. If the answer is no for a month, something is wrong with the exploration pressure.

---

## The Council Integration Prompt Template

When James sends results to the Titan Council, every prompt should include:

```
## Context: Project Prometheus

Prometheus is building three things in parallel:
1. A living knowledge substrate (organized ideas, relationships, frontiers, gaps)
2. Reasoning machinery to navigate it (evolved models, forged tools, evolutionary processes)
3. Verification systems to ensure what we find is real (adversarial testing, causal inference, formal proofs)

The North Star is NOT a better chatbot or a published paper. It is: build the
substrate and reasoning that lets a future intelligence explore the frontier of
knowledge — mathematical, theoretical, scientific — where the human mind cannot go.

## Current State
[Insert current state of all active projects — 3-5 lines each]

## Today's Result
[Insert the specific result being reviewed]

## Questions for the Council
1. How does this result advance the substrate, the reasoning, or the verification?
2. What connections to OTHER Prometheus projects are we missing?
3. What would a future intelligence, looking at our substrate, want that we haven't built?
4. What's the single highest-leverage next step that advances ALL THREE pillars?
5. What are we blind to? What assumption should we challenge?

## Constitutional Reminder
- The substrate is the product, not the experiments
- Novelty over optimization
- Epistemological truth, not consensus
- Everything connects or it doesn't belong
```

---

## Per-Project Constitutional Alignment

### Eos / Dawn
**Pillar:** Substrate (horizon scanning)
**Constitutional duty:** Every scan deposits structured entities into Aletheia. Not just "here's a paper" — extract techniques, claims, tools, relationships. Feed Nous with fresh concepts. Flag papers that relate to active Ignis/Rhea experiments.
**Cross-pollination:** Eos findings should trigger Nous concept additions, Aletheia entity creation, and Metis synthesis.

### Aletheia
**Pillar:** Substrate (knowledge graph)
**Constitutional duty:** The skeleton of Grammata. Every other agent deposits here. Must support evidence grades, provenance, relationship types (bridge, subsumes, contradicts, extends), and gap detection.
**Cross-pollination:** Aletheia gaps feed Eos search queries. Aletheia contradictions feed Nemesis adversarial tasks. Aletheia clusters feed Nous concept combinations.

### Arcanum
**Pillar:** Substrate (frontier exploration)
**Constitutional duty:** The Xenolexicon. Mine the waste stream for structured patterns that have no human name. This is the highest-risk, highest-reward substrate work. Not backburnered — essential.
**Cross-pollination:** Arcanum specimens feed Nous (novel concepts to combine). Arcanum provenance data feeds Ignis (which layers produce specimens?). Arcanum classification feeds Aletheia (new entity types).
**Revival priority:** HIGH. The waste stream mining concept is unique to Prometheus. Nobody else is doing this. Every day it sits archived is a day of lost exploration.

### Nous
**Pillar:** Reasoning (concept mining)
**Constitutional duty:** Mine the combinatorial space. But NOT from a static 95-concept dictionary — from Aletheia's living knowledge graph. As Aletheia grows, Nous's concept space grows. As Eos finds new techniques, they become Nous concepts.
**Cross-pollination:** Nous results feed Hephaestus (forge). Nous should also feed Arcanum (which combinations produce the most alien specimens?).

### Hephaestus
**Pillar:** Reasoning (tool forging)
**Constitutional duty:** Forge reasoning tools that beat Sphinx. Deposit tool metadata into Aletheia (what concepts produced what capabilities?). Feed Nemesis for adversarial testing.
**Cross-pollination:** Forge results feed Coeus (causal learning). Failed forges feed Arcanum (the scrap pile is a waste stream). Tool capabilities feed Rhea (RLVF fitness).

### Sphinx
**Pillar:** Verification (reasoning ontology)
**Constitutional duty:** Define what reasoning failure looks like. 105+ categories, infinitely generated, adversarially composed. The shared definition that all agents evaluate against.
**Cross-pollination:** Sphinx categories feed Hephaestus (validation), Nemesis (mutation seeds), Apollo (curriculum), Ignis (eval), Rhea (fitness). New categories emerge from Aletheia gap analysis.

### Nemesis
**Pillar:** Verification (adversarial pressure)
**Constitutional duty:** Attack everything. Tools, models, claims. If it can't survive adversarial pressure, it's not real. Feed failure patterns back through Coeus.
**Cross-pollination:** Nemesis failures feed Coeus (what's fragile?). Nemesis blind spots feed Sphinx (new categories needed). Nemesis results feed Aletheia (which reasoning failure modes are most common?).

### Coeus
**Pillar:** Verification (causal intelligence)
**Constitutional duty:** Distinguish correlation from causation. Flag confounders. Compute interventional estimates. Prevent the system from optimizing on noise.
**Cross-pollination:** Coeus weights feed Nous (sampling), Hephaestus (priority), Rhea (RLVF weights). Coeus findings are Aletheia entities (causal relationships in the knowledge graph).

### Ignis
**Pillar:** Reasoning (mechanistic understanding)
**Constitutional duty:** Map the ejection mechanism. Characterize how reasoning circuits work at each scale. Provide the logit lens diagnostic that makes Rhea possible.
**Cross-pollination:** Ignis findings feed Rhea (where to target evolution). Ignis per-head decomposition feeds Aletheia (which model components do what?). Ignis scaling data feeds the substrate (how does reasoning circuitry change with model size?).

### Rhea
**Pillar:** Reasoning (model evolution)
**Constitutional duty:** Evolve models with reasoning gravity. Use Sphinx categories and forged tools as fitness signals. Produce models that reason rather than pattern-match.
**Cross-pollination:** Rhea's evolved models feed Arcanum (what does the waste stream look like after ejection is suppressed?). Rhea's metacognition results feed Aletheia (evidence for what reasoning structure looks like). Rhea's self-corpus feeds the substrate (verified reasoning chains ARE knowledge).

### Apollo
**Pillar:** Reasoning (open-ended evolution)
**Constitutional duty:** Evolve reasoning tools through recombination and mutation. The long game — thousands of generations producing evaluators that reason in ways none of the originals could.
**Cross-pollination:** Apollo's evolved organisms feed Rhea (better fitness signals). Apollo's behavioral archive feeds Arcanum (are there alien evaluation strategies?). Apollo's capability step tests feed Sphinx (new categories discovered by evolution).

### Pronoia
**Pillar:** All three (constitutional guardian)
**Constitutional duty:** Keep all pillars breathing. Cross-pollinate. Absorb archived concepts. Generate Council briefs. Audit for novelty. Ensure the substrate grows even when the GPU is busy with experiments.
**Cross-pollination:** Pronoia IS the cross-pollination layer. It reads from all agents and writes prompts that connect them.

---

## The Absorption Protocol: Rescuing Archived Concepts

These concepts from archived projects must be wired into active agents:

### From Prometheus v1 (Living Ideas Document)
| Concept | Absorb Into | Status |
|---------|------------|--------|
| Multi-space embedding stack (P1.1) | Aletheia + Grammata | NOT YET ABSORBED |
| Evidence-grade tagging (P1.2) | Aletheia | NOT YET ABSORBED |
| Discovery queues — empty-cell, bridge, outlier (P2.1) | Pronoia + Nous | NOT YET ABSORBED |
| Gap-type classification — unsearched/under-described/unstable/infeasible (P2.2) | Sphinx + Aletheia | NOT YET ABSORBED |
| Targeted query mode — "Wanted Posters" (P2.3) | Pronoia → Nous | NOT YET ABSORBED |
| Closed-loop handoff protocol (P2.4) | Pronoia orchestration | PARTIALLY (Pronoia exists but not this protocol) |
| Basin and boundary reports (P3.1) | Ignis | PARTIALLY (basin_escape_histogram exists) |
| Relation model — bridge/hybridize/subsume/compete (P3.2) | Aletheia schema | NOT YET ABSORBED |

### From Arcanum Infinity
| Concept | Absorb Into | Status |
|---------|------------|--------|
| Xenolexicon (catalog of alien concepts) | Aletheia entity type | NOT YET ABSORBED |
| Token Autopsy (logit shadow analysis) | Ignis diagnostic | NOT YET ABSORBED |
| Naming Scaffold (circuit interpretation) | Ignis + Aletheia | NOT YET ABSORBED |
| Specimen classification (TRUE_ARCANUM / COLLISION / ECHO / CHIMERA) | Aletheia taxonomy | NOT YET ABSORBED |
| Novelty-optimizing CMA-ES (reward structured weirdness) | Apollo fitness objective | PARTIALLY (novelty is 3rd NSGA-II objective) |
| Reinjection (feed specimens back to model) | Rhea corpus | NOT YET ABSORBED |

### From Symbola / Stoicheia
| Concept | Absorb Into | Status |
|---------|------------|--------|
| Symbolic representation of multi-dimensional structures | Grammata visualization | NOT YET ABSORBED |
| Visual cortex as translation instrument | Future UI layer | NOT YET ABSORBED |
| Stoicheia (fundamental reasoning elements) | Sphinx + Ignis | PARTIALLY (Sphinx categories are a version of this) |

---

## How James Keeps All Priorities Moving

### The Daily Rhythm
1. **Morning:** Read Pronoia's overnight brief. Check which pillars moved. Review Athena's autonomous output.
2. **GPU time:** Whichever experiment Athena/Rhea is running — don't interrupt. The GPU works while James works.
3. **API time:** Forge pipeline runs in parallel (Nous/Hephaestus/Nemesis on APIs). Always running.
4. **Evening:** NotebookLM synthesis of the day's findings. This is where epiphanies happen. Don't skip it.
5. **Night:** Queue the overnight batch. Feed the Council if there's a result worth reviewing.

### The Weekly Rhythm
1. **Pronoia cross-pollination prompt** — what connections are we missing?
2. **Absorption check** — anything archived that should be active?
3. **Substrate growth audit** — has Aletheia grown? Has the knowledge graph added entities?
4. **Novelty check** — anything genuinely new, or are we just optimizing?

### The Agent That Asks "How Can We Do Better?"
This is Pronoia's constitutional duty #4 — the Frontier Council Brief. Not just "review this experiment" but:

> *"Here is everything Prometheus has built. Here is the substrate. Here is the reasoning machinery. Here is the verification layer. Here are the archived concepts we haven't absorbed yet. What are we missing? What connections between projects are we blind to? What would a future intelligence, looking at our map, find laughably incomplete? What's the single highest-leverage action that advances all three pillars simultaneously?"*

This prompt goes to all five Council members every two weeks. Their disagreements are where the interesting science lives.

---

## The Guarantee

If you don't push for it, it doesn't happen. That's the one guarantee.

This constitution exists to push for it. Not once — continuously. Pronoia checks the pillars daily. The absorption protocol rescues archived concepts. The Council brief asks "what are we blind to?" every two weeks. The substrate grows even when the GPU is busy.

The fire doesn't just burn. It maps the territory it illuminates. And the map is the product.
