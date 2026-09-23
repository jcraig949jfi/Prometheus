# Z80 x Atlas campaign - defects found during execution

Recorded while the campaign runs. NOT FIXED IN FLIGHT, deliberately: the campaign froze its
thresholds and flag rules before launch, and editing either one after seeing results is the
post-result threshold change the directive forbids. Both defects are in the SPECIAL-FLAG
layer, which is a preservation trigger ("keep this, look at it later"), not a promotion
mechanism. The map in the packet is built from matched pairs and is unaffected. Post-hoc
adjudication is handled by adjudicate.py, which reads the frozen record and applies rules
that are declared in the script rather than in the scheduler.

---

## Z80A-D01 - special flags mix a historical event with a final-state measurement

Severity: medium. Layer: scheduler.special_flags. Status: OPEN, adjudicated post hoc.

`summary["crossed"]` is TRUE if any organism ever reached the held-out threshold at any
validation pass. `summary["held_max"]` is the best held-out score among organisms ALIVE AT
THE END. The two disagree whenever a crossing lineage later dies, which in these worlds is
common: space is contested, the reaper runs, and a competent lineage can be overwritten.

REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION fires on the historical flag and then reports
the final-state numbers as its evidence, with no margin requirement. At 11.9 hours, the 13
instances had these margins (endogenous minus external, final-state held):

    0.833  0.750  0.667  0.146  0.083  0.083  0.062  0.000  0.000  -0.083  -0.083  -0.167  -0.750

Three of thirteen exceed 0.25. Four are NEGATIVE, meaning the exogenous control finished
better than the endogenous run that was flagged as reaching something the control could not.

Correct reading: the flag marks runs to preserve, and it does that. It is not evidence of
the effect it names. Adjudication requires a margin, requires the endogenous run to be at
threshold at final state, and requires the control to be below it.

---

## Z80A-D02 - the reservoir flag does not require the reservoir to have done anything

Severity: medium. Layer: scheduler.special_flags. Status: OPEN, adjudicated post hoc.

RESERVOIR_CROSSED_A_MOAT fires when a run whose structure is RESERVOIR, and whose task has
the answer-before-read moat, ever crossed. It does not check that the easy niche supplied
the lineage that crossed, and it does not check the reproduction physics. At 11.9 hours, of
24 instances:

- 22 of 24 came from SEEDED instrument populations, so they cannot support a claim about
  what evolution found unaided.
- Several carry EXTERNAL reproduction, which is the exogenous control, not a reservoir
  result.
- Evidence values include held 0.375 and held 0.0, both far below the 0.90 crossing
  threshold, again because of D01.
- Niche occupancy in the instances inspected is roughly uniform across all four niches,
  which is consistent with no stepping-stone structure at all.

What would be needed to support the claim the flag names: the crossing lineage's ancestry
traced back into the easy niche, which requires the lineage records rather than the
summary. The lineage records are preserved per run, so the question is answerable after the
campaign; the flag simply cannot answer it by itself.

---

## Z80A-D03 - the index whitelist omits the replication evidence, and the adjudicator read it there

Severity: low for the campaign, high for anyone reading the index alone. Layer:
scheduler.on_complete (index whitelist) and adjudicate.py. Status: adjudicator FIXED, index
schema deliberately unchanged.

Each index row carries a whitelist of headline summary keys. That whitelist includes
`replicated` and `replication_rate` but NOT `replication_events` or
`births_similar_no_write` - the two counters that distinguish a birth backed by evidence
that the organism placed the child's bytes from a resemblance that copying never caused.
The per-run RESULT.json has always carried both.

The first version of adjudicate.py read them from the index, found them absent, and
returned INADMISSIBLE for all 36 SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES flags with the
reason "no evidence-backed replication event in the run". That reason was false. Read from
the per-run record, the same 36 runs each show replication_events >= 1 with first-replicator
fidelity at or above 0.90, from populations that were genuinely random and unseeded.

Two decisions, both recorded rather than quietly taken:

1. The index schema is NOT changed while the campaign runs. A mid-flight schema change
   would leave the first half of the record shaped differently from the second, for a
   field that is already preserved per run.
2. The adjudicator now reads the per-run record. Its verdicts carry both counters, so a
   reader sees the ratio: in the instance inspected, one evidence-backed replication event
   against twenty-six resemblance events in the same run. That ratio is the thing to
   judge, and it belongs in front of the reader rather than inside a threshold.

## What is NOT affected

- Matched-pair effects in the packet: each pair differs in one declared factor and compares
  final-state outcomes on both sides.
- The replication detector: it was corrected BEFORE launch to require evidence that the
  organism placed the child's bytes, and it is holding. At 11.9 hours: zero voided runs,
  zero runner births, 914 runs with evidence-backed replication.
- The calibration gate, which passed 10 of 10 on the frozen grammar.
