# Ananke research backlog: temporal computation and distributed memory

Currency: 2026-09-27. A living document. Each Thread has: QUESTION / WHY /
EVIDENCE / UNCERTAINTY / CHEAPEST DISCRIMINATOR / LENS / NEW-LENS.
Status: OPEN, READY (a delegation file exists in threads/), CLOSED (with
the spike that closed it), SPLIT or MERGED. Consumption log at the end.

## A. Carriers (what holds the bit)

T-M2-1 CLOSED 2026-09-27 (S-M2): What encodes M2's in-flight bit?
  -> the sign of one payload component's in-flight sum (swap FLIPs). See
  C1B_REVIEW_AND_MECHANISMS s2.
T-M2-2 READY (threads/T-M2-2_interval_tuning.md): Is the echo interval
  set by the program or by the physics? Can one law hold several gaps?
  WHY: separates "delay line tuned by evolution" from "memory"; it
  decides whether PTE can ever produce interval-general memory.
  EVIDENCE: gap sweep peaks at 6-8, chance >= 12 (4/4). UNCERTAINTY:
  which dials set the round trip (lat_base, update_period, hop distance)?
  CHEAPEST: re-evaluate champions under lat_base +-1 and update_period
  1/3 with the gap re-tuned to the predicted round trip; then evolve with
  the gap drawn per trial from {6,8,10,12}. LENS: PTE. NEW-LENS: no.
T-M2-3 OPEN: Why does the code relabel across payload components (pay1 in
  3/4, pay0 in 1/4)? Is the hop-stage tag general? CHEAPEST: decompile
  the fresh champions (read-only; minutes). LENS: PTE.
T-M2-4 OPEN: Spatial extent. Which sites carry the echo? CHEAPEST:
  flush in-flight packets addressed to sites beyond distance d from the
  actuator, d = 1..3 (a between-tick hook). LENS: PTE.
T-DM-2 OPEN (specimen FOUND 2026-09-27: MAJ 4781b0a1, joint swap FLIPs,
  channel or site alone ~0.5 at mid-interval): Is any PTE mechanism genuinely JOINT (the bit only in a
  combination of carriers)? NEXT: map the split over ticks and sites
  (per-site flush + per-tick joint swaps), and test for synergy (dit). WHY: joint or synergistic carriers are what
  standard storage/transfer measures misattribute. CHEAPEST: search the
  C1 SIGNAL cells for single swaps that are CHANCE but a joint swap that
  FLIPs. LENS: PTE + dit (synergy).
T-DM-4 OPEN: Regeneration. After a full channel flush, can site state
  rebuild the bit? (None expected for M2.) The instrument is the
  flush-then-watch test. LENS: PTE.

T-CT-1 OPEN: Carrier heterogeneity inside C1 families. At mid-transit,
  RELAY champions carry the bit in the channel (3/4) or in site state
  (bbef66a1: a site-latched bucket brigade). MAJ: channel (2), site (1),
  joint (1). WHY: family labels hide carrier diversity; the North-Star
  question is which physics favours which carrier. CHEAPEST: the full C1
  SIGNAL carrier table (T-INS-1 step 4) plus a regression of carrier class
  on physics dials (decay, loss, update mode, caps). LENS: PTE.

## B. Configuration vs memory

T-M3-1 DONE (W-B): bootstrap-only holds for M3 (a zero-default artifact; a one-rule law is bit-identical) and for 64% of 42 cells; 29% are a readout-local per-tick conditional branch; r is never the carrier (0/18 FLIP). Split into T-BR-1 (decompile the branch; b59e6c3a, 63d17a90), T-BR-2 (HOLD sample/hold alternation; the 311c465f distractor dependence), T-BR-3 (a lineage-aware recount), T-INS-6 (r := 0 as the default in any prereg that asks whether rules are used). Was: Is SETRULE's
  evolutionary role in PTE mostly ESCAPING random initial rules? WHY: if
  so, the "rule switching" dial measures an init artefact, which changes
  how C2 should treat it. CHEAPEST: re-run the M3 champions with r
  initialized to 0 everywhere (freeze from the start then equals normal?),
  and census SETRULE usage across all C1 SIGNAL cells with rules > 1.
  LENS: PTE.
T-M3-2 OPEN: Why does M3's in-flight swap reach only 0.33, not ~0.13?
  Candidates: dup copies at ro+1, the async inbox, cue packets emitted
  after mid-delta. CHEAPEST: swap at several ticks (t0+1..t0+3) + swap
  the inbox too. LENS: PTE.
T-CF-1 OPEN: A general configuration detector. For any champion, measure
  whether r, w or Kp differ between mirror partners (cue-bearing) or only
  change early (configuration). CHEAPEST: the E1 census over all C1
  SIGNAL cells. LENS: PTE.

## C. Timing

T-TM-1 PARTLY ANSWERED (W-C): 7/13 specimens carry the cue as WHO FIRES (presence). Timing of arrival alone is still untested. Original: Does ANY evolved PTE law carry information in timing alone?
  WHY: Aether says timing-not-content; PTE so far says content. CHEAPEST:
  lag and count decoders + the delay swap over all C1 SIGNAL comm cells.
  If none: the lens question becomes "which physics makes timing codes
  win?" (sync vs async, jitter 0). NEW-LENS: possibly (a timing-only
  channel dial: payload-free packets). LENS: PTE, cross-engine with Aether.
T-TM-2 OPEN: Deadline vs code vs tolerance as a routine timing
  fingerprint (latency +-1, +-2) for every mechanism label. LENS: PTE.

## D. Instruments

T-INS-1 DONE 2026-09-27 (instruments/INSTRUMENT_CARRIER_SWAP.md; 10 known-answer tests; arm_identical flag). Step 4 (a C1-wide carrier table) is still OPEN as T-CT-1. Was: Promote the
  mirror-pair carrier swap to a first-class PTE assay (lens.py -> tested
  module + fixtures: echo plant FLIPs on channel content, latch plant
  FLIPs on S). WHY: it is stronger than every C1b label. LENS: PTE.
T-TA-1 DONE 2026-09-27 (instruments/INSTRUMENT_TEMPORAL_REACH.md; lens.cue_arrival_profile + reach; known-answer tests). The per-site profile is OPEN (F1). Was: cue_arrival_profile
  as a reach check for every windowed ablation; the WINDOW_UNREACHABLE
  label. LENS: PTE; fleet (T-X-4).
T-INS-2 OPEN: Per-component and per-edge census (replace the fixed pay0
  census). LENS: PTE.
T-INS-3 OPEN: Store champion genomes for every replication search (C1b S2
  omitted them; regenerated bit-identically 2026-09-27). LENS: PTE.
T-INS-4 OPEN: Relative thresholds for kill/drop (relative to normal),
  for use in any future prereg. LENS: PTE.
T-INS-5 OPEN: Information-dynamics screening with channel variables
  (JIDT/IDTxl), validated first on the JIDT CA example, then on the echo
  plant (known answer), then on M2. LENS: PTE + external code.

## E. Cross-engine and external

T-X-1 DONE (W-C): the contrast as framed DOES NOT HOLD. The real axis is the receiver operator (add vs arbitrate-replace) + code/data separation. Split into T-WC-1 (two-axis carrier reporting: physical class x reader verdict), T-WC-2 (emission cost -> presence codes; QUEUED Q2), T-WC-3..5 (Aether proposals: fwd vs fwd_add; freeze flags vs bytes; erase-on-collision; Aether owns them).
T-X-2 OPEN: Cosmos P1/P2 vs PTE carrier swap cross-validation (gated on
  Cosmos's sealed work). LENS: cross-engine.
T-X-4 READY (threads/T-X-4_intervention_reach.md; W-D mined 8 cases in 5 seats: no single pattern; 3 checks + an identical-arms alarm cover all). Research question, NOT a fleet rule.
T-D1 OPEN: reach counter beside every lens verdict (generalizes cue_arrival_profile). LENS: PTE.
T-D2 OPEN: plant library per lens intervention (must-flip + must-not-flip). Partly done by the test fixtures. LENS: PTE.
T-D3 DONE: arm_identical flag in carrier_table.
T-X-5 OPEN: CA carrier model (Herakles EvCA rules, domain/particle
  filter). LENS: other engine + theory.
T-EXT-1 READY (threads/T-EXT-1_prior_art_followups.md): Turn the prior-
  art raid into tests (the ping probe; the gap-vs-latency law; a
  simulator-state audit in the Thompson-FPGA spirit). LENS: theory +
  PTE.
T-EXT-2 OPEN: Fossilize a reservoir / echo-state reference system (the
  vault has none). LENS: Techne.

## G. Retention (SI01 successor)
T-RET-1 DONE (W-E): preregistered verdict NO (no recoverable retention at
  j >= 2 by the single-world decoder). Found: frozen cue-signed SCARS in
  non-decaying plastic stores (w, Kp, S), never read; one exploratory
  integrator (f7e62fe3 w_sum, 0.88-0.97 with a history-aware decoder).
  Retention follows the physics (decay 0 + plastic stores), not the
  carrier class.
T-RET-2 OPEN: preregistered confirmation with the history-aware decoder
  as primary (f7e62fe3 / fresh3 / 0ad7dc00 / 6a47bd68; k in {2,3,5}).
  READY in substance; package = W-E REPORT.
T-SI-SCAR OPEN: the SI successor around the actual carrier. Is the
  f7e62fe3 w-scar irreversible (can later input erase it = twins merge)?
  Can it ever become effective? Gate: T-RET-2 confirms first.
T-RET-3 OPEN: where the scars sit (per site).

## F. Environment and distributed causality

T-ENV-1 OPEN: PTE has a write-free environment, so environmental memory
  cannot arise. Is a "writable field" dial worth adding (stigmergy)?
  NEW-LENS: YES, a world change. Only if T-TM-1 and T-DM-2 leave the
  carrier question open.
T-DC-1 OPEN: Distributed causality maps: which sites' channel content is
  necessary (per-site flush) for M2/M3. MERGED with T-M2-4 for M2.

## Consumption log
2026-09-27 (cont.): T-RET-1 closed by W-E; it split into T-RET-2, T-SI-SCAR and T-RET-3. The joint carrier T-DM-2/T-JC-1 was reframed: 4781b0a1 is source-latched regeneration (a sensor latch -> channel handoff at the transmission deadline), not synergy. New: T-JC-2..4. T-CT-1 dequeued to W-F.
2026-09-27 (continuation): instruments hardened (T-INS-1, T-TA-1 DONE). Workers dispatched: W-A (echo interval = T-M2-2), W-B (SETRULE = T-M3-1), W-C (PTE vs Aether = T-X-1), W-D (intervention reach = T-X-4, DONE). T-JC-1 (joint carrier) opened with a committed PLAN. The lease helper was added (the bus lease is unreachable, so the fallback is used).
2026-09-27 (late): the S-CT carrier table opened T-CT-1 and gave T-DM-2 a
  real specimen (4781b0a1 joint). C2 and SI01 reviewed (C2_SI01_REVIEW.md):
  both are deferred behind T-INS-1.
2026-09-27: T-M2-1 CLOSED (S-M2 decoded the carrier). The M3
  "configuration or memory?" question CLOSED as configuration (S-M3) and
  SPLIT into T-M3-1 (bootstrap as init artefact) and T-M3-2 (the 0.33
  residual). The temporal-window lesson SPLIT into T-TA-1 (PTE instrument)
  and T-X-4 (fleet). New from the spikes: T-M2-2 (tuning), T-M2-3
  (relabelling), T-INS-2/3/4 (census, genomes, thresholds). "Is M2
  memory?" was POORLY FRAMED; replaced by T-M2-2 (interval tuning).
