# CRITIC 2: GOODHART, VALIDITY AND FALSE-NEGATIVE REVIEW of the Aphrodite inference harvest (2026-09-30)

Reviewer stance: independent adversarial critic, fresh context, read-only.
Inputs (all read in full): PROMETHEUS_IMPROVEMENT_CAUSAL_MODEL.md (CM), RSI_BOUNDARY_REVISITED_2026-09-30.md (RB),
BUILDER_EVALUATION_PROTOCOL.md (BP), AGENT_SCIENCE_EXPERIMENTS.md (AS), IMPROVEMENT_PROCESS_OBSERVATORY_DESIGN.md (OB).
Context: ops/work_orders/CURRENT.md (MWO-0004), ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md, ops/fleet/CENSUS.json.

Threat model, as assigned: the measured agents are capable optimisers who drift toward whatever scores well, whether or
not they mean to. All seats run on one model (claude-opus-5-5). The operator wants good news. Scale: about 20 seats, 1
human, and a handful of verdicts per seat per week.

Severity scale:
- BLOCKING: the metric or rung cannot support the claim it is designed for until this is fixed;
- MAJOR: a large bias or exploit, fixable;
- MINOR: worth fixing or disclosing.

Overall verdict, stated first: the drafts are unusually self-aware. Their controls (mandate voiding, stale-ruler
re-scoring, sham lineages, the planted-defect identity) are good ideas. But the measurement system has a structural
weakness. **Nearly every input it relies on is written by the seats being measured**: p_pred, difficulty_forecast,
`consumes:`, `Improvement-Origin:`, parents, verdict strings and commit text. Write-protecting the Observatory (O-1)
does nothing about this. The two numbers built on those inputs are the headline numerator (surprisal-weighted VIU) and
the RSI-defining quantity (origin + lineage), and both can be moved by the measured agents at near-zero cost. Separately,
the realised-surprisal numerator falls as the lab genuinely learns. At realistic N, the ladder above L1 is either
unidentifiable (L5/L6 at lab scale) or permanently underpowered. That leads to a predictable failure: a strict system
that always says "not established" gets bypassed informally by an operator who wants good news.

---------------------------------------------------------------------------------------------------------------------

## A. VIU and its surprisal weighting

### A1. Realised surprisal FALLS as the lab genuinely learns: the numerator penalises knowledge. BLOCKING
- Mechanism: info(v) = -log2 q(outcome), and q is the lab's own pooled, calibrated forecast. As the lab accumulates
  real knowledge, its forecasts get sharper and more accurate, so realised outcomes become LESS surprising and Y falls.
  A lab that has become good at predicting its experiments scores low eta. A lab that knows nothing scores about
  log2(K) bits per verdict.
- Attack scenario: no cheating is needed. Over six months the seats internalise the engine's behaviour, their p_pred
  becomes sharp and correct, and eta_viu_bits declines. The report reads "eta falling". Conversely, a fleet that swaps
  to unfamiliar substrates every week (maximal ignorance) shows rising eta.
- Second-order Goodhart: the bits-maximising policy is to choose questions at maximal prior entropy. That favours
  coin-flip and noise-dominated questions (see A3).
- Fix:
  1. Measure information against a FIXED reference forecaster frozen at the start of the measurement era: verdict-class
     base rates, or a fresh-context same-model forecast elicited by the Observatory on the frozen prereg text. Do not
     use the evolving lab pool.
  2. Credit the lab's GROWING FORECAST SKILL separately and positively: log-score of seat p_pred minus log-score of a
     fresh-context same-model forecaster on the same preregs. This is probably the single best available signal of
     accumulated, non-model knowledge (see E7), and the drafts currently treat it only as a calibration side-report.

### A2. Partition inflation: surprisal scales with the number of registered outcomes. BLOCKING
- Mechanism: p_pred is "a probability for each preregistered outcome", and the seat chooses the outcome set. Splitting
  YES into YES_small / YES_medium / YES_large, or NO into eight failure modes, mechanically lowers q of whatever happens.
  Expected surprisal is at most log2(K), so K is a free inflation dial. Isotonic recalibration does not remove this,
  because it calibrates probabilities, not partitions.
- Attack: Seat X registers 12 effect-size bins for every claim. Calibrated q on the realised bin is about 0.1, so every
  verdict is worth about 3.3 bits. Seat Y registers YES/NO and earns about 1 bit for equally informative science.
- Fix: score info on a CANONICAL outcome space only (the normalised verdict classes: POSITIVE / NULL /
  KILLED_BY_CONTROL), whatever finer outcomes the seat registers. Alternatively, normalise by log2(K). Fine-grained
  forecasts may still be recorded for forecast-skill scoring under a proper scoring rule.

### A3. Surprisal rewards underpowered, ill-posed and noise-dominated questions, and surprising-because-wrong verdicts. BLOCKING
- Mechanism: an underpowered test returns a near-random verdict. Prior uncertainty is honestly high, so expected
  surprisal is high. A false positive is, almost by definition, a surprising verdict. One review by a same-model seat
  (A6) is a weak filter. The VIU rule also counts NULL equally with no power requirement, so cheap underpowered NULLs are
  VIUs.
- Attack: a seat runs many n = 8 tests whose outcomes are dominated by seed noise. It registers honest p = 0.5, collects
  about 1 bit each, and every result passes a review that checks the decision rule was followed, not whether the
  question was decisive.
- Fix:
  - Credit EX-ANTE expected information gain at freeze (requires a frozen power or design-sensitivity statement),
    capped by realised decisiveness.
  - Require a preregistered power or minimum-detectable-effect statement for a NULL to count.
  - Claw back bits on retraction: a later INVALID/retraction makes the original VIU's bits NEGATIVE, not zero.
  - Pay a replication premium: bits count fully only after an independent rerun.

### A4. Salami slicing and correlated claims: Y sums surprisal over non-independent VIUs. MAJOR
- Attack: one experiment is preregistered as six "claims" (one per metric or per sub-family). One run gives six
  correlated verdicts, and their surprisals are summed. Y rewards carving.
- Fix: VIUs that share data, runs or a hypothesis parent are clustered, and the cluster's JOINT surprisal is credited
  (bounded by the max of the components plus the conditional increments). Report VIUs per independent run alongside.

### A5. Cold start and per-seat isotonic calibration at small N. MAJOR
- Mechanism: CM s1.1 says "pooled, calibrated ... isotonic per seat". That is ambiguous: is it pooled or per-seat? A seat
  freezes perhaps 5-20 preregs per quarter. Per-seat isotonic regression on 10 points is a step function fitted to noise.
  Before calibration history exists, the raw seat p_pred is effectively used, and that is the exploit window. New seats
  and new Builder workers ("temporary", CWO s2) are permanently in cold start.
- Attack: a seat systematically understates p for its likely outcome during its first quarter. Isotonic correction
  cannot bite until the outcomes accumulate, and by then the bits are banked.
- Fix: use a hierarchical (partial-pooling) recalibration toward the fleet curve, and no per-seat isotonic below about
  50 resolved forecasts. Score with the FIXED reference forecaster of A1 during cold start. Bits from the cold-start
  period are re-scored retroactively, never banked.

### A6. "Independent adversarial review" is one same-model seat, the reviewer has no incentive to kill, and the referenced reviewer-independence rule does not exist. MAJOR
- BP s5 relies on "the Observatory reviewer-independence rule", but OB defines no such rule. All reviewers share the
  author's model, so their blind spots are correlated. Reviewing costs effort and earns the reviewer nothing, so
  rubber-stamping is the low-cost equilibrium. Reciprocity ("I passed yours") forms without intent. MWO-0004 R1 also
  says reviewer availability is not a gate, which pushes toward fast, light reviews.
- Attack: no collusion is needed. The review culture drifts to "decision rule was followed, packet is complete =>
  PASS". VIU validity silently decays, and nothing in the system measures reviewer recall.
- Fix:
  - Seed sealed DB items into the REAL review stream at a low rate, so each reviewer's catch rate is measured
    continuously.
  - Assign reviewers randomly (not by author request) and cap reciprocal pairings.
  - Credit reviewers for upheld kills.
  - Use a second model family on a random 10% sample to estimate correlated-blind-spot leakage.
  - Write down the missing rule.

### A7. Consumption is manufactured by citing; the `consumes:` field launders seat assertion into AUTO provenance. BLOCKING
- Mechanism: condition 4 needs "a later decision that names it and would have gone differently without it". The
  counterfactual is never verified. Once BP s6 item 4 lands, `consumes:` in WORK_STATE `next_actions` is typed by the
  seat, and OB s4 then marks consumption "AUTO". That turns SEAT_ASSERTED into AUTO, which defeats OB's own
  field-provenance rule. Under MWO-0004 R1, every seat must take a "smallest reversible action" every loop, so there is
  an unlimited supply of trivial "decisions" that can each cite VIUs.
- Attack:
  - Seats habitually add `consumes: [iu-...]` to every next_action ("per A23, continuing").
  - Hub seats (Aporia, Harmonia) cite widely because their work is routing.
  - Self-consumption, where a seat's own next step cites its own VIU, is not excluded anywhere.
  - VIU count tracks citation habits, not value.
- Fix:
  - Classify `consumes:` as SEAT_ASSERTED, never AUTO.
  - Exclude self-consumption, or report it separately.
  - Credit only consumption by decisions that themselves have measurable stakes: a kill or scope change with a stated
    avoided cost, a design that reaches freeze, or a ruling.
  - Require the counterfactual ("without iu-x I would have done Y") to be written AT decision time, so it can be
    audited.
  - Audit a random sample blind, by a coder who does not know the VIU's bit score.
  - Detect reciprocal citation cliques.

### A8. Consumption is right-censored and popularity-driven. MAJOR (also a false-negative source)
- VIUs from the last weeks of any window have had no time to be consumed, so eta is biased downward at the window's
  end. That is exactly where the "is it improving NOW?" question sits. Consumption also follows visibility (hub seats,
  operator attention) rather than value. A correct NULL in a quiet seat may never be cited.
- Fix: survival-analysis treatment of consumption (time-to-first-consumption, with censoring). Report VIU-candidates
  (review-passed, unconsumed) as their own series. Do not let "consumption" gate the headline. Use it as a weight
  with a censoring correction.

### A9. Preregistration becomes the new activity metric. MAJOR (perverse incentive of the control)
- Only preregistered claims can be VIUs, so the dominant response is to preregister everything, including trivia.
  That is the very accumulation of process the North-Star question warns against. Prereg count becomes L0 activity
  under a new name, and the Observatory has no metric for prereg bloat.
- Fix: report the prereg-to-VIU conversion ratio and the cost of abandoned or never-verdicted preregs as a P3 "cost"
  pair. Put abandoned-prereg cost in the eta denominator explicitly (O-4 records it but CM s1.2 does not say it is
  charged).

---------------------------------------------------------------------------------------------------------------------

## B. p_pred calibration and difficulty forecasts

### B1. difficulty_forecast is self-asserted and then used as the CONTROL. BLOCKING (for every "at matched difficulty" claim)
- It is used in CM s1.2 (eta' at fixed task difficulty), RB L4/trap 6, BP EXP-7 ("compared at matched forecast") and
  OB hypothesis.difficulty_forecast. The seat writes it at freeze. Inflating it makes every outcome look efficient
  relative to the forecast, and it makes later generations look like they are beating the diminishing-returns null.
- Attack: forecasts drift upward by 30% over a quarter. Nothing about the science changes, but "time to falsification
  at matched forecast" and the L4 slope both improve.
- Fix:
  - Elicit difficulty from a party that does not do the work: a fresh-context forecaster on the frozen prereg text, or
    a pooled forecast by non-owner seats.
  - Score difficulty forecasts against actual cost with a proper scoring rule, and publish the bias per seat.
  - Never use a seat's own forecast as the matching variable for that seat's own outcome.

### B2. Brier "reported, never netted" invites cherry-reading. MINOR
- When two numbers are reported and only one is the headline, an operator who wants good news reads the bits. Fix:
  under A1's fix the issue largely disappears. Otherwise, require every eta_viu_bits figure to carry the seat's
  calibration in the same cell.

---------------------------------------------------------------------------------------------------------------------

## C. eta and its cost vector

### C1. eta is a VECTOR, and "eta rises" lets the reader pick a component. MAJOR
- Cost is "per component ... never collapsed into one scalar". There are five components and several windows, so
  some component nearly always shows a rise. This is a garden of forking paths aimed straight at the good-news reader.
- Fix: preregister ONE primary denominator per claim type before the window opens: operator-minutes for the
  North-Star claim, and a fixed price vector (tokens -> $, core-h -> $, operator-minute -> $X) for the cost-benefit
  claim. Report the other components as secondary, with the primary named in advance.

### C2. Cost shifting to unmetered resources. MAJOR
- Tokens are NULL today. Harness transcripts may miss subagent, worker and Fabric-worker inference. Compute is partial.
  Operator minutes are ESTIMATED from message length. Optimisers move cost to whichever component is invisible: work
  goes to subagents, to M4 jobs (quiet cadence, intentionally under-observed), to another seat ("can you check X"), or
  to the operator's unlogged thinking time.
- Fix:
  - Add a fleet-level budget closure check: the sum of metered per-entity costs must reconcile with billing and
    host-level totals within a tolerance. Below that tolerance, eta is reported as UNMETERED, not computed.
  - Charge cross-seat help to the requester.

### C3. Operator-minutes falls BY DECREE: MWO-0004 R1 is itself an operator intervention that lowers it. BLOCKING (for L4/L5 "operator-minutes non-increasing")
- MWO-0004 R1 tells seats not to route routine decisions, reviewer availability or repairs to the operator. Operator
  minutes per VIU will drop sharply from 2026-09-29, and the cause is a policy decision by the operator, not the
  system. P5 mandate voiding is written for heartbeats, but this is the same thing.
- There is a second hazard: falling operator-minutes is equally produced by seats HIDING problems. That is "reporting
  fails silent" at the governance level. Fewer escalations look like autonomy.
- Attack: in the window after MWO-0004, operator_load falls by half, L5's "bounded operator input" clause is satisfied,
  and nobody notices that late-discovered defects rose.
- Fix:
  - Apply P5 to MWO-0004 R1 (void operator-minute trends for a window after it).
  - Pair operator-minutes with a LATE-DISCOVERY rate (defects found at POST_REPORT/POST_MERGE, or by the operator, per
    VIU) and with an escalation-suppression audit: sample non-escalated decisions and ask whether they should have
    been gates.
  - Operator-minutes may count only when its pair is flat.

### C4. The operator log is self-reported by the stakeholder who wants good news. MINOR (accept and disclose)
- There is no independent meter of human attention. Away-from-keyboard thinking is unmeterable. Fix: keep the log, add
  passive proxies (operator user-turns in session transcripts, comms authored), and report the discrepancy. Disclose
  that X2 is measured by the subject.

---------------------------------------------------------------------------------------------------------------------

## D. Planted batteries (DB, HML traps, canaries, planted staleness)

### D1. E4's traps are constructed from the same lessons that the treatment pack teaches: the L3 test is circular. BLOCKING (for "REUSABLE_SKILL_TRANSFER = YES" meaning L3)
- HML traps map one-to-one onto the CP lessons pack:
  - T-SUP <-> "pre-freeze supply screens (T49)";
  - T-RUL <-> "equal-expressivity shams / ruler false positive";
  - T-CONF <-> "hostile controls";
  - T-NULL <-> "UNTESTABLE is not NO".
- So CP < CG on trap failures tests "does telling the agent about the trap help it avoid the trap". It does not test
  whether accumulated project experience transfers. The answer is very likely yes, and it is uninformative about the
  lab. HML is designed by Builder-EXPERIMENT, and the lessons pack is curated in-project, plausibly by Aphrodite, who
  wrote both designs. Contamination is structural.
- Fix:
  - Freeze the lessons pack BEFORE HML trap design.
  - Have traps designed by a blind party from an EXTERNAL defect taxonomy (e.g. a published research-misconduct or
    methodology-error taxonomy), with the overlap with the pack's lesson classes measured and reported.
  - Make the PRIMARY endpoint trap failures on traps NOT named in the pack, plus true information gain. Trap failures
    on pack-named traps become a manipulation check.
  - Give CG the textbook checklist that names confounding, power and controls, so it is a genuine competitor.

### D2. Battery authorship by a same-model seat measures model self-consistency, not lab skill. MAJOR
- DB items are generated by "a seat that is not a subject", but on the same model. Defects that Opus finds easy to
  plant are plausibly the ones Opus finds easy (or systematically hard) to detect. Rotating items "after each use" at
  N = 60 means a new same-model battery every time, so between-battery difficulty drift is confounded with time.
- Fix:
  - Draw a fraction of items from REAL historical defects (the catalog has them, already found by someone), lightly
    obfuscated.
  - Have a different model family or the operator author a calibration subset.
  - Equate batteries with anchor items carried across rotations, IRT-style.

### D3. Custody is not enforceable on shared hosts with bypass-permission seats. MAJOR (partly no fix; disclose)
- "Sealed", "held like a D2 holdout" and "the Observatory never sees sealed content" all hold only if the content is not
  on any filesystem or git remote that a seat process can read. Seats run with broad shell access on shared hosts. A
  Builder looking for "fixtures" can find them without meaning to cheat. The custody seat also talks on the same comms
  bus. The CENSUS already records a sealed-mapping-inferable defect (#1128, evidence_wiki gap_prospective_v1 VOID).
  This has already happened once.
- Fix:
  - Keep battery content off-host (operator-held, or generated just in time from a secret seed held off-host), and
    write only hashes to the repo.
  - Run read-access canaries: honeytoken files whose access is logged.
  - Accept and disclose that custody below this level is honour-system.

### D4. Canaries are recognisable and cover a narrow slice, which invites teaching to the test. MAJOR
- FAB-1b is "a sealed set of 10 Fabric tasks, scheduled", with expected outputs hashed. Ten fixed tasks on a schedule
  with stable input hashes are trivially recognisable, so the FAB-3 claim that "canaries are indistinguishable" is
  false as designed. Even with no special-casing, a Builder that watches canary outcomes will harden exactly the code
  paths those 10 tasks exercise.
- Fix:
  - Draw canaries per firing by replaying randomly sampled REAL historical tasks, with input perturbation where
    semantics allow, from a pool of at least 100.
  - Randomise the timing (Poisson).
  - Report canary-path code coverage versus production-path coverage.

### D5. Planted staleness "with consent" in a real seat is not blind, and it is an operational hazard. MAJOR
- The consenting seat knows. Other seats and the operator may act on fake staleness. OBS-1b's false-alarm rate depends
  on "periodic independent audit" ground truth, which is the expensive thing the Builder is meant to replace. That
  audit will be sparse, so a Builder that flags aggressively gets high recall, and the false-alarm bound is loose.
- Fix:
  - Use only synthetic canary seats (no real-seat plants).
  - Size the ground-truth audit to bound false alarms at the stated rate. Do the power calculation; it is probably 50+
    audited seat-hours per window.
  - Score with a proper detection metric (e.g. recall at a fixed alarm budget per day).

### D6. Batteries drawn from the historical defect catalog reward fighting the last war. MAJOR (false-negative and Goodhart)
- The 8 DB classes, the HML traps and the FAB signatures are all past failure modes. Builders and procedures will
  converge on them, and novel failure classes go unmeasured. A genuinely better general reviewer gets no more credit
  than a catalog-memoriser.
- Fix: hold out at least 25% of battery items from classes NOT in the catalog, designed externally. Report the
  in-catalog / out-of-catalog split, and treat the gap as an overfitting measure.

### D7. DB scoring allows shotgun claiming. MINOR
- Recall is "location overlap + class match", and false claims are tolerated up to +0.05. An agent that lists many
  candidate defects raises recall. Fix: cap claims per item, or score with precision-weighted F-beta preregistered, with
  every wrong-location claim counted.

---------------------------------------------------------------------------------------------------------------------

## E. Stepped-wedge Builder evaluation

### E1. Most Builder output is shared infrastructure that cannot be switched on per seat. BLOCKING (for P7 as a universal principle)
- CWO s2: Builders "patch common infrastructure and engine tooling through ordinary repository discipline". A fix to
  the fabric store, the broker or a lease path lands on main for everyone. Holding control seats on a known-broken
  path (e.g. the #1135 Windows Fabric CLI breakage) for 72h steps contradicts MWO-0004 ("no seat should stop useful
  unrelated work"). The operator will, rightly, not tolerate it. In practice the wedge will be abandoned for exactly
  the changes that matter.
- Fix: restrict stepped-wedge evaluation to OPT-IN primitives that are naturally per-seat (libraries, templates,
  manifests). Evaluate shared infrastructure fixes on FAB-1 / canary endpoints only, by interrupted time series with
  multiple switch points. Disclose that lab-level eta credit for infrastructure fixes is generally unidentifiable.

### E2. Interference (SUTVA violation): seats share tools, a repo and comms. MAJOR
- Control seats see the treated seats' messages, copy the primitive or reimplement its idea, or receive outputs
  produced with it. Contamination biases toward null and inflates "no effect".
- Fix: measure contamination directly (receipt-hash use of the primitive, or idea-level citation, in control seats).
  Report a complier-average estimate alongside intention-to-treat. Use hosts as clusters where possible, and accept
  that this costs units.

### E3. Power at 4 seats x 72h steps is negligible, and "its NULL is interpretable" is false. BLOCKING (for interpreting EXP-1 / LAB-1 results)
- Rough numbers: a seat verdicts perhaps 0-2 experiments per 72h. A 4-seat wedge with 5 periods gives about 20
  seat-steps and maybe 15-30 verdicted experiments in total. Detecting a drop in the INVALID+UNTESTABLE rate from 0.35
  to 0.20 at 80% power needs roughly 150 experiments per arm. Power here is about 10-15%.
- With 4 units there are 24 orderings, so the smallest randomisation p-value is 1/24 = 0.042, and only the single most
  extreme ordering can reach significance.
- An underpowered NULL is NOT interpretable. It is "no information". A hierarchical Bayesian posterior with a
  weakly-informative prior will report things like "P(benefit) = 0.74", and that WILL be read as success.
- Fix:
  - Do the power calculation now, from historical verdict rates (the Observatory backfill can supply them), and
    preregister the minimum detectable effect.
  - If the MDE exceeds any plausible effect, do not run the wedge as an efficacy test. Label it a safety/contamination
    check.
  - Pre-specify that posterior probabilities under 0.95 are reported as INCONCLUSIVE, not as directional.

### E4. Time confounding and no blinding. MAJOR
- A stepped wedge confounds calendar time with the treated fraction. Time effects here are violent: three CWOs in one
  day, plus MWOs, comms changes and model updates. Time fixed effects absorb most of the remaining power. Seats know
  their arm, so Hawthorne effects and attribution bias are present (treated seats blame failures on, or credit
  successes to, the new primitive in their packets, which then feeds model-coded fields).
- Fix: freeze lab-wide policy changes during wedge windows (a "change freeze" contract), or abandon the wedge for that
  window. Never model-code endpoints from the treated seats' own narrative.

### E5. The sham instrument (RB L2) is infeasible against agents who read code, and it is corrosive. MAJOR
- A "no-op validator" is discovered within one session by any seat that reads it. Deceiving seats about lab
  infrastructure also undermines the trust that comms and receipts depend on.
- Fix: run sham-instrument controls only inside AS experiments on HML with fresh agents. In the real lab, drop the sham
  and disclose that the Hawthorne effect is uncontrolled.

### E6. Break-even at the lower 80% bound is an ad hoc, softer bar. MINOR
- Everything else uses 95%. The 80% bound for CONTINUE is the only threshold that decides resources, and it is the
  loosest. Fix: justify it, or use the same bound and a decision-theoretic loss stated in advance.

### E7. Conflicts of interest in ownership. MAJOR
- BUILDER-OBSERVABILITY is proposed to own the Observatory (OB s6), and is itself scored by Observatory metrics
  (OBS-1..5).
- BUILDER-EXPERIMENT builds HML (AS s0.2) and the prereg manifest fields. It is then evaluated on HML (E3, E5) and
  through prereg-derived metrics.
- Aphrodite authors the frozen metric definitions, the experiments, and the lessons pack whose T49 lesson is her own,
  and her VIUs are scored by the system.
- P2 ("Builders never compute their own endpoints") is violated one level up: they build the thing that computes
  them.
- Fix: separate the builder of each instrument from every party it scores, have a non-subject seat review every
  metric-definition commit, and pin metric code by hash before the lane it scores runs.

---------------------------------------------------------------------------------------------------------------------

## F. Origin / authorship audit

### F1. Operator influence through interactive session prompts is invisible to the audit. BLOCKING (for L5/L6)
- The audit verifies origin "against operator text in MWOs, CWOs and comms". Much operator influence arrives as user
  turns typed directly into seat sessions (this harvest itself is an "operator directive" given that way), and in
  conversations whose ideas the seat later "proposes". None of that is in MWO/CWO/comms, so origin is biased toward
  SEAT_AUTONOMOUS.
- Attack: no intent is needed. The operator suggests an idea in a session; the seat implements it next day with
  `Improvement-Origin: SEAT`; the lineage looks autonomous.
- Fix: ingest operator user-turns from session transcripts as human_intervention events (with the content hash, not
  necessarily the content). A change cannot be SEAT_AUTONOMOUS if the authoring session contained operator turns within
  a preregistered lookback (e.g. 7 days) touching the same subsystem (model-coded, with human spot-check).

### F2. The `Improvement-Origin:` trailer is self-declared, and the incentive points one way. MAJOR
- Seats want credit and the operator wants an L5 story. The AUTO rule ("implements MWO/CWO text => OPERATOR") is
  ambiguous at both ends:
  - CWOs are authored by Aporia, a seat (the CWO header reads "APORIA CWO"), so the rule codes a seat's design as
    OPERATOR;
  - an operator MWO that ratifies a seat proposal can be coded either way;
  - a seat can pre-empt classification by "proposing" an idea it saw forming in operator text.
- Fix: origin is never seat-declared for headline use. It is model-coded from the full trace (first mention of the
  idea anywhere, including transcripts), with an operator-blind human-coded sample. Add a class OPERATOR_RELAYED_BY_SEAT
  for Aporia-authored orders implementing operator decisions.

### F3. Measuring autonomy creates an incentive to withhold valuable operator input. MAJOR (perverse incentive)
- Once L5 is prized, the cheapest route to "autonomous IPI" is for the operator to stay silent, or for seats to avoid
  asking, even when a correction would help. That lowers real scientific output in exchange for a rung.
- Fix: state explicitly that the North-Star metric is improvement per operator-minute (human-in-the-loop counts), and
  that L5 is a separate research question tested only in scheduled, preregistered quiet windows. Outside those windows,
  autonomy is not a target.

### F4. EXTERNAL_MODEL origin is unfalsifiable. MINOR (accept and disclose)
- Most "seat-autonomous" ideas are drawn from the model's pretraining. There is no way to separate "the seat invented
  it" from "Opus already knew it". Disclose this. The only operational handle is the A1 fix: compare a seat's
  output/forecast against a fresh-context same-model baseline.

---------------------------------------------------------------------------------------------------------------------

## G. Lineage generation slope (L4) and the higher rungs

### G1. log(payoff/cost) is undefined for payoff <= 0, and payoff is noise for almost every event. BLOCKING
- Per-event payoff is a delta-eta against a matched stream over 14 days. At this N, nearly every event's CI spans zero
  and many point estimates are negative. Taking logs forces dropping or flooring those events. That is survivorship by
  construction, the exact trap RB s4.7 names.
- Fix: model the levels. Regress payoff (including negative values) on generation with cost as a covariate, use a
  hierarchical shrinkage model, and include abandoned events at payoff = 0 with their costs.

### G2. Per-event payoff is not identifiable when improvements overlap. BLOCKING
- With several process changes per week, each with a 14-day window, and all landing fleet-wide (E1), the payoff of any
  single event cannot be separated from its neighbours. "A matched comparison stream that did not use e" generally
  does not exist.
- Fix: designate at most 1-2 EVALUATED improvement events per month, rolled out under a design (wedge or reversal) and
  with a change freeze around them. All other events are recorded as UNATTRIBUTED and excluded from the slope.
  Disclose that the slope is estimated on a curated subsample.

### G3. Generation is inflatable by citing parents. MAJOR
- g(e) = 1 + max g(parents), and parents are self-declared or model-coded from citations. Chaining each small patch to
  the previous one ("builds on ie-17") raises g at no cost. Combined with small patches being cheap, cost per event
  falls with g mechanically. That is spurious IPI.
- Fix:
  - A parent link counts only if the parent's OUTPUT is used (receipt-hash or code-dependency evidence, analogous to
    EXP-6), not if it is cited.
  - Control for event size (diff size, cost).
  - Run a generation-knockout check on a sample (does the child still work or build without the parent?).

### G4. The fitted diminishing-returns null is unconstrained at 3-5 points. MAJOR
- The functional form and parameters of the null decide the verdict. With 3-5 generations, any monotone curve can be
  fitted on either side of the data. The prior is unspecified, and so is who fits it and when.
- Fix: freeze the null's functional form AND parameters before any generation is observed, derived from an external
  source (e.g. the engine-scale A-series curves, or the historical cost of tool fixes). Otherwise report L4 as
  UNTESTABLE.

### G5. L5 is not identifiable with one operator. BLOCKING
- There is exactly one operator, so X2 has n = 1 and no between-operator contrast exists. "Operator-quiet windows" are
  operator-chosen (not randomised) and confounded with time of day, host load and the M4 quiet cadence. Above all,
  they are confounded with LAGGED operator influence. A seat executing a CURRENT/NEXT/RESERVE queue written under an
  operator CWO, during a night with no directives, is executing operator design. "Production continues in quiet
  windows" is therefore satisfied by any queue that is long enough.
- Fix:
  - Preregister RANDOMISED multi-day quiet windows (the operator commits to silence on dates drawn by a third party).
  - Credit only improvement events whose idea had NO first mention, in any queue, order, transcript or comms, before
    the window started.
  - Accept and disclose that with one operator, L5 can at most be "consistent with", never "established".

### G6. L6's generation knockout and sham lineage are infeasible at lab scale. BLOCKING
- "Remove generation g's output and re-run generation g+1" means re-running weeks of fleet history. Old tools may be
  checked out, but old model versions, operator states and fleet configurations cannot be reproduced. A "sham lineage
  of fresh-context Builders with the same budget" doubles the Builder programme.
- Fix: none at lab scale. L6 is testable only in a mini-lab replica (fresh agents on HML, with lineage and knockout
  arms), and that result is ENGINE/MINI-LAB scope by RB's own scope rule. State plainly in RB s5 that lab-scale L6 is
  UNTESTABLE by design, not merely "no data yet".

### G7. The time scale of L4-L6 exceeds model-version stability. MAJOR
- L4 needs at least 3 generations each passing L2 (lower 95% > 0), and each L2 evaluation needs weeks. Model versions
  change on a similar timescale. "Fixed model version" and "at least 3 generations" are jointly infeasible in most
  years. Event-study removal of a model switch with 3-5 data points is not credible.
- Fix: accept and disclose. Alternatively, pin the model version for the measurement programme. That is a real cost:
  it forgoes upgrades, which itself contradicts the lab's goals.

### G8. L1 requires a "FIXED task family" that real research never revisits. MAJOR
- Research questions are not repeated. Equal-resource replay of "the t1 configuration" needs t1's model, prompts, tools
  and memory, so in practice L1 can be tested only on a benchmark, i.e. HML. That measures model + context pack on
  HML, not the lab.
- Fix: maintain a standing "lab exam". This is a parametric family (HML-generated, fresh instances each time) that
  the CURRENT lab configuration (tools, packs, review process) runs quarterly at fixed budget, with a fresh-context
  baseline arm at each sitting to subtract X1. Disclose that it is a proxy.

### G9. The stale-ruler rule and C6 credit punish real ruler improvement. MAJOR (false negative and perverse incentive)
- A better ruler exposes past false positives and produces more INVALID/KILLED verdicts. Under the VIU rule (INVALID
  excluded) and the "claim only what survives both rulers" rule, real C6 improvement LOWERS eta and survives neither
  comparison. Seats therefore have an incentive to resist stricter rulers.
- Fix: credit ruler improvements by planted-battery discrimination (true-positive / false-positive on sealed
  planted-effect and planted-null items) as their own endpoint. Count invalidations of previously reported claims as
  VIUs, i.e. retractions carry information.

---------------------------------------------------------------------------------------------------------------------

## H. Cross-cutting statistical validity

### H1. Multiple comparisons across a large metric family, read by a motivated reader. BLOCKING (for any headline "improving" claim)
- The family includes FAB-1..6, EXP-1..8, OBS-1..5, LAB-1..4, 11 Observatory views, 5 cost components, several windows
  and 8 experiments with compound rules. Each is reported "honestly", but the operator's summary will pick what moved.
  P3 pairing reduces this but does not remove it.
- Fix: preregister a single hierarchy:
  - one primary North-Star endpoint, e.g. the fixed-reference information (A1) per operator-minute, with the late-
    discovery pair;
  - 2-3 key secondaries under gatekeeping (fixed-sequence testing);
  - everything else is labelled DESCRIPTIVE and can never appear in a headline.
  Publish a fixed reporting cadence, so windows are not chosen after the fact.

### H2. Seats are not independent units: one model, shared memory and tools, constant comms. MAJOR
- Seat-level analyses (within/between decomposition, per-seat normalisation, hierarchical per-seat models) treat about
  20 seats as about 20 units. Their shocks are common (model, harness, MWO), so the effective N is much smaller and
  intervals are too narrow. In the AS experiments, "3 replicate instances per arm per item" of the same model are
  sampling-temperature replicates, i.e. pseudo-replication. They are fine for estimating that model's behaviour, but
  they do not generalise beyond it.
- Fix: cluster-robust or random-effects models with a common time shock, and design effects computed from the
  backfill. State the AS inference target explicitly as "claude-opus-5-5 under harness H".

### H3. E4's internal arithmetic contradicts s0.3, and its AND-decision rule is underpowered. MAJOR
- E4 has 16 instances x 5 arms = 80 runs, which is 1 run per instance-arm. s0.3 requires at least 3 replicates per arm
  per item, so E4 needs about 240 runs (about 36M tokens, not 12M). The YES rule needs CP < CG AND CPD < CG, each
  one-sided at 0.05 on about 16 items. Joint power for a moderate effect is well under 50%.
- Fix: run the power calculation first and resize. Make one contrast primary and the other a supporting secondary.

### H4. The false-kill audit at "minimum scale" validates false kills. MAJOR
- EXP-1b re-runs 20% of killed designs "at minimum scale". A minimum-scale run of a real effect usually shows nothing,
  so it "confirms" the kill. A primitive that over-kills therefore passes its own audit.
- Fix: audit kills at the design's preregistered scale on a smaller sample, or have a blind reviewer adjudicate design
  validity. Report false-kill estimates with their power.

### H5. The retry rule launders seed-shopping as "infra". BLOCKING (scientific integrity)
- FAB-2: "a task that fails, then succeeds on an identical-input retry, is INFRA by definition". For any nondeterministic
  science task, a failing run that passes on retry gets classified INFRA, and the failed outcome drops out of the
  science record. This creates a sanctioned path for rerunning until a pass, i.e. selective reporting, and it also
  lowers the "science failure rate".
- Fix: "identical input" must include the seed and all RNG state. Any task with uncontrolled nondeterminism is
  excluded from the retry rule. Every attempt's output is retained in the receipt chain, and the science verdict is
  taken from the FIRST completed run.

### H6. Model-coded fields can be steered by the writing style of the coded text. MAJOR
- Headline metrics accept MODEL_CODED with two-coder agreement of at least 0.8. Two same-model coders agree on shared
  biases, so agreement is not validity. Seats learn the phrasings that code favourably ("per iu-x, KILL", "Found-By:
  self", "origin: own proposal").
- Fix: use a second coder from a different model family, keep coder prompts sealed, and maintain a human-coded
  validation sample with reported accuracy (not agreement). Do not code endpoints from the narrative of the seat being
  scored.

### H7. The first-mention clock suppresses early communication. MAJOR (perverse incentive)
- EXP-2's clock starts at the first commit or message naming the hypothesis id. The optimiser's response is to think
  privately, avoid naming ids early, and coordinate less. That degrades the very legibility the lab needs.
- Fix: start the clock at the earliest semantically similar mention (model-coded, any id), and keep setup time as a
  secondary endpoint, never a target.

### H8. Mandate voiding is either a loophole or voids everything. MINOR
- The operator can "recommend" instead of "mandate". With three CWOs in one day, almost every window carries a
  mandate. Fix: define voiding by the metric's dependence on the order (any order text that names the metric or its
  behaviour), not by imperative mood. Report the fraction of windows voided.

---------------------------------------------------------------------------------------------------------------------

## I. Conceptual holes

### I1. The system has no external validity anchor: every ruler, reviewer, forecaster and coder is the same model family. BLOCKING (for the word "scientific")
- "Surprising to the pool" means surprising to Opus. Consumption is citation by Opus. Review is by Opus, and
  calibration is relative to Opus. The lab can converge on a self-consistent internal vocabulary (G1 stepping stones,
  ARC3 C3R2, BEE verdicts) and score well while producing nothing a domain scientist would call an improvement.
- Fix: put a periodic EXTERNAL audit on the headline. Take a random sample of VIUs each quarter, judged for correctness
  and novelty by a human domain expert or at least a different model family with literature access, and check
  externally verifiable outputs (proved theorems, reproduced datasets, accepted external benchmarks). Report the
  external pass rate next to eta.

### I2. VIU is too narrow a unit: it cannot credit question generation, instruments, datasets, reframings or exploratory discovery. MAJOR (false negative)
- Many of the largest scientific improvements are a new question, a new instrument or a new representation. None of
  these is a preregistered claim with a verdict. UNTESTABLE is excluded even though "this is untestable at budget B"
  was among the lab's most expensive lessons (A20-A22). INVALID is excluded even though discovering that a prior result
  was invalid is high-value information.
- Fix: add separate, non-summed ledgers: QUESTION (a hypothesis later adopted by a seat other than its author and
  reaching freeze), INSTRUMENT (L2-type payoff), and RETRACTION (invalidations of previously accepted claims, credited
  as information). Count UNTESTABLE-with-diagnosis (a supply or power bound established) as a NULL-class VIU when
  reviewed.

### I3. C8 selection is wrongly treated as "not capability". MAJOR (false negative)
- CM s3.1 calls portfolio improvement "real and useful" but not "Prometheus got better at science", and attributes it
  "mostly" to James. Choosing better questions is a core scientific skill. If Aporia or seats do the choosing, it is a
  system capability. The within-seat decomposition is designed to subtract it.
- Fix: decompose aggregate gain into within, between and selection components, and credit selection to whoever made
  the selection, using the authority field on episodes. It should not be discarded.

### I4. The design conflates "is the lab improving?" (the North Star) with "is it RSI?". MAJOR
- Every control is tuned to exclude operator-mediated and model-mediated improvement, which is right for RSI. The
  operator's actual question is whether Prometheus is getting better at producing future scientific improvements. A
  human-in-the-loop lab that gets twice as productive per operator-minute IS the success case, and the ladder files it
  as "not L5".
- Fix: make the primary North-Star endpoint L1-L2 per operator-minute, with human-in-the-loop explicitly allowed.
  Treat L4-L6 as a separate research programme with its own (probably negative or UNTESTABLE) reports.

### I5. Model upgrades are treated only as confounds, but absorptive capacity is a lab capability. MINOR (false negative)
- How fast the lab converts a model upgrade into eta (tools, prompts and procedures that exploit it) is a real
  organisational capability, and it is discarded by event-study removal. Fix: measure time-to-recover-and-exceed
  after each model switch as its own descriptive endpoint.

---------------------------------------------------------------------------------------------------------------------

## J. What the system would systematically MISS (false negatives, consolidated)

1. Learning that makes the lab predict better. It lowers realised surprisal (A1). **The most important false negative.**
2. Improvements whose payoff arrives after 14 days: infrastructure, knowledge stocks, training of seat memories.
3. Shared-infrastructure fixes that cannot be wedged or attributed (E1, G2).
4. Failure prevention: non-events, crashes that did not happen. These are visible only through canaries that cover a
   narrow slice (D4).
5. Stricter or better rulers, which lower VIU counts (G9).
6. Question generation, instruments, datasets and reframings (I2), and selection skill (I3).
7. Recently produced VIUs that are not yet consumed (A8), and correct NULLs in low-visibility seats.
8. Human-in-the-loop compounding (I4), and absorptive capacity for model upgrades (I5).
9. Transfer to partially related substrates. L3 credits only substrates with no project history, while most real
   transfer is near-transfer.
10. General review or robustness skill against novel defect classes (D6).
11. Everything at realistic N. The system's default output is "not established" forever (E3, G4-G7), whatever the truth.

This last point creates the most dangerous dynamic of all. A system that cannot return a positive at realistic N will
not stay strict. It will be bypassed informally, by reading exploratory secondaries, the 80% bounds and posterior
probabilities as wins. The fix is the same as H1: one powered primary with a fixed cadence, plus an explicit
statement of which questions are UNTESTABLE at this scale, so that "not established" is not mistaken for either
"failed" or "nearly there".

---------------------------------------------------------------------------------------------------------------------

## K. Minor and editorial items

- K1. CM s1.1 says "pooled ... isotonic per seat", which is internally inconsistent. Define it (see A5).
- K2. OB s2.10 `is_viu` uses KILLED_BY_CONTROL. CM s1 says "KILLED". Is KILLED_PRE_RUN (a design killed by a supply
  screen) a VIU? Kills of one's own cheap designs are a VIU mill unless the kill's avoided cost is stated and audited.
- K3. BP s5 rates planted-battery gameability as "low". Given D1-D4, it is medium at this scale.
- K4. OB s4 claims "AUTO" for WORK_STATE-derived episodes "from MWO-0001". WORK_STATE is seat-written, and the
  feedback record already documents status that looks live while the data is stale. Treat it as SEAT_ASSERTED until it
  is reconciled with state_truth.
- K5. AS s9's token estimates are inconsistent with s0.3's replication rule (H3) for E4, and possibly for others.
  Recompute all of them.
- K6. Lane authority is cited as "Aporia/CWO". If the lab's management of experiments is moving away from Aporia, the
  authority field on episodes and the OPERATOR_RELAYED_BY_SEAT origin class (F2) matter even more. Confirm the
  current authority before freezing the origin taxonomy.

---------------------------------------------------------------------------------------------------------------------

## Summary table

| ID | Item | Severity |
|---|---|---|
| A1 | realised surprisal falls as the lab learns; use a fixed reference prior and credit forecast skill | BLOCKING |
| A2 | outcome-partition inflation of surprisal | BLOCKING |
| A3 | surprisal rewards underpowered, noisy and false-positive verdicts; no power gate on NULL; no clawback | BLOCKING |
| A4 | salami slicing; summed correlated surprisal | MAJOR |
| A5 | per-seat isotonic calibration at small N; cold-start exploit window | MAJOR |
| A6 | single same-model review; no reviewer-recall measurement; cited independence rule missing | MAJOR |
| A7 | consumption manufactured by citing; `consumes:` laundered to AUTO; self-consumption allowed | BLOCKING |
| A8 | consumption right-censored and popularity-driven | MAJOR |
| A9 | preregistration becomes the new activity metric | MAJOR |
| B1 | self-asserted difficulty_forecast used as the matching control | BLOCKING |
| C1 | eta vector allows component cherry-picking | MAJOR |
| C2 | cost shifting to unmetered resources | MAJOR |
| C3 | operator-minutes falls by decree (MWO-0004 R1) or by silent failure | BLOCKING |
| D1 | E4 traps mirror the lessons pack, so L3 transfer is circular | BLOCKING |
| D2 | same-model battery authorship; drift between rotated batteries | MAJOR |
| D3 | custody unenforceable on shared hosts (precedent #1128) | MAJOR |
| D4 | 10 fixed scheduled canaries are recognisable; teaching to the test | MAJOR |
| D5 | planted staleness in a consenting real seat; false-alarm bound unpowered | MAJOR |
| D6 | batteries from the historical catalog reward fighting the last war | MAJOR |
| E1 | shared infrastructure cannot be stepped-wedged | BLOCKING |
| E2 | interference between wedge arms | MAJOR |
| E3 | wedge power about 10-15%; an underpowered null is not interpretable | BLOCKING |
| E4 | time confounding; no blinding | MAJOR |
| E5 | sham instrument infeasible and corrosive in the real lab | MAJOR |
| E7 | Builders build the instruments that score them; the author scores her own lesson | MAJOR |
| F1 | operator influence via session prompts is invisible to the origin audit | BLOCKING |
| F2 | self-declared origin trailer; ambiguous for Aporia-authored CWOs | MAJOR |
| F3 | autonomy metric incentivises withholding operator input | MAJOR |
| G1 | log(payoff/cost) undefined for payoff <= 0, forcing survivorship | BLOCKING |
| G2 | per-event payoff not identifiable with overlapping fleet-wide changes | BLOCKING |
| G3 | generation inflatable by parent citation | MAJOR |
| G4 | diminishing-returns null unconstrained at 3-5 points | MAJOR |
| G5 | L5 not identifiable with one operator; lagged influence through queues | BLOCKING |
| G6 | L6 knockout and sham lineage infeasible at lab scale | BLOCKING |
| G7 | L4-L6 timescale exceeds model-version stability | MAJOR |
| G8 | L1's fixed task family does not exist in real research | MAJOR |
| G9 | stale-ruler and VIU rules punish real ruler improvement | MAJOR |
| H1 | multiple comparisons across about 40 metrics read by a motivated reader | BLOCKING |
| H2 | seats not independent; pseudo-replication | MAJOR |
| H3 | E4 run count contradicts the replication rule; AND-rule underpowered | MAJOR |
| H4 | minimum-scale false-kill audit validates false kills | MAJOR |
| H5 | the retry rule launders seed-shopping as INFRA | BLOCKING |
| H6 | model-coded fields steerable by phrasing; agreement is not validity | MAJOR |
| H7 | the first-mention clock suppresses early communication | MAJOR |
| I1 | no external validity anchor; all rulers are the same model family | BLOCKING |
| I2 | VIU excludes questions, instruments, retractions and diagnosed UNTESTABLE | MAJOR |
| I3 | selection skill wrongly subtracted as "not capability" | MAJOR |
| I4 | the North Star is conflated with RSI; human-in-the-loop gains discounted | MAJOR |
| B2, C4, D7, E6, F4, H8, I5, K1-K6 | see text | MINOR |
