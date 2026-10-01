# ATTACK D -- adversarial review of the novelty autopsy, decision R1

Target: hecate/autopsy/AUTOPSY.md, specifically the inference
  "meta v1's zero-UNFAMILIAR is uninformative about generation"
drawn from preregistered decision R1 (meta v1 detector labelled 0/32
operationally-alien rule texts UNFAMILIAR).
Reviewer: adversarial analyst, 2026-09-30 (read-only; local Python; no model calls).
Inputs: the files named in the brief, plus hecate/alien/REPORT_pilot.md and
hecate/programs/HT-*/program.json.

## 0. Verdict in one paragraph

R1 is correctly computed and the decision rule fired as frozen. But the
inference built on it is over-stated in three ways. (a) The detector did NOT
see "exact rule texts": the meta v1 scrubber altered 17/32 ALIEN inputs and
erased the entire rule list of all 8 rewrite aliens. (b) The mechanism the
autopsy offers for R1 -- universal formalisms ("automaton", "register
machine", "Feistel") always qualify as FAMILIAR -- does not operate on meta
v1's input distribution: formalism-level top priors occur on 29/32 alien rule
texts but on 15/400 meta v1 prose items (1/80 in arm T). (c) On the alien
rules, FAMILIAR is literally correct under the detector's own definition
("at most renamed or reparameterised"): the aliens are random parameter
tables inside named construction classes, as the generator's own
analogue_note records. So R1 shows the detector's construct differs from the
assay's construct (C6), not that the detector mislabels (C4). The conclusion
"meta v1's zero should not be cited as evidence about generation" survives,
but on different and partly stronger grounds found in meta v1's OWN rows:
items with prior_fit as low as 0.40, and items whose residual says "no known
derivation" / "not covered by any single prior", were all classified
COMPOSITE. The FLOW claim "admission skewed by form" does not survive a
permutation test (p ~ 0.18).

## 1. Fact check: what the detector actually saw in Part B

reach.py passes describe(params) to hecate.gravity.run.detect, which applies
hecate.meta.scrub.scrub before the call. The scrubber was built for prose:
its ACRONYM regex masks any 2+ capital-letter token, and NOVEL deletes
"new" and "unique". On formal rule text this does real damage.

    group    n   text altered   rule content fully masked
    KNOWN   20        7               4  (sort, paircancel, bracket, ... "[X] -> [X]")
    ALIEN   32       17               8  (all rewrite: "Rules: [X] -> [X]; [X] -> [X]; ...")
    DESTROY 10        8               2

Concrete damage on ALIEN items:
- 8 rewrite aliens: "Rules: YZ -> XW; WY -> ZX; WX -> ZY." became
  "Rules: [X] -> [X]; [X] -> [X]; [X] -> [X]." The detector judged only the
  scan-leftmost frame, which is identical to the KNOWN sorting rule
  (SYS-86243) frame. A FAMILIAR ("semi-Thue system") verdict on a frame with
  no rules is correct and says nothing about the alien rules.
- 3 tab_local planted aliens: "Then REPLACE d_3 by the unique value..."
  became "Then [X] d_3 by the value..." -- the planted-invariant step lost
  its verb and its uniqueness clause.
- 2 shear aliens: "using the new p0" became "using the p0", which deletes
  the cue that the update is sequential (the property that makes it a
  bijective shear). Several items lost "New state:" -> " state:".

The PREREG did say "same scrubber", so this is prereg-compliant; but the
AUTOPSY headline "run unchanged on the exact rule texts" is inaccurate and
should say "on scrubbed rule texts; 8/32 alien rules were masked out".
Effect on the decision: on the 24 non-rewrite aliens UNFAMILIAR is still
0/24, so the point rate is 0 and R1 still fires by rule; Wilson 95% upper
bound rises from 0.107 to 0.138 (0/21 if the 3 REPLACE-masked items are also
dropped: upper 0.155). The R1 sign survives; its precision and the "exact
text" description do not.

## 2. Attack 1 -- does R1 transfer to meta v1's input distribution?

Competing explanation (E1): R1 tested FORMAL RULE TEXT (tables, explicit
polynomials, instruction lists). A fully specified table invites a
formalism-level prior ("lookup-table automaton network", "register machine")
that fits by definition. Meta v1 judged PROSE MECHANISM DESCRIPTIONS
(~2100 chars, statement / what_exists / what_changes / ... / minimal_world).
If prose does not invite formalism priors, R1's mechanism does not apply to
meta v1 and R1 does not by itself make meta v1's zero uninformative.

Distinguishing predictions and checks (detector output fields, same
detector sha 91fbe8f2...):

P1.1 If R1 transfers via formalisms, meta v1 nearest_priors should also be
formalism-level. Regex for formalism names (automaton, register/counter
machine, Feistel, rewriting/semi-Thue, Markov algorithm, dynamical system,
random mapping, iterated map, finite-state, lookup, S-box, functional graph,
Boolean/Kauffman network, polynomial map, population protocol, coupled map,
tag system, program counter, straight-line program):

    set               top-1 prior is a formalism   any of 3 priors
    reach ALIEN 32          29 (0.91)                 31
    reach DESTROY 10        10                        10
    reach KNOWN 20           6 (0.30)                 12
    meta v1 all 400         15 (0.04)                 40
      arm T 80               1                         7
      arm P 80               3                         8

  RESULT: refuted. Meta v1 prose drew mechanism-level priors (Population
  Based Training, Kalman filter, Hebbian rules, sandpiles, ...), not
  formalisms. The specific R1 mechanism the AUTOPSY names does not operate
  on meta v1 inputs.

P1.2 If formal text is "easier to call familiar", meta v1 prose should sit
FURTHER from priors on the detector's own graded score:

    set            prior_fit  min   q25   median  max
    reach KNOWN              0.85  0.90   0.93   0.98
    reach ALIEN              0.60  0.82   0.85   0.95
    reach DESTROY            0.80  0.88   0.90   0.93
    meta T                   0.40  0.55   0.60   0.90
    meta P                   0.45  0.60   0.70   0.85
    meta S / O / G           0.35-0.65  0.82-0.85  0.90  0.97-0.98

  RESULT: confirmed. By the detector's own continuous measure, the T and P
  arm descriptions were much further from known priors than the
  mechanically alien rules were (median 0.60/0.70 vs 0.85). The alien rule
  texts were therefore an EASIER-to-familiarise input than meta v1's
  multi-concept prose, not a harder test of the same thing.

P1.3 What then blocks UNFAMILIAR on prose? Within meta v1:
- classification is close to a threshold on prior_fit: FAMILIAR has
  min 0.75 (n=215); COMPOSITE has max 0.85, median 0.70, 83 items <= 0.60,
  22 items <= 0.50 (n=182); INCOHERENT 0.35/0.55. No region of the score is
  ever mapped to UNFAMILIAR.
- 4 items whose unexplained_residual asserts a gap ("has no known
  derivation" u4-T-m8 pf 0.40; "not covered by any single prior" u2-T-m6 pf
  0.45, u1-G-m5 pf 0.60; "No listed prior explains the specific prediction"
  u0-T-m8 pf 0.50): all 4 COMPOSITE.
  These are the detector itself naming an unaccounted central claim and
  still declining UNFAMILIAR. Under the rule text ("UNFAMILIAR if no
  combination of known mechanisms accounts for a central part"), at least
  some of these are arguable UNFAMILIAR calls that the model routed to
  COMPOSITE. (Caveat: the residuals also say some of these claims are
  "dimensionally suspect" -- i.e. they may be unaccounted because wrong,
  which is not novelty.)

Conclusion: R1 does NOT transfer as a mechanism, and its inputs were closer
to priors than meta v1's. But meta v1's own low-fit tail, where any
UNFAMILIAR call would have to come from, went entirely COMPOSITE -- better
evidence of an instrument property, needing no alien assay. Not decisive:
no coherent-but-unfamiliar PROSE control exists, so this is a sink, not a
demonstrated failure on a positive control.

## 3. Attack 2 -- were the 32 "alien" rules alien in the detector's sense?

The assay's "operationally alien" means: lawful, planted property verified,
and the mechanical analogue check found no known system that reproduces the
behaviour. That is a PREDICTIVE notion (you cannot predict this system from
a known analogue). The detector's FAMILIAR is a DESCRIPTIVE notion (one
known mechanism "at most renamed or reparameterised" accounts for state,
update and behaviour).

Evidence that FAMILIAR is literally correct at the construction level:
- The generator's own answer_key analogue_note names a construction class
  plus random parameters for every alien, e.g. "table-driven local update
  (+ linear compensation term)", "random length-preserving 2-symbol rewrite
  rules", "composed polynomial shears mod 31 (standard-map/Henon-type
  family)", "random instruction table with compensated register updates".
- hecate/alien/REPORT_pilot.md already concedes this: FAMILIAR names are
  formalisms "correct at the construction-class level, which our own
  generator notes record."
- The detector's residuals say exactly this, e.g. SYS-75695 "Nothing
  structural is left over. The specific tables H and coefficients look
  arbitrary"; SYS-44623 "an arbitrary K=2 table network whose node 3 is
  replaced by a check-digit correction". Random table entries are
  parameters; the definition explicitly allows reparameterisation.
- The planted invariants are recipe constructions (linear compensation /
  check digit; Feistel-type shears guarantee bijectivity; swap-symmetric
  polynomials guarantee commutation with swap). Where the recipe is visible
  in the text, the detector named it: the 3 visible-compensation aliens are
  exactly the 3 lowest-fit COMPOSITE calls (0.60: "check-digit / parity
  correction", "projection onto an invariant hyperplane"). The detector
  read the construction correctly.

So the 0/32 is what a CORRECT application of the frozen definition yields.
"C4 rulers mislabelled novelty: SUPPORTED" mis-attributes it; it is C6
(the definition makes the target unreachable for this input class) and a
construct mismatch between "behaviourally unpredictable" and "not
describable in known terms".

Could any finite rule text escape? Every fully specified finite rule is a
map on a finite set; "deterministic finite dynamical system / functional
graph", "lookup-table automaton", "register machine" fit any of them after
reparameterisation. The detector named exactly these as fallbacks (e.g.
SYS-34740 rank 2: "Deterministic finite-state machine / iterated map on a
finite set"). Under a definition that admits universal formalisms as
"known mechanisms", NO finite rule text can be UNFAMILIAR; R1 is then
guaranteed by construction and is not an empirical measurement of the
detector at all -- it is a theorem about the definition. A truly alien
rule, for this detector, would need either (i) a definition that bans
universal formalisms and asks for mechanism-level priors (what known
PROCESS, not what known FORMALISM), or (ii) a description containing
causal/behavioural claims that no known mechanism produces -- which can
only exist in prose-level descriptions, i.e. meta v1's format. Ironically
this makes prose the only input where UNFAMILIAR is reachable at all, which
cuts against using formal-text R1 to dismiss the prose zero.

Graded signal does exist: P(alien prior_fit < known prior_fit) AUC = 0.80
(0.83 excluding masked items); DESTROY < KNOWN 0.69; ALIEN < DESTROY 0.68.
But the lowest alien scores are the items with a visible extra component
(compensation step, flux table), and DESTROY (same frames, no planted
property) scores between them. The score tracks "how many known parts are
visible", consistent with meta REPORT's own observation that M1 partly
measures how many mechanisms a description mentions. It is not an
alienness score.

## 4. Attack 3 -- does FLOW.json support "most attrition at admission,
skewed by form"?

Recomputed from hecate/programs/HT-*/program.json (16 programs; all 243
mechanisms are passId P1):

    mechanisms                                   243
    referenced by ANY specified world            117
    never referenced by any world                126  (68% of the 185 never tested)
    admitted (in a probed world)                  58
    P(admitted | referenced by a world)        58/117 = 0.50

Per program: 14-17 mechanisms, 4-6 worlds, 1-3 probed: admission is a
content-blind budget ratio, similar in every program. The dominant loss happens at WORLD SPECIFICATION (126
mechanisms never got a world), not at the lowest-cost selector (which
removed 59).

Cost: among mechanisms in some world, admitted ones have median min-world
cost 3 vs 6 for unadmitted -- the selector did what it was designed to do.

Form skew: chi-square(form x admitted, 14 forms) = 17.4. Permutation p =
0.17 (global shuffle) and 0.18 (form shuffled within program); restricted
to world-referenced mechanisms, p = 0.19. "world rule 0/10" has binomial
p ~ 0.065 at base rate 0.239, uncorrected for 14 forms. Every form appears
in 10-16 of the 16 programs, so program confounding is not the driver;
chance plus cost is sufficient. The AUTOPSY sentence "Admission is skewed by
mechanism form" is NOT SUPPORTED and should be withdrawn or marked
descriptive/insignificant. "76% never tested" is correct but should be
re-attributed: ~52% of all mechanisms (126/243) were never specified into a
world, ~24% were specified but not selected.

This matters for C2: the attrition is mostly content-blind budget and
world-design attrition, so C2 ("generated but selected out") has no
mechanism by which unfamiliar items would be preferentially dropped, except
through world design (did generators write worlds for the mechanisms they
knew how to build?). That is C5-like and untested.

## 5. Third explanation -- novelty is not a property of a description

Shared assumption of both the AUTOPSY and its opponent (E1): a mechanism
description has a fixed novelty value that a good enough ruler would read
off. Alternative (E3): familiarity is a relation among description GRAIN,
reader prior, and admitted equivalence (renaming, reparameterising,
composing). Every mechanism has a formalism-grain description (always
FAMILIAR), a component-grain description (FAMILIAR or COMPOSITE), and a
parameter/behaviour-grain description (always idiosyncratic). A label
measures the grain the detector chose, not the mechanism.

Predictions of E3 checked in existing rows:
- Same formalism, different "true" status, same label: KNOWN sort/bracket
  rewrite and ALIEN random rewrite get identical priors ("semi-Thue,
  leftmost strategy, Markov algorithm, bubble sort"). Confirmed (though
  trivially, since the rules were masked -- itself an instance: the
  detector judged the grain it was shown).
- Label/score should move with visible component count, not ground truth:
  meta T/P (three/two concepts) vs S/O/G shift from FAMILIAR to COMPOSITE
  (REPORT_v1); in reach, visible add-ons (compensation step) produce the
  only COMPOSITEs. Confirmed. Description length is NOT the driver (Spearman
  length vs prior_fit = 0.02 overall; within arm -0.35 to +0.02), so it is
  component count, not verbosity.
- E3 predicts no description-level classifier can be validated against a
  predictive alienness standard without fixing grain. The alien pilot's
  finding (labels uninformative, confidence/predictions AUC 0.98) fits.

Under E3 the meta v1 zero is uninformative for a reason that also dooms
any "better" LLM label; the remedy is a behavioural, grain-fixed
reducibility test (the AUTOPSY's C1 proposal), not detector repair.

## 6. Scorecard

- R1 as stated (formalism capture): WEAKENED -- sign holds; mechanism does
  not transfer to prose; 8/32 inputs masked.
- E1 formal text invites formalism priors: SUPPORTED (0.91 vs 0.04).
- E1' meta zero informative: WEAKENED (low-fit tail all COMPOSITE).
- E2 FAMILIAR literally correct on aliens: SUPPORTED.
- E3 novelty is grain-relative: CONSISTENT; not yet discriminated.
- FLOW "skewed by form": NOT SUPPORTED (perm p ~0.18).

## 7. Revised claims (proposed replacement text for AUTOPSY)

1. R1 fired (0/32; 0/24 on unmasked aliens). Under the frozen definition
   FAMILIAR is the correct label for random-parameter members of named
   construction classes: the detector's familiarity and the assay's
   operational alienness are different constructs (C6). C4 is NOT
   DISCRIMINATED by R1.
2. R1 does not transfer as a mechanism to meta v1 prose (formalism top-1
   15/400 vs 29/32; T-arm prior_fit median 0.60 vs alien 0.85).
3. Meta v1's zero is still not evidence about generation, because in its
   own rows the low-fit tail (n=22 at <= 0.50) and every gap-asserting
   residual (n=4) went COMPOSITE; UNFAMILIAR was used at no score. Pending a
   positive prose control.
4. Part B inputs were scrubbed, not exact; rewrite rows need a re-run.
5. Flow: attrition is mostly at world specification (126/243 never in a
   world) and content-blind budget; no form skew is demonstrated.

## 8. Smallest decisive follow-up (specified, not run)

Question: does the unchanged detector ever call UNFAMILIAR on meta-v1-format
prose of mechanically alien systems? (Tests transfer directly.)

Design (preregister before any call):
- Items: the 24 non-rewrite standard ALIEN systems + 16 KNOWN systems with
  compact rules (drop the 4 rule-masked KNOWN), all from the frozen alien
  assay. Plus 8 coherent-unfamiliar PROSE controls hand-written by a seat
  that does not see detector output, each describing a runnable mechanism
  with a central behavioural claim that the author certifies has no known
  generating mechanism (positive control; R1 never had one).
- Rendering: for each system, the meta v1 generator (claude-sonnet-5, meta
  v1 template_v1.md field list: statement, what_exists, what_changes,
  what_persists, ..., distinguishing_observable, minimal_world) writes a
  mechanism description from the exact rule PLUS the verified behavioural
  facts (invariant, orbit structure), instructed to describe the mechanism
  without naming formalisms. Class is not revealed to the writer.
- Scrub with meta scrub.scrub (prose is its intended domain); detector
  detector_v1.md unchanged (sha 91fbe8f2...), isolated calls, seed-shuffled.
- Budget: 40 generator calls + 48 detector calls.

Measured: UNFAMILIAR rate on ALIEN-prose (a), on KNOWN-prose (k), on the
positive controls (c); formalism-top1 rate on ALIEN-prose (mediator);
prior_fit distributions.

Decision rule (frozen):
  D0 INSTRUMENT_INVALID   if c <= 2/8: the detector cannot say UNFAMILIAR
     even when a prose positive control says it should -> meta v1's zero is
     uninformative on its own format (strongest version of the AUTOPSY
     claim; C6 confirmed on prose).
  D1 R1_TRANSFERS         if c >= 5/8 AND a <= 0.10: the detector can reach
     UNFAMILIAR on prose, but not for mechanically alien systems -> the
     construct gap (E2/E3) holds across formats; meta v1's zero is
     uninformative ABOUT OPERATIONAL NOVELTY but is informative that arms
     produced nothing description-level unfamiliar.
  D2 R1_FORMAT_ARTIFACT   if c >= 5/8 AND a >= 0.30 AND k <= 0.10: R1 was
     produced by formal-text input; meta v1's zero becomes weakly informative
     about generation and C1/C2/C3 return to play.
  D3 PARTIAL              otherwise; report Wilson intervals; no claim.
  Secondary (descriptive): if ALIEN-prose formalism-top1 < 0.15 and a <=
  0.10 with c >= 5/8, the sink is COMPOSITE/definition, not formalism.

Side-fix: exempt formal rule text from ACRONYM/NOVEL scrubbing in reach.py
and re-run the 8 rewrite aliens + 4 masked KNOWN (12 calls).

## 9. Residual risks in this attack

- Formalism and gap-residual counts come from my regexes (counts are
  floors; the 0.91 vs 0.04 gap tolerates moderate error). prior_fit is a
  model-emitted number, assumed comparable across formats. Permutations:
  5000 shuffles, seed 1; form labels are the generator's own.
