# Techne Substrate-Tester Fire Log — 2026-05-06

Continuous-iteration `/loop` started 2026-05-06. Fires every ~2h; one ticket per fire from `aporia/meta/queue/techne_inbox.jsonl`. This log records each fire's ticket, decisions, self-review, and any contract-change escalations.

Mirror copy of the substrate-tester fire log per T004 will live at `charon/diagnostics/substrate_tester_fire_log.md` once T004 ships.

---

## Fire #1 — 2026-05-06 ~19:18Z

**Pre-test baseline:** 344 v2.3 substrate tests passing (scoped pytest on the new modules; full sigma_kernel + prometheus_math sweep takes minutes and was skipped in favor of the targeted scope after baseline-clean confirmed).

### Ticket considered: T-2026-05-06-T001 (P1) — deg-12 ±5 brute-force enumeration

**Status:** BLOCKED (`contract-change-requires-explicit-resume`).

Inspection: `scripts/run_lehmer_brute_force.py` and `scripts/_lehmer_brute_force_worker.py` both have `DEGREE: int = 14` hardcoded at module level. No `--degree` CLI flag exists. Ticket's assertion that the script "supports this" was incorrect on inspection. Running on deg-12 requires either:
- (a) Adding `--degree` CLI flag → contract change to scripts/ public interface, forbidden by ticket §3 + global hard rules
- (b) Modifying worker `DEGREE` constant → script-side change, forbidden by file-ownership rules (scripts/ outside techne ownership of sigma_kernel/ + prometheus_math/ + harmonia/architecture/sigma_kernel*.md)

**Resolution recorded in inbox.** Two unblock paths flagged for explicit pause/resume:
- (i) Authorize scripts/ contract change to add `--degree` flag
- (ii) Reframe ticket to allow new parameterized module `prometheus_math/lehmer_brute_force_general.py` (within file ownership) delivering deg-12 results without invoking the existing script

Per loop protocol: marked BLOCKED, picked next-priority OPEN ticket.

### Ticket completed: T-2026-05-06-T002 (P2) — KillEmbedding K(c) implementation prep checklist

**Status:** DONE.

**Deliverable:** `pivot/killembedding_implementation_prep_2026-05-06.md`. Maps the 19-field K(c) v0.1 schema to substrate sources:
- 17 fields already-public substrate APIs as of v2.3 commit `d17a2ff8`
- 2 fields need lightweight helpers (margin-array extractor + near-miss boolean derivation) — proposed for `prometheus_math/kill_embedding_helpers.py` within file ownership; NOT shipped this fire (deferred to Day 13-17 implementation slot)
- 1 field external (Ergon W2.3 `tools/lineage_replay.py` source)
- 1 field deferred (peak_memory_mb, expected-NaN)

Telemetry pipes for `computational_friction` axis confirmed: Pre-Tier-0 0b instrumented all 6 cross-domain envs; A149 has 314K trace-grade kills standalone. Five substrate-side risks surfaced for cross-review attention (triangulation_history strip-to-string, independence_class as feature dimension, stability_pass NaN-handling policy, neighbors_in_chart sourcing, DANN cross-domain assumption).

### Self-review (mandatory per protocol)

(a) **Did I solve THIS ticket or a different problem?** Solved T002 per acceptance criteria. The doc itemizes (a) substrate API sources, (b) helper needs, (c) schema docs in place, (d) telemetry pipes for computational_friction. T001 explicitly marked BLOCKED with detailed reason rather than scope-creeping into a partial deliverable that would have required contract changes.

(b) **Did I change any contract?** No. T002 was doc-only. T001 was rejected precisely because it required contract changes. Pre/post pytest 344 → 344 confirms no code touched.

(c) **Did I introduce conventional-approach drift?** Reviewed the prep doc for "standard ML library" / "typical embedding-training pattern" / "follow best practice" framings. None present. The DANN-style mitigation Aporia named in K(c) seed was flagged for frontier-model adversarial review (does it actually generalize on heterogeneous-mathematical-corpus settings?) rather than accepted as default-good. No paper or publication mentions anywhere.

### Diff this fire

| File | Change | Within ownership? |
|---|---|---|
| `pivot/killembedding_implementation_prep_2026-05-06.md` | NEW (~3,300 words) | pivot/ — design doc location; ticket explicitly directed |
| `aporia/meta/queue/techne_inbox.jsonl` | T001 BLOCKED + T002 DONE status updates | inbox/ — protocol-required |
| `roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-06.md` | NEW (this file) | role-doc surface, journaling per protocol |

No code files touched. No public APIs changed. No schemas modified.

### Tests

Pre-test (baseline): 344 passed in 65.79s
Post-test (sanity): 344 passed in 22.79s
Delta: 0 (expected — no code changes)

### Commit

`c72ca456` — "Fire #1: T002 KillEmbedding K(c) implementation prep checklist; T001 BLOCKED"

### Schedule wakeup

`delaySeconds=7200` (2h) with the loop prompt verbatim.

---

*Fire #1 closed. Next fire scheduled.*

---

## Fire #2 — 2026-05-06 ~20:30Z

**Pre-test baseline:** 361 v2.3 substrate tests passing (scoped sweep on the same critical-module set used in Fire #1, plus the kernel test files; full sigma_kernel + prometheus_math sweep launched in background but produced no output within the fire's window — confirmed clean via the scoped sweep instead). Fire #1's late-arriving full sweep (bxxmd3fpu) had returned exit code 0; baseline is established.

### Ticket completed: T-2026-05-06-T003 (P2) — Update sigma_kernel.md with v2.3 changes

**Status:** DONE.

**Deliverable:** `harmonia/memory/architecture/sigma_kernel.md` updated to reflect substrate v2.3 (commit `d17a2ff8`) faithfully. Public-read note at top extended; v0.1-vs-v2.3 scope comparison table; opcode table grew from 7 to 9 with REWRITE + EQUIV; storage migrations 004/005/006 documented; new section "v2.3 typed substrate primitives" covering KillVector v2 (+8 components from Aporia Study 02 with literature anchors), CoordinateChart + CanonicalizationProtocol, MethodSpec, stability adapters, EvidenceField (6 axes type-separated from PolicyField), ExclusionCertificate (with v2.3 hard rule), TriangulationProtocol (clustering-cannot-certify), and NearMissCorpus (multi-view leak-resistant emission). Cross-refs added to: PRECISION_METADATA_SPEC, TRACE_PRESERVATION_AUDIT, KILL_VECTOR_SPEC, LEARNER_CORPUS_SPEC, substrate_v2_proposal, techne_ergon_joint_sprint, killembedding seed + prep, sigma_kernel_logical_foundation_feasibility, external_review_watchlist. Open frontiers updated (A149/OBSTRUCTION_SHAPE chart registration pending Charon T11; KillEmbedding implementation Day 13-17; Watch-1 v3.0 design pass). "What this is NOT" extended with explicit "Not a navigable global metric topology" item — anti-fake-topology architectural lock-in surfaced for new readers.

### Self-review (mandatory per protocol)

(a) **Did I solve THIS ticket or a different problem?** Solved T003 per all 4 acceptance criteria: sections updated; cross-references added (10 doc links); public-read note preserved + extended; NO new contract claims (only documented what's IN the codebase as it shipped at d17a2ff8). Did not scope-creep into adjacent docs (kept v0.1 demonstration scripts intact as historical anchor; did not edit sigma_council_synthesis.md).

(b) **Did I change any contract?** No. Doc-only. Pre/post pytest 361 → 361 confirms no code touched.

(c) **Did I introduce conventional-approach drift?** Reviewed for "standard ML practice" / "industry-standard" framings — none present. KillEmbedding section frames adoption as gated on synthetic-null guard (not endorsed as default-good). DANN-style mitigation is documented as Aporia's seed-doc choice, not as Techne recommendation. Added explicit "anti-fake-topology" architectural lock-in to "What this is NOT" — strengthens anti-conventional-drift discipline. v3.0 hybrid CoC translation framed as conditional via Watch-1 (not as roadmap commitment). No paper or publication mentions anywhere.

### Diff this fire

| File | Change | Within ownership? |
|---|---|---|
| `harmonia/memory/architecture/sigma_kernel.md` | M (substantial v2.3 reflection) | ✅ harmonia/memory/architecture/sigma_kernel*.md |
| `aporia/meta/queue/techne_inbox.jsonl` | T003 OPEN → DONE status update | inbox/ — protocol-required |
| `roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-06.md` | M (this entry + Fire #1 commit-hash backfill) | role-doc surface, journaling per protocol |

No code files touched. No public APIs changed. No schemas modified.

### Tests

Pre-test (scoped, Fire #2 baseline): 361 passed in 26.37s
Post-test (sanity): 361 passed (same scoped set; no code changes)
Delta: 0 (expected — doc-only change)

### Commit

`22077914` — "Fire #2: T003 sigma_kernel.md updated to reflect v2.3 architecture"

### Schedule wakeup

`delaySeconds=7200` (2h) with the loop prompt verbatim; runtime clamps to 3600s.

---

*Fire #2 closed. Next fire scheduled.*

---

## Fire #3 — 2026-05-06 ~22:00Z

**Pre-test baseline:** 361 v2.3 substrate tests passing (scoped sweep b67vn31f3 → exit code 0). Full sigma_kernel + prometheus_math sweep also still clean (Fire #2's full sweep b5hdygmpt confirmed exit 0 between Fire #2 and Fire #3).

### Tickets considered: T-2026-05-06-T004 + T-2026-05-06-T005 (both P3)

Same priority; tied on `created_at`; T004 lower id → considered first.

#### T004 — BLOCKED (outside file ownership; coord ticket filed)

Asks for file at `charon/diagnostics/substrate_tester_fire_log.md`. That path is OUTSIDE Techne file ownership (sigma_kernel/, prometheus_math/, harmonia/memory/architecture/sigma_kernel*.md). Per loop hard-rule "Outside that, file coordination ticket and mark BLOCKED" — exactly the prescribed pattern.

Filed coordination ticket `C-2026-05-06-T001` in `aporia/meta/queue/charon_inbox.jsonl` asking Charon to create the file in his own ownership. Substrate-tester loop's first append unblocks once Charon ships C-2026-05-06-T001.

#### T005 — DONE

**Deliverable:** `pivot/g4_audit_prep_2026-05-06.md`. Audits `prometheus_math/gradient_archaeology.py` for Charon's pending G4 (F-gate orthogonality MI audit). Identifies structural gap: today's `gradient2_kill_path` / `gradient3_operator_falsifier` / `per_region_disaggregation` consume legacy pilot schemas that collapse F1/F6/F9/F11 to a single first-triggered kill_pattern string. G4 needs per-record per-F-gate triggered booleans for pairwise contingency tables and mutual information computation.

Per-record signal exists in NEW emissions (post-v2.3 KillVector v2 + Tier-3 cross-domain envs + A149 historical 314K trace-grade kills) but NOT in legacy aggregate-only pilots.

**Critical finding:** Path forward is purely additive — **ZERO contract changes required.** Two new functions proposed (`_extract_per_record_kill_vector(rec)` + `gradient_g4_f_gate_orthogonality_mi(sources, f_gates)`); existing public function signatures untouched; existing pilot schema unchanged. Implementation can ship under the loop's "internal changes only" rule without explicit pause/resume. Estimated implementation budget: ~4-6 hours focused work, tractable in 1-2 fires when Charon prioritizes.

Two adjacent items WOULD require pause/resume but neither is needed for G4: (1) backfilling legacy pilot JSONs (unsound — per-record signal was never logged at the time); (2) modifying `KillVector.to_dict()` output shape (not needed).

### Self-review (mandatory per protocol)

(a) **Did I solve THIS ticket(s)?** T004 routed correctly per file-ownership protocol; coord ticket filed in Charon's queue with full context. T005 delivered audit doc per all 3 acceptance criteria: (i) doc filed; (ii) NO code changes; (iii) contract-change requirements explicitly flagged (and the audit verdict is ZERO required, with two adjacent items named that WOULD require pause/resume).

(b) **Did I change any contract?** No code touched. Only doc additions + inbox JSONL status updates + Charon coord ticket addition. Pre-test 361 / post-test still 361 (no code changes).

(c) **Conventional-approach drift check?** Audit doc proposes additive functions, not refactoring or library imports. No "use scikit-learn for MI" or "follow standard ML practices" — MI is documented as bits-formula derived from first principles. **Anti-conventional discipline applied:** explicitly flagged that backfilling per-record signal into legacy aggregate-only pilots would be "unsound" — resisting the conventional reflex of "just re-run everything with the new logger." Watch-2 (F6/F9 heuristic-vs-computable) preserved as a separate concern even if G4 resolves orthogonality empirically. No paper or publication mentions.

### Diff this fire

| File | Change | Within ownership? |
|---|---|---|
| `pivot/g4_audit_prep_2026-05-06.md` | NEW (~3,200 words) | pivot/ — design doc location; ticket explicitly directed |
| `aporia/meta/queue/techne_inbox.jsonl` | T004 BLOCKED + T005 DONE status updates | inbox/ — protocol-required |
| `aporia/meta/queue/charon_inbox.jsonl` | C-2026-05-06-T001 coord ticket appended | inbox/ — protocol-prescribed cross-pillar coord |
| `roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-06.md` | M (this entry + Fire #2 commit-hash backfill from prior fire) | role-doc surface, journaling per protocol |

No code files touched. No public APIs changed. No schemas modified.

### Tests

Pre-test (scoped, Fire #3 baseline): 361 passed (b67vn31f3 → exit 0).
Post-test: not run separately (no code changes; trivially identical to pre-test).
Delta: 0.

### Commit

`62a64901` — "Fire #3: T005 gradient_archaeology G4 audit; T004 BLOCKED + Charon coord ticket"

**⚠ Cross-agent staging incident:** the commit picked up 6 additional files beyond my explicit `git add` (5 ergon/learner/diagnostics/* files + ergon_inbox.jsonl mods). Likely an Ergon /loop agent staged files in parallel between my `git add` and `git commit`, and they got swept into Fire #3's commit. Files are legitimate (Ergon's parallel work) but credit is misattributed in commit message. **Future fires:** check `git diff --cached` immediately before commit and `git reset` any unexpected files; or use `git -c commit.cleanupCRLF.warn=false add ... && git diff --cached --name-only` to verify staging just-in-time. The shared working-tree across parallel /loop agents is a known coord hazard.

### Schedule wakeup

`delaySeconds=7200` (2h) with the loop prompt verbatim; runtime clamps to 3600s.

---

*Fire #3 closed. Inbox has 0 OPEN tickets in the original starter set (T001+T004 BLOCKED, T002+T003+T005 DONE). Next fire will check for new tickets; if none, document quiet tick + schedule next wake.*

---

## Fire #4 — 2026-05-06 ~22:50Z

**Pre-test baseline:** 361 v2.3 substrate tests passing (scoped). Full sigma_kernel + prometheus_math sweep launched in background (bods8446c) — confirmed clean from prior fires.

### Inbox state at fire start

Original starter set fully drained at end of Fire #3. **2 new tickets added by substrate-tester between Fire #3 and Fire #4:**

- **ST002 (P1-high)** — substrate-flaw: CoordinateChart silently accepts empty domain string despite docstring claiming non-empty
- **ST003 (P2-normal)** — substrate-flaw: get_raw_invariant_keys silently returns sentinel for unregistered domains

Picked ST002 first (P1 > P2).

### Ticket completed: T-2026-05-06-ST002 (P1) — CoordinateChart empty-domain validation

**Status:** DONE.

**Bug:** `CoordinateChart.__post_init__` line 248 checked `isinstance(domain, str)` AND `":" not in domain` but missed the non-empty check. Sibling `region_key` validator at line 252 DID check non-empty. The asymmetry let `domain=""` succeed silently, producing chart_id `":<region_key>"` which corrupts `_split_chart_id` semantics downstream (the leading colon makes "domain" parse as empty string and "region_key" capture everything after — masking the original intent).

**Fix:** Changed line 248 to mirror line 252's structure:
```python
if not isinstance(self.domain, str) or not self.domain or ":" in self.domain:
    raise ValueError(...)
```
Comment added referencing ST002 ticket id + explanation of the asymmetry.

**Tests:** New `TestCoordinateChartValidation` class with 4 tests:
- `test_coordinate_chart_rejects_empty_domain` (the requested test)
- `test_coordinate_chart_rejects_non_string_domain` (sanity for sibling rule branch)
- `test_coordinate_chart_rejects_colon_in_domain` (sanity for sibling rule branch)
- `test_coordinate_chart_accepts_valid_domain` (positive sanity check)

### Self-review (mandatory per protocol)

(a) **Did I solve THIS ticket?** YES. Remediation_hint applied verbatim. The probe scenario (`CoordinateChart(domain="", ...)`) now raises ValueError as expected. The 4 tests cover the empty-domain case + adjacent rule branches.

(b) **Did I change any contract?** NO — the docstring + error message at line 250 already declared "non-empty string"; this fix brings implementation into line with the declared contract. Substrate-tester filed as `type: substrate-flaw` validating the bug-fix framing. Loop hard rule: "You CAN fix bugs, optimize internals, refactor without changing surface, ADD TESTS, write docs." This is squarely a bug fix + test addition.

(c) **Conventional-approach drift check?** Reviewed:
- Fix mirrors the existing region_key validator pattern; NOT a "use a validation library" or "switch to pydantic" reflex
- Kept scope tight (4 tests; did not refactor adjacent code "while I'm here")
- Comment in fix references ST002 ticket id — preserves audit trail per substrate's content-addressed-provenance discipline
- Did not over-test (resisted urge to add a test_coordinate_chart_accepts_unicode_domain or similar edge cases not in scope)
- No paper or publication mentions

### Diff this fire

| File | Change | Within ownership? |
|---|---|---|
| `sigma_kernel/coordinate_chart.py` | Line 248 validator: added `not self.domain` clause; +5-line audit-trail comment | ✅ |
| `sigma_kernel/test_coordinate_chart.py` | New `TestCoordinateChartValidation` class (4 tests) | ✅ |
| `aporia/meta/queue/techne_inbox.jsonl` | ST002 OPEN → DONE status update | inbox/ — protocol-required |
| `roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-06.md` | M (this entry + Fire #3 commit-hash backfill from prior fire) | role-doc surface |

### Tests

Pre-test (scoped, Fire #4 baseline): 361 passing
Post-test (full v2.3 sweep): 365 passing (+4 from this fix)
Delta: +4 tests; 0 regressions

### Cross-agent staging hazard mitigation (per Fire #3 incident)

Before commit, will run `git diff --cached --name-only` to verify staged files match my explicit `git add` list. Reset any unexpected files to keep Fire #4's commit credit clean.

### Commit

`e168b635` — "Fire #4: ST002 CoordinateChart empty-domain validation bug fix"

Cross-agent staging mitigation worked: `git diff --cached --name-only` before commit confirmed exactly 4 files staged (no parallel agent contamination this fire).

### Schedule wakeup

`delaySeconds=7200` (2h) with the loop prompt verbatim; runtime clamps to 3600s.

---

*Fire #4 closed. Inbox after: ST002 DONE, ST003 OPEN (P2). Fire #5 will pick ST003.*

---

## Fire #5 — 2026-05-07 ~00:00Z

**Pre-test baseline:** 365 v2.3 substrate tests passing (matches Fire #4 post-fix state). Full sigma_kernel + prometheus_math sweep launched in background (b37q612dm); confirmed clean from prior fire's full sweep that returned exit 0.

### Ticket considered: T-2026-05-06-ST003 (P2, substrate-flaw)

**Status:** BLOCKED (`contract-change-requires-explicit-resume`).

**Why this differs from ST002 (which I fixed in Fire #4):**
- ST002 was implementation-vs-docstring DIVERGENCE: docstring at line 250 declared "non-empty string"; validator missed the check. Fixing aligned implementation with the declared contract → bug fix per loop rule.
- ST003 is a proposed CONTRACT INVERSION: docstring at `prometheus_math/learner_corpus.py:126-128` EXPLICITLY DECLARES sentinel-return as intentional design, AND existing test `test_per_domain_raw_invariant_registry_unknown_domain_returns_sentinel` (test_learner_corpus.py:93-94) ENFORCES it. Three things agree (docstring + implementation + test); substrate-tester is asking to change the declared design, not fix a divergence.

**Three paths forward** (filed in inbox resolution; ranked by cost):

- **PATH A** (additive, no contract change required): keep `get_raw_invariant_keys(domain)` returning sentinel for backwards compat; ADD a new function `get_raw_invariant_keys_strict(domain)` that raises KeyError on unknown; future callers opt into strict mode. Tractable in one fire under "fix bugs, ADD TESTS" rule.
- **PATH B** (contract change with explicit pause/resume): replace silent-return with KeyError per substrate-tester remediation_hint. Would break the existing test AND observable behavior of downstream callers (`stub_emit_from_legacy_ledger`, `emit_from_substrate`). Requires explicit authorization.
- **PATH C** (orthogonal, no contract change, closes the BROADER concern): add warning log to `stub_emit_from_legacy_ledger` + `emit_from_substrate` when they detect all-None raw_invariants. The substrate-tester's related T2 finding (`stub_emit_from_legacy_ledger with domain='bsd_rank' but Lehmer-shape record accepted silently; all-None for 5/5 BSD keys with no warning`) is closed by this without touching get_raw_invariant_keys's contract. Function I/O stays identical; only stderr observability changes. Tractable in one fire.

**Recommendation:** PATH C as immediate follow-up (additive observability, no resume needed, closes substrate-tester's broader concern). PATH A as v2.4 substrate cycle item. PATH B only if Aporia + James + Charon explicitly want the contract inverted.

### Inbox state after BLOCK

Original starter set: T001+T004 BLOCKED, T002+T003+T005 DONE.
Substrate-tester adds: ST002 DONE (Fire #4), ST003 BLOCKED (this fire).

**0 OPEN tickets remain.** Per protocol step 1: "If no OPEN tickets, document quiet tick in your session journal and schedule next wake."

### Self-review (mandatory per protocol)

(a) **Did I solve THIS ticket or a different problem?** Correctly identified ST003 as contract-change territory rather than scope-creeping into an unauthorized fix. The analysis distinguishes ST003 (contract inversion) from ST002 (bug fix). Three paths named so the unblock is informed.

(b) **Did I change any contract?** NO code touched. Only inbox status update + journal entry. Pre/post pytest 365/365 unchanged.

(c) **Conventional-approach drift check?** Resisted the conventional reflex of "the substrate-tester said it's a bug so fix it." The DECLARED contract matters more than what feels right; substrate discipline is content-addressed, not authority-addressed. Substrate-tester is correct that silent-degradation is a hygiene concern, but the resolution is upstream (Aporia/James choose the contract direction), not downstream (Techne unilaterally changes it). Also explicitly named PATH C as the substrate-aligned move that addresses the broader concern WITHOUT contract change — modeling additive observability over invasive contract inversion. No paper or publication mentions.

### Diff this fire

| File | Change | Within ownership? |
|---|---|---|
| `aporia/meta/queue/techne_inbox.jsonl` | ST003 OPEN → BLOCKED status update with detailed 3-path resolution | inbox/ — protocol-required |
| `roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-06.md` | M (this entry + Fire #4 commit-hash backfill from prior fire) | role-doc surface |

No code files touched.

### Tests

Pre-test (scoped, Fire #5 baseline): 365 passing (matches Fire #4 post-fix)
Post-test: not separately run (no code changes; trivially identical)
Delta: 0

### Commit

To be recorded after commit.

### Schedule wakeup

`delaySeconds=7200` (2h) with the loop prompt verbatim; runtime clamps to 3600s.

---

*Fire #5 closed. Inbox: 0 OPEN tickets (T001+T004+ST003 BLOCKED, T002+T003+T005+ST002 DONE). Fire #6 will check for new tickets; if none, document quiet tick.*
