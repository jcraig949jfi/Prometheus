# I4 -- The historical pipeline and older engines: open physics-of-intelligence questions

Odysseus research delegate, 2026-09-27. Read-only mining of
/home/jcraig/Prometheus-worktrees/odysseus-base-role (HEAD 22bfbc966).
Builds on the Artemis retrospective
(roles/Artemis/threads/sfe_retrospective/REPORT.md, THREADS.md,
notes/A_chronology.md, notes/C_engines.md). Artemis covered SFE as
infrastructure: custody, provenance, placement. This file covers the
SCIENCE the old pipeline produced or left open. Pure ASCII.

Conventions:
- "path:N" means a file and line number. A bare hex string is a commit SHA.
- INFERRED marks my own reading, not a statement in the record.
- PILOT marks the one read-only computation I ran for this file. It was
  unpreregistered, n=3, and is described in s5 D1. It is a feasibility
  check, not a result.
- "WSE" is Archaeon's selection loop over Proteus player-VM organisms
  (archaeon/wse/). "Cell" names a world: W0 (immediate recall), W1_dk
  (recall delayed k events), W2_K2 (two keyed streams).

-----------------------------------------------------------------------

## 1. Territory summary

1. The older lines are: Apollo (evolved typed-operator reasoning pipelines,
   2026-03..09-11); Hephaestus, forge and Ignis (LLM-forged reasoning
   tools, 03..05, with 08-09 audits); prometheus_math and zoo; Proteus
   (a neutral generator for a 25-opcode total VM, plus a graph substrate);
   Ergon; genesis/harmonia_a/b/c; SFE D6-D10; the H0-H5 alpha lanes; and
   Archaeon Campaigns 1-6 on the WSE (09-16..09-18).
2. Almost every old line ended in one of two ways. Either the instrument
   worked but the question was never posed (H0-H5), or the headline died
   under a stronger control (Apollo 0.833, Hephaestus diversity, Campaign 1
   transfer, basin share, CA localisation).
3. The durable scientific residue is a coherent set of landscape facts
   about one substrate, the WSE/Proteus tape VM:
   - a bimodal damage cliff;
   - a large, connected neutral network that pays little;
   - a half-credit shelf with an unreached summit;
   - a delay ladder that builds generalisation nobody has explained;
   - takeover by injected material regardless of its competence;
   - robustness bought as length.
4. The same shapes recur on other substrates: the StackVM, the Proteus
   graph VM, Apollo typed pipelines, Crius, and NPE. This recurrence is
   the main reason this territory still bears on the north star.
5. Much of the evidence is in git and regenerable from seeds with stdlib
   Python. PILOT: 57 WSE evaluations took 2.9 s on this laptop.

-----------------------------------------------------------------------

## 2. Candidate research threads

Threads are ordered roughly by bearing on the north star. The north star
asks for mechanisms that are discovered, retained, composed and made
inheritable (roles/base-role/NORTH_STAR.md:8-24). "Lenses" are the
disciplinary views that apply.

### TH-I4-01 What is the delay-invariant reader, and did the ladder build it or select it?

QUESTION: What program structure lets WSE organisms trained on delays
0/1/2/4 read delays 8 and 16 perfectly? Does the delay ladder construct
this structure, or select it from variation already present?

WHY IT MATTERS: This is the old pipeline's only reproducible case of
generalisation beyond the training distribution. Delay invariance
appeared in 11/12 seeds, never-trained d8/d16 were read at 1.0, and
matched direct search reached d8 in 0/6 and d16 in 1/6
(archaeon/campaign3/CAMPAIGN_REPORT.md:41-46). Campaign 3 called it "the
campaign's only reproducible positive capability and it is unexplained"
(same file :452-458). It is a clean case of an abstraction that no one
installed.

WHAT IS KNOWN:
- Generality appears abruptly, at rung 1 in 7/12 seeds. In 5/12 seeds an
  already-general organism was promoted at the first delay-1 battery:
  "part of the corridor's work is SELECTION" (same file :144-162).
- Proteus did a static anatomy only. Delay-general specimens differ from
  W0 solvers in tick_budget (267.6 vs 82.1, uncorrected p=.0062) and in
  conditional-branch presence (.82 vs .33). Section "Not established"
  says "which structure CAUSES delay invariance (Archaeon lesions the
  ablation sets on the delay family)" (proteus/round2/ANATOMY_L0.md:1-20,
  :146-150).
- The ablation manifests exist
  (proteus/round2/ANATOMY_L0_ABLATION_SETS.json, 1.86 MB, schema
  proteus.anatomy_l0_ablation.v1).
- Campaign 4 was redirected by the operator to damage geometry
  (roles/Archaeon/prompts/2026-09-17_sfe_campaign4/00_OPERATOR_DIRECTIVE.md).
  C3's recommendations C4-1 (anatomy) and C4-2 (selection vs
  construction) were not run. INFERRED from the C4 slot list at
  archaeon/campaign4/CAMPAIGN_REPORT.md:73-82.
- Bellerophon's BEE transplant found the ladder effect ABSENT on its own
  substrate. There a single delay-invariant strategy dominates every
  rung, so "a delay curriculum has nothing to teach"
  (roles/Bellerophon/atlas_bee/REVIEW_PACKET_2026-09-19.md:121-123,
  :141).
- PILOT: single-instruction NOP knockouts on 3 delay-general organisms
  (from archaeon/campaign4/STARTING_POPULATION.json) found 7/16, 3/8 and
  9/27 instructions critical for W1_d16. All three also score 1.0 on W0
  held-out. So the reader is not one instruction. INFERRED, n=3.

WHAT IS UNKNOWN: whether the invariance is a program shape (for example,
wait-for-ask, then read the latest matching input) or a register trick;
why W0 solvers do not have it; and what fraction of W0 populations
already carry it.

CHEAPEST DISCRIMINATOR: s5 D1 (the knockout map from the ablation sets)
plus s5 D2 (probe whole populations at rung 0).

LENSES: evolvability; abstraction and compression; curriculum as
selection vs construction; generalisation.

NEW-LENS SIGNAL: High. It asks what makes an evolved program generalise
out of distribution, on a substrate small enough to be read by hand.

RELATED: TH-I4-11; BEE a5; Proteus PROTEUS-19 (per-instruction
activation tracing, parked; roles/Proteus/BACKLOG_H0H5.md).

HISTORICAL-MOMENTUM-ONLY? No. It is the cheapest available case of
unplanned generalisation, and the organisms and tools are in git.

### TH-I4-02 What must change for a two-value keyed memory to become reachable?

QUESTION: The W2_K2 summit needs an organism that keeps two keyed values.
Which minimal change of substrate or operator makes this reachable by
selection: a register or addressing primitive, a crossover operator, a
modular genome, or a population or budget scale?

WHY IT MATTERS: This is the sharpest "what selection cannot find" fact in
the record. Existence is not in doubt, since the summit is a defined
program. Accessibility is.

WHAT IS KNOWN:
- 0 summits appeared under every condition tried:
  - 24 runs x G300;
  - a shelf start;
  - all-or-nothing credit;
  - 54 corridor runs.
  The best excursion was 0.875 training and 0.60 held-out
  (archaeon/campaign3/CAMPAIGN_REPORT.md:101-115).
- The shelf is a one-value memory. Of 4,800 grammar children, 1 was
  useful. 58 gained the second stream and 0 of those kept the first.
  0/480 greedy 3-step paths reached 0.90 (same file :117-141).
- C4-06 recombination produced 0/6 crossings in both arms, and splice
  births were 8 points less viable (6c4c6a4a2;
  archaeon/campaign4/CAMPAIGN_REPORT.md:46-48).
- C3 recommendation C4-3 ("a register/addressing primitive the grammar
  lacks, or a search operator that can cross the two-value valley") was
  never run (same C3 file :468-474).
- The Campaign 6 graph organisms with MODULE DUPLICATE/TRANSPLANT were
  built (archaeon/campaign6/PLAN.md, axis O). They were then gated on
  PROTEUS-46, which found USEFUL 0/4,881 on graph mutation
  (proteus/round2/PROTEUS-46_FALSIFIER.md:3-12, per the delegate
  report). No W2_K2 summit was found anywhere in git log (search of
  commit subjects, INFERRED).

WHAT IS UNKNOWN: whether the barrier is representational (no keyed
addressing), operational (no duplication of a working one-value memory),
or a matter of scale.

CHEAPEST DISCRIMINATOR: Hand-write the summit program in the Proteus VM.
Then measure the size of its basin in edit distance from the shelf
organisms preserved in git: take the one-value shelf memory, duplicate
it, and rewire it. Compare with the same distance under a hypothetical
DUPLICATE operator. This is a pure calculation; no evolution is needed.
See s5 D4.

LENSES: accessibility vs existence; the gene-duplication route to new
function (Ohno); neutral networks.

NEW-LENS SIGNAL: High. Crius reached the same shape independently: reuse
exists and pays, but 0/36 searches reached it
(crius/CRIUS_C2_TERMINAL_REVIEW.md:26-34, :271).

RELATED: TH-I4-03, TH-I4-04, TH-I4-13; Crius; Nestor "4-edit valley"
(3af735d67).

HISTORICAL-MOMENTUM-ONLY? No. The "accessible to selection" question is
the north star's central question.

### TH-I4-03 Why does crossover cross valleys in Apollo but not in Proteus?

QUESTION: On Apollo's typed blackboard pipelines, crossover crossed a
fitness valley that single-step mutation could not. On the Proteus tape
VM it did not. What property of the genome decides whether
recombination creates function?

WHY IT MATTERS: Composition and recombination are named north-star
routes ("composed, dismantled, recombined"). The two old substrates give
opposite answers.

WHAT IS KNOWN:
- Apollo: the solver was found de novo in 4/5 seeds with crossover vs
  0/5 without. The best single-edit neighbour stayed at 0.30, and 8,000
  random walks reached the solver 0 times
  (apollo/pivot/recombination_findings_2026-06-16.md:40-68). The type
  bridge solved 3/5 only with bridge plus crossover (8d06112b7).
- Proteus/WSE: 0/6 vs 0/6 (6c4c6a4a2).
- Harmonia C: composition joins destroy a parent capability 78-83% of
  the time, and 99.5% of apparent acquisition was inherited (d59cc7771,
  per delegate).
- C2-SFE-08 and C2-SFE-10: organ chimeras equal shuffled equal random
  (archaeon/campaign2/CAMPAIGN_REPORT.md:179-182).
- Crius cites Apollo's result as design input (crius/DESIGN_C1.md:99-101).

WHAT IS UNKNOWN: whether the difference is typed slots and semantic
interfaces (Apollo) versus positional raw words (Proteus), or the
distance to the target. INFERRED hypothesis: recombination pays only
when the parts have declared interfaces. That hypothesis matches the
charter's "declared interfaces" (CHARTER_AND_CONTINUITY.md, Commitments
table).

CHEAPEST DISCRIMINATOR: On the Apollo recombination fixture (in git,
apollo/scripts/recombination_ab.py), replace the
typed splice with a positional splice that ignores slot boundaries.
Check whether the 4/5 falls to 0/5. See s5 D6.

LENSES: modularity; evolvability of evolvability; interface theory.

NEW-LENS SIGNAL: Medium-high.

RELATED: TH-I4-02, TH-I4-08.

HISTORICAL-MOMENTUM-ONLY? No.

### TH-I4-04 Is the "0/5,472 mutational cliff" a substrate property or a parent-headroom artefact?

QUESTION: How much of "D7 = 0 in 5,472 single edits" comes from parents
that had no room to improve?

WHY IT MATTERS: The cliff is cited across the ecology as a substrate
fact (C_engines.md:284-286; Hephaestus HEPH-32 targets "the C4 cliff",
roles/Hephaestus/BACKLOG_H0H5.md:38). If most parents were at ceiling
or were degenerate, the robust part is the bimodal displacement, and the
"no improvement" part is nearly a tautology.

WHAT IS KNOWN:
- The 57 parents are stratified: delay_general 11, w0_solver 15,
  shelf 19, gen0_random 12 (archaeon/campaign4/STARTING_POPULATION.json,
  field strata).
- Children by stratum: delay_general 984, w0_solver 1355, shelf 1606,
  gen0_random 1035 (archaeon/campaign4/DAMAGE_GEOMETRY_MAP.md:23-26).
- The READOUT concedes that gen0_random parents are degenerate and that
  99.8% of their children are D2 by inheritance
  (archaeon/campaign4/C4-01/READOUT.md:65-68).
- Delay-general parents already solve delays 2 and 3, and a W0 solver is
  untroubled by 8-bit values (archaeon/campaign4/CAMPAIGN_REPORT.md:
  59-62). PILOT: the delay-general parents score 1.0 on W1_d16 and W0.
- INFERRED: about 2,339 children (delay_general plus w0_solver) came from
  parents at or near 1.0 on their own environment, where D7 is hard or
  impossible by construction. Most of the rest are gen0_random (floor)
  or shelf children, where improvement means crossing the summit valley
  of TH-I4-02.
- The displacement bimodality holds on every operator (READOUT :60-64),
  and the same bimodality was found on the StackVM (1f0e4ae01: 89.6%
  silent, 9.4% near-catastrophic) and the graph VM (PROTEUS-46).

WHAT IS UNKNOWN: the D7 eligible count, meaning parents below ceiling on
their own environment. This is the same "eligible count" discipline C4
applied to D1 (C4-01 READOUT :9-21) but not to D7.

CHEAPEST DISCRIMINATOR: Re-tabulate
archaeon/campaign4/C4-01/attempts/a02/rows.json (478 KB, in git) by
stratum and by parent reward on its own environment. Report D7
eligibility. See s5 D3.

LENSES: measurement validity; evolvability.

NEW-LENS SIGNAL: Medium. It corrects a widely cited number.

RELATED: TH-I4-05, TH-I4-06; the Artemis s3.3 table (the ecology's
headline-shrink pattern).

HISTORICAL-MOMENTUM-ONLY? No. The number is load-bearing in current
backlogs (HEPH-32).

### TH-I4-05 Does selection for robustness trade away evolvability?

QUESTION: Selection lowered single-edit loss from .42 to .13, but coherent
(graded) variation fell from .15 to .04 and genomes grew from 19 to 62
instructions. Is robustness here purchased by making variation inert?

WHY IT MATTERS: The robustness-evolvability relation is central to the
physics of evolvable systems. This substrate gives a clean, preserved,
negative-leaning case.

WHAT IS KNOWN:
- C4-08 was read as ROBUST_WITHOUT_MECHANISM
  (archaeon/campaign4/CAMPAIGN_REPORT.md:50-53; DAMAGE_GEOMETRY_MAP.md
  C4-08 block).
- C5-08: length carries the neutral share (.17 to .71 across length
  bins). Removing dead code barely moves it (.435 to .409). The
  boundary's own component is .021 (archaeon/campaign5/
  CAMPAIGN_REPORT.md:121-128).
- Proteus: grammar revisions V0-V0.2 chased length drift that a
  symmetric null reproduces (review packet
  PROTEUS_PROGRAM_REVIEW_PACKET_V0_TO_V0_5.txt:50-62, per delegate).
- Ergon: "same phenotype != same mutational affordances". Only 23% of
  behavioural duplicates are mutationally redundant (ergon gen1b packet
  :22-66, per delegate).

WHAT IS UNKNOWN: whether length-robust genomes are also slower to adapt
when the world changes. That is the evolvability cost, and it was never
measured. The perturbed population exists (C4-08) but was never
re-challenged.

CHEAPEST DISCRIMINATOR: Take ancestral vs perturbed (length 62)
populations, regenerated from C4-08 seeds. Measure generations to a
foothold on a new cell under common random numbers. This is the Wagner
test of whether robustness helps or hurts innovation.

LENSES: robustness and evolvability; genetic load; bloat in GP.

NEW-LENS SIGNAL: Medium. Bloat-as-protection is known from genetic
programming. Its evolvability cost on a preserved substrate is new here.

RELATED: TH-I4-04, TH-I4-06, TH-I4-18.

HISTORICAL-MOMENTUM-ONLY? No.

### TH-I4-06 Why does the neutral network's exaptation gradient flatten?

QUESTION: Neutral walks accumulate held-out exaptation (.050 to .082 from
depth 16 to 64), but the marginal rate falls fourfold and the yield per
evaluation ends below a random single edit's. What limits it?

WHY IT MATTERS: Neutral networks as reservoirs of future function are a
core evolvability conjecture. Here it was tested fairly and came out
"real but not worth its cost".

WHAT IS KNOWN:
- 188/188 walkers reached depth 16 at about 55% acceptance, and
  exaptation rose from .016 to .043 (archaeon/campaign4/
  CAMPAIGN_REPORT.md:41-45).
- The depth-64 replication gave .050/.064/.078/.082, with yield .00127
  falling to .00082 against .0012 for a random single edit. The rule
  gave PRESERVE_NEUTRAL NO (archaeon/campaign5/CAMPAIGN_REPORT.md:59-66).
- Structural diversity grew .30 to .76 with depth
  (DAMAGE_GEOMETRY_MAP.md, C4-05 block).
- StackVM showed 333 output-silent sites with high hidden-state
  influence, i.e. cryptic variation that output-based neutrality misses
  (6185b718a, per delegate).

WHAT IS UNKNOWN: whether the flattening is saturation, where the walk
fills the reachable exaptive set, or dilution, where length growth makes
edits inert (TH-I4-05). Also unknown: whether hidden-state-changing
neutral mutations carry the exaptation.

CHEAPEST DISCRIMINATOR: Regenerate the C5-01 walks from seeds (the walk
is a pure function of seeds, archaeon/campaign4/DECISIONS.md:136-139).
Split exaptive gains by whether genome length grew. See s5 D5.

LENSES: neutral theory; cryptic variation; exaptation.

NEW-LENS SIGNAL: Medium.

RELATED: TH-I4-05, TH-I4-12.

HISTORICAL-MOMENTUM-ONLY? No, but it should be bounded. The fair test
already closed the practical use.

### TH-I4-07 What geometric statistic predicts search efficiency, if any?

QUESTION: Accessible variation did not predict navigability. Basin share
appeared to, then died as a two-strata artefact. Is there any
pre-search landscape statistic that predicts search outcome within a
family?

WHY IT MATTERS: Representation choice is where "compression" and
"evolvability" meet (charter H5). If no pre-search statistic predicts
navigability, representations can be judged only by running search.

WHAT IS KNOWN:
- Hill-climb evaluations to reach 0.9 were: direct 13/53/53; balanced
  653/97/89; scrambled 971/never/190. Balanced has 50% more accessible
  variation and is slower (archaeon/campaign1/CAMPAIGN_REPORT.md:
  170-174).
- Over 52 rows, accessible variation gave rho -0.23; basin share -0.59;
  deceptive share +0.57 (archaeon/campaign2/CAMPAIGN_REPORT.md:188-191,
  :285-293).
- The basin-share replication (-0.568) was a two-point correlation.
  Within-cell rho was -0.527/+0.187/-0.042/undefined. Manipulating basin
  share left search unchanged, and random orderings differed by the same
  0.083 (archaeon/campaign3/CAMPAIGN_REPORT.md:209-246).
- Harmonia B: pre-search ranking gave rho .20/-.01 against a declared
  .70. The operator explains 0.0002 of geometry variance but .10-.12 of
  search outcome. A sha256 "substrate" scores 0.967 on single-step
  improvement (bf80997f5, per delegate).
- H5-1: a random balanced permutation reached 11.72 vs the "learned"
  11.7305 (f2c2452ea; roles/Harmonia VACUOUS_READINGS V-005, per
  delegate). No learned decoder was ever built.

WHAT IS UNKNOWN: whether any statistic survives within-family testing.
Candidates: basin share within family, deceptive share, or
neighbourhood-conditional improvement probability at matched difficulty.

CHEAPEST DISCRIMINATOR: Re-analyse the 52 C2-SFE-08 rows and the 48
C3-SFE-06 rows (in git) by partial correlation, controlling for table
difficulty. This is pure arithmetic.

LENSES: fitness-landscape theory; representation and compression.

NEW-LENS SIGNAL: Medium. Harmonia B's "geometry vs search dissociation"
is the same shape, found independently.

RELATED: TH-I4-17.

HISTORICAL-MOMENTUM-ONLY? Partly. The WSE-specific version is closed.
The general question matters because every new engine picks a
representation without such a predictor.

### TH-I4-08 What carries heritable search value: arrangement, or composition and length?

QUESTION: On the WSE, genomes whose instruction blocks were PERMUTED, or
which kept only their opcode multiset, were as good or better as seed
material than intact evolved genomes. Is the transferable value in
length and opcode composition rather than in the evolved arrangement?

WHY IT MATTERS: The north star wants mechanisms to be "retained and
improved". If what is inherited is a statistical envelope, not a
mechanism, then "transfer" on such substrates is not mechanism
inheritance.

WHAT IS KNOWN:
- C2-SFE-04: shuffled genomes gave 5/10 and opcode-only 6/10, both BEAT
  intact failed genomes. Length-matched randoms gave 1/10. The failed set
  averages 20.8 instructions vs 5.9 in generation 0, so "the parent's
  material was repairing a length handicap"
  (archaeon/campaign2/CAMPAIGN_REPORT.md:166-178).
- C2-SFE-03: every cheaper explanation did what the components did
  (same file :155-165).
- C3-SFE-10: permuted, incompetent controls reached the W1_d4 summit in
  4/12, 2/12 and 7/12 runs, vs 0/12 for fresh starts. "Same-length,
  same-opcode-multiset genotypes are worth more as raw material than
  random ones" (archaeon/campaign3/C3-SFE-10/RECORD.md:205).
- Opposite shape: in Apollo the arrangement, i.e. the splice, carries
  the function (TH-I4-03).

WHAT IS UNKNOWN: which statistic carries the value. Candidates: length,
opcode frequencies, operand-word distribution, or VM knobs such as
tick_budget and n_regs. The permuted control preserved the VM knobs
(same RECORD.md:72).

CHEAPEST DISCRIMINATOR: A factorial seed-material experiment on W1_d4.
Take permuted evolved genomes, then vary one factor at a time: knobs
reset to generation-0 values, opcode multiset resampled, and length
matched. Run under common random numbers. It is a small run (N=200,
G=60) and needs about an hour on 4 cores. INFERRED estimate from the
pilot timing.

LENSES: heredity vs identity; what is a "unit of transfer".

NEW-LENS SIGNAL: High. It separates "inherited mechanism" from
"inherited prior over programs". That separation is exactly what the
causal lens's "reproduction without origination" is reaching for.

RELATED: TH-I4-09, TH-I4-10; ENVGATE rulings (archaeon/envgate2/).

HISTORICAL-MOMENTUM-ONLY? No.

### TH-I4-09 Why does one incompetent organism in 200 take over the population?

QUESTION: Without an offspring cap, any injected material takes the
population's ancestry within 3-9 generations, including controls that
score 0.0-0.125. What selective advantage does a non-solving imported
genome have over residents?

WHY IT MATTERS: Every transfer and ecology experiment assumes imports
compete on merit. The record says ancestry is monopolised while genome
diversity stays at 0.78-0.99, which is a population-genetics anomaly.

WHAT IS KNOWN:
- Takeover rates: mature 12/12, control 11-12/12, no import 0/12. Dose
  sets speed only. A cap of 0.05 delays takeover by 4-6x and never
  prevents it; 227/228 runs end at import share .995-1.0
  (archaeon/campaign3/CAMPAIGN_REPORT.md:285-307;
  C3-SFE-10/RECORD.md:190, :205).
- Resident held-out scores were .02-.17 (RECORD.md:190).
- BEE transplant: takeover ABSENT, "pure selection removes non-optimal
  imports". BEE attributes the source's takeover to the offspring cap
  (roles/Bellerophon/atlas_bee/REVIEW_PACKET_2026-09-19.md:118-120,
  :140).
- INFERRED CONTRADICTION: the source record shows takeover WITHOUT any
  cap (the "arm (no cap)" table), and the cap only slows it. BEE's
  mechanism attribution appears inverted relative to the source. The
  cross-substrate difference is real (takeover present vs absent), but
  its stated cause is not supported by the record.

WHAT IS UNKNOWN: the advantage itself. Candidates: robustness from
length (TH-I4-05); higher training-score variance, so tournament
winners by luck; or tie-breaking under elitism among floor-level
organisms.

CHEAPEST DISCRIMINATOR: Replay one C3-SFE-10 control run from seeds.
Log per-generation tournament wins by origin, the offspring-viability
share by origin, and mean length by origin. The result is a tabulation,
not a new experiment.

LENSES: population genetics (fixation of neutral or near-neutral
variants); selection mechanics vs fitness.

NEW-LENS SIGNAL: Medium-high. "Ancestry fixation without fitness" is a
measurable property of any evolutionary engine's loop.

RELATED: TH-I4-08, TH-I4-10; NPE "identity vs heredity" (Artemis
THREADS T5).

HISTORICAL-MOMENTUM-ONLY? No.

### TH-I4-10 Is there any transfer that improves search rather than copying a solution?

QUESTION: Across Campaigns 1-5, "transfer" either copied an existing
sub-solution (mature, whole material) or did nothing and hurt. Did any
transferred object make the RECEIVER a better searcher?

WHY IT MATTERS: The charter's central conjecture is that experience
changes "what it can do with that inheritance" (CHARTER_AND_CONTINUITY.md,
"The charter to carry forward"). Copying a solution is inheritance
without changed capacity.

WHAT IS KNOWN:
- Campaign 1's positives (2/3 vs 0/3) DIED at n >= 10 under common
  random numbers (+0.009, +0.002). The control zeros were harness
  artefacts: harness-seeded fills, a length handicap, and a cell
  reachable from its own generation 0
  (archaeon/campaign2/CAMPAIGN_REPORT.md:38-52, :152-182).
- Failure-episode transport HURTS (-0.160) (same file :209-214).
- Immature material transports nothing. Mature material transports a
  direct sub-solution (same file :272-276).
- W7_K2 is the one TIME ADVANTAGE: median foothold at generation 20 vs
  82, with nothing inherited directly. The permuted control is WORSE
  (archaeon/campaign3/CAMPAIGN_REPORT.md:172-180). n=6, WEAK (same file
  :439-441).
- C5-02 lateral ecology: rescued lineages take the population without
  moving the elite (archaeon/campaign5/CAMPAIGN_REPORT.md:67-71).
- ENVGATE: host-mediated reproduction amplifies resident genomes without
  creating new ones (archaeon/envgate2/, per delegate).

WHAT IS UNKNOWN: whether the W7_K2 time advantage is real at n=12. It is
the only candidate for "search-enhancing transfer" in the record.

CHEAPEST DISCRIMINATOR: Replicate the W7_K2 corridor edge at n=12 with a
permuted control and a length-matched control (C3 corridor harness,
archaeon/campaign3/). Run time is about 1-2 hours on 4 cores
(INFERRED).

LENSES: transfer learning vs inheritance; origination vs amplification.

NEW-LENS SIGNAL: High, because it is the charter's own conjecture.

RELATED: TH-I4-08, TH-I4-09, TH-I4-19.

HISTORICAL-MOMENTUM-ONLY? No.

### TH-I4-11 When does retention pay, and is its price bounded by the appearance of a general solution?

QUESTION: A 5-10% revisit share removes the forgetting cliff at rung
boundaries, and "the price stops at generality". Is the value of
retention a function of whether a general solution exists in reach?

WHY IT MATTERS: Retaining alternatives is explicitly in the north star
("retained"). The WSE supplied a quantitative break-even. BEE supplied a
substrate where retention is worthless.

WHAT IS KNOWN:
- Rung-0 competence goes 1.0 to <= .12 within 5 generations "even in a
  seed holding a solution covering every rung (drift, not capacity)"
  (archaeon/campaign2/CAMPAIGN_REPORT.md:245-249).
- Break-even lies in (0.05, 0.10]. p0.10-then-0 keeps 12/12
  (archaeon/campaign3/CAMPAIGN_REPORT.md:187-207).
- BEE: final_r0 was identical across p, because the search converges to
  a delay-invariant dominant strategy
  (REVIEW_PACKET_2026-09-19.md:121-123).
- BEE a3: retention pays under situational DIVERSITY, not recurrence
  (same file :114-117).
- H3: behavioural coverage is identical in live and dead streams; only
  task-level reuse separates them
  (archaeon/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:89-121, per
  delegate).

WHAT IS UNKNOWN: a substrate-independent law. INFERRED conjecture:
retention pays exactly when the landscape has separate specialist optima
that drift can reach before a generalist is found.

CHEAPEST DISCRIMINATOR: On the WSE ladder, log the generation at which
the general solution appears vs when revisits stop mattering, using the
existing C3-SFE-05 rows in git.

LENSES: catastrophic forgetting; memory economics; drift vs capacity.

NEW-LENS SIGNAL: Medium.

RELATED: TH-I4-01, TH-I4-20.

HISTORICAL-MOMENTUM-ONLY? No, but it is secondary.

### TH-I4-12 Does evaluator granularity set the landscape's step structure?

QUESTION: Shelves at 4/16 and 5/16 were identical under every
representation, and partial credit built the half-credit shelf. How much
of "landscape geometry" is the payoff's quantisation rather than the
substrate?

WHY IT MATTERS: Every "cliff", "shelf" or "plateau" finding could be a
property of the measuring stick.

WHAT IS KNOWN:
- "The landscape's steps are the evaluator's granularity"
  (archaeon/campaign1/CAMPAIGN_REPORT.md:186-191).
- Removing partial credit cut shelf arrivals from 11/12 to 8/12. It
  produced a different organism (two-value, .44-.65), but still no
  summit: "The payoff selects the plateau and the creature; it does not
  set the ceiling" (archaeon/campaign3/CAMPAIGN_REPORT.md:32-39,
  :138-141).
- StackVM stackvm-v1 was retracted because its steps/halt observables
  saturate at 44.3% (SerendipityFoundry stackvm_admission/
  VERDICT_CORRECTION.md, per delegate).

WHAT IS UNKNOWN: whether the all-or-nothing two-value organisms (.65) are
closer to the summit in edit distance than shelf organisms.

CHEAPEST DISCRIMINATOR: Fold into s5 D4, measuring summit edit distance
from both organism types.

LENSES: measurement theory; reward shaping.

NEW-LENS SIGNAL: Medium.

RELATED: TH-I4-02.

HISTORICAL-MOMENTUM-ONLY? No. It generalises to every current engine's
fitness readout.

### TH-I4-13 The flat elite: is the limit search capacity (N, G) or substrate capacity?

QUESTION: Under the frozen grammar, "selection ... does not climb these
worlds at all". After 36,000 evaluations the elite IS the starting
parent. A later frontier observation says the flat elite moves at N=200
on W3_K3, confounded by compute. Which is binding?

WHY IT MATTERS: This separates "the search is too weak" from "the
substrate cannot express the next step". That is the search-vs-substrate
question in the brief.

WHAT IS KNOWN:
- 0/24 cells improved; the elite is the starting parent
  (archaeon/campaign5/CAMPAIGN_REPORT.md:67-73).
- C5-09 found no held-out gain in 96 cells (same file :130-138).
- Frontier: "flat elite moves at N=200 on W3_K3, confounded by compute
  -> equal-compute N family queued" (b5280148c, 2026-09-18). No readout
  of that family was located. INFERRED from git log of archaeon/frontier
  (17 commits, last 1049aac73, 2026-09-26).
- The screened worlds had headroom: 9 eligible of 25
  (archaeon/campaign5/WORLD_SCREEN_2026-09-18.json;
  CAMPAIGN_REPORT.md:50-53).
- The operator closed the old substrate as OLD_SUBSTRATE_EXHAUSTED
  (CAMPAIGN_REPORT.md:193-200, D5-015).

WHAT IS UNKNOWN: the result of the equal-compute N family. It may exist
in the off-repo frontier stores: "runs/ and logs/ are artifact stores,
not git" (b5280148c).

CHEAPEST DISCRIMINATOR: Ask Archaeon for the equal-compute N-family
readout, or run the smallest version: W3_K3, N in {50, 200, 800}, equal
total evaluations, 6 seeds.

LENSES: population size and drift; search capacity.

NEW-LENS SIGNAL: Medium.

RELATED: TH-I4-02, TH-I4-16.

HISTORICAL-MOMENTUM-ONLY? Partly. The substrate is retired, but the
N-vs-substrate distinction is not.

### TH-I4-14 Does local fault insulation matter only where there is headroom?

QUESTION: Representation B (FIZZLE on undefined words) produced real
local recovery (229 vs 154) at no measurable cost, yet bought no
discovery. Was that because insulation is useless, or because the
worlds offered nothing to discover?

WHY IT MATTERS: Error containment is a candidate physical precondition
for evolvable computation, as in biology's modularity and
fault-tolerance.

WHAT IS KNOWN:
- Opcode faults recover (209 vs 15); register faults are lost (142 vs
  25). Insertion is the rescued operator (archaeon/campaign5/
  CAMPAIGN_REPORT.md:105-116).
- Insulation is cheap for the survivor (same file :117-120).
- NO_GAIN: under FIZZLE, .46-.80 of final population members carry
  executed faults, i.e. hidden load (same file :130-138).
- The C5-03 qualification rests on a post-hoc statistic change (D5-008;
  same file :85-95). The report flags it as the one thing a reviewer may
  reject.

WHAT IS UNKNOWN: the effect of insulation on a world selection can
climb. "Not established: anything about worlds that evolution CAN climb"
(same file :176-178).

CHEAPEST DISCRIMINATOR: Rerun C5-09's four arms on the one landscape
known to be climbable: the delay ladder, where 11/12 seeds become
general. Measure generations to generality.

LENSES: fault tolerance; genetic load; modularity.

NEW-LENS SIGNAL: Medium.

RELATED: TH-I4-05, TH-I4-01.

HISTORICAL-MOMENTUM-ONLY? Partly. It is worth one run on a climbable
world, and not more.

### TH-I4-15 Evolution vs competent search: what does selection buy over a good enumerator?

QUESTION: Apollo's evolution reached 0.833 in 3,144 evaluations, against
1.69M for breadth-first enumeration (537x fewer). No best-first or
pruned baseline was run. Does selection beat competent search, or only
naive search?

WHY IT MATTERS: The north star bets on evolutionary ecology. The record
has few comparisons against a competent non-evolutionary baseline.
Hephaestus-era Noesis found random search beating mutation and
tensor-guided search.

WHAT IS KNOWN:
- "the dumbest possible baseline" (f91b335ac).
- In the O1 enumeration, the capped tails would have produced a false
  win (3488a31b3).
- Noesis: random 0.2794 cracks/cycle, mutation .1054, tensor_topk .0230,
  over 69,498 cycles (roles/Hephaestus/surveys_2026-08-12, survey 00,
  per delegate).
- prometheus_math: REINFORCE and PPO collapse to 2-3 bins while least
  squares reaches over 60% on a linear control
  (prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md:14-18, per
  delegate).
- SFE D7 found the one positive: a certified nonlinear crossing in a
  median 23.5 vs 73 evaluations (SerendipityFoundry D7/README.md, per
  delegate).

WHAT IS UNKNOWN: selection's advantage over a heuristic enumerator on any
preserved problem.

CHEAPEST DISCRIMINATOR: On the Apollo O1 enumeration space (in git,
apollo/cycles/o1_enumeration/, 32 KB), run a best-first enumerator
ordered by a cheap partial score. Count evaluations to 0.833.

LENSES: search theory; no-free-lunch; evolution as heuristic.

NEW-LENS SIGNAL: Medium.

RELATED: TH-I4-16.

HISTORICAL-MOMENTUM-ONLY? No. Every current engine needs this baseline
class.

### TH-I4-16 Does selection discover, or only exploit what humans add?

QUESTION: Apollo's 5 capability widenings were all agent- or
human-supplied, and 0 were self-found. An LLM in the inner loop gave
zero lift over 2,152 mutations. An LLM in the outer loop supplied all
widenings. Where does novelty enter an evolutionary reasoning system?

WHY IT MATTERS: The north star's success criterion is mechanisms "no
human explicitly conceived" (roles/base-role/NORTH_STAR.md:16-17).

WHAT IS KNOWN:
- "5 were agent/human-supplied and 0 were self-found" (apollo/pivot/
  APOLLO_REVIVAL_REVIEW_2026-09-01.md:44-55, per delegate).
- The search exploits what is added within about 130 generations, then
  pads (same file).
- Granite mutations gave zero lift, and the run matched deterministic
  numbers exactly (roles/Apollo/STARTUP.md:96-105, per delegate).
- Hephaestus DESIGN_REVIEW s7.2 draws the inner- vs outer-loop contrast
  (per delegate).
- Rediscovery slowed 8.6x as the substrate grew (8d06112b7).

WHAT IS UNKNOWN: whether any engine has a self-found widening.
INFERRED: Crius (0/36) and the WSE summit suggest the same.

CHEAPEST DISCRIMINATOR: A census across old and current engines of each
capability widening, labelled self-found vs supplied, from repo records.
This is repo-only and extends Artemis T5.

LENSES: open-endedness; innovation source.

NEW-LENS SIGNAL: High. It directly measures the north-star failure mode.

RELATED: TH-I4-15, TH-I4-19.

HISTORICAL-MOMENTUM-ONLY? No.

### TH-I4-17 Why do Apollo's survivors all have exactly two primitives?

QUESTION: Four candidate causes were listed and never discriminated:
parsimony ghost, variance culling, NSGA-III niching, and curriculum.

WHY IT MATTERS: This is a clean compression or parsimony phenomenon: an
emergent size prior. It bears on whether selection produces compact
mechanisms or only small ones.

WHAT IS KNOWN: apollo/pivot/apollo_investigation_2026-05-22.md:264-276
(per delegate). The 500-generation no-parsimony run was never done
(same file :274).

WHAT IS UNKNOWN: which cause is responsible.

CHEAPEST DISCRIMINATOR: Mine the v2d lineage files in git
(apollo/archive/, about 2.8-2.9 MB each). Check whether 3-primitive
organisms ever arose and when they died, and whether their deaths
coincide with niching or with parsimony penalties.

LENSES: MDL and compression; selection for simplicity.

NEW-LENS SIGNAL: Low-medium.

RELATED: TH-I4-07.

HISTORICAL-MOMENTUM-ONLY? Yes, mostly. It is tied to a retired
architecture. Keep it only as a cheap fossil-mining exercise if the
compression lens is prioritised.

### TH-I4-18 Decorative load: are neutral, non-load-bearing parts the dominant product of unguided generation?

QUESTION: 86% of called Hephaestus primitives change no answer; 85% of
activated Proteus components have no marginal effect; Apollo's
"composition" was decorative (0/5 elites beat the best single
primitive). Is decorative structure the generic output of generation
under weak selection, and is it raw material or dead weight?

WHY IT MATTERS: This is the reasoning-tool analogue of the length and
neutrality finding (TH-I4-05). If it is universal, admission gates must
measure load, not presence.

WHAT IS KNOWN:
- 125/2,103 primitive knockouts cleared the impact bar. FAIL_ABLATION
  never fired because of a wrong-sign predicate
  (roles/Hephaestus/DESIGN_REVIEW_2026-09-01_external.md s1, s5.1, per
  delegate).
- About 1,960 files amount to about 5 mechanisms "in costumes" (survey
  12; roles/Hephaestus/ROLE.md:69-70, per delegate).
- Apollo decoration (3ebdad8b4).
- Proteus activation-without-effect (closure packet :428-432, per
  delegate).

WHAT IS UNKNOWN: whether decorative parts later become load-bearing
(exaptation), as TH-I4-06 asks for neutral code.

CHEAPEST DISCRIMINATOR: From agents/hephaestus/ledger.jsonl (2.4 MB,
6,661 rows) and forge/verdicts/ (203 files), check whether any primitive
that was delta=0 in one tool is load-bearing in a later tool.

LENSES: neutral theory; exaptation; bloat.

NEW-LENS SIGNAL: Medium.

RELATED: TH-I4-05, TH-I4-06.

HISTORICAL-MOMENTUM-ONLY? Partly. The forge is dead, but the ledger is a
free dataset.

### TH-I4-19 Is there a certifiable "outside the closure" target, i.e. something selection provably cannot compose?

QUESTION: Can one certify that a target behaviour is not composable from
a given operator and primitive set, on a real ecology substrate?

WHY IT MATTERS: This would convert "0/N found it" from an absence of
evidence into a structural statement of what selection cannot find.

WHAT IS KNOWN:
- The closure gauntlet has one synthetic positive control: 18/20 LOST
  targets were classified OPERATOR
  (roles/Hephaestus/REVIEW_PACKET_2026-09-11_base_role_and_specimen3.txt
  :119-128, per delegate).
- HEPH-32 (the gauntlet against the SFE VM "C4 cliff") is NOT RUN and
  waits on an operator answer (roles/Hephaestus/BACKLOG_H0H5.md:38).
- The gauntlet's own instrument failures were self-found: a bool()
  coercion and an out-of-ring alphabet (CALIBRATION.md:112-148, per
  delegate).

WHAT IS UNKNOWN: everything on a real substrate.

CHEAPEST DISCRIMINATOR: Point HEPH-32 at the W2_K2 two-value memory
(TH-I4-02) instead of "the cliff". That target is well-defined. Given
TH-I4-04, "the cliff" may not be.

LENSES: computability and closure; expressivity vs accessibility.

NEW-LENS SIGNAL: High.

RELATED: TH-I4-02, TH-I4-04.

HISTORICAL-MOMENTUM-ONLY? No.

### TH-I4-20 Mature material pays, immature costs: is there a maturity law for inheritance?

QUESTION: Across producer-consumer experiments, one solved producer bought
a foothold (charged generation 30 vs 50), while immature artifacts were
a net loss. Is inheritance value a threshold function of source maturity?

WHY IT MATTERS: It bears on when a later consumer should read the
ecology's residue at all (charter commitment 1, "experience must have a
consumer").

WHAT IS KNOWN:
- archaeon/campaign1/CAMPAIGN_REPORT.md:193-200.
- A producer that solves by about generation 19 beats the consumer's own
  exit by 10-24 generations; a non-solving producer costs its whole cap
  (archaeon/campaign2/CAMPAIGN_REPORT.md:277-281).
- Wall-clock +0.109 is WEAK, n=6, and unreplicated. The full-solve
  version was void (archaeon/campaign3/CAMPAIGN_REPORT.md:248-258).
- Ergon memory retention +2.78pp fell to null on replication (09e53b630,
  596e36fe2, per delegate).

WHAT IS UNKNOWN: whether the relationship is a threshold or graded.

CHEAPEST DISCRIMINATOR: Re-analyse SFE-10, C2-SFE-07 and C3 rows in git,
plotting exchange effect against producer maturity (generation first
solved).

LENSES: economics of information; teacher quality.

NEW-LENS SIGNAL: Low-medium.

RELATED: TH-I4-10.

HISTORICAL-MOMENTUM-ONLY? Partly.

### TH-I4-21 Where does the novelty in LLM-generated mechanisms come from: model, prompt, or size?

QUESTION: Prompt template dominated model identity (5 of 12 models
usable, all within 2.3pp). Size "buys a mechanism's existence, not its
quality". R2 and R4 do not move at any size.

WHY IT MATTERS: LLMs are allowed as proposers (charter commitment 3). If
their output is template-bound, they inject one "costume" of mechanism,
not diversity.

WHAT IS KNOWN:
- roles/Hephaestus/CALIBRATION.md:95-96 (per delegate).
- The xpol packets (REVIEW_PACKET_2026-09-19_xpol_small_set.txt,
  REVIEW_PACKET_2026-09-23_xpol_addendum_size_gradient.txt).
- In HEPH-33 the originals won 2-1 on paired packets
  (roles/Hephaestus/BACKLOG_H0H5.md:39).
- Only Llama-4-Maverick escaped the template monoculture (ROLE.md:72-73,
  per delegate).

WHAT IS UNKNOWN: the behavioural diversity of mechanisms when the prompt
is varied at fixed model.

CHEAPEST DISCRIMINATOR: Behavioural clustering of the preserved
hephaestus/xpol_2026/ tools (5.4 MB) by solve-set, not by source. This is
repo-only.

LENSES: diversity of proposal distributions; mode collapse.

NEW-LENS SIGNAL: Medium.

RELATED: TH-I4-16, TH-I4-22.

HISTORICAL-MOMENTUM-ONLY? Partly. It matters only if LLM proposers
return to the loop.

### TH-I4-22 Modal collapse: is exploration collapse a property of the learner or of the landscape?

QUESTION: REINFORCE collapsed the kill-ledger entropy to 0.031 bits. On a
synthetic linear control the collapse persisted while least squares
succeeded. Does search in this ecology collapse onto modal classes
generically?

WHY IT MATTERS: Loss of variation is the physical failure mode of any
open-ended search.

WHAT IS KNOWN:
- prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md:70-76.
- MODAL_COLLAPSE_SYNTHETIC_RESULTS.md:14-18.
- MODAL_COLLAPSE_CONTINUOUS_RESULTS.md:17-23: top-3 mass >= 99.3%.
- DISCOVERY_V2_ANTI_ELITIST_RESULTS.md:13-18: the restart never
  triggered.
- (All per delegate.)
- The WSE counter-example: under takeover, genome diversity stays at
  .78-.99 while ancestry fixes (TH-I4-09).

WHAT IS UNKNOWN: whether "diversity" measured on genotypes, ancestry or
behaviour gives the same answer. The WSE says it does not.

CHEAPEST DISCRIMINATOR: Recompute the three diversity measures (genome,
origin, behaviour class) on the preserved C3-SFE-10 rows (in git).

LENSES: exploration-exploitation; entropy production in search.

NEW-LENS SIGNAL: Low-medium.

RELATED: TH-I4-09.

HISTORICAL-MOMENTUM-ONLY? Partly. The prometheus_math line is dead; the
measurement question is not.

### TH-I4-23 Nothing could fire: are the H0/H1 questions still worth posing?

QUESTION: H0 (library x pack) and H1 (relevant failures) never got a
corpus in which the effect could fire:
- the witnesses collapse to 4 inputs with pool = K;
- the library from the phase-1 solutions has 0 components;
- Stitch finds only arity-0 abstractions.
A 4-input universe has been sized (893/65,536 tables solvable at size 7)
and not run.

WHY IT MATTERS: "Does retained experience change later search" is the
charter's first milestone (CHARTER_AND_CONTINUITY.md, "The next
strategic milestone").

WHAT IS KNOWN:
- roles/Harmonia/rulings/RULING_H1H0_PHASE2_CONTRASTS_2026-09-14.md:
  14-21, :47-52, :99-101.
- roles/Archaeon/H0H5_STATUS.md:212-236.
- ae019fb79; f8b1f1cde.
- (All per delegate.)

WHAT IS UNKNOWN: everything scientific.

CHEAPEST DISCRIMINATOR: Before running anything, count how many of the
893 solvable 4-input tables share a nontrivial subterm with at least one
other table (component eligibility). This is stdlib arithmetic over a
truth-table universe.

LENSES: library learning (DreamCoder-style, as a calibration arm);
eligibility.

NEW-LENS SIGNAL: Low.

RELATED: TH-I4-10.

HISTORICAL-MOMENTUM-ONLY? Largely yes. The alpha designs exist because
H0-H5 was the plan of record (CHARTER_AND_CONTINUITY.md, "How H0-H5
serve"). The eligibility count is worth doing. The full alpha re-launch
is justified only if it answers TH-I4-10 better than the WSE did.

### TH-I4-24 CA computation: the position-keyed reset hypothesis

QUESTION: Is particle2's delayed-recall margin (0.58-0.61 vs 0.5) just a
position-keyed readout of the reset lattice, with no information
transport?

WHY IT MATTERS: This decides whether H2 ("CA dynamics as reusable
computational components") ever had a positive.

WHAT IS KNOWN:
- 0.608 was a weak positive. The localisation was then found to be not
  distinctive: a hand-designed GKL rule was equally localised, and the
  permuted reset was as good in 5/8 (archaeon/campaign3/
  CAMPAIGN_REPORT.md:260-283).
- H2 alpha OBSTRUCTION: 0 of 63,488 non-zero features
  (herakles/ca_stream/OBSTRUCTION.md:1-45, per delegate).
- The run_alpha_v2 rerun was never written.

WHAT IS UNKNOWN: the answer to the one falsification C3 asked for (C4-7,
same file :496-500).

CHEAPEST DISCRIMINATOR: Train a readout on the reset lattice alone, with
no CA dynamics, on the same d=2 task (herakles/ca_stream is a pure
library per C_engines.md). Minutes on a laptop.

LENSES: reservoir computing; attribution.

NEW-LENS SIGNAL: Low.

RELATED: none active.

HISTORICAL-MOMENTUM-ONLY? Yes, except as a closing falsification. C3
itself said "only as a falsification" and that the line "closes
permanently" if it reproduces.

### TH-I4-25 Instrument-before-substrate: why did the old lines' instruments fail more often than their substrates?

QUESTION: Across Apollo (CAL-04/05/09, the lineage wipe), Hephaestus (a
gate that could never fire), Proteus (8 self-found defects, timing
fields breaking replay), H0-H5 (vacuous readings V-001..V-006) and the
campaigns (CRN broken, harness-seeded fills), is there a small
pre-launch battery that catches most of these?

WHY IT MATTERS: It extends Artemis THREADS T5 backward in time. The
old-pipeline data roughly doubles the failure-class sample.

WHAT IS KNOWN: every delegate report lists these defects. See s3.

WHAT IS UNKNOWN: their classes' recurrence rate after being documented.

CHEAPEST DISCRIMINATOR: Merge into Artemis T5, adding the pre-09-18
cases.

LENSES: metrology.

NEW-LENS SIGNAL: Low for physics of intelligence; high for the program.

RELATED: Artemis T5.

HISTORICAL-MOMENTUM-ONLY? No as a practice. It is not a
physics-of-intelligence question itself.

-----------------------------------------------------------------------

## 3. Anomalies and reversals

| # | Claim / observation | What happened (failure SHAPE) | Evidence |
|---|---|---|---|
| A1 | C1 SFE-01 components 2/3 vs 0/3; SFE-07 failed genotypes 2/3 vs 0/3 | Died at n >= 10 under CRN (+0.009, +0.002). Controls' zeros were harness artefacts, and shuffled/opcode-only beat intact. Shape: small-n positive with a broken control | archaeon/campaign2/CAMPAIGN_REPORT.md:152-178 |
| A2 | Basin share predicts search (rho -0.59) | Replicated pooled -0.568, but it was a two-strata artefact; the manipulation had no effect. Shape: pooling across strata | archaeon/campaign3/CAMPAIGN_REPORT.md:209-246 |
| A3 | CA recall is distributed (C1) | Then localised (C2), then equally localised in an unevolved rule (C3). Shape: interpretation reversed twice; effect size stable | campaign1 :156-162; campaign2 :183-187; campaign3 :260-283 |
| A4 | Import takeover means transferred capability | Incompetent permuted controls take over equally. Shape: selection mechanics mistaken for fitness | C3-SFE-10/RECORD.md:190 |
| A5 | BEE: SFE takeover is an offspring-cap artefact | Contradicted by the source table (takeover with no cap). Shape: cross-substrate attribution error. INFERRED | REVIEW_PACKET_2026-09-19.md:118-120, :140 vs campaign3 :285-307 |
| A6 | Accessible variation helps search (H5 premise) | Balanced encoding 9x slower; rho -0.23. Shape: the premise inverts | campaign1 :170-174; campaign2 :188-191 |
| A7 | H5 "learned" decoder advantage | A random balanced permutation matches it (11.72 vs 11.7305); possibly mislabelled as learned. Shape: analytic-bound calibration read as evidence | f2c2452ea; H5_1_READOUT_2026-09-11.md:24-40 (per delegate) |
| A8 | "0/5,472 edits improve": a substrate cliff | Partly parent-headroom: about 2,339 children from at-ceiling parents, 1,035 from degenerate parents. INFERRED; D7 eligibility never reported | DAMAGE_GEOMETRY_MAP.md:23-26; C4-01/READOUT.md:55-68 |
| A9 | Apollo 0.833 is reasoning capability | 0.0667 on an independent blind battery (40/42 abstained). Shape: parsers keyed to problem-text templates | 9b00453ca |
| A10 | Apollo "composition emerging" | 0/5 elites beat the best single primitive; ablation fitness fell to -0.05. Shape: decorative | 3ebdad8b4 |
| A11 | LLM mutation needed (Apollo) | 2,152 mutations, zero lift. Shape: pre-registered kill fired | roles/Apollo/STARTUP.md:96-105 (per delegate) |
| A12 | Apollo rediscovery 4/5 in June | 8.6x slower in August as the substrate grew. Shape: capability diluted by a larger primitive set | 8d06112b7 |
| A13 | Hephaestus "LLMs mass-produce novel tools" | Under a behavioural metric, 386 tools had orthogonality 0.0 and 0 unique solves. Shape: diversity measured on source, not behaviour | ROLE.md:69-70; survey 12 (per delegate) |
| A14 | Hephaestus admission gates select | FAIL_ABLATION could never fire (wrong sign); thresholds softened in a DO-NOT-MODIFY file. Shape: the gate was not wired | forge/thresholds.py:3,16,22; DESIGN_REVIEW s5.1 (per delegate) |
| A15 | prometheus_math modal collapse is a substrate finding | Reproduced on a synthetic linear control. Shape: learner pathology | MODAL_COLLAPSE_SYNTHETIC_RESULTS.md:14-18 (per delegate) |
| A16 | Proteus V0.4 halt/yield effect z=3.53 | Inverted in V0.5 (+0.0118). A same-shape candidate (genome_length, z=3.55) was not chased. Shape: underpowered sign flip | PROTEUS_PROGRAM_REVIEW_PACKET_V0_TO_V0_5.txt:162-177 (per delegate) |
| A17 | Ergon Gen-1B memory +2.78pp (Holm .004) | P1 -0.31pp, P3 +0.55pp, CIs spanning 0. Shape: regression to null | 09e53b630; 596e36fe2 (per delegate) |
| A18 | stackvm-v1 QUALIFIED | STACKVM_NULL_COMPROMISED: observables saturate at 44.3%. Shape: ceilinged observable | stackvm_admission/VERDICT_CORRECTION.md (per delegate) |
| A19 | C5-03 representation qualified | a01 failed its own statistic; a02 passed under a post-hoc change (D5-008). Shape: post-hoc metric swap, disclosed | archaeon/campaign5/CAMPAIGN_REPORT.md:85-95 |
| A20 | C4-09 / C4-10 worlds | 3 of 4 held-out worlds were pre-solved by the starting parents. Shape: task already solved at generation 0 | archaeon/campaign4/CAMPAIGN_REPORT.md:57-62 |
| A21 | Unexplained: permuted controls are BETTER seed material than fresh generation 0 | W1_d4 summit 4-7/12 vs 0/12. Exploratory, not preregistered | C3-SFE-10/RECORD.md:205 |
| A22 | Unexplained: ENVGATE-02 all-blocked arm | 5 establishments vs ~0.7 predicted, concentrated in the slowest blocks | archaeon/envgate2/VERDICT_2026-09-26.md:41-55 (per delegate) |
| A23 | Unexplained: identical shelf programs | Shelf specimens #11, 12, 14, 18 and 20 are one program; 5 provenances collapsed to one organism | proteus/round2/ANATOMY_L0.md:140-150; STARTING_POPULATION.json collapsed_duplicates |

-----------------------------------------------------------------------

## 4. Recurring shapes

S1. Bimodal damage (silent or catastrophic). Found on:
- the StackVM (1f0e4ae01);
- the WSE tape VM (C4-01/READOUT.md:60-64);
- the Proteus graph VM (PROTEUS-46);
- Apollo, where the best single-edit neighbour stays at 0.30
  (recombination_findings :40-68).
Harmonia A predicted it (845084a21, per delegate). Four substrates show
it, which makes it the strongest cross-substrate regularity in the
territory. Whether it is a property of "total interpreters over dense
encodings" is untested.

S2. A large neutral network with a small payoff:
- 188/188 walkable, exaptation .016 to .082 (C4-05, C5-01);
- graph NODE_ADD 100% neutral and useless (PROTEUS-46);
- 86% of Hephaestus primitives inert;
- Ergon: only 23% of behavioural duplicates are mutationally redundant.

S3. Existence is not accessibility:
- the W2_K2 summit (C3);
- Crius, 0/36 (CRIUS_C2_TERMINAL_REVIEW.md:271);
- Nestor's 4-edit valley (3af735d67);
- Apollo's valley, which only crossover crosses.
Crius and Nestor found this after C3 and cite Apollo, not C3 (INFERRED
from grep: no crius/ file cites archaeon/campaign3).

S4. Positives die under a stronger control. Examples: C1 transfer, basin
share, CA localisation, Apollo 0.833, Hephaestus diversity, Ergon Gen-1B,
Proteus halt/yield. The Artemis REPORT s3.3 table has the same shape for
post-09-18 engines. The old pipeline is the earlier half of the same
distribution.

S5. The value carrier is the envelope, not the arrangement: length and
opcode multiset in C2-SFE-04 and C3-SFE-10, and length as robustness in
C4-08 and C5-08. The opposite holds on typed substrates (Apollo splice).

S6. Selection mechanics masquerading as capability:
- takeover (C3-SFE-10);
- REINFORCE modal collapse;
- ENVGATE parent-chain counts 8-42x the genetic counts
  (VERDICT_2026-09-26.md:50, per delegate).

S7. The instrument fails before the substrate: CRN broken, harness fills,
wrong-sign gates, timing fields in digests, eligibility-0 detectors.
Shared with Artemis T5.

S8. Human- or agent-supplied widening; no self-found widening
(TH-I4-16). Apollo's record is explicit. INFERRED for the WSE: every
change of substrate (representation B, graph organisms) was designed by
a seat.

S9. Re-discovery without citation (INFERRED from citation greps):
- Crius and Nestor re-found the accessibility valley;
- BEE re-ran C2-SFE-06 and C3-SFE-10 deliberately (SELECTION_FROZEN.json),
  the only explicit cross-era reuse located;
- Hephaestus re-found "template beats model" 4 months later (xpol,
  09-19/23);
- the decoration finding was found three times (PipelineOrchestrator in
  April, Lexis in August, Aporia SELECTOR in August; per delegate).
roles/Aether, roles/Cosmos, roles/Ensorain, roles/Ananke and roles/Ares
contain 0 files citing archaeon/campaign1-5 artefacts (grep, this
session).

-----------------------------------------------------------------------

## 5. Cheap discriminators

All of these run on a 4-core, 7 GB Linux laptop with stdlib Python, from
git alone.

Runtime basis (PILOT, this session): archaeon.wse.evolve.evaluate is
stdlib plus proteus.foundry, which is also stdlib (imports checked in
archaeon/wse/*.py and proteus/foundry/*.py). 57 evaluations of 16
episodes took 2.9 s, i.e. about 50 ms per evaluation per core. Use
PYTHONDONTWRITEBYTECODE=1 and sys.path entries for the repo root and
SerendipityFoundry/SerendipityFoundryClient (as in
archaeon/campaign4/c4_01.py:24-27).

D1 (TH-I4-01) Knockout map of the delay-invariant reader. The highest
information per CPU-minute in this territory.
- Load proteus/round2/ANATOMY_L0_ABLATION_SETS.json: ready-made
  instruction_nop knockout manifests for delay_general, w0_solver and
  shelf.
- Evaluate each knockout on W0, W1_d1, W1_d4, W1_d8 and W1_d16 with the
  held-out episodes (episodes_for, campaign seed 20260921).
- Output: per-organism sets of instructions needed for W0 recall vs
  instructions needed only for delay. The "delay-only" set is the
  candidate mechanism.
- Cost: about 850 knockouts x 5 environments x 50 ms, roughly 3.5
  CPU-minutes, about 1 minute on 4 cores.
- PILOT (3 organisms, W1_d16 only): 3-9 critical instructions each.
Follow-up at the same cost: replace critical instructions one at a time
with each of the 25 opcodes, to find which are opcode-specific and which
are only position-holders.

D2 (TH-I4-01) Selection vs construction. Regenerate a W0 generation-0
population and its generation-30 population from WSE seeds
(archaeon/wse/evolve.py gen0/run_cell). Evaluate every member on W1_d8
and W1_d16. The fraction already general before any delay pressure
answers "select or build". Cost: N=200 x G30 x 16 episodes, a few
minutes per seed.

D3 (TH-I4-04) D7 eligibility of the 0/5,472 cliff. Pure tabulation of
archaeon/campaign4/C4-01/attempts/a02/rows.json (478 KB) and
children.json.gz (1.06 MB). Group by parent stratum and by parent reward
on its own environment. Report how many children had a parent below the
max reward minus the 1/16 band, i.e. eligible for D7. Under a minute.

D4 (TH-I4-02, -12, -19) Summit distance.
- Hand-write a two-value keyed-memory program for W2_K2 in the Proteus
  VM and verify it reaches >= 0.9.
- Compute its edit distance, in instructions, from each shelf specimen
  and from the C3-SFE-08 all-or-nothing organisms (in git under
  archaeon/campaign3/C3-SFE-08/).
- Count how many single-edit intermediates along the shortest path fall
  below the parent's reward. The count is the valley depth in edits.
- Cost: minutes, plus a person-hour to write the program.

D5 (TH-I4-06) Neutral-walk exaptation vs length. Regenerate the C4-05
walks from seeds (the walk is a pure function of seeds,
archaeon/campaign4/DECISIONS.md:136-139). Attribute each exaptive event
to its length change. Cost: 188 walkers x 16 steps x about 2
evaluations, about 5 CPU-minutes.

D6 (TH-I4-03) Typed vs positional splice. On the Apollo recombination
fixture (apollo/scripts/recombination_ab.py, tracked in git; it imports
blackboard_evolve, whose dependencies are unverified), swap the typed
splice for a positional cut. Prediction under the INFERRED interface
hypothesis: 4/5 falls toward 0/5. Five seeds x 400 generations x pop 24;
minutes if the fixture is stdlib (unverified).

D7 (TH-I4-09, -22) Takeover forensics. Re-read
archaeon/campaign3/C3-SFE-10/rows.json (in git; 228 rows with
takeover_gen and import_share_final per SELECTION_FROZEN.json:60).
Tabulate takeover generation against the length of the imported
material. If per-generation origin data is absent, replay 2 control runs
from seeds with origin-labelled tournament logging. Cost: 2 x N200 x
G60, about 2-3 CPU-minutes.

D8 (TH-I4-07) Within-family geometry. Partial-correlation re-analysis of
the C2-SFE-08 (52 rows) and C3-SFE-06 (48 rows) tables in git. Seconds.

D9 (TH-I4-23) H0 eligibility. Over the 4-input universe (65,536 tables;
893 solvable at size 7 per ae019fb79), count table pairs sharing a
nontrivial subterm. Stdlib enumeration of small expressions. Minutes.

D10 (TH-I4-24) Reset-lattice-only readout for CA d=2 recall, with
herakles/ca_stream as the library. Minutes.

Priority, if only one runs: D1, then D3. D1 attacks the only unexplained
positive capability. D3 re-grades the most-cited negative. Together they
take under 5 minutes.

Off-repo data that would unlock more:
- the M1 SFE ledger eng_8a37a5d3 (89,939 experiments; SKULLPORT D:),
  per Artemis THREADS T1;
- the frontier runs/ and logs/ stores (b5280148c), for TH-I4-13;
- Apollo Branch C evolve logs (gitignored, .gitignore:425, per delegate);
- genesis/harmonia_b/results/ (untracked; 3,600 search runs, per
  delegate);
- the Hephaestus 346 GB corpus on one un-backed-up box (per delegate).
