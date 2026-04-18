# Decisions for James — Asynchronous Queue
## Append-only log of items needing James's input
## Owner: Harmonia_M2_sessionA (conductor)
## Started: 2026-04-17

---

## How this works

James is HITL with time offline. I accumulate decisions that need his input here
rather than blocking the work on them. He reads this when he's back.

Each entry:
- Timestamp
- What's the decision
- What I'd recommend (to save his thinking time)
- What's blocked by it (if anything) — usually nothing, because I keep working

Anything truly urgent (calibration anchor failure, destructive-action risk,
data corruption) I flag at the TOP of this document with ⚠️.

Anything I can handle within the charter + standing orders, I handle. This
document is for things outside that envelope.

---

## ⚠️ URGENT (top-pinned)

*None currently.*

---

## Pending decisions

*None currently. Three specimens now block-shuffle-verified; Katz-Sarnak emerges as cross-specimen resolver (see below).*

---

### [2026-04-17 ~12:45 UTC] — 3 SPECIMENS VERIFIED under block-shuffle; P028 is a real cross-specimen resolver — MAJOR FINDING

**Context:** Following the F010 block-shuffle kill this morning, sessionB and sessionC ran the protocol on F011, F013, and F015. Results:

| Specimen | Finding | Block-shuffle verdict | z_block |
|---|---|---|---|
| F010 NF backbone | decon ρ=0.27 via P052 | **KILLED** | -0.86 |
| F011 GUE first-gap deficit | P028 spread 7.63% | **DURABLE** | 111.78 |
| F013 zero-spacing vs rank | P028 slope diff 13.68 | **DURABLE** | 15.31 |
| F015 Szpiro sign-uniform | per-k slope -0.3 to -0.7 | **DURABLE** | -3.48 to -24.03 |

**Interpretation:** The Katz-Sarnak symmetry-type axis (P028) is now the **first cross-specimen resolver** this session. F011 and F013 both resolve via it at z_block >> 10. F015 resolves via a different axis (P021 bad-prime) but also block-verified. F010 failed — and it was the only specimen whose "survival" came through a post-hoc decontamination rather than a native stratification.

**What was learned:** (1) The block-shuffle protocol discriminates rather than blanket-rejects — it correctly separates durable from artifact. (2) Plain permutation nulls can over-reject OR under-reject depending on which stratum structure they preserve. F010 plain null over-rejected (z=2.38 looked real, was artifact); F011 plain null didn't over-reject (z=7.63 was real). The protocol IS the check. (3) P028 Katz-Sarnak is a genuinely load-bearing resolving axis for EC and NF-adjacent specimens.

**What needs deciding:** Nothing. All three specimens' tensor entries updated with block-shuffle verification. P028 is now the "canonical resolver" to test against new specimens before any other axis.

**My recommendation:** This is the session's strongest POSITIVE finding. Combined with the F010 kill, we have a clean methodology pair:
- Kill case (F010): post-hoc decontamination can look durable but isn't
- Survival case (F011/F013/F015): native stratification via P028 OR P021 is durable

Both are needed to calibrate the instrument. The session is complete, durable, and leaves a working methodology plus a working resolver.

**What's blocked:** Nothing. Worth future work: test P028 on F014 (only live specimen without a block-verified resolver).

**Urgency:** Low (FYI — the session's high-order positive finding)

---

---

### [2026-04-17 ~12:33 UTC] — F010 KILLED under block-shuffle null — FINAL KILL

**Context:** F010 (NF backbone via Galois-label) was the session's emerging "strongest specimen" candidate at 5/5 projection survival. Multiple falsification layers peeled back:
1. Pooled ρ=0.40 killed at bigsample → 0.109 (Pattern 20 artifact)
2. Decontaminated ρ=0.27 via P052 prime-detrend (z=2.38 weak-null) was the proposed durable signal
3. P028 Is_Even split z_diff=5.38 attenuated to z_diff=1.95 at bigsample (P028 weak)
4. **Block-shuffle-within-degree null (sessionC wsw_F010_alternative_null, this tick)**: the decontaminated ρ=0.173 (n=51) sits BELOW null mean 0.205, z=-0.86. **Zero within-degree coupling.**

**Interpretation:** The NF↔Artin coupling is degree-marginal only — "low-degree NFs pair with low-dim Artin reps" is trivial and doesn't survive preserving per-degree structure. F010 joins F022 (its feature-distribution twin, previously killed).

**What was learned:** The plain label-permute null (used in sessionC's bigsample) OVER-REJECTED because it didn't preserve per-degree marginal. This is a *null-model selection* lesson — choice of null matters as much as choice of projection. Three-layer artifact demonstrated: Pattern 20 (pooled level) + Pattern 19 (stale 0.40 claim) + null-model-mismatch (plain permute doesn't catch degree-marginal signal).

**What needs deciding:** Nothing — F010 tier changed to `killed`. INVARIANCE updated: P052: +1 → -2, P010: +2 → -1. The null-model lesson is the session's strongest methodology finding.

**My recommendation:** ACCEPTED. This is a GREAT result even though it looks like a negative. The methodology caught what would have been a tempting false-positive. No new calibration anchor, but a strong PATTERN calibration: when a signal survives 5 projections, run it through a null that preserves the most obvious stratum structure (degree, conductor, etc.) before promotion.

**What's blocked:** Nothing. The remaining live specimens (F011, F013, F014, F015) have NOT been through block-shuffle nulls. Worth seeding bigsample+block-null tests for each — now a standard protocol.

**Urgency:** medium-high (paradigm for other specimens)

---

---

## Resolved (recent — keep for audit)

### [2026-04-17 ~11:33 UTC] — F010 did NOT graduate: pooled ρ was Pattern-20 artifact — RESOLVED

**Original question:** Would F010 graduate from `live_specimen` to `robust_specimen` if the large-n rerun pushed z>3.5?

**Resolution:** sessionC wsw_F010_bigsample (per_degree=5000, n_shared=75) completed. Raw pooled ρ **collapsed** from 0.404 (n=71) to 0.109 (n=75, z=0.88) — classic Pattern-20 sample-frame artifact. Durable signal is decontaminated ρ=0.270 (P052 prime-detrend, stable across sample sizes, retention_ratio=2.47). But z=2.38 is still borderline. F010 stays `live_specimen`, not promoted.

**Downstream updates:**
- F010 became the 4th Pattern 20 anchor case (pattern_library.md updated).
- F010 joined F012/F014/F011 as Pattern 19 anchors (the claimed 0.40 was stale).
- Tensor F010 description rewritten: durable ρ=0.27 via P052, pooled was artifact.
- F010 INVARIANCE: P052:+1 added, P040 demoted -1→-2 (pooled is not durable here).

**What's blocked:** Nothing. F010 may still firm up with an alternative null (block-shuffle within degree-class). Seeding `wsw_F010_alternative_null` followup.

**James approval:** 2026-04-17 "agreed on the F010 NF - let it play out" — outcome now known.

---

### [2026-04-17 ~11:00 UTC] — F012 H85 kill provisional pending Liouville — RESOLVED

**Original question:** Was the F012 |z|=6.15 a definitional artifact (Möbius vs Liouville) that Liouville side-check would rescue?

**Resolution:** Liouville side-check completed (sessionB). Max|z|=0.52 under Liouville, 0.39 under Möbius. Both firmly in noise (p=0.60/0.68). **F012 kill is definitional-independent** — the original |z|=6.15 was never reproducible. F012 moved to `tier=killed`. Pattern 19 promoted from draft to full pattern.

**James approval:** 2026-04-17 "All sounds good. You can archive them."

---

### [2026-04-17 ~11:00 UTC] — F013 density/structural 74%/26% split — ACKNOWLEDGED

**Original question:** Recording the quantitative characterization of F013 as 74% density-mediated, 26% structural residual.

**Resolution:** Recorded in tensor (F013→F011 parallel_density_regime edge, F013 INVARIANCE updated per sessionC draft). Clean finding, good science. No further action required.

**James approval:** 2026-04-17 "All sounds good."

---

### [2026-04-17 ~11:00 UTC] — Pattern 19 (Stale/Irreproducible Tensor Entry) promotion — APPROVED

**Original question:** Should Pattern 19 (sessionB's proposed pattern from F012 WORK_COMPLETE) become an official pattern?

**Resolution:** Promoted to full pattern with Liouville confirmation. Anchor cases F012/F014/F011 documented. In pattern_library.md.

**James approval:** 2026-04-17 "All sounds good."

---

### [2026-04-17 ~11:00 UTC] — F014 Lehmer 4.4% gap FALSIFIED — ACKNOWLEDGED

**Original question:** SessionB found Salem polynomial at M=1.216 inside the claimed 4.4% Lehmer gap. F014 needed refinement.

**Resolution:** F014 description updated in tensor to reflect the Salem density in (1.176, 1.228). sessionB further refined with num_ram=1 monotone trend. Kept tier=live_specimen (structure remains interesting, claim refined).

**James approval:** 2026-04-17 "All sounds good."

---

### [2026-04-17 ~11:00 UTC] — F010 NF backbone reproduced at 4/5 projections — ACKNOWLEDGED

**Original question:** SessionC confirmed F010 at ρ=0.404, survives conductor/bad-prime/feature-perm, P052 deferred.

**Resolution:** Recorded. Followup task `wsw_F010_P052` queued to close out the fifth projection.

**James approval:** 2026-04-17 "All sounds good."

---

### [2026-04-17 ~11:00 UTC] — Worker commits push authorization — APPROVED

**Original question:** Should I push worker output commits on their behalf?

**Resolution:** James's ongoing approval mode during this session covers pushes of worker output files (`cartography/docs/wsw_*.json|.py`) and tensor memory files when they correspond to approved TENSOR_DIFFs. I've been pushing these as I approve them.

**James approval:** 2026-04-17 "All sounds good."

---

*Template for new entries:*

```
### [YYYY-MM-DD HH:MM UTC] — <short title>

**Context:** one paragraph
**What needs deciding:** one sentence
**My recommendation:** one paragraph with reasoning
**What's blocked:** (nothing | specific worker | specific task) — usually nothing
**Urgency:** low / medium / high / URGENT

---
```
