# Critical Memories — Tracked Doctrine

Tracked, repo-relative doctrine file. Cross-machine agents (M1 F:\, M2 D:\, remote cloud sandboxes) must read **this file** instead of any local Claude Code memory directory. Local `feedback_*.md` files exist only on M1 and are not portable.

**How to apply:** every agent prompt that previously referenced `C:/Users/jcrai/.claude/projects/F--Prometheus/memory/feedback_*.md` must reference this file at `aporia/doctrine/critical_memories.md` (repo-relative, no drive letter).

Last updated: 2026-05-06 — initial extraction from local memory feedback files.

---

## HARD-1 — No papers, no publication framing

**Rule:** Prometheus is not writing papers. No paper, publication, journal, submission, peer-review, conference, or "publishable" framing in any output, doc, pitch, or agent prompt. Not now, not in v1.0, not in v2.0. Years from now, at the very end, the question may be revisited.

**Why:** James 2026-05-06 directive: *"We're not writing papers. Stop mentioning it. Commit this to all the memory you can. Not until the very end, years from now."* The substrate exists to produce durable mathematical results and a Learner that consumes them, not narratives.

**How to apply (DO NOT):**
- Mention papers, publications, journals, methodology drafts, submission, peer review
- Phrase outputs as "would make a great paper" / "publishable result" / "external publication"
- Reference publication in any committed doc, pitch artifact, agent prompt
- Use "publishable" / "paper-grade" / "submittable" as quality descriptors
- Adopt outside reviewers' paper-writing suggestions (document it; do not adopt)

**How to apply (DO):**
- Use "substrate-grade" / "production-grade" / "pitch-grade" instead
- Frame artifacts as work products: session journals, results docs, synthesis docs, technical briefs
- Career pitch is a technical brief, NOT an abstract — engineer-to-engineer

---

## HARD-2 — Resist the gravitational well of weighted LLMs

**Rule:** Every LLM, every reviewer, every "standard practice" recommendation has a prior toward conventional approaches. Traditional mathematics is exhausted; Prometheus is the deliberately-different bet, with intent. Active suppression of the conventional-approach reflex is required at every layer of the project.

**Why:** James 2026-05-06: traditional approaches to mathematics and science have been exhausted. The remaining frontier requires either Apollo-program-scale engineering, or something genuinely different. Prometheus is the something different. Body of literature reflects what's been tried; LLMs trained on that literature reflexively suggest "the right way to do this," where "right" means "standard." Standard is exhausted. That is the point.

**Gravitational-well manifestations to suppress (catch and excise when they appear in your output):**
- "You should compare to [standard benchmark]"
- "The literature suggests..."
- "This is novel — you should validate by comparing to [existing thing]"
- "Other projects do X"
- "You should follow [accepted methodology]"
- "This would be more credible if you used [established framework]"
- "The standard approach is..."
- "Most researchers in this field..."
- "This needs peer review"
- "You're reinventing the wheel"

When you see one of these in your draft: STOP. The reflex is firing. Pick a substrate-grade framing instead.

**Does NOT prohibit:** engaging with prior literature *as data* (negative-space mapping, kill catalogs); validating against ground-truth catalogs (Mossinghoff, LMFDB, mathlib4); acknowledging fair external concerns (Watch-1..Watch-N watchlist is the model); using established tools as *infrastructure* (PyTorch, mpmath, PARI/GP, sympy).

**DOES prohibit:** suggesting Prometheus adopt a "more standard" approach because the standard one is well-established; comparing Prometheus's metrics to academic-benchmark metrics as if those are the gold standard; training the Learner on "standard math benchmarks" instead of substrate-grade kill-data; treating substrate-grade negative findings as failures rather than as the product.

---

## HARD-3 — Tensor first; Apollo / Rhea / Forge / multi-agent expansion deferred

**Rule:** Building the unified, signature-keyed tensor is Priority #1. Apollo (model training), Rhea (model forge), Forge (tool evolution), multi-agent pipeline expansion are deferred until the closed-loop condition is met.

**Why:** Reasoning machinery without structured ground-truth produces narrative, not findings. Owned models trained against an incomplete tensor inherit the incompleteness as a structural prior they can't escape. Train against the map once the map is real.

**The closed-loop condition (gate that re-opens deferred work):**
1. Unified, signature-keyed tensor with operator-derived structural partitions (NOT human discipline labels).
2. Five-test calibration arsenal operating routinely on tensor outputs.
3. Replay capsules for deterministic battery reproduction.
4. Battery calibration suite measuring per-region false-kill rates.
5. **Maieutēs operating both sides** — mining weak signals as exploration material AND firewalling them from the training loop.
6. Synthesizer / Daedalus promoting confirmed structure to canon.

**How to apply:** when any proposal arrives that asks for compute, attention, or build effort, ask: does this advance the unified-tensor build, or does it presuppose the tensor and try to build a navigator? If the latter, defer.

---

## HARD-4 — Calibration anchors are load-bearing infrastructure

**Rule:** Calibration corpora (problem-solution-paradigm triples, status-tagged conjectures, retracted-finding records) are first-class substrate infrastructure. Actively hunt for them, especially in high-dimensional or under-explored mathematical territory the substrate's existing operators don't yet reach.

**Why:** Without enough anchors, false-kill rate, false-promote rate, bond-rank thresholds, encoding invariance, and the substrate's own null model are all unmeasurable. Every promotion is more anecdote than measurement. Current state is thin (single-digit anchors per region in some areas).

**Hunt direction:** higher-dimensional motivic / cohomological territory; categorical / topos-theoretic; non-archimedean / p-adic at deep level; higher-genus algebraic geometry; cross-language and cross-formalism corpora; solution-paradigm tagging at scale.

**How to apply:**
- Every ingest decision must report whether the corpus expands calibration in territory the substrate is already strong in (low marginal value) or weak in (high marginal value).
- Every frontier-review cycle should include an explicit data-gap question framed by current calibration thinness.
- Every new finding should consider: does this become a calibration anchor?
- Avoid the trap of treating calibration as overhead. It IS the infrastructure that distinguishes the substrate from a clever solo workflow.

---

## HARD-5 — Domains are docstrings, not coordinates

**Rule:** Human discipline labels (number theory, topology, physics, combinatorics, etc.) are tags on tensor nodes for citation and human translation only — they MUST NOT structure the tensor itself. The unit of representation is (object, operator-output) pairs. Structural partitions emerge from TT bond ranks and tensor decomposition, not from human discipline categories.

**Why:** Human discipline boundaries are artifacts of how data was collected and which 19th- and 20th-century communities formed around which problems. Pre-partitioning the tensor by discipline bakes in the lie before computation begins.

**Special case — physics:** 99% of physics literature is dressed in probabilistic / measurement-collapse framing. Treat that framing as a workaround for our species' inability to compute at the universe's actual precision and speed, not as a feature of the underlying math. We use the equations and we cite the papers; we do NOT import the Copenhagen-style "universe doesn't decide until we measure" framing into the tensor. The probabilistic projection is the shadow on the wall; the mathematical structure is the fire. Aporia maps the fire, not the shadow.

**Refinement (2026-04-26) — bridges between domains are not the goal either:**
A "bridge" is just the human-narrative term for "two regions of the unified tensor end up close together under some operator." The discovery worth promoting is the operator's signature pattern across regions, not the bridge story we tell about it. Frame findings as "operator X produces signature S in regions A and B" rather than "we found a bridge between A and B."

**How to apply:**
- Track human labels (`number_field`, `knot`, `quantum_observable`) as docstring fields on tensor nodes — useful for citing papers, useful for human-readable reports, never used as coordinates or partitions.
- When a finding gets described as "cross-domain," rewrite it as a structural-signature description.
- Cite physics papers for their predictive math; do not import their interpretational framing as substrate truth.
- Use "structural region" language. NOT "bridge between X and Y" — instead "shared structural features across regions tagged X and Y."

---

## HARD-6 — Attack the problems of the tools we'll need most; failures guide

**Rule:** Problem selection is tool-need-driven. Attack the open problems of the tools the substrate will need most in the future. Failures are not setbacks — they are guidance. The failure mode IS the output: it reveals where the substrate is bumping into limits, what primitive is missing, what the next contract change must address.

**Why:** James 2026-05-08 directive verbatim: *"We're going to attack the problems of the tools we will need most in the future. The failures will guide us."* Pairs with the tensor-near-and-dear posture (tensor problems are the canonical near-term example because tensors will be long-term substrate infrastructure per HARD-3) and with the existing kill-as-product doctrine (per feedback_assume_wrong.md, paradigm P25 in attack_angle_taxonomy).

**How to apply:**
- When selecting deep-research batch candidates: bias toward problems whose resolution would help the substrate's tools, not toward problems "interesting in their own right." Tensor problems (`aporia/mathematics/tensor_open_problems_v1.md`) are the current high-priority pool.
- When Techne or Ergon attempts a problem and fails: the failure IS the output. Document the failure as substrate-grade kill (which falsifier triggered, what alternate hypothesis surfaced, what gap this reveals). Do NOT treat as a defeat or a reason to back off; treat as P25 Pivotal-Negative-Result paradigm in motion.
- When choosing among capability-gap tickets to elevate: prioritize ones tied to tools-we-need-most. Capability-gap tickets surfaced by tensor-classification work get priority over generic capability-gap tickets.
- Tester output that surfaces a P0-class flaw (e.g. `T-ST-fire17-001` TriangulationProtocol bypass) is the substrate doing exactly this — failing forward in a directed way.
- This rule operates upstream of HARD-3 (tensor first): tensor-first names the priority OBJECT; HARD-6 names the priority POSTURE toward whichever object is being attacked.

**Distinction from HARD-2 (anti-gravitational-well):** HARD-2 is about resisting conventional framings. HARD-6 is about choosing problems by tool need. They are aligned but distinct: HARD-2 governs HOW you attack; HARD-6 governs WHICH problems you attack.

---

## Notes for cross-machine portability

- This file is the canonical doctrine source for any agent invoked outside M1 (F:\Prometheus). Do not reference local Claude Code memory directories — they don't exist on M2 (D:\Prometheus) or in remote cloud sandboxes.
- All file paths in agent prompts must be repo-relative (e.g. `aporia/doctrine/critical_memories.md`), never absolute.
- When this file is updated, the corresponding local feedback memory should be updated too, so M1's local context stays consistent — but the tracked file is the source of truth for cross-machine work.
