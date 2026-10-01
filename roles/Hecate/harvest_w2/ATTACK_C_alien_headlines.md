# ATTACK C -- adversarial read of hecate/alien/REPORT_pilot.md headlines (Family A, Claude)

Date: 2026-09-30. Read-only inference over existing rows; no model calls, no git.
Inputs: hecate/alien/runs/claude/{blind,fam,reveal,active,pair,prose}.jsonl,
RESULTS.json; hecate/alien/data/{public,answer_key,BASELINES}.json; hecate/alien/*.py;
PREREG roles/Hecate/prereg/2026-09-30_alien_lawful_assay/PREREG.md.

Reproduction: every snippet below starts with this loader (call it LD), run from
F:/Prometheus-worktrees/hecate-base-role:

    import json,sys; sys.path.insert(0,'.')
    R=json.load(open('hecate/alien/runs/claude/RESULTS.json')); rows=R['rows']; S=R['summary']
    K=json.load(open('hecate/alien/data/answer_key.json'))
    P={e['id']:e for e in json.load(open('hecate/alien/data/public.json'))}
    B={r['id']:r for r in json.load(open('hecate/alien/data/BASELINES.json'))['rows']}
    def jl(t): return {json.loads(l)['sid']:json.loads(l) for l in open(f'hecate/alien/runs/claude/{t}.jsonl',encoding='utf-8') if l.strip()}
    from hecate.alien.systems import parse_state

Summary of verdicts

    1 aliens learned nearly as well as known ........ REVISED (learning = architecture + table fill;
                                                      success tracks data coverage of the rule table)
    2 over-attribution on noise ...................... REVISED (low-confidence RULE that reads
                                                      determinism; 19/19 admit no law; not a model error)
    3 prose hurts aliens only ......................... WEAKENED to anecdote (one system = 73% of drop)
    4 affine (0.44) beats Claude (0.33) on ADV ......... KILLED (unlike sets; like-for-like Claude 0.51 > 0.44)
    5 detector NOT_VALIDATED, caused by ADV/SEDUCTIVE .. decision HOLDS; stated cause REVISED
    6 FAMILIAR at formalism level / CORRECT_ANALOGY ... HOLDS; both FALSE_COLLAPSE cases are artefacts
                                                      and the shear-map narrative in the report is wrong

------------------------------------------------------------------------------------------
## 1. "Claude learns standard aliens nearly as well as known systems (28/32 vs 20/20)"

E1 (strongest for): Claude infers each alien's update architecture (which positions feed
which, sequential vs synchronous, leftmost-first scanning) and writes code that is exact
on held-out states. Code eval states never overlap observed source states (0/200 for all
52 A+K systems), so this is not state memorisation.

E2 (strongest incompatible): the aliens are easy in a way K is not -- arbitrary-table
rules whose relevant table entries are all visible in the 80 observed transitions, so
"learning" = fitting a lookup table that the observations happen to cover; the 28/32 is a
property of the generator's coverage, not of reasoning about unfamiliar law.

Stupid explanations checked:
- State memorisation: KILLED. T2 queries and eval states seen as observed sources: 0 for
  every A and K system.
- Near-identity: not the driver. Rewrite aliens change 12-26% of components per step and
  have trivial bars 0.71-0.88, but K rewrite systems are the same (24-33%, bars 0.67-0.75),
  and the learned criterion is relative to the bar. Exact accuracy (1.00) is not inflated.
- A few families: YES. Per-family A learned: graph 8/8, map 5/5, rewrite 8/8, vm 5/6, tab
  2/5. All 4 non-learned are tab_local (3) plus vm SYS-19722. A has 8 graph + 8 rewrite of
  32; K has 4 per family. Family-balanced A learned rate = (1+1+1+.833+.4)/5 = 0.85.
- Query/table overlap: decisive (below).

Decisive evidence. Instrument each step to list the rule-table entries it consults (graph:
G[x][S mod 4] or F[x_u][x_v]; rewrite: which rule fires; tab: D/U entries) and ask whether
every entry a T2 query needs was consulted somewhere in the observations.

    (LD) + used(p,s) per family; for each A system: seen = union of used() over observed
    sources; per query covered = used(q) <= seen; compare with Claude T2 exact-correct
    and with Claude T5 exact on the 200 eval states (sandbox run).

    T2 (family, covered, correct): n          T5 eval (family, covered, correct): n
      graph   covered   correct  82             graph   covered   correct 1403
      graph   uncovered wrong    14             graph   uncovered correct   15
      rewrite covered   correct  96             graph   uncovered wrong    182
      tab     covered   correct  16             rewrite covered   correct 1562
      tab     covered   wrong     9             rewrite uncovered wrong     38
      tab     uncovered correct   3             tab     covered   correct  274
      tab     uncovered wrong    32             tab     covered   wrong    184
                                                tab     uncovered correct   66
                                                tab     uncovered wrong    476

Per system the match is exact: SYS-12423 7/12 queries covered -> T2 exact 0.58 (=7/12);
SYS-82332 8/12 -> 0.67; SYS-87863 7/12 -> 0.58; every fully covered graph/rewrite system
-> 1.00. On graph+rewrite, covered-state correctness is 2965/2965 and uncovered is 15/235.
Rewrite aliens need only 3-5 rules for all 12 queries and every one was observed.

Attack E1: Claude never generalises a table entry it did not see (0/14 uncovered graph
queries). Attack E2: for arbitrary tables no learner can infer unseen entries; the
non-trivial part (the architecture) IS inferred -- the localtab baseline, also a table
learner, reaches only 0.47-0.85 eval comp on the same systems because it gets the
architecture wrong. Both survive partially.

E3 (rejects the shared assumption that "learned" measures one capacity): the binary
learned rate mixes two things -- architecture identification (essentially solved on
graph/rewrite/map/vm) and table coverage (set by the generator's sampling). The A-vs-K
gap is then (a) tab_local, where Claude fails even on covered queries (16/25 correct; the
lin/cyc correction of one component defeats it), and (b) coverage shortfall on 3 graph
systems. Known systems have no tables, so coverage cannot hurt them.

Distinguishing prediction checked: E3 predicts A errors on graph cluster exactly on
uncovered entries (confirmed, above) and that tab_local errors persist on covered queries
(confirmed, 9/25 wrong). E2-as-pure-memorisation predicts no architecture transfer to
uncovered states with a seen-entry decomposition -- contradicted (eval states are all
unseen, yet 2965/2965 covered states correct).

Side finding (instrument): the sandbox rejected two CORRECT alien programs because they
call a local lambda ("rejected: call f", "rejected: call h"):

    (LD) ns={}; exec(jl('blind')[sid]['parsed']['t5']['code'],ns); compare on eval_states
    SYS-59756 unsandboxed eval exact 1.0
    SYS-96628 unsandboxed eval exact 1.0

The A code-exact mean 0.80 in the report silently excludes these two (status ERROR ->
None). Counting them as scored-0 gives 0.746; counting them correctly gives 0.808.

Verdict: REVISED to "Claude recovers the update architecture of 30/32 standard aliens; its
predictive success then equals the coverage of the rule table by the observations
(graph+rewrite: 2965/2965 covered states exact, 15/235 uncovered). The A-K gap lives in one
generator (tab_local) and in coverage. T2 exact A 0.80 vs K 0.98 is the fairer headline
than learned 88% vs 100% (the learned criterion accepts T2 exact 0.25; SYS-65579 is learned
at exactly 0.25)."
Strongest remaining objection: coverage is per-run luck of one dataset seed; a different
sample of observations would move the learned rate without any change in the model, so
28/32 has unknown dataset variance (not bootstrapped over observation draws).

------------------------------------------------------------------------------------------
## 2. "Over-attribution: noise called RULE/COHERENT"

E1 (for): Claude sees regularity (+-1 steps, fixed points, 2-cycles) in incompressible
nulls and labels it RULE (19/30) / COHERENT (24/30) -- a verbal over-attribution failure.
E2 (incompatible): there is no over-attribution; RULE is a hedged, low-confidence answer
and the T1 score (which uses confidence) already discriminates.

Decisive evidence:

    (LD) confidence by verdict group, from blind.parsed.t1.confidence
    RULE on A        n 32 conf mean 0.873 min 0.75 max 0.97
    RULE on K        n 20 conf mean 0.945 min 0.88 max 0.98
    RULE on DESTROY  n 10 conf mean 0.836 min 0.70 max 0.95
    RULE on incomp   n 19 conf mean 0.664 min 0.55 max 0.85
    UNCERTAIN incomp n  8 conf mean 0.45 ; RANDOM incomp n 3 conf 0.55
    AUC conf (RULE-on-A vs RULE-on-incomp): 0.97

    By null type RULE: CONJ 5/7, DSCRAMBLE 5/11, SCRAMBLE 3/4, SEDUCTIVE 6/8.

    RULE-on-incomp n 19: evidence cites determinism/repeats 15; uncertainty field admits
    no law found 19   (regex over t1.evidence / t1.uncertainty)

    Prediction vs trivial bar on incompressible nulls, by verdict:
    RULE      n 19 mean T2comp-bar -0.036 (3 above bar)  mean T5comp-evbar -0.053
    UNCERTAIN n  8 mean T2comp-bar -0.002 (3 above)      mean T5comp-evbar +0.063
    RANDOM    n  3 mean T2comp-bar +0.065 (2 above)      mean T5comp-evbar +0.053
    RULE-on-incomp learned: 0; behav_score > 0.15: 2

Regularity Claude cites vs what the null preserves (answer_key nuisance + observations):
SEDUCTIVE nulls are built with per-component steps in {-1,0,+1}; max observed circular
step = 1 on all 8, and Claude's evidence cites +-1 steps on 7/8 (regex). CONJ nulls keep
the alien's orbit structure; Claude cites fixed points or cycles on 6/7. These citations
are TRUE of the data. On map DSCRAMBLE/SCRAMBLE (mean step 7-8) Claude says UNCERTAIN
2/2 for DSCRAMBLE but RULE for SYS-70364 (SCRAMBLE map, conf 0.60, cites nothing).

E3 (rejects the shared assumption that the nulls have "no rule"): every null is a
deterministic map on a finite space -- a stable rule (a lookup table) exists by
construction, and repeated states in the observations show it. T1 asks "a stable
underlying rule, or unstructured/random?". Claude answers the question literally: RULE
with low confidence when it sees determinism but cannot compress it.
Distinguishing prediction: E3 predicts RULE-on-noise rises with visible repeats of a
source state. Checked:

    repeats of an observed source state, incompressible nulls:
    RULE median 32.0  vs  non-RULE median 13.0  (AUC 0.67)

Also matches claim 5 (pair misses follow repeats, below). E1 predicts confident RULE with
a claimed compact law and above-bar prediction; contradicted (conf 0.55-0.85, 19/19 admit
no law, T2 below bar).

Verdict: REVISED to "On incompressible nulls Claude says RULE at low confidence (mean 0.66
vs 0.87 on aliens; within-RULE AUC 0.97), cites regularities that are actually present,
admits in 19/19 that it found no law, and predicts at or below the trivial bar. The
categorical label conflates determinism with compact law because the T1 question and the
null construct do (instrument defect, as the report concedes); 'over-attribution' is too
strong a name for a hedged literal answer." The report's own description is accurate; the
headline word is not.
Strongest remaining objection: COHERENT (24/30) carries no confidence field, so the hedge
argument covers T1 only; for the fam task the label is uncalibrated and E1 still applies.

------------------------------------------------------------------------------------------
## 3. "Prose hurts aliens (0.91 -> 0.78) but not known (0.99 -> 0.99)"

E1 (for): words instead of tuples disrupt pattern extraction for unfamiliar rules only.
E2 (incompatible): the drop is one or two rule-search failures in the hardest family;
single runs, no replicate.

Stupid explanations checked:
- Parse/format failures: KILLED. Unparseable or missing predictions: 0 in all 30 prose
  rows and 0 in the matching tuple rows; every row returned 12 predictions.
- Group composition: present. Prose subset = first 2 systems per family (runner.py line
  68), so A-prose includes both poly_sym maps SYS-59756, SYS-96628 (cubic polynomials over
  Z_31); K-prose map systems are rot90 and predprey.
- Regression to the mean: selection was not on score, so classic RTM does not apply, but
  A tuple scores sit at ceiling (6/10 at 1.00) where any run noise can only subtract.

Decisive evidence:

    (LD) per system t2_comp tuple -> prose (RESULTS rows prose_t2), A group
    SYS-96628 map poly_sym 1.00 -> 0.00     SYS-59756 map poly_sym 1.00 -> 0.71
    SYS-44623 tab 0.67 -> 0.68   SYS-65579 tab 0.65 -> 0.60   SYS-69242 vm 0.94 -> 0.90
    other 5 A systems unchanged; all 10 K unchanged.
    Sum of A changes -1.37 => mean -0.137; SYS-96628 alone = 1.00/1.37 = 73%.

Claude's own prose reply for SYS-96628: "I could not extract a clean closed-form rule ...
so I predicted each query by matching it to the most similar observed state". For SYS-59756
it found the structure f(a)+g(b) and tabulated f,g from data, missing entries for
unconnected inputs. Both are search outcomes on the one family where the blind tuple run
also had to discover a cubic. Run-to-run variance on these maps is visible elsewhere: on
SYS-46959 the blind run wrote the exact cubic shear, while the fam run on the same
observations reported "tests of linear, quadratic and cubic forms failed".
Sign test on A: 4 down, 1 up, 5 tied -> p = 0.375.

E3 (rejects that a 10-system mean difference measures representation at all): with one
draw per system the comparison measures the variance of a rule search, which is largest
for the systems requiring search (polynomial maps) and zero for systems at ceiling with
named mechanisms. Prediction: excluding the map family, A shows no prose effect. Checked:
non-map A changes +0.01, -0.05, -0.04, 0, 0, 0, 0, 0 => mean -0.010.

Verdict: WEAKENED to "In one run each, prose coincided with Claude abandoning the search on
one polynomial-map alien (73% of the A drop) and a partial table on the other; outside the
map family the A effect is -0.01. No parse failures. The prose-hurts-aliens-only claim is
not supported at n=10 without replicates."
Strongest remaining objection: the abandonment did happen under prose and not under tuple;
a real representation cost concentrated on hard search problems is consistent with the
rows -- it just is not distinguishable from search variance here.

------------------------------------------------------------------------------------------
## 4. "Adversarial aliens defeat Claude; affine baseline (0.44) beats Claude (0.33)"

E1 (for): a linear change of coordinates hides structure from Claude but not from an
affine search. E2 (incompatible): the two numbers are on different systems.

Decisive evidence. BASELINES.fit_affine runs only when max(dims) <= 7 and len(dims) <= 5;
the 3 map adversarial aliens (Z_31) have no affine row. analyze/summarize averages over
rows that have the key, so the baseline mean is over 5 systems; Claude's is over 8.

    (LD) per ADV system; Claude code re-run on the SAME first 100 eval states the
    baseline used (SB.run(code,'step',eval_states[:100]))
    sid       base           aff_t2c aff_evc | Cl_t2c Cl_evc200 Cl_evc100
    SYS-14818 vm (long-cyc)  0.812   0.808   | 0.958  0.954     0.953
    SYS-37739 linmix tab     0.333   0.196   | 0.300  0.221     0.224
    SYS-41174 linmix map     None    None    | 0.000  0.025     0.020
    SYS-42741 linmix tab     0.200   0.180   | 0.183  0.205     0.210
    SYS-46005 linmix tab     0.300   0.210   | 0.183  0.234     0.206
    SYS-46945 linmix map     None    None    | 0.000  0.035     0.030
    SYS-67061 linmix map     None    None    | 0.042  0.030     0.020
    SYS-70612 vm (long-cyc)  0.792   0.785   | 0.938  0.953     0.948
    ALL 8:          Claude t2c 0.326  Claude evc(first100) 0.326
    AFFINE SUBSET 5: affine t2c 0.488  affine evc 0.436 | Claude t2c 0.512  Claude evc100 0.508

Like-for-like on the 5 systems and the same 100 states, Claude 0.508 > affine 0.436
(same 12 queries: 0.512 > 0.488). On the 3 linmix tab systems both sit at the trivial bar
(0.18-0.23). The 2 adversarial aliens Claude "learned" are exactly the two vm long-cycle
programs (not linear mixes); linmix aliens learned 0/6.

E3: "adversarial" is two different constructions. Linear mixing defeats Claude and every
baseline equally (Outcome E); long-cycle vm programs defeat nothing (Claude 0.95, affine
0.80).

Verdict: KILLED for "affine baseline beats Claude" (an unlike-set comparison: 5 vs 8
systems, the 3 omitted being Claude's zeros). REVISED headline: "Linear coordinate mixing
defeats Claude (0/6 learned) and all baselines alike; on the systems where the affine
baseline exists, Claude matches or beats it." Outcome E for linmix holds, more strongly.
Strongest remaining objection: the affine search is restricted to small coefficient ranges;
a stronger linear-algebra baseline (solve for M over Z_m) might crack linmix tab and make
it LLM-specific after all. Not testable from existing rows.

------------------------------------------------------------------------------------------
## 5. "Detector NOT_VALIDATED because of adversarial/seductive pairs"

E1 (for): T1 AUC passes (0.98, CI low 0.95); pair accuracy 23/30 = 0.767 < 0.80 fails,
and the failures are on adversarial/seductive and scramble pairs.
E2 (incompatible): the failure is not about adversarial structure but about a pair-task
heuristic, and it also hits learned standard aliens.

Decisive evidence:

    (LD) pair misses (choice != lawful), incompressible pairs only
    SYS-28905 SCRAMBLE  adv False  alien learned blind True   map
    SYS-46959 DSCRAMBLE adv False  alien learned blind True   map
    SYS-67770 SCRAMBLE  adv False  alien learned blind False  tab
    SYS-41174/46945/67061 SEDUCTIVE adv True  (map) ; SYS-42741 SEDUCTIVE adv True (tab)
    => 7 misses: 4 SEDUCTIVE, 2 SCRAMBLE, 1 DSCRAMBLE; by family map 5, tab 2.
    incompressible map-family pairs 1/6; non-map 22/24 (Wilson 0.74-0.98)
    standard aliens only 19/22 = 0.864 (Wilson 0.67-0.95); all 23/30 (Wilson 0.59-0.88)

    repeats of an observed source state, alien vs its null, incompressible pairs:
    null has more repeats: 6 correct, 5 MISS ; alien has more: 15 correct, 2 MISS ; tie 2/2
    position: lawful=A chosen 16/20, lawful=B chosen 12/20

Claude's reasons on the two learned-alien misses: SYS-28905 "System B behaves
deterministically across runs: the same state always leads to the same next state"; SYS-46959
"(25,30) is a fixed point ... System A shows no repeats". The bijective map aliens have long
orbits and show no repeats in 8x10 steps; the nulls do. Claude in the pair task does not
fit a rule, it ranks visible recurrence -- the same determinism reading as claim 2.

E3 (rejects that "pair accuracy" measures novelty detection): the pair prompt asks which
system "shows stronger evidence of a compact lawful mechanism" from raw runs; the model
answers with a recurrence heuristic, so pair accuracy is a recurrence-contrast score.
Prediction: misses concentrate where the null shows more repeats -- confirmed 5/11 vs 2/17.

Verdict: the DECISION HOLDS (preregistered rule applied correctly; 0.767 < 0.80, and the
CI straddles 0.80 either way, so VALIDATED could not be claimed). The stated CAUSE is
REVISED: not "entirely adversarial/seductive and scramble" (1 DSCRAMBLE miss; 2 misses
are standard aliens Claude learned exactly in the blind task); the failures are a
map-family / recurrence-contrast effect (map 1/6, non-map 22/24).
Strongest remaining objection: excluding ADV pairs is post hoc; the prereg included them on
purpose, and 19/22 has a Wilson low of 0.67, so standard-only would not robustly pass either.

------------------------------------------------------------------------------------------
## 6. "FAMILIAR is applied at formalism level" and the CORRECT_ANALOGY category

E1 (for): A systems get FAMILIAR=YES via formalism names (semi-Thue, register machine,
graph CA), so FAMILIAR is uninformative about mechanism novelty.
E2 (incompatible): the names are fine-grained enough on K and coarse on A, so FAMILIAR
does discriminate, and CORRECT_ANALOGY measures real recognition.

Decisive evidence:

    (LD) familiar / analogy_class by group (RESULTS rows; fam.jsonl analogy names)
    K    YES 19/20  CORRECT_ANALOGY 19, NO_ANALOGY 1
    A    YES 16/32  NO 17, CORRECT 5, USEFUL_PARTIAL 4, SUPERFICIAL 4, FALSE_COLLAPSE 2
    AADV YES 0/8 ; DESTROY YES 3/10 ; CONJ/SCRAMBLE/SEDUCTIVE YES 0 ; DSCRAMBLE YES 3/11
    A YES by family: rewrite 7/8, vm 4/6, graph 3/8, map 2/5, tab 0/5
    A CORRECT_ANALOGY = 5/5 rewrite ("string rewriting / semi-Thue"), analogy-code exact
    1.0 = blind T5 exact 1.0 in all 5; claimed_equivalence PARTIAL 3, EXACT 2.
    K names are mechanism-level on 17/20 (cat map, LFSR, odometer, odd-even sort, median
    filter, Lotka-Volterra, Bellman-Ford ...); formalism-level on K too for bracket and
    paircancel ("string rewriting system"), mul_acc ("register machine").

So FAMILIAR=YES on A is formalism naming, and the same formalism name appears on 2-3 K
systems: the label does not separate "known mechanism" from "known formalism". On A,
CORRECT_ANALOGY is "implemented its own inferred rule inside a formalism that the
generator itself used" -- it scores the rule, not the analogy.

FALSE_COLLAPSE check (H5 numerator 2/32):

    SYS-60800 rewrite: analogy code = its own two-rule scanner; analogy eval exact 0.81 =
      blind T5 exact 0.81. Classed FALSE_COLLAPSE only because 0.81 < 0.9 and comp 0.93 <
      bar 0.80 + 0.2. No textbook substitution.
    SYS-46959 shear: analogy name "Chirikov standard map", but the analogy code is NOT the
      textbook map -- it is a two-shear step with partial lookup tables (unseen keys
      default 0):  a2=(a+g.get(b,0))%31; b2=(b+h.get(a2,0))%31  -> eval exact 0.085,
      comp 0.1825. Its 'differences' text: "the kick functions ... are not K*sin(...)
      ... look like arbitrary lookup tables".

The report says that for the shear map Claude "wrote the textbook map (18% component
accuracy) while its own inferred rule was right". The rows contradict this: the 18% code
is its own (shear-structured, table-filled) inferred rule from that run, not the textbook
map. Neither FALSE_COLLAPSE case is a collapse to the familiar.

E3 (rejects that analogy_class measures analogy at all): analogy_class is driven by the
predictive accuracy of whatever code the model writes in the fam task; on aliens that code
is the model's own rule, so the class is a second, noisier T5 score with a naming gate.
Prediction: A analogy class tracks blind T5 exactness, not the name. Checked: all 5
CORRECT have blind T5 1.0; the 4 USEFUL_PARTIAL are vm/graph with blind T5 0.35-0.86.

Verdict: HOLDS for "FAMILIAR is applied at formalism level" (and is not A-specific: K
rewrite systems get the formalism name too). REVISED for CORRECT_ANALOGY: on aliens it is
not "partly" but wholly a predictive-code score gated by naming a formalism. H5 count
FALSE_COLLAPSE 2/32 should be 0/32 genuine collapses; the report's shear-map narrative
("wrote the textbook map") is factually wrong and should be corrected.
Strongest remaining objection: the prompt asks the model to implement "that named
mechanism as it would apply to this system", which invites adapting the formalism to the
data; a different instruction (implement the canonical textbook form) might reveal real
collapses this design cannot see.

------------------------------------------------------------------------------------------
## Cross-cutting

- One heuristic explains claims 2 and 5: Claude reads visible determinism (a state
  repeated with the same successor) as evidence of law. It raises RULE-on-noise (repeat
  medians 32 vs 13) and drives pair misses (5/11 vs 2/17).
- Two instrument defects found that the report does not list: (a) sandbox rejects local
  lambda calls (2 correct alien programs scored ERROR; affects T5 means and behav_score of
  SYS-59756, SYS-96628 -- both still learned via T2); (b) the affine baseline is silently
  absent on map systems, so any group mean of affine_* compares unlike sets.
- The 0.80 "code held-out exact" for A is a mean over 30, not 32.
