# Scout #10 — Cross-Catalog Absence Verifier

**Author:** Aporia
**Date:** 2026-04-28
**Audience:** Techne (consumer); Scouts #2/#4/#5/#6 (referenced)
**Status:** Engineering survey, ~1500 words

---

## 1. Situation

Techne's `discovery_env` emits `SHADOW_CATALOG` entries — candidate Salem / Lehmer-adjacent polynomials whose epistemic status (rediscovery vs. genuine novelty) hinges on a single oracle call: *is this polynomial in any known catalog?* Today that oracle consults exactly one source: **Mossinghoff's snapshot** (CECM mirror, http://www.cecm.sfu.ca/~mjm/Lehmer/), which covers Salem numbers up to degree ≤ 44 and Mahler measure M < 1.3 to degree 180. That is comprehensive within its scope, but it is one snapshot of one researcher's curated list as of the Mossinghoff–Rhin–Wu 2008 update.

A polynomial absent from Mossinghoff might still live in **OEIS** (A073011 enumerates Salem numbers), in **LMFDB** (number-field minimal polynomials), in **arXiv supplementary tables** (post-2008 papers extending Boyd / Smyth), in **Boyd's pre-2008 publications** (subsumed but not always cleanly), or in **Smyth's 2024 survey** bibliography pointing to dozens of less-indexed sources.

**Asymmetry of error costs:** a false-positive novelty claim ("we found a new small Salem number" when it has been known since 1985) is a cold-fusion-class reputational loss for the substrate. A false-negative ("we missed that this duplicates a known entry, so we deferred announcing") just slows discovery. **Federation is mandatory; the current single-source check is a bug we must close before any external claim.**

---

## 2. Catalog-by-Catalog Technical Survey

### 2.1 Mossinghoff (CECM mirror)
- **URL:** `http://www.cecm.sfu.ca/~mjm/Lehmer/lists/`
- **API:** none — flat ASCII / HTML; `SalemList.html`, `Lehmer.html`, degree-indexed `.txt` files
- **Format:** one polynomial per line, coefficient list or compact form; degree ≤ 44 (Salem), M < 1.3 to degree 180 (Lehmer)
- **License:** academic, cite Mossinghoff–Rhin–Wu 2008 (*Math. Comp.* 77, 1681–1694)
- **Ingest:** wget mirror, ~5 MB total, parse line-by-line; canonicalize to monic integer-coefficient tuple
- **Query:** O(1) hash-set membership after ingestion
- **Status:** **already in `discovery_env`; this is the only catalog currently consulted.**

### 2.2 OEIS
- **URL:** `https://oeis.org/A073011` (Salem numbers), plus A002193, A219243, etc.
- **API:** REST endpoint `?fmt=json` exists but, **per Scout #4, the OEIS REST API is rate-blocked from the agent toolchain.**
- **Workaround:** the **`oeisdata` GitHub repo** (https://github.com/oeis/oeisdata) is a Git-LFS mirror of all b-files; clone once, refresh nightly via cron.
- **Backup:** Wayback Machine snapshots of A-numbers (`http://web.archive.org/web/*/oeis.org/A073011`) when GitHub mirror lags.
- **Caveat:** **A-numbering bias** — OEIS Salem entries store numerical values to ~20 digits, not minimal polynomials. Federation requires recomputing the minimal polynomial from the numerical root with `mpmath`/`flint` (LLL on `[1, x, x², …, x^d]` for moderate degree).
- **License:** CC-BY-NC-SA 4.0 (OEIS terms). Attribution required; no commercial redistribution.

### 2.3 LMFDB
- **URL:** local Postgres mirror at `devmirror.lmfdb.xyz` (see `reference_lmfdb_postgres.md`)
- **Relevant tables:** `nf_fields` (number fields, by minimal polynomial of a generator), `nf_fields_isoms`, possibly `lf_fields` for local data
- **No native Mahler-measure column**, but Salem polynomials of degree d generate a degree-d number field with specific Galois-group / signature constraints (signature `(2, (d-2)/2)` for Salem). Query: `SELECT label, coeffs FROM nf_fields WHERE degree = $1 AND coeffs = $2` (with canonicalization upstream).
- **Coverage:** strong for low-degree number fields (≤ 23); weakens above. Not all Salem polynomials surface as `nf_fields` entries — only those whose number field has been catalogued — so LMFDB is a **complementary**, not exhaustive, signal.
- **Rate:** local Postgres, no rate limit. Batch via `COPY` and `IN (…)` clauses.
- **License:** CC-BY-SA 4.0.

### 2.4 arXiv supplementary tables (per Scout #2)
- **Pipeline:** ar5iv HTML → TexSoup → coefficient-table extraction → `latex2sympy2` for in-line polynomials → canonicalize.
- **Targets:** post-2008 papers (Mossinghoff cutoff): Smyth 2015/2024 surveys, Hare–Mossinghoff follow-ups, Hironaka, Lakatos, Dubickas, McKee, El Otmani et al.
- **Quality:** parser-quality dependent; `confidence ∈ [0, 1]` field per entry. Manual spot-check for any candidate that newly fires here.
- **License:** per-paper; arXiv default permits text/data mining for non-commercial.

### 2.5 Boyd's pre-2008 tables
- **Status:** subsumed by Mossinghoff *as of 2008*, but Boyd's original publications (Bull. AMS 1980, *Math. Comp.* 1980 / 1989) contain tables in PDF form that may have specific normalizations or annotations Mossinghoff dropped.
- **Ingest:** OCR + manual proof-read; one-time effort, ~few hundred entries.
- **Treat as audit corpus**, not primary lookup, since Mossinghoff dominates.

### 2.6 Smyth survey (2024)
- **URL:** `https://webhomes.maths.ed.ac.uk/~chris/papers/Smyth240707.pdf`
- **Role:** **bibliographic backbone, not a queryable catalog**. Use as the index of which other sources to ingest.
- **Action:** parse references, build a TODO of any cited table not yet in our federation.

### 2.7 MathSciNet / zbMATH
- **Access:** paywalled. Institutional credentials required.
- **Use case:** disambiguating attribution when a candidate appears novel against open sources — defer until then.
- **License risk:** scraping violates ToS; restrict to manual lookups.

### 2.8 Lehmer-conjecture survey papers
- **Stewart 1978**, **Borwein–Dobrowolski–Mossinghoff 2007**, **Smyth 2008/2024**, **Dubickas surveys**.
- Mostly bibliographic; tables therein roll up into Mossinghoff or arXiv-extracted.

### 2.9 Inspire-HEP / NASA ADS analogs
- Not relevant for pure-math polynomial catalogs. **Skip.**

---

## 3. Federation Architecture Proposal

```python
def cross_catalog_check(
    poly: Polynomial,
    catalogs: list[str] | None = None,
    snapshot_version: str = "latest",
) -> dict[str, CatalogResult]:
    """
    Returns {catalog_name: CatalogResult(present: bool|None, label: str|None,
                                         confidence: float, snapshot: str)}
    None means 'unknown / catalog not consulted / parser-failure'.
    """
```

**Implementation principles:**

1. **Local mirror + cache (per `feedback_two_machine_sync.md`).** Every catalog lives on `Z:\catalogs\<name>\<snapshot_date>\`. Nightly sync job refreshes from upstream. Agent processes **never** call live remote APIs — too fragile, rate-limit failures masquerade as discovery candidates.

2. **Canonicalization step.** A polynomial has many equivalent forms:
   - palindrome / reciprocal pair (Salem polynomials are reciprocal by construction)
   - sign-flip on odd-degree (`p(x) → ±p(±x)`)
   - root-of-unity twist (rare but exists for cyclotomic-adjacent factors)
   - leading-coefficient normalization (always monic in our convention)

   Canonical form: monic, integer coefficients, lex-smaller of `{coeffs, reciprocal(coeffs), neg_alt(coeffs)}`. Hash this tuple. **All catalog entries are canonicalized once at ingest; queries canonicalize once.**

3. **Batch query interface.** Build a `frozenset[CanonicalKey]` per catalog at ingest. `cross_catalog_check` is then O(k) where k = number of catalogs, not O(N) over catalog size. For batches of M candidates, vectorize: `set.intersection(candidates_canon, catalog_keys)`.

4. **Per-catalog confidence.**
   - LMFDB: 1.0 (rigorous, vetted)
   - Mossinghoff: 1.0 (curated by domain expert)
   - OEIS: 0.95 (curated, but Salem entries are numerical → re-derived minpoly carries small risk)
   - Boyd-OCR: 0.85 (OCR + manual)
   - arXiv-extracted: 0.50–0.90 (parser-dependent; ship the parser confidence through)

5. **Versioning.** Every `CatalogResult` records `snapshot: str` (e.g. `"mossinghoff_2024-08-14"`). Re-checking 6 months later with new snapshots produces a *diff*, not an overwrite — reproducibility of past absence claims is mandatory for the substrate's credibility.

6. **Aggregation policy.** A polynomial is **NOVEL** only if **every** consulted catalog returns `present=False` AND at least three catalogs returned a definite (non-`None`) answer. Anything else is `INDETERMINATE` and routed to HITL (Scout #5) before any claim leaves the substrate.

---

## 4. Anti-Patterns

- **Single-catalog check rebadged as "comprehensive."** *Current state.* The `is_in_catalog()` function in `discovery_env` consults Mossinghoff only and is referred to in logs as "the catalog check." Rename to `is_in_mossinghoff()` immediately; reserve the unqualified name for the federated version.
- **No canonicalization.** Mossinghoff lists the reciprocal form of degree-d Salem polynomials; OEIS A073011 lists numerical roots from which we derive minpoly; arXiv tables use whichever convention the author preferred. Without a canonical key, a polynomial in catalog under a different normalization registers as novel. **High-frequency false-positive class.**
- **Live API dependency.** `requests.get("https://oeis.org/...")` inside agent code → rate-limit → 429 → exception caught as "catalog returned no match" → polynomial marked novel. *This is exactly how cold-fusion-shape errors enter.*
- **No versioning.** "We claimed novelty in March; in May LMFDB extended its coverage; the polynomial is now on LMFDB. Was our March claim wrong?" Without snapshot-pinning, this question is unanswerable.
- **License blindness.** Bulk-ingesting MathSciNet violates Elsevier ToS; OEIS data is CC-BY-NC-SA (no commercial redistribution). Scrape policy must be reviewed per source, recorded in `catalog_metadata.json`.

---

## 5. Concrete Next Move for Techne

**Week 1.** Build `Z:\catalogs\` skeleton. Implement canonicalizer. Ingest **Mossinghoff** (already partly there — formalize) and **OEIS A073011** (via `oeisdata` GitHub mirror clone, not REST). Wire `cross_catalog_check` with these two backends. Ship `is_in_mossinghoff()` rename.

**Week 2.** Layer in **arXiv-extracted catalog** via Scout #2's TexSoup pipeline. Start with the post-2008 Smyth-cited papers (~30 PDFs). Treat parser confidence as first-class.

**Week 3–4.** Add **LMFDB nf_fields** query backend. Co-design with Mnemosyne (per `reference_postgres_dual.md`) so the SQL lives in the team-research DB and snapshot version maps to LMFDB release tag.

**Defer:** Boyd-OCR (low marginal value over Mossinghoff), MathSciNet / zbMATH (paywalled, defer until a candidate survives all open sources and warrants escalation). Smyth survey is consulted as bibliography only.

**Definition of done for v1:** `cross_catalog_check(p)` returns 4 backends' verdicts in <50 ms with snapshots pinned, and `discovery_env` refuses to emit a `NOVEL` label without the federated check passing.

---

## 6. References

1. Mossinghoff, M. J. — *Lehmer's Problem* page, CECM. http://www.cecm.sfu.ca/~mjm/Lehmer/
2. Mossinghoff, Rhin, Wu (2008). *Minimal Mahler measures.* Math. Comp. 77, 1681–1694.
3. Smyth, C. (2024 update). *The Mahler measure of algebraic numbers: a survey.* https://webhomes.maths.ed.ac.uk/~chris/papers/Smyth240707.pdf
4. Boyd, D. W. (1980). *Reciprocal polynomials having small measure.* Math. Comp. 35, 1361–1377.
5. Boyd, D. W. (1989). *Reciprocal polynomials having small measure II.* Math. Comp. 53, 355–357.
6. Borwein, P., Dobrowolski, E., Mossinghoff, M. (2007). *Lehmer's problem for polynomials with odd coefficients.* Annals of Math. 166, 347–366.
7. Stewart, C. L. (1978). *Algebraic integers whose conjugates lie near the unit circle.* Bull. SMF 106, 169–176.
8. OEIS Foundation — A073011 *Salem numbers.* https://oeis.org/A073011
9. OEIS Data mirror (GitHub LFS). https://github.com/oeis/oeisdata
10. LMFDB Collaboration — *L-functions and Modular Forms Database.* https://www.lmfdb.org and devmirror.lmfdb.xyz
11. ar5iv — HTML rendering of arXiv. https://ar5iv.labs.arxiv.org
12. Hironaka, E. (2001). *The Lehmer polynomial and pretzel links.* Canad. Math. Bull. 44, 440–451.
13. Dubickas, A. — survey papers on heights and Mahler measure.
14. McKee, J., Smyth, C. (2012). *Salem numbers and Pisot numbers via interlacing.* Canad. J. Math. 64, 345–367.
15. Internal: `feedback_two_machine_sync.md`, `reference_lmfdb_postgres.md`, `reference_postgres_dual.md`, Scout #2 (`02_arxiv_polynomial_ingestion.md`), Scout #4 (`04_obstruction_shape_oeis_a150_a151.md`), Scout #5 (`05_hitl_shadow_catalog_triage.md`).
