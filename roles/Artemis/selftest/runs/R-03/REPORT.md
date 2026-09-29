REPORT -- matched controls that change pressure; identifiability preflight for factor-grammar campaigns

1. WHAT I SET OUT TO TEST
In the 72-hour Z80 x Atlas campaign (Archaeon's grammar), every treatment carried a
"reproduction" matched control that flips EXTERNAL <-> endogenous copying. For EXTERNAL
treatments the constructor also silently drops the pressures explicit_fitness and
recombination, because the grammar forbids them outside EXTERNAL. The concern was that
"reproduction advantage" readings (the moat_advantage and persistence_over_control flags,
which feed family scoring) are partly just pressure removal. I set out to (a) check the
already-published confound figure, (b) measure how much of the campaign's actual flag mass
comes from confounded treatment/control pairs, using only committed data, (c) check whether
the scorer really compares each treatment with its own control, and (d) see whether the same
defect class exists in another factor grammar in the repo, as a first step toward a
cross-engine preflight.

2. WHAT I DID
Repository: read-only clone, origin/main @ 6ff2b2f8a. archaeon/z80atlas/{grammar,preflight,
scheduler}.py are unchanged since a6b66ea96; campaign sampler taken from grammar.py @ c7610ea19.
Exported with git archive into src/ and ran there only. Scripts and outputs are in this directory:
- full_preflight.py -> full_preflight.json/.log: the committed preflight run end to end
  (preflight.run(grammar), 20k draws).
- control_audit.py -> control_audit.json: the matched-control audit for the fixed sampler and
  for the sampler the campaign actually used (c7610ea19), split by which pressure was dropped.
- campaign_marginals.py -> campaign_marginals.json: EXTERNAL runs in the real campaign, split
  into those with explicit_fitness/recombination (the confounded ones) and clean ones. Input is
  archaeon/z80atlas/campaign/PACKET.json (axis_map; per-pressure-combination flag counts).
- Read postcampaign/Z80ATLAS_POSTCAMPAIGN_ADJUDICATION_2026-09-23.json, section E (exact
  pairing for the recombination rows, computed off-repo from the 14 GB bundle), and
  postcampaign/replays/REPLAY_seeded_moat_advantage.json (932 seeded moat_advantage runs,
  including their scheduler_reason).
- pairing_audit.py -> pairing_audit_p0.json, pairing_audit_p4.json: builds families the way
  scheduler.py does, using the real grammar functions: exploration draw plus controls, then per
  promotion a fresh seed, a one-factor mutant plus its controls, and a crossover plus its
  controls. It then applies family_table's pairing rule verbatim ("any DONE run in the family
  whose reason startswith matched_control:reproduction, other spec, same task; last one wins")
  and classifies each pairing. 2000 families, with 0 or 4 promotions (931 of the 1037 promoted
  campaign families were promoted 4 times). "Best run" is chosen uniformly because flags are
  not simulated.
- second_grammar_audit.py -> second_grammar_audit.json: the same control audit on the
  independent Atlas grammar prometheus/z80atlas/grammar.py @ 6ff2b2f8a (Bellerophon's line):
  2000 sparse-sampler picks plus about 20k valid random vectors.

3. RESULT
(a) The published figure does not reproduce. The committed preflight at unchanged code gives,
for the fixed sampler, 969 of 3,351 simulated EXTERNAL treatments with a pressure-changing
control (28.9%), not 1,331 (40%). All the other published preflight numbers do reproduce
exactly: 139/209, 463/679, 505/412, 3,351 treatments, verdict PASS_WITH_RESTRICTIONS. With the
sampler the campaign actually ran, the rate is 2,186 of 3,731 (58.6%), because that sampler
over-drew recombination and explicit_fitness within EXTERNAL. In 668 of those 3,731 treatments
the control fell back to implicit_survival, so all of the treatment's pressures were replaced.

(b) Real campaign, from PACKET axis_map (all run kinds):
  EXTERNAL runs 43,131, of which 4,831 (11.2%) carry explicit_fitness or recombination.
                               n      moat_crossed  moat_advantage  persistence_over_control
  EXT with EF/recomb        4,831       0.917          0.229            0.499
  EXT clean                38,300       0.856          0.037            0.085
  The confounded 11% of EXTERNAL runs carry 1,107 of 2,531 EXTERNAL moat_advantage flags
  (43.7%) and 2,411 of 5,659 EXTERNAL persistence flags (42.6%). Campaign-wide, that is 35.6%
  of all 3,110 moat_advantage flags and 39.1% of all 6,162 persistence_over_control flags.
  Every one of these compares EXTERNAL plus selection/recombination against endogenous copying
  without it. None of them can be read as a reproduction-physics effect. (moat_advantage has
  weight 6, the largest promotion weight.) A caveat on the denominator: adjudication section E
  shows that, conditional on a run having a reproduction control, the flag rate is 35% for
  recombination rows vs 32% for other EXTERNAL rows. The raw 6x gap is therefore largely about
  which runs had a control. The attribution problem is unchanged either way.

(c) There is a larger scorer defect: the pairing is not treatment-specific.
  - scheduler.family_table pairs a run with whichever reproduction control spec in the family
    was recorded last with the same task, not with that run's own control. Control specs
    already store their treatment in parents[0], but the scorer never uses it.
  - Control runs are scored as treatments against other controls. In the committed replay of
    the 932 seeded moat_advantage runs, 407 (43.7%) are themselves matched_control:reproduction
    runs and another 50 are accessibility controls.
  - In the pairing model, unpromoted families are fine (1,915 of 2,000 treatments are paired
    with their own clean control; the other 85 are the pressure-drop cases). After 4
    promotions, only 6,637 of 17,499 treatment scorings (38%) use the run's own clean control.
    8,022 are compared with a control that differs in other factors too, and 2,553 with a
    control of the same reproduction mode (no reproduction contrast at all). 13,547 control
    specs get scored, and 8,216 of those comparisons have the same reproduction mode.
  - Verification controls are labelled "verify:<fam>:matched_control:reproduction", which
    fails the startswith test. So they are never used as controls, and verification treatments
    are scored against exploration-era controls. The PACKET verification table shows these
    controls themselves carrying moat_advantage.
  So the same two flags are confounded by construction on EF/recomb treatments, and are
  mis-paired in promoted families generally, which is where most of the flags live.

(d) The second Atlas grammar (prometheus/z80atlas) has the same defect class in 4 of its 9
named controls:
  exogenous_vs_endogenous  also drops CROSSOVER recombination   2,950 / 6,115  (48%)
  task_pressure_vs_neutral also resets pressure to IMPLICIT     7,993 / 17,322 (46%)
  endogenous_vs_exogenous  also resets MINIMAL_CRITERION        1,996 / 15,885 (13%)
  local_vs_wellmixed       control silently not constructed     1,387 / 2,746  (50%; GRAPH worlds)
  The other five controls are clean. The rates depend on the sampler (these are mostly uniform
  valid draws). I did not audit that grammar's scorer or its runs.

Plain conclusion: yes, the "reproduction advantage" readings are substantially pressure
removal. About 36-39% of all moat_advantage and persistence flags come from treatment/control
pairs that differ in pressure as well as reproduction. Independently, the scorer does not pair
treatments with their own controls once families are promoted. The published 40% is really
29% for the fixed sampler and 59% for the sampler that actually ran. How matched controls should
be built: when a flip is illegal together with a pressure, there is no single clean control.
Emit a bridge pair instead. C_p keeps the treatment's reproduction and removes the offending
pressure; C_r flips reproduction on top of C_p. Read the reproduction effect as C_p vs C_r and
the pressure effect as T vs C_p. Otherwise mark the treatment NO_CLEAN_CONTROL and do not
compute reproduction flags for it. The scorer must pair by control.parents[0] == treatment
spec_id (and seed), must never score a control as a treatment, and must match the verify-stage
labels.

4. DID IT RESOLVE THE QUESTION
Partly.
- Resolved: which contrasts are confounded and by how much, at campaign scale, from committed
  data. What the constructor fix should look like. That the published 40% is a misstatement.
- Resolved as a new defect: the scorer mis-pairs controls.
- Not resolved: an exact per-run count of confounded plus mis-paired flags. That needs
  RUNS.jsonl and the SPECs, which are in the 14 GB off-repo bundle and not committed; my
  campaign figures are marginals, and the pairing figures come from a model of family growth.
- Not resolved: the generic cross-engine preflight. The existing preflight only works through
  the Archaeon grammar's interface (spec_from_factors, CONTEXT, explore_step, spec-dict
  controls). I showed that a ~30-line grammar-agnostic control audit ports to a second grammar
  and finds the same defect there, but I did not locate or audit the other engines' sampled
  designs within budget.

5. CONSEQUENCES
- Instrument/harness defects:
  (1) The matched-control constructor changes pressure. This is already known, but it now has
      campaign-scale numbers: 36-39% of the key flags.
  (2) New: family_table pairs a run with an arbitrary family control and scores controls as
      treatments. The verify-stage label mismatch means verification controls are never used.
      The existing preflight cannot see this, because its check 4 audits the constructor on
      simulated draws, never the scorer's pairing.
  (3) The review's "1,331 of 3,351 (40%)" does not reproduce; it should read 969 (29%), or 59%
      for the sampler that actually ran.
- A false premise worth retiring: any ranking of Z80 x Atlas families, or claimed reproduction
  advantage, that used moat_advantage or persistence_over_control. It is not interpretable
  without re-pairing. The adjudication already voided the recombination reading; this extends
  the problem to explicit_fitness and to the pairing itself.
- The same defect class is present in a second engine line (prometheus/z80atlas; Bellerophon's
  seat). Its controls should be audited before its readings are used.
- Who should know:
  - Archaeon: scorer pairing fix, and the preflight should add a scorer-pairing audit.
  - Bellerophon: second grammar controls.
  - Whoever owns the cross-engine preflight recommendation: the generic check needs to audit
    constructors and scorer pairing, not only sampler support.
- No new positive result.

6. COST
About 1.3 hours of my time. About 10 CPU-minutes in total (the largest job was the preflight at
4.7 min wall-clock), with at most 1 process. No GPU, no database, no holdout.
Not done:
- Exact per-run re-pairing (the data is not committed).
- Auditing the second grammar's scorer and runs.
- Surveying the other engines' sampled designs for a generic preflight.
