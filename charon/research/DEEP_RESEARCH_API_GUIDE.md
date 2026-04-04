# Gemini Deep Research via API — Operational Guide
## Proven 2026-04-03 | Charon Sprint

---

## What We Proved Tonight

The Gemini Deep Research agent — the same one that produces 30K+ word cited research
reports through the web UI — is accessible programmatically via the Interactions API.
This changes the research pipeline from "James manually pastes briefs into a browser"
to "fire-and-forget batch submission with automatic result collection."

### Key Discovery: API Quota is Separate from Web UI

| Channel | Daily Limit | Quota Pool |
|---------|-------------|------------|
| Web UI (gemini.google.com) | 20 reports/day | Tied to Google One subscription |
| Interactions API | Unknown ceiling (tested 7 tonight, all succeeded) | Tied to API key / project |

We burned the web UI limit during the day on packages 1-9. The API submissions
for packages 10, 13-17, 21 all went through on the same calendar day. Either the
quotas are independent, or the API limit is higher than 20.

---

## The Pipeline

### Architecture

```
RESEARCH_BRIEF.md  →  Interactions API  →  Deep Research Agent  →  Poll for completion  →  Save .md
     (human)           (programmatic)      (multi-step web search)    (30s intervals)      (automatic)
```

### Timing

| Package | Topic | Chars Returned | Time to Complete |
|---------|-------|---------------|-----------------|
| 14 | Tamagawa theory | 27,906 | ~4 minutes |
| 15-17, 21 | Various | TBD (running) | ~4-5 min each |

### Cost

Free tier. The API key (`AIzaSy...DOI`) is on the free Google AI Studio tier.
Deep Research uses ~591K tokens per report (135K input, 13.7K output, 37K thinking,
405K tool use for web searches). No charges observed.

---

## How to Use

### Prerequisites

```bash
pip install google-genai  # v1.66.0+ required
```

API key in `F:\Prometheus\googleAI\.env`:
```
GEMINI_API_KEY=AIzaSyAuW6V9p8WvVSMc_nm2XCvnMxKtVzSwDOI
```

### Quick One-Off Submission

```python
from google import genai

client = genai.Client(api_key="YOUR_KEY")

interaction = client.interactions.create(
    agent="deep-research-pro-preview-12-2025",
    input="Your research question or brief here...",
    background=True,
)

print(f"ID: {interaction.id}")
print(f"Status: {interaction.status}")  # "in_progress"
```

### Poll for Results

```python
result = client.interactions.get(id=interaction.id)

if result.status == "completed":
    for output in result.outputs:
        if hasattr(output, 'text'):
            print(output.text)  # The full research report
```

### Batch Submission Script

```bash
# Test one package (dry run):
python charon/research/submit_deep_research.py --test 14

# Submit all pending:
python charon/research/submit_deep_research.py --all

# Submit specific packages:
python charon/research/submit_deep_research.py 14 15 16

# Check status of running submissions:
python charon/research/submit_deep_research.py --status
```

The batch script handles:
- Sliding window of 3 concurrent submissions (Deep Research limit)
- Auto-backfill: when one completes, the next queues immediately
- Automatic result saving to the package directory
- Status tracking in `_submission_status.json`

---

## API Details

### Endpoint

The Interactions API is experimental (as of google-genai v1.66.0). Key parameters:

```python
client.interactions.create(
    agent="deep-research-pro-preview-12-2025",  # Agent ID (may change in future versions)
    input="...",                                  # The research query (string)
    background=True,                              # Required for Deep Research (async)
)
```

### Response Object

```python
interaction.id        # Unique ID for polling
interaction.status    # "in_progress" | "completed" | "failed" | "cancelled"
interaction.created   # Timestamp
interaction.updated   # Timestamp
interaction.outputs   # List of content objects (None until completed)
interaction.usage     # Token counts (input, output, thinking, tool_use)
```

### Output Extraction

```python
for output in interaction.outputs:
    if hasattr(output, 'text'):
        report_text = output.text  # The markdown research report
```

### Status Values

| Status | Meaning |
|--------|---------|
| `in_progress` | Agent is searching the web and synthesizing |
| `requires_action` | Agent needs user input (shouldn't happen with background=True) |
| `completed` | Report ready in `.outputs` |
| `failed` | Something went wrong |
| `cancelled` | Cancelled via `client.interactions.cancel(id=...)` |
| `incomplete` | Timed out or partial result |

### Concurrency

- Web UI: max 3 concurrent Deep Research reports
- API: tested 3 concurrent successfully; same limit assumed
- Sliding window pattern: submit 3, poll, backfill on completion

### Token Usage (typical for a research brief)

| Category | Tokens |
|----------|--------|
| Input | ~135K |
| Output | ~14K |
| Thinking | ~37K |
| Tool use (web searches) | ~405K |
| **Total** | **~591K** |

---

## What This Enables

### Before (manual)
1. Open gemini.google.com
2. Click Deep Research
3. Paste research brief
4. Wait 3-5 minutes
5. Copy result
6. Save to file
7. Repeat 20x (daily limit)

### After (programmatic)
1. Write RESEARCH_BRIEF.md files
2. Run `python submit_deep_research.py --all`
3. Walk away
4. Results saved automatically to package directories

### For Prometheus Specifically

The research package pattern (write brief → submit → save results → analyze) is now
fully automatable. A single command dispatches an entire batch of research questions,
respects the concurrency limit, and collects results into the correct directories.

This means:
- **Council review cycles accelerate.** When the council demands 9 falsification tests,
  the literature searches for all 9 can fire simultaneously.
- **Research briefs become reusable.** The RESEARCH_BRIEF.md format works for both
  manual web UI submission and programmatic API submission.
- **Results are machine-readable.** Saved as markdown, parseable by any downstream agent.
- **No babysitting.** Fire before dinner, results waiting after.

---

## Files

```
charon/research/
├── submit_deep_research.py          # Batch submission script
├── _submission_status.json          # Tracks active/completed submissions
├── DEEP_RESEARCH_API_GUIDE.md       # This file
├── TONIGHT_REMINDER.md              # Tonight's submission plan
├── INDEX.md                         # Master index of all packages
├── package_14_tamagawa_theory/
│   ├── RESEARCH_BRIEF.md            # Input
│   └── gemini-research_2026-04-03.md # Output (27.9K chars)
├── package_15_normalization_artifacts/
│   ├── RESEARCH_BRIEF.md
│   └── gemini-research_2026-04-03.md # Output (pending)
...
```

---

## Caveats

1. **The Interactions API is marked "experimental."** The `agent` parameter name,
   agent ID, and response format may change in future SDK versions.

2. **Wachs (2026) citation quality.** Gemini's Deep Research frequently cites
   "Wachs (2026)" for murmuration/BSD results. In earlier manual submissions,
   Gemini hallucinated this reference. The API submission for package 14 also
   cites it extensively. Treat Wachs citations with caution — verify the actual
   arXiv ID exists before citing in any paper.

3. **Source URLs are redirects.** The citation URLs are `vertexaisearch.cloud.google.com`
   redirect links, not direct URLs. They resolve to the actual sources but may
   expire. Extract the actual URLs if archiving.

4. **Rate limits are undocumented.** We tested 7 submissions in one evening with
   no rejections. The ceiling is unknown. Don't fire 50 at once without testing.
