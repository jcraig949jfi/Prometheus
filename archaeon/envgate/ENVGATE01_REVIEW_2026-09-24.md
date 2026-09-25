+==============================================================================+
| ENVGATE-01 -- ENVIRONMENTAL GATING CAUSAL ASSAY -- REVIEW PACKET             |
| Author: Archaeon (M2 / SPECTREX5), session m2-db608f52                       |
| Date: 2026-09-24 (06:23Z - ~17:30Z; treatment run 06:40Z - 16:00Z)           |
| For: operator (HITL) + external reviewers                                    |
| Preregistered verdict: GATING_CAUSALLY_SUPPORTED + ALTERNATE_MECHANISM flag  |
| Archaeon's reading after forensics: GATING_PARTIALLY_SUPPORTED               |
|   (the band is a causal key; the single byte 128 is not)                     |
| Self-contained; directive verbatim at                                        |
|   roles/Archaeon/prompts/2026-09-24_environmental_gating/                    |
+==============================================================================+

0. SUMMARY
-----------------------------------------------------------------------------
Environmental input structure causally controls whether random vmcopy32
copiers establish lineages. The census's candidate key -- the single
exact-copy gate byte 128 -- is the wrong unit.
Copier-founded establishments (founders the frozen ruler says can
reproduce alone):
    U 47   SHAM 45   BLOCK_128 18   RESCUE_128 1   BAND_BLOCK 1
- Removing the 16-byte band abolishes establishment (46 vs 0 discordant;
  15/0 blocks).
- The equal-size sham removal does nothing (32 vs 30).
- Removing 128 alone costs about 60%.
- Restoring 128 alone rescues NOTHING (0 discordant).
Mechanism, measured afterwards:
- 128-gated copiers produce copier-grade offspring at inputs 120..131
  (right-shifted, NOP-sled copies that keep gate 128).
- Viable-offspring inputs available per copier: U 4.10, SHAM 4.10,
  BLOCK_128 3.10, RESCUE 1.00, BAND 0 -- the establishment order exactly.
- Branching-process reading: R0 ~ 60 x k/256 = 0.96 / 0.73 / 0.23 / 0.
The preregistered analysis returned GATING_CAUSALLY_SUPPORTED. Its rescue
component is an artifact:
- 69 of RESCUE's 70 establishments are host-labelled lineages in ONE
  takeover world (block 15), and that takeover was started by a copier
  gated at 255, not 128.
- The prereg's own block-level robustness test for the rescue contrast:
  p = 0.5.
The ALTERNATE_MECHANISM flag is real but means something narrower: inflow
tapes that are inert on their own execute resident copiers' code (foreign
execution) and emit copies of them. This is host-mediated reproduction.
It amplified residents, and in one world rescued a failing near-copier
lineage into a takeover. It does not originate new genomes.

1. OFF-MACHINE EVIDENCE COPY (item 1): OFF_MACHINE_COPY_BLOCKED
-----------------------------------------------------------------------------
Preferred destination: M1 (192.168.1.202).
Missing dependencies:
- no SSH key material on M2 (C:\Users\James\.ssh absent), and TCP 22 on
  M1 times out;
- SMB on M1 is reachable but share enumeration is denied for this account
  (no share or credential configured);
- no mapped drives, and no documented Prometheus transfer path.
No credentials invented, no cloud used.
Record: archaeon/envgate/OFF_MACHINE_COPY.json.
To unblock: an authorised M1 share (writable by this account) or an SSH
key pair. The copy plus per-file verification against MANIFEST.jsonl.gz
can then run unattended.
Local copies still stand: the bundle on C: (verified), and the ENVGATE-01
runs archived to C:\Prometheus-data\evidence\envgate01_2026-09-24\
(16 files, 20,184,006 B, all sha256 verified, read-only).

2. IDENTITY, DIGEST, PREREG (items 2, 3)
-----------------------------------------------------------------------------
Assay ENVGATE-01; mechanism digest da8a886fc9158b13. This is a new
identity, not a continuation of the 72-hour campaign; code under
archaeon/envgate/.
Commits:
  58f0463b2  engine, rulers, controls, preflight PASS
  f9c0bf3ec  PREREG frozen and pushed at 06:39Z
  (first treatment block launched 06:40Z)
  e15e4cde6  results + post-hoc forensics
  5649c78f8  forensic replay + viability map
The runner refuses to start unless 14 code/data sha256 hashes match the
prereg (engine, rulers, analysis, frozen z80atlas VM/engine/tasks/grammar,
census HITS/RESULTS).

3. DESIGN (items 4, 5, 10)
-----------------------------------------------------------------------------
Physics: the frozen z80atlas physics for one held configuration --
vmcopy32, ENDOGENOUS_COPY, well_mixed 128-cell ecology, implicit_survival,
ECHO_forced (one fresh uniform byte per case), local_byte mutation, fixed
env, unlimited resources, initial ecology empty.
Legacy mode reproduces z80atlas.engine.run EXACTLY: 3 seeds, per-epoch
population/births/fidelity and final population identical, 6,400-8,400
births each.
Inflow:
- K = 2,048 write-protected chambers are refilled every 64 epochs from the
  block's inflow stream, 1,024 refills.
- Chambered tapes are tested unchanged: no death, no mutation.
- Their births go to a random ecology cell.
- Result: 2,097,152 tapes per arm per block, 33,554,432 per arm in total,
  identical in every arm.
- Each world runs 65,536 + 181 epochs, with no step budget (a budget
  would make exposure arm-dependent).
Streams (arm-independent, seeds recorded): inflow(block), env(block, cell,
epoch), world(block), mutation(block).
Arms: every case draws two 32-bit words (u, v); base x = u >> 24. If x is
in the arm's blocked set it is replaced by pool[(v * |pool|) >> 32]; else
it passes unchanged.
  U           nothing blocked
  BAND_BLOCK  120..135 blocked
  SHAM_BLOCK  156..171 blocked
  BLOCK_128   128 blocked
  RESCUE_128  120..135 except 128 blocked (pool = the 240 values outside
              the band, so 128 stays at exactly 1/256)
RESCUE differs from BAND ONLY on cases whose base byte is 128.
Sham 156..171, frozen by rule before any ecology:
- among 16-byte intervals disjoint from the band, the fewest exact gates
  in the census, then the fewest birth-input incidences, then the
  farthest from 128;
- it has 0 gated-copier gates (the band has 89 of the 96).
Expected latent exact-copier arrivals per block, set from census density
9.6e-6 x 2,097,152: 20.1 (322 in total). Chance a single gate fires
during a 64-epoch dwell: 0.22.

4. RULERS, PREFLIGHT, CONTROLS (items 6, 7, 8, 9) -- all before treatment; PASS
-----------------------------------------------------------------------------
Pairing:
- every block's five arms received byte-identical arrival sequences
  (sha256 per arm, identical in all 16 blocks);
- regression tests show the sequence does not depend on which arms run.
Transforms (2.56M dry-run cases):
- U chi2 = 267 on df 255;
- 0 blocked values emitted in any arm;
- RESCUE P(128) = 0.003847 (z = -1.51);
- non-blocked values unchanged in every arm;
- RESCUE and BAND differ only where base = 128.
RNG isolation: inflow and environment code drew 0 times from the world
and mutation RNGs; exactly 2 words per case in every arm.
Memo and ruler: the VM memo equals vm.execute on 6,000 random calls; the
arrival ruler equals the frozen census ruler on 340 tapes.
Preflight: PASS, with no restrictions.
Controls (inserted, origin control_inserted, never scored), exact copies
from a chamber over 4,096 chamber-epochs per arm:
                      U    BAND  SHAM  BLOCK_128  RESCUE
  128-gated #0        16    0     14       0        15
  128-gated #1        12    0     12       0        11
  128-gated #2        12    0     13       0        13
  gated 127           13    0     11      11         0
  gated 243           13   11     12      13        11
  non-copier           0    0      0       0         0
  specimen (121)      17    0     21      17         0
Exact copies occur iff the gate is in the arm's alphabet. Note the
control rows also show that inexact births continue under the blocks
(128-gated #0: 1,634 U vs 1,547 BAND): the gate controls exact copying,
not reproduction.

5. OPPORTUNITY AND ESTABLISHMENT (items 11, 12)
-----------------------------------------------------------------------------
Arrivals per arm: 33,554,432. Ruler classes:
  INERT 32,826,479   TOUCH 725,392   WRITER 2,052   NEAR 199   SPAN 45
  EXACT_GATED 265    EXACT_UNGATED 0
Exact copiers:
- 7.9 per million (census 9.6, CI 7.8-11.7);
- 231 of the 265 are gated at 128;
- gate available by arm: U 265, BAND 3, SHAM 265, BLOCK_128 34,
  RESCUE 234.
Established (numerator / 33,554,432 arrivals):
                        U      BAND   SHAM   BLOCK_128  RESCUE
  all (prereg endpoint) 123     38    125      119        70
  copier-founded         47      1     45       18         1
  host / non-copier      76     37     80      101        69
Per latent exact copier (all): U 0.46, BAND 0.14, SHAM 0.47,
BLOCK_128 0.45, RESCUE 0.26.
Copier-founded establishments (112 in total):
- arrival -> first birth: median 2 epochs (max 38);
- persistence after the founder's removal: median 357 epochs
  (180..2,293);
- peak population median 62; max generation median 13;
- mean fidelity median 0.17; exact-birth fraction median 1.6%.
- Founder gates: 128 x75, none (near/span) x22, 127 x10, 255 x4, 129 x1.

6. PAIRED CAUSAL CONTRASTS AND RESCUE (items 13, 14)
-----------------------------------------------------------------------------
PREREGISTERED (arrival-level exact McNemar, Holm, all lineages):
  C1 U > BAND       115 vs 30   p = 3.1e-13   significant
  C2 U > SHAM       103 vs 105  p = 0.58      not significant
                    (specificity holds)
  C3 U > BLOCK_128  106 vs 102  p = 0.42      not significant
  C4 RESCUE > BAND   63 vs 31   p = 6.3e-4    significant
  -> GATING_CAUSALLY_SUPPORTED
PREREG ROBUSTNESS (block-level sign test, reported but not decisive in
the prereg):
  C1 p = 3.1e-5 (15 of 15 non-tied blocks)
  C2 p = 0.87
  C3 p = 0.011
  C4 p = 0.5    RESCUE = 0 in blocks 0-14; all 32 of its excess is block 15
POST-HOC, copier-founded only (labelled, SENSITIVITY.json):
  C1 46 vs 0   p = 1.4e-14   blocks 15/0
  C2 32 vs 30  p = 0.45      blocks 6/7
  C3 37 vs 8   p = 7.7e-6    blocks 11/1
  C4  0 vs 0   no discordance at all
Rescue result: restoring byte 128 alone did NOT restore establishment.
The preregistered C4 significance comes from block 15, where RESCUE and
BAND were both taken over by arrival 1,212,310, a copier gated at 255
(outside the band). RESCUE then logged 69 host-labelled lineages to
BAND's 37. That is noise from non-independent lineages, not rescue.
Forensic replay (6 worlds: blocks 2, 3, 6 x U / RESCUE; admitted only on
byte-identical established arrivals; 6/6 admitted):
- U: the 44 lineages founded by 128-gated copiers made 59 of 60 exact
  copies at 128. Descendants keep gate 128 (46/47 samples). 9
  established; max generation up to 27.
- RESCUE: the 41 such lineages made only 6 exact copies, all by the
  chambered founder. Generation depth never exceeded 2. None established.
- The gate does not drift. The lineages fail because they cannot GROW.
Offspring-viability map (81 census 128-gated copiers, all 256 inputs):
- copier-grade children arise at 120..131
  (x: 120 3, 121 5, 122 7, 123 5, 124 7, 125 11, 126 20, 127 34,
   128 81, 129 57, 130 54, 131 48 copiers);
- 328 of 332 such children are gated at 128.

7. EVERY ESTABLISHED LINEAGE (item 15)
-----------------------------------------------------------------------------
All 475 are listed with block, arm, arrival, tape sha, founder class,
gate, births, exact, peak, generation and persistence in
archaeon/envgate/ESTABLISHED_LINEAGES_TABLE.txt.
Full records: LINEAGES.json and runs/block_BB.json (arms.<arm>.lineages),
archived with sha256.
Takeover worlds (ecology ends >= 90% full): 6 --
  block 15 in all five arms; block 13 in BLOCK_128 only.
They contain 340 of the 363 non-copier establishments.
Resident genome of block 15 U: an EXACT_UNGATED copier (exact at all 256
inputs), evolved inside the world. Gating DISAPPEARED once a lineage took
over.

8. NOVEL MECHANISM CANDIDATE (item 16): HOST-MEDIATED REPRODUCTION
-----------------------------------------------------------------------------
363 established lineages have founders the ruler calls non-copiers
(INERT 290, WRITER 58, TOUCH 15). All carry
NOVEL_REPRODUCTIVE_MECHANISM_CANDIDATE.
Test, block 15 U, 63 INERT hosts against the resident genome, all 256
inputs:
- 26 give births, 23 of them EXACT copies of the resident;
- all 26 via foreign execution (the host jumps into the neighbour window
  and runs the resident's code);
- first-birth fidelity to the host's own tape: 0.008.
Origin trace, block 13 BLOCK_128:
- a NEAR_COPIER (arrival 447,492: 18 births, 6 exact, dead by epoch
  14,072) was failing;
- INERT arrival 446,966, chambered in the same refill, began hosting it
  at epoch 14,001;
- within 500 epochs the host-labelled population held 128 cells at
  fidelity 0.96.
Reading:
- host execution is a real reproductive route in this substrate;
- it can convert a failing near-copier lineage into a takeover;
- it amplifies residents but does not originate genomes;
- under a parent-chain lineage definition it credits the host's label
  with the resident's reproduction.
This is preserved and reported. The primary endpoint and allocation were
NOT changed because of it.

9. FALSIFIERS (item 17)
-----------------------------------------------------------------------------
Frozen booleans:
  F1 BAND as U                         no
  F2 SHAM like BAND                    no
  F3 BLOCK_128 no effect               YES (all lineages); not so for
                                       copier-founded (47 -> 18)
  F4 RESCUE fails where 128 copiers
     entered                           no by the frozen rule; YES in
                                       substance (block-level p = 0.5;
                                       copier-founded 1 vs 1)
  F5 establishment mostly from
     non-copiers                       YES (explained: host labelling,
                                       section 8)
  F6 128-gated lineages establish
     without their gate                no
  F7 exposure/occupancy confound       no (pairing identical, 0 births
                                       into chambers)
Also, per the directive's list: gating disappeared inside takeover
lineages (they evolved ungated).

10. VERDICT (item 18)
-----------------------------------------------------------------------------
Preregistered, as computed by the frozen rule and left unchanged:
  GATING_CAUSALLY_SUPPORTED, ALTERNATE_MECHANISM_OBSERVED
Archaeon's assessment: GATING_PARTIALLY_SUPPORTED.
- Environmental input gating of establishment is causal and specific.
- The causal unit is the reproductive-input window (about 120..131)
  around the neighbour-window base address, not the dominant exact gate.
- Removing 128 costs a large share; supplying 128 alone is insufficient.
The two prereg defects that produced the stronger label:
  (a) lineage identity by parent chain, so hosts are credited with
      residents' reproduction;
  (b) an arrival-level test that assumes arrivals are independent, which
      takeover worlds violate.
Both are recorded for any ENVGATE-02. Neither was changed after the fact.

11. RECOMMENDATION (item 19) -- operator's call; no campaign launches without review
-----------------------------------------------------------------------------
A general random-inflow ecology is now justified in principle, with two
conditions:
- The environment demonstrably gates establishment, so the next
  open-ended ecology should vary environmental information structure
  while staying mechanism-agnostic, as the directive's own branch says.
- It must expect host-mediated reproduction: inflow facing an occupied
  ecology is not a neutral supply of candidates. Chamber-to-ecology
  contact is itself a reproductive channel.
Before it, Archaeon's lean:
  (i)   fix lineage identity to follow genetic ancestry (the engine
        already carries donor-aware ancestry sets);
  (ii)  make the block (or cluster) the primary statistical unit;
  (iii) optionally ENVGATE-02, a small preregistered test of the window
        mechanism's prediction: blocking 129..131 should suppress more
        than blocking 120..127, since right-shift offspring dominate
        viability (57/54/48 copiers vs 34 at 127 and <= 20 below).
Also pending: the off-machine evidence copy needs an authorised
destination.

12. QUESTIONS FOR THE REVIEWER
-----------------------------------------------------------------------------
Q1 Should the frozen label stand as the record when forensics show its
   rescue component is a host-labelling artifact from one world, or
   should the record carry only the qualified reading?
Q2 Is "copier-founded" (the ruler class of the founder) a fair post-hoc
   exclusion, or does it bias against genuine non-copier innovations?
   Section 8 suggests the excluded class is hosting, not innovation.
Q3 Is the branching-process reading (R0 = 60 x k/256, only case 0
   reproduces) too simple, given overwrites, occupancy and host
   amplification?
Q4 Does host-mediated reproduction make chamber designs unsuitable for
   the next ecology, or is it the phenomenon to study?

13. ARTIFACTS
-----------------------------------------------------------------------------
archaeon/envgate/
  mechanism.py, engine.py, ruler.py, block.py, analyze.py, run_assay.py,
  preflight.py, lineages.py, sensitivity.py, forensic_replay.py
  PREREG.json, PREFLIGHT.json, RESULTS.json, RUNS_MANIFEST.json,
  LINEAGES.json, SENSITIVITY.json, FORENSIC_REPLAY.json,
  OFFSPRING_VIABILITY.json, ESTABLISHED_LINEAGES_TABLE.txt,
  OFF_MACHINE_COPY.json
archaeon/tests/test_envgate.py (9 tests)
Run state: archaeon/envgate/runs/ (gitignored) and
  C:\Prometheus-data\evidence\envgate01_2026-09-24\ (verified, read-only)
Directive: roles/Archaeon/prompts/2026-09-24_environmental_gating/

+==============================================================================+
| END. A null or a demotion would have been acceptable; the result is a        |
| real environmental lever whose key is not the one the census proposed.       |
+==============================================================================+
