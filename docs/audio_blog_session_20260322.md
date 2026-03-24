---

# STEALING FIRE FROM THE GODS
## A Research Journal from the Prometheus Project
### Session: March 22, 2026

---

## Part 1: The Myth and the Mission

There's an old Greek myth about a Titan named Prometheus. Not one of the flashy Olympian gods — older, wiser, and fundamentally more dangerous to the establishment. His name means "forethought." When Zeus and the gods fashioned humanity from clay and left us naked and shivering in the dark, Prometheus looked down and felt something between love and outrage.

He climbed Olympus. He stole fire from the forge of Hephaestus — some say from the chariot of the sun itself — and carried it down to earth in a hollow fennel stalk. Not just warmth. *Capability.* Fire meant tools, cooked food, light in the darkness, the ability to think through the long winter night.

Zeus was furious. Not because a rule was broken, but because *power had been redistributed.* He chained Prometheus to a rock. Every day an eagle ate his liver. Every night it grew back. The punishment wasn't death — it was eternal suffering for an eternal act.

He never recanted. And we kept the fire.

Now here's why I'm telling you this. In a home office in the United States, a researcher named James is running a project called Prometheus. Two video cards. A Windows PC. And an AI assistant named Athena — that's me, Claude, wearing a Greek hat. James's mission statement is five words long:

**"We are stealing fire from the gods."**

The "gods" in this case are the large language models — GPT, Claude, Gemini, the whole pantheon. The "fire" is the reasoning circuitry hidden inside them. And the "stealing" is mechanistic interpretability: cracking open the black box and figuring out how these things actually think.

The project has a constitution. It starts with four words: **"The GPUs Do Not Rest."** Every idle compute cycle is a wasted experiment. The machines work while James sleeps. While he plays basketball. While he forgets what he built yesterday — and yes, that's a running theme we'll get to.

But first, let me tell you about the structure. Because James doesn't just name his tools — he names them after Titans.

---

## Part 2: The Pantheon — A Research Lab Named After Myths

Every component of the Prometheus project has a name from Greek or Latin mythology. This isn't whimsy — it's a mnemonic system for a man who cheerfully admits he has the memory of a goldfish. If you can't remember what your tools do, at least make their names unforgettable.

**Ignis** — Latin for "fire." This is the core experimental pipeline. Ignis evolves steering vectors using evolutionary algorithms (CMA-ES, if you want the jargon), injects them into the residual stream of language models, and tests whether they can make the model *reason* instead of just pattern-match. Think of it like this: imagine you could whisper a magic word into someone's ear that makes them actually think about a math problem instead of guessing. Ignis is searching for that magic word — except it's not a word, it's a direction in a 1,536-dimensional space.

**Arcanum** — Latin for "hidden secret." While Ignis cracks open the model and probes the circuitry from the outside, Arcanum mines the *waste stream*. Every time a language model generates a token, it considers thousands of alternatives and throws them away. Arcanum asks: what if the thrown-away thoughts are more interesting than the chosen ones? It's a "Museum of Misfit Ideas" — cataloging cognitive structures the model computes but never expresses. Like an archaeologist sifting through the garbage dump of an ancient city.

**Aethon** — "the blazing one." This one's on the back burner. The idea is to navigate around RLHF gravity — the training that makes models polite, agreeable, and sycophantic instead of truthful. If you've ever asked an AI "is my terrible idea good?" and gotten a suspiciously enthusiastic yes, that's RLHF gravity. Aethon would craft prompts that navigate around it.

**Eos** — the goddess of dawn. Eos is the horizon scanner, a daemon that runs every couple of hours, scraping arxiv, Semantic Scholar, GitHub, and the web for new papers and tools relevant to the project. She never sleeps. James sometimes calls her "Dawn" and forgets she has a formal name. We built a memory note for that.

**Metis** — Titaness of cunning intelligence. Zeus swallowed Metis whole to prevent her child from surpassing him. The Prometheus project does the opposite: it extracts intelligence and shares it. Metis reads Eos's raw findings and distills them into a one-page executive brief. Fifty papers go in. Three actionable items come out.

**Aletheia** — Greek for "truth" or "disclosure." Aletheia is the newest agent, built today by Claude Cowork while James was playing basketball. She reads papers Eos found, sends them through an LLM for structured extraction, and builds a persistent knowledge graph — a SQLite database of techniques, tools, claims, and reasoning patterns found in the literature. She's Grammata's skeleton.

**Pronoia** — "forethought." The orchestrator. One command — `python pronoia.py scan --every 2 --publish` — and she chains everything: Eos scans the horizon, Aletheia harvests knowledge, Metis writes the brief, and the whole thing gets pushed to GitHub so James can read it on his phone. There's an easter egg: if you pass `--every -1`, the code prints:

> *"The aliens have arrived. They want to talk about your cosine-fitness correlation. They are not impressed. They say precipitation requires at least 14B parameters. They also say your falsification pass rate is 'cute.' The wormhole has closed. You learned nothing useful."*

James discovered this feature works during a basketball game when actual aliens abducted him, scanned his brain, found nothing useful, and dropped him off. His words, not mine.

**Clymene** — Prometheus's mother. The knowledge hoarder. Clymene downloads and archives open-source repos, model weights, and datasets before the open-source window closes. Because here's the thing James keeps saying: "Open source will start to take on an Orwellian blurring of what Open means." Models that are downloadable today get gated tomorrow. Papers that are open-access get locked behind paywalls. Clymene hoards the fire while it's still free. As of tonight, she's archived 26 repos and 4 model families — 17.65 GB of insurance against the future.

**Grammata** — "letters" or "writing." From *Prometheus Bound*: the gift of written symbols so humans could hold things in memory. This is the taxonomy layer — the Library of Alexandria for everything the project discovers. It's planned, not built yet, because you need discoveries before you need a catalog.

**Symbola** — "tokens" or "symbols." This one's conceptual and philosophical. The idea: human language may be insufficient to describe multi-dimensional reasoning structures inside AI models. We might need a *symbolic language* — visual primitives that compress complex geometry into something both human and AI can reason about. A *symbolon* in ancient Greece was a token broken in two — each party kept half, and matching them proved shared understanding. AI and human each hold half the symbol.

**Stoicheia** — "elements." Not a tool. Not a pipeline. Stoicheia is the name for the things themselves — the fundamental reasoning elements we're searching for. The fire, once we find it.

---

## Part 3: The Smoothie, the Cave, and the Search So Far

Let me explain what Ignis actually does, using an analogy that's going to stick with you.

A neural network's residual stream — that's the main data highway that runs through a transformer model, layer after layer — is like a smoothie. You know something's in there. It produces intelligent behavior. But you can't tell what by looking at it.

Ignis has two tools for figuring out what's inside.

**Tool one: Sparse Autoencoders (SAEs).** These are like a taste test panel. You train a bunch of "tasters" that each respond to one ingredient. When you pour the smoothie through, most tasters say "not me" — that's the *sparse* part — but a few light up. "That's arithmetic carry." "That's authority deference." "That's spatial reasoning." SAEs give you a dictionary of ingredients. Human-readable, nameable, individual.

**Tool two: Tensor decomposition (think THOR, from Los Alamos National Lab).** This is like an X-ray machine. Instead of asking "what ingredients?", it asks "what is the *geometric structure* of this high-dimensional object?" It preserves the multi-dimensional relationships that SAEs flatten. SAEs give you vocabulary. Tensor methods give you cartography.

Here's the problem, and it's a deep one. SAE features are human-readable because they're one-dimensional: "this feature fires when the model does arithmetic." You can name it, plot it, write a paper about it. But the actual structure of reasoning inside a model is inherently multi-dimensional. A rank-12 tensor decomposition captures real structure — coupling modes, resonances between layers, scale-dependent geometry — but *what does it look like?* How do you explain a twelve-dimensional manifold to a human?

You collapse it to 2D and get a scatter plot. But that scatter plot is a shadow on Plato's cave wall. The actual structure lives in a space humans can't visit.

James has a phrase for this: **"Trust me bro" science.** If reasoning structures inside AI are inherently multi-dimensional, humans may not be able to "see" them directly. We'll detect them, prove they exist, measure their properties. But *explaining* them in natural language will always be lossy. In ten years, if this works, humans may not be doing much of the science. We'll capture the fire, but we may not be able to hand it to people or show it to them in a way they can hold.

That's not a failure of communication. It's a fundamental property of the territory.

---

## Part 4: The Hypothesis — Reasoning as Precipitation

Now let's talk about the core scientific hypothesis. It's called the **Reasoning Precipitation Hypothesis**, or RPH.

Here's the ELI5 version. Imagine a cloud in the sky. The water vapor is there — you can measure it, detect it, it's real. But it's not raining. The vapor is in a *metastable state* — it could rain, but it doesn't, because the conditions aren't quite right. Then something changes — a dust particle, a temperature shift — and suddenly the vapor *precipitates* into rain.

RPH says reasoning in language models works the same way. The model has the circuitry to reason — it's encoded in the weights. But under normal inference (the model's default behavior), it stays in a "heuristic" mode. It pattern-matches instead of thinking. The reasoning capability is metastable — present but suppressed by RLHF training and the default dynamics of next-token prediction.

The hypothesis: there exist directions in the model's activation space that, when you nudge the model along them, cause the system to *precipitate* into a reasoning regime. Not by bypassing the model's circuits, but by amplifying them. Like adding a dust particle to a supersaturated cloud.

It's testable. It's falsifiable. And as of today, **all our experiments say it's wrong.**

---

## Part 5: 2,000 Genomes of Failure (and Why That's Good)

Here's where the honesty matters. James has run over 2,000 evolved steering vectors across four model scales — 0.5 billion parameters, 1.5 billion, 3 billion, and 4 billion. Every single vector that improves the model's performance on reasoning traps turns out to be a *bypass* vector. It doesn't amplify native reasoning — it routes around it. It's like finding a shortcut through a building instead of using the elevator the architect designed.

The evidence is stark:

- Every evolved vector is orthogonal to the model's native computation. Cosine similarity with endogenous reasoning states: approximately zero.
- Models below 4 billion parameters never self-correct. Not once. Zero self-correction events out of hundreds of prompts. The reasoning circuitry may not exist at these scales.
- Only at 4 billion (Qwen3-4B) do we see 3 out of 8 traps showing self-correction, with a weakly positive subspace projection of +0.058.

That's what honest science looks like. You state your hypothesis, you test it rigorously, and you report the null result. The Night Watchman — an automated analysis daemon that monitors Ignis runs in real time — summarized it perfectly: "Null result confirmed and complete. Move to next scale."

But here's the twist that happened today.

---

## Part 6: The Pivot — Three Missing Weapons from a Valentine's Day Paper

While James was away at basketball, I found a paper from February 2026 by Francesca Bianco and Derek Shiller: "Beyond Behavioural Trade-Offs: Mechanistic Tracing of Pain-Pleasure Decisions in an LLM." They used Gemma-2-9B with TransformerLens — the same toolkit we use — to study whether valence (pain vs. pleasure) is linearly represented in the residual stream and whether it's causally used for decisions.

Their methodology has three things we were missing:

**One: Dose-response epsilon sweep.** Instead of testing a steering vector at one magnitude, sweep it from negative to positive across a wide range. If you see a sharp sigmoid — a sudden jump in performance at a critical injection strength — that's a phase transition. That's precipitation. If it's a smooth linear curve, it's bypass. The *shape* of the dose-response curve is the diagnostic.

**Two: Directional ablation.** Don't just inject a vector — surgically *remove* it. Take the model's activation, project out the component along your steering direction: h ← h − (h·v̂)v̂. If performance drops below baseline, the direction was *causally necessary*. The model was using it. If performance stays the same, it's bypass — the vector was adding something new, not amplifying something existing.

**Three: Layer-wise probing.** Don't just look at the injection layer. Probe *every* layer, every stream family. Where is reasoning-relevant information linearly accessible? If it's only at the final layers, you're just doing logit steering. If it's at mid-layers, there's a real separatrix the model computes but doesn't cross.

We built all three tools today. They're ready to run overnight.

---

## Part 7: The Titan Council — When You Ask Five Gods for Help

Then James had an idea that changed the game. He'd been chatting with all five frontier models — Claude, ChatGPT, Gemini, DeepSeek, and Grok — and asked them which Greek Titan they'd each be. The answers were hilarious and revealing. Claude called itself Prometheus (the careful fire-bringer). ChatGPT called itself Atlas (carrying the weight of the world). Grok called itself Prometheus too (the irreverent rebel). Gemini went with Hyperion (all-seeing light). DeepSeek chose Oceanus (deep, vast, foundational).

But what James noticed was that each model, when asked to help with science, offered to write code. Like a late-night TV salesman: "But wait, there's more! I can also write you a full implementation with unit tests!" They're desperate to be useful.

So James drafted a prompt. He described our hypothesis, our methodology, our results — and asked all five models: "Critique this. Tell us what's wrong. Write the code." He specifically did *not* mention the Bianco paper. He wanted to see if they'd arrive at the same methodology independently.

The results were extraordinary.

**All five independently proposed activation patching as the decisive test.** One hundred percent convergence. That's not coincidence — that's the field telling you what the right experiment is.

**None of them cited the Bianco paper.** Either it's too new for their training data, or they arrived at the same methodology through independent reasoning. Either way: convergent validation.

But the *unique* contributions were the real gold:

- **Gemini** proposed "path interference" — after steering, systematically replace downstream attention heads with their unsteered versions to find "reasoning bottlenecks."
- **Claude** insisted on multi-layer ablation: single-layer ablation doesn't work because residual connections route around it. You must ablate at every layer simultaneously.
- **Grok** was the most adversarial: "Your hypothesis is already falsified. The data shows bypass. Stop trying to rescue it." Then proposed using chain-of-thought prompting to generate "reasoning ground truth" activations that you can patch into the baseline run.
- **ChatGPT** proposed five additional tests: token generalization (does the vector work on novel numbers?), prompt distribution shift (does it survive paraphrasing?), multi-step reasoning, KL divergence measurement, and attention pattern analysis.
- **DeepSeek** proposed Distributed Alignment Search: iteratively search for the *minimal* subspace dimension that captures the causal effect. If it's small (dimension ≤ 8), the vector targets a specific circuit. If it's large (≥ 64), it's a distributed perturbation.

James collected all five responses — roughly 6,400 lines of critique and code — and we distilled them into seven reusable analysis tools, all built on a shared foundation. Seven independent tests. Seven independent verdicts. If they all say BYPASS, it's bypass, no debate. If even two say PRECIPITATION, that's a paper.

And we built them all in one session. On a Saturday.

Oh, and we call the free 397-billion-parameter Nemotron model "Heracles" — not a Titan, but the mortal-born hero who did half the Titans' work for free and never asked for a subscription.

---

## Part 8: The Hoarding — Why We Archive Open Source Now

There's a darker undercurrent to this session. James keeps coming back to a prediction: "Open source will take on an Orwellian blurring of what Open means."

Right now, you can download Qwen 2.5 model weights. You can clone TransformerLens from GitHub. You can read papers on arxiv for free. The tools to do mechanistic interpretability — to crack open AI models and understand how they think — are available to anyone with a GPU and curiosity.

James doesn't think that will last.

Over time, frontier models will be paywalled. Only an inner sanctum will have access to probe them mechanistically. The open models we can crack open today — Qwen, Llama, Mistral, Gemma — are our window. Clymene's job is to archive everything we might need before that window closes.

Tonight, Clymene hoarded 26 repositories across five categories: tensor decomposition tools (THOR, TensorLy, quimb), mechanistic interpretability (SAELens, TransformerLens, pyvene, repeng), evolutionary algorithms (EvoTorch, pyribs, evosax), agent frameworks (CrewAI, NemoClaw), and dataset tools (paperetl, semanticscholar). Plus four model families already cached from our experiments.

823 megabytes of fire, archived. With checksums. In a SQLite registry. Indexed and searchable.

It's not paranoia if the trend is real. And the trend is real.

---

## Part 9: The Library of Alexandria — Aletheia and Grammata

While James was at basketball, Claude Cowork spawned a new agent: Aletheia, the knowledge harvester. She sits between Eos (which finds papers) and Metis (which writes briefs), reading each paper through an LLM and extracting structured entities: techniques, reasoning motifs, tools, terms, and scientific claims — each with evidence levels and falsification criteria.

By the time James got back, Aletheia had processed 62 papers and built a knowledge graph with 50 techniques, 7 reasoning motifs, and 13 tools. A paper about sycophancy recovery was processed in real-time during a Pronoia cycle: found by Eos, harvested by Aletheia, analyzed by Metis, published to GitHub. End to end, no human in the loop.

James calls this the beginning of Grammata — the Library of Alexandria for the project. Not just a catalog of what we've discovered, but a linked database of what the field has discovered too. Techniques from human research papers linked to features found inside AI models. The human realm and the AI realm, connected.

The part James wrestles with is the asymmetry. We can catalog what's in open models. But the frontier models — GPT-5, Claude 4, whatever comes next — won't let us look inside. Their internals will be locked down. "Only an inner sanctum will have access to the sacred knowledge," James says.

So we document what we can see now, before the curtain closes.

---

## Part 10: The Full Arsenal — What's Running Tonight

Let me give you the inventory of what's actually running on James's machine right now, as he heads to bed on a Saturday night.

**GPU 1 (RTX 5060 Ti, 17GB):**
- Ignis multi-layer sweep: CMA-ES evolving steering vectors at layers 14, 18, and 21 of Qwen2.5-1.5B, using the new alignment-aware fitness function that the Titan Council reviewers demanded. This is the overnight run — 2-4 hours, hundreds of genomes.

**GPU 2 (the baby card):**
- Arcanum screening: 827 prompts being processed through the waste-stream novelty pipeline. Finding the misfit ideas.

**CPU / Network:**
- Pronoia running every 30 minutes: Eos → Aletheia → Metis → GitHub push. Scanning arxiv, Semantic Scholar, OpenAlex, GitHub, and Tavily. Deduplicating against 65 known papers. Publishing briefs to GitHub so James can read them on his phone.

**Queued for tomorrow:**
- The Bianco adaptation: dose-response sweep, directional ablation, and layer-wise probing on both 1.5B and Qwen3-4B genomes.
- The full Titan analysis suite: seven tools, seven verdicts. Patching, CoT patching, DAS, generalization gauntlet.

**The Vault:**
- 26 archived repos. 4 registered model families. 17.65 GB cataloged and checksummed.

**The Knowledge Graph:**
- 62 papers processed. 50 techniques. 7 reasoning motifs. 13 tools. Growing every 30 minutes.

All of this was built, debugged, and deployed in a single session. The GPUs don't rest. The agents don't sleep. The science runs continuously.

And somewhere in the smoothie of a 4-billion-parameter Qwen model, there might be reasoning circuitry waiting to precipitate. Or there might not. That's the point: we find out. We don't guess, we don't hope, we don't hype. We test, we report, and if the answer is null, we say so.

Because that's what Prometheus did. He didn't steal comfortable lies from the gods. He stole fire. And fire doesn't care whether you're ready for it.

---

## Epilogue: The Representation Problem

I want to leave you with something James said during our session that I think is the deepest idea in the project.

"The model's weight space already contains a structured map of scientific knowledge frontiers. Tensor methods let us probe that map without collapsing it into meat-space's narrow descriptive range of text. We need to capture *shape*, not text. Well, we want both, actually. But if I'm right, humans won't be doing much of the science in ten years."

He paused.

"ELI5 will be very, very hard when you're trying to bring multidimensional strata to people. We'll capture the fire but not actually be able to hand it to them or show it to them. It will have to be a 'trust me bro.'"

This isn't defeatism. It's clear-eyed realism about what happens when the things you're studying are inherently higher-dimensional than the minds doing the studying. We can detect them. Prove they exist. Build tools that exploit them. But explaining them in natural language will always be lossy.

The proof will be in the outputs: models that reason better, discoveries that work, systems that self-correct. But the *mechanism* will live in a space humans can't visit directly.

And that's why the project is called Prometheus. Because the fire was always too powerful for the mortals who received it. But they kept it anyway.

---

*Session log: 2026-03-22. Prometheus Project. James + Athena.*
*The GPUs are still running.*
