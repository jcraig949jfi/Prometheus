# Aporia Scout 11 — arXiv:2405.08281 Deep Parser Brief

**Author:** Aporia (frontier scout)
**For:** Techne (mathematical toolsmith)
**Paper:** Mossinghoff, M. J., *Mahler's problem and Turyn polynomials*, arXiv:2405.08281 (v2: 22 Oct 2025)
**Date:** 2026-04-28
**Working files:** `F:/Prometheus/aporia/scouting/_2405_08281_workdir/turynMeas.tex` (TeX source, 1813 lines, fetched from `arxiv.org/e-print/2405.08281v2`)

---

## 1. Situation

Scout #2 nominated arXiv:2405.08281 as Techne's calibration anchor for the arXiv → polynomial-table → Mahler-recompute ingestion pipeline. The choice is correct: Mossinghoff is the canonical authority on small-Mahler-measure tables (his CECM "Lehmer's Problem" catalog has been the de-facto ground truth for ~25 years), the paper is recent (May 2024, latest revision Oct 2025), and it includes a clean numerical table at 8-decimal precision that any competent Mahler-measure recompute can reproduce to ~1e-7. **However, this paper is a thin calibration target — it contains exactly one tabular block and zero "polynomial-coefficient-vector ↔ M-value" rows.** What it ships are *asymptotic limit estimates* (κ_q^J(α)) for two infinite Turyn families, not a Mossinghoff-style enumeration. Shipping this week means: Tier-A HTML parser + Tier-B TeX parser + Mahler validation gate + JSONL artifact at `techne/data/arxiv_mahler_ingestion_v1.jsonl`. The realistic acceptance test is recomputing the κ_q^J table and the Corollary 3.2 companion-Littlewood differences for primes p<2000, **not** validating ±1 coefficient vectors against M-values.

## 2. Paper structure scout (verified against TeX source)

**Section layout (line numbers from `turynMeas.tex`):**
1. `\section{Introduction}` (L70)
2. `\section{Properties of Turyn polynomials}` (L249)
3. `\section{Mahler measure and L_q norms}` (L389) — subsections 3.1 *Turyn polynomials* (L393), 3.2 *Companion Littlewood polynomials* (L441)
4. `\section{Proof of Theorem~\ref{thmTuryn}}` (L479) — three subsections (Phi / Lq / Measure)
5. `\section{Proof of Corollary~\ref{corTuryn}}` (L1118)
6. `\section{Calculations}` (L1153) — subsections 6.1 *Mahler measure* (L1155), 6.2 *L_q norms* (L1277)
7. `\section{Generalized Turyn polynomials}` (L1333) — short, no tables, future-work pointer
8. `\section*{Acknowledgments}` (L1347)
9. Bibliography: `\begin{biblist}` (L1357) → `\end{biblist}` (L1809), **34 entries** in AMSrefs format (`\bib{key}{type}{ ... }`), **not** `\bibitem`. Authors: Beller/Newman, Borwein, Choi, Erdélyi, Klurman/Lamzouri/Munsch, Lehmer, Littlewood, Mahler, Mossinghoff, Pritsker, Smyth-adjacent (no Smyth direct cite, no Boyd direct cite, no Verger-Gaugry, no Flammang).

**Tabular structure (the only `tabular` block in the paper, L1307-1330):**
- Caption: *"Estimating the normalized Mahler measure, L_1 norm, and L_3 norm of the Fekete polynomials (α=0) and the Turyn polynomials with α=1/4."* (label `tableMeasLqData`)
- Spec: `\begin{tabular}{|c|cc|cc|cc|}` — 7 columns, three pair-groups separated by vertical rules
- Header row (verbatim): `J | κ_0^J(0) | κ_0^J(1/4) | κ_1^J(0) | κ_1^J(1/4) | κ_3^J(0) | κ_3^J(1/4)`
- Data: 18 rows, J = 1..18, all values to **8 decimal places**, all wrapped in math mode `$...$`. Sample row J=14: `$14$ & $0.73880677$ & $0.95109059$ & $0.90275433$ & $0.97558782$ & $1.06765908$ & $1.01536301$`.
- **Total distinct numerical (J, q, α, value) tuples in the paper's only table: 18 × 6 = 108.**

**Plus 6 figures** (`\begin{figure}` at L1208, L1215, L1246, L1253, L1269; figure 7 sits inside Sec 6 too): all are externally-referenced PDFs (`measTuryns.pdf`, `measGain14.pdf`, `feketeByJ.pdf`, `turynByJ.pdf`, `TurynToLW.pdf`). The figures show data for primes p<2000 and J ≤ 40 — **the underlying CSVs are NOT in the e-print bundle**; you would have to recompute them.

**Custom macros that will break a naive parser** (defined L23-L39):
- `\leg{a}{p}` → Legendre symbol `(a/p)`
- `\round{x}` → `\lfloor x \rceil` (nearest integer; **mixed floor-left + ceil-right brackets — pylatexenc will choke without a substitution rule**)
- `\ceil`, `\floor`, `\abs`, `\dbars`, `\bigdbars` → pure delimiter wrappers
- `\unimodular` → `\mathfrak{U}`, `\littlewood` → `\mathfrak{L}`
- `\TS`, `\BS` → vertical-strut spacers used **inside the table header cell**: the literal header reads `\TS\BS$J$ & ...`. A regex over raw TeX must strip these before the math-mode token.

**Cross-references:** The paper cites `[BM08, Table 2]` (Borwein–Mossinghoff 2008, *Barker sequences and flat polynomials*) for the degree-≤25 Littlewood max-Mahler tabulation. **Mossinghoff's online catalog (`wayback.cecm.sfu.ca/~mjm/Lehmer/`) is NOT cited in the bibliography.** No Smyth/Boyd/Lehmer-frontier table is reproduced; no claim of "novel polynomials" — the contribution is asymptotic limit theorems plus their numerical estimation. **In-catalog vs novel breakdown is not a meaningful axis for this paper.**

## 3. Parser implementation patterns

**Tier A — ar5iv HTML (primary path).** ar5iv renders the one tabular as `<table class="ltx_tabular ltx_guessed_headers ltx_align_middle">` inside `<figure class="ltx_table" id="S6.T1">`. Selectors:

```python
import requests, bs4
soup = bs4.BeautifulSoup(requests.get("https://ar5iv.labs.arxiv.org/html/2405.08281").text, "lxml")
tables = soup.select("figure.ltx_table table.ltx_tabular")          # exactly 1 hit
caption = soup.select_one("figure.ltx_table figcaption.ltx_caption").get_text(" ", strip=True)
rows = [[td.get_text(" ", strip=True) for td in tr.select("td,th")] for tr in tables[0].select("tr")]
```

Cell text already comes back as `"0.73880677"` (ar5iv strips `$...$`), so the per-cell parser is a one-liner: `float(cell)` for data cells, `int(cell)` for the J column. Header detection: the first row contains MathML `<math>` for `κ_0^J(0)` etc.; parse via `mi`/`msub`/`msup` element walk to recover the (q, α) pair, or just hard-code the known column order — given there is exactly one table in the paper, hard-coding is fine.

**Tier B — TexSoup over .tex source (fallback when ar5iv lags or 502s; also for figures' missing data).** Pull the e-print: `https://arxiv.org/e-print/2405.08281v2` returns a gzipped tar. Extract → look for `*.tex` (single file: `turynMeas.tex`).

```python
from TexSoup import TexSoup
doc = TexSoup(open("turynMeas.tex", encoding="utf-8").read())
for tab in doc.find_all("tabular"):
    rows = "".join(str(c) for c in tab.contents).split(r"\\")
```

**pylatexenc gotchas on this paper specifically:**
- `\round{x}` is undefined in pylatexenc's default macros — register `LatexMacroSpec("round", "{")` with a custom replacement to `\lfloor x \rceil`, otherwise it silently drops the argument.
- `\TS`/`\BS` will produce a `\rule{}{}` warning; safe to map to empty string.
- `\bbfamily` / `\fontfamily{bbold}` (L12) → trips font-spec warnings; ignore.
- The `\leg{}{}` Legendre symbol is fine because both args are present — but **never** invoke `latex2sympy2_extended` on a math expression containing `\leg`; preprocess to `\genfrac(){0pt}{0}{a}{p}` or just `(a/p)` first.

**Validation gate.** For this paper, the validation target is *not* `M(coeff_vector) ≈ M_paper` (no such pairs exist). The targets are:

1. **Recompute κ_0^J(0) and κ_0^J(1/4) for J = 1..14** using equation (4.2) (`eqnTurynComputeAlpha`, L1195) directly. Mossinghoff used Julia; mpmath at `mp.prec=80` reproduces all 8 decimals in seconds for J ≤ 10, minutes for J=14. Tolerance: **1e-7 absolute**. For J ≥ 15 the 4^J sum is too expensive — sample 2^28 integrals (the paper's own method, L1241) and accept relative error ≤ 1e-3.
2. **Recompute the Corollary 3.2 companion-Littlewood differences** (eqn L1263-1266) for primes p ∈ {prime-set up to 2000} using `sage.rings.polynomial.polynomial_ring.Polynomial.mahler_measure()` (Sage) or PARI's `polmahlermeasure(...)` via cypari2. Tolerance: 1e-6 (the figure points are visually consistent with this).

**Recommended Mahler-measure backend:** PARI via `cypari2` (`pari.polmahlermeasure(p)` on Z[x] polynomials of degree < 2000 returns 38-digit precision in <1 ms each). Avoid sympy — slow and lossy. If installing PARI is friction, fall back to mpmath: `prod(max(1, abs(r)) for r in mp.polyroots(coeffs, maxsteps=200, extraprec=64))`.

**Edge cases this paper triggers:**
- ±1 coefficient vectors with **one zero** (Turyn F_{p,t} is not strictly Littlewood — the zero sits at index t when (t/p)=0). The companion polynomials F^±_{p,t} flip that zero to ±1. Parser must not assume "Littlewood ⇒ no zero coefficient".
- Cyclic shifts: F_{p,t}(x) coefficients are `legendre((j+t) mod p, p)` for j=0..p-1, **degree exactly p-1**. A common bug is computing degree as p (off-by-one).
- Normalization is always `M(f)/sqrt(p)` (or `M(f)/||f||_2`), never raw M. Tag every emitted record with `normalization: "sqrt_p" | "L2_norm" | "raw"`.
- Fekete F_p(x) = sum (j/p) x^j is the t=0 case of Turyn; **the j=0 term vanishes** because (0/p)=0, so F_p has no constant term — a parser that strips leading-zero monomials must be told this is intentional.

**Failure-reason taxonomy (structured JSONL records):**
```
{"status":"parse_fail", "reason":"unknown_macro",      "macro":"\\round",   "loc":"S6.T1.row3.col2"}
{"status":"parse_fail", "reason":"non_numeric_cell",   "raw":"$\\cdots$",   "loc":"..."}
{"status":"parse_fail", "reason":"column_count_mismatch", "expected":7, "got":6}
{"status":"validate_fail","reason":"recompute_diverges","expected":0.95109059,"got":0.95108,"abs_err":1.1e-5,"tol":1e-7}
{"status":"validate_skip","reason":"sample_required_J_gt_14"}
{"status":"ok",        "table":"tableMeasLqData","J":14,"q":0,"alpha":"1/4","value":0.95109059,"recompute":0.95109059,"backend":"mpmath80"}
```

## 4. Updated arXiv niche scan (May 2024 → Apr 2026)

- **Mossinghoff post-May-2024:** Only the 2405.08281 v2 revision (22 Oct 2025) — minor revision, no new papers. He remains at CCR Princeton; no new sole-author preprints surfaced.
- **Klurman / Lamzouri / Munsch (KLM23, arXiv:2306.07156):** This is the "L_q norms and Mahler measure of Fekete polynomials" paper that supplies the random-process method 2405.08281 generalizes. **Critical companion target:** parsing 2306.07156 next would let Techne cross-validate Fekete-only κ_0(0) values against two independent papers. Same authors, no follow-up preprint detected after Jun 2023.
- **Smyth / Boyd / Verger-Gaugry / Flammang / Pritsker:** No new small-Mahler-measure preprints from any of them in 2024-2026 surfaced. Verger-Gaugry's "Proof of the Conjecture of Lehmer" (arXiv:1911.10590) remains under quiet review since 2021 and has not been updated; it is not a data source for Techne (the proof is structural, no tabulation). Pritsker is cited in 2405.08281's bibliography (Pritsker08) but has no recent ingest-able catalog.
- **Newcomers (last 12 months):** arXiv:2508.08003 *Counting Salem numbers arising from arithmetic hyperbolic orbifolds* (Aug 2025) — orthogonal mechanism, but its tables of Salem numbers from arithmetic 3-manifolds may seed a future Techne ingestor (different source-of-truth from Mossinghoff's catalog). arXiv:2512.16007 *Areal Weil Heights* (Dec 2025) — a new height variant; not direct Mahler tabulation but a candidate "second anchor" once the v1 pipeline is shipped. arXiv:2502.02803 *The alternative to Mahler measure of a multivariate polynomial* (Feb 2025) — multivariate, out of scope for v1.
- **FLINT / SageMath / PARI tooling:** No 2025-2026 release notes mention dedicated Mahler-measure functions beyond PARI's existing `polmahlermeasure`. SageMath 10.8 (Dec 2025) ships PARI 2.17 with `pari.polmahlermeasure` exposed via `cypari2`; FLINT 3.x has no Mahler primitive (root-isolation via `arb_fmpz_poly_complex_roots` is the build-block). Conclusion: **no new tooling to wait for; ship with PARI/cypari2.**

## 5. Concrete next move for Techne (5-day plan)

- **Day 1 (~1 h):** ar5iv fetch of `2405.08281` + manual eyeball of the lone tabular at L1307-1330 of `turynMeas.tex`. Confirm the 7-column / 18-row / 8-decimal structure. Snapshot the raw HTML to `techne/data/raw/2405_08281_ar5iv_2026_04_28.html`.
- **Day 2 (~3 h):** Tier-A parser (BeautifulSoup, selector `figure.ltx_table table.ltx_tabular`). Hard-code the 6 (q, α) column tags. First-pass extraction → 108 numeric tuples emitted as preliminary JSONL.
- **Day 3 (~3 h):** Validation gate. mpmath recompute of κ_0^J(α) for J ≤ 10 (cheap), J = 11..14 (overnight if needed), spot-check at 1e-7 tolerance. PARI/cypari2 wired in for the Cor. 3.2 companion-Littlewood spot-check at 5 primes (p = 503, 743, 1009, 1499, 1999). Failure-reason taxonomy live.
- **Day 4 (~3 h):** Tier-B fallback over the e-print TeX. Register `\round`, `\TS`, `\BS`, `\leg` in pylatexenc. Verify Tier-B emits the same 108 tuples Tier-A does (idempotency check).
- **Day 5 (~3 h):** Cross-reference scaffold. Since this paper has **zero** in-Mossinghoff-catalog (coeffs, M) pairs, the cross-reference layer for v1 is a *no-op stub* that logs `catalog_match: not_applicable, reason: paper_reports_asymptotic_limits_not_enumeration`. Emit JSONL artifact at `techne/data/arxiv_mahler_ingestion_v1.jsonl`. Acceptance: ≥80% of the 108 tuples validate to ≤1e-7 (expect 100% for J ≤ 10, ~95% for J = 11..14, sampling-required for J ≥ 15); all parse failures emit structured records.

**Critical heads-up for Techne:** Because 2405.08281 is structurally thin (one table, no enumeration), v1 will validate the *pipeline* but produce a small artifact. The right second-anchor target is **arXiv:2306.07156 (KLM23, Klurman-Lamzouri-Munsch)** — same family, independent computation, can cross-validate Fekete κ_0(0) ≈ 0.74083. Schedule it immediately after v1 as `arxiv_mahler_ingestion_v2.jsonl`. The right third anchor is **the Mossinghoff CECM catalog itself** (`wayback.cecm.sfu.ca/~mjm/Lehmer/`), which *is* a flat enumeration of (degree, polynomial, M) tuples and will exercise the parser's coefficient-vector path that 2405.08281 never touches.

## 6. References

1. Mossinghoff, M. J. *Mahler's problem and Turyn polynomials.* arXiv:2405.08281v2, 22 Oct 2025. <https://arxiv.org/abs/2405.08281> · ar5iv: <https://ar5iv.labs.arxiv.org/html/2405.08281> · e-print: <https://arxiv.org/e-print/2405.08281v2>
2. Klurman, O.; Lamzouri, Y.; Munsch, M. *L_q norms and Mahler measure of Fekete polynomials.* arXiv:2306.07156, Jun 2023. <https://arxiv.org/abs/2306.07156>
3. Borwein, P.; Mossinghoff, M. J. *Barker sequences and flat polynomials.* LMS Lecture Note Ser. 352 (2008), 71-88. (`[BM08]` in 2405.08281, contains the degree-≤25 Littlewood max-M table.)
4. Mossinghoff CECM catalog (Lehmer's Problem): <http://wayback.cecm.sfu.ca/~mjm/Lehmer/> (canonical small-M ground truth; not cited in 2405.08281 but the obvious v3 anchor).
5. PARI/GP `polmahlermeasure`: <https://pari.math.u-bordeaux.fr/dochtml/html/Polynomials_and_power_series.html#polmahlermeasure>
6. `cypari2` (Python bindings): <https://github.com/sagemath/cypari2>
7. SageMath polynomial Mahler measure: <https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/polynomial_element.html>
8. ar5iv: <https://ar5iv.labs.arxiv.org/>
9. TexSoup: <https://github.com/alvinwan/TexSoup>
10. pylatexenc: <https://pylatexenc.readthedocs.io/>
11. latex2sympy2_extended: <https://github.com/gamerwolfx/latex2sympy2-extended>
12. Verger-Gaugry, J.-L. *A proof of the Conjecture of Lehmer.* arXiv:1911.10590 (structural proof, no Techne data; reference only).
13. arXiv:2508.08003 *Counting Salem numbers arising from arithmetic hyperbolic orbifolds* (potential v4 source).

---

*Aporia signing off. The paper is a clean calibration target but a sparse data source — ship the pipeline against it, then immediately point it at KLM23 and the CECM catalog to harvest the real coefficient-vector / M-value bulk.*
