+==============================================================================+
| Z80 x ATLAS -- OPERATOR RULINGS 1-4 EXECUTED -- FOLLOW-UP REVIEW PACKET      |
| Author: Archaeon (M2 / SPECTREX5), session m2-db608f52                       |
| Date: 2026-09-24 (work 00:39Z - 03:10Z)                                      |
| For: operator (HITL) + external reviewers                                    |
| Status: ALL FOUR RULINGS DONE.                                               |
|   1 seeded moat ledger CLOSED                                                |
|   2 copier census LOTTERY_CONSISTENT                                         |
|   3 evidence bundle verified                                                 |
|   4 sampler fixed + launch preflight                                         |
| Self-contained. Follows Z80ATLAS_POSTCAMPAIGN_REVIEW_2026-09-23.             |
| Rulings verbatim at:                                                         |
|   roles/Archaeon/prompts/2026-09-23_postcampaign_rulings/                    |
+==============================================================================+

0. SUMMARY
-----------------------------------------------------------------------------
- The mystery is essentially explained by a measured prior.
  * Uniform random 32-byte vmcopy tapes are exact self-copiers at a rate of
    9.6e-6: 96 per 10 million, 95% CI [7.8e-6, 1.17e-5].
  * 99% of those copiers are input-gated, and 85% copy exactly only when
    the environment's input byte equals 128, the neighbour window's base
    address.
  * Across the campaign's random-origin endogenous worlds, this prior
    predicts lambda = 6.86 (95% CI [4.79, 11.09]) worlds with at least one
    exact-copier founder. 1 world survived.
  * The preregistered reading is LOTTERY_CONSISTENT. 84616cf8257b is one
    of about 7 expected lottery tickets, and its architecture is the
    commonest copier type, not an idiosyncrasy.
- Seeded-world moat_advantage ledger: CLOSED. 932 of 932 replays were
  admitted byte-identical.
  * 828 flags QUALIFIED (a random-only-ancestry organism crossed).
  * 104 VOID (inserted ancestry only).
  * A blanket subtraction would have destroyed 828 valid flags.
  * The top tier went from 35 to 33 families at 14, and it is identical
    under the lower and upper bounds.
- Evidence: 13.75 GB, 508,823 files, frozen into a sha256-manifested
  read-only bundle on a second physical disk. It was verified member by
  member.
- Sampler bug fixed at the root. The launch preflight would have REFUSED
  the 72-hour campaign: 0 of 209 expected bare-niches draws.

1. RULING 1 -- SEEDED MOAT: UNADJUDICATED -> BOUNDED REPLAY -> CLOSED
-----------------------------------------------------------------------------
Plan fixed before launch (MOAT_LEDGER.json, commit 29b03fd80).
Set: every seeded-init run carrying moat_advantage. That is 932 runs in
319 families, the complete set, not a sample, costing about 31 CPU-hours.
New instrument: first_clean_crossing, the first crossing by a
random-only-ancestry organism, recorded even when the witness crossed
first. It is observation only and RNG-neutral (tested).
Per task crossing (1,628 in total):
  QUALIFIED                   1,241  (375 of them at epoch 0: random
                                      founders that solve easy tasks
                                      immediately)
  WITNESS_ONLY_DESCENDANT       357
  WITNESS_ONLY_UNMODIFIED        30
Per run: QUALIFIED 828, VOID_INSERTED_ONLY 104.
Re-ranking (flags only REMOVED, never created):
  corrected (spontaneous only)      top tier 35 at 14
  UPPER (void removed)              top tier 33 at 14
  LOWER (void + unadjudicated
         seeded moat_crossed
         removed)                   top tier 33 at 14  -- identical
- Named families 2ace470e5c47 / 5b237a475b69 / e8394eee206d are QUALIFIED
  and stay at 14.
- Dropped out of the top tier: f03bf63b3a6a, 708f54fd28d2 (14 -> 12).
- 12 families scoring >=10 change. Some fall from 13 to 5 (e.g.
  3100b8ecc298, 005eb7c62263, fb50aa2d7361).
Remaining limits, stated plainly:
- Seeded moat_crossed on the other 47,900 seeded runs stays UNADJUDICATED
  by design (about 1,040 CPU-hours). It does not move the top tier.
- Not searched: 18,596 seeded treatments crossed where their control also
  crossed. That is an upper bound on advantages the original scorer could
  have missed, because seeded controls carry the witness too. In seeded
  worlds moat_advantage is a weak signal in both directions.
- Allocation rule recorded: only the LOWER ranking may steer.

2. RULING 2 -- COPIER CENSUS (COPIER-CENSUS-01, prereg b48245002 pushed first)
-----------------------------------------------------------------------------
Design:
- Uniform random tapes from recorded SplitMix64 streams.
- The FROZEN VM itself: no reimplementation, so nothing to drift from.
- Empty neighbour, all 256 input bytes per tape.
- An input-skip is used for tapes that never execute IN; it was proven
  exact against full sweeps.
- Rulers: the hand-written replicators (EXACT_UNGATED), the 84616 founder
  (EXACT_GATED at exactly input 121, 26 birth inputs) and an all-NOP tape
  (INERT). All passed before the run.
- The specimen was a ruler only. It is not in the sample, and nothing was
  searched or evolved.
stratum   tapes    exact(ungated/gated)  near  span  writer  exact density [95% CI]
vmcopy32  1.0e7    96 (1 / 95)            63    17    592     9.6e-6 [7.8e-6, 1.17e-5]
vmcopy64  2.0e6     9 (0 / 9)             11     1     42     4.5e-6 [2.1e-6, 8.5e-6]
z80_32    1.0e7     0                      0     0     35     0     [0, 3.7e-7]
z80_64    2.0e6     0                      0     0      4     0     [0, 1.8e-6]
Gating: 94 of the 96 vmcopy32 exact copiers are exact at exactly ONE input
byte; 1 at two; 1 is ungated. Gate values: 128 in 82 copiers, 127 in 6,
and the rest are scattered.
Mechanism (behavioural features, not template matching):
- 128 = the base address of the neighbour window.
- The dominant copier reads its copy DESTINATION from the environment
  (IN C ... COPY loop) and aligns exactly only when the input names the
  window.
- Offsets other than 128 are the same scheme with a source offset (the
  specimen: LD B,-7 -> 121).
- Exact-copier architectures:
    COPY-only rel-jump loop   39
    MIXED rel                 32
    COPY abs-jump loop        16
    MIXED abs                  7
    MIXED gated(2)             1
    COPY ungated input-blind   1
Robustness (stage 2, all 197 hits):
- Essential bytes per exact copier are mostly 3-5 (median 4).
- Single-byte mutants keeping an exact input: mean 0.77.
- 96/96 exact copiers breed true.
- 95/96 still copy exactly with an occupied neighbour.
- Offspring: 128 of 176 vmcopy32 hits produce copier-grade children
  (all 96 exact + 32 of the 80 near/span).
Substrate: without the COPY primitive (z80) there are ZERO copiers of any
grade in 1.2e7 tapes. Copying in this bench is effectively a property of
one primitive.
Prediction:
- Model: lambda = sum over worlds of 1 - (1-p)^76.8, with p taken per
  (substrate, genome, input regime); task=none worlds use density at
  input 0.
- Per class:
    vmcopy32  lambda 4.68  (observed 1 survivor)
    vmcopy64  lambda 2.17  (observed 0)
    task=none worlds lambda ~0.003 (only 1 copier in 1e7 is exact at
      input 0)
- Total 6.86 [4.79, 11.09] -> LOTTERY_CONSISTENT (band 0.05-20, fixed in
  the prereg).
- Implied conversion: about 1 surviving world per 7 copier-founder worlds.
  This rests on ONE event: Clopper-Pearson 95% CI for 1/7 = [0.004, 0.58].
Instrument incidents:
- The report's Clopper-Pearson overflowed at n=1e7. Replaced by the
  beta-quantile form, which matches the old one exactly on small n.
- A world-class key label mismatch hid the z80 classes. The point
  estimate was unchanged; the upper bound moved 9.93 -> 11.09.
- Neither touched a definition or threshold.

3. RULING 3 -- EVIDENCE BUNDLE
-----------------------------------------------------------------------------
Location: C:\Prometheus-data\evidence\z80atlas_campaign_2026-09-19\
  (NVMe; the source worktree is on D:)
Contents:
  campaign.tar        14.1 GB; 508,823 members incl. the campaign code at
                      c7610ea193caf4ed...
  MANIFEST.jsonl.gz   per-file sha256
  BUNDLE.json         also committed as
                      postcampaign/EVIDENCE_BUNDLE_2026-09-24.json
Figures: 101,512 run dirs, 31,528 families.
  campaign.tar sha256       86df9bdb124c2809...
  MANIFEST.jsonl.gz sha256  fd49c7897033f71f...
Verification:
- Every member was re-read against the manifest.
- Files are read-only.
- All 7 key-artifact hashes match the adjudication fingerprints.
- Source worktree untouched.
CORRECTION to the ruling's premise: the runtime state is 14 GB, not
264 MB. The 264 MB figure is RUNS.jsonl + ATLAS_INDEX only.
The bundle is still on ONE machine; see 8.

4. RULING 4 -- SAMPLER STARVATION FIX + SUPPORT/IDENTIFIABILITY PREFLIGHT
-----------------------------------------------------------------------------
Root cause (general, not niches-specific):
- Coverage counted a level wherever it appeared, including where it was
  FORCED (migration=none outside niches) or merely always-legal (fixed
  env, most pressures).
- Where the axis was free, those levels looked over-explored and starved.
- Pair costs did the same, and also made context-restricted levels
  (local_shift, env_coevolve) look unexplored.
- The same mechanism over-drew recombination within EXTERNAL.
Fix:
- grammar.CONTEXT holds the dependency map; it is derived from and checked
  against GR.CONSTRAINTS.
- A dependent axis draws only ELIGIBLE levels (probed from the
  constraints, not a duplicate rule table), weighted by coverage within
  its parent context.
- Pair costs skip forced levels and count dependent pairs within context.
- The scheduler and preflight run the same grammar.explore_step.
Preflight (archaeon/z80atlas/preflight.py, grammar-generic):
  1 structural zeros vs declared CONTEXT (undeclared coupling -> FAIL)
  2 sampler support vs the LEVEL-BALANCE design
  3 support for every declared causal contrast
  4 matched-control audit
scheduler --start refuses FAIL, and refuses PASS_WITH_RESTRICTIONS unless
--accept-preflight "<reason>" is given.
20k-draw simulation (support / expected under the design):
  contrast                        campaign sampler c7610ea19   fixed sampler
  topology alone (bare niches)    0 / 209 UNSUPPORTED          139 / 209 OK
  migration within niches         159 / 679 UNSUPPORTED        463 / 679 OK
  recombination within EXTERNAL   1175 / 412 (over-drawn)      505 / 412 OK
  reproduction via matched ctrl   RESTRICTED                   RESTRICTED
  verdict                         FAIL                         PASS_WITH_RESTRICTIONS
  starved cells                   1 (niches x none)            0; 0 reference rejections
RESTRICTED means grammar.matched_controls still changes pressure (it drops
recombination/explicit_fitness) in 1,331 of 3,351 simulated EXTERNAL treatments (40%). The
fix belongs in the control constructor or the scorer, and is left for the
next campaign design. The gate forces a recorded acceptance until then.
Also noted: the reference had to be LEVEL balance. Uniform-over-valid-specs
puts about 84% of the mass on niches (60 legal world combos vs 3), which
would have hidden the bug.

5. TESTS
-----------------------------------------------------------------------------
All z80atlas tests (provenance, denovo, census, preflight): 50 passed,
1 skipped (the slow historical replay, which runs with Z80ATLAS_SLOW=1).
New:
- first_clean_crossing (2)
- census rulers / skip exactness / stream disjointness (5)
- preflight: campaign-sampler regression, fixed-sampler support,
  control-confound report, undeclared coupling detected, CONTEXT matches
  constraints, launch gate, eligibility (7)
Non-DB suite unchanged apart from these: the same 2 pre-existing failures.
Note: DENOVO-01's prereg hashes engine/grammar/scheduler. DENOVO-01 is
complete, and a re-run of it would now (correctly) refuse.

6. WHAT THIS ESTABLISHES / DOES NOT
-----------------------------------------------------------------------------
ESTABLISHES:
- The copier prior in this substrate, measured blind, with CIs.
- Input-gating is the NORM (99%), not the exception.
- The dominant gate is "environment names the neighbour window".
- Copiers are small, robust, heritable motifs.
- Copying requires the COPY primitive in this bench.
- The 1/27,141 survivor is what the initial-founder lottery predicts.
- The seeded moat ledger is adjudicated.
- The sampler can no longer starve a declared contrast silently.
DOES NOT:
- Measure survival/conversion properly (1 event).
- Measure copiers arising by mutation during a world's life, or ones that
  need an occupied neighbour.
- Cover two-input tasks (the census supplies one byte; a second IN reads
  0).
- Replace an off-machine backup.

7. RECOMMENDATION (operator's call; Archaeon's lean)
-----------------------------------------------------------------------------
Inflow sizing from the measured prior:
  vmcopy32   about 1 exact copier per 1.0e5 random tapes; at the
             (1-event) conversion of about 1/7, roughly 7e5 inflow tapes
             per surviving lineage, order of magnitude
  z80        >= 2.7e6 tapes per copier at the 95% bound; effectively
             invisible
The census also yields a sharper and cheaper next experiment than a
general inflow ecology: test ENVIRONMENTAL GATING directly.
- 85% of copiers depend on the input stream ever containing 128.
- A preregistered in-world pair: identical vmcopy32 worlds, input stream
  uniform vs input stream excluding {120..135}.
- Seeded ONLY with census copiers as founders is NOT allowed (anti-gravity).
  Use random founders at inflow scale instead.
Lean, in order:
  (a) off-machine copy of the evidence bundle (needs your destination)
  (b) the gating pair as a small inflow pilot sized from the numbers above
  (c) only then a general random-inflow ecology
The 84616 specimen stays a ruler; the census shows it is typical, which
removes the temptation to chase it.

8. QUESTIONS FOR THE REVIEWER
-----------------------------------------------------------------------------
Q1 Is lambda (worlds containing a copier founder) the right quantity to
   compare with 1 survivor, given that gating makes most copier founders
   fire rarely (P(input=128) = 1/256 per case)? A tighter model would
   predict survivors, not copier-worlds.
Q2 The 375 epoch-0 QUALIFIED crossings are random founders solving easy
   tasks immediately. Are those "evolved" crossings? Provenance says
   clean, but the moat itself may be shallow for CONST tasks.
Q3 Should LOWER-bound ranking steer anything, when 18,596 possible missed
   advantages make seeded-world moat flags weak in both directions?
Q4 Is the level-balance design the right reference for "support", or
   should intended contrasts carry explicit minimum allocations instead?

9. ARTIFACTS
-----------------------------------------------------------------------------
roles/Archaeon/prompts/2026-09-23_postcampaign_rulings/00_OPERATOR_RULINGS.md
archaeon/z80atlas/postcampaign/MOAT_LEDGER.json
archaeon/z80atlas/postcampaign/MOAT_LEDGER_CLOSURE_2026-09-24.json
archaeon/z80atlas/postcampaign/close_moat_ledger.py
archaeon/z80atlas/postcampaign/replays/REPLAY_seeded_moat_advantage.json
archaeon/z80atlas/postcampaign/freeze_evidence.py
archaeon/z80atlas/postcampaign/EVIDENCE_BUNDLE_2026-09-24.json
archaeon/z80atlas/census/{copier_census.py, report.py, PREREG.json,
  RESULTS.json, HITS.json}
archaeon/z80atlas/{grammar.py, scheduler.py, preflight.py, engine.py}
archaeon/tests/test_z80atlas_{census,preflight,provenance}.py
Commits (branch archaeon/z80atlas-postcampaign-2026-09-23):
  29b03fd80 (rulings+plan)  b48245002 (census prereg)  a6b66ea96 (sampler+preflight)
  6878f582d (moat closed)  805ae076a (bundle)  c5067fac6 (census)

+==============================================================================+
| END. "Not worth continuing" remains a first-class answer. The census       |
| suggests the de-novo question in this bench is now answered by its prior.  |
+==============================================================================+
