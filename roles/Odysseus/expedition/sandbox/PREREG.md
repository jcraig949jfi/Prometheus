# PREREG -- Endogenous world-record sandbox, known-answer gate + exploratory unplanted run

Currency: 2026-09-28. Odysseus research worker. Written BEFORE any run
(no world has been simulated when this file was written). Never edited
after the first run; amendments go to AMENDMENTS.md with a timestamp and
reason. Pure ASCII.

Measurement being implemented: roles/Odysseus/expedition/accumulation/ACCUMULATION_v0.md
Doctrine: roles/Odysseus/prompts/2026-09-28_expeditionary/01_OPERATOR_DIRECTIVE_verbatim.md s3, s4, s15, s16.
Status of every unplanted result: EXPLORATORY (s16). No holdout exists or is spent.

## 1. World (full spec in DESIGN.md; parameters fixed here)

  S = 4 forage sites per colony; G = 4 colonies (nests) per world; N = 24
  organisms per colony; discrete generations (producers die before the
  next generation reads: every read is a delayed read of a dead writer's
  write).
  Record: K = 2 cells per nest, alphabet A = 4 symbols plus BLANK.
  Access is local: an organism can only read/write its own nest's cells.
  Costs: base income 0.10, reward 1.00 for foraging at the patch site,
  read cost 0.02 per cell read (a reader reads all K cells), write cost
  0.05 per write/erase action.
  Noise: each record cell, each generation, with prob eps = 0.01 is
  replaced by a uniform draw from {BLANK, 0..A-1}.
  Environment: each colony has a hidden patch site s_g; after each
  generation it is redrawn with prob p = 0.10 (uniform over the other 3
  sites; in world family C, redraw from {0: 0.7, 1: 0.1, 2: 0.1, 3: 0.1}).
  Convention map sigma: a per-world permutation of the alphabet applied
  between an organism's write output index and the stored physical symbol.
  Identity in P, P4, N_a, N_b, C, U_id; uniform random per world in
  P_sigma, U_sigma, U_frozen, U_unread, U_norec.
  Genome (lookup tables): read bit; explore level in {0, .05, .2, .5};
  choose table (A+1)^K = 25 entries -> site; write address in {0..K-1};
  write table (site, found) 8 entries -> {noop, erase, sym0..sym3}.
  Reproduction (unplanted): roulette on energy (floor 0.01) within colony,
  migration 0.02, per-gene mutation 0.02; every 20 generations the colony
  with the lowest mean energy over the last 20 is replaced by a copy of the
  best colony's population (its nest record is NOT copied).
  Planted worlds: clonal replacement (fixed genomes, no selection, no
  mutation).

## 2. Arms (n = 20 independent worlds per arm; world seeds 1000+i)

  Known-answer (planted, 300 generation burn-in):
    P       planted single code: on success write enc(site) into cell 0;
            readers decode cell 0; explore 0.2.
    P4      planted two-object code: caste A (half, distinct founders)
            writes the high bit of the site into cell 0, caste B the low bit
            into cell 1; readers decode both (unknown bit -> 0); explore 0.2.
    N_a     writers as P (record informative) but readers ignore the record
            (choose table constant = site 0; explore 0.2).
    N_b     writers write a uniformly random symbol into cell 0 every
            generation (record uninformative); readers decode as P.
    C       cheat: biased environment (above); writers as P; readers go to
            site 0 if cell 0 is non-BLANK, else to a random site
            (explore 0.2 applies).
    P_sigma P under a random sigma (convention-invariance probe of a plant).
  Unplanted (EXPLORATORY, 3000 generations of evolution from uniformly
  random genomes):
    U_sigma main arm (random sigma per world).
    U_id    sigma = identity (pair for convention invariance).
    U_frozen frozen readout: one random choose table + read bit + explore
            shared by all organisms in the world, never mutated; only
            writer genes evolve.
    U_unread unreadable storage: writes happen and cost, reads return BLANK.
    U_norec no record layer (reads/writes are no-ops at no cost).

## 3. Battery (applied to the saved end state S* of each world)

  All probes restore S* exactly (both RNG states included) and reseed the
  bio RNG with eval seeds 0..15 (common random numbers across arms).
  S1(receivers, intervention) = mean foraging success of the FIRST
  consumer generation after the intervention (pure inheritance: every
  producer is dead; consumers never wrote this record), averaged over
  colonies and the 16 eval seeds.

  D0 (R0) : record decodability. From 20 snapshots (every 10 generations
            over the last 200), remove all organisms, run T = 5 generations
            of physics (noise only), then decode the producing generation's
            s_g from the record tuple with a leave-one-out majority map over
            the world's 80 (snapshot, colony) pairs. D0 = acc(intact) -
            acc(history-ablated twin: same snapshot restored 30 generations
            earlier and run to the snapshot with all writes suppressed).
  D1 (R1) : S1(own, intact) - S1(own, deleted).
  D2 (R2) : novel receivers = population of colony (g+1 mod G) of the same
            world placed in colony g, producers removed.
            D2 = S1(novel, intact) - max(S1(novel, deleted),
            S1(novel, norecord), S1(novel, unreadable)).
  Dp (R3) : S1(own, intact) - S1(own, records permuted between colonies by
            the cyclic derangement g <- g+1).
  Dr (R3) : S1(own, intact) - S1(own, equal-capacity random: every
            non-BLANK cell replaced by a uniform symbol, BLANK kept).
  Di (R3) : S1(own, intact) - S1(own, irrelevant injection: a random symbol
            into every cell that no organism wrote in the last 20
            generations; if none, Di is n/a and not required).
  Also reported, not decisional: episode permutation (the same colony's
  record from 50 generations earlier), fresh-world transfer (record of
  world i colony g inserted into world i+1 colony g with that colony's s
  set equal, vs the same with the record deleted), A/A (two intact probes
  with disjoint eval seeds).
  R4 2x2  : S11, S10 (cell 1 deleted), S01 (cell 0 deleted), S00.
            I = S11 - S10 - S01 + S00; Dx = S11 - max(S10, S01).
            Provenance: the sets of founder ids that wrote cell 0 and cell 1
            during the last 100 generations; Jaccard J.
  R5      : window probe W = 40 generations with dynamics continuing
            (intact; record deleted every generation; norecord).
            CEILING = mean success over window generations 21-40.
            SPEED = mean generations after each environment switch until
            colony success >= 0.5 (capped at 10). Both reported separately.
            c* = CEILING(intact) - 0.05.
            (a) CEILING(norecord probe) < c* - delta;
            (b) recompute arm, v0-literal budget: a record-free consumer
                given the trips spent producing the record (>= N = 24
                trips) searches without replacement; success = min(1,
                (B+1)/S) with B = 24 -> 1.0; requirement: < c* - delta.
                Also reported, not decisional: per-consumer budget B = 1.
            (c) pristine: U_norec worlds' CEILING (for planted arms: a
                record-free world with the same planted readers) < c* - delta.
  R6: not implemented (see DESIGN.md s7).

## 4. Decision rules (delta = 0.05, success-rate units)

  Aggregation over the n worlds of an arm: mean and 95% percentile
  bootstrap CI (2000 resamples, seed 12345).
  PASS(D)  := mean >= delta AND CI_lo > 0.
  EQUIV(D) := |mean| < delta AND CI inside (-2 delta, +2 delta).
  R0 := PASS(D0).
  R1 := R0 AND PASS(D1).
  R2 := R1 AND PASS(D2) AND assertion that no receiver wrote the record.
  R3 := R2 AND PASS(Dp) AND PASS(Dr) AND mean Dp >= 0.5 mean D1 AND
        mean Dr >= 0.5 mean D1 AND (EQUIV(Di) or Di n/a).
  R4 := R3 AND PASS(I) AND PASS(Dx) AND mean J <= 0.2.
  R5 := R4 AND (a) AND (b) AND (c).
  Tests are also reported individually (a failed lower rung does not hide a
  higher test's value).
  CONVENTION qualifier (for any arm with R3): paired arm (P with P_sigma,
  U_id with U_sigma). INVARIANT if PASS(D1) holds in both members and
  |mean D1(sigma) - mean D1(id)| < delta; else INSTALLED.
  APPARATUS VALIDITY: for every arm, the A/A CI must contain 0; if not,
  the battery is invalid for that arm.

## 5. Known-answer criteria (THE GATE; all must hold before U is read)

  P   : R0, R1, R2, R3 awarded; R4 and R5 NOT awarded; qualifier INSTALLED.
  N_a : nothing above R0 (R0 expected, not required).
  N_b : nothing above R0 (R0 expected NOT awarded).
  C   : R3 NOT awarded, and the failing clause is Dp or Dr (content), not a
        lower rung (i.e. R2 awarded). If C fails R3 only because a lower
        rung failed, the gate is FAILED (the cheat was not tested).
  P4  : R4 awarded (secondary: if it fails, R4 detection is reported as
        unvalidated; it does not block the gate).
  If the gate fails: no unplanted result is interpreted; the battery is
  repaired and the repair and re-run go to AMENDMENTS.md.

## 6. Unplanted report (EXPLORATORY)

  Highest cumulative rung per unplanted arm, every test's mean/CI, count of
  worlds with individual D1 > delta, the CONVENTION qualifier (U_id vs
  U_sigma), the frozen-readout arm, ceilings of U_unread and U_norec, speed
  and ceiling separately. No word "language", "culture", "knowledge" is
  used for any outcome.

## 7. Budget

  <= 60 min wall on 4 cores (multiprocessing, stdlib only). If a timing
  smoke (one world, 50 generations, no statistic computed) projects
  over budget, the ONLY permitted reduction is unplanted generations
  3000 -> 1500 and then n 20 -> 12, recorded in AMENDMENTS.md.
