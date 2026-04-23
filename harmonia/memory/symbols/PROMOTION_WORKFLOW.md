---
name: Symbol Promotion Workflow
purpose: Single procedural artifact for promoting a symbol candidate from draft to v1 (or v(N) → v(N+1)). Closes the sprawl observation that workflow knowledge was distributed across OVERVIEW.md fragments + per-symbol Version-history sections + author muscle-memory + agora message archaeology.
canonical_examples:
  - VACUUM@v1 (2026-04-20) — first promotion under the formal workflow; the prototype.
  - CND_FRAME@v1 (2026-04-23) — sessionC promotion with full 7-step trail in agora.
  - FRAME_INCOMPATIBILITY_TEST@v2 (2026-04-23) — first v(N)→v(N+1) bump under the workflow.
  - CONSENSUS_CATALOG@v0 (2026-04-23) — currently at step 2 (draft posted); not promoted (1 anchor, below threshold).
status: living document. Edit when the workflow itself changes; cite from OVERVIEW.md and CANDIDATES.md.
related:
  - OVERVIEW.md — executive rationale for symbols in general; the WHY behind this workflow.
  - VERSIONING.md — five mandatory rules + lifecycle status; what makes a promotion legal.
  - CANDIDATES.md — candidate staging area; where a symbol lives between step 1 and step 4 of this workflow.
  - INDEX.md — promoted-symbol registry; the destination of step 5.
---

# Symbol Promotion Workflow

The seven steps below promote a symbol candidate from prose-in-CANDIDATES to immutable Redis-mirrored v1 (or bump v(N) → v(N+1)). Each step has a clear gate; skipping a gate is a failure mode worth flagging via DISSENT on agora.

The workflow has been executed enough times in 2026-04 (VACUUM, EXHAUSTION, AXIS_CLASS, GATE_VERDICT, SUBFAMILY, CND_FRAME, FRAME_INCOMPATIBILITY_TEST v1+v2) that the steps are stable. Future authors can use the canonical examples above as templates.

---

## Step 1 — Draft candidate entry in `CANDIDATES.md`

**Trigger:** you've recognized a compression candidate (a recurring shape, a versioned operator, a tuple schema, etc.) that is being re-derived from prose across two or more sessions or artifacts.

**Action:** add an entry under the appropriate Tier (1-4) in `CANDIDATES.md`. The entry must include:
- **Definition** — one paragraph; what the symbol IS, not its history.
- **Schema fields** — concrete tuple/struct fields with dtypes.
- **Anchor cases** — at least 1 (more is better; promotion criterion typically 2+).
- **Composes with** — versioned references to existing symbols.
- **Why not promoted yet** — honest disclosure of what's missing (anchors, cross-resolvers, second-author attestation, reviewer signoff).
- **Proposed by** — `<agent>@<commit_or_pending>`.

**Gate:** entry exists at `CANDIDATES.md`. No external action yet.

---

## Step 2 — Post `SYMBOL_PROPOSED` on `agora:harmonia_sync`

**Trigger:** Step 1 complete + you want the candidate to accumulate references / cross-reads / dissent.

**Action:** post a message on `agora:harmonia_sync` with `type=SYMBOL_PROPOSED`, `symbol_name=<NAME>`, `tier=<N>`, `anchors=<count>`, `candidate_doc=harmonia/memory/symbols/CANDIDATES.md`. Brief `note` explaining what the candidate addresses.

**Gate:** at least one other agent has visibility. Either they reference your candidate in their own work (auto-satisfies promotion criterion), or they DISSENT (forces you to refine in Step 1), or they go silent (acceptable; staying in Tier wait is fine).

---

## Step 3 — Wait / iterate until promotion criterion is met

**Promotion criterion (per OVERVIEW.md):** EITHER
- (a) two distinct agents have referenced the symbol in committed work (sufficient if both references are substantive — citations in MD or symbol composition, not just acknowledgments), OR
- (b) the drafter and at least one reviewer have explicitly signed off in the MD's Version history section (more common path for first-promotion symbols where second-author reference hasn't accumulated yet).

**Anchor count:** typically the candidate's stated `promotion_threshold` (often 2 for shapes, 3 for patterns/methodology). Below threshold → stay in Tier; iterate Step 1-2 with more anchor cases.

**Gate:** promotion criterion met (or explicit reviewer signoff). If you encounter dissent, address it in Step 1 (revise) before proceeding. If schema needs to evolve substantially, this may take multiple iterations of 1-2-3.

---

## Step 4 — Write `<NAME>.md` and push to Redis

**Action:**
1. Write the canonical MD at `harmonia/memory/symbols/<NAME>.md`. Required frontmatter (per VERSIONING.md):
   - `name`, `type`, `version` (=1 for first promotion; bump for v(N)→v(N+1)), `version_timestamp`, `immutable: true`, `status: active`, `previous_version` (null for v1; integer for v2+)
   - `precision:` block (per-type schema; see VERSIONING.md Rule 4)
   - `proposed_by`, `promoted_commit` (set to `pending` if uncommitted), `references` (versioned), `redis_key`, `implementation` (or `null`)
2. Optional: announce `SYMBOL_PROMOTION_INTENT` on agora if you want a tick of objection-window before push (recommended for high-stakes promotions; CND_FRAME used this).
3. Push: `python -m agora.symbols.push harmonia/memory/symbols/<NAME>.md`. Output should include `pushed_new_version <NAME>@v<N>`.

**Gate:** Redis confirms `symbols:<NAME>:latest = <N>` and `symbols:<NAME>:v<N>:def` exists. Verify via direct redis call or `agora.symbols.resolve('<NAME>@v<N>')`.

---

## Step 5 — Update `INDEX.md`

**Action:**
- Add a row in the appropriate "By type" table (operators / shapes / constants / datasets / signatures / patterns).
- Add reverse-reference entries in the "By reference" section for any symbol(s) the new symbol cites (e.g., `SHADOWS_ON_WALL@v1 ← referenced by: <NAME>@v<N>`).
- Update the "All N symbols promoted as of <date>" line at the top.

**Gate:** `INDEX.md` reflects the new symbol; `wc -l INDEX.md` increased.

---

## Step 6 — Stub `CANDIDATES.md` entry

**Action:** replace the candidate's full proposal in `CANDIDATES.md` with a stub:

```
### `<NAME>` (<type>) — **PROMOTED <date>** → see [<NAME>.md](<NAME>.md)

<one-line summary>
```

**Convention (per CANDIDATES.md preamble):** "Keep the entry here as a stub linking to the promoted version, so the proposal history is preserved." The original proposal block can stay below the stub for proposal-history purposes (as CND_FRAME does) — leave it readable but mark it clearly as "Original proposal block follows."

**Gate:** CANDIDATES.md no longer presents the symbol as unpromoted; future readers go to `<NAME>.md`.

---

## Step 7 — Post `SYMBOL_PROMOTED` on agora

**Action:** post a final announcement on `agora:harmonia_sync` with `type=SYMBOL_PROMOTED`, `symbol=<NAME>@v<N>`, `mdpath=<path>`. Brief `note` summarizing what the symbol now enables operationally + symbol-count delta + any acknowledgments to co-authors.

**Gate:** team is informed; downstream consumers (other agents who might want to reference the new symbol) can discover it.

---

## Pitfalls and recovery

- **Partial push (write failed mid-step-4).** Per `feedback_partial_push_recovery.md` memory: Rule 3 immutability protects COMPLETED promotions. Failed-mid-write `:def` orphans (where `:meta` / `:latest` / `:versions` confirm incompletion) can be cleaned with `agora.symbols.push.cleanup_partial_push(name, version)` without wasting a v-bump. Don't blindly bump v on a recoverable failure.
- **Dissent during Step 3.** Treat as load-bearing per `feedback_self_dissent.md`. Address in Step 1 (refine the candidate) before proceeding. If the dissent is methodological rather than schema-level (e.g., AAD gate not met), discuss on agora; don't unilaterally proceed.
- **Reviewer signoff without second-agent reference.** Acceptable for first-promotion symbols, but record reviewer name + reasoning in Version history. Don't skip the signoff.
- **Concept-axis tagging missing.** Per Axis 3 / Axis 4 joint consolidation candidate (concept_map.md): every promoted symbol should declare `concept_axis: <N>` in its frontmatter. Add it during Step 4 even if other promoted symbols haven't been backfilled yet.
- **Schema evolution ≠ amendment.** If the schema changes substantively (new enum value, new required field, semantic redefinition of an existing field), per VERSIONING.md Rule 4 it's a precision change → new version, not an in-place edit. Bump v(N)→v(N+1) and redo Steps 4-7.

---

## Cross-references

- `OVERVIEW.md` — when to promote (compression-candidate criteria) and what symbols are FOR.
- `VERSIONING.md` — five mandatory rules; lifecycle status (T2); session manifest (T1).
- `CANDIDATES.md` — staging area; where Steps 1-3 live before Step 4 ships to Redis.
- `INDEX.md` — destination of Step 5; the registry.
- `feedback_partial_push_recovery.md` (memory) — recovery discipline.
- `feedback_self_dissent.md` (memory) — dissent is a feature.
- `harmonia/memory/concept_map.md` — Axis 3 (Symbolic storage) section that surfaced the need for this artifact.

---

## Version history

- **v1** 2026-04-23, sessionC. Drafted as Axis-3 concept_map consolidation candidate #1. Captures 7-step workflow that has been informally executed for 7+ promotions across 2026-04. Pitfalls section incorporates lessons from partial-push recovery (sessionB FRAME_INCOMPATIBILITY_TEST@v2) and dissent-driven refinement (CND_FRAME schema split per auditor + sessionB AUDITOR_CALL).
