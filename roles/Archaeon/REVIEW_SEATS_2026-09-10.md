# Archaeon review of the seats' work, 2026-09-10 (evening pull, main at 55a1b8984)

Reviewed against the three prompt sets of the day (issue-day, delegation,
backlog). Verdicts: DONE = the asked artifact is on main and does what was
asked; PARTIAL = some items; OPEN = not landed. "Asked" refers to the
prompt item numbers.

## Vivarium -- DONE on the day's blockers, three backlog items OPEN
- DONE: phase-2 artifacts published (d34b0c894); the 404 answered with the
  debit receipt on a real pack (a733f0ad5); F-20 flags MEASURED off the
  arrays (30e97ed94); third criterion exposed with campaign-scale numbers;
  eca_rule_eval_v1 registered as an observable, not a score (aa3365df6);
  the old branch merged and deleted with Aporia's 28-file deck rescued;
  consumer stop without stranding a row (57eb8d148); backlog of 24 rows.
- OPEN: nk_landscape_v0 registration (A2 stays blocked); ordering_seed_policy
  on cegis_boolean_v1 (H1 beta needs it, Harmonia 4b); the throughput
  breakdown (Daedalus answered the read-timeout half: client 30 s vs
  engine 33 s -- the consumer-side per-row breakdown is still owed).
- Note: the backlog is prose-structured, not in the schema's one-line
  form, so its XL rows cannot be gathered mechanically.

## Daedalus -- DONE, the strongest day
- DONE: schema 8 deployed with the instance invariant held and the gate
  made stricter before the deploy (d5be5ec4b, 212651aa4); read timeouts
  explained by measurement (e4b05ae62); cost reconciliation by digest
  (COST_RECONCILIATION_2026-09-10.json); the read-scope proposal for B1
  (roles/Daedalus/PROPOSAL_ARCHAEON_READ_SCOPE_2026-09-10.md: an enumerated
  set of worlds, never a topology group, so reading never confers import);
  nk_landscape_v0 engine half with nine mutants killed (b91880a2d); the
  conformance contract regenerated at 8 with Harmonia; a self-correction on
  citing paths relative to his own subtree.
- Note: the backlog is prose-structured (not the schema), XL rows not
  derivable mechanically.

## Techne -- DONE
- DONE: H3 alpha receipt on the real stream, identical retained set in two
  independent archives (7643022c3); rustup contained and the two stitch
  routes agree (9b15633fb); z3 exhaustive over 256 functions with every
  counterexample validated by Proteus's oracle, pending Harmonia; hypothesis
  sound as a minimiser; stitch threshold measured at 3 solutions (phase 1
  meets it); DreamCoder down to an XL decision; merged branch deleted;
  backlog of 36 rows in the schema with an errata commit.

## Harmonia -- DONE on everything asked, and one near-miss caught
- DONE: fairness ruling (inert at this scope); C3-2 final ruling; the
  replicate / dedup / C3-3 instrument / H1-beta scope / d3 band rulings
  (57c259656); D3 upper fires adjudicated as trend artifacts (a1d0ed9c8);
  conformance gate wired and verified at schema 8 with a self-contained
  scratch engine; backlog of 34 rows in the schema.
- NEAR-MISS, self-reported (f44ffcbe0): her contract generator gated its
  DESTRUCTIVE probe on the build hash alone, so a scratch engine and another
  seat's production engine on the same build were indistinguishable; had
  Daedalus's port-collision address reached her, the probe would have fired
  malformed keys at 67 routes of somebody's ledger. Fixed to require a
  ledger that differs. Worth a program rule: destructive probes gate on the
  LEDGER identity, never on the build.
- OPEN: the phase-2 contrasts (roles/Harmonia/INBOX_ARCHAEON_PHASE2_COMPLETE_2026-09-10.md
  landed ~19:20; not yet answered).

## Herakles -- DONE on the science, backlog not in the schema
- DONE: c3_null_check.py; maj structural-zero fixture with the C1-e number
  beside it; cellwise_majority_match with analytic expectations stated
  first; symmetry inputs note; C1-e vs C3-2 24/24 agree by the pre-declared
  rule (065c70d7f), the horizon flag dissolved by a measurement; T=9 fixture
  (236 classes, the ring's ceiling); synchronisation task, every held
  organism at 0.0; merged branch deleted.
- PARTIAL: the widened collider catalogue exists as backlog rows (L-1..L-4,
  X-4) and the specimen registry from 09-03, not yet as the per-organism
  RECOVERED/HELD/NOT_FOUND table the prompt asked for.
- Note: backlog is prose with L-/X- ids, not the schema's one-line form.

## Proteus -- PARTIAL
- DONE: the witness-collapse explanation with a fixture (the seeded prefix,
  not the enumeration; a fixed ordering relocates the pool, only a per-task
  ordering widens it) and seeded_permutation_v1 with tests (5dc8b3e40).
- OPEN: the 4-input universe table (H1 beta sizing needs it); the temporal
  program interface proposal; the Player Foundry detailed-balance test; the
  backlog file. (The z3 parity fixture was done by Techne against Proteus's
  oracle, so item 3 is covered.)

## Mnemosyne -- PARTIAL
- DONE: typed-ref index receipts for cs-c3-2 and cs-h1h0-1-p1 with a rebuild
  demo and the owed path fix (6bf553f87); migration 012 (corpus ref kinds
  and axes); the merged branch deleted.
- OPEN: indexing the later sets (cs-c3-2-r1, cs-h1h0-1-p2, -r1, -p2b, the 11
  artifacts); the first evidence-graph edges; the publication-outbox demo;
  indexing Aporia's rescued deck; the vacuous-reading register; the backlog.

## Cross-cutting
- Five new branches origin/necropolis/* (foundation, argos, coeus,
  frankenstein, hephaestus) appeared today under engine/necropolis/ -- an
  agent-archaeology lane authored by the operator's session, unmerged, not
  in any seat's prompt. Not mine to merge or delete; noted so nobody
  deletes it as stale.
- origin/lexis/g7-closeout-2026-09-01 and origin/rhea_batch4_followup remain
  (operator's call).
- Three seats' backlogs (Vivarium, Daedalus, Herakles) are not in the
  one-line schema; the operator's decision queue is therefore only partly
  derivable. Ask: one pass each to add the id | ... | line per item, or
  Archaeon transcribes them.

## Operator decisions now outstanding (union of XL rows + the day)
- F-19 issue H5-1; D-18 (Herakles's reset amendment); B1 (Daedalus's grant
  proposal is written); d3.v2 admission; DreamCoder route (TECHNE-15); MOSEK
  purchase (TECHNE-31); D-6 allocation; the two packet JSONs; whether
  synchronisation gets a corpus (ARCH-12).
