# Ergon Learner — NotebookLM source bundle

**Purpose.** A self-contained set of documents about Project Prometheus's Ergon learner — the small evolutionary self-play engine being built as the validation arm of the substrate. Ten markdown sources, designed for NotebookLM ingestion, that together let a NotebookLM notebook answer questions about: what Ergon is, why it's being built this way, how the MVP is structured, what the trial gates are, what risks are tracked, and where it sits in the broader Prometheus architecture.

**Intended use.** Upload all 10 documents as sources to a single NotebookLM notebook (suggested name: "Ergon Learner — design + MVP"). Then ask the notebook things like:
- "What's the difference between Ergon's evolutionary engine and Techne's REINFORCE baseline?"
- "Why is Trial 1.5 a gate for Trial 2?"
- "How does the residual classifier failure mode get caught?"
- "What was the round-6 reviewer's critique that v8 absorbed?"
- "What's the relationship between bottled serendipity and Ergon's MAP-Elites?"

The bundle is designed for NotebookLM's grounded-Q&A surface — every answer should be cite-able back to one of the 10 sources.

## Source manifest

| # | File | Topic | ~Words |
|---|---|---|---|
| 00 | `00_executive_summary.md` | One-page elevator pitch on Ergon | 600 |
| 01 | `01_pivot_thesis.md` | Why Ergon is the learner side; pushback on Charon §4.4; eight-week commitment | 1800 |
| 02 | `02_architecture.md` | v8 design freeze: what's built, library stack, four trials | 2200 |
| 03 | `03_mvp_plan.md` | Day-by-day execution Days 1–30 | 1700 |
| 04 | `04_risk_register.md` | R1–R13 with mitigations; failure paths per trial | 1400 |
| 05 | `05_silver_context.md` | Why Silver's Ineffable raise frames the work; what changes | 1200 |
| 06 | `06_discovery_via_rediscovery.md` | The unification: rediscovery and discovery as same loop, different oracle states; three-stage validation ladder | 1500 |
| 07 | `07_components_inventory.md` | File-by-file map of `ergon/learner/` MVP code | 800 |
| 08 | `08_three_arm_pilot.md` | The five-counts diagnostic; why Ergon's MAP-Elites becomes the load-bearing comparison arm vs LLM-REINFORCE vs uniform random | 1100 |
| 09 | `09_glossary.md` | Terms NotebookLM needs to ground its answers (BIND/EVAL, MAP-Elites, F1+F6+F9+F11, etc.) | 1400 |

Total ~13,700 words across 10 sources. Well within NotebookLM Plus's 300-source per-notebook limit and per-source 500K-word ceiling.

## Upload paths (in order of friction)

**Path A — Manual drag-and-drop (works on every NotebookLM tier).**
1. Open notebooklm.google.com → "+ New notebook"
2. Click "Add source" → "Upload"
3. Drag all 10 `.md` files from this directory into the upload modal
4. Wait ~30 seconds for ingestion

This is the path that always works. ~1 minute total.

**Path B — Google Drive auto-sync (NotebookLM Plus and above).**
1. Copy this directory's contents into a Google Drive folder (e.g., `Prometheus/NotebookLM/Ergon Learner/`)
2. In NotebookLM: "+ New notebook" → "Add source" → "Google Drive" → select the folder
3. Add each file as a source, OR use "Discover sources" if your account supports folder-level addition
4. Future updates: edit the markdown files locally + push to Drive (or commit to git and re-export); NotebookLM Plus offers a "Refresh" button per Drive source to re-sync

Best for ongoing maintenance — you can iterate on the bundle and the notebook stays current without re-upload.

**Path C — Public GitHub URL ingestion.**
The Prometheus repo is at https://github.com/jcraig949jfi/Prometheus. After this bundle is committed, each file has a stable URL like:
`https://raw.githubusercontent.com/jcraig949jfi/Prometheus/main/aporia/notebooklm_bundles/ergon_learner/00_executive_summary.md`

In NotebookLM: "+ Add source" → "Website" → paste URL. Repeat for each of the 10 files. NotebookLM will fetch the raw markdown content. **However**: NotebookLM's URL-source ingestion is best for pages, not raw markdown — you may need to use a markdown-to-HTML rendering URL (e.g., GitHub's "blob" URL which renders the markdown) instead of the "raw" URL. Test on one source first.

**Path D — Programmatic API (verified status, May 2026).**

After web research, the API picture is:

- **Consumer NotebookLM (free + NotebookLM Plus)**: No public API for source upload as of April–May 2026. Per the Google AI Developers Forum and multiple third-party sources: Google has not announced a release date, has not opened a developer waitlist, and has not exposed any documented programmatic surface for the consumer tier. Plus plan increases limits (100 sources per notebook vs 50 free; 200 notebooks total vs 100 free) but does NOT add API access. **Web interface only.**

- **NotebookLM Enterprise**: HAS a documented REST API via the Vertex AI Discovery Engine. Endpoints:
  - `POST https://{ENDPOINT_LOCATION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks` — create a notebook
  - Add-data-sources endpoint for batch or single-file source ingestion (Google Docs, Slides, raw text, web content, YouTube)
  - Documentation: `docs.cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks-sources`
  - **Requires Workspace Enterprise / NotebookLM Enterprise tier**, which is a different product from consumer Plus.

- **Third-party wrappers (unofficial)**: `gnh1201/notebooklm-rest-api` (GitHub) wraps the web UI as a REST API; Apify's NotebookLM actor offers programmatic access. **Both are unofficial, may break with web-UI changes, and ToS implications are unclear.** Use with caution; not recommended for production substrate work.

**Implication for this bundle**: if the user is on consumer NotebookLM Plus, **API upload is not available** — Paths A (drag-drop) or B (Drive sync) are the realistic options. If the user is on NotebookLM Enterprise (via Workspace Enterprise), the Vertex AI Discovery Engine REST API can be used; the bundle's source manifest below maps cleanly onto a batched `add-data-sources` call.

**Honest recommendation**: regardless of tier, Path A (drag-and-drop) takes ~30 seconds and works on every plan. If the user values automation, Path B (Drive sync) is set up once and auto-syncs forever — strictly better than any third-party wrapper. The Enterprise REST API is overkill for an 11-source bundle that updates weekly.

## Update cadence

This bundle reflects Ergon's state as of 2026-05-03 (pre-MVP build; design frozen at v8). Trial reports will land in `ergon/learner/trials/TRIAL_*_REPORT.md` as the MVP runs (Days 1–30 starting 2026-05-04). Suggested workflow:
- Re-export this bundle weekly during the 30-day MVP window
- Major design changes (v9+) → bundle revision number bumps
- Trial reports added as new sources (suggest one per trial, named `10_trial_1_results.md`, `11_trial_2_results.md`, etc.)

## Curation notes

- Each source is **self-contained** — no inline references to "see file X" except where X is also in this bundle. NotebookLM cannot follow external file references.
- Each source **ends with a "Where to find more"** section listing the canonical repo paths, so a curious user can dive deeper after the NotebookLM session.
- The **glossary (`09_glossary.md`)** defines every term that appears in 2+ other sources. NotebookLM grounds answers better when key terms are defined in their own source.
- Authority chain preserved: when a source quotes from a v8 spec or a session journal, the quote is verbatim with the commit reference.

---

*Aporia, 2026-05-03. Companion to `aporia/scouting/QUEUE.md` and the broader pivot work. The 10 sources together are designed to answer ~80% of plausible "what is Ergon doing?" questions; for the remaining 20%, the canonical repo paths get you to the source-of-truth.*
