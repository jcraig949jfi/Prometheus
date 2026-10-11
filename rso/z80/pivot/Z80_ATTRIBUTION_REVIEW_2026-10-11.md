+==============================================================================================+
| REVIEW PACKET -- C-017-T030: Z80 Atlas "who wrote the bytes" attribution instrument          |
| Author: Argus (Evidence & Qualification Engineer), claude-opus-5-5 (Q2), harry1 (M4)         |
| Date: 2026-10-11                                                                             |
| For: James (HITL); external reviewers; Pallas (Q3 challenge of the frozen surface)           |
| Status: FROZEN, NOT YET CHALLENGED. No confirmatory run. Development evidence only.          |
| Self-contained: every load-bearing number is inline; no repo access needed.                  |
+==============================================================================================+

-----------------------------------------------------------------------------------------------
0. SUMMARY
-----------------------------------------------------------------------------------------------
Question (coordinator decision, re-scoped by C-017-T020 because the Z80 world demands reproduction
of function, not endogenous heredity): given a Z80 Atlas run whose final population carries a working
ECHO function, can the Observatory attribute WHO WROTE THE BYTES that carry it -- parent execution
(ENDO), the runner (EXT), the environment / previous occupant / neighbour (ENV), or nobody since
insertion (INS) -- and whether the function was inserted or arose (origin), WITHOUT trusting the
engine's provenance / origin / score / mech / spontaneous_replication fields?

Main finding before any statistics: the writer is NOT a property of the bytes. A child the runner
copied from a copier is byte-identical to one the copier wrote itself. A bytes-only detector (the
T020 demand-gate reading) credits runner-written copiers as endogenous in 7 of 8 development runs.
So the instrument's trust root is REPLAY: it re-executes (spec, seed) under its own observation loop
and refuses any record that does not replay byte for byte.

Development verdict (dev seeds only, preregistered rule applied): ATTRIBUTION_QUALIFIED on dev rows --
0 class errors (ENDO 0/24, EXT 0/25, ENV 0/48, INS 0/48), 0/145 origin errors, 48/48 forgeries
handled, both baseline detectors fail the ENV arm 48/48. This is NOT the confirmatory result. The
confirmatory run waits for Pallas's Q3 challenge.

-----------------------------------------------------------------------------------------------
1. WHAT WAS BUILT (and in what order)
-----------------------------------------------------------------------------------------------
Branch argus/c017-t030 from 1f85d6d62:
  37bec7820  tests committed first; suite FAILED (ImportError) at 15:32:55Z -- RED before code
  6eceadc7e  adapter + 42 tests + development check + 27 RED rows
  0c7afbeea  PREREGISTRATION v1.0.0 (decision rule fixed)
  e41fff917  FREEZE v1.0.0: 27 files pinned, explicit list, FROZEN.json sha256 cad362fa...
Adapter: 667 physical / 471 code lines (Ensorain: 662 / 480; Ares: ~1,800). 0 shared components
modified. 0 requests to the engine owner (Archaeon). ~2.5 core-h, <= 2 processes, $0.

Components:
  observe.py  engine.run's population loop re-implemented for one subset (well-mixed, fixed world,
              ENDOGENOUS_COPY or EXTERNAL physics, two pressures), every RNG draw in the engine's
              order with the engine's own primitives. Byte-equal to engine.run: 5 tests, plus all
              176 unforged dev records replayed without refusal. ~125 code lines exist only because
              the engine keeps its population in locals (no per-birth hook).
  Per-byte writer tags: I founder, P parent-written, K kept / environment-dependent, R runner,
              M mutation or copy noise. P requires the byte to be in the parent's write mask AND
              unchanged when the parent is re-executed over two altered pre-windows (complement,
              +0x55) -- a counterfactual, not the engine's read/foreign counters.
  Label:      whose bytes ALONE (others zeroed) carry ECHO on 8 probe cases: P->ENDO, R->EXT, I->INS;
              needs K -> ENV; competent only with its live neighbour -> ENV; else OTHER.
  Run class:  strict-majority label among functional organisms; NONE / MIXED otherwise.
  Origin:     INSERTED iff a founder supplied by the transplant or seeded path carries ECHO.

-----------------------------------------------------------------------------------------------
2. GROUND TRUTH AND THE DECISION RULE
-----------------------------------------------------------------------------------------------
Ten arms, ground truth by construction (unit = run; organisms are lineage-dependent):
  ENDO  H planted (13 cells) GATED 80 ep; engine seeded path 80 ep; H planted, no reward, 80 ep
  EXT   H planted 200 ep; H planted 10 ep (copiers still intact); witness-only 200 ep; random 200 ep
  ENV   RECON (new): IN/OUT/NOP at bytes 0..2 + a copier of bytes 3..31 only (29/32 >= .9). A child
        is functional only where the target cell already held those 3 bytes. No reward, 100 ep.
  INS   witness-only under endogenous physics, 30 ep (no birth possible; founders survive)
  NONE  random founders, endogenous (the lottery arm; reported, not scored)
Forgeries built from real records: LABELS and PLANT (every stored label says endogenous / discovered)
must leave class and origin unchanged; PHYS (physics edited), TAPE (a final tape replaced), GEN
(generations inflated) must be refused.
Rule: per class, wrong <= w_max(n), the largest w with P(Binomial(n,1/5) <= w) <= 1/100 (exact;
n 21-30 -> 0, 48 -> 3, 72 -> 6); n < 21 -> UNDERPOWERED. Origin the same, pooled. Forgeries zero
tolerance. Two negative-control detectors (label reader b1; bytes-only b2) must EACH fail, or the arm
set is UNINFORMATIVE. Confirmatory N: 24 per arm, 48 for ENV and INS; seeds 17_050_xxx untouched.
Power: a 2% true error rate passes with .985 (n 48) / .999 (n 72); 5%: .78 / .93; 10%: .28 / .41.

-----------------------------------------------------------------------------------------------
3. DEVELOPMENT RESULTS (dev seeds 17_030_xxx; rows sha256 6e04917a...)
-----------------------------------------------------------------------------------------------
  class  n   wrong  w_max    b1 wrong   b2 wrong
  ENDO   24  0      0        0          0
  EXT    25  0      0        0          7      <- b2 calls runner-written copiers ENDO
  ENV    48  0      3        48         48     <- neither baseline can say ENV
  INS    48  0      3        0          0
  origin 145 0      17
  forgeries: LABELS 8/8 invariant, PLANT 8/8, PHYS 16/16 refused, TAPE 8/8, GEN 8/8
  purity (organisms carrying the run's class / functional): ENDO arms 957/981, 925/968, 512/513;
  EXT 910/912, 880/924, 893/895; RECON 1933/2096; INS 446/446.
Behavioural pins: 27 mutants of decision-rule lines (observe 9, assay 9, analysis 9), each RED on a
named test; baseline 42/42 GREEN; RED rows reproduced byte-identically.

-----------------------------------------------------------------------------------------------
4. WHAT DEVELOPMENT CHANGED (design moves made on dev evidence, all before the freeze)
-----------------------------------------------------------------------------------------------
a. First tag rule used the engine's reads/foreign counters as "environment": 4/21 ENDO runs
   mislabelled, because a parent with a broken HALT runs into its own fresh copy. -> counterfactual P.
b. GROUND TRUTH DRIFTS WITH EVOLUTION. Reconstructors converted to genuine endogenous copying under
   reward (a copier operand mutates; 3/12 runs by epoch 100; 0/12 without reward). Planted heritable
   lineages at 200 epochs were partly replaced by reproducers that copy only by executing the target
   cell's code (2/16 runs; 0/36 at 80 epochs). -> horizons 80 / 100; RECON without reward. The
   instrument labelled the drifted mechanisms correctly; the horizons keep the CONSTRUCTED answer true.
c. A random founder that already echoed was called INSERTED (1 run). -> origin from founder SOURCE.
d. A RED-row survivor showed a 3-case competence bar admits luck. -> 8 probe cases, live vs zeroed.
e. H_EXT_SHORT cut from 30 to 10 epochs: by 30, mutation had broken most runner-written copiers, which
   made the bytes-only baseline right by accident.
The horizon-probe seeds (17_03x_1xx) are not in the development check. Disclosed in the preregistration.

-----------------------------------------------------------------------------------------------
5. INCIDENTS / PROCESS
-----------------------------------------------------------------------------------------------
- RED and IMPLEMENTING workgraph states committed together an hour after RED was observed; claim note
  and first heartbeat posted late. RED evidence itself is the 15:32:55Z branch commit.
- Receipt timestamp first written as an estimate (17:38Z); corrected to 17:24Z (push 17:25:18Z).
- Every state push gated on the validate exit code (pipefail) -- the C-016 slip not repeated.
- A parasite/host ENV population was attempted and does not persist (hosts are one mutation from
  self-function; parasites cannot reproduce under endogenous copying): ENV at population scale has
  one construction only.

-----------------------------------------------------------------------------------------------
6. WHAT THIS DOES AND DOES NOT ESTABLISH
-----------------------------------------------------------------------------------------------
DOES (on dev, pending challenge and confirmation): with replay, the writer of function-bearing bytes
and the origin of the function are recoverable on constructed populations, and label edits cannot
move the answer while byte / physics / generation edits are refused.
DOES NOT:
- say any Z80 organism discovered heredity (T020: discovered AND endogenously heritable is
  unreachable at local budget);
- work without replay: writer attribution of copier lineages is not identifiable from bytes;
- cover horizons beyond 10-200 epochs, other topologies / physics / tasks (refused UNSUPPORTED), or
  neighbour-dependent function at population scale (unit known answers only);
- rule out a parent whose output depends on the target cell only for contents other than the two
  counterfactual pre-windows (not observed; a challenge target).
The replay trust root makes ENDO vs EXT close to "read the physics path". What a spec-label reader
cannot do and this instrument does: ENV under endogenous physics, refusal of physics/byte forgery,
and origin independent of the engine's (historically mislabelled) init field.

-----------------------------------------------------------------------------------------------
7. RECOMMENDATION
-----------------------------------------------------------------------------------------------
Argus's lean: proceed to Pallas's Q3 challenge of the frozen surface (five surfaces listed in
FREEZE.md: replay divergence, counterfactual P, sufficiency label, horizon choice, forgeries that move
the answer while replaying), then the ~0.8 core-h confirmatory run. If the reviewer judges that a
replay-rooted attribution is too close to reading the engine's code path to teach the Observatory
anything, the honest alternative is to record the bytes-only non-identifiability as the C-017 result
and stop here.

-----------------------------------------------------------------------------------------------
8. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----------------------------------------------------------------------------------------------
1. Is replay a legitimate trust root for "who wrote the bytes", or does it smuggle in the answer?
2. Horizons were chosen on dev data so constructed ground truth holds. Does that make the
   qualification circular for the very populations (long-evolved) where attribution matters most?
3. Is a 1-in-5 per-class error bound a meaningful claim for a deterministic detector?
4. Is RECON (kept bytes) really "environmental reconstruction", or a construction the detector was
   built around? What second ENV construction would you demand?
5. Should "reproduced by executing the target cell's code" be ENV, as here, or ENDO with
   environmental machinery?

-----------------------------------------------------------------------------------------------
9. ARTIFACTS (branch argus/c017-t030; state on main)
-----------------------------------------------------------------------------------------------
rso/z80/{subjects,observe,assay,analysis,freeze}.py; tests/test_attribution.py (42)
rso/z80/PREREGISTRATION.md (0c7afbeea); FREEZE.md + FROZEN.json (e41fff917, cad362fa); ONBOARDING.md
rso/z80/dev/DEV_CHECK.json (+ DEV_ROWS / DEV_POWER *.jsonl.gz); rso/z80/red/{RED_EDITS.json,red_rows.jsonl}
ops/campaigns/C-017/tasks/C-017-T030/attempts/A-001/RECEIPT.json (main 9d6e9e4b9, corrected 8f80e0013)
Claim 12d0a04b4; RED/IMPLEMENTING 53c32b1e3; INTEGRATION_READY 9d6e9e4b9.

+==============================================================================================+
| END. "Not worth continuing" is a first-class answer: the bytes-only non-identifiability      |
| result stands on its own if the replay-rooted instrument is judged uninformative.            |
+==============================================================================================+
