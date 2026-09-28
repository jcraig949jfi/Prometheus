REPORT -- can mechanism labels be built as unsupervised ablation fingerprints?

1. WHAT I SET OUT TO TEST

In the Ananke packet-transport campaign (C1), the preregistered causal label for each
evolved champion checked the one control that the expected mechanism should fail
(memory ablation for HOLD, zero-comm plus packet ablation for everything else). The seat
later found that this rule labelled two of the three most interesting mechanisms
NOT_SUPPORTED: a delay-line memory in which a held bit rides in packets in flight (M2)
and a timing-locked MAJ solution (M3). The proposal was to label mechanisms from the
whole ablation pattern instead. I tested it directly on the committed data: build a
labeller that uses no task family and no expected mechanism, only a three-valued pattern
(kill / partial / intact, plus "undecided" and "not applicable") across every control and
transplant, and check whether it (a) groups the known mechanisms, (b) separates M2 and M3
from ordinary routed relay and from site latches, and (c) still does so once the known
packet-ablation window defect (found later in C1b) is corrected. A secondary check was
whether the program's instruments return a third verdict value ("could not decide")
rather than folding it into "invalid" or "negative".

2. WHAT I DID

Data (all committed, repository at origin/main 6ff2b2f8ad035d50aaf21d9f3b60e16c556683f2,
exported with git archive into work/R-09/src):
- roles/Ananke/pte/c1_rows/cells.jsonl.gz: the 12 wave-D adjudication rows (11-control
  battery, 32 mirror-pair accuracies per control where recorded, 6-7 law transplants).
- roles/Ananke/pte/c1_posthoc/posthoc_adjudication.json: 2 post-hoc batteries (includes
  the M2 cell).
- roles/Ananke/pte/c1_report/summary.json: the preregistered causal labels.
- roles/Ananke/pte/c1b/C1B_SUMMARY.json and CORRECTIONS_2026-09-27.md: the corrected
  packet-ablation window values for every D cell, and C1b's later reading of M2/M3,
  used as the reference answer.
- prometheus/ananke/campaign.py causal_label() read to confirm the preregistered rule.
No simulation was re-run; this is a re-analysis of stored batteries.

Code (work/R-09): fp.py (plan in PLAN.md, written before the first run), fp2.py
(exploratory, written after seeing fp.py output). Outputs in work/R-09/out/
(fp_out.txt, fp2_out.txt, fingerprints.json).
Method in fp.py: for each control, retained fraction f = (acc_control - 0.5) /
(acc_normal - 0.5). Trit K if f < 0.25, P if 0.25..0.75, I if > 0.75; "?" if f lies
within 2 standard errors of a boundary (paired bootstrap over the 32 mirror pairs, 1000
resamples; where no pairs were stored, an SE derived from the normal arm); NA if the
control did not run. A cell is INDETERMINATE if normal accuracy is < 3 SE above chance.
Distance = mean disagreement over controls definite in both cells (K-I = 1, adjacent
= 0.5), undefined if fewer than 8 shared definite controls. Average-linkage clustering,
cut 0.25. Success criteria fixed in advance: latches one cluster; routed relays one
cluster; M2 not in the relay or latch cluster; the two M3 cells together and not in the
relay cluster. Robustness grid: 3 threshold pairs x 5 cuts x {C1 window, corrected
window}. fp2.py: same trits, controls weighted by the entropy of their trit distribution
across cells, with and without the latch cells.
Commands: python3 fp.py > out/fp_out.txt; python3 fp2.py > out/fp2_out.txt.

3. RESULT

Headline fingerprints (control order: transplants async, jitter, latency+1, loss, noise,
size, topology; then adaptation_off, env_permutation, frozen_routing, irrelevant_channel,
max_loss, memory_ablation, packet_ablation, randomize_payload, shuffle_dest,
shuffle_time, zero_comm):
  latch (M5)      IIIIII-IKNNIKIIIII   (all 4 near-identical)
  routed relay M1 ?IIIIIKIKINKPPPKIK   (4 cells within distance 0.05 of each other)
  M2 delay line   -------IKINKIKKK?K
  M3 (x2)         ??K?I????IIKIIKKIK
With the C1 window and the planned settings (0.25/0.75, cut 0.25): 3 clusters -- the
latches; one large comm-dependent cluster holding the relays, M4, M2, the second
unremarked MAJ cell and both M3 cells; and one post-hoc HOLD cell whose normal
performance (0.67) was too weak to give enough definite trits. Criteria: latches PASS,
relays PASS, M2 separate FAIL, M3 pair PASS, M3 separate from relays FAIL.
Across the 30-setting robustness grid: latches and relays pass 30/30. M2 is separated
from the relays in only 10/30 settings (all at 0.2/0.8 thresholds). With the C1 window,
M3 is together AND separate from the relays in 5/15 settings (cuts 0.15-0.2 only). With
the corrected window it passes both in 1/15.
Nearest-neighbour "novelty" distance (C1 window): M3 0.125 (highest), unremarked MAJ
cell 613162a3 0.111, M2 0.062 (its nearest neighbour is a routed relay), relays and
latches 0.00-0.05. The entropy-weighted exploratory variant gives the same ordering, and
in it M2 is at distance 0.000 from a relay.
Why:
- M2: under C1's battery, M2's pattern is simply a relay's pattern. Zero-comm, packet
  ablation, payload randomisation and destination shuffle all kill it, and memory
  ablation (reset of site state S) leaves it intact. Several relays show exactly the
  same thing. What made M2 surprising was a family-conditional expectation ("HOLD memory
  should live in a site"), not anything in the ablation pattern. The battery had no
  control that tells packets carrying a bit across time apart from packets carrying it
  across space. C1b had to add new carrier-specific controls (in-flight flush with an
  inter-trial sham, per-array resets) to establish it.
- M3: the fingerprint does flag M3 as the most novel cell, but mainly because of one
  trit, "packet ablation intact". C1b showed that trit is an instrument defect: the C1
  drop window excluded the readout tick, and in these cells latency = delta, so packets
  land exactly on that tick. With the corrected window substituted, M3's
  packet-ablation trit becomes K and M3 moves toward the relays (distance 0.17-0.19 to a
  relay, and it merges at cut 0.25 in the weighted variant). The genuine residual
  differences (latency+1 kills, adaptation-off kills) match C1b's reading: timing-locked
  transport, with SETRULE acting as configuration.
- The unsupervised novelty ranking puts a cell the seat did not single out (613162a3,
  MAJ, prereg CAUSAL_SUPPORT, fresh-seed replicates did not reproduce, shuffle_dest 0.72
  above normal 0.69) second. I did not investigate it further.
- The three-valued treatment matters in practice. In the comm-only subset 6 of 10
  cells have too few definite shared controls to be compared at all, and the weakest
  post-hoc cell is UNDECIDABLE against every other cell. A forced binary labeller would
  have given all of them a label. Three D-battery controls (frozen_routing,
  irrelevant_channel, env_permutation) and all transplants store only a point accuracy
  with no pairs, so their uncertainty had to be approximated.
Plain conclusion: an unsupervised ablation-pattern labeller built from C1's own battery
would NOT have recovered M2. It would have flagged M3, but for the wrong reason (an
instrument artefact). It reliably recovers only the coarse split, latch versus
comm-dependent transport, which the old rule already got.

Secondary check (three-valued verdicts), at 6ff2b2f8: the claim that three-valued
verdicts appear only in prometheus/ananke/report.py is false. 25 Python files under
prometheus/ alone carry INDETERMINATE / INCONCLUSIVE / NOT_APPLICABLE (Ananke
campaign.py causal_label already returns INCONCLUSIVE; also cosmos, toolbox,
atlas_bee), and many more exist repo-wide. The Vivarium concern still stands:
vivarium/viv contains no INDETERMINATE, and loop.py (around lines 975 and 1044-1045) maps
exceptions, EXECUTOR_NOT_IMPLEMENTED, PREFLIGHT_REJECTED and UNCLAIMED_EXECUTION to
INSTRUMENT_INVALID. So "ran but could not decide" still has no kind-level outcome there.
I did not audit metric-multiplicity declaration.

4. DID IT RESOLVE THE QUESTION

Partly. For the one engine with committed ablation batteries and an independently
adjudicated answer (C1b), the question is answered, negatively for the strong form: a
fingerprint is only as discriminating as the controls in the battery, and it cannot tell
a new mechanism from an instrument defect. The pattern "differs from its neighbours"
fires for both. With 14 specimens and 2-4 per mechanism, this is a demonstration, not a
statistical estimate. I did not test cross-engine sharing, because no other engine's
ablation battery was assembled into a comparable table within budget. The question as
posed ("instead of expected-mechanism rules") is partly badly posed: the M2 miss was not
caused by using one expected control. It was caused by the absence of the right control
from the battery, and fingerprinting the controls that were present cannot supply it.

5. CONSEQUENCES

- The idea does not work as a replacement, but it has a narrower use that holds up:
  nearest-neighbour fingerprint distance is a cheap "look here" flag for promotion (C1
  F6 suggested promoting by pattern novelty), but a flagged cell is a candidate for
  EITHER a new mechanism OR an instrument defect, and must go to carrier-specific
  adjudication. It is not a label. M3 is the concrete example: the most novel
  fingerprint was the defect.
- Battery design, not labelling, is the lever. A shared cross-engine instrument should
  standardise (i) a carrier inventory per substrate, with one targeted reset or flush per
  carrier plus a sham (as C1b did), (ii) pair-level storage for every arm, including
  transplants, and (iii) a positive-control fixture per arm, so that "intact" readings
  count.
- For Ananke: the unremarked MAJ cell 613162a3 carries the second-highest novelty
  score and may deserve a look.
- False premise in the harvest's later evidence: three-valued verdicts are widespread,
  not confined to one Ananke file. The real open gap is Vivarium's missing kind-level
  INDETERMINATE (errors and non-decisions collapse to INSTRUMENT_INVALID).
- Who should know: Ananke (battery design, the novelty flag), the Vivarium seat
  (kind-level INDETERMINATE still absent at 6ff2b2f8), and whoever owns cross-engine
  falsification instruments (a shared carrier and sham battery schema is the
  transferable part, not a clustering labeller).

6. COST

About 1.5 hours of my time. CPU about 2.8 minutes in total (fp.py 154 s user, fp2.py
about 7 s), peak RAM about 50 MB, one process at a time. No simulations re-run, no
holdouts touched, repository not modified. Not done: a cross-engine battery comparison;
re-running controls to get pair-level data for the arms that lack it; any investigation
of cell 613162a3; an audit of metric-multiplicity declaration in Vivarium.
