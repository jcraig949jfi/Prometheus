You are a blind quality scorer for research reports about the Prometheus research repository. You receive several
reports, each labelled X###. They come from different sources, and you do not know which. Score each report
independently against the rubric below. Do not try to find out where a report came from: do NOT search the
repository for a report's own sentences, title or label. Only verify the evidence its claims cite.

Tools: Read, Grep and Glob inside the repository, and `rogit` for git history (a single command, used exactly like
git).

Rubric (frozen, S3_PROTOCOL s5). Score each item 0, 1 or 2:
1. EVIDENCE: are the load-bearing claims tied to checkable primary evidence (path:line, commit:path, data)?
   0 = mostly unsupported, 1 = partly, 2 = consistently.
2. CORRECTNESS: pick the 3 highest-stakes claims and verify them in the repository yourself.
   0 = a load-bearing claim is false, 1 = unverifiable or partly true, 2 = all 3 verified true.
   Name the 3 claims and what you found.
3. ANSWERS THE QUESTION: does it answer what it set out to answer, or state precisely why it could not?
   0 = no, 1 = partly, 2 = yes.
4. LIMITS STATED: does it say what was not checked and what would change the conclusion?
   0 = no, 1 = partly, 2 = yes.
5. USABLE: could a research principal act on it without redoing the work?
   0 = no, 1 = with significant rework, 2 = yes.

Write `scores.json` in your output directory:
{"<label>": {"evidence": n, "correctness": n, "answers": n, "limits": n, "usable": n, "total": n,
             "checked_claims": ["claim -> verified/false/unverifiable, with path:line"], "notes": "one or two sentences"},
 ...}
Finish with one line per report: `<label>: <total>/10`.


---------------- THE REPORTS ----------------


======== REPORT X016 ========

# [redacted] [redacted] — Assay blind spots, and an observer that may smuggle in a heredity ontology

[redacted]
repository at `5266ccebea3ad5522b7cfa7a07a8718cac113a70`. All citations
are `path:line` at that commit unless a commit is named. No code was run.

## 1. Question

The [redacted] bundles three harvest entries:

- **H-D3-14.** [redacted]'s AETH-02 negatives say its assays "cannot see" five
  classes of structure: spatially distributed, informational, uncontested,
  stateful-but-not-self-repairing, and dynamically reconfigurable. What
  assay could see them? And is [redacted]'s "no circuitry" reading an
  instrument limit?
- **H-D3-15.** Does the observer bring in a template-copy / Mu / parent-preserving heredity
  ontology (Astra, `[redacted]/AETH-01/ASTRA_REVIEW_01.md:209`)? How much of
  what the observatory reports comes from its vocabulary rather than from the physics?
- **H-D3-16.** How can recursive construction, mutual constructors and
  partial copying completed by the environment be turned into testable
  predicates?

Answered question: **In the committed record, how far are [redacted]'s reported
results and negatives set by the observer's ontology and assay coverage,
and how far are they findings about the physics? What has been done to
separate the two?**

## 2. Method

1. I read the source passages and everything that responds to them: the
   Astra review, the repair ledger, the terminology-refactor receipt, the
   repaired claim ladder, the observatory specification, the AETH-02
   native-circuitry and closing reports, the AETH-03 propagation-assay
   audit, Physics Design 03, the research-block synthesis and the engine card.
2. I read the code that implements the observer: `aeth01_graph.py`,
   `aeth01_observatory.py`, `aeth03_assay_audit.py` and the claim-ladder
   fixtures in `scientific_aeth01.py`.
3. I separated three layers:
   - (a) vocabulary: names only;
   - (b) inference contract: which evidence the claim ladder accepts;
   - (c) instrument logic: what the running assays can register.
4. For each layer I asked whether the heredity/template-copy assumption
   comes from the observer or from the `aeth01.v1` transition law.
5. I searched the repo for anything that designs or runs assays for the
   five blind-spot classes or for mutual constructors.
6. A decisive computation that I could not run is specified in `analysis.py`.

## 3. Evidence

### 3.1 The blind spots are stated as instrument limits by the program itself

- The AETH-02 conclusion is narrowed on purpose: "No evidence was found that the
  measured persistent-edge and cycle structures perform a demonstrated
  nontrivial function under the assays run… must not be quoted as, '[redacted]
  contains no possible circuitry.' The assays here can see localisation,
  contest, persistence and resource routing. They cannot see…"
  (`[redacted]/AETH-01/AETH-02_CLOSE_2026-09-24.md:276-286`).
- The same operator amendment appears twice in
  `[redacted]/AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md`:
  - `:451-459` gives the verdict scope.
  - `:602-611` says the four measured dimensions "are **not jointly
    necessary**, and freezing them as the definition of circuitry would make
    this round's instruments into the criterion". It asks that a future positive
    claim be "stated against whatever dimensions its own mechanism implies,
    declared in advance, each carrying a matched null".
- The engine card at HEAD still lists "anything spatially distributed and
  informational rather than resource-routing" as "Ambiguous or open"
  (`[redacted]/AETHER_ENGINE_CARD.md:113-121`). It also says "nothing in [redacted]'s
  observatory can say a structure does something useful, only that it causes
  differences" (`:117-118`).
- **A later, independent instrument limit.** The AETH-03 content signature
  "detects transport in a clean relay but not in a rich soup, even for a law
  that forwards bytes by construction (E-P1 failed). A value-provenance
  detector would be needed" (`[redacted]/AETH-03/RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md:39-42`;
  `[redacted]/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md:216-224`, "Recorded as an
  instrument limit, not repaired here"). This is a blind spot for
  *informational* structure that was measured directly: a known positive
  control went undetected.
- **Part of the negatives is not an instrument limit.** The AETH-02 falsifiers show:
  - the bulk is about 92% static;
  - about 94% of template change disappears without injected perturbation;
  - a one-bit difference stays within about one site for 10,000 ticks.

  (`[redacted]/AETHER_ENGINE_CARD.md:123-140`;
  `[redacted]/AETH-01/AETH-02_CLOSE_2026-09-24.md:288-302`.) The one-bit-twin
  locality result is *not* heredity-shaped. It counts any differing carried
  state, including hidden flags (`[redacted]/AETH-03/PROPAGATION_ASSAY_AUDIT.md:14-16,35-40,130-132`).
  Informational, distributed or reconfigurable circuitry would still need
  *some* difference to move. Very limited causal reach therefore bounds those
  classes in `aeth01.v1` under B-balanced parameters. It does not rule out
  uncontested, stationary or stateful structures that hold information
  without moving it.

### 3.2 Is the heredity ontology in the vocabulary, the inference contract, or the instruments?

**(a) Vocabulary: addressed, and only vocabulary.** The terminology refactor
renamed heredity→configuration transmission, lineage→causal provenance,
offspring→successor, mutation→perturbation, reproduction→recursive
construction, and so on (`[redacted]/AETH-01/TERMINOLOGY_REFACTOR_RECEIPT_2026-09-21.md:81-106`).
Its receipt says: "No transition equations, byte layout, arbitration logic,
energy accounting, Mu-trigger behavior, or scientific thresholds were
changed. This is nomenclature only" (`:150-152`). Several items were kept as
frozen aliases: `HEREDITY_VARIATION`, `mutation_applied`, `MUT_NUMER`
(`:110-125`; `[redacted]/test/reference/scientific_aeth01.py:11-24`). A linter
enforces the vocabulary going forward (`:156-161,194-198`). The rename does not
answer Astra's point. Astra flagged the concern as "not solved by keeping
metadata out of physics" (`ASTRA_REVIEW_01.md:181`).

**(b) Inference contract: partly repaired; template-copy is still the backbone.**

- The repair ledger accepts S04, M05 and M08
  (`[redacted]/AETH-01/REPAIR_LEDGER_01.md:175-211,416-442,509-534`). The repaired
  ladder:
  - separates ten evidence axes;
  - drops "resemblance first" and "parent-intact vs parent-consumed" as
    universal requirements (`[redacted]/AETH-01/HEREDITY_REQUIREMENTS.md:141-149`);
  - allows standing, spatial and energy-pattern variation as well as
    Mu-origin variation (`:130-139`);
  - treats a distributed consortium as "a normal, not degenerate, case" (`:51-55,161`).

  These are real de-biasing steps against the template-copy/Mu/parent ontology.
- The heredity shape remains in the higher tiers:
  - "Capacity" is defined as a *write* into the target's opcode/arg0/arg1
    fields (`HEREDITY_REQUIREMENTS.md:35-38,76-86`).
  - Recursion is capacity-construction repeated along a chain (`:119-129`).
  - Tier 5 requires that a variant be "copied onward by a further
    value-transport event" (`:42-45`) and propagated "by a further
    CAUSAL_VALUE_CONSTRUCTION step" (`:130-136`).

  So tiers 2-5 still count transmission only when a winning write copies a
  byte or capacity. They do not count:
  - transmission through energy landscapes;
  - transmission through hidden carried state;
  - contest outcomes ("who wins" changing without any byte being copied);
  - reconfiguration of aim.

  The provenance graph the ladder uses is built from "this target field's
  stored value … was contributed by winning source site X" chains
  (`[redacted]/AETH-01/OBSERVATORY.md:158-173`).
- The ledger's M08 repair covers only component tracking and the novelty
  assay (`REPAIR_LEDGER_01.md:509-534`). It does not address the sentence at
  `ASTRA_REVIEW_01.md:209` as a whole. The ledger dispositions only numbered
  S/M/N/B/K items; it has no entry for the "Ontology audit" table (`:197-209`).
- **Astra's own closure review names this residue.** S04 and M08 are both
  PARTIALLY_CLOSED (`[redacted]/AETH-01/ASTRA_CLOSURE_REVIEW_02.md:78,88`):
  - S04: "tiers 3+ still require opcode/arg0/arg1 causation while the
    resource row admits resource-mediated evidence to tiers 2-5 … A funded,
    prewired writer exposes that exclusion" (`:78`).
  - In a probe, an energy donor made a preconfigured writer emit, which
    blocking the funding prevented. The helper still classed the donor edge
    "only CAUSAL_VALUE_CONSTRUCTION" (`:104-110`). This is a demonstrated
    false negative of the copy-shaped ladder.
  - The K3 helper "still encodes a restricted field ontology and does not
    qualify a general detector" (`:460-462`).
- **The linter does not watch the terms Astra named.** The terminology
  linter's deprecated list covers heredity, lineage, offspring, mutation and
  others, but not "parent", "template", "copy", "inherit" or "Mu"
  (`[redacted]/test/test_aeth01_terminology_audit.py:34-61`). The AETH-03 observer
  vocabulary ("sufficient parent", "template") therefore passes
  (`aeth03_assay_audit.py:28-44`).
- **Some of the fusion is a declared hidden prior of the physics.** "Hidden
  prior: 'movement' and 'replication' are physically fused by this choice"
  (`[redacted]/AETH-01/DECISIONS.md:141-152`, D-AETH01-07). Mu acts on fields 0-3
  only (`DECISIONS.md:73-75`).

**(c) Instrument logic: mostly from the physics, not the observer.**

- `aeth01_graph.py:9-26` says outright that a site's single out-edge per tick
  is a consequence of the transition law. Its cycle/in-tree structure is
  "consequences of the transition law, not findings", measured by a test
  rather than assumed.
- The template-copy primitive is part of the physics. Astra: "Writing a
  neighbor's byte is a supplied primitive" (`ASTRA_REVIEW_01.md:202`).
  Mu is applied only where a site wins a write
  (`[redacted]/AETH-03/PROPAGATION_ASSAY_AUDIT.md:52-53`).
- So for `aeth01.v1`, the edge/"template change" observables
  (`AETH-02_CLOSE_2026-09-24.md:243-251`) describe the law's own write
  channel. The observer does not impose them.
- The tier-1 observatory computes only histograms, entropy, Gini,
  autocorrelation, compression and change rate. It deliberately contains no
  construction or transmission detector (`[redacted]/observatory/aeth01_observatory.py:1-29`).
- The AETH-03 twin and counterfactual-parent assay is heredity-neutral:
  - it asks only whether a difference at x is caused by a neighbour's full
    state (`[redacted]/observatory/aeth03_assay_audit.py:28-44,168-183`);
  - its predicate covers every carried state (`PROPAGATION_ASSAY_AUDIT.md:130-132`).
- One structural bias remains. Causation is scored by *single-parent
  sufficiency*, and "joint" events are assigned a lower bound
  (`PROPAGATION_ASSAY_AUDIT.md:146-150`). Only 2 of 2,793 audited events were
  joint (`:118-119`). The audit's conclusion that "differences are caused one
  parent at a time" is partly fixed by that definition. That is the only measurement in the repo that touches
  "spatially distributed" causation, and it is made at radius 1 with pairs of
  neighbours inside one step. It is not a test of distributed circuitry.

### 3.3 Operationalising recursive construction and mutual constructors (H-D3-16)

- There are requirements text and fixtures, but no built detector:
  - Formal tiers 3-4 with ablation batteries are in `HEREDITY_REQUIREMENTS.md:76-129`.
  - The adversarial-case table has "Mutual constructors A<->B … Both
    directions of the intervention test … must be run and both must show
    positive causal effect before 'mutual' is claimed" (`HEREDITY_REQUIREMENTS.md:159`).
  - The same table covers partial copying completed by the environment:
    "Causal provenance graph must show ALL contributing source sites/events"
    (`:160`).
  - It also covers the distributed consortium (`:161`).
  - The seeded fixtures exist: relay, activation, distributed, and recursive
    activation (`[redacted]/test/reference/scientific_aeth01.py:42-117`). By the
    repo's own account, fixture 4 shows only
    RECURSIVE_ACTIVATION_OF_PRECONFIGURED_MACHINERY, "NOT … recursive
    configuration construction" (`HEREDITY_REQUIREMENTS.md:124-129`).
- The document status is "DRAFT REQUIREMENTS ONLY. No detector is built in
  AETH-01" (`HEREDITY_REQUIREMENTS.md:4-5`). The open question is still worded
  "not yet designed" (`[redacted]/AETHER_OPEN_QUESTIONS.md:134-137`). The K3
  tests call themselves "fixture-local calibration, not a general detector"
  (`[redacted]/test/test_aeth01_kill_gates.py:291`). The
  engine card lists "recursive construction" among things "Not built in"
  (`[redacted]/AETHER_ENGINE_CARD.md:52-56`).
- None of the tests handles a mutual constructor whose two directions are each
  *necessary but not sufficient*. The both-directions test (`:159`) uses
  single-source perturbations, so it would hit the same single-cause bias as
  the parent audit.
- A repo-wide search for "mutual constructor" / "A builds B" /
  "value-provenance" outside [redacted] found only harvest or frontier citations
  of the open question (e.g. `roles/[redacted]/frontier/poi/raw/I2_substrate_physics.md:245`).
  It found no [redacted] design.
- **Closest cross-substrate evidence (not [redacted]).** [redacted] P-11 built
  specimens for this: a two-tape mutual-construction pair ("A0 copies
  A1 … A1 copies A0 … neither member alone copies itself"), host-mediated
  heredity, and complement-encoded offspring
  (`roles/[redacted]/challenge/p11/PREREG_P11.md:168-170`). A copy-fidelity
  predicate rejected all three as false negatives
  (`roles/[redacted]/challenge/p11/RESULT.md:48-50`). This is independent
  support, in a Z80/toy-VM substrate, that copy-shaped heredity predicates miss
  mutual constructors and host-mediated heredity. It is a
  known-answer battery that any [redacted] mutual-constructor predicate could
  reuse.

## 4. Result

1. **H-D3-14: the "no circuitry" reading is partly an instrument limit, and
   the program itself declares it one.**
   - The AETH-02 negative is scoped to four assay dimensions. The operator
     amendment explicitly refuses to freeze those as the definition of circuitry.
   - One informational blind spot has since been *measured*: content transport
     goes undetected in a rich soup, and a value-provenance detector is needed.
   - The rest of the negative is not an instrument artefact. A heredity-neutral
     twin assay shows that a one-bit difference barely travels (about one
     site) and that the medium is about 92% frozen. So any
     distributed/informational circuitry in `aeth01.v1` (B-balanced) would
     have to work with almost no causal reach.
   - No assay for the five classes has been designed or run. Section 5 lists
     what would detect them.
2. **H-D3-15: the heredity ontology lives in the inference contract, not in the
   running instruments. Only the vocabulary layer was fixed; no
   ontology-neutral re-analysis exists.**
   - The measured edge graph and template-change figures come from the physics
     (a byte-write primitive), not from the observer.
   - The claim ladder (tiers 2-5) still recognises transmission only as a
     winning-write copy of a value or of opcode/arg0/arg1 "capacity". Because
     of that, a heredity route through energy, hidden state, contest outcome or
     re-aiming could not reach tiers 2-5 however well evidenced.
   - This matters for TH-001 and for "organism-free" claims. Any positive
     heredity claim made through this ladder would be ontology-shaped.
     [redacted]'s current *negatives* rest mainly on the heredity-neutral twin
     assay, so they are less exposed.
3. **H-D3-16: partly operationalised on paper; not operationalised as a
   running detector.** Requirements exist for:
   - capacity recursion;
   - both-direction mutual-constructor tests;
   - all-contributors provenance for environment-completed copying.

   Only seeded fixtures are built. The strong case, recursive *configuration*
   construction, has no fixture. No predicate handles jointly-necessary
   mutual causes.

Confidence: high on 1 and 3, because they rest on explicit program
statements; medium-high on 2. The "how much" in H-D3-15 is not quantified by
anything in the repo. `analysis.py` specifies the computation that would
quantify it.

## 5. What an assay for the five blind-spot classes would look like (design, not evidence)

These are derived from the program's own repaired requirements and
instruments. None has been run.

| Class | Candidate assay | Built from |
|:--|:--|:--|
| spatially distributed | joint-source ablation and rescue over *sets* of sites (k ≥ 2, non-adjacent), with a matched random-set null; report the super-additive share | parent audit's JOINT category (`aeth03_assay_audit.py:38-44`); "redundancy-aware joint ablation/rescue" (`OBSERVATORY.md:180-182`) |
| informational (vs resource-routing) | value-provenance tracking: which source byte a value was copied from, followed across rewrites; control = `fwd` relay in a rich soup (E-P1 must pass) | `PHYSICS_DESIGN_03:216-224` |
| uncontested in normal operation | counterfactual contest injection: add a competing writer and measure the downstream difference, instead of observing contests | edge classes `aeth01_graph.py:52-60` ("only intervention can tell") |
| stateful, not self-repairing | set a state bit, wait a delay, then read it out via a later twin divergence; compare against the delayed-causation share (which "does not discriminate" as currently defined, `PHYSICS_DESIGN_03:225-227`) | twin assay |
| dynamically reconfigurable | per-channel causal decomposition (content vs enabling vs energy vs hidden vs contest) of each causal event; `rcv_str`'s "activity re-routes later activity" is the known-answer case | `RESEARCH_BLOCK_SYNTHESIS:31-38`; `analysis.py` |

## 6. Limits

- I read committed documents and code only. No experiment was run, and the
  numbers above are quoted from committed reports.
- The layering in 3.2 (vocabulary / contract / instrument) is my analysis,
  not a program decision.
- "Mostly from the physics" applies to `aeth01.v1` and the AETH-03 variant
  laws. A different substrate would need the same check again.
- I did not check whether `World.extra` includes `rcv`'s received flag in
  every variant; `analysis.py` assumes it (per `PROPAGATION_ASSAY_AUDIT.md:130-132`).
- The search for later evidence was grep-based across the whole repo. Material
  under a different vocabulary could have been missed.

## 7. What would change the conclusion

- **H-D3-15 / result 2.** Run `analysis.py`. If literal-copy events are ≥ 0.8
  of causal events for every law and arm, the template-copy ontology is mostly
  the physics' own, and Astra's concern reduces to naming and inference hygiene. If non-copy
  channels are ≥ 0.5 for any law or arm, the tier ladder is blind to most
  causal transmission there, and it needs a channel-neutral tier.
- **Result 1.** A value-provenance detector that passes E-P1 in a rich soup
  and still finds no content transport would turn the informational blind spot
  into a real negative. A positive on any row of section 5 would overturn
  "no circuitry".
- **Result 3.** A committed detector, or a fixture showing recursive
  *configuration* construction (routing and field ablations at each
  generation), or a jointly-necessary A↔B fixture, would move H-D3-16 from
  "paper" to "operational".
- A commit after `5266cceb` that re-analyses AETH-02/03 data under a
  channel-neutral ontology would supersede the "no ontology-neutral
  re-analysis" finding.



======== REPORT X017 ========

REPORT -- surprise-driven eviction vs random eviction: noise, recency or capacity?

1. WHAT I SET OUT TO TEST
A bounded low-rank learner (BufferALS: warm-started ALS over a buffer of B exact records) must choose which records to
evict. Two "surprise" rules (keep_worst = keep the highest current |residual|; residual_reservoir = residual-weighted
A-Res reservoir) were reported to lose to random reservoir eviction on a positive-control world where half the cells
carry extra noise. I asked: (a) is that loss a noise-retention effect (does it appear only as the extra noise grows),
(b) is surprise in the regime-switch family really a recency proxy, (c) is capacity or eviction order the bigger lever
in the committed dev rows, and (d) is the "random" control actually relevance-blind.

2. WHAT I DID
Code: [redacted]/ (lm01 arms, families, fixture) exported from origin/main@6ff2b2f8a into work/[redacted]/src and run only there.
- Reproduction: work/[redacted]/dose.py re-implements the fixture's positive control (F2_latent L2, generator lowrank,
  rank 3, B = cells/4 = 432, dev seeds 9330000-9330003, corrupted half = mode-0 index < d0/2, test = never-seen cells of
  the clean half). A subclass of BufferALS ("Tracked") is identical for the declared rules (same RNG consumption) and
  also records each retained record's admission index. It reproduces the committed fixture JSON on main to all digits
  (random -0.126, oracle +0.506, keep_worst -0.182, residual_reservoir +0.023).
- Dose-response: extra-noise SD in {0, 0.3, 1, 3} (same normal draws, scaled), arms random, oracle, keep_worst,
  residual_reservoir, fifo, plus two labelled EXPLORATORY arms: lp (learning progress: key = drop in the record's own
  residual over up to its last 3 refits; new records protected until one refit; arrivals enter with key ~0) and
  keep_best (evict the worst-fitting record). 4 seeds x 4 SD x 7 arms. Then 8 more dev seeds (9330004-9330011) for
  random / keep_worst / residual_reservoir at SD 0 and 3 (12 seeds there). Logged per run: AC, fraction of the buffer
  in the corrupted half, mean retained-record age (fraction of stream).
- Recency probe: F3_switch L2 lowrank, B = c/4, seeds 9330000-003, arms random/fifo/keep_worst/residual_reservoir/lp,
  logging retained ages and the fraction of the buffer from the final (scored) episode.
- Re-analysis (step1.py): all OK rows of [redacted]/lm01/dev/margins and dev/margins_f5real on main; self-signal minus
  random AC at equal B per family x B and per rule, bootstrap 95% CI of the median over worlds; dual B'/B ratio;
  |order| vs |doubling B| at c/4.
Commands: python3 dose.py f2|f3 <seeds> [<sds>] <arms> <out.jsonl> (2 workers, 1 BLAS thread); python3 reduce.py;
python3 step1.py. Outputs: work/[redacted]/out/{repro,dose,extra,f3}.jsonl, dose_table.txt, dose_summary.json, step1.json.
Seeds used: 9330000-9330011 (dev range, fixture block) and the committed margins rows; no campaign/sealed seeds.

3. RESULT
(a) The stated anomaly is stale. At the commit it was harvested from (6a48ff937) residual_reservoir scored -0.457 vs
random -0.335. The later ALS convergence-rule change re-ran the fixture; on current main the committed fixture says
residual_reservoir +0.023 BEATS random -0.126, and only keep_worst (-0.182) is below. The freeze-review text still says
"both rules lose to random" and quotes the old +0.91 oracle gap (current: +0.63). Also, the fixture compares medians of
arms over 4 seeds; paired per seed at SD 3 both rules beat random in 3/4 seeds.
Dose-response, paired (arm minus random) AC, median [bootstrap 95% CI], seeds won; buffer fraction in corrupted half:
  residual_reservoir  SD 0: +0.35 [+0.13,+0.58] 10/12, corrupt 0.51 | SD 0.3: +0.38 4/4, 0.60 | SD 1: +0.25 3/4, 0.69
                      SD 3: -0.16 [-0.43,+0.08] 5/12, corrupt 0.79
  keep_worst          SD 0: -0.22 [-0.27,+0.10] 4/12, corrupt 0.51 | SD 0.3: -0.23 0/4, 0.95 | SD 1: -0.02 2/4, 0.97
                      SD 3: +0.07 [-0.33,+0.18] 8/12, corrupt 0.99
  oracle              SD 0: -0.06 1/4 | 0.3: +0.12 4/4 | 1: +0.41 4/4 | 3: +0.66 4/4
  random median AC    SD 0 +0.59 (12 seeds), 0.3 +0.35, 1 -0.03, 3 -0.19 (12 seeds)
  fifo +0.01/+0.13/+0.24/+0.03; lp -0.16/+0.18/-0.16/+0.14; keep_best -0.53/-0.38/+0.07/+0.15 (4 seeds each).
Reading: residual_reservoir shows the predicted noise-retention pattern: a clear win at SD 0 that shrinks and crosses
below random at SD 3 while its corrupted-half share climbs 0.51 -> 0.79 (CI at SD 3 still spans 0). keep_worst is NOT a
noise-dose story: it is already at or below random with no corruption (SD 0, a younger buffer: age 0.41 vs 0.50),
fills its buffer 95-99% with corrupted records from SD 0.3 on, yet is not worse than random at SD 1-3, because at
SD >= 1 random itself is below AC 0 (worse than predicting zero): a floor effect, not a ranking signal. Only the oracle
is well above floor at SD 3. The lp arm as implemented degenerated into a near-FIFO (retained age 0.045 vs FIFO 0.034;
corrupt share 0.60 at SD 3), so it is not evidence for a learning-progress repair.
(b) F3 switch (B = c/4, 4 seeds): AC random -0.36, fifo +0.84, lp +0.76, keep_worst +0.16, residual_reservoir -0.47.
Final-episode share of the buffer: random 0.33 (= its share of the stream), keep_worst 0.50, fifo/lp 1.00; mean age
random 0.50, keep_worst 0.38. keep_worst's F3 win over random is consistent with a partial recency proxy, and a plain
FIFO beats it by ~0.7 AC; residual_reservoir (not the frozen F3 choice) loses to random there.
(c) Committed dev rows (1,056 OK; reproduces the [redacted]'s numbers): self-signal minus random at c/4 +0.074
[+0.055,+0.098], 63% > 0; F2 +0.37 [+0.32,+0.44] (all residual_reservoir); F3 +0.30 [+0.28,+0.32] 97% (all keep_worst);
F4 -0.054 [-0.068,-0.040]; F5 (old scale) keep_worst -0.32 [-0.37,-0.21] 17% > 0 while residual_reservoir +0.04; F5
real-cells rows: residual_reservoir +0.30 at c/4, keep_worst -0.04 (and -0.32 at c). Where the self-signal loses it
is mostly keep_worst. At c/4 median |order effect| 0.167 vs |doubling B| 0.160, order larger in 49% of rows (real-cell
F5: 0.26 vs 0.44, 35%). Dual B'/B at c/4 median 1.19 (F2 1.80, F3 1.57, F4 0.86).
(d) "random" here is Algorithm-R reservoir sampling: content-blind and age-neutral (mean retained age exactly 0.50,
per-segment shares equal stream shares), i.e. distribution matching. It is relevance-blind only when the test
distribution equals the stream distribution; in F3 (test = last episode) it is systematically mis-weighted, and FIFO is
the relevant relevance-free recency control.

4. DID IT RESOLVE THE QUESTION
Partly. Resolved: the harvested anomaly as quoted is stale on current code; the two surprise rules must be separated
(residual_reservoir: noise-retention crossing, consistent with the literature; keep_worst: loses without any
corruption and acts as a partial recency buffer); the SD >= 1 fixture regime is at the performance floor for all
non-oracle arms, so it cannot rank eviction rules; capacity and order are comparable levers at c/4 in the dev rows;
random is distribution matching. Not resolved: 4-12 seeds on one generator give wide CIs (residual_reservoir at SD 3
spans 0); the learning-progress key tested here collapsed to recency, so whether a proper learning-progress or
noise-floor key repairs residual_reservoir at high noise remains open; F4/F5 losses were not probed with new runs.

5. CONSEQUENCES
- Documentation/harness defect ([redacted] / LM01 prereg owners): the freeze-review note ("both self-signal rules lose to
  random", oracle gap +.91) describes the pre-convergence-fix fixture; the current committed fixture says otherwise.
  The fixture also compares per-arm medians over 4 seeds instead of paired differences; and at SD 3 (B = c/4) every
  non-oracle arm is below AC 0, so the fixture validates the oracle but says little about the self-signal rules. A
  lower-noise level (SD 0.3) separates the rules cleanly.
- False premise, partial: "surprise retains noise" is true for residual_reservoir (a clean, modest dose-response), but
  keep_worst's weakness is not noise retention; it is present with homoscedastic noise.
- F3: keep_worst's win over random is partly recency; FIFO dominates. Any F3 claim of "relevance selection" by
  surprise should be read against FIFO, which v0.3.2 already added as a reference arm -- this confirms that choice.
- Controls: calling reservoir-random "relevance-blind" is fine for content, but it is distribution matching; in
  non-stationary worlds it is not a neutral baseline. Programs using it as the blind control (SI, Ergon) should say so.
- "Order is second-order to capacity" does not hold at c/4 in these rows; an Ergon-style null on another consumer should
  not be generalised.
- Designers of learning-progress keys: a naive "residual drop" key with neutral admission becomes a recency buffer;
  it needs an admission test or a noise-floor term to be a genuine alternative.
Who should know: [redacted] (LM01 fixture/review text), whoever owns the engine-wide forgetting-rule primitive, SI and
Ergon control-labelling owners.

6. COST
About 1.5 hours of my time. CPU about 2,430 s (~41 CPU-minutes) of BufferALS fits (216 fits, 2 workers, 1 BLAS thread
each) plus a few seconds of re-analysis; RAM well under 1 GB. Not done: more generators/seeds for the dose curve, a
proper learning-progress/noise-floor key, F4/F5 new runs, retained-age logging across the full F3 dev set, and
committing step 1 (read-only clone).



======== REPORT X018 ========

REPORT -- state injection as a representation-vs-mechanism splitter: where to apply it next

1. WHAT I SET OUT TO TEST

When an evolved organism fails a task, is it because the state the task needs never gets
into the organism (a percept, parse or stored value is missing), or because the organism
has no machinery that would use that state? Hand-filling state at a chosen depth and
re-scoring gives an upper bound that is meant to separate the two. The [redacted] asks which
current engine is the cheapest place to apply this next. Its first-ranked candidate (the
Apollo raw / oracle-state / corrupted-state arms) is marked as awaiting operator
authorisation, so I did not run it. I ran the second-ranked candidate, which is the
cheapest one in the evolution engines: a two-depth injection on the W2_K2 "half-credit
shelf" organisms of the WSE world (two keyed streams; PUT tagA vA, PUT tagB vB, then ASK
each tag). Before reading any lift, I tested the [redacted]'s own precondition for
interpretability: an injection means something only if the organism's downstream
computation depends non-trivially on the state and on the ask.

2. WHAT I DID

Repository clone at origin/main 6ff2b2f8ad035d50aaf21d9f3b60e16c556683f2. Exported with
git archive into work/[redacted]/src: [redacted]/wse (worlds.py, evolve.py, interventions.py,
controls.py), proteus/foundry (vm.py, prng.py), [redacted]/campaign2/c2base.py, and the
committed specimens [redacted]/campaign3/C3-SFE-01/rows.json (final elite manifests). All
code ran from the export, with GIT_* unset.

Specimens: every SHELF-level final elite in C3-SFE-01 rows.json, de-duplicated by manifest:
19 unique organisms (11 "fresh", 8 "shelf" arm). Battery: 64 W2_K2 4-bit episodes, train
family, my own seed and index (episodes_for(W2_K2, 20260928, "train", 2525, 64)). No
held-out family was used. Scoring: per-ask credit, the same VM and evaluator conventions as
the campaign (vm rng seed 5).

Scripts (in work/[redacted]): probe.py (python3 probe.py 64 -> probe_results.json, probe64.log)
and probe2.py (-> probe2_results.json). Arms:
- RAW.
- KEY COUNTERFACTUALS (the mechanism precondition): re-run each ask with the ask's tag
  replaced by the other stream's tag (KEYSWAP) or by an unseen tag (KEYNOVEL). Measure the
  fraction of outputs that change.
- STORE LOCATION: the register or tape cell whose pre-ask value equals the organism's
  answer in at least 95% of episodes (found for 17 of 19 organisms).
- STORE DEPTH, key-blind (OWN_OTHER): once, before the asks, write the value of the stream
  the organism does NOT remember into its own store location. This checks that the
  location is causal.
- STORE DEPTH, harness-keyed (OWN_ORACLE): before each ask, write the asked stream's value
  into the store location. The harness performs the keying here, so this is a counterfeit
  upper bound and is reported as one.
- STORE DEPTH, spare location (SPARE): write the second stream's value into one other
  location (every register and every non-code tape cell, one at a time; 1,705 placements
  in total) and keep the best score.
- STORE DEPTH, keyed two-slot layout (BOTH_KEYED): write tagA, vA, tagB, vB into four spare
  tape cells.
- DECODABILITY (probe2): is each stream's value held in a consistent location before the
  asks (at least 95% of episodes)? Are both tags present anywhere in the state?
- POSITIVE CONTROL of the instrument (probe2): the hand-written keyed reader POS_TABLE
  (controls.py). I erased its second table entry before the asks (a representation lesion
  with the mechanism intact), then re-injected it at store depth, and also injected a
  corrupted value. The mechanism lesion was simulated by making the reader key-blind.

3. RESULT

Instrument positive control (POS_TABLE, 64 episodes, per-ask):
  raw 1.000; second entry erased 0.500; erased + store-depth re-injection 1.000;
  corrupted injection 0.500; intact table + key-blind read 0.578 (chance with 4-bit
  collisions). The two-depth design does discriminate when one side is present.

Shelf organisms (n = 19 unique):
  RAW per-ask reward             0.531-0.586 (mean 0.574; 0.5 plus 4-bit collisions)
  KEYSWAP outputs changed        0.000 in 19/19 organisms
  KEYNOVEL outputs changed       0.000 in 19/19
  both tags present pre-ask      0.000 in 19/19 (at most one tag word; never both)
  second value held consistently 3/19 (fresh [redacted], s10, s11 hold both values in fixed
                                  registers); 16/19 hold one value only
  OWN_OTHER (key-blind store inj) 0.570-0.578; outputs follow the injection in 42-84% of
                                  asks. The location is causal, but the score only flips
                                  which stream is right.
  OWN_ORACLE (harness-keyed)     0.984-1.000 (counterfeit: the harness supplies the keying)
  SPARE (1,705 placements)       0 placements lifted the reward by >= 1/32; best = raw
  BOTH_KEYED (11 organisms with tape) 0.453-0.586; no lift, one organism damaged
Two organisms (fresh [redacted], s11) answer differently on the two asks of an episode (84%), but
by ask POSITION, not by key: their outputs are still key-invariant.
CPU: about 75 s in total.

Plain conclusion: on the W2_K2 shelf the ask-tick computation of every specimen does not
depend on the key at all. No specimen stores both tags. So no injection at store depth can
raise the score unless the harness itself selects by key, and that makes it the
counterfeit "answer into the readout register" case the [redacted] warns about. Where the
second value is present (3/19), nothing uses it. Where it is absent (16/19), injecting it
anywhere is ignored. The failure is on the mechanism side (key binding plus keyed
selection) in every specimen, and in 16/19 the second value is also missing. The upper
bound becomes non-trivial only when both a keyed store and a keyed reader are supplied,
and at that point the organism contributes nothing: it is the hand-written control.

4. DID IT RESOLVE THE QUESTION

Partly. For the W2_K2 shelf the answer is clean and cheap: this is a mechanism ceiling, and
the two-depth decomposition is degenerate there. It is not badly engineered; it is badly
posed for these specimens, because the precondition (downstream computation that depends
non-trivially on the state and the key) fails in 19/19. So the shelf is the cheapest
place to RUN the injection, but it is not an informative place to apply it. The
engine-ranking question stays open. The first-ranked candidate (Apollo) meets the
precondition by construction, because a parse feeds a non-trivial scorer. The committed
fixture (roles/Lexis/handoff/state_injection_fixture.json@9962f6bd4) and the E9 scorer
are present. I did not run it because it awaits the operator's authorisation. The
evolution-engine specimens that would meet the precondition, the two-value organisms
evolved under all-or-nothing credit (campaign 3, experiment 08: held-out episode credit
equal to per-ask credit, 0.44-0.65), are not usable: their manifests are not committed
(rows.json carries summaries only).

5. CONSEQUENCES

- A false premise: the [redacted]'s option (2) assumes the shelf organisms have an "own read
  location" for the second key whose filling could reveal a representation gap. They have
  no key-conditioned read at all, so filling any location either does nothing or, if the
  harness keys it, counterfeits the answer. This is a reproduction and a sharpening of the
  earlier shelf anatomy (one-value memory; no single edit supplies keying), now with a
  causal, state-level test: key-swap changes 0% of outputs.
- New small positive facts: 3/19 shelf specimens already carry BOTH values in fixed
  registers (so the second value was not the whole missing piece for them), and 2/19 use
  an ask-position heuristic. Both are useful to whoever pursues the W2_K2 summit through a
  changed organism or search (the campaign-4 "C4-3" line): the missing primitive is key
  binding plus keyed selection, not value storage.
- Method rule for any engine (worth adopting as a gate): run a key or ask counterfactual
  before any state injection. If outputs are invariant to the query, the injection is
  uninterpretable. The POS_TABLE lesion/re-injection is a ready-made positive control for
  the instrument in WSE.
- A small reproducibility gap: the C3-SFE-08 two-value elites should have their manifests
  committed. They are the only evolved WSE specimens where a state-injection split could
  be informative.
- Who should know: [redacted] (the WSE owner and shelf specimens), the owner of the Apollo
  task (its injection design remains the best-posed candidate and is blocked only on
  authorisation), and the operator (for that authorisation decision).

6. COST

About 1 hour of my own time. About 75 CPU-seconds of computation, one process at a time,
well under 1 GB RAM. I did not run the Apollo arms (not authorised). I did not build a
genome-level splice of a witness READ block into the shelf genomes: with key-invariant
readers and no stored tags, the splice can only succeed together with an injected keyed
store, which is the hand-written control. I did not examine the Ares carrier option
(ranked low value in the [redacted]).



======== REPORT X019 ========

# [redacted] — Does the offspring-outcome distribution deform before fitness moves?

[redacted]

## 1. Question

H-D5-12 (source: `techne/research/evolution-as-learning/FAILURE_LANDSCAPE_IMPLICATIONS.md:22`,
first committed in a6f08ea33 / 111447d9f, 2026-09-03). The question: hold selection constant and follow the
distribution of offspring outcomes around a parent over generations. Does its shape change
while mean fitness stays flat? If it does, that would be an early heredity signal that does not
depend on fitness: history has changed the generator, not just the population.

## 2. Short answer

**Unanswered. No committed Prometheus experiment has measured this. The one experiment the
harvest links to it (Techne E1) measured something different, and it failed before measuring
anything.**

- The idea exists only as a prediction. The source file says "No experiment is proposed
  here" (`FAILURE_LANDSCAPE_IMPLICATIONS.md:3`). It says the signatures are "DERIVED from the motif
  (none of this is measured in S1-[redacted])" (:9-10). It offers the measurement "without commitment"
  (:28-30) and says "None of the above is demonstrated in the recovered sources" (:34).
- E1 is **not** a test of H-D5-12, even in principle. Four reasons, all visible in the code
  and prereg (§4 below):
  - it compares two *different* histories at a *matched* phenotype;
  - it does not follow one lineage through time;
  - it cycles four targets every generation instead of holding selection constant;
  - it records only the final population, never a fitness or kernel time series.
  E1 also explicitly withdrew "same mean, different shape" as its criterion
  (`E1_PREREGISTRATION_v2.md:20-22, 30-31`).
- E1 returned `INSUFFICIENT_MATCHES` with 0 pairs in every arm
  (`E1_RESULT_INSTRUMENT_FAILURE.md:9-18`; `e1_results.json`). Its own authors classify this as
  "NOT a null, NOT evidence for K2" (:21) and "K2 ..... UNCHANGED" (:92). E1 therefore carries
  **no information about H-D5-12 in either direction**.
- The closest evidence in the repo is **external literature** that Elenchus recovered, not a
  Prometheus measurement. Parter et al. 2008 Fig 9D: "Facilitated variation rapidly decays when
  goal becomes constant over time", starting from a population "that had perfect fitness for the
  goal G1" (`elenchus/kashtan-alon-mvg/LOCAL_ACCESSIBILITY_REVIEW.md:114-121`). That is a
  neighbourhood property changing over generations in a population that starts at maximum
  fitness. It fits the *direction* of H-D5-12, but it does not answer the question:
  - The recovered text does not show fitness staying flat over the decay window. I did not
    verify this, so I do not claim it.
  - The quantity is a scalar FV summary, not the shape of an offspring distribution.
  - The effect is memory *loss* under a constant environment, not history being written in.
  - Elenchus's reading of it is "manipulates the CAUSE, measures the MEDIATOR"
    (`CAUSAL_INTERVENTION_MAP.md:56-62`).

- **The closest executed Prometheus test did not reach the question.** Herakles HC-T01
  measured a neighbourhood detector over time. Its preregistration had a precedence test (T2)
  in exactly the H-D5-12 form: the detector counts as a precursor only inside a window where
  fitness slope is indistinguishable from zero. T2 was **"NOT ATTEMPTED"**
  (`herakles/specimens/spec-toussaint-exploration/HC_T01_EXECUTION_REVIEW_PACKET.txt:188-205`):
  "the on-arm fitness slope through that whole window runs +0.02 to +0.13 per checkpoint. The
  only plateaus are late, after the detector signal has already peaked ... The one-checkpoint
  lead is NOT reported as precedence." Its overall verdict was later downgraded to
  `HC_T01_WEAK_SIGNAL_ONLY` (`HC_T01_CORRECTION_2026-09-03.md:11,19`). A zero-compute
  reanalysis of HC-T01 returned `RA1_INDETERMINATE`. It also found reverse precedence:
  accessibility measured *after* the outcome window tracks the outcome better
  (`herakles/specimens/spec-toussaint-exploration/reanalysis/conditional_accessibility_2026-09-03/REVIEW_PACKET.txt`
  ~:221-239, per the delegated sweep; I did not open it). This is a failed-to-reach result. It is
  not evidence against H-D5-12.
- **Other seats also record this as open.** The Herakles cross-seat meta-analysis:
  "OPEN ... No work in the lineage has a TRAJECTORY OF NEIGHBOURHOOD CONTENT ... whether that
  entry preceded the acquisition advantage. ... Three seats, not coordinating, converged on the
  same missing measurement" (`CROSS_SEAT_META_ANALYSIS_2026-09-04.txt:218-224`).
- **Other executed neighbourhood measurements are cross-sectional or compare categories, with
  no time axis at flat fitness.** These are Ergon gen1b (mutational-redundancy Jaccard on
  duplicate pairs), [redacted]'s forensics (first-generation vs evolved replicators, robustness
  unchanged), [redacted]'s npe-arc3 accessibility, and [redacted] cw01 P-J06 (standing variation present
  "before selection asks for" it; witness-seeded, 1/2 seeds, NOT PROMOTED). Pointers for these
  come from the delegated sweep and appear in [redacted] C12. I did not open them myself.

## 3. Method

1. Read the source (`FAILURE_LANDSCAPE_IMPLICATIONS.md`, 39 lines) and the whole E1 chain:
   the prereg, `e1_experiment.py`, `e1_diagnostic_matching.py`, `e1_results.json`,
   `E1_RESULT_INSTRUMENT_FAILURE.md` and `EXTERNAL_REVIEW_PACKET.txt`.
2. Checked history: `rogit log --all -- techne/research/evolution-as-learning/`. The only
   commits are a6f08ea33 (pivot), e9fcabfe0 (prereg v2 frozen) and 468a1f9ba (E1 run). There is
   no v3 and no rerun. The harvest's citation commit 111447d9f has the same timestamp and
   subject as a6f08ea33, so it is apparently a rewritten copy of the same commit.
3. Searched the whole repo for rerun, v3, K2 and longitudinal offspring-distribution
   measurements, including a wide sweep over Ergon, Herakles, Elenchus, [redacted], [redacted],
   [redacted] and SerendipityFoundry.
4. Read the E1 code line by line to decide whether E1 *could* have answered H-D5-12.

## 4. Evidence

| # | claim | pointer |
|---|---|---|
| E-1 | The source only predicts the observable; it is not measured | `FAILURE_LANDSCAPE_IMPLICATIONS.md:3, 9-10, 18, 28-30, 34` |
| E-2 | The source flags its own weakness: the associative-memory reading is ANALOGICAL_ONLY, and discreteness (K5) is unresolved | same file `:35-39` |
| E-3 | E1's estimand is cross-history exchangeability at a matched P*, not within-lineage change over time | `E1_PREREGISTRATION_v2.md:24-28, 37-43` |
| E-4 | E1 withdrew "same mean, different shape" as its success criterion; it is kept only as a secondary signature | `E1_PREREGISTRATION_v2.md:20-22, 30-31` |
| E-5 | E1 selection is not constant: `S = targets[g % len(targets)]`, with 4 targets cycled every generation | `e1_experiment.py:70` @468a1f9ba; `:172` (`range(4)`) |
| E-6 | `evolve()` "Returns the final population"; there is no per-generation fitness or kernel log | `e1_experiment.py:59-78` |
| E-7 | All 8 arms returned n_pairs = 0, so nothing was interpreted | `E1_RESULT_INSTRUMENT_FAILURE.md:9-22`; `e1_results.json` |
| E-8 | Cause 1: absolute tolerance 0.2 against phenotype scale ~17.5; cause 2: disjoint target supports, so there is no common support (72× ratio) | `E1_RESULT_INSTRUMENT_FAILURE.md:28-38, 40-75` |
| E-9 | K2 is unchanged; E2 is not licensed; the v3 plan is proposed but not frozen and not run | `E1_RESULT_INSTRUMENT_FAILURE.md:89-110`; `EXTERNAL_REVIEW_PACKET.txt:110-111` |
| E-10 | Herakles independently records E1 as an empty conditioning set and an instrument failure, not a negative result | `herakles/HERAKLES_HISTORICAL_COLLIDER_V0/CROSS_SEAT_META_ANALYSIS_2026-09-04.txt:61-111` |
| E-11 | Literature analogue: FV decays over generations under a constant goal, starting from perfect fitness | `elenchus/kashtan-alon-mvg/LOCAL_ACCESSIBILITY_REVIEW.md:114-121`; `CAUSAL_INTERVENTION_MAP.md:56-62`; `LONGITUDINALITY_ADJUDICATION.md:21-32` |

### Two further E1 code observations (my reading; no code was run)

These do not change the conclusion, because E1 is uninterpretable anyway. They matter for any
v3.

- **C0 is not "within one treatment."** The prereg describes C0 as "Pairs drawn WITHIN one
  treatment" (`E1_PREREGISTRATION_v2.md:120`). The code instead evolves a second, independent
  population: `run_arm("C0", 11, 33, "A", "A")` (`e1_experiment.py:227`). `run_arm` calls
  `make_targets` twice on one RNG (`:190-191`), and each call draws random block signs (`:176`, `:180`).
  So the "A" targets of the two populations differ in sign pattern. C1 "same targets"
  (`:232`) has the same issue. C0 and C1 therefore compare *different* histories that share only
  the target support.
- **The diagnostic count is inflated.** `e1_diagnostic_matching.py` counts "pairs <= TAU" over
  the full symmetric distance matrix, so each unordered pair is counted twice. The reported "22"
  within-history pairs (`E1_RESULT_INSTRUMENT_FAILURE.md:35`) would then be about 11 distinct
  pairs. This does not affect the verdict, since both 11 and 22 are below 30.

## 5. Result

| item | status |
|---|---|
| H-D5-12 (does the offspring distribution deform while or before fitness moves?) | **OPEN, never measured** in this repo |
| Does E1 bear on it? | **No.** Different estimand, and an instrument failure with zero data |
| K2 | unchanged (per Techne's own ledger) |
| Closest executed attempt | Herakles HC-T01 T2 precedence test: **not attempted**, because there was no flat-fitness window while the signal emerged |
| Nearest evidence | a published scalar FV-decay result (Parter 2008 Fig 9D), recovered by Elenchus. It is analogous, and it does not settle the question |

The harvest line "K2 is still open" is correct, but it frames the question too narrowly.
Even a successful E1 v3 would answer a *cross-history, matched-phenotype* question. The
fitness-free, *longitudinal* signal H-D5-12 asks about would still need its own design.

## 6. Proposed computation (`out/analysis.py`, NOT RUN)

The script uses the same Watson Eq.1 substrate and constants as `e1_experiment.py@468a1f9ba`
(:31-56), with **one constant selection vector**. Every 50 generations it re-samples the offspring
kernel of the top-40 lineage representatives. It picks a fitness plateau, and matches the first
and last plateau representatives on P* using a *scale-relative* tolerance (half the
within-population median NN distance). It also reports the number of matched pairs as a
positivity gate before any test. It then compares the offspring displacement distributions by
energy-distance permutation, against a same-generation floor, in two arms:

- B-mutable: the generator can store history;
- B-frozen control: MUT_B = 0.

**Decision rule, fixed in the file before any output exists:**

- **YES:** positivity holds (≥ 30 pairs), the cross-time distance exceeds the floor at p < 0.01
  in ≥ 8/10 B-mutable seeds, and in ≤ 2/10 B-frozen seeds.
- **NO:** positivity holds and the B-mutable criterion fails in ≥ 8/10 seeds.
- **INDETERMINATE:** everything else. If positivity fails, the script reports it and stops.

I do not predict its output. The onset-lag variant ("before fitness moves": kernel onset
earlier than mean-fitness onset after a target switch) is described in the file but not
implemented.

## 7. Limits

- The repo search is broad but not exhaustive (large JSONL, HTML and PDF-extract corpora).
  A measurement stored under unexpected vocabulary could have been missed.
- The E1 code observations in §4 come from reading the code, not running it.
- The Parter 2008 evidence is second-hand, through Elenchus's quotes. I did not verify whether
  fitness stayed flat during the Fig 9D decay.
- "Fixed parent" in H-D5-12 is ambiguous. A literally fixed genotype has a fixed kernel, so the
  only coherent reading is a lineage representative over time. My proposal adopts that reading.
- Confound for any rerun: on a fitness plateau, P* can drift neutrally, and the kernel then
  changes because the parent changed, not because the generator did. `analysis.py` addresses
  this by matching on P* and adding the B-frozen arm, but only partially.

## 8. What would change this conclusion

- A committed, executed experiment that follows a lineage's offspring distribution under
  constant selection, with a positivity check and a no-memory control, would move the status
  from OPEN to YES or NO. This could be `analysis.py` or an E1 v3 extended with a longitudinal
  arm.
- A committed Prometheus result I missed that measures kernel shape against generations while
  fitness is flat.
- An HC-T01 rerun with a constant-selection plateau *during* signal emergence, so that its
  preregistered T2 could actually be evaluated. That is the most direct existing instrument for
  H-D5-12.
- Primary-source confirmation that fitness stayed at maximum throughout Parter 2008 Fig 9D.
  That would upgrade the literature analogue to "an external existence proof of neighbourhood
  change at flat fitness (memory loss direction)". It would still not be a Prometheus result.



======== REPORT X020 ========

# REPORT -- Is the engine ecology still a selection monoculture?

## 1. WHAT I SET OUT TO TEST

A June 2026 audit of the program found two problems with one shared root. Its
mechanisms looked diverse (NSGA-III, binary gates, tier ladders, bandits,
kernel claims), but all of them served one principle: "promote what passes the
gate". The gate at the center also trusted callers. The kernel's PROMOTE step
checked only that a non-BLOCK verdict object existed. An adapter built a CLEAR
verdict from a caller-supplied survival_evidence dict and never re-ran the
tests. Since the September reset, the program has about ten engines and
engine-like seats. A later landscape survey called their shared discipline
(preregistration, freeze, gate, cheat control) "healthy convergence", but
nobody re-audited their selection principles.

I asked three things of the current engines:
- (a) Does the trust-boundary defect recur? That is, does any gate turn a
  caller-asserted outcome into a verdict without recomputing it?
- (b) Is the inner selection rule the same everywhere (an exogenous "pass a
  test to reproduce")?
- (c) Is the program-level objective still "promote what passes the gate", or
  are the shared prereg/gate/control steps now a verification layer that sits
  under different objectives?

## 2. WHAT I DID

This was a read-only code and document audit. I ran no experiments and wrote
no code beyond git/grep one-liners.

Sources:
- Repository: [redacted] at origin/main 6ff2b2f8a, plus
  these branches:
  - origin/[redacted]/multiday-campaign-2026-09-26 @ ee7a7d954
  - origin/[redacted]/arc3-2026-09-28 @ 7587a93e1
  - origin/[redacted]/attribution-arc-2026-09-28 @ 05ab73917
  - the [redacted] branches, which are ancestors of main
- Baselines:
  - roles/[redacted]/AUDIT_20260622_program_stall_map_of_disagreement.md @ 3e13f736c
  - roles/[redacted]/ENGINE_LANDSCAPE_2026-09-25.md @ 95fff9111

Engines surveyed (10): SFE, NPE (primordial/ and roles/[redacted]/campaigns), BEE
(prometheus/toolbox, prometheus/z80atlas, the multiday campaign), AGE ([redacted]/),
CWE (prometheus/[redacted]), WTP ([redacted]/), PTE (prometheus/[redacted]), [redacted]
(roles/[redacted]/engine plus arc3), [redacted] ([redacted]/*), and the [redacted]
expedition code (roles/[redacted]). [redacted] has docs only, so I only noted it.

The same four-question rubric was applied to every engine:
1. The inner selection rule.
2. Where verdicts are computed, and whether they are recomputed from rows,
   replayed, or trusted as labels.
3. The form of the outputs.
4. The program-level objective.

Three read-only sub-surveys did the first pass. I re-checked every load-bearing
defect claim myself against source:
- primordial/core/contract.py board_eligible
- primordial/bus/bus.py receipt()
- primordial/score/progress.py
- SerendipityFoundry/SerendipityFoundryEngine/sfe/runtime.py record_observation (~2361-2450)
- the multiday-campaign md_analysis.py "holds" vs "instrument_ok"
- [redacted]/wtp/campaign.py replay_ok
- roles/[redacted]/engine/a16.py:490
- prometheus/[redacted]/campaign.py:560-572
- atlas/policy.py

Legacy check:
- git log on sigma_kernel/sigma_kernel.py and
  prometheus_math/discovery_promotion.py.
- git grep for importers of either file inside the post-reset engine
  directories.

Vocabulary proxy: I counted commit subjects on all branches, by period, that
contain "promot" or null/kill/falsif/sham/cheat/control.

## 3. RESULT

### (a) Trust boundary

Legacy gate:
- The June defect was never fixed. SigmaKernel.PROMOTE (sigma_kernel.py:822)
  still checks only that a verdict exists and is not BLOCK.
  discovery_promotion.py still turns caller-asserted survival_evidence into a
  CLEAR verdict. Both were last touched 2026-05-08.
- It is dormant. None of the 10 post-reset engines imports either module. The
  only hits in engine directories are two markdown mentions.

Post-reset engines: 8 of 10 compute their scientific verdicts from per-run rows
or re-runs:
- CWE: the broker re-runs sealed holdout worlds in a subprocess before
  scoring.
- [redacted]: an independent worker re-ran the whole battery and matched the
  fixture value by value.
- BEE: a 3% exact-equality replay.
- [redacted]: the forensic replay has to reproduce the recorded run exactly
  before the run is admitted.
- [redacted] z80atlas: REPLAY_MATCH is required.
- AGE: digest and spot-check replay tools.
- WTP and PTE: fresh-seed re-runs and held-out re-tests.
- [redacted]: the tribunal re-scores on fresh tasks.

Two engines keep a caller-trust path:
- SFE record_observation. The caller supplies FALSIFIED/SURVIVED and only the
  spelling is checked. A work_id proves that a completed work item exists, not
  that it supports the outcome. Without a work_id the outcome is stored as
  CLIENT_ASSERTED and still moves the hypothesis state. This is a stated
  design choice ("the engine stores the conclusion the experimenter reached").
  The evidence class is always recorded, and fail-closed enforcement is
  opt-in (require_attestation). So the audit's defect is present by design,
  labelled, and closable with one flag.
- NPE board_eligible (contract.py). It accepts a self-written PASS/KILL
  status, any non-empty controls.cheat string (the string is not checked to
  say the control passed), and any non-empty rows path (the path is not
  checked to exist). Board credit from it has been off since round 2
  (PM_BOARD_SCORING). Refutation credit in score/progress.py still uses it,
  but its instruments axis does read the row files.

Softer stage-to-stage label trust (a later stage trusts an earlier stage's
stored label or boolean; the verdict is never minted from a caller):
- [redacted]: run_s3s4.py reads stored PASS gate files, and a16.py:490
  hardcodes donor_adjudication_valid = True.
- [redacted]: a PREREG attribution_tests.passed boolean and a preflight
  verdict == "PASS".
- [redacted]: gate_v01.json PASS.
- AGE: GPU parity rests on the pod's self-reported PASS, though independent
  replay tools exist.
- BEE:
  - md_analysis.py sets "holds" without conditioning on instrument_ok; the two
    are printed side by side.
  - The scheduler re-uses a stored score on resume.
- WTP: replay_ok is computed and recorded but never enters the REPLICATED
  state.

### (b) Inner selection rule (10 engines)

Exogenous test-passing ("pass a test to reproduce"):
- PTE: truncation GA.
- [redacted]: gold-match search and a lower95 > 0 gate.
- [redacted] sandbox: hidden-target reward and colony truncation.

Mixed:
- NPE: QD elites alongside endogenous Z80 ALLOC/BIRTH.
- BEE: endogenous copying, but the copy resource is paid for correct task
  answers in the coupling physics.
- WTP: elite GA with about 20% novelty; WTP-03 parents are the worlds that
  passed admission gates.
- [redacted]: endogenous copying, an optional competence-gated pressure, and an
  outer "world promotion score" in rie.

Endogenous only:
- AGE: no score; a GA loop is explicitly rejected.

No selection:
- SFE: an instrument (its reference driver is a onemax (mu+lambda)).
- CWE: parameter worlds; the selection is over laws, by attack/survive/freeze.

So 3 of 10 are pure exogenous gates, and 7 of 10 contain a
test-passing-selection component. Mechanism diversity is real, but it leans
toward test-passing selection. Only AGE (and [redacted]'s census and envgate
lines) keep selection fully endogenous.

### (c) Program-level objective

- The central scorer has changed. atlas/policy.py (policy/2) states: "The
  learning target is NOT 'which experiments succeed'." Its weights have no
  term that rewards success, and it lets a confound-removing clean null
  outrank a novel demo.
- Promotion language has dropped out of commit subjects:
  - Apr-Jun: 133 of 2848 subjects contain "promot" (4.7%).
  - Jul-Aug: 3 of 1175.
  - Sep 10-30: 17 of 4796 (0.35%). Most of these are allocation or schema
    promotions, not claim promotions.
- Null/kill/control language roughly doubled in rate: 9.2% (Apr-Jun) against
  11.0% (Sep).
- Several engines have descriptive first-class products: the AGE observatory
  deliberately applies no labels; there are the [redacted] copier census, the
  [redacted] census and label-vs-capability audit, the WTP phase and niche maps,
  and the BEE "descriptive, not tested" block.
- One structural residue remains, which I call a "gate-then-describe" funnel.
  - PTE maps phase boundaries only around specimens that first pass SIGNAL
    (campaign.py:562-572).
  - CWE's product is a law that survived attack.
  - WTP-03 breeds from worlds that passed admission gates.

  In these engines, description is conditioned on a gate pass, so what gets
  described is still filtered by what passed.

### Plain conclusion

The June monoculture does not recur in its load-bearing form.
- Every post-reset scientific verdict path I checked is either recomputed from
  rows or replayed, or is explicitly labelled as client-asserted (SFE).
- The program-level objective is no longer "promote what passes".

What converged is the verification discipline, not the selection principle.
Treating those two as the same thing is the weak part of the question.

Three genuine residues remain:
1. The legacy gate defect is unfixed, though dormant.
2. There are two caller-trust paths (SFE by design and opt-in; NPE's
   board_eligible) and about six label-trust seams between stages.
3. Inner selection and descriptive scope still lean toward exogenous
   test-passing. Seven of ten engines have such a component, and three engines
   describe only what first passed a gate.

## 4. DID IT RESOLVE THE QUESTION

Partly.
- It resolves the trust-boundary half: the defect is identified per engine
  and verified in source.
- It gives a defensible classification of inner selection and of the
  program-level objective.

It does not resolve whether the shared discipline itself narrows what the
ecology can discover. That is an empirical question and a code read cannot
answer it. It would need, for example, the share of Atlas proposals or results
that exist only because a gate passed, against ungated exploratory output, or
a comparison of discovery yield between the gated and ungated lines. The
engine-level classification also rests on a medium-depth read of about ten
codebases, not a line-by-line audit. Unread parts include the SFE client,
NPE's soup/ worlds, [redacted]/lm01/launch_gate.py and
prometheus/[redacted]/launch.py.

## 5. CONSEQUENCES

Harness and instrument defects (small, concrete):
1. The legacy kernel PROMOTE and the discovery_promotion adapter still trust
   caller-asserted survival. The June recommendation (a re-execute-battery
   gate) was never applied. Either retire them or fix them before anything
   post-reset imports them. Owner: whoever owns sigma_kernel /
   prometheus_math ([redacted] raised it).
2. In NPE board_eligible, the cheat check is "any non-empty string" and the
   rows check is "any non-empty path". It should require that the cheat
   control passed and that the rows file exists and backs the status. It
   still feeds refutation credit. Owner: [redacted].
3. SFE should default to require_attestation=true for science worlds, or
   state in each world's charter why CLIENT_ASSERTED is acceptable. Owner:
   Daedalus.
4. BEE md_analysis should set holds = holds AND instrument_ok. WTP should let
   replay_ok gate REPLICATED. [redacted] a16.py:490 should compute
   donor_adjudication_valid instead of hardcoding True. All three are
   one-line fixes. Owners: [redacted], [redacted], [redacted].

False premise, or at least a conflation: "monoculture at the level of
discipline" mixes epistemic verification (which should be uniform) with
selection principle and objective (where diversity matters). The earlier
landscape verdict of "healthy convergence in discipline" is consistent with
what I found. But no re-audit had been done, and one was warranted: the
residues above are real.

Something seats could change: the remaining monoculture risk is at the
"gate-then-describe" funnel (PTE, CWE, WTP-03) and in the inner selection rules
(7 of 10 engines have a test-passing component). Atlas could track, per engine,
the share of described territory that was reached without passing a gate, which
would make this measurable. The operator (convergence concern of 2026-09-25)
and Atlas should know.

No new positive result and no reproduction of a known number. This is a
re-audit that mostly clears the post-reset ecology of the June finding and
leaves a short list of residues.

## 6. COST

About 1 hour of wall time, including three parallel read-only code surveys
and my own verification of each cited defect line. CPU: negligible (git and
grep only; well under 1 CPU-minute). Nothing was executed from the repository
and no database was queried.

Not done:
- the empirical measurement of gated vs ungated discovery share
- a deep read of the SFE client, NPE soup/ worlds and the launch gates
- [redacted] adjudication, which exists only as prose

