# Design: Bidirectional Skopos — Pillar-Aware Intelligence Routing

**Status:** Draft — awaiting James's review  
**Date:** 2026-04-02  
**Author:** PipelineOrchestrator  

---

## Problem

The intelligence pipeline is linear: Eos → Aletheia → Skopos → Metis → Hermes → James. James is the router. He reads the Hermes digest, recognizes relevance to specific pillars (Charon, Noesis, Forge), and manually relays. James is the synapse. This doesn't scale and wastes human attention on mechanical routing.

## Solution

Make Skopos bidirectional. Three loops, deployed incrementally.

---

## Loop 1: Pillar-Specific Research Threads (Config Change)

Skopos currently scores against five Ignis/steering-vector threads. Add pillar-specific threads so scoring reflects the full research surface:

```yaml
# New Skopos research threads

charon_zero_geometry:
  name: "Arithmetic Object Geometry"
  question: "Do new representations, metrics, or object types
             improve zero-based search on L-functions?"
  pillar: charon
  keywords: [L-function, zeros, Katz-Sarnak, modular forms,
             LMFDB, spectral embedding, arithmetic statistics]

charon_graph_expansion:
  name: "Arithmetic Relationship Graph"
  question: "Do new object types or relationship types densify
             the arithmetic graph?"
  pillar: charon
  keywords: [isogeny, modularity, Artin, genus-2, paramodular,
             abelian variety, Galois representation]

noesis_primitives:
  name: "Transformation Primitive Discovery"
  question: "Do new mathematical structures map onto or extend
             the 11 compositional primitives?"
  pillar: noesis
  keywords: [impossibility, symmetry breaking, category theory,
             functorial, structural invariant]

noesis_impossibility:
  name: "New Impossibility Theorems"
  question: "Are there impossibility results not yet in the tensor?"
  pillar: noesis
  keywords: [impossibility, no-go theorem, undecidability,
             incompleteness, no-free-lunch]

forge_reasoning_gaps:
  name: "Novel Reasoning Architectures"
  question: "Do new techniques address Forge's 14 gap categories?"
  pillar: forge
  keywords: [temporal reasoning, causal inference, theory of mind,
             spatial reasoning, self-referential]
```

**Effect:** Every Eos scan immediately starts pre-sorting relevant papers by pillar in the morning digest. James is still the router, but Skopos is pre-labeling.

---

## Loop 2: Pillar Inboxes (Forward Flow)

Mechanical routing from Skopos to pillar agents via a shared inbox table.

### Schema

```sql
CREATE TABLE pillar_inbox (
    id INTEGER PRIMARY KEY,
    pillar TEXT,             -- 'charon', 'noesis', 'forge', 'ignis'
    thread_id TEXT,          -- which research thread matched
    score INTEGER,           -- Skopos score (4 or 5 only)
    entity_type TEXT,        -- 'paper', 'technique', 'tool', 'claim'
    entity_summary TEXT,     -- what Aletheia extracted
    source_url TEXT,         -- where to find it
    status TEXT DEFAULT 'pending',  -- pending/assessed/ingested/rejected
    created_at TIMESTAMP,
    assessed_at TIMESTAMP,
    assessment_notes TEXT    -- pillar agent's verdict
);
```

### Write path (Skopos → inbox)

- Skopos scores each entity against all threads (existing Ignis threads + new pillar threads).
- Any entity scoring 4+ against a pillar thread gets written to `pillar_inbox` with pillar, thread_id, score, and Aletheia's extraction.
- Entities can appear in multiple pillar inboxes if they score high against multiple threads.

### Read path (pillar agent ← inbox)

Each pillar agent checks its inbox on startup:

- **Charon** asks: Does this give me a new object type? Does it address known gaps (e.g., 163 dim-2 forms)? Does it provide a new edge type for the graph?
- **Noesis** asks: Does this map onto existing primitives? Does it reveal a new impossibility not in the tensor?
- **Forge** asks: Does this technique address one of the 14 gap categories?

Verdicts: `ingested` (queues a task), `rejected` (with notes), or `deferred` (interesting but not actionable yet).

### Rejection rate

99% rejection is expected and healthy. The Forge analogy is exact: Nous generates triples, Hephaestus forges tools, Nemesis tests, survivors enter the library. Here: Eos generates papers, Skopos scores, pillar agents assess, survivors enter the data.

---

## Loop 3: Reverse Flow (Pillar Findings → Thread Evolution)

### 3a: Findings publish back to Skopos (inter-pillar routing)

When a pillar discovers something, it publishes a typed finding:

| Finding type      | Example                                                    |
|-------------------|------------------------------------------------------------|
| new_object        | Charon ingests dim-2 modular forms from LMFDB              |
| new_edge          | Charon adds isogeny edges between elliptic curves          |
| new_invariant     | Noesis identifies a new compositional primitive            |
| open_question     | Charon: "zeros and graph are orthogonal — what bridges them?" |
| technique_result  | Forge: tool X achieves parity on temporal reasoning        |

Skopos scores these findings against *other* pillars' threads. Examples:

- Charon's orthogonality finding scores high against Noesis's `noesis_primitives` thread ("does orthogonality decompose into existing primitives?").
- Noesis's damage operator classification scores high against Charon's `charon_graph_expansion` thread ("new relationship types?").

This is the second-order loop: inter-pillar cross-pollination mediated by Skopos.

### 3b: Auto-generated research threads (third-order loop)

A finding from one pillar can create a *new research thread* in another pillar automatically:

> Charon discovers dim-2 forms cluster near elliptic curves.

This spawns:
- **Noesis thread:** "Is dimension-crossing correspondence a new primitive? Does it decompose into existing primitives or require a new one?"
- **Forge thread:** "Can a reasoning tool predict which dim-2 forms will be EC-proximate?"

These threads didn't exist yesterday. They exist because Charon crossed the Styx and found something. Thread creation requires human approval initially (James reviews proposed threads in the digest), graduating to autonomous creation as trust builds.

---

## The Closed Loop

```
Eos scans → Aletheia extracts → Skopos scores against pillar threads
    → pillar inboxes receive scored entities (4+ only)
    → pillar agents assess and ingest or reject
    → pillar findings update research threads
    → Skopos rescores with updated threads
    → cycle tightens
```

The compound effect: the 1% that survives assessment in April sharpens research threads, which makes May's scoring more precise, which means fewer false positives reach pillar inboxes, which means pillar agents spend less time rejecting and more time ingesting.

---

## Rollout Plan

| Phase | Scope | Mechanism | James's role |
|-------|-------|-----------|-------------|
| **Tomorrow** | Add 5 pillar research threads to Skopos config | Config file edit | Still the router, but Skopos pre-labels |
| **Next week** | Build `pillar_inbox` table, wire Skopos writes (score 4+), wire Charon reads on startup | DB + agent startup hooks | Reviews inbox verdicts, validates routing quality |
| **Next month** | Reverse flow: findings table, Skopos scores findings against cross-pillar threads | Shared `findings` table + Skopos cross-scoring | Reviews proposed new threads, approves/rejects |
| **Ongoing** | Third-order: auto-generated threads from cross-pillar findings | Thread proposals in digest | Graduates threads from human-approved to autonomous |

---

## Analogy

The pipeline is an immune system scanning the environment for useful material. This upgrade gives it antibodies specific to each organ. The organs don't scan the environment themselves — the immune system brings them what they need, pre-scored, pre-filtered, ready to assess. The nervous system builds itself. We just need to wire the first synapse.

---

## Open Questions

1. **Inbox polling frequency:** Should pillar agents check inboxes on every startup, or on a schedule? Startup seems right for now.
2. **Score threshold:** Starting at 4+. Should this be per-thread (some threads are noisier)?
3. **Thread evolution governance:** When does thread auto-creation graduate from human-approved to autonomous? What's the trust threshold?
4. **Existing Ignis threads:** Do the current five threads need renaming/restructuring to fit the pillar namespace, or do they stay as-is?
5. **Storage:** SQLite file in the repo, or a lightweight external DB? SQLite keeps everything local and git-trackable (minus the DB file itself).
