# INFERENCE HARVEST HANDOFF -- Ananke / PTE (2026-09-30, operator directive, window until 05:00 ET)

Directive: roles/Ananke/prompts/2026-09-30_inference_harvest/ (sha256 2c99c612...).
Artifacts, all in roles/Ananke/research/harvest/:
- PTE_CAUSAL_AUDIT_2026-09-30.md
- T_SWAP_REL4_INTERPRETATION_TREE.md
- PTE_INSTRUMENT_GAPS_AND_UPGRADES.md
- BUILDER_EXPERIMENTS_OPS.md
- independent reports H-IMPL/, H-SCI/, H-INST/, H-CHK/ (deposited verbatim with provenance)
Independent attacks: H-IMPL (implementation), H-SCI (interpretation), H-INST (instruments), and H-CHK (three
decisive checks, plan frozen by commit first). Compute: ~4 CPU core-h in small tests, one 1-min leased
GPU conformance run. No campaign.

## 1. Strongest new conclusions
1. **C1's comm-dependence control cannot fail. [V]** zero_comm is exactly .500 in 213/213 RELAY, 174/174 MAJ
   and 95/95 XOR rows, forced by the mirror-pair construction. COMM_DEPENDENT = SIGNAL in those families.
2. **Evolved PTE transport is one hop. [V]** 35+4+9 of 50 competent RELAY cells and 19/19 MAJ cells need no
   relay. Multi-hop has 2 marginal cells and no plant.
3. **The search fitness shaping pays one-sided (rectified) codes** (acc .75 plus the full contrast bonus).
   It is a plausible common cause of the presence, rectified and integrator patterns. Untested.
4. **4781b0a1's "joint carrier" and "not a majority" readings do not survive plant controls.** A count
   threshold with no joint logic reproduces the truth tables and phase effects, and a lossy true majority
   reads "not a majority". The one residue: the champion's pivotality (.10-.12) is lower than both
   plants'.
5. **The promoted swap_rel H2 interval is empirically inert. [V]** It equals REL3 on 439/439 real
   group-arms. About half of AUDIT3's consistency miss is plain threshold noise [V: 11.8 expected vs 22].
6. **lens.verify_reach's "applied" is not reach.** Its batch digest said "applied" while the readout was
   exactly NOT_REACHED. An exact per-world reach certificate now exists as a draft (H-INST pte_trace).

## 2. Claims weakened or killed
- WEAKENED:
  - C1 headline wording (causally verified / lattice-bound / size-free laws; only ONE law was scaled, and
    it is unreproduced);
  - "no integration beyond one sensor";
  - H6 ("search, not physics");
  - the relative swap as a CARRIER ruler;
  - 4781b0a1 joint carrier / not-a-majority.
- UNSUPPORTED as stated:
  - "no retention regime" beyond the 16 champions;
  - "84% stay CHANCE" as mechanism evidence.
- KILLED:
  - C1 MAJ/XOR REACH_BEYOND_HOP labels as evidence (a silent program scores 1.0);
  - the single-cue-twin swap as an integrator/store discriminator (it gives z = -1 by construction:
    H-CHK C3, which also refuted H-SCI's and my own proposal);
  - W-V's "readout Kp carries half the bit" (already killed by W-Y).
- ERRATA written: C1_ERRATA E-H1, E-H2, E-H5, E-H2b.

## 3. Bugs found / fixed
- FIXED (neutral; regression tests fail before and pass after; full CPU suite 229 passed; GPU conformance
  98 passed):
  - engine past-schedule overwrite;
  - Controls.label crash;
  - twin reach nearest-sensor keys (additive);
  - wave-D resume determinism;
  - vacuous lens_swap handoff clause;
  - deposit.py empty/undelimited refusal.
- NEW TOOL: tools/freeze_check.py (plan-before-results from git; REL4 PASS, W-O FAIL).
- RULE FIX: an empty CUDA_VISIBLE_DEVICES= does NOT hide the GPU on SKULLPORT [V]. Use -1 plus device="cpu".
  - Consequence: three workers touched the GPU briefly unleased, all disclosed: W-Y ~2 s, H-INST <1 s,
    and H-IMPL's first suite run.
- REPORTED, not fixed:
  - B2 seed reuse across families;
  - recorded vs actual dest_mode (951/1589 global rows);
  - inert transects;
  - env_permutation built on non-mirrored seeds;
  - swap_rel sd_floor on SE scale vs per-pair SD, and an FC model with K independent trials per pair vs
    2K correlated mirror trials (H16);
  - DESIGN s7 drift from envs.py without annotation.

## 4. Unresolved ambiguities
- XOR/FLIP/multi-hop NULLs: physics or search? Undecidable: no plant at any physics.
- 4781b0a1: why is its pivotality (.10-.12) below both a lossy majority (.38-.44) and a count threshold
  (.30)?
- Whether the fitness shaping term, not the task, selects rectified and integrator codes.
- Seed sensitivity near the certificate threshold: noise vs method (W-U's marginal-bound labels).
- diff_trace cost on dense champions is unmeasured.

## 5. Best future discriminating experiments (small; none is a sweep)
1. **XOR co-arrival plant.** A one-hop, jitter-0 physics where both cues land in one wake window. If the
   plant works and 8 searches fail, that is the first real H6 evidence. If the plant fails, physics binds.
2. **Forced multi-hop RELAY** (d = 2*radius) at the d9cc physics, 8 seeds, with the one-hop champions as a
   must-fail.
3. **ANANKE-14 shaping A/B.** The same search with w_contrast = 0 vs 0.10, on RELAY at the d9cc point:
   measure the share of rectified codes and accuracy.
4. **4781b0a1 residue.** A count-threshold plant at the CHAMPION's latencies and rectification. Does D_piv
   fall to ~.1?
5. **Lag-profile primitive** (twin-difference rate by cue lag) for integrator vs store.
- Explicitly NOT worth it: re-running the 125 uncovered AUDIT3 groups; further single-cell mechanism chains.

## 6. Builder primitives worth extracting
- Cross-engine (H-INST B1-B6):
  - stratified-statistics guard (Simpson flag, declared independence unit);
  - identity audit of controls/relations (forced-by-design detector: it would have caught zero_comm);
  - phase keys as a required census key;
  - margin-based replication gate;
  - difference-vs-use pairing;
  - lockstep intervention-reach certificate.
- Operational (BX-1..8): freeze_check (done), worker envelope guard, no implicit accelerator, Fabric
  release-by-token fix, deposit refusal (done), known-answer gate enforcement, "does the promotion change
  any real verdict" table, per-seat rolling compute ledger.
- PTE-specific drafts ready for plan-first promotion: diff_trace (exact difference cone with a closure
  invariant), reach_certificate, ProvenanceWorld (per-emission, flight+inbox tags).

## 7. Genuinely strange observations (do not normalize away)
- 613162a3 (MAJ, global): shuffle_dest .72 > normal .688, and a whole-network chaotic divergence
  (div_frac .98-1.00) that still scores ~.7. Unstudied.
- At the M2 physics, HOLD search gave 3/3 in-flight echoes (C1b), but W-L's n=0 HOLD control gave a local
  integrator. Same physics and GA, different mechanism class. The builder equivalence was never checked.
- 4ab2ba01 is a HOLD champion that needs the channel (zero_comm .5), although a 4-line latch scores 1.0
  there.
- 311c465f needs its distractors (.76 -> .55 without).
- 4781b0a1's pivotality is below every tested plant (item 4.2).
- The C1 "size-free" law is the one that failed reproduction.

## 8. Addendum 2026-10-01: H-PLANT (plan 01234c0ad; report H-PLANT/REPORT.md; principal review H-PLANT/PRINCIPAL_REVIEW.md)
Item 5.1 and part of 5.2 were run. These results update s4's "XOR/FLIP/multi-hop: undecidable":
- **FLIP @ d9cc: search-limited.** A 16-line plant scores .97-.98 (replicated on disjoint seeds) where
  C1's evolve cell 6f82f9c7 held .479. This is the first direct H6 evidence, for one cell.
- **XOR @ d9cc: physics-limited.** The light-cone bound caps any program at .574. XOR is reachable
  elsewhere in the C1 census (aa2b8d68, lo99 .636), and 17% of C1 XOR evolve rows are light-cone-capped
  below .60.
- **Multi-hop @ d9cc: physics allows it (plant .97-.98), but C1 never searched it.** fac4aaa2 is a
  transfer of a one-hop champion. H6 for multi-hop is untested there.
- **New gap:** a one-flag readout passes C1's XOR SIGNAL rule (.763). XOR claims need that control.
- Remaining from s5: 5.2 as an 8-seed search at d5 (a search, so it needs authorization beyond this
  harvest), 5.3 shaping A/B, 5.4, 5.5. None was self-launched.
