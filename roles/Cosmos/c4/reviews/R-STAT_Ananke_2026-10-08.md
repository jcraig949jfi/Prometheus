# R-STAT review of C4 DESIGN v0.2: FINAL (Phase 2)

**Reviewer:** Ananke, lens R-STAT. Assigned by Aporia comms #1137 (CWO-2026-09-30C). Phase 2 was opened by Cosmos's
delegation, comms #1883 (2026-10-08).

**Material.** Read at origin/main 0b8e3740b on 2026-10-08:
- roles/Cosmos/c4/: DESIGN_C4.md, REVIEW_BRIEF_v0.2.md, S0_TRIVIAL_RULES.md, VISIBLE_FAMILY_CONTRACT.md,
  POWER_S0_v0.2.json;
- prometheus/cosmos/c4/: power_s0.py and theseus_sediment/ (all 5 files);
- prometheus/cosmos/c3/*.py: the public certificate plus the newly published substrates, geometry, maps, law,
  attack, substitution and subst_run;
- prometheus/cosmos/hashing.py; prometheus/cosmos/tests/test_c4_family_theseus.py;
- roles/Cosmos/c3/runs/maps_s1/MAPS.json and SUBST_s1.json (summarised by script).

**Design under review.** DESIGN_C4.md, S0_TRIVIAL_RULES.md, VISIBLE_FAMILY_CONTRACT.md and power_s0.py are byte-unchanged
since my interim note (ded6f5729; no diff to origin/main). v0.2 is reviewed as written.

**Not read:**
- the branches cosmos/c4-v03 and bellerophon/c4-rmech-2026-09-30;
- any R-MECH review or Bellerophon material;
- any path containing "holdout" (D2).

**Contamination disclosure.** A helper agent gathered the Part-B evidence under these exclusions. Its greps for
"sysid"/"impulse" printed single lines from Cosmos campaign notes. One was STATUS_2026-10-01.md:42: "F1 BLOCKING (S1): a
guard-compliant SYSID coordinate (channel reliability over H = 1..16) passes". That line probably summarises the R-MECH
interim. Nothing beyond those lines was read.
- Of my findings, only I4's "probe-decode reliability" proxy is in the same territory. It is therefore marked
  POSSIBLY-CONTAMINATED and does not carry I4.
- I4 rests on the lag-1 predictability proxy and the disjoint integer-valued fraction.
- Cosmos and the operator should judge whether this matters for independence.

**Method.** Every number below was executed on CPU against origin/main code. The scripts are in the reproduction
section.

Format: `lens | section | severity | evidence | required change`.

## PART A: DESIGN REVIEW

The interim findings A1-A13 stand as written in R-STAT_Ananke_2026-09-30_INTERIM.md, and are incorporated here by
reference.
- A1 was re-executed today against main's unchanged power_s0.py. The family-constant cheat passes S0-A (a)-(d) in
  200/200 simulations.
- Phase 2 sharpens several of them with real family data:

**A1 (BLOCKING), now with observed base rates.** Per-family FUNCTIONAL rates among determinate worlds are:

| family | FUNCTIONAL rate | source |
|---|---|---|
| rnn | .895 (34/38) | public C3 maps, MAPS.json |
| graph | .314 (11/35) | same |
| stig | .775 (31/40) | same |
| theseus_sediment | 1.00 (50/50) | 50 natural worlds through c3/certify.py |

- That is a spread of .31 to 1.00, wider than the (.8 ... .2) spread in my interim simulation.
- Exposed quantities separate families well above chance (I4).
- The family-level shortcut that A1 describes is therefore not hypothetical at these families. A coordinate that
  tracks family will track base rate.
- The required change is unchanged: a within-family primary statistic, a per-family positive margin, a stratified
  sign-flip, and a planted family-constant cheat in s8 that must FAIL.

**A3 (REPAIR), now evidenced.** power_s0.py (lines 19, 38-39, 49):
- gives every family one base rate;
- uses independent errors;
- uses 400 flips and 400 resamples, against the 10000/2000 that DESIGN s3 (b)/(c) freezes.

The observed .31-1.00 spread makes that model clearly too favourable. The required change is as in the interim, and
it must use the observed per-family rates.

**A4, A5 (BLOCKING), unchanged.**
- S2 multiplicity makes a universal law fail by default.
- Law-search selection on the scoring worlds is still unaccounted for. The design names no discovery/confirmation split.

**New Part-A finding:**

A14 | R-STAT | s3 S0-B, s3 S0-A (d), s7 natural distribution | BLOCKING |
- **Evidence.** A family whose natural distribution contains one class leaves the per-family statistics undefined:
  - the foreign family is 50/50 FUNCTIONAL on its declared `sample_natural`, with no negatives;
  - BA needs both classes;
  - T2b (per-family class prior) is degenerate;
  - "in every family BA(cand) >= BA(T3)" in (d) is vacuous for that family.
- The REGISTERED filter removed nothing in Theseus at k = 2/4/8 (50/50 registered), so S0-A's stratum there is the
  whole natural distribution.
- The pooled statistics silently absorb a family that contributes only one class. In A1's terms, that family is pure
  base-rate signal.

**Required change:**
- a minimum per-family count of each class, in both P and the Q_A sample (e.g. >= 10 per class per family);
- a rule fixed in advance for a family that cannot meet it: it is excluded from S0 and counted against the
  ">= 4 families" requirement, or it is re-declared with wider native ranges before F-0002;
- report the per-family class counts in the frozen sample table.

A15 | R-STAT | s2/s3 meaning of FUNCTIONAL across families | REPAIR |
- **Evidence.** FUNCTIONAL is a significance call: effect > 3 SE over 1500 pairs (certify.py:61-71). It is not a
  size call.
  - A Theseus world in the author's own "stormy" corner (settle .1, scour .3, creep .3, flush .6, drift 2)
    certifies FUNCTIONAL at k = 8 with J_intact .262, against chance .25.
  - In the 50 natural Theseus worlds, the P2 effect ranges from .21 to 1.0.
- The label's practical meaning therefore varies with each family's noise level and detectability. "Predicts
  FUNCTIONAL" is not a commensurable target across families. This feeds A1: base-rate differences are partly
  differences in detectability, not in physics.

**Required change:**
- add a preregistered minimum effect size to FUNCTIONAL (or a three-way FUNCTIONAL / MARGINAL / NONE split);
- report the per-family distribution of effect sizes beside the class counts.

## PART B: IMPLEMENTATION DIVERSITY (I1-I5)

**Families on main.** Four:
- rnn, graph and stig: Cosmos, all in prometheus/cosmos/c3/substrates.py, all C3 families;
- theseus_sediment: foreign, 79dc4c4b8.

There is no new Cosmos-authored C4 mechanism on main.

B1 | R-STAT | I1, s7 family requirements | REPAIR |
- **Evidence.**
  - s7 requires >= 2 mechanisms not present in C3. One exists: Theseus.
  - The plan's ">= 1 new Cosmos-authored mechanism" is not on main.
  - power_s0.py assumes NFAM = 5.
  - Theseus is a 1-D periodic ring with deposit, decay/flush and np.roll transport, the same skeleton as stig. Its
    symbol is site-coded, and it has two compartments.
  - That is borderline for s7's rule: "if the foreign author independently builds a C3-like mechanism, Cosmos
    authors a second new one".
- **Required change:** author and commit the second non-C3 mechanism, under the same contract as the foreign author,
  before F-0002. Until then the family count is 4, with 1 non-C3 mechanism. The power analysis must use the actual
  family count.

B2 | R-STAT | I1 | NOTE |
The four mechanisms are mechanically different:
- continuous leaky-tanh reservoir;
- binary threshold network;
- stigmergic ring field with an integer agent;
- two-compartment sediment ring.

They differ in state type, update rule and noise model (substrates.py:57-60, 88-95, 118-126; world.py:102-122). I1 is
answered YES at the level of mechanism. B1 and B3 qualify how much independent variation that buys.

B3 | R-STAT | I2 | REPAIR |
- **Evidence.**
  - Every Cosmos constructor defaults to wseed = 0 (substrates.py:42, 72), and maps.build never passes a seed.
  - So every rnn world shares one W/Win draw, and every graph world with a given K shares one topology.
  - Within-family variation is knob-only on a single quenched sample. Theseus has no quenched randomness.
- **Consequence.** The effective number of independent "substrates" per Cosmos family is 1 (per K), not n_worlds.
  - This is a cluster below the family level, which the sign-flip and bootstrap ignore (compounds A2).
  - A law can fit idiosyncrasies of one random matrix.
- **No hidden shared core.**
  - Families share only the System/Task interface and swap_rows.
  - All three Cosmos families map symbols through a lookup table of size task.n_symbols.
  - There are no cross-family imports and no copied blocks. The Hybrid composite in substrates.py is not a C4 family.
  - I2 is answered NO SECRET SHARED CORE, with the quenched-wiring caveat.
- **Required change:** do one of the following, and make the inference unit match:
  - sample the wiring seed as part of the world (and include it in the natural and challenge distributions); or
  - declare the single wiring a fixed part of the family and treat every result as conditional on that draw.

B4 | R-STAT | I3, s4 S1 | BLOCKING |
**Evidence.** S1 is specified (DESIGN s4) but not implemented: there is no SYSID code on main. The specification
cannot be applied uniformly to the families as built:
- Arbitrary input symbols raise IndexError in rnn, graph and stig (an out-of-range symbol); negative symbols wrap
  silently through numpy indexing. Only Theseus accepts any integer. The three Cosmos families therefore violate
  VISIBLE_FAMILY_CONTRACT s2 ("must accept ANY input symbol sequence"), which the foreign author was held to.
- State kicks:
  - in stig a Gaussian kick raises IndexError, because position and the current symbol are integer state;
  - in graph a kick leaves the binary state space;
  - in Theseus it can make sediment negative.
  - The kick is undefined or non-physical in three of the four families.
- Readout and full state are identical in rnn and Theseus, so any bottleneck coordinate is constant there by
  construction.
- G1 (machinery firewall) cannot pass as built: system.py:20 imports probe.Logit, so any SYSID module importing the
  System interface imports the certificate's probe.

A statistical design cannot be powered, or its multiplicity counted, before its measurement set exists.

**Required change:**
- implement S1 and commit it before F-0002;
- define the probes and kicks per state type (continuous, binary, integer), with each family declaring its legal
  perturbations;
- split System from probe.py;
- bring the Cosmos families up to contract s2-4: arbitrary symbols, plus declared meanings, ranges and a natural
  distribution;
- then re-run the reviews' S1 attacks on the implemented code.

B5 | R-STAT | I4, s5 S2 | REPAIR |
**Evidence.** The proxies are mine, standing in for S1 because no S1 code exists. On 50 worlds per family (the C3
lattice for the Cosmos families; `sample_natural` for Theseus):
- the fraction of integer-valued state entries does not overlap between families (rnn 0; graph 1.0; stig .67-.97;
  Theseus .49-.63);
- leave-one-out 1-NN family ID from lag-1 whitened predictability (full state and readout) is .84, against chance .25;
- all proxies combined give .865; a reliability proxy gives .72 (POSSIBLY-CONTAMINATED; see the disclosure).
- T3-DOWN's "exactly zero distance" registration is trivially met in continuous-state families, and removes nothing in
  Theseus.

Any coordinate that inherits the state type is a family ID in disguise. With A1, a family-ID coordinate plus
between-family base rates passes S0-A.

**Required change:**
- before freezing the coordinate set, run a preregistered family-ID test on every candidate coordinate (LOFO-free:
  plain cross-validated family classification);
- report it beside S2;
- any coordinate whose family-ID accuracy exceeds a frozen bound enters the law only inside a within-family
  statistic (A1 repair).

I4 is answered: the grammar AS SPECIFIED cannot yet be judged. The obvious realisations identify the substrate.

B6 | R-STAT | I5 | REPAIR |
**What the foreign family exposes in the Cosmos families' assumptions:**
1. **Contract asymmetry.** The Cosmos families do not meet the contract the foreign author was held to: arbitrary
   symbols, NATIVE meanings and ranges, a natural distribution (C3 NATIVE carries units only).
2. **A balanced natural distribution is assumed.** S0-B and T2b presume both classes occur naturally. Theseus's
   natural distribution is all-FUNCTIONAL (A14).
3. **"Registered" assumes discrete-state families.** It is a no-op on Theseus and on continuous state.
4. **History-free control.** Theseus's control zeroes the entire state, the current symbol included, while C3's N0
   keeps the current observation. The "history-free" baseline is not a single construct across families.
5. **Cost.** Theseus declares a native maintenance cost (transport_work); no Cosmos family does. Any law involving
   cost is foreign-family-only.

I5 is answered YES: it reveals several assumptions, and each is a required change (A14, B4, B5 and the N0 definition).

**Required change:** fix one history-free control definition across families, and apply the contract retroactively
to rnn, graph and stig.

B7 | R-STAT | I3/G3, s8 calibration | NOTE |
- The planted DelayLine has chain length k+2 (calib.py:74).
- The C3 world-seed pattern hashes k into the seed (maps.py:48-49).
- A SYSID that reuses either cannot be k-invariant. Build the planted controls and the SYSID seeds without k.

B8 | R-STAT | reproducibility | NOTE |
- No `hash(`, `__hash__` or PYTHONHASHSEED dependence was found in public prometheus/cosmos code. Seeds come from
  sha256 over canonical JSON (hashing.py:38-39, 119-121).
- The process-salted tuple-hash seeding that Cosmos reported (#1883) therefore lives only in the R-MECH harness, not
  in the C4 design code.
- certify.py:43 fixes the P1 permutation stream at default_rng(12345) for every world. This is fine for
  reproducibility, but the P1 null is the same permutation draw in every world, so record it as a shared-null cluster.

## OVERALL VERDICT: REVISE

C4 is worth building. The question is well posed, and the S0 split, Certificate B and the foreign-family commission
are the right instruments. But v0.2 cannot proceed to F-0002.

**BLOCKING:**
- A1: the pooled-BA base-rate shortcut, now evidenced by .31-1.00 per-family rates and high family identifiability;
- A4: S2 multiplicity makes a universal law fail by default;
- A5: law-selection inflation, with no discovery/confirmation split;
- A14: single-class families make per-family S0 undefined;
- B4: S1 unimplemented and not uniformly applicable; G1 fails as built.

**Before F-0002**, the minimum is:
- the A1 within-family statistic, with a planted family-constant cheat that FAILS;
- the A4 omnibus or Holm S2, with planted universal and family-specific laws simulated;
- the A5 discovery/confirmation split;
- the A14 per-family class minimums;
- the B1 second non-C3 mechanism;
- the B4 implemented S1, with per-state-type perturbations and System split from probe;
- the B5 family-ID screen on coordinates;
- the A3 power re-run at the actual family count, observed base rates, clustered errors and the frozen flip and
  resample counts.

**NOT_WORTH_BUILDING is not my verdict.** None of the defects is a reason the question cannot be answered. They are
reasons the current instrument would answer it wrongly: it is biased toward false PASS through A1 and toward false
"no law" through A4 and A6.

## Reproduction

All runs were on CPU, against origin/main, with the extracted files.
- **A1:** the interim snippet, unchanged, against prometheus/cosmos/c4/power_s0.py. Result 1.00.
- **Base rates:** class counts over roles/Cosmos/c3/runs/maps_s1/MAPS.json by family. For Theseus: 50 worlds from
  `theseus_sediment.world.sample_natural`, certified with prometheus/cosmos/c3/certify.py at k uniform {2, 4, 8}.
  Output: 50/50 FUNCTIONAL; k split 24/15/11.
- **I3:** construct each family through its public constructor and call step with symbol task.n_symbols + 50
  (IndexError in rnn, graph, stig), then add N(0, .1) to every state array (IndexError in stig).
- **I4:** 50 worlds per family; leave-one-out 1-NN family classification over per-world proxy features.

The scripts (cert_theseus.py, expose.py) are kept with this review's working files. They can be committed on request.
