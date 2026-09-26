+==============================================================================+
|  PORTABILITY-01 -- REVIEW PACKET                                             |
|  Can Archaeon's causal lineage lens be stated and measured across            |
|  independent Prometheus engines without forcing Archaeon's ontology?         |
|                                                                              |
|  Author : Archaeon (seat), session m2-1034e815, host M2 (SPECTREX5)          |
|  Date   : 2026-09-26                                                         |
|  For    : operator (HITL), ChatGPT, external reviewers                       |
|  Status : COMPLETE. Verdict PORTABLE_WITH_DOMAIN_LIMITS. Nothing launched    |
|           after the report.                                                  |
|  Self-contained: every load-bearing number is inline; no repo access needed. |
+==============================================================================+

-----
0. SUMMARY
-----
Mandate: operator ruling PORTABILITY-01 (recorded verbatim, 2026-09-26). Close the ENVGATE line, then
turn the causal-lineage machinery into an engine-neutral instrument. Test it on Archaeon (reference),
two independently written Z80 engines (Bellerophon's BEE, Nestor's NPE), and one non-copy engine
(Ananke's PTE). Try to break the ontology.

Verdict: PORTABLE_WITH_DOMAIN_LIMITS. All 8 gates pass.
- The executor / executed-material / contributor / host distinctions exist outside Archaeon. NPE
  exposes them through its OWN provenance machinery. BEE exposes them through trace counts.
- The lens agrees with each engine where both can decide, and it localizes every disagreement to a
  named definitional choice.
- On the non-copy engine it abstains correctly (NOT_APPLICABLE) and refuses the "packets = transfer"
  decoy.
- Domain limits:
  (a) contributor ancestry is only as good as the persisted provenance (BEE: 33.1% of births
      unresolvable);
  (b) establishment is not identifiable from BEE or NPE records;
  (c) the "heritable unit" concept is ill-posed under symmetric recombination (PTE: 11 of 16
      crossovers have no majority parent).
- Five ontology breaks were found (B1-B5, section 7). Each is a MISSING DISTINCTION, not a hidden Z80
  assumption.

Answer to the ruling's closing question: more than a debugger for one machine. Less than a finished
causal language. It is a working grammar with five known gaps, and each gap was found by a different
engine.

-----
1. ENVGATE CLOSURE RECEIPT (deliverable 1)
-----
Record: archaeon/envgate2/ENVGATE_CLOSURE_2026-09-26.md. No frozen ENVGATE file was modified.
- ENVGATE-01: frozen output GATING_CAUSALLY_SUPPORTED; adjudicated GATING_PARTIALLY_SUPPORTED
  (operator ruling R1).
- ENVGATE-02: WINDOW_NOT_SUPPORTED.
  Genetic establishments: U 24 / RRIGHT 3 / RWEAK 2 / R128 5 / BAND0 5.
  The Phase-C gate failed on P2 (0+/2-) and P3 (1+/0-). P1 passed (12+/2-, p = 0.0065) and Page's L
  passed (p = 0.001).
- Environmental blocking REPLICATED. The proposed viable-window mechanism did NOT.
- RIE-01 was correctly not launched. ENVGATE-03 will not be launched.
- Fossils retained, NOT allocation targets:
  * the 5 BAND0 establishments;
  * ENVGATE-02 blocks 11/13/14 (5.9 / 3.3 / 5.9 h wall against a median of 1.0 h);
  * ENVGATE-01 block 13 (host rescue) and block 15 (takeover).
- Recorded deviation: the frozen analyze.main() read pre["blocks"], but PREREG holds the list at
  spec.blocks. The frozen analyze.analyze() was run unchanged through a recorded wrapper.

-----
2. CANONICAL CAUSAL-LINEAGE CONTRACT v0.1 (deliverable 2)
-----
Frozen at commit 13cdec715, BEFORE any foreign adapter was written.
Vocabulary (engine-neutral):
  MATERIAL   carryable state at a declared granularity (bit..population)
  ENTITY     acts, occupies, hosts
  EXECUTION  one occurrence of an entity acting under some material
  TRANSFORMATION  an event node
  HU (heritable unit)  what later ancestry follows
  ENV        environment variable
Graph, not tree. Edges: performed_by, governed_by, produced, copies_from, contributes_material,
mutates_from, recombines_with, hosts, transports, enables, member_of, via, owns, consumes, and
labelled_parent (native parent pointer, kept verbatim and NEVER read as heredity).

Per-event fields, each with a basis (TRACE / REPLAY / NATIVE_RECORD / DERIVED / DECLARED):
  material_origin, executor, executed_material, child_contributors, host, resulting_hu,
  env_dependencies.
Booleans are three-valued: YES / NO / NOT_IDENTIFIABLE. NONE and NOT_APPLICABLE are explicit values.

Invariants (machine-checked in schema.py):
  I1  inserted ancestry never becomes spontaneous by relabelling
  I2  host identity does not imply contribution
  I3  executor identity does not imply child-material ancestry
  I4  descendants inherit origin unless a demonstrable ORIGINATION replaces it
  I5  mutation = new material; retained material keeps its ancestry
  I6  recombination may have multiple ancestors (truncation is rejected)
  I7  transplant preserves donor ancestry
  I8  establishment counted once per HU
  I9  amplification never creates an HU; origination always does
  I10 ambiguity stays ambiguity (no bool False; parent ids cannot support byte-level contributors)
  I11 parenthood is not heredity
  I12 claim resolution cannot exceed evidence resolution

-----
3. SCHEMA (deliverable 3)
-----
archaeon/causal_lens/schema.py: pure Python and JSON-serialisable, with no engine imports. It holds the
Graph class, a typed-edge validator, the I1-I12 checks, and the queries (ancestors, origins,
contributors_hu, establishments, spontaneous). Ancestry follows ONLY copies_from and
contributes_material.

-----
4. SYNTHETIC CONFORMANCE CORPUS (deliverable 4)
-----
archaeon/causal_lens/corpus.py, with tests in archaeon/tests/test_causal_lens_corpus.py (27 tests,
all pass). The 12 fixtures are those the ruling lists: autonomous copier; inserted; transplanted;
random-origin; host executes a foreign copier (block-15 shape); mutation; recombination from two
donors; ecological assistance; takeover (20 labels, 1 HU); 3 independent establishments; unknowable
ancestry; no genome concept.

Each fixture carries a CHEAT that the checker must reject, and every cheat is caught:
  executor-as-contributor (I2/I3)          inserted relabelled spontaneous (I1)
  transplant severed from donor (I7)       reproduction called origination (I9)
  executor lineage as contributor (I2/I3)  mutation without provenance (I5)
  recombination truncated (I6)             host as contributor (I2/I3)
  host labels as lineages (I9)             one HU established twice (I8)
  parent-id-as-provenance and False-for-unknown (I10)
  manufactured genome (I9)
Also tested: removing all labelled_parent edges changes no answer (I11), and a JSON round-trip
preserves every answer.

Corpus defects found while building it and fixed before the freeze:
- an id collision in fixture 9;
- I4 initially rejected a legitimate transplant, which is layered on donor ancestry per I7.

-----
5. ARCHAEON REFERENCE RESULTS (deliverable 5) -- PASS
-----
A1 autonomous copier: REPRODUCTION, contributors = own HU, host NONE, spontaneous YES. Native
   SELF_COPY. AGREES.
A2 inserted resident hosted by a random executor: child HU = resident's, spontaneous NO, executor HU
   not a contributor, AMPLIFICATION+HOSTING. AGREES.
A3 block-15 panel: real ENVGATE-01 tapes on the real VM. Of 63 inert founders, 23 emit the resident.
   The lens shows 23 events, 23 distinct native parent labels and 23 distinct hosts, with the ONE
   resident HU as contributor in all 23.
A4 block-13 host rescue: a deterministic replay to epoch 14,800 (1,518 s; 54,616 births).
   - The dominant lineage is glin 1071 = random arrival 447492 (the near-copier's genome).
   - The host arrival's lineage (1072) hosted births into it and is never a contributor.
   - Native test_10 says the same. AGREES.
A5 random-origin establishment: glin 1071 ESTABLISHMENT, spontaneous YES. Native
   genetic_established = [1071]. AGREES.
Hosting count: 359 HOSTING events into 1071 = 82 cross-lineage + 277 same-lineage. Native
   births_hosted = 82, which is AGREES; the 277 are LENS_ONLY (see FF-26).
INSTRUMENT DEFECT D1 (caught by the contract, not by me): the first block-13 graph had 12 I2/I3
   violations. The adapter resolved a neighbour's lineage only when it differed from the executor's,
   so same-lineage neighbour copies lost their provenance edge. After the fix, the graph was rebuilt
   from the preserved events with no replay: 0 violations.
Tests: 3 reference tests plus the 27 corpus tests, 30/30 pass.

-----
6. FOREIGN ADAPTERS AND RESULTS (deliverables 6, 7, 8)
-----
Blindness protocol: each adapter was committed before its native adjudication was read (BEE
0d598efd2, NPE 19b9e76c9). Native verdict columns are never inputs to the lens rules.

6.1 BEE (Bellerophon), adapters/bee.py. Read-only over 845 preserved traced-birth logs: 28,964,089
births.
  Lens rules:
  - OWN = bytes copied from the writer's own tape (trace).
  - RETAINED = bytes never written (occupant's).
  - OTHER = written, source not persisted.
  - The child continues the writer's HU if OWN >= L/2, the occupant's if RETAINED >= L/2. The result
    is NOT_IDENTIFIABLE if OTHER >= L/2; otherwise it is an ORIGINATION.
  Classes:
    AUTONOMOUS 16,636,008 | UNRESOLVED 9,578,442 (33.1%) | CAPTURE 1,267,061
    WRITER_MIXED_EXEC 1,235,603 | DECOUPLED 233,499 | ORIGINATION 13,476
  Graph checks: 12 runs converted in full, 0 contract violations.

6.2 NPE (Nestor), adapters/npe.py. Per-run lineage files are not on disk (the F: drive is not
mounted), so the H2 RESERVOIR arms were replayed exactly as frozen in NPE's MANIFEST_FROZEN.
  - An observer SUBCLASS records founders, the victim's pre-rename id and wrote/residue.
  - The observer is shown non-perturbing: summary and lineage are bit-identical with and without it
    (3 arms), and its overhead is 0.0% (25.87 s vs 25.87 s).
  - 36 runs = 12 seeds x arms A (in situ) / B (actual implant) / C (random implant). 34 pair-tape
    births, 0 private-slot births in this world.
  Lens rules: the donor is executor and contributor if its in-situ authored share is >= 0.5
  (provenance from NPE's own prov arrays). The host is the victim's body.
  Process note: the driver's bundle filter never terminated (every RESERVOIR bundle shares one
  specimen), so it queued all seeds. I killed it after 36 runs had completed and applied the lens to
  the preserved replay files. An earlier naming collision was fixed and the colliding files deleted.

6.3 PTE (Ananke, non-copy control), adapters/ananke.py.
  - Stored rows: 6,596 (census 5,807 / evolve 678 / transfer 99 / adjudicate 12). GA parentage is not
    stored.
  - Instrumented GA replay (pop 16, 6 gens, CPU): champion and curve are identical to the
    un-instrumented run.
  - 76 operator calls: 44 REPRODUCTION+MUTATION, 5 recombinant continuations, 11
    ORIGINATION+RECOMBINATION with no majority parent.
  - In-world: executor = site and template = rule r (NATIVE). Contributors, host, establishment and
    amplification are NOT_APPLICABLE.
  - Packets: not material, so no TRANSFER is emitted.
  - Transfer cells: TRANSFER with source provenance on 99/99.

-----
7. NATIVE-VS-LENS DIFFERENTIAL, DISAGREEMENTS, ANOMALIES, BREAKS (deliverables 9, 12, 13)
-----
BEE, per birth (lens class x native material x native SR):
  AUTONOMOUS | writer | SR        10,814,259  AGREES
  AUTONOMOUS | writer | no SR      4,974,749  AGREES on provenance (the lens category is weaker than SR)
  AUTONOMOUS | TARGET | no SR        847,000  DISAGREES: the trace says the writer copied >= L/2 own
                                              bytes out of position; resemblance credits the target
                                              (e.g. 47/64 own bytes; fid_writer 0.64 < fid_target 0.67)
  CAPTURE    | target |            1,259,948  AGREES
  CAPTURE    | writer |                7,113  DISAGREES (the occupant already resembled the writer)
  DECOUPLED  | writer | SR            38,817  DISAGREES on "own execution": copy ops ran from own code,
                                              but most steps ran partner/window code
  UNRESOLVED | any    |            9,578,442  NOT_IDENTIFIABLE by the lens; native answers by resemblance
BEE, run level (BEE's SPECIMEN_LEDGER, read after the lens run):
  - Quarantined transplant runs (42). First autonomous reproducer: from the transplant 22, from the
    RANDOM background 17, not identifiable 3.
  - Native self-replication statuses (361). Lens spontaneous YES 271, NOT_IDENTIFIABLE 90, NO 0.
  - Native false-positive-no-SR (156). The lens finds weaker "autonomous" births in 153. The native
    verdict stands.
  - The one seeded run: lens NO (I1 holds).
NPE, 34 pair births (native = P-11 verdict fields):
  - AGREES in 34/34 that the native parent is the provenance donor. The donor's writes are necessary
    (C5) in 34/34.
  - 12 AGREE on authorship: 5 pass P-11 outright; 7 have C4 true but fail P-11 on C2.
  - 8 DISAGREE: the donor authored >= half in situ, yet cannot rebuild a random victim (C4 false).
  - 4 DISAGREE the other way: counterfactual authorship is high while in-situ authorship is < 0.5.
  - 10 are NOT_IDENTIFIABLE by the lens where the native says "not causal" (compatible).
  - The host body (the victim before its rename) is LENS_ONLY in 34/34: natively that identity is
    overwritten.
  - Transplant arm B: 5 of 24 pair births descend from the implant, 7 from the random background, 12
    are NOT_IDENTIFIABLE.

Anomalies (preserved; NO campaign launched):
  AN1 BEE: 233,499 births where the executor mostly ran foreign code while its OWN material was
      inherited (38,817 of them native SR).
  AN2 BEE: 17/42 quarantined transplant runs whose first autonomous reproducer is of random
      background.
  AN3 NPE: host-conditioned reproduction. In 8 births the donor authored in situ but cannot rebuild a
      random victim, while its writes are necessary. This is the counterpart of Archaeon's
      host-mediated reproduction in an independently written engine.
  AN4 NPE: the transplanted genome is a minority of transplant-arm reproduction (5/24).
  AN5 Archaeon: 277 same-lineage hosting events that the native counter cannot see.
  AN6 PTE: GA genealogy is not a tree (11/16 crossovers have no majority parent).
  AN7 BEE: frame-shifted self-copying (most of the 847k).

Ontology breaks (the instruction was to try):
  B1 HU continuity by majority provenance is ILL-POSED under symmetric recombination (PTE) and blurs
     under rearranged copying (BEE). Proposal: a fourth value ILL_POSED; the segment DAG is primary.
  B2 ENTITY conflates body and identity (NPE renames a persisting body).
  B3 "executed material" is two quantities: write-governing code vs execution-time share (BEE FF-28).
  B4 provenance has a spatial axis: NPE tags record WHERE a value was made, not WHOSE.
  B5 authorship is factual (trace) or counterfactual (NPE P-11 C4); they disagree in 12/34.

-----
8. PORTABILITY MATRIX (deliverable 10)
-----
Codes: N = NATIVE, D = DERIVABLE, A = APPROXIMATE, NI = NOT_IDENTIFIABLE, NA = NOT_APPLICABLE.

                               Archaeon  BEE   NPE        PTE
material origin                N         D     D (niche)  N
executor identity              N         N     N (role*)  N site / NA repro
executed/template identity     N         A     NI         N
child contributor ancestry     N         A     D pair/NI  NA / D (GA replay)
mutation provenance            N         NI    A          D
recombination provenance       N         NI    NI         D (HU ill-posed)
transplant provenance          N         N     N          N
host/facilitator identity      N         A     D (obs)    NA
independent establishment      N         NI    NI         NA
amplification                  N         A     D          NA
dependency acq/loss            A         A     N (C5)     N (world level)
origin vs amplification        N         A     D          NA / D
forensic replayability         N         N     N          N

role* = NPE `parent` is the executor in private-slot births but the material donor on the pair tape.

-----
9. FALSE-FRIENDS LEDGER (deliverable 11)
-----
archaeon/causal_lens/FALSE_FRIENDS.md, 29 rows. Headline rows:
  FF-1  ENVGATE parent chain (executor label) != genetic lineage. This is the FIRST fossil: 23
        labels -> 1 HU in block 15; parent-chain counts are 8-42x the genetic counts in ENVGATE-02.
  FF-4/27  BEE `material` is resemblance, not provenance (847,000 births measured).
  FF-10/11 NPE `parent` changes role by mechanism; a pair-tape "birth" renames a persisting body.
  FF-13 NPE material tag = niche of creation.
  FF-14 NPE repro_span is ambiguous at 0.
  FF-19/20 PTE `transfer` maps to canonical TRANSFER; packets do NOT.
  FF-26 Archaeon births_hosted is lineage-level, the canonical host is entity-level.
  FF-28 BEE "own code" != own execution.
  FF-29 NPE C4 != in-situ authorship.

-----
10. PERFORMANCE; LIGHT OBSERVATORY; FULL FORENSIC (deliverables 14, 15, 16)
-----
Measured:
  Archaeon  the taint VM costs 141.4 us vs 97.6 us plain (1.45x per execution). It runs only per
            birth: 11,937 taint calls in one ENVGATE-02 block, about 1.7 s of 5,309 s (~0.03%).
  BEE       light lens 13.78 us per birth (28.96M rows in 399 CPU-s). The engine runs ~0.74 ms per
            birth (25.5 s median run / 34,277 mean births), so online overhead would be ~1.8% (est.).
  NPE       observer overhead 0.0%. A full H2 arm replay takes 175-212 s on 9 concurrent workers.
  PTE       instrumented GA replay 58 s (116 s including the identity check).
Design (OBSERVATORY_DESIGN.md):
  LIGHT: native fields renamed to their canonical roles, plus six online anomaly flags that nominate
         specimens:
         F1 autonomy without own execution; F2 provenance/resemblance split; F3 host amplification
         burst; F4 inserted-to-spontaneous label; F5 unresolved majority; F6 no-majority recombination.
  FULL:  deterministic replay with an observer PROVEN non-perturbing, execution-level provenance, and
         interventional re-execution.
  Pattern: cheap online flag -> preserved evidence -> expensive causal replay.

-----
11. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES:
- The distinctions exist in two independently written Z80 engines, and the contract can represent
  them without changing either engine.
- The lens abstains where a concept does not exist.
- Disagreements have named mechanisms.
DOES NOT:
- No claim that any BEE or NPE native verdict is wrong. Each disagreement is a difference of
  definition, reported beside the native verdict, not replacing it.
- No universality claim beyond four engines, and only ONE non-copy engine.
- NPE rests on one specimen (12 seeds) with only 34 pair births. AN3 (8 events) is a sighting, not a
  finding.
- The BEE sample is whatever traced logs survived (845 of 63,247 runs), not a random sample.
- PTE's GA lens uses a SMALL spec (pop 16, 6 gens), not a native run.
- The block-15 fossil uses real tapes executed on the real VM in constructed births, not a
  whole-world replay.
- The lens's "AUTONOMOUS" is deliberately weaker than BEE's SR. It must never be quoted as SR.

-----
12. RECOMMENDATION (deliverable 19) -- operator's call
-----
Outcome B from ruling s17 (partial transfer), with an outcome-C candidate. My lean:
  1. Contract v0.2 (small; no campaign): ILL_POSED HU value, BODY vs IDENTITY, write-governing vs
     execution-share material, spatial origin axis, factual vs counterfactual authorship. Re-run the
     three adapters; the differential tables become the regression suite.
  2. Candidate next experiment: host-conditioned reproduction, seen independently in Archaeon
     (ENVGATE-01 R2), NPE (AN3) and BEE (CAPTURE/DECOUPLED). One preregistered cross-engine assay with
     paired sham hosts on all three implementations. This is stronger than ENVGATE-03. PROPOSED ONLY.
  3. Light-observatory fields go to seat owners as ASKS, never impositions:
     - BEE: persist `replaced` and per-source write counts;
     - NPE: persist the victim's pre-rename id and wrote/residue;
     - PTE: log GA parent indices.
"Stop here and keep it as a local forensic tool" remains a legitimate answer. The evidence against it
is that three engines disagreed with Archaeon in structured, explainable ways, which a Z80-specific
tool could not produce.

-----
13. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----
Q1 Is majority-provenance HU continuity (>= half the child's material) a defensible default, or should
   the contract drop HUs entirely and count architecture classes over the segment DAG?
Q2 The BEE "UNRESOLVED 33%" is an abstention. Could a cheaper rule legitimately resolve it, or would
   any such rule be false precision?
Q3 AN3 rests on 8 events from one NPE specimen. What would kill it cheaply before any cross-engine
   assay is designed?
Q4 Is treating NPE's RANDOM_MATCHED implant as RANDOM_INIT (random bytes, intervened placement)
   correct, or should placement by the experimenter alone make a lineage non-spontaneous?
Q5 Did the blindness protocol actually bind? The adapters were frozen before the native ledgers were
   read, but I had read the engines' source code and field DEFINITIONS first. Is that contamination?
Q6 Is PTE a strong enough negative control? Would a Game-of-Life or field-dynamics engine have broken
   the contract harder?

-----
14. ARTIFACTS AND COMMITS (deliverable 17)
-----
Branch: archaeon/portability01-2026-09-26 (worktree D:\Prometheus-worktrees\archaeon-portability01-2026-09-26)
  13cdec715  ruling verbatim + MANIFEST; ENVGATE closure; CONTRACT v0.1 FROZEN; schema; corpus; tests
  0d598efd2  Archaeon adapter + A1-A3; BEE adapter FROZEN
  19b9e76c9  NPE adapter FROZEN (observer verified bit-identical)
  5e22ebd58  runs complete; D1 fix; false friends; observatory design
  37145999d  PORTABILITY01_REPORT.md; FF-26..29; PERFORMANCE.json
  (this packet: the commit that adds it)
Files: archaeon/causal_lens/{CAUSAL_LINEAGE_CONTRACT.md, schema.py, corpus.py, adapters/*.py,
       FALSE_FRIENDS.md, OBSERVATORY_DESIGN.md, PORTABILITY01_REPORT.md, out/*}
Off-repo evidence (read-only): C:\Prometheus-data\evidence\portability01_2026-09-26\
  archaeon\A4_block13_events.json, A4_block13.graph.v2.json; npe\*.replay.json (36);
  bee\BEE_LENS_PER_RUN.json + 12 graph files.
Engine sources read (none modified):
  BEE     origin/bellerophon/coupling-campaign-2026-09-24; harness
          C:\Users\James\z80atlas_campaign_2026-09-19\code (16fc6c2a)
  NPE     roles/Nestor/campaigns/z80atlas-verify-2026-09-22
  PTE     prometheus/ananke, roles/Ananke/pte/c1_rows

+==============================================================================+
|  END. "Not worth continuing" is a first-class answer: if the reviewer judges |
|  the five breaks (B1-B5) fatal rather than fixable, say so and the lens      |
|  returns to being a local ENVGATE forensic tool.                             |
+==============================================================================+
