# Self-location transplant tests: declarations (written BEFORE any transplant was run)

Delegate for Nestor, npe-arc3-2026-09-28. Computational artificial life: integer programs on the z8 VM.
Written 2026-09-28 before `selfloc.py` executed any condition. Nothing in this file is edited after results
exist; departures are recorded in SELFLOCATION.md under "Deviations".

## Substrate facts verified in code (z80atlas-verify-2026-09-22)

- `z8.run`: addresses masked `& (size-1)` if the tape is a power of two, else `% size`. Fresh `regs=None` -> all
  eight register slots 0, fz = fc = 0. LDIR/LDDR (ED B0/B8; on the dense VM also 1-byte 0xE5/0xE7): count BC,
  0 -> 0x10000, capped by the remaining step budget (each byte charged one step); afterwards HL/DE advanced,
  BC = 0, fz = 1. SELF (ED 32) sets HL = ctx.base, BC = ctx.length. GETPC (ED 33) exists but is DISABLED in
  both cells (ops mask 0x2A = SELF | SENSE | BLOCK). SENSE sets A = ctx.sense. JR is PC-relative; JP nn is
  absolute.
- `p11.interact`: tape pow2(2n) = 128 for n = 64; organism a at offset 0 runs first with sense 0, b at offset
  n runs second with sense 1; both ARENA. Donor-disabled control: donor policy OWN.
- Both cells: n = 64, slice = 300 steps, copy_mut = 0.002, ops mask 0x2A.

So the ENVIRONMENT supplies, by construction: (1) tape coordinates (the donor's base address, 0 or 64), (2) the
128-byte modular wrap, (3) the initial register state (fresh zeros), (4) sense (= execution index), (5)
execution order, (6) partner content, (7) the entry point (pc = base), and (8) on request, the SELF value
(base, length). The ORGANISM supplies its bytes. The tests below move one of (1)-(7) at a time.

## Reference condition and the criterion

REF = the standard P-11 assay on the donor's HOME side: tape 128, donor at h, random victim at h+64, home order
(h = 0 runs first, h = 64 runs second after the victim), sense = execution index, fresh registers,
genome unrotated. h = 0 if the standard side-0 rate >= the side-1 rate, else 64.

Generalized criterion GP11 (per seed): 3 randomized-victim draws; per draw C2 (final victim-slot fidelity to
the donor slot >= 0.90), C4 (donor authored >= 0.90 of the directed changes), C5 (donor-disabled control
fidelity < 0.90); seed passes if >= 2 of 3 draws pass. This is `p11.assay` with the tape layout, order,
sense, start state and entry point made parameters. Donor-disabled control uses OWN, or FREE with the
wrapped part of the own span as the free window when the donor's span wraps the tape end.
VALIDATION (must hold before any transplant result is used): GP11 in the standard layout with p11's own seed
tags reproduces `p11.assay` pass/fail exactly on >= 40 genomes x both sides.

Rate(condition) = passing seeds / K, K = 8 seeds, same victim draws (seed tag without the condition name)
across conditions so comparisons are paired. pass(c) := rate(c) >= 0.5.

## Tests (each changes exactly one factor from REF)

T1 tape offset (tape rotation). Donor at (h+d) mod 128, victim at (h+d+64) mod 128, d in {1,4,8,16,32,48,64},
home order and home sense, fresh zeros. Also STD_OTHER = the standard assay on the other side (changes
position, order and sense together; descriptive).
  - ORGANISM-supplied self-location: passes at d not a multiple of 64 (the genome finds its own base).
  - ENVIRONMENT-supplied: fails once d exceeds the copy's anchor tolerance (~6 bytes of fidelity slack).
T2 geometry. G256_ADJ (tape 256, victim at h+64, 128 blank bytes elsewhere, non-executing); G256_HALF (tape 256,
victim at h+128); G256_HI (tape 256, donor at 128+h, victim at 192+h); G192_ADJ (tape 192, not a power of two,
victim at h+64, third slot blank).
  - Pass G256_ADJ: the destination is own-base + 64 (genome-length relative), not a 128-wrap artefact.
  - Fail G256_ADJ while passing REF: relies on 128-byte wrap (e.g. high-address bits of immediates ignored).
  - Pass G256_HALF only: destination tied to tape half (not expected; would be environment-geometry).
T3 initialization. At home: CONST55 (all registers 0x55), CONSTFF, RAND (all registers and flags random per
seed), HL_PARTNER (HL = h+64), SELFPTRS (HL = h, DE = h+64). At displaced d = 32 (T1 d=32 is the zero
reference): D32_HL_SELF (HL = h+32), D32_DE_PARTNER (DE = h+96), D32_HLDE (both), D32_PTRSHIFT (L = E = 32 on
top of zeros, i.e. the zero origin shifted with the donor).
  - Pass RAND and both constants: the organism sets every register it uses (state-free; organism-supplied).
  - Fail RAND/CONST: the fresh zero state is an input (environment-supplied).
  - Fail T1 d=32 but a D32 seeding restores it: the missing coordinate lived in the initial registers, and
    the environment can re-supply it (state-anchored). No seeding restores it: the coordinate is an
    immediate/absolute address baked in the genome, and only the tape position can make it right
    (tape-anchored).
T4 neighbour/partner. P_BLANK (victim zeros), P_NOEXEC (victim does not execute), ORDER_FLIP (donor's execution
slot flipped, sense kept), SENSE_FLIP (sense = 1 - home sense, order kept), P_SELF (victim = copy of donor;
DESCRIPTIVE ONLY: records whether both halves still equal the donor at the end; not in GP11 or classes).
  - Fail P_NOEXEC or P_BLANK: the partner's execution or content participates (partner-relative).
  - Fail SENSE_FLIP: the organism reads the environmental side cue.
T5 translation within the slot. Genome rotated by r in {+1,+4,+16,-4} (slot bytes g' = g rotated right by r,
wrap within 64). _BASE: entry at the slot base (what the world does). _FOLLOW: entry at the moved program
start (base + r mod 64). The criterion copies the slot content g'.
  - Pass _FOLLOW: code is position-independent inside the slot (relative control flow and absolute copy
    region) - the copy is of the slot, so an absolute-slot copier passes if its code still runs.
  - Fail _FOLLOW: absolute jumps / immediates that address its own code.

## Classes (defined by transplant behaviour only; eligible = pass(REF))

Primary axis, self-location source:
  LOCATOR      pass at >= 5 of the 6 offsets d in {1,4,8,16,32,48}.
  PARTIAL      not LOCATOR, but pass at d = 32 with zeros.
  STATE_ANCHORED  fail at d = 32 with zeros; pass at d = 32 under >= 1 of the 4 D32 seedings.
  TAPE_ANCHORED   fail at d = 32 with zeros and under all 4 D32 seedings.
Secondary flags: STATE_FREE (pass RAND and CONST55 and CONSTFF), WRAP_DEPENDENT (fail G256_ADJ), PARTNER_REL
(fail P_NOEXEC or P_BLANK), SENSE_READ (fail SENSE_FLIP), ORDER_DEP (fail ORDER_FLIP), POS_INDEP_CODE (pass >= 3
of 4 _FOLLOW rotations).

## Predictive tests (declared before running)

(a) State robustness: the X-DD-SELFSTATE measure (run_ss.py logic: k prior blank-partner executions, carried
registers, then run_nc.copies = predecessor acceptance AND P-11), k in {0,1,2}, 5 seeds x 2 sides.
SELF_POISON if rate_1 < 0.25 rate_0 (rate_0 >= 0.1 required, else UNMEASURABLE).
(b) Competence under reset: rate_0 of (a) (fresh start each time, world criterion incl. predecessor
acceptance) >= 0.5.
(c) SELF-dependence: q1_partial.jsonl rate_full >= 0.5 and rate_noself < 0.5.
Expectations written now: E1 STATE_FREE copiers are almost never SELF_POISON (they overwrite what they read);
E2 STATE_ANCHORED copiers are mostly SELF_POISON; E3 LOCATOR, if any exist, are SELF-dependent (GETPC is off,
so SELF is the only in-VM locator); E4 TAPE_ANCHORED is the majority class. If a class adds nothing beyond
STATE_FREE for (a) and beyond SELF-dependence for LOCATOR, I say so and stop cataloguing.

## Sample

All competent (rate_full >= 0.5) SELF-dependent genomes in q1_partial.jsonl (55), all competent first donors,
and a stratified random draw of competent SELF-independent genomes filling to 300 non-SELF-dependent genomes,
strata = (cell, VM, origin experiment), equal allocation capped at stratum size, seed 20260928.
Lineage caveat declared: genomes from one run are not independent; per-class run counts are reported.
