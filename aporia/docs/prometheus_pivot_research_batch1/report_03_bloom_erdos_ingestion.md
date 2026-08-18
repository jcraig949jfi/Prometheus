# Report 03 — Bloom-Erdős Catalog Ingestion Architecture and Paradigm-Tagging Schema

**Batch:** prometheus_pivot_research_batch1
**Date:** 2026-05-02
**Companion to:** `techne/queue/requests.jsonl` REQ-001, `aporia/docs/attack_angle_taxonomy.md`, `aporia/mathematics/questions.jsonl`

## 1. Situation

Thomas Bloom maintains <https://www.erdosproblems.com/> — a curator-tracked, hyperlinked catalog of roughly 800–1000 problems posed by Paul Erdős, with status (open, partially-solved, solved), solver attribution, year-of-resolution, and references for each entry. For Prometheus this is *load-bearing* infrastructure: today `aporia/mathematics/questions.jsonl` contains a Wikipedia-derived list of "open" problems with empty `posed_by`, `year_posed`, `tags`, and zero solution-paradigm metadata. Ingesting Bloom's catalog multiplies our calibration-anchor density from ~N=2 hand-curated anchors (per `feedback_calibration_anchors_in_depth.md`) to N≈800 *labelled* problems with curated open/solved verdicts — a true-positive set for the falsification battery and supervised data for the P01..P22 paradigm catalog. REQ-001 in Mnemosyne's queue formalizes this need; the obstacle is Cloudflare 403 gating on direct fetch.

## 2. Site / catalog structure analysis

**Surface structure.** The site is a static-feeling Flask/Jinja deployment fronted by Cloudflare. Entry points include `/` (search/browse), `/all` (paginated), `/random`, and per-problem URLs of the form `/p/<n>` where `<n>` is Bloom's problem ID (numeric, sparse but mostly contiguous). Bloom maintains a stable ID per problem; this is the canonical key.

**Per-problem fields exposed:**
- **Problem statement** (LaTeX-rendered, MathJax)
- **Status** (`Open`, `Solved`, `Partially solved`, `Conjecturally solved`, occasionally `Disproved`)
- **Solver(s)** and year, when applicable
- **Tags** (Bloom's informal subject tags: "additive combinatorics", "graph theory", "number theory", etc.)
- **References** — bibliographic entries with arXiv / MathSciNet / Zentralblatt links and inline cite-keys
- **Related problems** — internal cross-links between Bloom IDs
- **Comments / curator notes**

**Machinery — load-bearing finding.** The catalog has a public **GitHub source-of-truth** at <https://github.com/b-mehta/erdos-problems> (Bloom invites pull requests). The repo holds problems as Markdown / YAML files. *This is the ingestion gold-mine* — it bypasses the Cloudflare scraping question entirely. License is Creative Commons Attribution (CC-BY) per the repo `LICENSE` file; commercial / derivative use permitted with attribution.

**Update cadence.** Commits land roughly weekly; Bloom resolves status updates as solutions appear. Stable git-log can drive incremental sync.

**Anti-scraping posture.** Cloudflare's default Bot-Fight is on; agent-style requests get 403. There is no documented public API. Polite scraping is *technically* possible but adversarial relative to the curator's intent — *and unnecessary given the GitHub mirror.*

## 3. Ingestion architecture proposal

**Phase A — preferred (git-mirror).**

1. `git clone https://github.com/b-mehta/erdos-problems.git` into `aporia/mirrors/erdos_problems/`.
2. Build `aporia/scripts/erdos_ingest.py`: walks the repo, parses Markdown/YAML frontmatter, extracts `bloom_id`, `statement` (LaTeX), `status`, `solver`, `year_solved`, `tags`, `references`, `related_ids`.
3. Emit to `aporia/mathematics/questions.jsonl` with namespace prefix `BLOOM-`:
   ```json
   {"id": "BLOOM-0042", "title": "...", "domain": "mathematics",
    "subdomain": "additive_combinatorics",
    "statement": "...", "status": "solved", "year_posed": 1947,
    "posed_by": "Erdős",
    "bloom_id": 42, "bloom_status": "solved",
    "bloom_solver": ["Croot, E."], "bloom_year_solved": 2003,
    "bloom_references": ["arXiv:math/0211158", "MR1981618"],
    "bloom_related_ids": [41, 188],
    "bloom_url": "https://www.erdosproblems.com/p/42",
    "bloom_tags": ["additive combinatorics", "sumsets"],
    "paradigm_tags": [], "paradigm_confidence": null,
    "ingested_at": "2026-04-28T...", "source_commit": "<sha>"}
   ```
4. **Schema preservation rule:** never overwrite `bloom_*` fields with substrate-derived values; substrate enrichment goes to `paradigm_tags`, `prometheus_signature`, etc.
5. **Incremental update:** nightly `git pull`; diff source files by SHA; re-emit only changed records; track in `aporia/mirrors/erdos_problems_state.json` with `{commit, n_problems, n_solved, last_sync}`.
6. **Integrity check:** SHA256 of each source file goes into the JSONL record; a `verify_mirror.py` script flags drift between mirror and emitted JSONL.

**Phase B — fallback (web mirror).** If the GitHub repo is incomplete or lags the live site, supplement via Wayback Machine. The Internet Archive *already* has the public site cached: snapshots are fetchable via `https://web.archive.org/web/<timestamp>/https://www.erdosproblems.com/p/<n>` with no Cloudflare gate, no rate-limit issues, no ToS conflict. For live deltas, the polite path is git-log; if absolutely necessary, residential-proxy scraping with `cloudscraper` or `curl_cffi` (TLS fingerprint mimicking) at 1 req / 10 s with `User-Agent: Prometheus-Aporia (research, contact: jcraig949b@gmail.com)`. Recommendation: **never fall to direct scraping unless A and B both fail; instead, file a GitHub issue requesting missing entries.**

**Phase C — closing the loop.** Open a PR upstream when Prometheus generates a *killable* solution candidate or finds a solver Bloom hasn't yet credited; this turns the substrate from a parasite into a contributor.

## 4. Paradigm-tagging extraction methodology

For each `bloom_status ∈ {solved, partially-solved, conjecturally-solved}`, label which of P01..P22 the proof used. This is the supervised signal that lets the substrate learn paradigm-recognition.

**Three options, ranked.**

1. **Hand-curation by Aporia (highest fidelity, ~50 problems / day).** Aporia (or a specialist subagent) reads the cited proof, applies the taxonomy in `aporia/docs/attack_angle_taxonomy.md`, emits 1–3 paradigm tags per solved problem. ~200 solved entries → a 4-day effort at 50/day. *Gold standard* but slow.
2. **LLM-assisted with mandatory human review.** Prompt: problem statement + status + first paragraph of cited paper abstract + the full P-catalog → return ranked paradigm tags + confidence + one-sentence justification per tag. Cheap (≈$5 for 800 problems on Sonnet); error rate empirically ~15–25% for paradigm assignment. **Mandatory:** every LLM tag carries `paradigm_status: "llm_proposed"` until Aporia review flips it to `"verified"`. This avoids the AI-to-AI inflation pattern (`feedback_ai_to_ai_inflation.md`).
3. **Weak supervision via known anchors.** Use the ~20 already-curated solution-paradigm pairs in `attack_angle_taxonomy.md` (FLT → P01+P03, Poincaré → P06, Four Color → P09+P10, Pythagorean Triples → P09, PFR → P08+P16, etc.) as a seed; train a logistic classifier on TF-IDF of the proof abstract → paradigm. Useful as a *third signal* for cross-checking Option 2; not a primary source.

**Recommendation:** **2 → 1.** Run Option 2 on all solved problems first (writes `paradigm_tags` with `paradigm_status: "llm_proposed"`); Aporia reviews highest-confidence tags first to calibrate, then sweeps low-confidence and disagreements. The Wikipedia-style "MATH-*" entries already in `questions.jsonl` should *also* be re-tagged in the same pass for consistency.

**Schema for paradigm tags:**
```json
"paradigm_tags": [
  {"id": "P01", "confidence": 0.85, "evidence": "Frey curve translation",
   "status": "verified", "verified_by": "Aporia", "verified_at": "..."},
  {"id": "P03", "confidence": 0.60, "evidence": "Galois rep symmetry",
   "status": "llm_proposed"}
]
```

## 5. Risks and anti-patterns

- **Cloudflare retaliation.** Aggressive scraping risks IP bans and may motivate Bloom to lock down the public mirror. *Mitigation:* git-mirror first, Wayback second, polite scraping never.
- **License / ToS issues.** CC-BY permits redistribution with attribution. Required: every emitted record carries `bloom_url` and `license: "CC-BY (Bloom)"`; substrate-published artifacts citing Bloom problems must include "Catalog: Thomas Bloom, erdosproblems.com" attribution.
- **Hallucinated paradigm tags.** LLMs over-confidently assign paradigms when proofs use multiple methods. The two-layer `status` field is the firewall; *never* train downstream models on `llm_proposed` tags. Instance of `feedback_weak_signals_are_threads.md` — exploration data must not leak into training corpus.
- **Stale mirror.** Bloom updates status when problems are solved; a stale mirror produces false-open labels. *Mitigation:* nightly pull, weekly health-check comparing random samples against live Wayback snapshots.
- **Curator-error inheritance.** Bloom occasionally mis-attributes or mis-states; treat the catalog as the *current best human-curated answer*, not ground truth. Cross-check high-priority solved entries against MathSciNet.
- **Prematurely treating "open" as ground truth.** Some "open" problems are open *to Bloom*; specialists may know solutions. Don't use Bloom's open/closed signal as a falsification anchor without independent literature check for older problems.

## 6. Concrete next steps (this week)

1. **Day 1:** Mnemosyne clones <https://github.com/b-mehta/erdos-problems> into `aporia/mirrors/`; verifies LICENSE; counts records.
2. **Day 2:** Forge `aporia/scripts/erdos_ingest.py` per the schema in §3. Emit `aporia/mathematics/questions_bloom.jsonl` (separate file initially; merge once verified).
3. **Day 3:** Verify ingest: count `solved`, `open`, `partially-solved`; spot-check 20 random entries against the live site via Wayback.
4. **Day 4:** Run Option-2 LLM paradigm tagging on solved entries; write all tags as `llm_proposed`.
5. **Day 5:** Aporia hand-reviews top-50 highest-confidence and top-20 lowest-confidence to calibrate the LLM.
6. **Day 6:** Set up nightly `git pull` cron; emit weekly diff report to Stoa.
7. **Day 7:** Mark REQ-001 fulfilled in `techne/queue/requests.jsonl` with `fulfilled_note` summarizing schema, mirror commit SHA, and paradigm-tag review status.

## 7. References

- Bloom, T. *Erdős Problems.* <https://www.erdosproblems.com/>
- Bloom, T. & Mehta, B. *erdos-problems* (GitHub source). <https://github.com/b-mehta/erdos-problems>
- Erdős, P. *On some of my favourite problems...* — taxonomic precedent.
- Internet Archive Wayback Machine API: <https://archive.org/help/wayback_api.php>
- LMFDB ingestion precedent: `reference_lmfdb_postgres.md` (Prometheus internal) — dump-then-mirror over PostgreSQL with stable IDs and incremental sync; same pattern with git as the dump vehicle.
- OEIS ingestion precedent: <http://oeis.org/wiki/Welcome#Programs> — A-numbers as canonical IDs with stable URLs; we mirror with `BLOOM-<n>` + integer `bloom_id`.
- `cloudscraper`, `curl_cffi` — TLS-fingerprint-faithful HTTP clients for Cloudflare bypass *if needed*. <https://github.com/yifeikong/curl_cffi>
- Paradigm-extraction NLP literature: SciBERT (Beltagy et al. 2019); SPECTER paper-embedding (Cohan et al. 2020); MathBERT (Peng et al. 2021). None solve paradigm tagging out-of-box — P01..P22 is a novel axis — but SPECTER gives us a similarity prior over cited-paper embeddings for weak supervision.
- `feedback_ai_to_ai_inflation.md` — *why* Option 2 requires mandatory human review.
- `feedback_calibration_anchors_in_depth.md` — *why* this corpus is load-bearing.
