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



======== REPORT X009 ========

# Report: why non-additive task families never qualify in the G4 foundry

## 1. WHAT I SET OUT TO TEST

[redacted]'s second recursion-campaign execution (commit 4f937e88f, branch
origin/[redacted]/a16-campaign-2026-09-26) got a valid "no" on bounded recursive
self-improvement. The seat itself put a caveat on that answer: the catalog could only
contain additive and subtractive folds, which is exactly the ground the inherited
abstraction already covers. In both catalogs the mul, mod and powr strata accepted 0 of
32 draws each, and fdiv and gcd accepted almost none. The report blamed a sampler
"dominated by degenerate draws" and proposed a new sampler that excludes degenerate
witnesses. I tested whether that diagnosis is right. The question was whether
non-additive families fail because the sampler draws degenerate witnesses (such as
division by constant 0 or pow with a non-positive base), or because of a real property
of the task space and the qualification instrument. The answer decides whether a
cleaner sampler could ever supply the non-additive families that a meaningful
recursion test needs.

## 2. WHAT I DID

Inputs, all committed at 4f937e88f and exported with `git archive` into
work/[redacted]/src:
- roles/[redacted]/engine/A17_DRAWS_2026-09-26.json (the drawn catalogs A and B)
- roles/[redacted]/engine/A17_FOUNDRY_EVALS_2026-09-26.jsonl (verdicts for all 416
  evaluated draws: [redacted] size, [redacted] result, [redacted] pilot)
- the code in a17.py, meta_tribunal.py, basis_v4.py, engine.py and tier3e.py

Scripts are in work/[redacted]/analysis/, with outputs next to them:
- **join.py** joins each draw to its verdict and gives the stage where it was rejected
  (rows.json). It reproduces the report's totals exactly: 151 rejected at [redacted], 233 at [redacted]
  and 12 at [redacted].
- **diag.py** takes each of the 416 draws, builds the TRUE witness artifact exactly as
  a17.job_q23 does (emitter 2), and re-scores it with the real MetaTribunal. I call the
  tribunal's input sets "batteries". It also records:
  - the fraction of tribunal instances whose gold is "None" (overflow above 1e40, or an
    exception);
  - whether the witness is invariant under the tribunal's own permutation probes;
  - the number of distinct outputs and the dependence on the input values at search
    lengths;
  - a counterfactual score in which gold "None" counts as matched by the artifact's
    "overflow" or None.

  Output: diag.json, summarised by tab.py into tab.txt.
- **census.py, core_census.py and sens.py** make an exhaustive census of the G4 fold
  space in the form a17.draws samples it: every init in H1_SPACE times every body with
  the given top operator that mentions both acc and v. That is 424 (init, body) cores
  per stratum, and 27,136 programs per stratum once finals are included. They use fixed
  batteries that copy the tribunal's distributions:
  - 150 held-out instances of length 20-60;
  - 40 stress instances of length 200;
  - 40 counterexamples of length 2, 3, 80 or 150, with m in {1, 2, 3..97};
  - 25 permutation pairs.

  Each core is classified as:
  - **admissible:** defined on at least 99% of each battery, and defined and invariant
    on all permutation probes;
  - **non-degenerate:** strong means at least 10 distinct accumulator values and at
    least 20% dependence on the values after the first; weak means at least 2 and 5%;
  - **novel:** its accumulator behaviour is not identical to any add or sub core.

  sens.py repeats the census with the overflow requirement relaxed, the
  order-invariance requirement relaxed, and both relaxed (sens.txt).

Everything was run with
`env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE python3 <script>`, with 2 worker
processes.

## 3. RESULT

**A. The stratum gap is created almost entirely at [redacted], the hostile tribunal applied to
the TRUE witness.** It is not created at [redacted], the identifiability check where degenerate
draws fail.

| Stratum | Pass [redacted] | Pass [redacted] given [redacted] |
|---------|---------|------------------|
| add     | 29/42   | 11/29            |
| sub     | 43/54   | 13/43            |
| mul     | 42/64   | 1/42             |
| fdiv    | 49/64   | 2/49             |
| mod     | 37/64   | 1/37             |
| gcd     | 26/64   | 3/26             |
| powr    | 39/64   | 1/39             |

The [redacted] failures are the low-information draws: median 1-2 distinct outputs in mul, powr,
add and sub. They occur at similar rates in add and sub. I re-scored [redacted] on every draw
that passed [redacted] and got the same verdict every time (0 mismatches).

**B. Why the true witness fails [redacted], among draws that passed [redacted] and failed [redacted]:**

| Stratum | Undefined only | Order-dependent only | Both |
|---------|----------------|----------------------|------|
| mul     | 21             | 3                    | 17   |
| powr    | 0              | 0                    | 38   |
| fdiv    | 0              | 14                   | 33   |
| mod     | 0              | 11                   | 25   |
| gcd     | 1              | 16                   | 6    |

"Undefined" means the gold is None on more than 1% of instances in some battery. Real
product and power folds are necessarily undefined at the tribunal's lengths: with
values of 2-30, a product passes 1e40 after about 30-130 elements. For mul, the median
share of stress instances that are undefined is 100%. In fdiv and mod, "undefined" is
mostly division by zero once the accumulator reaches 0. "Order-dependent" means the
tribunal's metamorphic check fails. Its docstring assumes that "every declared body is
commutative-associative over the sequence", but the G4 sampler does not impose that, so
the check filters out almost every sequential mod, fdiv or pow fold.

**C. An instrument defect on top of this.** On any instance where the true value
overflows or raises, the gold is str(None) = "None". The emitter-2 artifact returns
"overflow" there, or None on an exception. So the TRUE witness is scored wrong on
instances it gets right by construction:
- 223 of 416 true witnesses score below 0.99 on some accuracy battery.
- With that encoding repaired, all 416 score 1.00. The encoding is the only difference
  between witness and gold.
- The repair alone would lift [redacted] passes for mul from 1 to 22, add from 11 to 15, sub
  from 13 to 18 and gcd from 3 to 4. It would not change fdiv, mod or powr.
- The 21 extra mul families would be families whose answer is "overflow" on 50-100% of
  stress instances, so the repair does not produce useful families.

**D. Exhaustive census of the whole grammar (sens.txt), under the current strict
tribunal:**
- Admissible, strongly non-degenerate cores: 6 in mul, 0 in fdiv, 2 in mod, 7 in gcd and
  0 in powr. In add and sub the counts are 152 and 100.
- Of the 15 non-additive-stratum cores, 12 behave exactly like an add or sub core. An
  example is (1 * (acc + v)). The novel behaviours that remain number 0 in mul, fdiv, mod
  and powr, and 2 in gcd: gcd over (first % v), and gcd(last, product of v).
- With the weak threshold, the novel behaviours are 0 in mul, 1 in fdiv, 2 in mod, 9 in
  gcd and 11 in powr. Almost all of them are 0/1-valued predicates, for example
  "some v shares a factor with last" or "some exponent was 0".

Relaxing the tribunal opens the space. Counts are distinct strongly-novel behaviours:

| Tribunal setting | mul | fdiv | mod | gcd | powr |
|------------------|-----|------|-----|-----|------|
| Current (strict) | 0   | 0    | 0   | 2   | 0    |
| Overflow accepted as an answer | 16 | 0 | 0 | 2 | 0 |
| Order-invariance dropped | 13 | 20 | 25 | 47 | 7 |
| Both relaxed | 61 | 20 | 25 | 47 | 13 |

**E. The only non-additive draws that passed [redacted] and [redacted] are degenerate or additive in
disguise, or they are gcd or predicate families.**
- Rejected at [redacted] as too easy (PRISTINE 16/16):
  - (1 * (v + acc)), which is a sum;
  - gcd(0, acc + v), also a sum;
  - 1 % gcd(...), which is constant;
  - pow(v, 0 - acc), which only depends on the last v;
  - v // (acc + v).
- Accepted:
  - gcd(last, v * acc);
  - gcd(acc, first % v);
  - acc // gcd(v, last), a predicate.

**Plain conclusion:** mul, mod and powr go to 0 because of how the task space and the
tribunal fit together, not because of degenerate witnesses:
- The tribunal demands totality under a 1e40 ceiling at length 200, and invariance to
  the order of every element after the first.
- In this grammar almost no non-additive fold meets both demands without collapsing
  into something additive or trivial. Growth folds overflow. Sequential mod, fdiv and
  pow folds depend on order or divide by zero.

A sampler that only excludes degenerate witnesses would, by this census, still find
0-2 genuinely new qualifiable behaviours per non-additive stratum, nearly all of them
gcd.

## 4. DID IT RESOLVE THE QUESTION

**Yes, for the question actually posed:** was it degenerate witnesses or a real property
of the task space?
- The mechanism is identified per draw, and it is reproduced exactly with the seat's own
  tribunal code.
- The census covers the entire sampled grammar, not just the 416 draws.

**Only partly for the question behind it:** can an inherited abstraction derive
something new when the task supply contains families it does not explain? That needs
a new catalog and a donor assay, which is out of scope and would need a new preregistration.

Caveats:
- The census uses batteries with fixed seeds that copy the tribunal's distributions, not
  the per-family tribunal seeds. The per-draw part uses the real ones.
- "Novel" means not behaviourally identical to an add or sub core on about 150 probe
  inputs. It is not a semantic proof.
- [redacted] and [redacted] were not applied in the census, so the census gives upper bounds on what
  could qualify.

## 5. CONSEQUENCES

- **False premise.** The explanation "the sampler is dominated by degenerate draws" is
  right about [redacted] but not about the gap between strata. The proposed repair, a sampler
  that excludes degenerate witnesses, would not supply mul, mod, fdiv or powr families.
  It should not be preregistered on the expectation that it would.
- **Instrument defect.** In the tribunal (meta_tribunal.py together with
  basis_v4.run_program and the gold construction), gold "None" never matches the
  artifact's "overflow" or None. The TRUE witness is therefore marked wrong on
  instances it gets right. This affects 223 of 416 draws. It is small in effect on
  qualification, but it is a real mismatch between the emitter and the gold, and it
  should be fixed or explicitly declared.
- **Design constraint to surface.** The metamorphic check assumes bodies are
  commutative-associative. The G4 sampler does not impose that, so the tribunal quietly
  restricts the catalog to order-invariant folds. The stress lengths together with the
  1e40 ceiling exclude every growth fold. Either the tribunal must change (drop or
  condition the permutation check, use length regimes suited to each operator, treat
  "overflow" as an answer), or the grammar must (bounded operators such as max, min or
  a modulus applied at the top level, or bodies whose modulus is on the left). Without
  one of these, no non-additive supply is possible.
- **Labelling issue.** The stratum is taken from the body's top operator, which does not
  match the semantics. (1 * (acc + v)) counts as "mul". A real "sum mod m" family lives
  in the "add" stratum through the final (acc % last).
- **Who should know:** the [redacted] seat (foundry and tribunal owner) and whoever
  decides on the next recursion prereg. The recursion "no" should be kept explicitly
  conditional: with this instrument, a treatment-blind catalog cannot contain a
  non-additive family at all, apart from a handful of gcd or predicate folds.

## 6. COST

- About 50 minutes of my own time.
- About 11 CPU-minutes in total, never more than 2 processes, under 100 MB of RAM.
- I did not rerun [redacted] or [redacted] on counterfactual draws, build a new catalog, or run any
  donor assay. Those would need a new preregistration and more budget.
- No sealed data or holdout was touched, and nothing was written to the repository.



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



======== REPORT X007 ========

# [redacted] / H-D4-20 -- H3: does any archive/QD policy beat top-K on a real stream, and do the descriptors resolve anything?

Read-only analysis of repository commit 5266ccebea3ad5522b7cfa7a07a8718cac113a70. No code was run.
Any figure below not quoted from a committed file is my hand arithmetic on committed per-seed rows,
labelled as such. `out/analysis.py` recomputes it, and its output takes precedence over mine.

## Question

With retention budget held equal, does an archive or quality-diversity (QD) retention policy
(`behavioral` grid, `hybrid`) beat plain top-K / sequential-champion retention on a stream? And
does any declared descriptor pair separate candidates in a way that tells us something?

## Short answer

- **On a real stream: no evidence either way.** The only real stream is cs-c3-2, and it cannot
  answer the question. All 120 acquisition-arm candidates score exactly 0.0. The only
  per-policy scores on it come from query types that the program's own dead-stream control
  ruled unsafe.
- **On the synthetic stream (the dead-stream control v2, the only stream with a planted
  relation): no QD policy beats top_k.** On the live arm, top_k was at least as good as
  `behavioral` and at least as good as `hybrid` on every one of 5 seeds. Hand-computed paired
  means were +1.2 tasks (SE about 0.49) over `behavioral` and +1.4 (SE about 0.68) over
  `hybrid`, out of 12. Neither gap clears a df=4 t-threshold. So the result is "no QD
  advantage", not "top_k proven better". This is consistent with the external prior art
  (Chen 2026, no archive advantage at matched budget).
- **The descriptors resolve occupancy, not the relation.** The v1 equal-mass descriptors spread
  the random arm from 4 cells to 15 of 16. But coverage/occupancy was shown to be identical to
  the cell between a live stream and its score-permuted twin. So the descriptors separate
  candidates by table statistics, and that separation carries no information about which
  candidates are good. No behavioural descriptor has been tried.
- **Status:** the harvest entry's "later evidence: none found" still holds for a real or
  generated beta stream. ARCH-07 is open, TECHNE-03 runs on request only, and C3-3 is
  unissued. It is partly answered by the synthetic control, which the harvest entry quotes
  only for its caveat.

## Method

1. I read the three cited sources in full: the dead-stream readout, Techne's alpha receipt and
   [redacted]'s backlog.
2. I searched the tree at the pinned commit for later H3 work: ARCH-07, H3 beta, TECHNE-03,
   generated stream, the Chen 2026 citation, the sealed future-query scoring (TECHNE-24) and
   C3-3 issuance.
3. I extracted per-seed `family_b_solved` for every policy and arm from the committed v2
   control rows, and formed paired top_k − QD differences by hand.
4. I read the per-policy tallies from the committed TECHNE-24 receipt on the real stream, and
   classified each true answer as a score-threshold query or a cell-occupancy query.

## Evidence

### E1. The real stream cannot discriminate policies

- cs-c3-2 has 150 candidates. **126 of 150 score exactly 0.0, including all 120 random
  rules** (`roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:123-125`).
- Under the v0 descriptors, the 120 random rules fall into four cells
  (`roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:114-119`).
- In the three tie-dominated cells, all 107 candidates are exactly 0.0
  (`roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:135-150`).
- The receipt itself refuses to rank policies
  (`roles/Techne/H3_ALPHA_RECEIPT_2026-09-10.md:182-187`).
- [redacted]'s verdict says nothing about a real C3/H1 stream: "none exists yet: C3-2's random
  arm was constant zero and C3-3 is unissued"
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:130-131`).
- C3-3 issuance "still waits on the operator's word" as of 2026-09-16
  (`roles/[redacted]/BACKLOG_H0H5.md:51`).

### E2. Real-stream sealed-query scores exist, but only on unsafe query types

The TECHNE-24 receipt scored cs-c3-2 against the 12-query sealed manifest (digest de4cae9b),
and was "SCORED_WITHOUT_RANKING"
(`techne/acquisition/receipts/adapter_qualification-pyribs-20260911T065018Z.json:775,780`;
`roles/Techne/BACKLOG_H0H5.md:34`).

| Policy | True answers (of 9 scorable) | Receipt lines |
|---|---|---|
| top_k | 4 | :309-310 |
| uniform | 6 | :441-442 |
| behavioral | 7 | :573-574 |
| hybrid | 6 | :705-706 |

- Two of the nine are unattainable by any policy (:771-774), which leaves 7 that discriminate.
- The three transfer queries cannot be scored (:776).
- top_k's 4 are all score-threshold queries, and it misses every cell query (:187-280). The
  gap in `behavioral`'s favour is made up entirely of `occupies_cell` answers.
- The dead-stream control ruled exactly these two query families UNSAFE:
  - coverage/occupancy "does not see whether a stream carries a relation";
  - score-threshold reuse "measures the score marginal, not reuse".

  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:50-52,117-124`.)
- So the 7-vs-4 real-stream tally is not evidence that QD beats top_k. It measures the fact
  that a grid archive fills cells. Even `uniform` (6) beats top_k on it.

### E3. The synthetic stream: top_k at least as good as QD on every seed

Setup: 200 candidates, v1 descriptors, 16-item cap, reserve 4, 5 seeds, and 12 hidden 5-bit
tasks sealed before the run. The predictions and the v2 addendum were committed before the
v2 run (`[redacted]/docs/h0h5/H3_DEAD_STREAM_PREDICTION_2026-09-11.md:9-27`;
`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:59-86`).

Means as committed (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:93-97`):

| Policy | family B, live | family B, dead | family B, cheat |
|---|---|---|---|
| top_k | 10.4 | 4.2 | 10.6 |
| uniform | 4.2 | 4.2 | 4.2 |
| behavioral | 9.2 | 4.4 | 10.6 |
| hybrid | 9.0 | 4.0 | 10.2 |

Per-seed live-arm rows (`[redacted]/docs/h0h5/H3_DEAD_STREAM_CONTROL_v2_2026-09-11.json`; the
line numbers are the `family_b_solved` fields):

| Policy | seed 1 | seed 2 | seed 3 | seed 4 | seed 5 | Lines |
|---|---|---|---|---|---|---|
| top_k | 8 | 11 | 10 | 11 | 12 | :51, :317, :583, :849, :1115 |
| behavioral | 7 | 11 | 7 | 10 | 11 | :91, :357, :623, :889, :1155 |
| hybrid | 7 | 11 | 6 | 10 | 11 | :111, :377, :643, :909, :1175 |

Hand arithmetic, to be confirmed by `analysis.py`:

| Paired difference | Per seed | Mean | SE | t | Seeds won / lost |
|---|---|---|---|---|---|
| top_k − behavioral | 1, 0, 3, 1, 1 | +1.2 | ≈0.49 | ≈2.4 | 4 / 0 |
| top_k − hybrid | 1, 0, 4, 1, 1 | +1.4 | ≈0.68 | ≈2.1 | 4 / 0 |

- The critical t at df=4 is 2.78, so neither gap is significant. The exact two-sided sign test
  on 4 wins and 0 losses gives p = 0.125.
- On the cheat arm, top_k and `behavioral` are tied (10.6 vs 10.6).
- The readout says the three score-retaining policies' "differences here are within one SE of
  each other" and makes no ranking claim
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:131-133`). The paired view here
  sharpens that: every seed where the policies differ favours top_k, not QD.
- At the ceiling (v1, 3-bit tasks), top_k was 12.0, `behavioral` 11.8 and `hybrid` 11.8
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:10-13`). No QD advantage there
  either, although the ceiling makes that uninformative.
- Where QD does "win" in v1 is family A (`behavioral` 8.0 vs top_k 6.2), which again includes
  cell-occupancy queries (same lines). That is unsafe by E2.

### E4. What the descriptors resolve

- The v0 equal-width edges put 120 random rules in 4 cells (E1). The v1 equal-mass edges are
  the quartiles of Binomial(128,1/2) × Binomial(64,1/2)
  (`[redacted]/docs/h0h5/H3_DESCRIPTORS_v1.json:12-17,27-31`). On cs-c3-2 they put the random
  arm into **15 of 16 cells** (commit 2baf0680f message: "cells occupied v0: 8 of 16 v1: 15 of
  16; random rules in v0: 4 cells v1: 15 cells").
- The declaration itself says v1 "does not separate rules by behaviour; two tables in one cell
  may compute very different things. A behavioural descriptor is a different experiment and
  would need the C3-3 criterion first"
  (`[redacted]/docs/h0h5/H3_DESCRIPTORS_v1.json:35-36`).
- With v1 edges, coverage was identical between a live stream and its score-permuted twin "to
  the cell ... for every policy, on ten runs"
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:100-101,117-122`). So the
  descriptor separation is orthogonal to the fitness relation.
- On cs-c3-2 the separated random arm is a zero plateau, so no descriptor can make it
  informative for score-based retention.

### E5. Prior art and open work

- Chen 2026 (arXiv:2608.19703, "Loreley") is marked VERIFIED, with the note "the verified
  contrast is at 48" jobs (not 1,008) (`[redacted]/docs/hypotheses/H1/CITATIONS.md:69-72`).
- It is summarised as "NO archive advantage over a sequential champion at matched budgets"
  (`roles/[redacted]/REVIEW_PACKET_2026-09-10.md:260-261`).
- ARCH-07 (the generated 1,024-candidate beta stream with sealed queries) has no completion
  annotation (`roles/[redacted]/BACKLOG_H0H5.md:9`).
- TECHNE-03 (the CVTArchive comparator) is "only when Ludus/[redacted] ask"
  (`roles/Techne/BACKLOG_H0H5.md:13`; `roles/Techne/DONOR_FOUNDRY_CLOSEOUT_2026-09-12.md:125`).
- There are no H3 files under `[redacted]/docs/h0h5/` after 2026-09-11. In the git log, the last
  commit touching the H3 replay, seam or readout is 179cd46e4 / 11730100c, on 2026-09-11.
- A crosswalk entry notes that a QD advantage "cannot appear on onemax" and needs a deceptive
  landscape (`[redacted]/docs/expansion/CROSSWALK.md:720`).

## Result

1. **Does a QD policy beat top-K on a real stream?** Unanswered. It cannot be answered from
   committed content: no informative real stream exists. The one real-stream tally that favours
   `behavioral` (7 vs 4) comes only from cell-occupancy queries, which are certified unsafe.
2. **On a generated or synthetic stream at matched budget?** No. In the only such experiment
   (dead-stream control v2, live arm), neither `behavioral` nor `hybrid` beat top_k on any seed.
   top_k is ahead by +1.2 and +1.4 tasks of 12, and that is not significant at n=5. This agrees
   in direction with Chen 2026.
3. **Do the descriptors resolve anything?**
   - They resolve occupancy: v1 gives 15 of 16 cells for the random arm, against 4 under v0.
   - They do not resolve the organism→score relation: coverage is blind to it.
   - No descriptor pair tested so far separates candidates by behaviour or by stepping-stone
     value.
   - The neutral zero plateau on cs-c3-2 stays invisible to the archive, as the harvest entry
     feared.

## Limits

- The synthetic stream is not deceptive. Its score is agreement with a hidden target on
  random-table tasks, and its descriptors are table statistics unrelated to the target, which
  structurally favours top_k. QD's theoretical advantage (stepping stones on deceptive
  landscapes) was never put to the test.
- The control was designed as a dead-stream instrument check, not a policy comparison. The
  paired statistics here are post hoc, and n=5 seeds.
- Only direct reuse was measured, with no adaptation or search from the archive
  (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:133-134`). That is the setting
  where archive stepping stones would matter.
- On seed 1 of the synthetic run, `behavioral` and `hybrid` retain 16 items, like top_k (JSON
  `retained_n`), so the budget is matched on items. I did not read the other seeds' counts.
  Byte caps never bound (`[redacted]/docs/h0h5/H3_DEAD_STREAM_READOUT_2026-09-11.md:91`).
- The pinned tree may lack uncommitted or unmerged work, for example on other branches. I did
  not search all branches for ARCH-07 output.

## What would change the conclusion

- An ARCH-07-style generated stream with a policy-independent generator and queries sealed
  first, on which `behavioral` or `hybrid` beats top_k on family-B-type (task-level reuse)
  queries with paired t > 2.78. That would overturn "no QD advantage".
- A deceptive-landscape stream (a planted stepping-stone relation) where top_k's retained set
  cannot reach the high-value region. This is the first test that could favour QD at all.
- A behavioural descriptor (for example the C3-3 cellwise criterion) under which live and dead
  coverage *differ*. That would show descriptors resolving the relation.
- C3-3 issued with a non-constant acquisition arm, giving a real stream with score variance.
- If `analysis.py` shows my per-seed extraction is wrong (for example, if top_k − behavioral
  is negative on any seed), claim C3 must be revised.



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

