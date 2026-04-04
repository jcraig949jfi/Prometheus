# Tonight's Research Submission Plan
## When: After 8PM EST (Deep Research limit resets)
## Date: 2026-04-03

---

## Step 1: Test the API (one package)

First, test whether the Interactions API actually works for Deep Research.

```bash
# Make sure google-genai is installed
pip install google-genai

# Set your API key (if not already in googleAI/.env)
# Get one at https://aistudio.google.com -> "Get API Key"

# Test with package 14 (dry run — shows what would be submitted)
python charon/research/submit_deep_research.py --test 14

# If that looks right, submit ONE package to test the API:
python charon/research/submit_deep_research.py 14
```

**If the API works:** proceed to Step 2.

**If the API fails or needs allowlisting:** submit manually through gemini.google.com.
Copy-paste each RESEARCH_BRIEF.md into Deep Research. Save results to the package
folder as `gemini-research_2026-04-03.md`.

**If the Interactions API agent ID has changed:** check
https://ai.google.dev/gemini-api/docs/deep-research for the current agent ID.

---

## Step 2: Submit All 7 Packages

```bash
# Submit the 5 new packages + 2 still-pending from batch 1:
python charon/research/submit_deep_research.py --all

# Or submit specific ones:
python charon/research/submit_deep_research.py 10 13 14 15 16 17 21
```

**Submission order (priority):**
1. Package 16 — ILS support window (council members disagree, need definitive answer)
2. Package 14 — Tamagawa theory (all 4 reviewers demand this)
3. Package 15 — Normalization artifacts (is the wall real?)
4. Package 21 — Finite-conductor corrections (is the RMT gap structural?)
5. Package 17 — Wasserstein distance (novelty claim for architecture)
6. Package 13 — BSD invariants (Faltings height novelty check)
7. Package 10 — Nebentypus (character anomaly)

---

## Step 3: Check Results in the Morning

```bash
python charon/research/submit_deep_research.py --status
```

If using the manual web UI, results will be in your Gemini chat history.

---

## What These Research Packages Answer

| # | Package | What It Unblocks |
|---|---------|-----------------|
| 14 | Tamagawa theory | Whether to include Tamagawa in variance decomposition |
| 15 | Normalization | Whether the "BSD wall" could be an artifact |
| 16 | ILS window | Whether our wall location is consistent with theory |
| 17 | Wasserstein | Whether our distance metric idea is novel |
| 21 | Finite-conductor | Whether the RMT gap (0.05) is pre-asymptotic |
| 13 | BSD invariants | Whether Faltings height correlation is known |
| 10 | Nebentypus | Why 3.3x character enrichment goes against prediction |

---

## Meanwhile: The Other Instance

The other Claude Code session was stuck on a DuckDB insert loop (184K individual
inserts for Dirichlet L-function zeros). When it unsticks or you restart it:

**Fix the ingestion script** — replace individual INSERTs with batch insert:
```python
import pandas as pd
df = pd.DataFrame(rows, columns=[...])
con.execute("INSERT INTO dirichlet_zeros SELECT * FROM df")
```

**Then run the falsification battery** (these use existing data, no Gemini needed):
1. Orthogonalize BSD against conductor (Gram-Schmidt residuals)
2. Raw zeros reanalysis (unnormalized gamma_n)
3. Balanced sampling (458 vs 458 within SO(even))
4. 10,000 permutation trials (replace the 100-trial test)
