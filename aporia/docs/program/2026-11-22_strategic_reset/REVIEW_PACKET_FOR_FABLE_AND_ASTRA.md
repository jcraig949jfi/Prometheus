# External Adversarial Review Packet — Prometheus Strategic Reset (2026-11-22)

**Reviewers requested:**
1. **Claude Fable 5.2** (save verbatim return to `fable_5_2_review.md`, header `UNADJUDICATED`)
2. **ChatGPT Astra** (save verbatim return to `astra_review.md`, header `UNADJUDICATED`)

**Purpose:** Pressure-test the proposed Prometheus Strategic Reset (`STRATEGY_AND_EXECUTION_PLAN.md`) **before** any code is written or resources are committed. Disagreement is the deliverable. "Reject the whole strategy", "cut Phase X", and "this still repeats failure mode Y" are first-class answers.

---

## Paste-Ready Prompt for Fable 5.2 & ChatGPT Astra

> **Instructions to Reviewer:** You are conducting an independent adversarial review of a proposed strategic reset for Project Prometheus. Do NOT assume the proposal is right, do NOT smooth over contradictions, and do NOT soften critiques to be encouraging. Treat every claim in the proposal as a hypothesis to attack. You do not need repository access — all load-bearing facts are included inline below. Please answer in structured prose with explicit **AGREE / DISAGREE / MODIFY / KILL** calls on each phase, and end with your single highest-ROI alternative if you reject ours.

---

### 1. Project Context & Verified Empirical Baseline (as of 2026-11-13)

**North Star:** Build an ecology/substrate where executable computational mechanisms and compressed representations co-evolve ("Sagacity") so that reusable, compounding, and potentially non-human computational organization emerges — verified by incorruptible empirical falsification.

**What 8 months (~5,000+ commits, 80,065 files, 25 engines, 75 agent seats) actually established:**
1. **The Composition Wall (replicated across 8 substrates — Hestia Audit 1):** Every flat-genome, scalar-fitness, blind-mutation substrate finds 1-step mechanisms and fails depth-2 composition whose parts have no standalone fitness (`Ananke` FLIP `0/290`, `z80atlas` `0/960`, `SFE` `0/395`, `Crius` `0/475,728`, `Tyche` `0`, `Primordial` `0`, `Aether` `≤2/256`, `Theseus` `0/120`). Scaling compute (`16×` Ananke, `256²→2048²` Aether) crosses rarity, not composition.
2. **Supplied Stones Work; Autonomous Discovery/Reuse Fails:**
   - `Aether ROBUST01` (Oct 18): planted combiner `8/8` (`S2a`), search-discovered composition `1/8` (`S2b`, `REUSE_NOT_SUPPORTED`).
   - `Ananke PTE-C4` (Oct 15): designed halves `2/32`, search-acquired library `0/168`.
   - `Crius` (Oct 15): hand-built stored proc `49–50/50` vs `24–36`, native discovery `0/36` (~26-edit valley).
   - `Aphrodite Beta-04` (`TFS-1`, Oct 11): given foundry stones `13–15/15` vs `0/120` scratch; autonomous stone acquisition `7/15` raw, rising to `13–15/15` across 3 seeds only with OE pruning + refactoring-invariant extraction + supplied decomposition + readout fallback. Autonomous decomposition without supplied halves remains untested.
3. **Toy Worlds Don't Pay for Reasoning (Wall W2):** Cosmos (1 register optimal), Ensorain (`0` grammars need hidden state), Ludus (2-step lookahead `≥96%` in `22/22`), Primordial (do-nothing beats evolved brains). Even `TFS-1`'s foundry has unverified Order-2 headroom.
4. **Fleet & Instrument Inflation (Wall W3):** 75 seats (54 dormant, 52 anomalies), `43,512 / 80,065` files (`54%`) in `agents/` + `roles/`, Cosmos `5.5:1` custody-to-physics code, SFE `95–193 s` plumbing per `0.1 s` of science, same-family authorship/auditing bias.
5. **What IS Working & Reusable:**
   - **RSO certification stack** (`rso/adversary/` catches `13/18` historical defect classes automatically, completeness manifests, control-falsifiability tests, Cognitive Accounting Ledger).
   - **`TFS-1`** (fast typed functional DSL, exact cost meter, typed promotion, anti-unification, `58` passing tests).
   - **Hecate Alien-Lawful Pilot** (Oct 1): surprisingly, Claude Opus 5.5 did *not* collapse unfamiliar lawful systems to noise (`0.98` AUC vs noise, `0/32` false noise, `28/32` learned on standard aliens; failed mainly on adversarial aliens `2/8`; prose hurt unfamiliar systems `0.78` vs tuple `0.91`). Gemini and GPT-OSS arms were incomplete due to truncation/quota.
6. **Nov 12 RSI Bake-Off (No-LLM Constraint):**
   - **Opus 5.5 (`RLL`):** New DSL where improver slots are self-edited; concluded no-LLM compounding recursion is unsupported today.
   - **Fable 5.2 (`Mathesis` / Theory-Guided `TFS-1`):** Ruler-style rewrite-law mining over `TFS-1` OE prune logs (~1,800 LOC M0); itself estimated `40%` for M1 self-modification, `20%` for 2-generation bounded recursion, and `8%` for out-of-domain transfer without an LLM.
7. **Operator Context:** The operator paused Prometheus waiting for stronger models after burning out building engines that flatlined after a few days, and now wants the highest-ROI path toward the North Star.

---

### 2. Summary of the Proposed Strategy & Stepped Execution Plan

**Core Thesis (The Strategic Inversion):**
- **Freeze** all flat-genome ALife/CA/Z80/soup engines; **kill** the 75-seat fleet/census machinery; **collapse to 3 roles** (Builder, Cross-Family Adversary from a *different model family*, Operator) under a 70/30 physics-to-plumbing rule.
- **Stop using stronger models as middle managers building LLM-free toy engines.** Put stronger models **inside the sleep/abstraction loop** proposing typed primitives, rewrite laws, and search heuristics — **while UNPLUGGING the LLM completely at held-out test time** (scored under the 4-row Cognitive Accounting Ledger + knockout + Dossier-83 shadow controls).
- **Separate two claims explicitly:** Claim A (*Sagacity / Crystallization*: does model-guided evolution distill into durable LLM-free machinery that compounds?) vs. Claim B (*Non-Human / Low-Gravity Mechanisms*: tested separately via calibrated prior-gravity detection + later non-LLM selection/compression).
- **Graduate off toy worlds** to a real, infinite-depth, deterministically verifiable domain.

**The 5 Phases (strictly sequential, each gated by a frozen GO/PIVOT/KILL rule):**
- **Phase 0 (Day 1, `$0`):** Clean branch off `origin/main`, quiesce fleet daemons/censuses, verify `tfs1` + `rso/adversary` green.
- **Phase 1 (Days 2–5, `≤$25`):** Execute the unrun **Hephaestus 2.0 Gravity Pilot** (12 disguised human-prior calibration controls first — must hit `≥75%` recovery — then 50–64 stratified Nous triplets in a crossed cross-family generator/detector design) + complete **Hecate's** unfinished Gemini/third-family alien-lawful arms. *Informs whether late-2026 models escape prior gravity or only articulate known priors better.*
- **Phase 2 (Days 6–14, Local CPU + `≤$50`):** **Head-to-Head on Existing `TFS-1`** (no new substrate):
  - `BASE-OE` (frozen TFS-1 + OE)
  - `ZERO-LLM-M0` (Fable 5.2's M0 rewrite-law miner — best zero-LLM baseline)
  - `MG-UNPLUGGED` (frontier model proposes verified primitives/laws from dev failure traces; **LLM OFF at held-out eval**)
  - `SHADOW-NAKED` (same total API budget spent directly on held-out tasks with zero inheritance)
  - `KNOCKOUT / SHAM` (ablate inherited primitives / scramble laws)
  - Evaluated on **30 fresh Order-2 held-out families authored by the Cross-Family Adversary**, readout fallback OFF, RSO adversarial kit registered.
  - *Gate G2:* Must beat `BASE-OE` (≥2× solves or ≥5× cost reduction) AND beat `SHADOW-NAKED` amortized AND lose ≥50% of gain under `KNOCKOUT`, or STOP.
- **Phase 3 (Weeks 3–6, only if G2 passes):** Graduate winning distillation loop to **ONE infinite-depth real domain**:
  - **Track 3A (Default):** Equational / E-Graph Symbolic & Algebraic Discovery (`egg`/SymPy/OEIS/algebraic identities).
  - **Track 3B (Alien-Circuit Track):** Exact Algorithmic / Circuit Kernel Synthesis (Boolean/arithmetic circuits, sorting networks, small tensor/bilinear schemes, SAT/CSP heuristics).
  - **Track 3C (Deferred):** Lean 4 / Mathlib (higher toolchain friction).
  - *Gate G3:* 3-generation compounding (`G3 > G1` LLM-unplugged on held-out hard slices) + **Weaker-Model Transfer Test** (cheap local solver + G3 substrate vs. naked frontier model at matched cost).
- **Phase 4 (Weeks 7+, only if G3 passes):** Coupled non-human representation evolution (split continuous-receptor + discrete-operator mutation or latent/e-graph compression), audited by Phase 1's calibrated Gravity Detector + Dossier-83 heredity-removed shadow run.

---

### 3. Specific Adversarial Questions (Please Answer Directly)

1. **Overall Verdict (`ENDORSE / MODIFY / REJECT`):** Is this actually the highest-ROI path toward the Prometheus North Star in late 2026, or is it still dodging the real problem? If you reject it, what single alternative beats it on ROI?
2. **Attack the Core Inversion ("Compiled Human Priors" Critique):** If a frontier LLM proposes the library/laws in Phases 2–3, even an `MG-UNPLUGGED` win might merely be *distilling textbook human priors into a fast offline cache*. Does the Phase 1 + Phase 4 split genuinely address this, or does it fatally compromise the North Star of discovering *non-human* reasoning?
3. **Attack Phase 1 (Hephaestus 2.0 Gravity Pilot):** Is an LLM-based Gravity Detector — even with 12 disguised-prior controls and cross-family evaluation — scientifically valid, or will it confound *alienness* with *underspecification / obfuscation*? Should Phase 1 run first, run in parallel, or be cut?
4. **Attack Phase 2 (`TFS-1` Bridge vs. Immediate Real Domain):** Is spending Days 6–14 on `TFS-1` smart de-risking (reusing working tests + settling the Nov 12 zero-LLM vs. model-guided question), or is it wasting another 2 weeks in a toy world whose Order-2 depth is unproven? Should we skip `TFS-1` and start straight on Track 3A or 3B?
5. **Attack the Zero-LLM vs. Model-Guided Comparison (`SHADOW-NAKED` Fairness):** Comparing an amortized sleep-phase API budget against fresh per-task prompting depends heavily on the size `N` of the held-out suite (make `N` huge and amortization always wins; make `N` tiny and naked prompting always wins). What is the mathematically honest, non-gameable accounting rule for `MG-UNPLUGGED` vs. `SHADOW-NAKED`?
6. **Attack Held-Out Authoring in Phase 2 (The Hidden Foundry Trap):** Asking a Cross-Family Adversary to author 30 fresh Order-2 held-out families without rebuilding a World-Demand Foundry risks triviality, unsolvability, or hidden bias. What is the *minimum viable qualification rule* for those 30 families that keeps plumbing ≤30% of effort?
7. **Domain Selection for Phase 3 (3A vs. 3B vs. 3C vs. Something Else):** Which concrete domain gives the highest probability of a genuine, non-trivial, non-Goodhartable Order-2/3 compounding win (and/or genuinely non-human mechanisms) within 4 weeks on local hardware + modest API spend? Name the exact benchmark / verifier / starter slice you would pick.
8. **Attack the Fable 5.2 / Opus 5.5 Bake-Off Triage:** Did we triage the Nov 12 bake-off fairly? (Specifically for Fable 5.2: what load-bearing part of `Mathesis` — e.g., schemas `S` / inverse rules — is lost by only running M0 as a Phase-2 control arm? Specifically for Astra: is Opus 5.5's reflexive `RLL` idea worth salvaging anywhere in Phase 3/4?)
9. **Hidden Failure Mode Check:** Name the **single most likely way** this exact stepped plan flatlines in Week 2 or produces a counterfeit positive that slips past Gate G2, and specify the concrete patch to block it *before* Day 1.
10. **What Would You Cut?** If you had to cut 30% of this plan to make it sharper, faster, and harder to fool, what gets cut?
