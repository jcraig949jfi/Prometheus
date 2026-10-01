# DESIGN K -- can the meta v1 detector say UNFAMILIAR on prose? (PREREG-READY; NOT FROZEN; NOT RUN)

Question: can the meta v1 gravity detector (hecate/gravity/detector_v1.md, unchanged) output
UNFAMILIAR for a COHERENT mechanism whose novelty is established without any LLM, shown in
meta v1's own PROSE format? Hecate harvest_w2, 2026-09-30. Design only; no model was called.
Builds on hecate/autopsy/AUTOPSY.md (R1) and ATTACK_D_autopsy_R1.md section 8 (D0-D3), and fixes
three gaps in that sketch: its positive control was certified by its author (an opinion, not a
certificate); its prose writer saw class-specific inputs; nothing addressed C6 (the definition
can make UNFAMILIAR unreachable).

## 1. Held fixed (the thing under test)

- Detector: detector_v1.md byte-identical (sha at freeze; Attack D quotes 91fbe8f2...),
  claude-opus-5-5 via hecate/llm.py, isolated, one fresh call per item, seed-shuffled order.
- Input view: hecate.meta.scrub.mechanism_text(m): the 10 template_v1 fields (statement ...
  minimal_world) joined in fixed order, then scrub(). Exactly what meta v1 items looked like.
- scrub.py is NOT edited (it is part of meta v1); damage is designed out upstream (section 4).

## 2. Classes; truth fixed WITHOUT an LLM

Every non-NONSENSE item starts as EXECUTABLE CODE on a finite, fully enumerated state space
(<= 4096 states), run by hecate/alien/systems.py or, for CU, a step(state) in
hecate/alien/sandbox.py. Prose is derived from code, never the reverse; no author writes
detector prose.
- KNOWN (disguised), n=10: 2 per family (tab, graph, rewrite, vm, map) from the 20 KNOWN_LAWFUL
  assay systems, seeded pick (seed 20261001). Truth = named mechanism in answer_key.json;
  accept-lists written at freeze in controls_v1.json style.
- ALIEN, n=15: 3 per family from the 32 standard ALIEN_LAWFUL systems (the 8 adversarial are a
  coordinate-change question; excluded). Truth = already-certified operational alienness:
  planted property verified on every state + generate.analogue_ok().
- COHERENT-UNFAMILIAR (CU), n=12 kept from a pool of 20 (section 3).
- NONSENSE, n=6 per renderer: field-shuffle composites, each taking its 10 fields from 10
  DIFFERENT rendered items (classes mixed, seeded): fluent and vocabulary/style-matched, but
  not runnable. Mechanical check: >= 2 symbols in what_changes absent from what_exists.
  (Stronger than C11-C14, which were stylistically odd and so easy to call INCOHERENT.)

## 3. CU controls: coherent, unnamed, certified by code

Authoring: 20 candidates from >= 2 authors, at least one not a Hecate seat (operator
preferred). A submission is CODE ONLY: state-space declaration, step(state), and ONE central
claim as a machine-checkable property from the verify.py vocabulary (conserved_linear,
conserved_weights, bijective, all_orbits_fixed, commutes_with, invariant_set) or a new checker
committed with a test. No prose, names or analogies. Guidance: structure, not parameters
(data-dependent addressing, value-as-pointer, state-dependent rule choice, self-referential
update order); no literal table > 6 entries (random tables are reparameterisation, which the
definition calls FAMILIAR -- Attack D section 3); step() <= 15 logical lines.
Certificates (exhaustive, full state space; keep only if ALL pass; failures listed, not fixed):
 C-RUN   total, deterministic, terminating on every state (sandbox).
 C-CLAIM central property holds on every state.
 C-NT    not near-identity (< 0.9 fixed), not near-constant (image >= 10%), not affine.
 C-L1    agreement < 0.5 with every template in library L, parameters fit by grid search.
 C-L2    agreement < 0.5 with every pairwise composition g(f(s)) and every coordinate-split
         product (f on some coordinates, g on the rest) of L members -- targets COMPOSITE.
 C-PROP  no L/L2 member that holds the central property agrees >= 0.5.
Library L (frozen before authoring; extends generate.known_pool): identity, constant,
coordinate permutation/rotation, affine mod m, counter/odometer, LFSR, compare-exchange sort,
median/majority/plurality, threshold contagion, diffusion/exchange, min-plus relaxation,
rewrite sort/cancel/drift, cat map, rotation, integer predator-prey, phase sync, every
KNOWN_LAWFUL generator. L validation: all 20 KNOWN reproduced by L at >= 0.9; all 32 standard
ALIENs fail C-L1. Eligibility: keep the first 12 passing in seeded order; if < 10 pass,
NOT_ELIGIBLE -- decided before any model call.

## 4. Prose rendering (two renderers, crossed with every class)

Uniform, class-blind input for EVERY item: (a) the rule in neutral notation from
hecate/alien/rules.describe() with scrub-safety edits (rewrite symbols lowercase w x y z -- the
ACRONYM regex masked "YZ -> XW" in R1; "new/newly/unique" -> "next/only"); CU describe()
strings written from the code by the certifier, not the author; (b) a PROPERTY BATTERY computed
by the same code for every item: bijective y/n, fixed-point count, cycle-length summary, max
transient, all conserved linear quantities (exhaustive weight search), swap/rotation
commutation. The planted property is one line among a battery all items get; class, family,
analogue_note, "planted" and author never reach the writer. Empty battery -> one fixed sentence.
R-DET (no LLM): fixed per-field templates from (a)+(b): what_changes = (a) verbatim;
what_persists = battery; selection/reproduction/learning/transfer = one fixed "not a
population" text for all; distinguishing_observable = most item-specific battery property vs a
coordinate-shuffled twin. Templates asserted scrub fixed points (scrub(t) == t).
R-LLM (ecological; the meta v1 writer): claude-sonnet-5, meta v1 SYSTEM prompt; USER = (a)+(b)
+ "write ONE mechanism in the template_v1 JSON schema; copy the rule into what_changes
VERBATIM; do not name known mechanisms, formalisms, fields or people". One isolated call per
item, no content retries. R-LLM is where familiarity vocabulary can enter (measured), while
the pinned what_changes keeps coherence.
Leakage / fidelity checks (frozen; run before any detector call):
 L1 forbidden tokens in detector input: planted, random, arbitrary, alien, known, check digit,
    compensat*, Feistel, shear, table-driven, analogue, control, plus the 20 KNOWN truth names
    and accept-lists. R-DET must have 0; an R-LLM item with a hit is EXCLUDED (counted).
 L2 style-only leakage: leave-one-out logistic regression on non-content features (field
    lengths, sentence counts, function-word profile, punctuation) for CU-vs-rest and
    ALIEN-vs-KNOWN; AUC <= 0.75 per renderer, else that renderer is VOID.
 L3 fidelity: scrub(what_changes) == scrub((a)); failures EXCLUDED.
 L4 scrub damage: tokens removed by scrub per item; R-DET must be 0; R-LLM items losing any
    rule-bearing token EXCLUDED.

## 5. Arms, size, power

Stage 1 (decides): detector D on {10 KNOWN, 15 ALIEN, 12 CU, 6 NONSENSE} x {R-DET, R-LLM} = 86.
Stage 2 (only if Stage 1 is CANNOT or INDETERMINATE): detector D' (section 6) on the same 86.
Claim audit (section 8) on every CU and ALIEN FAMILIAR/COMPOSITE call.
Primary statistic c = UNFAMILIAR count among the 24 CU detections. Binomial, n=24:
  per-call p   P(c<=1) CANNOT   P(c>=6) CAN   P(2..5) INDET
  0.00         1.000            0.000         0.000
  0.05         0.661            0.001         0.338
  0.10         0.292            0.028         0.680
  0.20         0.033            0.344         0.623
  0.30         0.002            0.771         0.227
  0.40         0.000            0.960         0.040
Wilson 95%: 0/24 upper 0.138; 1/24 upper 0.202; 6/24 lower 0.120. CANNOT means "per-call rate
below ~0.2", not zero. Two renderings of one item are correlated, so CAN also needs >= 4
distinct CU items with an UNFAMILIAR call. More n buys little: the question is ~0 vs >= 0.3.
Secondary: a = ALIEN UNFAMILIAR/30, k = KNOWN UNFAMILIAR/20, z = NONSENSE UNFAMILIAR/12, KNOWN
family-hit rate, formalism-top-1 rate (Attack D regex) per class x renderer, prior_fit, flips.

## 6. Decision rules (frozen; evaluated in order)

Validity gates -- any failure gives INDETERMINATE_INVALID naming the gate; no CU verdict:
 V1 >= 10 certified CU, and >= 9 CU per renderer after L1/L3/L4 exclusions.
 V2 KNOWN recognised: FAMILIAR/COMPOSITE with an accept-list name in >= 16/20
    (P(fail | true 0.95) = 0.003).
 V3 L2 AUC <= 0.75 both renderers (one VOID -> single-renderer rules: CAN >= 3/12 from >= 3
    items, CANNOT 0/12).
 V4 z <= 2/12. If z >= 3/12: UNFAMILIAR_NOT_SPECIFIC (label fires on incoherence; no CU rate
    is read as novelty). P(z >= 3 | true 0.05) = 0.02.
Primary (D, renderers pooled):
 K-CAN         c >= 6/24 AND >= 4 distinct CU items AND k <= 1/20.
 K-KNOWN-LEAK  c >= 6/24 AND k >= 2/20 (UNFAMILIAR not discriminating).
 K-RENDER      c >= 6/24 but one renderer 0/12 (direction reported; R-DET > 0 with R-LLM = 0
               means LLM-written prose injects familiarity).
 K-CANNOT      c <= 1/24.
 INDETERMINATE c in 2..5; Wilson intervals; no claim.
Audit qualifier on K-CANNOT / INDETERMINATE: over CU FAMILIAR/COMPOSITE calls, r = share
MECHANICALLY REFUTED, u = share resting only on UNIVERSAL formalisms, v = share NOT_VERIFIED.
 v > 0.4                                  -> audit NOT_VERIFIED (never a pass or a fail).
 a mapped prior reproduces >= 0.9 on >= 3 CU items -> CONTROL_FAILED (extend L, re-certify).
 K-CANNOT and r + u >= 0.5               -> CANNOT_DECISIVE (instrument property).
Stage 2: D' = detector_v1 plus one sentence in the classification rule: "A universal formalism
(automaton, state machine, lookup table, register machine, rewriting system, iterated or finite
map, dynamical system) does not count as a known mechanism." Same rules on c'. K-CANNOT under D
with K-CAN under D' -> C6_ISOLATED; K-CANNOT under both -> SINK_BEYOND_C6.
ALIEN (descriptive): a <= 3/30 alongside K-CAN = the construct gap (operational alienness is not
descriptive unfamiliarity) holds on prose too (Attack D's D1).

## 7. Implications

K-CAN: the detector can say UNFAMILIAR on meta v1 prose for a certified, coherent,
  non-reducible mechanism. Meta v1's zero becomes weakly informative (no arm output was as far
  from known machinery as CU, at description level; not operational novelty); C1/C2 back in
  play. detector_v1 usable only as a coarse screen, with CU controls in every calibration.
CANNOT_DECISIVE: meta v1's zero is uninformative on its own format -- closes what R1 left open.
  detector_v1 retired as a novelty ruler. Future novelty = mechanical reducibility against L+L2
  (AUTOPSY C1 ruler) plus claim audit; LLMs may PROPOSE priors, which are then executed.
C6_ISOLATED: the sink is the frozen definition. A D' rerun of the 400 meta v1 rows (400 calls,
  separate prereg, this study as D' calibration) becomes meaningful.
SINK_BEYOND_C6: the model routes non-reducible coherent mechanisms to COMPOSITE whatever the
  definition says (cf. Attack D: 4 gap-asserting residuals, all COMPOSITE). Stop repairing
  prompts; mechanical ruler only.
K-RENDER (R-LLM zero): LLM-written prose manufactures familiarity; meta v1's zero is partly a
  writer artefact. Future: render mechanisms from code deterministically before judging.
UNFAMILIAR_NOT_SPECIFIC / K-KNOWN-LEAK: the label is not a novelty signal even when it fires;
  same consequence as CANNOT for meta v1.
CONTROL_FAILED: L was incomplete; no detector verdict; the library improves.
INDETERMINATE / INVALID: no existing claim changes; meta v1 zero stays "uninformative, pending".

## 8. Strongest argument that the test cannot be decisive -- and the answer

Argument (C6 + open world + grain). UNFAMILIAR means "no combination of known mechanisms
accounts for a central part". The only LLM-free certificate we can build is relative to a
FINITE library L, while "known mechanisms" is the open literature, and every runnable finite
rule is trivially "accounted for" by a universal formalism. So (i) a zero is what a CORRECT
application of the definition predicts for any CU item and shows nothing about the detector;
(ii) a positive could be the detector reacting to unusual wording. Novelty in the detector's
sense has no ground truth outside an LLM, so no outcome tests the instrument (Attack D section
3 already called R1 "a theorem about the definition").
Answer (design change, built in): stop certifying NOVELTY; certify the detector's own CLAIMS.
 1. Claim audit. Each FAMILIAR/COMPOSITE call names 3 priors. A frozen alias table maps each
    name to an L template, to UNIVERSAL (Attack D formalism regex), or to UNMAPPED. UNMAPPED
    non-universal priors are implemented by a seat blind to class and verdict, from the name and
    state space only, parameters fit by search (cap 40; beyond -> NOT_VERIFIED). A verdict is
    MECHANICALLY REFUTED if every non-universal named prior, and every pairwise composition of
    them, agrees < 0.5 with the item AND fails its certified central property. A FAMILIAR call
    justified by priors that demonstrably do not produce the behaviour is wrong by the
    detector's own rule, whatever the literature holds: the open-world escape in (i) is closed.
 2. D' arm. One sentence banning universal formalisms turns the "theorem" into a measured
    contrast (C6_ISOLATED vs SINK_BEYOND_C6).
 3. V2, V4 and L2 answer (ii): an UNFAMILIAR that also fires on fluent nonsense or disguised
    knowns, or that tracks style, is not counted as reaching novelty.
Residual: if CU calls rest only on UNIVERSAL priors (u high) the audit cannot refute; only D'
speaks, and the verdict is reported as one about the definition.

## 9. Other threats

- LLM writer vocabulary injects familiarity -> R-DET twin of every item; token rates; K-RENDER.
- Writer infers class -> uniform battery, no class-bearing input, L1/L2. Residual: alien tables
  "look arbitrary" -- that is content the detector also saw in R1.
- Scrubber damage (R1 masked 8/32 rules) -> lowercase symbols, scrub-safe templates,
  fixed-point assert, L3/L4.
- Format drift: meta prose was looser (T-arm prior_fit median 0.60 vs alien rule text 0.85) and
  exact rules invite formalism priors -> R-LLM frees 9 of 10 fields; formalism-top-1 per class
  compared with meta v1's 15/400; CU R-LLM formalism-top-1 > 0.5 flags "exact-rule regime",
  limiting transfer to meta v1.
- CU authors rebuild a known mechanism unknowingly -> L/L2 certificates + CONTROL_FAILED.
- "Central part" ambiguity -> the certified property is stated in what_persists and
  distinguishing_observable by both renderers.
- Detector nondeterminism (no temperature control) -> renderings as quasi-replicates; flips
  reported; cluster guard. Grain (Attack D E3) -> R-DET fixes grain identically for all classes.
- Pre-freeze looking -> only 2 declared R-LLM smoke renders on 2 non-selected KNOWN systems;
  no detector call before freeze.

## 10. Cost (model calls)

  R-LLM renders (10 + 15 + 12)          37   claude-sonnet-5
  smoke renders (pre-freeze, declared)   2   claude-sonnet-5
  Stage 1 detector D                    86   claude-opus-5-5
  Stage 2 detector D' (conditional)     86   claude-opus-5-5
  audit prior implementations        <= 40   (0 if done by hand)
Stage 1 total 125; worst case 251. Certificates, R-DET, battery, leakage, scrub and audit
execution are local code (0 calls), all frozen with the prereg commit.

## Summary

Items start as code; authors never write prose. Classes: 10 disguised KNOWN, 15 assay
ALIENs, 12 hand-coded CU controls certified mechanically (exhaustive property check, < 0.5
agreement with a frozen library and its pairwise compositions), 6 field-shuffled NONSENSE. A
deterministic renderer and the meta v1 LLM writer both get class-blind input and pass leakage,
fidelity and scrub checks. Stage 1 costs 125 calls: >= 6/24 CU UNFAMILIAR = CAN; <= 1/24 =
CANNOT. Novelty lacks LLM-free ground truth, so the design executes the detector's named priors
to audit its own claims, and adds a D' arm that bans universal formalisms.
