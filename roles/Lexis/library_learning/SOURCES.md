# Complete bibliography — library learning and vocabulary growth

**Compiled:** 2026-08-24, passes 1–8. Every source this study touched, with what was actually read
from it. Sources are grouped by lineage, not by relevance.

**Reading discipline used:** an entry marked **[primary]** means I fetched the paper or repository
and extracted the stated facts directly. **[secondary]** means the facts come from a search-result
summary or an abstract page only, and have not been verified against the full text. Anything
load-bearing in `SIDE_BY_SIDE.md` or `RETROSPECTIVE.md` should be primary; where it is not, that is
flagged at the point of use.

---

## Family A — Library learning from program corpora (MIT / Solar-Lezama–Tenenbaum lineage)

**DreamCoder: Growing generalizable, interpretable knowledge with wake-sleep Bayesian program
learning.** Kevin Ellis, Catherine Wong, Maxwell Nye, Mathias Sable-Meyer, Luc Cary, Lucas Morales,
Luke Hewitt, Armando Solar-Lezama, Joshua B. Tenenbaum. arXiv:2006.08381 [cs.AI], submitted
2020-06-15. DOI 10.48550/arXiv.2006.08381. **[primary]** — abstract page fetched; architecture read
from `github.com/ellisk42/ec/blob/master/docs/software-architecture.md` **[primary]**.
Code: `github.com/ellisk42/ec`. Adaptations: `mlb2251/dreamcoder`, `lio-wong/laps_dreamcoder`.

**Leveraging Language to Learn Program Abstractions and Search Heuristics** (LAPS). Catherine Wong
et al. arXiv:2106.11053. **[secondary]** — identified via search; not fetched. Uses natural-language
annotations to guide joint learning of libraries and neurally-guided search.

**Top-Down Synthesis for Library Learning** (Stitch). Matthew (Maddy) Bowers, Theo X. Olausson,
Lionel Wong, Gabriel Grand, Joshua B. Tenenbaum, Kevin Ellis, Armando Solar-Lezama.
arXiv:2211.16605, v1 2022-11-29, v2 2023-01-15. *Proc. ACM Program. Lang.* 7, POPL, Article 41
(Jan 2023), pp. 1182–1213. DOI 10.1145/3571234. **[primary]** — abstract page fetched; repository
`github.com/mlb2251/stitch` fetched **[primary]**; bindings `mlb2251/stitch_bindings`.
*Not obtained:* the formal utility/cost definition — the arXiv PDF fetch returned binary and the
readthedocs *Cost Metrics* page 404'd at the guessed URL. Two attempts, recorded as a gap.

**LILO: Learning Interpretable Libraries by Compressing and Documenting Code.** Gabriel Grand,
Lionel Wong, Maddy Bowers, Theo X. Olausson, Muxin Liu, Joshua B. Tenenbaum, Jacob Andreas.
arXiv:2310.19791, submitted 2023-10-30, v4 2024-03-15. ICLR 2024. **[primary]** — abstract page and
`github.com/gabegrand/lilo` fetched. Domains: REGEX (re2), CLEVR, LOGO. Entry point
`run_iterative_experiment.py`; `ocaml/` carries the DreamCoder dependency.

---

## Family B — E-graphs and equality saturation (UW PLSE: Willsey, Nandi, Tatlock)

**babble: Learning Better Abstractions with E-Graphs and Anti-Unification.** David Cao, Rose Kunkel,
Chandrakana Nandi, Max Willsey, Zachary Tatlock, Nadia Polikarpova. arXiv:2212.04596, 2022-12-08.
POPL 2023. **[primary]** — abstract page fetched. Library learning modulo equational theory (LLMT).
*Not obtained:* whether babble handles effects/state; the abstract page does not say, and the full
text was not fetched. This is load-bearing for the pass-4/5 recommendation and is flagged there.

**Rewrite Rule Inference Using Equality Saturation** (Ruler). Chandrakana Nandi, Max Willsey, Amy
Zhu, Yisu Remy Wang, Brett Saiki, Adam Anderson, Adriana Schulz, Dan Grossman, Zachary Tatlock.
arXiv:2108.10436. OOPSLA 2021. **[secondary]**. Infers rewrite rules given a grammar and interpreter;
5.8× smaller rulesets, 25× faster than a comparable CVC4-based tool.
Code: `github.com/uwplse/ruler`.

**Equality Saturation Theory Exploration à la Carte** (Enumo). Chandrakana Nandi et al.
*Proc. ACM Program. Lang.* 7(OOPSLA2):1034–1062, Oct 2023. DOI 10.1145/3622834. **[secondary]**.
A DSL for programmable theory exploration; introduces "fast-forwarding" for domains where equality
is undecidable; an Enumo program synthesized a ruleset deriving 90% of Halide's handwritten rules.
Artifact: Zenodo 8140951.

**egg** — the equality-saturation library underpinning the above. **[secondary]**, contextual only.

**ShapeCoder: Discovering Abstractions for Visual Programs from Unstructured Primitives.**
R. Kenny Jones, Paul Guerrero, Niloy J. Mitra, Daniel Ritchie. arXiv:2305.05661. *ACM Trans. Graph.*
(SIGGRAPH 2023), DOI 10.1145/3592416. **[secondary]**. Jointly discovers abstraction functions and
programs from **unstructured primitives**; uses a shape-to-program recognition network plus e-graphs
with a conditional rewrite scheme.

---

## Family C — Theory exploration in interactive/automated theorem proving (Chalmers: Johansson, Smallbone, Claessen)

**QuickSpec.** Koen Claessen, Nicholas Smallbone, John Hughes (and later Johansson). **[secondary]**.
Discovers conjectures about a set of functions by interleaving term generation with random testing.

**Hipster: Integrating Theory Exploration in a Proof Assistant.** Moa Johansson, Dan Rosén et al.
CICM 2014, Springer LNCS, DOI 10.1007/978-3-319-08434-3_9. **[secondary]** —
`cse.chalmers.se/~jomoa/papers/Hipster-cicm-2014.pdf` located but not fetched. Two modes:
*exploratory* (generate basic lemmas about new datatypes/functions) and — the one that matters here —
**proof mode: discover the missing lemmas that would allow the current goal to be proved.**

**Conjectures, Tests and Proofs: An Overview of Theory Exploration.** arXiv:2109.03721.
**[secondary]**. Survey of the field.

**Lemmanaid: Neuro-Symbolic Lemma Conjecturing.** **[secondary]**. An LLM is trained to generate
lemma **templates** describing the *shape* of a lemma; symbolic methods fill in the details.
Evaluated on Isabelle proof libraries.

**Twee: An Equational Theorem Prover (System Description).** Nicholas Smallbone. CADE-28, 2021,
DOI 10.1007/978-3-030-79876-5_35. `nick8325.github.io/twee/`. **[secondary]**, contextual.

**Twitch: Learning Abstractions for Equational Theorem Proving.** Guy Axelrod, Moa Johansson,
Nicholas Smallbone (Chalmers / Univ. of Gothenburg). arXiv:2603.06849, 2026-03-06. Comments field:
"20 pages, submitted to IJCAR 2026". **[primary]** — abstract page and full HTML fetched.
*Unreconciled:* the abstract advertises "12 rating-1 problems"; the body figures extracted were
11 / 18 / 19 at rating ≥ 0.9. Deferred four times, then formally dropped in pass 4 — see
`RETROSPECTIVE.md` §Gaps.

---

## Family D — LLM tool and skill libraries

**Large Language Models as Tool Makers** (LATM). arXiv:2305.17126. ICLR 2024. **[secondary]**.
Two-phase: a *tool maker* LLM crafts reusable Python utility functions from a few demonstrations;
a separate *tool user* LLM applies them. Tools are cached and reused; up to 79% per-instance cost
reduction on reasoning benchmarks.

**Voyager: An Open-Ended Embodied Agent with Large Language Models.** Guanzhi Wang, Yuqi Xie et al.
arXiv:2305.16291, 2023. `github.com/MineDojo/Voyager`. **[secondary]**. Three components: automatic
curriculum, **ever-growing skill library of executable code**, and iterative prompting with
environment feedback, execution errors, and self-verification. 3.3× more unique items, 2.3× longer
distance, tech-tree milestones up to 15.3× faster than prior SOTA.

**ReGAL: Refactoring Programs to Discover Generalizable Abstractions.** Elias Stengel-Eskin,
Archiki Prasad, Mohit Bansal. arXiv:2401.16467. ICML 2024, PMLR v235.
`github.com/esteng/regal_program_learning`. **[secondary]**. Gradient-free library learning by code
refactoring; **iteratively verifies and refines abstractions via execution**. Five datasets: LOGO,
Date reasoning, TextCraft, MATH, TabMWP. Motivating claim: *"LLMs lack the global view needed to
develop useful abstractions; they generally predict programs one at a time, often repeating the same
functionality."*

**A Compute-Matched Re-Evaluation of TroVE on MATH.** Tobias Sesterhenn, Ian Berlot-Attwell,
Janis Zenkner, Christian Bartelt. arXiv:2507.22069v2, 2025-08-10. **[primary]** — fetched. Finds the
original TroVE library-induction advantage does not survive compute-matched comparison.

**Symbolic Regression with a Learned Concept Library** (LaSR). Arya Grayeli, Atharva Sehgal,
Omar Costilla-Reyes, Miles Cranmer, Swarat Chaudhuri. arXiv:2409.09359, submitted 2024-09-14, final
2024-12-10. NeurIPS 2024. **[primary]** — abstract page fetched. Induces a library of **abstract
textual concepts** via zero-shot LLM queries over high-performing hypotheses.
*Not obtained:* the concept selection criterion is not stated on the abstract page.

**DreamProver: Evolving Transferable Lemma Libraries via a Wake-Sleep Theorem-Proving Agent.**
Youyuan Zhang, Jialiang Sun, Hangrui Bi, Chuqin Geng, Wenjie Ma, Zhaoyu Li, Xujie Si.
arXiv:2604.26311v1, 2026-04-30. CC BY 4.0. **[primary]** — HTML fetched twice (general, then narrowly
on recursive decomposition). Lean + Mathlib.

**A Survey on Deep Learning for Theorem Proving.** Zhaoyu Li et al. COLM 2024.
`github.com/zhaoyu-li/DL4TP`. **[secondary]**, contextual — a route to further sources, unmined.

---

## Prometheus-side primary sources (all read directly)

- `apollo/README.md`, `apollo/ARCHITECTURE.md` (v2_d "Gradient Recovery")
- `apollo/cycles/o1_enumeration/PREREGISTRATION.md`, `FINDINGS.md`, `RESULT.json`,
  `RESULT_INVALID_tails_capped_at_3.json`, `RESULT_INVALID_orders_capped_at_4.json`
- `apollo/scripts/o1_enumerate.py` (imports inspected)
- `apollo/src/genome.py`, `apollo/src/gene_extractor.py`, `apollo/src/blackboard_ops*.py`,
  `apollo/src/blackboard_evolve.py`
- `forge/README.md`, `forge/ARCHITECTURE_T2_T3.md`, `forge/STATUS_T1_T2_20260403.md`
- `agents/hephaestus/README.md`, `agents/hephaestus/STATUS.md`
- `aporia/doctrine/reasoning_ladder.md` (§6, Band H, H2 preconditions)
- `roles/Diomedes/RECON_2026-08-24_navigational_information.md`
- `aporia/docs/program_audit_2026-06-10.md`,
  `roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md`

## Instruments written for this study (read-only, scratchpad, never committed to Apollo)

- `audit_rw.py` — AST audit of declared vs actual `reads`/`writes` across all `blackboard_ops*.py`
- `commute.py` — Bernstein-conditions independence derivation over O1's ceiling pipeline

## Negative results of the search itself

- **No prior internal catalog entry for this literature.** Repo-wide scan for
  DreamCoder / Stitch / LILO / "library learning" returned only false positives — an Arcanum
  XENOLEXICON question, *"Can a manifold be 'stitched' together from disparate, non-overlapping
  algebraic fields?"* (`arcanum/questions/detail/Q-698A1830.md`).
- **No hidden reachability machinery.** A scan for "reachable ceiling" / "reachability" surfaced only
  RPH docs, the xenolexicon paper, and two Hephaestus humanreadable files — nothing that measures
  `R(a)` for a candidate abstraction.
