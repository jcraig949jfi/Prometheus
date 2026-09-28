<!-- DEPOSITED VERBATIM by Ananke for worker W-G; sha256(report)=72621bbfb8f4ed9c; delimited; see REPORT.provenance.json -->
W-G REPORT: does PTE contain any nontrivial retention regime? (adversarial, preregistered)

SETUP
- Namespaces: discovery 0x5EB, then confirmation 0x5EC, run once after PLAN.md was frozen (Addendum F).
- Worlds: 64 = 32 single-cue twin pairs. Twins are identical except for the sign of cue k=3. CPU, 2 threads.
- Specimens (16): 12 D-wave cells plus 4 M2 champions (4ab2ba01, fresh1, fresh2, fresh3).
- Signed effect: g = c*(a_lead - a_twin)/2. By construction g is the answer effect signed by cue k, and unsigned (chaotic) differences give a g that is symmetric about 0.
- Null: pair-wise sign flips, 20000 permutations. Holm correction at alpha 0.01 within each family.
- Levels, as operationalised in the plan:
  - L1 PRESENT: at least 4 of 32 pairs differ bitwise at the end of trial k+2.
  - L1.5: a paired decoder on the twin difference (signed trace or not). Reported, not a level.
  - L2 DECODABLE: single-world decoders D1 (threshold) and D2 (history-aware: regresses out the known targets of the other trials). Statistic is the maximum over lags j = 2..6. Family of 32.
  - L3 EFFECTIVE: statistic is the maximum over j = 1..6 of |sum g| + |sum y*g|. Family of 16.
  - L4 AVAILABLE: interventions applied identically to both twins after trial k+1, so they cannot write the cue sign:
    - P1 BLANK: all later inputs set to 0.
    - P2 PING: a weak, shared impulse (amplitude/4).
    - P3 CLEAR_S0: the readout register S0 wiped at every site.
    - P4 CLEAR_FAST: all S, inbox and in-flight state wiped; only w, Kp, r and E survive.
    - P5 RELOC: a sign readout moved to S_d at the actuator or at the sensor.
    - Family of 80 tests. "L4-dyn" means any of P1-P4.
- Mechanism: heal tests (copy the lead's carrier X into the twin), frozen or dynamic form, and a history-coefficient ratio (does the store integrate every cue?).
- DECISION RULE: YES iff, in 0x5EC, some specimen has L3 or L4-dyn after Holm, is not classed as chaotic, its controls behaved, and the same statistic had the same sign in 0x5EB.

CONTROLS (hand plants; M2 physics widened to state_dim 4 and prog_len 24; unadjusted alpha 0.01)
All five behaved as preregistered in both namespaces.
- C-NEG (latch overwritten by the next cue): null at every level, g == 0 under every probe.
- C-INT (S1 integrator of all inputs): L1, L1.5 and L2 fire (D2 0.81 / 0.70). L3 and P1-P4 give g == 0 exactly. RELOC fires.
- C-EFF (S0 integrator): L3 fires (p 0.0034 / 0.0038) and BLANK fires (p 4e-4 / 1.5e-4).
- C-AVL (latch in S0; integrator hidden in Kp via WIMM, used only when S0 == 0): normal-operation L3 gives g == 0 exactly, while CLEAR_S0 and CLEAR_FAST fire (p 4e-4 / 1.5e-4). The L4 instrument therefore detects a latent store that normal operation never expresses.
- C-CHAOS (hashed state added to the readout): L1 32/32 and answers differ unsigned in up to 62% of pairs, yet L1.5, L2, L3 and L4 are all not significant.
- Guards G1/G2/G3 (including probe schedules) passed in 42 of 42 runs.

VERDICT PER SPECIMEN (0x5EC; discovery agrees unless noted)
- No specimen has L3 or any L4 probe (P1-P5): every adjusted p equals 1.0, in both namespaces.
- Of the raw probe statistics, only e79e72df BLANK (raw p 0.022, 0x5EB) was below 0.1, and it did not replicate.

| Specimen | L1 | L1.5 | L2 | L3 | L4 | Class |
|---|---|---|---|---|---|---|
| 023539c4, feadc823 (MAJ); 223acaee, a8f4ea11 (RELAY); 67ddd858 (HOLD); M2 4ab2ba01, fresh1 | no (merge within 1 trial) | no | no | no | no | none |
| f7e62fe3 (RELAY) | persistent 32/32 | yes | YES, both namespaces (D2 0.953 / 0.906, adj 0.0016; w_sum) | no | no | ACCUMULATION in w |
| 0ad7dc00 (HOLD) | persistent 30/32 | yes | no (D1 adj 0.0105 in 0x5EC: a borderline miss) | no | no | two independent inert stores |
| 6a47bd68 (HOLD) | persistent 28-30/32 | yes | no | no | no | STATIC store in S, not single-world decodable |
| 5673ea4e, 544f3d24 | yes; slow natural merge | no | no | no | no | CHAOTIC |
| 9e72f9b6 | yes | no | no | no | no | CHAOTIC |
| e79e72df | yes | yes in 0x5EB (0.003), NOT in 0x5EC (0.39) | no | no | no | CHAOTIC in 0x5EC |
| fresh2 | persistent 32/32 | yes | 0x5EC only (D2 0.719, adj 0.0016; 0x5EB adj 0.76, so unreplicated) | no | no | see below |
| fresh3 | persistent 32/32 | yes | no | no | no | see below |

- f7e62fe3: the history coefficients are the same sign for every trial, and the ratio of other-trial to cue-k coefficients is 0.96-0.98. w_sum is roughly a constant plus about 36 times the sum of all cue targets.
- 0ad7dc00: S and Kp each keep a difference alone after the other is healed. The Kp difference is about -300 (times c), negative in 28 of 28 pairs.
- 6a47bd68: the residues (c*d = 5, 7 or 22) sit at the decay_shift-3 floor and are all positive.
- fresh2 and fresh3: answers differ in 15-38% of pairs, but g is unsigned. My class rule labels them REGENERATION because the paired decoder is significant; the anatomy below shows they are better described as a signed w offset driving chaos.

ANSWER: NO nontrivial retention regime among these 16 champions.
- The decision rule was met by no specimen, with every control valid.
- L2-only retention (f7e62fe3; fresh2 unreplicated) is "trace, not memory" under the preregistered rule.

MECHANISMS (exploratory, 0x5EB, explore.py; post hoc)
- f7e62fe3: the w trace is a frozen additive offset (identical at k+2 and k+6), including w elements at the actuator site. With everything except w healed, the difference stays confined to w. Under blank, ping, readout wipe and fast-state wipe the twins never answer differently (g == 0 exactly). Kind: environmental accumulation. The sensor writes routing weights on every cue, so w is a history integral, and it is behaviourally inert.
- fresh3 (and fresh2): the w scar is exactly +8 (times c) at the sensor site in 32 of 32 pairs, which is signed. With everything except w healed, the fast carriers re-diverge within 2 trials and 4-9 answers per trial differ, with sum g near 0.
  - The signed w write is READ: it perturbs routing and seeds chaotic divergence.
  - The read scrambles the sign, so the effect is interference, not memory.
  - Healing w alone does not merge the twins either, so the fast-state chaos may also sustain itself.
  - The Kp difference in fresh3 is inert.
- Summary of kinds found: accumulation (f7e62fe3 w), static quantisation floors (6a47bd68 S), independent self-sustaining S and Kp stores (0ad7dc00, e79e72df), and chaos regenerated from a plastic scar (fresh2, fresh3). There is no case of true trial-specific storage that is ever expressed.

WHAT FAILED OR SURPRISED ME
- Class-rule defects found in discovery and fixed before confirmation (they affect class labels only, not the decision):
  - F1: the heal test credited stores for merges that happen anyway (544f3d24).
  - F2: the accumulation ratio is meaningless when no single-world code exists.
- F2's 0.75 gate then mislabelled the integrator controls in 0x5EC (in-sample accuracy 0.72) as "specificity undetermined". The class labels are descriptive only.
- The strongest trace in PTE, f7e62fe3's w, includes elements at the actuator site, and still no cue-blind intervention (including wiping every fast carrier) turns it into a signed answer.
- The e79e72df paired signal did not replicate, and fresh2's L2 appeared only in 0x5EC. Single-namespace decoder hits in PTE are fragile.

DISAGREEMENTS
1. PTE_ENGINE_CARD / SYNTHESIS ARC2 "written-but-never-read scars ... with no effect": wrong for fresh2 and fresh3. Their w scar is read. It regenerates divergence that changes 4-9 answers per trial, but in no consistent direction. The correct label is "read but sign-scrambled (interference)". The label does hold for f7e62fe3, 0ad7dc00, 6a47bd68 and e79e72df, even under interventions.
2. ARC3_PRIORITIES T-ENV-1 note ("if T-RET-2 closes retention, PTE lacks a persistent substrate by construction"): not supported.
   - Plants C-EFF and C-AVL show that PTE physics supports persistent, usable retention: L3 in S, and L4 through a Kp/WIMM store that survives a wipe of all fast state. That was shown at M2 physics widened to state_dim 4; C-AVL fits the 16-line program length exactly.
   - f7e62fe3's w is itself a persistent store.
   - The NO is a fact about what evolved under tasks that never reward cross-trial memory, not about the substrate.
3. W-E / synthesis "f7e62fe3 w-integrator (exploratory)": confirmed as L2, preregistered and replicated (D2 adj 0.0016 in both namespaces). It should be called an accumulation trace (every cue weighted equally), not retention of cue k. It fails L3 and L4.
4. W-E "frozen" scars:
   - f7e62fe3: frozen, confirmed.
   - 0ad7dc00: the full difference is not frozen (frozen fraction 0.03). S and Kp each hold a self-sustaining but changing difference.
   - W-E's claim that e79e72df carries a signed trace did not replicate in 0x5EC.

PROPOSED FOLLOW-UP THREADS
- T-SI-SCAR: redefine it on fresh3's single +8 sensor w-write. It is the only case where a signed plastic write demonstrably drives later behaviour, via chaos. Question: is the effect's direction ever recoverable when conditioned on routing state?
- T-RET-EVO: evolve under a task that rewards cue k at trial k+2 (1-back or n-back) at M2 physics, with C-AVL/C-EFF as reachability controls. This tests whether a retention regime is reachable, rather than merely absent in champions selected on current tasks.
- Close SI01 for these champions only, and keep T-ENV-1 open on a different rationale than "no substrate".
- Instrument: fix F2 (require D2 held-out significance, not an in-sample 0.75, before computing the ratio). Add a heal-all-but-X test to the standard census; it separated "inert", "self-sustaining" and "regenerates chaos" where single heals could not.

ARTIFACTS (roles/Ananke/research/workers/W-G/)
- PLAN.md: v1, plus Addendum F frozen before 0x5EC.
- LOG.md.
- Code: wg.py, summarize.py, explore.py.
- out/0x5eb/, out/0x5ec/: per-specimen JSON.
- out/0x5eb_summary.json, out/0x5ec_summary.json.
- Logs: out/disc_*.log, out/conf_*.log, out/explore_0x5eb.*, out/freeze_sha256.txt.
