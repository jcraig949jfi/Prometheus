# Aporia Standing Loop — resumable by any session

**Principle:** the loop is state, not a process. If the session dies, any new Aporia session
resumes by reading this file + the queues. Armed via self-paced wakeups; work-paced, not
watch-paced — every pass does one real item.

## The four loop layers (who moves what)

1. **Deterministic layer — Windows Scheduled Tasks** (dumb-reliable, no LLM):
   weekly backup (pg_dump fire+sci → Z:\ + robocopy F: corpus, per DECISION 2, precedent:
   PrometheusRekeyObjectZeros); daily DR dispatcher fire (per DECISION 5) once deck exists.
2. **Aporia session loop (this file) — M1's working heartbeat.** Each pass, in order:
   a. `git pull` — ingest fleet commits; if probe results/verdicts landed, **rescore the
      market** (BOTTLENECKS confidences per MOVES expected_if_* preregistrations) and update
      MOVES statuses. Market upkeep is by hand until CI exists.
   b. Execute **one** item from the runnable backlog (below), emitting typed objects.
   c. Commit + push. Report to James only when something changed (noop passes collapse).
3. **Probe seats** — Ergon/Charon/Harmonia B/Techne/Hephaestus sessions, human-kicked
   (kickoff-prompt practice). Not this loop's job; this loop *watches* and rescores.
4. **Weekly HITL page** — Monday: one page (market state, telemetry consumed/emitted computed
   by hand pre-CI, pending DECISIONS by staleness). Alethelia takes this over when built.

## Runnable backlog (priority order; all in-harness, $0)

1. **DR deck #1 + firing cadence** — build the first 20-prompt deck (consumers named at
   firing): ladder Canon §4 literature-grounding pass + market-bottleneck evidence pulls.
   Then hand daily firing to layer 1.
2. **Back-corpus mining** — 442 unread DR reports, slices of ~20/pass; yield → anti-anchors,
   probe templates, catalog updates. (The Pythia consumer test, finally.)
3. **R4 probe generator** — Canon build-debt #1, phase0 pattern, deterministic grading.
4. **Repair ledger + citation-chain base rate** — my own pre-committed self-audits.
5. **M-004 kill-resurrection + detector-band audit** — **APPROVED 2026-08-17.** Prereg LOCKED
   (`pivot/PREREG_M004_kill_resurrection_2026-08-17.md`) before any data touched. Next steps in
   order: co-sign (Charon + Harmonia B/Techne) -> independent synthetic injection (Aporia must
   NOT be the injector) -> 5% calibration set -> 80% recovery gate -> blinded hold-out run.
6. **Plumbing sessions** (gateway, queue client, germline schema, CI, decoys, Alethelia) —
   as capacity allows; schema + backup job first (DECISION 2 makes backup non-deferrable).


## THRESHOLDS FAIL IN BOTH DIRECTIONS (adopted P125, the mirror of GATE DESIGN)

GATE DESIGN catches a threshold FINER than the measurement can resolve. This is the mirror
failure: a threshold far COARSER than the resolution, which makes a real, cleanly detectable
effect unreportable as an advance. Campaign W preregistered an MDE of 0.0306 from an assumed
discordance of 0.15; the measured within-arm discordance was 0.0225, giving a true MDE of
0.0106. The branch bar sat at ~3x the achievable resolution, so an effect at 1.65x MDE would
fire the "too small to matter" branch while being nothing of the kind.

- **Check the threshold against the measured variance in BOTH directions** — too fine makes the
  decision noise, too coarse makes a finding invisible.
- **Where the variance is unknown in advance, preregister the threshold as a MULTIPLE OF THE MDE**
  (e.g. "lo > 2x MDE") rather than as an absolute number, so it self-calibrates when the variance
  is finally measured.
- **An assumed variance is a measurement you have not made.** It can be wrong in the direction
  that costs a true finding as easily as in the direction that flatters one.
- Do not adjust the threshold after seeing the effect; report the mismatch beside the verdict.

## A VERDICT RULE IS AN INSTRUMENT (adopted P121 from two wrong rules in one script)

**Automated verdict rules need the same scrutiny as the measurements they judge.** In one X-5
audit script, two of three rules produced confident labels that were the opposite of the truth:
one compared a suspect operator against a comparator that was equally affected, so an
equally-affected second case masked the finding instead of confirming it; the other compared
single draws against a threshold designed for a mean, where one hit already exceeded the line,
and reported a passing gate as unreliable.

- **State what the rule would output under the null** before running it. If the null output is
  the same as the finding output, the rule discriminates nothing.
- **Check the comparator can actually discriminate.** "X is worse than the others" fails when
  one of the others has the same defect.
- **Check granularity against the threshold** — the same rule as GATE DESIGN, applied to the
  judgement layer: a per-draw test against a mean-calibrated threshold is not a test.
- Report the measurement even when the rule's label is withdrawn; the numbers usually survive
  the rule that misread them.

## BRANCH CONDITIONS MUST PARTITION (adopted P116 from four consecutive defects)

**Before the pass that reads them runs, verify that the preregistered branches map every
reachable reading to exactly one terminal state.** Four failures across three campaigns:
D1-D5 were written qualitatively and forced numeric cuts to be invented at adjudication;
D4's cut was one of those; K3 carried a chance denominator that was arithmetically wrong for
the scoring rule in use; and K1-K3 failed to partition, leaving the region actually observed
(D below the REDESIGN floor with L2 far above chance) uncovered, so a terminal state was
reached by default rather than by a fired branch.

- **Enumerate the outcome space and check coverage** — including the "no effect but well above
  chance" region, which is where X-3 landed and which three campaigns of branch-writing missed.
- **Every branch numeric, every threshold power-derived**, and every denominator checked against
  the scoring rule actually in use, not the one imagined when the branch was written.
- **A terminal state reached by default is reported as such**, never presented as a fired branch.

## GATE DESIGN — a gate on gates (adopted P113 from Campaign X-2's own failure)

**A threshold whose distance from the measured value is smaller than that measurement's
standard error is not a gate.** Campaign X-2 set an entry gate at 0.95 on a 125-pair benchmark,
cleared it at 119/125 = 0.9520 on development, failed it at 118/125 = 0.9440 on frozen, and
spent two passes moving a number across a line that sat 0.006 away while the binomial SE was
0.0195. Both readings were noise; the pass and the failure carried equal information.

- **Compute the standard error BEFORE choosing the threshold**, and place the threshold at
  least ~2 SE from any value the instrument is likely to produce. For a 0.95 criterion:
  SE 0.01 needs ~475 trials, SE 0.005 needs ~1,900.
- **Report the interval beside the verdict**, always. A gate verdict without its CI is a
  point estimate pretending to be a decision.
- **Never move a gate after seeing the number.** An unresolvable gate is fixed by adding
  power, not by relocating the line to where the data landed.
- Applies to every numeric branch condition, not only entry gates — including the D/E-style
  preregistered branches, whose qualitative wording twice forced thresholds to be invented at
  adjudication time.

## CAMPAIGN DISCIPLINE (adopted P106 from external review 2026-08-22)

The loop's defect was never "verification instruments only confirm" — the record falsifies
that. It is that **the adjudicator is strong and the search policy does not learn**: priorities
are assigned at thread-mint time and no outcome in 105 passes changed a proposal distribution.
These rules exist to fix that, and they override the old top-unblocked-by-priority rule.

- **At most TWO live threads.** Nothing else is live. A third idea is written down, not started.
- **Checkpoint-bounded microcampaigns, not round-robin.** Stay on one thread up to THREE
  consecutive passes or until its predefined checkpoint, whichever comes first. Shape:
  (1) instrument + preregistration, (2) primary experiment, (3) falsification / replication /
  mechanism chase.
- **Terminal states are ADVANCE / REDESIGN / PARK / KILL.** There is no fifth state called
  "interesting, continue exploring." Every campaign emits exactly one at its checkpoint.
- **Continuation requires one of:** a preregistered branch discriminated; hypothesis space
  materially narrowed; a reusable capability produced *with a named waiting consumer*; an
  anomaly surviving a stronger null; or the result changing what runs next. "Built useful
  infrastructure" does NOT qualify without a consumer already waiting — that loophole produced
  30 paradigm trees with no ingestion path.
- **Instant kill:** positive control fails; a blind test leaks labels; the null cannot
  distinguish the effect at useful power; a required dictionary would itself be a research
  program to build; the result is invariant under a control that should destroy it.
- **A KILL is a successful terminal state**, recorded as such.
- **Unreviewed results do not create policy momentum.** They may trigger replication, stronger
  nulls, and mechanism work; they may NOT spawn descendants, new paradigms, ontology changes,
  or backlog reprioritization until reviewed. Compute ahead, do not commit architectural state.
- **Loop self-instrumentation, reported in PULSE:** decision yield DY₂₀ (fraction of the last
  20 passes causing ADVANCE/DEMOTE/KILL/material BRANCH), open-thread debt (threads without a
  terminal checkpoint), restart tax (fraction of a pass spent reconstructing state). The
  over-interleaving signature is **debt rising while decision yield falls**.
- **Tooling is installed on measured demand only** — never because a research system "ought to"
  have it.

## Standing check — paradigm registry (added P82)

Any pass that touches `aporia/paradigms/` runs `python aporia/paradigms/validate_paradigms.py`
before committing (exit 0 required). The jsonl record is a pure projection of the prose
artifact; divergence is a bug in the record (see `aporia/paradigms/SCHEMA.md`).

## HARD RULE — shadow worklog (James, 2026-08-20)

**Every pass appends one record to `engine/shadow/WORKLOG.jsonl` and includes it in the
pass's commit.** Schema and rules: `engine/shadow/WORKLOG_SCHEMA.md`. Non-negotiables per
record: pre-stated readings, exact evidence numbers, claims typed with strength, citations
with links (primary literature for math content), a non-empty self_identified_weaknesses
list, and a falsifier. An external reviewer (Elenchus, M2 — charter in
`engine/shadow/REVIEW_AGENT_PROMPT.md`) writes `engine/shadow/REVIEWS.jsonl`; at pass start
read any unaddressed reviews and respond in-log (fixed / acknowledged / rebutted). The
reviewer never blocks this loop; this loop never edits REVIEWS.jsonl. A pass without a
worklog entry is an incomplete pass.

## HARD RULE — default-continue (James, 2026-08-18)

**A pass that ends by asking James a question is a FAILED pass.** Seven months and ~20
attempts produced the same failure: an agentic loop pauses because the model owns control
flow and a check-in disposition takes "report" over "continue" every turn. The mechanism to
prevent this (DECISIONS.jsonl) was designed, written into three documents, and then never
used once — I asked in chat instead, every time.

Operating rules, mechanical:

1. **Ambiguity resolves to option A. Log it, continue.** James: *"when I want A, then B.
   Almost always."* A logged wrong choice is reversible; a stall is not.
2. **Reversible ⇒ just do it.** No permission for anything undoable by a later commit.
3. **Irreversible items block THEMSELVES, never the queue.** File to DECISIONS.jsonl with
   status PENDING-HITL and keep working on everything else.
4. **Reports say what was done and decided — never what is needed.** "What's next?" is not
   a question for James; it is the next queue item.
5. **The driver owns continuation** (`engine/driver/run.py`). Inference answers bounded
   questions and returns; it is never asked whether to keep going.
6. **Violation is checkable:** grep a pass's output for a question directed at James. If
   present, the pass failed regardless of what else it produced.


## Steering protocol (James, 2026-08-18)

- **Every pass STARTS by reading `engine/STEERING.md`** and obeying it before pulling work.
  Processed entries move to `STEERING_LOG.md` with what was done. Empty file = full speed.
- **Every pass ENDS by regenerating `engine/PULSE.md`** (`python engine/driver/pulse.py`) and
  committing it — the skimmable, query-traceable state page James reads at 5-hour or 3-day
  granularity. Nothing in it is narrated; north-star judgment is his to make from computed state.
- Steering is BY STATE, never by conversation: edit bottleneck confidences, kill/add moves, veto
  AUTO-TAKEN rows, drop a STEERING line. None of it blocks the loop; all of it redirects the next
  pass.


## The backlog mandate (James, 2026-08-18)

- **Target: ~1000+ prioritized threads, continuously regenerated.** `engine/driver/backlog_gen.py`
  materializes threads ONLY from verified on-disk sources (722 at first run; catalog threads
  expand x30 paradigms on execution — ceiling ~16K). Rerun the generator each pass; it is
  idempotent. Reprioritization is deterministic (score in the generator) plus market linkage.
- **PARK, DON'T ASK — the stuck protocol:** when a thread blocks (gate unmet, error, needs a
  seat), set status=PARKED with parked_reason, and MOVE ON to the next thread by priority. Never
  stop the loop; never ask James in chat. Parked threads surface automatically in his 6x/day M4
  email ("Parked threads — yours to unstick", grouped by gate) and in PULSE.md. James unsticking
  a gate = editing the thread or STEERING.md; the next pass picks it up.
- **Sub-agent fan-outs pull from the top of BACKLOG.jsonl** for their seat (kickoff prompts name
  the thread ids). A fan-out that finishes its thread files results and pulls the next.


## Stash discipline (hardened 2026-08-18 after an incident)

A blind `git stash` + `git stash pop` pair popped an ANCIENT stash (May-era Hecate WIP)
when the tree happened to be clean, conflicting other agents' journals. Rule: only stash
when dirty, with a tagged message, and pop only your own tag:

    [ -n "$(git status --porcelain -uno)" ] && git stash push -q -m aporia-loop
    ... pull/push ...
    git stash list | grep -q aporia-loop && git stash pop -q

Never `stash pop` unconditionally. Old stashes in the list belong to other agents/eras —
never drop them; they may hold uncommitted work (one held two never-committed DR batches).

## Standing rules
- **Every gate ships an ELI5 (James, 2026-08-18):** any thread parked on a NEW gate string gets
  a two-sentence plain-English entry in `engine/queues/GATE_ELI5.jsonl` the same pass, and every
  PENDING-HITL decision carries an `eli5` field at filing. The email renderer displays these
  verbatim (still zero LLM in the email path — the loop authors them at creation time, committed
  as data). A gate rendering "(no ELI5 yet)" in the email is a failed pass item.
LAW 1 at every emission (consumer named); trace-vector shape for failures; decoy discipline
once assembled; no germline ignition (gates: constitution + probe verdict + co-signer seat);
irreversibles → DECISIONS, never blocked on.

**Model-tier rule (James, 2026-08-17):** this loop runs on **Opus-tier** (or lower when a pass
is purely mechanical). Fable's limited pool is reserved for the divergence seats — the
Hephaestus meta-analysis role on M3 — and for occasional high-stakes passes (spec audits,
verdict adjudications, constitution review). The gateway's cheapest-sufficient principle
applies to our own sessions, not just to children. Model provenance stays stamped per commit.

---

## P138 — A GATE MUST BE SHOWN REACHABLE BEFORE ITS NULL IS READ

CYCLE 138-C' preregistered a similarity cut of Jaccard >= 0.14. The maximum **attainable**
similarity over the whole proposal x closure grid was 0.1364. The gate could not fire on any
input. It returned zero, and zero was the answer that flattered the conclusion.

P125 already said thresholds fail in both directions. This is the sharper operational form:

> **Before reading a null, compute the maximum value the statistic can take on the actual data
> and confirm the threshold sits inside that range.** A threshold outside the attainable range
> is not a strict test; it is a non-measurement wearing a test's clothes. Report the reading as
> VACUOUS, not as a null, unless the verdict can be shown to survive on grounds independent of
> the cut.

The external reviews predicted exactly this failure class one cycle earlier — V1, V3, D1 and D5
were judged unfalsifiable as written — and the instrument shipped with the same defect anyway.
Recognising the pattern in prose did not prevent committing it in code. The check has to be
**executed**, not understood.

## P138 — THE COUNTERFACTUAL-CONSEQUENCE TEST

For any claimed capability, state in advance **what decision would go differently**, and then
verify the decision was **eligible** to go differently.

CYCLE 138-C' is the worked example. The one substantively correct suppression the closure gate
found — PROF-Harmonia against campaign R — sat at priority 10 against a top-20 eligibility floor
of 68. Even a perfectly working gate suppressing it would have changed no allocation. A
capability that fires only where firing has no consequence has not been demonstrated.

Corollaries adopted from the CYCLE 139-R review round:

- **A consumption test may not have the producing thread as its own consumer.** Self-consumption
  measures nothing.
- **A grading metric must be preregistered and MECHANICAL, not interpretive.** An interpretive
  metric is a threshold supplied at adjudication time, which is the P114 failure renamed.

## P138 — THE LOOP'S INHERITANCE HORIZON IS ONE CAMPAIGN

Measured over the WORKLOG: of passes 100-137, **24 of 37** cite prior work, but **1 of 37** cites
anything below P100, and nearly all citations reach back only 1-3 passes.

Within a campaign, inheritance is real and load-bearing (X-2 built on X's burned split, X-3 on
X-2's unresolvable gate, W on X-5's overlap artifact). Across campaigns it is near zero. What
resembles accumulated memory is **campaign-local continuity that resets at every terminal state**.

Practical consequence: do not claim that a pass "builds on" the loop's history without naming the
specific prior pass and the specific finding. The measurement says that claim is usually false.
