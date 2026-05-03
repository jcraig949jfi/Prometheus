# Aporia Frontier Scout 02 — Live arXiv Polynomial Ingestion for Mahler-Measure Discovery

**Date:** 2026-04-28
**For:** Techne (Mahler-measure discovery environment)
**Question:** Can Techne's Salem-cluster rediscovery harness be extended to ingest *fresh* arXiv polynomials and stress-test consistency on data not memorized in Mossinghoff / Boyd / Smyth?

---

## 1. The Niche Is Smaller (and Hotter) Than It Looks

The "small Mahler measure" subfield in 2024–2026 has bifurcated. Pure-computational extensions of the Mossinghoff list are rare — the canonical catalog (CECM mirror at <http://wayback.cecm.sfu.ca/~mjm/Lehmer/>, last large refresh tracing to the Rhin–Mossinghoff–Wu 2008 update plus 2003 Rhin–Sac-Epée additions) still defines the ground truth through degree 44 (complete for Salem numbers M < 1.3) and through degree 180 for known polynomials with M < 1.3. **No recent paper announces a new "below the Mossinghoff list" record.** What *is* active is application-driven generation of small-M polynomials from adjacent structures: arithmetic hyperbolic geometry, totally-real number fields, Newman/Turyn ±1 polynomial extremization, and trinomial dynamics. These adjacent papers are the ingestion targets.

### Five papers worth ingesting first

1. **Mossinghoff, "Mahler's problem and Turyn polynomials"** — arXiv:2405.08281 (May 2024, rev. Oct 2025). Establishes a new normalized Mahler-measure record exceeding 0.95 for ±1 (Turyn) polynomials via cyclic shifts of Fekete polynomials. Tables of shift-parameter, degree, and asymptotic M / L_q values are exactly the structured data Techne should target. Author is the canonical authority — every coeff/M pair here is high-trust ground truth.
2. **Paudel, Petersen, Wang, "Minimal Mahler Measure in Quartic Galois Number Fields"** — arXiv:2510.00295 (Sep 2025). Unconditional and ABC-conditional density results for minimal integral Mahler measure as a function of discriminant in Galois quartic fields. Likely contains worked-example polynomial tables for biquadratic / cyclic-quartic cases — a *cross-domain* feed (number-field theoretic, not Lehmer-list combinatorial). High value because the polynomials are not Mossinghoff-list members by construction.
3. **Verger-Gaugry, "A Non-Trivial Minoration for the Set of Salem Numbers"** — arXiv:2401.05843 (Jan 2024). Trinomial route (-1 + x + x^n) into Salem-number lower bounds via dynamical zeta functions; explicit numerical anchors (e.g. θ₃₁⁻¹ = 1.08544…). Trinomial families are easy to parse and easy to verify. Sub-Lehmer territory.
4. **Stankov, "Approximation of the number of nonunimodular zeros of a self-reciprocal polynomial"** — arXiv:2509.01015 (Aug 2025). Constructs polynomial sequences R_d(x) = P(x, x^n) from bivariate parents drawn from Boyd–Mossinghoff small-M lists. References the lists explicitly — useful as a *bridge* document that names polynomials, lets Techne's parser cross-reference Mossinghoff entries, and offers derived sequences that may *not* be in the canonical catalog.
5. **Flammang, "To answer a question of Professor Georges Rhin"** — arXiv:2401.12951 (Jan 2024). Recursive polynomial-generation algorithm for the Schur–Siegel–Smyth trace problem on totally positive algebraic integers, with auxiliary polynomial tables across nine subintervals of (0, 90). The recursive algorithm itself is a generator Techne could replicate.

### Two adjacent corpora worth a second pass

- **Chu–Murillo–Romero–Thompson**, arXiv:2508.08003 (Aug 2025), and **Dória–Murillo**, arXiv:2510.17041 (Oct 2025), and **Chu–Murillo**, arXiv:2506.20552 (Jun 2025) — counting Salem numbers via arithmetic hyperbolic orbifolds. Coefficient tables are likely sparse (the focus is asymptotic counts), but conditions like f(1)f(-1) ≡ −D or square-rootability give Techne *generative constraints* that can be inverted into novel polynomial families.
- **Pritsker / areal Mahler measure** lineage (e.g. arXiv:2512.16007 "Areal Weil Heights"). Different measure, but the analog of Lehmer's conjecture is *false* for areal heights — useful as a negative control and a falsifier surface for Techne's consistency checker.

---

## 2. Catalog Landscape Beyond Mossinghoff

There is no LMFDB analog for Lehmer. The de facto authoritative resources, in order:

- **Mossinghoff CECM mirror** — <http://wayback.cecm.sfu.ca/~mjm/Lehmer/> with downloadable plain-text lists at `/lists/` (full polynomial set), `/lists/SalemList.html` (Salem numbers), `/limitpoints/Q.html` (hexanomial Q(a,b) measures). Updates have slowed; last significant additions trace to 2008 (Rhin–Mossinghoff–Wu) and 2003 (Rhin–Sac-Epée), with 2000 Lisonek additions earlier. The note at <https://www.mossinghoff.info/lehmer/> is the maintained pointer.
- **Boyd's tables** — degree ≤ 20, M < 1.3, foundational, fully subsumed by Mossinghoff's 1998 *Math. Comp.* extension to degree 24 (Math. Comp. 67, 1998, S0025-5718-98-01006-0).
- **Smyth's survey, "The Mahler measure of algebraic numbers: A survey"** (<https://webhomes.maths.ed.ac.uk/~chris/papers/Smyth240707.pdf>) — the bibliographic backbone; not a catalog itself but the index into all catalogs.
- **Zudilin, "MM(P): Mahler Measures of Polynomials"** — <https://www.math.ru.nl/~wzudilin/mm(p).html>. Different focus (multivariate Mahler measure / L-value identities), but worth scraping for cross-references.
- **OEIS** — coverage is *unstructured*. A073011 lists Salem numbers; A003010 etc. are Lucas–Lehmer artifacts unrelated to this problem. There is no consistent A-number pattern keyed to (degree, polynomial-id, M-value); cross-referencing is ad hoc, prose-only. **Implication: Techne should *create* the structured cross-reference.**
- **Mossinghoff–Rhin–Wu, "Minimal Mahler Measures"**, *Experimental Mathematics* 17 (2008), 451–458 (<https://projecteuclid.org/euclid.em/1243429958>) — minimal M for primitive irreducible noncyclotomic polynomials at every even degree D ≤ 54. The "no degree ≤ 56 beats the Lehmer polynomial" result is anchored here.

**Net assessment:** the field is *catalog-poor and parser-friendly*. A Techne-curated `(coeffs, M, source-arxiv-id, in-mossinghoff?)` table would be a publishable artifact in itself, not just an internal validation set.

---

## 3. arXiv API — Practical Crawl Recipe

Endpoint: `http://export.arxiv.org/api/query`. Returns Atom 1.0 XML.

**Hard constraints (per <https://info.arxiv.org/help/api/user-manual.html>):**

- Max 2,000 results per request; max 30,000 total via paginated `start` (returns HTTP 400 beyond).
- 3-second sleep between successive calls is the official politeness ask. Community evidence (Google Group `arxiv-api`, ys2ypF0uifA) tolerates bursts of ~4 req/s if followed by 1 s sleep. Enforcement tightened around Feb 2026.
- Search results refresh once daily at midnight ET — cache aggressively.
- Recommended query for our needs:
  - `search_query=cat:math.NT+AND+(abs:"Mahler measure"+OR+abs:"Salem number"+OR+abs:"Lehmer conjecture"+OR+abs:"Pisot number")&sortBy=submittedDate&sortOrder=descending&max_results=200`
- For >1,000-result harvests, use **OAI-PMH** (`http://export.arxiv.org/oai2`) instead — it is the supported bulk channel.

**Source TeX retrieval** is essential because the API only returns metadata. Two clean paths:

1. `https://arxiv.org/e-print/<id>` returns the gzipped TeX bundle; recommended wrapper `arxiv-latex-extract` (<https://github.com/potamides/arxiv-latex-extract>).
2. `https://ar5iv.labs.arxiv.org/html/<id>` gives a rendered HTML version with `<table>` elements already extracted from `tabular` environments — significantly easier to scrape than raw LaTeX.

The Python `arxiv` package (<https://pypi.org/project/arxiv/>) wraps metadata cleanly; pair with `requests` for the e-print bundle.

---

## 4. Parser Design

Three-tier strategy, ordered by cost:

**Tier A — ar5iv HTML scrape (fast, brittle on math).** For each arXiv ID, fetch `ar5iv.labs.arxiv.org/html/<id>`, locate `<table>` blocks, BeautifulSoup-extract rows. Works for ~70% of math papers because ar5iv has handled the LaTeX rendering. Failure mode: tables built with custom macros render as MathML the parser must then unwind.

**Tier B — TexSoup over the e-print source (robust).** `pip install texsoup`; iterate `\begin{tabular}` / `tabularx` / `tabulary` nodes, split rows on `\\`, columns on `&`, run each cell through `pylatexenc.latex2text.LatexNodes2Text` for plain-text normalization. For coefficient lists (typically `[a_0, a_1, ..., a_d]` or polynomial expressions like `x^{10} + x^9 - x^7...`), apply `latex2sympy2_extended` (<https://github.com/huggingface/latex2sympy2_extended>) to recover `sympy.Poly` objects directly. This is the best general-purpose path; the practical cookbook at <https://yingjun-mou.github.io/posts/2021/06/Tabular%20data%20extration/> describes the canonical workflow.

**Tier C — LLM table extraction (last-resort, heterogeneous tables).** Two viable stacks:
- **Marker** PDF-to-Markdown (with `--use_llm`) followed by structured-output JSON extraction. Marker preprocessing was the strongest positive factor in the 2025 LLM-extraction benchmarks (TPDL 2025, arXiv:2510.04749).
- **Nougat** (`facebookresearch/nougat`, arXiv:2308.13418) for academic-document OCR if the source TeX is unavailable.
- Schema-guided extraction with constrained decoding (see SLOT, EMNLP-Industry 2025, aclanthology.org/2025.emnlp-industry.32) to pin output to `{"coefficients": [int], "degree": int, "M": float, "polynomial_latex": str}`.

**Validation gate (this is the key Techne integration):** every parsed `(coeffs, M_claimed)` pair runs through a numerical Mahler-measure recomputation (mpmath product over roots > 1, or Graeffe iteration for stability) and is rejected if `|M_recomputed - M_claimed| > 10^{-4}`. This *is* the consistency checker — any disagreement is either (a) a parser bug, (b) a typo in the source paper (real, and worth flagging), or (c) a definitional difference (logarithmic vs multiplicative, normalized by L_2, etc.) that needs explicit handling.

---

## 5. Concrete Recommended Next Move for Techne

**Week-1 milestone:** stand up an end-to-end pipeline that ingests the five papers above, extracts every `(coeffs, M)` pair, runs the consistency checker, classifies each pair as `{in-Mossinghoff, novel, contradiction}`, and produces a JSONL artifact at `techne/data/arxiv_mahler_ingestion_v1.jsonl`. Acceptance test: ≥80% of pairs from arXiv:2405.08281 (Mossinghoff's own paper) parse cleanly and validate, and *all* parse failures emit a structured failure-reason record (no silent drops).

**Stack:**
- Crawl: `arxiv` Python package + 3-s sleep + local SQLite cache of (id, last_seen, abstract).
- Source acquisition: `arxiv-latex-extract` for TeX, `ar5iv` HTML as fallback.
- Parse: TexSoup + pylatexenc + latex2sympy2_extended (Tier B). Tier C only when Tier B yields zero rows.
- Validate: existing Techne Mahler-measure consistency checker.
- Cross-reference: a local copy of the Mossinghoff plain-text lists from `/lists/` for the `in-mossinghoff?` flag.

**Five arXiv IDs to start with:**
1. `arXiv:2405.08281` (Mossinghoff, Turyn) — known-good calibration.
2. `arXiv:2510.00295` (Paudel–Petersen–Wang, quartic Galois) — novel-polynomial yield.
3. `arXiv:2401.05843` (Verger-Gaugry, Salem trinomials) — sub-Lehmer band probe.
4. `arXiv:2509.01015` (Stankov, self-reciprocal R_d) — bridge to Mossinghoff list.
5. `arXiv:2401.12951` (Flammang, Schur–Siegel–Smyth recursion) — generator-replication candidate.

---

## 6. Mutator-Front Bonus

For each *novel* (non-Mossinghoff) polynomial P(x) the parser yields, queue these mutators into Techne's exploration loop:

- **Palindrome lift:** if P is non-reciprocal, form P*(x) = x^d P(1/x) and the symmetric product P(x) · P*(x); re-evaluate M. (Often produces Salem-flavored siblings in the M < 1.3 band.)
- **Sign flip on odd-degree coefficients:** P(-x). Preserves Mahler measure for many Salem candidates but can land outside any catalog.
- **Cyclotomic multiplication:** P(x) · Φ_n(x) for n ∈ {1, 2, 3, 4, 5, 6, 7, 8, 10, 12}. Multiplicative on M (Φ_n are M=1), but pushes degree where Mossinghoff coverage thins (>44 for completeness) — most likely region to harvest novelty.
- **Root-of-unity twist:** P(ζ_k x) for small k; preserves M but generates conjugates that break naive equality-keyed catalog lookup, useful for stress-testing dedup.
- **Degree-shift (Stankov pattern):** R_d(x) = P(x, x^n) for bivariate parents — mechanically converts a single small-M parent into an indexed family; per arXiv:2509.01015 the limit ratios differ from M and are themselves novel invariants.
- **Boyd composition:** P(x^k) for k ∈ {2, 3}. Multiplies degree by k, preserves M; pushes into degree 60–180 territory where Mossinghoff list completeness is weakest.
- **Reciprocal pair-add:** P(x) + ε · x^d P(1/x) for small ε ∈ {-1, 0, 1} — non-multiplicative perturbation that can land near (but not on) the small-M band; check whether the new M is below the Lehmer-polynomial bound.

Each mutator emits a candidate; the consistency checker scores it; anything M < 1.3 and not-in-Mossinghoff goes to the human-in-the-loop queue with the source-paper provenance preserved.

---

## Sources

- [Mossinghoff Lehmer catalog (CECM mirror)](http://wayback.cecm.sfu.ca/~mjm/Lehmer/)
- [Mossinghoff Lehmer page](https://www.mossinghoff.info/lehmer/)
- [Lists of Polynomials with Small Mahler Measure](http://wayback.cecm.sfu.ca/~mjm/Lehmer/lists/)
- [Small Salem Numbers list](http://wayback.cecm.sfu.ca/~mjm/Lehmer/lists/SalemList.html)
- [Mossinghoff–Rhin–Wu, "Minimal Mahler Measures" (Exp. Math. 2008)](https://projecteuclid.org/euclid.em/1243429958)
- [Mossinghoff 1998 Math. Comp. extension](https://www.ams.org/journals/mcom/1998-67-224/S0025-5718-98-01006-0/)
- [Smyth, "Mahler measure of algebraic numbers: a survey"](https://webhomes.maths.ed.ac.uk/~chris/papers/Smyth240707.pdf)
- [Zudilin, MM(P) page](https://www.math.ru.nl/~wzudilin/mm(p).html)
- [arXiv:2405.08281 — Mossinghoff, Turyn polynomials](https://arxiv.org/abs/2405.08281)
- [arXiv:2510.00295 — Paudel–Petersen–Wang, Quartic Galois](https://arxiv.org/abs/2510.00295)
- [arXiv:2401.05843 — Verger-Gaugry, Salem minoration](https://arxiv.org/abs/2401.05843)
- [arXiv:2509.01015 — Stankov, nonunimodular zeros](https://arxiv.org/abs/2509.01015)
- [arXiv:2401.12951 — Flammang, Schur–Siegel–Smyth](https://arxiv.org/abs/2401.12951)
- [arXiv:2508.08003 — Chu–Murillo–Romero–Thompson, Counting Salem (orbifolds)](https://arxiv.org/abs/2508.08003)
- [arXiv:2510.17041 — Dória–Murillo, Salem deg-4 / hyperbolic 6-orbifolds](https://arxiv.org/abs/2510.17041)
- [arXiv:2506.20552 — Chu–Murillo, Salem & commensurability](https://arxiv.org/abs/2506.20552)
- [arXiv:2512.16007 — Areal Weil Heights](https://arxiv.org/html/2512.16007)
- [arXiv API user manual](https://info.arxiv.org/help/api/user-manual.html)
- [arXiv bulk data access](https://info.arxiv.org/help/bulk_data.html)
- [arxiv (PyPI)](https://pypi.org/project/arxiv/)
- [arxiv-latex-extract (GitHub)](https://github.com/potamides/arxiv-latex-extract)
- [arxiv-collector (GitHub)](https://github.com/djsutherland/arxiv-collector)
- [pylatexenc (GitHub)](https://github.com/phfaist/pylatexenc)
- [latex2sympy2_extended (HuggingFace)](https://github.com/huggingface/latex2sympy2_extended)
- [TexSoup tabular extraction recipe](https://yingjun-mou.github.io/posts/2021/06/Tabular%20data%20extration/)
- [Nougat (Meta)](https://github.com/facebookresearch/nougat)
- [Marker / LLM-based extraction benchmarks (TPDL 2025)](https://arxiv.org/html/2510.04749v1)
- [SLOT structured output (EMNLP Industry 2025)](https://aclanthology.org/2025.emnlp-industry.32.pdf)
- [Tables to LaTeX structure/content extraction](https://arxiv.org/pdf/2210.17246)
- [OEIS A073011 (Salem numbers)](https://oeis.org/A073011)
- [Lehmer's conjecture (Wikipedia)](https://en.wikipedia.org/wiki/Lehmer's_conjecture)
- [Hironaka, "What is Lehmer's number?"](https://www.ams.org/notices/200903/rtx090300374p.pdf)
