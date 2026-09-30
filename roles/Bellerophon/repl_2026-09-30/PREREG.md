# E-BEL-REPL-01 -- preregistration: independent BEE rebuild of NPE C-A3-INTERNALIZE, with a kill battery

Author: Bellerophon (M2 / SPECTREX5). Work order: MWO-0004 + CWO-2026-09-30 s3 BELLEROPHON CURRENT (Aporia #1033).
Selection: SELECTION.md (19e758e7f), criteria SELECTION_CRITERIA.md (9c4a4fabe, committed first).
This file, tools/repl_run.py, tools/repl_analysis.py, tools/state_free.py, tools/test_repl.py, tools/pilot_worlds.py (CELL)
and FOUNDERS.json are frozen by the commit that adds FREEZE_MANIFEST.json. That commit precedes every production output.
Nothing listed there changes afterwards. A later change is an amendment, and it must state whether production data had
been seen when it was made.

## 0. The claim under test (source text, not code)

NPE C-A3-INTERNALIZE (roles/Nestor/campaigns/npe-arc3-2026-09-28/c_a3_internalize/run_ci.py docstring; VERDICT.json
dce299ce8): "in fresh evolutionary runs, a lineage founded only by non-state-free donors repeatedly comes to carry
state-free competent genomes descended from those founders -- endogenous internalization of register initialization."
NPE result: 8/144 against a frozen bar of 4.

What this test adds is not a reproduction. It rebuilds the phenomenon in an engine the source seat did not write (BEE,
prometheus/z80atlas), and then tries to make it disappear:
- K1: a no-payoff null;
- K3: a content-level descent check;
- K4: a ruler swap.
Blindness: Nestor's own material audit (X-MAT-INTERNALIZE) is sealed (#1055). I have not read its outputs, and I will
not read them until this experiment's outputs are sealed.

## 1. World (BEE), as built and tested (engine commits 35b2fde55, ee82457a4, 8a2390d82; 88 tests)

- **Cell:** grounding G1 ENDOGENOUS_PARTIAL/Z80_64 (pilot_worlds.CELL). v2 physics, GRID LOCAL, 256 cells, lifespan 40,
  BYTE mutation at MED, IMPLICIT/ATOMIC/INC, budget 256. Ticks 2000 (NPE: 2000 epochs).
- **Register world** (the scaffold): what registers an organism enters an execution with.
  * ZERO: all zero on every execution. This is BEE's historical physics.
  * P90 / P75: CARRIED (an organism keeps its own exit registers; a newborn inherits the registers of the occupant it
    overwrote; a birth into an empty cell starts at zero). Before each execution the registers are reset to zero with
    probability 0.9 / 0.75. This is NPE's SCHEDULE text ("ZERO applied with probability p, else CARRIED"). The draw comes
    from a per-run register RNG and never from the world's RNG.
- **Founders:** FOUNDERS.json, 30 distinct first-self-replicator tapes from BEE's own grounding-round spontaneous origins
  (ENDOGENOUS_PARTIAL/Z80_64). Each is ZERO_DEPENDENT by the s2 assay (re-checked in G0). Pair s uses founder F[s mod 30],
  transplanted as a quarter of the population into a random majority (World init_tapes). NPE started from random
  populations; the change is justified in s3.
- **Pairs:** s = 0..99. The seed is 32,000,000 + s, identical in all three arms of a pair: 300 runs.

## 2. Instrument

- **COMPETENT_e** (tools/state_free.py; the BEE analogue of NPE X-A3-FAIR's battery, built from its text). Executed alone,
  from entry state e, with a random partner window and random inputs, the tape writes >= L/2 bytes of the window and the
  window matches the tape in >= 90% of bytes. The rate must be >= 0.5 over 20 trials (a 2-trial screen comes first).
  Trials use their own RNG.
- **STATE_FREE** = COMPETENT from both R1 and R2. These are two fixed random entry vectors, drawn once from
  "E-BEL-REPL-01|R" and recorded in PILOT1.
- **K4 ruler:** STATE_FREE_alt = COMPETENT from both R3 and R4, drawn from "E-BEL-REPL-01|R-alt".
- **Checkpoints:** every 100 ticks and at extinction. For each distinct live genome the runner records its STATE_FREE /
  STATE_FREE_alt status (cached per genome) and which descent sets carry it:
  * **G (primary):** at least one organism carrying the genome has a genetic lineage (Org.glineage) from the founder
    copies at tick 0.
  * **FM (K3):** the genome equals the founder at >= 16 of 64 positions. By chance, a random tape matches about 0.25
    positions.
  * **L (secondary only):** the causal lineage (Org.lineage) of the founder copies.
- **Runner:** tools/repl_run.py. It measures only; the scoring is in tools/repl_analysis.py.

## 3. Deviations from NPE's design, and why (all decided before any production run)

- **D1. Founders are transplanted rather than drawn from random populations.**
  * BEE's spontaneous-origin rate is 1-5% of runs (grounding), against NPE's 94/144 runs with donors.
  * PILOT 2 random-population runs gave: CARRIED 19/100 origins, 0 persisting; ZERO 6/100, 3 persisting.
  * NPE's eligibility clause ("every D0 genome NOT state-free") is met by construction, since every founder is certified
    ZERO_DEPENDENT.
- **D2. A partial scaffold (P90/P75) is used instead of plain CARRIED.**
  * Under plain CARRIED in BEE, zero-dependent founder lineages die out: PILOT 2 gave 0/24, and PILOT 3 gave p = 0.25
    0/12, p = 0.5 1/12, p = 0.75 2/12, p = 0.9 5/12. ZERO gave 10/24.
  * NPE's CARRIED world lets founder lineages persist, and its synthesis says the scaffold is "merely available" there.
  * P90 and P75 are the BEE worlds in which the scaffold is available and founder lineages can persist.
- **D3. The primary descent label is G, not causal L.**
  * In one SMOKE run (pair 900, outside the production range), BEE's causal lineage transferred on 1-byte
    ENDOGENOUS_PARTIAL writes. At tick 2000 it read L_share 0.0 while G_share was 1.0.
  * So causal L in this physics is not NPE's "accepted replication". That smoke run's only state-freedom readout was
    free = 0 at every checkpoint, and it is disclosed here.
  * G is itself a resemblance-based label: E-003 showed that BEE's native material label is not a descent label. For
    that reason, K3 re-scores every event with an independent CONTENT test (FM).

## 4. Pilots and exposure (all disclosed)

| pilot | what it saw |
|---|---|
| PILOT 1 | founder profiles only (no evolved genome) |
| PILOTS 2-3 | origin, extinction, persistence and cost only (tools/pilot_worlds.py prints no state-freedom). Seeds 30,000,000+ and 31,000,000+ |
| SMOKE runs | pairs 900 and 901 (P90, ZERO). No state-free genome was observed |

No production seed has been run. Compute used so far: about 2.9 core-h.

## 5. Gates (the verdict is INCONCLUSIVE if any gate fails)

- **G0.** tools/test_repl.py passes before launch. Its planted controls are:
  * a state-free replicator reads STATE_FREE (both batteries);
  * a planted S-dependent copier reads ZERO_DEPENDENT;
  * every production founder reads ZERO_DEPENDENT and is not STATE_FREE_alt;
  * the event detector fires and refuses on planted records;
  * the Fisher test matches a known value.
- **G1 complete:** 100 runs in each arm.
- **G2 founders not state-free:** checked on every production record (founder_state_free = founder_alt_free = false).
- **G3 power:** at least 20 treatment runs (P90 + P75) end with G_share >= 0.5, i.e. a persisting founder lineage.

## 6. Event and kill battery (computed in tools/repl_analysis.py)

- **EVENT (per run; NPE text with BEE's G):** at the LAST checkpoint with >= 1 STATE_FREE genome, >= 80% of the
  STATE_FREE genomes are carried by G AND G holds >= 50% of the live population.
- **E_T** = events in P90 + P75 (n = 200). **E_N** = events in ZERO (n = 100).

| kill | question | rule |
|---|---|---|
| K1 no-payoff null (primary) | ZERO has no register payoff for state-freedom. Does the event occur as often without the scaffold's payoff? | E_T < 4: NOT_REBUILT (BEE does not show the phenomenon: a transfer failure, NOT a kill of the NPE claim). Else one-sided Fisher exact (T rate > N rate), p < 0.05: SURVIVES. Else: DISAPPEARS |
| K2 sorting | Were state-free variants already present at founding? | Handled by design: the founder is a single certified ZERO_DEPENDENT genotype. The secondary reports the first tick at which a state-free genome appears in G |
| K3 content descent | Is it founder material or a label artefact? | Of the T events, >= 50% must also be events under FM: SURVIVES. Else: DISAPPEARS |
| K4 ruler | Is it produced by the fixed R1/R2 vectors? | Of the T events, >= 50% must also be events under the R3/R4 ruler (with G): SURVIVES. Else: DISAPPEARS |

- **Verdict:**
  * SURVIVES: K1, K3 and K4 all survive. The phenomenon goes to NEXT (mutant/falsifier expansion). It is NOT promoted.
  * DISAPPEARS (names the kills): at least one kill removes it.
  * NOT_REBUILT, or INCONCLUSIVE (names the failed gate).
- **Power note** (a precommitment that can be lost):
  * I expect SOME treatment events if the NPE phenomenon transfers. BEE runs ~50 generations in 2000 ticks at lifespan 40.
  * A NOT_REBUILT at this power is evidence about BEE and this design, not about NPE.
  * My stated expectation, which I can lose: E_T in 2..12 and E_N in 0..3. K1 is the most likely kill if the effect is
    drift that does not depend on payoff.

## 7. Secondaries (never decisive)

- per-arm event rate per run and per persisting run;
- dose response, P75 vs P90 (one-sided Fisher, P75 higher);
- replacement counts;
- causal-L events per arm;
- first tick of a state-free genome in G per run.

## 8. Execution and custody

- **Compute:** about 300 runs x ~90 s, roughly 7.5 core-h, inside MWO-0004 R2 (<= 16 core-h per item, including the
  pilots).
- **Where:** M2 under a spectrex5:cpu12 lease, or Fabric script workers.
- **Custody:** outputs go to C:/Users/James/repl_2026-09-30/production/. They are sealed (sha256) before the analysis
  runs, and the analysis runs once, by this frozen code. The runs.jsonl digest and the analysis output are committed
  together.
- Nothing under prometheus/cosmos/ is touched. No NPE code is read or run.
