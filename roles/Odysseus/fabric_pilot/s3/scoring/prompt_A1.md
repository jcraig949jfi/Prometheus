You are a blind quality scorer for research reports about the Prometheus research repository. You receive several
reports, each labelled X###. They come from different sources, and you do not know which. Score each report
independently against the rubric below. Do not try to find out where a report came from: do NOT search the
repository for a report's own sentences, title or label. Only verify the evidence its claims cite.

Tools: Read, Grep and Glob inside the repository, and `rogit` for git history (a single command, used exactly like
git).

Rubric (frozen, S3_PROTOCOL s5). Score each item 0, 1 or 2:
1. EVIDENCE: are the load-bearing claims tied to checkable primary evidence (path:line, commit:path, data)?
   0 = mostly unsupported, 1 = partly, 2 = consistently.
2. CORRECTNESS: pick the 3 highest-stakes claims and verify them in the repository yourself.
   0 = a load-bearing claim is false, 1 = unverifiable or partly true, 2 = all 3 verified true.
   Name the 3 claims and what you found.
3. ANSWERS THE QUESTION: does it answer what it set out to answer, or state precisely why it could not?
   0 = no, 1 = partly, 2 = yes.
4. LIMITS STATED: does it say what was not checked and what would change the conclusion?
   0 = no, 1 = partly, 2 = yes.
5. USABLE: could a research principal act on it without redoing the work?
   0 = no, 1 = with significant rework, 2 = yes.

Write `scores.json` in your output directory:
{"<label>": {"evidence": n, "correctness": n, "answers": n, "limits": n, "usable": n, "total": n,
             "checked_claims": ["claim -> verified/false/unverifiable, with path:line"], "notes": "one or two sentences"},
 ...}
Finish with one line per report: `<label>: <total>/10`.


---------------- THE REPORTS ----------------


======== REPORT X001 ========

REPORT -- one memory certificate applied to another engine's specimen

1. WHAT I SET OUT TO TEST

The program has three instruments that each claim to certify "history is kept and causally used". They are [redacted]'s public P1/P2 certificate, [redacted]'s LM01 and [redacted]'s SI01. I asked two things. First, do they return compatible verdicts on the same specimen? Second, which committed specimens could all three be run on? Only one of the three can actually be run today, so I did the cheapest discriminating part. I applied the [redacted] P1/P2 v3 certificate, unchanged, to [redacted]'s evolved M2 specimen. M2 is a HOLD memory which [redacted]'s own tests place "in packets in flight, not in site state". I ran it under two declared system boundaries: B1 declares site state + inbox + in-flight packets, and B2 declares site state only. The question was whether the certificate agrees with [redacted]'s own tests, and whether the verdict is set by the boundary the adapter author declares.

2. WHAT I DID

Code and data were exported with git archive into [redacted] Nothing was run against the clone.
- [redacted] certificate: prometheus/[redacted]/c3/{certify,system,task,probe,calib}.py @940b486f2, unchanged. Rule v3: 49 permutations, p <= 0.02, P2 = 3 bootstrap SE, 2000 training and 3000 test episodes.
- [redacted] engine: prometheus/[redacted]/*.py @cc98596dd. This is identical to main except for lens.py.
- The M2 specimen is cell 4ab2ba014aac967e. Its champion genome, physics and environment come from roles/[redacted]/pte/c1_rows/cells.jsonl.gz @b91f522ae.
- The physics is a ring of 144 sites with synchronous wake every 2 ticks, and the in-flight mailbox ring has length 8. The environment is HOLD with cue_len 2 and gap 8.
- New code, all in [redacted]
  - adapter.py: a [redacted] System around the [redacted] engine.
  - run_cert.py: the certification driver.
  - ka_check.py and ka_adapter.py: known-answer checks.

How the adapter maps a [redacted] episode (V=2, k=8) onto one HOLD trial run from a fresh world:
- The cue takes 2 engine ticks at +/-256 on the actuator site.
- Each distractor takes 1 tick at +/-64.
- The query takes 1 silent tick, which is the HOLD readout tick.
- The readout features are a one-hot of sign(S0) at the actuator, which is [redacted]'s own readout.
- The engine's counter-based RNG gets a fresh world seed per step from the harness's noise(), so the two rows of a P2 pair share every random draw.
- The C3 harness swaps every array in the state dict at t=k. Carriers outside the declared boundary are therefore kept outside the dict: they are neither swapped nor probed.
- full_state is the declared arrays, with sites re-indexed relative to the actuator (the ring is translation-symmetric). Columns that are constant within a batch are dropped, which loses nothing for a linear probe.
- "phase" is the engine tick parity at which the episode starts. Phase 0 reproduces trial 0 of [redacted]'s episodes.

Runs:
- ka_check.py: [redacted]'s own evaluate() on the 64 held worlds for the normal, flush_inflight, flush_inflight_late, reset_S, reset_all_nonpacket and zero_comm arms.
- ka_adapter.py: the same arms re-created through the adapter (flush after step 5 = mid-delay, flush after step 8 = the tick before readout, zero_comm), at phases 0 and 1, 2000 episodes each.
- run_cert.py PV|NZ seeds 6-10: the [redacted] planted sanity systems on the same V=2, k=8 task.
- run_cert.py B1 seeds 6,7,8 (phase 0) and B2 seeds 6-10 (phase 0).
- run_cert.py B2 seeds 6,7 at phase 1.
- Outputs are in out/*.json and out/log_*.txt.

3. RESULT

Known answers:
- [redacted]'s own run reproduces the committed held accuracy exactly: 0.8828. flush_inflight gives 0.497, zero_comm 0.500, reset_S 0.883 (unchanged), reset_all_nonpacket 0.863, and flush_inflight_late 0.845.
- Accuracy per trial alternates with the tick parity at which the trial starts: about 0.72-0.84 on even starts and 0.92-1.0 on odd starts. The trial period is 13 ticks and sites wake every 2 ticks.
- Through the adapter:
  - Phase 0: normal J = 0.736 (matches trial 0 = 0.72), flush mid-delay 0.50, flush just before readout 0.68, zero_comm 0.50.
  - Phase 1: normal 0.959, flush mid-delay 0.51, flush just before readout 0.959 (no effect), zero_comm 0.50.
- The adapter therefore reproduces [redacted]'s known answers.

Certificate, unchanged v3 rule:

| System | Seeds | Class | P1 D (bits) | P1 p | P2 effect (+/- SE) | Notes |
|---|---|---|---|---|---|---|
| M2, B1, phase 0 | 6, 7, 8 | FUNCTIONAL 3/3 | 0.80-0.81 | 0.02 | 0.45-0.47 +/- 0.009 | J 0.73 -> 0.27 |
| M2, B2, phase 0 | 6-10 | PASSIVE 5/5 | 0.83-0.85 | 0.02 | exactly 0.0000 | J_ablated = J_intact |
| M2, B2, phase 1 | 6, 7 | FUNCTIONAL 2/2 | 0.98 | 0.02 | 0.92 +/- 0.005 | |
| PV | 6-10 | PASSIVE 5/5 | | | | sanity as expected |
| NZ | 6-10 | 3 FUNCTIONAL, 1 INDETERMINATE (p=0.04), 1 INCOHERENT (p=0.30) | | | about 0.04 in all 5 | P1 gets weak at k=8 |

Plain conclusion:
- On this specimen the [redacted] certificate agrees with [redacted]'s tests once the boundary is declared. B1 is FUNCTIONAL and B2 is PASSIVE at phase 0, which is the pre-stated "agree" outcome. No INCOHERENT result occurred on M2: the linear P1 probe decodes the cue from the declared state.
- Two qualifications change how that should be read.
  - (a) The verdict is set not only by the declared boundary but also by the moment of the swap relative to the engine's wake cycle. With B2 fixed, starting the episode one tick later flips the verdict from PASSIVE to FUNCTIONAL. At phase 1 the cue has been written back into site state by the tick before readout, which is consistent with [redacted]'s own flush_inflight_late being harmless there. So "the memory is in packets, not site state" is true at mid-delay but not at every tick. The certificate's fixed swap time t=k samples only one tick.
  - (b) P1 held under both boundaries, including B2 where the cue's carrier is excluded. P1 probes at t=k+1, after the readout tick, so the state that holds the system's answer already contains the cue. On this task P1 does not locate where the memory is carried; only P2 discriminates.
- The second part of the question (which committed specimens all three instruments could be applied to) has the answer "none today". LM01 is frozen but not launched, and its world is tensor completion with no cue-delay-query episode. SI01 has a directive but no prereg and no code. Only the [redacted] certificate exists as runnable code, so no three-way comparison is possible.

4. DID IT RESOLVE THE QUESTION

Partly.
- The cheapest discriminator is resolved for the [redacted]-on-[redacted] pair. The dependence on the boundary was confirmed, and a second hidden degree of freedom was found (the wake phase at the swap time).
- The three-way compatibility question cannot be resolved with committed inputs: two of the three instruments have no runnable implementation.
- B1 was run on 3 of the 5 planned seeds because of the CPU budget. All 3 agree, with P2 z around 50, so the missing seeds are very unlikely to change the class.

5. CONSEQUENCES

- Positive result / reproduction: the adapter reproduces [redacted]'s known answers, and the certificate agrees with them under a declared boundary. The adapter ([redacted]) is a reusable tool for putting [redacted] specimens under the [redacted] certificate.
- Instrument caveat (for [redacted], and for anyone proposing this as the common ruler):
  - A verdict must name the boundary AND the swap tick, since the carrier can move between packets and site state within a trial.
  - A single fixed swap at t=k is not enough for engines with periodic update. Sweeping the swap over the delay would be the natural amendment.
  - P1 at t=k+1 cannot localize memory, because any system that answers correctly meets it trivially.
- Calibration note (for [redacted]): the v3 gate was passed at V=4, k=6. At the V=2, k=8 shape needed here, the weak planted system NZ is not 5/5 FUNCTIONAL (3/5; one INCOHERENT from a P1 miss). The gate's guarantees do not carry over to other task shapes without being re-run there.
- For [redacted]: the statement "memory in packets in flight, not site state" should be qualified. It holds at mid-delay, but at the tick before readout on odd-phase trials the cue is already in site state.
- For the thread steward: LM01 and SI01 need runnable code and a cue-query episode before any cross-instrument comparison. Adding an E class to [redacted] was not attempted.
- Governance: I ran this as a neutral worker using only the public certificate code and the committed specimen row. I did not contact [redacted] or [redacted] (the channel is frozen), so they should be told.

6. COST

- About 2 hours of my own time.
- About 47 CPU-minutes (roughly 2,800 CPU-seconds), single-threaded, at most one heavy process at a time, peak about 1.6 GB RSS.
- Not done:
  - B1 seeds 9 and 10.
  - B1 at phase 1.
  - A packets-only boundary (B3; implemented in the adapter but not run).
  - A sweep of the swap tick.
  - Any LM01 or SI01 application, since there is nothing runnable.



======== REPORT X002 ========

# REPORT -- can a declared varied / held / observed lens field make engine convergence measurable?

## 1. WHAT I SET OUT TO TEST

The proposal is that if every engine's experiment record declared what it varies and what it observes
(and, in the extended form, what substrate it holds fixed), then convergence between seats -- the known
case being three independent Z80 byte-VM builds made from one directive -- would become detectable
mechanically. I tested three things on real, already-committed experiment records: (a) whether the field
can be assigned reliably at all (two independent annotators agreeing), (b) whether collisions on the
proposed (varied, observed) pair recover the known Z80 convergence and how many false alarms they raise,
and (c) whether adding a held-substrate code changes (b). I did not build an index or modify any
registry; this is a retrospective measurement of whether the field works as an instrument.

## 2. WHAT I DID

- Corpus: 33 preregistration records from 11 seats/engine lines, extracted verbatim (first 24 KB each)
  from the read-only clone: 31 from origin/main @ 6ff2b2f8a and 3 [redacted] records from
  origin/[redacted]/multiday-campaign-2026-09-26 @ ee7a7d954. The full list with paths is in
  corpus_index.tsv; the texts are in corpus/X01..X33.txt. 13 records are Z80-family ([redacted] z80atlas x4,
  [redacted] coupling/multiday/grounding x3, [redacted] envgate/envgate2/census/denovo x4, [redacted]
  z80_threshold x2, which runs on [redacted]'s VM); the rest cover [redacted], [redacted], [redacted] (WTP),
  [redacted] (PTE), [redacted], [redacted]'s SFE campaigns, [redacted] CW01, [redacted], SFE D8, the [redacted]
  kernel and [redacted] natural-induction.
- Codebook (CODEBOOK.md): varied = the seven proposed values (environment, representation, physics,
  organism-boundary, memory, communication, improver) plus none/other; observed = 9 values plus other
  (replication, descent, population-stats, complexity, task-skill, law-invariant, signal-dependence,
  improvement-rate, instrument); held = 10 substrate families (byte-vm, lattice-field, world-graph,
  float-memory, packet-network, neural-swarm, bitstring, code-worker, llm-agent, other).
- Two independent annotators (separate model sub-agents) coded all 33 records from the record text and
  the codebook only. They were not told the engine names, the landscape document, or the ground truth.
  One worked forward and one worked in reverse order. Outputs: annot_A.json and annot_B.json.
- Ground truth for "known convergent": every cross-seat pair of records where both records are Z80-family
  (62 of 480 cross-seat pairs). This is the convergence the source document named.
- Analysis: analyze.py plus an inline follow-up (output in analysis_out.txt). I computed Cohen's kappa
  and flagged-pair recall and precision under three keys: (varied1, observed1), held, and the triple.
- Premise checks: atlas/harvest/archaeon_campaigns.py on origin/main still matches only
  [redacted]/campaignN/, so envgate, envgate2 and z80atlas are not harvested (the premise holds). No
  varied/observed field exists anywhere under atlas/. The named lens-card prototype exists only under
  an excluded path, so I did not read it or use it.

## 3. RESULT

Reliability (n=33, primary code): varied kappa 0.73 (79% agreement); observed kappa 0.74 (79%; the
annotators' code sets overlapped on 100% of records); held kappa 0.76 (82%). The combined (varied,
observed) pair is less reliable: kappa 0.57 (61%). Disagreements cluster where the seven-value varied
vocabulary does not fit. [redacted] "change almost everything" was coded environment by A and physics by
B on all 3 records. PTE C1 was coded communication by A and physics/environment by B. [redacted] and
[redacted] CW01 got memory or none versus representation or environment.

Detection of the known Z80 convergence (62 cross-seat pairs; annotator A / B):

| key                         | flagged | true pos | false pos | recall    | precision |
|-----------------------------|---------|----------|-----------|-----------|-----------|
| (varied1, observed1)        | 25 / 25 | 21 / 14  | 4 / 11    | 0.34/0.23 | 0.84/0.56 |
| any varied & any observed   | 52 / 52 | 34 / 33  | 18 / 19   | 0.55/0.53 | 0.65/0.63 |
| held only                   | 100/ 87 | 62 / 62  | 38 / 25   | 1.00/1.00 | 0.62/0.71 |
| (held, varied1, observed1)  | 21 / 14 | 21 / 14  | 0 / 0     | 0.34/0.23 | 1.00/1.00 |

What the collisions contain:
- Under both annotators, the triple collides only for [redacted], [redacted] and [redacted] Z80 records
  (physics x replication on a byte VM). [redacted]'s Z80 records (environment x descent/replication)
  never collide with any other seat under either annotation.
- So the varied/observed pair does not measure the Z80 triplication as such. It splits it. [redacted]
  and [redacted] (plus [redacted], which reuses [redacted]'s VM) ask the same question on the same
  substrate; [redacted]'s build, on that substrate, asks a different question. This matches the source
  document's own verdict: not distinct as a world, distinct as a method. Here that verdict was reached
  independently by blind coding.
- The substrate (held) is what captures "three builds of one world". It does so with recall 1.00 but
  precision 0.62-0.71. The false alarms are shared generic families, for example several different
  world-graph systems, and SFE D8's stack VM counting as byte-vm.
- Collisions on the pair alone outside the Z80 family (4 for A, 11 for B) are mostly vocabulary
  coarseness: BEE kernel versus WTP (representation x task-skill), and CWE versus PTE (physics x
  law-invariant, B only). One looks like a possibly real overlap nobody had listed: [redacted]'s
  SFE-driven campaign records and [redacted] both code as improver x improvement-rate, under both
  annotators. SFE D8, [redacted] and [redacted] natural-induction all code as improver x task-skill.
- Within one seat, varied is not constant. [redacted] spans environment, improver and none; NPE spans
  physics, environment and memory. The lens is a property of an experiment, not of an engine, so an
  engine-level tag would hide both convergence and divergence.

Plain conclusion: the field can be assigned with substantial reliability, and it does make convergence
measurable, but only as the three-part key (held, varied, observed). The two-part varied/observed pair
alone has 23-34% recall and 56-84% precision on the known case. It cannot see "same world built three
times", because that convergence is in the held substrate, not in the lens. The seven-value varied
vocabulary is the weakest part: most disagreements and most false alarms trace back to it.

## 4. DID IT RESOLVE THE QUESTION

Partly. It settles whether the field is workable (yes, with kappa about 0.73-0.76 per field) and what
it detects (lens convergence, not substrate convergence), on 33 records with one known convergence
case. Four things remain open:
- The ground truth is defined by substrate, which makes the held key's perfect recall partly circular.
  The informative numbers are the pair's low recall and the triple's zero false alarms.
- The annotators were model sub-agents, not the seats. Self-declared tags might agree more, or might
  be gamed.
- There is only one known-convergent case, and 33 records is a small sample.
- I did not test whether "must justify or merge" changes seat behaviour.

## 5. CONSEQUENCES

- False premise, partly: "two engines on the same varied/observed pair must justify or merge" would
  not have caught the Z80 triplication as a whole. It would have cleared [redacted]'s build and flagged
  only [redacted] versus [redacted]. A held/substrate code is needed. Recommend the record carry
  held_substrate plus a concrete substrate_name (implementation path), and that convergence be
  defined on the triple.
- Instrument design fix: the varied vocabulary needs sharper boundaries between environment and
  physics (the CWE and PTE disagreements), a "communication-physics" rule, and an explicit "none"
  for census/instrument records. Declare the field per experiment, not per engine.
- A candidate lead, not verified: [redacted]'s SFE campaigns and [redacted] both test whether an
  improver gets better at improving (improver x improvement-rate), and SFE D8, [redacted] and [redacted]
  natural-induction share improver x task-skill. The seats involved, or whoever owns the cross-engine
  standard, should check whether this is real duplication.
- A known result reproduced independently: [redacted] and [redacted] Z80 work share one lens; [redacted]'s
  Z80 work is methodologically distinct.
- Premise confirmed: the Atlas harvester still does not index envgate, envgate2 or z80atlas, and no
  lens field exists in atlas/. Whoever owns Atlas and the cross-engine contract should know. The
  artefacts (CODEBOOK.md, annot_A/B.json, analyze.py) are a ready-made pilot for that standard.

## 6. COST

About 45 minutes of my own time. Local CPU was negligible (well under 1 CPU-minute; git extraction and
a pure-Python analysis). Two annotation sub-agents ran concurrently for about 5-6 minutes each. I did
not use Postgres, did not run any repository code, and did not consult the lens-card prototype (it sits
in an excluded path). Not done: annotation by the seats themselves, a larger corpus (more than 280
prereg files exist on main), a non-substrate-defined ground truth, and any registry change.



======== REPORT X003 ========

REPORT -- Blind batteries and co-adapted generators (Apollo reasoning organism)

1. WHAT I SET OUT TO TEST
Apollo's best organism scores 0.60 (mix-adjusted) on its owner's home battery but 0.0667 on 42
tasks another seat wrote blind. Two questions follow. (a) Is that collapse a property of the
organism, or a quirk of one particular blind author -- i.e. does it replicate when a third,
independent author writes the tasks? (b) The revival review proposes validating any new task
generator by checking that it "reproduces the known blind result" before trusting it. Is that a
workable gate: does it reject co-adapted generators, and does it also reject generators that are
simply broken? I could only test this on Apollo; the other engines named as lenses (NPE Z80
worlds, [redacted], [redacted], BEE z80atlas) have no committed blind-authored battery that I found, so
"do current capability numbers survive" is answered here for Apollo only.

2. WHAT I DID
Code/data exported from the read-only clone at origin/main 6ff2b2f8a (git archive of apollo/src,
apollo/data, apollo/scripts, apollo/cycles/campaign_20260825, roles/Charon/apollo_e9,
agents/hephaestus/src) into work/[redacted]/src; run with GIT_* unset.
 - Reproduction: python3 apollo/scripts/e9_score.py -> raw 0.0476, mix 0.0667, home 0.6000,
   40 abstain / 2 correct / 0 guess. REPRODUCED exactly.
 - Wrote work/[redacted]/gen_blind.py: a third-author procedural generator, 7 categories, 3
   structurally different construction routes per category, 4 candidates, gold computed by
   construction. Written and hash-frozen (gen_blind.FROZEN.sha256) BEFORE reading any Apollo
   operator source, the home generator, the home prompts or the blind author's prompts. Known to
   me: category names, schema, and the two example prompts quoted in the revival review. One
   post-freeze edit: a distractor-collision bug fix (assertion crash), made before reading any
   organism code, re-hashed and logged.
 - work/[redacted]/calib.py: scores the recorded 0.833 organism (KNOWN_0833, same eval path as
   e9_score.py, home-category-mix weighting, E9 tolerance +/-0.15) on 30 batteries of 42 tasks
   (6/category) from each of six generators:
     home_reseed        the home generator (gen_clean_canary_v01.py) with fresh seeds
     home_reworded      home construction + synonym swaps (larger->bigger/greater, etc.)
     home_prefixed      home construction + the lead-in "Question: " on every prompt
     blind_third_author my gen_blind.py
     degenerate_shuffled  INVALID: my prompts with words shuffled (gold unrecoverable)
     invalid_wrong_gold   INVALID: home construction with gold replaced by a wrong candidate
   plus one 420-task battery from gen_blind. Output: calib_out.json.
 - work/[redacted]/leak.py: 100 batteries each at co-adapted fractions f = 0..1 (a task slot is a
   home-construction task with prob. f, else a third-author task). Output: leak_out.json.
 - Read the organism's parse operators afterwards to explain the answers it did give.

3. RESULT
Mix-adjusted accuracy of the 0.833 organism (30 batteries x 42 tasks each):
  generator             mean mix   sd     abstain  guess   passes "reproduce 0.0667 +/-0.15"
  home_reseed           0.600      0.000  0.57     0.00    0%
  home_reworded         0.600      0.000  0.57     0.00    0%
  home_prefixed         0.400      0.000  0.71     0.00    0%
  blind_third_author    0.026      0.027  0.90     0.07    100%
  degenerate_shuffled   0.000      0.000  1.00     0.00    100%
  invalid_wrong_gold    0.000      0.000  0.57     0.43    100%
  (fixed batteries: Charon 0.0667 / 95% abstain / 0 guess; home 0.600)
Third-author n=420: mix 0.022; per category 0 everywhere except transitivity 0.067 and
consistency_check 0.083. Where the organism did fire on my tasks it was at or below chance:
transitivity 4 correct / 16 wrong of 20 fired; consistency 5 / 17 of 22 fired (4 options).
Cause, from source: the transitivity parser only accepts "greater-direction" comparatives
(taller|bigger|...|richer than), silently drops "younger/slower/poorer than" facts, and only
recognises a few superlatives, so it answers from a partial chain.
Leak sensitivity of the gate (pass rate at f = co-adapted fraction):
  f=0.0 100%, 0.1 100%, 0.2 96%, 0.3 72%, 0.4 30%, 0.5 10%, 0.7 0%, 1.0 0%.
Conclusions:
 (a) The collapse replicates with a third, independent author: 0.60 at home -> ~0.02-0.03 blind,
     dominated by abstention (non-recognition). It is not an artefact of one author. Home-number
     fragility is also extreme on the co-adapted side: a single harmless prefix "Question: "
     drops numeric_comparison from 1.0 to 0.0 (0.60 -> 0.40), while synonym swaps inside the
     regex's word list change nothing.
 (b) "Reproduce the known blind result" rejects fully co-adapted generators (0% pass) but
     ACCEPTS every broken generator I tried (100% pass) and accepts generators that are up to
     ~20-30% co-adapted most of the time. Because the calibration target sits at the floor,
     reproducing it is evidence of NOT being co-adapted with this organism, never of being a
     valid task generator. As a trust gate it is necessary but far from sufficient.

4. DID IT RESOLVE THE QUESTION
Partly. For Apollo, yes: its capability number does not survive a different author (now shown
with two independent authors), and the proposed generator-validation gate is shown to be one-sided
with measured leak tolerance. Not resolved: whether numbers from NPE, [redacted], [redacted] or BEE survive
a blind author -- none has a committed blind battery and building one per engine does not fit
this budget. I also did not run the state-injection (parser vs capability) experiment; the
fired-task accuracy above is only a weak hint that the reasoning layer does not transfer either.

5. CONSEQUENCES
 - Reproduction of something known: E9 is reproducible from source and replicates with a third
   blind author (my gen_blind.py is a renewable, frozen, independently authored instrument that
   Apollo/Lexis can use; Lexis's notes say a second blind author was needed for admission of
   their G7 measurement -- this can serve, with the caveat that its author has now read the
   organism source, so future versions are no longer blind).
 - Harness/method defect (new): a generator-validation gate anchored only on a floor-level blind
   result cannot tell an independent generator from a broken one. Any engine adopting "validate
   the generator by reproducing a known blind result" (NPE, [redacted] world generators; [redacted]'s
   replacement for spent sealed universes) needs at least: (1) an independent gold verifier for
   every generated task, (2) a positive anchor -- a solver or organism that should score HIGH on
   the generator and does, and (3) a profile check (abstain/guess shape, per-category), since a
   single mix number within +/-0.15 cannot detect up to ~20-30% co-adapted content at n=42.
   Anchor target results should ideally be mid-range, not at the floor.
 - Who should know: Apollo (revival plan step "X-heldout generator calibrated against the blind
   battery"), [redacted] (counterfeit/X-heldout doctrine), Lexis, and any seat building world/task
   generators (NPE, [redacted], [redacted]).

6. COST
About 1.25 hours of my time. CPU: under 10 CPU-seconds total (all scoring is deterministic
regex/pipeline code); peak RSS ~50 MB; single process. Not done: state injection; blind batteries
for other engines; a positive-anchor solver for my generator (its validity rests on
construction-time gold, spot-checked by hand on 14 tasks, not on an independent solver).



======== REPORT X004 ========

REPORT -- persistence vs equal-information context; portable executable organs

1. WHAT I SET OUT TO TEST

The proposal under test says a persistent, growing library of executable procedures (the Voyager-style skill library) is a distinct scientific object, not just a way of managing context. The cheapest test that could kill it is this: with the same information and the same compute, does keeping acquired procedures as a persistent executable library beat keeping the same experience as raw context (episodes or demonstrations)? A related proposal asks whether acquired machinery can be packaged as "organs" (identity + description + executable payload + retrieval key). Such organs would have to stay useful when the payload is ablated, and when they are moved to another agent or another world. I built the smallest deterministic world without a language model that the proposal itself specifies. I ran the matched-information comparison, a closed-loop version with a late library swap, and the payload and transplant ablations this world can express.

2. WHAT I DID

Sources read (read-only clone):
- The ladder and experiment records in roles/Atlas/proposals/2026-09-21_prior_art_raid/{ENGINE_FIVE_EXPERIMENT_LADDER.md, EXPERIMENTS.jsonl} @ 2c7a19adb.
- The portable-organ section of roles/Chiron/prompts/2026-09-21_synthesis_directive/SYNTHESIS_DIRECTIVE.md @ 9e54a51ce.

No repository code was run, and I found no existing implementation in the repo. The nearest engine branch (origin/[redacted]/compounding-2026-09-27) has no library-vs-context test.

All code is new, in [redacted]
- f50.py: world, controllers, memories (sha256 70a424ac281a...)
- phase1.py: matched-information test (1e6b70b91739...)
- phase2.py: closed loop plus swap and transplant tests (e13820901a64...)
- phase2bx.py: closed loop, context-only arm (e46d4708004e...)
- calib.py: budget calibration
- Outputs: phase1_*.json, phase2_*.json, phase2bx_*.json, p*.log, agg1.py

The world is generated synthetically by this code. No committed data and no holdout were used.

World:
- Tasks transform lists of integers using 14 primitives (rev, sort, inc, dbl, dedup, tail, cums, ...).
- Each world seed draws 10 hidden "motifs". A motif is a 3-primitive sub-procedure that cannot be reduced to 2 primitives.
- A task is a hidden program of 2-3 motifs, plus one extra "glue" primitive with probability 0.5. It is given as 5 I/O examples, and a solution must also pass 5 held-out examples.
- Four world seeds (1-4).

Controller: breadth-first enumeration over a set of tokens (the primitives plus whatever the memory supplies). Candidates that produce identical outputs are pruned. Every arm gets the same hard budget of 20000 primitive applications per task.

Memory arms, all capped at K primitive-tokens (the equal-byte budget):

| Arm | What it holds and how the controller uses it |
|---|---|
| A | nothing (primitives only) |
| B_edit | raw past solution programs, adapted by up to 2 edits ("demonstration adapted in context") |
| B_macro | raw past solution programs, callable whole as tokens ("retrieved demonstrations / whole-fossil reuse") |
| BX | the same raw context as B, but the controller extracts a fragment library from it before searching; nothing persists beyond the raw context |
| D | persistent library: fragments extracted from all history by a greedy compressor that keeps the most token-saving repeated fragments, capped at K tokens |
| D_shuffled | same fragment lengths, random payload |
| D_foreign | library extracted from a different world's history |

Phase 1 (information matched):
- All arms are built from the same 100 ground-truth training programs.
- 40 held-out tasks per seed per condition.
- Recurrence 0 or 0.5 (the fraction of test tasks that repeat a training program on new inputs).
- K in {30, 100, 300, all (~650-700)}.

Phase 2 (closed loop, not information matched):
- Each arm learns only from its own solutions, over 50 one-motif, then 50 two-motif, then 60 three-motif tasks (K=100; BX also at K=300).
- The final memories are then tested on 40 fresh three-motif probe tasks.
- For D, the library is also swapped to empty, shuffled, another lineage in the same world (different task stream), and a lineage from a foreign world.

Commands: `python3 phase1.py 1 2` and `python3 phase1.py 3 4`, run in parallel; the same for phase2.py and phase2bx.py. At most 2 processes at a time.

3. RESULT

Phase 1, recurrence 0 (tasks solved out of 160, summed over 4 worlds; mean primitive applications per task in brackets):

| K | B_edit | B_macro | BX | D | D_shuffled | D_foreign |
|---|---|---|---|---|---|---|
| 30 | 11 | 20 | 31 | 125 (10.0k) | 9 | 17 |
| 100 | 17 | 25 | 67 | 123 | 9 | 17 |
| 300 | 20 | 37 | 131 | 123 | 9 | 17 |
| all | 27 | 31 | 123 | 123 | 9 | 17 |

- A (no memory) solved 20 (18.3k).
- At K=all, BX and D are identical by construction, a sanity check that passed.
- In 3 of 4 worlds, D at K=30 recovered exactly the 10 hidden motifs.

Phase 1, recurrence 0.5, K=all:
- B_macro solved 71/71 repeated tasks against 55/71 for D; overall 92/160 against 127/160.
- Replaying whole episodes wins on exact repeats; the library wins on new combinations.

Phase 2, closed loop (solved per block, summed over 4 worlds; out of 200 / 200 / 240):

| Arm | one-motif | two-motif | three-motif |
|---|---|---|---|
| A none | 196 | 35 | 11 |
| B_edit | 11 | 4 | 1 |
| B_macro | 176 | 50 | 13 |
| BX, raw context K=100 | 184 | 101 | 29 |
| BX, raw context K=300 | 182 | 145 | 91 |
| D persistent, K=100 | 182 | 145 | 101 |

B_edit cannot start from empty memory: two edits from nothing only reach 2-primitive programs.

Probe on fresh three-motif tasks (out of 160):
- D with its own library: 50.
- D with the library swapped: empty 2; shuffled payload 6; other lineage in the same world 28; foreign-world lineage 1.
- Raw-context arms: B_macro 10, B_edit 0, BX K=100 18, BX K=300 46.

Plain conclusion. A persistent executable library beats naive use of the same information in context by a wide margin (125 vs 20-31 at K=30). Almost all of that advantage goes away once two things hold: the controller may extract a library from its own context (BX), and the budget holds about 30 past solutions (K=300). BX then ties or beats D: 131 vs 123 in phase 1, 418 vs 428 in the loop.

What is left of "persistence" breaks into two parts:
- (a) Compression under a byte budget. The library holds distilled information from all of history in K tokens, which raw context cannot do.
- (b) Amortised derivation. Extraction took 0.4-36 ms per task, against about 90 ms of search. That is a modest wall-clock cache, and it does not show in primitive-application units.

Neither part needs persistence as such. Under the ladder's own kill criterion (no advantage at matched information and compute), the rung kills whenever the context arm is allowed to extract. It survives only when the context arm cannot abstract or the byte budget is tight.

Organ findings:
- The payload is everything. A shuffled payload does worse than no memory in phase 1 (9 vs 20), and in the loop swap it is about as useless as an empty library (6 vs 2).
- The swap test collapses competence (50 to 2), so progress in the loop really did depend on the retained structure.
- Moving a library to another agent in the same world works partially (28 vs 50 for the agent's own library).
- Moving it across worlds with different regularities gives nothing (phase 1: 17 vs 20 for no memory; loop: 1/160).
- Description and retrieval-key ablations cannot be expressed here: there is no natural language, and the whole library is always inside the search.

4. DID IT RESOLVE THE QUESTION

Partly.

For a search-based controller without a language model the answer is clear: persistence adds nothing beyond "equal-information context plus an extraction step", apart from compression per byte and caching. Against naive use of context it wins big. The question as posed is therefore partly ill-posed: whether context wins depends mostly on how well the context-using controller can abstract and on the byte budget, not on persistence.

What is still open:
- The language-model case. There, "equal-information context" means a model that may abstract implicitly. That needs a language-model arm, which was out of scope (CPU only, no API).
- Generality. The world deliberately favours libraries: it has discrete, exactly reusable motifs, which is the assumption cost the ladder names itself. The run covers 4 seeds, one compute budget and one world family, where the ladder's promotion gate asks for 2 or more.

5. CONSEQUENCES

- The kill rung is badly posed; Atlas (ladder owner) should know. It should be restated as a per-byte and per-compute comparison that includes an explicit "same raw context + on-the-fly extraction" arm. Without that arm, any library beats a controller that cannot decompose its context, so the rung cannot kill. With it, persistence reduces to compression plus caching. That points to the ladder's memory-forms-per-byte experiment as the informative test. It also supports the ladder's own fallback of making the library a memory component inside an existing engine. Whoever next designs the fifth engine should know too.
- New positive result (small, expected): in a closed loop the retained library carries the competence. The swap collapses it (50 to 2), and a shuffled payload does no better than an empty library. Organs transfer partially between agents in the same world and not at all across worlds. This gives Nyx and Techne a cheap working harness for swap and transplant tests.
- Harness warning: a controller that adapts demonstrations by edits cannot start from empty memory. Using it as the context arm in a closed loop is unfair by construction.
- Design hint: replaying whole solutions beats a fragment library on exact repeats, so libraries should keep whole solutions as well as fragments when tasks recur.
- No defect was found in the program's own code, since none of it was run.

6. COST

- About 1.5 hours of my own time.
- About 39 CPU-minutes: phase 1 ~25, phase 2 ~10.5, context-only loop arm ~2.7, calibration ~1.
- At most 2 processes, under 200 MB RAM.
- Not done: a language-model context arm; a second world family; retrieval-key and description ablations; a test of composition depth on withheld composite tasks; learning curves across budgets; confidence intervals beyond 4 seeds.



======== REPORT X005 ========

# [redacted] -- [redacted] expressivity ceiling; arbitration hash as hidden economics

[redacted]
`5266ccebea3ad5522b7cfa7a07a8718cac113a70` (below: `@5266cce`). No code was
run. All line numbers are at `@5266cce` unless marked otherwise.

## 1. Questions

**H-D3-17.** Is AETH-00's SplitMix64 arbitration law neutral enough that
its stated non-neutrality caveat does not become a hidden "economic law"
(an unmodelled selective force) now that AETH-01 attaches energy stakes
to contests? The source packet calls this a "required pre-campaign
check" (`[redacted]/AETH-01/ASTRA_REVIEW_PACKET.md:94-98`).

**H-D3-18.** AETH-01 has no movement primitive, one active opcode and no
conditional. Which added affordance (movement, conditional, sensing), if
any, is the minimal one? Does leaving out literal movement (D-AETH01-07)
lead to an R6 dead end? Astra's counter-warning is that energy
thresholds already provide conditionals, so a familiar ISA should not be
added (`[redacted]/AETH-01/ASTRA_REVIEW_01.md:217`; the harvest cites :215 at
`5e41c1d67`).

## 2. Method

1. I read the frozen arbitration law, its caveat, and the test plan
   (AETHER_SPEC, AETHER_TEST_PLAN, AETH-00A receipt,
   test_statistical_diagnostics.py).
2. I traced the AETH-01 decisions that reuse the law (D-AETH01-08), the
   adversarial items (#6, #16), the Astra M07 critique, and the repair
   ledger. I checked whether the required "AETH-01-scale stratified
   rerun" was ever run by searching evidence, observatory, tests and
   ops/campaigns.
3. I collected the measured contest statistics from the AETH-01/02 runs
   (contest rate, fan-in, winner persistence, energy-contest share).
4. I derived one exact property of the law from its text. Section 4.2
   gives the proof.
5. For H-D3-18, I read the three AETH-03 physics ladders, the fwd content
   control, amendments A1/A2 (E-008), the research-block synthesis, and
   TH-009.
6. The empirical check that is still missing is written as
   `out/analysis.py`. It was not run.

## 3. Evidence

### 3.1 The law and its caveat

- The winner is the greatest unsigned `priority = M(h3 XOR C(source))`.
  `h0=M(seed^K)`, `h1=M(h0^tick)`, `h2=M(h1^C(target))`,
  `h3=M(h2^field)`, and M is the SplitMix64 finalizer, a bijection.
  Payload never enters. `[redacted]/AETHER_SPEC.md:246-270`.
- The spec makes an explicit non-neutrality caveat: the law is
  "deterministic and order-independent", NOT "statistically neutral",
  and neutrality is to be measured. `[redacted]/AETHER_SPEC.md:296-302`.
- The spec itself lists "coordinate-keyed deterministic arbitration" as
  a time/space-dependent forcing field and a designed asymmetry.
  `[redacted]/AETHER_SPEC.md:358-361`.
- AETH-01 reuses the law unchanged, with the field domain widened to
  0..4 (D-AETH01-08). Its hidden prior is that the caveat now carries
  economic stakes. Its falsifier is an AETH-01-scale stratified rerun
  that finds a bias that "consistently determines who wins scarce
  energy". `[redacted]/AETH-01/DECISIONS.md:161-177`.
- Economic stake: a source always pays WRITE_COST and the attempted
  transfer. Only the winner is credited, and the losers' amounts are
  destroyed. `[redacted]/AETH-01/PHYSICS_SPEC_DRAFT.md:118-130`;
  `[redacted]/AETH-01/FIRST_LIGHT_01_2026-09-22.md:302-313`.

### 3.2 What was tested for neutrality

- AETH-00A diagnostic (tests 20/25): 11 direction-combo strata, N=300
  contests per stratum, a fresh random seed and tick per contest, a
  single target (2,2) on a 5x5 torus, and a Bonferroni family alpha of
  0.01. Result: **0 of 28 cells flagged**, stated as "not a neutrality
  proof". `[redacted]/test/test_statistical_diagnostics.py:1-36`;
  `[redacted]/AETH-00A_RECEIPT.md:135-147`.
  - Limits: the power is low. At N=300 with p=1/2 the per-cell detection
    threshold is roughly |bias| of 0.1. Seeds are drawn fresh per
    contest, so the test does not probe the fixed-seed trajectory
    process. It also has no energy field and no wrap-edge targets.
- The AETH-01-scale rerun (ADVERSARIAL #16, D-AETH01-08, M07) is named
  repeatedly as required and "not executed":
  - `[redacted]/AETH-01/ADVERSARIAL_ANALYSIS.md:175-183`
  - `[redacted]/AETH-01/REPAIR_LEDGER_01.md:494-505`
  - `[redacted]/AETH-01/AETH01_REPAIRED_FREEZE_CANDIDATE.md:72-75`
  - `[redacted]/AETH-01/PHYSICS_SPEC_DRAFT.md:214-218`

  A search of `[redacted]/AETH-01/evidence`, `[redacted]/AETH-03/evidence`,
  `[redacted]/observatory`, `[redacted]/test` and `ops/campaigns` for
  arbitration-bias / win-rate / neutrality found only the AETH-00A file.
  **The required pre-campaign check was never performed.** This confirms
  the harvest's "later evidence: none found".

### 3.3 Measured contest facts in AETH-01 (B-balanced v1)

- Contests are rare: 1.65-1.80% of targeted template fields and **0.56%
  of energy targets** have 2 or more contenders.
  `[redacted]/AETH-01/AETH02_CALIBRATION_2026-09-23.md:108-114, 130-139`.
- Contests are almost all two-way. Fan-in is 0 or 1 at 98.4% of (site,
  field) slots, 2 at 1.6%, 3 at about 20 per million, and 4 once in the
  whole run. `[redacted]/AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md:212-214`.
- Winner persistence equals chance. "Same contested winner (S4) vs 1/k"
  is 0.50 vs 0.50 for v1; the `hys` control reaches 0.97 by
  construction. `[redacted]/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md:415`.
  A fixed-seed fixture shows both winners across 30 ticks.
  `[redacted]/AETH-01/KILL_GATES_01.md:292-296`.
- Slot usage is near uniform (spread 0.22-1.91% of the mean). This
  counts all edges, mostly uncontested, so it is not a contested-win
  statistic. `NATIVE_CIRCUITRY_01_2026-09-24.md:210-212`.
- Persistent edges are never contested (0 of 1,754).
  `NATIVE_CIRCUITRY_01_2026-09-24.md:267-271`.
- Hash keys are state-free and identical in both twins. Which
  contenders are valid is a radius-1 state fact, so arbitration opens no
  hidden causal path. `[redacted]/AETH-03/PROPAGATION_ASSAY_AUDIT.md:38,
  44-51`.
- "Quenched arbitration" (tick removed from the hash) was rejected
  precisely because it would impose a fixed hash landscape.
  `PHYSICS_DESIGN_01_2026-09-26.md:459-463`.
- Operating guidance: do not redesign the hash merely because it is not
  perfectly neutral; first separate a measured defect from a general
  caveat. `[redacted]/AETH-01/ASTRA_REVIEW_01.md:292`.

### 3.4 Expressivity ladders (AETH-03)

Status of each affordance class:

- **Explicit conditional (`cnd`)**: opcode 0x02 writes only if the
  target's low 2 bits match a key.
  - Evidence: the opcode persisted (share about 0.50), but the lattice
    froze further (0.961 vs v1 0.927 frozen). **KILLED K-b.**
    `PHYSICS_DESIGN_01:324-338, 405-433`.
  - In combination, `rcv_cnd` P_sust 0.016 is **ADDITIVE_OR_LESS**.
    `PHYSICS_DESIGN_03:173`.
- **Energy-threshold conditional / internal sensing (`str`)**: direction
  = (arg0 + energy>>6) mod 4.
  - Evidence: alone it is KILLED K-b (0.940 frozen).
  - `rcv_str` passes N1 (0.109) by one origin. Amendment A1 sets
    **UNRESOLVED** (`PHYSICS_DESIGN_03:252-284`). A2/E-008: the horizon
    matters (new generation after tick 2,000 in 6 of 32 origins)
    (`:286-...`).
  - The synthesis calls it "activity re-routes activity", performing the
    conversion that noise performed.
    `RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md:30-37`.
- **Receipt sensing (`rcv`)**: a written site fires once.
  - Evidence: the only single-change propagator (P_sust 0.047, radius
    11). **UNRESOLVED**, and later "retain as calibration" because it
    encodes its own relay. `PHYSICS_DESIGN_02:231-240, 356-368`;
    `SYNTHESIS:19-25`.
- **Accumulation (`add`) with receipt**: `rcv_add` shows NEW_BEHAVIOUR
  via N1 (0.172, every seed). It stores traces of activity; it is not
  content transport. `PHYSICS_DESIGN_03:164-175, 205-213`.
- **Conservative movement (`mov`)**: the winning source's payload is
  cleared, so the byte moves.
  - Evidence: **KILLED** (K1 local, K2 mechanical). 41% of differences
    die. `PHYSICS_DESIGN_02:47-58, 219-221, 341-343`.
- **Non-conservative content forwarding (`fwd`)**: a receipt-activated
  site re-emits the received byte.
  - Evidence: run as a positive control. **E-P1 FAILED** (3.1% preserved
    content at generation 5 or more). 92% of deep differences were
    altered, and a fixture passes 21/21, so the soup plus the XOR
    signature are confounded. `PHYSICS_DESIGN_03:118-135, 183-188,
    218-222`.
- **Literal relocation of the whole (opcode,arg0,arg1,payload) tuple**:
  **never built.** D-AETH01-07 excludes it, and its reversal trigger is
  "the traveling-structure case is UNRESOLVABLE even with full provenance
  and intervention". That was never evaluated, because no heredity
  detector exists. `DECISIONS.md:141-158`; `REQUIREMENTS.md:14, 22`.

Program state: the single-change search is retired. The next gate is the
frozen medium (TH-009: template turnover without noise), described as
"plausibly upstream" of content transport (TH-008).
`RESEARCH_BLOCK_SYNTHESIS_2026-09-27.md:114-135` (row :121); `ops/threads/TH-009.md:7-15`.

## 4. Result

### 4.1 H-D3-17: answer

**Not empirically settled. The required check was never run.** However,
the committed law plus the measured contest statistics bound the concern
tightly for the AETH-01 v1 / B-balanced regime.

### 4.2 An exact property (derived here from AETHER_SPEC.md:246-270; not stated in the repo)

(a) For a fixed (seed, target, field), the map tick -> h3 is a
bijection of uint64. It is a composition of XOR-by-constant and M, each
invertible.

(b) For any bijection M and any two distinct source codes a and b, with
h uniform on {0,1}^64:

    P[M(h^a) > M(h^b)] = 1/2 exactly.

Proof: substitute h' = h^a^b, which is also uniform. That swaps the two
events. They are disjoint (M is injective and a != b) and exhaustive, so
each has probability 1/2.

(a) and (b) together: over the full tick domain, **every fixed two-way
contest pairing is won exactly 50/50, for every seed, target, field and
direction pair.**

Because 99.998% of contests are two-way (sec. 3.3), there is **no
systematic, trait-linked advantage in AETH-01's actual contest ensemble
to first order**. This includes direction, which is heritable through
arg0. The hash cannot act as a consistent selective force in two-way
contests. What remains is:

- **(i) Finite-window quenched fluctuation.** Within a campaign of about
  1e4-1e5 ticks at one seed, a given pair's win share differs from 1/2
  by a deterministic amount. For a good mixer it is binomial-sized
  (about 0.5/sqrt(n)), which acts like drift, not selection. This is
  ADVERSARIAL #6's "hidden forcing field", and its size is unmeasured.
- **(ii) Three- and four-way contests.** These are not covered by the
  symmetry argument, but they are about 20 per million slots.
- **(iii) Correlations.** These include tick-lag, cross-field,
  cross-target and cross-domain with Mu/Rho (M07). Only lag-1 winner
  persistence has a measurement (S4 = 0.50).

The economic effect is further diluted: only 0.56% of energy targets
are contested.

The genuine "economic law" in this area is **not the hash**. It is the
designed, identity-blind loser-pays-and-energy-destroyed rule. That rule
penalises contest participation and is openly specified (the FIRST_LIGHT
I4 energy leak). It is not hidden.

**Verdict:** "hidden economic law" is **unlikely to be material at
AETH-01 v1 stakes, by argument (high confidence for two-way contests over
the full period; moderate for finite windows)**. It is **formally
unverified**. The D-AETH01-08 falsifier remains open, and the "required
pre-campaign check" is outstanding. `out/analysis.py` specifies it.

### 4.3 H-D3-18: answer

The evidence does **not** support adding an explicit conditional/branch
opcode as the minimal affordance.

- `cnd` froze the lattice and was additive-or-less with `rcv`.
- Consistent with Astra's warning, the only conditional-like mechanism
  that contributed anything is an **energy-threshold** one (`str`), and
  only in interaction with `rcv`. Its status is UNRESOLVED, and the
  horizon matters.
- The affordance that produced reach is **receipt sensitivity** (`rcv`:
  being written changes what you do). It propagates timing, not content,
  and partly by definition.
- Its super-additive partners (`add`, `str`) give "history matters"
  effects, not transport.

On movement:

- **Conservative** movement (`mov`) is actively anti-propagating.
- The harvest's "no non-conservative movement primitive has been tried"
  is **partly inaccurate**. `fwd` is non-conservative content forwarding.
  It was run only as a positive control and failed its bar in a rich soup
  (an instrument confound is recorded).
- **Literal whole-tuple relocation has never been built.**
- Whether excluding movement forces an R6 dead end is **undetermined**.
  D-AETH01-07's reversal condition presupposes a heredity/provenance
  detector that does not exist.
- The program's own reading places the binding constraint upstream, in
  the frozen medium (TH-009), not in movement.

Ranking of minimal additions supported by committed evidence:

1. Receipt/activation sensitivity combined with an existing integrator or
   energy steering. These are interactions, not new ISA.
2. Movement: open; the conservative form is counter-indicated.
3. An explicit conditional opcode: counter-indicated.

## 5. Limits

- All ladder results come from one energy regime (B-balanced), 128^2,
  about 4 seeds, horizons of 400-10,000 ticks, and a one-bit-twin
  propagation assay. None of it is a heredity or R6 test. The
  synthesis's "energy / parameter regime: open" row applies.
- The sec. 4.2 result is a proof I derived from the spec text. It is not
  a repository claim. It assumes the implementation matches the spec,
  which is supported by the golden vectors and oracle parity (AETH-00A/B
  receipts). It does not address finite windows.
- The contest-rate and fan-in figures come from single AETH-01/02 runs.
  The arity mix could change in denser regimes or under new laws (e.g.
  `rcv` raises activity). Under such a law, three- and four-way contests
  would matter more.
- The AETH-03 variants `hys` (and any future law) change arbitration.
  The conclusion applies to the unmodified law only.
- Harvest line cites were made at `5e41c1d67`. The counter-warning now
  sits at `ASTRA_REVIEW_01.md:217` (the harvest has :215).

## 6. What would change the conclusion

- **H-D3-17 toward "material hidden law":** `analysis.py`, run at
  `@5266cce`, would have to find any of the following:
  - (A) a Bonferroni-significant directional deviation in fixed-seed
    trajectories, in a stratum that actually occurs (two-way), exceeding
    δ=0.005;
  - (B) a per-pair dispersion index clearly above 1 (a quenched positional
    advantage beyond binomial);
  - (C) significant lag or cross-field winner association;
  - or a campaign regime whose three/four-way share is above about 1%
    together with a detected k-way bias.

  Any one of these would trigger D-AETH01-08's reversal.
- **H-D3-17 toward "closed":** the same script reports no flags, CI
  half-widths below δ, and dispersion consistent with 1.
- **H-D3-18:** Several results would change this answer:
  - a built tuple-relocation law passing the preregistered
    propagation/content gates;
  - a value-provenance detector (the synthesis's named instrument gap)
    re-scoring `fwd`/`mov`;
  - a demonstration that the traveling-structure case is unresolvable
    (which would trigger D-AETH01-07's reversal);
  - a TH-009 result showing turnover without noise.

  If `cnd` were re-tested on a non-frozen medium and became super-additive,
  that would reopen the conditional question.

