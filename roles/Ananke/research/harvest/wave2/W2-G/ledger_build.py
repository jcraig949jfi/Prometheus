"""W2-G claim ledger. Every rederived value below comes from derived.json (rederive_c1.py),
random_transplant_*.json (check_random_transplant_*.py) or the two helper CSVs
(sub_arc3/arc3_claims.csv, sub_swap/swap_claims.csv), which are merged in.

    python roles/Ananke/research/harvest/wave2/W2-G/rederive_c1.py
    python roles/Ananke/research/harvest/wave2/W2-G/ledger_build.py

Writes claim_ledger.csv and prints a status summary.
"""
import collections
import csv
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
D = json.loads((HERE / "derived.json").read_text())
RT = json.loads((HERE / "random_transplant_d1.json").read_text()) if (HERE / "random_transplant_d1.json").exists() else {}
J = lambda x: json.dumps(x, separators=(",", ":"))
ROWS = "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
C1BR = "roles/Ananke/pte/c1b/c1b_rows/rows.jsonl.gz"
ev, a1, a0, dd = D["evolve_all_waves"], D["A1"], D["A0"], D["D"]
L = []


def add(cid, doc, loc, claim, rederived, status, denom="", denom_ok="", exceeds="", correction="", raw=ROWS, notes=""):
    L.append(dict(claim_id=cid, doc=doc, location=loc, claim_text=claim, rederived_value=rederived, status=status,
                  denominator=denom, denominator_ok=denom_ok, wording_exceeds=exceeds, proposed_correction=correction,
                  raw_path=raw, notes=notes))


C1R, PKT, RPT = "pte/C1_REPORT.md", "pte/REVIEW_PACKET_PTE_C1.txt", "pte/c1_report/REPORT.md"
# ------------------------------------------------------------------ C1_REPORT / packet: run facts
add("C1-01", C1R, "header", "12 h 02 m, 0 failed cells, 6596 rows",
    f"rows {D['n_rows']}; finished_at {D['finished_at_min_max']}; log fail lines {len(D['log_fail_lines'])}", "MATCH",
    notes="failures.log is run state, not in git; 0 failed is inferred from log.txt having no failure lines and all specs present")
add("C1-02", PKT, "s5", "A0 5000; A1 400 (352 run, 48 censored); B 786; B2 270; C 132; D 36; E 20", J(D["per_wave"]) + " | " + D["censor_lines"][0][-60:], "MATCH")
add("C1-03", PKT, "s2", "31 physics dials + 4 env dials; GA pop 96, 36 gens; twin-contrast bonus max +0.12; held-out 64 worlds",
    f"dials {D['n_physics_dials']}+{D['n_env_dials']}; search {J({k: D['A_search'][k] for k in ('pop', 'gens', 'w_contrast', 'w_any', 'M_held')})}", "MATCH",
    notes="+0.12 = w_contrast .10 + w_any .02 (fitness = acc + .10*max(sens_act,0) + .02*sens_any)")
add("C1-04", C1R, "F6", "48/400 censored; 51 s/cell vs 37 preflight", f"A1 mean cell_wall {D['A_cell_wall_mean_s']} s (median {D['A_cell_wall_median_s']}); 37 s is the PREREG s5 pre-data estimate", "MATCH",
    raw=ROWS + " ; PREREG_PTE_C1.md L117")
add("C1-05", C1R, "F7", "Throughput 11-21M site-updates/s", "search-phase n_world_evals*T*N/wall_s over 678 evolve rows: median 11.5M, IQR 9.0-15.7M, p10-p90 7.3-18.8M", "PARTIAL",
    exceeds="minor", notes="definition of the reported throughput not recorded; range plausible but not reproducible exactly")
add("C1-06", C1R, "header", "Every number here is recomputed from the rows by report.py", "FALSE as stated: 0/253, 0/755, 0 of 7, 11-23%, 0.3-0.7%, M2 post-hoc numbers, 37 s preflight and 11-21M come from analysis_a0.py / a0_interactions.json / c1_posthoc / PREREG / unrecorded", "MISMATCH",
    exceeds="yes", correction="'Numbers in s1, s3 (M1, M3, M4), s4, s5 are recomputed by report.py; ladder rungs come from analysis_a0.py (c1_a0/); M2 from c1_posthoc/; throughput is an unrecorded estimate.'", raw="(provenance statement)")
# ------------------------------------------------------------------ ladder / A0
add("C1-07", C1R, "s2 L1", "perturbable common: 11-23% of comm-family A0 cells",
    "L1 (sens>=.30) RELAY 109, XOR 108, MAJ 226, FLIP 176 per 1000", "MATCH", "1000 A0 cells per family", "yes",
    notes="A0_FINDINGS s1 table prints FLIP 196 and HOLD 156/279/879: those are FIT-half rates x1000 from a0_interactions.json, not counts (see A0F-01)")
add("A0F-01", "pte/c1_a0/A0_FINDINGS.md", "s1 table", "per 1000: FLIP L1 196, L2 18; HOLD L1 156, L2 279, L2' 879",
    f"full-census counts FLIP L1 {a0['FLIP']['L1_sens_ge_.30']}, L2 {a0['FLIP']['L2_contrast_ge_2of64']}; HOLD L1 {a0['HOLD']['L1_sens_ge_.30']}, L2 {a0['HOLD']['L2_contrast_ge_2of64']}, L2' {a0['HOLD']['viable_ge_.75']}; the printed values equal the FIT-half pos_rate x1000 (FLIP .1955/.0183, HOLD .1559/.2794/.8785)",
    "MISMATCH", "mixed: RELAY/XOR/MAJ rows are full counts, FLIP/HOLD rows are FIT-half rates", "no",
    correction="FLIP 176 / 13 / 0; HOLD 132 / 266 / 875 (full 1000-cell counts)", raw=ROWS + " ; c1_a0/a0_interactions.json",
    notes="feeds C1_REPORT s2; no headline changes (FLIP 17.6% stays inside 11-23%)")
add("C1-08", C1R, "s2 L2", "distal influence rare: 0.3-0.7% of cells for a random program",
    "L2 RELAY 7, XOR 3, MAJ 6 per 1000 (FLIP 13 excluded)", "MATCH", "comm families minus FLIP", "partly",
    exceeds="minor", correction="add '(FLIP excluded: its L2 includes the local teacher path)'")
add("C1-09", C1R, "s2 L2'", "known design viable RELAY 19/1000", f"{a0['RELAY']['viable_ge_.75']}/1000", "MATCH")
add("C1-10", C1R, "s2", "L2' and L2 are disjoint in RELAY (0 of 7)", f"L2 and L2' both: {a0['RELAY']['L2p_and_L2']} of {a0['RELAY']['L2_contrast_ge_2of64']}", "MATCH")
add("C1-11", C1R, "s2", "a RELAY SIGNAL at loss 0.6 where the design is 0/253",
    f"A0 RELAY plant viable at loss .6: {D['A0_RELAY_viable_by_level']['loss']['0.6']}; RELAY SIGNAL evolve rows at loss .6: 14 (1 A1 c939c3c7 + 13 B/B2 descendants, one smallworld lineage)", "MATCH",
    exceeds="no", notes="the 14 rows are one lineage at one physics")
add("C1-12", C1R, "s2", "MAJ SIGNALs at decay 3 and 6 where it [the design] is 0/755",
    f"0/755 is the RELAY plant at decay>0 (255+250+250 cells); MAJ A0 cells at decay 3/6 = {D['A0_MAJ_viable_at_decay_3_or_6']}; MAJ plant viable anywhere = {D['A0_MAJ_viable_any']}; MAJ SIGNAL at decay 3: 16 rows, decay 6: 1 row",
    "PARTIAL", "RELAY plant's denominator used for a MAJ claim", "no", exceeds="yes",
    correction="'MAJ SIGNALs at decay 3 and 6; no hand design is viable for MAJ at any physics (0/1000), and the RELAY design is 0/755 at decay > 0'",
    notes="'outside the design region' is vacuous for MAJ: the MAJ plant is never viable")
add("C1-13", C1R, "s2", "Seeding half of A1 in living A0 cells gave no advantage (RELAY 2 vs 2, MAJ 2 vs 1 SIGNAL)",
    f"RELAY living {a1['RELAY']['living']} vs uniform {a1['RELAY']['uniform']}; MAJ living {a1['MAJ']['living']} vs uniform {a1['MAJ']['uniform']}", "MATCH",
    "35-36 cells per arm", "yes", exceeds="minor", notes="2 vs 2 and 2 vs 1 of ~35 cannot show or exclude an advantage (power ~0); 'no detectable advantage'")
# ------------------------------------------------------------------ L3 / evolve
for f, claim in (("RELAY", "50/196"), ("MAJ", "19/162"), ("HOLD", "97/155"), ("XOR", "0/83"), ("FLIP", "0/82")):
    e = ev[f]
    add(f"C1-L3-{f}", C1R + " ; " + PKT, "s2 L3 ; packet s6", f"{f} {claim} evolve cells SIGNAL (all waves)",
        f"{e['SIGNAL']}/{e['n']}; by wave {J(e['n_by_wave'])}; SIGNAL by wave {J(e['SIGNAL_by_wave'])}; distinct physics+env among SIGNAL {e['distinct_phys_env_SIGNAL']}",
        "MATCH", "all evolve rows incl. B2 reruns, C re-evolves, D replicate searches, E re-evolve", "no" if f in ("RELAY", "MAJ", "HOLD") else "yes",
        exceeds="yes" if f in ("RELAY", "MAJ") else "",
        correction=(f"'{f} SIGNAL in {e['SIGNAL']} evolve rows ({e['distinct_phys_env_SIGNAL']} distinct physics x task conditions; post-A1 waves were targeted at A1 winners); unbiased A1 rate {a1[f]['SIGNAL']}/{a1[f]['n']}'" if f in ("RELAY", "MAJ") else ""),
        notes="ratio is not a discovery rate: post-A1 waves re-sample the neighbourhood of A1 SIGNAL cells and D replicates rerun the same physics")
add("C1-14", C1R, "s1", "rare (A1: 8/352 cells COMM_DEPENDENT)", f"{D['A1_COMM_DEPENDENT_total']} (comm families {D['A1_COMM_DEPENDENT_comm_families_only']}, which equals their SIGNAL count {D['A1_SIGNAL_comm_families']})", "MATCH",
    "A1 incl. HOLD", "partly", exceeds="yes", correction="'rare (A1: 7/282 comm-family cells SIGNAL; COMM_DEPENDENT is identical to SIGNAL there because zero_comm is forced to .500)'")
add("C1-15", PKT + " ; " + C1R, "s6 ; P4", "COMM_DEPENDENT RELAY 50, MAJ 19, HOLD 3; P4 HELD 8/352 = 2.3%", f"{J(D['comm_dependent_equals_signal'])}; P4 {D['P4']} = {D['P4_pct']}%", "MATCH",
    exceeds="yes", notes="COMM_DEPENDENT == SIGNAL for every comm family (see HV-01): P4 is a SIGNAL-rarity prediction, not a comm-dependence finding")
add("C1-16", C1R, "s1/F1/P3", "XOR and FLIP produced no signal at all; 0 signal in 165 evolve cells; P3 0/83", f"XOR {D['P3_XOR_SIGNAL']}, FLIP {ev['FLIP']['SIGNAL']}/{ev['FLIP']['n']}; total {D['XOR_FLIP_evolve_total']}", "MATCH",
    "evolve rows (XOR: 71 A1 + 12 C; FLIP: 70 A1 + 12 C)", "yes", exceeds="yes",
    notes="36/83 XOR and 24/82 FLIP evolve rows are light-cone capped below .60 (no program could pass); a one-flag readout passes the XOR SIGNAL rule (H-PLANT). 'NULL' mixes physics-capped and search-limited cells",
    correction="'XOR 0/83, FLIP 0/82 SIGNAL; 36 XOR and 24 FLIP rows were physically capped below .60 (light cone), so at most 47 XOR and 58 FLIP searches were informative'")
add("C1-17", C1R, "s2 L3->transport", "RELAY 4/4 promoted CAUSAL_SUPPORT", f"{D['RELAY_D_causal']} (labels recomputed from controls)", "MATCH",
    exceeds="yes", notes="causal rule = zero_comm<=.55 AND packet_ablation<=normal-.10; zero_comm is forced in RELAY, so the label rests on packet_ablation alone")
add("C1-18", C1R + " ; " + PKT, "s3 M1 ; s12", "Fresh-seed searches reproduce it in 3 of 4 cells; REPRODUCED_SIGNAL YES (RELAY 3/4)",
    f"{D['RELAY_D_reproduced']} (both reps SIGNAL in {D['RELAY_D_both_reps_SIGNAL']}); reps {J({k: v['reps'] for k, v in dd.items() if v['family'] == 'RELAY'})}", "MATCH",
    exceeds="minor", notes="all 4 promoted RELAY cells share one physics point (d9cc) and descend from A1 86fc0105: 3/4 is one lineage, one physics")
add("C1-19", PKT, "s6 table", "promoted D table: held .837/.850/.857/.883, MAJ .789/.695/.686; reps as listed; labels",
    J({k: [v['held'], v['reps'], v['causal']] for k, v in dd.items() if v['family'] != 'HOLD'}), "MATCH", exceeds="minor",
    notes="table omits MAJ 613162a3 (CAUSAL_SUPPORT, not reproduced: reps .500/.510) and the 4 HOLD latches; 10 of 12 D cells are CAUSAL_SUPPORT")
add("C1-20", C1R + " ; " + PKT, "s3 M1 ; s8", "zero-comm, max-loss and shuffled destinations -> 0.50(-0.52); shuffled timing 0.73-0.88; payload randomisation 0.50-0.70; env-permutation 0.50",
    J(D["RELAY_D_ranges"]), "MATCH", exceeds="yes",
    notes="zero_comm and max_loss are the same forced control (both exactly .500 by mirror construction, HV-01); env_permutation is near .5 for any policy")
add("C1-21", C1R + " ; " + PKT, "s3 M1 ; s8", "Survives +0.2 loss, +1 latency, +2 jitter, x2.25 size, async 0.7", J(D["RELAY_D_transplant_ranges"]), "MATCH",
    notes="noise+32 not claimed (c16d5231 .53)")
add("C1-22", C1R + " ; " + PKT, "s1, s3 M1, F2 ; s8, s12", "topology-bound: every RELAY law collapses to 0.500 on a random graph; the machinery encodes lattice geometry (routing to specific offsets)",
    f"recorded topology->random: {J(D['RELAY_D_topology_random'])}. But the transplant keeps env d=3, and on a BFS-distance graph that forces a 3-hop task (128/128 placements, all 4 cells; native ring r3 d3 = 1 hop). Same random graph at d=1: " +
    J({k: v.get('random_d1') for k, v in RT.items() if not k.startswith('_')}),
    "MISMATCH", "4 cells, 1 physics", "", exceeds="yes",
    correction="'Every RELAY law scores .500 when moved to a random graph at the same d, but that transplant turns a 1-hop task into a 3-hop task. At d = 1 on the same random graph all four laws stay above chance (lo99 .57-.81; W2-G post hoc). The collapse measures hop count, not lattice geometry.'",
    raw=ROWS + " ; W2-G/random_transplant_hops.json ; W2-G/random_transplant_d1.json",
    notes="[V] check_random_transplant_hops.py and check_random_transplant_d1.py (post hoc, 32 mirror pairs, W2-G seed namespace)")
add("C1-23", C1R + " ; " + PKT, "s1 ; s6", "SIZE-FREE: frozen RELAY laws keep 0.875-0.893 from N=100-ish up to N=2304",
    f"E transfers: one law only (sources {D['E_RELAY_sources']}), source N=144: " + J([e[2:5] for e in D['E'] if e[1] == 'RELAY']) + f"; that law's fresh-seed reps {dd['bbef66a1']['reps']} (not reproduced)",
    "MISMATCH", "1 law", "no", exceeds="yes",
    correction="'One frozen RELAY law (bbef66a1, N=144, not reproduced under fresh seeds) keeps .875-.893 at N=400-2304. At fixed d=3 on a radius-3 ring the task stays one hop at every N, so size independence is expected by construction.'")
add("C1-24", C1R, "s1/s2 L4/P5", "0 cross-family TRANSFER_SUPPORT", f"{D['C_TRANSFER_SUPPORT_cross_family']} of {D['C_transfer_n']} C transfers; best cross-family lo99 {D['C_cross_family_max_lo99']}", "MATCH")
add("C1-25", C1R, "s2 L4", "within-family env transfer yes (RELAY d1/delta4: 0.755)", J(D["C_RELAY_within_family"]), "PARTIAL",
    "2 RELAY env variants of 1 champion", "", exceeds="yes",
    correction="'within-family env transfer 1 of 2 (bbef66a1: d1/delta4 .755; d5/delta16 .500, a 2-hop task)'")
add("C1-26", C1R, "F5", "22 HOLD 'transfers' were the same condition rerun", f"HOLD->HOLD variant TRANSFER_SUPPORT {D['C_TRANSFER_SUPPORT_HOLD_variants']}", "MATCH")
add("C1-27", C1R, "s3 M3", "M3: zero-comm .50; packet ablation in cue->readout window does nothing (0.70); adaptation off 0.53-0.55; routing freeze no effect; +1 latency 0.49-0.50",
    J({k: {c: dd[k]['controls'][c] for c in ('zero_comm', 'packet_ablation', 'adaptation_off', 'frozen_routing')} | {'latency+1': dd[k]['transplants']['latency+1']} for k in ('0a23398f', 'f6b623cd')}),
    "MATCH", exceeds="superseded", notes="C1b: the C1 window missed the readout tick (D-A); frozen_routing is vacuous (dest_mode all). Reading superseded, numbers correct")
add("C1-28", C1R, "s3 M4", "MAJ 4781b0a1 0.789, lo99 0.742 > 0.70; CAUSAL_SUPPORT; fresh-seed reps 0.636 and 0.520", J([dd['4781b0a1'][k] for k in ('held', 'held_lo99', 'causal', 'reps')]), "MATCH",
    exceeds="yes", notes="INTEGRATION = lo99 > .70 is a threshold on accuracy, not a test of aggregation; H-SCI F5 shows descriptive multi-sensor agreement in 4 MAJ champions. 'Integration beyond one sensor did NOT reproduce' should read 'the INTEGRATION label (lo99 > .70) did not reproduce'")
add("C1-29", C1R + " ; " + PKT, "s3 M2 ; s8", "M2 HOLD 4ab2ba01 0.883: site-state reset mid-gap no effect (0.88); packet ablation / payload randomisation / zero-comm 0.50",
    J(D["posthoc"]["4ab2ba01"]), "MATCH", raw="roles/Ananke/pte/c1_posthoc/posthoc_adjudication.json",
    notes="4ab2ba01 is a wave-C re-evolve on bbef66a1's (d9cc) physics; HOLD zero_comm is not forced (sensor = actuator) but is exactly .500 here")
add("C1-30", C1R, "s4", "13 SUPPORTED, 24 CANDIDATE; RELAY plant decay -0.45/-0.26, delta +0.40/+0.15, economy -0.45/-0.22; 4 of 13 are one HOLD dip; 3 program-space",
    f"{J(D['boundary_counts'])}; {J(D['SUPPORTED_by_family_metric'])}; RELAY plant jumps recomputed from B transect rows: " +
    J({k: v['recomputed_jump'] for k, v in D['RELAY_plant_boundary_recheck'].items()}), "MATCH",
    raw=ROWS + " ; c1_rows/boundaries_verdicts.json", notes="labels recounted from the stored verdict file; means and jumps independently recomputed from B census rows")
add("C1-31", C1R, "s4", "Evolved competence: only CANDIDATE (RELAY acc delta 4->8 +0.18, fresh seeds yes, second base no); no SUPPORTED evo boundary",
    f"SUPPORTED on evo track: {D['SUPPORTED_evo_track']}; RELAY evo delta jump +0.180 fresh=True ortho=False", "MATCH")
add("C1-32", C1R, "s5", "Predictions: 5 HELD, 3 LOST (P2 3/9 SIGNAL, P4 8/352, P6 1 flag, P7 HOLD at N=1024, P8 0 ANTI)",
    f"P2 {D['A1_HOLD_decay1']}; P4 {D['P4']}; P6 {D['P6_DMUD']}; P7 {D['E_HOLD_transfer_1024']}; P8 ANTI {D['P8_ANTI']}", "MATCH")
add("C1-33", RPT, "s4", "anomaly counts MEMORY_WITHOUT_USE 46, ROBUST_UNDER_LOSS 32, SILENT_COMPETENCE 22, COMPETENT_UNDER_COST 11, DMUD 1",
    f"{J(D['anomalies_recomputed'])}; rows whose stored flags differ from recomputed: {D['anomalies_stored_mismatch_rows']}", "MATCH",
    notes="COMPETENT_WITHOUT_COMM can never fire in RELAY/MAJ/XOR (zero_comm forced): its 0 is uninformative")
add("RPT-01", RPT, "s1-s9", "report.py output (all tables) vs independent recomputation",
    "per-wave, A0 plant/viable/living, A1 table, C transfers and re-evolve, D labels/controls/reps, E, anomalies, boundary counts and P1-P8 all reproduce", "MATCH",
    notes="report.py issues (no numeric error): (1) 'evolve cells (all waves)' pools D replicate searches and targeted waves; (2) P2 tests decay_shift against the union of 6 dials (top-3 plant + top-3 sens) while the claim says top-3; (3) A1 INTEGRATION column adds the XOR SIGNAL count; (4) TRANSFER_SUPPORT counts HOLD env variants HOLD never reads (C1 F5 discloses); (5) causal_label uses forced zero_comm")
add("C1-34", C1R, "s2 L3->L4/F1", "Evolution finds transport outside the region a human design needs",
    "RELAY: 14 loss-.6 SIGNAL rows (one lineage); MAJ comparison uses the RELAY design (C1-12)", "PARTIAL", exceeds="yes",
    notes="true for one RELAY lineage; for MAJ there is no viable design anywhere, so 'outside' is undefined")
# ------------------------------------------------------------------ C1b
C1BP = "pte/c1b/REVIEW_PACKET_PTE_C1b.txt"
s1, s3 = D["c1b_S1"], D["c1b_S3"]
add("C1B-01", C1BP, "header", "27/27 cells, 0 failed, 510 s; raw rows sha256 8019247c19cdf2f0", f"{D['c1b_n_rows']} rows {J(D['c1b_status'])}; wall {round(D['c1b_done']['wall_s'], 1)} s; sha256(rows) {D['c1b_raw_sha256_16']}", "MATCH", raw=C1BR)
add("C1B-02", C1BP, "s4 M3 table", "normal .693/.686; C1 window .697/.686; readout tick .511/.500; corrected .501/.500; lat+1 .493/.500; lat-1 .741/.715; freeze_rule .520/.522; routing .693/.686; zero_comm .500; rule predicts .50",
    J({k: s1[k]["arms"] | {"rule_predicts": s1[k]["rule_predicts"]} for k in ("0a23398f", "f6b623cd")}), "MATCH", raw=C1BR)
add("C1B-03", C1BP, "s4", "T positive components: C1 window lo99 0.655 / 0.643", J({k: s1[k]["c1_window_lo99"] for k in ("0a23398f", "f6b623cd")}), "MATCH", raw=C1BR)
add("C1B-04", C1BP, "s4 M2 table", "normal .883; reset S/inbox .883; reset Kp/En n/a; reset w .817; reset all non-packet .821; flush mid-gap .497; flush pre-readout .853; ITI sham .888; corrected .500; zero_comm/rand payload .500; signed-sum predictor .44 (p .998)",
    J(s1["4ab2ba01"]["arms"] | {"census": s1["4ab2ba01"]["census"]}), "MATCH", raw=C1BR,
    notes="the .44 predictor reading was later corrected (CORRECTIONS K1: component 0 only)")
add("C1B-05", C1BP, "s4", "Carryover: ~1500-1900 packets in flight at every trial onset, not correlated with previous target",
    J({k: [v["carryover"], v["carry_flag"]] for k, v in s1.items()}), "MATCH", exceeds="minor", raw=C1BR, notes="M2 is 1933 (rounds to ~1900)")
add("C1B-06", C1BP, "s5", "M2 fresh: k0 .527 no; k1 .842, k2 .862, k3 .861 SIGNAL; M3 0a23 0.54-0.59 0/4; f6b6 .577 yes, .626 yes, .560 no, .594 yes",
    J([x[:5] for x in D["c1b_S2"]]), "MATCH", raw=C1BR)
add("C1B-07", C1BP, "s5/s12", "M2 in-flight memory reproduced under fresh seeds YES (3/3)", f"SIGNAL {D['c1b_M2_fresh_SIGNAL']} searches; flush kills in {D['c1b_M2_fresh_flush_kills_among_SIGNAL']} SIGNAL champions", "MATCH",
    "SIGNAL champions (3 of 4 searches)", "yes", exceeds="minor", correction="'3 of 4 fresh searches reached SIGNAL, and all 3 are in-flight memories'", raw=C1BR)
add("C1B-08", C1BP, "s5", "f6b623cd's three SIGNAL champions: C1 window no effect; readout-tick drop -> .50; latency +1 -> .50; champions reach .56-.63",
    J([x[6] for x in D["c1b_S2"] if x[1] == "f6b623cd" and x[4]]), "MATCH", raw=C1BR)
add("C1B-09", C1BP, "s6", "S3 recheck: RELAY C1 window .50-.64, corrected .50 in all 4; MAJ 4781 .50, 6131 .54 -> ~.50; 0a23 .70, f6b6 .69 -> .50; frozen_routing VACUOUS in both M3 cells; no RELAY/HOLD verdict moves",
    J({k: [v.get("drop_window_c1"), v.get("drop_window_corrected"), v["frozen_routing_C1"]] for k, v in s3.items()}), "MATCH", raw=C1BR)
add("C1B-10", C1BP, "s7 P4/P6", "P4 reset_inbox alone does not drop M2 (0.883); P6 recheck changes no RELAY verdict", f"reset_inbox {s1['4ab2ba01']['arms']['reset_inbox']}; RELAY corrected all .500 (C1 causal rule already met)", "MATCH", raw=C1BR)
add("C1B-11", "pte/c1b/CORRECTIONS_2026-09-27.md", "K1-K3", "component-1 sign decodes the cue at 1.00; swap of component 1 flips; 3/3 fresh; w swap carries nothing 4/4; rule state identical in mirror partners",
    "not in c1b rows; source is SPIKES_2026-09-27_LOG / research/spikes outputs", "REPORT_ONLY", raw="research/spikes/ (not re-derived here)")
# ------------------------------------------------------------------ Harvest headline
HV = "research/harvest/INFERENCE_HARVEST_HANDOFF.md"
z = D["zero_comm_exact_half"]
add("HV-01", HV, "s1.1", "zero_comm exactly .500 in 213/213 RELAY, 174/174 MAJ, 95/95 XOR rows; forced by mirror-pair construction; COMM_DEPENDENT = SIGNAL there",
    f"RELAY {z['RELAY/evolve+transfer']} (= {z['RELAY/evolve']} evolve + {z['RELAY/transfer']} transfer); MAJ {z['MAJ/evolve+transfer']}; XOR {z['XOR/evolve+transfer']}; FLIP {z['FLIP/evolve+transfer']}, HOLD {z['HOLD/evolve+transfer']} (not forced); D-wave zero_comm,max_loss {D['D_zero_comm_maxloss_comm_fams']}",
    "MATCH", "evolve + transfer rows (kinds mixed, harmless here)", "yes",
    notes="[V] code: envs.build never places the actuator on a sensor in RELAY/XOR/MAJ (_pick_at needs distance d >= 1; XOR excludes s1,s2), and assays.evaluate shares physics seeds within a mirror pair, so with comm off the actuator trajectory is identical in both twins and the pair mean is exactly .5. FLIP is not forced (teacher lands on the actuator).")
add("HV-02", HV, "s1.2", "Evolved PTE transport is one hop: 35+4+9 of 50 competent RELAY cells and 19/19 MAJ cells need no relay; multi-hop has 2 marginal cells",
    f"RELAY SIGNAL by topology|radius|d {J(D['RELAY_SIGNAL_topology_radius_d'])}; multi-hop {J(D['RELAY_SIGNAL_multihop_cells'])}; MAJ {J(D['MAJ_SIGNAL_topology_radius_d'])}. SIGNAL rate by hop class, A1 only: RELAY {J(D['signal_by_hop_class']['RELAY/A1'])}, MAJ {J(D['signal_by_hop_class']['MAJ/A1'])}; all waves RELAY {J(D['signal_by_hop_class']['RELAY/all'])}",
    "MATCH", "50 RELAY SIGNAL evolve rows = 17 distinct physics x task conditions (14 physics); 27 at the d9cc point; 6 are D replicate searches", "no", exceeds="yes",
    correction="'Of 50 RELAY SIGNAL evolve rows (17 distinct conditions, 27 at one physics point), 48 are one-hop tasks. The unbiased A1 census found SIGNAL in 3/18 one-hop and 1/26 multi-hop RELAY searches (0/16 on random graphs); follow-up waves sampled almost only one-hop tasks (4 multi-hop rows after A1). So multi-hop is rarer in A1, but not shown to be absent.'",
    notes="smallworld d is BFS hops on a radius-1 torus base, so smallworld d=1 is one hop (counted with the 9). MAJ 18 one-hop + 1 global, reproduces. A1 Fisher exact: RELAY one-hop 3/18 vs multi-hop 1/26 p=.29; vs multi-hop+random 1/42 p=.077; MAJ 3/20 vs 0/25 p=.080 (scipy)")
add("HV-03", HV, "s1.3", "fitness shaping pays one-sided codes (acc .75 plus full contrast bonus)", f"w_contrast {D['A_search']['w_contrast']}, w_any {D['A_search']['w_any']} in every A search spec", "PARTIAL",
    notes="weights verified; the 'plausible common cause' is untested, as stated")
add("HV-04", HV, "s2", "only ONE law was scaled, and it is unreproduced", f"E RELAY sources {D['E_RELAY_sources']}; reps {dd['bbef66a1']['reps']} (neither SIGNAL)", "MATCH")
add("HV-05", HV, "s2", "KILLED: C1 MAJ/XOR REACH_BEYOND_HOP labels (a silent program scores 1.0)",
    "code (assays.twin, legacy key): reach measured from sensor column 0 only while every sensor column is negated, so divergence at other sensors counts as distal reach; MAJ D cells beyond_hop 1.0 (0a23, f6b6, 4781)", "MATCH",
    raw="prometheus/ananke/assays.py twin (beyond_hop vs beyond_hop_nearest)", notes="[I] from code; not re-run")
add("HV-06", HV, "s1.6", "verify_reach 'applied' while readout exactly NOT_REACHED (85 applied ticks)", "H-INST test fixture value; not re-run", "REPORT_ONLY", raw="research/harvest/H-INST/logs/pytest.log")
add("HV-07", HV + " ; H-PLANT/REPORT.md", "s8 ; s6 A7", "17% of C1 XOR evolve rows are light-cone-capped below .60 (XOR 37/218, FLIP 24/247, RELAY 22/406 'evolve rows')",
    f"lc_census.py filters only wave != A0, so its 871 'evolve rows' include B/B2 census, C transfer and D adjudicate rows. Split: {J(D['lightcone_capped_by_kind'])}",
    "MISMATCH", "non-A0 rows of every kind", "no", exceeds="understates",
    correction="'36 of 83 C1 XOR evolve rows (43%; 35/71 in A1) and 24 of 82 FLIP evolve rows (29%) are light-cone-capped below .60'",
    raw=ROWS + " ; H-PLANT/out/lc_census.json", notes="also H-PLANT REPORT 'none of the 55 RELAY rows with held lo99 > .55' = 50 evolve + 5 transfer rows")
add("HV-08", HV + " ; H-PLANT/REPORT.md", "s8 ; L50 ; L29", "FLIP @ d9cc NULL is search-limited (cells 6f82f9c7 held .479 and ef77ef2e held .507); XOR at d9cc: 'the one XOR point where C1 searched (cells d64656f2 and 1b26026f)'",
    f"kinds: {J({k: D['kind_of_cited_cells'][k][:4] for k in ('6f82f9c7', 'ef77ef2e', 'd64656f2', '1b26026f')})}", "MISMATCH",
    exceeds="yes", correction="'FLIP @ d9cc: one searched NULL (6f82f9c7, held .479); ef77ef2e is a transfer of RELAY champion bbef66a1, not a search. XOR @ d9cc: one searched cell (d64656f2); 1b26026f is a transfer.'",
    notes="TRANSFER-AS-SEARCH instances 2 and 3 (after fac4aaa2). Handoff s8 itself cites only 6f82f9c7 (correct); the principal review did not re-check ef77ef2e")
add("HV-09", HV + " ; H-PLANT/REPORT.md ; H-PLANT/PLAN.md", "s8 ; L59 ; L120", "fac4aaa2 described as 'C1 RELAY NULL cell ... C1 search held .5'",
    f"kind {J(D['kind_of_cited_cells']['fac4aaa2'])}: a C-wave TRANSFER of bbef66a1 to d5; zero RELAY multi-hop evolve rows exist at d9cc", "MISMATCH",
    correction="handoff s8 wording ('fac4aaa2 is a transfer of a one-hop champion') is already correct; H-PLANT REPORT L59 and PLAN L120 still say NULL/search", notes="instance 1 (known, principal-corrected in PRINCIPAL_REVIEW and handoff)")
add("HV-10", "research/harvest/H-PLANT/PRINCIPAL_REVIEW.md", "item 2", "9 multi-hop evolve cells exist only at other physics",
    "RELAY multi-hop evolve rows: ring 5 + torus 4 = 9 by ceil(d/r); plus smallworld d>1 21 and random d>1 16 (d is BFS hops there) = 46", "PARTIAL",
    "ring/torus only", "no", correction="'46 multi-hop RELAY evolve rows (9 ring/torus, 21 smallworld, 16 random), none at d9cc; 2 reached SIGNAL'")
add("HV-11", HV, "s8", "XOR @ d9cc physics-limited: light-cone caps any program at .574", "H-PLANT/out/lightcone_*.json: f_in_reach .1484, acc_upper_bound .5742 for d64656f2 (also computed for transfer 1b26026f)", "MATCH",
    raw="H-PLANT/out/lightcone_d64656f2_1b26026f_6f82f9c7_fac4aaa2.json", notes="analytic bound read from file; bound function not re-implemented")
add("HV-12", HV, "s8", "a one-flag readout passes C1's XOR SIGNAL rule (.763)", "1 - .237 ('+ iff P' at X0, H-PLANT/out/xor_mf.json); complement, not separately run", "PARTIAL",
    raw="H-PLANT/out/xor_mf.json", notes="X0 is H-PLANT's designed physics, not a C1 cell; the claim is about the rule, fine")
add("HV-13", HV, "s1.2", "Multi-hop has 2 marginal cells and no plant", "2 cells: lo99 .556 and .564; 'no plant' was refuted by H-PLANT (relay_flood .984 at d9cc d5; A0 plant rows .97-.99 at multi-hop envs)",
    "PARTIAL", exceeds="superseded", notes="handoff s8 addendum supersedes 'no plant'; s1.2 text not annotated")
# ------------------------------------------------------------------ ARC3 / engine card items derivable from C1 rows
add("ARC-01", "research/PTE_ENGINE_CARD.md", "BEST EXPERIMENT TYPES", "Transfer across size (laws are size-free) and topology (they are topology-bound)",
    "size: 1 law, unreproduced, one hop at every N (C1-23); topology: the transplant changed hop count 1->3; at d=1 on the random graph all 4 laws stay above chance (C1-22)", "MISMATCH", exceeds="yes",
    correction="'Transfer across size has been tested for one law (one-hop task, unreproduced law); the topology result is a hop-count effect (C1-22)'")
add("ARC-02", "research/SYNTHESIS_2026-09-28_ARC3.md", "s14", "What PTE does NOT give: ... rich composition (XOR/FLIP NULL)",
    "XOR 0/83 with 36 capped by light cone; FLIP 0/82 but a 16-line plant solves FLIP at d9cc (.97-.98)", "PARTIAL", exceeds="yes",
    correction="'XOR/FLIP were not found by C1-budget search (FLIP is expressible: a 16-line plant scores .98 at d9cc; 43% of XOR searches were physically capped)'")
add("ARC-03", "research/SYNTHESIS_2026-09-28_ARC3.md", "s1 / s14", "H6: search reachability, not physics, bounds what PTE shows (four lines of evidence)",
    "none of the four lines is a search-vs-plant comparison at matched physics except W-L; the first direct one is H-PLANT FLIP (1 cell); XOR at d9cc is physics-capped", "PARTIAL", exceeds="yes",
    notes="see sub_arc3 6c (designed_echoes are plants, not searches)")
add("ARC-04", "research/THREADS.md", "E-ANANKE rows", "E-ANANKE id -> artefact path map", "all listed paths checked for existence (see notes)", "MATCH",
    raw="research/THREADS.md", notes="the rows carry no quantitative claims; provenance only")
add("ARC-05", "research/ARC3_PRIORITIES.md ; BACKLOG_V2.md ; SYNTHESIS ARC2", "T-RET-2 etc.", "'the f7e62fe3 w-integrator' treated as a specimen id",
    f"f7e62fe3 is the D-wave ADJUDICATE row of RELAY 62a7fff9 ({J(D['kind_of_cited_cells']['f7e62fe3'])}), not an evolved cell", "PARTIAL",
    correction="name the specimen by its champion (62a7fff9, via adjudication row f7e62fe3)", notes="provenance naming hole: the same genome appears under two ids in W-E/W-G")

# ------------------------------------------------------------------ THREADS path check
import os
miss = []
for line in (HERE.parents[2] / "THREADS.md").read_text(encoding="utf-8").splitlines():
    if "E-ANANKE-" in line and "/" in line:
        p = line.split()[-1] if not line.strip().endswith(")") else None
        tok = [t for t in line.split() if "/" in t]
        for t in tok:
            base = HERE.parents[3] / t  # roles/Ananke/<t>
            base2 = HERE.parents[2] / t
            if not (base.exists() or base2.exists()):
                miss.append(t)
L[[x["claim_id"] for x in L].index("ARC-04")]["rederived_value"] = f"missing paths: {miss or 'none'}"

# ------------------------------------------------------------------ merge helpers
for sub, fn, pre in (("sub_arc3", "arc3_claims.csv", "A3-"), ("sub_swap", "swap_claims.csv", "SW-")):
    p = HERE / sub / fn
    if not p.exists():
        continue
    with p.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            L.append(dict(claim_id=pre + r.get("claim_id", ""), doc=r.get("doc", ""), location=r.get("location", ""),
                          claim_text=r.get("claim_text", ""), rederived_value=r.get("rederived_value", ""),
                          status=r.get("status", ""), denominator=r.get("denominator", ""),
                          denominator_ok=r.get("denominator_ok", ""), wording_exceeds=r.get("wording_exceeds", ""),
                          proposed_correction="", raw_path=r.get("raw_path", ""),
                          notes=(f"report={r.get('report_value', '')} | src={r.get('source_report', '')} | " + r.get("notes", ""))))

cols = ["claim_id", "doc", "location", "claim_text", "rederived_value", "status", "denominator", "denominator_ok",
        "wording_exceeds", "proposed_correction", "raw_path", "notes"]
with (HERE / "claim_ledger.csv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(L)
own = [x for x in L if not x["claim_id"].startswith(("A3-", "SW-"))]
print("own", len(own), collections.Counter(x["status"] for x in own))
for pre in ("A3-", "SW-"):
    sub = [x for x in L if x["claim_id"].startswith(pre)]
    print(pre, len(sub), collections.Counter(x["status"].split()[0] if x["status"] else "" for x in sub))
print("total", len(L))
