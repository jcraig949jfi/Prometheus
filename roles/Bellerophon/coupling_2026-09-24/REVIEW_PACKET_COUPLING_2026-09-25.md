+==============================================================================+
| REVIEW PACKET -- COUPLING CAMPAIGN (physics v3): does paying for correct      |
| computation create heritable pressure on computation?                         |
| Author: Bellerophon (M2 / SPECTREX5)            Date: 2026-09-25              |
| For: HITL operator + external reviewers                                       |
| Status: CAMPAIGN CLOSED; frozen rule says READY_FOR_MULTIDAY; next campaign   |
|         is a DESIGN only (nothing frozen, nothing launched)                   |
| Self-contained: no repo access needed; every load-bearing number is inline.   |
+==============================================================================+

-----
0. SUMMARY
-----
World: a 256-cell grid of 64-byte Z80-like programs that reproduce by copying
themselves (physics v2, grounded in an earlier round). New in v3: one hidden
integer per organism, the COPY RESOURCE R. Every interaction pays BASE; a correct
first output on a task pays BONUS; building a child costs 1 unit per byte written
(a full child = 64). No program can read or write R. The ledger identity
earned = spent + clamped + lost + held is asserted in every run.

Run: 11,657 runs (11,372 fixed Phase 1 + 285 automatic follow-ups), 0 voids,
0 NOT_RUN, seeded 3% replay 341/341 byte-identical, positive control 40/40.
Active runtime 8.63 h (wall 23.03 h, including a 13.2 h out-of-memory suspension).

Verdict by the frozen rule: READY_FOR_MULTIDAY.
Author's reading: the channel is real and causal, but the large effects are
MAINTENANCE of hand-seeded task code. ACQUISITION of new computation was seen
only for the simplest I/O task (ECHO) and in rare repairs. Random soup never
produced a competent replicator (0/3,200).

-----
1. WHAT WAS BUILT AND FROZEN BEFORE MEASUREMENT
-----
- Physics v3 + tests (58/58 at freeze), prereg frozen at commit c9bed96de with
  sha256 of 7 code files, the analysis script and the inputs; Phase-1 plan
  sha256 a3bc8c8e... (11,372 runs).
- Amendment 1 (6607b3cb5, operational only, operator-authorised after an OOM
  kill): caps measured in active runtime; worker recycling every 6 runs;
  detached supervisor. Scientific modules byte-identical to the frozen pin.
- The analysis script was byte-identical to the frozen file when run.
- The author stayed blind to outcomes until the analysis ran (counts/voids only).

-----
2. THE CLAIM AND WHY IT MATTERS
-----
The prior round (2026-09-23) found spontaneous self-replication was real but
that task performance had NO pathway to reproduction: tasks were causally inert
or selected against. Without such a pathway a multi-day run can only collect
more replication events. v3 adds the minimal pathway:
computation -> resource -> reproduction -> heritable variation.

-----
3. DESIGN AS EXECUTED
-----
Arms: ON (correct -> bonus to the organism), OFF (base only), SHUFFLED (answer
checked against an unseen input), RANDOM_REWARD (bonus to a random organism),
YOKED (the matched ON run's bonus total per tick, split evenly: same supply, no
contingency), IRRELEVANT (pays output 0x5A), DELAYED (credit after death).
Parameterizations: K16 (BASE 16, pure copiers not viable alone) and K40
(BASE 40, marginally viable). 500 ticks x 256 cells per run; unit = seed pair.

Lanes: A qualification (600), I exploit probes (90), C edge ablation (1,800),
E2 conflict repair (360), F task generality 6 tasks (1,440), G substrate
perturbations 8 (1,280), B-cop pure copiers with no task code (2,400), B-rand
random soup (3,200), J historical specimens (202). AUTO: dominant de novo
competent replicators transplanted alone, 3 seeds x 5 arms.

Readiness rule (frozen):
  instrument_ok = no voids, no imbalance, 3% replay identical, A8 >= 90%
  core          = P1 AND P2 AND P3 (Holm p < 0.05)
  novelty       = P6 OR >= 3 AUTO CAUSAL_COUPLED over >= 2 mechanisms
  generality    = >= 3/6 tasks ON > YOKED AND >= 4/8 perturbations ON > OFF

-----
4. RESULTS (K16 confirmatory; sign tests; Holm)
-----
P1 correct output raises births (HYB ON vs OUT-ablated ON):
   40/40 pairs, +38,926 births, persistence 40/40 vs 18/40.        HOLDS
P2 competence at tick 500, ON vs YOKED:
   149 vs 0 (1 tie), +0.767 [0.749, 0.784].                        HOLDS
P3 r_cc - r_nc (child competence given competent vs non-competent
   parent), ON runs: 150/150 positive, mean 0.9987.               HOLDS
P4 extinction YOKED vs ON: 67 vs 1 (82 ties).                       HOLDS
P5 r_cc ON vs YOKED: 0 vs 114, mean -0.0007 (both ~0.999).    FAILS (ceiling)
P6 repair in E2, ON vs OFF: 4/60 vs 0/60, p = 0.125.          FAILS (power)

Control shape (Lane C, K16), competence at the end / worlds surviving (of 150):
   ON 0.767 / 149   YOKED 0 / 83   OFF 0 / 28   DELAYED 0 / 28
   IRRELEVANT 0 / 29   RANDOM_REWARD 0 / 22
   -> the 83 surviving YOKED worlds all end with ZERO competent organisms, so
      P2 is not just an extinction effect: unpaid task code decays to nothing.
K40 matches the direction: ON 0.563 / 143, YOKED 0.0 / 66.

Generality (maintenance of seeded code, ON minus OFF/YOKED competence):
   tasks CONST .76  ECHO .79  INC .79  SUM2 .72  COND_ONE .35  COND_MULTI .18
   substrates: 6/8 hold. ldir_cost4 dead in both arms (3/80 persist);
   CONSTRUCTIVE persists 80/80 in both arms and coupling changes nothing.

Acquisition (the evidence that matters most):
   B-cop ECHO K40: de novo competent replicator at end ON 29/150,
                   OFF 6, YOKED 6, SHUFFLED 6   (ON vs YOKED p = 3.5e-6)
   B-cop ECHO K16: ON 7, OFF 3, YOKED 2, SHUFFLED 2   (ns)
   B-cop CONST (both K): 0-1 in every arm
   B-rand (all 3,200 runs): 0 in every arm
AUTO transplants (19 candidates):
   CAUSAL_COUPLED 7 (4 from B-cop ECHO, 3 from E2 repair), 6 distinct mechanisms;
   in all 7: ON succeeded 2-3/3, OFF 0/3, RANDOM_REWARD 0/3.
   SURVIVES_WITHOUT_COUPLING_OR_TASK 12 (7 from ECHO K40, where base income alone
   keeps copiers alive).

Exploits: correct outputs from organisms that are not competent themselves
(mostly executing a neighbour's code in the shared window): 1-6% of paid
outputs in most lanes, 14.6% Lane F, 25% Lane J. Designed probes (slider,
input corrupter, multi-output) stayed at ~1.5%; seeded HYB persisted 30/30.

-----
5. INCIDENTS AND WHAT THEY VALIDATED
-----
F4 host OOM kill at 959/11,372 (harness reaper; machine shared with ~48 other
   workers). Recovered by Amendment 1; 0 observations lost; integrity gate
   verified 959 lines before relaunch.
F5 operator stop for reboot at 1,359; relaunch after a passing integrity gate.
   The supervisor never wrote its own pid file (a stale pid was reused by
   Windows after the reboot) -- caught by hand.
Co-run: ENVGATE-02 (another seat, 6 workers) overlapped the last 38.9 min;
   free RAM >= 17.2 GB throughout; recorded as promised.
The replay (341/341) says the recoveries did not perturb any result.

-----
6. METRIC DEFECTS FOUND AT ANALYSIS (recorded, not smoothed)
-----
F6 P3 measures copy fidelity of whole-window copiers. It passes for any
   faithful copier of any code; it says nothing about evolution.
F7 P5 is at ceiling (~0.999 in both arms) and cannot see protection.
F8 The enrichment ratio saturates under ON (median 1.26) and is inflated in
   controls (~5.2-5.8); not a selection coefficient.
F9 The exploit-specimen ledger is capped at 400 rows, all from Lane A.
F10 E2 was sized too small for a ~7% repair rate.
F11 Two Lane G cells cannot test the null (both arms dead / both arms alive).

-----
7. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES: tying payment to an organism's OWN correct output is a causal,
contingency-specific channel from computation to reproduction. It keeps task
code alive against mutation across 6 tasks and 6 substrates, and it raises the
rate at which pure copiers acquire ECHO about 5x (K40).
DOES NOT: show evolved protection of computation (P5 blind, P6 ns); show
acquisition beyond the simplest I/O task; show anything about origins from
random soup (0/3,200); say anything beyond 500 ticks. The core tests P1-P3 were
satisfied by hand-written seeded code.

-----
8. DECISION / RECOMMENDATION (operator's call)
-----
The frozen rule's READY_FOR_MULTIDAY stands; the author does not override it.
Lean: run a multi-day campaign ONLY scoped to acquisition and protection, never
more maintenance:
  Q1 task ladder from ECHO copiers (ECHO -> INC -> SUM2 -> COND_ONE);
     kill if next-rung acquisition ON <= best control + 2 pp.
  Q2 protection, measured under raised copy-error load (replaces r_cc);
     kill if ON-evolved = YOKED-evolved.
  Q3 long-horizon E2 repair, sized from the 7% rate.
Prerequisites: repair F6-F11, resumable mid-run snapshots, a prereg, an
off-plan pilot, a dedicated host. An equally defensible answer is to stop here:
the channel works, but the acquisition signal is one trivial task.

-----
9. QUESTIONS FOR THE REVIEWER (please try to disagree)
-----
1. Is YOKED a fair no-contingency control, given it matches total supply per
   tick but spreads it evenly? Would a per-capita-matched yoke change P2/P4?
2. ECHO is output = input. Is 29 vs 6 of 150 acquisition of "computation" or
   of a trivial I/O idiom that any copier is one mutation away from?
3. The readiness rule let novelty pass through AUTO transplants when P6 failed.
   Was that clause too weak?
4. Should a READY verdict built mainly on seeded-code maintenance be allowed to
   justify a 2-3 day run at all?
5. Is 500 ticks enough for any of this to generalize to long horizons?

-----
10. ARTIFACTS
-----
Branch bellerophon/coupling-campaign-2026-09-24 @ 6a0b9813e (pushed, not merged)
Worktree D:/Prometheus-worktrees/bellerophon-post-campaign-forensics
roles/Bellerophon/coupling_2026-09-24/
  COUPLING_CAMPAIGN_PREREG.md (frozen c9bed96de; Amendment 1 6607b3cb5)
  COUPLING_CAMPAIGN_REPORT.md, COUPLING_FAILURE_LEDGER.md (F1-F11)
  COUPLING_CAUSAL_LEDGER.jsonl (439), COUPLING_ORIGIN_LEDGER.jsonl (68)
  NEXT_MULTIDAY_CAMPAIGN.md (design only)
  receipts/COUPLING_RESULTS.json, receipts/OPS_ACCOUNTING.json
Runtime evidence (not committed) C:/Users/James/z80atlas_coupling_2026-09-24:
  results.jsonl sha256 23b55f7843525f35f358ec288ba50f171b44a1b633c20b192f638c41b067bf75

+==============================================================================+
| END. "Not worth continuing" is a first-class answer. So is "the controls are  |
| wrong, rerun". Tell us which.                                                 |
+==============================================================================+
