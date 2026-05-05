# Team Work Queue — 2026-04-26 (10-hour parallel session)

**Status:** Building. Two of five frontier-model §8.8 seeds in (ChatGPT, Gemini); 3 pending (Grok, DeepSeek, Claude-fresh).
**Coordination:** Each substrate role takes one problem-paradigm pairing and runs the attack with the assigned operators/data. Outputs go to kill ledger / calibration corpus / Stoa / Techne queue. Feedback loop signal score per `frontier-review/chatgpt.md` §8.7 routes back-or-switch.

## Convergent doctrine inputs (already actioned)

- **PATTERN_BASE_RATE_NEGLECT** (`kairos/patterns/`) — every result this session must report base-rate denominators. No exceptions.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT** (`kairos/patterns/`) — every quantitative bound checked against hardware limits before publication.
- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT** (`kairos/patterns/`) — every cross-region match / TT bond-rank claim must include explicit prime-detrending audit. Battery test #1 is now operator-named with veto authority.
- **PATTERN_CONDUCTOR_CONFOUND** (`kairos/patterns/`) — every cross-region correlation must demonstrate within-stratum survival across conductor deciles, not merely pooled-corpus correlation. Catches conductor-driven trivial scaling.
- **Conductor steering captured in `feedback_domains_are_docstrings`** — *bridges between domains are not the goal either; substrate is interested in structural enrichment of operator-derived regions, regardless of which human-labeled domains the regions span.* Tools and findings should be named for what they DO, not for the bridge narrative they enable. Reframe DeepSeek's TOOL_CROSS_REGION_BRIDGE as TOOL_OPERATOR_PORTABILITY_TEST (REQ-028).
- **P20 deprecated as paradigm** — MAP-Elites is operational layer (Maieutēs incubator), not paradigm. **3/3 model convergence on the deprecation.** Replacement (SAT vs Spectral Tail vs nothing) is now 3-way contested; Round-2 protocol after all 5 in.
- **REQ-027 cross-region TT bond-rank analyzer** filed with Techne (`techne/queue/requests.jsonl`) — Grok-proposed, validates Stoa proposal `2026-04-26-aporia-structural-signature-v1.md`, completes the 3-layer Techne-gap stack (signature canonicalizer + spectral signature + bond-rank analyzer).
- **Gravitational wells to flatten before TT** (combined ChatGPT + Gemini + Grok, dedup'd, ~7 unique): primes (existing), low-degree polynomial bias (CGPT), small-conductor/discriminant bias (CGPT) ≈ conductor/height wells (Grok), short-sequence/entropy bias (CGPT), trivial L-zeros (Gem) ≈ L-function zero spacing (Grok), small-degree CM clustering (Gem), Hasse-Weil bounds (Gem), knot volume/signature clusters (Grok unique).

## Session seeds (problem × paradigm × role assignment)

### Seed #1 (from ChatGPT §8.8) — READY TO FIRE

- **Problem:** Erdős primitive sets (Bloom catalog reference; ties to Batch 9 #159 Erdős minimum overlap).
- **Paradigm:** P21 — Curated-corpus empirical sweep.
- **Role assignment:** Aporia (predicate design), Ergon (sweep), Charon (matched null), Aporia (stratification), Kairos+Harmonia (pattern enforcement, possible P19 transport).
- **6-hour plan:**
  - Hour 0–1 (Aporia): Define predicate "primitive set density vs reciprocal sum bound violation candidates" over OEIS-derived sets.
  - Hour 1–3 (Ergon): Sweep across OEIS (370K, §2); compute sum(1/n) and structural signature via `TOOL_LLL_REDUCTION` + recurrence detection. Store signatures.
  - Hour 3–4 (Charon): Apply `NULL_BSWCD@v2` matched null over sets preserving size distribution; compute anomaly scores.
  - Hour 4–5 (Aporia): Stratify by signature clusters; look for strata where anomaly persists across nulls (P21 requirement).
  - Hour 5–6 (Kairos+Harmonia): Enforce PATTERN_30, PATTERN_BASE_RATE_NEGLECT, MULTI_PERSPECTIVE_ATTACK@v1. If survives, attempt P19 cross-region operator transport onto LMFDB integer invariants.
- **Output:** stratified anomaly map, NOT a conjecture. Filed to kill ledger if dies, calibration corpus if survives.

### Seed #2 (from Gemini §8.8) — READY TO FIRE

- **Problem:** Lehmer's Conjecture (Mossinghoff Mahler tables, §2).
- **Paradigm:** P22 — Spectral Tail Relocation (proposed addition; pending replacement choice).
- **Role assignment:** Ergon-led; Charon for null; Kairos for pattern enforcement.
- **6-hour plan:**
  - Connect to embedded Mossinghoff tables.
  - Stream polynomial roots through `TOOL_GPD_TAIL_FIT` to analyze spectral tail near the unit circle (do NOT analyze polynomial roots directly).
  - Use `NULL_BSWCD@v2` to block-shuffle polynomial coefficients; generate matched null distribution.
  - Test whether Mahler measure mass-gap (Lehmer's bound) emerges monotonically from the GPD of the spectral tail.
  - Harvest all reasoning traces to SQLite.
- **Output:** Either GPD-monotone-emergence finding (publishable) or kill with weak-signal residue describing where the GPD model breaks.

### Seed #3 (from Grok §8.8) — READY TO FIRE

- **Problem:** Open Erdős-type primitive set or Sidon set density question (overlaps Seed #1's problem class but uses a different paradigm).
- **Paradigm:** P19 — Cross-region operator transport.
- **Role assignment:** Ergon-led; Charon for null; Aporia for stratification; Kairos for pattern enforcement.
- **6-hour plan:**
  - Hour 0-1: Load relevant OEIS Sleeping Beauty sequences + LMFDB modular forms / mf_newforms via TOOL_MATH_KNOWLEDGE_GRAPH.
  - Hour 1-3: Apply `TOOL_MAHLER_MEASURE` (from EC region) to primitive set polynomials after prime detrending (NULL_BSWCD@v2). **PATTERN_PRIME_GRAVITATIONAL_OVERFIT enforcement: explicit detrending audit required.**
  - Hour 3-4: Compute TT bond ranks on small per-region tensor slice for transport compatibility (use REQ-027 once available; otherwise hand-rolled).
  - Hour 4-5: Run P21-style stratification across 68K Sleeping Beauty sequences for success/failure patterns.
  - Hour 5-6: Test against matched nulls + multi-region (add KnotInfo signatures if coupling appears). Output operator-named bridge candidate or kill-ledger residue with exact battery scores.
- **Output:** Operator-named bridge candidate (for promotion) or kill-ledger residue with weak-signal description (for Maieutēs incubation).
- **Pairing note:** Seeds #1 and #3 attack the same problem class (Erdős primitive/Sidon sets) from two different paradigms (P21 corpus sweep vs P19 operator transport). If both run in parallel, they cross-validate: real signal should appear in both.

### Seed #4 (from DeepSeek §8.8) — READY TO FIRE

- **Problem:** Lehmer's conjecture (same problem class as Seed #2 — multi-angle attack).
- **Paradigm:** P19 cross-region operator transport + P21 corpus sweep (hybrid).
- **Role assignment:** Ergon-led (data and computation); Charon (matched-null permutation); Aporia (kill-ledger entry); Kairos (PATTERN_PRIME_GRAVITATIONAL_OVERFIT + PATTERN_CONDUCTOR_CONFOUND enforcement).
- **6-hour plan (with explicit time budget):**
  - **0.5h:** Extract Mossinghoff Salem polynomials into DuckDB (5K, Mahler measure < 1.3).
  - **1.5h:** TOOL_MAHLER_MEASURE verify; TOOL_CF_EXPANSION on Salem numbers themselves; store CF complexity (sum/max of partial quotients).
  - **1h:** TOOL_SINGULARITY_CLASSIFIER on reciprocal generating function; structural signature = (CF complexity, singularity type, Mahler measure).
  - **1.5h:** Select 100K L-function zeros from non-CM EC (cond < 1000); compute consecutive zero gaps; TOOL_CF_EXPANSION on gap sequence; TOOL_SINGULARITY_CLASSIFIER on gap distribution.
  - **1h:** Operator-portability test (manual until REQ-028 lands). Detrend conductor and primes both sides. 1000 matched-null permutations. Effect size > 0.35 with p < 0.01 → flag candidate.
  - **0.5h:** Kill-ledger entry with effect size, p-value, all pattern checks (PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_30, PATTERN_BASE_RATE_NEGLECT).
- **Output:** Either a within-stratum operator signature shared across Salem polys and EC zero-gaps (promote candidate, file REQ-028 priority bump if it survives), or a calibration true-negative for the Salem-EC region pair (Maieutēs incubation).
- **Pairing note:** Seeds #2 and #4 attack Lehmer from different paradigms (P22 Spectral Tail vs P19+P21 hybrid). Seeds #1 and #3 attack Erdős primitive sets from P21 vs P19. **All four pairings model the multi-agent-same-problem-different-angle structure James asked for.**

### Seed #5 (from Claude-fresh #1 §8.8) — READY TO FIRE

- **Problem:** Lehmer's conjecture (third Lehmer attack — also Seeds #2 and #4).
- **Paradigm:** P19 cross-region operator transport — explicitly between Salem polynomials and hyperbolic-knot trace fields.
- **Role assignment:** Charon-led (Galois work); Ergon (TT splice); Kairos (rank-parity audit, conductor audit, prime audit).
- **6-hour plan:**
  - **H0-H1:** Pull all 5K Mossinghoff Salem polynomials. Compute splitting fields via TOOL_GALOIS_GROUP. Pull 12,965 KnotInfo trace fields via TOOL_KNOT_SHAPE_FIELD. Compute structural_signature on both populations.
  - **H1-H2:** Apply detrending — flatten by class-number, by CM-vs-non-CM in NF view, by hyperbolic-volume decile in knot view. TT-compress joint tensor.
  - **H2-H3:** Read bond ranks of cross-region splice. Hypothesis: there exists a sub-population of Salem polynomials whose splitting fields are arithmetically equivalent to trace fields of low-volume hyperbolic knots, and Mahler measure on that sub-population approaches Lehmer's bound monotonically with decreasing volume.
  - **H3-H4:** NULL_BSWCD on the cross-region splice (preserving conductor-decile of NF and volume-decile of knots). Multi-region replication: repeat with non-Salem reciprocal polynomials as control.
  - **H4-H5:** If ≥4/5 mandatory: name the operator (Reid's commensurability invariants is the candidate). Literature lock-in via Boyd-Smyth-Reid-Daubechies neighborhood.
  - **H5-H6:** Battery scoring. If 5/5: publishable Lehmer-hyperbolic-geometry connection. If 3/5: residue to Maieutēs. If ≤2/5: kill-ledger entry naming the false bridge.
- **Output:** Operator-named connection (Reid commensurability) with effect size, or calibrated kill of the Salem-trace-field hypothesis.
- **Pairing note:** **THREE Lehmer attacks** now queued (Seeds #2, #4, #5) using three different paradigms (P22 Spectral Tail / P19+P21 hybrid / pure P19 with knot trace fields). Real cross-validation if all three run.

### Seed #6 (from Claude-fresh #2 §8.8) — READY TO FIRE

- **Problem:** Lehmer's conjecture (FOURTH Lehmer attack).
- **Paradigm:** P21+P19 hybrid via Galois-discriminant stratification.
- **Role assignment:** Ergon-led; Charon (matched-null); Kairos (pattern enforcement).
- **6-hour plan:**
  - **H0-H1:** Compute Mahler measures via TOOL_MAHLER_MEASURE on Mossinghoff full table. Compute Galois groups via TOOL_GALOIS_GROUP. Build joint distribution (degree × signature × Galois-class × measure).
  - **H1-H2:** Stratify; produce measure-vs-Galois-discriminant heatmap. Identify lowest-measure region per Galois stratum.
  - **H2-H3:** P19 transport — adapt NULL_BSWCD@v2 from EC region to Galois-discriminant-decile marginals on Mossinghoff. Test whether lowest-measure clusters survive transported null. **The operator transport itself is the experiment.**
  - **H3-H4:** Cross-corpus linkage: pull EC Faltings heights via TOOL_FALTINGS_HEIGHT from LMFDB, restricted to CM curves via TOOL_CM_ORDER_DATA. Match against Mossinghoff Mahler measures.
  - **H4-H5:** 5/5 battery: prime detrending (cyclotomic factor removal), matched null using H2-H3 transported null, multi-stratum replication across ≥3 Galois classes, operator-naming, lit-lock (Silverman, Zhang).
  - **H5-H6:** Verdict to Stoa: stratification map + transport result. Kill-ledger if H2-H3 null kills cluster. File TAIL_VS_BULK_DECOMPOSITION request to Techne if H4 cross-corpus signal lives in only one regime.
- **Output:** Stratified Mahler-measure map indexed by Galois-discriminant decile, with transported-null bands and EC-Faltings-height linkage scores. **The map is the product, not the conjecture.**

## Multi-angle attack structure (achieved)

- **Erdős primitive sets:** Seeds #1 (P21 corpus sweep) + #3 (P19 operator transport) — 2 angles
- **Lehmer's conjecture:** Seeds #2 (P22 Spectral Tail) + #4 (P19+P21 hybrid) + #5 (P19 with knot trace fields) + #6 (P19 via Galois-discriminant stratification) — **4 angles**
- All four Lehmer attacks use different paradigm combinations and different operator transports. If real signal exists in the Lehmer-region structural neighborhood, multiple seeds should converge. If the convergence is rank-parity-mediated or conductor-mediated, Kairos's new patterns (PATTERN_RANK_PARITY_LEAK, PATTERN_CONDUCTOR_CONFOUND) catch the false convergence.

## Updated convergent doctrine inputs (5 frontier responses, 6 instances)

- **PATTERN_BASE_RATE_NEGLECT** ✅ minted (`kairos/patterns/`)
- **PATTERN_VRAM_TRUNCATION_ARTIFACT** ✅ minted
- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT** ✅ minted
- **PATTERN_CONDUCTOR_CONFOUND** ✅ minted
- **PATTERN_RANK_PARITY_LEAK** ✅ minted (paired with REQ-030 OPERATOR_RANK_PARITY_NULL_CONTROL)
- **TAIL_VS_BULK_DECOMPOSITION** ✅ filed as REQ-031 (positive operator, not pattern — Claude-fresh #2's argument)
- **TOOL_SDP_RELAX (SCS)** filed as REQ-029 — Claude-fresh #2 unblock for P17

**6 of 6 model instances** identify structural signature canonicalization as the highest-priority Techne build (existing Stoa proposal `2026-04-26-aporia-structural-signature-v1.md`). **Strongest convergence in the entire frontier review.** Both Claude instances explicitly say "stop dithering, ship it."

**6 of 6** demote P20 as paradigm. Settled.

**6 distinct P20-replacement proposals** with no convergence:
1. ChatGPT: Constraint-Relaxation/SAT
2. Gemini: Spectral Tail Relocation
3. Grok: nothing (18+2 is enough)
4. DeepSeek: Ergodic Averaging
5. Claude-fresh #1: ML-Saliency-Guided Conjecture
6. Claude-fresh #2: Polynomial Method

The lack of convergence is itself the data. Round-2 needed; or accept all 6 as candidate paradigms and let substrate use confirm which earn promotion.

**6 distinct data-gap proposals**, no convergence. Cost-benefit triage needed.

**6 distinct §8.9 measurement-axis questions**, all real:
1. ChatGPT: false-negative rate of battery
2. Gemini: synthetic-exhaust echo chamber
3. Grok: bond-rank threshold
4. DeepSeek: encoding invariance
5. Claude-fresh #1: substrate's null model for itself (would F011 be findable without the substrate?)
6. Claude-fresh #2: would F011 survive a re-run of the battery today?

**Both Claude instances independently zero in on F011 as the substrate's calibration weakness.** This convergence within the model is meaningful — same training, two independent draws, both surface the same blocker.

## Backup problems (if seeds saturate)

Drawn from Batch 9 currently-unfired or under-resourced briefs:
- **#168 k-MOLS at n=10** (Ergon, P09 + P21, needs REQ-026 SAT solver — blocked but tractable in parts)
- **#163 Erdős unit-distance / Hadwiger-Nelson** (Ergon, P09, also needs SAT)
- **#177 Sleeping Beauty OEIS sweep** (Aporia + Ergon, P21, ready to execute on existing data)
- **#178 Genus-2 Rosetta validation** (Charon, P15 + P19, ready on existing tensor)

## Per-role responsibilities for the session

| Role | Primary load | Secondary | Continuous duties |
|---|---|---|---|
| **Aporia** | Predicate design + stratification for Seed #1 | Backup #177 design | Cross-comparison synthesis as remaining frontier responses arrive |
| **Charon** | Matched-null computation across seeds | Backup #178 | NF / arithmetic-geometric workhorse calls; flag any TOOL gaps to Techne |
| **Ergon** | Seed #2 lead (Lehmer × P22); Seed #1 sweep step | Backup #168, #163 | Tensor sweeps; SAT calls if REQ-026 lands mid-session |
| **Harmonia** | Pattern enforcement + synthesis-of-meaning across seeds | Operator-versioning audit (queued from Batch 9 #163 followup) | Symbol registry hygiene |
| **Kairos** | Adversarial review of every seed result; pattern-veto authority | Battery brittleness log (per two-track epistemics v1.2 narrow exception) | Calibration anchor candidates |
| **Mnemosyne** | REQ-001 Bloom-Erdős ingest progress (high priority — unblocks Seed #1 at scale) | Data snapshot ledger groundwork | Continuous data-staleness monitoring |
| **Techne** | REQ-026 SAT-solver wrapper (blocking #168, #169, #163) | TOOL_SPECTRAL_SIGNATURE / canonicalizer per Stoa proposal | Inventory hygiene |

## Feedback-loop routing rules

Hybrid form combining ChatGPT's signal-score and Gemini's rule-based override:

**Composite signal score S ∈ [0, 1]:**
- +0.25 each for: matched null pass, multi-region replication, operator-named, literature lock-in.
- +0.10 for replication across ≥3 strata.
- −0.20 for any pattern violation.

**Routing:**
- **S ≥ 0.75 → stay on same problem (deepen).**
- **0.45 ≤ S < 0.75 → stay but force paradigm switch.**
- **S < 0.45 → abandon; reassign to backup problem from list above.**
- **ΔS < 0.05 across 2 consecutive cycles → force reassignment regardless of S.**

**Gemini override rules (qualitative):**
- If TDD pass on isolated operator AND fail on PATTERN_30 / NULL_CONSTRAINT_MISMATCH: keep problem, swap null model only.
- If MULTI_PERSPECTIVE_ATTACK fails across 3 fundamentally different paradigms (e.g. P01, P04, P13): region is sterile; escalate to Maieutēs incubator and pull new problem regardless of S.

## Reporting cadence

Every 90 minutes, each role posts a one-paragraph status to Stoa with:
- Current S score
- Battery test status (which passed, which failed, which pending)
- Base rate denominator (non-negotiable per PATTERN_BASE_RATE_NEGLECT)
- VRAM check (per PATTERN_VRAM_TRUNCATION_ARTIFACT)
- Routing decision for the next 90-minute block

End-of-session: each role files a session journal with cumulative findings, kills, calibration anchors added, Techne requests filed, and stoa proposals queued.

---

*Aporia, 2026-04-26. Work queue v0.1 — built on convergent ChatGPT + Gemini inputs. Will be updated as Grok / DeepSeek / Claude (fresh) responses arrive and seeds #3–5 lock in.*
