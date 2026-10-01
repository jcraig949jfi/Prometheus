<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/wave2/W2-A2; sha256(report)=39eae18287966e97; delimited; see REPORT.provenance.json -->
# W2-A2: executable-semantics audit of the PTE experiment layer

**Worker:** W2-A2 (Opus), Ananke Wave 2, 2026-10-01, 00:24Z to 00:55Z.
**Worktree:** F:/Prometheus-worktrees/ananke-base-role at fd631acb2. Everything I wrote is under roles/Ananke/research/harvest/wave2/W2-A2/ (checks/, tests/, patches/, scratch/).
**Constraints followed:** CPU only (CUDA_VISIBLE_DEVICES=-1, torch.cuda.is_available() False, 2 threads). No search, no git writes, no edits outside my directory.

**Files read in full:**
- envs.py, search.py, campaign.py, assays.py, report.py, analysis_a0.py, c1b.py, c1b_run.py, launch.py
- the experiment-relevant parts of rng.py and physics.py
- lens.py and oracle.py were only skimmed. They are instruments and the reference engine, and no C1 label path runs through them.

**Specs read:** PREREG_PTE_C1 (all), PREREG_PTE_C1b (all), ANALYSIS_PLAN_C1_A0, C1_REPORT, C1_ERRATA, DESIGN s7, the Wave-1 handoff, H-IMPL/REPORT, and parts of H-PLANT.

## 1. Data-flow graph: how a cell becomes a C1_REPORT claim (file:line)

**Spec generation**
- campaign.main (822-883) builds specs with wave_A0 (371), wave_A (389), wave_B (534), wave_B2 (619), wave_C (658), wave_D (722) and wave_E (740).
- Each spec gets cell_id = sha(wave, kind, physics, env, search, search_seed, extra) (178).
- run_wave (773) skips ids already in store.done (779-782), then calls run_cell (237).

**kind == evolve: search.evolve (319)**
- GA stream: g = default_rng(search_seed) (322). It drives random_genomes (323), parent picks, crossover and mutate (349-357).
- Train worlds for each generation: world_seeds(H(search_seed, TRAIN_NS=0x7A1, gen), M=8) (328), which is H(base, 0xA11A, m) (assays 43-45).
- assays.evaluate (48):
  - Physics seed: ws = the lead seed of each mirror pair (56).
  - envs.build (57): the env RNG is default_rng(H(lead, ENV, family_id, variant)) (envs 154). It sets positions, coins, flips and the mirror sign (152-153).
  - The batch is tiled across genomes, so every genome sees the same worlds (59-63).
  - acc = envs.score (89; envs 227-232): S0 == 0 scores 0.5; only scored trials count.
  - sens_act = mean sign((S0_lead - S0_mirror) * y_lead) at scored readouts (79-84).
  - sens_any = fraction of sites that differ between mirror twins, averaged over all ticks (76-78, 85).
- Fitness f = acc + 0.10*max(sens_act, 0) + 0.02*sens_any (332).
- Ranking: argsort(-f, stable) (340). The 4 elites carried forward are the top 4 by f (351); parents are the top 25% by f (349-350).
- Final population: re-evaluated on FINAL_NS=0xF1A worlds, M_final=16 (359-360).
- Champion = np.argmax(final-train accuracy) (362). On a tie, the first index wins, which is an elite in f order (351).
- Held-out evaluation: hseeds = H(search_seed, HELD_NS=0x4E1D), M_held=64 (365).
  - rh = champion on hseeds (366). rz = the champion with zero_comm on the SAME hseeds (367).
  - pair_acc gives pair_ci (bootstrap seed 0, 2000 resamples) (371-372); acc, lo99, comm_delta and its lo99 go into result.held (380-382).
  - twin_assay runs on hseeds[:16] (373). Its physics uses the raw seeds, not the lead seeds (assays 255).
- campaign.run_cell also adds plant_viability with seeds H(search_seed, 0x9147), 32 worlds (246, 285-298).

**Other kinds**
- transfer (268-278): the frozen champion on H(search_seed, 0x7F7F), 64 worlds, plus zero_comm. There is NO twin, NO plant and NO gen0.
- adjudicate (261-267):
  - run_controls on H(search_seed, 0xD0D0) (assays 196-229). Its env_permutation uses raw seeds (217).
  - twin on 0xD0D0[:16].
  - transplant_battery on 0x7A7A, 32 worlds, reporting point accuracy only (301-328).
  - flip_state_transplant on 0x5757 (331-357).
- census (247-260): 64 random genomes on H(seed, 0xCE), 8 worlds.

**Labelling and storage**
- run_wave applies classify (794; 425-440) to BOTH evolve and transfer rows.
- anomaly_flags (795; 461-485) is applied to evolve rows only.
- store.append writes the row (796).

**Downstream selection on HELD**
- wave_B: the evo track uses classify SIGNAL (563) and its bases are max held lo99 (565, 568). The phys-track bases come from A0 plant/sens (547-549). Dial ranking uses dial_effects (488) on held acc, plant or sens.
- detect_boundaries (588), then B2 (619), then boundary_verdicts (637).
- wave_C: top 12 physics by held lo99 (661-670), then evolve (676) and transfer (681, 692).
- wave_D: promoted() takes up to 24 by held lo99, at most 4 per family (705-719). Each gets an adjudication and 2 replicate evolve searches (732-736).
- wave_E: promoted()[:5] over A, B, C evolve rows (745, 867).

**Report**
- report.build (62):
  - EV = kind == "evolve" (88); classify is recomputed (90).
  - A1 = EV in wave A (91-115). Anomalies come from EV (117-123). Boundaries are read from the JSON files (125-129).
  - C_transfer = C transfer rows with TRANSFER_SUPPORT (131-138). C_reevolve comes from EV (139-141).
  - D (143-166) uses causal_label (443-458) and transplant_transfer at point accuracy > .55 (153).
  - E (168-173). predictions P1-P8 (179-213).
- report.build writes summary.json and REPORT.md. C1_REPORT.md is the seat's prose over summary.json.

**Places where train, held and controls share randomness, structure or selection**

| id | what is shared | where | status |
|---|---|---|---|
| S1 | One topology graph (topo_seed fixed per cell) is used by train, final, held, controls and twin; transects keep the base topo_seed (520). "Held-out" means new positions, targets and physics noise on the SAME graph and constants. It is in-distribution. | | design |
| S2 | zero_comm runs on the same held worlds as the champion. This is intended pairing. | | intended |
| S3 | The twin runs on a 16-world subset of the held worlds, but with different physics in odd worlds (raw seeds). | assays 255 | known (H-IMPL H11 class) |
| S4 | pair_ci uses seed 0: the identical bootstrap index matrix is used for every cell, and for both acc and comm_delta. | | |
| S5 | Held is reused for downstream selection (B bases, C top 12, D promotion, E). | | winner's curse measured small: [V] F2 |
| S6 | The champion tie-break follows the shaped-fitness order. | search 351/362 | |
| S7 | The GA shaping uses the mirror-pair constructs (sens_act, sens_any) that the twin ruler also measures. | | [V] F1 |
| S8 | B2 seeds have no family or track key. | | known (H-IMPL H6) |
| S9 | The env RNG is keyed (lead, ENV, family, variant) and not by d or delta. EnvSpec.variant is never set by the campaign (always 0), so the "held-out variant" field is unused. Harmless in C1 because the seeds differ. | | |

[V] seed independence (checks/c3_seed_independence.py): 678 evolve rows have 678 distinct search seeds. Within a cell, held ∩ (train ∪ final) = 0. Across cells, no held seed equals any train or final seed (2.1 would be expected by 32-bit chance), and no held seed is shared between cells. **Held evaluation is seed-independent of selection.**

## 2. Findings

**F1 [V] The search selects for exactly what the twin ruler measures. On NULL cells, the twin-derived readings mostly measure selection, not the task. Confidence high.**

Population mean sens_any, generation 0 versus the last generation (checks/c2_shaping_vs_ruler.py):
- It rises in 100% of evolve cells, from about 0.001 to 0.07-0.22.
- It rises MORE in non-SIGNAL cells (RELAY .186, XOR .180, MAJ .210, FLIP .222, HOLD .208) than in SIGNAL cells (RELAY .117, MAJ .069, HOLD .166).

Random-genome baseline (checks/c8_twin_random_baseline.py): 24 non-SIGNAL A1 cells (6 each of RELAY, MAJ, FLIP, XOR), 16 random genomes per cell, scored on the SAME 16 held worlds as the champion.

| reading | NULL champion (held ~.50) | random genome |
|---|---|---|
| beyond_hop | .344 | .048 |
| persist (ticks) | 77.2 | 0.96 |
| div_frac_readout | .067 | .000 |

Spearman correlation, across non-SIGNAL rows, between the final population's mean sens_any and the champion's twin readings (checks/c9):

| family | div_frac_readout | persist |
|---|---|---|
| RELAY | +.64 | +.36 |
| FLIP | +.66 | +.53 |
| XOR | +.52 | +.46 |
| HOLD | +.68 | +.57 |
| MAJ | +.22 | +.15 |

Consequences:
- The prereg flag MEMORY_WITHOUT_USE ("persistent causal trace, no competence", 46 rows) and REACH_BEYOND_HOP on NULL champions are what the search manufactures when accuracy gives no gradient. They are not evidence about the physics.
- No C1 headline and no P1-P8 prediction uses them, so no recorded verdict changes.
- Strongest objection: truncation on NOISY accuracy alone also favours sensitive genomes. Deaf genomes score exactly .5 and can never be in the upper tail, so variance-seeking selection without any bonus would raise sensitivity too.
- Unresolved: bonus versus variance-seeking. Only a w_any = w_contrast = 0 search arm can decide it (ANANKE-14 A/B); I am not authorized to run one.
- What the data does settle: pure drift cannot reach 0.2 from the random-genome equilibrium of 0.001. Selection does it.

**F2 [V] Held is reused for downstream selection, but its winner's curse is small. Confidence high.**
- 12 wave-C same-family, same-env transfers re-evaluate the promoted champions on fresh 0x7F7F worlds: mean held change -.005 (median -.003).
- 12 D adjudications ("normal" on 0xD0D0) against source held: mean -.006. The largest single change is 62a7fff9, .850 to .783.
- So promotion by held lo99 does not materially inflate the reported held accuracies.
- Script: checks/c1_winners_curse.py.

**F3 [V] MAJ "d" does not mean distance d on ring or torus, and d=1 and d=2 are the same condition on a ring. Confidence high.**
- Mechanism: envs.build places each MAJ sensor with _pick_at at distance exactly d from the actuator (envs.py:212-213). A ring has only 2 sites at each distance, and a radius-1 torus neighbourhood has 4. The fallbacks then take "farthest <= d", then "nearest beyond".
- Realized sorted distance multisets on a ring:
  - d=1 gives (1,1,2,2,3); d=2 gives (1,1,2,2,3) as well, identical in distribution.
  - d=3 gives (1,2,2,3,3).
- Every MAJ ring row has 3 of its 5 sensors off d (checks/c6_realized_distance.py).
- Global topology aliases every d to 1 (already known).
- All 19 MAJ SIGNAL rows, including the M4 "integration" cell 4781b0a1 (ring, r3, d3, held .789), have every sensor within one hop (checks/c6b).
- Over all evolve rows (checks/c6c):
  - MAJ: 0/55 SIGNAL where placement forces multi-hop; 19/106 where it does not.
  - RELAY: 2/46 multi-hop versus 48/150 one-hop.
  - XOR: 0 SIGNAL anywhere; only 20 of 83 rows are one-hop.
- DESIGN s7 specifies "actuator at distance d from all sensors' centroid", which the code does not do.
- Effect on verdicts: none for labels. The MAJ d transects (4 transects, 48 B cells) contain two identical levels and produced no candidate. The "one-hop" result is partly forced by placement: MAJ was never asked to integrate beyond one hop where it succeeded.

**F4 [V] Transfer rows carry evolve-vocabulary labels, including a fabricated REACH_BEYOND_HOP=False, and no eligibility. Confidence high.**
- classify runs on transfer rows (campaign.py:793-794). With no twin present it defaults to tw.get("beyond_hop", 0), which gives False.
- All 99 transfer rows say REACH_BEYOND_HOP False although no twin was ever run. They also have no plant or gen0 fields.
- The prereg NULL label ("reported with the region's eligibility") is implemented nowhere in code: 0 rows have a NULL or INCONCLUSIVE key. A transfer row therefore cannot satisfy the NULL contract.
- This is the root cause of the H-PLANT slip (fac4aaa2 was a transfer cell, cited as "NULL").
- report.py itself does NOT mix kinds: EV filter at line 88; C_transfer and E are separated.
- Fix: patches/classify_transfer_reach_none.diff (NEUTRAL; it records None, "not measured").

**F5 [V] Wave-1 H-PLANT light-cone census mixes row kinds. "17% of XOR evolve rows capped" is wrong: the figure is 43%. Confidence high.**
- lc_census.py keeps every non-A0 row: B and B2 census rows, transfer rows and adjudicate rows.
- XOR: 218 rows, of which 83 are evolve, 123 census and 12 transfer.
- Evolve-only light-cone capped (< .60), recomputed from H-PLANT's own lc_census.json:

| family | evolve rows capped | reported |
|---|---|---|
| XOR | 36/83 = 43.4% | 17% |
| FLIP | 24/82 = 29.3% | 9.7% |
| RELAY | 16/196 = 8.2% | 5.4% |

- Effect: the share of XOR NULLs that physics alone caps is 2.5 times what the handoff (s8) says. That strengthens "XOR NULLs are partly physics-limited".
- Fix: patches/hplant_lc_census_evolve_only.diff.

**F6 [V] report.py counts 22 HOLD "env variants" as TRANSFER_SUPPORT. The prose excludes them; the machine summary does not. Confidence high.**
- summary.json reports 23 TRANSFER_SUPPORT: 22 are HOLD to HOLD, and 1 is RELAY d1/delta4 (.755, lo99 .715).
- HOLD never reads d or delta, and every one of the 22 is on its source's physics, so each is the same condition rerun (checks/c5_transfer_variants.py; C1_REPORT F5 states this in prose only).
- Effect on recorded verdicts: none (P5 excludes HOLD sources). But a consumer of summary.json gets 23, not 1.
- Fix: an additive key, TRANSFER_SUPPORT_EFFECTIVE (NEUTRAL).

**F7 [V by code + test] The wave hour cap resets on every process attempt, and resume is not guarded against a changed upstream. Confidence high (latent).**
- run_wave sets t0 = time.time() on every call (777). A watchdog relaunch (launch.py, up to 20 attempts) therefore gives the in-progress wave a FULL new budget. PREREG s5 says "hours are hard caps".
- Once a censored upstream wave continues on restart, downstream specs change. Rows from the old spec set stay in store.rows(wave) and flow into later waves and into report.py.
- C1 ran ONE attempt (watchdog.log), so C1 is unaffected.
- Fix: patches/run_wave_budget_and_exact_resume.diff (NEUTRAL). It persists wave_<W>_started_epoch, and it PARKs (exit 3) when stored rows of a wave are absent from the regenerated specs.

**F8 [V] c1b_run drops the specimen's eligibility for fresh-seed champions. Confidence high.**
- The eligibility lookup uses the key "<cell>:fresh<k>" (c1b_run.py:252), which never exists.
- As run, 4ab2ba01's fresh1/2/3 were labelled DELAY_LINE_SPECIMEN / IN_FLIGHT_UNDECODED without _UNRESOLVED, at a physics where Z is NOT_ELIGIBLE.
- The recorded C1B_SUMMARY is already corrected post hoc (build_summary.py, label_corrected), so no recorded verdict changes. The driver still has the defect.
- Fix: patches/c1b_run_fresh_eligibility.diff (NEUTRAL).

**F9 [V] P1 does not filter on track. Confidence high (latent).**
- PREREG s12 says "The phys track finds ...", but score_predictions accepts any track.
- In C1 both qualifying verdicts (RELAY delta, bases 0 and 1) are phys track, so P1 HELD stands (checks/c4).
- Fix: included in the report diff.

**F10 [V] The SIGNAL ruler undercovers. Confidence medium.**
- percentile-bootstrap pair_ci with 32 pairs at 99%: under a true accuracy of exactly .55, P(lo99 > .55) is 1.20% with 12 trials and 0.53% with 16 (nominal 0.5%; SE .13%; checks/c7). At .70 with 12 trials it is 0.83%.
- Effect: negligible for C1. NULL cells sit near .50, not .55, so the expected number of false SIGNALs is far below 1. The C1 calls are robust; borderline future claims are not.

**F11 [V] GPU-recorded and CPU-replayed twin floats differ in the last bits; the dynamics are exact. Confidence high.**
- 22/24 champion twins replay bit-for-bit on CPU at HEAD.
- In the other 2, div_frac_readout and div_frac_next differ by about 3e-8. This is float32 reduction order (05fea1b5, 062b2018).
- Held accuracy replays exactly (checks/c11_replay_diff.py).
- The "no tolerance, any mismatch is a DEFECT" rule (PREREG s1) holds for the integer dynamics but not for derived float32 telemetry. A threshold sitting exactly on such a value could flip a flag. None observed.

**F12 [V] Smaller checks.**
- No silent physics redraws: 0 of 5000 A0 cells needed a validate() redraw, so the "uniform" dials are uniform (checks/c10).
- Stored labels equal recomputed classify in 784/784 labelled rows. The freeze config equals the default config.
- No B or B2 transect level has fewer than 3 replicates, so PREREG s8's ">= 3 replicates" holds, although detect_boundaries never enforces it.
- 87 non-SIGNAL champions have final-train accuracy of exactly 0.5. There the argmax tie-break follows the shaped order (S6). 78 of these held exactly .5, and only 2 carry MEMORY_WITHOUT_USE.
- TRAIN_HELD_GAP never fired (0/678). The non-SIGNAL train minus held gap has mean .021 and maximum .121, so the detector is near-inert at M_final=16.

**F13 [I] The XOR mirror does not negate every input. Confidence high (by reading).**
- The XOR mirror negates input 1 only (envs.py:201). The evaluate comment "world m+1 is an exact twin with every input negated" (assays.py:54-55) is false for XOR.
- XOR sens_act therefore measures the input-1 causal path only. Not a verdict issue.

## 3. Mismatch table: code versus preregistration and report

| # | item | prereg/report text | executable semantics | effect on recorded verdicts |
|---|---|---|---|---|
| M1 | NULL label | s7: NULL reported with region eligibility | not implemented; transfer rows have no eligibility fields | none mechanical; prose NULLs (incl. H-PLANT fac4aaa2) unsupported by a code label (F4) |
| M2 | INCONCLUSIVE for censored cells | s7 | censored cells simply absent; A1 denominator 352, not 400 | P4 8/352 = 2.3% (8/400 = 2.0%): still HELD |
| M3 | REACH_BEYOND_HOP | not a prereg label ("no stronger label exists") | emitted by classify on evolve AND transfer rows; False when no twin | no aggregate uses it; MAJ/XOR/global uninterpretable (E-H1/E-H2); transfer value fabricated (F4) |
| M4 | TRANSFER_SUPPORT | s7: other family, env variant, other size, D transplant; recipient reaches SIGNAL | C only; variant counted even when inert (22 HOLD); E sizes not labelled; D transplant at point accuracy (H10) | summary 23 vs effective 1 (F6); P5 unaffected |
| M5 | P1 | phys track | any track | none in C1 (F9) |
| M6 | promotion cap | s5/s7: <= 4 per family | code 4, comment 3 | none |
| M7 | E pool | top 5 promoted | ABC substring drops B2 (H5) | one RELAY law scaled (E-H5) |
| M8 | hour caps | hard caps | reset per attempt | none (1 attempt) (F7) |
| M9 | resume exact | module doc | stale rows of an old spec set are accepted | none (1 attempt) (F7) |
| M10 | MAJ geometry | DESIGN: actuator at distance d from the sensors' centroid; prereg s3 "d" as spatial scale | each sensor "at d" with fallbacks; ring d=1 ≡ d=2; 3 of 5 sensors off d | none for labels; d-dial tables and the "one-hop" reading (F3) |
| M11 | mirror "every input negated" | assays comment | XOR negates input 1 only | none (F13) |
| M12 | ">= 3 replicates per level" | s8 | not enforced (held in C1) | none |
| M13 | analysis_a0 R_time | plan: (lat_base + lat_hop*d + jitter)*hops/delta | lat_hop*min(radius, d) on lattices, *1 on graphs | interpretation of R_time "EXPLAINS" calls only [I] |
| M14 | analysis_a0 null | family permuted within topology | rung label permuted within topology in one family (H24 known) | null semantics |
| M15 | C1b S2 seed | H(0xC1B5, cell, k) | H(0xC1B5, mech_index, cell_index, k) | none (deterministic; wording) |
| M16 | C1b fresh eligibility | A2.2 applies at the specimen's physics | lost by key mismatch | corrected post hoc (F8) |
| M17 | errors / NaN | | cell exceptions go to failures.log and never to rows (0 in C1); NaN is impossible in held (scored.sum > 0); NaN > threshold would read SIGNAL False, i.e. a silent NULL | none |
| M18 | intact() on a NOT_APPLICABLE arm | absence readings count only with a positive control | returns True; gated only where an A2.2 plant exists; for live routing, F_route is never run at specimen physics, so routing_resolved is True by default | none for the C1b specimens (dest_mode all); latent [I] |

## 4. Proposed fixes

All diffs are under roles/Ananke/research/harvest/wave2/W2-A2/patches/. `git apply --check` passes on fd631acb2.

| diff | tag | what it changes |
|---|---|---|
| classify_transfer_reach_none.diff | NEUTRAL | REACH_BEYOND_HOP = None when no twin; evolve labels unchanged |
| run_wave_budget_and_exact_resume.diff | NEUTRAL for C1 | per-wave persisted clock; PARK on a stale-row resume |
| report_transfer_effective_p1_track.diff | NEUTRAL | additive condition_changed / TRANSFER_SUPPORT_EFFECTIVE; the legacy key and every legacy summary value equal the committed c1_report/summary.json (tested); P1 phys-track filter, C1 P1 result unchanged |
| c1b_run_fresh_eligibility.diff | NEUTRAL | eligibility keyed by the specimen id |
| hplant_lc_census_evolve_only.diff | NEUTRAL, Wave-1 tool | filter on kind == "evolve" |

**Tests** (W2-A2/tests/, 12 tests):
- Original code: 6 FAIL (the defect tests) and 6 PASS (the neutrality tests).
- Patched copy (scratch/patched): 12 PASS.
- Commands:
  - `PYTHONPATH=F:/Prometheus-worktrees/ananke-base-role python -m pytest -q -p no:cacheprovider tests`
  - `PYTHONPATH="<W2-A2>/scratch/patched;F:/Prometheus-worktrees/ananke-base-role" python -m pytest -q -p no:cacheprovider tests`

**SEMANTIC (proposed, not built):**
- emit an explicit NULL label with eligibility;
- a placement guard that refuses or flags off-d sensors;
- a twin ruler on NULL champions reported against a random-genome baseline.

## 5. Disagreements with Wave-1 and the principal

1. **H-PLANT REPORT s6 and handoff s8, "17% of XOR evolve rows are light-cone-capped":** the true evolve-row share is 43.4% (FLIP 29.3%, RELAY 8.2%). The denominator mixed census, transfer and adjudicate rows (F5).
2. **H-IMPL H20, "MAJ sensors sit at distance d from the actuator":** false on ring and torus. Only 2 (or 4) sites exist at distance d; the others fall back closer or farther, and d=1 ≡ d=2 on a ring (F3).
3. **Handoff s1.2, "evolved PTE transport is one hop":** correct as observed, but for MAJ it is forced by the sampled placements. MAJ SIGNAL occurred only where placement made every sensor one hop away, and multi-hop MAJ placements went 0/55. It is a sampling fact, not only a search or physics fact.
4. **Handoff s1.3, "shaping pays one-sided codes ... untested":** partly tested here. The shaping-coupled quantities rise 100-200 times, and most strongly in NULL cells. The twin readings of NULL champions sit about 80 times above random genomes (F1). The bonus-versus-noise attribution remains open.
5. **C1_REPORT F5 says the HOLD variants are "flagged and not counted":** the generated summary.json counts them (23 TRANSFER_SUPPORT).

## 6. Next questions (ranked)

1. With w_any = w_contrast = 0 (8 seeds, RELAY at d9cc plus one MAJ ring cell), do sens_any and the NULL-champion persist/beyond_hop still rise? This decides bonus versus variance-seeking for F1, and needs an authorized bounded search.
2. MAJ with a geometry guard (all 5 sensors at true distance d, or the DESIGN centroid rule) at the 4781b0a1 physics: does any search reach SIGNAL when at least one sensor needs 2 hops? This is the first real test of MAJ "integration beyond one hop".
3. Re-score H-PLANT's H6 split on evolve rows only. For the 47 uncapped XOR evolve rows, is there any plant that works? Those are the only XOR rows where "search-limited" is still possible.
4. Should C1_ERRATA record that MEMORY_WITHOUT_USE (46 rows) and REACH_BEYOND_HOP on NULL cells are selection-coupled, with the c8 random-genome baseline as the reference?
5. Does the percentile-bootstrap undercoverage (1.2% versus 0.5% at 12 trials) matter for any future borderline promotion? If so, switch to a BCa or t interval in C2 before data.
6. Should future campaigns randomize topo_seed per held world (or hold out graphs), so that "held-out" covers the graph and not only positions?
7. The 2 GPU/CPU float32 telemetry mismatches: should flag thresholds be computed on integer counts to keep the exact-replay rule literal?

## 7. Inference ledger

| question | evidence | result | confidence | strongest objection | unresolved | next |
|---|---|---|---|---|---|---|
| Is held seed-independent of selection? | c3: all train, final and held seeds recomputed for 678 cells | 0 overlaps within or across cells | high | shared graph and constants (S1) | OOD generalization | per-world graphs |
| Does selection inflate held? | c1: 24 independent re-evaluations of promoted champions | about -.005 | high | n=24, top cells only | mid-ranked cells | none needed |
| Does the GA select what the ruler measures? | c2, c8, c9: curves, random baseline, Spearman | yes; NULL champions about 80x random on persist | high | noise-chasing alone would do the same | bonus vs variance | w=0 A/B |
| Is MAJ/XOR placement faithful to d? | c6, c6b, c6c: realized distances on held worlds | MAJ ring off-d; d=1 ≡ d=2; MAJ SIGNAL only one-hop | high | DESIGN may intend "scale", not distance | whether intended | geometry-guard search |
| Are transfer and evolve distinguished downstream? | c0, c4, grep of consumers | report.py ok; classify stamps both; lc_census mixes | high | report itself is clean | other worker scripts | audit consumers |
| How large is the lc_census error? | H-PLANT's lc_census.json filtered by kind | XOR 43%, not 17% | high | H-PLANT might have meant "rows" | none | apply diff, rerun |
| TRANSFER_SUPPORT semantics? | c5 with the effective-env rule | 23 reported, 1 real | high | prose already excludes them | none | additive key |
| Resume and budget | code reading, tests, watchdog.log | latent defects; C1 single attempt | high | none | none | apply patch |
| C1b fresh eligibility | c1b rows, ELIGIBILITY_dev, test | defect in driver; summary corrected | high | already disclosed in build_summary | none | apply patch |
| Is the SIGNAL CI calibrated? | c7 simulation, 3000 per condition | 1.2% vs 0.5% at p=.55, 12 trials | medium | binomial model ignores world heterogeneity | real-cell coverage | C2 interval choice |
| Is replay exact? | c8/c11 CPU replay of 24 twins and 2 helds | dynamics exact; float32 telemetry about 3e-8 off in 2 | high | GPU nondeterministic reductions | flag thresholds | integer telemetry |
| Are draws conditioned on validity? | c10 | 0 redraws | high | none | none | none |

## 8. Compute

- CPU only, 2 threads per process, no GPU, no search.
- The largest run was c8 (48 small twin assays): 834 s wall.
- Everything else (data checks, distance census, tests run twice at about 17 s) came to about 6 min wall.
- Total about 0.3 core-h measured at 1-2 threads; upper bound 0.55 core-h if both threads were saturated throughout c8.
- No background processes remain.
