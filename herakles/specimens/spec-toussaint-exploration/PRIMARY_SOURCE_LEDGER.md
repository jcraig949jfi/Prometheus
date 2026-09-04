# A. PRIMARY SOURCE LEDGER

**Status: T0 PASSED on 2026-09-03.** Sixteen publications and six code artifacts recovered, hashed and stored. Every row below was read by this seat in the artifact named, not recalled.

Directive: `roles/Herakles/prompts/DIRECTIVE_HC_T01_TOUSSAINT_MISSING_CELL_2026-09-03.txt`, sha256 `5cc0241fe85567e71201416cd16a88fd0672ff5cc4ae921996606e33c30b0354`.
Artifacts and full digests: `RECOVERED_ARTIFACT_MANIFEST.jsonl`, 22 rows.

## How the bibliography was established

The prior pass supplied candidate titles from a research report. Per GATE-5 those were demoted to leads and re-derived from scratch here, because this seat has previously caught itself supplying two paper titles that exist in no author's bibliographic record.

Two independent authoritative sources were queried directly: the **arXiv API** author listing, and the **DBLP** publication API, paged in full. The bibliography below is what those returned, not what was remembered. Full texts came from the **author's own archive** at `argmin.lis.tu-berlin.de/papers/`, which holds every pre-2008 evolutionary-computation item under a `YY-author-VENUE` naming convention, and from arXiv.

## The load-bearing sources

| source_id | exact title | year | venue, exact locator | role in HC-T01 |
|---|---|---|---|---|
| SRC-PHD-2003 | The evolution of genetic representations and modular adaptation | 2003 | PhD thesis, Fakultaet fuer Physik und Astronomie, Ruhr-Universitaet Bochum, dated March 31 2003. Sections 1.5.1 to 1.5.5, Tables 1.6 and 1.7, Figures 1.4 to 1.7 | **carries both the detector and the ablation** |
| SRC-ARXIV-2001 | Self-adaptive exploration in evolutionary search | 2001 | arXiv physics/0102009v1, submitted 2001-02-05. Section 5.2, Figures 3 and 4 | earlier form of the detector; 10,000 samples per time step |
| SRC-FOGA-2002 | On the Evolution of Phenotypic Exploration Distributions | 2002 | Foundations of Genetic Algorithms 7, pp. 169-182, Morgan Kaufmann | formal theory, **no experiments** |
| SRC-CEC-2002 | Neutrality: A Necessity for Self-Adaptation | 2002 | CEC 2002, pp. 1354-1359, Toussaint and Igel | the sphere ablation; fitness and step size only |
| SRC-NATCOMP-2003 | Neutrality and self-adaptation | 2003 | Natural Computing 2(2):117-132, Igel and Toussaint | journal extension of the above |
| SRC-GECCO-PLANTS-2003 | Demonstrating the Evolution of Complex Genetic Representations: An Evolution of Artificial Plants | 2003 | GECCO 2003, pp. 86-97 | same mechanism, larger world, **no detector** |
| SRC-GECCO-STRUCT-2003 | The Structure of Evolutionary Exploration: On Crossover, Building Blocks, and Estimation-Of-Distribution Algorithms | 2003 | GECCO 2003, pp. 1444-1456 | theory of crossover and entropy |
| SRC-BIOSYS-2007 | Complex adaptation and system structure | 2007 | BioSystems 90(3):769-782, Toussaint and von Seelen | latest retrospective |

Also recovered and searched, none carrying the composition: SRC-TR-2001, SRC-ARXIV-2002N, SRC-ARXIV-2002S, SRC-ARXIV-2004, SRC-FOGA-2005, SRC-GECCOWS-2005, SRC-TCS-2006, SRC-TR-2006.

## Three corrections to the prior ledger

**1. The FOGA paper's year and page numbers.** The prior row said "FOGA VII 2003". DBLP records it as **FOGA 2002, pages 169-182**; Toussaint's own reference list in the GECCO plants paper cites it as "Foundations of Genetic Algorithms 7 (FOGA VII). Morgan Kaufmann. In press", dated 2003. Both are defensible because the workshop and the proceedings fall in different years. Cite as FOGA 7, pp. 169-182, workshop 2002, proceedings 2003.

**2. A source the prior ledger did not contain at all.** `SRC-NATCOMP-2003`, the Natural Computing journal extension of the CEC paper, is exactly the class of item the directive tells us to hunt, a later expanded version that could carry an omitted measurement. It was missing from the candidate list. It has been recovered and checked. It contains **two figures**, one schematic and one analytical, and it **drops** the sphere experiment rather than extending it. No omitted measurement.

**3. The thesis date.** The dissertation itself is dated **March 31, 2003**. A widely repeated secondary claim gives 2004, which is the year of the Logos Verlag book edition under the slightly different title "The evolution of genetic representations and modular neural adaptation". Both exist. HC-T01 uses the 2003 dissertation.

## The definitional trap, confirmed by direct reading

The prior pass recorded that the papers whose titles most directly promise exploration-distribution measurement contain none. **Confirmed.** `SRC-FOGA-2002` has sections 2, 3, 4 and 6 and no experiments, no simulation and no measured figure; `SRC-ARXIV-2002S` is likewise derivation. Anyone ranking this literature by title would mis-rank it badly. The measurement lives in the 2001 paper and in section 1.5 of the thesis.

## The two sample counts, resolved

Both numbers are real and belong to different experiments. `SRC-ARXIV-2001` Figure 3 states 10,000 samples at each time step for a single tracked individual under (1+1) selection. `SRC-PHD-2003` Table 1.7 states 2,000 as the number of samples used to analyse the exploration distributions, and section 1.5.3 states these are taken "for each individual". There is no contradiction and the prior suspicion that 2,000 was a misread generation label is refuted.

## Code artifacts, recovered from the Internet Archive

Toussaint's GECCO plants paper says "More trials, data, and source code can be found at the author's home page." That page is long gone, but the Wayback Machine holds the 2003 Bochum site. Recovered:

- `ART-CODE-STRINGRULE` — the **full source of `02-stringRuleJTB/main.cpp`**, the driver for the string-rule experiments, carried inside a Doxygen example page.
- `ART-CODE-EVOLUTION` — the full source of `MT/evolution.h`, containing the `evolve()` generation loop and every selection scheme.
- `ART-CODE-PLANTEVO` — the full source of the artificial-plants driver.
- `ART-CODE-LIBMT`, `ART-CODE-STRINGRULECLASS`, `ART-CODE-MAKEFILE` — the library aggregator naming every header of the 2003 codebase, the StringRule class documentation, and the build file.

The implementation headers themselves, in particular the `spectrum()` estimator inside `genotype.h` and `operonString.h`, were **not** crawled and are not recoverable from this source. The estimator's sample count is therefore taken from the thesis, where it is stated exactly.
