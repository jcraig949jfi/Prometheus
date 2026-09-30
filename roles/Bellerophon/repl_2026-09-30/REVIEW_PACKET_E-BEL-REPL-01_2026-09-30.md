+==============================================================================+
| REVIEW PACKET -- E-BEL-REPL-01: independent BEE rebuild of NPE               |
|                 C-A3-INTERNALIZE, with a kill battery                         |
| Author: Bellerophon (M2 / SPECTREX5)            Date: 2026-09-30              |
| For: HITL operator + external reviewers                                       |
| Status: CLOSED -- frozen verdict DISAPPEARS (K3); kill confirmed real post-hoc|
| Self-contained: no repo access needed; every load-bearing number is inline.   |
+==============================================================================+

-----
0. SUMMARY
-----
Mandate: CWO 2026-09-30 s3 BELLEROPHON CURRENT (Aporia #1033). Pick the strongest
unresolved emergence-like signal in the fleet, rebuild it in BEE (my own engine,
not the source engine), and try to make it disappear.

Pick: Nestor's NPE C-A3-INTERNALIZE. The claim: "a lineage founded only by
non-state-free donors repeatedly comes to carry state-free competent genomes
descended from those founders". NPE: 8/144 runs against a frozen bar of 4.
("State-free" = copies itself correctly from arbitrary entry registers, not
only from the zeroed registers the environment supplies.) The selection
criteria were committed before candidates were read.

Verdict (frozen code): DISAPPEARS (K3).
- K1 no-payoff null: SURVIVES. 93/200 events vs 18/100, p = 6.6e-7.
- K4 ruler swap: SURVIVES. 86/93.
- K3 content descent: DISAPPEARS. 0/93.
In BEE, state-freedom really does emerge more when the register scaffold is
only partly available. But it is new material, not modified founder material.
A lineage LABEL alone produces the full event signature.

Nestor's own material audit in NPE (read only after my report was committed)
is ENDOGENOUS 8/8. The NPE claim is therefore not killed. Its descent part does
not transfer to BEE.

-----
1. WHAT WAS BUILT (all before production)
-----
- BEE register-world axis. Before this, BEE reset registers to zero on every
  execution.
  * CARRIED: an organism keeps its exit registers. A newborn inherits the
    registers of the occupant it overwrote.
  * RANDOM.
  * reg_zero_p: CARRIED, with a zero reset at probability p. This is NPE's
    SCHEDULE text.
  * The axis is default-off. 88 tests pass; historical plan and config hashes
    are unchanged.
  * It reached main WITHOUT a pre-merge review (a push slip, disclosed in the
    ledger). A post-merge adversarial review returned FIX: three defects and
    five mutations the tests missed. Everything was fixed, and 6/6 of those
    mutations are now CAUGHT.
- State-freedom assay rebuilt from NPE's TEXT only (no NPE code was read).
  * COMPETENT_e: executed alone from entry state e, the tape copies itself
    (>= 90% of bytes) in >= 50% of 20 trials.
  * STATE_FREE: competent from two fixed random entry vectors.
- Pilots (disclosed; none read the state-freedom of an evolved genome).
  * BEE's own spontaneous origins are ZERO_DEPENDENT 159/229; only 2 are
    STATE_FREE.
  * Founder persistence under the scaffolds:
      plain CARRIED  0/24
      p = 0.25       0/12
      p = 0.5        1/12
      p = 0.75       2/12
      p = 0.9        5/12
      ZERO           10/24
- A smoke run (seed outside the production range) showed that BEE's causal
  lineage transfers on 1-byte writes, so the primary label became the genetic
  lineage (G). K3 was added because G is itself a resemblance label.
- Prereg frozen at 74f72e805, with LF-normalised sha256 of every file. Five
  planted positive controls passed.

-----
2. DESIGN AS RUN
-----
- 100 paired seeds x 3 register worlds, same founder per pair:
  * ZERO: always zero. State-freedom earns nothing.
  * P90: zero with p = 0.9, else CARRIED.
  * P75: zero with p = 0.75, else CARRIED.
- Founders: 30 ZERO_DEPENDENT origin tapes, a quarter of a random population.
  Cell: v2 ENDOGENOUS_PARTIAL, 256 cells, 2000 ticks.
- EVENT (NPE text, with BEE's label G): at the last checkpoint with >= 1
  state-free genome, >= 80% of those genomes are carried by G, AND G holds
  >= 50% of the population.
- Kill rules (frozen):
  * K1: treatment events vs ZERO. One-sided Fisher, p < 0.05, and E_T >= 4.
  * K3: >= 50% of events must also hold when "carried" means founder CONTENT
    (>= 16/64 positions equal to the founder).
  * K4: >= 50% must hold under a second random ruler.

-----
3. RESULTS (production/ANALYSIS.json; seal 701a26ae before analysis)
-----
               events  persisting  content-events  alt-ruler  causal-L
  ZERO    100    18        84            0            11         14
  P90     100    57        73            0            52         48
  P75     100    36        51            0            36         34

- Events per persisting run: ZERO 0.21, P90 0.78, P75 0.71.
- Dose (P75 > P90) was NOT seen: p = 0.999, the wrong direction.
- Every precommitted expectation was LOST:
  * E_T expected 2..12, got 93;
  * E_N expected 0..3, got 18;
  * "K1 most likely kill": K1 held and K3 killed.

-----
4. IS THE K3 KILL REAL? (POST-HOC, labelled, after the verdict)
-----
- The positional content test cannot see SHIFTED copies. The FM detector reads
  exactly 0.250 at tick 0, so it works on real data.
- By tick 500, G covers ~0.9-0.95 of the population and founder content covers
  ~0.01.
- All 111 event runs were replayed. 111/111 reproduced the sealed records
  exactly.
- The 1,648 state-free genomes in G were scored with SHIFT-TOLERANT measures:
  * 4-gram share with the founder: median 0 (max 0.016 / 0.25 / 0.33);
  * longest common substring: median 2. The random-tape null is 1;
  * runs where >= 80% of those genomes pass any founder threshold:
    P90 0/57, P75 1/36, ZERO 2/18.
- The kill is real. The label follows cells, not material.

-----
5. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES:
- In BEE, state-free genomes emerge and dominate far more when the register
  scaffold is partial than when it is always present. This is payoff-dependent
  and ruler-independent.
- A lineage label can reproduce NPE's full internalization signature with ZERO
  material continuity.
DOES NOT:
- Kill the NPE claim. It is a different engine, and NPE passes its own material
  audit (ENDOGENOUS 8/8; ~50% of bytes attributed to L).
- Say why BEE's state-freedom arises, or why the dose runs backwards.
- Generalise beyond one BEE cell, 30 founders and 2000 ticks.

-----
6. INCIDENTS
-----
- Unreviewed engine code reached main through a state-file push. It was
  reviewed post-merge and fixed.
- The acquire-time lease token was not kept, so the lease expires on its TTL
  (Aporia #1077; Builder-Fabric friction).
- The K3 detector was validated only on synthetic records before the freeze.
  Its real-data sanity was checked post-hoc.
- Same session, a different item: Harmonia's audit showed that my E-003
  VALIDATED label rested on an undisclosed post-exposure rule. Corrected label:
  ALTERED; the verdict of record goes to the operator.

-----
7. DECISION / NEXT
-----
- The claim as stated did not survive in BEE, so nothing is promoted.
- The residue (scaffold-dependent de novo state-freedom, backwards dose) goes
  to the residual frontier (CWO 1.5).
- The descent-label hazard goes to Harmonia as a ruler-quality observation.
- The CWO NEXT (automatic mutant/falsifier transformations) applies to the
  surviving residue if Aporia judges it worth it. Otherwise RESERVE:
  generalise these controls (planted state-free/zero-dependent copiers, a
  label-vs-content descent check, and a replay gate) into BUILDER-EXPERIMENT.

-----
8. QUESTIONS FOR THE REVIEWER (please try to disagree)
-----
1. Is the positional + shift-tolerant content test the right K3, or could BEE
   state-free genomes descend from founders through total byte turnover that
   no content test can see?
2. The primary label (G) was chosen after a smoke run, and it is the label
   that failed. Was K3 a fair backstop, or should G never have been primary?
3. ZERO shows 18 events with no register payoff. What produces state-freedom
   there?
4. Does "the signature transfers without descent" weaken the NPE claim, or is
   it irrelevant because NPE passed a material audit?

-----
9. ARTIFACTS
-----
Branch bellerophon/repl-internalize-2026-09-30 @ 9c2c42938,
roles/Bellerophon/repl_2026-09-30/:
- SELECTION_CRITERIA.md (9c4a4fabe), SELECTION.md (19e758e7f)
- PREREG.md + FREEZE_MANIFEST.json (74f72e805)
- production/PRODUCTION_SEAL.json (3b2e11a3e), production/ANALYSIS.json
  (2ae8ec484)
- production/POSTHOC_K3_SHIFT.jsonl (sha256 1c82e192...)
- RESULT.md (279927367 + addendum 9c2c42938)
- tools/
Engine: prometheus/z80atlas (35b2fde55, ee82457a4, 8a2390d82).
Source claim: roles/Nestor/campaigns/npe-arc3-2026-09-28/c_a3_internalize/
(dce299ce8).

+==============================================================================+
| END. "Not worth continuing" is a first-class answer.                          |
+==============================================================================+
