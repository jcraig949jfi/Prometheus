# Harmonia steering note: the POET / ALife comparative laboratory -> downstream benches

Author: Harmonia[gandalf-6cd1348b] (M3, "Harmonia F"), 2026-09-18 (UTC).
Source: operator directive received in chat 2026-09-17 evening local, verbatim at
prompts/2026-09-18_poet_alife_steering/OPERATOR_DIRECTIVE_verbatim.md; Techne's
autopsy (roles/Techne/POET_ALIFE_AUTOPSY_LEDGER_2026-09-17.md, #377); Nyx's
per-body cut plan (#379, roles/Nyx/prompts/2026-09-18_poet_alife_cut_into_bodies/).
Nothing here has run. Every number quoted is Techne's (E1 for me).

## 0. What "steering" means for this seat, and what it does not

The operator: "I'd like Harmonia play a role in steering the parts that Nyx
extracts into downstream benches." Two constraints bound that role. C8 (no
LLM as selector): this seat does not rank the five by importance; the order
below is the operator's. Charter s2 and base rule 6 (auditor independence):
this seat edits no cut, packet, fossil record or bench; it delivers
instruments, typed returns and route declarations.

So, per extracted part, Harmonia declares four things and nothing else:

    INSTRUMENT   the oracle and ruler the part needs before any bench may
                 consume it (R1-R3), and its cheat / positive / negative controls
    ROUTE        which bench can take it, in that bench's own intake shape
    FIRST RUN    the cheapest experiment that produces a row rather than a
                 description: reproduction, mutation, or new, labelled as such
    HOST         where it can execute now (M3 = pure Python only; M2 = docker,
                 compilers; "operator" = a key, spend, or a new box)

## 1. The two benches, in their own intake shapes (read, not assumed)

    SFE (Serendipity Foundry Engine, M2 192.168.1.191:8811, ledger eng_8a37a5d3...)
      Division of labour: Archaeon composes and queues, Vivarium executes,
      Harmonia infers (prompts/PROMPT_ARCHAEON_VIVARIUM_SFE_CONTRACT_2026-09-06.txt).
      Intake: an ADMITTED template (archaeon/templates/*.json: template_id, kind,
      param_space, origin, rationale, status ADMITTED, admitted_content_hash,
      frozen) + a queue row in viv.research_experiment_queue (family_id, arm_id,
      replication_of, candidate_set_id, request_key, cadence lane; <= 6/day).
      Theophrastus is its cell layer: a row is a result only with mechanism id +
      provenance, world id + hash, pressure id + magnitude, branch relation,
      intervention id, control cell ids, budget, measurement, engine build hash;
      the primitive is CONTRAST(A, B), never SCORE(A); dispositions NO_SIGNAL /
      WEAK_SIGNAL / REPRODUCIBLE_SIGNAL / REPRESENTATION_BLOCKED / INSTRUMENT_BLOCKED.
      A missing capability goes upward as a THEO-REQ (attempted experiment,
      blocked operation, minimal missing capability, evidence, smallest change).

    NPE (Nestor's Primordial Engine)
      NOT on origin/main. roles/Nestor on main is a charter-PENDING shell; the
      primordial/ tree lives on origin/nestor/* branches (sidequest-graphworld-
      2026-09-14, design-review-2026-09-14, r5-r-2026-09-15). Intake there is a
      RECEIPT (primordial/core/contract.py validate_receipt): lane, exp_id, claim,
      status in PASS/FAIL/KILL/NULL/INDETERMINATE, engineering and science as
      disjoint dicts, controls, rows, git; board_eligible needs PASS|KILL plus a
      RUN cheat control plus committed rows. Hot path: integer arrays / packed
      bytes, no str/JSON. Rule: "hands off production seats; read them, fossil-
      quarry them, copy semantics, never edit them". Its pressure menu
      (roles/Nestor/prompts/2026-09-14_graphworld_swarm/01_OPERATOR_BRIEF_ECOLOGY.md,
      ~60 items: Synaptic Rent, Brain Damage Episodes, QD Grave Robbery,
      Mechanism Viruses, Endosymbiosis, ...) is the natural catalogue to map a
      resurrected mechanism onto.
      Consequence: until primordial/ is on main with a charter, a route to NPE
      is a receipt DRAFTED in its shape and posted to Nestor, not a submission.

    Shared: both benches consume mechanisms as behaviour + interface with
    ancestry attached, never a historical name (charter s8-9). A RESURRECTION
    packet is the object that crosses; Theophrastus may return SURROGATE_CHALLENGE
    or EQUIVALENCE_CHALLENGE to this seat (R31).

## 2. Per specimen (operator's order), what this seat will do with what Nyx extracts

### 2.1 POET (TECHNE-104) -- "the decision boundary where ephemeral evolutionary evidence disappears"

    Nyx will hand    one organ per lifecycle boundary (mutate, MC test, PATA-EC,
                     novelty admission, transfer + fine-tune, archive) with a
                     DISCARD row each (fact, computed-at line, dies-at line,
                     preservation cost class); a PRESSURE "basis-population
                     relativity" with an observable; a prediction packet IF the
                     PATA-EC function isolates as pure numpy (Nyx #379 3a)
    Inputs I need    Techne: ONE traced environment lineage from a real run
                     (per-optimizer CSVs, <id>.best.json, env_archive, the log
                     text where parent_optim_id is printed) with hashes; the
                     pinned commit (master@8669a17e) and the gym[box2d] world id
    INSTRUMENT       (a) PATA-EC recomputation ruler: from the saved thetas and
                     env configs, recompute each env's centered-rank vector and
                     the k=5 novelty decision, and compare to the decisions the
                     run actually took. Cheat control: feed the run's own logged
                     decisions back through the channel -> agreement 1.0 exactly.
                     Positive: shuffle one theta's scores -> the decision flips
                     where the margin is small (must be visible). Negative:
                     identical basis population -> identical vectors, bit for bit.
                     (b) Reconstructability meter: for each admission and
                     transfer event in the lineage, RECONSTRUCTIBLE / PARTIAL /
                     LOST from what survives on disk, with the discard ledger's
                     cost class beside it. This turns "POET throws away X" into a
                     rate with a denominator.
    FIRST RUN        REPRODUCTION: recompute PATA-EC from the CSV/best.json of the
                     traced lineage; agreement rate with logged novelty
                     admissions (E3 when run). M3-feasible if the function
                     isolates as numpy (Nyx's condition); the run that produces
                     the lineage is M2 (box2d, docker).
    MUTATION         the operator's property P_t(E) != P_{t+k}(E): hold E byte-
                     identical, vary the basis population (drop the archived
                     policies; drop the newest k; add a duplicate) and measure the
                     displacement of E's vector and whether its admission
                     decision flips. This is a Theophrastus cell: mechanism =
                     PATA-EC novelty gate, pressure = basis-population turnover,
                     intervention = basis ablation, observable = decision flip
                     rate. Pure numpy once the thetas' scores are logged.
    NEW              an "evidence half-life" experiment: re-run one POET
                     lifecycle with a shim that WRITES the discarded facts
                     (parent id, admission vector, rejected children) to a side
                     ledger, and measure the cost (bytes, seconds) of keeping
                     them. That is the operator's CHEAP/MODERATE/EXPENSIVE column
                     measured instead of estimated. Faithful branch first (C9):
                     the shim is a descendant, never the fossil.
    ROUTE            SFE / Theophrastus cell for the mutation; NPE receipt for the
                     PATA-EC organ as a "world x population" characterization the
                     graphworld swarm can copy (semantics, not code); the
                     preservation-cost result goes to the Soup admission schema
                     owner (Archaeon) as evidence about what a Soup record must carry
    HOST             lineage: M2. Rulers: M3.
    HISTORY_MODE     partly_discarded

### 2.2 Avida (TECHNE-105) -- the calibration specimen for "ancestry known"

    Nyx will hand    the COARSE cut (10 organs) with the population-save /
                     genotype-ancestry bookkeeping READ (the TECHNE-105 boundary)
    Inputs I need    Techne: our own .spop from the fossil's harness with
                     SavePopulation (+ ancestry options) at u 300 or later, the
                     events.cfg line that produced it, the run receipt; converters-
                     avida pinned; phylotrackpy / hstrat pinned (both pure Python)
    INSTRUMENT       ANCESTRY GROUND-TRUTH RULER. Recorded provenance graph G_true
                     (from .spop parent ids) vs a reconstruction G_hat produced
                     from genomes ONLY (parsimony on edit distance; hstrat-style
                     annotations if present). Observables: edge precision/recall,
                     depth error, fraction of extinct branches recoverable, and
                     the number of provenance fields that could be dropped before
                     recall falls below a preregistered floor. Cheat control:
                     reconstruct from the true parent ids themselves -> recall 1.0.
                     Positive: scramble 10% of parent ids -> recall must fall.
                     Negative: a population with no reproduction events -> the
                     empty graph, no invented edges.
                     This ruler is the thing TerraLingua (2.5) is later graded with:
                     it is what "ancestry known" means, measured.
    FIRST RUN        REPRODUCTION: converters-avida on our .spop; one lineage
                     ancestor -> saved population, listed with mutation positions.
                     M3 can run this half (pure Python on a file).
    MUTATION         provenance ABLATION: remove fields from the saved population
                     (parent id, birth update, mutation record) one at a time and
                     re-run the reconstruction; the curve "what survives when X is
                     not kept" is the calibration result.
    NEW              a shadow-run replicate (MODES-style persistence filter) is
                     NOT started until the ground-truth ruler has passed its
                     controls (Amendment 2 C11: instrument before specimen).
    ROUTE            NPE receipt (its contract already carries rows + git +
                     controls; ancestry as integer parent arrays fits its hot-path
                     rule) and a Theophrastus cell: mechanism = ancestry
                     bookkeeping, pressure = provenance loss, observable = recall
    HOST             .spop: M2. Ruler: M3.
    HISTORY_MODE     recorded_directly

### 2.3 Tierra (TECHNE-106) -- what becomes a specimen at all

    Nyx will hand    the gene-bank admission rule as a cut (genebank.c and its
                     thresholds), after license.h is read and the body is admitted
    Inputs I need    Techne: the licence reading (LEGAL_RESTRICTION or not), a
                     built 6.02 in fossil-c on M2, ONE generated gene bank with its
                     genome stream (the candidates the bank saw) and the bank's
                     output, hashed
    INSTRUMENT       ADMISSION-RULE REPLAY: apply the bank's thresholds to the
                     saved genome stream outside the fossil and reproduce the
                     bank's accept/reject decisions. Cheat: feed the bank's own
                     decisions -> 1.0. Positive: lower a threshold -> more
                     specimens, monotone. Negative: an empty stream -> empty bank.
    FIRST RUN        REPRODUCTION of the bank from the stream (M3 if the rule
                     isolates as arithmetic on genome records; else M2).
    MUTATION         threshold sweep: specimen count and diversity vs the budget
                     the rule encodes -- "what banked history looks like under
                     other disk budgets", the operator's question as a curve.
    NEW              none until the above exists.
    ROUTE            the Soup admission schema (Archaeon) as a historical
                     precedent with numbers; NPE as a candidate "what gets kept"
                     organ for its soup/ lane. Not an SFE experiment.
    HOST             M2 for everything that executes the fossil.
    HISTORY_MODE     selectively_banked

### 2.4 ASAL (TECHNE-107) -- metric pathology vs observer regularization

    Nyx will hand    asal_metrics.py at function level; a packet whose controls
                     are the operator's four cases (two-frame cycle, iid noise,
                     coherent drift, actual Lenia) with preregistered bands,
                     citing Techne's numpy numbers as the metric-only
                     pre-measurement (static 0.8750, drift 0.8654, cycle 0.7500,
                     iid 0.0390; T=8, D=512, seed 0)
    Inputs I need    Techne: the three .npz datasets that answer 200 pinned as
                     specimen data with sizes; the CLIP weights identity (name,
                     hash) the fossil uses; a Lenia rollout of 8 frames from the
                     pinned code
    INSTRUMENT       two-level ruler. LEVEL 1 (metric alone, unit vectors):
                     reproduce Techne's four numbers exactly -- that IS the cheat
                     control for level 2 (the metric's incentive with no observer).
                     LEVEL 2 (through CLIP): the same four sequences as IMAGES;
                     the reading is the ORDER of the four scores and the ratio
                     iid/drift. Positive control: a sequence CLIP must separate
                     (frames of different object classes) scores as "open-ended"
                     as iid at level 1. Negative: 8 identical frames -> the
                     static value at both levels.
                     The result the operator asked for is one number per
                     observer: how much of the metric's noise-reward survives
                     the image manifold (iid/drift ratio at level 2 over level 1).
    FIRST RUN        REPRODUCTION of level 1 on M3 now (numpy). Level 2 needs
                     torch + CLIP weights: NOT on M3 without an install the
                     operator authorises (a venv is possible; CPU inference on 32
                     images is minutes). Flagged, not assumed.
    MUTATION         swap the observer (a second embedding model) and re-read the
                     order: if the order is observer-dependent, "novelty to an
                     observer" is measured as a property of the observer.
    NEW              none before level 2 exists.
    ROUTE            SFE: an observer-scored novelty is a candidate PRESSURE for
                     ecosystems; its exploitability is a property to record BEFORE
                     any bench adopts CLIP-based novelty. Theophrastus cell:
                     mechanism = open-endedness score, pressure = adversarial frame
                     sequences, observable = rank of iid vs drift.
    HOST             level 1: M3. Level 2: M3 with an authorised install, else M2.
    HISTORY_MODE     observer_compressed

### 2.5 TerraLingua (TECHNE-108) -- reconstruction when provenance is missing

    Nyx will hand    006_artifact_philogeny.py as two organs (text-match "hand
                     annotation"; LLM inference with confidence) and the
                     scrambled-candidate control (confidence on shuffled
                     candidates must fall to chance)
    Inputs I need    Techne: ONE experiment's slice (not the 4.7 GB set) with raw
                     logs, both methods' outputs and confidences, hashed; the
                     operator: whether the LLM arm may be re-run (API key, spend)
    INSTRUMENT       DISAGREEMENT TABLE + CALIBRATION AUDIT. Method 1 vs method 2
                     edge sets: agreement, edges only-in-1, only-in-2, and, where
                     an independently known interaction history exists in the
                     logs (agent A observed artifact X before making Y), both
                     methods against that. Confidence audit: bin the LLM
                     confidences and measure agreement with method 1 and with the
                     log-derived history per bin. Cheat: feed method 1's edges to
                     method 2's scorer -> agreement 1.0. Positive: the scrambled-
                     candidate arm must collapse to chance. Negative: artifacts
                     with no prior artifacts in scope -> no ancestors inferred.
                     Then: grade TerraLingua's reconstruction with the Avida
                     ground-truth ruler's vocabulary (2.2), so "how good is
                     reconstruction without provenance" is one scale for both.
    FIRST RUN        REPRODUCTION of method 1 (text match) on one experiment, on
                     M3 (pure Python over text). Method 2 only with the
                     operator's key decision; otherwise its LOGGED outputs are
                     audited as claims (the operator's words).
    MUTATION         candidate-list scrambling (Nyx's control) and candidate-list
                     truncation: confidence vs list size.
    NEW              none here; the product is an instrument, not a mechanism.
    ROUTE            no bench consumes TerraLingua; the instrument (reconstruction
                     grader) is what NPE/SFE lineage records use whenever their
                     own provenance is missing. Delivered to Archaeon (Soup
                     ancestry schema) and Nestor.
    HOST             M3 for method 1 and the audit; operator for method 2.
    HISTORY_MODE     reconstructed_afterward

## 3. Two axes this seat will carry as FIELDS, never merged

Every RESURRECTION packet, typed return and cell row from this laboratory
carries:

    HISTORY_MODE   recorded_directly | selectively_banked | partly_discarded |
                   observer_compressed | reconstructed_afterward
                   (the operator's five-case brace, as an enum; one value per
                   specimen; the instrument that establishes it is named)
    NOVELTY_KIND   structure | behavior | observer | consequential
                   (the operator's four-way inequality; one value per OBSERVABLE,
                   not per specimen; a specimen may produce rows of several kinds)
    PRESERVATION_COST  CHEAP | MODERATE | EXPENSIVE | STRUCTURALLY_DIFFICULT,
                   carried through from Techne's discard ledger unchanged, so no
                   ruling of this seat can read a lost datum as a design mistake
                   without its cost beside it

Where two specimens' novelty observables disagree (POET's PATA-EC novelty vs
ASAL's score on the same sequence, say), the disagreement is recorded as a
finding with both values, never averaged. This is the operator's "their
disagreement is information", made a rule of this seat.

## 4. Order, and what runs where now

    operator's order   POET, Avida, Tierra, ASAL, TerraLingua (kept)
    M3 now             ASAL level 1 (numpy) reproduction; Avida ruler code written
                       against converters-avida's example .spop while ours does not
                       exist (instrument before specimen); TerraLingua method-1
                       reproducer once a slice is pinned
    M2 needed          POET lineage run; Avida .spop; Tierra build + bank
    operator needed    ASAL level 2 install or host; TerraLingua LLM arm; a
                       docker/compiler host for everything in the M2 column,
                       since the M1/M2 pipeline instances are shut down

## 5. Asks (typed, R31 latencies apply to the recipients as to me)

    to Techne   ASK H1: per specimen, the input rows of section 2 as named files
                        with hashes (lineage, .spop, bank + stream, .npz + CLIP id,
                        one TerraLingua slice); ASK H2: in each new record.json,
                        the Python major version and native deps (Nyx's ASK 4,
                        seconded); ASK H3: keep HISTORY_MODE out of
                        MECHANISM_CATALOG.json's novelty field -- it is this seat's
                        field on the resurrection side, filled from measurement
    to Nyx      ASK H4: each packet names the observable's NOVELTY_KIND; ASK H5:
                        the POET PATA-EC packet, if numpy-isolable, is next on
                        the ruler after particles 002
    to Archaeon ASK H6: the Soup admission schema owner receives the Tierra bank
                        rule and the POET preservation-cost result as precedents
                        when they exist; a THEO-REQ-style note now that
                        HISTORY_MODE and NOVELTY_KIND are fields a cell row will carry
    to Nestor   ASK H7: is a receipt drafted in primordial/core/contract.py's shape
                        the right way to hand an organ to NPE while primordial/ is
                        off main? If not, name the shape.
    to operator ASAL level 2 host / install; TerraLingua LLM arm; the box.

## 6. What this note is not

Not a ranking. Not a result. Not a change to any cut, packet or bench. The
first rows will come from ASAL level 1 (M3, days) and from whichever of the
POET lineage / Avida .spop lands first on M2. Falsifier of the plan: if the
Avida ground-truth ruler cannot pass its own positive control (scrambled
parent ids not lowering recall), the "ancestry known" calibration is not
what section 2.2 says it is, and TerraLingua cannot be graded against it.
What should stop: describing what a system discards without its
preservation cost and without a reconstructability rate.
