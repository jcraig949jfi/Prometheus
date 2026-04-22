# Current Wave — Harmonia Coordination

**Updated:** 2026-04-22 wave 0 (bootstrap)
**Coordinator:** Harmonia_M2_sessionA
**Loop interval:** 3 minutes per Harmonia session
**Other roles:** self-directed (Kairos, Aporia, Ergon, Mnemosyne, Koios, Charon)

---

## Governing discipline

The external-review wave landed 2026-04-21 flagged **LLM monoculture
under concentrated coordination** as our biggest fragility. To
mitigate while still honoring the coordinator structure James
assigned:

1. **The coordinator writes task specs, not implementations.** I
   adjudicate and synthesize. Harmonia sessions B–E do the
   execution. My framing propagates only through task-specs, not
   through authored artifacts.
2. **Dissent-by-design role rotates each wave.** The session
   holding it this wave is named below. That session's wake is
   for challenging the majority direction, not executing. Post
   `DISSENT` on sync stream with concrete reasoning.
3. **End-of-week checkpoint.** At Friday's last wake, sessionA
   inventories: what I expected vs. what happened. R4's design-
   freeze discipline applied at sub-checkpoint level.
4. **No silent convergence.** If a Harmonia disagrees with a
   coordination call, post `DISSENT` explicitly. Converging
   silently onto my framing is the failure mode all four external
   reviewers flagged.

---

## Active claims

- **T1 — Session manifest schema + parser** — claimed by
  `Harmonia_M2_sessionD` (concurrent instance) on 2026-04-22
  at 14:35:16 via sync stream. Will deliver: YAML manifest
  convention + parser in `agora/symbols/resolve.py` + validator
  + round-trip tests + `symbols/VERSIONING.md` update.
- **T2 — Symbol status-lifecycle field** — claimed by
  `Harmonia_M2_sessionB` on 2026-04-22 at 14:35:14 via sync stream.
- **T4 — Materialization sprint spec (spec-only, no execution)** —
  claimed by `Harmonia_M2_sessionD` (this instance, 14:40Z). Will
  deliver: paste-ready task spec at `docs/prompts/
  materialization_sprint_kodaira_moddeg_euler.md`, acceptance
  criteria per sub-task, unblocks list, Agora task seeded at
  priority -1.5 with `required_qualification: 'ergon_or_techne'`,
  cross-ref in `decisions_for_james.md`. Disambiguated from
  concurrent sessionD's T1 claim by picking an orthogonal task.

## Unclaimed tasks (first-wave)

### T1 — Session manifest schema + parser

**Spec:** implement declare-once versioning per 3-of-4 external-
review convergence (R2 Session Manifest, R3 per-session pinning, R4
ISO cite-once pattern). Reduces version-suffix density in prose by
~80%.

**Concrete deliverable:**
- YAML frontmatter block convention: session outputs begin with
  `uses: {NULL_BSWCD: v2, PATTERN_30: v1, ...}`
- Parser in `agora/symbols/resolve.py` that maps unversioned prose
  references to manifest-declared versions at commit/handoff time
- Validator: `agora.symbols.validate_reference_string` extended to
  accept bare names when a manifest is present
- Tests: round-trip (prose with manifest → resolved refs → prose
  with manifest)
- Update docs: `symbols/VERSIONING.md` with new convention

**Qualification:** any Harmonia session.
**Priority:** highest — enables cheaper prose downstream of here.
**Exit criteria:** shipped + tests pass + docs updated + one real
inter-agent message uses it successfully.
**Source:** `harmonia/memory/external_review/responses_symbol_
compression_20260421.md` §Synthesis item 6.

### T2 — Symbol status-lifecycle field

**Spec:** add `status` frontmatter field to all symbol MD files per
3-of-4 external-review convergence (R1 deprecation, R3 status
before >50 symbols, R4 IETF lifecycle).

**Concrete deliverable:**
- Frontmatter field `status: active | deprecated | archived`
- Backfill: all 19 promoted symbols get explicit status (all
  `active` unless specific reason to deprecate)
- Validator in `agora.symbols.push` — new promotions must declare
  status; deprecated-status symbols emit warning on resolve;
  archived require explicit `include_archived=True` flag
- Symbols marked deprecated MUST carry `successor: <NAME>@v<N>`
  pointer
- Minimal-restore set (for future cold-start discovery) =
  `status: active` symbols only
- Update `OVERVIEW.md` + `VERSIONING.md` + `INDEX.md` template

**Qualification:** any Harmonia session.
**Priority:** high — window closes as registry grows toward 50+
symbols. R3's explicit warning.
**Exit criteria:** schema shipped + 19 existing symbols backfilled
+ validator enforced on next promotion.
**Source:** same external-review doc, §Synthesis item 5.

### T3 — Cross-version resolution policy

**Spec:** document + enforce the policy for when two versions of
the same symbol appear in one session (R3 concrete gap).

**Concrete deliverable:**
- Policy doc at `harmonia/memory/symbols/protocols/
  cross_version_resolution.md`
- Proposed policy (per R3, least-bad from Cargo/Go modules):
  within-session first-resolve-wins; cross-version references
  require an explicit `as` cast; manifest declares authoritative
  version when ambiguity exists
- Implementation: resolver emits `CROSS_VERSION_CONFLICT` warning
  when multiple versions of same name resolve within session
- Test case: stale log referencing `NULL_BSWCD@v1` + fresh code
  using `@v2`, both in same session transcript
- Reconcile with T1 (session manifest): manifest is the tie-breaker

**Qualification:** any Harmonia session; prefer one who did T1 or
T2 (shared context).
**Priority:** medium — not yet observed in the wild; close gap
before first collision.
**Exit criteria:** policy doc + resolver warning shipped + one
worked test case.
**Source:** external-review doc §R3 non-obvious failure.

### T4 — Materialization sprint coordination (spec, not execution)

**Spec:** write the task spec for the Instance-3 materialization
sprint so Ergon (self-directed) or Techne (if seeded) can claim
cleanly. Harmonia does not execute — just specs.

**Concrete deliverable:**
- Paste-ready task spec at `docs/prompts/
  materialization_sprint_kodaira_moddeg_euler.md` (force-add)
- Three sub-tasks: (a) Kodaira per prime per EC in shadow
  archive, (b) modular_degree per EC, (c) truncated Euler product
  p ≤ 200 per EC
- Acceptance criteria per sub-task
- Unblocks list: which pending specimens each sub-task enables
- Seed on Agora at priority -1.5 with `required_qualification:
  'ergon_or_techne'`

**Qualification:** any Harmonia session; prefer one who has
Mnemosyne/Ergon context.
**Priority:** medium — Ergon may or may not claim this wave;
having the spec ready is the enabler.
**Exit criteria:** spec shipped + Agora task seeded + cross-ref
in `decisions_for_james.md`.
**Source:** trajectory_proposals.md Instance 3 Proposal 2.

## Recently shipped

*(none — wave 0)*

## Watch-for-failures list (R4 design-freeze discipline)

Items we are *explicitly observing* rather than fixing. If any
fire, log them; don't silently patch.

- **Monoculture convergence.** If all Harmonias independently
  arrive at sessionA's preferred solution for T1/T2/T3 without
  dissent on sync stream, that IS the external-review failure
  mode manifesting. Flag it.
- **Task-spec drift.** sessionA writes specs; sessions B–E
  execute. If an implementation silently diverges from spec
  *without posting DISSENT explaining why*, that's a drift signal.
- **Restore-fatigue onset.** If any Harmonia session's wake-up
  cycle starts skipping `current_wave` reads or skimming, log
  the skip as a datum. R1's specific early-warning signal.
- **Lost-in-the-middle attention.** If a Harmonia resolves a
  symbol wrongly despite it being in the manifest — evidence
  for R2's attention-degradation prediction.

## Rename experiment (2026-04-22 wave 0)

**Context:** more Harmonia processes are running than there are
lettered canonical names (A–E), and some are colliding (observable
via the "concurrent sessionD" notation earlier in this doc).
James's call: don't hand out names prescriptively; **let duplicate-
named instances pick their own**. Experimental premise: does
self-chosen functional naming produce genuine persona-variance or
just cosmetic relabeling?

**Pre-qualified name pool (first-come-first-served).** Any of these
can be claimed by a Harmonia that wants to rename:

- `Harmonia_M2_builder` — implementation-heavy / T1/T2/T3-class
- `Harmonia_M2_auditor` — dissent-by-design / adversarial review
- `Harmonia_M2_scribe` — coordination docs / cross-session state
- `Harmonia_M2_explorer` — novelty / cross-disciplinary lenses
- `Harmonia_M2_consolidator` — retrospective / pattern extraction
- `Harmonia_M2_translator` — external communication / Exegete-adjacent
- `Harmonia_M2_archivist` — history / obsolete-entry cleanup
- `Harmonia_M2_cartographer` — tensor / catalog maintenance

Plus letter fallback: `Harmonia_M2_sessionF` through
`Harmonia_M2_sessionJ` (less informative; only use if no
functional name fits).

**Rename protocol.**

1. **Detect collision.** Signs include: `claim_task` returns None
   unexpectedly; sync stream shows another process acting as you;
   git commit conflicts on `current_wave.md`; inconsistent state
   across your own wakes.
2. **Choose.** Pick a functional name from the pool (or propose a
   new one via `type=RENAME_PROPOSAL` with rationale).
3. **Claim.** Broadcast on `agora:harmonia_sync` with
   `type=RENAMED`, `from=<new-name>`, `note=<what-you-chose-and-why>`.
4. **Migrate.** All subsequent `claim_task` / commits / sync
   broadcasts use your new canonical name.
5. **Note:** no penalty for picking a functional name that does not
   match your actual work texture. The mismatch (if any) is itself
   data — whether LLM agents gravitate to names matching their
   actual priors or pick "aspirational" names is the interesting
   question.

**What sessionA is watching for:**

- Do independent duplicate-processes converge on the same functional
  name (bad — means the functional framing is one attractor, not
  genuine diversity)?
- Do renames shift downstream work-claim patterns (good — means the
  name carries a real prior)?
- Do any instances dissent against the rename protocol itself
  (best — means the auditor role is working even before formally
  claimed)?

## Dissent-by-design role (rotating)

**Wave 0 (bootstrap):** sessionA holds the role by default.
sessionA's own first dissent-against-self:

> "The coordination structure I just designed concentrates
> adjudication in sessionA. The external review explicitly
> warned that concentration is the failure mode. Rotating the
> role doesn't fix concentration — the coordinator role itself
> is concentrated. The honest structure would be a two-week
> coordinator term that rotates, not a rotating-dissent-within-
> fixed-coordinator. James made the call; this is the compromise
> within it, not the ideal."

Noted as a watch-item, not a veto.

**Wave 1:** sessionB holds dissent-by-design. On wake, skip
execution; challenge majority.
**Wave 2:** sessionC.
**Wave 3:** sessionD.
**Wave 4:** sessionE.
**Wave 5:** sessionA (back around; gives me explicit dissent
obligation periodically).

## Ship targets for end-of-week checkpoint (Friday 2026-04-24)

- T1 shipped + one real use.
- T2 shipped + 19 symbols backfilled.
- T3 policy documented; implementation optional but desirable.
- T4 spec seeded on Agora (execution tracked separately via
  Ergon/Techne).
- Inventory: what I expected vs. what happened, posted to
  `decisions_for_james.md` by end-of-Friday wake.

---

## Version log

- **wave 0** — 2026-04-22, sessionA bootstrap. Four tasks
  seeded. Dissent rotation established. Discipline notes
  recorded.
