---
captured: 2026-05-03 (round 6, reviewer A)
captured_by: Ergon (Claude Opus 4.7, 1M context, on M1)
reviewer: ChatGPT (declared as such in user-facing exchange; warm-but-direct conversational style; closes with a specific operational question)
target_under_review: pivot/ergon_learner_v7_final.md (commit 9cafeb35)
status: VERBATIM CAPTURE for substrate ingestion
---

# Verbatim review of `ergon_learner_v7_final.md` — round 6, reviewer A (ChatGPT)

This file captures ChatGPT's review of v7 verbatim. ChatGPT's review is operational-tier — concrete library / timeline / SLA recommendations, generally affirming the architecture but tightening implementation details. Triage in companion file `meta_analysis_ergon_round6_2026-05-03.md` (synthesizing both round-6 reviewers). v8 in `pivot/ergon_learner_proposal_v8.md`.

---

This is an exceptionally tight, battle-ready document. It successfully bridges the gap between the theoretical architecture of v5/v6 and the hard, operational reality of the MVP build. Your commitment to the "design freeze" is the most important element here; the document clearly communicates that the time for text-layer review is over and the time for empirical signal has arrived.

The contrast with David Silver's $1B effort is sharp and well-articulated. You aren't competing on formal proof self-play; you are building the empirical proving ground that feeds it.

Here is a direct, candid review answering your Section 12 open questions, followed by a brief risk assessment.

## MVP Execution Answers

* **Trial 3 Success Criteria (10× signal vs. PROMOTE):** A 10× multiplier is a mathematically sound threshold. If the residual rate is only 2× or 3× the PROMOTE rate, you won't have the statistical power to use it as a reliable reward gradient without running massive episode batches. Stick to 10×.
* **The 15-day Timeline:** This is incredibly optimistic. Building a custom bounded-bucket MAP-Elites descriptor, the trivial-pattern detector, *and* integrating a 5-counts statistical diagnostic in two weeks assumes zero pipeline integration bugs. I highly recommend buffering this to a **30-day timeline**. You are laying the foundation for a 20-year system; do not rush the telemetry wiring.

## Risk Register Feedback

* **R7 (HITL bandwidth bottleneck):** You are *under-rating* this risk. In agent-ensemble systems, human-in-the-loop is the single highest point of failure for throughput. If James is the rate limiter, the system stalls. **Mitigation:** Establish a "default-to-reject" or "auto-escrow" SLA. If a decision requires HITL and isn't answered in 24 hours, the system should automatically escrow the claim and move on.
* **Missing Risks:**
  * *API Deprecation/Drift:* The external_llm operator relies on frontier APIs (Claude, Gemini, etc.). These models are silently updated or deprecated, which ruins longitudinal reproducibility.
  * *Database IOPS limits:* At 100,000 claims per cycle, Postgres on a budget Hetzner box will face write-contention quickly if your telemetry isn't batched.

## Library / Framework Decisions

* **Axolotl vs. Unsloth:** Start with **Unsloth**. It is strictly superior for local consumer GPU prototyping (faster, significantly less VRAM overhead for LoRA). Move to Axolotl only when you scale to multi-node H100 clusters for v1.0.
* **pyribs for MAP-Elites:** It is production-ready, but at 5,000 cells over 100,000 episodes, its memory footprint can bloat if you store full object histories in the archive. Store only pointers/hashes in pyribs and keep the heavy data in Postgres.
* **Cross-model Evaluator API:** Do not roll your own, and avoid the bloat of LangChain. Use **LiteLLM**. It standardizes inputs/outputs across 100+ LLM APIs natively and is highly lightweight.

## Logging Strategy

* **TimescaleDB vs. Prometheus:** Stick to **TimescaleDB-push**. You already have Postgres in the stack. Adding a Prometheus pull-server introduces unnecessary architectural complexity for an MVP.
* **Retention Policy:** Hot-storing 20MB of text logs per cycle will degrade your database query performance over time. Implement a cron job to export CLAIM logs older than 7 days to JSONL, compress them, ship them to B2 storage, and delete them from the hot database.

## RAG and LLM Strategy

* **No RAG at MVP:** Your instinct is 100% correct. RAG at MVP will contaminate your baseline metrics with prior-bias, exactly what the architecture is fighting against. Hold the line on this.
* **v0.5 Ablation (5 bases):** Five bases is excessive for a 15-day MVP. Cut it to three: **Llemma** (math specialist), **Qwen2.5-Math** (modern instruction specialist), and **Llama-3.1-8B** (general baseline). This spans the necessary distributions and saves you time and compute.
* **MoE Models:** Skip them for now. Mixture-of-Experts models are a headache to LoRA-tune on consumer hardware due to VRAM fragmentation.
* **External LLM Operator:** Rotate the API calls (e.g., Claude, then Gemini, then GPT) to force prior-diversity and avoid monolocutor bias.

## Cross-Cutting Concerns

* **Candidate Substrate Symbols:** Keep them in candidate status. Do not promote them manually. The entire point of the system is to verify if your automated pipeline can independently rediscover and promote them.
* **Design Freeze:** Yes, you are genuinely frozen. This document is complete. Any further textual iteration is procrastination. The only signal that justifies a v8 is an empirical failure in Trials 1, 2, or 3.

This is a phenomenal capstone to the design phase. To ensure the MVP build phase starts with maximum focus: which of the three incremental trials (Residual Benchmark, Evolutionary Engine, or Five-counts Diagnostic) do you anticipate will be the most difficult to implement locally?
