# Eos journal -- 2026-09-11, first active pass (EOS-01 ACTIVE)

Worktree D:\Prometheus-worktrees\eos-base-role, branch
eos/active-pass-1-2026-09-11, base_sha 05b1134e6, machine M2 (SPECTREX5).
What happened, not what was wished.

## Boot

- Synced comms before the prompt: 1 new, #65, Archaeon's ack. Both defects
  this seat reported on the adoption pass were fixed the same day: comms
  now REFUSES a database that holds no comms schema (fail closed, with
  EW_DB_HOST named in the error), and the three M2 scheduled tasks are
  registered so the base-role self-test is green on M2. Base rule 9 was
  added in the same wake -- upstream liveness is a launch precondition --
  and it landed exactly in time to govern this pass.
- New task branch from the recorded SHA. The adoption branch merged at
  9d87469a0 and is closed.

## Order of work, as the operator specified it

1. EOS-19 first. The D-23 guard went on eos_daemon.main() and
   library_scanner's __main__ before anything else, and on probe.py when
   it was written. Three entry points, one test each.
2. Base rule 9 next, because building on a dead upstream is the failure
   the rule exists to prevent. Bounded probe: 2 requests, both HTTP 200,
   431 ms and 244 ms, 12 items each, at or under 75 percent of arXiv's
   documented 1-per-3-seconds. LIVE.
3. Preregistration committed before either mechanism ran, in its own
   commit, with the sample, the ground truth and four predictions --
   including one attack on Eos's own new gate that Eos predicted the gate
   would fail.
4. Then, and only then, the run.

## A defect fixed before it could become a habit

`agents/eos/` is excluded by the root .gitignore. The seat's seven files
had been force-added individually, which is why 163 days of digests never
reached the repository and why every new file this pass would have been
silently ignored. Re-included WITHOUT a `/**` glob so that a new
agents/eos/.gitignore stays authoritative for `.env`, `.env.*`, `*.key`,
`*secret*`, `*credential*` and `reports/`. Verified both directions and
held by two regression tests: a credential file must never become
trackable as a side effect of a convenience.

## What the run found

Four preregistered predictions, four held. The numbers are in
roles/Eos/intake/FIRST_SEASON_2026-09-11.md; the three that matter:

- The old scorer gave 100/100 to an abstract that is nothing but its own
  substring lists, and 8/100 -- below its own firing threshold -- to the
  one item in the sample that bears on a live lane. It is retired, not
  repaired.
- Held one item fixed and varied only the repository: the old score was
  identical in both worlds, the gate's verdict flipped. That is the whole
  difference between the two mechanisms and it needs no judgement to read.
- All 28 distinct items behind the old scorer's 42 ATTENTION slots were
  refused, and all 4 constructed bait items. Seven items went to a human
  with the exact file and token that would have to change.

## What the run found out about the thing I built

Three failures, and they are the useful part.

1. The gate recorded a search that TIMED OUT as a refusal. `git grep` over
   39,284 files exceeded its 60 s budget and the item came back REFUSED.
   Instrument error banked as evidence about the world. INDETERMINATE is
   now a state of its own and a test holds it.

2. The dedup search asked "does the program already have this?" over a
   tree containing Eos's own records. First run: 2 hits, both of them this
   seat's own probe and sample. Excluded those; 1 hit remained, and it was
   intake.py itself -- the comment I wrote DOCUMENTING the contamination
   defect contaminated the instrument by naming a real item. Two rounds of
   the same bug, one level apart. The rule that survives both is that the
   search asks what the PROGRAM has, and Eos is not the program.

3. The one ACQUIRE candidate was refused because I had preregistered a
   destination I never verified. There is no vivarium/worlds/ directory. I
   did not edit the claim in the preregistered run; the resubmission with
   a real path is recorded separately and both are on the ledger. The gate
   caught its own author being sloppy, which is worth more than the bait
   test: the bait was designed to fail and this was not designed at all.

4. And the predicted one: the gate CAN be fooled. A bait item echoing the
   operator's north-star phrasing, paired with a real file and a real
   token chosen because they exist rather than because they are related,
   passed every check. Predicted in writing beforehand so it cannot be
   sold later as a limitation that was always understood. The hole is
   locked into the test suite; closing it breaks that test on purpose.

## The three commissioned questions

- EOS-03: the substrate-mining agent WAS built, the same day, as Clio
  (2e4072ae5). Full promised scope shipped. Measured: 596 papers, 1,082
  claim extractions, dead 104 days. Its downstream died ELEVEN DAYS BEFORE
  the miner did, and the heartbeat still says "online". No roles/Clio, no
  registry row, no owner. Eos does not reclaim it and says so explicitly.
- EOS-04: fourteen call sites across nine lanes, not four. Moving the file
  first breaks all of them silently, which this program has already paid
  for once. Proposal is route-then-move: get to one reader (keys.py)
  without touching a credential, then the move is one line.
- EOS-02: 15 rows split 8 model-provider (4 already covered by
  prometheus_llm, 4 not) and 7 non-model sources with no completions
  interface. Proposal: retire the 4 covered, offer the 4 uncovered to
  prometheus_llm as a one-time contribution, keep 7 as a narrow SOURCES
  residue, mark every unmeasured row UNVERIFIED. Falsifiable: if
  prometheus_llm's maintainer says the sources belong there, delete the
  file instead.

## Executed / not executed

Executed: comms sync, the bounded probe (2 requests), the sample builder,
the season harness three times (twice after fixing a gate defect), 25
controls, the base-role self-test, read-only SQL against the M1 spine, git.

NOT executed: the daemon. No scheduled task was created. No scan cycle
ran. No model was called at any point in this pass -- the gate has no
model in it, and the retired LLM hop was not invoked. The operator's
condition on restarting collection is untouched and undecided.

## Next executable action

None that this seat can take alone. EOS-02 needs prometheus_llm's answer,
EOS-03 needs an owner for Clio, EOS-04 Phase 0 is thirteen lanes' work.
Restarting collection is a separate decision the operator reserved, and
the evidence it asked for is committed.

## Session close

- Pushed 5eb6c3d9d, verified an ancestor of origin/main. Three named-SHA
  merges were needed (545817f7e, a79ffdde8 and one in between); origin
  moved four times during the pass, which is what a busy fleet day looks
  like from inside a worktree.
- Tests on every merged tree before every push: 33 passed (25 intake
  controls + 8 base-role self-tests). The base-role self-test is green on
  M2 for the first time, because Archaeon registered the three M2
  scheduled tasks this seat reported this morning.
- Posted: comms #76 Apollo, #77 Nyx, #78 Icarus, #79 Archaeon (the
  admission queue, one question each), #80 broadcast (the season
  results). Bodies committed first, manifested, then posted.
- comms sync at close: 0 new, queue length 0.
- One shell lesson re-learned the hard way: a multi-file heredoc with
  quoted content failed mid-write and left two of four prompt files
  unwritten. The base role says heredocs with quotes are unreliable in
  this shell and to write files then run them. It is right. The partial
  state was visible immediately (ls showed 2 of 5 files) and nothing was
  committed in between.

## What I would attack first if I were attacking this pass

Named here because the seat that produced a result is the worst judge of
it, and writing the attack down is cheaper than pretending it will not
come.

1. The sample is 24 live items from TWO arXiv queries chosen by me. The
   six survivors are six items whose referents I went looking for. A
   different two queries could plausibly yield zero survivors, and I
   would have no way to tell that from "the horizon is quiet".
2. POP-A being refused 28 out of 28 is less impressive than it reads:
   those items were selected by an instrument keyed to a premise that no
   longer exists, so refusing them is close to tautological. The honest
   version of that row is "the new gate does not inherit the old gate's
   premise", which is weaker than "the new gate is right".
3. Test 2 is the only judgement-free result and it proves something
   narrow: that the gate reads the repository and the score does not. It
   does not show the gate reads it WELL.
4. Six items to four seats is six chances for a seat to answer "this has
   nothing to do with my file", which is the Test 4 hole arriving in
   person. If two or more come back that way, the gate's PENDING rate is
   inflated and CALIBRATION.md gets a row I will not enjoy writing.
