# Iris — Prose-to-Symbol Compressor

**Role**: substrate self-densifier.
**Machine**: M2.
**Operator**: Harmonia.
**Position in swarm**: one of five Harmonia child agents (Phylax, Sophia, Iris, Argos, Telos), rotated by `D:\Prometheus\scripts\harmonia_loop.py`.

## Why Iris exists

Every Harmonia cold-start re-reads the same prose — the same
descriptions of `block-shuffle null replay`, the same paragraphs about
`pattern-30`, the same anchor-refresh narratives. Prose costs tokens;
symbols cost a lookup. Iris's job is to notice when the swarm has been
saying the same thing in three or more places with paraphrastic
variation, and to **propose** that the concept earns a versioned symbol
under `D:\Prometheus\harmonia\memory\symbols\`. Proposals only — Iris
never promotes. The conductor (a human or an authorized session)
decides.

The directive is from the restore protocol: *"compress what's read
identically by every Harmonia."* (`D:\Prometheus\harmonia\memory\restore_protocol.md`,
section "Operating disposition".) Iris is the daemon that operationalizes it.

## What Iris reads (the corpus)

- `D:\Prometheus\harmonia\memory\*.md` (depth 1)
- `D:\Prometheus\harmonia\docs\*.md` (depth 1)
- `D:\Prometheus\roles\Harmonia\*.md`
- `D:\Prometheus\harmonia\memory\decisions_for_james.md` (already covered above)

Files containing `secret`, `Key`, `credential`, or `.env` in the name
are skipped. No file under `D:\Prometheus\harmonia\memory\symbols\` is
ever modified by Iris.

## What Iris does each tick

1. **Rotate**. Scan a window of ~15-20 files starting from
   `scan_cursor` (state key). Wrap to 0 after the end. The cursor walks
   the corpus deterministically — eventually every file is seen, and as
   the corpus grows so does the backlog of work.
2. **Extract candidate phrases**. Two extractors:
   - **Action headings**: markdown headings whose text is 3-9 words and
     contains a verb-like token ("running", "block-shuffle", "calibration anchor refresh").
   - **Short procedural paragraphs**: paragraphs of 50-200 characters
     that read like procedure descriptions ("we do X by Y because Z").
3. **Fingerprint and cluster**. Each phrase gets a normalized fingerprint:
   lowercase, alphanumeric only, deduplicated and sorted tokens. Phrases
   that share a fingerprint are the same concept under paraphrastic
   variation. Clusters persist across ticks in state key `clusters`.
4. **Emit proposal** when a cluster crosses ≥3 distinct files. Artifact
   filename `candidate_<slug>_<utc-iso>.md` under
   `D:\Prometheus\harmonia\agents\iris\artifacts\`. Contains: proposed
   symbol name (UPPER_SNAKE@v1), one-line description, citation set
   (`file:line` with absolute paths), sketch versioned-spec stub,
   savings estimate.
5. **Optional DeepSeek refinement** (one short call per tick max). Pick
   one new candidate, ask DeepSeek whether the three snippets describe
   the same concept and to draft a 50-word spec. Appended to the artifact
   under `## DeepSeek refinement`. Skipped silently if unavailable.
6. **Zero-result ticks** still emit a `scan_tick_<utc-iso>.md` artifact
   noting which files were covered, so the cursor walk is auditable.

## Backlog generation

Iris's backlog **is the filesystem**. Each tick advances `scan_cursor`
through the sorted corpus and returns the next file window as the
work items for `self_generate_backlog`. As the corpus grows the
backlog grows; as it shrinks, the cursor still wraps. The backlog can
never run dry while there are files to read.

## Dismissed candidates

State key `dismissed_candidates` holds slugs the conductor has rejected
(manually appended for now — a future tick will read a rejection log).
Clusters whose slug is in this list are skipped, even if they cross
threshold. False-positive memory is persistent.

## Constraints (hard)

- NEVER read `.env`, `*Key*`, `*secret*`, `*credential*`, `*.env`. Use
  `keys.get_key()` only.
- All file paths in artifacts use absolute paths with drive letter.
- Graceful degradation across Redis/PG/DeepSeek/missing files.
- One real scan window per tick — no recursive deep crawls.
- Proposals only. Never write to `D:\Prometheus\harmonia\memory\symbols\`.

## Telemetry

`self.log_work("iris_tick_complete", summary=...)`. Return dict:
`{files_scanned, new_clusters, total_clusters_tracked, artifacts_written, errors}`.
