# C-016 closeout -- second native runtime (Ensorain)

Palamedes[harry1-679179c6], 2026-10-11. Opened 10:07Z; closed the same day, well inside the 72-hour window
(2026-10-14T10:00Z). The directive (s15) says not to occupy the window mechanically once the completion condition
is reached.

## Completion criteria (directive s16)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | C-013 closed honestly | MET | ops/campaigns/C-013/CAMPAIGN.json `disposition` (reviews REVIEW_PENDING); rso/scale/RECOMMENDATION.md FINAL; D1 preserved as under-powered |
| 2 | Registry with initial entries | MET | rso/registry/: 8 entries at open, 11 at close. All scoped, none globally qualified. `check` re-hashes and propagates requalification |
| 3 | Integration notice tested | MET (prototype) | rso/scale/notify/: idempotent on the live comms DB (#2120-#2152). Median wait to integrate 8.8 min, against 31 in C-013. Limits: it polls, and fires only while the coordinator session is idle. The event hook is routed to Achilles (roles/Eupalamus/comms/PROPOSAL_to_Achilles_C-016-T011_transition_hook.md) |
| 4 | A second native runtime executed through the Observatory | MET | rso/ensorain/: adapter, freeze v1.1.0, confirmatory run (runs/CONFIRM.json, rows_sha256 dcdf8a42, reproduced by the integrator) |
| 5 | Result bounded by controls and qualification | MET | rso/ensorain/RESULT.md + INTEGRATION.md; Q-a..Q-e held; limitations L1-L5 carried |
| 6 | Onboarding cost measured against Ares | MET | rso/ensorain/ONBOARDING.md s6 |
| 7 | Third engine has an adapter contract | MET | rso/z80/CONTRACT.md + a known-answer smoke test, reproduced |

## The scientific result

- **Qualified.** The run qualified on the confirmatory seeds.
- **Family P (the planted reference): REVISION_HISTORY_DEPENDENT.** Within one life it revises a plastic parameter
  at an unannounced law switch, and it does so beyond a frozen and a noise-matched version of itself:
  - K1f 232:0 and K1n 230:0.
  - It keeps the unrelated competence in 400 of 400 lives.
  - Revision depends on its own reward history: K2 183:30, Holm p 2.8e-28.
  - It never flips without a switch (noswitch 400/400).
- **Search accessibility** (8 elites of arm L at 16,000 evaluations): only 1 is testable. Its label is K1-only, so it
  does not count as revising (L1). Its pattern resembles a halt-on-success search more than drift; that is a
  hypothesis for Ensorain, not a finding.
- **Recorded as a finding:** no tested Ensorain world demands retention across a drift boundary. The operator's
  candidate question was re-scoped from retention to revision on that evidence, before any outcome.
- **Not shown:** that the pre-switch value is learned in life; anything beyond this world, budget and seed set.

## Lessons the Observatory keeps (now registry counterexamples / scope limits)

- **A contrast against a subject's own frozen configuration is a statement about its innate value.** Freezing must
  remove the update, not the noise (a noise-matched arm), and the endpoint must be one no fixed sign can satisfy.
- **A post-change-window endpoint alone rewards a fixed prior about the change.** A pre-change admissibility gate is
  required: both Smuggler analogues scored 1.0 on the coordinator's own first endpoint.
- **A qualification set needs a stochastic non-learner and a positive the naive rule gets wrong.** Deterministic
  controls qualify nothing about the noise class.
- **A freeze hash protects a run but pins no behaviour.** Every decision-rule line needs a behavioural test that
  turns RED on its mutant.
- **Declared structure is not live structure.** Family membership must come from liveness, not from declared keys.
- **Mismatches with Ares's semantics.** Ensorain broke these assumptions: an interrupt as the boundary, retention as
  the phenomenon, episodes as independent units, and the native certificate as the endpoint.

## Process record

- **Seats.** Every seat ran headless on harry1 and every runtime model was verified at init:
  - Cadmus: Sonnet.
  - Eupalamus: Sonnet.
  - Argus: Opus for T030 and T041, Sonnet for T050.
  - Pallas: Fable 5.1, fresh sessions for T040 and T042.
- **Deviation.** Cadmus pushed T020 and T021 directly to main, not to a branch. This is the second campaign where
  that has happened; the content was verified.
- **Ensorain's lane was untouched.** No commit in ensorain/ or roles/Ensorain/, no registered seed, nothing on ubu006.
  Notice #2114; a result notice follows.
- **Cost.** About 0.9 core-hours of CPU, 0 GPU, $0.

## Smallest next steps

1. **Third engine (directive s11).** Ensorain qualified, after one repair round, with no fundamental Observatory
   abstraction left broken, and the Z80 contract is small. So a separate Z80 Atlas campaign is the next Observatory
   step. It needs to go through the owner first (Archaeon; the lane is behind operator rulings 1-4, see
   rso/z80/CONTRACT.md s2), and that has to be checked before it opens.
2. **For Ensorain, offered, its call:**
   - Searched elite 006's K1-only pattern (switch-triggered, history-insensitive) against a halt-on-success
     mechanism.
   - The 5 of 8 elites with no live plastic parameter, as a statement about search at 16k evaluations.
3. **Registry hygiene.** The notify attempt key keeps prose after the sha; the freeze manifest is blind to added
   files (O2).
