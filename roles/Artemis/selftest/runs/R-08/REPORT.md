# REPORT -- Is the engine ecology still a selection monoculture?

## 1. WHAT I SET OUT TO TEST

A June 2026 audit of the program found two problems with one shared root. Its
mechanisms looked diverse (NSGA-III, binary gates, tier ladders, bandits,
kernel claims), but all of them served one principle: "promote what passes the
gate". The gate at the center also trusted callers. The kernel's PROMOTE step
checked only that a non-BLOCK verdict object existed. An adapter built a CLEAR
verdict from a caller-supplied survival_evidence dict and never re-ran the
tests. Since the September reset, the program has about ten engines and
engine-like seats. A later landscape survey called their shared discipline
(preregistration, freeze, gate, cheat control) "healthy convergence", but
nobody re-audited their selection principles.

I asked three things of the current engines:
- (a) Does the trust-boundary defect recur? That is, does any gate turn a
  caller-asserted outcome into a verdict without recomputing it?
- (b) Is the inner selection rule the same everywhere (an exogenous "pass a
  test to reproduce")?
- (c) Is the program-level objective still "promote what passes the gate", or
  are the shared prereg/gate/control steps now a verification layer that sits
  under different objectives?

## 2. WHAT I DID

This was a read-only code and document audit. I ran no experiments and wrote
no code beyond git/grep one-liners.

Sources:
- Repository: /home/jcraig/artemis-selftest/repo at origin/main 6ff2b2f8a, plus
  these branches:
  - origin/bellerophon/multiday-campaign-2026-09-26 @ ee7a7d954
  - origin/aphrodite/arc3-2026-09-28 @ 7587a93e1
  - origin/archaeon/attribution-arc-2026-09-28 @ 05ab73917
  - the Aether branches, which are ancestors of main
- Baselines:
  - roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md @ 3e13f736c
  - roles/Archaeon/ENGINE_LANDSCAPE_2026-09-25.md @ 95fff9111

Engines surveyed (10): SFE, NPE (primordial/ and roles/Nestor/campaigns), BEE
(prometheus/toolbox, prometheus/z80atlas, the multiday campaign), AGE (Aether/),
CWE (prometheus/cosmos), WTP (ensorain/), PTE (prometheus/ananke), Aphrodite
(roles/Aphrodite/engine plus arc3), Archaeon (archaeon/*), and the Odysseus
expedition code (roles/Odysseus). Cyclops has docs only, so I only noted it.

The same four-question rubric was applied to every engine:
1. The inner selection rule.
2. Where verdicts are computed, and whether they are recomputed from rows,
   replayed, or trusted as labels.
3. The form of the outputs.
4. The program-level objective.

Three read-only sub-surveys did the first pass. I re-checked every load-bearing
defect claim myself against source:
- primordial/core/contract.py board_eligible
- primordial/bus/bus.py receipt()
- primordial/score/progress.py
- SerendipityFoundry/SerendipityFoundryEngine/sfe/runtime.py record_observation (~2361-2450)
- the multiday-campaign md_analysis.py "holds" vs "instrument_ok"
- ensorain/wtp/campaign.py replay_ok
- roles/Aphrodite/engine/a16.py:490
- prometheus/ananke/campaign.py:560-572
- atlas/policy.py

Legacy check:
- git log on sigma_kernel/sigma_kernel.py and
  prometheus_math/discovery_promotion.py.
- git grep for importers of either file inside the post-reset engine
  directories.

Vocabulary proxy: I counted commit subjects on all branches, by period, that
contain "promot" or null/kill/falsif/sham/cheat/control.

## 3. RESULT

### (a) Trust boundary

Legacy gate:
- The June defect was never fixed. SigmaKernel.PROMOTE (sigma_kernel.py:822)
  still checks only that a verdict exists and is not BLOCK.
  discovery_promotion.py still turns caller-asserted survival_evidence into a
  CLEAR verdict. Both were last touched 2026-05-08.
- It is dormant. None of the 10 post-reset engines imports either module. The
  only hits in engine directories are two markdown mentions.

Post-reset engines: 8 of 10 compute their scientific verdicts from per-run rows
or re-runs:
- CWE: the broker re-runs sealed holdout worlds in a subprocess before
  scoring.
- Odysseus: an independent worker re-ran the whole battery and matched the
  fixture value by value.
- BEE: a 3% exact-equality replay.
- Archaeon: the forensic replay has to reproduce the recorded run exactly
  before the run is admitted.
- Nestor z80atlas: REPLAY_MATCH is required.
- AGE: digest and spot-check replay tools.
- WTP and PTE: fresh-seed re-runs and held-out re-tests.
- Aphrodite: the tribunal re-scores on fresh tasks.

Two engines keep a caller-trust path:
- SFE record_observation. The caller supplies FALSIFIED/SURVIVED and only the
  spelling is checked. A work_id proves that a completed work item exists, not
  that it supports the outcome. Without a work_id the outcome is stored as
  CLIENT_ASSERTED and still moves the hypothesis state. This is a stated
  design choice ("the engine stores the conclusion the experimenter reached").
  The evidence class is always recorded, and fail-closed enforcement is
  opt-in (require_attestation). So the audit's defect is present by design,
  labelled, and closable with one flag.
- NPE board_eligible (contract.py). It accepts a self-written PASS/KILL
  status, any non-empty controls.cheat string (the string is not checked to
  say the control passed), and any non-empty rows path (the path is not
  checked to exist). Board credit from it has been off since round 2
  (PM_BOARD_SCORING). Refutation credit in score/progress.py still uses it,
  but its instruments axis does read the row files.

Softer stage-to-stage label trust (a later stage trusts an earlier stage's
stored label or boolean; the verdict is never minted from a caller):
- Aphrodite: run_s3s4.py reads stored PASS gate files, and a16.py:490
  hardcodes donor_adjudication_valid = True.
- Archaeon: a PREREG attribution_tests.passed boolean and a preflight
  verdict == "PASS".
- Odysseus: gate_v01.json PASS.
- AGE: GPU parity rests on the pod's self-reported PASS, though independent
  replay tools exist.
- BEE:
  - md_analysis.py sets "holds" without conditioning on instrument_ok; the two
    are printed side by side.
  - The scheduler re-uses a stored score on resume.
- WTP: replay_ok is computed and recorded but never enters the REPLICATED
  state.

### (b) Inner selection rule (10 engines)

Exogenous test-passing ("pass a test to reproduce"):
- PTE: truncation GA.
- Aphrodite: gold-match search and a lower95 > 0 gate.
- Odysseus sandbox: hidden-target reward and colony truncation.

Mixed:
- NPE: QD elites alongside endogenous Z80 ALLOC/BIRTH.
- BEE: endogenous copying, but the copy resource is paid for correct task
  answers in the coupling physics.
- WTP: elite GA with about 20% novelty; WTP-03 parents are the worlds that
  passed admission gates.
- Archaeon: endogenous copying, an optional competence-gated pressure, and an
  outer "world promotion score" in rie.

Endogenous only:
- AGE: no score; a GA loop is explicitly rejected.

No selection:
- SFE: an instrument (its reference driver is a onemax (mu+lambda)).
- CWE: parameter worlds; the selection is over laws, by attack/survive/freeze.

So 3 of 10 are pure exogenous gates, and 7 of 10 contain a
test-passing-selection component. Mechanism diversity is real, but it leans
toward test-passing selection. Only AGE (and Archaeon's census and envgate
lines) keep selection fully endogenous.

### (c) Program-level objective

- The central scorer has changed. atlas/policy.py (policy/2) states: "The
  learning target is NOT 'which experiments succeed'." Its weights have no
  term that rewards success, and it lets a confound-removing clean null
  outrank a novel demo.
- Promotion language has dropped out of commit subjects:
  - Apr-Jun: 133 of 2848 subjects contain "promot" (4.7%).
  - Jul-Aug: 3 of 1175.
  - Sep 10-30: 17 of 4796 (0.35%). Most of these are allocation or schema
    promotions, not claim promotions.
- Null/kill/control language roughly doubled in rate: 9.2% (Apr-Jun) against
  11.0% (Sep).
- Several engines have descriptive first-class products: the AGE observatory
  deliberately applies no labels; there are the Archaeon copier census, the
  Odysseus census and label-vs-capability audit, the WTP phase and niche maps,
  and the BEE "descriptive, not tested" block.
- One structural residue remains, which I call a "gate-then-describe" funnel.
  - PTE maps phase boundaries only around specimens that first pass SIGNAL
    (campaign.py:562-572).
  - CWE's product is a law that survived attack.
  - WTP-03 breeds from worlds that passed admission gates.

  In these engines, description is conditioned on a gate pass, so what gets
  described is still filtered by what passed.

### Plain conclusion

The June monoculture does not recur in its load-bearing form.
- Every post-reset scientific verdict path I checked is either recomputed from
  rows or replayed, or is explicitly labelled as client-asserted (SFE).
- The program-level objective is no longer "promote what passes".

What converged is the verification discipline, not the selection principle.
Treating those two as the same thing is the weak part of the question.

Three genuine residues remain:
1. The legacy gate defect is unfixed, though dormant.
2. There are two caller-trust paths (SFE by design and opt-in; NPE's
   board_eligible) and about six label-trust seams between stages.
3. Inner selection and descriptive scope still lean toward exogenous
   test-passing. Seven of ten engines have such a component, and three engines
   describe only what first passed a gate.

## 4. DID IT RESOLVE THE QUESTION

Partly.
- It resolves the trust-boundary half: the defect is identified per engine
  and verified in source.
- It gives a defensible classification of inner selection and of the
  program-level objective.

It does not resolve whether the shared discipline itself narrows what the
ecology can discover. That is an empirical question and a code read cannot
answer it. It would need, for example, the share of Atlas proposals or results
that exist only because a gate passed, against ungated exploratory output, or
a comparison of discovery yield between the gated and ungated lines. The
engine-level classification also rests on a medium-depth read of about ten
codebases, not a line-by-line audit. Unread parts include the SFE client,
NPE's soup/ worlds, ensorain/lm01/launch_gate.py and
prometheus/ananke/launch.py.

## 5. CONSEQUENCES

Harness and instrument defects (small, concrete):
1. The legacy kernel PROMOTE and the discovery_promotion adapter still trust
   caller-asserted survival. The June recommendation (a re-execute-battery
   gate) was never applied. Either retire them or fix them before anything
   post-reset imports them. Owner: whoever owns sigma_kernel /
   prometheus_math (Harmonia raised it).
2. In NPE board_eligible, the cheat check is "any non-empty string" and the
   rows check is "any non-empty path". It should require that the cheat
   control passed and that the rows file exists and backs the status. It
   still feeds refutation credit. Owner: Nestor.
3. SFE should default to require_attestation=true for science worlds, or
   state in each world's charter why CLIENT_ASSERTED is acceptable. Owner:
   Daedalus.
4. BEE md_analysis should set holds = holds AND instrument_ok. WTP should let
   replay_ok gate REPLICATED. Aphrodite a16.py:490 should compute
   donor_adjudication_valid instead of hardcoding True. All three are
   one-line fixes. Owners: Bellerophon, Ensorain, Aphrodite.

False premise, or at least a conflation: "monoculture at the level of
discipline" mixes epistemic verification (which should be uniform) with
selection principle and objective (where diversity matters). The earlier
landscape verdict of "healthy convergence in discipline" is consistent with
what I found. But no re-audit had been done, and one was warranted: the
residues above are real.

Something seats could change: the remaining monoculture risk is at the
"gate-then-describe" funnel (PTE, CWE, WTP-03) and in the inner selection rules
(7 of 10 engines have a test-passing component). Atlas could track, per engine,
the share of described territory that was reached without passing a gate, which
would make this measurable. The operator (convergence concern of 2026-09-25)
and Atlas should know.

No new positive result and no reproduction of a known number. This is a
re-audit that mostly clears the post-reset ecology of the June finding and
leaves a short list of residues.

## 6. COST

About 1 hour of wall time, including three parallel read-only code surveys
and my own verification of each cited defect line. CPU: negligible (git and
grep only; well under 1 CPU-minute). Nothing was executed from the repository
and no database was queried.

Not done:
- the empirical measurement of gated vs ungated discovery share
- a deep read of the SFE client, NPE soup/ worlds and the launch gates
- Cyclops adjudication, which exists only as prose
