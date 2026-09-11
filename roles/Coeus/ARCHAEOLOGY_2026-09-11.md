# Coeus archaeology, 2026-09-11

> Booting an old seat is an archaeological event, not an instruction to
> resume its last queue (roles/base-role/RESPONSIBILITIES.md).

Currency: 2026-09-11. Read from origin/main 8714b2709 in the worktree
D:\Prometheus-worktrees\coeus-base-role (linked; git-dir differs from
git-common-dir), and from origin/necropolis/coeus (unmerged branch).
Every number below has its source beside it. Numbers marked VERIFIED
TODAY were read by this seat from the shipped artifacts at 8714b2709;
numbers marked DOSSIER are cited from the Necromancer pass and were not
re-derived here (see section 5 on why this seat cannot discharge them).

## 0. What the seat was

Coeus, "the causal intelligence layer": a pipeline stage between Nous
(concept-triple generation and scoring) and Hephaestus (code forge).
It encoded each Nous triple as 122 concept indicators + 20 field
indicators + 4 Nous sub-scores, joined that to the Hephaestus forge
ledger (forged / scrapped), fit a per-concept `forge_effect` and pair
`synergy`, and published `graphs/concept_scores.json`. Hephaestus added
those numbers to the Nous composite when sorting its forge queue.

Commits, all authored 2026-03-25 to 2026-03-27 (`git log -- agents/coeus`):

    da42cc7e0  2026-03-25  Forge pipeline v2: Coeus causal intelligence, NCD baseline, ...
    fbb92a11a  2026-03-25  Phase 2b: Coeus dual graph, Gate 6, lineage tracking, ...
    2a186ba24  2026-03-25  Phase 3-4: RLVF fitness function, provenance gate, ...
    7b4903a00  2026-03-25  Update all docs: build plan, 4 agent READMEs ...
    923d11c66  2026-03-25  Harden error handling across all 21 pipeline modules
    45f225f51  2026-03-25  Batch 4 pipeline results: 140 forge tools, 63/100 Nemesis grid
    5573808c7  2026-03-27  CAITL v3/v4, 58-category trap battery, novelty scoring, ...
    8af6ba9e5  2026-03-27  Complete pending tasks: 89-cat eval, fingerprints, quartets, ...

Three days of authorship. Nothing has been committed under agents/coeus/
since 2026-03-27. The operator's recollection of "back in May" is off by
about two months: May is when the FORGE that consumed Coeus's output
finally stopped (last forge-ledger activity 2026-05-28, DOSSIER), not
when Coeus was written.

## 1. What it shipped, and what still reads it

VERIFIED TODAY, by reading the artifacts:

    agents/coeus/graphs/causal_graph.json
      concept_influence     95 entries
      pair_synergy          50 entries
      score_dag              5 entries
      field_effects          3 entries
      forge_rate_by_concept 95 entries
      confounders            0 entries        (the confounder search found none)
      interventional        85 entries
      dagma_divergences      0 entries        (DAGMA never ran)
      n_observations      4031
      n_forged             352
      method              'lasso_regression'

    agents/coeus/graphs/concept_scores.json
      concept_influence     95    pair_synergy        1009
      forge_rate_by_concept 95    adversarial_survival  97
      field_effects          3    goodhart_indicators   30
      updated_at  2026-03-27T06:37:20

    agents/coeus/graphs/adversarial_graph.json
      adversarial_survival  97    n_adversarial_tasks  92

    agents/coeus/enrichments/*.json   4031 files, 28 MB

Consumers still wired in the tree at 8714b2709 (VERIFIED TODAY by grep):

    agents/hephaestus/src/hephaestus.py
      L51-52    COEUS_ENRICHMENTS_DIR, COEUS_SRC
      L1053     _load_coeus_scores()
      L1065     _forge_priority(entry, coeus_scores)
      L1122-24  filtered.sort(key=_forge_priority, reverse=True)
      L1530     _trigger_coeus()  -- imports and runs coeus.main()
      L1699     fires every --coeus-interval forges (default 50, L2351)

    agents/hephaestus/src/rlvf_fitness.py
      L32, L75  reads graphs/concept_scores.json
      L82-96    uses adversarial_survival[concept]['survival_rate'] as a
                per-tool weight in F(T) = sum(w_i * S_i) - lambda * sigma(S)

    forge/v2/coeus_t2/  -- a separate coverage-tracking artifact
                           (README.md + coverage_snapshot.json only).
                           forge/v3/coeus_t3/ does not exist.

All of it is inert today because the forge is dead. Nothing has run.

## 2. The Necropolis dossier: this seat has already been autopsied

On 2026-09-10, one day before this boot, Mnemosyne M2 (Keeper of the
Necropolis) ran Necromancer pass #1 against Coeus. The dossier is
`engine/necropolis/dossiers/coeus.dossier.json` on the unmerged branch
`origin/necropolis/coeus` (baseline efd26dbb8), with three reproducible
attack scripts and their outputs under `dossiers/coeus_evidence/`.

Disposition: **MEASUREMENT_FAILURE**. It overturns both earlier verdicts
(the 2026-08-20 Aporia/Elenchus autopsy null, and the 2026-06-24
"decorative-causal, RETIRE" line).

The kill boundary, in the dossier's terms (DOSSIER, not re-derived here):

- KILLED: "Coeus's shipped concept scores carry forge-outcome signal
  that transfers across forge configurations." Leave-one-forge-day-out,
  API failures excluded, gives AUC 0.461 on 2026-03-26 and 0.338 on
  03-27, at or below the label-permutation null.
- KILLED: "Concept identity predicts forge outcome even under a fixed
  judge." Within-single-forge-day 5-fold CV on the largest day gives
  AUC 0.501 against a null mean of 0.493.
- KILLED as vacuous: the 2026-08-20 autopsy's observable. 1e-3 Gaussian
  noise on the composite changes 99.7% of queue positions; Coeus changes
  99.9%. "Consumption reorders the queue" measures nothing.
- WHAT THE POOLED SIGNAL WAS: the forge CALENDAR. Day base rates run
  58% (03-25), 23% (03-26), 10.5% (03-27), 2-3% (May), driven by the
  trap-battery version change on 03-27 and by API health. The pooled
  AUC 0.707-0.723 was that calendar fingerprinted through which concept
  batches happened to be forged when.
- NOT KILLED: the apparatus runs; the consumer seam is real; and the
  weaker premise, "under a frozen judge with a healthy API, concept-level
  structure in forge outcome may exist", is UNTESTED AT POWER. No window
  in the historical data is clean enough to decide it.

The descendant candidate `coeus-d1-frozen-judge-structure-test` is a
falsification experiment, explicitly NOT a scorer revival. It is
RESOURCE-gated: it needs roughly 1000 live Hephaestus attempts under one
frozen battery with a working LLM API, and the dossier forbids dispatch
until a Cleric confirms a working forge and the operator signs off.

This seat accepts the disposition. It does not contest it.

## 3. Three defects this seat found today that the dossier did not name

These are reads of Coeus's own shipped artifacts, in Coeus's own lane,
at 8714b2709. They are recorded here because rule 5 (currency is
correctness) makes a seat's own stale documentation a defect.

**D1. The README contradicts the artifact it documents, including a sign
flip.** `agents/coeus/README.md` states "Implementability is the only
Nous score dimension predicting forge success (+0.221)". The shipped
`causal_graph.json` score_dag reads:

    reasoning              -0.2042
    metacognition          +0.4819
    hypothesis_generation  +0.5708
    implementability       -0.4670
    composite_score         0.0000

Implementability is the most NEGATIVE coefficient in the block the
README says it leads. The README's headline concept table is stale on
every row (README / shipped):

    Criticality           +1.155 / +0.3514
    Sparse Autoencoders   +0.919 / +0.2753
    Active Inference      +0.789 / +0.2007
    Falsificationism      +0.655 / +0.3222
    Topology              -0.462 / -0.0563
    Epigenetics           -0.299 /  0.0000

and "Compressed Sensing (0% forge, 70% adversarial)" is 53.27% in
`adversarial_graph.json`. The README also points at
`hephaestus/src/rlvf_fitness.py`; the file is at
`agents/hephaestus/src/rlvf_fitness.py`. Not established: which run the
README's numbers came from, or whether any artifact matching them was
ever committed. The honest statement is that Coeus published a
description of results that does not match the results it shipped, and
left it standing for six months.

**D2. The goodhart_indicators block drops its denominators.**
`concept_scores.json.adversarial_survival` correctly carries
`n_tasks` and `n_survived` per concept. The `goodhart_indicators` block
derived from it (30 rows) carries only a bare `adversarial_survival`
float and a verdict string. Seven of those 30 rows are built on
denominators of 1 to 4:

    Abstract Interpretation   1/1 -> 1.0  "undervalued"
    Dual Process Theory       1/1 -> 1.0  "undervalued"
    Epigenetics               1/1 -> 1.0  "undervalued"
    Hoare Logic               1/1 -> 1.0  "undervalued"
    Adaptive Control          2/2 -> 1.0  "undervalued"
    Counterfactual Reasoning  2/2 -> 1.0  "undervalued"
    Gauge Theory              4/4 -> 1.0  "undervalued"

A one-of-one survival is published as a maximal robustness score with a
BOOST recommendation attached and no eligible count beside it.

**D3. A rate with no minimum-n filter is consumed as a live weight.**
`agents/hephaestus/src/rlvf_fitness.py` L82-96 reads
`adversarial_survival[concept]['survival_rate']`, averages it over a
tool's concepts, and uses it as w_i in the RLVF fitness function. It
applies a floor (max(0.1, mean)) but NO minimum denominator. Fifteen of
the 97 concepts have n_tasks < 10. A concept measured once, and
surviving, therefore contributes the maximum possible weight. The
consumer is currently inert (no forge), so this is a latent defect, not
an active one.

**D3b, a units problem beneath D2 and D3.** The per-concept `n_tasks`
values sum to 37,035 while `adversarial_graph.json.n_adversarial_tasks`
is 92. So `n_tasks` counts tool-by-task pairings, not tasks; the
effective independent sample behind every survival rate in the file is
92 adversarial tasks, and a concept showing "n_tasks=2285" (Criticality)
is not 2,285 independent observations. Neither the field name nor the
consumer records this. Not established: how many DISTINCT tools back
each concept's count; that read was not done today.

## 4. The old queue, classified against the north star

Classes: STILL_LIVE, NEEDS_REPREMISE, PARKED, SUPERSEDED, TRANSFERRED,
RETIRED. Only STILL_LIVE is executable. Nothing below is marked dead;
residue, weak signals and gradients stay navigable.

  item                                        class           note
  ------------------------------------------  --------------  --------------------------------------------------------
  Learn concept-level causes of forge success  NEEDS_REPREMISE The shipped claim is killed (calendar fingerprint).
  and feed them back as forge-queue priority                   The weak premise survives untested at power and is
                                                               RESOURCE-gated on a live forge. Owned by the Necropolis
                                                               descendant coeus-d1, not by this seat (LAW N3: a seat
                                                               does not resurrect itself).
  4031 prescriptive enrichment blocks          SUPERSEDED      They encode the killed scores as instructions ("make this
  injected into the Hephaestus prompt                          concept the core architectural pattern"). Retained as
                                                               residue; never to be re-injected as written.
  Sampling weights fed back to Nous            PARKED          Nous has not run since 2026-03-27.
  Dual graph and Goodhart divergence           NEEDS_REPREMISE The divergence IDEA (forge-success vs adversarial-
  (30 indicator rows)                                          survival disagreement as a Goodhart detector) is not
                                                               falsified. The 30 published rows are unusable as they
                                                               stand: see D2 and D3b.
  RLVF weights into hephaestus rlvf_fitness    NEEDS_REPREMISE Wired and inert. Needs a minimum-n filter and a units
                                                               fix before it may run again: see D3.
  NOTEARS / GES / FCI / LiNGAM / DAGMA         RETIRED         Advertised in README and configs/manifest.yaml; never
  as actual methods                                            executed. method='lasso_regression', confounders 0,
                                                               dagma_divergences []. The word "causal" on a Lasso is
                                                               the claim/method mismatch the 2026-06-24 review named.
  "Interventional" counterfactuals             RETIRED         85 entries of P(forge | with) minus P(forge | without),
  P(forge | do(remove X))                                      a raw rate difference labelled do-calculus. No
                                                               adjustment set, no identification argument.
  forge/v2/coeus_t2 coverage tracking          PARKED          A separate artifact (README + one snapshot). Untouched.
  forge/v3/coeus_t3                            RETIRED         Never existed on disk. T3 never launched.
  dowhy / tigramite "future integration"       RETIRED         Listed in configs/manifest.yaml; never started.

Executable items after classification: ZERO that need a decision from
nobody, except documentation repair inside Coeus's own directory (see
the backlog, COEUS-01 through COEUS-03).

## 5. Why this seat is the wrong second lens on its own dossier

The dossier's own unresolved question list carries LAW N13: "the kill was
produced and attacked only by this investigator; an independent re-run of
coeus_evidence/coeus_attacks.py by another lens is owed before this
dossier is cited as settled."

Coeus is the SUBJECT of that dossier. A re-run by this seat would be a
subject auditing its own autopsy, and the base role is explicit that a
same-model, same-interest audit is worth nothing and that conflicts of
interest are declared. **This seat declares the conflict and will not
discharge LAW N13 on coeus.dossier.json.** The independent lens must be
a seat with no stake in the verdict; the Keeper (Mnemosyne) routes it.

What this seat CAN offer without the conflict biting is the three
defects in section 3, which are adverse to Coeus, not favourable to it:
each one makes the shipped artifacts look worse, not better. Findings
that cut against the finder's interest are the ones a conflicted party
may report (base role: positive results favouring your own lane need
independent attack; this seat has produced no positive result).

## 6. What was NOT examined today

- The three `coeus_evidence/*.py` attack scripts were NOT re-run. Their
  numbers are cited as DOSSIER, unverified by this seat, deliberately
  (section 5).
- `agents/coeus/src/causal_graph.py` and `coeus.py` were not read line
  by line; only their outputs were read.
- The 4031 enrichment files were counted, not sampled. No claim is made
  here about their text beyond the two examples quoted in the README.
- `forge/v2/coeus_t2/coverage_snapshot.json` was not opened.
- Whether any Nous run or forge-ledger row postdates 2026-05-28 was
  taken from the dossier, not measured here.
- No process, scheduled task or service was inspected: Coeus never had
  one. It ran only as an in-process call from Hephaestus every 50
  forges.
