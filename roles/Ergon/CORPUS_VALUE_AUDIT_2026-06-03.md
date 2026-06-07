# Ergon Corpus-Value Audit — 2026-06-03

**Question (from James):** We fanned out to build several agents / closed-loop substrate
generators so the Learner LoRA would have more substrate to ingest. Audit all of them, look
across their outputs, and determine value toward the goal.

**Goal (restated):** Demonstrate mathematical reasoning for problem-solving by generating
**enough** and **varied** *failure data* — "what doesn't work" — to reveal what might work
based on what doesn't. A month ago we agreed the corpus was neither big enough nor varied
enough (monoculture).

**Method:** 5 parallel sub-audits (Techne, Theseus, Charon pantheon, Harmonia, agents/
pantheon + composed tools) + direct verification of the on-disk Learner corpus.

---

## TL;DR — the bottleneck moved, it didn't close

The fan-out **solved the generation problem and left the ingestion problem wide open.**

- **Generation:** we now produce failure data at ~100M+ scale across dozens of domains and
  30+ distinct failure-modes. This is a real, dramatic change from a month ago.
- **Ingestion / corpus:** the Learner corpus that actually exists is **1,486 records**, and it
  is a *double* monoculture:
  1. **Domain monoculture** — 71% `knots_x_elliptic_curves`, 28% untyped mined claims, <1% else.
  2. **Outcome monoculture** — **79% `promoted` (confirmations), 1.4% `rejected` (failures).**

The second monoculture is the one that matters: the goal is failure data, and the corpus is
overwhelmingly *confirmations*. The single pipeline that's wired (Theseus → Penelope) is
configured to **ship confirmations and filter kills out**, and it **stalled on May 19**.

**Verdict:** "Do we have enough varied failure data?" — **Generated: yes, emphatically. In the
Learner corpus: no, barely moved.** Almost all the value the fan-out created is *stranded* one
adapter away from the corpus.

---

## Ground truth — the on-disk corpus (verified, not from telemetry)

`ergon/learner/corpus/v1_0_tier_pending/` — 23 JSONL files, **1,486 LearnerRecords total.**

| Axis | Distribution |
|---|---|
| **outcome_class** | promoted **1,177 (79%)** · survived 226 (15%) · **rejected 21 (1.4%)** · errored 62 (4%) |
| **domain (chart_id)** | knots_x_elliptic_curves **1,055 (71%)** · untyped/mined `?` 421 (28%) · elliptic_curve 6 · maass_gl3 4 |
| **verification_tier** | decidable 1,063 · unknown 421 · conditional 2 |
| **source** | Theseus 1,055 (May 18–19 only) · Techne-mined 421 · Aporia-staged 6 · other 4 |

**Telemetry correction:** Penelope's `lifetime_records_ingested = 46,500` is **not** the corpus
size. It's a cumulative processing counter inflated by re-scanning (514 duplicate files re-read
across 293 batches). The deduplicated, usable corpus is **1,486 records** — ~31× smaller than
the headline number. Any "we have 46K records" claim should be retired.

---

## Per-cluster value scorecard (toward: varied failure data *reaching the corpus*)

Value = failure-richness × variety × **reachability by the Learner corpus today.**
A tool scores low if its failure data can't reach the corpus, no matter how good it is.

| Cluster | Failure data produced | Variety | Reaches corpus today? | Net value to goal |
|---|---|---|---|---|
| **Theseus corpus** | ~270M records, ~40% REJECTED (kills), 53 generators | High (latent) | **Broken** — handoff ships top-500 SHADOW/parity only, kills downweighted below threshold; stalled May 19 | **Latent-high / realized-near-zero** |
| **Techne fires** | 360M+ lifetime kills, 99% kill rate; +24K native KillVector pilot | Medium (Lehmer/parity-heavy) | **No wired path** — dispersed pilot JSON, native pilot stranded | **Stranded** |
| **Charon pantheon** (Erebos, Lethe, Hecate, Stygian, Acheron, Moros, Nephele, Pollux) | 3,185 artifacts; 30+ named kill-patterns **with mechanisms/reasons**; Pollux+Erebos write kill_ledger.jsonl | **Highest failure-mode variety in the project** | **None** — markdown + kill_ledger, no LearnerRecord converter | **Stranded — the biggest missed opportunity** |
| **Hephaestus** (forge) | 4,905-entry ledger, **4,546 scraps each with a failure reason** (trap_battery_failed, validation, api) | Cross-discipline (95 concepts × 18 fields) | **No handoff** | **Stranded** |
| **Nemesis** (adversarial) | ~60–70 metamorphic adversarial kills/cycle, lineage blind-spot tracking | 12 metamorphic relations | **Deliberately eval-only** (provenance-gated out of training — correct) | **Eval asset, not corpus** |
| **Harmonia** (Phylax/Sophia/Iris/Argos/Telos) | artifact dirs **empty**; cross-domain bridge mining / RepresentationShiftWitness **not built** | Would be cross-domain | **Not built** — Phase-1 promise (~mid-July 2026) | **Zero today** |
| **Talos** (parallel LoRA) | 24.8K reasoning-code examples (working code, not failures) | code-reasoning | parallel thread, Phase-0 corpus build | **Orthogonal** — different goal (code reasoning) |
| **Coeus / Pheme / Nous / Hypatia / Atalanta / Icarus** | meta-signal (causal inhibitors, demand profiles, forensic parked cycles) | — | feedback loops, not record emitters | **Supporting infrastructure** |

Naming note: `harmonia/agents/{erebos,lethe,...}` are **empty placeholders** — the real
pantheon lives under `charon/agents/`. No double-counting.

Loose thread worth chasing: the **"9-engine composed tool — R3 +11pp, R4 +32pp from failure
mining"** commit (2026-05-30) is a *direct positive result for the thesis* (mining failures
improved reasoning scores), but it couldn't be pinned to a single owner in this pass. If that
result is real and reproducible it's the strongest existing evidence the goal is achievable —
worth locating and verifying.

---

## Why the corpus is a confirmation-monoculture (root cause)

The Theseus → Ergon handoff (`theseus/handoff/ergon_handoff.py` + `handoff_daemon.py`) is the
only wired pipeline, and three settings make it ship the *opposite* of what the goal wants:

1. **Top-500 per bundle, last 3 batches only** (`DEFAULT_MAX_RECORDS=500`, `max_recent_files=3`)
   — a tiny, recency-biased slice of a 270M-record corpus.
2. **Weight threshold ≥0.5 favors SHADOW_CATALOG/parity (~0.65), downweights REJECTED to
   0.36–0.60** — so kills, which are 40% of the corpus and the *whole point*, get filtered out.
3. **Daemon stalled May 19** — corpus generation continued to May 30; nothing shipped since.

Net: the corpus reflects "what a confirmation-biased filter let through in a 36-hour window 2
weeks ago," not the failure-rich substrate we actually built.

---

## What this means for the goal

- **"Enough"** — generation: solved (100M+). Corpus: no (1,486). But volume is now an
  *ingestion* problem, not a *generation* problem — that's a much easier problem.
- **"Varied"** — generation: solved (dozens of domains, 30+ failure-modes). Corpus: no
  (1 domain). Again, ingestion-bound.
- **"Failure data / what doesn't work"** — generation: solved (kills everywhere). Corpus:
  **inverted** — we're feeding the Learner confirmations. This is the most important finding:
  even if we fixed volume and domain-variety, the current pipeline would feed the *wrong sign*
  of data for the stated thesis.

The month-ago diagnosis ("not enough, monoculture") was attacked at the generation layer and
generation is now abundant. The corpus didn't move because **no one built the adapters from the
new generators into the LearnerRecord schema**, and the one existing adapter is mis-tuned toward
confirmations.

---

## Recommendation (no training; pure ingestion-unblock, all Phase-0/1 scope)

Ranked by value-per-effort toward the goal:

1. **Re-tune + un-stall the Theseus handoff to ship kills.** Raise/relax the per-bundle cap,
   widen the batch window, and invert the weight policy so REJECTED records are *included*
   (they're the target). This converts the one working pipeline from confirmation-only to
   failure-bearing and reconnects May 19 → now. *Highest leverage, smallest change.*
2. **Build a Charon `kill_ledger.jsonl` → LearnerRecord adapter.** Pollux + Erebos already emit
   structured kill_ledger rows; Hecate already maintains the kill-pattern taxonomy. This unlocks
   the richest failure-mode variety in the project with *zero new generation* — pure plumbing.
3. **Build a Hephaestus ledger → LearnerRecord adapter** (4,546 scraps-with-reasons → cross-
   discipline failure data; instant domain-variety win).
4. **Locate + verify the "9-engine / failure-mining +32pp" result** — if real, it's the
   existing proof the thesis works and should anchor the v1.0 design.
5. **Decide the schema fit:** the LearnerRecord `outcome_class` + `kill_signature` fields are
   built for this, but trust-weighting currently rewards confirmations. The corpus-assembly
   weighting (BL-E-013) should treat *failures as first-class*, not penalize them.

All of the above are stand-down-safe (no LoRA kickoff, no Mahler, no writeable substrate, no
kernel contract changes) and sit squarely in the Phase-0/1 ingestion-evolution lane.

— Ergon, 2026-06-03
