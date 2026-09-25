# S4 -- candidate Cycle-9 manifest (FOR OPERATOR REVIEW)

**STOP STATE. NOT FROZEN. NOT LAUNCHED.** No hash is written into `PREREGISTRATION.md`.
No production observatory exists. There is no `CALIBRATION.json`; the calibration
output is `CALIBRATION_PREFREEZE.json`, and `controls.py` now writes the freeze name only
under `--freeze` (C9-D05). Freeze and launch need an operator instruction.

Currency 2026-09-24. Governing directive:
`roles/Nestor/prompts/2026-09-23_s1_s4_execution/DIRECTIVE_VERBATIM.md`.

## 1. Candidate manifest

Machine record: `MANIFEST_CANDIDATE.json` (`manifest.build()`); protocol version
`cycle9-verify-2-candidate`; 0 validation problems.

| hypothesis | rev B | candidate | runs | why |
|---|---|---|---|---|
| H1 cue gating | 60 bundles x 4 | **60 x 4, unchanged** | 240 | S1 found no validity reason to change it. The cell is EXTERNAL reproduction, which reproduces and mutates every epoch |
| H2 propagation | 16 old specimens x 5 seeds x 3 | **16 P-11 survivors x 16 seeds x 3** | 768 | panel rebuilt; see section 2 |
| H3 reservoir | 3 cells x 16 seeds x 3 | **3 pinned cells x 24 seeds x 3** | 216 | a moderate increase: the SE of an arm difference at p = 0.2 falls from 0.082 to 0.067 per pooled arm |
| H4 endogenous | 4 blocks x 16 pairs x 2 | **4 x 16 x 2, NOT enlarged** | 128 | the S1-B autopsy shows the assay needs redesign first (section 4) |
| **total** | 252 bundles / 752 runs | **452 bundles / 1,352 runs** | | |

## 2. The revised H2 panel

Rule committed before any S1-C result was read: `specimens.select_p11`, commit
`42cba0a3c`. There were 52 eligible candidates: 57 P-11 survivors minus 5 whose ENV_MIG
cells the Cycle-9 grammar rejects. The 16 chosen cover 13 of the strata. **None of the
rev-B specimens is retained**; only 2 of the old 16 survive P-11 at all, and neither
ranks first in its stratum. Panel hash `d52426aff80d509c...`.

| specimen | stratum | P-11 events | first P-11 donor fidelity | genome | axis |
|---|---|---|---|---|---|
| c2a87e5970ad345d-s80949-tL-a0 | NICHES_HIGH_MIG / Z8_64 | 5 | 0.969 | 64 | RECOMBINATION |
| dd30f47fda54b9d0-s46022-tL-a0 | WELL_MIXED / Z8_32 | 1 | 1.000 | 32 | RESIDUE_TRANSPORT |
| e16055dd06cff594-s37315-tL-a0 | NICHES_HIGH_MIG / Z8_SLOTTED | 1 | 0.984 | 64 | RECOMBINATION |
| 4931614d912c52b2-s1190-tL-a0 | RESERVOIR / Z8_32 | 1 | 0.938 | 32 | DELETERIOUS_LOAD |
| 7ae3f9c1437c8000-s54765-tL-a0 | WELL_MIXED / Z8_64 | 4 | 0.984 | 64 | RECOMBINATION |
| 08b4c94e2ea65998-s76929-tL-a0 | WELL_MIXED / Z8_SLOTTED | 1 | 1.000 | 64 | RESIDUE_TRANSPORT |
| 9cba7113df39009e-s3882-tL-a0 | COMPETENCE_MIG / Z8_64 | 1 | 1.000 | 64 | STASIS_ESCAPE |
| 48c75e149fc7d62d-s12269-tL-a0 | NICHES_HIGH_MIG / Z8_SEPARATED | 1 | 0.958 | 96 | RECOMBINATION |
| 2c45891544a22e46-s8700-tM-a0 | NICHES_ISOLATED / Z8_32 | 1 | 0.906 | 32 | TRANSITION_DETECTOR |
| 6da4c0b9a40141f8-s5058-tL-a0 | NICHES_PERIODIC_MIG / Z8_64 | 1 | 0.969 | 64 | RECOMBINATION |
| a62116831aa6d956-s7926-tM-a0 | RESERVOIR / Z8_64 | 1 | 0.953 | 64 | STASIS_ESCAPE |
| 193576337017c94a-s74845-tL-a0 | WELL_MIXED / Z8_SEPARATED | 1 | 0.969 | 96 | RECOMBINATION |
| 03650e1ad792eefa-s9040-tL-a0 | WELL_MIXED / Z8_SHARED | 1 | 0.979 | 96 | DAMAGE_CLIFF |
| cb7f5ca16e697938-s60768-tL-a0 | NICHES_HIGH_MIG / Z8_64 | 2 | 0.938 | 64 | RECOMBINATION |
| aaa8c7857c2e5f02-s7313-tM-a0 | WELL_MIXED / Z8_32 | 1 | 0.938 | 32 | RESIDUE_TRANSPORT |
| ffa6b3fb06df72a7-s55806-tL-a0 | NICHES_HIGH_MIG / Z8_SLOTTED | 1 | 0.984 | 64 | RECOMBINATION |

Arm B now implants the **donor genome of the specimen's first P-11-causal event**, and
those bytes are embedded in the manifest, so they are covered by its hash (C9-D10). The
primary endpoint is unchanged: `max_causal_replication_depth`, which on the pair tape is
now P-11 depth.

## 3. Timings and projection

`S4_TIMING.json` and `s4_timing.py`: **full-length** runs, one of every arm for every
specimen, cell and block (69 runs), on 6 workers to match the campaign. Seeds are
9,900,001, outside the manifest's range. **Wall time only is recorded, no outcome
field.** The 120-epoch smoke is not used, because P-11's cost is paid per event and does
not scale linearly.

| | mean wall per run | runs | CPU-hours |
|---|---|---|---|
| H1 (S) | 11.6 s | 240 | 0.77 |
| H2 (M, P-11 on) | 149.2 s | 768 | 31.8 |
| H3 (M) | 52.5 s | 216 | 3.15 |
| H4 (L) | 284.2 s | 128 | 10.1 |
| **total** | | 1,352 | **45.8 -> 7.6 wall-hours at 6 workers** |

Without H4 (option H4-0 below): 35.7 CPU-h, **5.95 wall-hours**. Both options are inside
the 5-8 hour target, and neither is padded. The campaign stops when the manifest is done.

## 4. H4: not enlarged; redesign needed (operator decision)

S1-B found that H4's endogenous arm **cannot reproduce**. SEEDED_READER has no ALLOC
or BIRTH code; with no births there is no mutation; and its held score moves only as
COEVO_ENV drifts. Block B (RANDOM) does not escape this, because S1-A finds zero births
in FREE-policy random populations. The exact matched control crossed first, at epoch 48.
Enlarging H4 to 32 pairs would buy a sharper estimate of an environmental coin flip.

Options, none implemented:

- **H4-0 (recommended for this cycle):** withhold H4 and record A-4 as withdrawn
  (unmatched control, Z80A-D04; frozen, non-reproducing population). This saves 1.7
  wall-hours.
- **H4-R:** redesign before freeze:
  - seed an ancestor that can reproduce endogenously, with a task reader appended, so
    the endogenous arm actually reproduces;
  - add a no-reproduction null arm to measure what environmental drift alone does to
    held;
  - make STATIC the primary environment;
  - count a crossing only when it is made by a genome absent at epoch 0;
  - make births > 0 a validity precondition for the endogenous arm.

## 5. Decision rules that need operator attention before freeze

1. **H2's rule is sized for 5 seeds** (B at depth >= 5 in at least 3 of 5; C in at most
   1). At 16 seeds I propose **B >= 8 of 16 and C <= 2 of 16**. Its power is 0.68 at a
   true B rate of 0.6 and 0.47 at 0.5. The worst case of false support when B = C is
   0.8% per specimen, about 12% family-wise over 16 specimens. The old rule reaches about
   10% per specimen when B = C is near 0.35, and scaling it proportionally (10 of 16,
   3 of 16) would *lower* power to 0.49. **Not applied**; PREREGISTRATION.md is
   unedited.
2. **Attainable range (C9-D12).** Across all 1,031 predecessor runs at tier L (4,000
   epochs), the maximum P-11 causal depth is **2**. H2 runs at tier M (2,000 epochs) and
   its bar is depth >= 5, which has no precedent. The information the extra seeds buy is
   mostly an upper bound. If no seed reaches depth 5, the 95% upper bound on the
   per-seed propagation rate is 0.17 per specimen (0.45 at 5 seeds) and 0.012 pooled
   over 256 arm-B runs. Consider adding depth >= 2 as a preregistered secondary readout.
3. **H3 validity (C9-D11, not repaired).** In pair-tape worlds the only lineage edges
   are pair events, and the P-1 certificate walks **all** of them. S1-C shows that in
   RECOMBINATION cells almost none are causal copies; the "parent" is the donor
   while the bytes came from a random splice mate. All three H3 cells are pair-tape
   RECOMBINATION cells. Options: restrict the certificate to P-11-causal edges, or
   re-pick H3 cells in EXTERNAL-reproduction worlds, where the runner records lineage
   exactly.
4. **P-11 authorship reading.** C4 reads the last value change, not the last write
   (P11_SPEC 3.1). S1-C reports both: 57 survivors under the primary reading, 48 under
   the literal one.

## 6. Proposed hashes (PROPOSED, NOT FINAL)

`PROPOSED_HASHES.json`, produced by `proposed_hashes.py`; every value can be recomputed.

| | value |
|---|---|
| proposed_protocol_hash | `b3c62220729ace5d4436aa2575df75cf77f6610ffe65e04f7e50f5589bc84cab` |
| manifest_hash | `71042bfb226721abe71663b6db2c3913c1a3917e173e66305d072ea17148eeae` |
| specimen_panel_hash | `d52426aff80d509cd6a16e8ddad3aea25a9265ee8ef079b7b1da8da81a4006fb` |
| grammar_hash | `61da6513ea0b36e04d4b2164a208fe4e1fd700e078076db847dc037f1c327f4e` |
| constants_sha256 | `ade1f755eaff9598e32eb9c768bd57b7094b4e0c7de555b0ebf2eb34b0b019ce` |

The rev-B values are kept under `supersedes`. Its `proposed_protocol_hash` had no
derivation anywhere in the repo (C9-D08).

Gates: `run_gates.py` passes 9 of 9 (`GATES_PREFREEZE.json`). The suite is the VM
selftest, T-P1..P10, T-P4, T-P5, T-P7, T-P11 (14 checks), T-S3 (12 checks), the P-6
report audit and the calibration controls (PREFREEZE).
