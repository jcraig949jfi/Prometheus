# Corpus Ingestion — TODO

## Priority 1: OpenWebMath (Hugging Face) — IN PROGRESS
- **Source:** `open-web-math/open-web-math` on Hugging Face
- **Size:** ~14.7B tokens, millions of math documents
- **Format:** JSONL with keys: url, text, date, metadata. LaTeX inline as `$...$` and `$$...$$`
- **Auth:** None needed (public dataset, streaming supported)
- **Pipeline:** Extract LaTeX → parse to ASTs (sympy) → symbol/operator extraction → feed L2a ast_bridge
- **Why first:** Pre-cleaned, no parsing infrastructure needed, directly upgrades L2a from symbol bags to real ASTs
- **Status:** Streaming confirmed, `datasets` library installed

## Priority 2: ARQMath Formula Datasets
- **Source:** NTCIR MathIR / ARQMath competition datasets
- **Size:** Millions of isolated formulas from arXiv + MathOverflow
- **Format:** Indexed formulas with structural markup
- **Auth:** TBD (may need competition registration)
- **Pipeline:** Download → normalize notation → feed L2a + concept layer
- **Why:** Purpose-built for structural math search — exactly our use case
- **Status:** Not started

## Priority 3: S2ORC (Semantic Scholar Open Research Corpus)
- **Source:** Semantic Scholar API / bulk download
- **Size:** Tens of millions of papers, structured JSONL
- **Format:** Parsed text, citation graphs, isolated math elements
- **Auth:** May need API key
- **Pipeline:** Filter to math papers → extract formulas + citation graph → feed L2a + L2c
- **Why:** Citation graph is a massive new graph for graph_invariants. Math isolation already done.
- **Status:** Not started

## Priority 4: arXiv Bulk Data (raw .tex)
- **Source:** Kaggle / Google Cloud / AWS S3
- **Size:** 1TB+ of raw .tex source files, 2M+ papers
- **Format:** Raw LaTeX
- **Auth:** Public
- **Pipeline:** Parse .tex → extract formulas → normalize notation → feed everything
- **Why:** Ground truth, every keystroke. But massive parsing effort.
- **Warning:** Notation variation across authors will inject noise. Need normalization layer BEFORE tensor ingestion.
- **Status:** Parked until Priorities 1-3 are exhausted

## Post-Ingestion: Structural Fingerprint Embedding
- **After OpenWebMath ingestion completes (~4-5M formulas expected)**
- Build `formula_embeddings.py` in `v2/layer2/`
- Each formula → 50D feature vector (operator_counts, structural_token_counts, depth, complexity)
- Run UMAP or spectral embedding on the full matrix for 2D/3D coordinates
- Cluster by structural similarity, not symbolic identity
- Cross-domain bridges = formulas from different domains in the same cluster (verb bridges)
- Wire into ast_bridge.py to replace Jaccard with structural distance
- **This is Option 2 — operator Jaccard (Option 1) was killed by F13**

## The Notation Problem
Different authors write the same math differently. Dedekind sums alone have 6+ notations.
OpenWebMath has partially standardized this. arXiv raw hasn't.
Any corpus ingestion pipeline MUST include a notation normalization step or the tensor fills with noise.
