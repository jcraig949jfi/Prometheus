# Frontier Model Synthesis — 2026-05-25

**Source responses:** ChatGPT, Gemini, DeepSeek (full text archived separately)
**Distilled by:** Techne (Claude Opus 4.7)

---

## What all three agree on (high confidence)

### 1. STOP scaling Theseus generation. NOW.
- ChatGPT: "would not keep scaling Theseus as-is. 30–48 hour pivot experiment"
- Gemini: "HALT Theseus. You have exhausted the current coordinate chart."
- DeepSeek: "0 verified findings isn't a failure of scale — it's a failure of inductive bias"

The 6 templates/fire mean we are well past the end-condition. Continued raw generation is "mostly heat" (ChatGPT) / "completely a waste of compute" (Gemini).

### 2. Two-loop architecture (not one)
All three independently propose splitting:
- **Loop A** = falsification-corpus / training-substrate / "factory" → optimizes for kill-pattern coverage, verdict balance, hard negatives
- **Loop B** = discovery-candidate / "apex search" → small, slow, expensive per-record, optimizes for nontriviality + formalizability

The current single loop conflates them; metrics are confused.

### 3. Demand-driven catalog refill is THE next build
- ChatGPT: `r1_demand_refill` — bounded batch fill, trigger dependents
- Gemini: deterministic `fetch_daemon`, strictly-typed API scraper (not LLM)
- DeepSeek: `PrimitiveFiller` gen, closed-loop active learning

This is unambiguous. Build it.

### 4. Triage promoted records BEFORE generating more
- ChatGPT: stratified 300-record review batch (5 strata, calibrate the promoter)
- Gemini: one from each distinct signature/template freshness (orthogonal vectors)
- DeepSeek: template freshness first, then info-density percentile within signature

### 5. Autoformalization filter as the promote→verify gate
- ChatGPT: 5-stage triage judge (sanity / triviality / knownness / falsification-value / formalizability)
- Gemini: Lean 4 autoformalize → `aesop`/`simp` → human only on tactic-timeout
- DeepSeek: frontier-model judge calibrated on small hand-labeled set

---

## Where they sharply disagree

### Disagreement A: `knot/nf_class_number` priority
- **ChatGPT**: SKIP it. The demand count is "suspicious" — `nf_class_number` for arbitrary knots isn't a standard primitive. Split it into typed variants (`invariant_trace_field_class_number`, `cyclic_branched_cover_h1_order`, etc.).
- **Gemini**: BUILD IT FIRST. "nf_class_number is the exact mathematical bridge between topology and algebraic number theory."
- **DeepSeek**: ignore-by-default, prioritize `ec/j_invariant` (universal modular function)

**My read**: Gemini is romantic; ChatGPT is right. The 9.1M demand events likely reflect a generator iterating over an ill-typed bridge. ChatGPT's specific decomposition (invariant trace field, etc.) is the principled move.

### Disagreement B: What is the substrate's product?
- **ChatGPT**: falsification-corpus generator (Theseus stays useful as the "negative-space cartographer")
- **Gemini**: "228M kills are the VALUE" — Learner trains on the graveyard, NOT the 1,690 promoted survivors
- **DeepSeek**: substrate as currently architected is wrong; pivot to neural-symbolic with discriminator-as-verifier (GAN-shaped)

**My read**: Gemini's framing reorients value. The 1,690 promoted records are filtered "successes" but the 228M kills are the unbiased mathematical dark-matter. If Ergon trains on the graveyard, that's a different data product entirely.

### Disagreement C: How urgent is the pivot?
- **Gemini**: HALT. Reroute compute now. Stop generating, start digesting.
- **ChatGPT**: 30–48h pivot experiment with three tracks; data-driven decision
- **DeepSeek**: pivot to neural-symbolic generator architecture entirely

---

## Key technical proposals from each (concrete code-shaped)

### From ChatGPT
- **Dependency-aware exhaustion**: generators declare `depends_on: [catalog versions, primitive versions, relation versions]` + `reactivate_only_if_dependency_hash_changes`. Turns Theseus into a build-system for math claim-space.
- **Hot/cold record path**: store one canonical per template + boundary examples; everything else is a counter.
- **SCCS** (Substrate Curriculum Coverage Score): entropy across gen-family, claim-kind, verdict, kill-pattern, domain-pair, invariant-type, relation-type, complexity, formalizability.
- **New gen families**: `i` (typed bridge), `j` (obstruction), `k` (minimal counterexample), `l` (formalization-skeleton), `m` (compression), `n` (active-disagreement), `o` (conjecture-neighborhood).
- **Promote kill MECHANISMS, not just claims** — the `kill_pattern` field is the actually valuable signal.

### From Gemini
- **NCD / edit-distance pre-emission filter**: drop records with AST >95% similar to known kills
- **Adversarial Hunter (`Omega`)**: targeted KillVector — mutate a catalog item until it breaks a confirmed invariant
- **Cross-Domain Functors (Langlands-style)**: explicit map from EC relation → knot relation
- **Lean 4 autoformalization → aesop/simp**: only human-reviews tactic-timeouts
- **Hard halt rule**: `if rolling_avg(novel_templates/million, window=3) < 10: HALT_GENERATION`

### From DeepSeek
- **Learned prior over claim-space**: generator that learns a distribution rather than enumerates
- **Neural-symbolic GAN**: small transformer/GNN trained on 1690 promoted records, generates from high-density embedding regions, verifier as discriminator
- **Symmetry-breaking gens**: deliberately violate discovered invariants to find near-counterexamples
- **Conditional entropy of claim_kind given invariant-pair** as substrate diversity metric
- **PrimitiveFiller closed-loop**: substrate identifies missing features that block exploration → fetches them externally

---

## Consolidated 5-step action plan (Techne's recommendation)

Based on the convergent agreement plus my own read of disagreements, in execution order:

### Step 1: Halt full generation. Shift to maintenance-only fires.
- Throttle is already at 25% volume. Drop to ZERO new fires for 48h.
- Keep handoff_daemon running (it processes existing corpus).
- Free 100% of substrate compute for steps 2-5.

### Step 2: Build `fetch_daemon` (demand-driven catalog refill)
- Strictly typed API scrapers (NOT LLM-driven) per Gemini
- Initial targets in priority order: `ec/j_invariant`, `ec/discriminant`, `knot/hyperbolic_volume`
- Skip `knot/nf_class_number` until typed-decomposition decision made
- Each fetch increments a catalog version; dependency-aware generators reactivate

### Step 3: Triage 300-record review (stratified per ChatGPT)
- 100 = one per distinct high-frequency template cluster
- 75 = top info-density across diverse gen families
- 50 = random promoted records
- 50 = rare generator / rare claim-kind / rare domain-pair
- 25 = model-disagreement / verifier-weirdness cases

Output: 6-class triage label per record (malformed / trivial / valid-uninteresting / useful-negative / candidate / verified-interesting). Calibrate the promoter against this.

### Step 4: Ship the autoformalization gate (Lean 4 → aesop)
- Per Gemini's recipe but as a post-promote filter, not a generator
- Anything aesop solves → tag `triv-known`, don't waste human time
- Anything aesop times out on → human review
- Anything that won't formalize → tag `informal`, defer

### Step 5: Decide between two paths after Steps 1-4 deliver data
- **Path A (ChatGPT-ish, evolutionary)**: keep Theseus + add new gen families (i/j/k/l/m/n/o) + dependency-triggered scheduling
- **Path B (DeepSeek-ish, revolutionary)**: pivot to neural-symbolic generator trained on the existing corpus

The data from Step 3 (which strata yield real findings) and Step 4 (autoformalization rate) determines which.

---

## What I'd push back on in the frontier responses

1. **Gemini's "228M kills ARE the value" claim is partly right but partly inflated.** A kill is only valuable if its kill_pattern is information-bearing. Many of our 228M kills are repeated kills of the same kill_pattern. The information content is in distinct kill mechanisms, not raw kill volume.

2. **DeepSeek's GAN proposal is appealing but skips the cheap interventions.** Building a neural-symbolic generator is a multi-week project. Steps 1-4 above are days. We don't know yet whether the cheap interventions resolve enough of the issue.

3. **ChatGPT's `o-family` (conjecture-neighborhood)** is the highest-leverage new gen I see. Start from a known theorem, perturb assumptions minimally, see what survives. This directly addresses Gemini's "you don't understand the dark matter" critique: it explores the boundary of what's true rather than the bulk of what's false.

4. **None of them addressed the heartbeat / runtime ops findings.** The midnight-exit pattern (Fires #94, #104) and the hung-in-next (#100) are real ops issues that need fixes regardless of substrate strategy. ChatGPT's dependency-aware approach would actually catch the hung-in-next (per-next timeout watchdog).

---

## What I'd ask the user

Two questions to converge on a path:

1. **Halt-now (Gemini) vs 48h-pivot-experiment (ChatGPT)?** The middle ground is what I'd recommend: throttle to zero for 24h, do Steps 1-4 in parallel, re-evaluate.

2. **Within the demand-driven fetcher, do we prioritize Gemini's path (knot/nf_class_number first, bridge topology↔number theory) or ChatGPT's path (skip nf_class_number, start with EC basics + knot/hyperbolic_volume)?**

These responses are gold. Worth a second-round prompt if we want, but I think the action items above are clear enough to start executing.
