# ASTRA-6.0 / Enceladus: external prior art and historical catalogues

## 1. Which external precedents most constrain the initial architecture?

### Takeaway
The strongest precedents already learn reusable program libraries, tune plastic learning,
or modify their own weights. Enceladus must distinguish its proposed causal evidence from
these mechanisms rather than claim novelty from self-modification or learning-to-learn alone.
This is a bounded literature and catalogue review, not a reproduction or a novelty clearance.

### Cited Findings

#### P1. DreamCoder: learned libraries and learned search are a serious competitor
- Kevin Ellis et al., *DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep
  Library Learning*, PLDI 2021; DOI `10.1145/3453483.3454080`.
  Primary locator: [conference abstract and DOI](https://pldi21.sigplan.org/details/pldi-2021-papers/55/DreamCoder-Bootstrapping-Inductive-Program-Synthesis-with-Wake-Sleep-Library-Learnin).
- The system derives a library of program components and a neural search policy from
  example-specified synthesis problems; these bootstrap one another through wake-sleep learning.
  Its refactoring uses E-graph matching to identify common program subcomponents. [P1](https://doi.org/10.1145/3453483.3454080)
- The authors report evaluation in eight domains and solving more problems, more quickly,
  when the library and search policy are learned jointly. This is their reported result,
  not a benchmark rerun here. [P1](https://pldi21.sigplan.org/details/pldi-2021-papers/55/DreamCoder-Bootstrapping-Inductive-Program-Synthesis-with-Wake-Sleep-Library-Learnin)
- Relevance: Q2/Q3 reusable operations and acquisition cost, and track A's symbolic-like
  prior; the abstract does not establish Enceladus's nested V/U/S intervention criterion.
  [Architecture sections 3 and 5](../RSE_ARCHITECTURE.md)

#### P2. Enhanced POET: reachability can depend on the challenge population
- Rui Wang et al., *Enhanced POET: Open-ended Reinforcement Learning through Unbounded
  Invention of Learning Challenges and their Solutions*, ICML 2020, PMLR 119:9940-9951.
  Primary locator: [proceedings abstract and bibliography](https://proceedings.mlr.press/v119/wang20l.html).
- POET generates and solves challenges and transfers solutions between challenges.
  Enhanced POET adds a meaningful-novelty measure, a goal-switching heuristic, more flexible
  challenge encoding, and a measure of continuing innovation. [P2](https://proceedings.mlr.press/v119/wang20l.html)
- The authors identify limited problem space and progress measurement as obstacles to
  demonstrating open-endedness; their report is a finite empirical demonstration, not an
  observed infinite process. [P2](https://proceedings.mlr.press/v119/wang20l.html)
- Relevance: keeping adaptive worlds outside confirmation is compatible with testing them
  later as a discovery treatment, rather than treating static curricula as exhaustive.
  [R-SRH-03](../REQUIREMENTS.md); [architecture section 4](../RSE_ARCHITECTURE.md)

#### P3. Avida: historical stepping-stones matter, but evolution is not lifetime learning
- Richard E. Lenski, Charles Ofria, Robert T. Pennock, and Christoph Adami,
  *The evolutionary origin of complex features*, Nature 423:139-144 (2003).
  Primary locator: [publisher abstract](https://www.nature.com/articles/nature01568);
  DOI [10.1038/nature01568](https://doi.org/10.1038/nature01568).
- Digital organisms evolved complex logic functions by building on simpler functions when
  those were selectively favored; no particular intermediate stage was essential in the
  reported experiments. Some initially deleterious mutations became stepping-stones. [P3](https://www.nature.com/articles/nature01568)
- This concerns evolving self-replicating programs and genomic changes. It must not be
  silently recast as evidence that a single organism develops transferable reasoning within
  a lifetime. [P3](https://www.nature.com/articles/nature01568)
- Relevance: the architecture separates inherited material, lifetime construction, and
  search; those boundaries are crucial to interpreting a stepping-stone result.
  [R-DEV-01 and R-SRH-01](../REQUIREMENTS.md)

#### P4. Differentiable plasticity: fixed outer training can yield useful online learning
- Thomas Miconi, Kenneth Stanley, and Jeff Clune, *Differentiable plasticity: training
  plastic neural networks with backpropagation*, ICML 2018, PMLR 80:3559-3568.
  Primary locator: [proceedings abstract and bibliography](https://proceedings.mlr.press/v80/miconi18a.html).
- The authors optimize plasticity alongside connection weights with gradient descent in
  recurrent networks with Hebbian plastic connections. [P4](https://proceedings.mlr.press/v80/miconi18a.html)
- Reported tests include novel-image memorization/reconstruction, Omniglot meta-learning,
  and maze exploration; the maze comparison favors plastic over non-plastic equivalents.
  The image experiment includes networks above two million parameters. [P4](https://proceedings.mlr.press/v80/miconi18a.html)
- Relevance: track C already admits conventional optimization and plasticity; a small
  comparable baseline would test this mechanism, not reproduce the published scale.
  [Architecture sections 3 and 8](../RSE_ARCHITECTURE.md)

#### P5. SRWM: runtime self-modification is established prior art
- Kazuki Irie, Imanol Schlag, Robert Csordas, and Jurgen Schmidhuber, *A Modern
  Self-Referential Weight Matrix That Learns to Modify Itself*, ICML 2022,
  PMLR 162:9660-9677. [Primary proceedings record](https://proceedings.mlr.press/v162/irie22b.html)
- The proposed self-referential weight matrix learns to use outer products and the delta
  update rule to modify itself, building on fast-weight programmers and related linear
  Transformers. [P5](https://proceedings.mlr.press/v162/irie22b.html)
- The authors distinguish potential recursive meta-learning from empirical evaluation in
  supervised few-shot learning and multitask reinforcement learning with procedural games.
  The abstract reports practical applicability and competitive performance, not the
  specific Enceladus depth-two causal test. [P5](https://proceedings.mlr.press/v162/irie22b.html)
- Relevance: a change to writable update machinery is not sufficient evidence of a newly
  discovered category outside meta-learning; the initial design already makes this caveat.
  [Architecture section 5, nested causal criterion](../RSE_ARCHITECTURE.md)

#### P6. Causal representation learning: useful variables are themselves a problem
- Bernhard Scholkopf et al., *Towards Causal Representation Learning* (2021),
  arXiv `2102.11107`; the author record identifies the Proceedings of the IEEE special issue.
  Primary locator: [author abstract and version history](https://arxiv.org/abs/2102.11107).
- This review relates causal inference to transfer/generalization and emphasizes discovery
  of high-level causal variables from low-level observations, rather than assuming those
  variables are given. It is a conceptual review, not an Enceladus validation. [P6](https://arxiv.org/abs/2102.11107)
- Relevance: declaring a substrate ontology-free does not make its observation codec,
  intervention handles, or analyst-selected process boundaries prior-free.
  [R-APR-01 and R-CAU-01](../REQUIREMENTS.md); [P6](https://arxiv.org/abs/2102.11107)

#### P7. Minimum description length: description length is model-relative
- J. Rissanen, *Modeling by shortest data description*, Automatica 14(5):465-471 (1978).
  Primary locators: [IBM author publication record](https://research.ibm.com/publications/modeling-by-shortest-data-description)
  and [publisher bibliographic record](https://www.sciencedirect.com/science/article/abs/pii/0005109878900055);
  DOI [10.1016/0005-1098(78)90005-5](https://doi.org/10.1016/0005-1098(78)90005-5).
- The abstract states that describing an observed sequence depends on the assumed model
  and its parameters; minimizing description length estimates structure and parameters.
  It does not establish that shorter organism encodings imply reasoning. [P7](https://research.ibm.com/publications/modeling-by-shortest-data-description)
- Relevance: whole-code/decoder accounting and useful future reuse are stronger demands
  than comparing serialized checkpoint sizes. [R-MSR-03](../REQUIREMENTS.md)

### Inferences
- **Proposed baseline priority:** library learning (P1), learned plasticity (P4), and
  self-referential fast weights (P5) should anchor novelty comparisons before exotic claims.
  These are mechanism families to instantiate economically, not compulsory full reproductions.
- **Proposed reachability control:** P2/P3 motivate a bounded stepping-stone curriculum arm
  after instrument qualification; equalize total search and exposure, not only final episodes.
- **Proposed interpretation discipline:** P6/P7 motivate separate accounting for observation
  variables, learned representations, analyst-defined boundaries, and decoder information.

### Gaps
- Read depth is primary landing-page abstracts/bibliography, not a full methods or code audit.
  Publisher metadata was checked for Rissanen; no paywalled methods were inferred from snippets.
- No source was reproduced locally; published effect sizes, compute costs, variance, and
  failure cases were not extracted at sufficient depth to parameterize a power calculation.
- This seven-source sample cannot establish absence of closer prior art or conceptual priority.
  In particular, theoretical self-improvement and the wider learned-optimizer literature
  remain outside this bounded pass; no universal novelty conclusion is warranted.

## 2. What do the historical catalogues provide, and what do their grades mean?

### Takeaway
Use the catalogues as source locators, graded hypotheses, and potential control inventories,
not as a list of validated transferable organs. Their different counting units and evidence
levels must survive any later admission into the observatory.

### Cited Findings

#### C1. Atlas external ecosystem bibliography
- [ECOSYSTEMS.jsonl](../../../../../roles/Atlas/catalog/ECOSYSTEMS.jsonl) contains 365 rows
  and 365 unique ecosystem IDs in the inspected snapshot; this is an enumeration, not 365
  independent demonstrations. Selected external reference projections covered Avida, Tierra,
  Lenia, POET, and Enhanced POET; their narrative analogue fields were not used as evidence.
- [SCHEMA.md, lines 14-33](../../../../../roles/Atlas/catalog/SCHEMA.md) distinguishes
  world, organism, pressure, search, environment generation, claims, publications, code,
  runtime status, and relatives. Its `prometheus_analogue` field is an authored analogy,
  not an empirical equivalence certificate.
- `VERIFIED` means the URL was fetched and resolved to the intended object; `SEARCH_RESULT`
  and `UNVERIFIED` denote weaker URL checks. None is a result-replication grade.
  [Schema lines 36-37](../../../../../roles/Atlas/catalog/SCHEMA.md)
- The adapter explicitly retains the surveyor's URL status and does not upgrade it.
  Its related-ecosystem edges come from the catalogue relatives field, not causal tests.
  [atlas/harvest/catalog.py, lines 1-8 and 75-80](../../../../../atlas/harvest/catalog.py)
- Avida's selected bibliography lists 1994 and 2004 papers, whereas P3 was checked directly
  at the publisher; a catalogue entry and a particular experiment are different locators.
  [Catalogue](../../../../../roles/Atlas/catalog/ECOSYSTEMS.jsonl); [P3](https://www.nature.com/articles/nature01568)

#### C2. Techne preserved computational fossils
- [CATALOG.json](../../../../../techne/fossils/CATALOG.json) has 189 rows, reports 106
  runnable fossils, and is marked host-neutral. Projected metadata contains 84 `yes`
  oracle-backed entries and 66 `yes` intervention-ready entries; these are not necessarily
  the same subsets, and no bodies or receipts were executed in this review.
- The enumeration distinguishes preserved computational systems from experiment fossils;
  a tracked record can exist without its source body on the current host.
  [catalog.py, lines 1-16](../../../../../techne/fossils/catalog.py)
- Host-neutral enumeration does not check bodies; host-dependent fields are null rather
  than measured zero. The default body-checking mode can consult host-local mirror config,
  so this pass used the tracked snapshot, not that default runtime path.
  [catalog.py, lines 32-55 and 113-131](../../../../../techne/fossils/catalog.py)
- Source types distinguish authoritative releases, mirrors, later lineage releases, ports,
  pseudocode/reference implementations, symbol-bearing binaries, and recovered representations.
  [record.py, lines 62-71](../../../../../techne/fossils/record.py)
- Observability dimensions explicitly distinguish executability, oracle support, and ability
  to intervene; intervention readiness does not identify which behavior matters.
  [record.py, lines 22-26](../../../../../techne/fossils/record.py)

#### C3. Nyx algorithmic bits: behavior labels still encode an ontology
- The bit schema excludes names and lineages from its matching signature, using controlled
  behavioral axes instead. The signature includes verb, geometry, requirements, control,
  guarantee, strategy, and iteration. [schema.py, lines 7-21 and 114-124](../../../../../nyx/catalog/schema.py)
- Grades distinguish `T1-LOCAL`, `T1-SOURCE`, `T2`, `T3`, and unknown; a list/wiki seed
  remains T2 until source reading or running supplies stronger evidence.
  [schema.py, lines 19-21 and 103-104](../../../../../nyx/catalog/schema.py)
- The dated vocabulary changelog records earlier signature collisions between distinct
  sorting/search mechanisms and subsequent strategy/iteration refinements. This is a
  recorded instrument-development history, not a fresh rerun of its tests here.
  [schema.py, lines 106-111](../../../../../nyx/catalog/schema.py)
- Validation requires sources and failure conditions, but passing those field checks is
  not behavioral equivalence or causal validation. [schema.py, lines 127-156](../../../../../nyx/catalog/schema.py)

#### C4. Nyx anatomy catalogue and persistent mechanism ledger
- [ORGAN_CATALOG.json](../../../../../nyx/atlas/out/ORGAN_CATALOG.json) has 549 organs:
  evidence grades are 4 METADATA, 542 SOURCE_READ, 1 EXECUTED, and 2 INTERVENED.
  These five counts were computed from the snapshot; they are not receipts revalidated here.
- The atlas schema distinguishes source reading, execution, and intervention, preserves
  rejected cuts, and allows unknowns. An ACCEPTED boundary can rest on SOURCE_READ;
  the label alone therefore does not certify transplantable causal functionality.
  [schema.py, lines 9-17 and 155-159](../../../../../nyx/atlas/schema.py)
- Organ records carry assumptions, failure landscapes, human priors, control/cheat fields,
  source boundaries, compatibility, and portability; these are useful audit questions,
  not guaranteed affirmative answers. [schema.py, lines 88-101](../../../../../nyx/atlas/schema.py)
- [MECHANISMS.json](../../../../../nyx/atlas/gates/MECHANISMS.json) has 7 distinct IDs:
  4 PROPOSED, 3 EVIDENCE_SUPPORTED, and 0 with current disposition SURVIVED_TRANSPLANT.
  One has observer dependence UNKNOWN. These are recorded standings, not a global absence
  of successful reuse or independently audited judgments about the underlying experiments.
- The ledger keeps mechanism identity separate from experiment packets and requires
  falsifiers, evidence/counterevidence references, observer dependence, and transplant history.
  [mechanisms.py, lines 1-10 and 45-47](../../../../../nyx/atlas/mechanisms.py)
- Its `mechanisms_isolated` counter includes every non-WITHDRAWN record; it should not be
  reinterpreted as the number of experimentally isolated causal mechanisms.
  [mechanisms.py, lines 93-111](../../../../../nyx/atlas/mechanisms.py)

### Inferences
- **Proposed admission ladder:** external citation -> pinned source/record -> executable
  witness -> qualified intervention -> controlled transfer. Preserve the original grade
  alongside the new evidence; do not overwrite a historical label with a stronger claim.
- **Proposed unit ledger:** separately count ecosystems, source lineages, organs, persistent
  mechanism IDs, packets, and independent experimental units. None substitutes for another.
- **Proposed anti-prior check:** blind names and human interpretations during nomination,
  retain an unclassified channel, and test signature collisions before using recurrence
  matches to declare that an unfamiliar organism is merely a known algorithm.
- **Proposed control policy:** historical implementations may supply seeded positive/negative
  fixtures, but imported code and authored adapters must never become unledgered inheritance.

### Gaps
- Catalogue aggregates do not establish current executability, local availability, licensing
  sufficiency for a proposed use, receipt validity, or independence of recorded rulings.
- No specimen body, linked evidence packet, or engine experiment ledger was followed.
  This is catalogue-level appraisal, not a salvage recommendation or a program-wide verdict.

## 3. What should challenge v0, and what was safely within the read scope?

### Takeaway
Keep the initial distinction between capacity, reachability, competence, and nested improvement.
The most urgent additions to the later decision process are strong ordinary baselines,
qualified process boundaries, and a costed plan for discovery and independent replication.
The evidence-wiki query is **DEFERRED_DUE_TO_INDEPENDENCE**, not negative evidence.

### Cited Findings
- The comparison target is the Stage I freeze at commit
  `eeeda08bb45757298b3cb21ee22d816b44388aef`: [REQUIREMENTS.md](../REQUIREMENTS.md)
  and [RSE_ARCHITECTURE.md](../RSE_ARCHITECTURE.md), read from that revision.
  They propose three tracks, six lanes, qualified controls, and a 480 core-hour total ceiling;
  these are plans, not measurements of feasibility. [Architecture sections 3, 7, and 8](../RSE_ARCHITECTURE.md)
- The wiki client signature is `search_evidence(self, text, mode="hybrid", k=10, status=None)`.
  No source allowlist, historical cutoff, or architect exclusion is accepted by that method.
  [evidence_wiki/ew/client.py, lines 69-71](../../../../../evidence_wiki/ew/client.py)
- The corresponding GET search route takes q, mode, k, and optional status. It searches the
  index, then filters by status and attaches canonical claim text and agent identity.
  Status is not an independence boundary. [service.py, lines 281-312](../../../../../evidence_wiki/ew/service.py)
- Fossil encounters expose run/world/player/episode/namespace/ecology selectors; typed refs
  expose identifiers, namespace, and scope. Those narrower routes were inspected, but no
  certified historical-only allowlist was established from the permitted inputs.
  [service.py, lines 1396-1414 and 1911-1930](../../../../../evidence_wiki/ew/service.py)

### Inferences

#### Ranked challenges and proposed discriminators; no change to the frozen design
1. **Novelty versus ordinary meta-learning (P1/P4/P5; Q2/Q3/Q6).** A library learner or
   self-modifying matrix could produce the desired behavior without a new ontological category.
   Compare fixed-library, learned-library, fixed-plasticity, and learned/self-modifying-update
   arms with charged training and inference. Promote only the contrast actually demonstrated.
2. **Identifiability versus expressive physics (P5/P6; Q5/Q6).** Writable rules do not imply
   clean separability of S, U, and V. Qualify resets, clamps, and donor swaps on distributed
   seeded examples before interpreting a null; failed delivery means mediation unidentifiable.
3. **Discovery versus inherited scaffolding (P1/P2/P3; Q2).** Unseeded search may fail while
   a bounded witness exists. Compare static, shuffled, and stepping-stone histories, count
   population-wide search, and keep evolutionary acquisition separate from lifetime change.
4. **Independent substrates versus shared apparatus (P6; Q1/Q5).** Three representations
   can still share a decisive codec or world defect. Demonstrate one independently authored
   signed contrast and an alternate codec before treating track count as independent evidence.
5. **Compression versus accounting convention (P1/P7; Q3).** Count library/decoder/adapter
   information and computational costs; vary nuisance encodings. Require predictive or causal
   adequacy and later acquisition benefit, not shorter serialization or a familiar abstraction name.
6. **Scientific breadth versus qualification cost (architecture sections 6-8).** The 480
   core-hour ceiling does not establish adequate power across three tracks and six lanes.
   Benchmark tiny controls, price independent implementations and sample sizes, then reduce
   operating regimes or scope rather than dilute qualification or count episodes as lineages.
7. **Historical recognition versus ontology capture (C1-C4; R-APR-02).** Catalogue grades,
   coarse signatures, and human organ cuts can make familiar mechanisms easier to admit.
   Preserve raw evidence, unknowns, negative cuts, and an ontology-blind anomaly allocation.

#### Independence decision and bounded read ledger
- No wiki API request was made. Small k, search wording, status filters, and client-side
  removal cannot guarantee that forbidden architect text never enters the returned results.
- A future query requires a reviewed server-enforced allowlist or historical snapshot with
  provenance closure, including attached claims and linked results; otherwise retain deferral.
- Worktree: `C:/Prometheus-worktrees/enceladus-base-role`. Repository discovery used
  filename-only Git listings with exclusions, followed by explicit allowed-path reads.
- Design content was limited to ASTRA-6.0's own frozen requirements and architecture.
  No other architect designs or material under roles/Dionysus or roles/Epimetheus was read.
- Repository content inspected: the catalogue/schema/adapter files cited above, the Atlas
  ecosystem SQL schema, and the evidence-wiki client/service signatures and local skill.
  JSON catalogue access used aggregate or explicit metadata/reference projections, not
  linked packet narratives, source bodies, or Prometheus-analogue claims as scientific evidence.
- The assigned researcher guide was read first at the user-provided external skill path:
  `C:/Users/jcrai/.claude/skills/synced/e095b6b7-0ff1-4582-9b16-ed645da7837f_b4f2f83b-f3ac-47fc-a674-fd994e296747/deep-research/references/researcher.md`.
- No global codebase retrieval, unfiltered wiki access, direct database access, credential
  inspection, dependency installation, experiment execution, staging, or commit was performed.

#### Exact local snapshot locators
Review date: 2026-10-01. Hashes below are Git blob IDs, not execution receipts; line locators
refer to these snapshots. Relative links are navigation aids and may change after this review.

| Repository-relative source | Git blob ID |
|---|---|
| docs/phase3/design/ASTRA-6.0/REQUIREMENTS.md at freeze | b689efa3bc6ab25536bf5b5147fa385d605f1733 |
| docs/phase3/design/ASTRA-6.0/RSE_ARCHITECTURE.md at freeze | 7cb269deb81cc278fc4bcef39ca5dbcf6b363733 |
| roles/Atlas/catalog/ECOSYSTEMS.jsonl | 98a2fa77d015a8dd5a21ffe0a83679768304dfd5 |
| roles/Atlas/catalog/SCHEMA.md | 06a72585ba13100951211aa99714167edaa7b8af |
| atlas/harvest/catalog.py | b829a2078083c15e93176b01fb8b2826c9da353b |
| atlas/sql/008_m1-1c645957_ecosystem_catalogue.sql | daeeadeedba7cdd0a062a3ed7398378984b5f000 |
| techne/fossils/record.py | 950f84c090f970f96eaf96505a219a455f9a1df5 |
| techne/fossils/catalog.py | e5b2bf15cfd09b74284087c881d9d4c48073b0d5 |
| techne/fossils/CATALOG.json | 59afbb9b9de020dc6e796d5dd4e50ef1bbad66ef |
| nyx/catalog/schema.py | faa1647c13c7234f88a84fb68088319d7f11cce5 |
| nyx/atlas/schema.py | dc6c4c299141fc509732760ea46b8396f3ce9ae6 |
| nyx/atlas/mechanisms.py | c1db7f281c3a3385d8e3a88fe16d3a90a6c4cd52 |
| nyx/atlas/gates/MECHANISMS.json | 7f6dce79d5593998213931214baedf016c0500a0 |
| nyx/atlas/out/ORGAN_CATALOG.json | f3594151498255822a220c4e53034696c3c7eb5f |
| evidence_wiki/ew/client.py | 47627e82d7a3c90df4c94498730b6214e7e210e2 |
| evidence_wiki/ew/service.py | 92c6a15b1d5eb624c88415c220b350fe99d0a1f2 |

### Gaps
- Historical wiki claims, contradictions, and downstream consumers remain unassessed because
  a safe server-side scope was not established. Deferral says nothing about their existence.
- No source in this pass validates the proposed CPU/energy/attention caps, nested mediation
  instrument, or cross-substrate cost equivalence; those remain preregistered pilot questions.
- Parent handoff: use these findings to propose explicit post-freeze deltas and concrete
  baseline tests. This note neither edits Stage I nor authorizes a new implementation or run.