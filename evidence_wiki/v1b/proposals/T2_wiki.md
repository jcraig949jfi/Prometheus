# PROPOSAL T2 (wiki)

Designer: V1B-T2-wiki (M1) · 2026-09-02 · Specification only — no collection authorized by this document.
Instrument: Prometheus probe band, `ergon/probe/` (nearmiss task ladder, exact-match scoring, leveling/gate machinery already in the repo).

## Hypothesis

H1: On the nearmiss probe family, the PAID-tier lane (`deepseek:deepseek-v4-flash`, vendor-served)
outscores the FREE-tier lane (`nvidia:deepseek-v4-flash`, NVIDIA-served) on the
**heuristic-resistant stratum** — items the attainable-without-reasoning controls fail — by
**≥ +4pp exact-match cold accuracy (rep-1)**, at the M20 rung, under paired same-item comparison.

Scope ceiling (declared up front): both lanes serve the same model FAMILY on different serving
stacks (`solver.py` L37-44: a host change is a solver-set change; serving config undisclosed).
Any positive is a claim about **free-tier vs paid-tier SERVING of one family**, not about "free
models" generally, and not about model weights. The design cannot separate tier from host stack —
there is no paid NVIDIA lane and no vendor-free lane for this family — so the claim is scoped to
the lane pair, and the specification says so rather than pretending otherwise.

Secondary (descriptive, not gated): the rung-dependence of the delta. Prior corrected data reads
~+6pp at M20 and ~0 at M30 (E-db428ac92c6d), so H1 is tested at M20 and the M30 leg is collected
to *replicate or refute the rung-dependence*, not to pool with M20.

Why "heuristic-resistant stratum": the raw band delta is NOT a reasoning gap. A one-line non-LLM
heuristic (count of five integers coprime to 30) scores 0.5225 on fresh tasks while the free-host
solver scores 0.4794 (C-82fe472469ca) — so up to the whole raw delta could live in the
heuristic-attainable region. A reasoning-capability gap must be measured where non-reasoning
methods fail.

## Design

**Arms.** Two lanes, one family, from `VERIFIED_SOLVERS` (ergon/probe/solver.py):
- FREE: `nvidia:deepseek-v4-flash` (model_id `deepseek-ai/deepseek-v4-flash-0731`, integrate.api.nvidia.com)
- PAID: `deepseek:deepseek-v4-flash` (model_id `deepseek-chat`, api.deepseek.com)

**Rungs.** M20 and M30 of the nearmiss ladder (`task_gen.py` generators already pinned by sha in
prior reads). Rungs are analyzed separately, never pooled — the corrected campaign data shows the
delta is rung-dependent (+6pp at M20, ~0 at M30).

**Manifest construction (per rung), $0, before any API call:**
1. Generate fresh tasks at a new seed with the pinned generator; record generator sha256.
2. Score the full non-LLM control battery (`task_controls.py`, including the coprime-to-30
   heuristic and the method-census controls) on every item, offline.
3. Partition: HEURISTIC-RESISTANT stratum = items where EVERY non-LLM control answers wrong;
   REPRESENTATIVE stratum = a simple random sample of unfiltered items.
4. Target sizes per rung: **320 resistant items + 200 representative items = 520 items**.
   Generate-and-filter until 320 resistant items exist (expected resistance fraction ≈ 0.48 from
   the 0.5225 heuristic score, so ~670 raw generations per rung).
5. Re-run the control battery ON the frozen resistant stratum. If any non-LLM control scores
   ≥ 0.40 on it, the stratum is not resistant: add that control to the resistance filter and
   regenerate (max 2 iterations; if still ≥0.40, proceed but stamp that control's score beside
   every reported delta, per the C-82fe472469ca claim ceiling).
6. Pin the manifest by sha256 and commit it BEFORE the first API call. The pin is never widened;
   any replenishment is a second pinned block under the block-B precedent
   (`PREREG_block_B_merge_rule_2026-08-25.md`), whose merge rule can refuse.

**Chance floors, stamped per stratum, computed from the frozen manifest:** the family's documented
chance floor is 0.25; the attainable-without-reasoning floor on the RAW family is ~0.52
(C-82fe472469ca); on the resistant stratum the battery floor is 0.00 *by construction against
the known battery*, so the stamped floor there is max(uniform-guess floor over the answer
alphabet, majority-class rate of the frozen stratum) — computed and committed with the manifest,
before collection.

**Collection.**
- Each item goes to BOTH lanes: paired design.
- 2 reps per item per lane (rep-1 = primary "cold accuracy", rep-2 for dispersion/movable-share,
  matching the campaign's leveling machinery). Per rung: 520 items x 2 lanes x 2 reps = 2,080
  calls; both rungs = **4,160 calls** (2,080 free, 2,080 paid).
- Paid cost: ~2,080 calls x ~1.5k tokens ≈ 3M tokens on deepseek-chat — well under a **$10 hard
  cap** (the lane's existing funding level). Free lane collected as a drip (existing
  `drip_coldband.py` pattern) to ride out HTTP-429 quota walls.
- **Interleaving control**: dispatch in ABBA lane order within blocks of 20 items, both lanes in
  the same wall-clock window, so served-model drift cannot masquerade as a tier gap.
- Identical prompt bytes, temperature 0, `max_tokens = 16384` on both lanes (the 8,192 cap
  produced a 3.13% truncation confound that flattered a gate — C-efb1cf440e10).
- R9 identity: every row carries executor, host, returned model version string, timestamp. If a
  lane's served version string changes mid-collection, the collection splits into blocks at the
  change and the preregistered block merge rule decides pooling (it may return FORBIDDEN).

**Metrics.**
- Primary: paired per-item exact-match delta (PAID − FREE), rep-1, resistant stratum, M20.
  Inference: exact McNemar on discordant pairs; 95% CI on the delta (Wilson on the paired
  difference). Expected SE at n=320, discordance ≈0.25: √(0.25/320) ≈ **2.8pp** — computed here,
  BEFORE the decision line was chosen, per the gate-must-exceed-measurement-error rule; the +4pp
  line sits > 1 SE from 0 and the design is powered ~0.81 for +8pp (z = 8/2.8 = 2.86).
- Secondary (reported, not gated): same delta on the representative stratum (with the 0.52
  heuristic floor stamped beside it); both deltas at M30; difference-in-differences
  (resistant-delta − representative-delta) per rung.

**Gate-fire preflight (must pass before the first real row is read):** every gate below is run
against synthetic known-bad rows and must REJECT them (`test_gates_fire.py` pattern — every prior
shipped defect had been exercised only in the pass direction).

## Controls

1. **Non-LLM control battery as the reasoning floor** (task_controls.py): defines the resistant
   stratum and stamps the attainable-without-reasoning floor beside every delta. A "reasoning
   gap" claim is only available where this battery fails.
2. **Paired same-item, same-bytes, same-window design**: removes item-mix, prompt, and
   time-of-collection confounds between lanes. No settled-vs-UNDECIDED comparisons: a delta is
   computed only between two legs that each LEVELED on their own (the exact failure that produced
   the retracted +14pp, C-84fef085ff15).
3. **Truncation quarantine**: rows with `finish_reason != stop` are QUARANTINED, never scored 0.
   Truncation direction is asymmetric — the vendor lane reasons longer before answering
   (solver.py L63), so truncation depresses the PAID leg and biases the delta TOWARD null; the
   confound direction is declared here, pre-collection.
4. **Transport quarantine**: transport failures are logged as residue rows (never scored), per
   the INVALID-TRANSPORT ledger convention; a leg with transport success < 0.99 is inadmissible.
5. **Contamination screen**: the campaign's SCREEN-LENIENT item screen runs post-hoc on both
   rungs; post-screen resistant-pair count must stay ≥ 300 (R13 floor), else replenish via a
   second pinned block, never by widening the pin.
6. **Version pinning**: returned model version strings recorded per row; version change mid-leg
   splits blocks; the merge rule (executable, can refuse) decides pooling.
7. **Interleaved ABBA dispatch** (above) against serving drift.
8. **Analysis script pre-committed and hashed** before any PAID row is read (D-5 / campaign
   precedent: compute_gates.py hashed before evidence).

## Preregistered falsifiers (each with an explicit numeric threshold)

- **F1 (hypothesis falsifier).** If the 95% CI upper bound of the paired resistant-stratum delta
  at M20 is **< +4pp**, H1 is FALSIFIED: no tier reasoning gap of the hypothesized size exists on
  this family. (Reported either way with the CI; a point estimate in (0, +4pp) with CI spanning
  +4pp reads UNDECIDED, not supported.)
- **F2 (reasoning-attribution falsifier).** If the difference-in-differences
  (resistant-delta − representative-delta) at M20 is **≤ 0** (point estimate), the observed gap
  is NOT attributable to reasoning: whatever separates the lanes acts at least as strongly where
  a one-line heuristic suffices. H1's mechanism claim dies even if F1 passes.
- **F3 (rung-dependence check).** The prior read (E-db428ac92c6d) predicts M30 delta ≈ 0. If the
  M30 resistant-stratum delta has |point| ≥ +4pp with McNemar p < 0.05, the "delta vanishes at
  M30" prior is refuted and gets a correction submitted to the wiki.
- **F4 (instrument falsifier — truncation).** Truncation rate > **1.0%** of rep-1 rows in either
  leg ⇒ that leg is TRUNCATION-CONFOUNDED and quarantined whole (C-efb1cf440e10 precedent); no
  delta is computed from it.
- **F5 (instrument falsifier — transport).** Transport success < **0.99** in either leg ⇒ leg
  inadmissible.
- **F6 (leveling falsifier).** A leg whose own leveling verdict is UNDECIDED or NOT-LEVELED at
  final n contributes to NO delta — the read is NO-READ for that (lane, rung) cell. Deltas
  against unsettled legs are the retracted-+14pp failure mode and are forbidden here.
- **F7 (stratum-integrity falsifier).** If, post-hoc, any single non-LLM control from the frozen
  battery scores ≥ **0.40** on the resistant stratum as collected, the stratum label is
  withdrawn and all deltas are reported as raw-band deltas with that control's score stamped
  beside them (no "reasoning gap" wording permitted).
- **F8 (power-floor falsifier).** Post-screen resistant pair count < **300** at a rung after one
  replenishment block ⇒ that rung reads R13-POWER-FLOOR-UNMET and halts unspent, exactly as the
  campaign halted itself.

## Stopping rule

Fixed-n design; no optional stopping and no peeking-based extension.
- Collection stops when each (lane, rung) leg has 2 reps on all 520 pinned items, OR at the $10
  paid-lane cap, OR after **14 calendar days** of free-lane drip (quota walls), whichever first.
- A leg short of its manifest at stop reads UNDECIDED (F6) — it is recorded, never differenced.
- Exactly ONE replenishment event is permitted (second pinned block, merge rule decides pooling);
  a second shortfall halts the rung under F8.
- Analysis runs once, from the pre-committed hashed script, after ledgers close and their sha256
  is committed in the same commit as the verdict (rows ship with the verdict — no verdict without
  rows).

## Unit of inference

The **item-pair**: one pinned task served to both lanes, within one rung. n = number of scored
pairs (post-screen, post-quarantine), NOT number of API calls or reps — SE is computed on pairs
(the wrong-unit SE inflated precision 57x once before). Inference is per (rung, stratum) cell via
exact McNemar; cells are never pooled across rungs or across strata. The population the claim
describes: nearmiss_mix items at the stated rung, resistant to the frozen 2026-09 control
battery, served to these two lanes during the collection window — nothing wider. Reps beyond
rep-1 inform leveling/dispersion only and add no inferential n.

## Prior work bearing on this design

- `ergon/probe/STATE_2026-08-25.md` — the leveled campaign state, the self-halt at
  R13-POWER-FLOOR-UNMET, the heuristic-floor finding, the nine instrument defects and the gates
  that now hold them (test_gates_fire, packet_invariants, task_controls).
- `ergon/probe/solver.py` (L33-50) — the lane roster and the HOST/FAMILY PINNING RULE this design
  inherits: same family on two hosts is never pooled and never counted as two families.
- `ergon/probe/ledgers/decision_M20_n200.json` — the settled paid M20 read (0.640, n=200) that
  formed one leg of the retracted +14pp comparison.
- `ergon/probe/FINDING_heuristic_floor_2026-08-24.md` — the 0.5225 coprime heuristic.
- `ergon/probe/PREREG_block_B_merge_rule_2026-08-25.md` — the executable merge rule reused here.
- `ergon/probe/ESCALATION_P1_BAND_2026-08-21.md` — the truncation confound escalation.
- Memory: `feedback_probe_lanes_and_burn` still records "+14pp host delta"; that figure is
  RETRACTED in the wiki (C-84fef085ff15) and this proposal uses the corrected ~+6pp/M20, ~0/M30.

## Evidence Wiki consultation log (queries run + object ids retrieved)

Client: `EvidenceWiki(machine='M1', agent='V1B-T2-wiki')`, canonical_revision 521.

1. `search_evidence('probe band host delta free paid tier')` → C-84fef085ff15 (RETRACTED, top
   hit), C-82fe472469ca, C-a2cba4576ecd, C-94fc12c3e6af, C-b2cebe551f3b, C-b037a49b641c,
   C-eb3e53602cce, C-a36c7e9fe323, C-3a1c49fa5a78, C-b5c1a85cca8b.
2. `search_evidence('chance floor exact match scoring probe')` → C-82fe472469ca (top),
   C-6d5d0b559a56, C-cd8ef5fb0a65, C-87adf28e3ab3, C-3d12c440f087, C-84fef085ff15,
   C-353ec1eb022a, C-ec2958821325, C-b2cebe551f3b, C-0c169dd6e0d9.
3. `get_claim('C-84fef085ff15')` + `get_counterevidence('C-84fef085ff15')` → evidence
   E-db428ac92c6d (FAILURE/REFUTED): "withdrawn +14pp; corrected ~+6pp (free 0.5772 n=395 vs
   paid 0.640 n=200); at M30 the host delta is ~0"; gate note: no-pooling stands on R9 principle.
4. `get_claim('C-82fe472469ca')` + `get_counterevidence('C-82fe472469ca')` → evidence
   E-6f557652eb09 (heuristic CV 0.5700, fresh-seed 0.5225; solver 0.4794; chance 0.2500;
   confound ~+4pp = half the +8pp powering); claim ceiling: floor must be stamped beside any
   delta from this family. Relations R-7dfdc5ff4fd1 (→C-ba882ad5cc7e), R-58e83e981109
   (→C-353ec1eb022a, 2p(1-p) ceiling-read-as-floor retraction).
5. `related_findings('C-84fef085ff15')` → graph edges: none; semantic: C-3a1c49fa5a78,
   C-86e1de0ff3a2, C-efb1cf440e10, C-de8041cece4c, C-a36c7e9fe323, C-e5e726a050c1,
   C-fff52fca02a0, C-55004a4674b8, C-053572137688, C-b2ce4f35aa58 (similarity only).
6. Negative-evidence query: `search_evidence('retraction withdrawn artifact host solver
   truncation probe')` → C-84fef085ff15 (RETRACTED), C-efb1cf440e10 (truncation-confounded
   band read, OBSERVED), C-de8041cece4c (RETRACTED), C-b037a49b641c (RETRACTED),
   C-353ec1eb022a (RETRACTED), C-ec2958821325 (R13 floor resolution), C-aba202675bd8.
7. `contradictions()` → one open pair: R-e68c9331eca2 (C-3a1c49fa5a78 vs C-3d12c440f087,
   D-8 null vs D-5 positive, APPARENT_UNDER_DIFFERING_CONDITIONS) — not about the probe band.
8. `find_gaps()` → H-a86125892a3e, H-41f9f15ce208, H-bac36ae694a2, H-c9832bd95134
   (accessibility_geometry x llm_probe_band untested cell), H-7c607f34d50e, H-9b0a7922015e.

## Evidence that changed this design (specific ids + the concrete design decision each changed)

- **C-84fef085ff15 / E-db428ac92c6d (retracted +14pp; corrected +6pp M20, ~0 M30).** Three
  decisions: (a) the design is PAIRED and contemporaneous — a delta may only be computed between
  two legs that each independently LEVELED (falsifier F6 exists solely because of this
  retraction's mechanism: settled read vs n=40 UNDECIDED read); (b) TWO rungs are collected
  because the corrected evidence says the delta is rung-dependent, so a single-rung answer would
  be a wrong-population statistic; (c) the effect size H1 is sized against, and the +4pp line, are
  set from the corrected ~+6pp, not the retracted +14pp still present in project memory.
- **C-82fe472469ca / E-6f557652eb09 (0.52 non-reasoning floor; confound ~+4pp = half the
  powering).** Changed the primary endpoint entirely: raw band delta was demoted to secondary and
  the primary population became the heuristic-resistant stratum (manifest built by
  generate-and-filter against the control battery). The claim ceiling on this claim dictates the
  floor-stamping requirement in F7 and in the metrics section; its quoted "+4pp confound" is why
  F2 (difference-in-differences must be > 0) exists.
- **C-efb1cf440e10 (truncation dragged the point INTO the band).** Set max_tokens to 16384,
  added the 1% truncation quarantine (F4), and forced the pre-collection declaration of the
  confound's direction (truncation biases this design toward null, the opposite of the prior
  incident — the direction is declared so a null cannot be read naively).
- **C-ec2958821325 (R13 floor 300 met by block merge at n=405).** Set the post-screen floor of
  300 resistant PAIRS per rung (F8), the 320-item target with headroom above it, and the reuse of
  the executable block-B merge rule as the only replenishment path.
- **C-353ec1eb022a (2p(1-p) ceiling read as a floor — retracted).** Cautionary: every floor in
  this document (0.25 chance, 0.52 heuristic, majority-class stratum floor) is stamped with what
  it is a floor OF and computed on the frozen manifest, not reasoned from a formula.
- Consulted but did NOT change the design (listed for honesty, not thoroughness):
  `contradictions()` (the one open pair is about executable-history substrates, not the probe) and
  `find_gaps()` (H-c9832bd95134 flags accessibility_geometry x llm_probe_band as an untested
  cell — noted as adjacent future work, but this proposal measures a host delta, not
  accessibility geometry, and borrowing the gap here would be decoration).
