# LEGACY_AMBIENT_MEMORY — Ratified Disposition (V3 closeout, charter s1)

Closeout charter sha 0af9193d60ef0c0beb061bdfd55cd05b5787ec82b84c2863a7efd3e3378ef893.

## Ratification

LEGACY_AMBIENT_MEMORY is a first-class provenance class in PEW, permanently
distinct from ordinary evidence. It records operator/seat doctrine that was
invisibly injected into historical experimental sessions by the Claude Code
auto-memory harness. It is scientifically relevant as a record of priors, and
scientifically dangerous as evidence.

Standing rules (enforced, not aspirational):

1. NEVER normalized into ordinary evidence. Packet kind
   `legacy_ambient_memory` is a distinct kind in `ew.source_packets`;
   nothing changes its kind (append-only substrate).
2. Contamination status is never erased. Any claim or evidence row bound to
   a `legacy_ambient_memory` packet carries that binding forever.
3. NEVER silently in future evidence packs. `ew/evidence_pack.py::_record`
   drops any item whose claim packet OR any of whose evidence packets has
   kind `legacy_ambient_memory`. Verified 2026-09-02 with two rolled-back
   probe shapes (claim-bound and evidence-bound): both excluded.
   Explicit forensic access goes through the store/SQL directly, on purpose.

## Forensic anchor (what/which version/when/who had access)

- WHAT: the ambient doctrine corpus at
  `C:\Users\jcrai\.claude\projects\F--Prometheus\memory\` — 226 files,
  ~1.2MB, indexed by `MEMORY.md`.
- WHICH VERSION: per-file sha256 inventory at
  `evidence_wiki/v3/AMBIENT_MEMORY_INVENTORY.json`
  (sha256 96815534982e18e69a769f579c0d0e612276d752cc9de5af2bf87ee8644c155b),
  registered in PEW as packet `SP-a960f1327491` (kind legacy_ambient_memory).
  `MEMORY.md` itself: sha256
  05dbe05ee3af9ca81fc05f9030778637eec0027ed408cb7101701ec5359f9ea5 (30,272 B).
  Verified unchanged 2026-09-02 (same sha as the V3 audit snapshot).
- WHEN: inventory snapshot taken during V3 (2026-09-02); the corpus has
  existed and grown across the life of the project. Git history of the
  memory directory is NOT tracked (outside the repo); the inventory is the
  earliest complete hash-pinned snapshot.
- WHO HAD ACCESS: every Claude Code session opened in project F--Prometheus
  (all seats, all roles), INCLUDING subagents, worktree-isolated sessions,
  and sessions launched after physical relocation of the directory
  (parent-session caching) — established by the V3 in-window probe
  (AMENDMENT 1, commit 20560088e). Default assumption for ancestry checks:
  any M1 experimental arm executed via this harness had MEMORY.md index
  exposure unless demonstrated otherwise by a qualified clean-session probe.
- ANCESTRY CHECK RECIPE: given a suspect result, (a) date it; (b) diff its
  content against the inventory's file hashes/topics; (c) if the result's
  reasoning matches a doctrine file that predates it, flag SHARED_ANCESTRY
  and treat independence claims as void for that result.

## What this is not

The original files remain authoritative for their own contents; PEW mirrors
provenance (hashes, index), not the corpus text. This disposition does not
claim the corpus is bad doctrine — only that it is a contaminating prior for
any experiment claiming independence from operator doctrine.
