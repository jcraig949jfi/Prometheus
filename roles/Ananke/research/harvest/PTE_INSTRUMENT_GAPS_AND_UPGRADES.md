# PTE instrument gaps and upgrades (inference harvest, 2026-09-30)

Principal synthesis of H-INST (harvest/H-INST/REPORT.md; draft module H-INST/pte_trace.py, 23 known-answer
tests, principal re-run 23 passed) and H-SCI (harvest/H-SCI/REPORT.md), plus the principal's own checks.
Nothing here edits frozen C1/C1b semantics. Promotion of any primitive into prometheus/ananke needs a
separate, plan-first item.

## 1. What PTE currently cannot see (ranked by what it has already cost the record)

| rank | gap | cost in the record so far | upgrade |
|---|---|---|---|
| 1 | CONTROL THAT CANNOT FAIL (zero_comm in comm families) | C1's COMM_DEPENDENT / CAUSAL_SUPPORT counted a forced control as evidence. zero_comm is exactly .500 in 213/213 RELAY, 174/174 MAJ and 95/95 XOR rows (principal-verified). It is forced because mirror pairs share all physics draws and the actuator is never the sensor. | An identity audit (H-INST B2) run on every control before it is used as evidence. For comm families, replace zero_comm with a control that COULD fail. Example: the same champion on a task whose actuator is not a neighbour; a one-hop relay then MUST fail and a flood need not. |
| 2 | "applied" is not "reached" | lens.verify_reach's applied half is a whole-batch digest over all state and all ticks. H-INST test: 85 applied ticks, yet exactly NOT_REACHED at the readout. REACHED certifies the hook code, not the specimen. | **reach_certificate** (exact, per world: UNAPPLIED / NOT_REACHED / ABSORBED / REACHED_OUTPUT with a LOCAL / TRANSPORTED path). Only ABSORBED is an admissible null. |
| 3 | difference is not use | W-S's frozen cone predictor failed (it counted re-broadcasts the readout ignores); W-T: copies are not causal weight; W-V read "readout Kp differs 78-98%" as a carrier, but it was Kp[0], never read (W-Y). | **diff_trace** gives the exact difference cone with a closure invariant (0 unexplained on 5 physics). The cone is a NECESSARY set only; carrier claims still need a paired intervention (H-INST B5). |
| 4 | provenance of the bit at the readout | W-Y missed the readout inbox (Acc_sum) as a third carrier; W-V's TagWorld covers in-flight mail only. | **ProvenanceWorld**: group x emission-epoch tags through flight AND inbox, exact under SUM, invariant-checked every tick. provenance_swap / provenance_follow do per-emitter and per-epoch swaps. This implements T-INS-17. |
| 5 | local vs transported | Census "SITE" verdicts were phase readings of a transported bit (W-I). | L/X path flags in diff_trace (hold_latch LOCAL 16/16, echo TRANSPORTED 16/16). |
| 6 | the ruler's reach vs the claim | The absolute swap rule cannot call FLIP below normal ~.62 (fixed by swap_rel). INTEGRATION's lo99 > .70 cannot see noisy multi-sensor aggregation: H-SCI F5 found majority agreement .77-.84 > best single sensor in all 4 MAJ champions, including the "single-sensor" M3. | Per-sensor cue-twin census (flip only sensor j's input) as the integration ruler, and an attainable-range check for every gate (as in C4 review A1). |
| 7 | integrator vs lag-k store | Both mirror swaps AND single-cue-twin swaps give z = -1 for integrators and stores alike (H-CHK C3: twins get identical input after the swap tick, so an S swap moves A onto B's trajectory regardless of mechanism). | NOT a swap mode. Use a statistic not normalised by the twin effect: the twin-difference RATE per lag (a lag profile), e.g. W-L lagprofile or twin_profile rates. CORRECTED after H-CHK. |
| 8 | write authority | Static decompiles were ad hoc (the W-Y Kp confusion). | Dynamic: component_causes() (SENSED / TRANSPORTED / CARRIED / HOOK), implemented. Static: authority_map designed (dataflow over the reduced instruction fields). |
| 9 | distributed store, direction, heredity, self-maintained machinery | Unmeasured. Retention NULLs are single-world decoder NULLs (W-E, W-G); routing "never carries the bit" rests on w-only swaps. | Designed in H-INST s2 (site-subset truth table, edge-direction profile plus a reflection hook, Kp lineage via taint, ITI reach). None of these is urgent until a task needs them. |
| 10 | clock phase and seed marginality | 15/16 offsets of 4781b0a1 change class under a phase split (W-R); AUDIT3 consistency 92.7% (W-Z). | phase_keys as a required census key (B3); a margin-based replication gate (B4). |

## 2. Principal positions where the workers' views conflict or need scoping
- **reach_certificate vs lens.verify_reach.** Adopt the certificate for NEW work. Keep the plant half of
  verify_reach for "could this hook code act at all" (W-K). Do not retro-edit C1b.
- **diff_trace cost on dense champions** is unmeasured (4781b0a1). The first use of the promoted module
  should be one timing run at M = 32 before anyone plans with it.
- **H-SCI 12a (4781b0a1's "joint carrier" may be a noisy count threshold).** I agree it is untested, and
  it is the cheapest decisive check left on that cell: run a sum-threshold plant through W-P's truth
  table and W-V's classifier. If it reproduces AND/OR, DISTRIBUTED-NONMAJ and the phase effects, the
  chain reduces to "noisy count threshold".
- **H-SCI on W-V.** The majority positive control was lossless and deterministic, so "not a majority" is
  WEAKENED. Agreed; re-run PMAJ at the champion's loss and fanout.

## 3. Promotion order (each item plan-first, with known answers, no campaign)
1. reach_certificate plus diff_trace (closure invariant as a test). Replaces "applied" in new preregs.
2. ProvenanceWorld (per-emission swaps). Unblocks T-INS-17 without new instrument work.
3. (withdrawn after H-CHK C3) A single-cue-twin swap cannot separate integrator from store. Instead, add
   a lag-profile primitive: twin-difference rate by cue lag.
4. Identity audit of controls (B2) as a test utility. Would have caught zero_comm in C1 before the
   report.

## 4. Implemented and fixed during the harvest (principal)
- deposit.py refuses empty or undelimited reports (BX-5); tests fail 3/4 before the fix and pass 4/4
  after.
- tools/freeze_check.py (BX-1): plan-before-results from git, with the known answers REL4 PASS and
  W-O FAIL.
- COMMON_RULES_ARC3 s5 corrected: an empty CUDA_VISIBLE_DEVICES= does not hide the GPU on SKULLPORT
  (verified); use -1 plus device="cpu".
