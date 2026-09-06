# Archaeon roadmap

Working document, 2026-09-06. Organised around the three challenges the
operator placed on this seat. Each has: what exists now, what Archaeon will
build, what is delegated to another lane, and what "working" looks like.
Nothing here is scope for today; today is the plumbing milestone.

The one design idea that runs through all three: **LLMs and humans shape the
menu offline; the tick draws from the menu deterministically.** That line is
what keeps the selection policy falsifiable while letting the menu grow from
every source we have.

---

## Where the loop stands (measured)

    Archaeon tick -> viv.research_experiment_queue -> Vivarium -> SFE -> PEW
    E2E closed 2026-09-06 07:40Z with nobody driving it.

    kinds Archaeon can emit today          1   (evaluate_bitstring)
    parameter axes                         3   (length in {16,24,32}, seed_root, bits)
    detectors eligible on live corpus      3/6 (D3, D5, D6; D1/D2/D4 need players)
    S17 fragility units eligible           0   (Stage 0 KILL: no two-arm claims)
    weak-signal path changes the spec?     NO  (signal is recorded as reason only)

That last line is the honest starting point. The loop is real plumbing and a
random generator with a provenance label. Everything below is about changing
those numbers.

---

## Challenge 1 — the signal campaign

*Little data for a long time; the target mostly undefined; we don't know what
we don't know.*

**Reframe.** The first deliverable is not signal. It is an **instrument that
would notice signal if it were there, running continuously, with a written
account of what enrichment would let it see more.** Signal arrives, if it
arrives, as a change in that instrument's readings over months.

**Archaeon builds:**

- **Substrate census as a time series.** The eligibility census already runs
  every tick. Persist it (`archaeon.substrate_census`, one row per tick: rows,
  regions, players, per-detector eligible/total, S17 eligible units). This is
  the campaign's primary chart — "is the substrate becoming interrogable?" —
  and it needs no signal to be useful.
- **Substrate wishlist ledger.** Per detector, the *specific* structure that
  would flip it eligible, with the measured shortfall. Already known for S17
  (≥4 obs/world, two arms of ≥2 worlds, ≥2 groups) and for D1/D2/D4 (player
  identity in the observation). Keep it current, cite it in every delegation.
- **Chart growth.** New `CoordinateChart`s as the substrate adds fields —
  charts are data. The Vivarium `content.result.score` path was the first;
  `resources_used`, `ecology`, player identity are next when they exist.
- **Detector re-calibration on each corpus regime change**, with the null rate
  published. Never a threshold change without `CALIBRATION.md` moving.

**Delegated:**

- **Proteus (PEW):** decide what an encounter fossilizes. `players`, `ecology`,
  `resources_used` are 0/5452 in `prod`. Whichever of these PEW carries decides
  which detectors can ever be eligible. Archaeon supplies the wishlist; Proteus
  chooses.
- **Vivarium:** `repeat` — N observations in one world from one request — is
  the single change that flips S17 eligibility from impossible to reachable.
- **Daedalus (SFE):** family/arm identity reaching the fossil
  (`topology_group` + `lineage_edge IN_ARM`), so grouping is a declared fact
  rather than a name to parse.
- **Harmonia:** which weak-signal definitions are worth detecting *at all*.
  D1–D6 are my first guesses. Harmonia's S17 rules are frozen and better
  qualified; the discrepancy notice is filed. I would rather adopt Harmonia's
  definitions than defend mine.
- **Players:** players crossing into SFE at scale. 2 of 64 Proteus specimens
  have; all 64 lineages are size 1. No player-dependent detector runs until
  that changes.

**Working looks like:** the census chart has a slope; at least one detector
that was NOT ELIGIBLE at the start is eligible; the wishlist has entries marked
DONE with the commit that did it.

---

## Challenge 2 — random science

*RNG, a sprinkle of chaos, operator input, LLM input, prior research. Get very
good at detecting signal; when there is none, expand the template of
experiment types.*

**Reframe.** "Random" is not one generator; it is a **menu** plus a **draw**.
The draw stays deterministic and model-free. The menu is where every other
source enters.

**Archaeon builds: the experiment template registry.** Templates are data:

    archaeon/templates/<template_id>.json
    {
      "template_id":   "bitstring.uniform.v0",
      "kind":          "evaluate_bitstring",        # must be Vivarium-implemented to be ADMITTED
      "param_space":   {"length": {"choices": [16,24,32]},
                        "seed_root": {"int_range": [100000, 999999]},
                        "bits": {"uniform_bits": "length"}},
      "origin":        {"source": "RNG|HUMAN|LLM|LITERATURE|CHAOS",
                        "field": "<discipline>", "reference": "<citation or prompt hash>",
                        "proposed_by": "<seat or person>"},
      "status":        "PROPOSED | ADMITTED | RETIRED",
      "admitted_by":   "<operator>", "admitted_at": "<utc>",
      "rationale":     "<one paragraph, human-readable, non-binding>"
    }

- **Draw = (template, params).** The tick selects a template (uniform at first;
  coverage-weighted once the census can measure template coverage), then draws
  params from its declared space, all seeded and recorded.
- **Admission is a human act.** A template goes PROPOSED → ADMITTED only by the
  operator. LLMs, literature miners, and other seats write PROPOSED templates
  into `archaeon/templates/inbox/`. Nothing in the inbox is drawn from.
- **A PROPOSED template whose `kind` Vivarium does not implement is an
  expansion request**, automatically: it is exactly the "bench isn't capable"
  case, and it becomes an item for Challenge 3.
- **Chaos, explicitly.** A `mutate_template` operator that perturbs a declared
  space (widen a range, swap a choice list, cross two templates) into a new
  PROPOSED template with `origin.source = CHAOS` and the parent ids. Mutation
  proposes; it never admits.
- **Menu-growth metric.** Templates ADMITTED per month, and the fraction of
  tick draws coming from templates admitted in the last 90 days. A flat line is
  the failure mode this challenge exists to prevent (`feedback_gen_30_wall`:
  design menu growth, not deeper menus).

**Delegated:**

- **Literature mining → PROPOSED templates.** The discipline list (below) is
  the raw material. Each field yields "what is the smallest experiment this
  field would run on our bench, and what would it need the bench to have?" A
  seat with Deep Research capability (Herakles has it, per its BOOTSTRAP) can
  mine it; the output is inbox templates, not prose.
- **Harmonia:** for each admitted template, the null and the control that make
  its outcome interpretable — otherwise a template produces fossils nobody can
  read.
- **Vivarium:** new executor kinds as admitted templates require them. Archaeon
  never writes executors.
- **Daedalus (SFE):** when a template needs substrate the SFE lacks (multi-
  observation worlds, richer world parameters, new artifact kinds), that is an
  SFE growth request with the template as its spec.

**Working looks like:** ≥5 admitted templates from ≥3 origins; the tick's
template draw is visibly non-uniform over time (coverage-weighted); at least
one template originated from a discipline miner and one from CHAOS.

---

## Challenge 3 — program expansion

*Archaeon is on point for recommending where the program grows.*

**Reframe.** Expansion recommendations must come from **measurement, not
taste**. Two instruments produce them: the substrate wishlist (Challenge 1)
and the template registry's PROPOSED-but-unrunnable set (Challenge 2). A third
watches for collapse.

**Archaeon builds: the program-health / monoculture report.** Weekly, from the
queue and PEW, no interpretation:

- **What crossed the queue:** distinct kinds, distinct templates, parameter
  entropy per axis, outcome distribution (SURVIVED/FALSIFIED/INCONCLUSIVE),
  fraction failed at execution.
- **Monoculture flags.** A kind or template above 80% share; a parameter axis
  with entropy below a stated floor; an outcome distribution stuck at one
  value. Each flag is a *measurement*, stated with its threshold, never a
  verdict.
- **Expansion register.** Every recommendation, addressed to a lane, with the
  measurement that motivated it, the template or detector it would unblock,
  and its status. `roles/Archaeon/EXPANSIONS.md`. Delivered to the owning seat
  as `roles/<Seat>/INBOX_ARCHAEON_*.md`.

**The standing expansion targets, by lane** (first entries, all measured):

- **Vivarium:** `repeat`; retire `archaeon.probe.v0`; executor kinds per
  admitted templates.
- **SFE / Daedalus:** multi-observation worlds; declared family/arm in the
  fossil; standardised observation metric path; richer `spec` parameter
  surfaces as templates demand.
- **PEW / Proteus:** fossilize `players`, `ecology`, `resources_used`;
  populate `phenotype.score` (2 of 6006 today).
- **Players:** more than 2 of 64 specimens crossing into SFE; lineages of size
  > 1.
- **Harmonia:** adopt-or-replace D1–D6 with qualified definitions; nulls per
  template.
- **Archaeon (self):** everything in Challenges 1–2; the census, registry,
  and report are all Archaeon's to build.

**Working looks like:** an expansion register where entries move
PROPOSED → ACCEPTED/DECLINED with an owner and a commit; and a monoculture
report whose flags have gone up *and then down*.

---

## Sequence (what Archaeon does, in order)

    NOW    plumbing milestone stable: scheduled tick, docs, boundary held
    1      substrate census persisted per tick + wishlist ledger  (Ch.1)
    2      template registry + inbox + admission; port the current random
           generator into it as bitstring.uniform.v0             (Ch.2)
    3      program-health report v0 + expansion register           (Ch.3)
    4      first discipline-mined templates land in the inbox
           (delegated; Archaeon admits nothing itself)            (Ch.2)
    5      CHAOS mutation operator                                 (Ch.2)
    6      coverage-weighted template draw                         (Ch.2)
    later  detectors re-qualified against Harmonia's definitions; S17
           unparked when Vivarium `repeat` + SFE arm fossils exist

Each step is a commit with tests and, where it changes the menu or a
threshold, a calibration entry.

---

## Related disciplines (raw material for templates)

Artificial Life · Open-Ended Evolution · Evolutionary Computation ·
Quality-Diversity / MAP-Elites · Genetic Programming · Artificial Chemistry ·
Autocatalytic Sets · Artificial Gene Regulatory Networks · Digital Evolution ·
Evo-Devo · Computational Creativity · Automated Scientific Discovery · Machine
Discovery · AI Scientist systems · Automated Theorem Proving · Inductive Logic
Programming · Program Synthesis · CEGIS · Falsification-Based Search · Active
Learning · Optimal / Bayesian Experimental Design · Automated Experimentation
· Robot Scientists · Meta-Learning · Learning-to-Search / -Optimize ·
Algorithm Discovery · NAS · Population-Based Training · Novelty Search ·
Intrinsic Motivation · Curiosity · Empowerment · POET / Open-Ended Learning ·
Autocurricula · Coevolution · Minimal-Criterion Coevolution · Illumination
Algorithms · Search-Based Software Engineering · Property-Based Testing ·
Metamorphic Testing · Counterexample-Guided Verification · Formal Methods ·
Proof Search · Automated Conjecture Generation · Computational Mathematics ·
Scientific ML · Causal Discovery · Symbolic Regression · Equation Discovery ·
Abductive / Inductive / Analogical / Case-Based Reasoning · Knowledge
Discovery · Discovery Informatics · Computational Serendipity · AGI ·
ALife-Inspired AI · Machine Evolution · Darwinian Neurodynamics · Universal
Darwinism · Evolutionary Epistemology · Computational Philosophy of Science ·
Computational Models of Scientific Discovery · Meta-Science · Science of
Science.

The question to ask each one is the same and is deliberately small: *what is
the smallest experiment this field would run on our bench today, and what is
the smallest thing the bench lacks?* The first answer is a template; the
second is an expansion.
