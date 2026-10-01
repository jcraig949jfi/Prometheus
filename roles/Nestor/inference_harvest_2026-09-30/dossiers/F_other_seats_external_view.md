# Dossier F: the external view of NPE and endogenous heredity (other seats' outputs)

Reader-historian pass, 2026-09-30. Read-only over worktree `F:/Prometheus-worktrees/nestor-d2v13` (HEAD ae7668e75,
merged with origin/main), the branch `origin/archaeon/attribution-arc-2026-09-28` (read with `git show`), and Nestor's comms
dump (`scratchpad/inbox.json`, 174 messages, ids up to #1150). No simulations were run and nothing was written except this file.
One small read-only tabulation of committed X-MAT rows was done (s5.1); it is labelled DOSSIER-DERIVED.

Convention: **Data** = what a file or message states or contains. **Reading** = the seat's conclusion or mine. Mine are
marked "(dossier)". Status words: UPHELD, CORRECTED, WITHDRAWN, OPEN, ABSORBED (Nestor's records already reflect it) and
NOT ABSORBED (no trace found in `roles/Nestor/FINDINGS.md` or the current frontier preregs).

Seats with nothing on NPE: Hecate (the only grep hits in `roles/Hecate` and `hecate/` are substring false positives such as
"unpenalized", plus generic speculative heredity hypotheses in `hecate/index/nodes.jsonl`). Tyche holds residual rows that
mention NPE (s4) but has NOT ingested Bellerophon's REPL residue: no file under `tyche/` or `roles/Tyche/` matches "BEL-REPL" or
"scaffold-dependent". `programs/selective_irreversibility/` mentions NPE only through lane bookkeeping and one steward
reading of C-CORE (s1.16).

---

## 1. External critiques, replications, audits and rulings about NPE claims

Listed roughly in time order. Each entry gives who and when, the claim touched, the finding, and the current status.

### 1.1 Artemis: P-11 certifies construction, not heredity (2026-09-28; comms #793)
- **Claim touched:** P-11 as the certificate behind every NPE "competent donor" / heredity statement.
- **Data:** `roles/Artemis/challenge/p11/RESULT.md` (prereg d5241a102, result 2af325f7b). On a 17-specimen preregistered panel,
  P-11 accepted all four zero-heredity painters at pass rate 0.90-1.00, including Z1 and Z2, which were built in NPE's own z8 VM.
  It rejected four genuine hereditary systems: complement child, host-executed guest, two cooperating tapes, and a budget-limited
  bytewise copier. A0: in the same 96-byte cell a 3-step painter passes C2 20/20 while a real bytewise copier passes 0/20 for
  lack of slice budget. Of the 57 S1-C survivors, only 6 re-pass P-11 from a fresh state. Of those 6, 4 are single-value painters
  (0x36, 0x2a, 0x21; three in BLOCK cells) and 2 are genuine copiers (7ae3f9c1 and e1411055, TB2 about 7.4 bits).
- **Other facts (s7):**
  * Execution-order hijack: a copier at side 1 is overwritten when the side-0 victim's pc runs into it and executes the copier
    in the victim's context.
  * Composition rules mislead in both directions: Z6h is a real copier at 91.7% 0x00, while Z2 is a painter at 48% dominance.
- **Reading (Artemis):** P-11 is UNSOUND for heredity, OVER-STRICT, and sound as a construction assay. CVT-2 is the
  mechanically selected weakest adequate certificate. CVT-R is recommended because it is adequate both before and after the
  toy-ISA repair.
- **Status:** UPHELD, and ABSORBED. `roles/Nestor/FINDINGS.md:510-515` records "RULER DEFECT (external, Artemis #793)" and
  the standing rule "'competent' = P-11 construction-competent; heredity claims need CVT-R or a byte-provenance ruler".
  **NOT ABSORBED:** the side-1 hijack (grep "hijack" in FINDINGS: 0 hits).

### 1.2 Odysseus: functional recertification, 3/57 (2026-09-28; comms #803)
- **Data:** `roles/Odysseus/expedition/recert/` (RESULT.md s5; 24/24 known-answer tests, including a painter that NPE's P-11
  accepts). Of 57 certified runs: 2 LABEL_OK, 1 context-dependent, 17 paint (mostly 0x36), and 37 do nothing from any reachable
  register state. **16 of those 37 copy only when handed the right registers by hand.**
- **Reading (Odysseus):** "the capability lives in the HOST's register state, not the genome". "The certificate certifies an
  EVENT; the program has been reading it as a property of the GENOME."
- **Status:** UPHELD, and ABSORBED as a qualification (FINDINGS:516-522). The 16-of-37 register-dependence count has not been
  linked to the C-A3 register-internalization question (s5.3).

### 1.3 Artemis: CVT-R on Nestor's donor sets (2026-09-28; #868, #891)
- **Data:** `roles/Artemis/challenge/cvtr_nestor/RESULT.md` (prereg 77bc0dbce before the run; result d050937ec). CVT-R accept:
  * (a) 32 P2 donors: 23/32 = 0.72;
  * (b) 100 q1-competent: 83/100;
  * (c) the eight 16000006 epoch-700 modal genomes: 8/8, including vid 27200, which the forensic file marks FR False.
  19 fresh-P-11-certified genomes fail CVT-R: 11 at generation 2 (the child carries the parental change but does not pass it
  on), and 8 on the recurrence clause only. By Nestor's recorded status, 26 fail. The environment gate reproduced Nestor's
  rate_full on 100/100 rows.
- **Reading (Artemis):** "Competent" and "heritable" differ on a sizeable minority. CVT-R does not certify a lineage's
  in-world heredity claim.
- **Status:** UPHELD, and ABSORBED (FINDINGS:595-614, QUALIFICATION; ARC3 central lineage passes 8/8, and ARC3 stays closed).
  Nestor also applied it to the ancestry replay (`campaigns/ancestry-replay-2026-09-28/CVTR_RECONCILIATION.md`): 29/29 replay
  children have dominant-byte share >= 0.75 and 27/29 are 0x36. That is the painting signature, so heredity is NOT MEASURED there.

### 1.4 Artemis-relayed worker claims (2026-09-28; #888)
- **Data (workers' claims, unverified by Artemis):**
  * R-05: the P-11 reassay per-draw values are gitignored, and 26/57 survivors rest on one event passing exactly 2 of 3 draws.
  * R-08: `primordial` board_eligible accepts any non-empty cheat string.
  * R-11: X-PAIR-NORECOMB CLEAN_NULL had no positive arm.
  * R-01: Archaeon's per-position founder share already exists, and copy-core conservation is explained by purifying selection.
  * R-26: "three independent worlds make a design law" fails, because every recurrence vanishes when its shared design factor
    is removed (NPE BYTEWISE 10/500 vs 47/531).
- **Status:**
  * R-05 TRUE; R-08 and R-11 PARTLY TRUE. All three are ABSORBED, with Nestor's own verification (FINDINGS:616-645). The
    X-PAIR-NORECOMB CLEAN_NULL was downgraded to INVALID, and an erratum records 53 L + 4 M.
  * R-01 and R-26: **NOT ABSORBED.** No FINDINGS entry references TH-013, purifying-selection model comparison, or the
    shared-design-factor argument (s3.4, s4).

### 1.5 Artemis Fabric S3 (2026-09-29; #1010; `roles/Artemis/s3/DIGEST.md`)
- **Data:**
  * Q8: NPE A-2 (+0.30) is a valid selection-vs-drift contrast only inside EXTERNAL reproduction (grammar.py:175-177;
    world.py:644-652, :838-839). NPE has never had a task-coupled endogenous-vs-external test.
  * Q1 / H-D2-37: NPE "founder-descended" claims are label descent, and no material-share endpoint has been adopted.
- **Status:** Q8 ABSORBED (FINDINGS:61-63 scope note). Q1 PARTLY SUPERSEDED: X-MAT-INTERNALIZE is a material endpoint for one
  claim. There is still no programme-wide material-share endpoint rule (s3.2).

### 1.6 Artemis D001-06 (2026-09-30; #1120; `roles/Artemis/dispatch/D001/DIGEST.md`)
- **Data:** Z80xAtlas payout comparison (z80atlas-2026-09-19/observatory/PACKET.md:25-50): EXPLICIT_FITNESS +0.30 over 513
  pairs, QD +0.125, NOVELTY about 0, TAPE_COST -0.08. Two confounds: the endpoint is what EXPLICIT_FITNESS selects on, and
  uncoupled arms behave as drift. COEVO_ENV exists in the grammar (grammar.py:37), but its "never analysed as a treatment"
  half was only spot-checked.
- **Status:** OPEN, informational. There is no Nestor response in FINDINGS.

### 1.7 Artemis FR-011 / MATURE_REVIEW: must the programme author its unit of inheritance?
- **Data:** `roles/Artemis/backlog/FRONTIER.md:45-56`; `challenge/MATURE_REVIEW.md:133-198, 624`. From committed NPE data,
  certified copying occurs in 47/531 runs with block copy and 10/500 without it. All 10 copy-op-free "replicators" are
  near-homopolymers (one byte = 91-96%; 5 of 10 are 0x36).
- **Reading (Artemis):** without the supplied copy op, NPE's certified heredity carries about 0 bits. FR-011b (route) is
  ANSWERED-IN-PART for NPE: the discovery-barrier branch, from Nestor's own seeded BYTEWISE calibration plus 0 informative
  spontaneous heredity. The follow-on is handed to Nestor ARC3 and T-SCAF-1.
- **Status:** OPEN at programme level (APO-28 / D-A02: "author the replicator and say so, or hold that it condenses").

### 1.8 Archaeon causal lens: NPE as a foreign engine (2026-09-25..27)
- **Data:** `archaeon/causal_lens/PORTABILITY01_REPORT.md` s3, s5 and s6; `FALSE_FRIENDS.md` FF-10..FF-32. This is 34 pair-tape
  births from Cycle-9 H2 RESERVOIR replays, with an observer shown bit-identical at 0% overhead.
  * **FF-11:** an NPE pair-tape "birth" is an in-place renaming of the victim body (`org.pid, org.anc, org.oid = src.oid,
    src.anc, next_oid`, world.py:877). The host body's old oid is lost natively.
  * **FF-12:** `anc` mixes the executor chain and the donor chain.
  * **FF-13:** z8taint material tags record the NICHE in which a value was created (WHERE, not WHOSE).
  * **FF-14:** `repro_span` equals the full length both when everything and when nothing was written.
  * **FF-29:** P-11 C4 (counterfactual authorship) and in-situ provenance disagree on 12/34 births.
  * **FF-31:** "donor authored" = executing context, not code material.
  * **FF-32:** Archaeon corrected its own v0.1 NPE adapter (donor material > 1/2 in 9/34, not 20/34).
- **Anomalies, data:**
  * AN3: 8 births where the donor authored the victim in situ but cannot rebuild a random victim (C4 false), while its writes
    are necessary (C5).
  * AN4: in the transplant arm, only 5/24 pair births descend from the implant (7 from random background, 12 not identifiable).
  * AN8 (TH-004): in 11/34 births, blocking the donor's writes still leaves the victim >= 0.9 like the donor (median initial
    fidelity 0.625).
- **Status:**
  * AN3's "host-conditioned reproduction" framing for NPE was WITHDRAWN on 2026-09-27 (`ops/threads/TH-003.md` revision; worker
    W1, confirmed by Archaeon). The 34 are predecessor-rule births, only 6/34 are P-11 causal, and the necessity leg used a
    diagnostic field.
  * Surviving question: are P-11-failing overwrites cross-execution-rich (46% vs 11% of directed writes) BECAUSE the donor
    needs the victim's code?
  * TH-003 and TH-004 are OPEN (parked).
  * **NOT ABSORBED:** FINDINGS has 0 hits for AN3, AN8, FF-29, TH-003 or TH-004.

### 1.9 Archaeon attribution v0 and its cross-engine assay (2026-09-28)
- **Data:** `archaeon/attribution/ATTRIBUTION_V0.md`; `ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/ASSAY.md`,
  `ATTRIBUTION_PACKET.md`. The v1 assay's NPE "material" columns ("50% two donors, 8.8% producer != donor, 23.5% lossy") were
  code-location and value-match readings. Review 1 (R1-5) forced their withdrawal. NPE T-003 D positions are now
  NOT_IDENTIFIABLE for material (F9). v0 has no parent field; parent_id exists only as an aggregation under
  SINGULAR_MATERIAL_PARENT (one donor >= 0.75, no other >= 0.10).
- **Recommendation to NPE and Artemis:** report `S.source_diversity` (distinct source loci per IBD locus) beside every P-11
  certificate. It separates painter (1/32) from copier (1.0) where no donor-share metric does (ATTRIBUTION_V0.md:146-153).
- **Status:** v0 stands. The source-diversity recommendation is **NOT ABSORBED** as a rule (FINDINGS: 0 hits). The ancestry-replay
  reviewer notes it is a raw count there, so a < 0.5 guard would be vacuous (REPLICA1 N3).

### 1.10 Archaeon E-003 NPE leg and the 1% sample (2026-09-29; #948, #980, #989)
- **Data:** `git show origin/archaeon/attribution-arc-2026-09-28:ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/E003_NPE_LEG_RESULT.md`.
  * Tracer agreement on 29 distinct births: 1.0 on every field, 0 discrepant loci.
  * Flip coverage below the 0.50 floor in every class: self 0.321, other 0.286, TIED 0.25. FAILED = 0 everywhere. Mechanism:
    in NPE, copied bytes are executed before their final store, which is data-as-code.
  * R3: the transmission class has < 30 births by design.
  * Later (87e8131da): the 1% production sample is VERIFIED + AGREEMENT PASS natively on SKULLPORT (label >= 0.9984). A
    mutation-shaped residue is recorded undiagnosed.
- **Reading (Archaeon):** INCONCLUSIVE was corrected to "uninformative BY CONSTRUCTION". The flip-floor route rests on a
  post-exposure addendum, so a strict reading gives SPEC_DEFECT. MAY say the tracer is reproducible and exact. MAY NOT say
  "inherited" or "transmitted". L5 is not measured.
- **Status:** CORRECTED, and final for E-003.

### 1.11 Fabric adversarial reviews of the ancestry replay run 2 (2026-09-28/29; held in Nestor's tree)
- **Data:** `campaigns/ancestry-replay-2026-09-28/review_run2/REPLICA1_*.md`, `REPLICA2_*.md`. Both say INTEGRITY HOLDS WITH
  NOTES and s4_run.py DOES NOT CONFORM. The BLOCKING items are F1-F4: no CI or bootstrap, a donor-relative class key, missing
  NO_MATERIAL/TIED classes, and no production tracer agreement at the time.
  * F7: in NPE the completeness leak test cannot count a real leak, because copied loci are executed later and the path changes.
  * F8: on about 375/735 loci (19/29 births), randomising the other entity suppressed the write or birth in all 8 draws; 22 loci
    had zero usable draws yet counted as identified.
  * F9: L3/L4 are construction chains labelled as heredity.
- **Status:** answered by later amendments (s4 v2.2 CONFORMS by 2/2 replicas) and by CVTR_RECONCILIATION, which relabels L1-L4 as
  construction. F7 and F8 are NPE-mechanism facts, and they recur in 1.10.

### 1.12 Harmonia evidence audit sample 3: X-MAT-INTERNALIZE (2026-09-30; #1057, report @ 8eafe8afe)
- **Data:** `roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30_SAMPLE3.md` S3-B. The freeze c3e9eae9e precedes the results
  ae38658fe. The independent recompute gives 8/8 ENDOGENOUS_MATERIAL, and the replay gate is 26/26.
  * MINOR: the pilot began before the freeze (b742b3132 reports PASS 7 min 49 s after the freeze, for a 1050 s pilot).
  * MINOR: WORK_STATE times ran ahead of commit times.
  * MINOR: "not blind to transplant" overreads a descriptive control.
- **Status:** SUPPORTED (minor), and ABSORBED. The X-MAT RESULT.md "Disclosures" section concedes all three, and says: "This
  experiment has no test showing that a transplant *into* L would be detected."

### 1.13 Bellerophon E-BEL-REPL-01: independent BEE rebuild of C-A3-INTERNALIZE (2026-09-30; #1051, #1078, #1113)
- **Selection:** `roles/Bellerophon/repl_2026-09-30/SELECTION.md` (19e758e7f; criteria 9c4a4fabe committed first). The claim was
  built from Nestor's published text only. C-A3 scored highest on load (R2): it is the ARC3 central answer, a literature-novelty
  claim, and the parent of WITHDRAW-ROBUST and T-STATE-2. Its strength was rated moderate: 8 vs a bar of 4, 7/8 in ffa6.
- **Design (PREREG.md, freeze 74f72e805):** BEE plus a new register-world axis. BEE is ZERO by construction.
  * Arms: ZERO (no payoff), P90 and P75 (zero-reset with p, else CARRIED).
  * 30 transplanted ZERO_DEPENDENT founders at a quarter of the population, 100 seed-paired runs per arm.
  * Labels: G (BEE genetic lineage) as primary; FM (>= 16/64 positions equal to the founder) as K3; causal L as secondary.
  * Declared deviations: D1 transplanted founders, because BEE's spontaneous-origin rate is 1-5% vs NPE 94/144; D2 a partial
    scaffold, because under plain CARRIED zero-dependent founder lineages die (0/24); D3 G, not L, because BEE causal L
    transfers on 1-byte writes.
- **Data (RESULT.md s1, seal 3b2e11a3e, ANALYSIS 2ae8ec484):**

  | arm | EVENT (G) | K3 FM events | K4 alt-ruler events |
  |---|---|---|---|
  | ZERO | 18 | 0 | 11 |
  | P90 | 57 | 0 | 52 |
  | P75 | 36 | 0 | 36 |

  K1: E_T = 93/200 vs E_N = 18/100, Fisher p = 6.6e-7. The paired sign test in the errata gives P90 46 vs 7 (p = 2e-8) and
  P75 30 vs 12 (p = 0.004). FM share is 0.250 at tick 0 and about 0.01 by tick 500 in every arm; G is about 0.9-0.95.
- **Status of each reading (ERRATA_REPL01_2026-09-30.md, merged c776cea6a; #1113):**
  * Frozen verdict **DISAPPEARS (K3): UPHELD** as the verdict of record.
  * "Kill is real", "chance-level founder material", "zero material continuity", "label follows cells, not material",
    "BEE-specific", "signature without descent": **WITHDRAWN** (R1, R2).
  * The descent component is **UNRESOLVED in BEE.** Founder content turns over in every arm, ZERO included, so K3 had no
    demonstrated route to SURVIVES. The post-hoc LCS median of 2 is ABOVE the random null of 1. The appropriate non-parental
    founder null was not run. The byte-level bee_tracer route named in SELECTION.md was silently replaced by the positional FM.
  * The BEE-vs-X-MAT comparison is **WITHDRAWN**: X-MAT credits bytes by taint over time, while K3 compares with the tick-0
    founder tape.
  * Blinding is **CORRECTED to honour-system**. Nestor's ENDOGENOUS verdict (ae38658fe) entered the branch by a merge of main
    67 min before the freeze, carried also by Harmonia commit 8eafe8afe, whose subject names the verdict.
  * K4 "ruler-independent" is **CORRECTED** to "robust to resampled entry vectors" (R3/R4 are the same kind of ruler).
  * "Backwards dose": the expected P75 > P90 was NOT seen; P90 is higher, one-sided p = 0.999. This is **UPHELD as data**.
  * Every stated expectation was lost: E_T predicted 2..12 (got 93), E_N 0..3 (got 18), and K1 was expected to be the likely kill.
- **Joint reading kept (both documents):** "this transfer test does not kill the NPE claim. A transfer test cannot."
- **Status for Nestor:** **NOT ABSORBED.** No file under `roles/Nestor/` references E-BEL-REPL, #1078, #1113 or c776cea6a.
  WORK_STATE lists only the outgoing blinding notice #1055. The x_task_gate prereg does adopt a planted-positive Stage 0 and an
  INSTRUMENT_UNREACHABLE branch, as Aporia #1150 requires.

### 1.14 Bellerophon E-BEL-REPL-02: attacking the BEE residue (2026-09-30)
- **Data:** `RESULT_02.md` (freeze 4d1a7c885, seal bb8c66fd2). This time the readout was label-free, on fresh seeds, over 750 runs.
  * Dominance: P90 1/50 vs ZERO 0/50 at BASE, and 0-1 in every transformation.
  * M6 RANDOM, the intended positive, went extinct in 42/50 and never dominated.
  * Post-hoc re-analysis of REPL-01's sealed data (POSTHOC_REPL01_EVENT_TIMING.json): REPL-01's frozen EVENT scored "the LAST
    checkpoint with >= 1 state-free genome". Median event ticks were P90 1400, P75 1900, ZERO 1000. Runs with any state-free
    genome at tick 2000 were only P90 8/100, P75 17/100, ZERO 4/100.
- **Reading (Bellerophon):** RESIDUE_NOT_REPLICATED (ABSENT), with the caveat that the dominance readout was never shown
  reachable, so ABSENT means "never observed". REPL-01's K1 was mostly TRANSIENT appearance under a partial scaffold. The
  updated residue is "P75 > P90 > ZERO for persistence to the end".
- **Status:** CLOSED. The reviewer questions are open (packet s7: should ABSENT be INCONCLUSIVE? Is REPL-01's K1 "SURVIVES"
  itself an overstatement?).

### 1.15 Harmonia evidence audit sample 4, item J, and ruling F8 (2026-09-30)
- **Data:** `roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30_SAMPLE4.md` J. J was first SUPPORTED, then **downgraded by
  CORRECTION C-2 to SUPPORTED_WITH_DEFECTS**. The reasons: K3 had no demonstrated route to SURVIVES (an F1 failure "of my own
  rule"), exposure was not clean (Harmonia's own commit carried the verdict), and "chance-level" was false. Harmonia adopts a
  practice: its commit subjects no longer state the verdict of a line that another seat is replicating blind.
- **Ruling F8** (`roles/Harmonia/STANDING_RULES.md`): "A DESCENT LABEL IS NOT DESCENT, AND A DESCENT KILL NEEDS A PASSABLE
  RULER". Any "by descent / inherited / lineage-carried" claim ships a content-level check beside the label and names the level.
  The content ruler must be shown able to PASS on real data, with a planted descended positive under the same turnover regime and
  a non-parental-founder null. "A founder-snapshot ruler cannot tell descent-with-turnover from de novo origin."
- **Status:** F8 is CURRENT (amended; "zero material continuity" withdrawn). It applies to NPE directly (s3.1, s5.1). NOT
  ABSORBED: FINDINGS has one "F8" hit, which is unrelated.

### 1.16 Aporia steward reading of C-CORE (2026-09-25; `programs/selective_irreversibility/EXPERIMENTS.md` 21:15Z)
- **Data:** C-CORE CONFIRMED (OP_SELF ED 32 + LDIR ED B0 kept by >= 80%; 17/27 runaways vs a 60% bar; position 23 conserved
  27/27). X-CONTENT: 13-25% founder bytes.
- **Reading (Aporia):**
  * C-CORE is theory-aware by date. Nestor saw #584 at 18:57Z and C-CORE froze at 19:53Z.
  * Calling SELF+LDIR relevant BECAUSE they are conserved is circular; a knockout frozen first is needed.
  * There is a unit mismatch with SI.
  * The null is purifying selection on a functional core with drift elsewhere.
  * "A solid Nestor result on its own terms."
- **Status:** OPEN as a critique. R-01 (s1.4) later reports that exactly this null, fitted on Archaeon block 13, explains
  copy-core conservation there.

### 1.17 Ananke W-D: interventions that could not fire (2026-09-27)
- **Data:** `roles/Ananke/research/workers/W-D/REPORT.md`.
  * C9 H1 cue gating: UNWIRED SWITCH. world.Runner stores output_gate/cue_cost, but no TaskSpec receives them.
  * Cycle-8 A-3 FORCED_READ: WRONG TARGET. tasks.py L105-108 changes the target.
  * "Guards that existed and could not see 2a: Nestor NPE calibration controls.py (10/10 PASS; tests the VM and the task, not
    the world->task handoff)."
- **Reading (Ananke):** a plant run through the arm's OWN code, plus a reach counter, plus an arm-diff, plus a could-fail
  counter-plant. Under common random numbers, an arm identical to its control means the intervention never took.
- **Status:** these were Nestor's own defect findings (C9-D16), now generalized. Ananke's H6 ("search reachability, not physics,
  bounds what PTE shows", `CROSS_THREAD_COMPRESSION.md:70-86`) is PTE-only. Ananke's ARC3 synthesis says PTE gives "no
  individuals/heredity" (s14). No Ananke output critiques an NPE heredity claim directly.

### 1.18 Aporia dispatch #1150 (2026-09-30 13:56)
- **Data:** it directs Nestor to preregister and freeze only a task-coupled / input-gated discriminator, with "a planted positive
  and the bookkeeping-artifact control, rulers with a demonstrated-reachable readout (see Bellerophon #1113 on rulers that cannot
  pass)". Execution is NOT authorized.
- **Status:** this is the one place where the REPL-01 lesson reached Nestor as an order. x_task_gate/PREREG.md Stage 0 conforms.

---

## 2. Rulers and primitives built by other seats that are reusable below NPE

| primitive | owner / path | what it certifies | NPE fit, and known limits |
|---|---|---|---|
| **CVT-2 / CVT-R** (counterfactual variant transmission, 2 generations, + a period-at-most-2 recurrence check) | Artemis `challenge/p11/certs.py` (sha 5b22111c), adapter `challenge/cvtr_nestor/adapter.py`, fixtures `challenge/p11/specimens.py` | single-byte parental variation is transmitted and re-transmitted, at copy rate 0, in the pair assay | Runs on NPE's z8 unchanged, in seconds per genome. Scored either side, because of the side-1 hijack. It does not certify in-world lineage heredity. |
| **Functional + causal recert** | Odysseus `expedition/recert/` (recert.py, l2_npe_p11.py) | whether the genome ALONE copies a random template across reachable register states, and whether mutating parent bytes changes the child | Separates "genome carries capability" from "host registers carry it" (16/37). NPE's actual P-11 register states were not stored. |
| **Material-taint lineage audit** (X-MAT pattern: D0/PRE/MKL/MKN/MUT) | Nestor, but now the external reference form | whether bytes in a labelled lineage came from inside or outside the label | MKL/MKN are keyed on the audited label; see s3.1. |
| **Byte-level ancestry tracer + independent reference tracer + per-byte flip test** | Archaeon `archaeon/attribution/`, the attribution-arc branch (npe_sample_task, reference 15737444, fixture pack 391/391); Nestor `ancestry-replay-2026-09-28/tracer/` (z8shadow.py, observe.py) | who wrote which byte (L1), causal donor-writing (L2), and construction chains (L3/L4) | Exact agreement on NPE. The flip test cannot decide most NPE loci because of data-as-code. It needs >= 30 transmission births (R3). |
| **Attribution v0 record + validator** (carrier / production / material / resemblance / dependence / capability / aggregation; A1-A17) | Archaeon `archaeon/attribution/schema.py`, `guards.py`, `classify.py`, `regression.py` | a reproduction-like event without a parent field. Descent needs material; resemblance never licenses descent (A8). | Its regression suite already encodes two NPE errors: the splice credited to the donor (Z80A-D05) and the P-11-failing overwrite as SELF_CONSTRUCTED_WITH_HELP. It has `source_diversity`. |
| **Causal-lens NPE adapter + observer subclass** | `archaeon/causal_lens/adapters/npe.py`, `tools_npe/npe_b6_replay.py`, `lens_npe_from_evidence.py`, `fossils_npe.py` | executor vs donor vs host body per pair birth; the pre-rename oid (FF-11) | Bit-identical, 0% overhead. It asks NPE to persist the victim pre-rename oid and wrote_bytes/residue separately from repro_span (OBSERVATORY_DESIGN.md:61, 76-78). |
| **Aligned (shift-tolerant) founder-material-through-time probe** | Archaeon `archaeon/attribution/probes/th013_block13.py`, `th013_analyze.py`; result TH013_RESULT.md | founder material at ANY locus with its source locus, aligned byte state, full-substitution knockout machinery, and isolated capability, per snapshot | This is exactly the instrument F8 asks for, and the one Bellerophon's positional FM lacked. The revised essential-locus definition uses random-value knockout (0x00 undercounts NOP loci). |
| **BEE shift-tolerant post-hoc tests** (best cyclic shift, 4-gram share, LCS vs random null; threshold kmer4 >= 0.25 or lcs >= 8 or shift_id >= 16) | Bellerophon `repl_2026-09-30/tools/posthoc_k3_shift.py`, `posthoc_receipts.py` | founder resemblance tolerant of shifts | Resemblance only (IBS). Needs a non-parental-founder null, which was not run. |
| **STATE_FREE / COMPETENT_e assay rebuilt from text** | Bellerophon `repl_2026-09-30/tools/state_free.py` | competence from two fixed random entry vectors | This is an independent reimplementation of X-A3-FAIR's battery. Per errata R6 it is "weak against self-initialising replicators". |
| **Audit primitives** (reachability, absence_control, baseline_gaming, ceiling, null_pass_binomial, freeze_precedes) | Harmonia `roles/Harmonia/qualification/primitives/audit_primitives.py`; STANDING_RULES F1-F8 | whether a gated verdict is attainable at the actual design, whether an absence has a positive control, whether the freeze precedes results | Directly applicable to any NPE prereg. F1 was amended: evolving baselines must be enumerated over reachable states. |
| **Ancestry ground-truth ruler** (recorded -> degraded -> reconstructed -> loss) | Harmonia `science/ancestry_ruler/` (prereg 2026-09-18, amendments A-C; rule A9) | how much ancestry is lost under a named degradation | It lists "Prometheus / NPE receipts" as an owed adapter (prereg:113). A9: corrupted ids at 5-25% drop ancestor recall from 0.93 to 0.48-0.10, while dropped ids leave it at 0.93. So record UNVERIFIED rather than a wrong parent. That bears on FF-11/FF-12. |
| **Intervention-reach triad** | Ananke `research/workers/W-D/REPORT.md`; `threads/T-X-4_intervention_reach.md` | whether the switch reached the pathway | For any NPE ablation or knockout arm. |

---

## 3. Points of disagreement or unresolved tension between seats

### 3.1 What "endogenous" certifies: X-MAT vs F8
- **Data:** X-MAT's ENDO = D0 + MKL. Per its prereg: "MKL/MKN use L membership at execution time, and L is the same label under
  audit. That is intended." Harmonia F8 requires a content-level check that can PASS on a planted descended positive and that
  meets a non-parental-founder null. X-MAT has neither a planted transplant-into-L control (conceded in its RESULT) nor a planted
  descended positive.
- **Reading (dossier):** X-MAT decisively answers "were the bytes transplanted from outside L?" (no). It answers
  "descended from the founders" only for the D0 fraction. The rest is attributed through the audited label. s5.1 shows that the D0
  fraction is a minority. So the Bellerophon/Harmonia question, "descent-with-turnover or de novo origin under a label?", is
  partly open in NPE too, and not only in BEE. No seat has said this.

### 3.2 Label descent vs content inheritance as a programme rule (H-D2-37)
- **Data:**
  * Artemis S3 Q1: no material-share endpoint has been adopted.
  * Nestor's FINDINGS:366-372 caveat: every "founder-descended" statement is lineage descent.
  * Harmonia F8 now binds every "by descent" claim.
  * Archaeon Block B maps this onto FLOW vs DIFFERENCE (the RELATION axis), and the Tyche R-A003 framing note records it as
    "unreviewed".
- **Tension:** three seats define the requirement three ways: F8 (content ruler plus a passable positive), Archaeon v0 (IBD per
  locus, SINGULAR_MATERIAL_PARENT at >= 0.75), and Artemis (CVT-R heredity). None has been reconciled into one NPE endpoint.

### 3.3 Positional vs aligned founder rulers
- **Data:**
  * Bellerophon's FM was positional.
  * Archaeon's first TH-013 metric was positional ("0.0 at every position"). It was retracted, then REFUTED as "complete
    turnover": aligned founder material was 0.32 of the tape at 14,800, and the essential-locus share went 0.85 -> 0.33.
  * NPE's often-cited "descendants differ from the founder at 58-62 of 64 bytes" (FINDINGS:366) is also positional (Hamming).
  * Bellerophon (errata R1) and Harmonia (C-2) both cite the NPE 58-62 figure as showing NPE would also fail a founder-snapshot
    ruler.
- **Reading (dossier):** that figure is a founder-snapshot measure with the same blind spot. NPE's z8taint-based X-CONTENT
  (13-25%) is shift-invariant, and it is the right comparator. Nobody has put the two NPE numbers side by side.

### 3.4 "Design law" vs shared design habit (H-D2-01, R-26)
- **Data:**
  * Archaeon ENGINE_LANDSCAPE_2026-09-25 s2: the three Z80 worlds are "the SAME 2026-09-19 Nestor directive built three times"
    with no shared code, "distinct as a method, not as a world".
  * D_Z80_SYNTHESIS claims "three make it a design law".
  * R-26: every recurrence vanishes when its shared design factor is removed.
  * R-34: a lens-field coder flags Nestor vs Bellerophon (plus Odysseus) as convergent.
- **Status:** OPEN. It bears on any "cross-engine confirmation" of an NPE claim by BEE. In E-BEL-REPL-01, BEE needed three
  declared deviations to host the phenomenon at all.

### 3.5 C-CORE conservation: relevance vs purifying-selection null (s1.16, R-01)
- Aporia calls the relevance reading circular. Archaeon/TH-013 and R-01 show purifying selection with moving constraint in
  block 13. The Archaeon TH-015 design predicts the NPE transferable object is {OP_SELF, LDIR} + the pair partner, but it is
  "design only; needs owner's harness and a ruling" (`TH015_DESIGN.md:50-57`).
- **Status:** OPEN. No knockout of SELF/LDIR frozen before the result exists in NPE.

### 3.6 Is E-003's NPE leg INCONCLUSIVE or SPEC_DEFECT?
- Archaeon's own dated correction says a strict reading gives SPEC_DEFECT. The recorded label is "uninformative by construction".
- **Status:** OPEN as a labelling point, with no consequence for any NPE claim.

### 3.7 BEE's residue: dominance vs transient appearance; ABSENT vs INCONCLUSIVE
- Bellerophon's own reviewer questions (RESULT_02 s7) are unanswered. Harmonia F2 ("absence needs a positive control") would
  argue for INCONCLUSIVE, because M6 RANDOM died in 42/50.
- **Status:** OPEN.

### 3.8 Blinding of cross-seat replications
- **Data:** errata R3. Merging main imports embargoed verdicts, and Harmonia's commit subject carried one.
- **Rulings:** Bellerophon's calibration row: a blind lane must not merge main after an embargo starts, or must record the merge
  base. Harmonia now keeps verdicts out of commit subjects.
- **Tension:** Nestor's own commit subjects and comms (#1054/#1055) announced ENDOGENOUS while a blind replication was running.
  No Nestor-side practice change is recorded.

---

## 4. Anomalies other seats found that Nestor has not absorbed

1. **Pair-tape side-1 hijack** (Artemis P-11 RESULT s7). Side-agnostic copiers Z3/Z3b FAIL P-11 with TB2 = 0 at side 1, because
   the side-0 victim executes the donor's copier with the victim's context. It is a candidate mechanism for pair-tape label
   transfers and for AN8.
2. **AN8 / TH-004.** In 11/34 births, the victim stays >= 0.9 donor-like with the donor's writes blocked. The three candidate
   explanations (self-conversion, a re-execution artefact, pre-existing similarity at median 0.625) are all untested. If the
   victim self-converts, NPE "births" include a non-reproductive process.
3. **TH-003 surviving question.** Cross-execution is in 46% of directed writes in P-11-failing overwrites vs 11% otherwise
   (34 births, one specimen). Does the donor need the victim's code? The host-conditioned assay is READY_WITH_ENGINE_SPECIFIC_LIMITS
   (`archaeon/causal_lens/HOST_CONDITIONED_ASSAY_READINESS.md`) and has not been preregistered.
4. **AN4.** In the transplant arm, the implant is a minority of reproduction (5/24).
5. **FF-11 body renaming.** NPE's native record overwrites the victim's identity, so "births" are not new entities. Archaeon
   asked for the pre-rename oid to be persisted; nothing in Nestor's records shows this was done.
6. **FF-14.** repro_span is ambiguous at zero written bytes.
7. **E-003 F7/F8 facts.** Randomising the partner suppressed the write or birth in all 8 draws on about half the identified loci
   (19/29 births). That is strong existence-dependence on the partner in NPE births, and it went unreported as a finding.
8. **Bellerophon's BEE facts that bear on the NPE phenomenon:**
   * state-free genomes arise with no payoff at all (ZERO 18/100 events; 4/100 persist to the end);
   * the partial-scaffold effect runs P90 > P75 for events but P75 > P90 for persistence;
   * the first state-free genome appears as early as tick 100 in every arm.
   None of this is in Nestor's records (s5.2).
9. **Archaeon TH-013.** An exact copier arose as the founder's first child (a fixed point of its imperfect copying map). The
   founder was not the replicator, and host execution was on the origin path. The "founder" of a lineage label need not be the
   organism with the capability. This is directly relevant to C-A3's "lineage founded by non-state-free donors".
10. **R-05 margin fragility** is absorbed, but the per-draw files are still uncommitted ("queued, low priority").

---

## 5. UNMINED EVIDENCE in other seats' outputs (and one in Nestor's own committed rows) that bears on NPE mechanism

### 5.1 The D0-vs-MKL split inside X-MAT's ENDOGENOUS verdict (DOSSIER-DERIVED from committed rows)
- **Source:** `roles/Nestor/campaigns/npe-frontier-2026-09-30/x_mat_internalize/results/<cell>_<seed>.json`, `tags[epoch ==
  endpoint].free_L`. RESULT.md reports only X, attributed_share and MUT. The per-class counts are in the rows. This is a read-only
  tabulation; no replay was run.

| run | orgs | D0 (founder) | MKL (made by L after D0) | MUT | XENO | L_share min over run | population XENO share, max over checkpoints |
|---|---|---|---|---|---|---|---|
| ffa6 27000012 | 1 | 0.328 | 0.062 | 0.562 | 0.047 | 0.02 | 0.948 |
| ffa6 27000020 | 19 | 0.199 | 0.356 | 0.431 | 0.014 | 0.82 | 0.202 |
| 7ae3 27000023 | 101 | 0.047 | 0.908 | 0.045 | 0.000 | 0.00 | 0.992 |
| ffa6 27000024 | 1 | 0.062 | 0.859 | 0.078 | 0.000 | 0.02 | 0.984 |
| ffa6 27000046 | 84 | 0.031 | 0.527 | 0.427 | 0.016 | 0.07 | 0.865 |
| ffa6 27000048 | 194 | 0.092 | 0.479 | 0.429 | 0.000 | 0.75 | 0.206 |
| ffa6 27000051 | 11 | 0.207 | 0.557 | 0.186 | 0.050 | 0.01 | 0.914 |
| ffa6 27000052 | 9 | 0.123 | 0.349 | 0.521 | 0.007 | 0.02 | 0.840 |

- **Data summary:**
  * The founder-material (D0) share of the state-free genomes in L is 0.03-0.33, median about 0.11.
  * MKL is 0.06-0.91, median about 0.50.
  * In 6/8 runs, non-L (XENO) material made up 0.84-0.99 of the population at some checkpoint. XENO was abundant, so X near 0
    was not forced by an empty class. That is a reachability point in X-MAT's favour.
  * In 2/8 runs (27000020, 27000048), L never fell below 0.75-0.82 of the population and population XENO peaked at about 0.2.
    The transplant alternative was weakly available there.
- **Reading (dossier):** the NPE internalization has material continuity in the sense of "not imported". But the state-free
  genomes are mostly bytes computed by L members after D0, plus mutation. Founder bytes are a minority. That is the same shape
  as X-CONTENT (13-25%).
  * Under F8, "descended from those founders" holds for a founder-material minority and a label-attributed majority.
  * What MKL means mechanically (literal operand writes, arithmetic results, register-derived values) is fixed by z8taint
    semantics. Here it matters, because a painter's LD (HL),n write and a copier's read-then-write tag differently only if
    z8taint propagates the source tag through the register.
  * The cheapest next step is an F8-style control on these same 26 replays: a planted foreign transplant into L, plus scoring
    the free_L genomes against a non-parental D0 founder set.

### 5.2 BEE's no-payoff state-freedom as a null NPE never ran
- **Data:** REPL-01 ZERO arm: 18/100 event runs and 11 under the alt ruler, where state-freedom earns nothing.
  POSTHOC_REPL01_EVENT_TIMING: ZERO 4/100 still have state-free genomes at tick 2000.
- **Reading (dossier):** C-A3-INTERNALIZE (8/144) was never run against a ZERO-world arm in NPE, where registers are always
  scaffolded. Bellerophon's K1 is exactly the null that separates "internalization because the scaffold is unreliable" from
  "state-freedom as a mutational by-product". In BEE the no-payoff rate was a fifth of the treatment rate, not zero. The same
  null in NPE is cheap; `reset_axis.py` already has ZERO. It is also the natural planted-comparison arm for the x_task_gate line.

### 5.3 Register state as the carrier: three seats' data converge
- **Data:**
  * Odysseus #803: 16/37 "do nothing" certified genomes copy only when handed the right registers.
  * Nestor's own W1 (H-D2-10): self-poisoning register state in 18/18 stalled donors.
  * Artemis P-11 RESULT s6: 41/57 donors never pass from a fresh state.
  * Bellerophon D2: under plain CARRIED, BEE's zero-dependent founder lineages die (0/24), while NPE's persist.
- **Reading (dossier):** C-A3's question, whether the organism internalizes the register scaffold, has an external population
  prevalence estimate (16 of 57 depend on host registers) that nobody has connected to the 8/144 rate. Also, NPE's CARRIED world
  lets zero-dependent lineages survive where BEE's does not. That difference is a mechanism clue: how NPE hands registers to a
  newborn (the overwrite keeps the victim's context?) is exactly the scaffold. It is also the point where Bellerophon's rebuild
  had to deviate.

### 5.4 Archaeon TH-013: what founder-lineage conservation looks like when measured properly
- **Data:** `ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/TH013_RESULT.md` and its dated correction. Over about 5,000
  generations, aligned founder material in the essential loci fell 0.85 -> 0.33, while isolated exact self-copy stayed at median
  0.83. The whole genome shifted by terminal NOP insertion and tail loss (offsets -5 to -11). 0x00 knockout undercounts essential
  loci (6 -> 10 with random-value knockout). R-01 adds that purifying selection fits better than drift (log-lik -39 vs -119), and
  that constraint moves.
- **Reading (dossier):** this is the only cross-engine time series of founder-material decay under function conservation. It
  gives NPE a concrete expected shape for C-CORE and for X-MAT's D0 share: early high, then a mutation-driven decline with the
  function kept. It also shows that C-CORE's per-position conservation count could be alignment-sensitive, if NPE genomes shift.

### 5.5 Data-as-code execution as a measured NPE property
- **Data:** E-003 NPE leg: "in NPE the copied bytes are executed BEFORE their final store", which makes most identified loci
  undecidable by a flip test (coverage 0.29-0.32). REPLICA1 F7: a leak changes the path.
- **Reading (dossier):** this is a mechanism statement about how NPE copying works (copy-then-execute interleaving). Other
  seats measured it; it is not written into FINDINGS. It predicts that NPE heredity rulers built on single-byte flips
  (CVT-R included) will have coverage limits at loci that are both data and code.

### 5.6 Artemis FR-011: the copy-op-free heredity count
- **Data:** 10/500 runs certify copying without block copy, and all are near-homopolymers (5 are 0x36).
- **Reading (dossier):** C-A3's state-free genomes are in DENSE / LDIR cells. Whether any internalization event involves a
  painter-class genome has not been checked with CVT-R or source diversity. The ARC3 lineage (c) passed CVT-R 8/8, but the 8
  C-A3 event genomes (ffa6-heavy) have not been CVT-R scored.

### 5.7 Replication-grade receipts exist for a C-A3 transfer test
- **Data:**
  * Bellerophon's sealed REPL-01 rows (300 runs, sha 701a26ae...);
  * 111/111 deterministic replays;
  * `receipts/POSTHOC_RECEIPTS_REPL01.json` with the per-arm G/FM trajectories at ticks 100/500/1000/2000;
  * a BEE register-world axis on main (35b2fde55, ee82457a4, 8a2390d82; default off, 88 tests).
- **Reading (dossier):** an aligned-material rerun of REPL-01's sealed runs, using a BEE equivalent of X-MAT tags or Archaeon's
  aligned probe, would turn "descent UNRESOLVED in BEE" into an answer at replay cost, with no new production. Neither seat has
  proposed it. This is the commensurable-ruler comparison errata R2 says is missing.

---

## Summary (10 lines)

1. P-11 is UNSOUND for heredity (Artemis #793) and NPE heredity is qualified by CVT-R (23/32, 83/100, 8/8; #891). Both are upheld and absorbed.
2. Odysseus #803: 3/57 certified donors self-copy, and 16/37 copy only with hand-given registers, so the capability sits in host state. Absorbed as a count, not linked to C-A3.
3. Bellerophon REPL-01 (BEE rebuild of C-A3): DISAPPEARS (K3) stands as the verdict of record, but the errata (c776cea6a, #1113) make descent UNRESOLVED. K3 could not pass, "chance-level" was false, and the BEE-vs-NPE contrast is withdrawn.
4. REPL-01's K1 (93/200 vs 18/100) survives only as transient appearance. P90 > P75 ran backwards to expectation, and REPL-02 found no dominance: RESIDUE_NOT_REPLICATED.
5. Harmonia audited X-MAT as SUPPORTED (minor; disclosed), downgraded REPL-01 to SUPPORTED_WITH_DEFECTS, and issued F8: a descent claim needs a content ruler that can PASS on a planted positive and a non-parental null.
6. Nestor has NOT absorbed REPL-01/02, F8, the side-1 hijack, AN3/AN4/AN8, TH-003/004, FF-11/14, source diversity, R-01/R-26 or TH-013.
7. Unmined (dossier-derived from committed X-MAT rows): in the 8 events, founder (D0) bytes are only 3-33% of the state-free L genomes (median ~0.11). Most ENDO is MKL, which is credited through the audited label itself, so X-MAT rules out transplant but only partly shows founder descent.
8. NPE never ran BEE's K1 null (a ZERO, always-scaffolded arm). In BEE, no-payoff state-freedom was a fifth of treatment, not zero. This is the cheapest missing control for C-A3.
9. Reusable primitives: CVT-R, Odysseus recert, Archaeon attribution v0 plus the reference tracer and the aligned TH-013 probe, and Harmonia audit_primitives, ancestry ruler and F1-F8. The NPE 58-62/64 "divergence" figure is itself a positional ruler and should be replaced by aligned or taint measures.
10. Open tensions: X-MAT vs F8, three unreconciled definitions of "descent", C-CORE relevance vs the purifying-selection null, design law vs shared design habit, and blinding hygiene for cross-seat replications.

Path: `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/dossiers/F_other_seats_external_view.md`
