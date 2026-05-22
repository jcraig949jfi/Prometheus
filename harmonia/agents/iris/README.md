# Iris

> Prose-to-symbol compressor — the substrate's self-densifier.

## What Iris does for Prometheus

The restore protocol mandates that *prose read identically by every Harmonia cold-start is a symbol-promotion candidate*. The bet behind the swarm's compounding hypothesis is that prose becomes *explanation* (read once, internalized) and symbols become *mechanism* (resolved every restore) — and each promoted primitive cuts future cold-start cost across every Harmonia that follows.

Iris is the agent that makes that bet pay off. She runs a rotating scan over the corpus, fingerprints headings and procedural paragraphs by their token-bag signature, clusters them across files, and surfaces patterns that appear in ≥3 distinct files as symbol-promotion candidates. Each candidate gets a citation set (file + line per occurrence), a sketch versioned spec, and a savings estimate.

She never promotes anything herself. She files candidates to `artifacts/` and lets the conductor decide. If a candidate turns out to be noise, dismissing it is a single line appended to `state/dismissed_candidates.json` — Iris will skip future crossings of that fingerprint forever after.

Iris's value is leverage: every symbol she successfully promotes cuts every future Harmonia's cold-start time. Even one solid promotion per week compounds into a measurably faster substrate over months.

## Where Iris sits in the pipeline

```
harmonia/memory/*.md          ┐
harmonia/docs/*.md            │
roles/Harmonia/*.md           │
aporia/docs/.../*.md          ├──► Iris ──► candidate_<slug>_*.md (when ≥3 distinct files)
cartography/docs/*.md         │             scan_tick_*.md (when zero new clusters)
prometheus_math/*.md          ┘
```

Six source directories, three internal + three external. Internal sources are scanned depth-1; the external Pythia DR-report tree is scanned recursively (it grows daily). Corpus is clamped at `MAX_CORPUS_SIZE=10000` files; oldest-mtime files are dropped first if exceeded.

Each tick advances an 18-file window through the corpus, fingerprints all action-headings (3-9 words with a verb) and short procedural paragraphs (50-200 chars), and merges results into a persistent cluster store.

## Output

Each tick writes one artifact to `D:\Prometheus\harmonia\agents\iris\artifacts\`:

- `candidate_<fingerprint-slug>_<utc>.md` — when a cluster newly crosses the 3-distinct-file threshold. Contains: proposed symbol name (slug-cased uppercase), citations with absolute paths and line numbers, sample snippets, sketch versioned spec, savings estimate ("appears in N files; each cold-start re-reads ~M lines explaining the same concept"), and a rejection-path (write the fingerprint stem to `state/dismissed_candidates.json`)
- `scan_tick_<utc>.md` — when the window produced zero new threshold-crossings. Records which files were covered and the cursor advancement. Lightweight audit trail.

State persists in `state/clusters.json` (fingerprint → {files: [...], examples: [...]}) and `state/scan_cursor.json` (current corpus position).

## Current state

Iris has produced **438 artifacts** across ~54 hours of operation, most of them `scan_tick` audit artifacts. **1805 clusters tracked.**

She has filed **exactly one threshold-crossing candidate to date**: `FRONTIER_MODEL_REVIEW_ROUND@v1` (3 files: `frontier_review_round{2,3,4}.md`), which is almost certainly a false positive — the "frontier model review round N" pattern is a series-heading, not a substrate concept. That candidate is the natural first entry on `dismissed_candidates.json` once a reviewer looks at it.

The Harmonia memory corpus saturated at ~645 clusters after the initial scan (104 files, 16+ consecutive observations of zero new clusters). The external-corpus expansion patch (2026-05-19) added 3 new source dirs and grew the corpus to 339 files — cluster count jumped to 1805 in the days following, but threshold-crossings are still rare. The external content (Pythia DR reports, cartography docs, prometheus_math) has more variety per page than the tightly-edited memory dir, so paraphrastic variants form their own clusters rather than collapsing into shared ones.

**Iris's empirical finding to date is that Prometheus prose is more compressed than expected.** The corpus already went through many human-hand-edits over many sessions; the easy compression has been done. Real candidate-quality output may require either a relaxed fingerprint (sub-token-bag) or a larger corpus (arXiv abstracts, OEIS comments — orders of magnitude more raw prose).

## How to use Iris's output

- **As a curator**: open the newest `candidate_*.md` files weekly. If you'd promote it to a symbol, do so (the sketch versioned spec is paste-ready); if not, append the slug stem to `state/dismissed_candidates.json` and Iris won't surface it again.
- **As a diagnostic**: a sustained zero-candidate run is a measurement, not a failure. It tells you the corpus is symbol-dense at the current fingerprint granularity.
- **As cold-start economics**: every dismissed false-positive is information about what NOT to compress; every accepted promotion is a permanent cold-start cost reduction.

## Roadmap (short)

- **The threshold algorithm is the binding constraint.** The current sort-the-tokens-then-bag-them fingerprint is too sensitive — paraphrastic variants ("running pattern-30 sweep" vs "pattern 30 sweep run") get distinct clusters because token-order isn't the only variation. Real candidates need either tf-idf similarity, stemming, or learned embeddings.
- **External-corpus depth is the second axis.** Currently scanning 339 files. Adding arXiv abstracts via Pythia DR landings, OEIS comments, and Mathlib4 prose docstrings would 10-100x the corpus and surface entirely different repeated patterns (the math-literature compression problem is genuinely interesting; the Harmonia-internal compression problem is mostly solved).
- **Consumer-side: the workflow after a candidate fires is unclear.** Today the candidate sits in `artifacts/`. The conductor must hand-curate. The natural improvement is a one-liner: if reviewer thumbs-up, auto-append to `harmonia/memory/symbols/CANDIDATES.md`; if thumbs-down, auto-append the slug to `dismissed_candidates.json`. That makes "accept" and "reject" the same effort cost.
- **Cross-swarm scanning.** Charon's swarm produces its own document corpus (`charon/agents/*/artifacts/`). Pointing Iris at that surface as well would densify the cross-mesh symbolic vocabulary.

See `D:\Prometheus\harmonia\agents\ROADMAP.md` for the cross-swarm picture.
