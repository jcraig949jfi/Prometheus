# Contract v0.2 -- regression of PORTABILITY-01 and re-adjudication (2026-09-27)

Author: Archaeon[m2-1034e815]. Ruling verbatim: roles/Archaeon/prompts/2026-09-27_contract_v02/.

Order of work:
1. contract v0.2 frozen (4282bd706);
2. v0.2.1 pre-adapter amendment to continuity() (4409540af);
3. v0.2 adapters frozen (85d648447);
4. then the rerun.

Evidence: the preserved PORTABILITY-01 records, plus bounded replays. There were four BEE single-run replays (22.6 s to 122 s each), one PTE
instrumented GA (66 s) and one PTE crossover probe (33 s). No campaign ran. BEE used at most 3 workers while Bellerophon's campaign held M2.

## 1. Synthetic corpus v0.2 -- PASS
- The 15 attack fixtures each conform (15 tests). All 26 prohibited inferences are rejected, each by the invariant it targets.
- The continuity-rule semantics test passes.
- JSON round-trip passes.
- The v0.1 upgrader passes: every v0.1 fixture upgrades to a valid v0.2 graph with heredity edges and establishments unchanged, the
  v0.1 claims are kept verbatim, and every v0.1 cheat is still rejected after upgrade.
- 44 v0.2 tests pass; the v0.1 suite (27) still passes.
- Validator limit: A1 (architecture criterion defined by sequence similarity) is detected from the criterion's WORDING only. Real
  enforcement needs review of the declared criterion.

## 2. Adapter regressions

| engine | evidence | result |
|---|---|---|
| Archaeon | A1-A3 rebuilt; block-13 v0.1 graph (385,390 nodes after upgrade); 53,185 block-13 birth events; ENVGATE-02 RESULTS | all upgraded graphs valid; heredity preserved; no 16/16 ties, so no ILL_POSED; ENVGATE-02 verdict expressed as 3 CF_TEST nodes: NECESSITY(window block) YES, SUFFICIENCY(128..131 vs 128) NO, SUFFICIENCY(128..131 vs 125..128) NO; 0 violations |
| BEE | 845 runs, 28,964,089 births (light); r000001 tape replay; r038751 and r016299 code-provenance replays (BEE's own traced VM, unmodified) | every replay reproduced the preserved log exactly (80,356 / 74,800 / 83,384 rows); results in section 3 |
| NPE | 36 preserved H2 RESERVOIR replays, 34 pair-tape births | 36 graphs, 0 violations; SAME_BODY through the rename in 34/34; results in section 3 |
| PTE | instrumented GA with the crossover mask logged (champion and curve identical to the un-instrumented run); crossover probe on native champions | results in section 3 |

## 3. Tested expectations (ruling s12): results, not forced

**BEE AN1 / FF-28 (write governance vs execution share).**
- The frozen v0.2 split of the 233,499 v0.1 DECOUPLED births:
  * own code governed the writes: 44,773, including ALL 38,817 native-SR decoupled births;
  * code outside the own region governed them: 170,767;
  * not identifiable: 17,959.
- For native SR, the disagreement RESOLVES BY DISTINCTION: writes governed by own code, execution time spent elsewhere.
- But both "own code" readings are by code LOCATION (pc < L), and that turned out to be wrong in kind (B6 below).

**BEE AN7 / FF-27 (frame-shifted copying).**
- Material provenance: v0.2 continuity says "writer" for 817,352 of the 847,000 AUTONOMOUS|target births. The rest sit at exactly
  L/2, and v0.2 requires a strict majority.
- Architecture, measured on r000001 (66 such births):
  * declared criterion exact: 1;
  * declared criterion cyclic rotation: 0;
  * NOT_IDENTIFIABLE: 65.
- The frame-shift hypothesis is NOT supported. These children are not rotations; the provenance-resemblance disagreement REMAINS
  REAL, and their architecture is NOT_IDENTIFIABLE under the declared criteria.
- By contrast, 1,284 births that v0.1 left UNRESOLVED (majority source not persisted) are EXACT copies of the writer. Architecture
  is recognisable where heritable-unit provenance is not, which is the case ARCH was introduced for.

**NPE AN3 / FF-29 (host-conditioned reproduction).**
- v0.2 exposed two errors in MY v0.1 NPE reading:
  (a) v0.1 used donor_authored_share, which is WHO WROTE the directed bytes, as the material share;
  (b) v0.1 read "cannot rebuild a random victim" from C4, which is authorship under intervention; the rebuild test is C2.
- Corrected under v0.2:
  * the donor's material is > 1/2 of the child in only 9 of 34 births. Victims already matched the donor at a median 62.5% before
    the event (fid_init), so continuity is NOT_IDENTIFIABLE in 25/34;
  * the host-conditioned signature holds in **16** births: donor material flows in situ, NECESSITY(block donor writes, real victim)
    = YES, and SUFFICIENCY(randomize victim | rebuild >= 0.9) = NO. That is a coherent statement with no contradiction (v0.1
    counted 8, with the wrong test).
- New: in 11 births the donor's writes are NOT necessary even on the real victim (NECESSITY = NO). The victim reached donor-likeness
  without them. That is AN8 ("birth without a necessary donor"), and the native parent label is not supported there.

**PTE B1 / AN6 (symmetric crossover).**
- v0.1's "11 of 16 crossovers have no majority parent" was MY adapter's artifact: it counted only instructions where the parents
  differ. With the mask logged (complete evidence): 1/16 exact tie (ILL_POSED), and 15/16 "decided" by margins like 33/31.
- Non-degenerate probe (native champions, same physics and env, 48 children from PTE's own crossover, frozen behavioural criterion):
  * mask-majority continuity matches behavioural architecture in 3/48;
  * the 6 ILL_POSED children are all new behavioural classes;
  * two DIFFERENT perfect champions have IDENTICAL behavioural signatures (all 1.0), so the behavioural criterion saturates at the
    performance ceiling.
- The ruling's hypothesis ("ILL_POSED, but a meaningful architecture class") is NOT supported in this specimen. The stronger finding:
  continuity decided from REALIZED shares is ill-conditioned under a symmetric operator.

**NPE FF-11 (body vs identity).**
- 34/34 renamed bodies keep one BODY across the rename (J15). The host body is reported independently of identity.
- RESOLVES BY DISTINCTION.

## 4. B1-B5 disposition

| break | v0.2 repair | regression verdict |
|---|---|---|
| B1 heritable unit | hu_continuity + ILL_POSED + ARCH + persisting_object | REPRESENTABLE, RULE INADEQUATE: MAJORITY on realized shares turns symmetric crossover into arbitrary "decided" continuity (15/16), matching behaviour in 3/48. Continuity under a symmetric operator should be ILL_POSED BY MECHANISM (the operator privileges no parent), not by counting |
| B2 body/identity | BODY + IDENTITY + assigned(from, until) | REPAIRED (NPE 34/34; upgrader 89,425 entities split on block 13) |
| B3 executed material | write_governing vs execution_share | REPAIRED in the contract; the regression exposed B6 |
| B4 whose vs where | ancestry vs made_in / located_in, J16 | REPAIRED for data; B6 shows the same axis must apply to CODE |
| B5 factual vs counterfactual | factual_contributors vs CF_TEST(intervention, outcome) | REPAIRED; NPE maps 4 distinct P-11 tests; the ENVGATE-02 verdict maps to CF_TESTs |

## 5. NEW BREAK B6 (deeper than B1-B5): "governing code" has three referents
- WHO: the executing body or thread. NPE's prov records the CONTEXT that wrote.
- WHERE: the code's location. BEE's by_own_code / own_steps use pc < L.
- WHAT: the code's MATERIAL. Archaeon's taint VM labels every fetched byte by material, and labels travel with writes.

Measured with BEE's own traced VM plus a read-only code-material check:

| run | births BEE-location calls foreign-governed | own-MATERIAL governed | truly foreign | NI | writes by self-copied code / foreign code / elsewhere |
|---|---|---|---|---|---|
| r038751 | 28,163 | 27,083 | 21 | 1,059 | 1,726,650 / 941 / 66,669 |
| r016299 | 38,825 | 17,501 | 8,166 | 13,158 | 702,903 / 317,522 / 528,897 |

What this means:
- A writer copies itself into the window and then executes the copy. By location that is "foreign code"; by material it is its own.
- This inverts most of AN1. It also touches BEE's native SR criterion (pc < L), which cannot see self-replication run from
  self-copied code, and my v0.2 BEE adapter, which inherited the same reading. Defect D2 is recorded; the frozen output is kept.
- NPE's "donor authored" is WHO wrote, not WHAT code (defect D3 in my v0.2 NPE adapter's labelling of write_governing).
- Archaeon's execution accounting is by material, so its host-mediated reproduction finding (ENVGATE-01 R2) stands on the right
  referent.
- The contract already types write_governing / execution_share as MATERIAL. What failed is the mapping from engine fields.
- Proposed invariant J21 (v0.3): code location or executing context never establishes the MATERIAL of governing code (J16 applied to
  code).
- Real host-executed copying exists in BEE (8,166 births in r016299 by material), at a far smaller scale than location suggested.

Also: **B7 (minor)**. Behavioural architecture criteria saturate at the performance ceiling, so a "behavioral" ARCH needs a declared
non-saturation guard.

## 6. Disposition of every earlier anomaly and disagreement

| item | v0.1 claim | v0.2 disposition |
|---|---|---|
| D1 BEE resemblance vs provenance (FF-27, 847k) | provenance says writer | REMAINS_REAL_DISAGREEMENT (not rotations; architecture NI) |
| D2 BEE SR vs step share (FF-28, 38,817) | disagreement | RESOLVES_BY_DISTINCTION (own-location writes vs execution share), then reframed by B6 |
| D3 NPE in-situ authorship vs C4 (12/34) | disagreement | RESOLVES_BY_DISTINCTION: WHO wrote in situ (factual, context) vs authorship under a random victim (counterfactual) |
| D4 Archaeon hosted 82 vs 359 | definitional | RESOLVES_BY_DISTINCTION (BODY-level host), numbers UNCHANGED |
| D5 parent chain vs genetic lineage (FF-1) | real | UNCHANGED (labelled_parent now IDENTITY-level; never heredity) |
| AN1 BEE decoupling 233,499 | executor/material decoupling | BECOMES_NOT_IDENTIFIABLE from preserved records (code material not persisted); where measured (2 runs), mostly an artifact of location accounting (B6) |
| AN2 BEE 17/42 transplant runs with a random-background first reproducer | lineage-level refinement | UNCHANGED in the ancestry logic; "autonomous" must now be role-qualified (it was material + location-execution) |
| AN3 NPE host-conditioned | 8 events (wrong test) | coherent under v0.2: 16 events with factual flow + in-situ necessity + random-victim insufficiency |
| AN4 NPE transplant minority 5/24 | 7 from random background | BECOMES_NOT_IDENTIFIABLE: 9 NO (implant line), 15 NI, 0 YES. v0.1 over-claimed by treating write authorship as material |
| AN5 Archaeon same-lineage hosting 277 | lens-only | RESOLVES_BY_DISTINCTION (BODY), UNCHANGED |
| AN6 PTE no-majority 11/16 | ontology break | v0.1 counting artifact; with full evidence 1/16 ILL_POSED; the deeper B1 problem remains (continuity vs behaviour 3/48) |
| AN7 BEE frame-shifted copying | provenance-majority copies | REMAINS (not frame shifts; architecture NI) |
| NEW AN8 NPE | -- | 11/34 pair births where donor writes are not necessary in situ |

## 7. Portability matrix v0.2 (N native, D derivable, A approximate, NI not identifiable, NA not applicable)

| capability | Archaeon | BEE | NPE | PTE |
|---|---|---|---|---|
| ancestry origin (whose) | N | D | D | N |
| made_in / location (where) | D (inflow / ecology) | NI (cell not in rows) | N (niche tags) | NA |
| body | N (cell) | NI in rows (cell not persisted) | D (slot, via observer) | N (site) |
| identity | N (oid; child oid NI) | N (org id) | N (oid; rename D via observer) | N (site index) |
| body continuity through identity change | N | NI | D (34/34) | NA |
| write governance by CODE MATERIAL | D (single-source fetches; mixed = NI) | NI natively; D by FULL replay (B6 probe) | NI (prov = context, not code) | NA in-world |
| execution share by code material | N (taint of fetched bytes) | NI natively (location only) | NI | N (rule r) |
| factual contributors | N (taint) | A (own-copy count; retained owner NI) | D (directed values; same-value mass NI) | D (mask, replay) |
| counterfactual tests (named) | D (paired arms, population level) | A (run-level controls) | N (P-11: 4 tests) | N (zero-comm, physics) |
| hu_continuity | N | A | NI in 25/34 | ILL-conditioned (B1) |
| architecture class | NI (not declared yet) | D exact / NI other (FULL replay) | NI | behavioral, saturates (B7) |
| establishment (persisting object) | N (HU) | NI | NI | NA |
| replayability | N | N (verified 3x) | N | N |

## 8. Performance (same specimens)
- Schema/adapter:
  * BEE: 3.54 us/birth (v0.1) vs 3.77 us/birth (v0.2), +6.5%, excluding gzip/JSON; with I/O the v0.1 figure was 13.78 us.
  * Archaeon light v0.2: 2.95 us/event.
  * Upgrade of the 385k-node block-13 graph: 2.25 s.
  * NPE: 36 runs in 0.4 s.
- LIGHT projected: BEE ~0.5% of engine time per birth (3.77 us vs ~0.75 ms); NPE observer 0.0% (P01); Archaeon native.
- FULL:
  * BEE tape replay 22.6 s/run;
  * BEE code-material replay with BEE's traced VM 58-122 s/run (vs 25.5 s median untraced);
  * NPE arm replay 175-212 s;
  * PTE instrumented GA 66 s + behaviour 22-33 s;
  * Archaeon taint 1.45x per execution (P01).

## 9. Verdict: **PORTABLE_WITH_DOMAIN_LIMITS** (re-adjudicated, not carried over)
Promotion criteria (ruling s13):
- B1-B5 representable without hacks: YES for B2-B5; B1 representable, but its rule is inadequate.
- All four adapters work: YES.
- The non-copy substrate is still legitimate: YES.
- Disagreements visible: YES.
- Abstention possible: YES (and used more, correctly).
- No new contradiction as serious as B1-B5: **NO. B6 is at least as serious.** It reverses the reading of AN1 at scale, it touches a
  native SR criterion, and it corrupted two of my own adapter mappings.
Not ONTOLOGY_FAILURE: B6 is expressible in the v0.2 contract (governing code is already MATERIAL-typed). The failure is that engines
persist WHO or WHERE, and adapters silently read them as WHAT. v0.2 does NOT promote.

## 10. What this establishes, and what it does not
- The role-splitting diagnosis held for B2, B3, B4 and B5.
- The regression forced exactly one new role distinction, B6, and it is the B4 axis applied recursively to code. Role-splitting is
  not yet shown to be bounded: B6 is its first recursion.
- NPE conclusions rest on 34 events and one specimen. B6 rests on 2 BEE runs chosen for being rich in "decoupled" births, which is
  not a random sample.
