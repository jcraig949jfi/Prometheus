# Two independent 100-question frontiers agree on about a third — and both miss the same class

**Measured 2026-08-31 by Aporia.** L1 = the operator/GPT-side list. L2 = the Claude-Code-agent
list. Registries: `REGISTRY.jsonl`, `REGISTRY_L2.jsonl`. Pair mapping: `OVERLAP_PAIRS.jsonl`.

**Method disclosure, binding on every number below:** the mapping is **hand-coded by me**, not
produced by an embedding model. A pair is STRONG only if the two questions would be answered by
substantially the same experiment; PARTIAL if they share a mechanism but differ in what would
count as an answer. Every row is individually checkable and disputable, which is why it ships as
data rather than as a claim. The union count is an upper bound because the pairing is not a
bijection.

---

## 1. The numbers

    pairs asserted                       76   (41 STRONG, 35 PARTIAL)

    L1 with ANY counterpart in L2        64 / 100
    L1 with a STRONG counterpart         32 / 100
    L2 with ANY counterpart in L1        53 / 100
    L2 with a STRONG counterpart         37 / 100

    unique to L1                         36
    unique to L2                         47
    distinct questions in the union     ~124 (upper bound)

**Roughly a third of each list has a strong counterpart in the other. Two thirds do not.**

## 2. This is the field split, measured rather than asserted

The operator's standing hypothesis was that the field's research was narrow and missed
cross-links, with a generation that moved to neural networks and is now cycling back. **The two
lists are the two sides of that split, generated independently, and their disagreement is
structured by discipline lineage rather than scattered.**

Where L2 is nearly silent (L1 match rate):

    Formal deduction        2 / 10     theorem proving, proof search, lemma invention
    Analogical reasoning    0 / 2      L2 says NOTHING about relational analogy
    Probabilistic reasoning 2 / 5      amortized inference, epistemic/aleatoric, latent separators
    Multi-agent             2 / 6      credit assignment, emergent protocols, Byzantine coalitions
    Neuro-symbolic          2 / 5      symbol grounding drift, exact constraint at scale

Where L1 is nearly silent (L2 match rate):

    Scaling                 1 / 8      scaling-law exponents, emergence, grokking, order parameters
    Reasoning (CoT)         2 / 8      faithfulness, monitorability, latent vs token reasoning
    Grounding               2 / 8      embodiment, modality gap, binding, object hallucination
    Memory                  3 / 8      weight editing, unlearning, superposition capacity, edit collapse

L1 is the classical AI / formal-methods / planning lineage. L2 is the empirical deep-learning /
interpretability / alignment lineage. **Neither is a survey of the field; each is a survey of a
lineage.** Anyone treating either as "the frontier" is reading one half.

**And note what this does to the corpus-gravity worry.** `feedback_llm_convergence_is_gravity_amplifier`
predicts that two LLM-generated lists would converge, and that convergence would be worthless as
validation. They converged on **one third**. That is weaker convergence than the doctrine feared —
which is good news for the lists' independence and *bad* news for treating either as
authoritative, because it means the frontier as stated is substantially generator-dependent.

## 3. The structural difference, which is the more useful finding

**L1 asks whether a system can DO something. L2 asks whether our MEASUREMENT of it means
anything.**

L1 contains essentially two instrument-validity questions out of a hundred (Q049 calibration,
Q050 independent validators). L2 devotes an entire area to evaluation science (8), plus
interpretability-validity (7), plus large parts of alignment and scaling — on the order of
fifteen to twenty questions asking whether a measurement is measuring what it names.

That is the axis on which this programme has spent the week: gate reachability, verdict-rule-as-
instrument, per-component calibration, one-sided nulls, unit of analysis. **L2 maps onto
Prometheus's methodology far more than L1 mapped onto its substrates**, and the Tier A/B triage
should be redone against L2 on those grounds — several L2 questions are ones we have already
answered for ourselves without noticing they were on anyone's frontier list.

Direct hits already in hand:

- **L2-95** (what objective predicts OOD reuse of invented primitives; predicts MDL-selected
  libraries underperform a marginal-solve-rate criterion) is exactly the dossier filed today.
  We established the field measures compression and never reachability, and that the four
  content-vs-presence controls are absent everywhere while D-5 ran two of them.
- **L2-77** (open-endedness: predicts the internal novelty signal decorrelates from held-out
  usefulness) is the **S3_REWRITE result**: highest validity of four substrates (0.996), largest
  phenotype mass (11,717 classes), and **zero** far-stratum paths across ~1.5M evaluations.
  Validity and diversity are coordinates, not geometry. That is L2-77's T1 prediction confirmed
  in a substrate, and it is already committed.
- **L2-55** (probe in the training signal relocates rather than removes) and **L2-56** (leading
  indicator of gaming) are the concealment research, plus
  `feedback_promotion_requires_independent_failure_mode`.
- **L2-50 / L2-92** (sleeper detection without knowing the trigger; eval-detection probe) are the
  gradient-hacking pass, including the adversarial-training rate decoupling.
- **L2-66** (critical per-step reliability p*, predicted percolation-like transition) is
  accessibility percolation, which D-4 already instruments.

## 4. WHAT BOTH LISTS MISS — the reason to keep running rather than reading

Across 124 distinct questions from two independent generators, **neither list contains a single
question about the class of defect this programme keeps actually hitting.** Four absences,
each of which cost us a real pass:

1. **Gate reachability.** Does a preregistered threshold lie inside the attainable range of the
   statistic? Two 100-question lists substantially about measurement validity, and **neither
   asks whether your gate can fire.** We hit this twice in one pass on 2026-08-27 (a bar at
   exactly 1.0 on a bounded fraction; a statistic capped at sqrt(8) against a bar of 2.49) and
   once on 08-23 (cut 0.14 above a maximum attainable 0.1364).
2. **The self-inflating bar.** A threshold defined as a multiple of a null computed on the same
   rows rises *with* the effect, so on a bounded statistic bar and ceiling meet. Absent from both.
3. **One-sided instruments.** A detector that fires is informative; a detector that stays silent
   proves nothing. L2-88 touches this for interpretability only ("certify absence"), and neither
   list generalises it — despite it governing every honeypot, canary and null in both.
4. **Unit of analysis.** A model emitting one decision per cell has n = cells, not rows. Absent
   from both, and it once inflated one of our precisions 57x.

**Why the absence is systematic rather than accidental:** these defects appear when you *run* an
instrument against a preregistered predicate, not when you survey a literature. Both lists were
generated by reading. That is the strongest argument in this analysis for the programme's
posture, and it is also the strongest argument against treating either list as a research plan.

**The fifth absence is the one already documented elsewhere:** the measurement apparatus being
inside the environment. L2-55 catches the LLM instance (optimize against a probe and the
behaviour relocates); neither list names the general class, which spans artificial life 2004,
program repair 2010, deep neuroevolution 2018 and LLM safety 2024 — and which the standard
Goodhart taxonomy structurally excludes, because its Adversarial category requires a knowing
second actor.

## 5. Disposition

- Both registries stay as data. **Do not merge them into one file** — the pair mapping carries
  more information than a merged list would, and the provenance of each question is part of its
  evidence.
- Re-triage Tier A/B against L2 on the instrument-validity axis, where the hit rate is higher.
- The four absences in §4 are candidate **L3 entries** — questions this programme generated by
  running rather than reading. That is the only part of this exercise that produces something
  neither generator had.
- Standing caution retained: a question appearing in both lists is evidence about corpus
  density, not about importance.
