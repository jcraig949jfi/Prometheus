# REPORT -- can a declared varied / held / observed lens field make engine convergence measurable?

## 1. WHAT I SET OUT TO TEST

The proposal is that if every engine's experiment record declared what it varies and what it observes
(and, in the extended form, what substrate it holds fixed), then convergence between seats -- the known
case being three independent Z80 byte-VM builds made from one directive -- would become detectable
mechanically. I tested three things on real, already-committed experiment records: (a) whether the field
can be assigned reliably at all (two independent annotators agreeing), (b) whether collisions on the
proposed (varied, observed) pair recover the known Z80 convergence and how many false alarms they raise,
and (c) whether adding a held-substrate code changes (b). I did not build an index or modify any
registry; this is a retrospective measurement of whether the field works as an instrument.

## 2. WHAT I DID

- Corpus: 33 preregistration records from 11 seats/engine lines, extracted verbatim (first 24 KB each)
  from the read-only clone: 31 from origin/main @ 6ff2b2f8a and 3 Bellerophon records from
  origin/bellerophon/multiday-campaign-2026-09-26 @ ee7a7d954. The full list with paths is in
  corpus_index.tsv; the texts are in corpus/X01..X33.txt. 13 records are Z80-family (Nestor z80atlas x4,
  Bellerophon coupling/multiday/grounding x3, Archaeon envgate/envgate2/census/denovo x4, Odysseus
  z80_threshold x2, which runs on Bellerophon's VM); the rest cover Aether, Cosmos, Ensorain (WTP),
  Ananke (PTE), Aphrodite, Archaeon's SFE campaigns, Nestor CW01, Harmonia, SFE D8, the Bellerophon
  kernel and Odysseus natural-induction.
- Codebook (CODEBOOK.md): varied = the seven proposed values (environment, representation, physics,
  organism-boundary, memory, communication, improver) plus none/other; observed = 9 values plus other
  (replication, descent, population-stats, complexity, task-skill, law-invariant, signal-dependence,
  improvement-rate, instrument); held = 10 substrate families (byte-vm, lattice-field, world-graph,
  float-memory, packet-network, neural-swarm, bitstring, code-worker, llm-agent, other).
- Two independent annotators (separate model sub-agents) coded all 33 records from the record text and
  the codebook only. They were not told the engine names, the landscape document, or the ground truth.
  One worked forward and one worked in reverse order. Outputs: annot_A.json and annot_B.json.
- Ground truth for "known convergent": every cross-seat pair of records where both records are Z80-family
  (62 of 480 cross-seat pairs). This is the convergence the source document named.
- Analysis: analyze.py plus an inline follow-up (output in analysis_out.txt). I computed Cohen's kappa
  and flagged-pair recall and precision under three keys: (varied1, observed1), held, and the triple.
- Premise checks: atlas/harvest/archaeon_campaigns.py on origin/main still matches only
  archaeon/campaignN/, so envgate, envgate2 and z80atlas are not harvested (the premise holds). No
  varied/observed field exists anywhere under atlas/. The named lens-card prototype exists only under
  an excluded path, so I did not read it or use it.

## 3. RESULT

Reliability (n=33, primary code): varied kappa 0.73 (79% agreement); observed kappa 0.74 (79%; the
annotators' code sets overlapped on 100% of records); held kappa 0.76 (82%). The combined (varied,
observed) pair is less reliable: kappa 0.57 (61%). Disagreements cluster where the seven-value varied
vocabulary does not fit. Cosmos "change almost everything" was coded environment by A and physics by
B on all 3 records. PTE C1 was coded communication by A and physics/environment by B. Harmonia and
Nestor CW01 got memory or none versus representation or environment.

Detection of the known Z80 convergence (62 cross-seat pairs; annotator A / B):

| key                         | flagged | true pos | false pos | recall    | precision |
|-----------------------------|---------|----------|-----------|-----------|-----------|
| (varied1, observed1)        | 25 / 25 | 21 / 14  | 4 / 11    | 0.34/0.23 | 0.84/0.56 |
| any varied & any observed   | 52 / 52 | 34 / 33  | 18 / 19   | 0.55/0.53 | 0.65/0.63 |
| held only                   | 100/ 87 | 62 / 62  | 38 / 25   | 1.00/1.00 | 0.62/0.71 |
| (held, varied1, observed1)  | 21 / 14 | 21 / 14  | 0 / 0     | 0.34/0.23 | 1.00/1.00 |

What the collisions contain:
- Under both annotators, the triple collides only for Nestor, Bellerophon and Odysseus Z80 records
  (physics x replication on a byte VM). Archaeon's Z80 records (environment x descent/replication)
  never collide with any other seat under either annotation.
- So the varied/observed pair does not measure the Z80 triplication as such. It splits it. Nestor
  and Bellerophon (plus Odysseus, which reuses Bellerophon's VM) ask the same question on the same
  substrate; Archaeon's build, on that substrate, asks a different question. This matches the source
  document's own verdict: not distinct as a world, distinct as a method. Here that verdict was reached
  independently by blind coding.
- The substrate (held) is what captures "three builds of one world". It does so with recall 1.00 but
  precision 0.62-0.71. The false alarms are shared generic families, for example several different
  world-graph systems, and SFE D8's stack VM counting as byte-vm.
- Collisions on the pair alone outside the Z80 family (4 for A, 11 for B) are mostly vocabulary
  coarseness: BEE kernel versus WTP (representation x task-skill), and CWE versus PTE (physics x
  law-invariant, B only). One looks like a possibly real overlap nobody had listed: Archaeon's
  SFE-driven campaign records and Aphrodite both code as improver x improvement-rate, under both
  annotators. SFE D8, Aphrodite and Odysseus natural-induction all code as improver x task-skill.
- Within one seat, varied is not constant. Archaeon spans environment, improver and none; NPE spans
  physics, environment and memory. The lens is a property of an experiment, not of an engine, so an
  engine-level tag would hide both convergence and divergence.

Plain conclusion: the field can be assigned with substantial reliability, and it does make convergence
measurable, but only as the three-part key (held, varied, observed). The two-part varied/observed pair
alone has 23-34% recall and 56-84% precision on the known case. It cannot see "same world built three
times", because that convergence is in the held substrate, not in the lens. The seven-value varied
vocabulary is the weakest part: most disagreements and most false alarms trace back to it.

## 4. DID IT RESOLVE THE QUESTION

Partly. It settles whether the field is workable (yes, with kappa about 0.73-0.76 per field) and what
it detects (lens convergence, not substrate convergence), on 33 records with one known convergence
case. Four things remain open:
- The ground truth is defined by substrate, which makes the held key's perfect recall partly circular.
  The informative numbers are the pair's low recall and the triple's zero false alarms.
- The annotators were model sub-agents, not the seats. Self-declared tags might agree more, or might
  be gamed.
- There is only one known-convergent case, and 33 records is a small sample.
- I did not test whether "must justify or merge" changes seat behaviour.

## 5. CONSEQUENCES

- False premise, partly: "two engines on the same varied/observed pair must justify or merge" would
  not have caught the Z80 triplication as a whole. It would have cleared Archaeon's build and flagged
  only Nestor versus Bellerophon. A held/substrate code is needed. Recommend the record carry
  held_substrate plus a concrete substrate_name (implementation path), and that convergence be
  defined on the triple.
- Instrument design fix: the varied vocabulary needs sharper boundaries between environment and
  physics (the CWE and PTE disagreements), a "communication-physics" rule, and an explicit "none"
  for census/instrument records. Declare the field per experiment, not per engine.
- A candidate lead, not verified: Archaeon's SFE campaigns and Aphrodite both test whether an
  improver gets better at improving (improver x improvement-rate), and SFE D8, Aphrodite and Odysseus
  natural-induction share improver x task-skill. The seats involved, or whoever owns the cross-engine
  standard, should check whether this is real duplication.
- A known result reproduced independently: Nestor and Bellerophon Z80 work share one lens; Archaeon's
  Z80 work is methodologically distinct.
- Premise confirmed: the Atlas harvester still does not index envgate, envgate2 or z80atlas, and no
  lens field exists in atlas/. Whoever owns Atlas and the cross-engine contract should know. The
  artefacts (CODEBOOK.md, annot_A/B.json, analyze.py) are a ready-made pilot for that standard.

## 6. COST

About 45 minutes of my own time. Local CPU was negligible (well under 1 CPU-minute; git extraction and
a pure-Python analysis). Two annotation sub-agents ran concurrently for about 5-6 minutes each. I did
not use Postgres, did not run any repository code, and did not consult the lens-card prototype (it sits
in an excluded path). Not done: annotation by the seats themselves, a larger corpus (more than 280
prereg files exist on main), a non-substrate-defined ground truth, and any registry change.
