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

### [2026-04-17 ~11:16 UTC] — F010 NF backbone is emerging as strongest specimen

**Context:** sessionC wsw_F010_P052 completed. F010 Galois-label coupling now survives **5/5 tested projections**:
- P010 Galois-label keyed (original finding)
- P020 conductor conditioning (73% retention)
- P021 bad-prime stratification (65% retention)
- P042 feature permutation (full survival)
- P052 prime decontamination (rho 0.231→0.269, actually **strengthens** after removing prime structure)

Prime detrend R² = 0.885 (NF) / 0.84 (Artin) — primes explain MOST of the raw variance, yet the coupling persists. F010 is in the 4% of couplings NOT prime-mediated, contra the 96% default from the pattern library. Only issue: at current n=62 shared labels, z=1.80 is borderline.

**What needs deciding:** Nothing blocking. I've queued `wsw_F010_bigsample` at priority -3 to rerun with per_degree=5000+, targeting n_shared ≥ 500. If z jumps to >3.5, F010 becomes the definitive strongest specimen in the tensor.

**My recommendation:** Let it play out. If the large-n rerun confirms, F010 graduates from live_specimen to something stronger (needs a new tier name — maybe `robust_specimen` or similar). This is the first coupling that's survived everything we've thrown at it.

**What's blocked:** Nothing.

**Urgency:** medium (FYI — potentially the session's best finding)

---

---

## Resolved (recent — keep for audit)

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
