<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-C; sha256(report)=2838bb1837be8810; delimited; see REPORT.provenance.json -->
W2-C REPORT: mutation / metamorphic testing of PTE experimental semantics
Question: would the PTE pipeline detect a corrupted experiment?

0. WHAT WAS BUILT (all under roles/Ananke/research/harvest/wave2/W2-C/)
- pte_mut/operators.py: 14 mutation operators. Each one is a context manager that monkeypatches prometheus.ananke attributes (engine.World methods, assays.evaluate/twin_assay, envs.build/score/per_trial, lens_swap.run_arms, search.H_int) and restores them on exit, also on exceptions. It never edits a file. Each operator states its metamorphic relation (MR). There are two layers: engine (the World runs different physics or IO than recorded) and protocol (arms, seeds, labels or scoring are wired wrongly).
- pte_mut/stages.py: the real pipeline entry points, each reduced to (verdict, numeric, alarms, World fingerprints):
  - held: the real search.evolve with a tiny spec and a population seeded with the fixture genome, so the champion is the fixture; then campaign.classify and anomaly_flags.
  - controls: assays.run_controls, then causal_label.
  - plant: campaign.plant_viability.
  - lens_swap: mixture_scan in single mode with frozen census, follow census, and swap_rel REL4 on the site and channel arms.
  - report: report.build over the assembled rows.
  - oracle: the test_conformance checks.
- pte_mut/score.py: expectations and classification. pte_mut/fixtures.py: the fixtures. run_score.py: the driver.
- pte_mut/guards.py: the proposed standing gate (G0-G12). run_guards.py produces the guard score.
- Tests: tests/test_pte_mut.py (43), tests/test_guards.py (15), tests/test_causal_label_competence.py (1 plus 1 strict xfail). Result: 59 passed, 1 xfailed.
- Outputs in out/: mr_spec.json (expectations written BEFORE any run; table sha256 00adaf2f3e899a48...), baseline.jsonl, results.jsonl, score_cells.json, score_table.md, score_summary.json, guard_score.json.

Fixtures (CPU only, M = 64 held worlds, 8 trials unless stated):
- relay64: relay_flood, 8x8 torus r1, RELAY d2 (2 hops).
- hold64: hold_latch (local).
- echo: echo_hold at c1b_echo_physics (bit only in flight, timing-tuned).
- relay_dirgraph: relay_flood on a directed random graph (k = 3).
- xor_hp: H-PLANT p_xor at run_xor X0/ENV0.
- c1_relay: C1 b059e735 champion.
- c1_maj: C1 88a1a041 champion.
- sel_random: 16 pre-screened partially working mutants of relay_flood, for real selection.
- Cut before any mutant ran, based on baseline cost only: flip_hp, c1_hold, and the controls/lens stages for c1_relay.

Classification rules:
- KILLED(A): a new alarm state appeared (self-detection; no clean run needed). Alarm states are anomaly flags, NOT_APPLICABLE, UNDEFINED/IDENTITY-BROKEN, NOT_ELIGIBLE, conformance failure, or an exception.
- KILLED(D): the verdict differs from the clean baseline, with no alarm. This is caught only by differential replication.
- EQUIVALENT: no change, and either (a) the worlds and the reported numbers are bit-identical, or (b) the pre-declared expectation was "invariant".
- SURVIVED: no change, no alarm, and the expectation was "change" or "alarm_only".
- UNRESOLVED: no change, and the expectation was "unknown".

1. MUTATION-SCORE TABLE (K-A = KILLED(A), K-D = KILLED(D), EQ, SURV, UNR, . = not run)

Held stage

| operator | relay64 | hold64 | echo | dirgraph | xor | c1_relay | c1_maj | sel |
|---|---|---|---|---|---|---|---|---|
| swap_labels | K-A | EQ | K-A | . | K-A | K-A | K-A | . |
| duplicate_condition | K-A | EQ | K-D | . | K-A | K-A | K-A | . |
| disable_channel | K-D | EQ | K-D | . | K-D | K-D | K-D | . |
| control_ignored | K-A | EQ | K-D | . | K-A | K-A | K-A | . |
| freeze_state (S frozen after T/2) | SURV | SURV | SURV | . | SURV | SURV | K-D | . |
| randomize_source | SURV | EQ | K-A | SURV | SURV | K-D | K-D | . |
| reverse_edges | EQ | EQ | EQ | SURV | EQ | EQ | EQ | . |
| alter_timing (lat+1, jitter+1) | SURV | SURV | K-D | . | SURV | UNR | K-D | . |
| sever_search_ruler | K-A | K-A | K-A | . | K-A | K-A | K-A | . |
| reuse_selection_seeds | SURV | SURV | SURV | . | SURV | SURV | SURV | SURV |
| drop_mirror | SURV | SURV | SURV | . | SURV | SURV | K-A* | . |
| permute_seeds | EQ | EQ | EQ | . | EQ | EQ | EQ | . |
| silent_sensors | K-D | K-D | K-D | . | K-D | K-D | K-D | . |
| invert_sign | K-A | K-A | K-A | . | K-A | K-A | K-A | . |

Controls, plant, lens_swap, report and oracle stages

| operator | ctl:relay64 | ctl:echo | plant:relay64 | plant:hold64 | plant:dirgraph | lens:relay64 | lens:hold64 | lens:echo | report | oracle |
|---|---|---|---|---|---|---|---|---|---|---|
| swap_labels | K-A | K-A | K-D | EQ | . | SURV** | K-D | K-D | K-A | . |
| duplicate_condition | K-A | K-A | EQ | EQ | . | K-A | K-A | K-A | K-A | . |
| disable_channel | K-A | K-A | K-D | EQ | . | K-A | EQ | K-A | K-A | K-A |
| control_ignored | K-A | K-A | EQ | EQ | . | . | . | . | K-A | K-A |
| freeze_state | SURV | SURV | K-D | K-D | . | SURV | SURV | SURV | K-D | K-A |
| randomize_source | SURV | K-D | SURV | EQ | SURV | K-D | EQ | K-D | K-A | K-A |
| reverse_edges | EQ | EQ | EQ | EQ | SURV | EQ | EQ | EQ | SURV | K-A |
| alter_timing | SURV | SURV | SURV | SURV | . | K-D | SURV | K-A | K-D | K-A |
| sever_search_ruler | . | . | . | . | . | . | . | . | K-A | . |
| reuse_selection_seeds | . | . | . | . | . | . | . | . | SURV | . |
| drop_mirror | SURV | SURV | SURV | SURV | . | K-A | K-A | K-A | K-A | . |
| permute_seeds | UNR | UNR | EQ | EQ | . | EQ | K-D | K-D | SURV | . |
| silent_sensors | K-A | K-A | K-D | K-D | . | K-A | K-A | K-A | K-A | K-A |
| invert_sign | K-D | SURV | K-D | K-D | . | K-A | K-A | K-A | K-A | . |

Totals over 191 cells:
- KILLED(A) 68, KILLED(D) 37, EQUIVALENT 36, SURVIVED 47, UNRESOLVED 3, FRAGILE 0.

Per stage:

| stage | K-A | K-D | EQ | SURV | UNR |
|---|---|---|---|---|---|
| held | 27 | 18 | 17 | 24 | 1 |
| controls | 10 | 2 | 2 | 8 | 2 |
| plant | 0 | 8 | 11 | 7 | 0 |
| lens_swap | 15 | 7 | 6 | 5 | 0 |
| report | 9 | 2 | 0 | 3 | 0 |
| oracle | 7 (of 7 engine operators) | 0 | 0 | 0 | 0 |

Footnotes:
- * The c1_maj drop_mirror kill is spurious: TRAIN_HELD_GAP fired from a 2-world training estimate in the tiny spec. Read it as SURVIVED.
- ** Equivalent in substance: the baseline census is a symmetric MIXTURE/CHANCE (fS .40 vs fC .44), so swapping site and channel cannot change it. It is classed SURVIVED only because the numbers moved.

Where the self-alarms come from (new alarms in KILLED(A) cells):

| stage | alarm | count |
|---|---|---|
| controls | NOT_APPLICABLE (the existing no-op guard) | 55 |
| controls | CAUSAL_INCONCLUSIVE | 8 |
| oracle | conformance failure | 34 |
| held | TRAIN_HELD_GAP | 13 |
| held | COMPETENT_WITHOUT_COMM | 8 |
| held | ANTI_CORRELATED | 6 |
| lens_swap | REL4 NOT_ELIGIBLE | 18 |
| lens_swap | census UNDEFINED | 16 |
| lens_swap | census IDENTITY-BROKEN | 9 |

The held-stage self-alarms are anomaly flags: advisory "flags, not verdicts". Nothing blocks on them.

2. FINDINGS
(Each finding has a tag ([V] verified by me with a check, [I] inferred), a confidence, the strongest objection, and what remains unresolved.)

F1 [V, high]. A corrupted experiment that kills the signal reads as a legitimate NULL.
- silent_sensors and disable_channel at the held stage: SIGNAL True -> False in 7 of 7 and 5 of 5 comm fixtures, with ZERO self-alarms (all KILLED(D)).
- The pipeline cannot tell "physics or search cannot do it" from "the experiment was broken".
- This matters for the XOR/FLIP/multi-hop NULL interpretations (H6).
- Check: run_score.py mutants; out/score_cells.json keys silent_sensors|held|* and disable_channel|held|*.
- Strongest objection: a NULL is a NULL; replication would catch it. Answer: C1 never re-runs NULL cells, so in the record differential detection does not exist.
- Unresolved: whether any recorded C1 NULL coincides with a guard alarm (Q3).

F2 [V, high]. causal_label has no competence precondition.
- invert_sign on echo: the normal arm's accuracy is 0.0 and the label stays NOT_SUPPORTED, with no alarm.
- alter_timing on echo: normal falls to .523 and the label stays NOT_SUPPORTED.
- freeze_state on relay64: CAUSAL_SUPPORT is kept while normal drops by .25.
- A broken adjudication run reports a SCIENTIFIC claim instead of INVALID.
- Patch: patches/causal_label_competence.SEMANTIC.diff, with tests/test_causal_label_competence.py. The test is a strict xfail on current code and passes on the scratch copy.
- It changes no C1 D label: all 12 C1 adjudications have normal >= .60 [V, row scan].
- Objection: wave D only adjudicates promoted cells, which are competent by construction. Answer: the adjudication RUN itself is never checked; corruption inside it is invisible.

F3 [V, high]. The held-out disjointness rule (Ares) is not enforced anywhere.
- reuse_selection_seeds survives in 8 of 8 held cells and in the report. There is no assertion that held seeds and selection seeds are disjoint.
- On the plant fixtures the verdict is legitimately unchanged (there is no selection).
- On sel_random the same champion was chosen, so this instance showed no inflation. Confidence on the size of the inflation is low.
- Consequence scale from C1 rows [V]:
  - champ_train_final - held: mean +.018, median +.013; 72.6% positive (n = 678).
  - Adding the mean gap would push 35 non-SIGNAL rows over lo99 > .55; adding each row's own gap, 39.
  - This is crude: train_final is on 16 worlds.
- Unresolved: the false-SIGNAL rate at real C1 scale (Q1).

F4 [V, high]. Freezing state mid-run is invisible to the labels.
- freeze_state: pooled held accuracy drops .25-.27 and lo99 drops about .31, yet SIGNAL, COMM_DEPENDENT and the causal labels are unchanged in 6 of 7 held, 2 of 2 controls and 3 of 3 lens cells.
- The verdicts see only pooled accuracy; there is no per-trial or time-homogeneity statistic.
- This is a blind spot, not an equivalent mutant: half the trials are dead.
- Guard G12 catches it once tightened (see F9).

F5 [V, high]. The irrelevant_channel control is exempted from the no-op guard by an assumption that lives only in the code.
- The comment reads "applied by construction".
- Under control_ignored (the engine ignores every switch), run_controls on relay64 reports irrelevant_channel RAN with acc 1.000 = normal, while the 7 other controls are correctly NOT_APPLICABLE.
- Check: results.jsonl key control_ignored|controls|relay64, raw controls.
- Objection: causal_label does not use irrelevant_channel. True; it remains a reported measurement that cannot be shown to have been applied.

F6 [V, high]. Only the existing no-op guard and the lens identity check give real self-detection. Both sit outside the path that produces C1 labels.
- run_controls catches duplicate_condition and control_ignored by itself (K-A in 4 of 4).
- But COMM_DEPENDENT comes from search.evolve's held block, whose zero_comm arm has NO no-op guard. There, the same corruptions are caught only by advisory flags or differentially.
- Lens: the census identity check and REL4 eligibility catch duplicate_condition and drop_mirror in 6 of 6.

F7 [V, high]. The forced zero_comm control (Wave-1 item 0.1) makes the common-random-numbers design untestable through it.
- permute_seeds (control arms on other worlds) is EQUIVALENT in every held and plant cell. The cause: zero_comm is exactly .5 in every pair, whatever the world.
- The same degeneracy makes drop_mirror verdict-equivalent at held and plant.
- The mirror is a variance and exactness device; SIGNAL stays statistically valid without it.
- Guard G0 flags the degenerate control on every relay baseline.

F8 [V, medium]. Engine-level corruptions are caught by the conformance tests, which is a guarantee of the code, not of the run.
- The oracle stage catches 7 of 7 engine operators.
- It cannot see protocol operators (7 of 14) or corruptions in recorded configuration: physics recorded != physics executed is caught only if the bug is in engine code.
- alter_timing survives at held, plant and controls on timing-robust specimens. That is expected for the verdict, but there is no provenance alarm.

F9 [V, high]. The proposed guards turn 13 of 14 operators into self-alarms.
- Guard score (out/guard_score.json; held relay64 + hold64, plant relay64): every operator raises a new guard alarm on held relay64 except randomize_source.
- On hold64, disable_channel correctly raises nothing (equivalent: hold_latch never emits).
- Each guard has a must-fire test (tests/test_guards.py).
- G12 gave a false positive on a 4-world training batch and was tightened: it now needs >= 16 worlds and >= 90% of the worlds that changed in the first half to go silent in the second. Baselines and freeze_state were re-run (logged in guard_score.json).
- Unresolved: an in-situ guard for packet provenance (randomize_source). Today only the conformance tests catch it.

F10 [V, medium]. Several survivors are equivalent mutants. I corrected my own pre-declared expectations rather than count them as findings.
- randomize_source and reverse_edges on flood plants: relay_flood and the XOR plant spread the bit everywhere, so where a packet starts and edge direction barely matter (dirgraph acc -.03 to -.07). "comm" was the wrong property; "location-dependent" is the right one. The one-hop C1 champions ARE killed, differentially only.
- alter_timing on xor_hp: I expected "change"; the plant is timing-robust at delta 8. Equivalent.
- reverse_edges on ring/torus/global: equivalent, 12 of 12 EQ.
- The report-stage SURV cells for permute_seeds and reverse_edges are equivalent (nothing upstream changed). The report SURV for reuse just propagates F3.

F11 [V by code, low impact]. run_controls' env_permutation null is computed on worlds that are not the evaluated worlds.
- It builds World(..., seeds) with ws = seeds; evaluate shares ws within each mirror pair. So odd worlds in the null have different physics draws from the normal arm.
- Not quantified on lossy physics (Q8).

3. PROPOSED FIXES

| fix | type | status |
|---|---|---|
| causal_label competence precondition | SEMANTIC (frozen C1 function); apply for C2+ only | patches/causal_label_competence.SEMANTIC.diff (scratch copy scratch/campaign_patched.py); tests/test_causal_label_competence.py; no C1 label changes |
| Promote pte_mut/guards.py to prometheus/ananke as an additive, observe-only module | NEUTRAL | runners must call it and write INVALID rows on any alarm except G0; tests/test_guards.py |
| Remove the irrelevant_channel exemption once a distractor-delivery counter exists in telemetry | NEUTRAL engine telemetry plus guard change | no diff yet |
| Add a per-trial accuracy profile to held output (closes F4 at the ruler level, beyond G12) | SEMANTIC for new preregs | no diff yet |

4. PROPOSAL: a standing mutation gate before any PTE prereg is frozen
1. The prereg declares its evidence-bearing labels and controls. For each one it names the operator(s) it must detect, for example:
   - COMM_DEPENDENT: disable_channel, control_ignored, duplicate_condition;
   - CAUSAL_SUPPORT: freeze_state, alter_timing on a timing plant, invert_sign;
   - carrier census: drop_mirror, duplicate_condition, swap_labels on an ASYMMETRIC positive control.
2. Run pte_mut on the prereg's own entry points and on known-answer plants with the relevant properties. mr_spec.json (the expectations) is committed and hashed before the run. The full matrix costs about 20-25 CPU-minutes at M = 64.
3. Freeze is refused unless:
   - (a) every declared label is KILLED(A) by its designated operator on a positive control. KILLED(D) is not enough: production has no clean run.
   - (b) every SURVIVED cell is either fixed, or argued EQUIVALENT with a written check, as in F10.
   - (c) no FRAGILE cells.
   - (d) a control whose designated mutant is EQUIVALENT on the positive control is a "control that cannot fail" and must be replaced before freeze. This would have caught zero_comm in C1.
4. Guards G1-G12 run fail-closed in every runner. G0 (degenerate control) is printed in the freeze packet.
5. The score table plus the mr_spec hash goes into the freeze packet. Any change to the runner re-runs the gate.

5. DISAGREEMENTS WITH WAVE 1 / THE PRINCIPAL
- PTE_INSTRUMENT_GAPS ranks "identity audit of controls" as a control-battery fix. The larger gap: the label that matters (COMM_DEPENDENT) consumes search.evolve's UNGUARDED zero_comm arm. run_controls' no-op guard already works (F6). The audit should name evolve's held block.
- The audit treats zero_comm forcedness as a ruler problem only. It is also a testability problem: it makes the CRN-pairing and mirror design elements unfalsifiable at held (F7).
- The irrelevant_channel guard exemption is an unaudited assumption encoded only in code (F5); no Wave-1 product lists it.
- H6 ("search, not physics, bounds PTE"): the null side of every claim lacks a broken-experiment check (F1). NULLs need guards before being read as search-limited or physics-limited.

6. NEXT QUESTIONS (ranked)
1. At real C1 search scale (pop 96, M_final 16), how much does reuse_selection_seeds inflate held accuracy, and what is the false-SIGNAL rate? (Bounded GA, needs explicit authorization.)
2. Build an in-situ provenance guard for randomize_source (H-INST ProvenanceWorld tags as a guard) and test that it fires on one-hop champions.
3. Re-run the held evaluation of C1 NULL cells (XOR/FLIP/multi-hop) under the guards: do any raise G3/G11/G12 (a broken experiment rather than a NULL)?
4. Add a distractor-delivery counter so irrelevant_channel's applied-ness can be checked, then drop the exemption.
5. Specify a per-trial-time homogeneity statistic as a ruler for held/controls (closes F4 properly) and find its false-alarm rate on C1 champions.
6. How reliable is TRAIN_HELD_GAP? It gave a spurious kill with a 2-world training estimate; check its calibration at M_final 16 against the C1 gap distribution.
7. Add an asymmetric positive control to the lens gate: swap_labels is undetectable by construction on a symmetric MIXTURE baseline.
8. Quantify F11 (the env_permutation null on non-mirrored worlds) on lossy, jittered physics.

7. INFERENCE LEDGER
(question | evidence | result | confidence | strongest objection | unresolved | next)
- Do signal-killing corruptions alarm? | silent_sensors/disable_channel held | NULL with no alarm | high | replication would catch it | C1 NULL cells under guards | Q3
- Is adjudication guarded against a dead normal arm? | invert_sign/alter_timing on echo controls | NOT_SUPPORTED with normal 0.0/.52 | high | only promoted cells are adjudicated | none on C1 (all normal >= .60) | apply patch for C2
- Is Ares disjointness enforced? | reuse_selection_seeds 8/8 SURV; C1 gap +.018 | not enforced | high (rule) / low (magnitude) | the plant fixture has no selection | inflation at C1 scale | Q1
- Do labels see half-dead runs? | freeze_state 11 SURV | no | high | lo99 still > .55 legitimately | ruler design | Q5
- Can an unapplied control be reported RAN? | control_ignored on relay64 | irrelevant_channel RAN 1.000 | high | not used by causal_label | telemetry counter | Q4
- Where does self-detection live? | alarm tally | no-op guard + lens identity + advisory flags | high | flags are designed to be read | enforcement | gate s4
- Is CRN/mirror testable via zero_comm? | permute_seeds/drop_mirror EQ at held | no (degenerate control) | high | the mirror is only a variance device | - | gate s4 item 3(d)
- Do guards close the survivors? | guard_score.json | 13/14 operators fire | high | G12 needed tightening | randomize_source | Q2
- Which survivors are equivalent? | flood plants, symmetric tables, xor timing | 4 classes equivalent | medium | my expectation errors were corrected after the fact | - | -
- env_permutation provenance | code read | non-mirrored ws | medium | low impact | magnitude | Q8

8. COMPUTE
- CPU only (CUDA_VISIBLE_DEVICES=-1, torch.cuda.is_available() asserted False), 1 thread per process.
- Baselines 395 s; mutants 1189 s; guard score 144 s; tests, probes, G12 re-run and two discarded sel_random baselines about 200 s.
- Total about 1930 s, about 0.54 CPU core-hours: slightly OVER the 0.5 cap. Fixture cuts were made from baseline costs before any mutant ran, but the guard run and test re-runs pushed it over.
- No GPU, no leases touched, no files outside W2-C edited, no git writes.
