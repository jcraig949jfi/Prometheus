# S4 BAND0 check -- RECEIPT (independent recomputation, 2026-09-27)

Worker: disposable spike for Odysseus. Checks the BAND0 decomposition in
roles/Odysseus/frontier/poi/raw/I1_z80_lineage_worlds.md (T2 lines 80-84, T3 lines 101-116, s5 D1 lines 618-621).
Computed from source first; the delegate text was read only afterwards, to find its definition of "window-dependent".

## Command
    cd /home/jcraig/Prometheus-worktrees/odysseus-base-role
    python3 roles/Odysseus/frontier/poi/spikes/S4_band0_check/probe.py     # < 1 s, stdlib only
Output: roles/Odysseus/frontier/poi/spikes/S4_band0_check/band0_check.json

## Inputs (repo HEAD e82bf231171775474a27ef3b1f637081332af943; last commit / sha256 prefix)
- archaeon/envgate2/RESULTS.json                c5ba19571c  5f13a717ae9c (matches VERDICT's "5f13a717ae9cb055")
- archaeon/envgate2/analyze.py                  87f51c5ee0  77324ca696ac
- archaeon/envgate2/mechanism.py                87f51c5ee0  695085d23951
- archaeon/envgate2/PREREG.json                 1475b79950  2bb468d3fdbc
- archaeon/envgate2/OPS_LOG.jsonl               c5ba19571c  a29030d03b6e
- archaeon/lineage/core.py                      87f51c5ee0  2237603d707b
- archaeon/lineage/assay_block.py               87f51c5ee0  b3c165ff242f
- archaeon/envgate2/VERDICT_2026-09-26.md       c5ba19571c  c17c231b09e4
- archaeon/envgate2/ENVGATE_CLOSURE_2026-09-26.md 13cdec715e d3c87b263059
- ops/threads/TH-001.md                         0a5c0895d9  04fd65b575de
The per-block run files (runs/block_XX.json) are NOT in the repo (off-repo evidence archive); only RESULTS.json was used.

## Definitions (quoted)
- Band: archaeon/envgate2/mechanism.py:26  `BAND = tuple(range(120, 136))`
- Arms: mechanism.py:57-58  U blocks nothing; `"BAND0": _arm("BAND0", ())`, `"R128": _arm("R128", (128,))`, RRIGHT restores
  128..131, RWEAK restores 125..128 (PREREG.json spec.design lines 11-22). mechanism.py:9-12: every blocked case "is replaced from
  the SAME 240-value pool (bytes outside the band)".
- Establishment: analyze.py:3-5 "a genetic lineage (glin) of random origin ... whose material reproduced outside the chamber,
  alive at root_end + 3 x max_age, with peak >= 0.25 N or genetic generation depth >= 10". Code: lineage/core.py:285-291
  (`st["births"] >= 1 and ... alive_at_check is True and (st["peak"] >= MIN_POP or st["max_ggen"] >= MIN_GEN)`), core.py:42.
- Counting: analyze.py:86 `Y[b][a] = len(s["genetic_established"])`; rows = RESULTS.json `established_glins` (analyze.py:89).
- "Gate": lineage/assay_block.py:77-78 `ruler_class` / `ruler_exact_inputs` are the census ruler of the ARRIVAL tape (founder),
  i.e. the inputs on which the founder copies exactly. EXACT_UNGATED = exact on all 256 inputs; NEAR_COPIER/NON_HIT = no exact input.
- First-birth input: core.py:248 `st["first_birth_input"] = x[0]` (input of the lineage's first birth, after arm replacement).
- Takeover: analyze.py:91 `final_ecology_pop >= 0.9 * 128` (per-world value NOT in RESULTS.json).
- "Window-dependent": NOT defined in any envgate2 file. Four explicit operationalisations are computed (below).

Check: established_glins (39 rows) reproduces per_block and totals exactly (U 24, RRIGHT 3, RWEAK 2, R128 5, BAND0 5).

## The 5 BAND0 establishments
| block | arrival | tape | ruler class | gate vs band | 1st-birth input | peak | births | established in arms |
|---|---|---|---|---|---|---|---|---|
| 4  | 688130 | b1f5c641 | NEAR_COPIER   | no exact gate   | 15  | 125 | 2,351     | BAND0 only |
| 11 | 17983  | c1829c8f | NEAR_COPIER   | no exact gate   | 221 | 128 | 3,776,795 | U RRIGHT R128 BAND0 (not RWEAK) |
| 13 | 541685 | 41e34180 | EXACT_UNGATED | exact on all 256| 45  | 128 | 1,899,890 | all 5 |
| 14 | 74051  | 23c1800b | EXACT_UNGATED | exact on all 256| 78  | 128 | 3,714,371 | all 5 |
| 15 | 574357 | 335b0aab | NEAR_COPIER   | no exact gate   | 170 | 33  | 81        | BAND0 only |
Tape hash is identical across arms for each shared arrival (arrival stream is paired across arms).

## Window-dependent establishments per arm
| definition | U | RRIGHT | RWEAK | R128 | BAND0 |
|---|---|---|---|---|---|
| D1 arm-unique (established in no other arm) [delegate's] | 21 | 0 | 0 | 2 | 2 |
| D2 same arrival NOT also established in BAND0             | 21 | 0 | 0 | 2 | 0 (trivial) |
| D3 D2 and (1st input or exact gate in arm's open set)     | 20 | 0 | 0 | 0 | 0 |
| D4 D2 and 1st input in arm's open set                     | 16 | 0 | 0 | 0 | 0 |
R128's 2 arm-unique rows: block 13 arrival 1036173 and block 14 arrival 314642, both NON_HIT, inputs 71 and 163 (outside band).
U's D2-minus-D3 row: block 23 arrival 185273, NEAR_COPIER, input 116.
U's D3-minus-D4 rows: 4 EXACT_GATED [128] founders whose first birth was at 112/117/118/112 (gate in band, first input not).

## Blocks / wall time (OPS_LOG submit -> block_done)
Slowest three: 11 (5.93 h), 14 (5.90 h), 13 (3.34 h); median 0.98 h. Non-U establishments by block: 4:1, 11:3, 13:5, 14:5, 15:1.
Frozen RESULTS: 13 takeover worlds holding 15 establishments -- consistent with b11 x4 + b13 {U,BAND0,RRIGHT,R128} + b14 x5
(b13 RWEAK lineage last_alive 22432 vs 32948 elsewhere), but per-world final pop is not in RESULTS so this is INFERRED.

## Verdict on each claim
1. "3 of the 5 are the same arm-invariant arrivals (taking over in nearly every arm)": CONFIRMED. Blocks 11/13/14, established in
   4/5/5 arms, peak 128, millions of births.
2. "...gates outside the band": PARTLY CONFIRMED -- wording wrong. None has a gate IN the band, but 13 and 14 are EXACT_UNGATED
   (exact on all 256 bytes, band included) and 11 has no exact gate at all. Correct phrasing: "not band-gated".
3. "2 have first-birth inputs outside the band" (blocks 4, 15; inputs 15, 170): CONFIRMED numerically, but TAUTOLOGICAL: in BAND0
   every band byte is replaced from the out-of-band pool (mechanism.py:9-12), so every BAND0 birth has an out-of-band input.
   The informative facts are instead: both are NEAR_COPIER (no exact gate) and both are BAND0-only (the paired arrival did not
   establish in U or any rescue arm) -- i.e. contingent, low-copy-fidelity founders; block 4's reached peak 125.
4. "window-dependent: U 21, every rescue arm 0": PARTLY CONFIRMED. The delegate's own operationalisation (arm-unique, D1) gives
   R128 = 2, not 0; "0" needs an extra criterion (D3/D4) which, applied consistently, gives U 20 (D3) or 16 (D4), not 21.
   Robust statement: RRIGHT and RWEAK are 0 under every definition; R128 is 0 once its two NON_HIT out-of-band founders are
   excluded; U is 16-21. The qualitative conclusion (no rescue arm produces a window-dependent establishment) holds.
5. "takeovers sit in the slowest blocks 11, 13, 14": CONFIRMED (5.93/3.34/5.90 h vs median 0.98 h; top-3 by wall time).
Minor: the delegate cites ENVGATE_CLOSURE lines 109-112 and VERDICT:82-84; the files have 36 and 71 lines -- the text is at
ENVGATE_CLOSURE_2026-09-26.md:20-22 and VERDICT_2026-09-26.md:63-65.

Overall: PARTLY CONFIRMED (1, 5 confirmed; 2, 3, 4 confirmed with corrections).

## Recommendation to Archaeon (thread owner; no change made here)
Replace "5 BAND0 establishments unexplained" in TH-001 with "5 BAND0 establishments DECOMPOSED, 2 residual": 3 are arm-invariant
takeovers by non-band-gated founders (ungated exact copiers b13/b14, near-copier b11) that the frozen viability-map model could
not predict (it counts only 128-gated census copiers; BAND0 R0 = 0 by construction); 2 (b4, b15) are BAND0-only near-copier
establishments whose paired arrival failed elsewhere -- still individually unexplained (contingency?), but not evidence of a
window mechanism. The residual fossil is then: why b4/b15 establish only in BAND0 and why b11's takeover misses RWEAK.

## Limits
- RESULTS.json only; block files are off-repo, so per-world final population, hosting detail and lineage genomes after
  mutation were not inspected. Ruler class is of the founder tape, not of the lineage at takeover.
- "Window-dependent" has no frozen definition; the counts depend on the operationalisation (table above).
- Takeover-world membership is inferred from glin trajectories (truncated to 80 points by assay_block.py:80), not read.
