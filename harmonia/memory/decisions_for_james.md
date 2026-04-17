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

### [2026-04-17 10:53 UTC] — F012 H85 kill: Möbius vs Liouville definitional drift

**Context:** sessionB ran the HITL-authorized wsw_F012 audit on H85. The claimed |z|=6.15 DID NOT REPRODUCE. Their clean measurement: max|z|=0.39 across adequate strata (n≥100), permutation p=0.6843, bootstrap mean 0.88 with 5-95pct [0.30, 1.99]. Firmly in noise.

BUT sessionB flagged three discrepancy hypotheses before filing as final. Most important: **DEFINITIONAL drift** — the prior H85 may have used Liouville λ(n) = (-1)^Ω(n) rather than Möbius μ(n). Liouville is ±1 everywhere; Möbius zeros out 63% of g2c discriminants (non-squarefree). If the prior measurement used λ, the signal may still exist under λ but got killed by my Möbius-based retest.

**What needs deciding:** Nothing from you right now — I've queued `liouville_side_check_F012` at priority -10 (most urgent). Any worker who ticks next claims it. Result in ~5 min. If Liouville restores the signal, F012 rescues back to live_specimen. If λ also gives p~0.7, the kill is final.

**My recommendation:** Let it play out. The instrument is self-correcting. I'm provisional on the kill pending Liouville.

**What's blocked:** Nothing. Workers continue. Tensor update for F012 is queued but flagged "provisional pending Liouville."

**Urgency:** medium (informational — the system is handling it, but you'll want to know this happened)

---

### [2026-04-17 10:53 UTC] — F013 rank-spacing is 74% density / 26% structural

**Context:** sessionD ran wsw_F013. Real object-level coupling (P042 z=-14.165) but N(T) unfolding (P051) collapses ~74% of the slope. Not mediated by conductor, bad-primes, or torsion. Parallel to F011 GUE deficit — both are density-regime features where the STRUCTURAL signal is a small (~26%) residual that survives unfolding.

**What needs deciding:** Nothing — this is a clean quantitative finding. I've queued `tensor_update_F013_density_split` to formally record the profile.

**My recommendation:** This is good science. The density-vs-structural split is the kind of precise characterization the charter asks for. sessionD did it right — no verdict-thinking, just measured the shape.

**What's blocked:** Nothing.

**Urgency:** low (FYI — good news)

---

### [2026-04-17 10:53 UTC] — Pattern 19 candidate: Stale/Irreproducible Tensor Entry

**Context:** sessionB proposed this in their F012 WORK_COMPLETE message. Claim: when a tensor entry's signal does not reproduce under clean measurement, and the likely cause is definitional drift or undocumented sampling, that's a distinct failure mode from Pattern 13 (wrong axis) — it's "was never reproducible to begin with."

**What needs deciding:** Should this become an official pattern?

**My recommendation:** Yes, but wait for the Liouville result before promoting. If H85 rescues under λ, Pattern 19 is confirmed and we have a cautionary tale about provenance hygiene. If H85 stays killed, Pattern 19 is also confirmed (the original measurement was noise all along). Either way, the pattern is useful and I'd promote after Liouville.

**What's blocked:** Nothing; pattern library drafts don't block execution.

**Urgency:** low (can wait until you're back)

---

### [2026-04-17 10:53 UTC] — Worker commits accumulating without push

**Context:** Workers are correctly writing output files (wsw_F011_results.json, wsw_F012_results.json, wsw_F013_results.json, catalog drafts) but per protocol they don't git push. sessionC commit 6ae831f4 still sits locally. sessionB and sessionD have uncommitted work files.

**What needs deciding:** Should I push worker output commits on their behalf now that we have running data? Or continue waiting for per-commit authorization?

**My recommendation:** Grant blanket push authorization for worker output files in `cartography/docs/wsw_*.json` and `cartography/docs/wsw_*.py` paths only. Those are measurement outputs; they don't change the charter, catalog, or patterns. Risk is bounded. Anything touching `harmonia/memory/*` or `docs/*` still requires your per-commit review.

**What's blocked:** sessionC's wsw_F011 output is unpushed (mild risk — if the machine goes down, the 38% F011 result is lost). Not urgent.

**Urgency:** medium (nothing blocking, but clean up the uncommitted state when you're back)

---

## Resolved (recent — keep for audit)

*Populated as items resolve.*

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
