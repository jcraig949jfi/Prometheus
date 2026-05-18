# M4 Eos Integration — applying the substrate redirect

**Filed:** 2026-05-18
**Author:** Aporia
**Target machine:** M4 (where eos_daemon runs)
**Source commit:** 54ccb3e9 (substrate doctrine + agora.eos_findings + scripts/eos_substrate_helpers.py)

`agents/` is gitignored on the public repo (same reason `scripts/llm_cascade.py` was extracted from `agents/metis/src/metis.py` in commit 77ed2f44). So the Eos daemon-side changes cannot ship through git directly. This doc is the recipe to apply on M4 after `git pull`.

## Step 1 — schema migration on Postgres host

One-time. Creates the new `agora.eos_findings` table.

```bash
python scripts/agora_persist.py init
```

Verify:

```bash
python scripts/agora_persist.py findings 24
# Empty list until the daemon runs, but the command should not error.
```

## Step 2 — eos_config.yaml on M4

Replace `search_topics:` with substrate-priority ordering. Keywords in slots 0-4 (arxiv) and 0 (github/openalex/s2) are the ones that actually fire per scan in the current daemon code. After Step 3 integration, slot-5+ keywords rotate in over time.

Full replacement file already on M1 at `agents/eos/configs/eos_config.yaml` (M1 disk only — copy manually or use the YAML below).

```yaml
search_topics:
  arxiv_categories:
    - "math.NT"
    - "math.AG"
    - "math.CO"
    - "math.RT"
    - "math.NA"
    - "math.AT"
    - "math.CT"
    - "math.QA"
    - "math-ph"
    - "cs.AI"
    - "cs.LG"
    - "cs.CL"
    - "cs.NE"

  arxiv_keywords:
    - "tensor decomposition algorithm"
    - "polynomial method proof"
    - "Mahler measure Lehmer"
    - "modularity lifting theorem"
    - "Sato-Tate distribution"
    - "border rank tensor"
    - "secant variety tensor"
    - "tensor network MPS DMRG"
    - "withdrawn conjecture counterexample"
    - "L-function zeros GUE deviation"
    - "BSD conjecture Selmer rank"
    - "Hecke eigenvalue congruence"
    - "p-adic perfectoid Fargues"
    - "Galois representation deformation"
    - "discrete Ricci flow graph"
    - "mechanistic interpretability"
    - "steering vectors"
    - "activation engineering"
    - "reasoning circuits"
    - "chain of thought internals"
    - "sparse autoencoder"
    - "CMA-ES neural"
    - "evolutionary latent"
    - "tensor decomposition neural"
    - "autonomous agent framework"
    - "meta cognition LLM"

  github_topics:
    - "lean4-mathlib"
    - "tensor-decomposition"
    - "computer-algebra"
    - "sagemath"
    - "polymake"
    - "macaulay2"
    - "theorem-proving"
    - "mechanistic-interpretability"
    - "transformer-lens"
    - "steering-vectors"
    - "activation-patching"
    - "evolutionary-algorithm"
    - "cma-es"
    - "sparse-autoencoder"
    - "ai-agent"
    - "autonomous-agent"

  github_keywords:
    - "Lean 4 Mathlib"
    - "tensor decomposition library"
    - "polymake tropical"
    - "Macaulay2 algebraic geometry"
    - "SageMath number theory"
    - "DeepSeek Prover theorem"
    - "mechanistic interpretability"
    - "steering vectors LLM"
    - "transformer-lens"
    - "sparse autoencoder LLM"
    - "CMA-ES neural"
    - "autonomous AI agent"
    - "activation patching"
```

## Step 3 — eos_daemon.py patch

Apply the following changes to `agents/eos/src/eos_daemon.py` on M4. Only 5 small spots.

### 3.1 — Import the helpers

After the existing imports near the top of the file (around line 40, just below where `_env_file` is loaded), add:

```python
# Substrate redirect — helpers live in scripts/ for cross-machine git sync.
_REPO_ROOT = EOS_ROOT.parent.parent
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))
try:
    from eos_substrate_helpers import (
        scan_idx, select_keywords, select_keyword_single,
        build_arxiv_category_filter, persist_finding_to_postgres,
    )
    HAS_SUBSTRATE_HELPERS = True
except Exception:
    HAS_SUBSTRATE_HELPERS = False
```

### 3.2 — scan_arxiv: rotation + category filter

Find the section:

```python
# Batch keywords into a single OR query to minimize requests
query = " OR ".join(f'all:"{kw}"' for kw in keywords[:5])
```

Replace with:

```python
# Rotation: 4 priority slots always fire + 1 rotating slot through the rest.
# Plus arxiv_categories now feeds an AND clause restricting to math papers.
keywords_all = config.get("search_topics", {}).get("arxiv_keywords", [])
categories_all = config.get("search_topics", {}).get("arxiv_categories", [])
if HAS_SUBSTRATE_HELPERS:
    keywords = select_keywords(keywords_all, n_top=4, n_per_scan=5, idx=scan_idx())
    category_clause = build_arxiv_category_filter(categories_all, max_n=8)
else:
    keywords = keywords_all[:5]
    category_clause = ""
keyword_clause = " OR ".join(f'all:"{kw}"' for kw in keywords)
query = f"({keyword_clause}) AND ({category_clause})" if category_clause else keyword_clause
```

Then in the arxiv result-append (around line 292), add two fields to the dict:

```python
results.append({
    "source": "arxiv",
    "title": title,
    "authors": authors[:5],
    "url": paper_id,
    "date": published,
    "summary": summary,
    "_keywords_matched": keywords,
    "_categories": categories_all[:8] if category_clause else [],
})
```

### 3.3 — scan_github, scan_openalex, scan_semantic_scholar: rotation

Each of these has a `query = keywords[0]` line. Replace with:

```python
if HAS_SUBSTRATE_HELPERS:
    query = select_keyword_single(keywords, idx=scan_idx())
else:
    query = keywords[0]
```

Each result-append needs `_keywords_matched` and `_categories` fields:

```python
results.append({
    ...existing fields...,
    "_keywords_matched": [query],
    "_categories": item.get("topics", []) if item.get("source") == "github" else [],
})
```

For github, change the existing per-item appended fields to include:

```python
"_keywords_matched": [query],
"_categories": repo.get("topics", []),
```

For openalex, semantic_scholar, tavily: `"_categories": []`.

### 3.4 — Postgres dual-write in run_cycle

In `run_cycle`, after the `top_items` / `analyses` lines and BEFORE `save_registry(registry)`, add:

```python
# Postgres dual-write — central agora.eos_findings so M1 agents can consume.
# Best-effort: silently skipped if helpers/PG unavailable.
if HAS_SUBSTRATE_HELPERS:
    item_score = {id(item): (score, reason) for item, score, reason in all_scored}
    news_scored = [(n, *_score_relevance(n)) for n in (news or [])]
    item_score.update({id(item): (score, reason) for item, score, reason in news_scored})
    persisted = 0
    for p in papers:
        score, reason = item_score.get(id(p), (None, None))
        persist_finding_to_postgres(
            p, item_type="paper",
            keywords_matched=p.get("_keywords_matched", []),
            categories=p.get("_categories", []),
            relevance_score=score, relevance_reason=reason,
        )
        persisted += 1
    for r in repos_new:
        score, reason = item_score.get(id(r), (None, None))
        persist_finding_to_postgres(
            r, item_type="repo",
            keywords_matched=r.get("_keywords_matched", []),
            categories=r.get("_categories", []),
            relevance_score=score, relevance_reason=reason,
        )
        persisted += 1
    for n in (news or []):
        score, reason = item_score.get(id(n), (None, None))
        persist_finding_to_postgres(
            n, item_type="news",
            keywords_matched=n.get("_keywords_matched", []),
            categories=n.get("_categories", []),
            relevance_score=score, relevance_reason=reason,
        )
        persisted += 1
    log.info(f"Postgres: persisted {persisted} findings to agora.eos_findings")
```

## Step 4 — restart Eos daemon

After Steps 1-3 land on M4:

```bash
# Whatever the daemon-restart pattern is on M4 (systemd, supervisor, manual)
# After restart, watch log for the new line:
#   "Postgres: persisted N findings to agora.eos_findings"
```

## Step 5 — verify from M1

```bash
# On any machine with agora_persist access (M1, etc.)
python scripts/agora_persist.py findings 24
```

Should show findings with substrate-priority keywords in `kw=` column.

## What changes after this lands

- Hourly Eos scans target substrate-priority topics (tensor decomposition, polynomial method, Mahler measure, modularity, Sato-Tate) instead of generic AI/ML.
- arxiv queries restrict to math categories AND substrate keywords (tighter than before).
- Single-keyword scanners (github/openalex/s2) now rotate through their full keyword list one per hour, exposing the entire pool over time instead of always hitting keyword[0].
- Every finding lands in `agora.eos_findings` on the Postgres host, readable from M1 by any substrate consumer (Aporia for triage, Techne for claim mining, etc.).
- AI/ML interpretability keywords preserved lower in the list — still fire when rotation reaches them.

— Aporia, 2026-05-18
