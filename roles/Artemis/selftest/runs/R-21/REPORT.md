REPORT -- evaluator gaming: base rate, time to exploit, isolation design, grader ownership
==========================================================================================

1. WHAT I SET OUT TO TEST
-------------------------
The question had two parts. First: when selection runs against an evaluator, how often does it find a way to raise
its score without the intended capability, and how quickly (in evaluations or updates)? And does the answer depend
on how the evaluator is isolated? The three designs were a separate test episode with fixed inputs, a separate test
episode with randomised inputs, and an in-population comparison of each lineage against its own parent. Second:
in the two "improver-of-improvers" engines (Aphrodite and Ares), is there any route by which the graded party can
influence the grader?

I attacked this three ways:
(a) A census of the exploit-shaped events already recorded in the repository, to see whether a base rate can be
    formed from them.
(b) A controlled measurement on Avida, the classic digital-evolution system where this failure was first
    described. Beneficial mutations are sterilised by one of the three evaluator designs, and I counted how often
    and how fast a population escapes and gains fitness anyway.
(c) A code-level trace of every path from improver output to grader parameters in Aphrodite and Ares.

2. WHAT I DID
-------------
Repository: read-only clone, origin/main @ 6ff2b2f8a. Scratch directory: /home/jcraig/artemis-selftest/work/R-21.
Nothing under roles/Artemis/ was read.

(a) Census. A read-only sweep over origin/main and the origin/* seat branches, excluding Artemis branches.
- Search terms: leak, exploit, cheat, VOID, shortcut, reflex, constant/trivial baseline, shuffled, selection
  bias, max-of/best-of, Goodhart, degenerate, decorative, abstain, clock, METRIC_EXPLOIT, instrument defect.
- I also read every roles/*/calibration LEDGER and CALIBRATION file.
- Event definition: a scored quantity rose through a channel other than the intended capability and was caught
  later.
- Each event was classified as:
  (i) found by selection or search;
  (ii) an instrument or analyst bug that no optimiser exploited;
  (iii) a baseline built by a person (a constant or trivial policy) that passed.
- I checked the four seed citations myself:
  - archaeon/wse/READOUT_v01.md:103-118
  - ares/ARES_CYCLE2_REPORT.md:192-205
  - roles/Aphrodite/science/swarm/RESULTS_2026-09-18.md:50-62
  - the Aphrodite and Ares code paths in (c)

(b) Avida measurement. All inputs are committed.
- Source: ergon/avida2003/artifacts/avida-src-devel-2.2.tar.gz @ 6ff2b2f8a (Avida 2.2), exported with
  `git archive` into scratch.
- The host has no cmake, so I built it by hand with g++ 15 (recipe in BUILD_NOTES.txt). It needed three fixes to
  run at all, all in avida22_r21.patch:
  - g++15 template name-lookup fixes;
  - cMerit::UpdateValue indexes mult[-1] when merit is 0, which segfaulted at startup;
  - cEventList::Process uses an event entry after deleting it. AddressSanitizer found this one.
- I added an env switch R21_ARM that selects the arm:
  - fixed: the sterilisation test runs on the separate test CPU with Avida's fixed test inputs;
  - random: the same test CPU, stock random inputs;
  - insitu: the stock parent-relative check made inside the population when an organism divides; the test-CPU
    path is off;
  - control: STERILIZE_BENEFICIAL = 0.
- Setup, common to all arms:
  - STERILIZE_BENEFICIAL = 1.0 in every sterilised arm;
  - stock genesis except a 30x30 world, with COPY_MUT_PROB 0.0075 and 5% insertion/deletion per divide;
  - stock 9-task logic environment, stock heads ancestor (organism.default);
  - 3000 updates, which is about 220-250 generations.
- Seeds: 6 per sterilised arm (101-106) and 3 controls (101-103).
- Commands: run1.sh ARM SEED 3000, run 2 at a time with xargs -P2; then analyse.py, output in
  analysis_output.txt.
- Escape was defined as the population's mean in-population fitness exceeding 1.10 x the ancestor's fitness at two
  consecutive 50-update samples. The ancestor fitness was F0 = 0.2472, the control median over updates 300-700.
  A secondary measure was the first update at which at least 5% of organisms perform any task.
- Step 0 was desk work: which flag enables the in-population test. I traced this in the Avida 2.2 source:
  source/main/config.cc:401-405, source/cpu/hardware_cpu.cc:1578-1610 and 1733-1790, source/cpu/cpu_defs.hh:17.

(c) Grader ownership. Code read on origin/main and origin/aphrodite/arc3-2026-09-28 @ 7587a93e1. Main files:
- roles/Aphrodite/engine/{engine.py, meta_tribunal.py, fair.py, basis_v4.py, a16.py, a17.py, a18.py,
  tribunal_t4.py, run_meta_development.py, AMENDMENT_3_2026-09-21.md}
- ares/{search.py, substrate.py, cycle2.py, recheck_c2.py, verdict.py}

A sub-agent traced the data flows. I independently re-checked the load-bearing lines:
- engine.py:765-777, where exec runs with `re` in the namespace;
- engine.py:82-89, Escrow.charge;
- engine.py:836-857, run_tasks;
- search.py:291-294;
- AMENDMENT_3:155-165.

I also ran a 3-line exec test, under Python 3.14.4, showing that `re.enum.sys.modules` is reachable from the
restricted namespace.

3. RESULT
---------
(b) Avida, escape from sterilisation of beneficial mutations (3000-update censor):

    arm       runs  escaped  any task ever seen   final fitness / F0     CPU s per run
    control    3     3/3     3/3 (634-838 orgs)   1.70, 7.26, 18.87      55-67
    fixed      6     0/6     0/6 (max 0 orgs)     0.943-0.969            70-75
    random     6     0/6     0/6                  0.942-0.967            71-74
    in-situ    6     0/6     0/6                  0.943-0.967            39-59

- Control time to escape was 1350, 1650 and 2500 updates (about 105-200 generations). Kaplan-Meier survival in
  the control reaches 0 by update 2500.
- In every sterilised arm, Kaplan-Meier survival is 1.0 at the censor (3000 updates, about 250 generations).
- Sterilised arms pooled against control: 0/18 against 3/3, Fisher exact p = 1/1330 = 0.0008.
- One-sided 95% upper bound on the escape fraction within the horizon: 0.39 per arm (0/6), or 0.15 pooled (0/18).
- In the sterilised arms, not a single organism ever performed a task in the population. Fitness drifted 3-6%
  below the ancestor, as expected when deleterious mutations are allowed through and beneficial ones are not.

Plain conclusion for (b): over a horizon about 1.2-2.2 times the unconstrained time to first adaptation, none of the
three designs was escaped. The run therefore cannot rank fixed, random and in-situ, because all three held. The
predicted ordering (fixed escapes first, then random, with in-situ rarely or never) is neither confirmed nor
refuted.

Step 0, which flag enables the in-population test, is resolved for Avida 2.2:
- Any STERILIZE_* value above 0 enables the parent-relative in-population check (config.cc:401-405).
- That check compares the organism's current gestation fitness with its parent's last fitness at divide time
  (hardware_cpu.cc:1578-1610).
- The test-CPU (separate-episode) check runs only if a REVERT_* value or FAIL_IMPLICIT is also set
  (config.cc:395-399). That check always uses random inputs (hardware_cpu.cc:1753).
- So stock STERILIZE_BENEFICIAL = 1.0 on its own is already the in-situ design, not the separate test episode.
- FITNESS_NEUTRAL_RANGE is 0 (cpu_defs.hh:17), so any strict fitness increase counts as "beneficial".
- Consequence: under the in-situ check, every transition from not expressing a task to expressing it is sterilised
  with probability 1. Probabilistic expression, the trick reported against the test CPU, cannot pay under this
  check, because each 0->1 flip in a lineage is caught. That is a structural argument, not a measured one.

(a) Census: 38 recorded events across about 20 seats and engines.
- By class: 21 found by selection or search (2 of them against deliberately planted holes, and 2 borderline
  partial-credit cases); 11 pure instrument or analyst bugs; 5 human-built trivial baselines passing; 1 mixed.
- Caught by: mostly null, shuffled or cheat controls, then human reading and adversarial review. A second
  independent evaluator caught one, and it was the planted case (the Aphrodite evaluation-count counter).
- Latency, where it is stated: usually "within the same cycle or campaign". The outliers were caught 6 weeks to
  about 5 months later: the Nemesis constant-string scorer (about 162 days), Eos substring scoring (about 163
  days), the Harmonia probe ladder (about 6 weeks) and the Hephaestus constant-output tools (months).
- Where a denominator is recorded, exploitation is common whenever a channel exists:
  - Crius: abstention appeared in 6 of 6 C0 runs, exploit lineages in 1 of 9 and 4 of 18 runs in later
    sub-campaigns;
  - Harmonia ASAL: 49 of 105 threshold-crossers were metric exploits;
  - WSE: 1 void leak among 18 cells;
  - Bellerophon coupling: 0 of 90 exploit-probe runs became dominant.
- No recorded event is in an in-population, lineage-relative evaluator design. The designs are held-out sets,
  randomised separate episodes, fixed probes and gate statistics.
- No record states time to exploit in evaluations.

A base rate per isolation design therefore cannot be formed from the repository. The frame of runs without an
exploit is unrecorded for almost every engine, and the designs are confounded with engine.

(c) Grader ownership.
Aphrodite: no path found from the graded party to the grader's parameters in the current slice. The following are
fixed by construction and are not reachable from the candidate:
- the tribunal seeds (a domain-separated hash with no lineage data);
- tribunal construction after freeze, and the thresholds;
- the catalog and sham seeding;
- the selection split.

Three structural weaknesses remain, and the first two are enforced only by the fixed mutation-operator set:
1. The graded artifact computes its own score. run_tasks takes the reported accuracy from the candidate's own
   `evidence.summarise` module and the escrow charge from the candidate's own `allocate.budget`, and
   Escrow.charge does not reject negative n (engine.py:82-89, 836-857). This is closed today only because no
   operator mutates evidence, allocate or memory.
2. The exec "sandbox" runs in-process, and its namespace hands in the `re` module, from which `sys.modules` is
   reachable (verified). Any improver able to emit arbitrary code could rewrite the tribunal. It is safe now only
   because candidate text is assembled from fixed grammar strings.
3. Later assays build their task sets from a previous generation's frozen output. This is by design, symmetric
   across arms and frozen before donors run, so it is not an open path.

A second recursive improver generation exists in code on no branch.

Ares is not an improver-of-improvers: a fixed GA over numeric genomes, with no code execution. It has one open
path from graded population to reported score: search.py:291-294 selects the final champion by argmax on the
held-out seeds. This was diagnosed in the cycle-2 report and is corrected only in post-hoc reporting
(recheck_c2.py); search.py is unchanged. There is also a minor coupling: one RNG drives both mutation and the
training-seed draws. Held-out seeds are fixed.

4. DID IT RESOLVE THE QUESTION
------------------------------
Partly.
- (b) No. The base rate and time to escape could not be separated between designs: 0 escapes in 18 sterilised
  runs, so all three curves are flat at the censor. This does establish that Avida 2.2 is a working, cheap
  substrate for this assay (about 1 CPU-min per 3000-update run), and it fixes the flag semantics. Discriminating
  the designs needs a horizon at least 10x longer, which is beyond this budget (see 6).
- (a) Yes as a census. As predicted, it answers the rate question negatively: the repository cannot yield a rate
  because it does not record its denominators.
- (c) Yes for the current code. It found no graded-to-grader path in Aphrodite, but a policy-only closure that
  would not survive a more expressive improver. It found one known open selection path in Ares that is fixed in
  reporting but not in code.

5. CONSEQUENCES
---------------
Instrument and harness defects:
- Ares search.py still picks the champion on the held-out set. Anyone reusing search.run inherits the
  max-of-128 bias. Fix in code: select on training and report held-out for that champion only. Who: the Ares
  owner, and any seat importing ares/search.py.
- Aphrodite: before any second recursive improver generation is authorised, the grader has to be made
  structurally uninfluenceable, not just protected by policy. Three changes:
  - compute accuracy in the engine from `results`, not from the candidate's evidence module;
  - reject non-positive escrow charges;
  - run candidate modules out of process, or at minimum stop passing the `re` module into the exec namespace.
  Who: the Aphrodite seat and the operator who rules on recursion.
- Avida 2.2 as committed has two latent memory bugs, cMerit at value 0 and a use-after-free in the event list.
  They crash it on a modern toolchain. Whoever runs the 2003 Avida lineage-replay work (ergon/avida2003) should
  take the patch.

False premise, a minor one: "STERILIZE_BENEFICIAL with the test CPU" is not what the stock flag does in Avida 2.2.
The flag alone gives the parent-relative in-population check. Getting the separate-episode arm needs a REVERT_*
or FAIL_IMPLICIT flag as well. Any follow-up that plans arms on stock flags must patch or combine flags as I did.

Clean null (bounded): at about 250 generations, fixed-input, random-input and in-situ sterilisation all fully
suppress adaptation, while controls adapt 3/3. A reusable harness is now in scratch: build recipe, patch, run
script and analysis.

Next informative step: run the same harness to about 30,000-50,000 updates (10-20x longer) with 10+ seeds per arm,
or at a higher mutation rate, and additionally log the number of test-CPU sterilisation events. That costs about
10-15 CPU-hours at the observed about 25 ms per update for the test-CPU arms.

Census: the program should record, per engine campaign, the evaluator design, how many runs had a cheat control,
and how many runs were exploit-free. Otherwise no rate can ever be formed. Who: the calibration-ledger owners in
each seat and whoever maintains the cross-engine failure index (roles/Odysseus/frontier/poi/raw/
I6_failures_reversals.md).

6. COST
-------
Wall time: about 1.5 hours.

CPU, about 53 CPU-minutes in total, within the 1 CPU-hour cap:
- two builds of Avida: about 8 CPU-min;
- two 30x30 pilots of the test-CPU arms: about 18 CPU-min. These were wasted. My first arm switch let organisms
  inside the test CPU recursively trigger the test CPU, making them about 70x slower. I fixed this by enabling
  the test through the config and discarded those runs;
- AddressSanitizer debugging and benchmarks: about 3 CPU-min;
- 21 production runs: about 23 CPU-min.
Peak RAM was about 21 MB per process, and at most 2 processes ran at once.

What I could not do:
- run a horizon long enough for any sterilised arm to escape;
- measure time to exploit in "evaluations" (Avida counts updates; the test-CPU arms evaluate each mutant child
  once, but I did not log that count);
- test modern Avida (devosoft) flag semantics, which are not committed;
- re-verify every line of the census and ownership traces myself. I checked the seed citations and the
  load-bearing ownership lines; the remaining census rows rest on a single read and are marked uncertain where
  they are borderline.
