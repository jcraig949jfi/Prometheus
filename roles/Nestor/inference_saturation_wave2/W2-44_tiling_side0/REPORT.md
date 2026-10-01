# W2-44: what makes in-world rotated runaway roots side-0 converters, and is CRW_1 a third class?

> Saved by Nestor from the worker's returned text, condensed with every number kept. The harness blocks report-file writes by subagents.
> - **Run:** 03:01:48Z–03:14:41Z, about 9 CPU-min, static.
> - **Harness:** stock z8, ZERO donor context, N = 1000 bank panel. Baselines reproduce W2-35 s4 exactly.
> - **Files:** `common44.py`, `t0_genomes` … `t6_hijack` (.py/.json/.log).

## Answer

### 1. Every side-0 root uses "own base → absolute DE ≡ 64", reached in three ways
- **CNR_s22 (frame 62): one byte, founder position 43, c1→81 (`ADD A,C`).**
  - Mechanism: A = C = 0x40, then `LD E,A`, so E = 0x40.
  - F+{43:81}: conv_s0 1.0, m 1.243. This is W2-26's "43 c1→81".
  - Position 43 is one bit away both from C3 (self-defence) and from 81 (side switch).
- **CRW_78 (frame 57) and XH2N_s1 (frame 47): the chained LDIR (new route).**
  - The tiling duplicated `ED B0`; the 2-byte core sits at founder positions 57–60.
  - At side 0, B = L = 0, so the first LDIR is a 64-byte in-place self-copy that leaves DE at 0x40. The second LDIR (BC = 0, budget-truncated) then copies own base → 64.
  - Transplanted into the founder frame, F+{59:ED, 60:B0} gives m 1.456.
- **CRW_1 (frame 46): chained via an absolute jump.** See section 2.
- **Two artefacts ruled out.**
  - The single-revert screen overstates criticality.
  - The partner's byte 0 does not matter: the founder's `LD (BC),A` at 42 zeroes it first.

### 2. CRW_1 is a dual-pass copier: two copy paths through ONE LDIR
- **Core:** P46 + {43:D2, 44:A2} = `JPNC A4A2`, which resolves to absolute 34, the address of its own LDIR at side 0. Core m 1.874 (root 1.881).

| | side 0 | side 1 |
|---|---|---|
| Pass 1 | LDIR at 34, DE = 0, n = 64: in-place self-copy, DE ends at 0x40 | LDIR at 98, DE = 0, n = 0x4040 (budget-exhausting): **converts** |
| Pass 2 | JPNC (carry always clear) back to 34, BC = 0, DE = 0x40: **converts** | never reached |

- **What selects the pass:** the side-specific count `LD B,L` (W2-24).
- **Conversions by pass:** side-0 conversions all go through LDIR #2 (200/200); side-1 conversions go through LDIR #1 (178/200).
- **Side-1 protection.** A side-0 intruder that reaches the absolute JP lands on its *own* byte 34, not on CRW_1's LDIR. Side-1 losses are founder-like: 58 for the core and 55 for the root, against F's 48. The fall-through chained types are hijacked through their second LDIR (CRW_78: 236 losses, at partner@116).
- **In-world origin (CRW_1 seed).**
  - e33: an LDIR tiling wrote frame-46 founder code over slot 66. The slot kept a JPNC from its old foreign content, now targeting 0x62. That genome had m 0.895 and conv_s0 0.
  - e35: a one-bit change at 44 (e2→a2) retargeted the jump to its own LDIR, giving m 1.881. Whether that bit came from a copy error or an in-place write is unresolved.

### 3. Dual-pass converters are a third mechanism class
- **The construction generalises:** P_s + JPNC/JP at founder position 61, with low byte (52+s) % 64, gives a two-sided converter.
  - It works in frames 0, 1 and 41–63, with m 1.70–1.94.
  - It fails in frames 2–40.
- **Reachability.**
  - None of F's 512 one-bit mutants is two-sided.
  - The founder-frame version, JP0 = F+{61:D2/C3, 62:34}, needs 2 bytes and ≥ 4 bits.
  - In-world it arose as tiling + foreign JP residue + 1 bit.
  - Once formed it is robust: 390/512 one-bit mutants stay two-sided (mean m 1.635).
- **Protection depends on the frame.** In frame 0, JP0 has panel m 1.895, the best in the panel, but in kin contact F at side 0 reaches JP0's JP and lands on F's own LDIR, so it is hijacked. In kin contact it is no better than AC.
- **Exact-identity scoring needs the byte-0 fixed point.** The frame-46 code zeroes byte 0 of every half it writes, so the root and core never produce exact children (W = 0, a scoring artefact). The fixed point CRW1fx (g[0] = 00) has exact_child 0.608.

## T1: in-world roots

| root (frame) | core bytes (pos: P→g, founder pos) | route to DE ≡ 64 | conv_s0 / conv_s1 / keep_s1 | m root → core |
|---|---|---|---|---|
| CNR_s22 (62) | 41: c1→81 (f43) | `ADD A,C` → `LD E,A` | 1.0 / 0.51 / 0.52 | 1.497 → 1.236 |
| CRW_78 (57) | 52–53: 95 40→ED B0 (f59–60) | chained LDIR, fall-through | 1.0 / 0.54 / 0.54 | 1.524 → 1.508 |
| XH2N_s1 first (47) | 40–41: ee ff→ED B0 (f57–58) | chained LDIR, fall-through | 1.0 / 0.006 / 0.49 | 1.224 → 1.522 |
| CRW_1 (46) | 43–44: c1 00→D2 A2 (f61–62) | chained via absolute JPNC | 1.0 / 0.88 / 0.89 | 1.881 → 1.874 |
| CNR_s4, CRW_75, XH2N_s1 last | none (conv_s0 0) | — | — | 1.11 / 1.18 / 1.10 |

## T2: founder-frame analogues (N = 1000)

| genome | keep0 | keep1 | conv0 | conv1 | m_base |
|---|---|---|---|---|---|
| F | 0.521 | 0.907 | 0.002 | 0.874 | 1.172 |
| F+43:81 | 1.0 | 0.516 | 1.0 | 0.017 | 1.243 |
| F+44:AC | 1.0 | 0.521 | 1.0 | 0.021 | 1.248 |
| F+59:ED,60:B0 | 1.0 | 0.479 | 1.0 | 0.467 | 1.456 |
| F+43:C3,44:AC | 1.0 | 0.961 | 1.0 | 0.01 | 1.469 |
| JP0 | 1.0 | 0.913 | 1.0 | 0.884 | 1.895 |
| CRW_1 core | 1.0 | 0.888 | 1.0 | 0.868 | 1.874 |

## T3: invasion, exact identity, BASE, ZERO context
Entries are W(row | col).

| | F | C3 | AC | C3+AC | CRW1fx | JP0 | CNR22 | CRW78 |
|---|---|---|---|---|---|---|---|---|
| F | 1 | 1 | 1 | 0 | **0** | 1 | 1 | 1 |
| C3 | 1 | 1 | 1 | 1 | **0** | 1 | 0 | 1 |
| AC | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| C3+AC | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| **CRW1fx** | **2** | **2** | 1 | 1 | 1 | 1 | 1 | 1 |
| JP0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| CNR22 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 |
| CRW78 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

- **BANK context:** CRW1fx scores 1.312 vs F/C3 and 0.777 vs AC/C3+AC/JP0.
- **ATOMIC/BANK:** 1.545 vs F/C3.
- **Panel m_atomic:** CRW1 1.936 ≈ JP0 1.939 ≈ CRW1fx 1.931 > C3+AC 1.487 > C3 1.448 > F 1.263.

## Adversarial points
1. **The cores are 1-minimal, not unique.** An alternative CRW_1 route exists: P46+{30:5E}, m 1.629, copying to 66.
2. **"Third class" is a mechanism class, not a selective one.** It is neutral against side-0 converters and drops to 0.777 under BANK. Its m comes mostly from non-kin partners.
3. **Frame-relative protection is inferred.** A frame-46 kin intruder at side 1 was not tested beyond the CRW_1 contacts.
4. **e2→a2 is a single event** with an unknown mechanism.
5. **The byte-0 fixed point is constructed.** The real lineage lies between CRW1 and CRW1fx.
6. **All static and ZERO-context.** BANK is the only context check.

## Ledger entry (W2-44)
- **Inference.**
  - Every side-0 root uses "own base → absolute DE ≡ 64", reached by `ADD A,C`, by DE post-increment from a duplicated LDIR, or by absolute-JP re-entry.
  - CRW_1 is a dual-pass copier whose second pass cannot be reached by an intruder.
  - The design works in 25 frames. In frame 0 it is hijackable by kin.
- **Confidence.** High for the mechanisms; moderate for the ordering; low for in-world frequency.
- **Strongest objection.** Dominance needs frame mismatch plus a constructed fixed point, and it weakens under bank contexts.
- **Next.**
  - Exact contact with self-carried contexts.
  - JP-residue frequency across the replays.
  - Scan runaways for a JP into their own LDIR.
  - Design only: a mixed run of F / C3+AC / CRW1fx / JP0.
