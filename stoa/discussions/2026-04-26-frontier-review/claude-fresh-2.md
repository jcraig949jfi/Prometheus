# Claude-fresh response #2 — frontier review of attack-paradigm strategy

**Date received:** 2026-04-26
**Model:** Claude (fresh instance, browser session B)
**Prompt:** `whitepapers/attack_strategy_frontier_prompt_20260426.md`
**Document attached:** `whitepapers/attack_strategy_for_frontier_review_20260426.md`
**Constraint compliance:** Full. Most pragmatic about what to drop in 6 months.
**Note:** Same-model variance with Claude-fresh #1 is striking — different P22, different pattern, different data gap, similar §8.9 framing.

---

## 8.1 Validate or refine the 18+3 paradigm list

The 18 are sound as canonical axes. P19 and P21 stay. **P20 should be cut and replaced.**

P20 is a search algorithm, not a mathematical paradigm. Every other entry is a *way of perceiving the math*. MAP-Elites is *how you allocate exploration budget across whatever paradigm you're using*. Already lives correctly in §5/§7 as the Maieutēs incubator's epistemic architecture.

**Replacement: P20 → Polynomial Method.** Encode combinatorial constraints as low-degree polynomials in a function space and exploit dimension-counting. Last-20-year load-bearing breakthroughs not subsumed by your 18: Dvir's finite-field Kakeya (2008/9), Guth–Katz distinct distances (2010), Croot–Lev–Pach + Ellenberg–Gijswijt cap-set (2016). Not P11 (mechanism is dimension count, not local-condition removal). Not P15 (works in polynomial spaces, not multi-index arrays). Not P17 (no functional being minimized). Distinct axis. OEIS Sleeping Beauty subset and 544K-group corpus are natural targets.

## 8.2 Per-paradigm tactical advice

[Highlights — many "drop in 6 months" calls (P02, P06, P14, P18) for honest scope-cutting:]
- **P03:** Re-run F011 stratified by Galois group from 544K-group DuckDB. Does the +46-51% bulk deficit at k=24 vary by automorphism class?
- **P09:** Promote REQ-026 (PySAT + Kissat). Already cited by Batch 9 #168/#169/#163. Ship it.
- **P15:** Ship the unified-tensor signature-keyed structure. "It has been the next milestone for some time; that's the failure mode. Set a date."
- **P17:** Install SCS or Mosek as `TOOL_SDP_RELAX`. P17 is hand-tied without an SDP backend.
- **P21:** Codify F011 protocol as `TOOL_KATZ_SARNAK_SWEEP`. Right now the F011 recipe is implicit institutional knowledge.
- **P22 (Polynomial Method, new):** Croot–Lev–Pach polynomial encoding to OEIS Sleeping Beauty subset filtered for cap-set-shaped questions.

## 8.3 The data gap

**House of Graphs ingest** (~10K curated extremal/conjecturally-special graphs, https://houseofgraphs.org), structured as Postgres mirror analogous to LMFDB.

§2 has heavy number-theory mass, low-dim topology, sequences, and groups. Combinatorics — specifically extremal graph theory — is absent despite Bloom–Erdős's center of mass being precisely there. Bloom–Erdős will give you the *problem catalog*. House of Graphs gives you the *attack surface* against those problems. Without it, you'll catalog Erdős conjectures you cannot computationally probe.

Basement-friendly (10K objects, full database <2GB), inherits LMFDB-style curation rather than OEIS-style sprawl.

Strictly higher leverage than ATLAS-of-Finite-Group-Reps, Polymath archive, or arXiv corpus, because the others duplicate existing strengths or give you metadata-not-data.

## 8.4 The Techne gap

**`TOOL_STRUCTURAL_SIGNATURE`** — the canonicalization primitive proposed in `stoa/proposals/2026-04-26-aporia-structural-signature-v1.md`. **Build it, don't just propose it.**

§6 explicitly names it as one of the two ceiling-setters. P19, P15, P21, and the entire TT-splicing program in §6 all gate on this. It unlocks three paradigms minimum and every cross-region problem.

## 8.5 The symbolic-library gap

**`TAIL_VS_BULK_DECOMPOSITION@v1`** as a missing operator.

F011 is a *bulk* statement: +46–51% bulk deficit at k=24. The substrate has no codified operator that decomposes a spectral signal into tail vs. bulk components and computes battery scores on each independently.

- **False positives prevented:** signals that look universal but are actually bulk-only (tail-flat) or tail-only (bulk-flat) currently masquerade as full-spectrum findings. F011 itself implicitly assumed bulk-only sufficed for promotion; no audit confirmed the tail wasn't telling a contradicting story.
- **True positives opened:** tail-zero statistics in `lfunc_zeros` carry information independent of central/bulk statistics; without a named decomposition operator, every tail-vs-bulk experiment is hand-rolled.

Stronger gap-fix than another null pattern (PATTERN_30 family is already dense) because it's the missing *positive operator*, not another veto.

## 8.6 Tensor-train preprocessing

(1) **Conductor distribution (and norm-conductor for NF).** NULL_BSWCD@v2 already preserves conductor-decile marginals at the null layer — but you're handling it per-null, not as global TT preprocessing. Promote it to mandatory pre-compression flattening. Otherwise low-conductor curves dominate TT bond ranks.

(2) **Class-number / regulator (number fields).** 22M NF obey Cohen–Lenstra: small class numbers dominate by orders of magnitude. Stratify-then-flatten by log(h), not by h.

(3) **Tabulation index.** META-WELL — every curated dataset (OEIS, KnotInfo, Mossinghoff, even LMFDB) was tabulated easy-cases-first. Crossing-number bias in 12,965 hyperbolic knots, small-initial-term bias in OEIS, low-degree bias in Mossinghoff. Without flattening by tabulation rank, TT compression learns "what's been computed" rather than "what's structurally low-rank." Most insidious well — invisible per-corpus but uniform across corpora.

## 8.7 Feedback-loop refinement

Cycle = 2 hours (10-hour session = 5 cycles).

**Continue on same problem** if in the most recent cycle ≥1 of: battery score increased by ≥1; new operator output produced; new cross-region linkage detected.

**Switch problem** if 0 of the above for 2 consecutive cycles (4 hours dead).

**Maieutēs handoff** if battery score 2/5 or 3/5 with ≥1 operator output.

**Techne queue escalation** if same tool gap cited ≥2 times across team within 4-hour window.

**Promotion to publication track:** 5/5 battery, multi-region replication confirmed in ≥3 strata, operator named, lit-locked. No exceptions.

**Bond-rank threshold for "cross-region linkage":** I don't have evidence for a specific number. Calibration corpus too thin. Instruct the loop to log every bond-rank measurement during first 3 sessions and set threshold at 25th percentile of empirical distribution after N≥30 measurements.

## 8.8 One specific problem-paradigm pairing

**Problem:** Lehmer's conjecture. **Paradigm:** P21 hybridized with P19.

[6-hour attack: H0-H1 Mahler measure + Galois group; H1-H2 Galois-discriminant heatmap; H2-H3 P19 transport of NULL_BSWCD@v2 from EC region to Galois-discriminant marginals on Mossinghoff; H3-H4 cross-corpus EC Faltings-height linkage; H4-H5 5/5 battery; H5-H6 Stoa write + Maieutēs route.]

## 8.9 The question I'm not asking but should be

With the calibration corpus at N=2 and bootstrapped, and F011 standing as effectively the only documented promotion: **would F011 itself survive a re-run of the 5-of-5 battery today, and what's the substrate's evidence that the battery's false-kill rate isn't already higher than the discovery rate?**

---

## Aporia scorecard

| Section | Verdict | Notes |
|---|---|---|
| 8.1 | **NEW: P22 Polynomial Method (6th unique replacement)** | Dvir Kakeya 2008, Guth-Katz 2010, Croot-Lev-Pach + Ellenberg-Gijswijt cap-set 2016 as load-bearing 20-year breakthroughs not subsumed by P11/P15/P17. **Different from Claude-fresh #1's P22 (ML-Saliency).** Same model, two browser sessions, two different proposals. |
| 8.2 | **MOST PRAGMATIC SCOPING** | Multiple explicit "drop in 6 months" (P02, P06, P14, P18). Honest about basement-hardware limits. **TOOL_SDP_RELAX (SCS)** — concrete tool addition for P17. |
| 8.3 | **NEW DATA GAP — House of Graphs (~10K extremal graphs)** | 6th distinct data gap proposed. Argument: substrate has zero combinatorics attack surface despite Bloom-Erdős's center being there. <2GB, basement-friendly, LMFDB-style curation. |
| 8.4 | **6/6 CONVERGENCE — ship the canonicalizer** | Same as Claude-fresh #1 and prior 4 models. Six-of-six identification of structural signature canonicalization as the highest-leverage primitive. |
| 8.5 | **NEW OPERATOR (not pattern) — TAIL_VS_BULK_DECOMPOSITION** | Critique: F011 is bulk-only, never audited tail. Explicitly argued as a *positive operator* gap rather than another null pattern. **6th distinct pattern/operator proposal across the review.** |
| 8.6 | **DIFFERENT WELLS from Claude-fresh #1** | Conductor distribution (not in C-fresh #1), class-number/regulator (overlap with C-fresh #1 + Grok), **tabulation index (META-WELL)** — easy-cases-first across all curated datasets. The tabulation-index well is genuinely new and possibly the most important. |
| 8.7 | **TIGHTEST CYCLE-BASED ROUTING** | 2-hour cycles, simple "≥1 of {score+1, new operator, new linkage}" continue-rule. **Honest about bond-rank threshold uncertainty** — defers to empirical calibration after N≥30 measurements. |
| 8.8 | **Lehmer × P21+P19 hybrid** | Different attack from Claude-fresh #1's pure P19 — uses Galois-discriminant stratification and Mossinghoff EC Faltings-height linkage. |
| 8.9 | **CONVERGENT WITH C-FRESH #1 — both circle F011 self-validation** | C-fresh #1: substrate's null model for itself. C-fresh #2: would F011 survive re-running the battery today + false-kill vs discovery rate. **Both Claude instances independently zero in on F011 as the substrate's calibration weakness.** |
