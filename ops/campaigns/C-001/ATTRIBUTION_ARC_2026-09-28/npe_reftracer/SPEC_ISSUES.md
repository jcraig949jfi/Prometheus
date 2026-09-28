# NPE reference tracer: spec issues, the choices I made, and where another conforming tracer could differ

Spec: ANCESTRY_PREREG_v4.md s1, s2.1-2.2, s4.1 (+ Amendment B1), as modified by ANCESTRY_PREREG_v5.md R1, R4, R8, C1-C5.
Engine: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/ (z8.py, world.py, p11.py, z8taint.py), used read-only.
Engine files are cited as `file:line`.

Each issue is tagged:
- **[DIVERGE]**: another conforming tracer could legitimately choose differently, and the per-locus fields would then differ.
  These are the likely sources of three-way disagreement (v4 s4.3).
- **[NOTE]**: a fact about the engine or the cell that the text does not state.
- **[GAP]**: the text says nothing, so I had to invent something.

---------------------------------------------------------------------------------------------------------------------------

## A. Unit, entities and pre-state

**A1 [NOTE] What the unit is in the engine.** One pair interaction is `world.Runner._pair_interact` (world.py:782-889):
- The 64-byte tape is `_pow2(2n)`, so for n=32 there is NO padding (world.py:787). The OTHER group is empty, as C5 N4 says.
- Organism a (offset 0, `sense=0`) runs first. Organism b (offset 32, `sense=1`) runs second on the same tape (world.py:801-811).
- Each slice gets budget `t["slice"]`. That is 360 in tier L (grammar.py:242). It is NOT `_slice_len`, even though the cell's
  pressure is EXEC_TIME_COST.
- Then each half is mutated and written back: a first, then b, from one world RNG (world.py:825-830). After that comes
  acceptance (world.py:839).

**A2 [NOTE] Only registers and flags persist, not the PC.** Each slice starts at the half's base, not at the persisted
`org.pc` (world.py:808/811). Persisted state is `regs` (8 bytes, including the unreadable slot `r[6]`) plus `fz` and `fc`
(world.py:812). A victim keeps its registers through a birth. `org.oid` is reassigned but `regs` is not reset (world.py:877).

**A3 [NOTE] The engine's production path is `z8taint.run_tainted`, not `z8.run`.** The cell is RESERVOIR x PAIR_EXECUTION, so
`track_material` is on (world.py:196-197, 807-809). The two functions compute identical values. My shadow is asserted equal to:
- `z8.run` per slice;
- `p11.interact` per interaction;
- the real `Runner._pair_interact` in selftest F11. That call goes through `run_tainted` and checks final halves, regs/flags,
  RNG state and acceptance count.

The engine's own niche tags (`here=org.niche`, `_mutated_orig`, which aligns by difflib: world.py:1351-1370) are a different
label system and use value alignment, which v4 s1.2 forbids. I do not use them.

**A4 [DIVERGE] Entity naming and orig_id.** v4 names entities by role in one execution (w = executing organism, o =
occupant/partner). In the pair both organisms execute, and each slice can run the other's material (see A5).
- I name entities by organism: `('ENTITY','a',j,orig)` and `('ENTITY','b',j,orig)`.
- `orig_id` is not defined for NPE, because there is no ALLOC. I take it from a caller-supplied per-locus vector (the persisted
  label vector). The default is the side name.
- Every pre-state byte is RE-BASED to `ENTITY(side, j, orig)` at interaction start, per the single-interaction rule (v4 s1.1)
  and "inherited labels count to their carrier entity".
- Alternative: carry the previous interaction's labels verbatim (e.g. a MUTATION or a foreign ENTITY), so that a byte's data
  label can name a third organism.

**A5 [NOTE -> DIVERGE] A slice can execute the partner's material.** The PC wraps modulo 64 over the whole tape (z8.py:211). In
selftest F2, a's NOP sled runs into b's code at 32, and a executes b's copier.
- So "the executing organism" (the slice) and the "performer" (the material of the opcode byte) are different things.
- I export both: `store_by` (slice side) and `performer`/`performer_entity` (material).
- R1's class key ("self = the executing organism") is ambiguous here. It could mean the slice's organism, the victim or the
  donor. I leave the class computation to the pipeline. A tracer that reports only one of the two fields would disagree on
  class.

**A6 [GAP][DIVERGE] Labels of persisted registers and flags.** s1.2 does not say what a persisted register's label is.
- My choice: `('PREG', side, 'B'|...|'A'|'fz'|'fc')`, a base label of its own kind. It is not ENTITY and not CONST. It forms the
  "persisted registers" source group of R1.3.
- `regs is None` (the organism's first interaction after `_place`) gives CONST('reset'), by analogy with BEE RESET registers.
- `trace_interaction(reg_labels_a=..., reg_labels_b=...)` can instead carry the labels exported by the previous interaction
  (`reg_labels_after`), per "label vectors persist".
- Alternatives:
  * label persisted registers as ENTITY of their organism, which would make a PREG store a MOVE and identifiable;
  * make them FOREIGN-INFORMATIVE;
  * always carry the labels over, which chains interactions. That violates single-interaction scope but follows v4 s1.2
    "Persistence".
- Selftest F4/F5 show PREG appearing in data labels and in COMPUTED bases.

## B. Data-label propagation (s1.2)

**B1 [DIVERGE] Logic ops' carry flag.** For AND/XOR/OR, `fc` is always 0 (z8.py:246-253: t stays in 0..255), so I label C
`CONST('logic_nc')` (also AND/XOR/OR n: z8.py:348-356). A tracer that labels C `COMPUTED(operands)` gets extra ctrl_deps at a
later JRC/JRNC/JPC/JPNC or ADC/SBC.

**B2 [DIVERGE] Result-independent idioms.** v4 lists XOR A,A and SUB A,A.
- I also treat CP A,A (0xBF) as an idiom: its flags are constant (Z=1, C=0).
- These stay COMPUTED over A: SBC A,A (the value is -C, but it is not listed), AND A,A, OR A,A, and value-level
  independences such as AND 0.
- The idiom flags (Z, C) are CONST.

**B3 [DIVERGE] COMPUTED_FROM scope.**
- INC r and DEC r on a register give COMPUTED_FROM(label).
- INC (HL) and DEC (HL) give COMPUTED{base}, because the operand is memory, not "register-only".
- 16-bit INC/DEC rr (z8.py:314-320): the low byte gets COMPUTED_FROM(low). The high byte gets COMPUTED{hi, lo} because of the
  carry. Alternatives: CF for both bytes, or COMPUTED for both. This mostly moves pointer labels, so addr_deps.
- Nesting is flattened: CF(CF(x)) = CF(x), and CF(COMPUTED S) = COMPUTED S.
- v4's "NPE NEG and rotate" does not apply: Z8 has neither opcode.
- The Z flag after INC/DEC r is COMPUTED{bases(r)}, not CF.

**B4 [GAP] COMPUTED with no non-constant base** (e.g. ADD A,B with both operands CONST) is kept as `('COMPUTED', frozenset())`.
It is new material, not CONST. Alternative: CONST.

**B5 [NOTE] Immediates.** LD r,n / LD rr,nn / ALU n: the value carries the operand byte's data label, and its addr set is that
byte's addr set. The PC (code location) is never a pointer label (v4 s1.4).
- So a control-flow bit decoder that selects between immediates (F3, K31-like) produces a MOVE of the executing organism's
  operand byte, with the real source only in ctrl_deps.
- The flip test cannot catch this. R1.3's dependence arm does: F3 shows 6/8 value changes when b is randomised, so the locus is
  not identified.
- If the "0" comes from XOR A,A, the label is CONST instead.

**B6 [NOTE] SENSE and GETPC.**
- SENSE gives `CONTEXT('SENSE_side')`, value = side (world.py:803; the always-on mask bit at world.py:234).
- GETPC gives `CONTEXT('GETPC')` on both H and L. H is always 0 because pc < 64 (z8.py:471).
- Disabled ED ops (ALLOC, BIRTH, SELF, SPLIT, LDIR, LDDR under mask 0x0C) are 2-byte no-ops (z8.py:399-466).

**B7 [DIVERGE] IN with no inputs.** C5 N3 gives `CONST('in_exhausted')`. R4 says IN pad bytes are `in_pad`. I followed N3,
because it is NPE-specific and later.
- C2 says the IN counter's label is "the PC label at that point" and acts as the load pointer. So A's addr set = the PC label
  at the IN.
- The engine never advances `in_cursor` when there are no inputs (z8.py:366-371). A tracer could therefore argue that the
  counter was never written and its label is empty, which gives an empty addr set. That changes addr_deps for stores of
  IN-derived bytes, and ctrl via flags.

**B8 [NOTE] OUT has no locus.** OUT appends to `ctx.outputs` (z8.py:388-390) and never writes the tape.
- The v4 "16-output guard" is a 64 guard here.
- The H1 gate `in_reads < out_gate_reads` is 0 < 0 in the pair ctx (z8.py:382).
- Both guards are evaluated conditionals. Their inputs are counters whose labels are subsets of the PC label, so they are
  no-ops in whole scope, and they are not branches, so they have no pdom scope.
- OUT events enter the store-address sequence for the flip test as `('OUT', who, k)` (R4).

## C. Dependence sets (s1.3 as amended by C2/R8)

**C1 [DIVERGE, big] ctrl scope across the two slices.** "Whole-execution PC label, no declassification" versus BEE SEPARATED's
"register labels reset at the second entry". I export four fields:
- `ctrl_deps` (PRIMARY): PC label accumulated from INTERACTION start. b's stores inherit a's conditions (F1: `{a6}` at b's first
  store).
- `ctrl_deps_slice`: PC label reset at each slice entry.
- `ctrl_deps_pdom`: the post-dominator scope (C3 below).
- `ctrl_deps_whole`: every condition evaluated in the whole interaction.

A tracer that treats the PC label as a register reset at b's entry reports my `ctrl_deps_slice` as its ctrl_deps. On pair
copiers that differs at every locus b writes.

**C2 [DIVERGE] exec_deps scope.** R8 literally says "from interaction start UP TO the store", so b's stores include every byte a
fetched. The store instruction's own bytes are included. `exec_deps_whole` is also exported.

**C3 [DIVERGE, big] Post-dominator scope for self-modifying code on a wrapping tape.** "Standard dynamic control-dependence
scope" is not defined for this setting. My definition:
- **CFG:** the 64 tape addresses, decoded from the tape contents AT THE MOMENT the branch executes. HALT goes to EXIT. Jump
  targets are masked to 6 bits.
- **Budget:** the step budget is NOT an edge, because it is CONSTANT (v4 s1.3).
- **Unreachable EXIT:** a node that cannot reach EXIT gets ipdom None, so its scope lasts to the end of the slice. Typical
  evolved code never HALTs, so for it pdom scope == slice scope.
- **Stack:** Xin-Zhang style. A new entry with the same ipdom as the top is merged into it. Entries are popped only from the
  top, when pc == ipdom. The stack is reset at slice entry. Branches with empty condition deps are not pushed.

Alternatives, each giving different `ctrl_deps_pdom`:
- budget edges from every node to EXIT (then pdom scope always equals slice scope);
- a CFG snapshot taken at slice start;
- popping deeper entries;
- a static CFG over the half only.

F3/F8 show the standard implicit-flow miss: after the join the pdom scope is empty.

**C4 [NOTE] addr sets are transitive (C2 CHOICE 5), implemented as follows:**
- a load's value addr = the memory byte's addr ∪ the load pointer's deps;
- a store's byte addr = the value's addr ∪ the store pointer's deps;
- a computed value's addr = the union over its operands;
- condition deps = bases(flag) ∪ flag.addr;
- a fetched byte contributes bases ∪ addr to exec_deps.

Consequence (F1): after a GETPC-based copy, every copied byte carries `{CONTEXT(GETPC), a3, a4}`. When b executes those bytes,
exec_deps and ctrl_deps pick that set up.

**C5 [DIVERGE] Pointer labels ignore the address mask.** Addresses are masked to 6 bits (z8.py:207). The H/D/B byte and bits
6-7 of the low byte never affect the address, yet I include both pointer bytes' full labels (over-approximation). A tracer that
drops the high byte (value-aware masking) gets smaller addr_deps. The flip test agrees with the engine's masking: F1 shows
DE-operand bits 6 and 7 path-preserving.

**C6 [DIVERGE] CONTEXT is a member of dependence sets.** C2 CHOICE 3 excludes only CONSTANT. CONTEXT is FOREIGN-STRUCTURAL but
"reported", so I keep it in ctrl/addr/exec. Dropping it would change addr_deps at nearly every locus of a GETPC copier.

**C7 [DIVERGE] Fetched bytes = bytes the engine actually reads.**
- IN (0xDB) and OUT (0xD3) are 2-byte instructions, but their operand byte is never read (z8.py:365-392), so it is NOT in
  exec_deps.
- LD SP,nn (0x31) operands ARE read (z8.py:297) and included, although unused.
- A disabled ED op's second byte is read (z8.py:396) and included.
- Alternative: every byte of the decoded instruction length.

**C8 [NOTE] "written".** A locus is written if any store hit it in the interaction. Value-preserving stores count; the engine's
`prov` counts only changes (z8.py:189-191). The per-locus record describes the LAST store. The write-back is a harness store
but positional, so labels carry.

## D. Performer (s2.2)

**D1 [DIVERGE]** The performer is the full data label of the store instruction's opcode byte, captured at fetch, before the
instruction's own store. A store can overwrite its own opcode (F5 writes onto 32, but its store opcode is at 35).
- The performer can be COMPUTED, CONST, PREG or MUTATION (evolved code runs on bytes it computed). I then report
  `performer_entity=None`.
- Alternative: use the performer's `bases`/carrier entity, e.g. give a COMPUTED{a3} opcode performer entity a.
- The only NPE stores are LD (HL),r / LD (HL),n / INC (HL) / DEC (HL) / LD (BC),A / LD (DE),A. There is no LDIR in this cell.

## E. Write-back mutation (C5 N1/N5, v4 s1.2 Mutation)

**E1 [NOTE] OPCODE/LOCAL operator** (world.py:484-550):
- For each position one `rng.random()` is drawn. If it is below 0.002 and the position is a linear-decode boundary, one
  `rng.randrange(256)` is drawn.
- Boundaries come from `z8.dis` of the PRE-mutation half, computed once (world.py:502), so earlier hits do not re-decode.
- ED at the last position decodes as a 1-byte NOP (z8.py:598).

My shadow is asserted equal to `Runner._mutate` on a cloned RNG, including the RNG state after both halves.

**E2 [NOTE] No RNG draws during the slices.** The world RNG is passed to the slices (world.py:802), but it is only used by
copy-mutation inside LDIR (z8.py:415), which is disabled. So the write-back RNG state = the state at interaction start
(verified in F11).

**E3 [GAP][DIVERGE] The "draw index" of MUTATION(draw, old_label).** A global draw index needs the world RNG call count, which
one interaction cannot see.
- I use `(side, k, pos)`, where k = RNG calls since the start of this interaction's write-back (a's half first). Callers can
  add a global offset.
- MUTATION is assigned even when `randrange` reproduces the old value (never by diff).

**E4 [DIVERGE] The decode-dependence set** = the base labels (post-interaction labels) of the opcode bytes at the boundaries
BEFORE position i. Each instruction's length depends only on its opcode byte (z8.dis), so these bytes decide i's position
class.
- Hits on NON-boundary positions (draw < rate, but the position is an operand, so no mutation) are also exported as
  `applied: False` events with their decode-dependence. The decode decided that nothing happened there.
- Alternatives: include the byte at i itself; report only applied events.

**E5 [DIVERGE] The flip test and interventions are evaluated on the interaction output (pre-mutation).** Mutated loci carry
MUTATION labels and are excluded from the flip test. A tracer that compares post-mutation values with the same RNG would differ
only where a flip changes the decode boundaries.

## F. Birth (C5 N1)

**F1 [DIVERGE] What "birth" means.** "A P-11 predecessor acceptance of a half" = `p11.predecessor_accepts(fid_other, fid_self,
donor_writes_other, n)` (p11.py:153; world.py:833-839), computed on the MUTATED half against both PRE genomes.
- The P-11 randomized-victim assay (`res["pass"]`, world.py:867) is NOT part of my birth definition.
- A reader who takes "P-11 ... acceptance" to require the assay pass gets fewer births.
- Both halves can be accepted in one interaction.

**F2 [GAP] Birth-existence deps are exported in four components:**
- the victim's final-half base labels;
- all victim pre loci;
- all donor pre loci;
- the dependence of the donor's `writes_other` counter. I take that as the union, over the donor's stores, of the PC label at
  the store and the store pointer's deps. Whether a write is "other" depends on its address. Exec is not included.

F9 (K30-like) shows a residue-only acceptance: the victim is accepted, but its written loci are CONST and its copy-descent
majority is itself.

## G. Flip test (v4 s4.1 + B1 + R4)

**G1 [DIVERGE] R4 opcode equivalence for NPE.** R4 defines equivalence only for BEE. My NPE classes:
- all undefined 1-byte opcodes -> NOP1;
- ED + an unknown or disabled second byte -> NOP2 (ALLOC, BIRTH, SELF, SPLIT, LDIR and LDDR are disabled by mask 0x0C);
- every other opcode is its own class.

Not merged, although semantically no-ops: LD r,r with the same register (0x40, 0x49, 0x52, 0x5B, 0x64, 0x6D, 0x7F), and the
3-byte LD SP,nn (0x31). Full semantic equivalence would turn some of my INAPPLICABLE bits into CONFIRMED.

**G2 [NOTE] What the path comparison covers:**
- the trace `(who, masked pc, class)`;
- stores `(who, addr)` plus `('OUT', who, k)`;
- loads `(who, addr)` plus `('IN', who, 0)` (B1).

Values of registers and flags are not compared. The predicted value is the pre-state byte of (X, j) XOR the bit. The flip is
applied to X's genome before tape assembly. Reruns are cached per (source, bit) and shared across loci.

**G3 [NOTE] Flip-test blind spots on NPE:**
- A MOVE whose source is an opcode byte can never be confirmed or failed: every flip changes the path. So the `loc0` mutant is
  NOT caught on the pair copier (F1), because a0 is the GETPC's ED byte; only the label expectation catches it. `loc20` and
  `reverse` are caught.
- Pointer-operand high bits are path-preserving because of the mask. That is correct, but it means a pointer byte can be
  "confirmed" as moved data.

**G4 [NOTE] The R1.3 dependence arm (`dependence_arm`).**
- Groups: the a bytes, the b bytes, and each organism's regs+flags. A regs group is used only when that organism's regs are not
  None; otherwise there are no persisted registers to randomise.
- "The write occurs" = the locus is written by any store in the rerun. Alternative: the same store instruction.
- Q8c-whether is counted for every group, the performer included (C4.1).

## H. Things I did not build

- the Q* aggregation;
- the per-byte completeness/precision arms (R5);
- the round-trip into v0;
- the s3 export format.

The tracer returns the per-locus fields those need.

Performance: about 25 ms per traced interaction in CPython, about 60 MB RSS. The full 2.8M-interaction scale (C5 N6) would need
a label-free fast path for flips.
