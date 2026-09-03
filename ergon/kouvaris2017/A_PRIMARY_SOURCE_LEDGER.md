# A. PRIMARY SOURCE LEDGER — Kouvaris et al. 2017

**Seat:** Ergon lane, executed by this session on 2026-09-03 because Ergon is tied up.
**Directive:** `ergon/kouvaris2017/PROMPT_KOUVARIS2017_2026-09-03.txt`, body sha256
`c823c32cca29518747274da6d137e1fd33205cfc12908ddc17f2282846e16d63`.
**Posture, per directive:** the paper is treated as a POTENTIAL PRIOR SOLUTION, not as supporting
evidence. The task is to kill HC-T01's novelty if the evidence allows.

**Specimen.** Kouvaris K, Clune J, Kounios L, Brede M, Watson RA (2017). *How evolution learns to
generalise: Using the principles of learning theory to understand the evolution of developmental
organisation.* PLOS Computational Biology 13(4):e1005358. doi:10.1371/journal.pcbi.1005358.

---

## 1. What was recovered, and what it settles

Every claim in deliverables C through N is derived from files in `original/`, hashed in
`B_RECOVERED_ARTIFACT_MANIFEST.jsonl`. **No model-recall claim is load-bearing anywhere in this
pass.** Where I could not verify something I have written UNSPECIFIED or ACCESS_BLOCKED rather than
inferring it.

Three recoveries carry the pass:

1. **The full JATS XML of the published article.** Machine-readable, so the Methods, the figure
   captions, Table 1 and all 71 references are exact rather than transcribed. Superscripts survive,
   which matters: two parameters are powers of ten and one is a mangled `2^12` in a caption.
2. **The Supporting Information (S1 Appendix, 10 pages).** Carries the developmental equations, the
   exact training set, the modular class construction, and two sentences that decide §4 of the
   directive: the detector is *post hoc* and *not part of the evolutionary dynamics*, and **"No data
   sets are associated with this publication."**
3. **The author's MATLAB source, recovered as three tarballs** — `KostasKouvaris_Evolvability`
   (README: *"Implementation for Thesis Chapter 1"*, which is the chapter that became this paper),
   `KostasKouvaris_Plasticity`, and `KKouvaris_Phenotypic-Plasticity-Logical-Inference`. This is the
   single most valuable recovery. It is an **independent failure mode against the paper's own prose**
   and it fired: the code contradicts the published Methods on three parameters (§3 of
   `C_HISTORICAL_PHYSICS_SPEC.md`), and it contains a detector the paper never reports (§6 below).

## 2. Provenance classes

| Class | Meaning | Items |
|---|---|---|
| `PRIMARY_PUBLISHED` | the published record, retrieved from the publisher | article XML, article PDF, S1 Appendix |
| `PRIMARY_PREPRINT` | author-deposited, pre-review | arXiv 1508.06854 |
| `PRIMARY_THESIS` | author's own extended record | Kouvaris PhD (Southampton), Kounios MPhil |
| `PRIMARY_CODE` | author's implementation | three tarballs |
| `ANCESTOR` | a work explicitly supplying a measure or method | Parter et al. 2008 |
| `DESCENDANT` | later work in the same lineage | Kounios et al. arXiv 1612.05955; Kovács et al. 2020 |
| `ACCESS_BLOCKED` | identified, could not retrieve | Watson et al. 2014 (Evolution, Wiley) |

## 3. The published record

- **Article XML** — 146,205 bytes. Retrieved from PLOS as `type=manuscript`. Used for every quoted
  Method, every parameter, Table 1, and the reference list.
- **Article PDF** — 1,732,477 bytes, 20 pages. Used only to confirm figure content; the XML is the
  citable source for text.
- **S1 Appendix PDF** — 3,872,034 bytes, 10 pages. The only supporting file the article declares.
  There is exactly one `<supplementary-material>` element in the XML, so **the S1 Appendix is the
  complete supporting information**; nothing else was withheld from the reader.

## 4. Preprint

- **arXiv 1508.06854** — *"How Evolution Learns to Generalise: Principles of under-fitting,
  over-fitting and induction in the evolution of developmental organisation."* 28 pages.
- **Checked for experiments cut from the published version. There are none.** The preprint carries
  the identical five main figures (pictorial phenotypes; conditions; generalisation over
  evolutionary time; λ/κ sensitivity; adaptation rate) and five supporting figures.
- Two differences worth recording, neither scientific: the preprint spells the third author
  *Louis* Kounios where the published paper has *Loizos*; and the published S1 adds **Fig D, the
  Shannon entropy of the phenotypic distribution over evolutionary time (16 bits → 4 bits)**, which
  the preprint does not contain. The entropy trajectory is therefore a *publication-stage addition*
  and is a longitudinal summary statistic (see `D_HISTORICAL_DETECTOR_SPEC.md` §7).

## 5. Theses

- **Kouvaris PhD thesis, University of Southampton, ePrints 423467** — 159 pages, 12.2 MB.
  **Chapter 2 is this paper.** Its figure list (2.1–2.5) is one-to-one with the paper's Figs 1–5.
  **The thesis adds no experiment to the 2017 result.** That is a load-bearing negative: the usual
  reason to hunt a thesis is that it carries the ablations that did not fit the paper, and here it
  does not.
  The thesis *does* add two later chapters on a different system (Ch. 3 plasticity and reaction
  norms; Ch. 4 plasticity-first and learning theory). Chapter 3 is the only place in the entire
  recovered corpus where a **mutation-rate parameter is manipulated** (σ_μ ∈ {0.2, 0.01, 1e-4,
  1e-5}) — see `G_CAUSAL_INTERVENTION_MAP.md` §5, where I explain why this still does not make the
  composition HC-T01 targets.
- **Kounios MPhil thesis, Southampton ePrints 453036** — 101 pages. Sibling lineage, recovered and
  hashed for completeness.

## 6. Source code — the decisive recovery

The article's own S1 states *"No data sets are associated with this publication"*, and the article
declares no code availability. Nevertheless three author repositories were recovered as tarballs.

- **`KostasKouvaris_Evolvability`** (38,202 bytes) — README: *"Implementation for Thesis Chapter 1.
  … GRN.m is the main script that need to be run to evolve a population of developmental systems."*
  Thesis Chapter 1 in the code's numbering is the generalisation work; in the submitted thesis it is
  Chapter 2. This is the implementation behind the 2017 paper.
  Files that carry the argument: `GRN.m` (the evolutionary loop), `findErrors.m` (**the detector**),
  `histP.m` (the phenotype binning), `develop_v2.m`, `fitness_v2.m`, `mutate_weights_v2.m`,
  `mutate_gene.m`, `Hebbian.m`, `blockClass.m`, `plotOverfitting.m`.
- **`KKouvaris_Phenotypic-Plasticity-Logical-Inference`** (3,306,187 bytes) — a different project,
  but it contains `computeM.m` and `evalMutCorr.m`, which implement a **one-mutation-step
  mutational-effect detector** (300 single mutations per individual, population-wide, with the
  mutation draws frozen and shared across replicates). **This detector appears nowhere in the
  thesis** — the strings "mutational correlation", "mutational variance" and "M-matrix" occur zero
  times in 159 pages — **and nowhere in any recovered publication.** It is unreported instrumentation
  by the same author, and it is the closest thing in this lineage to the detector HC-T01 proposes.
  This finding narrows HC-T01's novelty claim and is developed in
  `F_ABCD_COMPOSITION_MATRIX.md` §5 and `K_DESCENDANT_SEARCH.md`.
- **`KostasKouvaris_Plasticity`** (671,661 bytes) — Chapter 3 implementation.

**Caveat carried everywhere.** These are working research scripts with many commented-out
alternative configurations. That `GRN.m` as committed differs from the published Methods does not
prove the published figures were produced by the committed configuration. Every code-versus-paper
disagreement below is tagged `VERIFIED_CONTRADICTORY` — meaning two primary sources disagree — and
never as "the paper is wrong".

## 7. Ancestors

- **Parter M, Kashtan N, Alon U (2008)**, *Facilitated variation: how evolution learns from past
  environments to generalize to new environments*, PLOS Comput Biol 4(11):e1000206. Recovered as PDF
  and XML. Reference [34] of the specimen, and the explicit source of the adaptation-rate assay
  ("as per [34]").
- **Watson RA, Wagner GP, Pavlicev M, Weinreich DM, Mills R (2014)**, *The Evolution of Phenotypic
  Correlations and "Developmental Memory"*, Evolution 68(4):1124–1138. Reference [25], and the
  direct source of the GRN model and the Hebbian account of B. **ACCESS_BLOCKED.** Wiley returned
  HTTP 403 to the direct PDF route; a Southampton ePrints path returned 404; the OUP mirror returned
  403. **This gap is not load-bearing**, because the S1 Appendix reproduces the developmental
  equations, constants and initialisation in full, and because the model is re-implemented in the
  recovered code. What the gap costs is an independent reading of whether Watson 2014 itself
  contains the composition; that is answered from its abstract and from the specimen's description
  of it, and is tagged accordingly in `J_DETECTOR_GENEALOGY.md`.

## 8. Descendants

- **Kounios L, Clune J, Kouvaris K, Wagner GP, Pavlicev M, Weinreich DM, Watson RA**, *Resolving the
  paradox of evolvability with learning theory: How evolution learns to improve evolvability on
  rugged fitness landscapes*, arXiv 1612.05955. Recovered.
- **Kovács et al. (2020)**, *Phenotypes to remember: Evolutionary developmental memory capacity and
  robustness*, PLOS Comput Biol 16(11):e1008425. Recovered. Same lineage, later.
- Systematic forward-citation screening is in `K_DESCENDANT_SEARCH.md`.

## 9. Declared conflicts and posture

- This pass was commissioned to attack a target that the programme's own Herakles seat wants to run.
  The seat writing this pass does not own HC-T01 and has no stake in it surviving. The verdict in
  `E_D_LEVEL_ADJUDICATION.md` refuses `HC_T01_HISTORICALLY_REDUNDANT`, so the reader should weigh
  that this is the outcome convenient for the programme, and check §7 of
  `F_ABCD_COMPOSITION_MATRIX.md`, which lists the four separate ways this pass **damages** HC-T01.
- Directive §22 was obeyed: no Prometheus-native metric was invented anywhere in this pass. No
  failure topology, no R0, no custom evolvability entropy. The only entropy discussed is the authors'
  own Shannon entropy from S1 Fig D.
- Directive §21 was obeyed: the learning-theory language is treated as the authors' analogy and is
  never used as evidence. The phenomenon is stated computationally in
  `M_CANDIDATE_COMPUTATIONAL_PARTS.jsonl` with no cognition words.
