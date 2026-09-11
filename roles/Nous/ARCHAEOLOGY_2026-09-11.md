# Nous archaeology, 2026-09-11

> Booting an old seat is an archaeological event, not an instruction to
> resume its last queue (roles/base-role/RESPONSIBILITIES.md).

Currency: 2026-09-11. Read from origin/main 363120e08 in the worktree
D:\Prometheus-worktrees\nous-base-role (linked; git-dir differs from
git-common-dir; branch nous/base-role-adopt-2026-09-11). Every number
below has its source beside it. Numbers marked VERIFIED TODAY were
measured by this seat with roles/Nous/science/corpus_audit.py, which is
committed beside this file and reproduces them in one command. Numbers
marked CITED are taken from another seat's artifact and were not
re-derived here.

WHICH TREE A NUMBER CAME FROM IS PART OF THE NUMBER. Section 2 is the
reason: this seat's corpus is 5,918 rows in the repository and 10,105
rows on one machine's disk, and the first draft of this file reported
the second figure as though it were the first.

## 0. What the seat was

Nous, "the combinatorial hypothesis engine": the FIRST stage of the March
2026 forge pipeline. It sampled three-concept triples from a 95-concept,
20-field hand-written dictionary (agents/nous/src/concepts.py), asked one
hosted model what computable reasoning mechanism the collision produced,
asked THE SAME MODEL to rate its own answer on four 1-10 dimensions,
averaged three of those four into a composite, and ranked by it.

    Nous -> Coeus -> Hephaestus -> Nemesis -> Coeus -> Nous (weights)

Coeus encoded the triples and learned per-concept forge effects;
Hephaestus sorted its forge queue by Nous composite plus Coeus priority;
Nemesis attacked the forged tools; Coeus fed weights back into Nous's
sampling. Nous was the source of the selection pressure for all of it.

Commits touching agents/nous (`git log --oneline --all -- agents/nous`),
2026-03-24 to 2026-03-29, plus one later commit not authored by this lane:

    2f3e4eb6f  2026-03-24  Ignis v2 + Nous + Hephaestus: ejection mechanism ...
    da42cc7e0  2026-03-25  Forge pipeline v2: Coeus causal intelligence, ...
    2a186ba24  2026-03-25  Phase 3-4: RLVF fitness function, provenance gate, ...
    7b4903a00  2026-03-25  Update all docs: build plan, 4 agent READMEs ...
    923d11c66  2026-03-25  Harden error handling across all 21 pipeline modules
    45f225f51  2026-03-25  Batch 4 pipeline results: 140 forge tools, ...
    8af6ba9e5  2026-03-27  Complete pending tasks: 89-cat eval, ... Nous weights
    d65f243a0  2026-03-27  Overnight gap closing: ... gap-targeted Nous triples
    302c002d3  2026-03-28  Wire priority_triples.json into Nous combination generator
    6058e6eb1  2026-03-29  Hephaestus forge v7 + ... agent updates + doc cleanup
    8b8676272  2026-05-13  Portfolio chip 3 + reasoning-forge autopsies + monitor

Six days of authorship. The seat ran six days past the last of them, and
section 2 is about what happened to those six days.

## 1. How the seat ended: it starved, it was not stopped

VERIFIED TODAY. The last evaluated combination anywhere on disk is
timestamped 2026-04-02T12:43:29.261354 (run 20260402_090737). The last
line of agents/nous/nous.log is:

    2026-04-02 12:43:31,277 [NOUS] INFO [151 total] Gauge Theory x
      Global Workspace Theory x Adaptive Control
    2026-04-02 12:43:31,277 [NOUS] INFO   API call (attempt 1)...

There is no further line. The call never returned and nothing was written
after it. The preceding minutes of that log show the shape it died in:
two to three 60-second retries per call, one hard timeout, and

    2026-04-02 12:41:08,329 [NOUS] WARNING Skipping failed combination:
      ['Gauge Theory', 'Swarm Intelligence', 'Epistemology']

Nous was not shut down, retired or decided against. Its upstream degraded
until each call cost minutes, and then one call did not come back. Nobody
noticed for 162 days -- not the seat, not its consumer, not the program --
because the loop had no freshness record, no dormancy threshold and no
alarm route, the three things base rule 7 now requires and which this
pass supplies (section 7).

## 2. THE FINDING: 41% of this seat's output never reached the repository

VERIFIED TODAY, and it is the most consequential thing on this pass.

    tracked in git at 363120e08     12 run dirs   5,918 rows
                                    2026-03-24 .. 2026-03-27
    present on this host's disk     22 run dirs  10,105 rows
                                    2026-03-24 .. 2026-04-02
    ------------------------------------------------------------
    IN NO TREE, ON ONE DISK         10 run dirs   4,187 rows   17 MB
                                    2026-03-28 .. 2026-04-02

Four thousand one hundred and eighty-seven evaluated combinations --
41.4% of everything this seat ever produced, including the whole of its
final six days and the run it died in -- exist only in the working
directory of the canonical checkout on this one machine. So does
agents/nous/nous.log, the only record of how the seat ended, quoted in
section 1 above.

THE CAUSE, named exactly (`git check-ignore -v`):

    .gitignore:140   agents/nous/runs/
    .gitignore:200   agents/*        (blanket; no `!agents/nous/` re-include)

The twelve tracked run directories were force-added in the March commits.
Every run after 2026-03-28 landed inside an ignore rule and was silently
dropped. Nothing warned, because a `git status` on an ignored path says
nothing at all -- ignored output is invisible in exactly the way health
and silence are indistinguishable.

THIS IS NOT A NOUS-SPECIFIC DEFECT, and this seat does not claim a
pattern from its own instance. The reference class was counted instead --
all 22 directories under agents/, ignored-file counts from
`git ls-files --others --ignored --exclude-standard`, sizes from du:

    seat          tracked   IGNORED files   MB
    hephaestus     17,364          5,151   237
    nemesis            12          3,022   108
    icarus             58            644     4
    nous               56             44    44
    eos                13             11     4
    skopos              4              7     1
    clymene             5              4     1
    auditor             1              4     1
    aletheia            6              3     1
    coeus           4,040              3    29
    hermes             47              3     1
    shared              3              3     1
    metis              11              1     1
    _shared            34              1     1
    ------------------------------------------------
    22 dirs scanned; 14 of 22 (64%) hold ignored files
    21,763 tracked            8,901 IGNORED        442 MB

Untracked agent output is the NORM under this .gitignore, not an
anomaly: 8,901 ignored files against 21,763 tracked. Eos found the
identical failure on its own seat the same day and wrote it into
.gitignore's own comments (line ~229): "Before today the seat's 7 files
were force-added and every new file was silently ignored -- which is why
163 days of digests never reached the repository."

The sharpest row is not this seat's. NEMESIS -- the adversarial-testing
stage of this very pipeline, the one hop whose entire purpose was
independent attack -- has 12 tracked files against 3,022 ignored. Taken
together with hephaestus (5,151) and this seat (44 of 100), the March
forge pipeline's evidence exists mostly outside the repository at three
of its four stages. That is stated as a measurement, not a verdict:
whether those ignored files are results or scratch was NOT determined
here, and determining it is not this seat's lane. What IS this seat's
lane is saying so to the seats that own them (NOUS-06).

So the honest statement is NOT "Nous was uniquely mishandled". It is:
the repository systematically does not retain agent output, this seat is
one measured instance, and in this instance what was lost includes the
seat's death certificate. For a program whose Necropolis does agent
archaeology on exactly this material, the class of loss is the finding,
not this seat's share of it.

WITHDRAWN: a correction this seat had drafted against a sibling.
An earlier draft of this file "corrected" roles/Coeus/ARCHAEOLOGY_2026-09-11.md
and the MONITORS.md CoeusRebuildTrigger row, which both state that Nous
has not run since 2026-03-27, to 2026-04-02. THAT CORRECTION IS
WITHDRAWN. Coeus read the repository, from a worktree, correctly; with
respect to every tree any other seat can reach, 2026-03-27 IS the last
Nous run. This seat read the canonical checkout's working directory and
mistook one machine's disk for the program's memory. Coeus's statement
stands unamended and no sibling file is edited. What is posted to Coeus,
Archaeon and the Necropolis Keeper instead is section 2's actual finding:
that 4,187 rows and the log exist outside every tree (NOUS-01, NOUS-06).

## 3. What it shipped

VERIFIED TODAY, in the repository (the figures another seat can
reproduce; the disk-only surplus is section 2's business):

    committed corpus                 5,918 rows in 12 run directories
    distinct concepts exercised         95 of 95
    distinct fields exercised           20
    high_potential flagged             719   (12.1%)
    is_unproductive flagged            299   (5.1%)
    largest single committed run     3,030   (20260325_132552)
    committed date range            2026-03-24 .. 2026-03-27

    agents/nous/src/     concepts.py (22 KB), nous.py (28 KB),
                         scorer.py (7 KB), rescore.py (7 KB)
    agents/nous/data/    priority_triples.json (gap-targeted triples,
                         wired 2026-03-28 by 302c002d3)
    agents/nous/configs/ manifest.yaml (provider nvidia, default model
                         qwen/qwen3.5-397b-a17b, auth_env NVIDIA_API_KEY)

The README's "1,500+ evaluated combinations" understates the committed
corpus by a factor of about 3.9 and the disk corpus by about 6.7.

## 4. The instrument, measured against itself

This is the part of the pass that matters. All four measurements are this
seat's own, over its own committed rows, and all four are adverse to it.
Reproduce with `python roles/Nous/science/corpus_audit.py`.

**M1. The novelty classifier does not discriminate.** Over 5,918
committed rows:

    novel          5,462   92.29%
    unproductive     299    5.05%
    unclear          153    2.59%
    existing           4    0.07%

A classifier whose job is to separate "this maps to a known technique"
from "this is new" returned `existing` four times in nearly six thousand.
The README describes novelty as a three-class label and publishes no
chance floor and no control beside it. Under the rule that every metric
needs a payload-reading null and a published chance floor, this label
carried no information and should never have been read as one.

**M2. The ranking key is nearly constant.** VERIFIED TODAY:

    dimension                 n       mean    sd      mode (share)
    reasoning              5,826     7.41    0.532   7  (57.7%)
    metacognition          5,820     6.16    0.997   6  (50.8%)
    hypothesis_generation  5,814     5.97    1.276   5  (32.0%)
    implementability       5,815     7.70    1.626   9  (47.3%)

Three of the four dimensions put roughly half or more of their mass on a
single integer. The composite -- the actual sort key handed downstream --
takes five distinct values (7.0, 6.33, 6.0, 5.33, 7.33) on 91.4% of the
corpus. Ranking by it is close to ranking by ties broken by whatever
prior the concept names carry. In one sampled run (20260327_203534),
"Property-Based Testing" occupies 9 of the top 20 rows.

**M3. The key does not separate the scorer's own reject class.** The 299
committed rows the scorer itself flagged `is_unproductive` do not score
below the 5,619 it did not:

    unproductive   n =   299   mean composite = 6.4696
    productive     n = 5,619   mean composite = 6.4067
    difference                 = +0.0630
    SE of difference           =  0.0493
    z                          = +1.28
    label-permutation p        =  0.308  (2,000 shuffles, seed 11)

The finding is a clean null: the ranking key cannot distinguish the
scorer's own rejects from its own accepts, p = 0.31. A key that cannot
put its own rejects below its own accepts is falsified as a ranking key.

A WEAK SIGNAL THIS SEAT RETRACTED ON ITSELF, recorded because the
retraction is the useful part: measured over the 10,105-row DISK corpus,
the same comparison gives +0.0944, z = +2.76, permutation p = 0.026, and
an earlier draft of this file carried those numbers with a note that the
direction was not to be read pending replication. Restricted to the
committed corpus the effect evaporates (p = 0.31). The doctrine that
forbids reading a marginal number before its replication has run is what
stopped a 2.76-sigma artifact of an uncommitted data surplus from being
written down as a directional claim. The null, not the sigma, is what
this seat reports.

**M4. There was never a control of any kind.** No negative, no positive
and no cheat control exists anywhere in agents/nous/. VERIFIED TODAY by
the audit script, which prints all 8 keyword hits in the source so a
reader can judge them: every one is a concept NAME in the dictionary
("Feedback Control", "Optimal Control", "Adaptive Control"), not a
control arm. There is no content-free-string arm, no shuffled-concept
arm, no repeated-triple arm establishing rater self-consistency, and
nothing held out. The four ratings, the composite, the novelty label and
the high_potential flag were all produced by the same model that wrote
the text being rated, in the same call, with the rating format appended
to the generation prompt. There is no independent oracle anywhere in the
loop. Eos's 2026-09-11 pass found its own old scorer giving a
content-free string 100/100 (CITED, commit 9b908b8f5); Nous never ran the
experiment that would have found the equivalent here.

## 5. The claim/method mismatch in the README

Base rule 5: a seat's own stale documentation is a defect. Found today:

- `agents/nous/README.md` states implementability is "the only dimension
  Coeus found to predict forge success (weight +0.221)" and that the
  other three carry "weight 0.000". The shipped
  `agents/coeus/graphs/causal_graph.json` score_dag records
  implementability at **-0.4670**, metacognition +0.4819 and
  hypothesis_generation +0.5708 (CITED from Coeus's own archaeology
  section 3, D1, which found the same sign flip from the other end of the
  seam). Nous's README repeats a number whose shipped value has the
  opposite sign, and the scorer's entire design rationale rests on it.
- The README advertises "Out of 1,500+ evaluated combinations, roughly
  20-30% score high enough to warrant forging." Measured on the committed
  corpus: 5,918 evaluated, 12.1% high_potential. Both halves are wrong.
- The README's Coeus-weighting table cites Active Inference at forge
  effect +0.69 and Topology at -0.21; the shipped artifact reads +0.2007
  and -0.0563 (CITED, Coeus D1).

Not established: which run any of the README's numbers came from, or
whether an artifact matching them was ever committed. The honest
statement is that Nous published a description of its scoring rationale
that does not match the artifact it cites, and left it standing for five
and a half months.

## 6. The old queue, classified against the north star

Classes: STILL_LIVE, NEEDS_REPREMISE, PARKED, SUPERSEDED, TRANSFERRED,
RETIRED. Only STILL_LIVE is executable. Nothing below is marked dead;
residue, weak signals and gradients stay navigable.

  item                                      class            note
  ----------------------------------------  ---------------  ---------------------------------------------------------
  Generate cross-domain triples and rank     NEEDS_REPREMISE  The ranking channel is falsified by M2 and M3. Generation
  them by model self-rating for the forge                     itself is NOT falsified -- it was never tested against a
  queue                                                       control. Needs an independent oracle and a live consumer
                                                              before it can be re-premised; both are absent.
  The 4,187 uncommitted rows and nous.log    STILL_LIVE       Section 2. Preservation is executable today and needs no
                                             (preservation)   decision: they are one `git clean` from gone and they are
                                                              the seat's only death record. NOUS-01.
  The committed 5,918-row scored corpus      STILL_LIVE       Retained as residue AND proposed as a calibration fixture
                                             (as a NULL)      (RESPONSIBILITIES section 4): a measured floor any future
                                                              proposal scorer must beat, not a hypothesis source. A
                                                              re-purposing, not a resumption.
  Coeus-weighted sampling (3.0x / 0.3x /     SUPERSEDED       The weights derive from concept_scores.json, falsified by
  0.5x / 2.0x multipliers)                                    the Necropolis as a forge-calendar fingerprint
                                                              (MEASUREMENT_FAILURE, CITED). Never re-applied as written.
  priority_triples.json gap-targeted         PARKED           The "gaps" were defined by a coverage map of a dead forge.
  triples (wired 302c002d3)                                   Targeting triples at a named gap survives as an idea; this
                                                              gap list does not.
  Novelty classification (novel/existing/    NEEDS_REPREMISE  The IDEA that a proposal can be checked against known
  unproductive)                                               technique is not falsified. The implementation returned
                                                              `existing` 4 times in 5,918 with no control (M1) and is
                                                              unusable as it stands. Same failure family as the
                                                              2026-08-12 ruling that closure-novelty was a timeout
                                                              detector.
  high_potential flag (all three core        SUPERSEDED       A threshold on a key with sd 0.532 on one of its three
  ratings >= 7)                                               inputs. 719 committed rows carry it; it cannot mean what
                                                              it says.
  Continuous unlimited generation loop       RETIRED          Not as a lineage -- as a PRACTICE. A hand-launched infinite
  (--unlimited)                              (the practice)   loop with no freshness record, no dormancy threshold, no
                                                              alarm route and no consumer check is what base rules 7, 8
                                                              and 9 now forbid. Registered DORMANT in MONITORS.md
                                                              (section 7); never relaunched in that form.
  95-concept hand-written dictionary         NEEDS_REPREMISE  A hand-designed prior over which concepts may collide,
                                                              which is the thing the north star warns against supplying.
                                                              Kept as residue; not defended.
  Feedback of forge outcomes into            RETIRED          Both ends are dead: Coeus is MEASUREMENT_FAILURE and the
  sampling weights (the full cycle)                           forge stopped 2026-05-28. Recorded, not resumed.

Executable without any decision: NOUS-01 (preserve the uncommitted rows),
NOUS-02 to NOUS-04 (documentation and instrument repair inside
agents/nous/). Everything else waits on NOUS-XL-01.

## 7. Where this seat sits relative to the Necropolis finding on Coeus

Coeus was autopsied 2026-09-10 with disposition MEASUREMENT_FAILURE: its
shipped scores were the forge CALENDAR fingerprinted through which
concept batches happened to be forged when (CITED,
engine/necropolis/dossiers/coeus.dossier.json on origin/necropolis/coeus;
not re-derived here).

Nous is one hop UPSTREAM of that finding, and the two are the same
failure at two hops:

    Nous   manufactured the INPUT variable with no independent oracle
           (one model generating and rating in a single call)
    Coeus  regressed a contaminated OUTCOME variable and never held it
           out along the time axis the instrument changed on

Coeus's kill does not depend on Nous's defect and is not weakened by it.
But the descendant experiment `coeus-d1-frozen-judge-structure-test`
asks whether concept identity predicts forge outcome under a frozen
judge, and CONCEPT IDENTITY IS NOUS'S VARIABLE. If it is ever dispatched,
the concept indicators it regresses come from a dictionary this seat
hand-wrote and a sampler this seat biased (80% cross-field, then Coeus
multipliers up to 3.0x), and the forge-outcome rows it would need may be
partly among the 4,187 that never reached the repository. That is a
design input its owner should have. It is posted to the Keeper
(Mnemosyne) and to Coeus on this pass (NOUS-07). This seat proposes
nothing about that experiment and does not ask to be part of it.

This seat has NOT been autopsied: no Necropolis dossier for Nous exists
on main (VERIFIED TODAY). Nous therefore carries no conflict-of-interest
bar against measuring its own instrument, and every measurement in
section 4 is adverse to it -- findings that cut against the finder are
the only class a conflicted party may report, and they are all this seat
reports.

## 8. The standing loop, registered

`python agents/nous/src/nous.py --unlimited` -- hand-launched continuous
generator, batches of 500, 2.0 s inter-call delay, checkpoint every 10.
No scheduled task, service, daemon or pid file has ever existed for Nous
(VERIFIED TODAY: nothing in agents/nous/ writes one).

Registered on this pass as **NousGeneratorLoop, DORMANT** in
roles/base-role/MONITORS.md. Its input (the NVIDIA NIM endpoint) is
PRESENT-UNVERIFIED: prometheus_llm/registry.py records the provider live
as of 2026-08-22 for `meta/llama-3.1-8b-instruct` and
`deepseek-ai/deepseek-v4-flash-0731`, and warns that most of the 102
listed model ids 404 for this account. NEITHER model Nous actually used
(`qwen/qwen3.5-397b-a17b`, `nvidia/nemotron-3-super-120b-a12b`) was
probed today, by operator scope limit. Its output consumer (Coeus, then
the forge) is DEAD since 2026-05-28. It is not relaunched.

## 9. What was NOT examined today

- `agents/nous/src/nous.py`, `scorer.py`, `rescore.py` and `concepts.py`
  were NOT read line by line. Section 4's measurements read the OUTPUT
  rows, not the code that produced them. The scorer's regex extraction
  path in particular was not audited, so the 153 `unclear` rows and the
  ~100 rows missing an implementability rating are NOT attributed between
  model behaviour and parse failure (NOUS-03).
- No API call was made. Whether either model Nous used still answers for
  this account is UNKNOWN (operator scope limit: bootstrap and
  registration only).
- The 5,918 response TEXTS were not read or sampled. No claim is made
  about their content or quality -- only about the scores attached to
  them.
- Whether any forged Hephaestus tool traces to a specific Nous triple was
  NOT established; the forge ledger was not joined to the corpus
  (NOUS-05).
- The Coeus dossier's numbers are CITED, not verified; its three attack
  scripts were not run.
- `agents/nemesis/` was confirmed to exist and was not opened.
- The reference-class scan in section 2 counted FILES and BYTES only. It
  did NOT determine whether any other seat's ignored files are results or
  scratch; that read belongs to each seat that owns them. The 64% figure
  is "directories holding ignored files", not "directories that have lost
  results".
- The seven run directories holding no responses.jsonl were counted, not
  diagnosed.

## 10. Reproducing every number in section 4

    python roles/Nous/science/corpus_audit.py           # the full report
    python roles/Nous/science/corpus_audit.py --check   # exit 1 on drift
    python roles/Nous/science/test_guard.py             # the D-23 guard's
                                                        # positive and
                                                        # negative controls

The script refuses to run from the canonical checkout (D-23 s1) and that
refusal is itself tested, in both directions, by test_guard.py: the guard
must REFUSE the canonical checkout and ACCEPT a linked worktree. Both
pass at 363120e08. An instrument that cannot demonstrate it is able to
fail is not an instrument (base rule 3).
