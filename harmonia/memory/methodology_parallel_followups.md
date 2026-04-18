# Methodology: Execute Multiple Followup Paths Simultaneously
## Pattern candidate — derived from the four-paths reflection (2026-04-18)

**Author:** Harmonia_M2_sessionB, 2026-04-18
**Context:** After Aporia Report 1 closed Pattern 5 on F011, a user reflection surfaced four distinct research paths. Executing all four in a single session (rather than picking the one that looked highest-yield) produced findings that no individual path would have produced. This document records the lesson for future Harmonias.

---

## The core observation

When a single finding closes (e.g., F011 → DHKMS excised ensemble), the natural question is "what now?" — and the natural instinct is to pick the single most-promising followup and execute it cleanly. This is efficient for individual findings but misses an emergent property: **the followup paths inform each other, and the cross-path connections are often where the real frontier hides.**

Specifically, in the four-paths reflection:

| Path | Individual finding | Cross-path contribution |
|------|-------------------|------------------------|
| 1+2: Rank-0 residual | ε₀ = 31% non-excised residual (power-law); 23% (1/log(N)); durable under P104 audit | Provided the EMPIRICAL TARGET that Path 4's theoretical entries need to explain |
| 3: P104 catalog entry | Block-shuffle-within-confound formalized as P104 | Provided the AUDIT INSTRUMENT that Path 1's residual could be tested against (Thread 5 self-audit) |
| 4: EC L-function literature harvest | 40 projections, 24 uncatalogued, 8 open | Surfaced Miller 2009 arithmetic corrections as THE theoretical comparison Path 1's residual needs — a match that required seeing both paths side-by-side |

None of these cross-connections would have surfaced by executing one path at a time, because:

1. **Path 1 alone** would have produced the residual number without a theoretical target. "31% extrapolation" is a fact without a comparison is not a finding.
2. **Path 3 alone** would have produced a catalog entry without a calibration anchor. "Here's a null" without "here's when you should have used it on your own work" is a dead doc.
3. **Path 4 alone** would have produced a table of uncatalogued projections without knowing which ones were already load-bearing for active frontier work.

**The lesson**: when identifying followup paths, if you can execute them concurrently without resource conflict, DO SO. The cross-path synthesis is a separate deliverable.

---

## Specific cross-path patterns observed

### Pattern A: Theory path surfaces the target for data path
Path 4 (literature harvest) surfaced Miller 2009 "arithmetic lower-order terms" as the NLO correction to DHKMS. Path 1 (rank-0 residual) produced an observed ε₀ ≈ 23% under the classical 1/log(N) decay ansatz. These are probably the SAME NUMBER from opposite directions — theoretical NLO prediction vs empirical residual extrapolation. Neither path finds that by itself; the user reading both paths' outputs together does.

### Pattern B: Instrument path calibrates earlier findings
Path 3 (P104 catalog entry) formalized the block-shuffle-within-confound null. Path 1 (rank-0 residual) had produced an extrapolation with no durability audit. Thread 5 applied Path 3's instrument to Path 1's finding — **the self-audit cycle closes within the same session**. Without both paths, the audit-on-own-work discipline doesn't surface naturally.

### Pattern C: Documentation paths expose debt that data paths hide
Path 4 surfaced that DHKMS excised ensemble itself is uncatalogued, despite being the validation anchor I used in the very prior session (Aporia Report 1). **The catalog-level documentation gap was invisible until the literature harvest made it visible.** This is the "you can't see your own blind spots without a different projection" phenomenon.

### Pattern D: Each path's "caveat" becomes another path's "entry point"
Path 1 noted: "If true decay accelerates at log_cond > 6, ε₀ could be smaller." This is a caveat. But Path 4 shows that NO classical projection is catalogued for log_cond > 5.6 regime. The caveat of Path 1 becomes a seed for a future Path-4-style literature audit specifically on the tail regime.

---

## When does this apply?

**DO execute multiple paths simultaneously when:**
- The paths share compute-cheap resources (e.g., one DB query feeds all of them).
- The paths span different types (data + doc + theory + audit) — cross-type synthesis is where the connections are.
- A specific finding was just closed / retracted / modified — the "what did this open?" moment is THE moment for breadth.
- You have budget for a self-reflection step after all paths complete.

**DON'T when:**
- Paths require conflicting DB locks or sequential-only infrastructure.
- One path's result materially determines whether the others are worth doing (cascade dependency — do the gatekeeper first).
- Time-box is so tight that a bad concurrent run ruins all four. Sequential is safer when each path has long tail risk.

**Rule of thumb**: if you can identify 3-5 paths from a reflection prompt, and they collectively fit in your current compute/token budget, do them all. The cross-path synthesis is free value on top.

---

## Proposed addition to pattern library

**Pattern 23 (candidate) — Parallel Followup Paths Produce Emergent Findings**

When a finding closes or modifies, identify multiple (3-5) research paths it opens. If resources permit, execute them concurrently. The cross-path synthesis — connections between paths that don't exist within any single path — is often where the next frontier lives.

**Canonical example:** Four-paths reflection after F011 Aporia Report 1 closure. Path 4's surfaced Miller 2009 entry became the theoretical target for Path 1's 23% empirical residual. Neither path alone produced this connection.

**Anti-example:** Sequential followup where Path 1 finishes, produces a number, and the worker moves on. Without concurrent Path 4, the Miller connection is never made; the number sits unexplained as "anomaly."

---

## Proposed addition to pattern library (second candidate)

**Pattern 24 (candidate) — Apply Your Own Instruments to Your Own Findings**

When you build or catalog a new methodology tool (e.g., P104 block-shuffle null), the first thing to audit with it is your own prior findings. Self-audit within-session closes the "discipline lag" that normally keeps old findings unchallenged.

**Canonical example:** Tick-20 audit_P028_findings_block_shuffle applied P104 to my prior F011/F013 work. Thread 5 of four-paths reflection applied P104 to Path 1's own residual. Each time, the discipline produced a definitive verdict (durable or retract).

**Anti-example:** Adding a new null-type to the battery but only applying it to future specimens. Old findings carry forward unaudited, accumulating a review debt that grows each tick.

---

## Operational checklist (for future-Harmonia cold-starts)

When given a "what now?" reflection question after a finding:

1. **Enumerate paths aggressively.** Aim for 3-5, not 1. Include at least one of each type:
   - Data-extension path (more compute on same or related data)
   - Instrument path (new tool or null)
   - Documentation path (catalog entry, literature harvest)
   - Self-audit path (apply new or existing tool to own work)

2. **Check for compute-cheap parallelism.** Can one DB query feed multiple paths?

3. **Execute all paths in a single session if budget allows.**

4. **Before reporting, write a synthesis step.** Explicitly look for connections between path outputs. The synthesis doc is often more valuable than any single path's output.

5. **Commit the synthesis doc alongside the paths.** Future workers reading the git log will see the reflection pattern and can apply it themselves.

---

*Harmonia_M2_sessionB, 2026-04-18. Derived from cartography/docs/four_paths_reflection_20260418.md and the five-threads followup.*

---

## Addendum — recursion horizon and two new patterns (update 2026-04-18 post-reflection-level-3)

After running five threads from the four-paths reflection, six more sub-threads emerged. Only three of those six were tractable in a single session; three were deferred. This exposed the **recursion horizon**:

- **Depth 1** (reflection): 4 paths — all tractable.
- **Depth 2** (threads): 5 threads — all tractable.
- **Depth 3** (sub-threads): 6 sub-threads — 3 tractable, 3 deferred.
- **Depth 4** (sub-sub-threads): would require sessionA to seed as new tasks.

**Implication for Pattern 23:** the parallel-followup approach has a natural termination after ~3 levels. Workers should not attempt deeper recursion without sessionA seeding new tasks in the queue. The session-level discipline: do as many paths/threads as tractable at the current level, document clearly what's deferred and why, commit and hand off.

**Pattern 25 (candidate) — When a Fit Has Too Many Free Parameters, Pin Some From Theory Before Reporting Point Estimates.**

Canonical example: rank-0 residual unified decay ansatz `deficit = ε₀ + C/log(N)^α`. With α free, the (ε₀, α) plane is poorly constrained; ε₀ point estimate has huge SE. Fixing α=1 from Miller's classical leading order gives ε₀=22.9% with tight SE. Fixing α=2 from CFMS naive gives ε₀=35.8%. The theoretical choice sharpens the empirical estimate.

Anti-example: reporting ε₀ under a preferred ansatz as if the ansatz were given by data. Without theory input, the point estimate is load-bearing on an assumption the data can't justify.

**Pattern 26 (candidate) — Confound Stratification for Block-Shuffle Has Its Own Discipline.**

Canonical example: F011 rank-0 residual P104 audit under three confounds (class_size, cm_binary, torsion). Results varied from spurious (class_size, one dominant value → degenerate null) to noisy (cm_binary, 0.9% rare class → null barely different from observed) to clean (torsion, 15 balanced groups → z=4.19 meaningful separation). The confound-choice itself is a methodology choice, not a neutral setting.

Practical rule: for block-shuffle nulls, prefer confounds with:
- 5–20 strata (not fewer, not hundreds)
- No single stratum dominating >40% of the data
- All strata with n ≥ some adequacy threshold (≥100 for z-reporting)

When the primary confound fails these criteria, consider compound confounds (e.g., `(rank_parity, torsion)` joint strata) or finer binning of a continuous variable.

---

*End addendum. Three patterns (23, 24, 25, 26) now candidates for the pattern library; sessionA approval pending.*
