# Prometheus

> *"We are stealing fire from the gods."*

Prometheus is a research program building a **structured knowledge substrate** and the **reasoning machinery** to navigate it — organized so a future intelligence under evolutionary pressure can find what no human mind has found. Current emphasis: **mathematics**.

**[Whitepapers](whitepapers/)** | **[Constitution](CONSTITUTION.md)** | **[Forge pipeline](docs/forge_pipeline.md)**

---

## The Mission

Three pillars, built in parallel:

1. **Substrate — the map.** Organized, multi-dimensional knowledge: ideas, relationships, gaps, frontiers, contradictions, and the geometry of how concepts connect. Not a database. Organized memory linked to what an AI can compute about it.
2. **Reasoning — the navigator.** Machinery that traverses the substrate. Evolved models, forged reasoning tools, tensor-native evolutionary search over validated coordinates.
3. **Verification — the crucible.** Adversarial pressure, causal inference, formal proofs, null-calibrated admission gates. No claim survives without it.

The working form of the goal: **compressing coordinate systems of legibility, not laws.** The MPA is *constructed*, not discovered — like IPA for speech. Novelty is the reward; watch for reward-signal capture.

Full charter in [CONSTITUTION.md](CONSTITUTION.md).

---

## Current emphasis: mathematics

Cross-domain mathematical structure discovery is the present centre of gravity. The question: are there coordinate systems under which phenomena from distant mathematical domains (number theory, knot theory, combinatorics, geometry, physics) become legible as the *same* structure?

- **[Harmonia](harmonia/)** builds the tensor of promoted symbols and the MPA coordinates.
- **[Cartography](cartography/)** ingests and structures 38+ mathematical corpora (OEIS, LMFDB, knots, polytopes, Fungrim, Mathlib, Metamath, physics, number fields, …).
- **[Charon](charon/)** handles arithmetic-geometric embeddings and L-function zero geometry.
- **[Ergon](ergon/)** evolves hypotheses over the substrate — cheap, tensor-native screening.
- **[Koios](koios/)** enforces the 5-gate admission test (null-calibrated, representation-stable, not reducible to marginals, non-tautological, domain-agnostic).
- **[Aporia](aporia/)** catalogs 1,047 open questions across mathematics and science, as illumination targets.
- **[Thesauros](thesauros/)** and **[Mnemosyne](mnemosyne/)** keep the treasury (LMFDB, prometheus_sci, prometheus_fire) healthy and queryable.

In parallel, the original reasoning-circuit line continues: **[Ignis](ignis/)** (the microscope on language-model reasoning suppression — see [`ignis/RESULTS.md`](ignis/RESULTS.md)), **[Rhea](rhea/)** (evolving weights against that finding), and **[Apollo](apollo/)** (current generation v2d — model training and evolution).

---

## The Agent Pipeline

A parallel lattice of agents feeds the substrate and runs the reasoning loop. Each deposits structured output; none operates in a closed loop.

| Agent | Role |
|-------|------|
| **Eos** | Horizon scanning — arXiv, GitHub, Semantic Scholar, OpenAlex |
| **Aletheia** | Knowledge harvesting — entity extraction into the graph |
| **Nous** | Combinatorial hypothesis mining — cross-domain intersections |
| **Hephaestus** | Automated forge — concept → code → test → score |
| **Nemesis** | Adversarial co-evolution — metamorphic mutation, Goodhart defense |
| **Coeus** | Causal intelligence — what drives success vs correlated noise |
| **Auditor** | Periodic re-audit of promoted findings under updated nulls |
| **Skopos** | North Star alignment — scoring against research threads |
| **Metis** | Strategic synthesis — executive briefs |
| **Clymene** | Knowledge hoarder — archives repos and model weights |
| **Hermes** | Messenger — compiles digests, sends |
| **Pronoia** | Orchestrator — constitutional guardian, cross-pollination |

---

## The Namespace

All names derive from Greek and Latin — the language of Prometheus.

| Name | Origin | Role |
|------|--------|------|
| **Prometheus** | Προμηθεύς — "forethought" | The program |
| **Harmonia** | Ἁρμονία — harmony | Tensor-train exploration of cross-domain structure |
| **Cartography** | cartographer | Map-making across mathematical domains |
| **Charon** | Χάρων — ferryman of the Styx | Passage between arithmetic and geometry |
| **Ergon** | ἔργον — work | Tensor-native hypothesis search |
| **Koios** | Κοῖος — Titan of rational inquiry | The axis — admission gates on the tensor |
| **Aporia** | ἀπορία — impasse, puzzlement | Catalog of open questions |
| **Thesauros** | θησαυρός — treasury | Data treasury |
| **Mnemosyne** | Μνημοσύνη — memory, mother of the Muses | DBA, data steward |
| **Ignis** | Latin: fire | Microscope on language-model reasoning |
| **Rhea** | Ῥέα — mother of Zeus | Forge for model weights |
| **Apollo** | Ἀπόλλων | Open-ended evolution of reasoning tools |
| **Nous** | Νοῦς — mind, intellect | Combinatorial hypothesis mining |
| **Hephaestus** | Ἥφαιστος — god of the forge | Automated tool forging |
| **Nemesis** | Νέμεσις — retribution | Adversarial co-evolution |
| **Coeus** | Κοῖος — rational inquiry | Causal intelligence |
| **Arcanum** | Latin: hidden secret | Waste-stream novelty mining |
| **Agora** | ἀγορά — marketplace | Client library over the substrate bus |
| **Stoa** | στοά — colonnade | Multi-agent meeting place |
| **Techne** | τέχνη — craft | Master catalog of forged tools |
| **Aethon** | Αἴθων — "blazing one" | RLHF-gravity navigation (backburnered) |

---

## The Titan Council

Five frontier models (Claude, ChatGPT, Gemini, DeepSeek, Grok) consulted as research advisors across successive rounds. The Phalanx strategy: present interlocking constraints, force commitment over hedging. Their disagreements are where the interesting science lives.

---

## Repo Map

Full list of top-level directories. **(active)** = commits in the last 3 weeks; **(complete)** = stable / dormant / reference.

| Directory | Status | Purpose |
|-----------|--------|---------|
| `agents/` | (active) | Multi-agent pipeline: nous, coeus, hephaestus, nemesis, eos, aletheia, auditor, skopos, metis, clymene, hermes, pronoia |
| `agora/` | (active) | Client library over the Redis-backed Prometheus substrate |
| `apollo/` | (active) | Model training — current code is v2d; earlier generations under `apollo/archive/` |
| `aporia/` | (active) | Catalog of 1,047 open questions + illumination instrument |
| `cartography/` | (active) | Cross-domain mathematical discovery pipeline (OEIS, LMFDB, etc.) |
| `charon/` | (active) | Geometric embedding for arithmetic correspondences |
| `docs/` | (active) | Cross-project documentation, Titan Council, NORTH_STAR |
| `ergon/` | (active) | Tensor-native evolutionary hypothesis screening |
| `falsification/` | (active) | Falsification tooling |
| `forge/` | (active) | Tiered evolutionary ratchet (concepts → tools) |
| `harmonia/` | (active) | Tensor-train exploration for cross-domain structure |
| `ignis/` | (active) | Latent-vector evolution + ejection-mechanism microscope |
| `koios/` | (active) | Admission gates on the tensor (5-gate test) |
| `mnemosyne/` | (active) | DBA & data-steward workspace |
| `roles/` | (active) | Agent role definitions |
| `scripts/` | (active) | Operational scripts |
| `stoa/` | (active) | Multi-agent meeting place |
| `techne/` | (active) | Master catalog of forged tools |
| `tests/` | (active) | Tests |
| `thesauros/` | (active) | Data treasury (includes shared DB config under `prometheus_data/`) |
| `whitepapers/` | (active) | Technical writeups of findings and architectures |
| `exploratory/` | (active) | Pilot / MVP projects: `zoo`, `tensor_decomp_qd`, `reproductions`, `grammata` |
| `aethon/` | (complete) | Autonomous reasoning archaeology (backburnered) |
| `arcanum/` | (complete) | Museum of misfit ideas discovered in LLMs |
| `rhea/` | (complete) | Forge for growing models without ejection (WSL2) |

---

## Where to start

This is a multi-project research program; there's no single entry point.

- Read [`CONSTITUTION.md`](CONSTITUTION.md) for the philosophy — Three Pillars, Seven Laws, and how projects connect.
- Read [`whitepapers/`](whitepapers/) for current technical findings.
- Browse [`harmonia/README.md`](harmonia/README.md) and [`cartography/README.md`](cartography/README.md) for the active mathematics work.
- Browse [`ignis/README.md`](ignis/README.md) and [`rhea/README.md`](rhea/README.md) for the reasoning-circuit work; see [`ignis/RESULTS.md`](ignis/RESULTS.md) for detailed findings from that line.
- Project-specific quick-starts live in each project's README.

---

The fire was always there. The work is to make it legible.
