<!-- DEPOSITED VERBATIM by Ananke for worker W-H; sha256(report)=c539da196727431f; delimited; see REPORT.provenance.json -->
W-H REPORT: what does dynamic rule switching (SETRULE) do in PTE champions?
Worker W-H, namespace 0x5ED (64 worlds = 32 mirror pairs, 99% pair bootstrap). Wall time about 1 h 15 min (01:00 to 02:15, 2026-09-28).
Files: roles/Ananke/research/workers/W-H/{PLAN.md (frozen, with Addenda A-C written before the runs they govern), LOG.md, harness.py, obs.py, cf.py, hand.py, hand_h3dbg.py, hand_s4.py, search_arms.py, summarize_search.py, out/*}.
GPU lease 2ce85284abe2 was held 01:11-02:14 and has been released.
Independence: before writing PLAN I read only the raw W-B scripts and out/*.json. I did not read the W-B REPORT/PLAN/LOG or any principal SYNTHESIS/REVIEW/CARD/PRIORITIES file. I read PRIOR_ART s4.5, s4.10 and s6 only after the results were in.

PRE-STATED CRITERION (PLAN Part 2)
- "Same length" means the same per-tick length L with rules=1 and otherwise identical physics.
- A* is the champion's lower 99% bound on my analysis worlds.
- COMPRESSION: any hand-compiled (H) or searched (B) rules=1, length-L program has mean accuracy &gt;= A*.
- EXPANSION (bounded): no H or B program reaches A*, AND the champion's own search budget (A) reaches A* in at least 1 of 4 seeds, AND the H failure has an identified cause.
- INCONCLUSIVE: anything else.
- Secondary arm C: rules=1 with prog_len = R*L, i.e. the same amount of genome text.

ENGINE FACT
r is a per-site register with three properties: it never decays, it costs no energy, and it is readable only through which program variant runs. SETRULE sets r_next := A mod R.
So a switching genome can in principle do more than a rules=1 program of the same L: it has R*L instructions of text, a free state register, and dispatch that costs no instructions. That is where expansion could come from. The question was whether champions use it.

SPECIMENS (chosen to discriminate mechanisms)

S1 b59e6c3a (RELAY d1, delta 16, smallworld, asynchronous updates, R=4, L=12)
- Branch: at every site, rule 0 does four things:
  - The sensor emits only on a + cue (EMIT = max(SENSE, 0)).
  - S0 := S0 - S1 - 60, a steady ramp down.
  - SETRULE r := CNT0 mod 4.
  - The condition is exact in 11,320 observed readout-site ticks: CNT0=0 gives 0, CNT0=1 gives 1, CNT0=2 gives 2.
- Consequence: rule 1 writes S0 := 776, holds for 1-2 ticks, then returns to rule 0. The ramp then counts down about 60 per awake tick, so the sign of S0 at readout means "a packet arrived within about the last 13 ticks".
- Role: an event-triggered conditional branch, i.e. a set-then-leaky-timer.
- CF1, forbid the switch at the readout site: accuracy exactly .500 (difference -.241 [-.272, -.207]), NECESSARY.
  - Control, the same pin on a random other site: difference 0.
- CF2, force rule 1 at t0+5 in y=-1 trials: .022 [0, .088] on those trials (normal .947), SUFFICIENT-FLIP.
- H1, a 7-instruction rules=1 program (a select on CNT0 between 776 and S0-60): .764 [.736, .793], above A* .707. VERDICT: COMPRESSION.

S2 311c465f (HOLD gap 4, torus, sync update period 2, R=2, L=8, decay 3)
- Branch: S0 is written only in rule 1 (S0 := SENSE ^ E), and rule 1 lasts one awake tick.
- Rule 0 runs a clock: S2 ^= SENSE, then r := S2 mod 2. The parity of S2 changes through decay, and the cue XOR resets it, so the clock opens the S0 write-enable near the cue.
- The clock does not depend on the cue sign.
- Role: phase selection, i.e. a sample-and-hold write-enable clock.
- CF1, forbid rule 1 on the cue phases: .495 (difference -.254), NECESSARY.
- CF2, force rule 1 in the gap: .528 [.449, .599], SUFFICIENT-CHANCE (it samples a distractor).
- H2, a 4-instruction latch that uses |SENSE| as the write-enable: .999 [.995, 1.0], against the champion's .755.
- Search, B_fixed_L: 2 of 4 seeds reach .963. A_orig: 1 of 4.
  - Not pre-registered: the one A_orig winner still scores .948 with its rules frozen after boot, so it does not use ongoing switching either.
- VERDICT: COMPRESSION. The switching champion is strictly worse than trivial fixed programs.

S3 95649e2c (RELAY d1, delta 16, ring, asynchronous updates, R=4, L=12)
- Branch: in rule 0, S0 := CNT0 (never negative) and r := IN0_0 mod 4.
  - A single -110 payload gives 2 (mod 4). Two packets sum to -220, which gives 0.
  - So the condition is arithmetic on the payload sum.
- Consequence: rule 2 makes the site forward (EMIT := ENERGY), does not write S0, and returns to rule 0 after exactly one awake tick (1,404 of 1,404 cases).
- Role: temporary specialization as a one-tick relay, with refractoriness coming from the payload arithmetic.
- All competence is on + trials: y=-1 trials score .49 in normal runs because S0 &gt;= 0 produces ties.
- CF1, forbid rule 2 at all sites: difference -.070 [-.087, -.055], NECESSARY but partial. At the readout site only: -.021.
- CF2, force rule 2: NO-EFFECT.
- H3, a faithful fixed-rule forwarder: FAILED, .511. My 3 debug iterations ended at .536 because the reverberation lifetime could not be tuned by hand.
- H3alt, the S1 mechanism (H1) run on S3's physics: .792 [.762, .824], above A* .648.
- Search: B 0/4 (best .639), A_orig 0/4, C 1/4 (.762).
- VERDICT: COMPRESSION under the pre-stated wording, because some fixed-L program solves the task better. The narrower question, whether this particular relay mechanism can be written fixed-rule at L=12, is UNRESOLVED.

S4 faafa5b0 (HOLD gap 16, decay_shift 1; Addendum B)
- This is the one cell where fast decay would make r's decay-free storage matter.
- H4b, a Kp latch via WIMM with rules=1: 1.000. The champion scores .590.
- COMPRESSION.

S5 ed884172 (HOLD, decay 1, WIMM off, no plastic routing; Addendum C)
- Here r is the only decay-free store other than E.
- A plain S0 latch scores .735 (the positive sign survives decay) against A* .592.
- COMPRESSION: the task never needed the storage.

WHAT HELD
- Switching is used during operation and is causally necessary in S1, S2 and S3 (CF1 all NECESSARY, with a clean site control in S1).
- Three distinct roles showed up:
  - an event-triggered branch (S1),
  - a phase-selected write-enable (S2),
  - a transient relay specialization (S3).
- Every switch is a 1-2 tick excursion that returns to rule 0. None is a persistent state-machine state or a rule used as memory. The answer bit lives in S0 or in traffic, not in r.

WHAT FAILED
- The EXPANSION hypothesis: 0 of 5 cells.
- My faithful H3 compile.
- Using search as evidence for S1 and S3: the champion's own budget reproduced the champion in 0 of 4 seeds, so those search comparisons are uninformative.

WHAT SURPRISED ME
- Fixed-rule hand programs of 4-7 live instructions beat the switching champions, sometimes by a lot (S2 .999 vs .755, S4 1.000 vs .590).
- The binding constraint is what the search can reach, not what the program can express.
- Arm C (more text, no switching) did no better than arm B on S2 and helped once on S3. Program-text budget is not the limit either.

ANSWER
In these cells, dynamic rule switching COMPRESSES; it does not EXPAND. Each observed role can be expressed with a select or a latch inside L instructions. The engine's real expansion headroom (a free, decay-free register plus free dispatch) went unused in all 5 cells. This is "not found within these bounds", not an impossibility result.

DISAGREEMENTS
- I did not read the principal's interpretations, so I cannot point at specific statements. Against any reading that SETRULE champions show switching as memory, or as a capability beyond fixed programs, the evidence says no:
  - r never holds the bit beyond 2 ticks.
  - Fixed-rule latches match or beat every champion.
- Against the brief's candidate "state-machine transition": not observed.

PRIOR ART (read after the results)
- The rule index is "hidden state" in Buonomano &amp; Maass's sense (s4.10), but here it acts as a control strobe, not a store.
- S2 is a bundled-data sample-and-hold clock in the sense of s6.1, and it fails in exactly that way when sampled off-phase (CF2).

PROPOSED THREADS
- T-H1: pin down expressivity by building a task and physics where a rules=1 L program provably cannot solve it but R&gt;1 can (state_dim=1, WIMM off, decay&gt;0, a long hold). Then ask whether search finds the switching solution.
- T-H2: evolvability study: rules on vs off, 16+ seeds, larger budget, across the 42 qualifying cells. The S1 and S3 champions look like lucky tails.
- T-H3: an automatic flattening compiler (R variants into one select-dispatched program) to measure the instruction overhead per champion.
- T-H4: finish a faithful fixed-rule relay for S3 at L=12 (a payload-parity refractory relay).
