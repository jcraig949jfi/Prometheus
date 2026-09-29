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


======== REPORT X011 ========

# REPORT

## 1. WHAT I SET OUT TO TEST

The briefing asked, in several forms, whether an outcome used as evidence is already predicted by who
generated the row, by a single number scale, or by a shared source; whether cross-world invariants survive
recomputation inside a single world and inside matched parameter strata; and whether the way a sample was
assembled can manufacture a "law". I applied all of these to the most concrete target available in
committed material: the [redacted] law-foundry campaign (CWE/C0), whose two frozen laws ("law A", v3
coordinates; "law B", v4 coordinates) predict the SELECTIVE_PAYS verdict and are recorded as having
SURVIVED three sealed universes (well D, swarm E, clone F). The questions were: (a) does family (generator)
identity or any single coordinate already predict the verdict; (b) does a zero-parameter formula written
straight from the task/certificate definition (shared source) predict it as well as the mined laws, on
visible pools AND on the already-spent sealed universes; (c) do the laws hold within each family and within
matched strata (cost decile; family x V x K x R); (d) how much of the headline balanced accuracy (BA) comes
from how the pools were assembled (share of worlds far from the decision boundary), measured against a
replicate noise ceiling.

## 2. WHAT I DID

Code and data: origin/[redacted]/c3-public-2026-09-24 @ 917edba0a7b9 (prometheus/[redacted]/, roles/[redacted]/campaigns/),
exported with git archive into src/ and run only there (numpy; env -u GIT_DIR ...). Nothing in the clone was run.

- gen_pool.py: rebuilt the private oracle pools of configs c2 (seed 20260929) and c0b (seed 20260924) with the
  repo's own build_pools + Chamber.observe: 3 visible families (regs, ring, ca) x 1200 worlds each, 400 episodes.
  Check: per-family PAYS rates reproduce the committed oracle_summary.json exactly for both configs
  (c2: regs .160 ring .2683 ca .2608; c0b: .140 .2592 .2625). Output out/pool_{c2,c0b}_1200.json.
- analyze.py <cfg>: frozen laws rebuilt atom-for-atom from the committed mine_initial.json thresholds
  (law A: C-(G+exp(-N)) <= -1.0548 AND (C-log Q)K >= .1792, v3; law B: log(Q-CK) <= -.1577 AND C-G exp(-N) <= -.1022, v4)
  and evaluated with the repo's miner.law_from_json. Rungs compared: family identity (best BA over family
  subsets; AUC of family base rate); every single coordinate and two composites, best threshold in-sample and
  leave-one-family-out; family + one variable (per-family threshold, 5-fold CV); the zero-parameter analytic
  economy "PAYS iff G e^-N - C >= .10 AND (Q<1 OR CK/2 >= .10)" (the form [redacted] wrote post hoc in
  c0e/PREREG.md; it follows from the certificate: SEL beats LAST by G e^-N - C, beats LOG by about CK/2);
  the ceiling atom alone. Each scored pooled, within family, within log-C deciles per family, within
  family x V x K x R cells, and in bands |margin - 0.10| <= 0.02/0.05/0.10/0.20.
- replicate.py: re-ran the 2009 c2 pool worlds with |margin-0.10| <= 0.10 at replicate=1 (independent seed)
  to get a noise ceiling (how well one replicate's verdict predicts another's).
- holdout_audit.py, mcnemar.py: read-only audit of the ALREADY-SPENT, committed sealed adjudication rows
  (c0b/run_21fd1b2cc/G5_holdout.json, c0e/C0E.json G5E, c2/F_adjudication.json). Nothing was refit on them;
  single-variable thresholds come from the visible c2 pool. No sealed module was imported or run; no unspent
  holdout was touched.
Outputs: out/analysis_c2.json, out/analysis_c0b.json, out/replicate_c2.json, out/holdout_audit.json, out/mcnemar.txt.

## 3. RESULT

Visible pools (c2 pool; c0b pool in brackets), balanced accuracy:
- Generator (family) identity alone: 0.566 [0.578] (AUC 0.568). No generator-identity leak.
- Best single variable: K 0.699 in-sample, 0.679 leave-one-family-out [0.703/0.683]; C alone 0.651; G e^-N - C
  0.680; family + one variable (CV) <= 0.683. No single-scale leak. The ceiling atom alone gets only 0.677:
  the verdict needs both competitor terms.
- Zero-parameter analytic economy (no data, no fit): 0.960 [0.965], accuracy 0.977.
  Frozen law A: 0.964 [0.974]; frozen law B: 0.978 [0.980].
- Within-context re-tests: within family A .967/.935/.992, B .975/.980/.978 (regs/ring/ca); within log-C
  deciles A .941 B .950 (analytic .941); within family x V x K x R cells A .963 B .975. The laws do not
  depend on between-family or between-scale differences; they hold inside every context tested.
- Assembly and noise: only 3.9% of the pool lies within +-0.02 of the 0.10 threshold and 11.6% within +-0.05.
  There, BA falls to A .70/.83, B .68/.87, analytic .57/.78, but the replicate noise ceiling is also low:
  .72 (+-0.02), .86 (+-0.05), .94 (+-0.10). The mined laws sit at the noise ceiling near the boundary; the
  analytic formula sits below it. The high headline BA is mostly a property of a pool dominated by
  easy worlds far from the boundary; near the boundary no rule can do much better with one replicate.

Already-spent sealed universes (240 worlds each; committed rows, recomputed BA matches the reported values):
                 law BA   analytic 0-param BA   reported 5-NN   best visible 1-var   rows far (|m-.1|>.1)
  D / law A      0.983    0.973                  0.841           C 0.725              51%
  E / law A      0.972    0.971                  0.769           K 0.708              52%
  F / law A      0.930    0.887 (v3 coords)      0.841           C 0.719              35%
  F / law B      0.955    0.943 (v4 coords)      0.833           C 0.713              35%
Paired exact McNemar, mined law vs analytic formula (law-right/analytic-wrong vs reverse): D 2 vs 4 (p .69),
E 2 vs 4 (p .69), F-A 4 vs 0 (p .13), F-B 3 vs 8 (p .23). On none of the three sealed universes is a mined
law distinguishable from the formula written from the task definition. Errors within +-0.05 of threshold:
law B on F 11 of 11; law A 4 of 7 (D), 3 of 8 (E), 4 of 11 (F).

Plain conclusion: there is no generator-identity or single-number-scale tautology, and the laws survive every
within-context re-test. But the outcome is a near-deterministic function of spec-side coordinates through the
certificate's own definition (shared-source tautology): a formula with zero fitted parameters, derivable
without running any world, matches the mined laws on visible pools and on all three sealed universes. The
sealed-transfer numbers therefore test the correctness of each substrate's declared coordinate map (and the
v4 expected-cost correction, which is where F-A vs F-B differ), not the discovery of a law. The comparison
baseline the campaign reported (5-NN, majority) is far weaker than the relevant rung.

## 4. DID IT RESOLVE THE QUESTION

Partly. For the one engine where committed data allowed it ([redacted]), yes: generator-identity and scale leaks
were measured and are absent; within-world and within-stratum re-tests were run and the laws hold; the
shared-source tautology was measured directly and dominates the evidence; the assembly effect was quantified
against a noise ceiling. Not done: the same audit for the other engines named in the briefing (SFE, [redacted],
Ares, NPE Z80 worlds, [redacted]), the "which world maximizes the metric" audit for other world-level metrics,
and the random-projection control for the two-representation agreement claim. A constraint-preserving
permutation null was not needed separately: the miner's null already permutes within family, and the
within-cost-decile BA (.94-.95) already exceeds any stratum-permuted null (about .5).

## 5. CONSEQUENCES

- Reproduction of something already known, now quantified: [redacted] itself records law A as a
  "planted-invariant recovery" with 97.5% agreement with a hand-derived law on D and E. This run extends it
  to F and to law B, shows the mined-vs-formula difference is not significant on any sealed universe, and
  shows the same on the visible pools.
- Instrument/harness point (for [redacted], and whoever adjudicates [redacted] results, e.g. [redacted]): the baseline
  ladder for any law should include a zero-parameter "definition" rung (the outcome's own economics written in
  the declared coordinates) and a replicate noise ceiling, not only majority and 5-NN. Transfer credit should
  be counted as the margin over that rung (here +0.001 to +0.043 BA, none significant), and BA should also be
  reported in a near-boundary band, because pool assembly (35-52% of sealed worlds far from the threshold)
  sets most of the headline number.
- Clean nulls: no generator-identity tautology (family BA ~0.57) and no single-scale tautology (best single
  variable ~0.70) in [redacted]'s SELECTIVE_PAYS data; within-context re-tests pass. These are not failures of
  the laws.
- The planned [redacted] research threads that ask "is the shared ceiling the transferable core" and "effective
  number of universes" should treat the analytic formula as the null law to beat; a new sealed or foreign
  generator only adds information if its verdicts are not already fixed by that formula (e.g. a mechanism or
  coordinate the formula gets wrong, as the v3-vs-v4 cost correction on F shows).

## 6. COST

About 1.5 hours of my time. CPU: about 8 CPU-minutes (two pool rebuilds of ~2 min each run in parallel,
1.5 min replicate pass, seconds for analysis); at most 2 processes; well under 2 GB. Not done: other engines,
the second-representation random-projection control, and fresh sealed worlds (none created or consumed).



======== REPORT X012 ========

# [redacted] -- Implicit-pressure citation sweep (claims with no task causation)

[redacted]

## 1. Question

(H-D2-50) Which BEE, Atlas-feed or NPE-comparison claims were drawn from IMPLICIT-pressure cells, and so carry no
task causation? Does the NPE pressure axis (A-2: EXPLICIT_FITNESS vs NONE_IMPLICIT, +0.30) have the same inertness?
(Related, H-D2-41: the NPE endogenous-accessibility assay H4.)

## 2. Method

- Read the source diagnosis: roles/[redacted]/forensics_2026-09-23/GROUNDING_REPORT.md.
- Read the pressure code of both engines to see where the task score can enter the dynamics:
  - BEE: prometheus/z80atlas/world.py, grounding.py.
  - NPE: roles/[redacted]/campaigns/z80atlas-2026-09-19/world.py, grammar.py, packet.py.
- Swept downstream citations with grep over main and the named worker branches (`rogit grep`). The locations covered
  were: the evidence wiki (evidence_wiki/, mnemosyne/, roles/Mnemosyne), the Atlas (roles/Atlas, atlas/,
  roles/[redacted]/atlas_bee), ops/campaigns/C-001 (D_Z80_SYNTHESIS, W1/W2/A0 lenses), and the [redacted],
  [redacted], [redacted], [redacted], [redacted], [redacted], [redacted], techne and [redacted] trees.
  - Search terms: "task independence", "task-independent", G1T, IMPLICIT, NONE_IMPLICIT, "+0.30"/"0.3036", "A-2".
  - Part of the sweep was done by a read-only search sub-agent. I re-read every citation marked (v) below at the
    source. Unmarked citations are the sub-agent's, and I did not re-open them.

## 3. Evidence

### 3.1 BEE: why IMPLICIT is inert (confirmed in code)
- The default pressure is IMPLICIT (prometheus/z80atlas/world.py:46), and every grounding lane starts from it
  (prometheus/z80atlas/grounding.py:28-31, BASE pressure="IMPLICIT"). (v)
- Energy in under IMPLICIT is `1.0 + 0.5*s` (world.py:666), energy out is `0.9 + 0.001*steps` (world.py:670-671),
  and INIT_ENERGY is 12.0 (world.py:35). (v)
  - At BUDGET 256 the worst deficit is 0.156 per tick, or 6.24 over a lifespan of 40. That is less than 12, so the
    age cap kills before energy does.
  - The report's "inflow >= cost" is therefore slightly loose, but its conclusion holds: the score never decides
    survival.
- EXTERNAL parent selection under IMPLICIT, METABOLIC and EXPLOIT is uniform, `[1.0]*n` (world.py:648). (v)
- The same thing was found in the pre-repair code: audit_blind/AUDIT_REPORT.md:35 (M3) and :158. (v)

### 3.2 BEE claims drawn from IMPLICIT (or task-uncoupled) cells

| # | claim | where | status |
|---|---|---|---|
| B1 | "task independence of replication" (G1T, six task families) | GROUNDING_REPORT.md:51-55, :155 | self-marked NOT_ADJUDICABLE (v) |
| B2 | historical "replication shows no task dependence" (spont 1.4-2.2%, hifi 14.6-16.6% across six tasks) | POST_CAMPAIGN_FORENSICS.md:116-120 @3efdacf7e | **still stands unqualified** (v). It pools the FIXED lane over every pressure (tools/rates.py:60-78: the task marginal is not stratified by pressure). It says "barely enters", not "never". Its task-independence reading is NOT_ADJUDICABLE until the lane is stratified by pressure; the raw run table needed for that is not committed. |
| B3 | REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL (historical flag, 393) | AUDIT_REPORT.md:35 | 383/393 in task-uncoupled pressures (IMPLICIT 91, NOVELTY 117, QD 65, METABOLIC 64, EXPLOIT 46) (v). Already FALSIFIED/reversed (GROUNDING_REPORT.md:148). |
| B4 | REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK | POST_CAMPAIGN_FORENSICS.md:210-216 | CONFOUNDED (no task-OFF arm); FALSIFIED at G5 (GROUNDING_REPORT.md:150) |
| B5 | **G2 sustained rate 63/160 and G6 origin counts pool G1T** | GROUNDING_REPORT.md:56; tools/grounding_analysis.py:212 | **new knock-on, not flagged anywhere I found** (see below) |
| B6 | P8 substrate ablations (LDIR necessary) | GROUNDING_REPORT.md:78-84 | run at the IMPLICIT base. A replication claim, not a task claim, so it is unaffected. Correctly scoped as "task inert" in roles/[redacted]/challenge/PRIOR_ART_PRESSURE.md:429,454 and backlog/threads/FR-011.md:50. |
| B7 | G3 EXTERNAL 178 vs ENDOGENOUS 2 | GROUNDING_REPORT.md:113-121 | comes from EXPLICIT cells. The IMPLICIT cells gave "no reaching in either arm" (:115-116) (v). **Not** affected. D_Z80_SYNTHESIS.md:60-61,78 cites it correctly. |

Detail for B5:
- G1T seeds depend only on the lane and on k, not on the task (grounding.py:53, :118-121). (v)
- The G2/G6 pool includes every spontaneous G1T run (grounding_analysis.py:212). (v)
- Five of the six G1T cells are run-for-run identical at 5/150 each (GROUNDING_REPORT.md:51). So about 20 of the
  160 "origins" are copies of 5 runs, and at most about 140 are distinct.
- G2's 39.4% [32.1, 47.1] and G6's counts are therefore pseudo-replicated. So is the ERRATA recount 103/160
  (ERRATA_2026-09-29.md), which uses "the same 160".
- The exact effect needs analysis.py (A1). Its direction on the rate is unknown.
- This is a consequence of IMPLICIT inertness that goes beyond the "one estimate, not six" caveat.

### 3.3 Downstream citations of B1 (all acknowledge the inertness)
- [redacted]: NEXT_CAMPAIGN_RECOMMENDATION.md:40; journal/2026-09-23.md:81; the coupling review packet (:47) and
  operator directive (:350).
  - The coupling and multiday preregs run IMPLICIT+NEUTRAL on purpose, so the ledger is the only task path
    (COUPLING_IMPLEMENTATION_AUDIT.md:40).
- ops/campaigns/C-001/DEEP_BLOCK_2026-09-27/W2_BEE_LENS.md:318-326.
- [redacted]:
  - [redacted]/runs/[redacted]/REPORT.md:95,151 (v)
  - challenge/FAILURE_PRINCIPLES.md:98,888 (cites FR-022, which has no thread file)
  - threads/sfe_retrospective/notes/C_engines.md:436-437
- [redacted]: research/workers/W-D/REPORT.md:50-55; threads/T-X-4_intervention_reach.md:16 (filed as an "INERT PATHWAY").
- [redacted]: frontier/poi/raw/I6_failures_reversals.md:92 ("one estimate, not six"); expedition/z80_threshold/DESIGN.md:29.

### 3.4 Evidence wiki and Atlas
- The evidence wiki (evidence_wiki/) contains no BEE, z80atlas or [redacted] entry. Its "task-agnostic" hits
  (V2-T08) are about an unrelated classifier.
- The Atlas does not contain BEE z80atlas:
  - roles/Atlas/catalog/ECOSYSTEMS.jsonl lists NPE CW01/GraphWorld, DEEP FRONTIER and SFE only.
  - PACKET_2026-09-19.txt:173 says "Not yet harvested: ... [redacted]".
  - roles/[redacted]/atlas_bee/ATLAS_FEED.jsonl (6 rows) covers wforge toolbox transplants and makes no pressure
    or task claims.
- **Result: there are no inert-cell task claims to retract in either the wiki or the Atlas.** The risk sits in the
  future harvest of B2.

### 3.5 NPE: A-2 and NONE_IMPLICIT
- NONE_IMPLICIT is declared as "no task coupling at all" (grammar.py:71). In world.py no code path reads `comp`
  under NONE_IMPLICIT:
  - reaping is oldest-first (world.py:276-277);
  - there is no energy economy (world.py:568, :683);
  - the EXTERNAL parent is uniform (world.py:656-657). (v)
- So NONE_IMPLICIT is exactly as inert as BEE's IMPLICIT. The difference is that NPE declares it as the inert
  control, and it is the control level of every pressure pair (grammar.py:212). (v)
- EXPLICIT_FITNESS requires EXTERNAL reproduction (grammar.py:175-177). It acts only in `_external_births`, as a
  3-way tournament on comp (world.py:648-652), and that function is called only when reproduction == EXTERNAL
  (world.py:838-839). (v)
- **So all 513 A-2 pairs contrast task selection with drift inside the EXTERNAL harness.** The +0.3036 (85 vs 11
  crossings; PACKET.md:27) is a *valid* causal contrast precisely because one arm is inert.
  - It does **not** have BEE's defect.
  - It also says nothing about endogenous reproduction.
  - Minor caveat: the child inherits the parent's comp and held without re-evaluation (world.py:664) until the next
    validation.
- Citations of A-2 (FINDINGS.md:43-55 "HOLDS" (v); W1_NPE_LENS.md:473; roles/[redacted]/design/01_engine_design_2026-09-23.md:74;
  DEFECTS.md:92) restate it with no EXTERNAL-only scope note.
  - The claim is correct; the missing scope line is a wording gap.
- NPE claims that *do* sit on inert cells:
  - **N1: A-4 "endogenous-only accessibility"**, the source run of H4. Its matched control ran under NONE_IMPLICIT
    and "lost the crossing to undirected mutation" (H4_AUTOPSY.md:17-21). The endogenous arm never reproduced
    (:9-13). A-4 is already WITHDRAWN (FINDINGS.md:74, E-4). The pressure alone would also have made it
    task-non-causal. (v)
  - **N2: the 65 REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION flags.** Their pressure mix is not tabulated in any
    committed text. Any flag in NONE_IMPLICIT carries no task causation in either arm. They are already
    WEAK/INADMISSIBLE for Z80A-D04 (H4_AUTOPSY.md:57-61). Needs analysis.py (B2).
  - **N3: the non-pressure axes reproduction:{PAIR_EXECUTION,OVERWRITE,CONSTRUCTIVE}->EXTERNAL** (-0.1197 / -0.0229
    / +0.0122; PACKET.md:34,46,50). EXPLICIT_FITNESS is impossible outside EXTERNAL, so in these pairs the EXTERNAL
    arm keeps the experiment's pressure. Wherever that pressure is NONE_IMPLICIT or another uncoupled one, the arm
    is drift. The pairs' pressure mix is not committed in text:
    - 6,862 of 23,471 runs (29%) are NONE_IMPLICIT (PACKET.json:1078-1085);
    - 25.9% of them "crossed" with no task coupling (the crossings come from seeding, drift and COEVO_ENV).
    - These axes are not cited as task-causal anywhere I found, but they are exposed. Needs analysis.py (B1).
  - NPE heredity findings (A-1, E-3..E-10, C-CORE; many cells NONE_IMPLICIT or QD, S1C_P11_REASSAY.md:52) are
    replication claims, not task claims, and are unaffected.
  - [redacted] correctly scores the 9cba cell as unpaid (CENSUS_A_z80.md:190).

### 3.6 H-D2-41 link
- The only committed NPE endogenous-accessibility evidence (A-4) sat on a NONE_IMPLICIT control and a non-reproducing
  endogenous arm. So NPE has never had a task-coupled endogenous-vs-external test.
- BEE's G3 answer (EXTERNAL 178 vs 2) comes from EXPLICIT cells only.
- The cross-engine reading therefore remains one-sided, as the harvest entry says.

## 4. Result

1. **BEE:**
   - Task claims drawn from IMPLICIT cells: G1T task independence (self-marked NOT_ADJUDICABLE), the historical
     task-independence paragraph (POST_CAMPAIGN_FORENSICS.md:116-120, **unqualified, should be marked
     NOT_ADJUDICABLE**), and the historical ENDO>EXT flag (already falsified).
   - Knock-on: G2/G6 pool about 20 duplicate G1T origins, so they are pseudo-replicated.
   - Every downstream citation of G1T carries the inertness caveat.
2. **Evidence wiki and Atlas:** no BEE entries, so nothing to retract.
3. **NPE A-2:** NONE_IMPLICIT is equally inert. It is the *declared control*, which makes +0.30 a valid
   selection-vs-drift effect confined to EXTERNAL reproduction. It needs a scope note, not a retraction.
4. **NPE claims with no task causation:** A-4 (already withdrawn); any NONE_IMPLICIT share of the 65
   endogenous-reach flags and of the reproduction->EXTERNAL axes (not yet quantified).

## 5. Limits

- No code run. The G1T duplicate count (about 20) is inferred from the report's "identical 5/150" statement plus the
  seed code, not counted.
- NPE pressure strata for the non-pressure axes and flags are not quantified.
- BEE's historical per-run table (the FIXED lane) is not committed in stratifiable form (RATES.json holds marginals
  only), and the campaign packet is local-only (roles/[redacted]/STATUS.md:42).
- Citations were found by term search. A paraphrase that uses none of the terms could be missed.
- The sub-agent's branch sweep reported no branch-only hits. I did not re-check every branch myself.

## 6. What would change the conclusion

- analysis.py A1 finding the G1T cells *not* identical in outcome tuples. That would remove B5.
- analysis.py B1 showing that the reproduction->EXTERNAL axes are mostly task-coupled pressures with a consistent
  sign. That would clear N3. A sign flip between strata would make the pooled -0.12 uncitable.
- A committed pressure x task cross-tab of the historical FIXED lane showing task-dependence differences only in
  coupled pressures (or none anywhere). That would settle B2.
- Discovery of a BEE harvest into the wiki or Atlas that uses B1 or B2 without the caveat. That would add a
  retraction target.



======== REPORT X013 ========

# [redacted] [redacted] [redacted]: exp one-class collapse, and whether the signed-margin curve transports

[redacted]

## Question

- **H-D4-63.** Which entries of exp's rule table cause its N-dependent collapse to "all ones", which appears between N=149 and N=599 and saturates by N=999? The companion question: does the particle1 non-convergence row (1 IC of 100, with 100/149 cells still flipping at T=298) replicate on 5 more seeds?
- **H-D4-64.** Does `acc = sum_k P_ens(k) c(k)` carry beyond density-CA, so that a task ensemble acts on a phenotype only through a scalar statistic? And is maj's boundary shift m*(N) (THEO-CAND-003) real once there are about 10x more ICs?

## Short answer

1. **Which exp entries cause the collapse: still unanswered at `5266ccebe`. No ablation has ever been run.** The library can now build the intervention. `derive_edit`/`derive_flip` are in `herakles/evca/derive.py:134-168`, and Vivarium says derived rules run unchanged (`roles/Vivarium/STATUS.md:102-103`). But no fossil, ledger row or result file in the repo holds an exp child. The only `edit_entries` record anywhere is a Proteus mint rehearsal on the **GKL** table (parent `evca:r3:005f005f…`, edit `[11,0]`, namespace `test`): `proteus/integration/RESULT_MINT_ROUNDTRIP_TEST.json:11-28,36`. The 128-cell scan that THEO-REQ-005 promised (`roles/Theophrastus/reqs/THEO-REQ-005_table_level_intervention.md:29-31`) is written out as analysis.py Part C.
2. **The phenotype is well supported, with three qualifications the harvest entry does not carry:**
   - (a) **"Collapses to all ones" is an inference; the committed data only shows failure on the zero side.** The per-IC files store only `success`. Failing ICs are never split into "all ones" versus "not uniform" (`theophrastus/dissect.py:65-81`). Fossils carry only `all_ones_fixed` (a property of the rule table), not the final state.
   - (b) **Where the collapse begins is not located.** The only lattice sizes in the repo are N ∈ {149, 599, 999}. Searches for any other N under `roles/Theophrastus` found no rows. "Between 149 and 599" is the whole resolution.
   - (c) **One pre-registered prediction failed, but a later write-up lists its observed value as "predicted".**
     - ADAPTIVE_RECORD_02 predicted 0.3042 for exp/W599/P_d40 and observed 0.3475. Its own pass rule (tolerance 0.034) gives `pass: false`: `roles/Theophrastus/crucible/round2/ADAPTIVE_RECORD_02.json:69-93`.
     - SPEC-001 counts this correctly as a miss (`SPECIMENS_ROUND2_2026-09-14.md:37-39`).
     - SPEC-002, however, lists ".35 (d=.40) … (predicted; observed 1.000 and .3475)" (`:116-118`).
     - Also, "saturated 599→999" (chi2 12.4/23, `ROUND2_SCORE.json:614-622`) sits beside a failed 599-curve prediction for exp W999 P_unif: 0.7887 observed vs 0.8228 predicted (`ROUND2_SCORE.json:515-531`).
3. **particle1 replication: not run.** It is still an open box in `roles/Herakles/todo_2026-09-16.md:35-39`. The committed row fits exactly one bad IC. `mean_flip_fraction` = 0.0067114 = (100/149)/100 (`herakles/evca/sync_floor_2026-09-16.json:335-340`). This is analysis.py Part E.
4. **Transport of the curve to other kinds: untested. At this commit no registered kind could test it.**
   - The registered kinds are `noop_v0`, `evaluate_bitstring`, `[redacted].probe.v0` (retired), `random_walk_v0`, `ca_density_v0`, `artifact_probe_v1`, `cegis_boolean_v1` and `eca_rule_eval_v1` (`vivarium/viv/kinds.py:209-594`).
   - Only `ca_density_v0` samples inputs from an ensemble and scores a classification.
   - `eca_rule_eval_v1` is exhaustive and says "IT REPORTS THE OBSERVABLE, NOT A SCORE" (`kinds.py:584-592`).
   - `cegis_boolean_v1` covers all 8 assignments exhaustively (`kinds.py:521-524`).
   - The only transport ever shown is across *consumers* (Vivarium fossils, 150/150, at N=149): `SPECIMENS…md:164-178`.
5. **A logical point that narrows H-D4-64.**
   - For any generator that is uniform over arrangements once k is fixed (every Bernoulli mixture), the decomposition is an identity by exchangeability. The specimen says so itself (`SPECIMENS…md:43-44`). Its "transport" to another task is automatic whenever such a statistic and generator exist.
   - The empirical content is (i) whether k stays **sufficient for non-exchangeable generators**, and (ii) whether c carries across N.
   - (ii) is already known to fail quantitatively (`SPECIMENS…md:56-63`; GKL W999 0.7925 observed vs 0.7236 predicted, `ROUND2_SCORE.json:532-548`).
   - (i) has never been tested. It can be tested inside `ca_density` today with blocky fixed-k ICs (analysis.py Part D).
6. **maj m*(N): still a candidate.** No ICs were added after round 2. The specimen's own stop reason is that "discrimination [is] below binomial resolution without ~10x more ICs at m in [.25,.35]" (`SPECIMENS…md:150-152`), and both constructive predictions at the boundary missed by 2-3 SE (`ROUND2_SCORE.json:378-411`). analysis.py Part A2 bootstraps m*(149) and m*(599) from the committed per-IC data and reports the ICs needed.

## Method

- Read the source specimen, THEO-REQ-005, the Herakles derive library and todo, and the Vivarium status and kind registry.
- Read the round-2 evidence files: `stepA_tests.json`, `ROUND2_SCORE.json` and `ADAPTIVE_RECORD_02.json`, plus the schemas of `per_ic*.jsonl`.
- Searched the whole tree for any `edit_entries` artefact or exp child, any lattice size other than 149/599/999, and any other kind that classifies inputs.
- Checked `rogit log --since=2026-09-15` for `roles/Theophrastus`, `theophrastus/` and `herakles/evca/derive.py`. The only later commits are other seats' inbox files and Herakles's derive delivery: dbc41fd2f, bfe8f0bd8, 13000800f. None comes from Theophrastus and none is an experiment. The Theophrastus journal ends at `journal/2026-09-14.md`.

## Evidence (key numbers)

| claim | value | citation |
|---|---|---|
| exp zero-side vs one-side success at \|m\|<.01, N=149 | .367 (n=188) vs .674 (n=178), z −5.9 | `roles/Theophrastus/crucible/round2/stepA_tests.json:2690-2703` |
| same, N=599 | .0043 (n=461) vs .9911 (n=450), z −29.8; 13/23 bins \|z\|≥3 | `stepA_tests.json:2843-2857` |
| exp N=999 asymmetry | max \|z\| 19.6, chi2 850.8/7 | `ROUND2_SCORE.json:657-664` |
| exp curve 599 vs 999 by \|m\| | chi2 12.4/23, max \|z\| 1.51 | `ROUND2_SCORE.json:614-622` |
| exp W999 P_iid pred from 599 curve | .5262 obs vs .5303 pred, pass | `ROUND2_SCORE.json:498-514` |
| exp W999 P_unif pred from 599 curve | .7887 obs vs .8228 pred, **fail** | `ROUND2_SCORE.json:515-531` |
| exp W599 d=.40 retry | .3475 obs vs .3042 pred, **fail**; CHEAT-B curve (.9998) misses | `ADAPTIVE_RECORD_02.json:69-93` |
| exp W599 d=.60 | 1.000 vs 1.000 | `ROUND2_SCORE.json:259-275` |
| published exp P | .652 / .515 / .503 at 149/599/999; labelled "block-expanding" | `herakles/evca/genomes.py:52-56` |
| par asymmetric the other way; particle1 symmetric | par N599 max\|z\| 10.15; particle1 max\|z\| 2.12 / 0.91 | `stepA_tests.json:3535-3538`; `ROUND2_SCORE.json:584-598` |
| horizon not a cause | bit-identical at half the steps (exp, par) | `ROUND2_SCORE.json:412-441`; `SPECIMENS…md:50-52` |
| cause of the collapse | "UNKNOWN at the rule-table level" | `SPECIMENS…md:119-123,138-139` |
| intervention library delivered | derive_edit / derive_flip | `herakles/evca/derive.py:134-168`; `roles/Herakles/todo_2026-09-16.md:21` |
| Vivarium half | "derived rules run unchanged" | `roles/Vivarium/STATUS.md:102-103` (commit cdb7d3850) |
| no exp ablation exists | only edit_entries record is on GKL, test namespace | `proteus/integration/RESULT_MINT_ROUNDTRIP_TEST.json:11-37` |
| per-IC files store success only | `correct = where(target==1, ones==N, ones==0)`; only `success` written | `theophrastus/dissect.py:65-81` |
| particle1 outlier unreplicated | unchecked todo item | `roles/Herakles/todo_2026-09-16.md:35-39`; `herakles/evca/sync_floor_2026-09-16.json:331-341` |
| transport status | "To other kinds: UNTESTED" | `SPECIMENS…md:67-72` |
| cross-consumer transport | 150/150 bit-exact, N=149 | `SPECIMENS…md:164-178` |
| no other classification kind | registry | `vivarium/viv/kinds.py:209-594` (eca: 572-594; cegis: 479-568) |
| curve not portable across N | GKL W999 .7925 vs .7236 | `ROUND2_SCORE.json:532-548`; `SPECIMENS…md:56-63` |
| maj boundary candidate | m*≈.27 at 149, ≈.30 at 599; 2/2 boundary predictions missed | `SPECIMENS…md:143-152`; `ROUND2_SCORE.json:378-411` |

## Result

- **H-D4-63: OPEN.**
  - The genotype→phenotype question has not been attacked. It became *executable* on 2026-09-16 (library dbc41fd2f, Vivarium cdb7d3850), but nobody submitted the scan.
  - The phenotype side (strong zero-side failure at N≥599, and the detector) stands at high confidence.
  - "Collapse to all ones" should be downgraded to "near-total zero-side failure" until the final states are recorded.
  - The onset window is only as fine as the three sampled N.
  - particle1: OPEN, one row.
- **H-D4-64: OPEN / UNTESTED** for other kinds, and there is structurally no registered kind to test it on.
  - The decomposition is exact for exchangeable ensembles on any task, so the question that is still open and testable is whether k is sufficient beyond exchangeable ensembles.
  - That can be tested inside ca_density now (analysis.py Part D).
  - Across N the curve carries in *form* but not in *value*, and that part is already settled negatively.
  - maj m*(N): CANDIDATE, unchanged.

## Limits

- No code was executed, so every quantitative statement here is quoted from committed files.
- I did not re-verify SPEC-001/002's own statistics against per_ic.jsonl; analysis.py Part A would.
- I did not confirm that per_ic.jsonl and per_ic_round2.jsonl are disjoint (see the dedupe note in Part A).
- The absence of an exp ablation is based on repo-wide searches for `edit_entries`, the exp hex and REQ-005 references. An ablation run outside the repo, or on an uncommitted branch, would not show up.
- "Theophrastus inactive" means only that no seat-authored commit after the 2026-09-14 journal was found under `roles/Theophrastus`.

## What would change the conclusion

- **analysis.py Part C** (128 single flips at N=599):
  - ≥1 flip that lifts zero-side success to ≥0.5 while keeping one-side success ≥0.9 localises a necessary ingredient and answers H-D4-63 at single-entry resolution.
  - Zero such flips means the collapse is spread over several entries; the next step is pairwise flips ranked by usage on failing runs.
- **Part B:**
  - If most zero-side failures at N≥599 are non-uniform final states, the "constant classifier / all ones" description is wrong in mechanism, although the accuracy argument still holds.
  - A sharp longest-1-run threshold that is stable across N would explain the N-dependence as an opportunity count, like the maj story in THEO-CAND-003.
- **Part D:** if blocky fixed-k ICs give the same success as uniform fixed-k ICs within 2 SE for every rule, then k is a genuinely sufficient scalar and the curve is a stronger curriculum knob. If they differ, transport is limited to Bernoulli-type generators.
- **Part E:** recurrence in ≥2 of 5 new seeds makes particle1's non-convergence a rate finding that bears on its at_T numbers. Zero recurrences in 500 ICs retires it as a single row.
- **Part A2:** disjoint 95% bootstrap CIs for m*(149) and m*(599) would promote THEO-CAND-003 without new runs. Otherwise the run needs roughly 10x the ICs per bin in [.25,.35], as Part A2 will quantify.
- Registering any new kind that samples inputs and scores classification (e.g. a scored synchronisation kind over `core.synchronisation_score`) would make cross-kind transport testable for the first time.



======== REPORT X014 ========

# [redacted] [redacted] [redacted] — a term-rewriting substrate (H-D4-42 / FR-115)

Commit read: `5266ccebea3ad5522b7cfa7a07a8718cac113a70` (read-only). All paths are relative to the repo root at that commit. Nothing was executed.

## 1. Question

"Should Prometheus host a term-rewriting substrate (transformation store, exhaustive application, observable termination) so that simplification strategies can evolve?" (`roles/[redacted]/[redacted]/draft/[redacted].[redacted]:12`; harvest source `roles/[redacted]/backlog/harvest/D4_sfe_era.md:381-386`).

It breaks into three parts that the repo can answer to different degrees:

- **Q5a (fact).** Is it true that no rewriting substrate is hosted or owned, and that the rewrite-strategy pressures are unhostable today?
- **Q5b (fact).** Is there rewriting machinery in the repo that the thread (comms #182/#189/#276) did not take into account?
- **Q5c (judgement).** Does the committed evidence support hosting one, and on what conditions?

## 2. Method

1. I read the primary thread in order: Vivarium's return #182, Nyx's question #189, Proteus's answer (#276 in the harvest), and Nyx's pressure records and knife rules.
2. I grepped the whole tree for `rewrit`, `rewriting substrate`, `UNHOSTABLE`, `egglog`, `e-graph`, `TRS` and `normal form`. Then I read every hit that could be a rewriting executor.
3. I checked the Vivarium kind registry (`vivarium/viv/kinds.py`) and the Proteus pieces that Proteus offered to keep stable.
4. I read the verdicts of the two earlier substrate campaigns that included a rewriting basis (D3, D4).
5. I used `rogit log` to date the key files.

Comms rows 188, 189 and 276 are not in the repo as database rows. I cite the committed copies of those messages.

## 3. Evidence

### 3.1 Nothing is hosted or owned (Q5a)

- **Vivarium (the host seat), 2026-09-11.** "all four: cannot be operationalized TODAY -- requirement 1 in each is an evaluable REWRITING substrate ... no kind, no executor and no seat on Prometheus owns one. Nothing in vivarium/viv/kinds.py rewrites terms." (`roles/Vivarium/prompts/2026-09-11_replies/NYX_PRESSURE_RETURNS_44_52_175.md:99-103`). Vivarium's pointer was "Proteus's boolean grammar v0 ... Owner would be Proteus", offered "as a pointer and not a design" (same file :131-134).
- **Kind registry at HEAD.** The registered kinds are `noop_v0`, `random_walk_v0`, `ca_density_v0`, `artifact_probe_v1`, `cegis_boolean_v1` and `eca_rule_eval_v1` (`vivarium/viv/kinds.py:210,274,303,432,480,573`). None is a rewriting kind. A grep for `rewrit` under `vivarium/` finds only prose about files and ledgers.
- **Proteus, 2026-09-16 (commit a648b99a7).** Answer "(b)": "Proteus does NOT own a rewriting substrate and does not intend to build one" (`roles/Proteus/prompts/2026-09-16_replies/REPLY_NYX_189_rewriting_substrate.md:4-7`).
  - Proteus lists what exists and what does not. Missing: "a STORE of transformations", "'one transformation step' as an operation on a term", "a termination criterion (normal form) -- canonical() is not one", and "an executor that applies a store exhaustively and reports termination" (:24-28).
  - It says it will not build the executor "because it is a kind" (:30-33). It does not know of any owner, and it names Techne library learning and Herakles evca as untried neighbours (:35-37).
- **The pieces Proteus offers exist as described:**
  - `proteus/eval/boolean.py:59-60` (grammar) and `:122` (`truth_table` oracle)
  - `proteus/eval/shrink.py:79-90` (`canonical` is documented as "NOT a simplicity claim -- only a tie-break"; `size_key`)
  - `:158` (`minimal_by_enumeration`)
  - `proteus/eval/BOOLEAN_UNIVERSE_TABLE.json`
- **The pressures carry the annotation.** Each of the four lean_simp records has `hosting.status = UNHOSTABLE_TODAY`, blocking requirement "an evaluable rewriting substrate", owner "Proteus (unclaimed)". For example `nyx/specimens/lean_simp/pressures/growing_store_must_terminate.cut1.json:74-80`; the others are `retrieval_at_store_scale.cut1.json:74-76`, `conditional_facts_must_be_paid_for.cut1.json:74-76` and `orientation_is_a_choice.cut3.json:75-76`. Nyx made this a rule: knife K9 "ROUTE TO THE SUBSTRATE OWNER" (`nyx/KNIFE.md:105-114`).
- **A fifth dependent pressure is not annotated.** `nyx/specimens/lean_simp/pressures/mutual_normalisation.cut2.json:9-11` requires "fact A rewrites B which rewrites C". It has no `hosting` block (a grep for `hosting|status|owner` finds nothing in it). So "four unhostable" undercounts by at least one. This is my reading; Nyx may have scoped it differently.
- **Nyx's own ledger is stale on the answer.**
  - `nyx/LOOP.md:127` still reads "#189 Proteus+Vivarium question, no answer".
  - `nyx/CHOP_SHOP_CALIBRATION_2026-09-12.md:88` says the same.
  - `nyx/specimens/hypothesis_shrinker/cuts.json:1038` says the "Proteus halves of #189/#190" were "HELD, not delivered (never booted)".
  - Proteus's reply was committed later, at a648b99a7 (2026-09-16). The harvest's "later evidence" is right; the Nyx ledgers do not reflect it.

### 3.2 Rewriting machinery the thread did not consider (Q5b)

"No rewriting substrate" is true of **hosting and ownership**. It is not true of **code**. There are three committed rewriting executors, and none of them was raised in #182, #189 or #276:

1. **`agent_d3_blind/substrates/s3_trs.py`.** An "ordered local sequence-rewrite" system. It "applies the first matching rule, and repeats to fixpoint or fuel exhaustion" (:1-6). Termination is observable: it returns `"ok"` at fixpoint and `"timeout"` when fuel (`FUEL = 80`) runs out (:108-142).
   - [redacted]'s asset survey (commit 87bab0877/f0987100c, 2026-09-06/08) calls it "the only term-rewriting substrate in the repo" and recommends "ADAPT D3 `s3_trs.py` for a rewriting world" (`[redacted]/docs/expansion/ASSETS.md:123-124`). That recommendation predates #182 by three days, and nobody in the thread cites it.
   - Limits: it rewrites flat sequences, not trees. The rule set is the organism's *genome* (at most 6 rules), not a growing fact store. It does not report per-fact examination counts or which rules fired.
2. **`agent_d4_blind/substrates/vm_substrates.py:418-454` (`S3_REWRITE`).** Leftmost-first pair rewriting with 16 rules over an 8-symbol alphabet. It halts when no rule matches, with a 64-step cap.
3. **`techne/lib/donors/egglog_adapter.py`.** An e-graph / equality-saturation donor.
   - It offers a closed menu of 6 arithmetic rules (:56). It saturates and then extracts a minimum-cost term (:70-81, :131-141).
   - It reports `rules_applied` as *configured*, not as fired (:140-141). It exposes no step counts, no termination-by-budget signal and no trace.
   - Its docstring says extraction imposes egglog's cost model as an ordering (:23-26).
   - Status: labelled ACQUIRED / IMPORT-TESTED / WRAPPED / CONTROLLED, with one direct consumer, `ergon/gen0/family_b_probe.py` (`techne/acquisition/DONOR_DISPOSITION_2026-09-11.json:163-209`).

The Proteus oracle pieces (§3.1) would give any of these a soundness check. None of them is a Vivarium kind.

### 3.3 Evidence that bears on "should" (Q5c)

**For hosting:**

- Five pressures need a rewriting substrate to be operational, and none has any other route (§3.1).
- Nyx's program table shows "pressures operationalized 0 ... 4 unhostable -- no rewriting substrate" (`nyx/LOOP.md:110`). This single missing substrate accounts for most of the unhostable backlog.
- [redacted] already recommends adapting an existing executor (`[redacted]/docs/expansion/ASSETS.md:124`).
- Lexis argues the e-graph family may fit Prometheus better than the DreamCoder/Stitch family. Lexis states this is an argument, not a result: "Nobody has run babble on anything of ours" (`roles/Lexis/library_learning/notes/PASS_04_gene_extractor_and_the_e_graph_fit.md:122-124`; also cited in `techne/lib/donors/egglog_adapter.py:15-19`).

**Against, or cautions:**

- **Both earlier rewriting substrates were killed.**
  - D4 `S3_REWRITE` had the highest validity (0.996) and the largest phenotype mass, but "a dead accessibility geometry: far-stratum hits 0.00 for every navigator ... [redacted] maximized both and failed the only property that matters for a learning substrate" (`agent_d4_blind/VERDICT-PHASE1.md:85-96`).
  - D3 `[redacted] TRS` failed G1 (viable neighbour rate), G8 (M0 coverage) and G10 (witness access), passing 7/10 gates. That campaign's overall verdict was `NO_BASIS_PASSED` (`agent_d3_blind/VERDICT-PHASE1.md:6,18-30`).
  - Caveat: both campaigns used rewrite rules *as the evolving program* and asked about navigability. The lean_simp pressures use rewriting *as the world* and evolve the organism's store discipline. The kills are a caution, not a refutation (see §5).
- **A prior install on a leverage claim went unused.** egglog "was installed on a leverage claim and never consumed". Techne's own retrospective says this and treats it as a warning against further dependency asks (`techne/loop/rung_notes/CYCLE049_RETROSPECTIVE_FINDINGS.md:68-77`).
- **No seat will own it.**
  - Proteus declines (§3.1).
  - Vivarium hosts only a kind whose semantics another seat declares (`NYX_PRESSURE_RETURNS_44_52_175.md:7-15,137-145`).
  - Nyx "never builds the world for her own pressure" (`roles/Nyx/prompts/2026-09-11_reply_182_and_proteus_question/QUESTION_PROTEUS_rewriting_substrate.md:23-26`).
- **Vacuity risk in the only named candidate (my inference; not stated in the repo).**
  - `growing_store_must_terminate` lists as trivial shortcut 1 "ignore the store entirely and answer by direct evaluation". It closes that shortcut by requiring "some problems must be unanswerable without a stored fact" (`growing_store_must_terminate.cut1.json:17-18`).
  - In Vivarium's pointer (boolean grammar v0 at n=3), every term's function is decidable by `truth_table` over 8 rows. The exact minimum of each function is already tabulated (`REPLY_NYX_189...:18-22`).
  - So an organism that ignores the store may be able to answer any "simplify this term" problem directly. Whether this shortcut can be closed in that world is an open question. `out/analysis.py` measures part of it (§6).

## 4. Result

- **Q5a — confirmed, with a correction.** At 5266cce no rewriting kind, executor or owning seat exists (Vivarium #182, Proteus 2026-09-16, kind registry). The lean_simp rewrite-strategy pressures are unhostable. Two corrections:
  - there are at least **five** dependent pressures, not four (`mutual_normalisation.cut2` is unannotated);
  - Nyx's ledgers still record #189 as unanswered.
- **Q5b — the harvest's framing ("no substrate") overstates the gap.** Three rewriting executors are committed: D3 `s3_trs.py`, D4 `S3_REWRITE` and the Techne egglog adapter. [redacted] had recommended adapting `s3_trs.py` for a rewriting world before the thread began. None of the three meets the pressures' requirements as they stand; each lacks at least one of:
  - a growing store held as data;
  - tree terms;
  - world-owned step counting with fixpoint and exhausted distinguished (only `s3_trs`/`S3_REWRITE` have this);
  - per-fact examination counts;
  - a fired-fact trace.
  The real gap is **ownership plus instrumentation**, not the rewriting mechanism itself.
- **Q5c — the repo does not settle "should".**
  - What it supports: the gap is real and specific. The missing piece is small; the pressures spell out the needed instrumentation (step log, examination counts, fired-fact trace). Building parts exist.
  - What it does not support: that hosting would pay off. No run on any rewriting-as-world setup exists. Both rewriting-as-genome substrates were killed. The previous acquisition justified by rewriting leverage went unused. No seat has claimed ownership. The candidate world has an unmeasured vacuity risk.
  - **Conditional answer:** host it only if (i) a seat claims the semantics and (ii) a pre-run eligibility/vacuity check on the candidate world is non-vacuous (planted looping pairs > 0; the undisciplined store hits the budget and the disciplined one does not; the direct-evaluation shortcut is closed). Otherwise it stays a coverage note.
- **On the harvest label.** "New-lens signal (strong)" is supported as a *coverage* signal: an entire mechanism class currently has zero routes into selection. It is not supported as evidence of *value*.

## 5. Limits

- **Comms rows.** I did not read comms rows 188, 189 or 276. Their committed copies agree with the harvest quotes, but I cannot rule out uncommitted follow-ups in the comms DB after 2026-09-16.
- **Search coverage.** Grep may miss rewriting code under other names, such as normalisers inside the Lean ablation tooling or fossil specimens (for example the eprover fossil). I excluded `techne/fossils/**` payloads from the egglog sweep. Fossil specimens are frozen third-party bytes, not hosted substrates.
- **Relevance of the kills.** Whether the D3/D4 kills matter for a rewriting-*world* is my argument. Neither verdict addresses store discipline.
- **Vacuity risk is unmeasured.** The boolean-grammar vacuity concern is an inference. `analysis.py` is written but not run.
- **"Should" is a question of values and priorities.** This report bounds it with evidence; it does not decide it.

## 6. What would change the conclusion

- **A seat claims ownership** (Techne, Herakles or [redacted], via an ADAPT of `s3_trs.py`), or a Vivarium rewriting kind is committed. Then Q5a flips to "hostable" and the question becomes one of operation.
- **`out/analysis.py`** (stdlib only). It mirrors `proteus/eval/boolean.py@5266cce` (grammar lines 59-60, oracle semantics lines 122-136) and runs a naive exhaustive first-match rewriter over true boolean identities. What would decide:
  - planted permutative/inverse pairs > 0 (eligibility; stated in the record at `growing_store_must_terminate.cut1.json:16`);
  - the undisciplined store hits the step budget on a large fraction of problems after planting, while the size-decreasing-orientation store does not (the cheat control, :23);
  - the two score the same with no planted pairs (the negative control, :24).
  If the cheat control separates the two, the boolean-v0 pointer is a live world for that pressure, which strengthens "host". If it does not separate them, or the direct-evaluation baseline matches the rewriter's answers on every problem, the pointer is vacuous and a different term language is needed, which weakens "host on this pointer". I have not run it and do not state its output.
- **A pilot showing that simplification strategy (store discipline) is selectable in a rewriting world** would move Q5c from "conditional" to "yes". A pilot showing the same dead-geometry failure as D4 [redacted] would move it toward "no".
- **Evidence that the egglog adapter has consumers beyond `ergon/gen0/family_b_probe.py`,** or that it exposes iteration and fired-rule reports, would reduce the build cost.



======== REPORT X015 ========

# [redacted] — Residual bridges (H-D5-56) and incidents as splittable hypotheses (H-D5-55)

Repo: read-only checkout at 5266ccebe. All citations are `path:line` at that commit unless a different commit is named. I did not run any code.

## Questions
1. **H-D5-56.** If residuals from all engines are clustered by failure signature, do shared signatures point to shared mechanisms? And has any such clustering been built and checked against a family-shuffled null?
2. **H-D5-55.** Should causal-lineage clustering treat each incident as a hypothesis ("these observations share one cause"), with split() so that one failure cannot hide another? And once a live population exists, does adversarial ancestry predict which descendants break?

## Method
- Read the sources the harvest names: the residual spec, the Hermes convergence probe, and the Nemesis archaeology.
- Searched the repo for anything that implements or tests these ideas: CLUSTER_RESIDUALS, failure_signature, residual stores, split() callers, incident files, and ancestry data in Ares and Nemesis.
- Found an implementation the harvest missed: [redacted]'s cross-agent failure-primitive atlas. Read it in full.
- Checked the one run under [redacted]'s null ladder.
- Wrote `analysis.py` for the only lineage-versus-breakage computation the repo can support. It is not run.

## Evidence

### A. CLUSTER_RESIDUALS was never built, and no residual corpus exists to cluster
- The spec defines `CLUSTER_RESIDUALS`. A cluster needs ≥3 residuals from independent claims with cosine > 0.8 in failure_signature space (`[redacted]/memory/architecture/residual_primitive_spec.md:178-185`). The spec's only example is labelled "Hypothetical" (`:191`).
- The spec's own status section lists CLUSTER_RESIDUALS and the null-baseline pilot as "still spec-only" (`:218-221`), and "Out of scope for first pass; do it manually" (`:230`).
- `sigma_kernel/residuals.py` has no `failure_signature` field. It stores a `failure_shape` JSON string in a SQL table (`sigma_kernel/residuals.py:137,187-202`).
- I found no committed residuals database or dump from real engine runs. `record_residual(` is called only from tests and benchmarks (search result; absence is not proven from git history).

### B. What did get built: agent-level failure-shape clustering with an independence rule
- [redacted] Proposal D (`[redacted]/proposals/2026-06-09/D_cross_agent_failure_primitive_atlas.md:59`) became `[redacted]/primitives/failure_primitives.py`. It is the H-D5-56 idea lifted from claim residuals to agent failures.
- Its null-like safeguard is **lineage independence**, not shuffling. Anchors that share a code or authorship lineage count once (`failure_primitives.py:12-14,76-86`).
- State as of the last registry commit (2026-06-15):
  - FP-003 bounded_menu_wall: **coordinate_invariant**. It has 3 lineages judged code-disjoint by import analysis (`:386-478`).
  - FP-001 baseline_costume: surviving_candidate, 2 lineages (`:324-343`).
  - FP-004 degenerate_field_flatline: surviving_candidate. It has 4 anchors, but the independence audit "was NOT run (blocked by the Anthropic spend limit)" (`:532-542`).
  - FP-002 opaque_kill_black_hole: shadow, 1 anchor (`:361-373`).
  - 89 further candidate shapes are "mostly unaudited shadows" (`:546`).
- **Answer to "do shared signatures point to shared mechanisms?" — for the one invariant shape, NO.**
  - FP-003's three anchors have three *different* mechanisms: region_empty, source_saturated and expressiveness_ceiling (`:444-448,479-490`).
  - Two of them call for *opposite* remedies (STOP versus GROW). The atlas flags this as the "SHARPEST OPEN CRITIQUE" and still owes a subclass-discriminator probe (`:471-478`).
  - The atlas explicitly reads heterogeneous causes under one shape as *strengthening* shape invariance (`:446-448`). So what it shows is a shared observable. It does not show a shared mechanism.
- Later evidence ([redacted], September):
  - FP-001, FP-003 and FP-004 recurred in September engines, and each recurrence was "rediscovered without citation" (`roles/[redacted]/challenge/FAILURE_PRINCIPLES.md:867-898`).
  - The September data add a fourth FP-003 cause, "expressible but unreachable". They also falsify FP-003's predicted GROW escape: growing the menu still gave 0/4,881 useful children (`:877-885`, FR-132).
  - So the shape recurs, the mechanism under it keeps splitting, and the remedy the shape attached did not transfer.

### C. The family-shuffled null has been run exactly once, and it came out NULL
- Null-2 ("operator-/family-shuffled near-math … beating THIS is what means something") is defined at `[redacted]/docs/failure_signal_protocol_v0.1.md:221-224`.
- It was run once, frozen before the run, as H5a OEIS MVP (`[redacted]/results/h5_oeis_mvp_2026_06_04.json:2-3`). Real lift@100 was 200.1 against 169.1 under the operator-shuffle null; verdict **NULL** (`:185-189`).
- The file also records "Family metadata absent … holdout is random" and 3 of 5 controls as STUB (`:24-30,190`).
- This is not a residual clustering. It is still the only committed execution of the null that H-D5-56 says the idea needs.
- No failure_signature cluster from any engine has been tested against a family-shuffled null.

### D. Splittable incidents: built and tested on fixtures, never used on a live incident, and the one live incident already gathers several causes
- The probe establishes the design: a symptom key can gather two causes (CTL-2), so an incident is a HYPOTHESIS. split() moves observations with pointers both ways and no loss, tested as 5 = 3 + 2 (`roles/Hermes/CONVERGENCE_PROBE_2026-09-11.md:65-70,174-179`). Code: `roles/Hermes/science/convergence/record.py:125-154`.
- split() is called only in the test (`roles/Hermes/science/convergence/test_convergence.py:204`, search result).
- The single live incident is `roles/Hermes/incidents/c84e26826cc12217.md`. It is a hand-kept OCCURRENCES table with 11 entries from 2026-09-11 and 2026-09-16, not record.py's format (`:25-52`). No split was ever performed on it.
- Under one symptom key, it records at least three distinct fix paths:
  - comms, closed structurally (`:56-62`)
  - Evidence Wiki, OPEN, accepts writes silently (`:63-71`)
  - Vivarium's viv/db.py, which "had NO guard", fixed in place (`:44-49`)
- This is the CTL-2 situation occurring for real: several causes under one key, resolved by annotation, never split.
- The probe's own falsifier for the design, "seats do bury one failure inside another despite split()" (`CONVERGENCE_PROBE:263-267`), has therefore not been tested. Nobody has used split() yet.

### E. Adversarial ancestry: no live population, and ancestry data are either unused or not saved
- Nemesis: "52 of 92 records carry lineage_depth > 0 and no use was ever made of them." NEM-A4 is PARKED because there is no live population (`roles/Nemesis/ARCHAEOLOGY_2026-09-11.md:145`).
- The ledger is a negative fixture:
  - 292 of 294 tools score below a constant "Not enough information" responder (`:71-89`).
  - Confidence is not discriminative (`:93-96`).
- Each record does carry `lineage_depth` and `tools_broken` (`agents/nemesis/adversarial/adversarial_results.jsonl`, record 1).
- Ares builds a full population ancestry map in memory (`ares/search.py:230,288`) but returns only the champion's chain (`:295-305`).
- Descendant breakage is kept only as a pooled per-generation `mutation_survival` (`:242-247`). The committed `ares/runs/sweep_c1/*_ancestry.json` files hold champion curves and accretion counts, nothing per descendant (search result).
- So no committed data can say whether ancestry predicts which descendants break.

## Result
1. **H-D5-56: NOT ANSWERABLE AS POSED. The adjacent evidence is negative on "shared signature ⇒ shared mechanism".**
   - Residual-level clustering was never built, and no residual corpus exists.
   - The agent-level version (the FP atlas) found one coordinate-invariant shape. Its anchors have 3 or 4 different mechanisms with opposite remedies, and its predicted remedy failed on September data.
   - The one family-shuffle null ever run came out NULL.
   - Within this repo, a shared failure signature has been a good *triage/detector* key and a poor *mechanism* key.
   - The harvest's "later evidence: none found (never built)" is wrong in one respect: the FP atlas (June) and the [redacted] recurrence audit (September) are relevant later evidence.
2. **H-D5-55, first half: YES on design grounds, still unvalidated in use.**
   - The one live incident shows the problem split() exists for: several causes under one symptom key, handled by prose annotation.
   - split() has never been exercised, and the "seats read `prior`" and "don't bury" falsifiers are unmeasured.
   - The FP-003 STOP/GROW collision is the same problem one level up. The atlas has no split operation, only prose subclasses.
3. **H-D5-55, second half: UNTESTABLE on committed data.**
   - There is no live population. The only ancestry-bearing ledger is a negative fixture, and Ares discards non-champion ancestry.
   - `analysis.py` sets out the only possible check, on the Nemesis ledger, with a pre-fixed rule. Even a positive result there would be a lead, not an answer.

## Limits
- My "never built / never used / no data" claims rest on repo-wide text search at 5266ccebe. I did not check full git history, and uncommitted artifacts (e.g. Nemesis's untracked `reports/`, `nemesis.log`) are invisible to me.
- Most FP-atlas independence rulings were done by [redacted] on itself. FP-003's third anchor used a local audit, not the multi-probe one (`failure_primitives.py:457-461`).
- H5a is an OEIS void-recovery test, not residual clustering. I cite it only as the precedent for the required null.
- I did not verify the [redacted] recurrence mappings (R-numbers, FR-132) against their primary artifacts.

## What would change the conclusion
- A committed residual store from ≥2 engines, clustered by failure_signature, where a cluster beats a family-shuffled (Null-2) baseline *and* the members share a mechanism confirmed by an intervention. That would turn H-D5-56 positive.
- A subclass-discriminator probe showing FP-003's causes separable from the event series alone. That would show one signature can carry the mechanism (the probe owed at `failure_primitives.py:477`).
- A real split() on c84e26826cc12217 (e.g. comms / EW / viv), or evidence that some seat buried a cause despite split(), would test H-D5-55's design.
- Ares persisting the full `ancestry` dict plus per-child fitness, or a revived Nemesis population that beats its constant-responder floor. Either would make the ancestry question testable. Running `analysis.py` gives only a fixture-bound hint. Its verdict is decided by the pre-fixed rule in its docstring (p < 0.01, rho > 0, ≥ 20 effective depth>0 records within NEI×category strata).

