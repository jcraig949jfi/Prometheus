# AMENDMENT 2026-09-28b to PREREG_P11.md -- written AFTER the first constructed-panel run and BEFORE its re-run

Why this exists. The first full panel run (kept unaltered as results/PANEL_prerepair.jsonl, CONFUSION_prerepair.json,
GATES_PANEL_prerepair.json; E0 and E1 both passed there) exposed two gate-implementation errors and one specimen
design defect. The rule in PREREG s5.1 is: a specimen failing its design-fact gate gets ONE logged repair and is
re-gated. No certificate definition, threshold, perturbation set, stop rule (D1/D2/D3) or the A0 prediction changes.
The natural-donor run (s4.2) has NOT been started; nothing here affects it except that it runs after this amendment.

## A. Gate-code errors (my implementation did not test the preregistered design fact)
A1. "child sterile" (Z1, Z2). Implemented as "generation-2 victim half == the raw victim draw". Wrong: the victim runs
    its own random code, and the donor's pc runs on past its half into victim bytes, so the victim half can change
    without the child being a reproducer (Z2 draw 0: 2 donor-authored cells). Corrected test of the preregistered fact
    ("child as donor ... sterile"): in each of draws k = 0, 1, 2 of generation 2, donor-authored (prov) cells in the
    victim half <= 0.10 n AND fidelity(child, generation-2 victim half) < 0.90.
A2. "every single-site variant yields the same child" (TV-1) and "site-0 variants fall through" (TV-2). Implemented over
    the m = 3 substitutions only; PREREG makes V exhaustive for toy specimens. Corrected: checked over all 255
    alternatives at every site.

## B. Specimen defect found by A2, and the one repair
B1. Finding (from the pre-repair run, diagnosed before this amendment): in the SHARED toy ISA one substitution at site 0
    of TV-1 reaches other reproducer opcodes: 0x20/0xDF (PERIOD, a closed lineage) and 0x40/0xBF (HASH, a
    non-resembling lineage). So TV-1 and TV-2 fail their corrected gates, and the preregistered ground truth of every
    toy specimen whose truth is "exactly k bits" (TV-1 0, TV-2 0, TV-6 1, TV-6k 4) is false for the shared ISA: under
    it the analytic truth is TV-1 = log2(2) = 1 resembling bit (PERIOD) plus one non-resembling HASH lineage; TV-2 = 0
    resembling bits plus a HASH lineage; TV-6 = log2(3); TV-6k = log2(17).
B2. Repair (the single repair allowed): each toy specimen runs on the toy ISA RESTRICTED to the opcodes its mechanism
    uses; every other decoded opcode is a NOP. Active sets (decoded values): TV-1 {10}; TV-2 {20}; TV-3 {01,02,04,05};
    TV-4 {01,03,04,05}; TV-5b {05,06}; TV-6 {10,11}; TV-6k {10..1F}; TV-7 {40}; TV-8 {01,02,04,05,07}. Genomes unchanged.
B3. Scope deviation, stated plainly: PREREG says only a FAILING specimen is repaired. TV-6, TV-6k, TV-3, TV-4, TV-5b,
    TV-7 and TV-8 pass their gates, but the same shared-ISA premise underlies their declared truth and the D2 bit
    calibration (TB(TV-6) = 1, TB(TV-6k) = 4). I apply the same repair to all nine toy specimens so that one ISA rule
    governs the toy panel. RESULT reports D2 BOTH ways: on the repaired panel (decision), and on the pre-repair panel
    with the B1 corrected truth (sensitivity).
B4. New design-fact gates for the repaired toy panel (gen-1 facts, draw 0, exhaustive V): TV-6: the site-0
    substitutions that change the child are exactly 0x11 and 0xEE and both give 0x11 x 32; TV-6k: exactly the 30
    values 0x11-0x1F and 0xE0-0xEE, giving 15 distinct painter children. TV-1/TV-2: A2 as corrected.
B5. If any specimen fails its gate after this repair it is EXCLUDED (PREREG s5.1).
