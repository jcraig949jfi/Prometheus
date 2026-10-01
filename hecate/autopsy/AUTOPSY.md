# Novelty autopsy -- why zero UNFAMILIAR mechanisms (CWO 2026-09-30, Hecate CURRENT)

> CORRECTIONS 2026-10-01 (roles/Hecate/harvest_w2/CORRECTIONS_2026-10-01.md; text below is unchanged):
> K5 the largest loss is at world SPECIFICATION (126/243 mechanisms never in any world; admission 58/117); the by-form
> admission skew does not survive a permutation test (p ~ 0.18). K6 Part B inputs were scrubbed (rewrite rules erased;
> R1 still holds on the other 24); R1 is a property of the definition on fully specified rules -> C6 (not C4), and does
> not transfer to meta v1's prose as argued; meta v1's zero remains uninformative on meta v1's own rows.


PREREG: roles/Hecate/prereg/2026-09-30_novelty_autopsy/PREREG.md (frozen before
Part B ran). Rows: hecate/autopsy/FLOW.json (Part A, no model calls),
hecate/autopsy/reach_rows.jsonl + REACH.json (Part B). Related:
hecate/meta/REPORT_v1.md (the zero), hecate/alien/REPORT_pilot.md (assay).

## Headline

The zero is an INSTRUMENT RESULT, not a finding about generation. Run
unchanged on the exact rule texts of systems whose alienness is established
mechanically, meta v1's detector called 32/32 alien rules FAMILIAR (28) or
COMPOSITE (4), 0 UNFAMILIAR (Wilson 95% upper 0.107): preregistered decision
R1 DETECTOR_CANNOT_REACH_UNFAMILIAR. Separately, the 243 mechanisms of the
triplicate programs were never put through any novelty detector at all.

## Part A -- mechanism flow (triplicate programs, committed records only)

    stage                                   count   share of generated
    generated mechanisms                      243        1.00
    admitted (a probed world built on it)      58        0.24
    read validly (valid reading or SIGNAL)     38        0.16
    behind a SIGNAL                             6        0.02
    survived Pass 4                             0        0.00
    worlds: 80 specified, 37 probed, 12 untestable as specified,
    19 NULL, 1 CONFOUNDED, 5 SIGNAL; programs PARK 15, PROBING 1.

Where attrition happens: (1) admission -- 76% of mechanisms were never
tested (one world per program per round, lowest cost); (2) specification --
12/37 probed worlds could not be read; (3) Pass 4 -- 5/5 signals reduced to
trivial or known explanations. Admission is skewed by mechanism form:
error-correction 9/19 and dynamical law 9/28 admitted, but representation
3/19, memory structure 1/17, world rule 0/10.

There was no novelty stage in this pipeline: the prior-art / gravity pass
(backlog HECATE-14) never ran on the program mechanisms. "Flagged" means
SIGNAL, not "flagged as novel". A per-mechanism familiarity self-assessment
existed only in generator chat replies, never in committed records -- a
provenance gap.

## Part B -- detector reachability (R1)

    group     n   FAMILIAR  COMPOSITE  UNFAMILIAR  median prior_fit
    KNOWN    20      20         0          0            0.93
    ALIEN    32      28         4          0            0.85
    DESTROY  10      10         0          0            0.90

Nearest priors on alien rules are FORMALISMS that fit any computable rule:
"cellular automaton / automata network on a graph", "register machine",
"Feistel network", "semi-Thue string rewriting", "polynomial dynamical
system over a finite field", "random mapping on a finite set". In one case it
named the planted construction itself ("projection onto an invariant
hyperplane"). Under a definition that says FAMILIAR when one known mechanism
"at most renamed or reparameterised" accounts for the rule, a universal
formalism always qualifies.

## The six causes

    C1 search never generated unfamiliar mechanisms ...... NOT DISCRIMINATED
       The only ruler used (meta v1 detector) cannot say UNFAMILIAR even for
       mechanically alien rules, so the zero carries no information about
       generation. Direct evidence is limited to 6 mechanisms: all 5 Pass-4
       signals reduced to known mechanisms (decoding radius, channel reset,
       perturbation response, a trivial listener, an endpoint confound).
    C2 generated but selected out ........................ PARTIAL / NOT DISCRIMINATED
       Heavy attrition at admission (76% never tested) and by form, but
       with no valid per-mechanism novelty ruler it cannot be said that the
       dropped mechanisms were the unfamiliar ones.
    C3 representation collapsed distinct mechanisms ...... WEAKLY SUPPORTED
       Meta v1 judged prose descriptions only; its matcher showed domain
       vocabulary survives scrubbing; in the alien assay prose cut
       prediction of alien structure (0.91 -> 0.78) but not of known
       structure (0.99 -> 0.99).
    C4 rulers mislabelled novelty ......................... SUPPORTED
       R1: 0/32 mechanically alien rules labelled UNFAMILIAR; alien assay:
       FAMILIAR given to 16/32 alien systems at formalism level, COHERENT
       to 24/30 incompressible nulls.
    C5 familiar mechanisms had a fitness advantage ....... WEAKLY SUPPORTED (small n)
       Everything that survived probing was reducible to known machinery;
       Pass 3 v2 requires a positive control "with the effect present by
       construction", which favours mechanisms whose effect the generator
       already knows how to build.
    C6 the UNFAMILIAR definition made the target unreachable ... SUPPORTED
       This is the mechanism of C4: with COMPOSITE and universal
       formalisms available, no finite rule is "unaccounted for".

## What would discriminate the rest (smallest experiments)

- C1: a MECHANICAL novelty ruler. For each implemented world, fit a
  library of known-mechanism templates (linear response, majority/vote,
  diffusion/exchange, minimum-distance decoding, relaxation, reset/forget
  rules, ...) to the treatment rows; call a mechanism "not reducible" only
  if no template reaches 0.9 of its predictive accuracy on held-out states,
  AND it survives Pass 4. Calibrate on the alien assay (known systems must
  be reducible, aliens must not be). This replaces LLM prior recognition.
- C2: once that ruler exists, compare admitted vs never-admitted mechanisms
  (implement a random sample of the 185 never-tested ones cheaply).
- C5: probe a matched set of worlds without the constructed positive
  control requirement (use a planted-effect null instead) and see whether
  the familiar/unfamiliar survival ratio shifts.

## Consequences

- Meta v1's zero-UNFAMILIAR must not be cited as evidence that triplicate
  collision cannot produce new mechanisms. (Its rows are not changed.)
- Hecate stops using LLM prior-recognition labels as a novelty ruler
  (consistent with the alien assay's NOVELTY_DETECTOR_NOT_VALIDATED).
- RESERVE (generator-side interventions) should be built around the
  mechanical ruler above: generate, implement, attack, then test
  reducibility -- not rename.
