<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-AG; sha256(report)=6f5fab1d97ecf834; delimited; see REPORT.provenance.json -->
# W2-AG: PTE preservation register of strange observations (Ananke Wave 2)

Directory: roles/Ananke/research/harvest/wave2/W2-AG/. The deliverable is STRANGE_REGISTER.md.
- Scripts and outputs: ag_decompile.py, ag_dict_trace.py, ag_dict_trace2.py, ag_dict2.py, decompiled.json, decompiled_hopscan.json, dict_trace_4781.json, dict_trace2_4781.json, dict2_4781.json.
- CPU only (CUDA_VISIBLE_DEVICES=-1, cuda asserted unavailable), 2 threads, eager. No search. No git writes. Nothing outside W2-AG/ was edited.

## 1. Findings

**1. [V] The one-hop wall is exact, not just low** (SR-01). Confidence: high.
- In W2-I's hopscan outputs (W2-I/out/hopscan_*.json), 13 of 14 native 2-hop conditions have lo99 = hi99 = .500. The 7 laws' own rings are used.
- So the readout is identical in both mirror twins. No information from any trial, not even stale cross-trial residue, crosses 2 hops.
- The one exception is c16d5231 at d4: .498 [.4948, .500].
- Static decompile (no engine run; engine.py:310-318 and :358):
  - In 4 of 5 single-rule laws (4781b0a1, bbef66a1, 31cd2a8a, 62a7fff9), a site that never senses can never emit.
  - c16d5231's non-sensing sites do emit, but with zero payloads (presence only). It is also the only condition showing any variance beyond one hop.
- Strongest objection: Kp/WIMM offsets on ADDI lines were not traced, and the two 4-rule SETRULE laws were not read.
- Unresolved: whether this holds across all 69 SIGNAL champions.

**2. [V] 4781b0a1 carries its vote only through reverberation between adjacent cued sensors** (SR-03). Confidence: medium. This is a candidate, not a finding.
- Static reading:
  - Each sensor latches the sign of its last cue and emits while latched.
  - After its 2-tick cue, its payload is PAY1 = max(IN0_1, SENSE), i.e. only what it hears.
  - The readout is S0 = IN0_1 - 3, the last wake window's payload sum.
- Trace: under W2-M's DICT ablation, the actuator gets one 253 burst about 4 ticks after cue onset, then S0 = -3 at every readout. Every mirror pair is exactly .5, which reproduces W2-M's degenerate .500.
- Pre-stated check (ag_dict2.py docstring, 16 held pairs):

| sensors cued | acc [99% CI] |
|---|---|
| all 5 | .784 [.714, .846] |
| one adjacent pair | .573 [.529, .620] |
| one non-adjacent pair (both one hop from the actuator) | .500 [.500, .500], sd 0 |
| a single sensor | .500 [.500, .500] |

- This one mechanism plausibly explains four reported oddities: cluster-bound (W2-I F3), DICT = .500 (W2-M), pivotality below every plant (Wave 1), and non-sensors never emitting.
- It supports Wave 1's candidate "sensor-to-sensor relaying" (PTE_CAUSAL_AUDIT:116). It contradicts W2-E S6's plain k=1 threshold, which predicts DICT > .5.
- Strongest objection: one cell, 16 pairs. The pivotality link is inferred.
- Unresolved: a sensor-to-sensor edge cut, and W-V's D_piv measured on a reverberation plant.

**3. [V, from recorded outputs joined to row physics] MAJ champions at the M3 physics integrate near the any-program ceiling, and INTEGRATION can never fire there** (SR-04). Confidence: high on the numbers; the ceiling's assumption is W2-M's.
- The physics: ring 100, radius 3, async .8, lat 4 = delta 4, loss .3. Ceilings (W2-M attain.json): any program .701, single sensor .590.
- 11 SIGNAL rows sit at this physics. 8 have champion lo99 > .590; for example 0a23398f .695 (lo .648) and 18c218f5 .699 (lo .650).
- 6 of them beat W2-M's single-sensor transport.
- Strongest objection: the ceiling assumes S0 carries no information when the actuator is asleep at readout (W2-M:141).

**4. [V] The stale-information "exceedance" has a tail residue** (SR-14). Confidence: medium.
- Over the 259 A0 cells with ceiling .5: mean .5015, sd .0217.
- The top cell, 74b13c29 at .589, is 4.0 SD out, against about 2.9 SD expected for the maximum of 259; the next cell is .5625.
- One heavy-tailed draw; it does not reopen the explanation.

**5. [I] The decay floor recurs as an exploited substrate** (SR-12). Confidence: low-medium.
- It appears in 613162a3's persistence, in 311c465f's clock and in P-FLIP's decay failure. No isolating check was run.

**6. [I] 964053bb's payoff-free anti-teacher latch may be a w_any shaping fossil** (SR-06). Confidence: low. Not checked.

**7. Register content** (STRANGE_REGISTER.md s0-s3).
- 15 entries. Each has: the observation; its source (path:line); a status; whether the original interpretation died while the observation survived; the cheapest decisive test; and a cross-engine question phrased only from CROSS_ENGINE_THREADS.md and CROSS_THREAD_COMPRESSION.md, which are what I read. Two entries say none was found rather than invent one.
- Reading coverage: in full, W2-E, Q, I, R, D, L, S, T, M, P, U, O, W, J, A1 and K. Skimmed by grep: W2-B, G, H, A2, C, F, AC and AB.
- Archive of explained items: SR-X1..X7 (the Wave-1 s7 list) plus 3 more that are not reproduced or explained away.

**Ranking (strangest and most deserving):**
1. SR-01, the one-hop wall.
2. SR-02, distractor strobe and parity clock.
3. SR-03, 4781b0a1's adjacent-sensor reverberation.
4. SR-04, near-ceiling integrators the ruler cannot see.
5. SR-05, 613162a3 and the global paradox.
6. SR-06, anti-copy champions.
7. SR-07, the rule-mosaic lottery.
8. SR-08, M2 latch-as-needle.
9. SR-09, the FLIP landscape.
10. SR-10, one-tick mis-tuning.
11. SR-11, LATCHED-PARTIAL.
12. SR-12, the decay floor.
13. SR-13, 53e569f4.
14. SR-14, stale-information exceedance.
15. SR-15, sensitivity climbing at zero accuracy variance.

**Case for the top 3:**
- **SR-01.** The exactness (degenerate intervals; twin-identical readouts) plus the static muteness of non-sensing sites makes "one hop" a structural property of what C1 search produced. Every topology, size and transfer statement rests on it. And a 12-line flood that does cross 2 hops exists at d9cc.
- **SR-02.** Evolution recruited the environment's fixed schedule, and in one case even the distractor amplitude's bit pattern (63 and 65 kill it, 64 works). The mechanism class is decided by the search seed at identical physics (CTC H5 fails inside one cell). It is the nearest PTE case to CTC H6's missing "search-reachable but undesigned" mechanism.
- **SR-03.** C1's only INTEGRATION law has four separately reported oddities, and one pre-stated check gives a single candidate mechanism for all of them. If it holds, PTE integration uses a carrier that no packet-level instrument was built to see.

## 2. Proposed fixes
None. No executable defect was found, so no diff and no test.

## 3. Disagreements
- **W2-E S6 / finding 7** ("the k=1 threshold explains 4781b0a1's low D_piv"): incomplete. A one-copy threshold on direct traffic predicts DICT > .5. The observed result is exactly .500, and a non-adjacent pair is also exactly .500 (W2-AG check).
- **CTC H6** ("anything search-reachable that we cannot design? Not yet observed"): 613162a3 (the champion beats every plant at global topology) and the strobe/parity-clock champions are standing candidates. Both are noted, not claimed.
- **CTC deeper compression** ("the latch dominates HOLD"): under search at M2 it does not (SR-08).
- **The HANDOFF draft headline "evolved transport is one hop" as a sampling fact:** the comparative claim is indeed unsupported (W2-AC). But the 2-hop zero-variance cliff, together with the static muteness, is structural for the laws tested, not only a sampling fact.

## 4. Next questions (ranked)
1. Emitter census by site class over all 69 RELAY/MAJ SIGNAL champions: do never-sensing sites ever emit a non-zero payload? Under 0.1 core-h. This makes SR-01 structural or breaks it.
2. 4781b0a1: cut only sensor-to-sensor edges at the native ring (W2-I graph-variant style). Prediction: .500. Then W-V's D_piv on a reverberation plant (prediction about .1).
3. DICT-k curve (k = 1..5) at 0a23398f: monotone integration or a count step at the near-ceiling M3 cells (SR-04)?
4. Register trace of 2c300c47 and 311c465f under the first-slot-kept jitter edit. Prediction: an amplitude 64 -> 66 change inverts 311c465f around .5.
5. sens_any and sens_act of 964053bb, 22104294 and 545aff2f on their training seeds: are the anti-copy and teacher-copy latches w_any shaping products?
6. Symmetric-decay monkeypatch for 311c465f and 613162a3 (SR-12).
7. Network-majority readout for 613162a3, with LC2/epidemic renormalisation of the global A0 cells (SR-05).

## 5. Inference ledger
question | evidence | result | confidence | strongest objection | unresolved | next
- Is the 2-hop collapse exact? | W2-I hopscan JSON lo/hi | 13/14 degenerate .500; c16d5231 d4 tiny variance | high | one physics for 4/7 laws | other champions | Q1
- Do non-sensing sites emit in the hop-scan laws? | static decompile + engine.py:310-318, :358 | 4/5 single-rule laws: never; c16d5231: zero-payload presence | medium-high | Kp/WIMM not traced; 4-rule laws unread | dynamic census | Q1
- Why is 4781b0a1 DICT exactly .500? | trace: one burst, then S0 = -3 at every readout | the lone sensor's payload dies after its cue | high | one pair traced in detail | — | Q2
- Adjacent vs non-adjacent pair (pre-stated) | ag_dict2.py, 16 pairs | .573 [.529, .620] vs .500 [.500, .500]; single .500 | medium | one cell, 16 pairs | edge cut, pivotality | Q2
- Do M3-physics champions integrate below the ruler's reach? | W2-M score_signal + attain + row physics | 8/11 above the .590 single-sensor ceiling; near the .701 any-program ceiling | high (numbers) | ceiling assumption | DICT-k | Q3
- Stale-exceedance tail | rows join over 259 ceiling-.5 A0 cells | max 4.0 SD vs ~2.9 expected; next 2.8 SD | medium | heterogeneous per-cell variance | FP rate | W2-P Q5
- Wave-1 s7 list status | HANDOFF:104-113 vs W2-E/W2-Q/W2-I/W2-M | 2 explained, 1 explained (builder), 3 reproduced and mechanised, 1 label conflation | high | — | — | register s3
- Cross-cutting decay floor | W2-E:26, :29, :83; W2-L:55-58 | candidate substrate exploit | low-medium | no isolating check | symmetric decay | Q6

## 6. Compute used
- About 230 CPU-s, about 0.064 core-h, against the 0.3 cap.
  - Decompiles: about 10 s each, two runs.
  - DICT trace: 49 s. Readout series: 23 s. Pair check: 123 s.
  - Row and JSON joins: about 15 s.
- CPU only, 2 threads, every process under 3 min wall. No GPU, no leases, no search, no git writes.
