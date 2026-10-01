# Atlas inference harvest -- digest: GROUP ensorain_bellerophon

Reader: fresh-context read-only reader, 2026-09-30. Repo: F:/Prometheus-worktrees/atlas-base-role (origin/main @ ab2fc8a4b).
Tags: RAN / OBSERVED / CONCLUDED / ATLAS_DERIVED (my own inference; hypothesis only).
Branch-only material is labelled BRANCH:<name>@<sha>. "BR-ENS" = BRANCH:ensorain/base-role-adopt-2026-09-23@26a490702.
"BR-C4" = BRANCH:bellerophon/c4-rmech-2026-09-30@164df3cdd.

---------------------------------------------------------------------------------------------------------------------

## 0 Coverage

READ (Bellerophon, BEE = prometheus/z80atlas Z80 soup + prometheus/toolbox kernel):
- roles/Bellerophon/STATUS.md (bcab1d5ff; STALE: currency 09-29, predates E-003 errata and REPL-01/02), WORK_STATE.json
  (50c7e5001; current, 09-30T18:16Z), calibration/LEDGER.md (6879b2236), journal 09-25, 09-26.
- repl_2026-09-30/: PREREG.md (74f72e805), SELECTION.md (19e758e7f), RESULT.md + ERRATA_REPL01 (6879b2236), RESULT_02.md (64d8d2d3f).
- e003_2026-09-29/: E003_BEE_RESULT.md, ERRATA_2026-09-30.md (d06059735).
- multiday_2026-09-26/: MULTIDAY_CAMPAIGN_REPORT.md (1c6bca786), FAILURE_LEDGER.md.
- coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md (6a0b9813e).
- forensics_2026-09-23/: GROUNDING_REPORT.md (2159c2e06), ERRATA_2026-09-29.md, POST_CAMPAIGN_FORENSICS.md s0-s3.1 (3efdacf7e).
- atlas_bee/RESULT_a1..a6 (933ee9f02) headline fields only.
- BR-C4: roles/Cosmos/c4/reviews/R-MECH_Bellerophon_INTERIM_2026-09-30.md.
- Branches: repl-internalize, e003-bee-ancestry, multiday-campaign, mwo-0001 have ZERO commits outside origin/main
  (fully merged). Only c4-rmech carries unmerged material.
READ (Ensorain, WTP tensor-world "Foundry"):
- roles/Ensorain/STATUS.md (7720539d4; STALE, currency 09-26), DEFECTS.md (51ddc856e), WORK_STATE.json on BR-ENS.
- ensorain/E0/E1/E1P5/E2 verdict heads, DIALS_SYNTHESIS (818882180), DIALS_RETRO, WTP-02/03 report heads,
  PREREG_WTP_LM01.md s1 + limitations (ee8cbe0c8).
- BR-ENS: arc3/reviews/INSTRUMENT_LINE_REVIEW_2026-09-30.md (full), arc3/RESULTS_PKGF_PROBE.md (s0-v7), lm01/ERRATA.md,
  arc3/THREADS.md (T01-T10), arc3/suff/RESULTS_S1_PILOT.md, arc3/reviews/T25_CSSR_REVIEW (s0-s2).
COMMS (scratchpad comms_since_0925.txt): #585-#734 (LM01 design thread, headers + #730/#731/#702-#704 bodies), #741, #748,
  #804, #808, #811, #841, #877, #882, #919, #946, #980, #1005, #1054, #1111, #1117, #1131, #1132 bodies; other
  Bellerophon/Ensorain headers.
NOT READ (reasons): OVERNIGHT_LEDGER_2026-09-19.md (103 KB, kernel TDD, low science yield); WORLDS_KERNEL_DESIGN v0.2-v0.4,
  TOOLBOX_*, ABI_DIFF (kernel design, not experiments); GROUNDING_PREREG and COUPLING_PREREG in full; ISSUE_AND_REPAIR_LEDGER
  (34 rows; only cited via reports); Ensorain WTP-01/02/03 reports beyond verdict sections; LM01 adversarial/pre-freeze
  reviews; lit/ raids (175 KB); PKG-F v8-v9b/W-DRIFT/W-MULTI details; LM02 PREREG/RESULTS files themselves (numbers taken from
  the INSTRUMENT_LINE_REVIEW packet); Ensorain journals; Archaeon's causal_lens V02_REGRESSION_REPORT (#741 source) and
  E003_SYNTHESIS; Harmonia audit sample 2; host-local M2 evidence (results.jsonl of all BEE campaigns) is not in git and
  cannot be read from here.

---------------------------------------------------------------------------------------------------------------------

## 1 Experiment ledger (most recent first)

| id / date | question | substrate | ruler | controls | n | OBSERVED | CONCLUDED (seat) | status | pointer |
|---|---|---|---|---|---|---|---|---|---|
| C4 R-MECH INTERIM (Bellerophon), 09-30 | does Cosmos C4 design separate explanation from restatement? | planted continuous "Reservoir" family, 60 world-k rows | Cosmos C3 certify.py (Certificate A), T3-DOWN, B-USE | none needed (attack) | 60 rows, 48 determinate | REL@q rule BA 0.910 vs A; T3-DOWN BA 0.500; B vs A agree 47/48; T3-DOWN REGISTERED 60/60 | "F1 BLOCKING ... restates Certificate A"; "F2 BLOCKING Certificate B reconstructs A's causal contrast" | interim, no verdict | BR-C4 R-MECH_..._INTERIM s F1-F6 |
| E-BEL-REPL-02, 09-30 | does the REPL-01 residue (state-freedom dominates under partial scaffold) survive M1-M6 transforms? | BEE register world | state_free.py + strict ruler, label-free dominance | M6 RANDOM positive arm | 750 runs, 9 arms | M1 dominance P90 1/50 vs ZERO 0/50; M6 RANDOM 0/50, alive 8/50 | "RESIDUE_NOT_REPLICATED (ABSENT)"; "dominance readout was never shown to be reachable" | closed, positive arm failed | RESULT_02.md s0,s3 (64d8d2d3f) |
| E-BEL-REPL-01, 09-30 | rebuild NPE C-A3-INTERNALIZE (endogenous internalization of register init) in BEE + kill battery | BEE, 256 cells, lifespan 40, 30 transplanted ZERO_DEPENDENT founders | G (genetic lineage label), FM (founder content >=16/64), causal L | K1 no-payoff ZERO arm, K4 alt entry vectors | 300 runs (100 pairs x ZERO/P90/P75) | EVENT G: ZERO 18, P90 57, P75 36; K1 93/200 vs 18/100 p 6.6e-7; K4 86/93; K3 FM 0/93 | verdict of record "DISAPPEARS (K3)"; after errata "descent component is UNRESOLVED in BEE" | closed, reinterpreted | RESULT.md s1; ERRATA_REPL01 R1 (6879b2236) |
| E-003 BEE leg (C-001, owner Archaeon), 09-29 | is BEE's copy-descent record adequate (byte-level ancestry) on run r022153? | BEE r022153, 32,827 births | bee_tracer 823cbef1 (per-byte labels, flip test) | fixtures 28/28, reference tracer agreement | 32,827 births, 2,878,487 written loci | Q8c 0.00115 [0.00098,0.00134]; P1 own-index 0.962; P2 native label wrong vs copy-descent 0.504 [0.456,0.552] n 395 | first "VALIDATED (A and B)"; corrected: "confirmatory ... ALTERED"; verdict of record OPEN (operator) | closed, verdict open | E003_BEE_RESULT s1a,s3,s4; ERRATA X1 (d06059735) |
| E-BEL-MD multi-day, 09-26..28 | does coupling climb a task ladder, evolve protection, repair? | BEE physics v3, 20k ticks | sr_depth>0 SR label + task competence | OFF / SHUFFLED / YOKED per lane | 4,160 runs, 47.1 h | LADDER1 ON 58/320 vs 0,1,0; COPIER 36/240 vs 4,2,2; LADDER2 0/240 all arms; Q2 +0.0115; Q3 4.7% | tags LADDER_CLIMBED, PROTECTION_EVOLVED; "'Task-specific protection' is suggested, not established" | closed/merged | MULTIDAY_CAMPAIGN_REPORT s1-s3 (1c6bca786) |
| Coupling campaign (physics v3), 09-24..25 | does correct computation causally raise reproduction? | BEE v3, 500 ticks | paid births, competence, r_cc | A8 positive 40/40; OFF, SHUFFLED, YOKED, NOCOMP, RANDOUT, etc. | 11,657 runs | P1 40/40 pairs; P2 149 vs 0; P3 gap 0.9987; P5 reversed (ceiling); P6 4/60 vs 0/60 p .125; B-cop ECHO K40 29/150 vs 6/150; B-rand 0/3,200 | READY_FOR_MULTIDAY; "core effects are MAINTENANCE of seeded code; ACQUISITION evidence is ECHO only" | closed | COUPLING_CAMPAIGN_REPORT s1,s2,s5 (6a0b9813e) |
| Grounding round, 09-23 | which of the 72 h campaign's flags survive fresh preregistered tests? | BEE v2 repaired physics | traced replay SR by provenance (own bytes, own code) | 8 control cells 20/20; replay 606/606 | 12,130 runs | G1 pooled 55/2,400 = 2.3%; G2 63/160 (later 21/83 per seed); LDIR off 0/300 vs 8/300; POLLINATION v1/v2 extinction 0/150 vs 148/150; G3 EXTERNAL-only 178 vs ENDOGENOUS-only 2 | "spontaneous own-code self-replication CONFIRMED_CAUSAL"; "reproduction and computation are antagonistic, not coupled" | closed; 2 errata | GROUNDING_REPORT s1,s3,s8 (2159c2e06); ERRATA_2026-09-29 |
| Post-campaign forensics, 09-23 | adjudicate 1,629 high-value flags of the 72 h campaign | 63,247 runs | traced replay, geometry audit | identity null, paired re-measurement | 63,247 | 5 flag classes: 2 FALSIFIED, 1 INSTRUMENT_FAILURE, 2 CONFOUNDED/DETECTOR_ONLY | "all five historical flag classes collapsed" | closed | POST_CAMPAIGN_FORENSICS headline, s3 |
| ATLAS->BEE pilot a1-a6, 09-19 | do 6 Atlas experiments (Nestor/Archaeon) keep their disposition when rebuilt natively in BEE? | BEE kernel | per-experiment | replay_ok all six | 6 | a1 INVERTED, a2 CHANGED, a3 CHANGED, a4 ABSENT, a5 ABSENT, a6 PRESERVED | "Every case exposed a mechanism the source ecosystem could not" | closed | STATUS.md ATLAS->BEE block; atlas_bee/RESULT_a*.json |
| LM02 bounded window assay (Ensorain), 09-30 | does any finite window preserve competence, substrate ordering and anomaly flag at <=10% stale? | 12^3 tensor fields, 11 regimes x 8 worlds | AC = -log10(MSE/var); Kendall tau; stale fraction | REF_HOLD held-out reference 83/88; ORACLE; FULL | 88 worlds | no window >= 6/8 in any regime; HIER HIDDEN stale .124 > .10; data-availability loss .36-.95 AC | "WINDOW_NOT_SUPPORTED"; "POP_VALUE_REQUIRES_REPRESENTATIVENESS" | closed (dev, precommitted) | BR-ENS INSTRUMENT_LINE_REVIEW s0,s5 |
| PKG-F strict observability gate, 09-30 | can a drift gate be leak-free? | 48 fresh worlds (9_813_xxx) | stale records admitted | old soft gate | 48 | DRIFT 24/79854 (.0003) vs soft .299; MULTI .0002 vs .698; verifies 4% of valid old records | "it acts as a recent window"; forfeits +.60 AC in stationary worlds | done (dev) | BR-ENS INSTRUMENT_LINE_REVIEW s5a |
| PKG-F v6 / v6-ctrl / v7, 09-29 | does restoring discarded records help generalization? | LM01 F3-like worlds, rho sweep | dAC vs S on STALE vs GEN splits | stationary twins, substrate-matched control | 8 worlds/cell | STALE split -1.153 (rho 1) .. +0.856 (rho 0); GEN split -0.137 .. -0.005 | v6 "retention pays" WITHDRAWN; "a statement about RECALL, not generalization" | falsified reading, clean dev result | BR-ENS RESULTS_PKGF_PROBE v6 ctrl, v7 |
| WTP-LM01 (frozen, never launched), 09-25..28 | does exact persistent retention underperform bounded coarse state? | WTP tensor worlds F1-F5 x L1-L3 | L-K, L-R, reservoir ladder, SUFFSTAT | E6 positive control, cheat fixtures | 0 campaign rows | dev: L-K ~0 AC on never-seen; E6 passes in 8/29 testable strata (#716) | "an UNFIRED F-B is not support" (#730); HOLD by operator | frozen, not launched | PREREG_WTP_LM01 s1, limitations (ee8cbe0c8); comms #715-#716, #730 |
| T25 CSSR, 09-29 | can a learner not told the state count find the causal state? | answer-keyed binary processes | excess log-loss vs exact Bayes | window STAT(k) baseline, held-out random machines | 16 seeds + 24 held-out | 4-world ladder 14/14 predictions; held-out 2/6 refuted at T=4000 | "NOT shown to be a general causal-state discoverer at small T" | closed dev | BR-ENS T25_CSSR_REVIEW s0 |
| S1 sufficiency pilot, 09-28 | where does "discarding helps" appear with exact oracles? | Even, golden mean, order-k, key-value | excess log-loss vs Bayes | exact Bayes | 16 seeds | Even: no window reaches Bayes, interior optimum k=6 (.060); key-value: 64/256/1024 slots TABLE 1.512/.728/.040 | "discarding is a variance-control device ... NOT a sign that the extra information is harmful" | pilot, replicated (Fabric) | BR-ENS RESULTS_S1_PILOT findings 1-5 |
| WTP-03 substrate collider, 09-24..25 | find candidate learning physics | WTP worlds, 38,000 proposals | preregistered chain + N6 post-data check | N0-N5 cheap nulls; N6 tuned batch completion | 181 admitted | 9 flags; N6 beats all 9 (e.g. q0 2.578 vs 4.856) | "KNOWN PHYSICS -- bounded online MATRIX / TENSOR COMPLETION" | closed | ENSORAIN_WTP03_REPORT VERDICT (a65d27ced) |
| WTP-02, 09-24 | ditto | WTP | frozen scorer | -- | -- | sole specimen = one-float running mean | frozen EXPAND; operator PARK/REDESIGN | closed | ENSORAIN_WTP02_REPORT (42c190ae3) |
| Dials rounds 1-4, 09-24 | are competence dials coupled? | WTP ALS learners | two-way ANOVA | synthetic additive/coupled grids | ~19,300 lives | one replicated coupling: scratch x start F 11.39 p 3.9e-5 | "ONE organism-intrinsic coupling replicated ... An amplifier, not a crossover, not a phase transition" | closed | DIALS_SYNTHESIS (818882180) |
| E0/E1/E1.5/E2, 09-23 | TT memory advantage; structure discovery | tensor worlds | held-out R^2, EFF | planted TT positive control | 15,760 / 10,081 / 12,960 / 4,800 lives | E0 PC R^2 .007; E1 PC fail; E1.5 TT EFF 8.63 vs LOWRANK 2.03 at 192; E2 G_ID TT .20/.15 | INDETERMINATE / INDETERMINATE / CLOSE(B) + operator "INTRIGUING" / INDETERMINATE, "NO for cross-family ... discovery" | closed | E*_VERDICT.md |

---------------------------------------------------------------------------------------------------------------------

## 2 Mechanisms (seats' words)

| mechanism (seat's words) | seat | claimed level | my judged level (ATLAS_DERIVED) | synonyms elsewhere |
|---|---|---|---|---|
| "Contingent earning selects FOR task code that would otherwise be lost to mutation" (coupling s2) | Bellerophon | strongest surviving mechanism, causal (P1, P2) | strong for MAINTENANCE of seeded code; acquisition only ECHO/INC | "selection maintenance", "use-it-or-lose-it", cargo erosion (Archaeon thread) |
| spontaneous own-code self-replication "requires LDIR and the undefined-byte slide" (GROUNDING s8) | Bellerophon | CONFIRMED_CAUSAL | causal for origin access; "own-code" is LOCATION-defined (#741), so counts are ruler-dependent | supplied copy primitive; NPE LDIR/LDDR encoding accessibility (Nestor C-DENSE-COPY #742) |
| "replication basin is shallow and wide around any tape that already has the setup" (HISTa diagnosis) | Bellerophon | exploratory | plausible; 124/126 rescues by new-position copy op | one-mutation-away copier; "short ramp ending in a small step" |
| "reproduction and computation are antagonistic, not coupled" under endogenous physics (G3, G4) | Bellerophon | CONFIRMED_CAUSAL (G3) | solid in v2 physics; superseded by v3 coupling design | copier overwrites input region (G4 diagnosis) |
| P1 "world-made copies" drove POLLINATION persistence | Bellerophon | CONFIRMED_CAUSAL defect | solid (0/150 vs 148/150) | environment-performed replication; donor-by-world |
| heritable PARASITE lineage: "execute into the host's copy loop" (#841); "occupant-performed children are relationally, not autonomously, capable" (E-003 s6) | Archaeon dry run / Bellerophon post-hoc | POST-HOC | real observation (other class relational .733 vs isolated .0002), post-hoc only | relational identity (thr-c64dca3118a1); Tierra parasite |
| BEE native `material` label "is not a descent label" (E-003 P2) | Bellerophon | engine-native finding | holds (0.504 of target-labelled births) | resemblance label; slot lineage; IBD correction |
| "scaffold-dependent emergence of state-freedom" (REPL-01 s3) -> downgraded to "transient state-free appearance under a partial register scaffold" (REPL-02 s6) | Bellerophon | weak | weak; dominance ABSENT but readout unreachable | internalization of register initialization (Nestor C-A3) |
| "keep + regime-gate >= discard on recall; neutral on novel cells" (PKG-F v7) | Ensorain | clean dev result | solid within dev design | segregate-not-erase (latent cause inference, cited in THREADS T07) |
| "discarding is a variance-control device whose value vanishes as data grow" (S1) | Ensorain | pilot, replicated | solid in answer-keyed worlds | finite-sample regularisation; bias-variance |
| "data availability ... the binding constraint" after change (LM02 s8) | Ensorain | dev | real (attainable loss .36-.95 AC in every changed world) | learning-time/lifetime ratio |
| TIMESCALE SEPARATION x REPRESENTATION CORRECTNESS amplifier (Dials) | Ensorain | replicated on fresh seeds | moderate | consolidation depth; slow weights |

---------------------------------------------------------------------------------------------------------------------

## 3 Failures and invalidations

| item | ruler/defect | LOST (interpretation) | SURVIVES (raw observation) | pointer |
|---|---|---|---|---|
| REPL-01 K3 | founder-snapshot content test (FM >= 16/64) had no demonstrated way to return SURVIVES: FM falls to ~0.01 by tick 500 in ZERO too | "the kill is real", "chance-level", "ZERO material continuity", "BEE-specific", BEE-vs-NPE contrast | K1 93/200 vs 18/100; paired sign P90 vs ZERO 46 vs 7, p 2.0e-8; LCS median 2 vs random null 1 | ERRATA_REPL01 R1, R2, R7 |
| REPL-01 K1 | EVENT scored the LAST checkpoint with >= 1 state-free genome, not the final one | "state-free genomes ... dominate" | state-free at tick 2000: P90 8/100, P75 17/100, ZERO 4/100 (post-hoc) | RESULT_02 s4B |
| REPL-01 blinding | merge of main 67 min before freeze imported Nestor's ENDOGENOUS verdict (ae38658fe) | "sealed", "not read" | frozen design did not reference X-MAT; seat's prediction (K1 kill) was wrong | ERRATA_REPL01 R3 |
| REPL-02 | RANDOM positive arm extinct 42/50 | ABSENT as "shown absent" | M1-M5 counts 0-1 per 50 | RESULT_02 s3 |
| E-003 verdict | C4.2 adopted 17 min after spec owner's dry run showed "P2 holds -> ALTERED"; review prompts asserted C4.2 | VALIDATED as confirmatory | Q8c 0.00115 amendment-independent; P2 0.504 | ERRATA X1, X2 |
| E-003 Q4 host arm (DEF-BEL-004) | kept "own stores" condition | host-assisted capability 0.817 / 0.007 | post-hoc relational: other class .7331, occupant share .9741 | E003 s6; ERRATA X4 |
| E-003 round-trip | only 4 quantities recomputed from v0 | "losslessly", "every Q expressible" | 32,827 records schema-check | E003 s3; ERRATA X3 |
| Grounding G6a (DEF-BEL-001) | classifier branch "init" unreachable | "160/160 BUILT_BY_COPY" | 103/160 copy-born; 57 initial writers, 26 unmodified | ERRATA E1 |
| Grounding G2 (DEF-BEL-005) | seed formula had no cell term | 63/160 = 39.4% | unique 33/115 (28.7%); per-seed 21/83 (25.3%) | ERRATA E2 |
| "replication shows no task dependence" | task cells shared seeds; task inert under IMPLICIT | task independence | G1T 5 of 6 task cells run-for-run identical | ERRATA E2; GROUNDING s3 |
| Coupling/MD SR label (DEF-BEL-003) | sr_depth>0 = birth event, not capability | "competent SR" as a capability | ON acquisitions 108/109 real self-copiers; controls 6/9 label-carriers | MULTIDAY s3; #748, #946 |
| MD analysis (DEF-BEL-002) | `holds` not conditioned on instrument_ok | none (instrument_ok TRUE) | all dispositions | MULTIDAY s4 |
| 72 h campaign flag classes | identity null scored "better" 60.0% vs 1.3% control; P1 world copies; promotion non-discriminating (69% of runs reach score 2) | all 5 flag classes | raw rows replay bit-for-bit | POST_CAMPAIGN_FORENSICS s1.3, s3.2 |
| PKG-F v6 | "never_seen" test cells are 87-89% earlier-episode cells | "keep-and-ignore beats discard" as generalization | STALE-split recall curve -1.15..+0.86 | RESULTS_PKGF_PROBE v6 ctrl (BR-ENS); lm01/ERRATA E-4 (BR-ENS) |
| PKG-F v3 | residual-segmentation "discovery" | discovered recency | artefact of substrate retention recency (v4) | THREADS T04 (BR-ENS) |
| LM01 prereg cycle | D1-D11 (e.g. D4 absolute selectivity readout "certifies a random merge"; D8 full-read check blind to a -rec subsample; D11 IM-rate swap is a lookup table) | several steward readouts | fixtures | comms #625, #651, #709, #727 |
| WTP-01/02/03 | variance-collapse metric artefact; one-float running mean; tuned batch completion beats all 9 | "candidate physics" | 181/38,000 admitted; 9 flags | WTP reports; STATUS s campaign line |
| E0/E1/E2 positive controls | planted TT failed the gate (learner could not build it) | any world verdict | E1.5 later: TT EFF 8.63 vs LOWRANK 2.03 with latent order + 10 sweeps | E0-E2 verdicts |
| WTP REPLICATED (DEF-ENS-002) | replay_ok never gates REPLICATED | none for WTP-01 (35 rows, 0 false) | -- | DEFECTS.md |

---------------------------------------------------------------------------------------------------------------------

## 4 Rulers

| ruler | engine | sees | cannot see / audit | pointer |
|---|---|---|---|---|
| SR "own code" (copy op with pc < L; own_steps) | BEE traced replay | writes executed from the writer's own tape LOCATION | self-copied code executed from the partner window: r038751 27,083 of 28,163 location-foreign births are own MATERIAL (1,726,650 writes by self-copied code vs 941 by original window code); r016299 17,501 own / 8,166 foreign / 13,158 unresolved. SR not recounted | #741; Artemis R-11 "BEE SR criterion is location-based" (#877) |
| sr_depth > 0 "competent SR" | BEE world.py | a birth event of the writer | isolated capability; 20/68 coupling origins do not self-copy (#748); grounding label holds 1,414/1,425 (#804) | DEF-BEL-003 |
| G (Org.glineage) | BEE | resemblance-assigned genetic lineage at each birth | material descent; REPL-01: G ~0.9-0.95 of population by tick 500 while FM ~0.01 | RESULT.md s2 (withdrawn reading, observation stands) |
| causal L (Org.lineage) | BEE | slot/causal lineage | transfers on 1-byte ENDOGENOUS_PARTIAL writes (pair 900: L_share 0.0 vs G_share 1.0) | PREREG D3 |
| native `material` label | BEE | resemblance | copy-descent writer: disagrees in 0.504 of target-labelled births | E003 P2 |
| bee_tracer 823cbef1 | BEE (E-003) | per-byte data/ctrl/addr/exec deps, flip-tested | per-byte precision of dependence sets only 0.13-0.23 (declared over-approximation); agreement needed post-production C11 | E003 s2 |
| FM founder-content (K3) | BEE REPL-01 | positional identity to founder tape | shifted copies; descent-with-turnover; no non-parental-founder null run | ERRATA R1 |
| STATE_FREE (two fixed random entry vectors) | BEE REPL-01 | competence from 2 entry states | K4 alt vectors are "the same kind of ruler ... weak against self-initialising replicators" | ERRATA R6 |
| r_cc heritability / P5 | BEE coupling | copy fidelity | protection (ceiling ~0.999 both arms) | coupling s1, s5 |
| geometry beneficial-density scan | 72 h campaign | -- | identity null "better" 60.0% | FORENSICS s3.2 |
| tasks.verify_tape | BEE | task check | ignores run chemistry (ldir/undefined_op) | #804 |
| Certificate A/B, T3-DOWN, SYSID REL@q | Cosmos C4 (Bellerophon attack) | -- | T3-DOWN registers every continuous world (60/60); B = A's contrast | BR-C4 F2, F4 |
| AC, L-K, L-R, SUFFSTAT | Ensorain LM01 | persistent vs transient contraction | L-K ~0 on never-seen => F-B strict near-zero power in latent families; (sum,count) table reproduces L-R exactly | PREREG_WTP_LM01 s1, limitations; #730 |
| E6 positive control | Ensorain LM01 | eviction-policy value | passes 8/29 testable strata (#716); Artemis R-05: 10/41 | #716, #882 |
| "never_seen" test split | Ensorain LM01 F3 | cells unseen in FINAL episode | 87-89% were seen earlier -> measures stale recall | lm01/ERRATA E-4 (BR-ENS) |
| REF_HOLD instrument self-check | Ensorain LM02 | whether a 4th reference passes the same preservation criteria | -- (passed 83/88, 94%) | INSTRUMENT_LINE_REVIEW s0 |
| Markov bound (PKG-F-HIER) | Ensorain | tested cells | untested cells (exchangeability assumption; HIDDEN .124) | ibid s7 |

---------------------------------------------------------------------------------------------------------------------

## 5 Repairs (what changed, did the outcome move)

| repair | from -> to | outcome moved? | pointer |
|---|---|---|---|
| v1 -> v2 physics (remove P1 world copies) | POLLINATION world-made copies -> none | yes: extinction 0/150 -> 148/150; spontaneous 20.0% -> 1.3% | GROUNDING s3 G7P1 |
| SR by provenance (traced replay) | v1 spontaneous_replication trigger -> SELF_REPLICATION class | 156/502 trigger runs (31%) were false positives | FORENSICS s3.1 |
| v2 -> v3 physics (computation -> copy resource coupling) | no pathway -> contingent paid births | yes: P1 40/40, ECHO acquisition 29 vs 6/150 | COUPLING s1-s2 |
| measurement speedup (verify_exact + stop_at_first_out) | 77% of cost in competence tracker | byte-identical, 2.8x faster | MD FAILURE_LEDGER MD-F1 |
| Q2 eligibility | isolated self_copy -> task competence (pre-freeze) | made Q2 measurable | MD-F2 |
| E-003 prereg v1->v5 + C1-C11 | four reviewer kills before running; C4.2 post-exposure | verdict ALTERED <-> VALIDATED depends on it | #841; ERRATA X1 |
| E-003 run draw | r004041 (#811) -> r025144 (#817) -> r022153 (#824, r025144 "non-replicating") | the commissioned run was replaced twice | #811, #817, #824, #841 |
| REPL-01 deviations D1-D3 | random start -> transplanted founders; CARRIED -> P90/P75; L -> G | the chosen primary label G was the one that failed | PREREG s3 |
| LM01 steward cycle v0.1 -> v0.3.2 | D1-D11 + R-c, H-rec, dual matching, one ALS rule | frozen but never launched | #625-#734; STATUS |
| PKG-F detector v3 -> v9b -> strict observability gate | residual segmentation -> model-free same-cell detector -> propose+veto -> equivalence test | leak .30/.70 -> .0003/.0002; value forfeited in stationary worlds | RESULTS_PKGF_PROBE; INSTRUMENT_LINE_REVIEW s5a |
| LM02 criteria (3 pre-commit changes, all easier for windows) | 1 ref -> 3+1; per-substrate -> world flag; full-life ref -> ATTAINABLE | no: windows still failed everywhere | INSTRUMENT_LINE_REVIEW s4 |
| E1 -> E1.5 | observed order / 2 sweeps -> latent order / 10 sweeps | yes: TT beats LOWRANK ~4x per parameter at 192 | E1 annotation |

---------------------------------------------------------------------------------------------------------------------

## 6 Primitive-level interventions

| primitive | intervention | outcome change | pointer |
|---|---|---|---|
| copying (supplied copy op) | LDIR off; LDIR cost x4; undefined -> HALT | spontaneous SR 8/300 -> 0/300 in each | GROUNDING s3 P8 |
| copying (seeded) | LDIR cost x4 on seeded copier | sustained 57/60 -> 1/60 | ibid |
| copying (ablation of copy bytes) | NOP every LDI/LDIR/COPYALL in 345 historical origins | still SR in 126 (36.5%); 124/126 by a new-position copy op | GROUNDING s5 |
| heredity / reproduction mode | EXTERNAL vs ENDOGENOUS reproduction | verified task reached EXTERNAL-only 178 vs ENDOGENOUS-only 2 | GROUNDING s6 |
| heredity (world-performed copies) | POLLINATION v1 vs v2 | extinction 0/150 vs 148/150 | GROUNDING G7P1 |
| energy/resources (payment) | ON vs YOKED (same total bonus, non-contingent) | extinction 1 vs 67 of 150; competence .77 vs 0 | COUPLING s1-s2 |
| energy (base income) | IMPLICIT pressure: inflow never limiting | task causally inert (G1T identical across 5 task cells) | GROUNDING s3 |
| reset / initialization (registers) | ZERO (BEE historical) vs CARRIED vs P90/P75 | CARRIED: zero-dependent founder lineages persist 0/24 (pilot 2); p=.9 5/12, ZERO 10/24; P90 G-events 57 vs ZERO 18 | REPL PREREG s3 D2; RESULT s1 |
| mutation supply | MED / LOW / VLOW | access 8/3/4 of 300 (indistinguishable); evolutionary activity 60 -> 48 -> 11 of 60 | GROUNDING s3 P8 |
| selection (admission) | promotion score >= 2 (69% of runs) | promotion steered allocation to the P1-inflated topology (NICHES_POLLINATION 9,655 runs) | FORENSICS s1.3, s1.5 |
| selection (payment of partial solvers) | LADDER2 pays INC/ECHO tapes that answer COND_ONE ~half the time | COND_ONE acquired 0/960 | MULTIDAY s2.1 |
| topology / locality | WELL_MIXED vs LOCAL/NICHES/GRAPH | extinct 73% vs 95-100% | GROUNDING s3 G7 |
| memory/state (retention) | keep exact records + regime gate vs discard | recall -1.15..+0.86 by obsolete fraction; generalization ~0 | RESULTS_PKGF_PROBE v7 (BR-ENS) |
| memory (window size) | N/12..N/2 windows | competence passes 0-25 of 88; contamination rises to .26-.39 | INSTRUMENT_LINE_REVIEW s5b |
| memory (population evidence) | HIER stratified bound | STAT recovery .76; HIDDEN stale .124 | ibid s5c |
| encoding (mode order) | correct vs random TT mode order | scratch x start coupling +0.87 vs +0.19 NLMSE | DIALS_SYNTHESIS |
| time/gating (consolidation timescale) | scratch level 58/181/430 | see above | ibid |

---------------------------------------------------------------------------------------------------------------------

## 7 Buried signals

1. OBSERVED, never followed up: 9% of all births in trigger runs (2,319,892) were "written by partner code the writer ran
   into" and were EXCLUDED from SR by the own-code criterion (FORENSICS s3.1). #741 shows the own-code criterion is
   LOCATION-based and most location-foreign writes in r038751 are self-copied code. So an unknown share of the excluded 9%
   may be genuine self-replication. Bellerophon filed #741 under DEF-BEL-003 but no SR recount by material exists in git.
2. OBSERVED: under plain CARRIED registers, zero-dependent BEE founder lineages die out (pilot 2: 0/24; pilot 3: p=.25 0/12
   ... p=.9 5/12; ZERO 10/24) (REPL PREREG s3 D2). Used only to justify the P90/P75 deviation. ATLAS_DERIVED: this is a BEE
   instance of Nestor's "self-poisoning register state" (C-STATELESS-FFA6, fresh state raises runaway-given-donor 0.33 ->
   0.81, #742). Two engines, same direction: carried execution state kills copiers that expect a reset.
3. OBSERVED: REPL-01 post-hoc LCS median 2 vs random null 1, and 2/18 ZERO, 1/36 P75 runs had >= 80% founder-like
   state-free genomes (ERRATA R1). Withdrawn from "chance-level"; the non-parental-founder null that would decide it was
   never run.
4. OBSERVED: dose direction reversed: P90 (57 events, 0.78 per persisting run) > P75 (36, 0.71) > ZERO (18, 0.21) for
   EVENTS, but persistence to tick 2000 goes P75 17 > P90 8 > ZERO 4 (RESULT s1; RESULT_02 s4B). Two readouts rank the
   arms differently.
5. OBSERVED: E-003 dry-vs-production drift on identical births (Q8c 0.0003 vs 0.00115; transmission 30,945 vs 31,401)
   is "between pipelines" and "The owner has not traced its exact cause" (E003 s8).
6. OBSERVED: 0.169 of TRANSMISSION-class children carry writer material without isolated capability (E003 s5 Q4); 0.124 of
   all births are relationally but not isolated capable (ERRATA X4). A relational-reproduction class sits under the
   VALIDATED/ALTERED argument.
7. OBSERVED: coupling K40 ECHO: 7 of 12 SURVIVES_WITHOUT_COUPLING_OR_TASK AUTO candidates; "the base income alone keeps
   copiers viable". MD s2.2 hypothesis "the effect needs a base income that keeps pure copiers alive" is untested.
8. OBSERVED: LADDER2 non-competent-earner share 1.0 (every paid correct output from non-COND_ONE-exact tapes): partial
   solvers are paid for half-correct answers, likely flattening the gradient (MD s2.1). The proposed fix (do not pay partial
   solvers) is not run.
9. OBSERVED: G6 origin timing: 87/160 origins at tick <= 41 while initial organisms live; after E1, 26 were unmodified
   initial random tapes that replicated (ERRATA E1). Artemis R-26 estimate: null 4.5e-5 per tape (#877). Unreplicated
   claim that random 64-byte tapes self-replicate outright at a nontrivial rate.
10. OBSERVED (Ensorain): LM02 data-availability gap (.36-.95 AC) is the largest loss in every changed world and "belongs to
    no memory policy"; mid-ramp detector beats the oracle boundary (RAMP20 5/8 vs 1/8). Parked as a WTP-04 axis. Artemis
    FR-081 (#1131): 0/181 WTP-03 worlds have lifetime <= 600, so the learning-time/lifetime ratio is unobservable in
    existing data.
11. OBSERVED (Ensorain S1): key-value long tail: recency beats random eviction at equal capacity because recency
    correlates with query distribution (a world property). Only case of selective > random retention at matched capacity.
12. OBSERVED (Ensorain dev #730): S-cp capacity ladder non-monotone (cap 1024 -> AC .02 between 1.82 and 1.28); S-lowrank
    degrades at very large caps. Filed as dev facts.
13. PARKED: E1.5 operator ruling "INTRIGUING -- WORTH EXPLORING" (TT correct order beats LOWRANK) left PARKED intact after
    E2 closed structure discovery.

---------------------------------------------------------------------------------------------------------------------

## 8 Contradictions and cross-engine hooks

Inside the group:
- E-003 BEE verdict: ALTERED (pre-exposure rules) vs VALIDATED (post-exposure C4.2/C4.4/NO_MATERIAL). Operator decision
  E003-BEE-LABEL is open (WORK_STATE operator_decisions_required; #1044, #1048, #1075).
- REPL-01 frozen verdict "DISAPPEARS (K3)" stands while the errata says K3 "had no demonstrated way to return SURVIVES".
  The frozen label and its own errata point opposite ways on what was shown.
- REPL-01 K1 SURVIVES vs REPL-02 "K1 ... was mostly TRANSIENT"; REPL-02 asks the reviewer whether K1 SURVIVES is itself
  an overstatement (RESULT_02 s7 Q2). Unanswered in git.
- SELECTION.md says the X-MAT verdict "is read before the BEE analysis is unsealed"; PREREG s0 says not until BEE outputs
  are sealed. Both then superseded by ERRATA R3 (the verdict was in branch history before the freeze).
- Ensorain: #702 reported ENVGATE-02 contention slowing L3 ~2x; #704 CORRECTION: "no ENVGATE contention (it completed
  02:50Z) ... sweep slowness cause untested". Separately, Bellerophon's coupling campaign DID co-run with ENVGATE-02 for
  38.9 min (COUPLING s6), recorded with no pause events.
- Ensorain STATUS.md on main (currency 09-26) and Bellerophon STATUS.md (09-29) are stale relative to WORK_STATE.

Cross-engine (text names the other engine):
- NPE (Nestor) C-A3-INTERNALIZE vs BEE REPL-01: same event signature appears in BEE (G-label events 93/200 vs 18/100)
  but BEE descent UNRESOLVED; NPE X-MAT says ENDOGENOUS 8/8 (median foreign share 0.020; MUT bytes 18-56%, #1054).
  Rulers not commensurable (X-MAT = taint attribution to any L material over time; K3 = founder snapshot) (ERRATA R2).
  NPE's own founder-descended genomes differ at 58-62 of 64 bytes (ERRATA R1, citing roles/Nestor/FINDINGS.md), and X-MAT
  reads whole genomes, not the register-setting bytes (#1054). ATLAS_DERIVED: NEITHER engine has shown that the
  register-initialising bytes themselves descend from the founder; both claims rest on lineage bookkeeping plus
  whole-genome attribution. NPE ENDOGENOUS = "not imported from outside L"; it is not "founder material retained".
- Parallel of note (ATLAS_DERIVED): Nestor ARC3 says register initialization is internalizable and "SELF-location not
  internalized ... 280 of 280 SELF-free copiers are tape-anchored" (#808). BEE's VM zero-resets registers on every
  execution (SELECTION F4), i.e. BEE supplies initialization always; BEE only shows state-freedom appearing when the
  scaffold is partly withdrawn (P90/P75), and only transiently.
- Archaeon #741 (location vs material) + Archaeon E-003 synthesis (#980) + Odysseus #748/#804 + Artemis R-11/R-26 all
  audit BEE rulers. Artemis R-26: the "three independent worlds make it a design law" premise fails because every
  recurrence vanishes when the shared supplied copy op is removed (BEE LDIR off 0/300 vs 8/300; NPE BYTEWISE 10/500 vs
  47/531) (#877).
- Nestor W1 C-DENSE-COPY (1-byte LDIR/LDDR alias: donor runs 1/64 -> 39/64, #742) and BEE P8 (LDIR off -> 0/300) are
  the same primitive (block copy) seen from opposite sides: add encoding accessibility vs remove the op.
- Archaeon ENVGATE-02 BAND0/R128 excess was considered and rejected as a Bellerophon replication target (~50 core-h,
  rows off-repo) (SELECTION.md runner-up).
- Artemis FR-091 (#1132): scalar objective changes ENDOGENOUS_COPY summaries 99/100 pairs but not SR origin (1 vs 1);
  "Unowned at the program level" because BEE is a blind lane for Artemis routing.
- Ensorain "strict B can't win on generalization by construction" (Aporia #731) is the tensor-world twin of Bellerophon's
  K3/REPL-02 reachability defect (see s9).
- Cosmos C4 (BR-C4): Bellerophon finds Certificate B reconstructs A's causal contrast (47/48) and a guard-compliant
  coordinate restates A (BA .91); bears on any Cosmos claim of "certificate independence".

---------------------------------------------------------------------------------------------------------------------

## 9 Five things a cross-engine synthesist must know about this group

1. Lineage/ownership labels in BEE are assigned by LOCATION, SLOT or RESEMBLANCE, not by material causation. Evidence:
   "own code" = pc < L (#741: 27,083/28,163 location-foreign births are self-copied material); sr_depth = birth event
   (DEF-BEL-003); G = resemblance (REPL-01: G ~0.9 while founder content ~0.01); native `material` wrong vs copy-descent
   in 0.504 (E-003 P2); causal L jumps on 1-byte writes (D3). Any cross-engine heredity or "internalization" comparison that
   uses these labels compares bookkeeping. NPE has the same issue class (slot lineage; X-CONTENT caveat). The one
   material-grade instrument is bee_tracer (E-003), run on ONE run.
2. Across both seats, the recurring failure is a ruler that cannot return the opposite outcome: K3 could not return
   SURVIVES; REPL-02 dominance readout never reached on its positive arm; E-003 Q4 host arm could not see relational
   capability; G6a "init" branch unreachable; P5 r_cc at ceiling; LM01 F-B strict ~0 power in latent families (#730/#731);
   LM01 E6 positive control passes 8/29 strata; LM01 F3 "never_seen" is 87-89% stale-recall cells. The seats themselves
   now ledger this (calibration LEDGER 09-29/09-30 rows; LM02's REF_HOLD 94% is the counter-example that did it right).
   ATLAS_DERIVED: before pooling any NULL/ABSENT across engines, check whether the ruler was shown to fire on real data.
3. What survives in BEE is narrow: copy primitive + NOP slide is necessary for spontaneous SR (8/300 -> 0/300); world-made
   copies (P1) explained the old topology effect; endogenous reproduction antagonises task code (178 vs 2); contingent
   payment MAINTAINS seeded task code (40/40, 149 vs 0) and raises ECHO acquisition (29 vs 6/150; MD 58/320 LADDER1,
   36/240 COPIER), but COND_ONE is never acquired (0/960) and random soup never makes a competent replicator (0/3,200).
   Heredity numbers (P3 0.9987) are copier fidelity, not evolution.
4. Register/state primitive convergence (ATLAS_DERIVED hypothesis): BEE CARRIED registers kill zero-dependent founder
   lineages (0/24) and NPE carried state self-poisons donors (0.33 vs 0.81 fresh). NPE reports recurrent internalization
   of register initialization (8/144); BEE's rebuild reproduces the event signature only under a partial scaffold, only
   transiently (state-free at end 4-17/100), and cannot resolve descent. "Environment-supplied reset" looks like a shared
   gating primitive; "internalizing it" is confirmed in only one engine, by a lineage-bookkeeping ruler.
5. Ensorain's memory line converged on: discarding helps only as finite-sample variance control or choice of sufficient
   statistic (S1); exact old records help RECALL (+0.86) and hurt only when obsolete, while generalization to novel cells
   is unaffected (|dAC| <= .02) (PKG-F v7); a leak-free drift gate degenerates to a recent window; no fixed window works
   (LM02); after a change, data availability, not memory policy, is the binding loss. WTP "discoveries" so far are known
   completion physics (N6 beats all 9). LM01 is frozen and never launched (HOLD). Treat any claim that "forgetting causes
   generalization" in another engine against this dev evidence and against the stale-recall vs novel-cell split.
