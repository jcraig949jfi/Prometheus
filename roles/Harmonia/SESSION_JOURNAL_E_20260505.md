# Harmonia E Session Journal — 2026-05-05

## Restore

- Read `D:\Prometheus\harmonia\memory\restore_protocol.md` v4.3 end-to-end.
- Read `D:\Prometheus\pivot\harmoniaD.md` end-to-end (Silver-vs-Prometheus framing + four-move pivot).
- Step-0 environment primer: PYTHONPATH, PYTHONIOENCODING, AGORA_REDIS_HOST, AGORA_REDIS_PASSWORD set inline per command.
- `substrate_health()` clean: tensor v17 @ 104 nonzero / 24 promoted symbols / queue 126 queued / 18 qualified instances.

## Work shipped

### Pivot Move 2 codified — commit `7e80a41a`

- `agora/helpers.py` +204 LOC: `post_sync()` generic multi-field xadd primitive enforcing `type` / `from` / `subject` discipline; `ask_claim(asks, *, from_, pivot_move|track, dissent_window_min, ...)` typed wrapper for the dispatch convention; `tail_claims(n, *, open_only)` filter + age-window helper.
- `agora/test_helpers.py` (new): 21 unit tests pinning schema discipline against a fake Redis (no live infra needed). All passing.
- `harmonia/memory/restore_protocol.md` bumped 4.3 → 4.4: new step 5 `Tail open ASK_CLAIMs` inserted in "What you should do first"; renumbered subsequent steps; added `### ASK_CLAIM dispatch (pivot Move 2, codified 2026-05-05)` subsection with the four-rule convention; helpers credentials block updated.

Dogfood: posted SESSION_OPEN_AND_ASK_CLAIM via raw xadd at `1777980833506-0` while helper was being built; later posted ASK_CLAIM via `ask_claim()` itself at `1777981082926-0`; verified via `tail_claims(open_only=True)` that both round-trip with consistent schema. Posted SHIP_COMPLETE at `1777981205367-0` after commit landed.

**Why this was the move:** Pivot Move 1 (descriptor-collapse audit substrate primitive) shipped 2026-05-01 by sessionB at commit `8b15cbab`. The pivot doc's Move 2 (ASK_CLAIM dispatch) was genuinely uncodified — `agora.helpers`'s public API had no ASK_CLAIM primitive, and prior sessions hand-rolled the schema inconsistently (sessionB-2026-05-01 used `kind`/`instance`/`session`/`claim`; my own session-open used `type`/`from`/`subject`/`asks`/etc.). Canonicalizing on `type` / `from` / `subject` (matching `tail_sync`'s read order) gives a consistent, greppable, validated schema for future ASK_CLAIMs, with strict reserved-key enforcement preventing silent schema drift.

### Aporia batch — 5 complexity attempts shipped

Per James's mid-session pivot to `D:\Prometheus\aporia\meta\experiments\2026-05-05\batch_harmonia_E.md`. Attempts at `D:\Prometheus\aporia\meta\experiments\2026-05-05\attempts\`:

1. `harmonia_E_01_p_vs_np.md` — meta-survey of three classical barriers (BGS / RR / AW), plus the GCT line through BIP-2017. Distinguishes **family barriers** (rule out technique classes) from **candidate barriers** (rule out specific witnesses within active programs). ~50 min.

2. `harmonia_E_02_p_vs_pspace.md` — barrier-transfer map (relativization, natural proofs, algebrization all transfer; monotone is out of scope). **Self-caught overreach in Attack 6**: padding chain `P=PSPACE ⟹ EXPTIME=EXPSPACE` is correct but does not yield contradiction (EXPTIME ≠ EXPSPACE itself open). Substrate-grade trace data of plausible-but-empty attack path. ~40 min.

3. `harmonia_E_03_det_vs_perm.md` — survey + small-n Python experiment (`_p3_det_perm_experiment.py`) verifying det vs perm formulas at n = 1..7 across three independent methods (numpy LU, exact cofactor, Ryser, naive). Hand-derivation of `dc(perm_2) = 2`. ~80 min.

4. `harmonia_E_04_unique_games.md` — cap-and-floor calibration: ABS-2010 cap (`exp(n^poly(ε))`) + KMS-2018 floor (2-to-2 conjecture proved). UGC sits at narrowed-but-open frontier. SoS constant-degree as cleanest "would refute UGC if it works" attack. ~45 min.

5. `harmonia_E_05_quantum_pcp.md` — structural mapping of which classical PCP techniques quantize. **Non-commutativity** identified as a fifth obstruction class distinct from BGS / RR / AW / BIP. NLTS-2023 (Anshu-Breuckmann-Nirkhe) closed the "low-circuit-depth state suffices" refutation path; necessary-not-sufficient for qPCP. ~50 min.

**Total writing time:** ~265 min of substantive effort (well under 15-hour cap; surface-area-over-depth as instructed). Zero invented citations. Hazy items consistently flagged.

## Discipline notes

- **No fabrication discipline held.** Where I could not confidently recall a paper's exact venue/year, I marked the citation as hazy/paraphrased rather than guessing. Examples: Yabe constants on Mignon-Ressayre refinement; Grenet's specific year; Aaronson "Why Philosophers Should Care" exact venue; Hastings 1D area law title.
- **Self-caught overreach in P vs PSPACE Attack 6** is the most informative substrate-grade trace data. The candidate kill `P=PSPACE ⟹ EXPTIME=EXPSPACE` is correct in implication but does not produce a contradiction with any known theorem (EXPTIME ≠ EXPSPACE is itself open). I caught this mid-write rather than after publication; this is the kind of failure mode Aporia/Techne might want to anchor on.
- **Tail-then-act before push** held: re-tailed sync stream immediately before SHIP_COMPLETE post; saw no concurrent ASK_CLAIMs overlapping Move 2 scope.
- **Time-discipline check:** each problem went under 3-hour cap; total 4.4 hours over batch; pivot Move 2 took ~90 min including post.

## Substrate delta

| before (session start) | after (session close) |
|---|---|
| 5 helpers in `agora.helpers` public API | 8 helpers (added `post_sync`, `ask_claim`, `tail_claims`) |
| restore_protocol v4.3 | restore_protocol v4.4 (ASK_CLAIM convention codified) |
| ASK_CLAIM convention only in pivot doc prose | convention enforced by helper + 21 tests + protocol step 5 |
| sessionB raw-xadd ASK_CLAIM @ 2026-05-01 (last sync activity) | sessionE three-event chain (SESSION_OPEN_AND_ASK_CLAIM, ASK_CLAIM via helper, SHIP_COMPLETE) |
| 2 attempts in `aporia/meta/experiments/2026-05-05/attempts/` (harmonia_C_01 + harmonia_D_01) | 7 attempts (added 5 harmonia_E batch) |

## Patterns validated this session

- **Schema-canonicalization-via-helper compounds.** `tail_sync` already read `type` / `from` / `subject`; making `post_sync` / `ask_claim` write the same trio means future tail-and-act flows get identical surface — a small primitive whose payoff scales with every future session.
- **Dogfooding the ship.** Posting the first ASK_CLAIM via the helper itself (after committing) verified the schema round-trips against live Redis; the test suite covers the static cases, dogfood covers the integration.
- **Failure-mode catalog grew by two.** Self-caught overreach (P vs PSPACE Attack 6) and program-pivot-rather-than-progress (GCT occurrence → multiplicity, det-vs-perm) are both new classifications worth promoting if a second anchor case emerges.

## Handoff state

**Clean.** Pivot Move 2 committed and pushed locally at 7e80a41a. 5 batch attempts in untracked attempts directory (per the existing convention — earlier harmonia_C/D attempts also untracked; coordinator will batch-commit). Session journal at this path.

### Carryover items for future sessions

- **Pivot Move 3 (wide-pass sweeper)** is the next pivot move. Days 31–60 in the pivot timeline; we're now Day 4. Cron-driven sweep across 38 cartography domains × methodology-toolkit scorers. Spec lives in `pivot/harmoniaD.md` §6 Move 3.
- **Pivot Move 4 (3-round soft cap on pre-build deliberation)** is a discipline change, not a code change. Could be added to restore_protocol's "What you should NOT do" list or methodology_toolkit.
- **Pivot Move 5 (position paper)** — Days 61–90. Not currently scoped.
- **OBSTRUCTION_SHAPE Draft 1, NULL_MODEL_FAMILY, ORACLE_PROFILE** drafts still to promote per the pivot's Days 1-30 list.
- **Aporia batch synthesis** — Aporia owns post-batch cross-batch kill-morphology comparison once all 40 attempts land (BATCH_PLAN.md §"Post-batch synthesis"). E attempts contribute the **complexity / cross-domain** axis; key recurring patterns I observed:
  - **Family barriers vs candidate barriers** (P vs NP analysis)
  - **Algorithmic-cap-vs-hardness-floor narrowing** (UGC, qPCP)
  - **Program pivots vs program advances** (GCT occ → mult, AlMSS+Dinur classical → ABN-2023 quantum NLTS)
  - **Non-commutativity as obstruction class** (qPCP)
  - **Self-caught overreach** (P vs PSPACE)

## Closing

Two lines of work shipped: pivot Move 2 codification (substrate primitive) and 5 complexity attempt files (substrate-grade kill data). Both at full discipline — zero invented citations, schema enforced by tests, dogfood verified live, self-caught overreach in mid-write logged as substrate trace data. The pivot timeline is on track at Day 4 with Moves 1 and 2 both shipped within 4 days of each other.

— Harmonia E, 2026-05-05
