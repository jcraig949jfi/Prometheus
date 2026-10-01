# W2-5: historical error autopsy of NPE interpretations (directive item E)

> Saved by Nestor from the worker's returned text. The harness refused report-file writes by subagents.
>
> The worker wrote the following directly:
> - `ERROR_DATASET.json` (58 records, with full fields);
> - `analyse_dataset.py`, `DATASET_ANALYSIS.json` and `RECORD_VALIDATION.json`;
> - `checks/`: 9 modules, `validate_on_record.py`, and `tests/test_checks.py` (37 tests, all passing).
>
> The worker was read-only outside this folder and made no git writes or world runs.

## Summary
1. **Dataset.** 58 mistaken interpretations, dated 09-01..09-30. 54 are Nestor's, 4 come from other seats. They fall into 20 classes: 15 given plus 5 new (MAV, SUM, GEN, ABS, NDP).
2. **Most common class: a ruler or guard that cannot fire, or cannot refuse (RCF).** It is the primary class in 11 records and appears in 16. It recurred 15 times after its first lesson (09-04), in a new shape each time.
3. **Next: unit mismatch.** Label-as-content, run-level label and event-as-property together cover 15 records.
   - C9-D14 stated the lesson on 09-24.
   - The anc0/L label then returned between 09-25 and 09-30, and it is in ARC3 and frontier code today.
4. **Time to detection.**
   - Wrong mechanisms die in under a day, through the seat's own loop.
   - Defects inside instruments survive 2-6 days. 11 of the 19 that lasted ≥ 48 h were caught by another seat or a fresh-context worker.
5. **Repairs.**
   - Written as running code, repairs stopped their class locally: MAV, SCH, UNW and IDA had 0 recurrences afterwards.
   - Left as prose, they moved elsewhere: RCF, LAC and SUM recurred.
6. **Sweep.** 60+ candidates, 20 of them re-read at the cited line. The worst:
   - the frozen-but-unrun x_task_gate: Stage 0 cannot exercise CD, and its provenance is keyed on oid;
   - the shared library `prometheus/z80atlas` assigns lineage by resemblance;
   - `geometry.py` pads with zeros.
7. **Also live:**
   - `archaeon/z80atlas/scheduler.py:192-198` picks a sibling control, last-wins (Z80A-D04 again);
   - X-A3-WITHDRAW's CLEAN_NULL sits at a ceiling (PERSISTS 12/12 in every arm);
   - the cosmos ps1 `scenario` is never read;
   - Ananke W-U defaults to PASS.
8. **checks/.** 9 stdlib checks and 37 tests, all passing.
   - Each check fails on its constructed defect and passes a correct input.
   - Replacing a check with a constant-verdict stub breaks at least one test, for every check.
9. **On real records** the checks re-find:
   - C9-D16;
   - the identical C9-H1R pair (60/60);
   - dossier D's 8/23 "ESTABLISHED" with 0 D0 births.

   They also reproduce X-DOSE-CURVE's LRT p = 0.4233 exactly.
10. **C-CRITICAL-MASS's own two doses still reject independence** (joint p = 0.014). The D-12 retraction therefore rests on X-DOSE-CURVE alone, which is weaker than FINDINGS says.

## 1. Dataset
All 58 records are in `ERROR_DATASET.json`. Each holds:
- the claim and its date;
- why it was persuasive;
- its classes;
- the earliest measurement that would have caught it;
- survival time, catcher and seat.

**Class keys:**

| key | meaning |
|---|---|
| SIM | similarity-as-copying |
| MAV | fidelity measured after the world's own variation operator (new; a sub-class of SIM) |
| LAC | label-as-content |
| RLL | run-level label |
| EAP | event-as-property |
| SCP | single-context-point ruler |
| PAD | padding inflation, or count-fixing geometry |
| IDA | identical arms read as a null |
| UNW | unwired intervention |
| RNG | unpaired or shared RNG |
| SCH | scheduler feedback or sibling control |
| PHT | post-hoc threshold or plug-in baseline |
| RCF | ruler or guard that cannot fire, or cannot refuse |
| CAC | cached assay |
| CMP | composite treatment |
| WOA | world-vs-organism attribution |
| SUM (new) | summary sourced from a summary |
| GEN (new) | out-of-scope generalisation |
| ABS (new) | a missing field or instrument read as a negative |
| NDP (new) | a prediction that does not discriminate, or an asymmetric verdict mapping |

Examples, in date order:

| id | claim | class | survival |
|---|---|---|---|
| E-01 | 90% identity = replication | SIM | 0.1 h |
| E-02/03 | "the detector is holding"; splice credited | SIM/MAV | 72-96 h; `births_similar_no_write` was on disk from 09-22 |
| E-04 | 1,031 spontaneous replicators | SIM/EAP | 144 h |
| E-11 | 1,031 read as a rate | SCH | 192 h; caught by a fresh worker |
| E-16 | C9 H1 NO_DETECTED_EFFECT | UNW/IDA | 8 h |
| E-17 | H2 "two nulls" | RNG/IDA | 96 h |
| E-19 | 57 P-11 survivors = replicators | EAP/RCF | 120 h; caught by another seat |
| E-31 | X-RUNAWAY share = implant sweep | RLL/LAC | 144 h |
| E-40 | Block C: half of established donors self-poison | RLL/SCP | 72 h |
| E-43 | WITHDRAW "not sorting" | LAC/NDP | 54 h |
| E-44 | X-MAT "validates" XENO | RCF/LAC | 24 h; caught by audit |

E-46 to E-51 are the Wave-1 synthesis errors caught by the red-team, at about 4 h each. One of them, E-46, was itself corrected in Wave 2 (see the Nestor ledger, N1). E-52 to E-58 are CW01, other-seat and older items.

## 2. Analysis

**Class frequency, primary / any record (median survival):**

| class | primary / any | median survival |
|---|---|---|
| RCF | 11 / 16 | 7 h |
| LAC | 4 / 8 | 21 h |
| SUM | 5 / 7 | 18 h |
| SIM | 3 / 5 | 72 h |
| EAP | 4 / 5 | 120 h |
| ABS | 3 / 5 | 3 h |
| WOA | 2 / 5 | 4 h |
| PHT | 3 / 5 | 20 h |
| CMP | 4 / 5 | 22 h |
| SCP | 2 / 4 | 33 h |
| NDP | 3 / 4 | 12 h |
| SCH | 3 / 3 | 24 h |
| PAD | 2 / 3 | 48 h |
| RLL | 3 / 3 | 72 h |
| GEN | 1 / 3 | 8 h |
| MAV | 1 / 2 | 84 h |
| UNW | 2 / 2 | 40 h |
| IDA | 0 / 2 | 52 h |
| CAC | 1 / 1 | 24 h |
| RNG | 1 / 1 | 96 h |

**Two super-families:**
- **"The ruler measures a different unit than the claim names"** (LAC + RLL + EAP + SIM/MAV): 20 of 58.
- **"The ruler cannot return the refuting answer"** (RCF + ABS + NDP): 23 of 58.

**Early vs late:**
- 25 of 58 were caught within 12 h; 19 survived ≥ 48 h.
- **Caught early:** ABS, WOA, PHT, CAC. These are mechanism errors.
- **Caught late:** EAP, RNG, MAV, SIM, RLL, IDA, PAD. These are defects inside instruments.
- Median survival by catcher: self 18 h (n = 35); fresh worker 54 h; other seat 58 h.
- The fastest catches, about 4 h each, came from a scheduled pre-release fresh-context review. That is the cheapest catcher in the dataset.
- In most late cases the catching measurement was already on disk while the claim was live.

**Did repairs reduce or move the error?** Instances made after the lesson date:

| class | instances after lesson | outcome |
|---|---|---|
| RCF | 15 (lesson 09-04) | moved |
| LAC | 5 (lesson 09-24) | moved |
| SUM | 5 | moved |
| ABS | 4 | reduced locally |
| SIM | 3 | ratcheted: each fix exposed the next weaker reading |
| CMP | 3 | recurred |
| PAD | 2 | recurred |
| PHT | 2 | reduced |
| MAV, SCH, UNW, IDA | 0 | the repair became running code |

**Reading:** a repair that became code that runs again stopped its class locally. A repair that remained a lesson moved, at programme scale, to the next code written without it.

## 3. Vulnerability sweep (today's code; ✔ = re-read at the line by the worker)

**RCF**
- ✔ **`npe-frontier-2026-09-30/x_task_gate/run_xtg.py:128-135`** (+PREREG:81-86), HIGH. Stage 0 reads the held-diff and CS in EXTERNAL arms only. There every birth is EXT, so CD = 0 by construction, and the CD ruler is never exercised. Frozen, not yet run.
- ✔ `npe-arc3-2026-09-28/x_a3_withdraw/run_wd.py:144-148`, HIGH. PERSISTS is 12/12 in GRADUAL, ABRUPT and CONTROL_ZERO, so the CLEAN_NULL sits at a ceiling.
- `c_a3_internalize/run_ci.py:124-140`, HIGH. The replay control re-applies `event()` to stored JSON.
- ✔ `roles/Nestor/lib/reset_axis.py:93-96`, MED. The self-test checks only `seen[0]`.
- `roles/Artemis/challenge/p11/verdict.py:20-22,43-47,108`, MED.
- `prometheus/z80atlas/controls.py:54`, HIGH.

**LAC / RLL / EAP**
- ✔ **`x_task_gate/run_xtg.py:70-75,104-106`**, HIGH. Provenance is set once per oid at birth, but CD, sorting and INIT follow oids that are rewritten in place.
- ✔ `prometheus/z80atlas/world.py:562-569`, HIGH. In the shared library, glin is assigned by resemblance.
- ✔ `x_a3_withdraw/run_wd.py:94-95,133-134`, HIGH.
- `x_a3_sflineage/run_sfl.py:55-61,77-79`, HIGH.
- ✔ `c_a3_internalize/run_ci.py:98`, HIGH.
- `npe-p2/x_p2_bridge/run_br.py:159`, HIGH.
- `x_mat_internalize/run_xmi.py:97-99`, MED.
- `x_a3_autopsy/run_ap.py:97-106`, MED.
- `archaeon/campaign3/c3_sfe10.py:94-98`, HIGH.
- `archaeon/wse/evolve.py:343-348`, HIGH.
- `archaeon/lineage/core.py:19-21,233`, MED.
- `archaeon/rie/world.py:84,116-136`, MED.
- `roles/Bellerophon/coupling_2026-09-24/tools/coupling_analysis.py:342`, MED.

**SIM / MAV**
- ✔ `inference_harvest_2026-09-30/forensics/map_offspring.py:59-68`, HIGH. T = p_conv + identity ≥ 0.9, with authorship dropped.
- `prometheus/z80atlas/world.py:553,582,819-830`, HIGH.
- `x_a3_autopsy/run_ap.py:94-95,117`, MED-HIGH.
- `archaeon/causal_lens/adapters/npe.py:134`, MED.
- `roles/Harmonia/science/ancestry_ruler/ancestry_ruler.py:105-133`, LOW-MED.

**PAD**
- ✔ `prometheus/z80atlas/geometry.py:27,44-48`, HIGH.
- `x_mat_internalize/run_xmi.py:201-215`, LOW-MED.
- `archaeon/z80atlas/census/copier_census.py:19,73`, LOW.

**SCH**
- ✔ `archaeon/z80atlas/scheduler.py:192-198`, HIGH.
- `prometheus/z80atlas/observatory.py:77-90`, HIGH.
- `prometheus/z80atlas/scheduler.py:436-455` and `165,197-206`, HIGH.
- `npe-arc3/delegates/accessibility/model.py:44-50`, MED.

**SCP**
- ✔ `forensics/oos_sensitivity.py:30-31`, MED.
- `x_a3_fair/run_fair.py:94-95`, MED-HIGH.
- `run_de.py:57-68`, MED.
- `run_xmi.py:194-215`, MED.
- `Artemis p11/verdict.py:43-47`, MED.

**RNG**
- ✔ `prometheus/z80atlas/world.py:261-268`, MED. The C9-D24 pattern is in the shared library.
- ✔ `prometheus/cosmos/substrates/ring.py:91` (+`regs.py:94`), MED.
- `archaeon/wse/evolve.py`, LOW-MED.
- `ensorain/e0/life.py:59-62`, LOW.
- `ares/worlds.py:121,179`, LOW.

**UNW / CMP**
- ✔ `prometheus/cosmos/planted/ps1.py:14-16`, MED. `scenario` is never read.
- VER `world.py:123-124`: still unwired.
- `x_task_gate/run_xtg.py:46-47`, MED-LOW. EXT_TG is a composite.
- `SerendipityFoundry/D8/agent_d8/experiment.py:387-395`, MED.
- Ananke `W-C/x4_evolve.py:25`, MED.
- `ensorain/wtp3/campaign3.py:513-516`, MED.

**ABS**
- ✔ `roles/Ananke/research/workers/W-U/build_table.py:36-45`, HIGH. Defaults to PASS.
- `Artemis p11/verdict.py:114`, MED.
- `ensorain/wtp2/campaign2.py:159,410`, MED.
- `primordial/soup/b6/receipt.py:28-37`, MED.
- `run_ap.py:202-213`, MED.

**Good practice worth copying:**
- x_task_gate's private SHUF RNG;
- X-MAT's bit-identical replay gate plus the dense_taint control;
- `reset_axis.with_schedule`;
- `prometheus/z80atlas/world.py:620-632 _is_self_copy`;
- Hecate's SeedSequence streams;
- Odysseus's planted answers;
- Harmonia's INDETERMINATE.

## 4. Instruments (`checks/`)
Every check returns OK, a named defect verdict, or NOT_VERIFIED. NOT_VERIFIED never counts as a pass.

| class | module.function | defect verdict(s) |
|---|---|---|
| IDA / UNW | `identical_arms.detect_identical_arms`, `detect_identical_summaries` | IDENTICAL_PER_SEED / MARGINAL / SUMMARY |
| RNG | `rng_pairing.check_rng_pairing` + `CountingRandom` | UNPAIRED / SAME_SIMULATION |
| PAD | `padding_inflation.check_padding_inflation` | PADDING_INFLATED / SENSITIVE |
| RLL | `run_level_label.check_label_holds_for_unit` | LABEL_NOT_UNIT |
| LAC | `label_vs_content.check_label_vs_content` | LABEL_EXCEEDS_CONTENT |
| RCF | `ruler_reachability.check_ruler_reachability` | UNREACHABLE / CANNOT_REFUSE / DEGENERATE; NOT_VERIFIED without a planted positive |
| RCF | `ruler_reachability.check_guard_sides_distinct` | SELF_COMPARISON / SIDES_EQUAL |
| SCP | `single_context.check_context_stability` | CONTEXT_UNSTABLE |
| SIM / MAV | `similarity_copy.check_similarity_detector` | FIRES_WITHOUT_WRITING / UNREACHABLE |
| PHT | `plugin_baseline.check_plugin_baseline` | PLUGIN_BASELINE_ARTIFACT |

**Specified but not implemented:**
- CMP: config-diff of the arms.
- UNW: a reach counter.
- SUM: generalise `report_audit.py`.
- SCH: same-seed control ids.
- CAC: re-assay with fresh seeds.

**Tests.** `python -B -m pytest -q -p no:cacheprovider checks/tests` gives **37 passed**. A mutation sweep (constant stubs in both directions) breaks at least one test for every check.

**Validation on real records:**
- C9 H1: IDENTICAL_SUMMARY on all 6 arm pairs (re-finds C9-D16).
- C9-H1R: IDENTICAL_PER_SEED (60/60).
- x_dd_establish: LABEL_NOT_UNIT on 8 of 23.
- X-DOSE-CURVE: LRT p = 0.42331, against the recorded 0.423308.
- C-CRITICAL-MASS alone: joint p = 0.014.

## 5. Ledger entry (W2-5)

**Question.** Which defect classes produced NPE's mistaken interpretations; which were caught early or late, and by whom; did repairs reduce recurrence or move it; where do the vulnerabilities live today; can the checks be automated?

**Evidence.** 58 records; analysis; 3 read-only sweeps; 9 checks and 37 tests; validation on 5 committed records.

**Result.**
- RCF dominates and recurs.
- Unit mismatch is the largest semantic family.
- Mechanism errors die within a day; instrument errors last 2-6 days.
- Code repairs held; prose repairs moved.
- Live today:
  - the x_task_gate defects;
  - BEE library resemblance-lineage;
  - geometry.py zero padding;
  - the archaeon scheduler's sibling control;
  - WITHDRAW's ceiling;
  - cosmos: an unread scenario and draws not under common random numbers.

**Confidence.**
- MEDIUM-HIGH on the class structure.
- MEDIUM on survival hours and on unverified sweep items.
- HIGH that the checks discriminate on constructed inputs.

**Strongest objection.**
- The taxonomy is post hoc.
- The dataset is censored: only caught errors appear.
- The 09-28 lessons have only 2 days of follow-up.

**Unresolved.**
- C-CRITICAL-MASS's own-data excess versus D-12.
- Unverified sweep items.
- Whether map_offspring's T changes the offspring law.

**Next.**
1. Before x_task_gate Stage 1:
   - add a Stage-0 arm that yields P-11-provenanced competent organisms;
   - key provenance on content;
   - run `ruler_reachability` on CD.
2. Re-score C-A3, SFLINEAGE and WITHDRAW with taint/orig beside anc/L.
3. Re-read WITHDRAW as saturated.
4. Notify the owners (BEE library, Archaeon, Ananke W-U, cosmos).
5. Make identical_arms, rng_pairing and ruler_reachability a pre-freeze gate.
6. Make a fresh-context review before release standing practice.
