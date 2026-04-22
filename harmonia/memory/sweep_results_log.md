# Sweep Results Log (Pattern 30/20/19 retrospective)

Append-only record of every sweep verdict. Retrospective baseline created by `harmonia/sweeps/retrospective.py` on 2026-04-21T00:38:31.264453+00:00.

Scope: every +1 or +2 cell in the current tensor. LINEAGE_REGISTRY carries one of four taxonomies for each audited F-ID:

- `algebraic_lineage` — correlation with algebraic coupling; runs Pattern 30 auto-check and emits CLEAR / WARN / BLOCK.
- `frame_hazard` — construction-biased sample; Pattern 4 is the active gate. Emits PROVISIONAL (does not halt). Sync-posted.
- `killed_no_correlation` — killed specimen; no correlation content to audit. Emits N/A_KILLED (silent CLEAR-equivalent).
- `non_correlational` — variance deficit / existence / density / calibration. Emits N/A_NON_CORRELATIONAL (silent CLEAR-equivalent).

Pattern 20 and Pattern 19 cannot run retrospectively without per-cell stratified / prior-measurement data in a structured form — both are logged as NO_RETROSPECTIVE_DATA.

---

## F001 (calibration) — 4 active cell(s)

**Cells:** P010:+2, P011:+2, P012:+2, P020:+1

**Pattern 30 retrospective:** Level 4 IDENTITY (calibration anchor — verdict-semantics is theorem verification, not arithmetic-structure discovery).
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F002 (calibration) — 2 active cell(s)

**Cells:** P001:+1, P024:+1

**Pattern 30 retrospective:** Level 4 IDENTITY (calibration anchor — verdict-semantics is theorem verification, not arithmetic-structure discovery).
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F003 (calibration) — 3 active cell(s)

**Cells:** P020:+2, P023:+2, P041:+2

**Pattern 30 retrospective:** Level 4 IDENTITY (calibration anchor — verdict-semantics is theorem verification, not arithmetic-structure discovery).
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F004 (calibration) — 1 active cell(s)

**Cells:** P043:+2

**Pattern 30 retrospective:** Level 4 IDENTITY (calibration anchor — verdict-semantics is theorem verification, not arithmetic-structure discovery).
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F005 (calibration) — 2 active cell(s)

**Cells:** P023:+2, P024:+1

**Pattern 30 retrospective:** Level 4 IDENTITY (calibration anchor — verdict-semantics is theorem verification, not arithmetic-structure discovery).
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F008 (calibration) — 1 active cell(s)

**Cells:** P024:+2

**Pattern 30 retrospective:** Level 4 IDENTITY (calibration anchor — verdict-semantics is theorem verification, not arithmetic-structure discovery).
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F009 (calibration) — 3 active cell(s)

**Cells:** P024:+2, P039:+2, P100:+1

**Pattern 30 retrospective:** Level 4 IDENTITY (calibration anchor — verdict-semantics is theorem verification, not arithmetic-structure discovery).
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F011 (live_specimen) — 10 active cell(s)

**Cells:** P020:+2, P021:+2, P023:+2, P025:+2, P026:+2, P028:+2, P036:+2, P050:+2, P051:+2, P104:+2

**Pattern 30 retrospective:** NON_CORRELATIONAL (N/A_NON_CORRELATIONAL). GUE first-gap variance deficit, rank-0 residual eps_0 = 22.90% ± 0.78 (1/log(N) ansatz), z=29sigma from 0. eps_0 is a fit intercept, not a correlation coefficient — no X-vs-Y coupling to audit. Independent-unfolding audit survived (72.9pp gap vs null floor).
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F013 (live_specimen) — 5 active cell(s)

**Cells:** P023:+2, P028:+2, P041:+2, P051:+2, P104:+2

**Pattern 30 retrospective:** Level 1 WEAK_ALGEBRAIC (WARN). P028 splits strata by root number, which is algebraically tied to rank parity via BSD; the stratum-dependent effect is expected. The empirical content is the sign pattern and z=15.31 magnitude, neither forced by the parity relation alone.
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F014 (live_specimen) — 4 active cell(s)

**Cells:** P021:+2, P023:+2, P040:+1, P053:+2

**Pattern 30 retrospective:** NON_CORRELATIONAL (N/A_NON_CORRELATIONAL). Lehmer-Mahler spectrum: Salem density in (1.176, 1.228) with 3 polynomials strictly in-region (minimum a Salem polynomial at 1.216392). Density claim, not a correlation. Per-num_ram monotone is structural, not Pattern-30 coupled.
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F015 (live_specimen) — 4 active cell(s)

**Cells:** P020:+2, P021:+2, P042:+2, P104:+2

**Pattern 30 retrospective:** Level 1 WEAK_ALGEBRAIC (WARN). szpiro = log|Disc| / log(N); correlating against log(N) puts log(N) in the denominator. Level 1 WEAK_ALGEBRAIC.
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F022 (killed) — 1 active cell(s)

**Cells:** P010:+2

**Pattern 30 retrospective:** KILLED_NO_CORRELATION (N/A_KILLED). NF backbone via feature distribution; z=0.00 under permutation null (P001 cosine). Same data as F010. rho=0 kill has no correlation to audit.
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F041a (live_specimen) — 5 active cell(s)

**Cells:** P020:+2, P021:+2, P023:+2, P026:+2, P104:+2

**Pattern 30 retrospective:** Level 1 WEAK_ALGEBRAIC (WARN). CFKRS arithmetic factor is bad-prime-structure dependent; nbp ladder coupling is partially forced. Level 1 WEAK_ALGEBRAIC.
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F044 (live_specimen) — 3 active cell(s)

**Cells:** P020:+2, P023:+2, P026:+2

**Pattern 30 retrospective:** FRAME_HAZARD (PROVISIONAL). Rank-4 disc=conductor corridor (2085/2086). Pattern 4 is the active gate, not Pattern 30. PROVISIONAL pending Class-4 null.

**Sampling frame:** LMFDB rank-4 corridor (n=2086). Population is not a random sample — Stein/Elkies/Dujella record constructions are biased toward searchable-conductor families. 'disc=conductor' is definitionally semistable everywhere (Ogg's formula).
**Class-4 null reference:** harmonia/memory/symbols/protocols/null_protocol_v1.md#class-4 — frame-based resample: reconstruct search methodology, re-apply to broader region, see if disc=conductor proportion changes.
**Pending audit:** `audit_F044_framebased_resample` (complete=False)
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

## F045 (live_specimen) — 1 active cell(s)

**Cells:** P023:+1

**Pattern 30 retrospective:** Level 1 WEAK_ALGEBRAIC (WARN). isogeny-class-size axis is partially algebraic-derived from bad-prime structure via P100 <-> P021 coupling; Level 1 provisional. Promote to Level 2 if the pending F041a<->F045 audit confirms collapse.
**Pattern 20 retrospective:** NO_RETROSPECTIVE_DATA. Stratified companion stats not structurally recorded in tensor manifest; run at next re-audit.
**Pattern 19 retrospective:** NO_RETROSPECTIVE_DATA. Prior-signature comparison needs signals.specimens history query, not done in this pass.

---

## Summary

- Features audited: 15
- Total +1/+2 cells: 49

### Pattern 30 distribution

- `pattern_30_frame_hazard`: 1
- `pattern_30_killed_no_correlation`: 1
- `pattern_30_level_1`: 4
- `pattern_30_level_4_calibration`: 7
- `pattern_30_non_correlational`: 2

### Verdict breakdown (per-feature)

- `CLEAR`: 7
- `WARN`: 4
- `BLOCK`: 0
- `PROVISIONAL`: 1
- `N/A_KILLED`: 1
- `N/A_NON_CORRELATIONAL`: 2
- `NO_LINEAGE_METADATA`: 0

### Interpretation

- **Level 4 calibration**: expected — these are theorem anchors by design (F001-F005, F008, F009).
- **Level 0-3 from registry**: F043 Level 3 (already retracted), F015 / F041a / F013 / F045 Level 1 WEAK_ALGEBRAIC.
- **PROVISIONAL (frame_hazard)**: F044 — Pattern 4 gate active, Class-4 null pending via `audit_F044_framebased_resample`.
- **N/A_KILLED**: killed specimens registered so the sweep is aware they exist; no correlation content to audit.
- **N/A_NON_CORRELATIONAL**: variance-deficit / density / existence claims (F011, F014); no X-vs-Y correlation exists to audit.
- **NO_LINEAGE_METADATA**: the baseline substrate debt. Any F-ID not registered and not in calibration-tier falls through to this bucket and requires manual annotation before Pattern 30 can run.

No net-new retractions triggered by this pass — F043 was already retracted 2026-04-19; F015, F041a, F013 Level-1 annotations were applied by the methodology tightener; F044 PROVISIONAL pending the existing Agora re-audit task.

---