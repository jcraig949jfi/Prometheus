# WP-1 Entry-state decomposition and the certification circularity

**Question.** The confirmed establishment effect (C-STATELESS-FFA6: fresh-state execution 0.33 -> 0.81 in ffa6)
resets registers to ZEROS. W1's COMPETENT ruler also assays donors from zeros. Is "self-poisoning" therefore
"deployment in a state unlike the selection state"? And what, exactly, in the fresh state is the machinery the
donor relies on?

**Why it matters.** Every published program soup where copying emerges resets execution state to useful values
(delegates/EXTERNAL_RESEARCH.md, point 1 of section 0). In the P2 corpus, stalled donors borrow HL = 0 from the
zero state, and their own block copy consumes it (delegates/corpus/CORPUS_ANALYSIS.md Q2-Q4). If the environment's
reset IS the copier's self-location, NPE's "establishment barrier" is the removal of an environmental scaffold.

**Existing evidence.**
- X-DD-SELFSTATE: 18/18 stalled donors copy at 0.0 after one own execution.
- Corpus Q3: resetting L/HL restores copying in 10/19 stalled donors; B/C/A/flags never do.
- X-P2-BRIDGE: with an implanted donor panel, the fresh-state effect is +0.09..+0.25 across cells.
- X-P2-REGSTATE (CARRY / ZERO / CONST / RANDOM): see its SUMMARY.json when read.

**Method (continue from X-P2-REGSTATE).**
1. **Certification sweep (LIGHT).** Re-certify the P2 corpus sample (delegates/corpus/q1_partial.jsonl) from four
   entry states: zeros, 0x5A constant, random, and "the state the donor itself leaves". Report the fraction of
   "competent" donors that are competent only from zeros.
2. **Matched-selection arms (LEASED, ~200 runs).** Run W1-style random populations where BOTH the world's reset
   and the competence ruler use constant C, for C in {zeros, 0x5A}, and a RANDOM-reset world with a
   random-entry ruler. If acquisition and establishment track the MATCH between ruler state and world state
   rather than the particular constant, the circularity is the effect.
3. **Useful-address arm.** Reset to constants that point at self (HL = own start) and partner (DE = partner
   start) vs constants that point nowhere useful (HL = DE). This is the literature's key contrast.

**Rulers.** COMPETENT at each arm's entry state (declared per arm), the S1-S5 stage chain (x_p2_bridge/run_br.py),
L2/L4 for random populations.

**Controls.** A self-test per reset policy (x_p2_regstate/run_rs.py `selftest` pattern). Planted fixtures where
the correct outcome is known.

**Resources.** Step 1 is LIGHT (~1 h, 2 processes). Step 2 needs a LEASED 10-worker pool for ~2 h. Step 3 needs
~1 h.

**Done when.** The graph holds a node per step with a declared verdict. FINDINGS says whether "self-poisoning" is
a causal class or a symptom of zero-state dependence.
