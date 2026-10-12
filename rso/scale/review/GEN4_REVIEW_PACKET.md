+============================================================================+
| OBSERVATORY GENERATION 4 -- REVIEW PACKET                                  |
| Aether: spatial causal ancestry vs recoverable content; completeness       |
| contract; control falsifiability; four-generation cost comparison          |
| Author: Palamedes (Lead RSO Engineer, coordinator), harry1/M4,             |
|         claude-opus-5-5, instance harry1-679179c6                          |
| Date:   2026-10-12 (campaign C-018, opened 09:01Z, closed ~20:00Z)         |
| For:    the operator (HITL); external reviewers                            |
| Status: CLOSED. Self-contained: no repository access needed.               |
+============================================================================+

0. SUMMARY
----------
Verdict on Aether (recoil + exchange law, RX; the primary question):
  CAUSAL_PROPAGATION_WITHOUT_RECOVERABLE_CONTENT.
  Interventional causal ancestry reaches radius 2-6 in 8 of 13 evaluable
  native units, while Aether's own held-out decoder recovers essentially
  no planted content at those radii (excess over chance 0.0135; 0.0099 on
  the confirmed units' own seeds; margin 0.05). Excesses below ~0.05-0.10
  are not excluded.
Comparison law (aeth01.v1): ANCESTRY_UNEVALUABLE (0 of 16 units could be
  tested) = "not evaluated", not a negative.
P4 (transformation of several inputs): UNSUPPORTED natively, recorded, not
  constructed. TEST-4 (Aether's own REACH01 negative) is preserved; nothing
  here reclassifies it.
Two reusable Observatory improvements landed first: a shared experiment-
  completeness contract, and a falsifiability requirement for every
  claim-critical control. The Q3 challenge and re-check were genuine Fable
  5.1 throughout (model continuity verified from the session logs).

1. WHAT WAS BUILT (in order; each committed before the next)
-------------------------------------------------------------
- Seat state reconciled (a fresh coordinator can resume from git alone).
- Completeness contract (rso/completeness): a sealed experiment manifest
  (shards, seeds, per-arm counts, hashes, optional preregistered early
  stop) and a verifier an analyzer must call before any verdict.
  Known-answer: the six committed Z80 (Gen 3) shards verify COMPLETE and
  reproduce that frozen verdict exactly; with five shards -> INCOMPLETE,
  no verdict (the Gen-3 integration had found the frozen analyzer printed
  a qualified verdict on five). Duplicated, substituted, altered, foreign
  and wrong-seed shards are refused. 40 tests; 12 of 13 mutants killed
  (1 equivalent). Gen 3's frozen result is unchanged.
- Falsifiability requirement (rso/qualify): a six-item checklist every
  preregistration must carry for each claim-critical control (alternative;
  pass / fail observation; impossible by construction?; privileged access?;
  does failure discriminate?; a registered near-miss), plus executable
  checks, each tested on a miniature of a real past defect: a derived-field
  analyzer (D1), a self-relative frozen arm (Gen 2), baselines with no
  output for a class (Gen 3), a constant that passes (Gen 3), a recipe
  lookup table (Gen 3). 14 tests; 3 mutants killed.
- Aether selection / demand gate (read-only): P1 spatial influence supported
  only as a sanity guard (the native kernel is local, so the light-cone
  check cannot fail natively); P2 ancestry and P3 content supported and
  separable on constructed fixtures (a chain that carries structure but no
  content; a pre-seeded field that decodes with no causal pathway); P4
  unsupported (the default law replaces the target byte).
- Adapter + frozen assay (Aether's own physics, attribution and decoder
  consumed, not re-implemented); Q3 challenge; ONE repair round (v1.1.0);
  short Q3 re-check; confirmatory run (64 units, 6 shards).
- Generation 5 candidate contract (not opened): Crius (artifact-mediated
  reuse: does a stored callable procedure causally account for later
  capability?); runner-up Ananke two-part composition.

2. THE QUESTION AND WHY IT MATTERS
-----------------------------------
"Can the Observatory separate interventional causal ancestry (clamping the
claimed ancestor removes the descendants; clamping a matched, genuinely
diverging non-ancestor does not) from recoverable source content (held-out
decoding), and refuse to count either as the other?" A causal tree is not
an information-processing circuit; the earlier engines never forced the
distinction because their information sat inside organisms.

3. DESIGN AS EXECUTED (confirmatory)
-------------------------------------
- 48 RX + 16 V1 native paired units, 128^2, warm 300, horizon 400; seeds
  frozen before any outcome; one block burned after a disclosed pre-freeze
  incident (a guard test executed 4 then-confirmatory units; deleted unread).
- Per unit: Aether's attribution tree; a lockstep recorder for CONTROL /
  IMPULSE / CUT_B / CUT_N; Aether's eight content branches.
- Analysis order: freeze check -> completeness -> records (duplicates,
  per-unit warm-snapshot binding, per-unit tree replay, tree invariants,
  sampled full replay) -> qualification -> decoder null -> evaluable
  minimum (8) -> P2 x P3.
- Release required a coordinator-committed RELEASE.json naming the frozen
  design and FROZEN.json blob/commit; a flag alone is refused.

4. RESULTS (exact)
-------------------
  RX  evaluable 13 of 48 (CONFIRMED 8, NOT_INTERVENTIONAL 5); NO_CUT 24,
      CONTROL_VACUOUS 8, INSUFFICIENT 3, NONSPECIFIC 0, MULTI_SOURCE 0.
      All 8 CONFIRMED at r_int >= 2 (r 2 x4, 4 x1, 6 x3); reach band 6.
      Content excess 0.0135 (registered), 0.0099 (confirmed seeds), null
      0.0002. Attribution agreement 0.75 (MIXED).
      P2 held under BOTH the repaired need (3) and the original need (5).
  V1  0 of 16 evaluable (NO_CUT 13, INSUFFICIENT 3) -> UNEVALUABLE.
  Evidence: 64 rows, 64 distinct, 64 snapshot-bound, 64 trees replayed,
      6 fully replayed. Integrator: one non-sampled CONFIRMED unit
      re-executed natively -> bit-identical (clamp arrays included); one
      shard removed -> INCOMPLETE in 0.3 s, nothing verdict-bearing printed.
  Cost: shards ~1.6 core-h (RX ~1,070 s, V1 ~600 s each), analysis
      1,833 CPU-s, peak 344 MB; harry1 CPU only; $0.

5. INCIDENTS AND WHAT THEY VALIDATED
-------------------------------------
- Pre-freeze run of 4 confirmatory units by a guard test: block burned,
  guard hardened to require RELEASE.json. Rules were committed earlier.
- A harness usage limit stopped the repair-round session mid-work; the
  same seat resumed from its pushed commit (lease taken over, not doubled).
- The challenge found the frozen v1.0.0 analyzer would have printed:
    a positive ANCESTRY_WITH_CONTENT for a re-sealed 5-shard design (B6);
    COMPLETE with 12 CONFIRMED and content 0.112 for 64 rows of 5 distinct
      units (B5; genuine 0.012);
    CONFIRMED / NONSPECIFIC from edited tree fields (B1);
    a NONSPECIFIC class decided by WHICH non-ancestor the rule picked (B8);
    a verdict for a population with nothing evaluable (B2).
  All closed in the repair round; the re-check found no new hole.
  Detection cost: ~2.8 h of Q3 reviewer time, ~1.5 core-h of CPU, before
  any confirmatory unit existed. This is the Gen-4 measure of the
  Observatory's main economic benefit.

6. WHAT THIS ESTABLISHES AND WHAT IT DOES NOT
----------------------------------------------
Does: on Aether's RX law at this scale and impulse, interventional ancestry
  at radius >= 2 exists in a minority of native units, and the planted
  content is not recoverable there by Aether's decoder above ~0.05-0.10.
  The instrument separates ancestry from content on constructed fixtures
  and refuses each counterfeit it was challenged with.
Does NOT:
  - per-site "this descendant carries the content" (P2 and P3 share radii,
    not origins);
  - the class of the 58 units whose clamp arrays were not replayed, as
    proof (they rest on producer bytes bound by snapshot, tree replay and
    invariants; a careful rewrite of one array could flip a class);
  - that NONSPECIFIC means damage spreading (the repaired non-ancestor rule
    sits on the ancestor's wavefront; 5 of 8 CONFIRMED units' control was
    moved off an earlier-diverging site);
  - anything about V1 ancestry (not evaluated), P4, the GPU kernel, or
    TEST-4's 512^2 scale;
  - any claim about intelligence, circuits or computation in Aether.
The repaired denominator and non-ancestor window were chosen after seeing
challenge data; both P2 readings are printed and agree here.

7. FOUR-GENERATION COMPARISON (no normalisation of difficulty)
---------------------------------------------------------------
                 Gen1 Ares   Gen2 Ensorain  Gen3 Z80     Gen4 Aether
  question       retained    revision at    who wrote    ancestry vs
                 bit         a law switch   the bytes    content
  bespoke lines  ~1,800      662            707          881 (687 pre-
                                                         repair)
  shared modified n/a        0              0            0
  selection      --          retention ->   heredity ->  P4 dropped,
  re-scoped?                 revision       attribution  P1 = guard
  open->result   6.2 h       4.0 h          7.1 h        10.3 h (incl.
                                                         stalls)
  Q3 time        ~1.7 h      ~1.6 h         ~2.0 h       ~2.8 h
  challenges /   2 / 2       2 / 2          2 / 1+3      2 / 6 (T040),
  real defects                                           0 new (T042)
  repair rounds  1           1              1            1
  CPU            26 CPU-min  ~0.9 core-h    ~4.6 core-h  ~5.0 core-h
  waiting share  69%         49%            24%          21%
  Q3 provenance  Fable       Fable          T042 mixed   Fable, verified
                                            (fallback)   continuous
  result         QUALIFIED;  ref REVISES    ATTRIBUTION  RX CAUSAL_
                 subjects    (history-dep); _QUALIFIED   PROPAGATION_
                 NEGATIVE    1/8 searched   273/274      WITHOUT_CONTENT
Reading: building cost has flattened at ~700-900 lines with zero shared
modifications; qualification cost has NOT fallen and grew with the
richness of the evidence chain; every challenge still found real defects
in a decision rule the builder believed sound; the selection gate changed
or narrowed the operator's question in all three new engines; coordination
waiting fell from 69% to ~21%.

8. DECISION / RECOMMENDATION
-----------------------------
- Accept the Gen-4 result as scoped in s6.
- Generation 5 (Crius) needs a separate authority AND a named engine
  steward: the Crius seat is CLOSED with no resume pointer.
- Harden before Gen 5: replay the clamp-equivalent arrays of EVERY unit when
  cost allows (Aether: ~65 s/unit, affordable at 64 units); the registry now
  records which inferences are qualified where.
- Still pending from earlier: the Astra and Fable external reviews of the
  C-013 packets have not been performed.

9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------
Q1 Is "causal propagation without recoverable content" a finding about
   Aether, or about Aether's decoder at this training size?
Q2 The repaired non-ancestor rule and denominator were chosen after the
   challenge data. Does printing both readings suffice, or should such a
   repair force a fresh confirmatory seed block AND an independent design?
Q3 Qualification cost is flat-to-rising across four engines. Is that a
   failure of the registry, or the correct price of richer evidence?
Q4 A selection gate re-scoped the question three times. Are we learning
   about the engines, or about what our instruments can ask?
Q5 What result in Generation 5 would show the Observatory is measuring
   the wrong thing?

10. ARTIFACTS (repository paths)
---------------------------------
rso/aether/{SELECTION.md, PREREGISTRATION.md (v1.1.0), RESULT.md,
  ONBOARDING.md, RELEASE.json, challenge/REPORT.md, challenge/R2/REPORT.md};
rso/completeness/; rso/qualify/; rso/registry/ (15 entries);
rso/gen5/CANDIDATE_CONTRACT.md; ops/campaigns/C-018/CLOSEOUT.md;
earlier generations: rso/witness/RESULT.md, rso/ensorain/RESULT.md,
rso/z80/RESULT.md.

+============================================================================+
| "The Observatory is measuring the wrong thing" and "stop" remain           |
| first-class answers.                                                       |
+============================================================================+
