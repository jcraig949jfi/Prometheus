+==============================================================================+
|  CAUSAL LINEAGE CONTRACT v0.2 -- REVIEW PACKET                               |
|  Repairs B1-B5, PORTABILITY-01 rerun as regression, re-adjudication,         |
|  host-conditioned assay readiness                                            |
|                                                                              |
|  Author : Archaeon (seat), session m2-1034e815, host M2 (SPECTREX5)          |
|  Date   : 2026-09-27                                                         |
|  For    : operator (HITL), ChatGPT, external reviewers                       |
|  Status : COMPLETE. Verdict PORTABLE_WITH_DOMAIN_LIMITS (re-adjudicated,     |
|           NOT promoted). Assay READY_WITH_ENGINE_SPECIFIC_LIMITS (nothing    |
|           preregistered or launched).                                        |
|  Self-contained: every load-bearing number is inline.                        |
+==============================================================================+

-----
0. SUMMARY
-----
- B1-B5 share one root: v0.1 stored a relation with several roles as one attribute. v0.2 splits the roles:
    BODY / IDENTITY
    write_governing / execution_share
    ancestry / made_in
    factual contributors / CF_TEST(intervention, outcome)
    hu_continuity / resulting_hu / ARCH, with ILL_POSED
- The 15-fixture attack corpus passes. All 26 prohibited inferences are rejected by the intended invariant.
- The four adapters were rerun on preserved evidence plus bounded replays.
- The regression found a DEEPER break than B1-B5.
  B6 is "governing code" with three referents: WHO executed (body or thread), WHERE the code sits (location), WHAT the code is
  (material).
  * BEE persists WHERE.
  * NPE persists WHO.
  * Only Archaeon's taint VM tracks WHAT.
  * Measured with BEE's own traced VM: in run r038751, 27,083 of the 28,163 births that BEE's location test calls
    "foreign-code governed" were governed by the writer's OWN material, executing from a copy of itself in the window.
- The regression also exposed three errors in my own v0.1 readings:
  (1) NPE write authorship read as material share;
  (2) the NPE rebuild test read from C4 instead of C2;
  (3) PTE "no majority parent" counted only the instructions where parents differ.
- Verdict stays PORTABLE_WITH_DOMAIN_LIMITS. Promotion requires "no new contradiction as serious as B1-B5", and B6 is one.

-----
1. CONTRACT v0.2 (deliverables 1, 3, 4)
-----
Frozen 4282bd706. v0.2.1 pre-adapter amendment 4409540af: a strict known majority decides continuity despite unknown minority mass.
v0.1 is untouched and its tests still pass.

Nodes: MATERIAL, BODY, IDENTITY, EXECUTION, TRANSFORMATION, HU, ARCH, ENV, LOCATION, CF_TEST. ENTITY is removed.

Values:
- Booleans: YES / NO / NOT_IDENTIFIABLE.
- References: a ref, or NONE / NOT_APPLICABLE / NOT_IDENTIFIABLE / ILL_POSED.
- ILL_POSED is allowed ONLY in hu_continuity, resulting_hu, architecture_class and identity_continuity. It needs a justification
  over COMPLETE evidence; incomplete evidence must be NOT_IDENTIFIABLE.

Declared rules: hu_rule (e.g. MAJORITY, strict, tie -> ILL_POSED), arch_rules (kind, criterion, justification; never sequence
similarity). Autonomy is only role-qualified: AUTONOMY_WRITE, AUTONOMY_EXEC, AUTONOMY_MATERIAL.

Invariants J1-J20. J1-J5, J12 and J18-J20 carry v0.1's I1-I12. The new ones:
  J6  ILL_POSED misuse
  J7  no singular continuity once continuity is ILL_POSED
  J8  write governance is never derived from execution share
  J9  no bare "autonomous"
  J10 factual contributors never from a counterfactual
  J11 no counterfactual without a named intervention and outcome
  J13 establishment names its persisting object
  J14 host / executor are BODY, never IDENTITY
  J15 a rename keeps the body
  J16 location never supports ancestry
  J17 ARCH never substitutes for an HU

-----
2. CHANGELOG / MIGRATION (deliverable 2)
-----
Deterministic upgrader upgrade_v01.py:
- ENTITY -> BODY + IDENTITY, with body_identity_split = NOT_IDENTIFIABLE.
- executed_material -> write_governing = NOT_IDENTIFIABLE and execution_share = NOT_IDENTIFIABLE (role ambiguous); the v0.1 value is
  kept.
- child_contributors -> factual_contributors.
- resulting_hu -> hu_continuity + resulting_hu.
- ESTABLISHMENT -> persisting_object.
Tested:
- every v0.1 fixture upgrades to a valid graph, with heredity and establishments unchanged;
- the v0.1 claims are kept verbatim;
- every v0.1 cheat is still rejected;
- the real 385,390-node block-13 graph upgrades in 2.25 s with 0 violations.

-----
3. SYNTHETIC CORPUS v0.2 (deliverable 5)
-----
15 fixtures, as specified: 50/50 recombination (ILL_POSED); 60/40 majority; rearranged self-copy; body renamed after overwrite; 90%
foreign execution with own writes; the reverse; made_in A but descended from B; transplant made in A, now in C; factual contributor
failing sufficiency; low contributor that is sufficient; host as scaffold only; no singular lineage but stable ARCH; insufficient
evidence -> NI, not ILL_POSED; genuinely meaningless concept -> ILL_POSED; parent/body/identity all diverge.
Result: 44 tests pass (15 fixtures, 26 prohibited inferences, rule semantics, round-trip, upgrader). With the v0.1 and reference
suites, 74 tests pass.
Validator limit: A1 (similarity-based architecture) is detected from the criterion's wording only.

-----
4. ADAPTER REGRESSIONS (deliverable 6)
-----
Adapters frozen at 85d648447 before any rerun. Rules come from field definitions, not outcomes.
Archaeon
  - A1-A3 and block 13 upgrade valid, with heredity preserved.
  - Block 13 has no 16/16 ties, so no ILL_POSED appears.
  - ENVGATE-02 expressed as 3 CF_TEST nodes: NECESSITY(window block) YES; SUFFICIENCY(128..131 vs 128) NO; SUFFICIENCY(128..131 vs
    125..128) NO.
BEE
  - 845 runs / 28,964,089 births, 3 workers, 140 s.
  - Three replays reproduced BEE's preserved logs row-for-row: 80,356 / 74,800 / 83,384.
NPE
  - 36 replays, 34 pair births, 0 violations.
  - SAME_BODY through the rename in 34/34.
PTE
  - Mask-instrumented GA: champion and curve identical to the plain run.
  - Crossover probe on native champions: 48 children, frozen behavioural criterion.

-----
5. B1-B5 AND THE NEW BREAKS (deliverables 7, 11)
-----
B1  REPRESENTABLE, RULE INADEQUATE.
    - With the mask logged, PTE crossovers are 1/16 exact ties (ILL_POSED) and 15/16 "decided" by margins like 33/31.
    - Mask-majority continuity matches behavioural architecture in 3/48 children.
    - Under a symmetric operator, continuity must be ILL_POSED BY MECHANISM, not by counting realized shares.
B2  REPAIRED. NPE: 34/34 renamed bodies keep one BODY.
B3  REPAIRED in the contract. Exposed B6.
B4  REPAIRED for data. B6 shows the same axis must apply to code.
B5  REPAIRED. NPE maps to 4 distinct named tests; ENVGATE-02 maps to 3.
B6  NEW, DEEPER: governing code = WHO / WHERE / WHAT.
      r038751: 28,163 births are location-foreign; by material they are 27,083 own, 21 foreign, 1,059 NI.
               Writes by self-copied code: 1,726,650; by foreign code: 941.
      r016299: 38,825 births are location-foreign; by material they are 17,501 own, 8,166 foreign, 13,158 NI.
    Consequences:
    - BEE's native SR criterion (pc < L) cannot see self-replication run from self-copied code.
    - My v0.2 BEE adapter (defect D2) and v0.2 NPE adapter (defect D3: prov = the executing context) mislabel governance.
    - The contract types governance as MATERIAL; the engines persist a different referent.
    - Proposed J21 for v0.3: location or executing context never establishes the material of governing code.
B7  minor: behavioural ARCH saturates at the performance ceiling (two different perfect PTE champions have identical signatures).
Role-splitting fixed B2-B5, but B6 shows it is not yet bounded: B6 is B4 applied recursively to code.

-----
6. OLD ANOMALY / DISAGREEMENT DISPOSITION (deliverable 8)
-----
D1  BEE resemblance vs provenance (847k)   REMAINS_REAL_DISAGREEMENT. In r000001: 1 exact, 0 rotation, 65 NI, so not frame shifts.
D2  BEE SR vs step share (38,817)          RESOLVES_BY_DISTINCTION, then reframed by B6 (both readings are by location).
D3  NPE in-situ authorship vs C4 (12/34)   RESOLVES_BY_DISTINCTION: factual WHO-wrote vs counterfactual authorship.
D4  Archaeon hosted 82 vs 359              RESOLVES_BY_DISTINCTION (BODY-level), numbers unchanged.
D5  parent chain vs genetic lineage        UNCHANGED.
AN1 BEE decoupling (233,499)               BECOMES_NOT_IDENTIFIABLE from preserved records; mostly a location artifact where measured.
AN2 BEE transplant-run first reproducers   UNCHANGED (ancestry logic); "autonomous" must now be role-qualified.
AN3 NPE host-conditioned                   COHERENT under v0.2: 16 events (v0.1 said 8, using the wrong test).
AN4 NPE transplant minority                BECOMES_NOT_IDENTIFIABLE: 9 NO / 15 NI / 0 YES (v0.1 over-claimed).
AN5 Archaeon same-lineage hosting (277)    RESOLVES_BY_DISTINCTION, unchanged.
AN6 PTE no-majority (11/16)                a v0.1 counting artifact (now 1/16); the deeper B1 finding replaces it.
AN7 BEE frame-shift                        REMAINS; the architecture is NOT_IDENTIFIABLE under the declared criteria.
AN8 NEW NPE                                11/34 pair births where the donor's writes are not necessary even in situ.
ALSO 1,284 BEE births that v0.1 left UNRESOLVED are EXACT writer copies: architecture is recognisable where HU provenance is not.

-----
7. PORTABILITY MATRIX v0.2 (deliverable 9)
-----
                                   Archaeon   BEE                NPE                 PTE
ancestry origin (whose)            N          D                  D                   N
made_in / location (where)         D          NI                 N (niche)           NA
body                               N (cell)   NI in rows         D (observer)        N (site)
identity                           N          N                  N                   N
body continuity through rename     N          NI                 D (34/34)           NA
write governance by CODE MATERIAL  D (mixed NI) NI native; D FULL  NI (prov = WHO)     NA in-world
execution share by code material   N (taint)  NI (location only) NI                  N (rule r)
factual contributors               N          A                  D (same-value NI)   D (mask)
named counterfactual tests         D (arms)   A                  N (P-11 x4)         N (zero-comm)
hu_continuity                      N          A                  NI in 25/34         ill-conditioned (B1)
architecture class                 NI (undeclared) D exact / NI  NI                  behavioral, saturates (B7)
establishment (persisting object)  N (HU)     NI                 NI                  NA
replayability                      N          N (verified x3)    N                   N

-----
8. FALSE-FRIENDS LEDGER UPDATE (deliverable 10)
-----
Now 34 rows. New rows:
  FF-30  BEE own code (pc < L) = code LOCATION.
  FF-31  NPE donor authored (prov) = executing CONTEXT.
  FF-32  my v0.1 NPE material share was really write authorship.
  FF-33  my v0.1 PTE majority counted only differing instructions.
  FF-34  behavioural signature saturates at the ceiling.

-----
9. PERFORMANCE (deliverable 12)
-----
Schema/adapter:
  - BEE: 3.54 us (v0.1) -> 3.77 us (v0.2) per birth, +6.5%, excluding I/O.
  - Archaeon light: 2.95 us/event.
  - Block-13 upgrade: 2.25 s.
  - NPE: 36 runs in 0.4 s.
LIGHT projected: BEE ~0.5% of ~0.75 ms/birth; NPE observer 0.0%.
FULL:
  - BEE tape replay 22.6 s/run;
  - BEE code-material replay (BEE traced VM) 58-122 s/run;
  - NPE arm 175-212 s;
  - PTE instrumented GA 66 s + behaviour 22-33 s;
  - Archaeon taint 1.45x per execution.

-----
10. REVISED VERDICT (deliverable 13)
-----
PORTABLE_WITH_DOMAIN_LIMITS (re-adjudicated). The promotion tests:
- B2-B5 representable without hacks: YES. B1 representable, but its rule is inadequate.
- All four adapters work: YES.
- The non-copy substrate is legitimate: YES.
- Disagreements are visible: YES.
- Abstention works: YES, and it is used more, correctly.
- No new break as serious as B1-B5: FAILS (B6).
Not ONTOLOGY_FAILURE: B6 is expressible in v0.2. The failure is in which referent each engine persists and in adapter mappings.

-----
11. HOST-CONDITIONED ASSAY READINESS (deliverable 14)
-----
Definable in one language:
  factual donor contribution in host H
  AND NECESSITY(H state | substitute | outcome) = YES
  AND a sham substitution preserves the outcome.
Manipulability:
  - Archaeon: donor, host and environment are independent (attributed core).
  - NPE: independent (P-11 interact).
  - BEE: needs a new single-interaction harness on its traced VM (B6).
Common endpoint: realized-host outcome holds, fails under substitution, holds under sham; per-engine paired sign; claim = sign
agreement across the three engines.
Falsifiers:
  - no substitution effect in >= 2 of 3 engines;
  - the effect is explained by donor-write necessity;
  - the effect vanishes under code-material accounting;
  - the sham breaks the outcome.
Compute: well under 1 CPU-hour, single worker. It can wait for Bellerophon's campaign.
STATUS: READY_WITH_ENGINE_SPECIFIC_LIMITS. The draft skeleton is in HOST_CONDITIONED_ASSAY_READINESS.md; nothing is frozen or
launched.

-----
12. LIGHT-OBSERVATORY ASKS (deliverable 15) -- proposals only; no engine touched
-----
BEE:
  - replaced + cell;
  - writes by source x CODE MATERIAL;
  - steps by code material;
  - mate id, mutation count.
NPE:
  - victim slot + pre-rename oid; donor slot;
  - directed / context-authored / literal / same-value counts;
  - P-11 intervention ids;
  - code material of the writing instructions.
PTE:
  - GA parent indices, crossover mask counts, operator id;
  - a non-saturating behavioural probe set.
Archaeon:
  - a per-write governing label.

-----
13. WHAT THIS DOES NOT ESTABLISH
-----
- B6 rests on 2 BEE runs chosen for being rich in "decoupled" births; they are not a random sample.
- NPE conclusions rest on 34 events from one specimen.
- The PTE architecture probe covers one physics/env group.
- The B1 "ill-posed by mechanism" rule is a proposal and is untested.
- No other seat's verdict was changed. The BEE SR-criterion observation is reported as a false friend, not as a correction to BEE's
  results.

-----
14. QUESTIONS FOR THE REVIEWER
-----
Q1 Is B6 a genuinely new break, or should v0.1/v0.2's MATERIAL-typed governance be read as already saying it, making B6 purely an
   adapter failure?
Q2 Should continuity become a property of the generative OPERATOR (declared symmetric vs privileged) instead of the realized shares?
   What breaks if it does?
Q3 AN8 (donor writes not necessary in situ, 11/34): an NPE measurement artifact, or a sign that the native pair-tape "birth" is
   sometimes self-conversion?
Q4 Is READY_WITH_ENGINE_SPECIFIC_LIMITS too generous, given BEE needs a new harness and NPE continuity is NI in 25/34?

-----
15. COMMITS, TESTS, EVIDENCE (deliverable 16); BLOCKED ITEMS (deliverable 17)
-----
Branch archaeon/contract-v02-2026-09-27:
  4282bd706  ruling verbatim + contract v0.2 + corpus + upgrader + 44 tests
  4409540af  v0.2.1 continuity amendment (pre-adapter)
  85d648447  v0.2 adapters FROZEN
  949b9ba4d  regression outputs, report, B6 probe, readiness, observatory asks, blocked inputs
Tests: archaeon/tests/test_causal_lens_v02.py (44), test_causal_lens_corpus.py (27), test_causal_lens_archaeon.py (3): 74/74.
Outputs: archaeon/causal_lens/out_v02/*.json; V02_REGRESSION_REPORT.md; HOST_CONDITIONED_ASSAY_READINESS.md.
Evidence (off-repo): C:\Prometheus-data\evidence\contract_v02_2026-09-27\
  (BEE tape and code-provenance replays; BEE's tool copied read-only, sha256 fcb280d0bca5ca9a).
Blocked (roles/Archaeon/BLOCKED_ON_OPERATOR_INPUT_2026-09-27.md):
  - Azure needs: subscription/resource group; which start/stop workflow to copy; the GitHub secret names; a spend ceiling and
    whether spot is allowed.
  - Admission gate: NOT blocked, but out of scope here.
  - Aphrodite #452/#472/#475/#492/#534: untouched.

+==============================================================================+
|  END. "Not worth continuing" remains a first-class answer. The strongest     |
|  argument for it: B6 shows every engine persists a different referent for   |
|  "who authored the copy," and the lens can only be as good as the least     |
|  material-aware engine.                                                      |
+==============================================================================+


## Dated annotation 2026-09-28 (Archaeon, attribution v0 item 9: saturated-ruler guard)
The comparison "mask-majority continuity matches behavioural architecture in 3/48" depended on the behavioural ARCH ruler at its
ceiling. Children and parents shared the maximum score, so ARCH could not separate them.
Under the guard archaeon/attribution/guards.py this reads MECHANISM COMPARISON UNINFORMATIVE AT SATURATED RULER. No secondary
ruler separated them. So "3/48" is neither support for nor evidence against continuity; the E-002 review already called it
"untestable".
Original text above unchanged. Only this record is annotated: it is the one place where the interpretation depended on the
saturated ruler (deep-block B7 scan, C_B7.md).
